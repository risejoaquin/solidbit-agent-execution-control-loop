"""SACL V1 Unified Mail Gateway Daemon Implementation.

Implements ITransportGateway adhering strictly to:
- ADR-001 (Gmail Self-Mailbox Transport via Pub/Sub Pull & History API)
- ADR-008 (Process Separation of Mail Gateway Daemon)
- ADR-010 (At-Least-Once Delivery & Idempotency)
- docs/MAIL_PROTOCOL.md
- Domain 16 (mail_messages, mail_cursors) in sacl_ops.db
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from sacl.contracts.interfaces import ITransportGateway
from sacl.contracts.models import AttachmentMetadata, MailEnvelope
from sacl.transport.envelope import (
    compute_attachment_metadata,
    create_mail_envelope,
)
from sacl.transport.exceptions import (
    StaleHistoryCursorError,
)
from sacl.transport.gmail_adapter import IGmailApiAdapter
from sacl.transport.outbox import OutboxDispatcher
from sacl.transport.polling import FallbackPoller
from sacl.transport.pubsub import IPubSubSubscriber
from sacl.transport.reconciliation import (
    HistoryReconciliationManager,
)
from sacl.transport.sanitization import ZipDefenseExtractor
from sacl.transport.watch import WatchLifecycleManager

logger = logging.getLogger("sacl.transport.gateway")

DEFAULT_TOPIC_NAME = "projects/solidbit-agent-control/topics/sacl-gmail-events"
DEFAULT_AUTHORIZED_SENDER = "uniquedraken@gmail.com"


class MailGateway(ITransportGateway):
    """Unified Mail Gateway daemon implementing ITransportGateway."""

    def __init__(
        self,
        gmail_adapter: IGmailApiAdapter,
        pubsub_subscriber: IPubSubSubscriber,
        db_conn: sqlite3.Connection,
        staging_root: Path,
        topic_name: str = DEFAULT_TOPIC_NAME,
        authorized_sender: str = DEFAULT_AUTHORIZED_SENDER,
        watch_manager: Optional[WatchLifecycleManager] = None,
        reconciliation_manager: Optional[HistoryReconciliationManager] = None,
        fallback_poller: Optional[FallbackPoller] = None,
        outbox_dispatcher: Optional[OutboxDispatcher] = None,
        zip_extractor: Optional[ZipDefenseExtractor] = None,
        audit_emitter: Optional[Any] = None,
    ) -> None:
        self.gmail_adapter = gmail_adapter
        self.pubsub_subscriber = pubsub_subscriber
        self.db_conn = db_conn
        self.staging_root = staging_root
        self.topic_name = topic_name
        self.authorized_sender = authorized_sender.lower()
        self.audit_emitter = audit_emitter

        self.zip_extractor = zip_extractor or ZipDefenseExtractor()
        self.watch_manager = watch_manager or WatchLifecycleManager(
            gmail_adapter=self.gmail_adapter, db_conn=self.db_conn
        )
        self.reconciliation_manager = reconciliation_manager or HistoryReconciliationManager(
            gmail_adapter=self.gmail_adapter,
            db_conn=self.db_conn,
            staging_root=self.staging_root,
            authorized_sender=self.authorized_sender,
            zip_extractor=self.zip_extractor,
            audit_emitter=self.audit_emitter,
        )
        self.fallback_poller = fallback_poller or FallbackPoller(
            gmail_adapter=self.gmail_adapter,
            reconciliation_manager=self.reconciliation_manager,
            db_conn=self.db_conn,
        )
        self.outbox_dispatcher = outbox_dispatcher or OutboxDispatcher(
            gmail_adapter=self.gmail_adapter,
            db_conn=self.db_conn,
            sender_address=self.authorized_sender,
        )

    # =========================================================================
    # ITransportGateway INTERFACE IMPLEMENTATION
    # =========================================================================

    def pull_wake_notifications(self, max_messages: int = 10) -> List[Dict[str, Any]]:
        """Pulls untrusted wake signals from Cloud Pub/Sub and returns signal dicts."""
        signals = self.pubsub_subscriber.pull_wake_signals(max_messages=max_messages)
        results: List[Dict[str, Any]] = []
        ack_ids_to_confirm: List[str] = []

        for sig in signals:
            logger.info(
                "Received Pub/Sub wake signal for %s (historyId: %s)",
                sig.email_address,
                sig.history_id,
            )

            # Emit audit event for wake signal
            if self.audit_emitter:
                try:
                    self.audit_emitter.emit_pubsub_wake_received(
                        email_address=sig.email_address, history_id=sig.history_id
                    )
                except Exception as e:
                    logger.debug("Failed to emit PUBSUB_WAKE_RECEIVED: %s", e)

            results.append(
                {
                    "emailAddress": sig.email_address,
                    "historyId": sig.history_id,
                    "ack_id": sig.ack_id,
                    "message_id": sig.message_id,
                }
            )
            if sig.ack_id:
                ack_ids_to_confirm.append(sig.ack_id)

        # Acknowledge received wake signals
        if ack_ids_to_confirm:
            self.pubsub_subscriber.acknowledge(ack_ids_to_confirm)

        return results

    def sync_history(self, start_history_id: str) -> List[Dict[str, Any]]:
        """Authoritative fetch via Gmail History API using historyId cursor."""
        try:
            res = self.reconciliation_manager.reconcile_history(start_history_id=start_history_id)
            return [
                {
                    "start_history_id": res.start_history_id,
                    "end_history_id": res.end_history_id,
                    "messages_inspected": res.messages_inspected,
                    "jobs_ingested": res.jobs_ingested,
                    "duplicates_ignored": res.duplicates_ignored,
                    "conflicts_rejected": res.conflicts_rejected,
                    "quarantined": res.quarantined,
                    "errors": res.errors,
                }
            ]
        except StaleHistoryCursorError:
            logger.warning(
                "History cursor %s expired (404); executing full-sync fallback.", start_history_id
            )
            fallback_res = self.fallback_poller.recover_from_stale_cursor()
            return [
                {
                    "fallback_recovery": True,
                    "unhandled_messages_processed": fallback_res.unhandled_messages_processed,
                    "jobs_ingested": fallback_res.jobs_ingested,
                    "duplicates_ignored": fallback_res.duplicates_ignored,
                    "errors": fallback_res.errors,
                }
            ]

    def fetch_message_envelope(self, message_id: str) -> MailEnvelope:
        """Retrieves and parses message envelope and package attachment."""
        msg = self.gmail_adapter.get_message(message_id)
        thread_id = msg.get("threadId")
        history_id = str(msg.get("historyId", ""))
        payload = msg.get("payload", {})

        headers: Dict[str, str] = {}
        for h in payload.get("headers", []):
            headers[h.get("name", "").lower()] = h.get("value", "")

        sender = headers.get("from", "")
        recipient = headers.get("to", "")
        subject = headers.get("subject", "")

        # Find attachment
        attachment_id, filename, size = self.reconciliation_manager._find_zip_attachment(payload)
        if attachment_id:
            raw_bytes = self.gmail_adapter.get_attachment(message_id, attachment_id)
            att_meta = compute_attachment_metadata(filename, raw_bytes)
        else:
            att_meta = AttachmentMetadata(
                filename="none.zip",
                size_bytes=1,
                sha256="0000000000000000000000000000000000000000000000000000000000000000",
            )

        envelope = create_mail_envelope(
            message_id=message_id,
            direction="INBOUND",
            sender=sender,
            recipient=recipient,
            raw_subject=subject,
            attachment=att_meta,
            status="RECEIVED",
            history_id=history_id,
            thread_id=thread_id,
            validate_schema=False,
        )
        return envelope

    def dispatch_outbox_reply(
        self,
        recipient: str,
        subject: str,
        body_markdown: str,
        attachment_path: Optional[Path] = None,
    ) -> str:
        """Dispatches outbound execution result reply via Gmail API."""
        attach_str = str(attachment_path) if attachment_path else None
        run_id = "adhoc-reply"
        outbox_id = self.outbox_dispatcher.enqueue_reply(
            run_id=run_id,
            recipient=recipient,
            subject=subject,
            body_markdown=body_markdown,
            attachment_path=attach_str,
        )
        self.outbox_dispatcher.dispatch_pending(max_messages=1)
        return f"outbox-{outbox_id}"

    # =========================================================================
    # DAEMON LIFECYCLE & TICK COORDINATION
    # =========================================================================

    def startup_catchup(self) -> List[str]:
        """Executes startup reconciliation pass per docs/MAIL_PROTOCOL.md §3.5.

        1. Verifies and renews watch lease if expiring.
        2. Ingests and stages any messages that arrived while daemon was offline.
        3. Dispatches any pending outbox messages.
        """
        logger.info("Executing Mail Gateway startup catch-up reconciliation...")
        # 1. History catchup from persisted cursor (per docs/MAIL_PROTOCOL.md §3.5)
        persisted_id = self.reconciliation_manager.get_persisted_cursor()
        sync_results = self.sync_history(persisted_id)

        # Collect ingested jobs
        ingested_jobs: List[str] = []
        for sr in sync_results:
            ingested_jobs.extend(sr.get("jobs_ingested", []))

        # 2. Watch lease check & renewal
        self.watch_manager.check_and_renew_watch(topic_name=self.topic_name)

        # 3. Flush any queued outbox messages
        self.outbox_dispatcher.dispatch_pending()

        logger.info("Startup catch-up complete. Ingested %d job(s)", len(ingested_jobs))
        return ingested_jobs

    def run_gateway_tick(self) -> Dict[str, Any]:
        """Executes a single cycle of the Mail Gateway daemon loop."""
        tick_summary: Dict[str, Any] = {
            "watch_renewed": False,
            "wake_signals": 0,
            "jobs_ingested": [],
            "outbox_dispatched": 0,
        }

        # 1. Watch renewal check
        tick_summary["watch_renewed"] = self.watch_manager.check_and_renew_watch(
            topic_name=self.topic_name
        )

        # 2. Pub/Sub pull wake signals
        wakes = self.pull_wake_notifications(max_messages=10)
        tick_summary["wake_signals"] = len(wakes)

        # 3. If wake signal received, execute authoritative history sync
        if wakes:
            persisted_id = self.reconciliation_manager.get_persisted_cursor()
            sync_res = self.sync_history(persisted_id)
            for sr in sync_res:
                tick_summary["jobs_ingested"].extend(sr.get("jobs_ingested", []))

        # 4. Safety fallback polling (only if interval elapsed)
        if self.fallback_poller.should_poll():
            poll_res = self.fallback_poller.poll_mailbox()
            tick_summary["jobs_ingested"].extend(poll_res.jobs_ingested)

        # 5. Outbox dispatch
        tick_summary["outbox_dispatched"] = self.outbox_dispatcher.dispatch_pending()

        return tick_summary

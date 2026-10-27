"""SACL V1 History API Cursor Reconciliation & Ingress Pipeline.

Adheres strictly to:
- ADR-001 (Authoritative fetch via Gmail History API)
- ADR-008 (Mail Gateway isolation)
- ADR-010 (At-Least-Once Delivery & Idempotent Deduplication Matrix)
- docs/MAIL_PROTOCOL.md §2.4, §3.3, §3.5
- Domain 16 (mail_messages, mail_cursors) in 001_init.sql
"""

from __future__ import annotations

import dataclasses
import datetime
import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from sacl.transport.envelope import (
    compute_attachment_metadata,
    generate_nonce,
    parse_routing_hint,
)
from sacl.transport.exceptions import (
    StaleHistoryCursorError,
    ZipDefenseViolation,
)
from sacl.transport.gmail_adapter import IGmailApiAdapter
from sacl.transport.sanitization import ZipDefenseExtractor

logger = logging.getLogger("sacl.transport.reconciliation")

DEFAULT_AUTHORIZED_SENDER = "uniquedraken@gmail.com"
DEFAULT_CURSOR_NAME = "GMAIL_USERS_WATCH"


@dataclasses.dataclass
class ReconciliationResult:
    """Summary of messages processed during a History API synchronization pass."""

    start_history_id: str
    end_history_id: str
    messages_inspected: int = 0
    jobs_ingested: List[str] = dataclasses.field(default_factory=list)
    duplicates_ignored: List[str] = dataclasses.field(default_factory=list)
    conflicts_rejected: List[str] = dataclasses.field(default_factory=list)
    quarantined: List[str] = dataclasses.field(default_factory=list)
    errors: List[str] = dataclasses.field(default_factory=list)


class HistoryReconciliationManager:
    """Synchronizes mailbox changes from Gmail History API with SQLite cursors and deduplication."""

    def __init__(
        self,
        gmail_adapter: IGmailApiAdapter,
        db_conn: sqlite3.Connection,
        staging_root: Path,
        authorized_sender: str = DEFAULT_AUTHORIZED_SENDER,
        cursor_name: str = DEFAULT_CURSOR_NAME,
        zip_extractor: Optional[ZipDefenseExtractor] = None,
        audit_emitter: Optional[Any] = None,
    ) -> None:
        self.gmail_adapter = gmail_adapter
        self.db_conn = db_conn
        self.staging_root = staging_root
        self.authorized_sender = authorized_sender.lower()
        self.cursor_name = cursor_name
        self.zip_extractor = zip_extractor or ZipDefenseExtractor()
        self.audit_emitter = audit_emitter

    def get_persisted_cursor(self) -> str:
        """Retrieves authoritative historyId from SQLite mail_cursors."""
        cursor = self.db_conn.cursor()
        cursor.execute(
            "SELECT history_id FROM mail_cursors WHERE cursor_name = ?", (self.cursor_name,)
        )
        row = cursor.fetchone()
        if row and row[0]:
            return str(row[0])
        return "1"

    def advance_persisted_cursor(self, new_history_id: str) -> None:
        """Atomically advances authoritative historyId cursor in SQLite."""
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        cursor = self.db_conn.cursor()
        cursor.execute(
            """
            INSERT INTO mail_cursors (cursor_name, history_id, last_synced_at)
            VALUES (?, ?, ?)
            ON CONFLICT(cursor_name) DO UPDATE SET
                history_id = excluded.history_id,
                last_synced_at = excluded.last_synced_at
            WHERE excluded.history_id > mail_cursors.history_id OR mail_cursors.history_id IS NULL;
            """,
            (self.cursor_name, new_history_id, now_iso),
        )
        self.db_conn.commit()

    def reconcile_history(self, start_history_id: Optional[str] = None) -> ReconciliationResult:
        """Executes gapless authoritative synchronization via users.history.list.

        Returns ReconciliationResult summarizing message outcomes.
        """
        start_id = start_history_id or self.get_persisted_cursor()
        logger.info("Executing History API reconciliation starting from historyId=%s", start_id)

        try:
            history_resp = self.gmail_adapter.list_history(start_history_id=start_id)
        except StaleHistoryCursorError:
            # Let caller or poller handle stale fallback
            logger.warning(
                "History cursor %s is stale (>7 days). Raising StaleHistoryCursorError.", start_id
            )
            raise

        records = history_resp.get("history", [])
        end_history_id = str(history_resp.get("historyId", start_id))
        result = ReconciliationResult(start_history_id=start_id, end_history_id=end_history_id)

        # Collect unique message IDs added
        message_ids: Set[str] = set()
        for rec in records:
            for added in rec.get("messagesAdded", []):
                msg_info = added.get("message", {})
                mid = msg_info.get("id")
                if mid:
                    message_ids.add(mid)

        for mid in sorted(message_ids):
            result.messages_inspected += 1
            try:
                outcome, job_id = self.process_inbound_message(mid)
                if outcome == "INGESTED" and job_id:
                    result.jobs_ingested.append(job_id)
                elif outcome == "DUPLICATE_IGNORED":
                    result.duplicates_ignored.append(mid)
                elif outcome == "CONFLICT_REJECTED":
                    result.conflicts_rejected.append(mid)
                elif outcome == "QUARANTINED":
                    result.quarantined.append(mid)
            except Exception as e:
                logger.error("Error processing inbound message %s: %s", mid, e)
                result.errors.append(f"{mid}: {e}")

        # Advance cursor after processing all messages in this batch
        self.advance_persisted_cursor(end_history_id)

        # Emit audit event if emitter configured
        if self.audit_emitter:
            try:
                self.audit_emitter.emit_history_fetched(
                    start_history_id=start_id,
                    end_history_id=end_history_id,
                    messages_count=result.messages_inspected,
                )
            except Exception as e:
                logger.debug("Failed to emit HISTORY_FETCHED audit event: %s", e)

        return result

    def process_inbound_message(self, message_id: str) -> Tuple[str, Optional[str]]:
        """Processes an individual inbound message through the 8 defense-in-depth layers.

        Returns:
            Tuple of (outcome_status, optional_job_id)
        """
        raw_msg = self.gmail_adapter.get_message(message_id)
        thread_id = raw_msg.get("threadId")
        msg_history_id = str(raw_msg.get("historyId", ""))
        snippet = raw_msg.get("snippet", "")
        payload = raw_msg.get("payload", {})
        headers_list = payload.get("headers", [])

        # Parse headers
        headers: Dict[str, str] = {}
        for h in headers_list:
            headers[h.get("name", "").lower()] = h.get("value", "")

        sender = headers.get("from", "")
        recipient = headers.get("to", "")
        subject = headers.get("subject", "")
        rfc_msg_id = headers.get("message-id", f"<{message_id}@mail.invalid>")
        received_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        nonce = generate_nonce()

        # Extract email address part from 'Name <email>' format
        sender_email = sender
        if "<" in sender and ">" in sender:
            sender_email = sender[sender.find("<") + 1 : sender.find(">")]
        sender_email = sender_email.strip().lower()

        # Layer 3: Sender Whitelist Verification (Self-mail supported)
        if sender_email != self.authorized_sender:
            logger.warning(
                "Unauthorized sender '%s' (expected '%s'). Quarantining message %s.",
                sender_email,
                self.authorized_sender,
                message_id,
            )
            self._record_message_status(
                message_id=message_id,
                history_id=msg_history_id,
                thread_id=thread_id,
                sender=sender,
                recipient=recipient,
                subject=subject,
                snippet=snippet,
                received_at=received_at,
                nonce=nonce,
                attachment_sha="none",
                status="QUARANTINED",
                rejection_reason=f"SENDER_NOT_WHITELISTED: {sender_email}",
            )
            return ("QUARANTINED", None)

        # Layer 4: Subject Routing Hint
        routing_hint = parse_routing_hint(subject)
        if not routing_hint.is_valid_routing_hint:
            logger.warning(
                "Invalid routing hint in subject '%s'. Rejecting message %s.", subject, message_id
            )
            self._record_message_status(
                message_id=message_id,
                history_id=msg_history_id,
                thread_id=thread_id,
                sender=sender,
                recipient=recipient,
                subject=subject,
                snippet=snippet,
                received_at=received_at,
                nonce=nonce,
                attachment_sha="none",
                status="REJECTED",
                rejection_reason="INVALID_ROUTING_HINT",
            )
            return ("QUARANTINED", None)

        job_id = routing_hint.job_id

        # Locate ZIP Attachment
        attachment_id, attachment_filename, attachment_size = self._find_zip_attachment(payload)
        if not attachment_id:
            logger.warning("No ZIP attachment found in message %s. Rejecting.", message_id)
            self._record_message_status(
                message_id=message_id,
                history_id=msg_history_id,
                thread_id=thread_id,
                sender=sender,
                recipient=recipient,
                subject=subject,
                snippet=snippet,
                received_at=received_at,
                nonce=nonce,
                attachment_sha="none",
                status="REJECTED",
                rejection_reason="MISSING_ZIP_ATTACHMENT",
                job_id=job_id,
            )
            return ("QUARANTINED", job_id)

        # Download raw attachment bytes
        attachment_bytes = self.gmail_adapter.get_attachment(message_id, attachment_id)
        att_meta = compute_attachment_metadata(attachment_filename, attachment_bytes)

        # Layer 6: Deduplication & Conflict Invariants (ADR-010)
        dedup_status, conflict_err = self._check_deduplication(message_id, job_id, att_meta.sha256)

        if dedup_status == "DUPLICATE_IGNORED":
            logger.info(
                "Message %s is duplicate delivery of job %s. Idempotently ignored.",
                message_id,
                job_id,
            )
            self._record_message_status(
                message_id=message_id,
                history_id=msg_history_id,
                thread_id=thread_id,
                sender=sender,
                recipient=recipient,
                subject=subject,
                snippet=snippet,
                received_at=received_at,
                nonce=nonce,
                attachment_sha=att_meta.sha256,
                status="DUPLICATE_IGNORED",
                job_id=job_id,
            )
            return ("DUPLICATE_IGNORED", job_id)

        if dedup_status == "CONFLICT":
            logger.warning(
                "CONFLICT: Job '%s' resubmitted with divergent hash (stored: %s, incoming: %s)",
                job_id,
                conflict_err,
                att_meta.sha256,
            )
            self._record_message_status(
                message_id=message_id,
                history_id=msg_history_id,
                thread_id=thread_id,
                sender=sender,
                recipient=recipient,
                subject=subject,
                snippet=snippet,
                received_at=received_at,
                nonce=nonce,
                attachment_sha=att_meta.sha256,
                status="REJECTED",
                rejection_reason="JOB_ID_HASH_MISMATCH",
                job_id=job_id,
            )
            self._queue_conflict_reply(job_id=job_id, thread_id=thread_id, rfc_msg_id=rfc_msg_id)
            if self.audit_emitter:
                try:
                    self.audit_emitter.emit_conflict_detected(
                        job_id=job_id, reason="JOB_ID_HASH_MISMATCH"
                    )
                except Exception:
                    pass
            return ("CONFLICT_REJECTED", job_id)

        # Layer 7: Zip Defense Inspection & Safe Staging
        run_id = f"{job_id.lower()}-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}-{nonce[:6]}"
        stage_dir = self.staging_root / "packages" / "inbox" / run_id

        try:
            self.zip_extractor.validate_and_extract(
                archive_source=attachment_bytes,
                destination_dir=stage_dir,
                package_id=job_id,
            )
        except ZipDefenseViolation as e:
            logger.error("Zip defense violation on package %s: %s", job_id, e)
            self._record_message_status(
                message_id=message_id,
                history_id=msg_history_id,
                thread_id=thread_id,
                sender=sender,
                recipient=recipient,
                subject=subject,
                snippet=snippet,
                received_at=received_at,
                nonce=nonce,
                attachment_sha=att_meta.sha256,
                status="QUARANTINED",
                rejection_reason=str(e),
                job_id=job_id,
            )
            return ("QUARANTINED", job_id)

        # Successful Ingestion: Record in mail_messages
        self._record_message_status(
            message_id=message_id,
            history_id=msg_history_id,
            thread_id=thread_id,
            sender=sender,
            recipient=recipient,
            subject=subject,
            snippet=snippet,
            received_at=received_at,
            nonce=nonce,
            attachment_sha=att_meta.sha256,
            status="PERSISTED",
            job_id=job_id,
            run_id=run_id,
            processed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        )

        logger.info(
            "Successfully ingested and staged package for job '%s' (runId=%s) to %s",
            job_id,
            run_id,
            stage_dir,
        )

        if self.audit_emitter:
            try:
                self.audit_emitter.emit_job_ingested(
                    job_id=job_id, run_id=run_id, package_sha=att_meta.sha256
                )
            except Exception:
                pass

        return ("INGESTED", job_id)

    def _find_zip_attachment(self, payload: Dict[str, Any]) -> Tuple[Optional[str], str, int]:
        """Traverses MIME payload parts looking for .zip attachment."""
        parts = payload.get("parts", [])
        for part in parts:
            filename = part.get("filename", "")
            mime = part.get("mimeType", "")
            if filename.lower().endswith(".zip") or mime == "application/zip":
                body = part.get("body", {})
                att_id = body.get("attachmentId")
                size = body.get("size", 0)
                if att_id:
                    return (att_id, filename or "package.zip", size)

        # Check top-level payload if attachment is directly attached
        body = payload.get("body", {})
        att_id = body.get("attachmentId")
        filename = payload.get("filename", "")
        if att_id and filename.lower().endswith(".zip"):
            return (att_id, filename, body.get("size", 0))

        return (None, "", 0)

    def _check_deduplication(
        self, message_id: str, job_id: str, incoming_sha: str
    ) -> Tuple[str, Optional[str]]:
        """Evaluates ADR-010 deduplication matrix against SQLite tables."""
        cursor = self.db_conn.cursor()

        # Check identical message ID
        cursor.execute(
            "SELECT status, attachment_sha FROM mail_messages WHERE message_id = ?", (message_id,)
        )
        row = cursor.fetchone()
        if row:
            return ("DUPLICATE_IGNORED", None)

        # Check job_id in mail_messages
        cursor.execute(
            "SELECT attachment_sha, status FROM mail_messages WHERE job_id = ? AND status != 'REJECTED' ORDER BY received_at DESC LIMIT 1",
            (job_id,),
        )
        row = cursor.fetchone()
        if row:
            stored_sha = row[0]
            if stored_sha == incoming_sha:
                return ("DUPLICATE_IGNORED", None)
            else:
                return ("CONFLICT", stored_sha)

        return ("NOVEL", None)

    def _record_message_status(
        self,
        message_id: str,
        history_id: str,
        thread_id: Optional[str],
        sender: str,
        recipient: str,
        subject: str,
        snippet: str,
        received_at: str,
        nonce: str,
        attachment_sha: str,
        status: str,
        rejection_reason: Optional[str] = None,
        job_id: Optional[str] = None,
        run_id: Optional[str] = None,
        processed_at: Optional[str] = None,
    ) -> None:
        """Persists message record into SQLite mail_messages."""
        cursor = self.db_conn.cursor()

        # Ensure job_id exists in jobs table to satisfy FOREIGN KEY constraint
        if job_id:
            cursor.execute("SELECT 1 FROM jobs WHERE job_id = ?", (job_id,))
            if not cursor.fetchone():
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO jobs (job_id, status, priority, created_at, updated_at)
                    VALUES (?, 'RECEIVED', 0, ?, ?)
                    """,
                    (job_id, received_at, received_at),
                )

        # Ensure run_id exists in runs table if specified
        if run_id and job_id:
            cursor.execute("SELECT 1 FROM runs WHERE run_id = ?", (run_id,))
            if not cursor.fetchone():
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO runs (
                        run_id, job_id, package_id, project, repository, mode,
                        source_orchestrator, target_repo_path, run_dir, status,
                        ready_for_integration, started_at
                    ) VALUES (
                        ?, ?, ?, 'default', 'default/repo', 'isolated_branch_development',
                        '', '', '', 'RECEIVED', 'NO', ?
                    )
                    """,
                    (run_id, job_id, f"pkg-{job_id}", received_at),
                )

        cursor.execute(
            """
            INSERT INTO mail_messages (
                message_id, history_id, thread_id, sender, recipient,
                subject, snippet, received_at, processed_at, nonce,
                attachment_sha, status, rejection_reason, job_id, run_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(message_id) DO UPDATE SET
                status = excluded.status,
                rejection_reason = excluded.rejection_reason,
                processed_at = excluded.processed_at;
            """,
            (
                message_id,
                history_id,
                thread_id,
                sender,
                recipient,
                subject,
                snippet,
                received_at,
                processed_at,
                nonce,
                attachment_sha,
                status,
                rejection_reason,
                job_id,
                run_id,
            ),
        )
        self.db_conn.commit()

    def _queue_conflict_reply(self, job_id: str, thread_id: Optional[str], rfc_msg_id: str) -> None:
        """Queues conflict notification email reply in mail_outbox table."""
        subject = f"[SACL][RESULT][v1][{job_id}] - REJECTED (Hash Conflict)"
        body = (
            f"# Execution Package Submission Rejected\n\n"
            f"Job **{job_id}** was submitted with a package hash that diverges from "
            f"the previously registered package hash for this Job ID.\n\n"
            f"Per ADR-010, the orchestrator rejects conflicting payloads to prevent "
            f"workspace contamination. If this was intended as a retry, submit with a new Job ID "
            f"or use explicit retry semantics.\n"
        )
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        conflict_run_id = f"conflict-{job_id}"
        cursor = self.db_conn.cursor()

        # Ensure jobs row exists
        cursor.execute("SELECT 1 FROM jobs WHERE job_id = ?", (job_id,))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT OR IGNORE INTO jobs (job_id, status, priority, created_at, updated_at) VALUES (?, 'REJECTED', 0, ?, ?)",
                (job_id, now_iso, now_iso),
            )

        # Ensure runs row exists to satisfy FOREIGN KEY constraint in mail_outbox
        cursor.execute("SELECT 1 FROM runs WHERE run_id = ?", (conflict_run_id,))
        if not cursor.fetchone():
            cursor.execute(
                """
                INSERT OR IGNORE INTO runs (
                    run_id, job_id, package_id, project, repository, mode,
                    source_orchestrator, target_repo_path, run_dir, status,
                    ready_for_integration, started_at
                ) VALUES (
                    ?, ?, ?, 'default', 'default/repo', 'isolated_branch_development',
                    '', '', '', 'REJECTED', 'NO', ?
                )
                """,
                (conflict_run_id, job_id, f"pkg-{job_id}", now_iso),
            )

        cursor.execute(
            """
            INSERT INTO mail_outbox (run_id, recipient, subject, body_markdown, status, created_at)
            VALUES (?, ?, ?, ?, 'QUEUED', ?)
            """,
            (conflict_run_id, self.authorized_sender, subject, body, now_iso),
        )
        self.db_conn.commit()

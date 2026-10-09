"""SACL V1 Degraded Fallback Polling & Stale Cursor Recovery.

Adheres strictly to:
- ADR-001 (Degraded fallback polling only)
- docs/MAIL_PROTOCOL.md §3.3, §3.6
- DECISION_BASELINE §3.1 (Unread mailbox state is NEVER the source of truth)
"""

from __future__ import annotations

import dataclasses
import datetime
import logging
import sqlite3
from typing import Any, Dict, List, Optional, Set

from sacl.transport.gmail_adapter import IGmailApiAdapter
from sacl.transport.reconciliation import HistoryReconciliationManager

logger = logging.getLogger("sacl.transport.polling")

DEFAULT_FALLBACK_QUERY = "to:me subject:[SACL][JOB][v1]"
DEFAULT_FALLBACK_INTERVAL_SECONDS = 900  # 15 minutes


@dataclasses.dataclass
class PollingResult:
    """Summary of degraded fallback polling execution."""
    messages_found: int = 0
    unhandled_messages_processed: int = 0
    jobs_ingested: List[str] = dataclasses.field(default_factory=list)
    duplicates_ignored: List[str] = dataclasses.field(default_factory=list)
    errors: List[str] = dataclasses.field(default_factory=list)


class FallbackPoller:
    """Provides periodic safety reconciliation and recovery from 404 stale cursor conditions."""

    def __init__(
        self,
        gmail_adapter: IGmailApiAdapter,
        reconciliation_manager: HistoryReconciliationManager,
        db_conn: sqlite3.Connection,
        fallback_query: str = DEFAULT_FALLBACK_QUERY,
        min_interval_seconds: int = DEFAULT_FALLBACK_INTERVAL_SECONDS,
    ) -> None:
        self.gmail_adapter = gmail_adapter
        self.reconciliation_manager = reconciliation_manager
        self.db_conn = db_conn
        self.fallback_query = fallback_query
        self.min_interval_seconds = min_interval_seconds
        self._last_polled_at: Optional[datetime.datetime] = None

    def should_poll(self, force: bool = False) -> bool:
        """Determines if enough time has elapsed to justify a fallback polling pass."""
        if force:
            return True
        if self._last_polled_at is None:
            return True
        elapsed = (datetime.datetime.now(datetime.timezone.utc) - self._last_polled_at).total_seconds()
        return elapsed >= self.min_interval_seconds

    def poll_mailbox(self, force: bool = False) -> PollingResult:
        """Executes fallback polling pass to catch unhandled messages.

        INVARIANT: Unread mailbox state is NEVER the source of truth.
        All messages matching query are evaluated against SQLite persisted state.
        """
        if not self.should_poll(force=force):
            logger.debug("Skipping fallback poll: min interval has not elapsed.")
            return PollingResult()

        logger.info("Executing safety fallback polling pass with query: '%s'", self.fallback_query)
        self._last_polled_at = datetime.datetime.now(datetime.timezone.utc)

        list_resp = self.gmail_adapter.list_messages(query=self.fallback_query, max_results=50)
        messages_stubs = list_resp.get("messages", [])

        result = PollingResult(messages_found=len(messages_stubs))
        unhandled_ids = self._filter_unhandled_message_ids([m.get("id") for m in messages_stubs if m.get("id")])

        for mid in unhandled_ids:
            try:
                outcome, job_id = self.reconciliation_manager.process_inbound_message(mid)
                result.unhandled_messages_processed += 1
                if outcome == "INGESTED" and job_id:
                    result.jobs_ingested.append(job_id)
                elif outcome == "DUPLICATE_IGNORED":
                    result.duplicates_ignored.append(mid)
            except Exception as e:
                logger.error("Error during fallback polling on message %s: %s", mid, e)
                result.errors.append(f"{mid}: {e}")

        return result

    def recover_from_stale_cursor(self) -> PollingResult:
        """Executes full-sync fallback recovery when History API returns 404 (cursor expired).

        Resets historyId in mail_cursors to latest observed mailbox state.
        """
        logger.warning("Initiating full-sync recovery from stale History cursor (404)...")
        # 1. Run full fallback poll
        res = self.poll_mailbox(force=True)

        # 2. Resync cursor to latest message historyId
        try:
            # Query any recent message to get current mailbox historyId
            list_resp = self.gmail_adapter.list_messages(query=self.fallback_query, max_results=1)
            msgs = list_resp.get("messages", [])
            if msgs:
                latest_msg = self.gmail_adapter.get_message(msgs[0]["id"])
                latest_history_id = str(latest_msg.get("historyId", "1"))
                self.reconciliation_manager.advance_persisted_cursor(latest_history_id)
                logger.info("Reset persisted history cursor to %s after stale recovery", latest_history_id)
        except Exception as e:
            logger.error("Failed to update history cursor after stale recovery: %s", e)

        return res

    def _filter_unhandled_message_ids(self, candidate_ids: List[str]) -> List[str]:
        """Filters candidate message IDs to those not yet recorded in mail_messages."""
        if not candidate_ids:
            return []

        cursor = self.db_conn.cursor()
        placeholders = ",".join("?" for _ in candidate_ids)
        cursor.execute(
            f"SELECT message_id FROM mail_messages WHERE message_id IN ({placeholders})",
            candidate_ids,
        )
        handled_ids = {row[0] for row in cursor.fetchall()}
        return [cid for cid in candidate_ids if cid not in handled_ids]

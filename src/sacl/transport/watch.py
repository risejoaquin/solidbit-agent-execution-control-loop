"""SACL V1 Gmail API users.watch Lifecycle Manager.

Manages registration, lease tracking, and automated renewal of the Gmail API
users.watch subscription per:
- ADR-001 (Gmail Self-Mailbox Transport)
- docs/MAIL_PROTOCOL.md §3.1, §3.4
- SQLite table mail_cursors (Domain 16)
"""

from __future__ import annotations

import datetime
import logging
import sqlite3
from typing import Any, Dict, List, Optional

from sacl.transport.gmail_adapter import IGmailApiAdapter

logger = logging.getLogger("sacl.transport.watch")

DEFAULT_CURSOR_NAME = "GMAIL_USERS_WATCH"
DEFAULT_WATCH_LABEL_IDS = ["INBOX"]
DEFAULT_RENEWAL_THRESHOLD_SECONDS = 86400  # 24 hours prior to expiration


def parse_expiration_timestamp(expiration_val: Any) -> str:
    """Converts Gmail epoch milliseconds or ISO string to ISO-8601 UTC timestamp."""
    if isinstance(expiration_val, str) and not expiration_val.isdigit():
        # Already an ISO timestamp string
        return expiration_val

    try:
        epoch_ms = int(expiration_val)
        dt = datetime.datetime.fromtimestamp(epoch_ms / 1000.0, tz=datetime.timezone.utc)
        return dt.isoformat()
    except (ValueError, TypeError):
        # Fallback to now + 7 days
        dt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
        return dt.isoformat()


class WatchLifecycleManager:
    """Coordinates Gmail API users.watch registration, renewal, and persistence."""

    def __init__(
        self,
        gmail_adapter: IGmailApiAdapter,
        db_conn: sqlite3.Connection,
        cursor_name: str = DEFAULT_CURSOR_NAME,
    ) -> None:
        self.gmail_adapter = gmail_adapter
        self.db_conn = db_conn
        self.cursor_name = cursor_name

    def register_watch(
        self, topic_name: str, label_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Registers users.watch with Gmail API and persists lease to SQLite mail_cursors."""
        labels = label_ids or DEFAULT_WATCH_LABEL_IDS
        logger.info("Registering users.watch with topic '%s' (labels: %s)", topic_name, labels)

        watch_resp = self.gmail_adapter.watch(topic_name=topic_name, label_ids=labels)
        history_id = str(watch_resp.get("historyId", "1"))
        raw_exp = watch_resp.get("expiration")
        expiration_iso = parse_expiration_timestamp(raw_exp)
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        cursor = self.db_conn.cursor()
        cursor.execute(
            """
            INSERT INTO mail_cursors (cursor_name, history_id, last_synced_at, expiration_at, resource_id)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(cursor_name) DO UPDATE SET
                history_id = excluded.history_id,
                last_synced_at = excluded.last_synced_at,
                expiration_at = excluded.expiration_at,
                resource_id = excluded.resource_id;
            """,
            (self.cursor_name, history_id, now_iso, expiration_iso, topic_name),
        )
        self.db_conn.commit()

        logger.info(
            "users.watch successfully registered. Cursor '%s' set to historyId=%s, expires=%s",
            self.cursor_name,
            history_id,
            expiration_iso,
        )
        return {
            "cursor_name": self.cursor_name,
            "history_id": history_id,
            "last_synced_at": now_iso,
            "expiration_at": expiration_iso,
            "resource_id": topic_name,
        }

    def get_active_watch_cursor(self) -> Optional[Dict[str, Any]]:
        """Retrieves active watch cursor record from SQLite mail_cursors."""
        cursor = self.db_conn.cursor()
        cursor.execute(
            """
            SELECT cursor_name, history_id, last_synced_at, expiration_at, resource_id
            FROM mail_cursors
            WHERE cursor_name = ?
            """,
            (self.cursor_name,),
        )
        row = cursor.fetchone()
        if not row:
            return None

        if isinstance(row, sqlite3.Row):
            return dict(row)
        return {
            "cursor_name": row[0],
            "history_id": row[1],
            "last_synced_at": row[2],
            "expiration_at": row[3],
            "resource_id": row[4],
        }

    def check_and_renew_watch(
        self,
        topic_name: str,
        label_ids: Optional[List[str]] = None,
        renewal_threshold_seconds: int = DEFAULT_RENEWAL_THRESHOLD_SECONDS,
    ) -> bool:
        """Checks if active watch is expiring soon or expired, and renews if necessary.

        Returns:
            True if watch was renewed; False if active lease remains valid.
        """
        record = self.get_active_watch_cursor()
        if not record or not record.get("expiration_at"):
            logger.info("No active watch record found; registering fresh watch.")
            self.register_watch(topic_name, label_ids)
            return True

        exp_str = record["expiration_at"]
        try:
            exp_dt = datetime.datetime.fromisoformat(exp_str)
            if exp_dt.tzinfo is None:
                exp_dt = exp_dt.replace(tzinfo=datetime.timezone.utc)
        except Exception:
            logger.warning("Corrupt expiration timestamp in DB ('%s'); renewing watch.", exp_str)
            self.register_watch(topic_name, label_ids)
            return True

        now = datetime.datetime.now(datetime.timezone.utc)
        remaining_seconds = (exp_dt - now).total_seconds()

        if remaining_seconds <= renewal_threshold_seconds:
            logger.info(
                "Watch lease expiring in %.1f hours (threshold: %.1f hours); renewing.",
                remaining_seconds / 3600.0,
                renewal_threshold_seconds / 3600.0,
            )
            self.register_watch(topic_name, label_ids)
            return True

        logger.debug(
            "Watch lease healthy: %.1f hours remaining until expiry.", remaining_seconds / 3600.0
        )
        return False

    def stop_watch(self) -> None:
        """Terminates active users.watch and clears expiration in mail_cursors."""
        logger.info("Stopping active users.watch registration.")
        self.gmail_adapter.stop_watch()
        cursor = self.db_conn.cursor()
        cursor.execute(
            """
            UPDATE mail_cursors
            SET expiration_at = NULL, last_synced_at = ?
            WHERE cursor_name = ?
            """,
            (datetime.datetime.now(datetime.timezone.utc).isoformat(), self.cursor_name),
        )
        self.db_conn.commit()

"""SACL V1 Mail Repository.

Domain 16: Gmail API transport queue and historyId synchronization cursors (SB-FREEZE-P1-01).
Compatibility Tables: mail_inbox, mail_outbox.
"""

from __future__ import annotations

import sqlite3
from typing import Any, Dict, List, Optional

from sacl.state.exceptions import DuplicateEntityError, EntityNotFoundError
from sacl.state.repositories.base import BaseRepository
from sacl.state.utils import normalize_repo_path, utc_now

VALID_MAIL_STATUSES = frozenset({
    'RECEIVED', 'AUTHENTICATED', 'VALIDATED', 'PERSISTED',
    'QUEUED', 'PROCESSED', 'REJECTED', 'QUARANTINED', 'DUPLICATE_IGNORED'
})


class MailRepository(BaseRepository):
    """Repository managing Domain 16 'mail_messages', 'mail_cursors', and compatibility queues."""

    # =========================================================================
    # DOMAIN 16: INBOUND MAIL MESSAGES
    # =========================================================================

    def record_inbound_message(
        self,
        message_id: str,
        sender: str,
        recipient: str,
        subject: str,
        nonce: str,
        attachment_sha: str,
        status: str = "RECEIVED",
        history_id: Optional[str] = None,
        thread_id: Optional[str] = None,
        snippet: Optional[str] = None,
        job_id: Optional[str] = None,
        run_id: Optional[str] = None,
        received_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Records inbound email transport envelope in mail_messages and mail_inbox."""
        if status not in VALID_MAIL_STATUSES:
            raise ValueError(f"Invalid mail message status: {status}")

        now = received_at or utc_now()

        sql_msg = """
            INSERT INTO mail_messages (
                message_id, history_id, thread_id, sender, recipient,
                subject, snippet, received_at, processed_at, nonce,
                attachment_sha, status, rejection_reason, job_id, run_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, ?, ?, NULL, ?, ?);
        """
        try:
            self.execute(
                sql_msg,
                (
                    message_id, history_id, thread_id, sender, recipient,
                    subject, snippet, now, nonce, attachment_sha, status,
                    job_id, run_id,
                ),
            )
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: mail_messages.nonce" in str(e):
                raise DuplicateEntityError(f"Duplicate mail nonce detected: '{nonce}'") from e
            if "UNIQUE constraint failed: mail_messages.message_id" in str(e):
                raise DuplicateEntityError(f"Duplicate mail message_id detected: '{message_id}'") from e
            raise

        # Mirror to compatibility mail_inbox
        inbox_status = 'PENDING'
        if status in ('VALIDATED', 'PROCESSED', 'REJECTED', 'DUPLICATE_IGNORED'):
            inbox_status = status

        sql_inbox = """
            INSERT OR IGNORE INTO mail_inbox (
                message_id, sender, subject, received_at,
                nonce, attachment_sha, status, rejection_reason, run_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, NULL, ?);
        """
        self.execute(sql_inbox, (message_id, sender, subject, now, nonce, attachment_sha, inbox_status, run_id))
        self.commit()
        return self.get_message(message_id)  # type: ignore[return-value]

    def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves mail message by message ID."""
        sql = "SELECT * FROM mail_messages WHERE message_id = ?;"
        return self.fetchone_dict(sql, (message_id,))

    def get_message_by_nonce(self, nonce: str) -> Optional[Dict[str, Any]]:
        """Retrieves mail message by cryptographic anti-replay nonce."""
        sql = "SELECT * FROM mail_messages WHERE nonce = ?;"
        return self.fetchone_dict(sql, (nonce,))

    def update_message_status(
        self,
        message_id: str,
        status: str,
        rejection_reason: Optional[str] = None,
        job_id: Optional[str] = None,
        run_id: Optional[str] = None,
        processed_at: Optional[str] = None,
    ) -> None:
        """Updates lifecycle status of a transport mail message."""
        if status not in VALID_MAIL_STATUSES:
            raise ValueError(f"Invalid mail status: {status}")

        now = processed_at or (utc_now() if status in ('PROCESSED', 'REJECTED', 'DUPLICATE_IGNORED') else None)

        sql = """
            UPDATE mail_messages
            SET status = ?,
                rejection_reason = COALESCE(?, rejection_reason),
                job_id = COALESCE(?, job_id),
                run_id = COALESCE(?, run_id),
                processed_at = COALESCE(?, processed_at)
            WHERE message_id = ?;
        """
        self.execute(sql, (status, rejection_reason, job_id, run_id, now, message_id))

        # Mirror to mail_inbox
        self.execute(
            """
            UPDATE mail_inbox
            SET status = ?,
                rejection_reason = COALESCE(?, rejection_reason),
                run_id = COALESCE(?, run_id)
            WHERE message_id = ?;
            """,
            (status if status in ('VALIDATED', 'PROCESSED', 'REJECTED', 'DUPLICATE_IGNORED') else 'PENDING',
             rejection_reason, run_id, message_id),
        )
        self.commit()

    # =========================================================================
    # DOMAIN 16: MAIL CURSORS (historyId Synchronization)
    # =========================================================================

    def get_cursor(self, cursor_name: str = "GMAIL_USERS_WATCH") -> Optional[Dict[str, Any]]:
        """Retrieves monotonic historyId cursor record."""
        sql = "SELECT * FROM mail_cursors WHERE cursor_name = ?;"
        return self.fetchone_dict(sql, (cursor_name,))

    def advance_cursor(
        self,
        cursor_name: str,
        history_id: str,
        expiration_at: Optional[str] = None,
        resource_id: Optional[str] = None,
        synced_at: Optional[str] = None,
    ) -> None:
        """Advances authoritative historyId cursor monotonically."""
        now = synced_at or utc_now()
        sql = """
            INSERT INTO mail_cursors (cursor_name, history_id, last_synced_at, expiration_at, resource_id)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(cursor_name) DO UPDATE SET
                history_id = excluded.history_id,
                last_synced_at = excluded.last_synced_at,
                expiration_at = COALESCE(excluded.expiration_at, mail_cursors.expiration_at),
                resource_id = COALESCE(excluded.resource_id, mail_cursors.resource_id);
        """
        self.execute(sql, (cursor_name, history_id, now, expiration_at, resource_id))
        self.commit()

    # =========================================================================
    # COMPATIBILITY TABLE: mail_outbox
    # =========================================================================

    def enqueue_outbox(
        self,
        run_id: str,
        recipient: str,
        subject: str,
        body_markdown: str,
        attachment_path: Optional[str] = None,
        created_at: Optional[str] = None,
    ) -> int:
        """Enqueues outbound execution result reply."""
        now = created_at or utc_now()
        norm_attachment = normalize_repo_path(attachment_path) if attachment_path else None

        sql = """
            INSERT INTO mail_outbox (
                run_id, recipient, subject, body_markdown,
                attachment_path, status, attempts, created_at, sent_at, error_log
            ) VALUES (?, ?, ?, ?, ?, 'QUEUED', 0, ?, NULL, NULL);
        """
        cursor = self.execute(sql, (run_id, recipient, subject, body_markdown, norm_attachment, now))
        self.commit()
        return cursor.lastrowid  # type: ignore[return-value]

    def dequeue_outbox(self) -> Optional[Dict[str, Any]]:
        """Retrieves next pending message from the outbox."""
        sql = "SELECT * FROM mail_outbox WHERE status = 'QUEUED' ORDER BY created_at ASC LIMIT 1;"
        return self.fetchone_dict(sql)

    def mark_outbox_sent(self, outbox_id: int, sent_at: Optional[str] = None) -> None:
        """Marks outbound message as SENT."""
        now = sent_at or utc_now()
        sql = """
            UPDATE mail_outbox
            SET status = 'SENT',
                sent_at = ?,
                attempts = attempts + 1
            WHERE outbox_id = ?;
        """
        self.execute(sql, (now, outbox_id))
        self.commit()

    def mark_outbox_failed(self, outbox_id: int, error_log: str) -> None:
        """Marks outbound message attempt as FAILED."""
        sql = """
            UPDATE mail_outbox
            SET status = 'FAILED',
                error_log = ?,
                attempts = attempts + 1
            WHERE outbox_id = ?;
        """
        self.execute(sql, (error_log, outbox_id))
        self.commit()

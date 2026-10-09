"""SACL V1 Outbound Result Dispatcher & Outbox Queue.

Adheres strictly to:
- ADR-001 (Outbound Results Dispatch via Gmail REST API users.messages.send; Zero SMTP)
- docs/MAIL_PROTOCOL.md §4, §5.1 (RFC 2822 headers, MIME multipart, threadId, retries with jitter)
- Domain 16 / Compatibility Table 7 (mail_outbox in 001_init.sql)
"""

from __future__ import annotations

import datetime
import logging
from pathlib import Path
import random
import sqlite3
import time
from typing import Any, Dict, List, Optional, Tuple

from sacl.transport.envelope import build_outbound_mime
from sacl.transport.exceptions import TransportError
from sacl.transport.gmail_adapter import IGmailApiAdapter

logger = logging.getLogger("sacl.transport.outbox")

OUTBOX_RETRY_BACKOFF = [5.0, 15.0, 45.0, 120.0, 300.0]  # docs/MAIL_PROTOCOL.md §5.1
MAX_DISPATCH_RETRIES = 5
DEFAULT_SENDER = "uniquedraken@gmail.com"


class OutboxDispatcher:
    """Monitors SQLite mail_outbox table and dispatches results via Gmail API."""

    def __init__(
        self,
        gmail_adapter: IGmailApiAdapter,
        db_conn: sqlite3.Connection,
        sender_address: str = DEFAULT_SENDER,
        max_retries: int = MAX_DISPATCH_RETRIES,
        backoff_steps: Optional[List[float]] = None,
        sleeper: Optional[Any] = None,
    ) -> None:
        self.gmail_adapter = gmail_adapter
        self.db_conn = db_conn
        self.sender_address = sender_address
        self.max_retries = max_retries
        self.backoff_steps = backoff_steps or list(OUTBOX_RETRY_BACKOFF)
        self._sleeper = sleeper or time.sleep

    def enqueue_reply(
        self,
        run_id: str,
        recipient: str,
        subject: str,
        body_markdown: str,
        attachment_path: Optional[str] = None,
    ) -> int:
        """Enqueues a message in mail_outbox with status 'QUEUED'."""
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        cursor = self.db_conn.cursor()

        # Ensure run_id exists in runs table to satisfy FOREIGN KEY constraint
        cursor.execute("SELECT 1 FROM runs WHERE run_id = ?", (run_id,))
        if not cursor.fetchone():
            job_id = run_id
            if run_id.startswith("conflict-"):
                job_id = run_id[len("conflict-") :]
            cursor.execute("SELECT 1 FROM jobs WHERE job_id = ?", (job_id,))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT OR IGNORE INTO jobs (job_id, status, priority, created_at, updated_at) VALUES (?, 'RECEIVED', 0, ?, ?)",
                    (job_id, now_iso, now_iso),
                )
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
                (run_id, job_id, f"pkg-{job_id}", now_iso),
            )

        cursor.execute(
            """
            INSERT INTO mail_outbox (run_id, recipient, subject, body_markdown, attachment_path, status, attempts, created_at)
            VALUES (?, ?, ?, ?, ?, 'QUEUED', 0, ?)
            """,
            (run_id, recipient, subject, body_markdown, attachment_path, now_iso),
        )
        self.db_conn.commit()
        return int(cursor.lastrowid or 0)

    def dispatch_pending(self, max_messages: int = 10) -> int:
        """Processes up to max_messages from mail_outbox where status = 'QUEUED'."""
        cursor = self.db_conn.cursor()
        cursor.execute(
            """
            SELECT outbox_id, run_id, recipient, subject, body_markdown, attachment_path, attempts
            FROM mail_outbox
            WHERE status = 'QUEUED'
            ORDER BY outbox_id ASC
            LIMIT ?
            """,
            (max_messages,),
        )
        pending_rows = cursor.fetchall()
        dispatched_count = 0

        for row in pending_rows:
            outbox_id = row[0]
            run_id = row[1]
            recipient = row[2]
            subject = row[3]
            body_md = row[4]
            attach_path = row[5]
            attempts = row[6]

            success = self._dispatch_single(
                outbox_id=outbox_id,
                run_id=run_id,
                recipient=recipient,
                subject=subject,
                body_markdown=body_md,
                attachment_path=attach_path,
                current_attempts=attempts,
            )
            if success:
                dispatched_count += 1

        return dispatched_count

    def _dispatch_single(
        self,
        outbox_id: int,
        run_id: str,
        recipient: str,
        subject: str,
        body_markdown: str,
        attachment_path: Optional[str],
        current_attempts: int,
    ) -> bool:
        """Attempts to send a single outbox message with thread correlation and retries."""
        thread_id, in_reply_to = self._find_thread_correlation(run_id)

        # Load attachment bytes if path specified
        attachment_bytes: Optional[bytes] = None
        attachment_name: Optional[str] = None
        if attachment_path:
            p = Path(attachment_path)
            if p.exists() and p.is_file():
                attachment_bytes = p.read_bytes()
                attachment_name = p.name
            else:
                logger.warning("Outbox attachment path '%s' not found on disk", attachment_path)

        mime_bytes = build_outbound_mime(
            recipient=recipient,
            sender=self.sender_address,
            subject=subject,
            body_markdown=body_markdown,
            attachment_bytes=attachment_bytes,
            attachment_filename=attachment_name,
            in_reply_to=in_reply_to,
            references=in_reply_to,
        )

        attempt = current_attempts
        last_error = ""

        while attempt < self.max_retries:
            attempt += 1
            try:
                resp = self.gmail_adapter.send_message(
                    raw_mime_bytes=mime_bytes, thread_id=thread_id
                )
                sent_msg_id = resp.get("id", "unknown")
                now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

                # Mark SENT
                cursor = self.db_conn.cursor()
                cursor.execute(
                    """
                    UPDATE mail_outbox
                    SET status = 'SENT', attempts = ?, sent_at = ?, error_log = NULL
                    WHERE outbox_id = ?
                    """,
                    (attempt, now_iso, outbox_id),
                )
                self.db_conn.commit()
                logger.info(
                    "Outbox message %d dispatched successfully as Gmail message %s",
                    outbox_id,
                    sent_msg_id,
                )
                return True

            except Exception as e:
                last_error = str(e)
                logger.warning(
                    "Outbox dispatch failed (outbox_id=%d, attempt %d/%d): %s",
                    outbox_id,
                    attempt,
                    self.max_retries,
                    e,
                )

                if attempt < self.max_retries:
                    backoff_idx = min(attempt - 1, len(self.backoff_steps) - 1)
                    backoff = self.backoff_steps[backoff_idx] * random.uniform(0.8, 1.2)
                    self._sleeper(backoff)

        # Retries exhausted -> mark FAILED
        cursor = self.db_conn.cursor()
        cursor.execute(
            """
            UPDATE mail_outbox
            SET status = 'FAILED', attempts = ?, error_log = ?
            WHERE outbox_id = ?
            """,
            (attempt, last_error, outbox_id),
        )
        self.db_conn.commit()
        logger.error(
            "Outbox message %d failed permanently after %d attempts: %s",
            outbox_id,
            attempt,
            last_error,
        )
        return False

    def _find_thread_correlation(self, run_id: str) -> Tuple[Optional[str], Optional[str]]:
        """Finds thread_id and originating RFC Message-ID for thread correlation."""
        cursor = self.db_conn.cursor()
        # Query by run_id
        cursor.execute(
            """
            SELECT thread_id, message_id FROM mail_messages
            WHERE run_id = ? ORDER BY received_at DESC LIMIT 1
            """,
            (run_id,),
        )
        row = cursor.fetchone()
        if row:
            return (row[0], row[1])

        # If run_id looks like conflict-<job_id>, query by job_id
        if run_id.startswith("conflict-"):
            job_id = run_id[len("conflict-") :]
            cursor.execute(
                """
                SELECT thread_id, message_id FROM mail_messages
                WHERE job_id = ? ORDER BY received_at DESC LIMIT 1
                """,
                (job_id,),
            )
            row = cursor.fetchone()
            if row:
                return (row[0], row[1])

        return (None, None)

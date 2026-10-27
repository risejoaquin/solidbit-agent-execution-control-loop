"""SACL V1 Result Outbox Handoff Subsystem.

Enforces:
- STATE_MACHINE.md: Lifecycle progression RESULT_PACKAGED -> RESULT_SENT -> COMPLETED.
- docs/MAIL_PROTOCOL.md: Routing hint subject syntax [SACL][JOB][v1][<JOB_ID>] [RESULT] <VERDICT>.
- Domain 16 / Compatibility Table 7: Integration with SQLite table mail_outbox.
- ADR-001: Asynchronous results dispatch via Gmail transport.
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Union

from sacl.observability.audit import AuditEventEmitter
from sacl.observability.events import (
    Severity,
)
from sacl.results.models import OutboxHandoffResult

logger = logging.getLogger("sacl.results.outbox")

DEFAULT_RESULT_RECIPIENT = "uniquedraken@gmail.com"


def format_result_subject(job_id: str, verdict: str) -> str:
    """Formats canonical subject line with intake routing hint."""
    return f"[SACL][JOB][v1][{job_id}] [RESULT] {verdict}"


class ResultOutboxHandoff:
    """Manages the handoff of sealed execution result packages to the transport outbox."""

    def __init__(self, audit_emitter: Optional[AuditEventEmitter] = None) -> None:
        self.audit_emitter = audit_emitter

    def enqueue_result_to_outbox(
        self,
        run_id: str,
        job_id: str,
        body_markdown: str,
        attachment_path: Optional[Union[str, Path]],
        final_verdict: str,
        db_conn: sqlite3.Connection,
        recipient: str = DEFAULT_RESULT_RECIPIENT,
        custom_subject: Optional[str] = None,
    ) -> int:
        """Enqueues a packaged result message into SQLite mail_outbox table.

        Returns:
            outbox_id (int): Primary key of the inserted mail_outbox record.
        """
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        subject = custom_subject or format_result_subject(job_id, final_verdict)
        norm_attachment = str(attachment_path).replace("\\", "/") if attachment_path else None

        cursor = db_conn.cursor()

        # Insert into mail_outbox
        cursor.execute(
            """
            INSERT INTO mail_outbox (
                run_id, recipient, subject, body_markdown, attachment_path,
                status, attempts, created_at
            ) VALUES (?, ?, ?, ?, ?, 'QUEUED', 0, ?)
            """,
            (run_id, recipient, subject, body_markdown, norm_attachment, now_iso),
        )
        outbox_id = cursor.lastrowid or 0

        # Update results table with recipient
        cursor.execute(
            """
            UPDATE results
            SET delivered_to = ?
            WHERE run_id = ?
            """,
            (recipient, run_id),
        )

        db_conn.commit()

        # Emit audit event
        if self.audit_emitter:
            self.audit_emitter.emit(
                event_type="OUTBOX_ENQUEUED",
                severity=Severity.INFO,
                job_id=job_id,
                run_id=run_id,
                payload={
                    "outbox_id": outbox_id,
                    "recipient": recipient,
                    "subject": subject,
                    "attachment_path": norm_attachment,
                },
            )

        logger.info(
            "Enqueued result outbox message %d for run %s to %s with subject '%s'",
            outbox_id,
            run_id,
            recipient,
            subject,
        )
        return int(outbox_id)

    def dispatch_outbox_item(
        self,
        outbox_id: int,
        db_conn: sqlite3.Connection,
        dispatcher: Optional[Any] = None,
    ) -> OutboxHandoffResult:
        """Attempts immediate transmission of a queued mail_outbox entry.

        Parameters:
            outbox_id: Primary key of mail_outbox row.
            db_conn: Active SQLite connection.
            dispatcher: Optional callable, IGmailApiAdapter, or OutboxDispatcher.

        Returns:
            OutboxHandoffResult detailing dispatch success or queued state.
        """
        cursor = db_conn.cursor()
        cursor.execute(
            "SELECT run_id, recipient, subject, body_markdown, attachment_path, status, attempts FROM mail_outbox WHERE outbox_id = ?",
            (outbox_id,),
        )
        row = cursor.fetchone()
        if not row:
            raise KeyError(f"Outbox entry {outbox_id} not found in mail_outbox.")

        run_id, recipient, subject, body_markdown, attachment_path, current_status, attempts = row
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        if dispatcher is None:
            # No dispatcher provided; entry remains in QUEUED status for transport daemon
            return OutboxHandoffResult(
                outbox_id=outbox_id,
                run_id=run_id,
                recipient=recipient,
                subject=subject,
                status="QUEUED",
                dispatched=False,
                error_message=None,
            )

        # Attempt dispatch via provided dispatcher
        try:
            if hasattr(dispatcher, "dispatch_outbox_reply"):
                # ITransportGateway contract
                dispatcher.dispatch_outbox_reply(
                    recipient=recipient,
                    subject=subject,
                    body_markdown=body_markdown,
                    attachment_path=Path(attachment_path) if attachment_path else None,
                )
            elif hasattr(dispatcher, "send_message"):
                # GmailApiAdapter contract
                dispatcher.send_message(
                    to=recipient,
                    subject=subject,
                    body=body_markdown,
                    attachment=attachment_path,
                )
            elif callable(dispatcher):
                dispatcher(
                    recipient=recipient,
                    subject=subject,
                    body_markdown=body_markdown,
                    attachment_path=attachment_path,
                )
            else:
                raise TypeError(f"Unsupported dispatcher type: {type(dispatcher)}")

            # Update mail_outbox to SENT
            cursor.execute(
                """
                UPDATE mail_outbox
                SET status = 'SENT',
                    sent_at = ?,
                    attempts = attempts + 1
                WHERE outbox_id = ?
                """,
                (now_iso, outbox_id),
            )

            # Update results table delivery confirmation
            cursor.execute(
                """
                UPDATE results
                SET delivered_at = ?,
                    delivered_to = ?,
                    status = 'RESULT_SENT'
                WHERE run_id = ?
                """,
                (now_iso, recipient, run_id),
            )

            # Update runs table status to RESULT_SENT
            cursor.execute(
                "UPDATE runs SET status = 'RESULT_SENT' WHERE run_id = ?",
                (run_id,),
            )

            # Update jobs table status to RESULT_SENT
            cursor.execute(
                """
                UPDATE jobs
                SET status = 'RESULT_SENT',
                    updated_at = ?
                WHERE current_run_id = ? OR job_id = (SELECT job_id FROM runs WHERE run_id = ?)
                """,
                (now_iso, run_id, run_id),
            )

            db_conn.commit()

            # Emit audit event
            if self.audit_emitter:
                self.audit_emitter.emit(
                    event_type="RESULT_SENT",
                    severity=Severity.INFO,
                    run_id=run_id,
                    payload={
                        "outbox_id": outbox_id,
                        "recipient": recipient,
                        "sent_at": now_iso,
                    },
                )

            logger.info(
                "Successfully dispatched outbox result %d for run %s to %s",
                outbox_id,
                run_id,
                recipient,
            )
            return OutboxHandoffResult(
                outbox_id=outbox_id,
                run_id=run_id,
                recipient=recipient,
                subject=subject,
                status="SENT",
                dispatched=True,
                dispatched_at=now_iso,
            )

        except Exception as e:
            error_msg = str(e)
            cursor.execute(
                """
                UPDATE mail_outbox
                SET attempts = attempts + 1,
                    error_log = ?
                WHERE outbox_id = ?
                """,
                (error_msg, outbox_id),
            )
            db_conn.commit()
            logger.error("Failed to dispatch outbox result %d: %s", outbox_id, error_msg)
            return OutboxHandoffResult(
                outbox_id=outbox_id,
                run_id=run_id,
                recipient=recipient,
                subject=subject,
                status="FAILED",
                dispatched=False,
                error_message=error_msg,
            )

    def handoff_and_dispatch(
        self,
        run_id: str,
        job_id: str,
        body_markdown: str,
        attachment_path: Optional[Union[str, Path]],
        final_verdict: str,
        db_conn: sqlite3.Connection,
        dispatcher: Optional[Any] = None,
        recipient: str = DEFAULT_RESULT_RECIPIENT,
    ) -> OutboxHandoffResult:
        """Enqueues result and immediately triggers dispatch if dispatcher provided."""
        outbox_id = self.enqueue_result_to_outbox(
            run_id=run_id,
            job_id=job_id,
            body_markdown=body_markdown,
            attachment_path=attachment_path,
            final_verdict=final_verdict,
            db_conn=db_conn,
            recipient=recipient,
        )
        return self.dispatch_outbox_item(
            outbox_id=outbox_id,
            db_conn=db_conn,
            dispatcher=dispatcher,
        )


__all__ = [
    "ResultOutboxHandoff",
    "format_result_subject",
    "DEFAULT_RESULT_RECIPIENT",
]

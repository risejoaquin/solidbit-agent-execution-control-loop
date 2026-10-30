"""SACL V1 Durable Queue Primitives.

Implements durable relational queues with at-least-once delivery semantics,
priority scheduling, and concurrency-aware dispatching against SQLite.
"""

from __future__ import annotations

import sqlite3
from typing import Any, Dict, Optional

from sacl.contracts.invariants import JobSideStatus, JobStatus
from sacl.state.repositories.base import BaseRepository
from sacl.state.repositories.jobs import JobRepository
from sacl.state.repositories.mail import MailRepository
from sacl.state.repositories.runs import RunRepository
from sacl.state.utils import utc_now


class DurableJobQueue(BaseRepository):
    """Priority-based durable job dispatch queue enforcing project concurrency rules."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        super().__init__(conn)
        self.job_repo = JobRepository(conn)
        self.run_repo = RunRepository(conn)

    def enqueue_job(
        self,
        job_id: str,
        package_id: Optional[str] = None,
        project_id: Optional[str] = None,
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Places a job into the queue in state QUEUED."""
        return self.job_repo.create_job(
            job_id=job_id,
            package_id=package_id,
            project_id=project_id,
            status=JobStatus.QUEUED.value,
            priority=priority,
            metadata=metadata,
        )

    def dequeue_job(self, project_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Claims the highest-priority pending job whose project is not actively mutating.

        Under the Concurrency Baseline, exactly one mutating job per project may execute.
        If a project already has a run in RUNNING, DISPATCHED, or VERIFYING, queued jobs
        for that project remain in QUEUED state.
        """
        now = utc_now()
        # Find queued jobs ordered by priority DESC, created_at ASC
        candidate_sql = """
            SELECT * FROM jobs
            WHERE status = 'QUEUED'
            ORDER BY priority DESC, created_at ASC;
        """
        candidates = self.fetchall_dict(candidate_sql)

        for job in candidates:
            target_proj = job.get("project_id")
            if project_id and target_proj != project_id:
                continue

            # Check if project currently has active mutating run
            if target_proj and self.run_repo.has_active_mutating_run_for_project(target_proj):
                continue  # Defer this job; another is active for this project

            # Attempt atomic transition from QUEUED to DISPATCHED
            claim_sql = """
                UPDATE jobs
                SET status = 'DISPATCHED',
                    updated_at = ?
                WHERE job_id = ? AND status = 'QUEUED';
            """
            cursor = self.execute(claim_sql, (now, job["job_id"]))
            if cursor.rowcount > 0:
                self.commit()
                return self.job_repo.get_job(job["job_id"])

        return None

    def ack_job(self, job_id: str, final_status: str = JobStatus.COMPLETED.value) -> None:
        """Acknowledges successful completion of a job."""
        self.job_repo.update_job_status(job_id, status=final_status)

    def nack_job(self, job_id: str, error_summary: str, retry: bool = False) -> None:
        """Negative-acknowledges a job, marking it for retry or terminal failure."""
        status = JobSideStatus.RETRY_WAIT.value if retry else JobSideStatus.FAILED.value
        self.job_repo.update_job_status(job_id, status=status, error_summary=error_summary)

    def peek_job(self, project_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Peeks at the highest-priority pending job without claiming it."""
        return self.job_repo.peek_next_queued_job(project_id=project_id)

    def qsize(self, project_id: Optional[str] = None) -> int:
        """Returns the number of jobs currently in QUEUED status."""
        if project_id:
            sql = "SELECT COUNT(*) AS cnt FROM jobs WHERE status = 'QUEUED' AND project_id = ?;"
            row = self.fetchone_dict(sql, (project_id,))
        else:
            sql = "SELECT COUNT(*) AS cnt FROM jobs WHERE status = 'QUEUED';"
            row = self.fetchone_dict(sql)
        return int(row["cnt"]) if row else 0


class DurableMailQueue(BaseRepository):
    """Durable inbound mail transport queue with at-least-once semantics."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        super().__init__(conn)
        self.mail_repo = MailRepository(conn)

    def enqueue_inbound(
        self,
        message_id: str,
        sender: str,
        recipient: str,
        subject: str,
        nonce: str,
        attachment_sha: str,
        history_id: Optional[str] = None,
        thread_id: Optional[str] = None,
        snippet: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Enqueues inbound mail message for processing."""
        return self.mail_repo.record_inbound_message(
            message_id=message_id,
            sender=sender,
            recipient=recipient,
            subject=subject,
            nonce=nonce,
            attachment_sha=attachment_sha,
            status="QUEUED",
            history_id=history_id,
            thread_id=thread_id,
            snippet=snippet,
        )

    def dequeue_inbound(self) -> Optional[Dict[str, Any]]:
        """Atomically claims next pending inbound email message."""
        sql_peek = "SELECT message_id FROM mail_messages WHERE status = 'QUEUED' ORDER BY received_at ASC LIMIT 1;"
        row = self.fetchone_dict(sql_peek)
        if not row:
            return None

        msg_id = row["message_id"]
        sql_claim = "UPDATE mail_messages SET status = 'VALIDATED' WHERE message_id = ? AND status = 'QUEUED';"
        cursor = self.execute(sql_claim, (msg_id,))
        if cursor.rowcount > 0:
            self.commit()
            return self.mail_repo.get_message(msg_id)
        return None

    def ack_inbound(
        self, message_id: str, job_id: Optional[str] = None, run_id: Optional[str] = None
    ) -> None:
        """Marks inbound message as successfully PROCESSED."""
        self.mail_repo.update_message_status(
            message_id, status="PROCESSED", job_id=job_id, run_id=run_id
        )

    def nack_inbound(self, message_id: str, reason: str) -> None:
        """Marks inbound message as REJECTED."""
        self.mail_repo.update_message_status(message_id, status="REJECTED", rejection_reason=reason)

    def peek_inbound(self) -> Optional[Dict[str, Any]]:
        """Peeks at next pending inbound message without claiming it."""
        sql = "SELECT message_id FROM mail_messages WHERE status = 'QUEUED' ORDER BY received_at ASC LIMIT 1;"
        row = self.fetchone_dict(sql)
        if not row:
            return None
        return self.mail_repo.get_message(row["message_id"])

    def qsize(self) -> int:
        """Returns the number of inbound messages currently in QUEUED status."""
        sql = "SELECT COUNT(*) AS cnt FROM mail_messages WHERE status = 'QUEUED';"
        row = self.fetchone_dict(sql)
        return int(row["cnt"]) if row else 0


class DurableOutboxQueue(BaseRepository):
    """Durable outbound execution result reply queue."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        super().__init__(conn)
        self.mail_repo = MailRepository(conn)

    def enqueue(
        self,
        run_id: str,
        recipient: str,
        subject: str,
        body_markdown: str,
        attachment_path: Optional[str] = None,
    ) -> int:
        """Enqueues result summary for outbound dispatch."""
        return self.mail_repo.enqueue_outbox(
            run_id=run_id,
            recipient=recipient,
            subject=subject,
            body_markdown=body_markdown,
            attachment_path=attachment_path,
        )

    def dequeue(self) -> Optional[Dict[str, Any]]:
        """Retrieves next pending outbox message."""
        return self.mail_repo.dequeue_outbox()

    def peek(self) -> Optional[Dict[str, Any]]:
        """Peeks at next pending outbound message without claiming it."""
        sql = "SELECT * FROM mail_outbox WHERE status = 'QUEUED' ORDER BY created_at ASC LIMIT 1;"
        return self.fetchone_dict(sql)

    def qsize(self) -> int:
        """Returns the number of outbound messages currently in QUEUED status."""
        sql = "SELECT COUNT(*) AS cnt FROM mail_outbox WHERE status = 'QUEUED';"
        row = self.fetchone_dict(sql)
        return int(row["cnt"]) if row else 0

    def ack(self, outbox_id: int) -> None:
        """Marks message as SENT."""
        self.mail_repo.mark_outbox_sent(outbox_id)

    def nack(self, outbox_id: int, error_log: str) -> None:
        """Marks message as FAILED with diagnostic log."""
        self.mail_repo.mark_outbox_failed(outbox_id, error_log)

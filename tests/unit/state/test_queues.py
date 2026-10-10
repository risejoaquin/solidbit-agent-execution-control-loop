"""Unit tests for SACL V1 Durable Queue Primitives.

Covers DurableJobQueue (priority scheduling, project concurrency baseline),
DurableMailQueue (inbound transport queue), and DurableOutboxQueue (result reply queue).
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path
from typing import Generator

# Ensure repo root is on sys.path
_repo_root = Path(__file__).resolve().parents[3]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

import pytest

from sacl.contracts.invariants import JobSideStatus, JobStatus
from sacl.state.connection import create_connection
from sacl.state.migrations import MigrationRunner
from sacl.state.queues import DurableJobQueue, DurableMailQueue, DurableOutboxQueue
from sacl.state.repositories.jobs import JobRepository
from sacl.state.repositories.projects import ProjectRepository
from sacl.state.repositories.runs import RunRepository


@pytest.fixture
def queue_db(migration_sql_path: Path) -> Generator[sqlite3.Connection, None, None]:
    conn = create_connection(":memory:")
    runner = MigrationRunner(migration_sql_path.parent)
    runner.apply_all(conn)
    yield conn
    conn.close()


def test_durable_job_queue_priority_and_fifo(queue_db: sqlite3.Connection) -> None:
    """Verifies priority ordering with FIFO tie-breaking for queued jobs."""
    q = DurableJobQueue(queue_db)

    # Enqueue low, high, and medium priority jobs
    q.enqueue_job("job-low", priority=1)
    q.enqueue_job("job-high", priority=100)
    q.enqueue_job("job-mid", priority=50)

    assert q.qsize() == 3
    assert q.peek_job()["job_id"] == "job-high"

    # Dequeue highest priority first
    first = q.dequeue_job()
    assert first is not None
    assert first["job_id"] == "job-high"
    assert first["status"] == JobStatus.DISPATCHED.value

    # Next is mid
    second = q.dequeue_job()
    assert second is not None
    assert second["job_id"] == "job-mid"
    assert second["status"] == JobStatus.DISPATCHED.value

    # Next is low
    third = q.dequeue_job()
    assert third is not None
    assert third["job_id"] == "job-low"

    # Queue empty
    assert q.dequeue_job() is None
    assert q.qsize() == 0


def test_durable_job_queue_concurrency_baseline_exclusion(queue_db: sqlite3.Connection) -> None:
    """Verifies that project with active mutating run does not dequeue subsequent jobs."""
    ProjectRepository(queue_db).register_project("proj-ecommerce", "Ecommerce", "C:/repos/eco")
    run_repo = RunRepository(queue_db)
    q = DurableJobQueue(queue_db)

    # Enqueue two jobs for proj-ecommerce
    q.enqueue_job("job-eco-1", project_id="proj-ecommerce", priority=10)
    q.enqueue_job("job-eco-2", project_id="proj-ecommerce", priority=20)

    # Dequeue first job (job-eco-2 has higher priority)
    claimed_1 = q.dequeue_job()
    assert claimed_1 is not None
    assert claimed_1["job_id"] == "job-eco-2"

    # Simulate run started and in RUNNING state for proj-ecommerce
    run_repo.create_run(
        run_id="run-eco-2",
        job_id="job-eco-2",
        package_id="pkg-1",
        project="proj-ecommerce",
        project_id="proj-ecommerce",
        repository="org/repo",
        mode="isolated_branch",
        source_orchestrator="C:/orch",
        target_repo_path="C:/repos/eco",
        run_dir="runs/run-eco-2",
        status="RUNNING",
    )

    # Attempt to dequeue remaining job for proj-ecommerce -> must return None (concurrency lock)
    claimed_blocked = q.dequeue_job(project_id="proj-ecommerce")
    assert claimed_blocked is None
    assert q.qsize(project_id="proj-ecommerce") == 1

    # Once active run completes, queued job becomes eligible
    run_repo.update_run_status("run-eco-2", status="COMPLETED")
    claimed_after = q.dequeue_job(project_id="proj-ecommerce")
    assert claimed_after is not None
    assert claimed_after["job_id"] == "job-eco-1"


def test_durable_job_queue_ack_and_nack(queue_db: sqlite3.Connection) -> None:
    """Verifies job ack and nack transitions."""
    q = DurableJobQueue(queue_db)
    job_repo = JobRepository(queue_db)

    q.enqueue_job("job-ack-test", priority=5)
    claimed = q.dequeue_job()
    assert claimed is not None

    # ACK
    q.ack_job("job-ack-test")
    assert job_repo.get_job("job-ack-test")["status"] == JobStatus.COMPLETED.value

    # NACK with retry
    q.enqueue_job("job-nack-test", priority=5)
    q.dequeue_job()
    q.nack_job("job-nack-test", error_summary="Transient timeout", retry=True)
    nack_job = job_repo.get_job("job-nack-test")
    assert nack_job["status"] == JobSideStatus.RETRY_WAIT.value
    assert nack_job["error_summary"] == "Transient timeout"

    # NACK terminal failure
    q.nack_job("job-nack-test", error_summary="Fatal syntax error", retry=False)
    assert job_repo.get_job("job-nack-test")["status"] == JobSideStatus.FAILED.value


def test_durable_mail_queue_lifecycle(queue_db: sqlite3.Connection) -> None:
    """Verifies DurableMailQueue enqueue, peek, dequeue, ack, and nack."""
    q = DurableMailQueue(queue_db)

    assert q.qsize() == 0
    q.enqueue_inbound(
        message_id="msg-101",
        sender="client@example.com",
        recipient="uniquedraken@gmail.com",
        subject="[SACL][JOB][v1] Execute Wave",
        nonce="nonce-inbound-101",
        attachment_sha="sha256-abc-123",
    )
    assert q.qsize() == 1

    # Peek without claiming
    peeked = q.peek_inbound()
    assert peeked is not None
    assert peeked["message_id"] == "msg-101"
    assert q.qsize() == 1

    # Dequeue claims and transitions to VALIDATED
    claimed = q.dequeue_inbound()
    assert claimed is not None
    assert claimed["message_id"] == "msg-101"
    assert claimed["status"] == "VALIDATED"
    assert q.qsize() == 0

    # ACK inbound (create job in jobs table first to satisfy foreign key)
    JobRepository(queue_db).create_job("job-created-1", None, None)
    q.ack_inbound("msg-101", job_id="job-created-1")
    msg = q.mail_repo.get_message("msg-101")
    assert msg["status"] == "PROCESSED"
    assert msg["job_id"] == "job-created-1"

    # Enqueue second message for NACK
    q.enqueue_inbound(
        message_id="msg-102",
        sender="untrusted@example.com",
        recipient="uniquedraken@gmail.com",
        subject="Spam",
        nonce="nonce-inbound-102",
        attachment_sha="sha256-bad",
    )
    q.dequeue_inbound()
    q.nack_inbound("msg-102", reason="Untrusted sender")
    msg_rejected = q.mail_repo.get_message("msg-102")
    assert msg_rejected["status"] == "REJECTED"
    assert msg_rejected["rejection_reason"] == "Untrusted sender"


def test_durable_outbox_queue_lifecycle(queue_db: sqlite3.Connection) -> None:
    """Verifies DurableOutboxQueue enqueue, peek, dequeue, ack, and nack."""
    q = DurableOutboxQueue(queue_db)
    JobRepository(queue_db).create_job("job-out", None, None)
    RunRepository(queue_db).create_run(
        "run-out-1", "job-out", "pkg-1", "proj", "risejoaquin/proj", "mode", "src", "target", "runs/r", "RUNNING"
    )

    assert q.qsize() == 0
    outbox_id = q.enqueue(
        run_id="run-out-1",
        recipient="uniquedraken@gmail.com",
        subject="[SACL][RESULT] Wave Completed",
        body_markdown="# All 5 agents passed",
        attachment_path="artifacts/runs/run-out-1/response.zip",
    )
    assert outbox_id > 0
    assert q.qsize() == 1

    # Peek
    peeked = q.peek()
    assert peeked is not None
    assert peeked["outbox_id"] == outbox_id
    assert q.qsize() == 1

    # Dequeue
    claimed = q.dequeue()
    assert claimed is not None
    assert claimed["outbox_id"] == outbox_id

    # ACK
    q.ack(outbox_id)
    assert q.dequeue() is None
    assert q.qsize() == 0

    # NACK test
    outbox_id_2 = q.enqueue(
        run_id="run-out-1",
        recipient="uniquedraken@gmail.com",
        subject="[SACL][RESULT] Wave Retry",
        body_markdown="Pending retry",
    )
    q.nack(outbox_id_2, error_log="SMTP Connection Refused")
    cursor = queue_db.cursor()
    cursor.execute("SELECT status, attempts, error_log FROM mail_outbox WHERE outbox_id = ?;", (outbox_id_2,))
    row = cursor.fetchone()
    assert row["status"] == "FAILED"
    assert row["attempts"] == 1
    assert "SMTP Connection Refused" in row["error_log"]

"""Tests for Same-Run Resumption Engine.

Constitutional Invariant (SB-FREEZE-P1-06, ADR-007):
Approvals resume the SAME logical run; they do NOT spawn disconnected or unlinked orphan runs.
resume_run must strictly evaluate to True.
When an approval grant is attested, the waiting job and run transition back to RUNNING
under the identical run_id.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import sqlite3
import pytest

from sacl.approval.manager import BoundedApprovalManager
from sacl.approval.models import ApprovalToken, Approver
from sacl.approval.resumption import SameRunResumptionManager
from sacl.approval.validator import format_iso_datetime
from sacl.contracts.exceptions import (
    ApprovalExpiredError,
    HardDenyViolation,
    PolicyDeniedError,
)
from sacl.contracts.invariants import ApprovalChannel, JobSideStatus


@pytest.fixture
def setup_waiting_run(sqlite_memory_db: sqlite3.Connection):
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cursor = sqlite_memory_db.cursor()

    cursor.execute(
        """
        INSERT INTO jobs (job_id, status, priority, created_at, updated_at, current_run_id)
        VALUES ('job-resume-001', 'WAITING_APPROVAL', 0, ?, ?, 'run-resume-001')
        """,
        (now_iso, now_iso),
    )
    cursor.execute(
        """
        INSERT INTO runs (
            run_id, job_id, package_id, project, repository, mode,
            source_orchestrator, target_repo_path, run_dir, status,
            ready_for_integration, started_at
        ) VALUES (
            'run-resume-001', 'job-resume-001', 'pkg-001', 'solidbit', 'org/repo', 'isolated_branch',
            '', '', '', 'WAITING_APPROVAL', 'NO', ?
        )
        """,
        (now_iso,),
    )
    cursor.execute(
        """
        INSERT INTO agents (
            agent_id, run_id, stage_id, node_id, status, result_verdict,
            prompt_path, report_path, stdout_path, stderr_path, started_at, updated_at
        ) VALUES (
            'AG-WORKER-1', 'run-resume-001', 1, 'node-1', 'WAITING_APPROVAL', 'UNKNOWN',
            'prompt.md', 'report.md', 'stdout.log', 'stderr.log', ?, ?
        )
        """,
        (now_iso, now_iso),
    )
    sqlite_memory_db.commit()

    return "job-resume-001", "run-resume-001"


def test_same_run_resumption_approved_success(
    sqlite_memory_db: sqlite3.Connection, setup_waiting_run
) -> None:
    job_id, run_id = setup_waiting_run
    resumption_mgr = SameRunResumptionManager(db_conn=sqlite_memory_db)

    future_time = datetime.now(timezone.utc) + timedelta(hours=1)
    token = ApprovalToken(
        request_id="REQ-20261007-001",
        job_id=job_id,
        run_id=run_id,
        action="STAGE_CONTINUATION",
        scope=["docs/*"],
        expires_at=format_iso_datetime(future_time),
        decision="APPROVED",
        approver=Approver(identity="Joaquín", channel=ApprovalChannel.CLI.value),
        resume_run=True,
        cannot_override_hard_deny=True,
    )

    outcome = resumption_mgr.resume_run(token=token, target_status="RUNNING")

    assert outcome.success is True
    assert outcome.run_id == run_id  # Identical run_id! No new run spawned
    assert outcome.status == "RUNNING"

    cursor = sqlite_memory_db.cursor()
    # Verify jobs table transitioned to RUNNING
    cursor.execute("SELECT status FROM jobs WHERE job_id = ?", (job_id,))
    assert cursor.fetchone()[0] == "RUNNING"

    # Verify runs table transitioned to RUNNING
    cursor.execute("SELECT status FROM runs WHERE run_id = ?", (run_id,))
    assert cursor.fetchone()[0] == "RUNNING"

    # Verify waiting agent unpaused to READY
    cursor.execute("SELECT status FROM agents WHERE run_id = ? AND agent_id = 'AG-WORKER-1'", (run_id,))
    assert cursor.fetchone()[0] == "READY"

    # Verify exactly 1 run exists in runs table (no orphan runs created)
    cursor.execute("SELECT COUNT(*) FROM runs WHERE job_id = ?", (job_id,))
    assert cursor.fetchone()[0] == 1


def test_same_run_resumption_rejected_blocks_run(
    sqlite_memory_db: sqlite3.Connection, setup_waiting_run
) -> None:
    job_id, run_id = setup_waiting_run
    resumption_mgr = SameRunResumptionManager(db_conn=sqlite_memory_db)

    future_time = datetime.now(timezone.utc) + timedelta(hours=1)
    token = ApprovalToken(
        request_id="REQ-20261007-002",
        job_id=job_id,
        run_id=run_id,
        action="UNSAFE_OPERATION",
        scope=["*"],
        expires_at=format_iso_datetime(future_time),
        decision="REJECTED",
        approver=Approver(identity="Joaquín", channel=ApprovalChannel.CLI.value),
        resume_run=True,
        cannot_override_hard_deny=True,
    )

    outcome = resumption_mgr.resume_run(token=token)

    assert outcome.success is False
    assert outcome.status == "BLOCKED"

    cursor = sqlite_memory_db.cursor()
    cursor.execute("SELECT status FROM jobs WHERE job_id = ?", (job_id,))
    assert cursor.fetchone()[0] == "BLOCKED"

    cursor.execute("SELECT status FROM runs WHERE run_id = ?", (run_id,))
    assert cursor.fetchone()[0] == "BLOCKED"

    cursor.execute("SELECT status FROM agents WHERE run_id = ? AND agent_id = 'AG-WORKER-1'", (run_id,))
    assert cursor.fetchone()[0] == "BLOCKED"


def test_same_run_resumption_deferred_leaves_paused(
    sqlite_memory_db: sqlite3.Connection, setup_waiting_run
) -> None:
    job_id, run_id = setup_waiting_run
    resumption_mgr = SameRunResumptionManager(db_conn=sqlite_memory_db)

    future_time = datetime.now(timezone.utc) + timedelta(hours=1)
    token = ApprovalToken(
        request_id="REQ-20261007-003",
        job_id=job_id,
        run_id=run_id,
        action="STAGE_CONTINUATION",
        scope=["docs/*"],
        expires_at=format_iso_datetime(future_time),
        decision="DEFERRED",
        approver=Approver(identity="Joaquín", channel=ApprovalChannel.CLI.value),
        resume_run=True,
        cannot_override_hard_deny=True,
    )

    outcome = resumption_mgr.resume_run(token=token)

    assert outcome.success is False
    assert outcome.status == "WAITING_APPROVAL"


def test_resumption_fails_closed_if_resume_run_is_false(
    sqlite_memory_db: sqlite3.Connection, setup_waiting_run
) -> None:
    job_id, run_id = setup_waiting_run
    resumption_mgr = SameRunResumptionManager(db_conn=sqlite_memory_db)

    future_time = datetime.now(timezone.utc) + timedelta(hours=1)
    token = ApprovalToken(
        request_id="REQ-20261007-004",
        job_id=job_id,
        run_id=run_id,
        action="STAGE_CONTINUATION",
        scope=["docs/*"],
        expires_at=format_iso_datetime(future_time),
        decision="APPROVED",
        approver=Approver(identity="Joaquín", channel=ApprovalChannel.CLI.value),
        resume_run=False,  # Invariant violation!
        cannot_override_hard_deny=True,
    )

    with pytest.raises(PolicyDeniedError) as excinfo:
        resumption_mgr.resume_run(token=token)
    assert "resume_run=False" in str(excinfo.value)


def test_resumption_fails_closed_if_cannot_override_hard_deny_is_false(
    sqlite_memory_db: sqlite3.Connection, setup_waiting_run
) -> None:
    job_id, run_id = setup_waiting_run
    resumption_mgr = SameRunResumptionManager(db_conn=sqlite_memory_db)

    future_time = datetime.now(timezone.utc) + timedelta(hours=1)
    token = ApprovalToken(
        request_id="REQ-20261007-005",
        job_id=job_id,
        run_id=run_id,
        action="STAGE_CONTINUATION",
        scope=["docs/*"],
        expires_at=format_iso_datetime(future_time),
        decision="APPROVED",
        approver=Approver(identity="Joaquín", channel=ApprovalChannel.CLI.value),
        resume_run=True,
        cannot_override_hard_deny=False,  # Invariant violation!
    )

    with pytest.raises(HardDenyViolation):
        resumption_mgr.resume_run(token=token)


def test_resumption_expired_token_fails_closed(
    sqlite_memory_db: sqlite3.Connection, setup_waiting_run
) -> None:
    job_id, run_id = setup_waiting_run
    resumption_mgr = SameRunResumptionManager(db_conn=sqlite_memory_db)

    past_time = datetime.now(timezone.utc) - timedelta(minutes=10)
    token = ApprovalToken(
        request_id="REQ-20261007-006",
        job_id=job_id,
        run_id=run_id,
        action="STAGE_CONTINUATION",
        scope=["docs/*"],
        expires_at=format_iso_datetime(past_time),
        decision="APPROVED",
        approver=Approver(identity="Joaquín", channel=ApprovalChannel.CLI.value),
        resume_run=True,
        cannot_override_hard_deny=True,
    )

    with pytest.raises(ApprovalExpiredError):
        resumption_mgr.resume_run(token=token)

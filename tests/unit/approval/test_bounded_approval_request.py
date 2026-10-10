"""Tests for Bounded Approval Request Generation & Lifecycle.

Constitutional Invariants (ADR-007, SB-FREEZE-P1-06):
- Approval requests are bound to (job_id, action, scope, request_id, expires_at).
- Constitutional hard denials can NEVER be requested or approved (Hard deny always wins).
- Requests transition jobs and runs to WAITING_APPROVAL.
- Expiration is strictly fail-closed.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import sqlite3
import pytest

from sacl.approval.manager import BoundedApprovalManager
from sacl.approval.models import ApprovalRequest
from sacl.approval.validator import format_iso_datetime
from sacl.contracts.exceptions import HardDenyViolation
from sacl.contracts.invariants import HARD_DENIED_ACTIONS, JobSideStatus


@pytest.fixture
def manager(sqlite_memory_db: sqlite3.Connection) -> BoundedApprovalManager:
    # Seed a job and run to satisfy foreign key constraints
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cursor = sqlite_memory_db.cursor()
    cursor.execute(
        """
        INSERT INTO jobs (job_id, status, priority, created_at, updated_at)
        VALUES ('job-req-001', 'RUNNING', 0, ?, ?)
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
            'run-req-001', 'job-req-001', 'pkg-001', 'solidbit', 'org/repo', 'isolated_branch',
            '', '', '', 'RUNNING', 'NO', ?
        )
        """,
        (now_iso,),
    )
    sqlite_memory_db.commit()
    return BoundedApprovalManager(db_conn=sqlite_memory_db)


def test_create_approval_request_success(manager: BoundedApprovalManager) -> None:
    req_id = manager.create_approval_request(
        job_id="job-req-001",
        action="STAGE_CONTINUATION",
        scope=["docs/*", "schemas/*"],
        run_id="run-req-001",
        ttl_seconds=1800,
        reason="Stage 2 continuation requires human sign-off.",
    )

    assert req_id.startswith("REQ-")
    req = manager.get_request(req_id)
    assert req is not None
    assert req.job_id == "job-req-001"
    assert req.run_id == "run-req-001"
    assert req.action == "STAGE_CONTINUATION"
    assert req.scope == ["docs/*", "schemas/*"]
    assert req.status == "PENDING"
    assert req.reason == "Stage 2 continuation requires human sign-off."


@pytest.mark.parametrize(
    "hard_denied_action",
    [
        "remote_production_execution",
        "github_merge",
        "production_db_write",
        "secret_export",
        "arbitrary_remote_code",
        "main_branch_execution",
        "primary_checkout_mutation",
        "hard_reset",
        "auto_stash",
        "git_merge",
        "remote_deploy",
        "production_db_mutation",
        "main_push",
    ],
)
def test_create_approval_request_hard_deny_prohibited(
    manager: BoundedApprovalManager, hard_denied_action: str
) -> None:
    """Cannot create approval requests for hard denied actions (Hard Deny Supremacy)."""
    with pytest.raises(HardDenyViolation) as excinfo:
        manager.create_approval_request(
            job_id="job-req-001",
            action=hard_denied_action,
            scope=["*"],
            run_id="run-req-001",
        )
    assert "strictly hard-denied" in str(excinfo.value)


def test_create_approval_request_transitions_sqlite_state(
    manager: BoundedApprovalManager, sqlite_memory_db: sqlite3.Connection
) -> None:
    """Creating a request transitions jobs and runs to WAITING_APPROVAL."""
    req_id = manager.create_approval_request(
        job_id="job-req-001",
        action="BRANCH_INTEGRATION",
        scope=["feature/test"],
        run_id="run-req-001",
    )

    cursor = sqlite_memory_db.cursor()
    # Check jobs table status
    cursor.execute("SELECT status FROM jobs WHERE job_id = 'job-req-001'")
    job_status = cursor.fetchone()[0]
    assert job_status == JobSideStatus.WAITING_APPROVAL.value

    # Check runs table status
    cursor.execute("SELECT status FROM runs WHERE run_id = 'run-req-001'")
    run_status = cursor.fetchone()[0]
    assert run_status == JobSideStatus.WAITING_APPROVAL.value

    # Check approvals table row
    cursor.execute("SELECT request_id, action, status, decision FROM approvals WHERE request_id = ?", (req_id,))
    appr_row = cursor.fetchone()
    assert appr_row[0] == req_id
    assert appr_row[1] == "BRANCH_INTEGRATION"
    assert appr_row[2] == "PENDING"
    assert appr_row[3] == "PENDING"


def test_check_and_expire_requests(
    manager: BoundedApprovalManager, sqlite_memory_db: sqlite3.Connection
) -> None:
    """Pending requests past expires_at are marked EXPIRED fail-closed."""
    # Create request with 10 second TTL
    req_id = manager.create_approval_request(
        job_id="job-req-001",
        action="SPECIFICATION_MATERIALIZATION",
        scope=["docs/*"],
        ttl_seconds=10,
    )

    # Fast forward reference time by 1 hour
    future_time = datetime.now(timezone.utc) + timedelta(hours=1)
    expired_count = manager.check_and_expire_requests(reference_time=future_time)
    assert expired_count == 1

    req = manager.get_request(req_id)
    assert req.status == "EXPIRED"

    cursor = sqlite_memory_db.cursor()
    cursor.execute("SELECT status FROM approvals WHERE request_id = ?", (req_id,))
    assert cursor.fetchone()[0] == "EXPIRED"


def test_list_pending_requests(manager: BoundedApprovalManager) -> None:
    """Lists pending requests filtered by job_id or globally."""
    r1 = manager.create_approval_request(job_id="job-req-001", action="ACTION_A", scope=["*"])
    pending = manager.list_pending_requests(job_id="job-req-001")
    assert len(pending) == 1
    assert pending[0].request_id == r1

    empty = manager.list_pending_requests(job_id="non-existent-job")
    assert len(empty) == 0

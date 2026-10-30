"""Integration tests for SACL V1 Bounded Approvals and Same-Run Resumption.

Tests:
1. Constitutional Hard Deny Supremacy (ADR-007, SB-FREEZE-P1-06)
2. Bounded Approval Lifecycle & SQLite State Transitions (Domain 10)
3. Same-Run Resumption Invariants (same run_id, unpausing WAITING_APPROVAL agents)
4. Expiry and Rejection Handling
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from sacl.approval.manager import BoundedApprovalManager
from sacl.approval.models import Approver
from sacl.approval.resumption import SameRunResumptionManager
from sacl.contracts.exceptions import (
    ApprovalExpiredError,
    HardDenyViolation,
)
from sacl.contracts.invariants import (
    ApprovalChannel,
    ApprovalDecision,
    JobSideStatus,
)
from sacl.state.store import SqliteStateStore


@pytest.fixture
def state_store(tmp_path: Path) -> SqliteStateStore:
    """Provisions an initialized SQLite operational state store."""
    db_file = tmp_path / "sacl_ops_test.db"
    store = SqliteStateStore(db_path=db_file, auto_migrate=True)
    return store


@pytest.fixture
def populated_db(state_store: SqliteStateStore) -> sqlite3.Connection:
    """Sets up a test project, job, run, and agent record in SQLite."""
    conn = state_store.connection

    # 1. Project
    state_store.projects.register_project(
        project_id="proj-integ-1",
        name="Integration Test Project",
        root_path="/repos/test-proj",
    )

    # 2. Package
    state_store.packages.record_package(
        package_id="pkg-integ-1",
        archive_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        manifest={"schema": "solidbit.execution-package.v1"},
        storage_path="/storage/pkg-integ-1.zip",
        project_id="proj-integ-1",
    )

    # 3. Job
    state_store.jobs.create_job(
        job_id="job-integ-1",
        package_id="pkg-integ-1",
        project_id="proj-integ-1",
        status="RUNNING",
    )

    # 4. Run
    state_store.runs.create_run(
        run_id="run-integ-1",
        job_id="job-integ-1",
        package_id="pkg-integ-1",
        project_id="proj-integ-1",
        project="Integration Test Project",
        repository="solidbit/test-repo",
        mode="isolated_branch_development",
        source_orchestrator="/orch",
        target_repo_path="/repos/test-proj",
        run_dir="/runs/run-integ-1",
        status="RUNNING",
    )

    # Update job current_run_id
    state_store.jobs.update_job_status(
        job_id="job-integ-1",
        status="RUNNING",
        current_run_id="run-integ-1",
    )

    # 5. Agent in WAITING_APPROVAL
    state_store.agents.record_agent(
        agent_id="AG-WORKER-1",
        run_id="run-integ-1",
        status="WAITING_APPROVAL",
        prompt_path="/runs/run-integ-1/prompts/AG-WORKER-1.md",
        report_path="/runs/run-integ-1/reports/AG-WORKER-1.REPORT.md",
        stdout_path="/runs/run-integ-1/logs/AG-WORKER-1.stdout.log",
        stderr_path="/runs/run-integ-1/logs/AG-WORKER-1.stderr.log",
    )

    conn.commit()
    return conn


class TestApprovalIntegration:
    """Integration suite verifying bounded approvals and resumption."""

    def test_hard_deny_supremacy_blocks_approval_request(self, populated_db: sqlite3.Connection):
        """Verifies that requesting approval for any hard-denied action is rejected fail-closed."""
        manager = BoundedApprovalManager(db_conn=populated_db)

        # Ensure all actions in HARD_DENIED_ACTIONS raise HardDenyViolation
        for denied_action in ["deploy", "github_merge", "production_db_write", "secret_export"]:
            with pytest.raises(HardDenyViolation) as exc_info:
                manager.create_approval_request(
                    job_id="job-integ-1",
                    action=denied_action,
                    scope=["main"],
                    run_id="run-integ-1",
                )
            assert "strictly hard-denied" in str(exc_info.value) or "Hard denial violated" in str(
                exc_info.value
            )

    def test_bounded_approval_lifecycle_and_state_transitions(
        self, populated_db: sqlite3.Connection
    ):
        """Verifies approval request transitions job/run to WAITING_APPROVAL, and grant issues token."""
        manager = BoundedApprovalManager(db_conn=populated_db)

        # 1. Create valid approval request for branch push
        request_id = manager.create_approval_request(
            job_id="job-integ-1",
            action="github_branch_push",
            scope=["feature/integ-branch"],
            run_id="run-integ-1",
            ttl_seconds=3600,
            reason="Integration branch push requires human approval",
        )
        assert request_id.startswith("REQ-")

        # Verify DB state transitioned to WAITING_APPROVAL
        cur = populated_db.cursor()
        cur.execute("SELECT status FROM jobs WHERE job_id = 'job-integ-1'")
        assert cur.fetchone()[0] == JobSideStatus.WAITING_APPROVAL.value

        cur.execute("SELECT status FROM runs WHERE run_id = 'run-integ-1'")
        assert cur.fetchone()[0] == JobSideStatus.WAITING_APPROVAL.value

        # Verify approval row recorded in DB
        cur.execute(
            "SELECT action, status, decision FROM approvals WHERE request_id = ?", (request_id,)
        )
        appr_row = cur.fetchone()
        assert appr_row[0] == "github_branch_push"
        assert appr_row[1] == "PENDING"
        assert appr_row[2] == "PENDING"

        # 2. Grant sovereign human approval
        approver = Approver(
            identity="lead-operator",
            channel=ApprovalChannel.CLI.value,
        )
        token = manager.record_decision(
            request_id=request_id,
            decision=ApprovalDecision.APPROVED.value,
            approver=approver,
            notes="Authorized for branch deployment",
            signature="sig-hmac-sha256-verified-lead",
        )

        assert token.decision == ApprovalDecision.APPROVED.value
        assert token.resume_run is True
        assert token.cannot_override_hard_deny is True

        # Verify approvals table in DB updated
        cur.execute(
            "SELECT status, decision, approver FROM approvals WHERE request_id = ?", (request_id,)
        )
        updated_row = cur.fetchone()
        assert updated_row[0] == "APPROVED"
        assert updated_row[1] == "APPROVED"
        assert "lead-operator" in updated_row[2]

    def test_same_run_resumption_engine(self, populated_db: sqlite3.Connection):
        """Verifies same-run resumption unpauses the run, job, and agents under the exact same run_id."""
        manager = BoundedApprovalManager(db_conn=populated_db)
        resumption_mgr = SameRunResumptionManager(db_conn=populated_db)

        # Create and approve request
        request_id = manager.create_approval_request(
            job_id="job-integ-1",
            action="github_branch_push",
            scope=["feature/integ-branch"],
            run_id="run-integ-1",
            ttl_seconds=3600,
        )
        approver = Approver(identity="admin", channel=ApprovalChannel.CLI.value)
        token = manager.record_decision(
            request_id=request_id,
            decision=ApprovalDecision.APPROVED.value,
            approver=approver,
            signature="valid-sig",
        )

        # Execute Same-Run Resumption
        resumption_ctx = resumption_mgr.resume_run(token)

        # Constitutional Invariant: run_id must match identical original run_id
        assert resumption_ctx.run_id == "run-integ-1"
        assert resumption_ctx.job_id == "job-integ-1"
        assert resumption_ctx.success is True

        # Verify SQLite states transitioned back to RUNNING and READY
        cur = populated_db.cursor()
        cur.execute("SELECT status FROM jobs WHERE job_id = 'job-integ-1'")
        assert cur.fetchone()[0] == "RUNNING"

        cur.execute("SELECT status FROM runs WHERE run_id = 'run-integ-1'")
        assert cur.fetchone()[0] == "RUNNING"

        cur.execute(
            "SELECT status FROM agents WHERE run_id = 'run-integ-1' AND agent_id = 'AG-WORKER-1'"
        )
        assert cur.fetchone()[0] == "READY"

    def test_resumption_blocks_cannot_override_hard_deny_violation(
        self, populated_db: sqlite3.Connection
    ):
        """Verifies that an approval token attempting to falsify cannot_override_hard_deny is rejected."""
        resumption_mgr = SameRunResumptionManager(db_conn=populated_db)

        # Create valid token then manually mutate cannot_override_hard_deny
        manager = BoundedApprovalManager(db_conn=populated_db)
        request_id = manager.create_approval_request(
            job_id="job-integ-1",
            action="github_branch_push",
            scope=["feature/test"],
            run_id="run-integ-1",
        )
        token = manager.record_decision(
            request_id=request_id,
            decision=ApprovalDecision.APPROVED.value,
            approver=Approver(identity="admin", channel=ApprovalChannel.CLI.value),
            signature="valid-sig",
        )

        # Corrupt invariant
        token.cannot_override_hard_deny = False

        with pytest.raises(HardDenyViolation):
            resumption_mgr.resume_run(token)

    def test_expired_approval_token_rejected(self, populated_db: sqlite3.Connection):
        """Verifies that an expired approval request cannot be approved."""
        manager = BoundedApprovalManager(db_conn=populated_db)

        # Request with 1 second TTL
        request_id = manager.create_approval_request(
            job_id="job-integ-1",
            action="github_branch_push",
            scope=["feature/test"],
            run_id="run-integ-1",
            ttl_seconds=1,
        )

        # Try to record decision at future reference time (1 hour later)
        future_time = datetime.now(timezone.utc) + timedelta(hours=1)
        approver = Approver(identity="admin", channel=ApprovalChannel.CLI.value)

        with pytest.raises(ApprovalExpiredError):
            manager.record_decision(
                request_id=request_id,
                decision=ApprovalDecision.APPROVED.value,
                approver=approver,
                reference_time=future_time,
            )

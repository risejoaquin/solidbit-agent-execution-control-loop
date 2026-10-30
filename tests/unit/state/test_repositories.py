"""Unit tests for SACL V1 Repositories across all 16 domains and compatibility tables."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Generator

import pytest

from sacl.contracts.exceptions import ApprovalExpiredError
from sacl.contracts.invariants import (
    ApprovalChannel,
    ApprovalDecision,
    ArtifactType,
    GraphNodeStatus,
    JobStatus,
    Verdict,
)
from sacl.contracts.models import Approver, AuditEvent
from sacl.state.connection import create_connection
from sacl.state.exceptions import DuplicateEntityError, InvalidStateTransitionError
from sacl.state.migrations import MigrationRunner
from sacl.state.repositories.agents import AgentRepository
from sacl.state.repositories.approvals import ApprovalRepository
from sacl.state.repositories.artifacts import ArtifactRepository
from sacl.state.repositories.errors import ErrorRepository
from sacl.state.repositories.events import EventRepository
from sacl.state.repositories.graph import GraphRepository
from sacl.state.repositories.jobs import JobRepository
from sacl.state.repositories.mail import MailRepository
from sacl.state.repositories.packages import PackageRepository
from sacl.state.repositories.projects import ProjectRepository
from sacl.state.repositories.results import ResultRepository
from sacl.state.repositories.runs import RunRepository


@pytest.fixture
def repo_db(migration_sql_path: Path) -> Generator[sqlite3.Connection, None, None]:
    """Provides in-memory SQLite DB with 001_init.sql schema applied."""
    conn = create_connection(":memory:")
    runner = MigrationRunner(migration_sql_path.parent)
    runner.apply_all(conn)
    yield conn
    conn.close()


# ============================================================================
# DOMAIN 2 & 3: PROJECTS & PACKAGES
# ============================================================================


def test_project_repository(repo_db: sqlite3.Connection) -> None:
    repo = ProjectRepository(repo_db)
    proj = repo.register_project(
        project_id="solidbit-core",
        name="SolidBit Control Loop",
        root_path="C:/repos/solidbit",
        default_branch="main",
        policy_override={"max_parallel": 4},
    )
    assert proj["project_id"] == "solidbit-core"
    assert proj["policy_override"]["max_parallel"] == 4

    fetched = repo.get_project("solidbit-core")
    assert fetched is not None
    assert fetched["name"] == "SolidBit Control Loop"

    repo.update_policy_override("solidbit-core", {"max_parallel": 5})
    updated = repo.get_project("solidbit-core")
    assert updated["policy_override"]["max_parallel"] == 5


def test_package_repository(repo_db: sqlite3.Connection) -> None:
    # Register parent project
    ProjectRepository(repo_db).register_project("proj-1", "P1", "C:/root")

    repo = PackageRepository(repo_db)
    pkg = repo.record_package(
        package_id="pkg-w1",
        archive_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        manifest={"manifest_version": "1.0", "job_id": "job-1"},
        storage_path="packages/pkg-w1.zip",
        project_id="proj-1",
    )
    assert pkg["package_id"] == "pkg-w1"
    assert pkg["manifest"]["job_id"] == "job-1"

    repo.update_package_status("pkg-w1", "VALIDATED")
    updated = repo.get_package("pkg-w1")
    assert updated["status"] == "VALIDATED"


# ============================================================================
# DOMAIN 4: JOBS (12 PRIMARY + 10 SIDE STATES)
# ============================================================================


def test_job_repository_lifecycle(repo_db: sqlite3.Connection) -> None:
    ProjectRepository(repo_db).register_project("proj-1", "P1", "C:/root")
    PackageRepository(repo_db).record_package(
        package_id="pkg-1",
        archive_sha256="hash1",
        manifest="{}",
        storage_path="path",
        project_id="proj-1",
    )

    repo = JobRepository(repo_db)
    job = repo.create_job(
        job_id="job-100",
        package_id="pkg-1",
        project_id="proj-1",
        status=JobStatus.RECEIVED.value,
        priority=10,
        metadata={"author": "Joaquín"},
    )
    assert job["job_id"] == "job-100"
    assert job["priority"] == 10
    assert job["metadata"]["author"] == "Joaquín"

    # Progress through lifecycle
    for next_status in [
        JobStatus.AUTHENTICATED.value,
        JobStatus.VALIDATED.value,
        JobStatus.PERSISTED.value,
        JobStatus.QUEUED.value,
        JobStatus.DISPATCHED.value,
        JobStatus.RUNNING.value,
        JobStatus.VERIFYING.value,
        JobStatus.RESULT_PACKAGED.value,
        JobStatus.RESULT_SENT.value,
        JobStatus.COMPLETED.value,
    ]:
        repo.update_job_status("job-100", status=next_status)
        fetched = repo.get_job("job-100")
        assert fetched["status"] == next_status

    completed_job = repo.get_job("job-100")
    assert completed_job["completed_at"] is not None

    # Invalid status raises error
    with pytest.raises(InvalidStateTransitionError):
        repo.update_job_status("job-100", status="NON_CANONICAL_STATUS")


def test_job_repository_priority_peek(repo_db: sqlite3.Connection) -> None:
    repo = JobRepository(repo_db)
    repo.create_job("job-low", None, None, status=JobStatus.QUEUED.value, priority=1)
    repo.create_job("job-high", None, None, status=JobStatus.QUEUED.value, priority=100)
    repo.create_job("job-mid", None, None, status=JobStatus.QUEUED.value, priority=50)

    peeked = repo.peek_next_queued_job()
    assert peeked is not None
    assert peeked["job_id"] == "job-high"


# ============================================================================
# DOMAIN 5: RUNS
# ============================================================================


def test_run_repository(repo_db: sqlite3.Connection) -> None:
    JobRepository(repo_db).create_job("job-200", None, None, status=JobStatus.RECEIVED.value)

    repo = RunRepository(repo_db)
    run = repo.create_run(
        run_id="run-200-1",
        job_id="job-200",
        package_id="pkg-1",
        project="solidbit",
        repository="risejoaquin/solidbit",
        mode="isolated_branch_development",
        source_orchestrator="C:/orch",
        target_repo_path="C:/repos/solidbit",
        run_dir="runs/run-200-1",
        status="RUNNING",
    )
    assert run["run_id"] == "run-200-1"
    assert run["ready_for_integration"] == "NO"

    repo.set_ready_for_integration("run-200-1", "YES")
    repo.update_run_status("run-200-1", status="COMPLETED", reconciled_verdict="PASS")

    updated = repo.get_run("run-200-1")
    assert updated["ready_for_integration"] == "YES"
    assert updated["reconciled_verdict"] == "PASS"
    assert updated["completed_at"] is not None


# ============================================================================
# DOMAIN 6 & 7: GRAPH NODES, ATTEMPTS & COMPATIBILITY TABLES
# ============================================================================


def test_graph_repository(repo_db: sqlite3.Connection) -> None:
    JobRepository(repo_db).create_job("job-300", None, None)
    RunRepository(repo_db).create_run(
        "run-300", "job-300", "pkg", "p", "r", "mode", "src", "target", "runs/r", "RUNNING"
    )

    repo = GraphRepository(repo_db)
    node = repo.create_node(
        run_id="run-300",
        node_id="AG-COMPAT",
        job_id="job-300",
        phase_number=1,
        stage_name="COMPATIBILITY",
        agent_id="AG-COMPAT",
        status=GraphNodeStatus.READY.value,
    )
    assert node["node_id"] == "AG-COMPAT"

    # Attempt tracking
    attempt_id = repo.record_node_attempt(
        run_id="run-300",
        node_id="AG-COMPAT",
        attempt_number=1,
        pid=1234,
        status="RUNNING",
        report_path="runs/run-300/AG-COMPAT.REPORT.md",
    )
    repo.update_node_attempt(attempt_id, status="SUCCEEDED", exit_code=0, verdict="PASS")

    attempts = repo.list_node_attempts("run-300", "AG-COMPAT")
    assert len(attempts) == 1
    assert attempts[0]["exit_code"] == 0
    assert attempts[0]["verdict"] == "PASS"

    # DAG stages compatibility
    stage_id = repo.record_stage("run-300", phase_number=1, stage_name="PHASE_1")
    repo.update_stage_status(stage_id, "COMPLETE")
    stages = repo.list_stages("run-300")
    assert len(stages) == 1
    assert stages[0]["status"] == "COMPLETE"

    # Agent dependencies compatibility
    repo.add_dependency("run-300", upstream_agent_id="AG-COMPAT", downstream_agent_id="AG-ARCH")
    deps = repo.list_dependencies("run-300")
    assert len(deps) == 1
    assert deps[0]["upstream_agent_id"] == "AG-COMPAT"


# ============================================================================
# DOMAIN 8: AGENTS & COLLISION TRACKING
# ============================================================================


def test_agent_repository_and_conflicts(repo_db: sqlite3.Connection) -> None:
    JobRepository(repo_db).create_job("job-400", None, None)
    RunRepository(repo_db).create_run(
        "run-400", "job-400", "pkg", "p", "r", "mode", "src", "target", "runs/r", "RUNNING"
    )

    repo = AgentRepository(repo_db)
    agent_a = repo.record_agent(
        agent_id="AG-ARCH",
        run_id="run-400",
        status="RUNNING",
        prompt_path="prompts/arch.md",
        report_path="reports/arch.md",
        stdout_path="logs/arch.stdout.log",
        stderr_path="logs/arch.stderr.log",
        pid=4567,
    )
    assert agent_a["agent_id"] == "AG-ARCH"

    agent_b = repo.record_agent(
        agent_id="AG-SEC",
        run_id="run-400",
        status="RUNNING",
        prompt_path="prompts/sec.md",
        report_path="reports/sec.md",
        stdout_path="logs/sec.stdout.log",
        stderr_path="logs/sec.stderr.log",
        pid=4568,
    )
    assert agent_b["agent_id"] == "AG-SEC"

    # File modifications
    repo.record_file_modifications("run-400", "AG-ARCH", ["src/config.py", "docs/ARCH.md"])
    repo.record_file_modifications("run-400", "AG-SEC", ["src/config.py", "docs/SEC.md"])

    # Cross-branch conflict detection on overlapping 'src/config.py'
    conflicts = repo.detect_file_conflicts("run-400")
    assert len(conflicts) == 1
    assert conflicts[0]["file_path"] == "src/config.py"
    assert "AG-ARCH" in conflicts[0]["agents"]
    assert "AG-SEC" in conflicts[0]["agents"]

    # Run ready_for_integration must now be NO
    run_repo = RunRepository(repo_db)
    assert run_repo.get_run("run-400")["ready_for_integration"] == "NO"

    # Resolve conflict
    repo.resolve_file_conflict(conflicts[0]["conflict_id"], "RESOLVED")
    assert repo.list_file_conflicts("run-400")[0]["resolution"] == "RESOLVED"


# ============================================================================
# DOMAIN 9: EVENTS
# ============================================================================


def test_event_repository(repo_db: sqlite3.Connection) -> None:
    repo = EventRepository(repo_db)
    event = AuditEvent(
        event_type="SAFETY_GATE_TRIGGERED",
        severity="WARN",
        payload={"reason": "preflight_check", "status": "BLOCKED"},
        created_at="2026-10-07T12:00:00Z",
        run_id="run-500",
        agent_id="AG-SUPERVISOR",
    )
    event_id = repo.record_event(event)
    assert event_id > 0

    events = repo.list_events(run_id="run-500")
    assert len(events) == 1
    assert events[0]["event_type"] == "SAFETY_GATE_TRIGGERED"
    assert events[0]["payload"]["reason"] == "preflight_check"

    # Mirroring to legacy audit_events
    audit_events = repo.list_audit_events(run_id="run-500")
    assert len(audit_events) == 1
    assert audit_events[0]["event_type"] == "SAFETY_GATE_TRIGGERED"


# ============================================================================
# DOMAIN 10: APPROVALS
# ============================================================================


def test_approval_repository(repo_db: sqlite3.Connection) -> None:
    JobRepository(repo_db).create_job("job-600", None, None)

    repo = ApprovalRepository(repo_db)
    req_id = repo.create_approval_request(
        job_id="job-600",
        action="GIT_COMMIT_PRIMARY",
        scope=["docs/adr/ADR-001.md"],
        expires_at="2099-01-01T00:00:00Z",
    )
    assert req_id.startswith("req-")

    # Pending token
    token = repo.get_approval(req_id)
    assert token is not None
    assert token.decision == "PENDING"
    assert token.scope == ["docs/adr/ADR-001.md"]

    # Record Human Decision
    approver = Approver(identity="Joaquín", channel=ApprovalChannel.CLI.value)
    approved_token = repo.record_decision(
        request_id=req_id,
        decision=ApprovalDecision.APPROVED.value,
        approver=approver,
        rationale="Approved by human sovereign",
    )
    assert approved_token.decision == "APPROVED"
    assert approved_token.approver.identity == "Joaquín"
    assert repo.check_approval_valid(req_id, "GIT_COMMIT_PRIMARY", "job-600") is True


def test_approval_expiration(repo_db: sqlite3.Connection) -> None:
    JobRepository(repo_db).create_job("job-exp", None, None)
    repo = ApprovalRepository(repo_db)

    # Expired token in the past
    req_id = repo.create_approval_request(
        job_id="job-exp",
        action="TEST_ACTION",
        scope=["*"],
        expires_at="2020-01-01T00:00:00Z",
    )

    approver = Approver(identity="Joaquín", channel="CLI")
    with pytest.raises(ApprovalExpiredError):
        repo.record_decision(req_id, "APPROVED", approver)


# ============================================================================
# DOMAIN 11 & 12: ARTIFACTS & RESULTS
# ============================================================================


def test_artifacts_and_results(repo_db: sqlite3.Connection) -> None:
    JobRepository(repo_db).create_job("job-700", None, None)
    RunRepository(repo_db).create_run(
        "run-700", "job-700", "pkg", "p", "r", "mode", "src", "target", "runs/r", "RUNNING"
    )

    art_repo = ArtifactRepository(repo_db)
    art_id = art_repo.record_artifact(
        run_id="run-700",
        job_id="job-700",
        artifact_type=ArtifactType.SUMMARY_MD.value,
        storage_path="runs/run-700/SUMMARY.md",
        file_size_bytes=1024,
        sha256_hash="abcdef1234567890",
    )
    assert art_id > 0
    assert len(art_repo.list_artifacts_for_run("run-700")) == 1

    res_repo = ResultRepository(repo_db)
    res_id = res_repo.record_result(
        job_id="job-700",
        run_id="run-700",
        status="COMPLETE",
        final_verdict=Verdict.PASS.value,
        summary_md_path="runs/run-700/SUMMARY.md",
        summary_json_path="runs/run-700/SUMMARY.json",
    )
    assert res_id > 0
    res = res_repo.get_result("run-700")
    assert res["final_verdict"] == "PASS"

    res_repo.mark_delivered("run-700", delivered_to="uniquedraken@gmail.com")
    res_delivered = res_repo.get_result("run-700")
    assert res_delivered["delivered_to"] == "uniquedraken@gmail.com"


# ============================================================================
# DOMAIN 15 & 16: ERRORS & MAIL
# ============================================================================


def test_error_repository(repo_db: sqlite3.Connection) -> None:
    repo = ErrorRepository(repo_db)
    err_id = repo.record_error(
        error_code="DIRTY_ROOT_HALT",
        category="POLICY",
        severity="FATAL",
        message="Uncommitted modifications detected in root",
        context={"dirty_files": ["README.md"]},
    )
    assert err_id > 0
    errs = repo.list_errors(category="POLICY")
    assert len(errs) == 1
    assert errs[0]["error_code"] == "DIRTY_ROOT_HALT"
    assert errs[0]["context"]["dirty_files"] == ["README.md"]


def test_mail_repository_and_deduplication(repo_db: sqlite3.Connection) -> None:
    repo = MailRepository(repo_db)
    msg = repo.record_inbound_message(
        message_id="msg-001@mail.gmail.com",
        sender="uniquedraken@gmail.com",
        recipient="uniquedraken@gmail.com",
        subject="[SACL][JOB][v1][W0]",
        nonce="nonce-unique-12345",
        attachment_sha="hash-pkg-zip",
        history_id="100025",
    )
    assert msg["message_id"] == "msg-001@mail.gmail.com"

    # Re-inserting with duplicate nonce raises DuplicateEntityError
    with pytest.raises(DuplicateEntityError):
        repo.record_inbound_message(
            message_id="msg-002@mail.gmail.com",
            sender="uniquedraken@gmail.com",
            recipient="uniquedraken@gmail.com",
            subject="[SACL][JOB][v1][W0]",
            nonce="nonce-unique-12345",  # DUPLICATE NONCE
            attachment_sha="hash-pkg-zip",
        )

    # Monotonic cursor
    repo.advance_cursor("GMAIL_USERS_WATCH", "100025")
    cur = repo.get_cursor("GMAIL_USERS_WATCH")
    assert cur["history_id"] == "100025"

    # Outbox queue
    JobRepository(repo_db).create_job("job-mail-out", None, None)
    RunRepository(repo_db).create_run(
        "run-mail-out",
        "job-mail-out",
        "pkg",
        "p",
        "r",
        "mode",
        "src",
        "target",
        "runs/r",
        "RUNNING",
    )
    outbox_id = repo.enqueue_outbox(
        run_id="run-mail-out",
        recipient="uniquedraken@gmail.com",
        subject="[SACL][RESULT][v1][W0]",
        body_markdown="# Run Succeeded",
    )
    assert outbox_id > 0
    outbox_item = repo.dequeue_outbox()
    assert outbox_item["outbox_id"] == outbox_id

    repo.mark_outbox_sent(outbox_id)
    assert repo.dequeue_outbox() is None

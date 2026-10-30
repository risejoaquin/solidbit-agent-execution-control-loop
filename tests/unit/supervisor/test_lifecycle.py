"""Unit tests for SACL V1 canonical job lifecycle transitions."""

import sqlite3

import pytest

from sacl.contracts.exceptions import ArchitectureInvariantError
from sacl.contracts.invariants import JobSideStatus, JobStatus
from sacl.observability.audit import AuditEventEmitter
from sacl.supervisor.lease import LeaseCoordinator
from sacl.supervisor.lifecycle import (
    JobLifecycleManager,
)


def test_canonical_12_state_linear_progression(sqlite_temp_db: sqlite3.Connection):
    """Verifies complete 12-state linear lifecycle progression of a job."""
    emitter = AuditEventEmitter(sqlite_temp_db)
    lifecycle = JobLifecycleManager(sqlite_temp_db, audit_emitter=emitter)

    # 1. Create job in RECEIVED
    job = lifecycle.create_job("job-linear-01", status=JobStatus.RECEIVED)
    assert job["status"] == "RECEIVED"

    # Step through 12 linear states
    linear_states = [
        JobStatus.AUTHENTICATED,
        JobStatus.VALIDATED,
        JobStatus.PERSISTED,
        JobStatus.QUEUED,
        JobStatus.DISPATCHED,
        JobStatus.RUNNING,
        JobStatus.VERIFYING,
        JobStatus.RESULT_PACKAGED,
        JobStatus.RESULT_SENT,
        JobStatus.COMPLETED,
        JobStatus.ARCHIVED,
    ]

    for state in linear_states:
        updated = lifecycle.transition("job-linear-01", state)
        assert updated["status"] == state.value
        assert updated["previous_status"] is not None

    record = lifecycle.get_job("job-linear-01")
    assert record["status"] == "ARCHIVED"
    assert record["completed_at"] is not None


def test_side_state_transitions(sqlite_temp_db: sqlite3.Connection):
    """Verifies valid branch-out and resumption from side states."""
    lifecycle = JobLifecycleManager(sqlite_temp_db)

    # 1. WAITING_APPROVAL flow: RUNNING -> WAITING_APPROVAL -> RUNNING
    lifecycle.create_job("job-side-appr", status=JobStatus.RUNNING)
    t1 = lifecycle.transition("job-side-appr", JobSideStatus.WAITING_APPROVAL)
    assert t1["status"] == "WAITING_APPROVAL"
    t2 = lifecycle.transition("job-side-appr", JobStatus.RUNNING)
    assert t2["status"] == "RUNNING"

    # 2. RETRY_WAIT flow: RUNNING -> RETRY_WAIT -> RUNNING
    lifecycle.create_job("job-side-retry", status=JobStatus.RUNNING)
    lifecycle.transition("job-side-retry", JobSideStatus.RETRY_WAIT)
    t3 = lifecycle.transition("job-side-retry", JobStatus.RUNNING)
    assert t3["status"] == "RUNNING"

    # 3. BLOCKED flow: RUNNING -> BLOCKED -> QUEUED
    lifecycle.create_job("job-side-block", status=JobStatus.RUNNING)
    lifecycle.transition("job-side-block", JobSideStatus.BLOCKED)
    t4 = lifecycle.transition("job-side-block", JobStatus.QUEUED)
    assert t4["status"] == "QUEUED"

    # 4. INTERRUPTED flow: RUNNING -> INTERRUPTED -> VERIFYING
    lifecycle.create_job("job-side-inter", status=JobStatus.RUNNING)
    lifecycle.transition("job-side-inter", JobSideStatus.INTERRUPTED)
    t5 = lifecycle.transition("job-side-inter", JobStatus.VERIFYING)
    assert t5["status"] == "VERIFYING"


def test_illegal_state_transitions_fail_closed(sqlite_temp_db: sqlite3.Connection):
    """Verifies illegal lifecycle jumps raise ArchitectureInvariantError."""
    lifecycle = JobLifecycleManager(sqlite_temp_db)
    lifecycle.create_job("job-illegal-01", status=JobStatus.RECEIVED)

    # Illegal: jumping directly from RECEIVED to RUNNING
    with pytest.raises(ArchitectureInvariantError):
        lifecycle.transition("job-illegal-01", JobStatus.RUNNING)

    # Illegal: jumping from RECEIVED to COMPLETED
    with pytest.raises(ArchitectureInvariantError):
        lifecycle.transition("job-illegal-01", JobStatus.COMPLETED)

    # Advance to COMPLETED
    lifecycle.transition("job-illegal-01", JobStatus.AUTHENTICATED)
    lifecycle.transition("job-illegal-01", JobStatus.VALIDATED)
    lifecycle.transition("job-illegal-01", JobStatus.PERSISTED)
    lifecycle.transition("job-illegal-01", JobStatus.QUEUED)
    lifecycle.transition("job-illegal-01", JobStatus.DISPATCHED)
    lifecycle.transition("job-illegal-01", JobStatus.RUNNING)
    lifecycle.transition("job-illegal-01", JobStatus.VERIFYING)
    lifecycle.transition("job-illegal-01", JobStatus.RESULT_PACKAGED)
    lifecycle.transition("job-illegal-01", JobStatus.RESULT_SENT)
    lifecycle.transition("job-illegal-01", JobStatus.COMPLETED)

    # Illegal: attempting to resume from terminal COMPLETED back to RUNNING
    with pytest.raises(ArchitectureInvariantError):
        lifecycle.transition("job-illegal-01", JobStatus.RUNNING)


def test_automatic_project_lease_release_on_terminal_state(sqlite_temp_db: sqlite3.Connection):
    """Verifies that transitioning a job to COMPLETED or FAILED releases the project lease."""
    coordinator = LeaseCoordinator(sqlite_temp_db)
    lifecycle = JobLifecycleManager(sqlite_temp_db, lease_coordinator=coordinator)

    # Insert project in projects table to satisfy foreign key
    cursor = sqlite_temp_db.cursor()
    cursor.execute(
        "INSERT INTO projects (project_id, name, root_path, created_at, updated_at) "
        "VALUES ('proj-auto', 'Test Project', 'C:/repo', '2026-10-07T00:00:00Z', '2026-10-07T00:00:00Z')"
    )
    sqlite_temp_db.commit()

    # Create job with project
    lifecycle.create_job("job-term-lease", project_id="proj-auto", status=JobStatus.RUNNING)

    # Acquire project lock
    coordinator.acquire_project_lease("proj-auto", run_id="run-term-01", is_mutating=True)
    assert coordinator.get_project_lease("proj-auto") is not None

    # Transition job to COMPLETED
    lifecycle.transition("job-term-lease", JobStatus.VERIFYING, current_run_id="run-term-01")
    lifecycle.transition("job-term-lease", JobStatus.RESULT_PACKAGED, current_run_id="run-term-01")
    lifecycle.transition("job-term-lease", JobStatus.RESULT_SENT, current_run_id="run-term-01")
    lifecycle.transition("job-term-lease", JobStatus.COMPLETED, current_run_id="run-term-01")

    # Project lease must be released automatically
    assert coordinator.get_project_lease("proj-auto") is None


def test_run_synchronization_and_audit_events(sqlite_temp_db: sqlite3.Connection):
    """Verifies run record status is synchronized with job transitions and audit events are emitted."""
    emitter = AuditEventEmitter(sqlite_temp_db)
    lifecycle = JobLifecycleManager(sqlite_temp_db, audit_emitter=emitter)

    # Seed job and run
    lifecycle.create_job("job-sync", status=JobStatus.RUNNING)

    cursor = sqlite_temp_db.cursor()
    cursor.execute(
        """
        INSERT INTO runs (
            run_id, job_id, package_id, project, repository, mode,
            source_orchestrator, target_repo_path, run_dir, status, started_at
        )
        VALUES ('run-sync-1', 'job-sync', 'pkg-1', 'proj', 'repo', 'dev', 'orch', 'repo_path', 'runs/r1', 'RUNNING', '2026-10-07T00:00:00Z')
        """
    )
    sqlite_temp_db.commit()

    # Advance job to FAILED
    lifecycle.transition(
        "job-sync",
        JobSideStatus.FAILED,
        current_run_id="run-sync-1",
        error_summary="Unit test crash",
    )

    # Verify run record in SQLite was synchronized
    cursor.execute(
        "SELECT status, error_summary, completed_at FROM runs WHERE run_id = 'run-sync-1'"
    )
    run_row = cursor.fetchone()
    assert run_row["status"] == "FAILED"
    assert run_row["error_summary"] == "Unit test crash"
    assert run_row["completed_at"] is not None

    # Verify STATUS_CHANGE audit events
    events = emitter.query_events(run_id="run-sync-1")
    status_events = [e for e in events if e.payload.get("to_status") == "FAILED"]
    assert len(status_events) >= 1

"""Unit tests for SACL V1 job dispatcher, priority queue, and concurrency."""

import sqlite3
import pytest

from sacl.contracts.invariants import JobSideStatus, JobStatus
from sacl.observability.audit import AuditEventEmitter
from sacl.observability.errors import ErrorRecorder
from sacl.supervisor.dispatcher import JobDispatcher, RunContext
from sacl.supervisor.lease import LeaseCoordinator
from sacl.supervisor.lifecycle import JobLifecycleManager


def _seed_project(conn: sqlite3.Connection, project_id: str) -> None:
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR IGNORE INTO projects (project_id, name, root_path, created_at, updated_at)
        VALUES (?, ?, 'C:/repo', '2026-10-07T00:00:00Z', '2026-10-07T00:00:00Z')
        """,
        (project_id, f"Project {project_id}"),
    )
    conn.commit()


def test_prioritized_queue_dispatch(sqlite_temp_db: sqlite3.Connection):
    """Verifies that higher priority jobs are dispatched ahead of lower priority jobs."""
    _seed_project(sqlite_temp_db, "proj-prio")
    coordinator = LeaseCoordinator(sqlite_temp_db)
    lifecycle = JobLifecycleManager(sqlite_temp_db, lease_coordinator=coordinator)
    dispatcher = JobDispatcher(sqlite_temp_db, coordinator, lifecycle, executor_launcher=lambda ctx: 7701)

    # Insert two jobs: low priority first, high priority second
    lifecycle.create_job("job-low", project_id="proj-prio", status=JobStatus.QUEUED, priority=1)
    lifecycle.create_job("job-high", project_id="proj-prio", status=JobStatus.QUEUED, priority=100)

    # Poll and dispatch with limit 1
    dispatched = dispatcher.poll_and_dispatch(limit=1)
    assert len(dispatched) == 1

    # Verify job-high was dispatched
    job_high = lifecycle.get_job("job-high")
    assert job_high["status"] == "RUNNING"
    assert job_high["current_run_id"] == dispatched[0]

    # job-low remains queued
    job_low = lifecycle.get_job("job-low")
    assert job_low["status"] == "QUEUED"


def test_project_concurrency_lock_blocks_second_mutating_job(sqlite_temp_db: sqlite3.Connection):
    """Verifies that only 1 mutating job per project can run simultaneously."""
    _seed_project(sqlite_temp_db, "proj-alpha")
    _seed_project(sqlite_temp_db, "proj-beta")

    coordinator = LeaseCoordinator(sqlite_temp_db)
    lifecycle = JobLifecycleManager(sqlite_temp_db, lease_coordinator=coordinator)
    dispatcher = JobDispatcher(sqlite_temp_db, coordinator, lifecycle, executor_launcher=lambda ctx: 7701)

    # Queue 2 jobs for proj-alpha and 1 job for proj-beta
    lifecycle.create_job("job-alpha-1", project_id="proj-alpha", status=JobStatus.QUEUED, priority=10)
    lifecycle.create_job("job-alpha-2", project_id="proj-alpha", status=JobStatus.QUEUED, priority=5)
    lifecycle.create_job("job-beta-1", project_id="proj-beta", status=JobStatus.QUEUED, priority=10)

    # Poll and dispatch all eligible
    dispatched = dispatcher.poll_and_dispatch()

    # job-alpha-1 and job-beta-1 should dispatch; job-alpha-2 should be blocked by project lock
    assert len(dispatched) == 2

    assert lifecycle.get_job("job-alpha-1")["status"] == "RUNNING"
    assert lifecycle.get_job("job-beta-1")["status"] == "RUNNING"
    assert lifecycle.get_job("job-alpha-2")["status"] == "QUEUED"

    # Once job-alpha-1 finishes, job-alpha-2 can dispatch
    lifecycle.transition("job-alpha-1", JobStatus.VERIFYING)
    lifecycle.transition("job-alpha-1", JobStatus.RESULT_PACKAGED)
    lifecycle.transition("job-alpha-1", JobStatus.RESULT_SENT)
    lifecycle.transition("job-alpha-1", JobStatus.COMPLETED)

    # Next dispatch poll now dispatches job-alpha-2
    dispatched2 = dispatcher.poll_and_dispatch()
    assert len(dispatched2) == 1
    assert lifecycle.get_job("job-alpha-2")["status"] == "RUNNING"


def test_dirty_root_rule_halts_dispatch(sqlite_temp_db: sqlite3.Connection):
    """Verifies Local Dirty-Root Rule prevents dispatch and transitions job to BLOCKED."""
    _seed_project(sqlite_temp_db, "proj-dirty")

    coordinator = LeaseCoordinator(sqlite_temp_db)
    lifecycle = JobLifecycleManager(sqlite_temp_db, lease_coordinator=coordinator)
    error_recorder = ErrorRecorder(sqlite_temp_db)

    # Simulate dirty root returning uncommitted files
    def dirty_checker(path: str):
        return False, ["src/dirty_file.py", "README.md"]

    dispatcher = JobDispatcher(
        sqlite_temp_db,
        coordinator,
        lifecycle,
        clean_root_checker=dirty_checker,
        error_recorder=error_recorder,
        executor_launcher=lambda ctx: 7702,
    )

    lifecycle.create_job("job-dirty", project_id="proj-dirty", status=JobStatus.QUEUED)

    # Dispatch attempt
    run_id = dispatcher.dispatch_job("job-dirty")
    assert run_id is None

    # Job must transition to BLOCKED
    job = lifecycle.get_job("job-dirty")
    assert job["status"] == "BLOCKED"
    assert "DIRTY_ROOT_HALT" in job["error_summary"]

    # Project lease must NOT remain held
    assert coordinator.get_project_lease("proj-dirty") is None

    # Diagnostic error recorded in SQLite
    errors = [
        error
        for error in error_recorder.get_recent_errors(limit=20)
        if error.category == "EXECUTION"
    ]
    assert len(errors) >= 1
    assert errors[0].error_code == "DIRTY_ROOT_HALT"


def test_executor_launcher_invocation(sqlite_temp_db: sqlite3.Connection):
    """Verifies that the executor launcher callback is invoked with RunContext."""
    _seed_project(sqlite_temp_db, "proj-exec")

    coordinator = LeaseCoordinator(sqlite_temp_db)
    lifecycle = JobLifecycleManager(sqlite_temp_db, lease_coordinator=coordinator)

    launched_contexts: list[RunContext] = []

    def mock_launcher(ctx: RunContext):
        launched_contexts.append(ctx)
        return 7788  # Simulated worker PID

    dispatcher = JobDispatcher(
        sqlite_temp_db,
        coordinator,
        lifecycle,
        executor_launcher=mock_launcher,
    )

    lifecycle.create_job("job-exec", project_id="proj-exec", status=JobStatus.QUEUED)
    run_id = dispatcher.dispatch_job("job-exec")

    assert run_id is not None
    assert len(launched_contexts) == 1
    assert launched_contexts[0].run_id == run_id
    assert launched_contexts[0].job_id == "job-exec"
    assert launched_contexts[0].pid == 7788
    assert lifecycle.get_job("job-exec")["status"] == "RUNNING"



def test_missing_executor_blocks_without_creating_run_or_lease(sqlite_temp_db: sqlite3.Connection):
    """P0: missing Graph-H launcher cannot create a phantom RUNNING run."""
    _seed_project(sqlite_temp_db, "proj-no-executor")
    coordinator = LeaseCoordinator(sqlite_temp_db)
    lifecycle = JobLifecycleManager(sqlite_temp_db, lease_coordinator=coordinator)
    dispatcher = JobDispatcher(sqlite_temp_db, coordinator, lifecycle)
    lifecycle.create_job("job-no-executor", project_id="proj-no-executor", status=JobStatus.QUEUED)

    assert dispatcher.dispatch_job("job-no-executor") is None
    job = lifecycle.get_job("job-no-executor")
    assert job["status"] == JobSideStatus.BLOCKED.value
    assert "EXECUTOR_UNAVAILABLE" in job["error_summary"]
    assert job["current_run_id"] is None
    assert coordinator.get_project_lease("proj-no-executor") is None
    assert sqlite_temp_db.execute(
        "SELECT COUNT(*) FROM runs WHERE job_id = ?", ("job-no-executor",)
    ).fetchone()[0] == 0


def test_executor_returning_none_fails_and_releases_lease(sqlite_temp_db: sqlite3.Connection):
    """P0: null launch result must fail and release lease; never RUNNING."""
    _seed_project(sqlite_temp_db, "proj-empty-executor")
    coordinator = LeaseCoordinator(sqlite_temp_db)
    lifecycle = JobLifecycleManager(sqlite_temp_db, lease_coordinator=coordinator)
    dispatcher = JobDispatcher(
        sqlite_temp_db, coordinator, lifecycle, executor_launcher=lambda ctx: None
    )
    lifecycle.create_job("job-empty-executor", project_id="proj-empty-executor", status=JobStatus.QUEUED)

    assert dispatcher.dispatch_job("job-empty-executor") is None
    job = lifecycle.get_job("job-empty-executor")
    assert job["status"] == JobSideStatus.FAILED.value
    assert "EXECUTOR_UNAVAILABLE" in job["error_summary"]
    assert coordinator.get_project_lease("proj-empty-executor") is None
    rows = sqlite_temp_db.execute(
        "SELECT status FROM runs WHERE job_id = ?", ("job-empty-executor",)
    ).fetchall()
    assert len(rows) == 1
    assert rows[0]["status"] == JobSideStatus.FAILED.value

"""Unit tests for SACL V1 Graph-P persistent supervisor daemon."""

from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import pytest

from sacl.contracts.exceptions import LeaseAcquisitionError
from sacl.contracts.invariants import JobSideStatus, JobStatus, Verdict
from sacl.observability.audit import AuditEventEmitter
from sacl.observability.heartbeat import HeartbeatService
from sacl.supervisor.dispatcher import JobDispatcher, RunContext
from sacl.supervisor.graph_p import (
    GraphPSupervisor,
    SupervisorConfig,
    SupervisorState,
)
from sacl.supervisor.lease import LeaseCoordinator
from sacl.supervisor.lifecycle import JobLifecycleManager


def _seed_project(conn: sqlite3.Connection, project_id: str = "proj-gp", root_path: str = "C:/repo") -> None:
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR IGNORE INTO projects (project_id, name, root_path, created_at, updated_at)
        VALUES (?, ?, ?, '2026-10-07T00:00:00Z', '2026-10-07T00:00:00Z')
        """,
        (project_id, f"Project {project_id}", root_path),
    )
    conn.commit()


def test_supervisor_zero_idle_token_posture_when_no_jobs(sqlite_temp_db: sqlite3.Connection):
    """Verifies ADR-003: Zero idle LLM token posture when no execution jobs are pending or active."""
    coordinator = LeaseCoordinator(sqlite_temp_db)
    lifecycle = JobLifecycleManager(sqlite_temp_db, lease_coordinator=coordinator)
    dispatcher = JobDispatcher(sqlite_temp_db, coordinator, lifecycle)

    supervisor = GraphPSupervisor(
        sqlite_temp_db,
        instance_id="sup-idle-test",
        config=SupervisorConfig(poll_interval_seconds=0.1),
        lease_coordinator=coordinator,
        lifecycle_manager=lifecycle,
        dispatcher=dispatcher,
    )

    # Boot supervisor
    supervisor.start()

    # Zero Idle Token Posture assertions
    assert supervisor.is_idle() is True
    assert supervisor.state == SupervisorState.IDLE
    assert len(supervisor.active_runs) == 0

    # Singleton lease is held
    singleton_lease = coordinator.get_singleton_lease()
    assert singleton_lease is not None
    assert singleton_lease.holder_id == "sup-idle-test"

    # Tick with no jobs keeps IDLE posture
    supervisor.run_supervisor_tick()
    assert supervisor.is_idle() is True
    assert supervisor.state == SupervisorState.IDLE

    # Clean shutdown
    supervisor.shutdown()
    assert supervisor.state == SupervisorState.STOPPED
    assert coordinator.get_singleton_lease() is None


def test_supervisor_job_wake_and_dispatch(sqlite_temp_db: sqlite3.Connection):
    """Verifies explicit wake signal and polling dispatch of queued jobs into ephemeral Graph-H."""
    _seed_project(sqlite_temp_db, "proj-gp")
    coordinator = LeaseCoordinator(sqlite_temp_db)
    lifecycle = JobLifecycleManager(sqlite_temp_db, lease_coordinator=coordinator)

    launched_contexts: list[RunContext] = []

    def mock_launcher(ctx: RunContext):
        launched_contexts.append(ctx)
        return 9901  # Mock worker PID

    dispatcher = JobDispatcher(
        sqlite_temp_db,
        coordinator,
        lifecycle,
        executor_launcher=mock_launcher,
    )

    # Simulate worker 9901 as alive
    supervisor = GraphPSupervisor(
        sqlite_temp_db,
        instance_id="sup-dispatch-test",
        lease_coordinator=coordinator,
        lifecycle_manager=lifecycle,
        dispatcher=dispatcher,
        process_checker=lambda pid: pid == 9901,
    )
    supervisor.start()

    # Create job in QUEUED
    lifecycle.create_job("job-wake-01", project_id="proj-gp", status=JobStatus.QUEUED)

    # Wake with explicit job ID
    run_id = supervisor.wake("job-wake-01")
    assert run_id is not None
    assert supervisor.is_idle() is False
    assert supervisor.state == SupervisorState.RUNNING
    assert run_id in supervisor.active_runs

    # Verify RunContext and tracking PID
    active_tracking = supervisor.active_runs[run_id]
    assert active_tracking.pid == 9901
    assert active_tracking.job_id == "job-wake-01"
    assert active_tracking.project_id == "proj-gp"

    # Project lease is held
    assert coordinator.get_project_lease("proj-gp") is not None

    supervisor.shutdown()


def test_supervisor_4_point_reconciliation_on_process_exit(tmp_path: Path, sqlite_temp_db: sqlite3.Connection):
    """Verifies that when a worker process exits, Graph-P reconciles deliverables via 4-point protocol."""
    _seed_project(sqlite_temp_db, "proj-recon")
    coordinator = LeaseCoordinator(sqlite_temp_db)
    lifecycle = JobLifecycleManager(sqlite_temp_db, lease_coordinator=coordinator)

    # Prepare deliverable report with passing regex marker
    report_file = tmp_path / "AG-COMPAT.md"
    report_file.write_text(
        "# AG-COMPAT Report\n\nExecution completed.\n\nAGENT_AG-COMPAT_RESULT = PASS\n",
        encoding="utf-8",
    )
    stdout_file = tmp_path / "stdout.log"
    stdout_file.write_text("Worker execution succeeded.\n", encoding="utf-8")
    stderr_file = tmp_path / "stderr.log"
    stderr_file.write_text("", encoding="utf-8")

    is_process_running = True

    def process_checker(pid: int) -> bool:
        return is_process_running

    def mock_launcher(ctx: RunContext):
        # Insert worker into agents table to simulate Graph-H materializing the worker
        cursor = sqlite_temp_db.cursor()
        cursor.execute(
            """
            INSERT INTO agents (
                agent_id, run_id, status, result_verdict, pid,
                prompt_path, report_path, stdout_path, stderr_path,
                updated_at, exit_code
            )
            VALUES (?, ?, 'RUNNING', 'UNKNOWN', 8811, 'prompt.md', ?, ?, ?, '2026-10-07T00:00:00Z', 0)
            """,
            ("AG-COMPAT", ctx.run_id, str(report_file), str(stdout_file), str(stderr_file)),
        )
        sqlite_temp_db.commit()
        return 8811

    dispatcher = JobDispatcher(
        sqlite_temp_db,
        coordinator,
        lifecycle,
        executor_launcher=mock_launcher,
    )

    supervisor = GraphPSupervisor(
        sqlite_temp_db,
        instance_id="sup-recon-test",
        lease_coordinator=coordinator,
        lifecycle_manager=lifecycle,
        dispatcher=dispatcher,
        process_checker=process_checker,
    )
    supervisor.start()

    lifecycle.create_job("job-recon-01", project_id="proj-recon", status=JobStatus.QUEUED)
    run_id = supervisor.dispatch_job("job-recon-01")
    assert run_id is not None
    assert supervisor.is_idle() is False

    # Simulate worker process termination
    is_process_running = False

    # Supervisor tick monitors active runs and detects process exit
    supervisor.run_supervisor_tick()

    # Invariants verified:
    # 1. 4-point reconciliation evaluated deliverable -> PASS
    # 2. Canonical transitions: RUNNING -> VERIFYING -> RESULT_PACKAGED -> RESULT_SENT -> COMPLETED
    job = lifecycle.get_job("job-recon-01")
    assert job["status"] == "COMPLETED"

    cursor = sqlite_temp_db.cursor()
    cursor.execute("SELECT status, reconciled_verdict FROM runs WHERE run_id = ?", (run_id,))
    run_row = cursor.fetchone()
    assert run_row["status"] == "COMPLETED"
    assert run_row["reconciled_verdict"] == "PASS"

    # Agent row updated
    cursor.execute("SELECT status, result_verdict FROM agents WHERE run_id = ?", (run_id,))
    agent_row = cursor.fetchone()
    assert agent_row["status"] == "COMPLETE"
    assert agent_row["result_verdict"] == "PASS"

    # Project lease released automatically
    assert coordinator.get_project_lease("proj-recon") is None

    # Supervisor returns to IDLE posture
    assert supervisor.is_idle() is True
    assert supervisor.state == SupervisorState.IDLE

    supervisor.shutdown()


def test_exit_code_zero_alone_is_insufficient_fails_when_deliverable_missing(tmp_path: Path, sqlite_temp_db: sqlite3.Connection):
    """Verifies that exit code 0 alone does NOT produce success if deliverable report is missing."""
    _seed_project(sqlite_temp_db, "proj-no-evid")
    coordinator = LeaseCoordinator(sqlite_temp_db)
    lifecycle = JobLifecycleManager(sqlite_temp_db, lease_coordinator=coordinator)

    is_process_running = True
    missing_report = tmp_path / "NON_EXISTENT_REPORT.md"
    stdout_file = tmp_path / "stdout.log"
    stdout_file.write_text("Worker exited with 0 but wrote no deliverables.\n", encoding="utf-8")
    stderr_file = tmp_path / "stderr.log"
    stderr_file.write_text("", encoding="utf-8")

    def mock_launcher(ctx: RunContext):
        cursor = sqlite_temp_db.cursor()
        cursor.execute(
            """
            INSERT INTO agents (
                agent_id, run_id, status, result_verdict, pid,
                prompt_path, report_path, stdout_path, stderr_path,
                updated_at, exit_code
            )
            VALUES (?, ?, 'RUNNING', 'UNKNOWN', 8822, 'prompt.md', ?, ?, ?, '2026-10-07T00:00:00Z', 0)
            """,
            ("AG-SCHEMA", ctx.run_id, str(missing_report), str(stdout_file), str(stderr_file)),
        )
        sqlite_temp_db.commit()
        return 8822

    dispatcher = JobDispatcher(
        sqlite_temp_db,
        coordinator,
        lifecycle,
        executor_launcher=mock_launcher,
    )

    supervisor = GraphPSupervisor(
        sqlite_temp_db,
        instance_id="sup-noevid-test",
        lease_coordinator=coordinator,
        lifecycle_manager=lifecycle,
        dispatcher=dispatcher,
        process_checker=lambda pid: is_process_running,
    )
    supervisor.start()

    lifecycle.create_job("job-noevid-01", project_id="proj-no-evid", status=JobStatus.QUEUED)
    run_id = supervisor.dispatch_job("job-noevid-01")

    # Worker process terminates (exit code 0 recorded, but deliverable missing)
    is_process_running = False
    supervisor.run_supervisor_tick()

    # Must transition to FAILED, NEVER COMPLETED!
    job = lifecycle.get_job("job-noevid-01")
    assert job["status"] == "FAILED"

    cursor = sqlite_temp_db.cursor()
    cursor.execute("SELECT status, reconciled_verdict FROM runs WHERE run_id = ?", (run_id,))
    run_row = cursor.fetchone()
    assert run_row["status"] == "FAILED"
    assert run_row["reconciled_verdict"] == "FAILED"

    # Project lease released
    assert coordinator.get_project_lease("proj-no-evid") is None
    assert supervisor.is_idle() is True

    supervisor.shutdown()


def test_supervisor_singleton_lease_mutual_exclusion(sqlite_temp_db: sqlite3.Connection):
    """Verifies that a second supervisor cannot start while the primary is actively running."""
    coordinator = LeaseCoordinator(
        sqlite_temp_db,
        process_checker=lambda pid: True,  # Both PIDs considered alive
    )
    lifecycle = JobLifecycleManager(sqlite_temp_db, lease_coordinator=coordinator)
    dispatcher = JobDispatcher(sqlite_temp_db, coordinator, lifecycle)

    sup1 = GraphPSupervisor(
        sqlite_temp_db,
        instance_id="sup-primary",
        lease_coordinator=coordinator,
        lifecycle_manager=lifecycle,
        dispatcher=dispatcher,
    )
    sup1.start()

    # Second supervisor with distinct instance ID & PID
    sup2 = GraphPSupervisor(
        sqlite_temp_db,
        instance_id="sup-secondary",
        lease_coordinator=coordinator,
        lifecycle_manager=lifecycle,
        dispatcher=dispatcher,
    )
    sup2.pid = 99999  # Distinct PID

    with pytest.raises(LeaseAcquisitionError):
        sup2.start()

    sup1.shutdown()


def test_crash_recovery_never_blindly_restart_old_running(tmp_path: Path, sqlite_temp_db: sqlite3.Connection):
    """Verifies that cold-start crash recovery never blindly restarts old RUNNING jobs when deliverables missing."""
    _seed_project(sqlite_temp_db, "proj-crash", root_path=str(tmp_path))
    coordinator = LeaseCoordinator(
        sqlite_temp_db,
        process_checker=lambda pid: False,  # All old workers dead
    )
    lifecycle = JobLifecycleManager(sqlite_temp_db, lease_coordinator=coordinator)
    dispatcher = JobDispatcher(sqlite_temp_db, coordinator, lifecycle)

    # Seed an interrupted job and run in RUNNING status
    lifecycle.create_job("job-crashed", project_id="proj-crash", status=JobStatus.RUNNING)
    cursor = sqlite_temp_db.cursor()
    cursor.execute(
        """
        INSERT INTO runs (
            run_id, job_id, package_id, project_id, project, repository, mode,
            source_orchestrator, target_repo_path, run_dir, status, ready_for_integration, started_at
        )
        VALUES ('run-crashed-01', 'job-crashed', 'pkg-crashed', 'proj-crash', 'proj-crash', 'repo', 'dev',
                'orch', ?, ?, 'RUNNING', 'NO', '2026-10-07T00:00:00Z')
        """,
        (str(tmp_path), str(tmp_path / "runs" / "run-crashed-01")),
    )
    # Seed worker record with dead PID and non-existent report
    cursor.execute(
        """
        INSERT INTO agents (
            agent_id, run_id, status, result_verdict, pid, prompt_path,
            report_path, stdout_path, stderr_path, updated_at
        )
        VALUES ('AG-CRASHED', 'run-crashed-01', 'RUNNING', 'UNKNOWN', 7711, 'p.md',
                'nonexistent.md', 'out.log', 'err.log', '2026-10-07T00:00:00Z')
        """,
    )
    # Project lock was left occupied by dead run
    coordinator.acquire_project_lease("proj-crash", run_id="run-crashed-01", holder_pid=7711, is_mutating=True)
    sqlite_temp_db.commit()

    # Supervisor starts up with crash recovery enabled
    supervisor = GraphPSupervisor(
        sqlite_temp_db,
        instance_id="sup-recovery",
        lease_coordinator=coordinator,
        lifecycle_manager=lifecycle,
        dispatcher=dispatcher,
        process_checker=lambda pid: False,
    )
    supervisor.start()

    # Inviolable Invariant Verified:
    # 1. Job was NOT re-dispatched.
    # 2. Status was transitioned to INTERRUPTED.
    job = lifecycle.get_job("job-crashed")
    assert job["status"] == "INTERRUPTED"

    cursor.execute("SELECT status, reconciled_verdict FROM runs WHERE run_id = 'run-crashed-01'")
    run_row = cursor.fetchone()
    assert run_row["status"] == "INTERRUPTED"

    # Orphaned project lock was reclaimed/released
    assert coordinator.get_project_lease("proj-crash") is None

    # Supervisor is clean and IDLE
    assert supervisor.is_idle() is True
    assert supervisor.state == SupervisorState.IDLE

    supervisor.shutdown()


def test_crash_recovery_finalizes_when_deliverables_exist(tmp_path: Path, sqlite_temp_db: sqlite3.Connection):
    """Verifies that cold-start crash recovery finalizes completed runs when deliverables exist on disk."""
    _seed_project(sqlite_temp_db, "proj-deliv", root_path=str(tmp_path))
    coordinator = LeaseCoordinator(
        sqlite_temp_db,
        process_checker=lambda pid: False,  # Old worker dead
    )
    lifecycle = JobLifecycleManager(sqlite_temp_db, lease_coordinator=coordinator)
    dispatcher = JobDispatcher(sqlite_temp_db, coordinator, lifecycle)

    # Deliverable report was written before host crash
    report_file = tmp_path / "DELIV_REPORT.md"
    report_file.write_text(
        "# AG-ARCH Report\n\nExecution finished before crash.\n\nRESULT = PASS\n",
        encoding="utf-8",
    )

    lifecycle.create_job("job-deliv-01", project_id="proj-deliv", status=JobStatus.RUNNING)
    cursor = sqlite_temp_db.cursor()
    cursor.execute(
        """
        INSERT INTO runs (
            run_id, job_id, package_id, project_id, project, repository, mode,
            source_orchestrator, target_repo_path, run_dir, status, ready_for_integration, started_at
        )
        VALUES ('run-deliv-01', 'job-deliv-01', 'pkg-deliv', 'proj-deliv', 'proj-deliv', 'repo', 'dev',
                'orch', ?, ?, 'RUNNING', 'NO', '2026-10-07T00:00:00Z')
        """,
        (str(tmp_path), str(tmp_path)),
    )
    cursor.execute(
        """
        INSERT INTO agents (
            agent_id, run_id, status, result_verdict, pid, prompt_path,
            report_path, stdout_path, stderr_path, updated_at
        )
        VALUES ('AG-ARCH', 'run-deliv-01', 'RUNNING', 'UNKNOWN', 7722, 'p.md',
                ?, 'out.log', 'err.log', '2026-10-07T00:00:00Z')
        """,
        (str(report_file),),
    )
    coordinator.acquire_project_lease("proj-deliv", run_id="run-deliv-01", holder_pid=7722, is_mutating=True)
    sqlite_temp_db.commit()

    supervisor = GraphPSupervisor(
        sqlite_temp_db,
        instance_id="sup-deliv-recon",
        lease_coordinator=coordinator,
        lifecycle_manager=lifecycle,
        dispatcher=dispatcher,
        process_checker=lambda pid: False,
    )
    supervisor.start()

    # Reconciled to COMPLETED without re-execution!
    job = lifecycle.get_job("job-deliv-01")
    assert job["status"] == "COMPLETED"

    cursor.execute("SELECT status, reconciled_verdict FROM runs WHERE run_id = 'run-deliv-01'")
    run_row = cursor.fetchone()
    assert run_row["status"] == "COMPLETED"
    assert run_row["reconciled_verdict"] == "PASS"

    # Project lock released
    assert coordinator.get_project_lease("proj-deliv") is None
    assert supervisor.is_idle() is True

    supervisor.shutdown()


def test_crash_recovery_halts_on_dirty_root(sqlite_temp_db: sqlite3.Connection):
    """Verifies that Local Dirty-Root Rule blocks recovery when human uncommitted edits exist."""
    _seed_project(sqlite_temp_db, "proj-dirty-rec", root_path="C:/dirty/repo")
    coordinator = LeaseCoordinator(sqlite_temp_db, process_checker=lambda pid: False)
    lifecycle = JobLifecycleManager(sqlite_temp_db, lease_coordinator=coordinator)

    def dirty_checker(path: str):
        return False, ["human_work.py", "scratch.md"]

    dispatcher = JobDispatcher(
        sqlite_temp_db,
        coordinator,
        lifecycle,
        clean_root_checker=dirty_checker,
    )

    lifecycle.create_job("job-dirty-rec", project_id="proj-dirty-rec", status=JobStatus.RUNNING)
    cursor = sqlite_temp_db.cursor()
    cursor.execute(
        """
        INSERT INTO runs (
            run_id, job_id, package_id, project_id, project, repository, mode,
            source_orchestrator, target_repo_path, run_dir, status, ready_for_integration, started_at
        )
        VALUES ('run-dirty-rec', 'job-dirty-rec', 'pkg', 'proj-dirty-rec', 'proj', 'repo', 'dev',
                'orch', 'C:/dirty/repo', 'runs/r', 'RUNNING', 'NO', '2026-10-07T00:00:00Z')
        """,
    )
    coordinator.acquire_project_lease("proj-dirty-rec", run_id="run-dirty-rec", holder_pid=7733, is_mutating=True)
    sqlite_temp_db.commit()

    supervisor = GraphPSupervisor(
        sqlite_temp_db,
        instance_id="sup-dirty-rec",
        lease_coordinator=coordinator,
        lifecycle_manager=lifecycle,
        dispatcher=dispatcher,
        process_checker=lambda pid: False,
    )
    supervisor.start()

    # Recovery halted with BLOCKED status; uncommitted changes are NOT touched
    job = lifecycle.get_job("job-dirty-rec")
    assert job["status"] == "BLOCKED"
    assert "DIRTY_ROOT_BLOCKS_RECOVERY" in job["error_summary"]

    assert coordinator.get_project_lease("proj-dirty-rec") is None
    supervisor.shutdown()


def test_supervisor_liveness_heartbeat_service(sqlite_temp_db: sqlite3.Connection):
    """Verifies periodic process liveness heartbeat recording."""
    coordinator = LeaseCoordinator(sqlite_temp_db)
    lifecycle = JobLifecycleManager(sqlite_temp_db, lease_coordinator=coordinator)
    dispatcher = JobDispatcher(sqlite_temp_db, coordinator, lifecycle)
    heartbeat_svc = HeartbeatService(sqlite_temp_db)

    supervisor = GraphPSupervisor(
        sqlite_temp_db,
        instance_id="sup-hb-test",
        config=SupervisorConfig(heartbeat_interval_seconds=0.0),  # emit every tick
        lease_coordinator=coordinator,
        lifecycle_manager=lifecycle,
        dispatcher=dispatcher,
        heartbeat_service=heartbeat_svc,
    )

    supervisor.start()
    supervisor.run_supervisor_tick()

    # Query heartbeats table
    cursor = sqlite_temp_db.cursor()
    cursor.execute(
        "SELECT component, instance_id, status FROM heartbeats WHERE instance_id = 'sup-hb-test' ORDER BY heartbeat_id DESC"
    )
    row = cursor.fetchone()
    assert row is not None
    assert row["component"] == "SUPERVISOR"
    assert row["status"] == "IDLE"

    supervisor.shutdown()

    # Final heartbeat status is STOPPED
    cursor.execute(
        "SELECT status FROM heartbeats WHERE instance_id = 'sup-hb-test' ORDER BY heartbeat_id DESC"
    )
    final_row = cursor.fetchone()
    assert final_row is not None
    assert final_row["status"] == "STOPPED"



@pytest.mark.parametrize(
    ("process_name", "offset", "has_time", "liveness", "expected"),
    [
        ("agy", 0, True, True, True),
        ("powershell", 299, True, True, True),
        ("agy", 301, True, True, False),
        ("unrelated.exe", 0, True, True, False),
        ("agy", 0, False, True, False),
        ("agy", 0, True, False, False),
    ],
)
def test_graph_p_cold_start_default_path_verifies_three_way_pid_identity(
    sqlite_temp_db: sqlite3.Connection,
    process_name: str,
    offset: int,
    has_time: bool,
    liveness: bool,
    expected: bool,
) -> None:
    """An existing PID alone must not reconnect a worker after host restart."""
    from datetime import timedelta
    from sacl.recovery.process_identity import MockProcessInspector

    recorded = datetime.now(timezone.utc)
    inspector = MockProcessInspector()
    inspector.register_process(
        pid=99371,
        process_name=process_name,
        is_active=True,
        start_time=recorded + timedelta(seconds=offset) if has_time else None,
    )
    supervisor = GraphPSupervisor(
        db_source=sqlite_temp_db,
        recovery_process_inspector=inspector,
        # Do NOT set a custom process_checker: exercise production identity path.
    )
    # Only mock the OS liveness syscall, not the process identity contract.
    supervisor.process_checker = lambda pid: liveness
    assert supervisor._use_canonical_recovery_identity is True
    assert supervisor._is_recovery_worker_alive(99371, recorded.isoformat()) is expected
    assert supervisor._is_recovery_worker_alive(99371, None) is False

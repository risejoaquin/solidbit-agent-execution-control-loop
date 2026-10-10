"""Integration tests for SACL V1 Graph-P Persistent Supervisor Daemon.

Tests:
1. Persistent Zero-Idle Token Posture (ADR-003)
2. Level 1 Singleton Lease & Level 2 Project Lease Coordination (ADR-003, CONCURRENCY §2)
3. End-to-End Job Dispatch & 4-Point Deliverable Reconciliation Synthesis
4. Cold-Start Crash Recovery (RECOVERY_MODEL.md)
5. Graceful Operator Shutdown Protocol
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import pytest

from sacl.contracts.exceptions import LeaseAcquisitionError
from sacl.contracts.invariants import JobStatus, Verdict
from sacl.state.store import SqliteStateStore
from sacl.supervisor.dispatcher import JobDispatcher, RunContext
from sacl.supervisor.graph_p import GraphPSupervisor, SupervisorConfig, SupervisorState
from sacl.supervisor.lease import LeaseCoordinator
from sacl.supervisor.lifecycle import JobLifecycleManager


@dataclass
class MockProcessHandle:
    """Mock process handle simulating an ephemeral worker subprocess."""

    _poll_result: int | None = None
    pid: int = 12345

    def poll(self) -> int | None:
        return self._poll_result

    def complete(self, exit_code: int = 0) -> None:
        self._poll_result = exit_code


@pytest.fixture
def state_store(tmp_path: Path) -> SqliteStateStore:
    """Provisions an initialized SQLite operational state store."""
    db_file = tmp_path / "sacl_ops_test.db"
    return SqliteStateStore(db_path=db_file, auto_migrate=True)


@pytest.fixture
def supervisor_env(state_store: SqliteStateStore, tmp_path: Path):
    """Sets up a clean supervisor test environment."""
    conn = state_store.connection

    # Setup target repo directory
    target_repo = tmp_path / "mock_target_repo"
    target_repo.mkdir(parents=True, exist_ok=True)

    # Register project
    state_store.projects.register_project(
        project_id="proj-sup-1",
        name="Supervisor Test Project",
        root_path=str(target_repo),
    )

    # Register package
    state_store.packages.record_package(
        package_id="pkg-sup-1",
        archive_sha256="abc12345",
        manifest={"schema": "solidbit.execution-package.v1"},
        storage_path=str(tmp_path / "pkg-sup-1.zip"),
        project_id="proj-sup-1",
    )

    return {
        "store": state_store,
        "conn": conn,
        "target_repo": target_repo,
        "tmp_path": tmp_path,
    }


class TestSupervisorWorkflow:
    """End-to-end integration tests for Graph-P Supervisor."""

    def test_zero_idle_token_posture_and_singleton_lease(self, supervisor_env):
        """Verifies supervisor acquires Level 1 singleton lease and maintains zero-idle posture."""
        conn = supervisor_env["conn"]
        config = SupervisorConfig(poll_interval_seconds=0.1, singleton_ttl_seconds=30)
        supervisor = GraphPSupervisor(db_source=conn, config=config, instance_id="graph-p-test-1")

        # Initial zero-idle posture
        assert supervisor.is_idle() is True

        # Tick executes lease renewal/acquisition
        supervisor.run_supervisor_tick()
        assert supervisor.is_idle() is True
        assert supervisor.state == SupervisorState.IDLE

        # Verify singleton lease held in SQLite
        cur = conn.cursor()
        cur.execute(
            "SELECT holder_id FROM leases WHERE lease_name = ?",
            (LeaseCoordinator.SUPERVISOR_SINGLETON_KEY,),
        )
        row = cur.fetchone()
        assert row is not None
        assert row[0] == "graph-p-test-1"

    def test_singleton_lease_contention_raises_error(self, supervisor_env):
        """Verifies that a second supervisor cannot acquire an active singleton lease."""
        conn = supervisor_env["conn"]
        config = SupervisorConfig(poll_interval_seconds=0.1, singleton_ttl_seconds=300)

        # Supervisor 1 acquires singleton lease
        sup1 = GraphPSupervisor(
            db_source=conn,
            config=config,
            instance_id="graph-p-holder",
            process_checker=lambda pid: True,
        )
        sup1.run_supervisor_tick()

        # Supervisor 2 attempts to tick
        sup2 = GraphPSupervisor(
            db_source=conn,
            config=config,
            instance_id="graph-p-contender",
            process_checker=lambda pid: True,
        )

        with pytest.raises(LeaseAcquisitionError):
            sup2.run_supervisor_tick()

    def test_end_to_end_dispatch_and_4_point_reconciliation(self, supervisor_env):
        """Verifies dispatch, project lease acquisition, and 4-point deliverable reconciliation."""
        conn = supervisor_env["conn"]
        store = supervisor_env["store"]
        tmp_path = supervisor_env["tmp_path"]

        # 1. Enqueue job
        store.jobs.create_job(
            job_id="job-dispatch-1",
            package_id="pkg-sup-1",
            project_id="proj-sup-1",
            status=JobStatus.QUEUED.value,
        )

        # Prepare mock process
        mock_proc = MockProcessHandle()

        def mock_launcher(ctx: RunContext) -> MockProcessHandle:
            return mock_proc

        lease_coord = LeaseCoordinator(db_source=conn, process_checker=lambda pid: True)
        lifecycle = JobLifecycleManager(db_source=conn, lease_coordinator=lease_coord)
        dispatcher = JobDispatcher(
            db_source=conn,
            lease_coordinator=lease_coord,
            lifecycle_manager=lifecycle,
            executor_launcher=mock_launcher,
        )

        supervisor = GraphPSupervisor(
            db_source=conn,
            instance_id="graph-p-worker-test",
            lease_coordinator=lease_coord,
            lifecycle_manager=lifecycle,
            dispatcher=dispatcher,
            process_checker=lambda pid: True,
        )

        # 2. First tick: should discover QUEUED job and dispatch it
        supervisor.run_supervisor_tick()
        assert supervisor.is_idle() is False
        assert len(supervisor.active_runs) == 1

        run_id = list(supervisor.active_runs.keys())[0]

        # Verify Level 2 project lease acquired
        cur = conn.cursor()
        cur.execute(
            "SELECT holder_id FROM leases WHERE lease_name = 'PROJECT_proj-sup-1'",
        )
        proj_lease = cur.fetchone()
        assert proj_lease is not None
        assert run_id in proj_lease[0]

        # Verify job transitioned to RUNNING
        cur.execute("SELECT status FROM jobs WHERE job_id = 'job-dispatch-1'")
        assert cur.fetchone()[0] == JobStatus.RUNNING.value

        # 3. Simulate agent worker completing and writing required report
        report_dir = tmp_path / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_file = report_dir / "AG-SUB-1.REPORT.md"
        report_file.write_text(
            "# Task Report\nAGENT_ID: AG-SUB-1\n**Final Status:** PASS\nFINAL_RESULT = PASS\nAll requirements satisfied.\n",
            encoding="utf-8",
        )

        log_dir = tmp_path / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        stdout_file = log_dir / "AG-SUB-1.stdout.log"
        stderr_file = log_dir / "AG-SUB-1.stderr.log"
        stdout_file.write_text("Execution complete.\nFINAL_RESULT = PASS\n", encoding="utf-8")
        stderr_file.write_text("", encoding="utf-8")

        # Record agent deliverable in SQLite with exit_code=0
        store.agents.record_agent(
            agent_id="AG-SUB-1",
            run_id=run_id,
            status="COMPLETE",
            prompt_path=str(tmp_path / "prompt.md"),
            report_path=str(report_file),
            stdout_path=str(stdout_file),
            stderr_path=str(stderr_file),
            pid=mock_proc.pid,
            result_verdict="PASS",
        )
        store.agents.update_agent(
            agent_id="AG-SUB-1",
            run_id=run_id,
            status="COMPLETE",
            result_verdict="PASS",
            exit_code=0,
        )

        # 4. Mark mock process complete (exit_code=0)
        mock_proc.complete(0)

        # 5. Subsequent tick: triggers 4-point deliverable reconciliation
        supervisor.run_supervisor_tick()

        # Verify job advanced through canonical lifecycle to COMPLETED
        cur.execute("SELECT status FROM jobs WHERE job_id = 'job-dispatch-1'")
        assert cur.fetchone()[0] == JobStatus.COMPLETED.value

        # Verify run reconciled verdict
        cur.execute("SELECT reconciled_verdict FROM runs WHERE run_id = ?", (run_id,))
        assert cur.fetchone()[0] == Verdict.PASS.value

        # Verify project lease released
        cur.execute(
            "SELECT holder_id FROM leases WHERE lease_name = 'PROJECT_proj-sup-1'",
        )
        assert cur.fetchone() is None

        # Verify supervisor returned to Zero-Idle posture
        assert supervisor.is_idle() is True

    def test_cold_start_crash_recovery(self, supervisor_env):
        """Verifies cold-start crash recovery handles interrupted runs without blindly restarting."""
        conn = supervisor_env["conn"]
        store = supervisor_env["store"]
        tmp_path = supervisor_env["tmp_path"]

        # Create job and interrupted run
        store.jobs.create_job(
            job_id="job-crashed-1",
            package_id="pkg-sup-1",
            project_id="proj-sup-1",
            status=JobStatus.RUNNING.value,
        )
        store.runs.create_run(
            run_id="run-crashed-1",
            job_id="job-crashed-1",
            package_id="pkg-sup-1",
            project_id="proj-sup-1",
            project="Supervisor Test Project",
            repository="test-repo",
            mode="isolated_branch_development",
            source_orchestrator=str(tmp_path),
            target_repo_path=str(supervisor_env["target_repo"]),
            run_dir=str(tmp_path / "run-crashed-1"),
            status=JobStatus.RUNNING.value,
        )

        # Initialize supervisor and trigger cold-start startup reconciliation
        supervisor = GraphPSupervisor(
            db_source=conn,
            instance_id="graph-p-recovery",
            process_checker=lambda pid: False,  # No process is alive
        )

        reconciled_runs = supervisor.reconcile_startup()
        assert "run-crashed-1" in reconciled_runs

        # Inviolable Invariant: Never blindly restart old RUNNING. Job must be marked INTERRUPTED or FAILED
        cur = conn.cursor()
        cur.execute("SELECT status FROM jobs WHERE job_id = 'job-crashed-1'")
        final_job_status = cur.fetchone()[0]
        assert final_job_status in ("INTERRUPTED", "FAILED", "BLOCKED")

    def test_graceful_shutdown(self, supervisor_env):
        """Verifies supervisor stops cleanly and updates operational state."""
        conn = supervisor_env["conn"]
        supervisor = GraphPSupervisor(db_source=conn, instance_id="graph-p-shutdown")

        supervisor.run_supervisor_tick()
        assert supervisor.state == SupervisorState.IDLE

        supervisor.stop()
        assert supervisor.state == SupervisorState.STOPPED

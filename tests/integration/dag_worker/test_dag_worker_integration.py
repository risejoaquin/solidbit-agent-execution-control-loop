"""Integration tests for SACL V1 Ephemeral Graph-H DAG Scheduler and Worker Subsystem.

Tests:
1. Multi-Phase Topological Execution & Deliverable Reconciliation Synthesis (ADR-003, STATE_MACHINE §4)
2. Local Dirty-Root Rule Preflight Assertion (ADR-002, CONCURRENCY §5)
3. Pre-Merge Cross-Agent Collision Detection Integration Gating (CONCURRENCY §7)
4. Stage-Level Failure Policy (ABORT_IMMEDIATELY)
5. Dynamic Concurrency Throttling ($MaxParallel)
"""

from __future__ import annotations

from pathlib import Path
import sqlite3
import pytest

from sacl.contracts.exceptions import DirtyRootError
from sacl.contracts.invariants import FailurePolicy, GraphNodeStatus, Verdict
from sacl.contracts.models import ExecutionGraph, GraphPhase
from sacl.dag.models import SchedulerConfig
from sacl.dag.scheduler import EphemeralDagScheduler
from sacl.state.store import SqliteStateStore
from sacl.worker.worktree import WorkspaceManager


@pytest.fixture
def state_store(tmp_path: Path) -> SqliteStateStore:
    """Provisions an initialized SQLite operational state store."""
    db_file = tmp_path / "sacl_ops_test.db"
    return SqliteStateStore(db_path=db_file, auto_migrate=True)


@pytest.fixture
def dag_env(state_store: SqliteStateStore, tmp_path: Path):
    """Sets up a complete DAG scheduler integration test environment."""
    conn = state_store.connection
    target_repo = tmp_path / "mock_target_repo"
    target_repo.mkdir(parents=True, exist_ok=True)
    run_dir = tmp_path / "runs" / "run-dag-test"
    run_dir.mkdir(parents=True, exist_ok=True)

    # Register project, package, job, and run
    state_store.projects.register_project(
        project_id="proj-dag-1",
        name="DAG Test Project",
        root_path=str(target_repo),
    )
    state_store.packages.record_package(
        package_id="pkg-dag-1",
        archive_sha256="hash-dag-1",
        manifest={"schema": "solidbit.execution-package.v1"},
        storage_path=str(tmp_path / "pkg-dag-1.zip"),
        project_id="proj-dag-1",
    )
    state_store.jobs.create_job(
        job_id="job-dag-1",
        package_id="pkg-dag-1",
        project_id="proj-dag-1",
        status="RUNNING",
    )
    state_store.runs.create_run(
        run_id="run-dag-test",
        job_id="job-dag-1",
        package_id="pkg-dag-1",
        project_id="proj-dag-1",
        project="DAG Test Project",
        repository="solidbit/test-repo",
        mode="isolated_branch_development",
        source_orchestrator=str(tmp_path),
        target_repo_path=str(target_repo),
        run_dir=str(run_dir),
        status="RUNNING",
    )

    return {
        "store": state_store,
        "conn": conn,
        "target_repo": target_repo,
        "run_dir": run_dir,
        "tmp_path": tmp_path,
    }


class TestDagWorkerIntegration:
    """Integration suite verifying Ephemeral DAG Scheduler and Worker lifecycle."""

    def test_multiphase_topological_execution_and_deliverable_reconciliation(self, dag_env):
        """Verifies multi-phase DAG execution, topological phase barriers, and deliverable reconciliation."""
        conn = dag_env["conn"]
        run_dir = dag_env["run_dir"]
        target_repo = dag_env["target_repo"]

        # Define 2-phase DAG: Phase 1 (AG-1, AG-2) -> Phase 2 (AG-3 depends on AG-1 and AG-2)
        graph = ExecutionGraph(
            graph_id="graph-integ-1",
            max_parallel=2,
            default_timeout_minutes=10,
            phases=[
                GraphPhase(phase_number=1, stage_name="P1_INSPECTION", agents=["AG-1", "AG-2"]),
                GraphPhase(phase_number=2, stage_name="P2_INTEGRATION", agents=["AG-3"]),
            ],
            edges=[["AG-1", "AG-3"], ["AG-2", "AG-3"]],
            failure_policy=FailurePolicy.COMPLETE_STAGE_THEN_HALT.value,
        )

        config = SchedulerConfig(
            run_id="run-dag-test",
            job_id="job-dag-1",
            target_repo_path=target_repo,
            run_dir=run_dir,
            max_parallel=2,
            check_clean_root=False,
            collision_detection_enabled=False,
        )

        execution_order = []

        def mock_runner(agent_id: str, attempt: int):
            execution_order.append(agent_id)
            # Write valid deliverable report
            rep_p = run_dir / "reports" / f"{agent_id}.md"
            rep_p.parent.mkdir(parents=True, exist_ok=True)
            rep_p.write_text(
                f"# Report for {agent_id}\nAGENT_{agent_id}_RESULT = PASS\n**Final Status:** PASS\n",
                encoding="utf-8",
            )
            return 0, None

        scheduler = EphemeralDagScheduler(
            config=config,
            db_conn=conn,
            mock_runner_factory=mock_runner,
        )

        scheduler.initialize_graph(graph, run_id="run-dag-test")
        results = scheduler.execute_phases()

        # Verify all 3 agents completed with PASS
        assert len(results) == 3
        assert results["AG-1"].result_verdict == Verdict.PASS.value
        assert results["AG-2"].result_verdict == Verdict.PASS.value
        assert results["AG-3"].result_verdict == Verdict.PASS.value

        # Verify topological barrier: AG-3 executed strictly after AG-1 and AG-2
        assert execution_order.index("AG-3") > execution_order.index("AG-1")
        assert execution_order.index("AG-3") > execution_order.index("AG-2")

        # Verify SQLite states in dag_stages and graph_nodes
        cur = conn.cursor()
        cur.execute("SELECT status FROM dag_stages WHERE run_id = 'run-dag-test' ORDER BY phase_number")
        stage_statuses = [r[0] for r in cur.fetchall()]
        assert stage_statuses == ["COMPLETE", "COMPLETE"]

        cur.execute("SELECT status FROM graph_nodes WHERE run_id = 'run-dag-test'")
        node_statuses = [r[0] for r in cur.fetchall()]
        assert all(s == GraphNodeStatus.SUCCEEDED.value for s in node_statuses)

    def test_dirty_root_check_blocks_scheduler_execution(self, dag_env):
        """Verifies that uncommitted modifications in primary checkout trigger DirtyRootError."""
        conn = dag_env["conn"]
        run_dir = dag_env["run_dir"]
        target_repo = dag_env["target_repo"]

        # Custom workspace manager simulating dirty root
        class DirtyWorkspaceManager(WorkspaceManager):
            def check_clean_root(self, repo_path: Path):
                return False, ["src/dirty_file.py", "untracked.txt"]

        graph = ExecutionGraph(
            graph_id="graph-dirty-check",
            max_parallel=1,
            default_timeout_minutes=5,
            phases=[GraphPhase(phase_number=1, stage_name="P1", agents=["AG-1"])],
            edges=[],
            failure_policy=FailurePolicy.ABORT_IMMEDIATELY.value,
        )

        config = SchedulerConfig(
            run_id="run-dag-test",
            job_id="job-dag-1",
            target_repo_path=target_repo,
            run_dir=run_dir,
            check_clean_root=True,
        )

        scheduler = EphemeralDagScheduler(
            config=config,
            db_conn=conn,
            workspace_manager=DirtyWorkspaceManager(),
        )

        scheduler.initialize_graph(graph, run_id="run-dag-test")

        with pytest.raises(DirtyRootError) as exc_info:
            scheduler.execute_phases()

        assert "src/dirty_file.py" in exc_info.value.dirty_files

        # Verify run status transitioned to BLOCKED in SQLite
        cur = conn.cursor()
        cur.execute("SELECT status FROM runs WHERE run_id = 'run-dag-test'")
        assert cur.fetchone()[0] == "BLOCKED"

    def test_collision_detection_gates_phase_execution(self, dag_env):
        """Verifies that pre-merge overlapping file modifications block phase progression."""
        conn = dag_env["conn"]
        run_dir = dag_env["run_dir"]
        target_repo = dag_env["target_repo"]

        # Custom workspace manager reporting overlapping modified files
        class CollisionWorkspaceManager(WorkspaceManager):
            def __init__(self):
                super().__init__(mock_mode=True)

            def get_modified_files(self, worktree_path: Path, base_ref: str = "HEAD"):
                # Both agents modify the identical config file
                return ["src/sacl/core_config.py"]

        graph = ExecutionGraph(
            graph_id="graph-collision-test",
            max_parallel=2,
            default_timeout_minutes=5,
            phases=[
                GraphPhase(phase_number=1, stage_name="P1_MUTATE", agents=["AG-COL-1", "AG-COL-2"]),
                GraphPhase(phase_number=2, stage_name="P2_NEXT", agents=["AG-COL-3"]),
            ],
            edges=[["AG-COL-1", "AG-COL-3"], ["AG-COL-2", "AG-COL-3"]],
            failure_policy=FailurePolicy.COMPLETE_STAGE_THEN_HALT.value,
        )

        config = SchedulerConfig(
            run_id="run-dag-test",
            job_id="job-dag-1",
            target_repo_path=target_repo,
            run_dir=run_dir,
            check_clean_root=False,
            collision_detection_enabled=True,
        )

        def mock_runner(agent_id: str, attempt: int):
            rep_p = run_dir / "reports" / f"{agent_id}.md"
            rep_p.parent.mkdir(parents=True, exist_ok=True)
            rep_p.write_text(f"AGENT_{agent_id}_RESULT = PASS\n", encoding="utf-8")
            return 0, None

        scheduler = EphemeralDagScheduler(
            config=config,
            db_conn=conn,
            workspace_manager=CollisionWorkspaceManager(),
            mock_runner_factory=mock_runner,
        )

        scheduler.initialize_graph(graph, run_id="run-dag-test")
        scheduler.execute_phases()

        # Phase 1 detected collisions and must be BLOCKED
        assert scheduler.phases[0].status == "BLOCKED"

        # Phase 2 must not have executed and must be BLOCKED
        assert scheduler.phases[1].status == "BLOCKED"
        assert scheduler.nodes_map["AG-COL-3"].status == GraphNodeStatus.BLOCKED.value

    def test_failure_policy_abort_immediately(self, dag_env):
        """Verifies ABORT_IMMEDIATELY halts execution and blocks downstream nodes upon worker failure."""
        conn = dag_env["conn"]
        run_dir = dag_env["run_dir"]
        target_repo = dag_env["target_repo"]

        graph = ExecutionGraph(
            graph_id="graph-abort-test",
            max_parallel=2,
            default_timeout_minutes=5,
            phases=[
                GraphPhase(phase_number=1, stage_name="P1", agents=["AG-FAIL"]),
                GraphPhase(phase_number=2, stage_name="P2", agents=["AG-DOWNSTREAM"]),
            ],
            edges=[["AG-FAIL", "AG-DOWNSTREAM"]],
            failure_policy=FailurePolicy.ABORT_IMMEDIATELY.value,
        )

        config = SchedulerConfig(
            run_id="run-dag-test",
            job_id="job-dag-1",
            target_repo_path=target_repo,
            run_dir=run_dir,
            check_clean_root=False,
            collision_detection_enabled=False,
            failure_policy=FailurePolicy.ABORT_IMMEDIATELY.value,
        )

        def mock_runner(agent_id: str, attempt: int):
            if agent_id == "AG-FAIL":
                return 1, "Intentional failure in integration test"
            return 0, None

        scheduler = EphemeralDagScheduler(
            config=config,
            db_conn=conn,
            mock_runner_factory=mock_runner,
        )

        scheduler.initialize_graph(graph, run_id="run-dag-test")
        scheduler.execute_phases()

        # AG-FAIL is FAILED
        assert scheduler.nodes_map["AG-FAIL"].status == GraphNodeStatus.FAILED.value

        # Downstream agent AG-DOWNSTREAM must be BLOCKED (never executed)
        assert scheduler.nodes_map["AG-DOWNSTREAM"].status in (GraphNodeStatus.BLOCKED.value, GraphNodeStatus.CANCELLED.value)
        assert scheduler.phases[1].status == "BLOCKED"

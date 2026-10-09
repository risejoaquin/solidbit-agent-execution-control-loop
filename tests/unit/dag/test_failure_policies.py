"""Tests for Graph-H failure policies: abort_immediately, complete_stage_then_halt, continue_independent."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import pytest

from sacl.contracts.invariants import FailurePolicy, GraphNodeStatus
from sacl.contracts.models import ExecutionGraph, GraphPhase
from sacl.dag.models import SchedulerConfig
from sacl.dag.scheduler import EphemeralDagScheduler


def make_mock_runner(failing_agents: set[str], pass_verdict: str = "PASS"):
    """Factory to produce deterministic mock runner for agents."""
    def _runner(agent_id: str, attempt: int) -> Tuple[int, Optional[str]]:
        if agent_id in failing_agents:
            return 1, f"Simulated failure for {agent_id}"
        return 0, None
    return _runner


def test_failure_policy_complete_stage_then_halt(tmp_path: Path, sqlite_memory_db):
    """complete_stage_then_halt allows active stage nodes to finish, but halts before next stage."""
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    target_repo = tmp_path / "repo"
    target_repo.mkdir()

    # Phase 1 has A and B; B fails. Phase 2 has C (depends on B).
    graph = ExecutionGraph(
        graph_id="GRAPH-STAGE-HALT",
        max_parallel=2,
        default_timeout_minutes=30,
        phases=[
            GraphPhase(phase_number=1, stage_name="P1", agents=["AG-A", "AG-B"]),
            GraphPhase(phase_number=2, stage_name="P2", agents=["AG-C"]),
        ],
        edges=[["AG-B", "AG-C"]],
        failure_policy=FailurePolicy.COMPLETE_STAGE_THEN_HALT.value,
    )

    # Prepare report files
    for ag in ["AG-A", "AG-C"]:
        rep = run_dir / "reports" / f"{ag}.md"
        rep.parent.mkdir(parents=True, exist_ok=True)
        rep.write_text(f"AGENT_{ag.replace('-', '_')}_RESULT = PASS\n")
        out = run_dir / "logs" / f"{ag}.stdout.log"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("ok\n")
        err = run_dir / "logs" / f"{ag}.stderr.log"
        err.write_text("")

    # AG-B does not have a report (fails)
    out_b = run_dir / "logs" / "AG-B.stdout.log"
    out_b.parent.mkdir(parents=True, exist_ok=True)
    out_b.write_text("error log\n")
    err_b = run_dir / "logs" / "AG-B.stderr.log"
    err_b.write_text("error\n")

    # Insert parent job row in sqlite
    sqlite_memory_db.execute(
        """
        INSERT INTO jobs (job_id, status, created_at, updated_at)
        VALUES ('job-01', 'RUNNING', '2026-10-07T00:00:00Z', '2026-10-07T00:00:00Z');
        """
    )
    sqlite_memory_db.execute(
        """
        INSERT INTO runs (
            run_id, job_id, package_id, project, repository, mode,
            source_orchestrator, target_repo_path, run_dir, status,
            ready_for_integration, started_at
        ) VALUES (
            'run-halt-01', 'job-01', 'pkg-01', 'solidbit', 'repo',
            'dev', 'orch', ?, ?, 'RUNNING', 'NO', '2026-10-07T00:00:00Z'
        )
        """,
        (str(target_repo), str(run_dir)),
    )
    sqlite_memory_db.commit()

    config = SchedulerConfig(
        run_id="run-halt-01",
        job_id="job-01",
        target_repo_path=target_repo,
        run_dir=run_dir,
        max_parallel=2,
        failure_policy=FailurePolicy.COMPLETE_STAGE_THEN_HALT.value,
        check_clean_root=False,
    )

    runner = make_mock_runner(failing_agents={"AG-B"})
    scheduler = EphemeralDagScheduler(
        config=config,
        db_conn=sqlite_memory_db,
        mock_runner_factory=runner,
    )

    scheduler.initialize_graph(graph, "run-halt-01")
    results = scheduler.execute_phases()

    # AG-A in Phase 1 succeeded
    assert "AG-A" in results
    assert results["AG-A"].status == "SUCCEEDED"

    # AG-B in Phase 1 failed
    assert "AG-B" in results
    assert results["AG-B"].status == "FAILED"

    # Phase 2 AG-C was halted and never executed!
    assert "AG-C" not in results
    assert scheduler.nodes_map["AG-C"].status == GraphNodeStatus.BLOCKED.value


def test_failure_policy_abort_immediately(tmp_path: Path, sqlite_memory_db):
    """abort_immediately terminates active execution as soon as a failure is detected."""
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    target_repo = tmp_path / "repo"
    target_repo.mkdir()

    graph = ExecutionGraph(
        graph_id="GRAPH-ABORT-IMM",
        max_parallel=1,
        default_timeout_minutes=30,
        phases=[
            GraphPhase(phase_number=1, stage_name="P1", agents=["AG-FAIL", "AG-NEXT"]),
        ],
        edges=[],
        failure_policy=FailurePolicy.ABORT_IMMEDIATELY.value,
    )

    # Insert parent job row in sqlite
    sqlite_memory_db.execute(
        """
        INSERT INTO jobs (job_id, status, created_at, updated_at)
        VALUES ('job-01', 'RUNNING', '2026-10-07T00:00:00Z', '2026-10-07T00:00:00Z');
        """
    )
    sqlite_memory_db.execute(
        """
        INSERT INTO runs (
            run_id, job_id, package_id, project, repository, mode,
            source_orchestrator, target_repo_path, run_dir, status,
            ready_for_integration, started_at
        ) VALUES (
            'run-abort-01', 'job-01', 'pkg-01', 'solidbit', 'repo',
            'dev', 'orch', ?, ?, 'RUNNING', 'NO', '2026-10-07T00:00:00Z'
        )
        """,
        (str(target_repo), str(run_dir)),
    )
    sqlite_memory_db.commit()

    config = SchedulerConfig(
        run_id="run-abort-01",
        job_id="job-01",
        target_repo_path=target_repo,
        run_dir=run_dir,
        max_parallel=1,
        failure_policy=FailurePolicy.ABORT_IMMEDIATELY.value,
        check_clean_root=False,
    )

    runner = make_mock_runner(failing_agents={"AG-FAIL"})
    scheduler = EphemeralDagScheduler(
        config=config,
        db_conn=sqlite_memory_db,
        mock_runner_factory=runner,
    )

    scheduler.initialize_graph(graph, "run-abort-01")
    results = scheduler.execute_phases()

    assert scheduler.is_cancelled is True
    assert "AG-FAIL" in results
    assert results["AG-FAIL"].status == "FAILED"
    assert "AG-NEXT" not in results

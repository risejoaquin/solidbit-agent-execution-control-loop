"""End-to-end unit tests for Ephemeral Graph-H DAG Scheduler and SQLite state store."""

from __future__ import annotations

from pathlib import Path

from sacl.contracts.invariants import Verdict
from sacl.contracts.models import ExecutionGraph, GraphNode, GraphPhase
from sacl.dag.models import SchedulerConfig
from sacl.dag.scheduler import EphemeralDagScheduler
from sacl.observability.audit import AuditEventEmitter


def test_scheduler_end_to_end_phased_wave_success(tmp_path: Path, sqlite_memory_db):
    audit = AuditEventEmitter(sqlite_memory_db)
    run_dir = tmp_path / "run_e2e"
    run_dir.mkdir()
    target_repo = tmp_path / "target_repo"
    target_repo.mkdir()

    # Create 2-phase execution graph matching frozen example
    graph = ExecutionGraph(
        graph_id="SACL-W0-1-GRAPH",
        max_parallel=2,
        default_timeout_minutes=30,
        phases=[
            GraphPhase(
                phase_number=1,
                stage_name="MATERIALIZATION",
                agents=["AG-PROTOCOL-MAT", "AG-ARCH-MAT"],
            ),
            GraphPhase(phase_number=2, stage_name="QA_AUDIT", agents=["AG-QA-MAT"]),
        ],
        nodes=[
            GraphNode(
                node_id="AG-PROTOCOL-MAT",
                agent_id="AG-PROTOCOL-MAT",
                phase_number=1,
                timeout_minutes=20,
            ),
            GraphNode(
                node_id="AG-ARCH-MAT", agent_id="AG-ARCH-MAT", phase_number=1, timeout_minutes=25
            ),
            GraphNode(
                node_id="AG-QA-MAT", agent_id="AG-QA-MAT", phase_number=2, timeout_minutes=20
            ),
        ],
        edges=[
            ["AG-PROTOCOL-MAT", "AG-QA-MAT"],
            ["AG-ARCH-MAT", "AG-QA-MAT"],
        ],
        failure_policy="complete_stage_then_halt",
    )

    # Prepare deliverable reports and logs
    for ag in ["AG-PROTOCOL-MAT", "AG-ARCH-MAT", "AG-QA-MAT"]:
        rep = run_dir / "reports" / f"{ag}.md"
        rep.parent.mkdir(parents=True, exist_ok=True)
        rep.write_text(f"# Deliverable for {ag}\n\nAGENT_{ag.replace('-', '_')}_RESULT = PASS\n")

        out = run_dir / "logs" / f"{ag}.stdout.log"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(f"Agent {ag} initialized.\nAgent {ag} finished.\n")

        err = run_dir / "logs" / f"{ag}.stderr.log"
        err.parent.mkdir(parents=True, exist_ok=True)
        err.write_text("")

    # Insert parent job row
    sqlite_memory_db.execute(
        """
        INSERT INTO jobs (job_id, status, created_at, updated_at)
        VALUES ('job-e2e-001', 'RUNNING', '2026-10-07T00:00:00Z', '2026-10-07T00:00:00Z');
        """
    )
    sqlite_memory_db.execute(
        """
        INSERT INTO runs (
            run_id, job_id, package_id, project, repository, mode,
            source_orchestrator, target_repo_path, run_dir, status,
            ready_for_integration, started_at
        ) VALUES (
            'run-e2e-001', 'job-e2e-001', 'pkg-e2e-001', 'solidbit', 'repo',
            'dev', 'orch', ?, ?, 'RUNNING', 'NO', '2026-10-07T00:00:00Z'
        )
        """,
        (str(target_repo), str(run_dir)),
    )
    sqlite_memory_db.commit()

    config = SchedulerConfig(
        run_id="run-e2e-001",
        job_id="job-e2e-001",
        target_repo_path=target_repo,
        run_dir=run_dir,
        max_parallel=2,
        check_clean_root=False,
    )

    def mock_runner(ag, att):
        return (0, None)

    scheduler = EphemeralDagScheduler(
        config=config,
        db_conn=sqlite_memory_db,
        audit_emitter=audit,
        mock_runner_factory=mock_runner,
    )

    scheduler.initialize_graph(graph, "run-e2e-001")
    results = scheduler.execute_phases()

    # All 3 agents completed with SUCCEEDED and PASS verdict
    assert len(results) == 3
    for ag in ["AG-PROTOCOL-MAT", "AG-ARCH-MAT", "AG-QA-MAT"]:
        assert ag in results
        assert results[ag].status == "SUCCEEDED"
        assert results[ag].result_verdict == Verdict.PASS.value

    # Verify SQLite persistence
    cur = sqlite_memory_db.cursor()

    # 1. runs table: status must be VERIFYING (or COMPLETED), verdict PASS, ready_for_integration YES
    cur.execute(
        "SELECT status, reconciled_verdict, ready_for_integration FROM runs WHERE run_id = 'run-e2e-001'"
    )
    run_row = cur.fetchone()
    assert run_row[0] == "VERIFYING"
    assert run_row[1] == "PASS"
    assert run_row[2] == "YES"

    # 2. graph_nodes table: all 3 must be SUCCEEDED
    cur.execute(
        "SELECT node_id, status, result_verdict FROM graph_nodes WHERE run_id = 'run-e2e-001'"
    )
    nodes_rows = {row[0]: (row[1], row[2]) for row in cur.fetchall()}
    assert len(nodes_rows) == 3
    for nid, (st, vd) in nodes_rows.items():
        assert st == "SUCCEEDED"
        assert vd == "PASS"

    # 3. dag_stages table: both stages COMPLETE
    cur.execute("SELECT phase_number, status FROM dag_stages WHERE run_id = 'run-e2e-001'")
    stages = cur.fetchall()
    assert len(stages) == 2
    for p_num, st in stages:
        assert st == "COMPLETE"

    # 4. node_attempts table: exactly 3 attempts recorded
    cur.execute(
        "SELECT node_id, attempt_number, status, verdict FROM node_attempts WHERE run_id = 'run-e2e-001'"
    )
    attempts = cur.fetchall()
    assert len(attempts) == 3
    for nid, att_num, st, vd in attempts:
        assert att_num == 1
        assert st == "SUCCEEDED"
        assert vd == "PASS"


def test_scheduler_cancellation(tmp_path: Path, sqlite_memory_db):
    run_dir = tmp_path / "run_cancel"
    run_dir.mkdir()
    target_repo = tmp_path / "target_repo"
    target_repo.mkdir()

    graph = ExecutionGraph(
        graph_id="GRAPH-CANCEL",
        max_parallel=2,
        default_timeout_minutes=30,
        phases=[GraphPhase(phase_number=1, stage_name="P1", agents=["AG-LONG"])],
        edges=[],
        failure_policy="complete_stage_then_halt",
    )

    sqlite_memory_db.execute(
        """
        INSERT INTO jobs (job_id, status, created_at, updated_at)
        VALUES ('job-can-001', 'RUNNING', '2026-10-07T00:00:00Z', '2026-10-07T00:00:00Z');
        """
    )
    sqlite_memory_db.execute(
        """
        INSERT INTO runs (
            run_id, job_id, package_id, project, repository, mode,
            source_orchestrator, target_repo_path, run_dir, status,
            ready_for_integration, started_at
        ) VALUES (
            'run-can-001', 'job-can-001', 'pkg-can-001', 'solidbit', 'repo',
            'dev', 'orch', ?, ?, 'RUNNING', 'NO', '2026-10-07T00:00:00Z'
        )
        """,
        (str(target_repo), str(run_dir)),
    )
    sqlite_memory_db.commit()

    config = SchedulerConfig(
        run_id="run-can-001",
        job_id="job-can-001",
        target_repo_path=target_repo,
        run_dir=run_dir,
        max_parallel=2,
        check_clean_root=False,
    )

    scheduler = EphemeralDagScheduler(
        config=config,
        db_conn=sqlite_memory_db,
    )
    scheduler.initialize_graph(graph, "run-can-001")

    # Cancel execution
    scheduler.cancel_execution(reason="Operator requested safe stop")

    assert scheduler.is_cancelled is True
    assert scheduler.cancel_reason == "Operator requested safe stop"

    cur = sqlite_memory_db.cursor()
    cur.execute("SELECT status FROM runs WHERE run_id = 'run-can-001'")
    assert cur.fetchone()[0] == "CANCELLED"

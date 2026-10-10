"""Tests for ResultCollector Subsystem.

Validates end-to-end multi-agent 4-point reconciliation, collision evaluation,
and overall run verdict aggregation.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import pytest

from sacl.contracts.schema_validator import SchemaValidator
from sacl.results.collector import ResultCollector
from sacl.results.collision import CollisionDetector
from sacl.results.reconciler import ResultReconciler


@pytest.fixture
def collector(schema_validator: SchemaValidator) -> ResultCollector:
    reconciler = ResultReconciler(validator=schema_validator)
    collision_detector = CollisionDetector()
    return ResultCollector(reconciler=reconciler, collision_detector=collision_detector)


@pytest.fixture
def multi_agent_run_workspace(tmp_path: Path, sqlite_memory_db: sqlite3.Connection):
    run_dir = tmp_path / "multi_agent_run"
    run_dir.mkdir(parents=True, exist_ok=True)
    reports_dir = run_dir / "reports"
    reports_dir.mkdir(exist_ok=True)
    logs_dir = run_dir / "logs"
    logs_dir.mkdir(exist_ok=True)

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Seed job and run in SQLite
    cursor = sqlite_memory_db.cursor()
    cursor.execute(
        """
        INSERT INTO jobs (job_id, status, priority, created_at, updated_at)
        VALUES ('job-coll-001', 'RUNNING', 0, ?, ?)
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
            'run-coll-001', 'job-coll-001', 'pkg-001', 'solidbit', 'org/repo', 'isolated_branch',
            '', '', '', 'RUNNING', 'NO', ?
        )
        """,
        (now_iso,),
    )
    sqlite_memory_db.commit()

    return run_dir, sqlite_memory_db


def test_collect_all_passing_agents(
    collector: ResultCollector, multi_agent_run_workspace
) -> None:
    run_dir, db_conn = multi_agent_run_workspace
    reports_dir = run_dir / "reports"
    logs_dir = run_dir / "logs"

    # Agent 1
    rep1 = reports_dir / "AG-1.REPORT.md"
    rep1.write_text("AGENT_1_RESULT = PASS\n", encoding="utf-8")
    log1 = logs_dir / "AG-1.stdout.log"
    log1.write_text("Done", encoding="utf-8")
    err1 = logs_dir / "AG-1.stderr.log"
    err1.write_text("", encoding="utf-8")

    # Agent 2
    rep2 = reports_dir / "AG-2.REPORT.md"
    rep2.write_text("AGENT_2_RESULT = PASS\n", encoding="utf-8")
    log2 = logs_dir / "AG-2.stdout.log"
    log2.write_text("Done", encoding="utf-8")
    err2 = logs_dir / "AG-2.stderr.log"
    err2.write_text("", encoding="utf-8")

    agent_specs = [
        {
            "agent_id": "AG-1",
            "report_path": rep1,
            "stdout_path": log1,
            "stderr_path": err1,
            "worktree_path": run_dir,
            "modified_files": ["docs/part1.md"],
        },
        {
            "agent_id": "AG-2",
            "report_path": rep2,
            "stdout_path": log2,
            "stderr_path": err2,
            "worktree_path": run_dir,
            "modified_files": ["docs/part2.md"],
        },
    ]

    res = collector.collect_run_results(
        run_id="run-coll-001",
        job_id="job-coll-001",
        run_dir=run_dir,
        agent_specs=agent_specs,
        db_conn=db_conn,
    )

    assert res.overall_verdict == "PASS"
    assert res.ready_for_integration == "YES"
    assert len(res.agent_results) == 2
    assert res.agent_results[0].result_verdict == "PASS"
    assert res.agent_results[1].result_verdict == "PASS"


def test_collect_with_failure(
    collector: ResultCollector, multi_agent_run_workspace
) -> None:
    run_dir, db_conn = multi_agent_run_workspace
    reports_dir = run_dir / "reports"
    logs_dir = run_dir / "logs"

    # Agent 1 passes
    rep1 = reports_dir / "AG-1.REPORT.md"
    rep1.write_text("AGENT_1_RESULT = PASS\n", encoding="utf-8")
    log1 = logs_dir / "AG-1.stdout.log"
    log1.write_text("Done", encoding="utf-8")
    err1 = logs_dir / "AG-1.stderr.log"
    err1.write_text("", encoding="utf-8")

    # Agent 2 fails (missing report)
    rep2 = reports_dir / "AG-FAIL.REPORT.md"  # Does not exist!
    log2 = logs_dir / "AG-FAIL.stdout.log"
    log2.write_text("Fatal error", encoding="utf-8")
    err2 = logs_dir / "AG-FAIL.stderr.log"
    err2.write_text("Crash", encoding="utf-8")

    agent_specs = [
        {
            "agent_id": "AG-1",
            "report_path": rep1,
            "stdout_path": log1,
            "stderr_path": err1,
            "worktree_path": run_dir,
        },
        {
            "agent_id": "AG-FAIL",
            "report_path": rep2,
            "stdout_path": log2,
            "stderr_path": err2,
            "worktree_path": run_dir,
        },
    ]

    res = collector.collect_run_results(
        run_id="run-coll-001",
        job_id="job-coll-001",
        run_dir=run_dir,
        agent_specs=agent_specs,
        db_conn=db_conn,
    )

    assert res.overall_verdict == "FAIL"


def test_collect_with_done_review_required(
    collector: ResultCollector, multi_agent_run_workspace
) -> None:
    run_dir, db_conn = multi_agent_run_workspace
    reports_dir = run_dir / "reports"
    logs_dir = run_dir / "logs"

    rep1 = reports_dir / "AG-1.REPORT.md"
    rep1.write_text("AGENT_1_RESULT = DONE_REVIEW_REQUIRED\n", encoding="utf-8")
    log1 = logs_dir / "AG-1.stdout.log"
    log1.write_text("Done", encoding="utf-8")
    err1 = logs_dir / "AG-1.stderr.log"
    err1.write_text("", encoding="utf-8")

    agent_specs = [
        {
            "agent_id": "AG-1",
            "report_path": rep1,
            "stdout_path": log1,
            "stderr_path": err1,
            "worktree_path": run_dir,
        }
    ]

    res = collector.collect_run_results(
        run_id="run-coll-001",
        job_id="job-coll-001",
        run_dir=run_dir,
        agent_specs=agent_specs,
        db_conn=db_conn,
    )

    assert res.overall_verdict == "DONE_REVIEW_REQUIRED"
    assert res.overall_verdict != "PASS"

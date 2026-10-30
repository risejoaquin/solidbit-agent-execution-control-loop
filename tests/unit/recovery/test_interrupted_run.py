"""Unit tests for SACL V1 Interrupted Run Crash Recovery & State Transitions."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pytest

from sacl.contracts.invariants import Verdict
from sacl.recovery.interrupted import (
    find_interrupted_runs,
    recover_interrupted_run,
)
from sacl.recovery.process_identity import MockProcessInspector
from sacl.recovery.safe_to_resume import SafeToResumeOutcome
from sacl.recovery.worktree_inspection import MockGitClient


@pytest.fixture
def populated_db(sqlite_memory_db: sqlite3.Connection, tmp_path: Path) -> sqlite3.Connection:
    """Pre-populates a minimal valid schema for packages, jobs, runs, agents, and graph_nodes."""
    now = datetime.now(timezone.utc).isoformat()
    conn = sqlite_memory_db

    with conn:
        # 1. Package
        conn.execute(
            """
            INSERT INTO packages (package_id, archive_sha256, manifest_json, storage_path, created_at, status)
            VALUES ('pkg-test-01', 'hash123', '{}', '/tmp/pkg.zip', ?, 'VALIDATED');
            """,
            (now,),
        )
        # 2. Job
        conn.execute(
            """
            INSERT INTO jobs (job_id, package_id, status, created_at, updated_at)
            VALUES ('job-test-01', 'pkg-test-01', 'RUNNING', ?, ?);
            """,
            (now, now),
        )
        # 3. Run
        repo_dir = str(tmp_path / "repo")
        Path(repo_dir).mkdir(parents=True, exist_ok=True)
        run_dir = str(tmp_path / "runs" / "run-test-01")
        Path(run_dir).mkdir(parents=True, exist_ok=True)

        conn.execute(
            """
            INSERT INTO runs (
                run_id, job_id, package_id, project, repository, mode,
                source_orchestrator, target_repo_path, run_dir, status,
                started_at
            ) VALUES (
                'run-test-01', 'job-test-01', 'pkg-test-01', 'TestProject', 'test/repo',
                'isolated_branch_development', '/tmp/source', ?, ?, 'RUNNING', ?
            );
            """,
            (repo_dir, run_dir, now),
        )
    return conn


def test_find_interrupted_runs(populated_db: sqlite3.Connection) -> None:
    """Verifies that runs in RUNNING status are discovered."""
    runs = find_interrupted_runs(populated_db)
    assert len(runs) == 1
    assert runs[0]["run_id"] == "run-test-01"


def test_interrupted_run_halted_by_dirty_primary_root(
    populated_db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    """Local Dirty-Root Rule: If primary checkout is dirty, recovery halts with BLOCKED."""
    runs = find_interrupted_runs(populated_db)
    run_row = runs[0]

    mock_git = MockGitClient()
    mock_git.set_status(run_row["target_repo_path"], [" M uncommitted_file.py"])

    report = recover_interrupted_run(
        run_row=run_row,
        conn=populated_db,
        git_client=mock_git,
    )

    assert report.dirty_root_halted is True
    assert report.final_status == "BLOCKED"
    assert report.final_verdict == Verdict.BLOCKED.value
    assert report.run_decision.outcome == SafeToResumeOutcome.BLOCKED_DIRTY_ROOT

    # Verify SQLite update
    cursor = populated_db.cursor()
    cursor.execute(
        "SELECT status, reconciled_verdict, error_summary FROM runs WHERE run_id = 'run-test-01';"
    )
    db_run = cursor.fetchone()
    assert db_run["status"] == "BLOCKED"
    assert db_run["reconciled_verdict"] == "BLOCKED"
    assert "DIRTY_ROOT_BLOCKS_RECOVERY" in db_run["error_summary"]


def test_interrupted_run_surviving_worker_resumes_supervision(
    populated_db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    """Worker survived supervisor crash -> reconnects supervision and stays RUNNING."""
    now = datetime.now(timezone.utc).isoformat()
    repo_dir = tmp_path / "repo"
    mock_git = MockGitClient()
    mock_git.set_status(repo_dir, [])

    # Register an agent with an active process
    with populated_db:
        populated_db.execute(
            """
            INSERT INTO agents (
                agent_id, run_id, status, pid, prompt_path, report_path, stdout_path, stderr_path,
                started_at, updated_at
            ) VALUES (
                'AG-SURVIVOR', 'run-test-01', 'RUNNING', 1111, '/tmp/prompt.md',
                '/tmp/report.md', '/tmp/out.log', '/tmp/err.log', ?, ?
            );
            """,
            (now, now),
        )

    inspector = MockProcessInspector()
    inspector.register_process(
        pid=1111,
        process_name="pwsh",
        is_active=True,
        start_time=datetime.now(timezone.utc),
    )

    runs = find_interrupted_runs(populated_db)
    report = recover_interrupted_run(
        run_row=runs[0],
        conn=populated_db,
        inspector=inspector,
        git_client=mock_git,
    )

    assert report.final_status == "RUNNING"
    assert report.run_decision.outcome == SafeToResumeOutcome.RESUME_SUPERVISION
    assert report.agent_reports[0].reconciled_status == "RUNNING"
    assert report.agent_reports[0].is_alive is True


def test_interrupted_run_reconciles_passing_deliverables(
    populated_db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    """Terminated worker that left passing report on disk reconciles to COMPLETE."""
    now = datetime.now(timezone.utc).isoformat()
    repo_dir = tmp_path / "repo"
    mock_git = MockGitClient()
    mock_git.set_status(repo_dir, [])

    # Create deliverable report file
    report_file = tmp_path / "AG-SCHEMA.REPORT.md"
    report_file.write_text(
        "# AG-SCHEMA REPORT\n\nAll tasks verified.\n\nAGENT_AG_SCHEMA_RESULT = PASS\n",
        encoding="utf-8",
    )

    wt_dir = tmp_path / "wt-schema"
    wt_dir.mkdir()
    mock_git.set_status(wt_dir, [])

    with populated_db:
        populated_db.execute(
            """
            INSERT INTO graph_nodes (
                run_id, node_id, job_id, phase_number, stage_name, agent_id, status
            ) VALUES ('run-test-01', 'NODE-SCHEMA', 'job-test-01', 1, 'SCHEMA', 'AG-SCHEMA', 'RUNNING');
            """
        )
        populated_db.execute(
            """
            INSERT INTO agents (
                agent_id, run_id, node_id, status, pid, worktree_path, branch, prompt_path,
                report_path, stdout_path, stderr_path, started_at, updated_at
            ) VALUES (
                'AG-SCHEMA', 'run-test-01', 'NODE-SCHEMA', 'RUNNING', 2222, ?, 'feature/schema',
                '/tmp/prompt.md', ?, '/tmp/out.log', '/tmp/err.log', ?, ?
            );
            """,
            (str(wt_dir), str(report_file), now, now),
        )

    inspector = MockProcessInspector()
    # Process is terminated (exited 0)
    inspector.register_process(
        pid=2222,
        process_name="agy",
        is_active=False,
        exit_code=0,
    )

    runs = find_interrupted_runs(populated_db)
    report = recover_interrupted_run(
        run_row=runs[0],
        conn=populated_db,
        inspector=inspector,
        git_client=mock_git,
    )

    assert report.final_status == "VERIFYING"
    assert report.final_verdict == Verdict.PASS.value
    assert report.agent_reports[0].reconciled_status == "COMPLETE"
    assert report.agent_reports[0].reconciled_verdict == "PASS"

    # Verify SQLite updates
    cursor = populated_db.cursor()
    cursor.execute("SELECT status, result_verdict FROM agents WHERE agent_id = 'AG-SCHEMA';")
    ag_db = cursor.fetchone()
    assert ag_db["status"] == "COMPLETE"
    assert ag_db["result_verdict"] == "PASS"

    cursor.execute("SELECT status, result_verdict FROM graph_nodes WHERE node_id = 'NODE-SCHEMA';")
    gn_db = cursor.fetchone()
    assert gn_db["status"] == "SUCCEEDED"
    assert gn_db["result_verdict"] == "PASS"


def test_interrupted_run_uncommitted_worktree_yields_blocked_recovery_review(
    populated_db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    """Worker left uncommitted changes -> FAILED (UNCOMMITTED_CHANGES), run BLOCKED (BLOCKED_RECOVERY_REVIEW)."""
    now = datetime.now(timezone.utc).isoformat()
    repo_dir = tmp_path / "repo"
    mock_git = MockGitClient()
    mock_git.set_status(repo_dir, [])

    wt_dir = tmp_path / "wt-dirty"
    wt_dir.mkdir()
    # Dirty worktree!
    mock_git.set_status(wt_dir, [" M src/dirty.py"])

    report_file = tmp_path / "AG-DIRTY.REPORT.md"
    report_file.write_text("AGENT_AG_DIRTY_RESULT = PASS\n", encoding="utf-8")

    with populated_db:
        populated_db.execute(
            """
            INSERT INTO agents (
                agent_id, run_id, status, pid, worktree_path, prompt_path,
                report_path, stdout_path, stderr_path, started_at, updated_at
            ) VALUES (
                'AG-DIRTY', 'run-test-01', 'RUNNING', 3333, ?, '/tmp/p.md',
                ?, '/tmp/o.log', '/tmp/e.log', ?, ?
            );
            """,
            (str(wt_dir), str(report_file), now, now),
        )

    inspector = MockProcessInspector()
    inspector.register_process(pid=3333, process_name="agy", is_active=False, exit_code=0)

    runs = find_interrupted_runs(populated_db)
    report = recover_interrupted_run(
        run_row=runs[0],
        conn=populated_db,
        inspector=inspector,
        git_client=mock_git,
    )

    assert report.final_status == "BLOCKED"
    assert report.run_decision.outcome == SafeToResumeOutcome.BLOCKED_RECOVERY_REVIEW
    assert report.agent_reports[0].reconciled_status == "FAILED"
    assert report.agent_reports[0].reconciled_verdict == "FAILED"
    assert "UNCOMMITTED_CHANGES_ON_RECOVERY" in str(report.agent_reports[0].error_message)


def test_interrupted_run_missing_deliverables_transitions_to_interrupted(
    populated_db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    """Terminated worker with missing deliverables -> run marked INTERRUPTED."""
    now = datetime.now(timezone.utc).isoformat()
    repo_dir = tmp_path / "repo"
    mock_git = MockGitClient()
    mock_git.set_status(repo_dir, [])

    missing_report = tmp_path / "missing_report.md"

    with populated_db:
        populated_db.execute(
            """
            INSERT INTO agents (
                agent_id, run_id, status, pid, prompt_path,
                report_path, stdout_path, stderr_path, started_at, updated_at
            ) VALUES (
                'AG-CRASHED', 'run-test-01', 'RUNNING', 4444, '/tmp/p.md',
                ?, '/tmp/o.log', '/tmp/e.log', ?, ?
            );
            """,
            (str(missing_report), now, now),
        )

    inspector = MockProcessInspector()
    inspector.register_process(pid=4444, process_name="agy", is_active=False, exit_code=1)

    runs = find_interrupted_runs(populated_db)
    report = recover_interrupted_run(
        run_row=runs[0],
        conn=populated_db,
        inspector=inspector,
        git_client=mock_git,
    )

    assert report.final_status == "INTERRUPTED"
    assert report.run_decision.outcome == SafeToResumeOutcome.CANNOT_RESUME_INTERRUPTED
    assert report.agent_reports[0].reconciled_status == "FAILED"
    assert report.agent_reports[0].reconciled_verdict == "FAILED"

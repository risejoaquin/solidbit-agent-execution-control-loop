"""Crash-restart integration: a *file-backed* SQLite state survives host supervisor loss.

Everything is under pytest tmp_path. Process identities and Git status are
deterministic mocks. Never spawns a worker, contacts GitHub, or executes agy.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pytest

from sacl.recovery.process_identity import MockProcessInspector
from sacl.recovery.startup_reconciliation import StartupReconciliationEngine
from sacl.recovery.worktree_inspection import MockGitClient
from sacl.state.store import SqliteStateStore


@pytest.mark.parametrize(
    ("scenario", "expected_run", "expected_supervisor"),
    [
        ("dead_missing", "INTERRUPTED", "RECONCILED"),
        ("dead_report_pass", "VERIFYING", "RECONCILED"),
        ("surviving_process", "RUNNING", "SUPERVISION_RESUMED"),
        ("dirty_primary", "BLOCKED", "HALTED_SAFETY"),
    ],
)
def test_cold_start_recovers_file_backed_state_without_restarting_agents(
    tmp_path: Path,
    scenario: str,
    expected_run: str,
    expected_supervisor: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Restart must reconcile persisted evidence, never launch the old process."""
    db_path = tmp_path / "sacl-recovery-test.sqlite"
    repo = tmp_path / "checkout"
    repo.mkdir()
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    worktree = tmp_path / "mock-worktree"
    worktree.mkdir()
    report_path = run_dir / "reports" / "AG-TEST.md"
    now = datetime.now(timezone.utc).isoformat()

    store = SqliteStateStore(db_path=db_path, auto_migrate=True)
    try:
        with store.connection:
            store.connection.execute(
                """INSERT INTO packages
                   (package_id, archive_sha256, manifest_json, storage_path, created_at, status)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                ("pkg-r", "checksum-mock", "{}", str(tmp_path / "package.zip"), now, "VALIDATED"),
            )
            store.connection.execute(
                """INSERT INTO jobs (job_id, package_id, status, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?)""",
                ("job-r", "pkg-r", "RUNNING", now, now),
            )
            store.connection.execute(
                """INSERT INTO runs
                   (run_id, job_id, package_id, project, repository, mode,
                    source_orchestrator, target_repo_path, run_dir, status, started_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    "run-r", "job-r", "pkg-r", "sandbox", "sandbox-only",
                    "isolated_branch_development", str(tmp_path),
                    str(repo), str(run_dir), "RUNNING", now,
                ),
            )
            store.connection.execute(
                """INSERT INTO agents
                   (agent_id, run_id, status, pid, worktree_path, branch,
                    prompt_path, report_path, stdout_path, stderr_path,
                    started_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    "AG-TEST", "run-r", "RUNNING", 99921,
                    str(worktree), "task/recovery",
                    str(run_dir / "prompt.md"), str(report_path),
                    str(run_dir / "stdout.log"), str(run_dir / "stderr.log"),
                    now, now,
                ),
            )
        assert store.connection.execute("PRAGMA journal_mode").fetchone()[0].lower() == "wal"
    finally:
        # Simulates abrupt disappearance of the supervisor's DB connection.
        store.close()

    git_client = MockGitClient()
    git_client.set_status(repo, [" M preserved-human-file.txt"] if scenario == "dirty_primary" else [])
    git_client.set_status(worktree, [])
    inspector = MockProcessInspector()
    if scenario == "dead_report_pass":
        report_path.parent.mkdir()
        report_path.write_text("AGENT_AG_TEST_RESULT = PASS\n", encoding="utf-8")
    if scenario == "surviving_process":
        inspector.register_process(
            99921, "agy", is_active=True,
            start_time=datetime.fromisoformat(now),
        )
    else:
        inspector.register_process(99921, "agy", is_active=False, exit_code=0)

    # Even accidental future refactors must not invoke a live worker.
    def fail_spawn(*args: object, **kwargs: object) -> None:
        raise AssertionError("Cold-start recovery must never launch a worker")

    monkeypatch.setattr("subprocess.Popen", fail_spawn)
    engine = StartupReconciliationEngine(
        db_source=db_path,
        supervisor_pid=12080,
        inspector=inspector,
        git_client=git_client,
    )
    result = engine.execute_startup_reconciliation()
    assert result.lease_acquired is True
    assert result.interrupted_runs_count == 1
    assert result.supervisor_state == expected_supervisor
    assert result.run_reports[0].final_status == expected_run
    assert result.run_reports[0].run_decision.requires_blind_restart is False

    # A distinct connection is mandatory: this tests persistence, not memory.
    with sqlite3.connect(db_path) as check_conn:
        check_conn.row_factory = sqlite3.Row
        row = check_conn.execute(
            "SELECT status FROM runs WHERE run_id = ?", ("run-r",)
        ).fetchone()
        assert row is not None
        assert row["status"] == expected_run

        if scenario == "dead_report_pass":
            agent = check_conn.execute(
                "SELECT status, result_verdict FROM agents WHERE agent_id = 'AG-TEST'"
            ).fetchone()
            assert tuple(agent) == ("COMPLETE", "PASS")
        if scenario == "dead_missing":
            # The lost process cannot be restarted automatically.
            assert "Blind restart prohibited" in check_conn.execute(
                "SELECT error_summary FROM runs WHERE run_id='run-r'"
            ).fetchone()[0]
        if scenario == "dirty_primary":
            assert "DIRTY_ROOT" in check_conn.execute(
                "SELECT error_summary FROM runs WHERE run_id='run-r'"
            ).fetchone()[0]

    if scenario == "dead_missing":
        # Repeated cold start does not redispatch terminal INTERRUPTED work.
        second = engine.execute_startup_reconciliation()
        assert second.interrupted_runs_count == 0
        assert second.supervisor_state == "IDLE"

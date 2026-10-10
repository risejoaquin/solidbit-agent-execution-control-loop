"""Unit tests for SACL V1 CLI monitor command."""

from __future__ import annotations

from pathlib import Path
import sqlite3
import pytest

from sacl.cli.main import main


@pytest.fixture
def monitor_db(tmp_path):
    db_file = tmp_path / "sacl_ops.db"
    conn = sqlite3.connect(str(db_file))
    conn.execute(
        """
        CREATE TABLE runs (
            run_id TEXT PRIMARY KEY, job_id TEXT, package_id TEXT, project TEXT,
            status TEXT, started_at TEXT, completed_at TEXT, created_at TEXT, updated_at TEXT
        );
        """
    )
    conn.execute(
        """
        CREATE TABLE agents (
            run_id TEXT, agent_id TEXT, status TEXT, pid INTEGER, exit_code INTEGER,
            started_at TEXT, finished_at TEXT, report_path TEXT, stdout_path TEXT,
            stderr_path TEXT, error_message TEXT, result_verdict TEXT, updated_at TEXT,
            PRIMARY KEY (run_id, agent_id)
        );
        """
    )
    conn.execute(
        "INSERT INTO runs VALUES ('r-mon-1', 'job-m1', 'PKG-MON', 'my-proj', 'RUNNING', '2026-10-10T12:00:00Z', NULL, 'now', 'now')"
    )
    conn.execute(
        "INSERT INTO agents VALUES ('r-mon-1', 'AG-M1', 'RUNNING', 8888, NULL, '2026-10-10T12:00:00Z', NULL, NULL, NULL, NULL, NULL, NULL, 'now')"
    )
    conn.commit()
    conn.close()
    return db_file


def test_cli_monitor_once(monitor_db, capsys):
    code = main(["monitor", "--db", str(monitor_db), "--once"])
    assert code == 0
    captured = capsys.readouterr()
    assert "SOLIDBIT AGENT EXECUTION CONTROL LOOP" in captured.out
    assert "r-mon-1" in captured.out
    assert "AG-M1" in captured.out

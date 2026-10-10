"""Unit tests for SACL V1 CLI status command."""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import pytest

from sacl.cli.main import main


@pytest.fixture
def test_db(tmp_path):
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
        "INSERT INTO runs VALUES ('run-1', 'job-1', 'pkg-1', 'proj-1', 'RUNNING', '2026-10-10T12:00:00Z', NULL, 'now', 'now')"
    )
    conn.execute(
        "INSERT INTO agents VALUES ('run-1', 'AG-STATUS-1', 'COMPLETE', 5555, 0, '2026-10-10T12:00:00Z', '2026-10-10T12:05:00Z', 'rep.md', 'out.log', 'err.log', NULL, 'PASS', '2026-10-10T12:05:00Z')"
    )
    conn.commit()
    conn.close()
    return db_file


def test_cli_status_table(test_db, capsys):
    code = main(["status", "--db", str(test_db)])
    assert code == 0
    captured = capsys.readouterr()
    assert "SACL AGENT EXECUTION STATUS" in captured.out
    assert "AG-STATUS-1" in captured.out
    assert "COMPLETE" in captured.out


def test_cli_status_json(test_db, capsys):
    code = main(["status", "--db", str(test_db), "--json"])
    assert code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert len(data) == 1
    assert data[0]["AGENT"] == "AG-STATUS-1"
    assert data[0]["STATUS"] == "COMPLETE"
    assert data[0]["PID"] == 5555


def test_cli_status_filtered_agent(test_db, capsys):
    code = main(["status", "--db", str(test_db), "--agent", "NON-EXISTENT"])
    assert code == 0
    captured = capsys.readouterr()
    assert "No active or recorded agent state found" in captured.out

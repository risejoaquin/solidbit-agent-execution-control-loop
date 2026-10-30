"""Unit tests for SACL V1 CLI stop command."""

from __future__ import annotations

import shutil
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest

from sacl.cli.main import build_parser
from sacl.cli.stop import execute_stop
from sacl.worker.process import IProcessInspector


class MockInspector(IProcessInspector):
    def __init__(self, running=True, name="agy.exe"):
        self.running = running
        self.name = name

    def is_process_running(self, pid: int) -> bool:
        return self.running

    def get_process_name(self, pid: int):
        return self.name

    def get_process_start_time(self, pid: int):
        return datetime.now(timezone.utc)

    def terminate_process(self, pid: int, force: bool = False) -> bool:
        return True


@pytest.fixture
def stop_db(tmp_path):
    db_file = tmp_path / "sacl_ops.db"
    conn = sqlite3.connect(str(db_file))
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
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    conn.execute(
        f"INSERT INTO agents VALUES ('run-stop', 'AG-KILL', 'RUNNING', 7777, NULL, '{now_iso}', NULL, NULL, NULL, NULL, NULL, NULL, 'now')"
    )
    conn.commit()
    conn.close()
    return db_file


def test_cli_stop_success(stop_db, capsys):
    parser = build_parser()
    args = parser.parse_args(["stop", "--agent", "AG-KILL", "--db", str(stop_db)])
    ins = MockInspector(running=True, name="agy.exe")
    code = execute_stop(args, inspector=ins)
    assert code == 0
    captured = capsys.readouterr()
    assert "successfully terminated" in captured.out


def test_cli_stop_safety_refusal_on_name_mismatch(stop_db, capsys):
    parser = build_parser()
    args = parser.parse_args(["stop", "--agent", "AG-KILL", "--db", str(stop_db)])
    ins = MockInspector(running=True, name="explorer.exe")
    code = execute_stop(args, inspector=ins)
    assert code == 1
    captured = capsys.readouterr()
    assert "SAFETY_REFUSAL" in captured.out
    assert "process spared to protect host" in captured.out


def test_sacl_stop_script_pid_parameter_binding():
    powershell = shutil.which("powershell.exe") or shutil.which("powershell")
    if not powershell:
        pytest.skip("PowerShell is not installed or available in PATH")
    repo_root = Path(__file__).resolve().parents[3]
    script_path = repo_root / "scripts" / "sacl-stop.ps1"
    res = subprocess.run(
        [
            powershell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script_path),
            "-Pid",
            "99999999",
        ],
        capture_output=True,
        text=True,
    )
    # The script should not fail with PowerShell variable collision
    assert "VariableNotWritable" not in res.stderr
    assert "Cannot overwrite variable Pid" not in res.stderr
    assert "No se puede sobrescribir la variable Pid" not in res.stderr
    assert "SACL SAFE STOP CONTROLLER" in res.stdout

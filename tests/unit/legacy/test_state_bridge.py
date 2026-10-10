"""Unit tests for SACL V1 Legacy State Bridge."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import pytest

from sacl.legacy.state_bridge import LegacyStateBridge
from sacl.worker.process import IProcessInspector


class MockInspector(IProcessInspector):
    def is_process_running(self, pid: int) -> bool:
        return pid == 9999

    def get_process_name(self, pid: int):
        return "agy.exe"

    def get_process_start_time(self, pid: int):
        return datetime.now(timezone.utc)

    def terminate_process(self, pid: int, force: bool = False) -> bool:
        return True


@pytest.fixture
def bridge():
    return LegacyStateBridge(process_inspector=MockInspector())


def test_write_and_read_agent_state(bridge, tmp_path):
    state_file = tmp_path / "state" / "AG-1.json"
    written = bridge.write_agent_state(
        state_file=state_file,
        agent_name="AG-1",
        status="RUNNING",
        pid=1234,
        exit_code=None,
    )
    assert state_file.exists()
    assert written["agent"] == "AG-1"
    assert written["status"] == "RUNNING"
    assert written["pid"] == 1234

    read_back = bridge.read_agent_state(state_file)
    assert read_back == written


def test_write_run_meta_and_latest_run(bridge, tmp_path):
    meta = bridge.write_run_meta(
        run_dir=tmp_path,
        run_id="w0-test-1",
        package_id="PKG-1",
        source_orchestrator="C:/src",
        max_parallel=3,
    )
    assert meta.exists()
    with open(meta, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["runId"] == "w0-test-1"
    assert data["maxParallel"] == 3

    bridge.write_latest_run_marker(tmp_path, "w0-test-1")
    assert (tmp_path / "LATEST_RUN.txt").read_text(encoding="utf-8").strip() == "w0-test-1"
    assert (tmp_path / "LAST_RUN.txt").read_text(encoding="utf-8").strip() == "w0-test-1"


def test_reconcile_legacy_agent_running(bridge, tmp_path):
    state_file = tmp_path / "state" / "AG-1.json"
    bridge.write_agent_state(
        state_file=state_file,
        agent_name="AG-1",
        status="RUNNING",
        pid=9999,  # MockInspector returns True for 9999
        started_at=datetime.now(timezone.utc).isoformat(),
    )
    recon = bridge.reconcile_legacy_agent(
        agent_id="AG-1",
        run_dir=tmp_path,
        state_dir=tmp_path / "state",
    )
    assert recon["Status"] == "RUNNING"
    assert recon["IsRunning"] is True


def test_reconcile_legacy_agent_complete_with_report(bridge, tmp_path):
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(parents=True)
    report_file = reports_dir / "AG-1.REPORT.md"
    report_file.write_text("AGENT_1_RESULT = PASS\n", encoding="utf-8")

    state_file = tmp_path / "state" / "AG-1.json"
    bridge.write_agent_state(
        state_file=state_file,
        agent_name="AG-1",
        status="RUNNING",
        pid=1111,  # dead process
        exit_code=0,
    )
    recon = bridge.reconcile_legacy_agent(
        agent_id="AG-1",
        run_dir=tmp_path,
        state_dir=tmp_path / "state",
        reports_dir=reports_dir,
    )
    assert recon["Status"] == "COMPLETE"
    assert recon["Verdict"] == "PASS"
    assert recon["ReportExists"] is True


def test_export_and_import_sacl_run(bridge, tmp_path):
    # Setup in-memory SQLite DB
    conn = sqlite3.connect(":memory:")
    conn.execute(
        """
        CREATE TABLE runs (
            run_id TEXT PRIMARY KEY,
            job_id TEXT,
            package_id TEXT,
            project TEXT,
            status TEXT,
            started_at TEXT,
            completed_at TEXT,
            created_at TEXT,
            updated_at TEXT
        );
        """
    )
    conn.execute(
        """
        CREATE TABLE agents (
            run_id TEXT,
            agent_id TEXT,
            status TEXT,
            pid INTEGER,
            exit_code INTEGER,
            started_at TEXT,
            finished_at TEXT,
            report_path TEXT,
            stdout_path TEXT,
            stderr_path TEXT,
            error_message TEXT,
            result_verdict TEXT,
            updated_at TEXT,
            PRIMARY KEY (run_id, agent_id)
        );
        """
    )
    conn.execute(
        "INSERT INTO runs VALUES ('r1', 'j1', 'pkg1', 'proj', 'RUNNING', '2026-10-10T00:00:00Z', NULL, 'now', 'now')"
    )
    conn.execute(
        "INSERT INTO agents VALUES ('r1', 'ag1', 'COMPLETE', 123, 0, '2026-10-10T00:00:00Z', '2026-10-10T00:05:00Z', 'rep.md', 'out.log', 'err.log', NULL, 'PASS', 'now')"
    )
    conn.commit()

    # Export to legacy
    run_dir = tmp_path / "exported_run"
    bridge.export_sacl_run_to_legacy(conn, "r1", run_dir)
    assert (run_dir / "run-meta.json").exists()
    assert (run_dir / "state" / "ag1.json").exists()

    # Import back to new DB
    conn2 = sqlite3.connect(":memory:")
    conn2.execute(
        """
        CREATE TABLE runs (
            run_id TEXT PRIMARY KEY, job_id TEXT, package_id TEXT, project TEXT,
            status TEXT, started_at TEXT, created_at TEXT, updated_at TEXT
        );
        """
    )
    conn2.execute(
        """
        CREATE TABLE agents (
            run_id TEXT, agent_id TEXT, status TEXT, pid INTEGER, exit_code INTEGER,
            started_at TEXT, finished_at TEXT, report_path TEXT, stdout_path TEXT,
            stderr_path TEXT, error_message TEXT, updated_at TEXT,
            PRIMARY KEY (run_id, agent_id)
        );
        """
    )
    imported_run_id = bridge.import_legacy_run_to_sacl(run_dir, conn2)
    assert imported_run_id == "r1"

    cursor = conn2.cursor()
    cursor.execute("SELECT agent_id, status FROM agents WHERE run_id = 'r1'")
    row = cursor.fetchone()
    assert row == ("ag1", "COMPLETE")

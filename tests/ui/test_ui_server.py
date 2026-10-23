"""Integration tests for SACL V1 Decision Shell Web Server."""

from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import urllib.request
import pytest

from sacl.approval.manager import BoundedApprovalManager
from sacl.state.connection import create_connection
from sacl.state.migrations import MigrationRunner
from sacl.ui.server import DecisionShellServer


@pytest.fixture
def running_server(tmp_path: Path, migration_sql_path: Path):
    db_file = tmp_path / "sacl_ops.db"
    conn = create_connection(db_file)
    runner = MigrationRunner(migration_sql_path.parent)
    runner.apply_all(conn)

    # Seed job row to satisfy foreign key
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    conn.execute(
        """
        INSERT INTO jobs (job_id, status, priority, created_at, updated_at)
        VALUES ('job-server', 'RUNNING', 0, ?, ?);
        """,
        (now_iso, now_iso),
    )
    conn.commit()
    conn.close()

    server = DecisionShellServer(
        host="127.0.0.1",
        port=0,  # OS assigned ephemeral port
        db_path=db_file,
    )
    host, port = server.start(blocking=False)
    yield host, port, db_file
    server.stop()


def test_ui_server_root_html(running_server):
    host, port, _ = running_server
    url = f"http://{host}:{port}/"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        assert "text/html" in resp.headers.get("Content-Type", "")
        body = resp.read().decode("utf-8")
        assert "SolidBit Orchestrator" in body
        assert "Human Decision Center" in body


def test_ui_server_api_snapshot(running_server):
    host, port, _ = running_server
    url = f"http://{host}:{port}/api/snapshot?mode=audit"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        assert "application/json" in resp.headers.get("Content-Type", "")
        data = json.loads(resp.read().decode("utf-8"))
        assert "readiness_score" in data
        assert "safety" in data
        assert data["mode"] == "audit"


def test_ui_server_api_connections(running_server):
    host, port, _ = running_server
    url = f"http://{host}:{port}/api/connections"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert "connections" in data
        assert data["count"] > 0


def test_ui_server_gate_decide_endpoint(running_server):
    host, port, db_file = running_server

    # Issue an approval in DB
    conn = create_connection(db_file)
    mgr = BoundedApprovalManager(db_conn=conn)
    req_id = mgr.create_approval_request(
        job_id="job-server",
        action="GIT_COMMIT_PRIMARY",
        scope=["docs/TEST.md"],
        reason="Server API test",
    )
    conn.close()

    # Make decision via POST /api/gates/decide
    url = f"http://{host}:{port}/api/gates/decide"
    payload = json.dumps({
        "request_id": req_id,
        "decision": "APPROVED",
        "justification": "Approved via automated test",
    }).encode("utf-8")
    http_req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(http_req) as resp:
        assert resp.status == 200
        res = json.loads(resp.read().decode("utf-8"))
        assert res["success"] is True
        assert res["status"] == "APPROVED"

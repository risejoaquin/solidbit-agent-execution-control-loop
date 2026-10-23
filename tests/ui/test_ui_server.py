"""Integration tests for SACL V1 Decision Shell Web Server with SSE and Remote Gates."""

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
    yield host, port, db_file, server
    server.stop()


def test_ui_server_root_html(running_server):
    host, port, *_ = running_server
    url = f"http://{host}:{port}/"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        assert "text/html" in resp.headers.get("Content-Type", "")
        body = resp.read().decode("utf-8")
        assert "SolidBit SACL" in body
        assert "SSE LIVE PUSH" in body


def test_ui_server_api_snapshot(running_server):
    host, port, *_ = running_server
    url = f"http://{host}:{port}/api/snapshot?mode=audit"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        assert "application/json" in resp.headers.get("Content-Type", "")
        data = json.loads(resp.read().decode("utf-8"))
        assert "readiness_score" in data
        assert "safety" in data
        assert data["mode"] == "audit"


def test_ui_server_gate_impact_endpoint(running_server):
    host, port, *_ = running_server
    url = f"http://{host}:{port}/api/gates/impact?request_id=REQ-101"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert "human_summary" in data
        assert "contracts_status" in data
        assert "diff_preview" in data


def test_ui_server_campaign_launch_endpoint(running_server):
    host, port, *_ = running_server
    url = f"http://{host}:{port}/api/campaigns/launch"
    payload = json.dumps({"campaign_id": "TEST_CAMPAIGN"}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["success"] is True
        assert data["status"] == "RUNNING"


def test_ui_server_connection_auth_endpoint(running_server):
    host, port, *_ = running_server
    url = f"http://{host}:{port}/api/connections/auth"
    payload = json.dumps({"tool_id": "resend", "credentials": {"token": "re_sample"}}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["success"] is True


def test_ui_server_mobile_quick_decide(running_server, monkeypatch):
    host, port, db_file, server = running_server

    # Issue approval
    conn = create_connection(db_file)
    mgr = BoundedApprovalManager(db_conn=conn)
    req_id = mgr.create_approval_request(
        job_id="job-server",
        action="GIT_COMMIT_PRIMARY",
        scope=["docs/TEST.md"],
        reason="Server quick decide test",
    )
    conn.close()

    # Hit quick-decide URL as a mobile browser (includes HMAC signature)
    gate_details = server.service.gates.get_gate_impact_details(req_id)
    url = f"{gate_details['mobile_approval_url']}&decision=APPROVED"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        body = resp.read().decode("utf-8")
        assert "Acción Autorizada con Éxito" in body

"""Integration tests for SACL V1 Decision Shell Web Server with SSE and Remote Gates."""

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

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
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["success"] is True
        assert data["status"] == "RUNNING"


def test_ui_server_connection_auth_endpoint(running_server):
    host, port, *_ = running_server
    url = f"http://{host}:{port}/api/connections/auth"
    payload = json.dumps({"tool_id": "resend", "credentials": {"token": "re_sample"}}).encode(
        "utf-8"
    )
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )
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


def test_ui_server_chat_api(running_server):
    host, port, *_ = running_server

    # 1. GET /api/chat/history
    url = f"http://{host}:{port}/api/chat/history"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert "history" in data
        assert len(data["history"]) >= 1

    # 2. POST /api/chat/message
    post_url = f"http://{host}:{port}/api/chat/message"
    payload = json.dumps({"prompt": "revisar compuertas pendientes"}).encode("utf-8")
    post_req = urllib.request.Request(
        post_url, data=payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(post_req) as resp:
        assert resp.status == 200
        res = json.loads(resp.read().decode("utf-8"))
        assert res["success"] is True
        assert "compuerta" in res["assistant_message"]["content"].lower()


def test_ui_server_orchestrator_api(running_server):
    host, port, *_ = running_server

    # 1. GET /api/orchestrator/context
    url = f"http://{host}:{port}/api/orchestrator/context"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert "active_project" in data
        assert "jira_backlog" in data
        assert len(data["jira_backlog"]) >= 5

    # 2. POST /api/orchestrator/auto-plan
    post_url = f"http://{host}:{port}/api/orchestrator/auto-plan"
    payload = json.dumps({"jira_key": "SOLID-106", "mode": "waves"}).encode("utf-8")
    post_req = urllib.request.Request(
        post_url, data=payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(post_req) as resp:
        assert resp.status == 200
        plan = json.loads(resp.read().decode("utf-8"))
        assert plan["jira_ticket"]["key"] == "SOLID-106"
        assert len(plan["roles"]) >= 4
        assert len(plan["waves"]) >= 3

    # 3. POST /api/orchestrator/execute-sprint
    exec_url = f"http://{host}:{port}/api/orchestrator/execute-sprint"
    exec_payload = json.dumps({"sprint_plan": plan}).encode("utf-8")
    exec_req = urllib.request.Request(
        exec_url, data=exec_payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(exec_req) as resp:
        assert resp.status == 200
        exec_res = json.loads(resp.read().decode("utf-8"))
        assert exec_res.get("success") is True or exec_res.get("status") == "COMPLETED"

    # 4. POST /api/orchestrator/apply-changes
    apply_url = f"http://{host}:{port}/api/orchestrator/apply-changes"
    apply_payload = json.dumps(
        {
            "approval_id": "REQ-SERVER-TEST",
            "operator": "OPERADOR_SACL",
            "justification": "Test deployment gate approval",
        }
    ).encode("utf-8")
    apply_req = urllib.request.Request(
        apply_url, data=apply_payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(apply_req) as resp:
        assert resp.status == 200
        apply_res = json.loads(resp.read().decode("utf-8"))
        assert apply_res["success"] is True
        assert apply_res["jira_ticket"] == "SOLID-106"
        assert "hmac-sha256:" in apply_res["hmac_signature"]

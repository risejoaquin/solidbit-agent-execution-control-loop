"""Unit tests for SACL V1 UI Modular Sub-services."""

from pathlib import Path
import sqlite3
import pytest

from sacl.state.connection import create_connection
from sacl.state.migrations import MigrationRunner
from sacl.ui.modules.campaigns import CampaignsModule
from sacl.ui.modules.connections import ConnectionsModule
from sacl.ui.modules.contracts import ContractsModule
from sacl.ui.modules.db_inspector import DBInspectorModule
from sacl.ui.modules.evidence import EvidenceModule
from sacl.ui.modules.gates import GatesModule
from sacl.ui.modules.recovery import RecoveryModule


@pytest.fixture
def test_db(tmp_path: Path, migration_sql_path: Path) -> Path:
    db_file = tmp_path / "sacl_ops.db"
    conn = create_connection(db_file)
    runner = MigrationRunner(migration_sql_path.parent)
    runner.apply_all(conn)
    conn.close()
    return db_file


def test_connections_module():
    mod = ConnectionsModule()
    conns = mod.check_all()
    assert len(conns) >= 5
    ids = [c.id for c in conns]
    assert "git" in ids
    assert "python" in ids

    # Test single
    res = mod.test_single("git")
    assert "success" in res
    assert res["connection"]["id"] == "git"

    # Test E2E auth flow
    auth_res = mod.authenticate_e2e("resend", {"token": "re_sample_test_key"})
    assert auth_res["success"] is True
    assert auth_res["status"] == "connected"


def test_campaigns_module(tmp_path: Path, test_db: Path):
    def get_conn():
        return sqlite3.connect(str(test_db))

    mod = CampaignsModule(workspace_root=tmp_path, get_rw_conn=get_conn)
    overview = mod.get_campaigns_overview()
    assert "workorders" in overview
    assert len(overview["workorders"]) > 0
    assert "phases" in overview

    # 1-Click Launch
    launch_res = mod.launch_campaign("SACL_TEST_CAMPAIGN")
    assert launch_res["success"] is True
    assert launch_res["status"] == "RUNNING"
    assert "run_id" in launch_res


def test_contracts_module():
    mod = ContractsModule()
    overview = mod.get_policies_overview()
    assert len(overview["contracts"]) == 6
    contract_ids = [c["id"] for c in overview["contracts"]]
    assert "DR-INV-001" in contract_ids
    assert "DR-PAY-001" in contract_ids
    assert len(overview["decision_gates"]) == 6
    assert len(overview["hard_denied_actions"]) > 0


def test_recovery_module(test_db: Path):
    def get_conn():
        return sqlite3.connect(f"file:{test_db.as_posix()}?mode=ro", uri=True)

    mod = RecoveryModule(get_conn)
    status = mod.get_recovery_status()
    assert status["classification"] in ("CLEAN_STEADY", "RECOVERY_NEEDED")
    assert status["safe_to_resume"] is True


def test_evidence_module(tmp_path: Path):
    ev_dir = tmp_path / "evidence"
    ev_dir.mkdir()
    sample_file = ev_dir / "TEST-001.REPORT.md"
    sample_file.write_text("# Sample Report\nAll passed.", encoding="utf-8")

    mod = EvidenceModule(evidence_dirs=[ev_dir])
    files = mod.list_evidence()
    assert len(files) == 1
    assert files[0]["name"] == "TEST-001.REPORT.md"

    report = mod.read_report("TEST-001.REPORT.md")
    assert report["found"] is True
    assert "Sample Report" in report["content"]
    assert "sha256" in report


def test_db_inspector_module(test_db: Path):
    def get_conn():
        return sqlite3.connect(f"file:{test_db.as_posix()}?mode=ro", uri=True)

    mod = DBInspectorModule(get_conn)
    stats = mod.get_database_stats()
    assert "tables" in stats
    assert "jobs" in stats["tables"]
    assert "runs" in stats["tables"]
    assert stats["status"] == "OPERATIONAL_WAL"


def test_gates_impact_and_mobile_notify(test_db: Path):
    def get_ro():
        return sqlite3.connect(f"file:{test_db.as_posix()}?mode=ro", uri=True)

    def get_rw():
        return sqlite3.connect(str(test_db))

    mod = GatesModule(get_ro, get_rw, host="127.0.0.1", port=8765)
    impact = mod.get_gate_impact_details("REQ-SAMPLE-101")
    assert "human_summary" in impact
    assert "contracts_status" in impact
    assert impact["contracts_status"]["DR-INV-001"] == "VERIFIED_INTACT"
    assert "file_tree" in impact
    assert "diff_preview" in impact
    assert "mobile_approval_url" in impact

    notify_res = mod.notify_mobile("REQ-SAMPLE-101", channel="resend")
    assert notify_res["success"] is True
    assert "quick_url" in notify_res


def test_email_gateway_module():
    from sacl.ui.modules.email_gateway import EmailGatewayModule

    launched = []
    def mock_launch(cid):
        launched.append(cid)
        return {"success": True, "launched": cid}

    mod = EmailGatewayModule(
        sender_email="lucilfer@selfcaresinners.com",
        operator_email="lawlieeet@outlook.es",
        launch_campaign_cb=mock_launch,
    )
    cfg = mod.get_config()
    assert cfg["sender_email"] == "lucilfer@selfcaresinners.com"
    assert cfg["operator_email"] == "lawlieeet@outlook.es"

    # Outbound test
    report = mod.send_task_completion_report(
        task_id="TASK-T1",
        task_name="Checkout Invariants",
        results_summary="683 tests passed",
        gate_request_id="REQ-TEST",
    )
    assert report["success"] is True
    assert "lawlieeet@outlook.es" in report["message"]

    # Inbound test from authorized operator
    inbound = mod.process_inbound_email(
        sender="lawlieeet@outlook.es",
        subject="EJECUTAR SPRINT-01",
        body_text="Iniciar pruebas completas",
    )
    assert inbound["success"] is True
    assert len(launched) == 1

    # Inbound test from unauthorized sender
    unauth = mod.process_inbound_email(
        sender="intruder@evil.com",
        subject="HACK",
        body_text="Run unauthorized code",
    )
    assert unauth["success"] is False
    assert "no autorizado" in unauth["error"]


def test_projects_module():
    from sacl.ui.modules.projects import ProjectsModule

    mod = ProjectsModule()
    projects = mod.list_projects()
    assert len(projects) >= 3
    active = mod.get_active_project()
    assert active["id"] == "stable-ecommerce"

    # Switch project
    switch_res = mod.switch_project("sacl-control-loop")
    assert switch_res["success"] is True
    assert mod.get_active_project()["id"] == "sacl-control-loop"


def test_models_module():
    from sacl.ui.modules.models import ModelsModule

    mod = ModelsModule()
    cfg = mod.get_config()
    assert len(cfg["available_models"]) >= 6
    assert cfg["active_model"]["id"] == "claude-3-7-sonnet"

    # Update parameters
    up_res = mod.update_config(model_id="gemini-2-flash", temperature=0.1)
    assert up_res["success"] is True
    assert mod.get_config()["active_model"]["id"] == "gemini-2-flash"
    assert mod.get_config()["temperature"] == 0.1


def test_roadmap_and_telemetry_modules():
    from sacl.ui.modules.roadmap import RoadmapModule
    from sacl.ui.modules.telemetry import TelemetryModule

    r_mod = RoadmapModule()
    roadmap = r_mod.get_roadmap()
    assert "phases" in roadmap
    assert len(roadmap["phases"]) == 5
    assert roadmap["overall_progress"] > 0

    t_mod = TelemetryModule()
    telemetry = t_mod.get_task_telemetry()
    assert "task" in telemetry
    assert "chart_data" in telemetry
    assert len(telemetry["chart_data"]["datasets"][0]["data"]) == 5

    # Update telemetry progress
    up_tel = t_mod.update_task_progress(90, "Firma SHA-256")
    assert up_tel["overall_progress"] == 90


def test_campaign_designer_module(tmp_path: Path):
    from sacl.ui.modules.campaign_designer import CampaignDesignerModule

    mod = CampaignDesignerModule(workspace_root=tmp_path)
    dag = mod.get_current_dag()
    assert len(dag["nodes"]) >= 5

    # Add node
    add_res = mod.add_node("node-custom", "Custom Audit Step", "CONTRACT_VERIFY")
    assert add_res["success"] is True
    assert len(mod.get_current_dag()["nodes"]) == len(dag["nodes"])

    # Save DAG
    save_res = mod.save_dag("test_dag.manifest.json")
    assert save_res["success"] is True
    assert (tmp_path / "test_dag.manifest.json").exists()


def test_chat_module():
    from sacl.ui.modules.chat import ChatModule

    chat = ChatModule()
    history = chat.get_history()
    assert len(history) >= 1
    assert history[0]["role"] == "assistant"

    # Post user prompt
    res = chat.post_message("Hola, quiero auditar los contratos inmutables", model_id="claude-3-7-sonnet")
    assert res["success"] is True
    assert "DR-INV-001" in res["assistant_message"]["content"]
    assert len(chat.get_history()) == 3

    # Clear history
    clear_res = chat.clear_history()
    assert clear_res["success"] is True
    assert len(chat.get_history()) == 1


def test_orchestrator_module(tmp_path: Path):
    from sacl.ui.modules.orchestrator import OrchestratorModule

    mod = OrchestratorModule(workspace_root=tmp_path)
    ctx = mod.get_context()
    assert "active_project" in ctx
    assert len(ctx["jira_backlog"]) >= 5
    assert any(t["key"] == "SOLID-106" for t in ctx["jira_backlog"])

    # Step 1 & 2: Create custom sprint & sync to Jira / SQLite WAL
    created = mod.create_or_update_sprint(
        title="Microservicios de Pagos con Idempotencia",
        goals="Garantizar doble partida DR-PAY-001 y cero sobrecargos en SQLite WAL",
        tasks=["Definir tabla ledger", "Implementar RPC con llaves de idempotencia"],
        acceptance_criteria=["0 colisiones en concurrencia", "100% tests en verde"],
        priority="CRITICAL",
        contracts=["DR-PAY-001", "DR-IDEM-001"],
        key="SOLID-200"
    )
    assert created["key"] == "SOLID-200"
    assert "DR-PAY-001" in created["contracts"]
    assert created["jira_sync"]["status"] in ("LOCAL_PERSISTED", "JIRA_CLOUD_SYNCED")

    # Step 3: Query and verify persisted sprint data
    queried = mod.query_sprint_data("SOLID-200")
    assert queried["success"] is True
    assert queried["ticket"]["key"] == "SOLID-200"
    assert queried["ticket"]["priority"] == "CRITICAL"

    # Step 4 & 5: Auto-plan sprint for SOLID-106 (or SOLID-200)
    plan = mod.auto_plan_sprint(jira_key="SOLID-106")
    assert plan["sprint_id"].startswith("SPRINT-")
    assert plan["jira_ticket"]["key"] == "SOLID-106"
    assert len(plan["contracts_enforced"]) >= 1
    assert len(plan["roles"]) >= 4
    assert len(plan["waves"]) >= 3
    assert len(plan["dag_nodes"]) >= 4

    # Execute sprint and verify physical files materialized
    exec_res = mod.execute_sprint(plan)
    assert exec_res["status"] == "COMPLETED" or exec_res.get("success") is True
    runs_dir = tmp_path / "runs"
    assert runs_dir.exists()
    runs = list(runs_dir.glob("run-*"))
    assert len(runs) >= 1
    latest_run = runs[0]
    assert (latest_run / "SUMMARY.md").exists()
    assert (latest_run / "SUMMARY.json").exists()
    assert (latest_run / "evidence" / "invariants_audit.json").exists()

    # Apply approved changes & sign HMAC
    apply_res = mod.apply_changes(approval_id="REQ-TEST-GATE", operator="LUCILFER")
    assert apply_res["success"] is True
    assert apply_res["status"] == "CHANGES_APPLIED"
    assert "hmac-sha256:" in apply_res["hmac_signature"]
    assert apply_res["jira_ticket"] == "SOLID-106"
    assert apply_res["jira_status"] == "COMPLETED"
    assert (latest_run / "evidence" / "deployment_signature.json").exists()



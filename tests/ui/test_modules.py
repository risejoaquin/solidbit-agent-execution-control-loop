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

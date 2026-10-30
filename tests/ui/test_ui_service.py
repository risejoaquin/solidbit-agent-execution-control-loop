"""Unit tests for SACL V1 UI Service."""

from datetime import datetime, timezone
from pathlib import Path

import pytest

from sacl.approval.manager import BoundedApprovalManager
from sacl.contracts.invariants import ApprovalStatus
from sacl.state.connection import create_connection
from sacl.state.migrations import MigrationRunner
from sacl.ui.service import UIService


@pytest.fixture
def test_db(tmp_path: Path, migration_sql_path: Path) -> Path:
    db_file = tmp_path / "sacl_ops.db"
    conn = create_connection(db_file)
    runner = MigrationRunner(migration_sql_path.parent)
    runner.apply_all(conn)

    # Seed jobs row to satisfy FK
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    conn.execute(
        """
        INSERT INTO jobs (job_id, status, priority, created_at, updated_at)
        VALUES ('job-gate-check', 'RUNNING', 0, ?, ?);
        """,
        (now_iso, now_iso),
    )
    conn.commit()
    conn.close()
    return db_file


def test_ui_service_technology_connections(test_db: Path):
    service = UIService(db_path=test_db)
    conns = service.check_technology_connections()
    assert len(conns) > 0
    names = [c.name for c in conns]
    assert any("Git VCS" in n for n in names)
    assert any("Python" in n for n in names)


def test_ui_service_pending_gates_and_decision(test_db: Path):
    # Setup a pending approval in SQLite using manager API
    conn = create_connection(test_db)
    mgr = BoundedApprovalManager(db_conn=conn)
    req_id = mgr.create_approval_request(
        job_id="job-gate-check",
        action="GIT_COMMIT_PRIMARY",
        scope=["docs/DECISION_GATES.md"],
        reason="Human validation of decision gates",
    )
    conn.close()

    # Query pending gates via UI service
    service = UIService(db_path=test_db)
    pending = service.get_pending_gates()
    assert len(pending) == 1
    assert pending[0].request_id == req_id
    assert pending[0].action == "GIT_COMMIT_PRIMARY"

    # Make decision via UI service
    outcome = service.submit_gate_decision(
        request_id=req_id,
        decision_str="APPROVED",
        approver_id="architect_julian",
        justification="Verified against SOLIDBIT architecture rules",
    )
    assert outcome["success"] is True
    assert outcome["status"] == ApprovalStatus.APPROVED.value

    # Verify no pending gates remain
    pending_after = service.get_pending_gates()
    assert len(pending_after) == 0


def test_ui_service_dashboard_snapshot(test_db: Path):
    service = UIService(db_path=test_db)
    snap = service.get_dashboard_snapshot(mode="technical")
    assert snap.mode == "technical"
    assert snap.readiness_score >= 0
    assert snap.safety.production_allowed is False

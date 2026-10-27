"""SACL V1 UI Backend Service.

Coordinates read models from SQLite, external CLI readiness checks,
and human approval gate decisions across modular sub-services.
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from sacl.approval.manager import BoundedApprovalManager
from sacl.engine.workflow_engine import WorkflowEngine
from sacl.observability.monitor import MonitorReadModel
from sacl.state.connection import create_connection
from sacl.state.migrations import MigrationRunner
from sacl.ui.models import (
    ConnectionState,
    FullDashboardView,
    HumanGateCard,
    RecoverySummaryView,
    SafetyBoundaryStatus,
    TechnologyConnection,
)
from sacl.ui.modules.actions import ActionExecutionModule
from sacl.ui.modules.campaign_designer import CampaignDesignerModule
from sacl.ui.modules.campaigns import CampaignsModule
from sacl.ui.modules.chat import ChatModule
from sacl.ui.modules.connections import ConnectionsModule
from sacl.ui.modules.contracts import ContractsModule
from sacl.ui.modules.db_inspector import DBInspectorModule
from sacl.ui.modules.diff import GitDiffModule
from sacl.ui.modules.email_gateway import EmailGatewayModule
from sacl.ui.modules.evidence import EvidenceModule
from sacl.ui.modules.gates import GatesModule
from sacl.ui.modules.models import ModelsModule
from sacl.ui.modules.orchestrator import OrchestratorModule
from sacl.ui.modules.projects import ProjectsModule
from sacl.ui.modules.recovery import RecoveryModule
from sacl.ui.modules.roadmap import RoadmapModule
from sacl.ui.modules.slash_commands import SlashCommandRegistry
from sacl.ui.modules.subagents_manager import SubagentsManager
from sacl.ui.modules.telemetry import TelemetryModule
from sacl.ui.security import load_or_create_secret

logger = logging.getLogger("sacl.ui.service")


def utc_iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class UIService:
    """Unified facade coordinating all UI backend modules and read models."""

    def __init__(
        self,
        db_path: Optional[Union[Path, str]] = None,
        workspace_root: Optional[Union[Path, str]] = None,
        host: str = "127.0.0.1",
        port: int = 8765,
    ) -> None:
        self.host = host
        self.port = port
        if db_path is not None:
            self.db_path = Path(db_path)
        elif Path("sacl_ops.db").exists():
            self.db_path = Path("sacl_ops.db").resolve()
        elif Path("data/sacl_ops.db").exists():
            self.db_path = Path("data/sacl_ops.db").resolve()
        else:
            self.db_path = Path("sacl_ops.db")

        self.workspace_root = Path(workspace_root) if workspace_root else Path.cwd()
        self.secret = load_or_create_secret(self.workspace_root)
        self._ensure_db_initialized()

        # Initialize sub-modules
        self.connections = ConnectionsModule()
        self.gates = GatesModule(
            self._get_read_only_conn,
            self._get_read_write_conn,
            host=self.host,
            port=self.port,
            secret=self.secret,
            workspace_root=self.workspace_root,
        )
        self.campaigns = CampaignsModule(self.workspace_root, get_rw_conn=self._get_read_write_conn)
        self.recovery = RecoveryModule(self._get_read_only_conn)
        self.evidence = EvidenceModule()
        self.contracts = ContractsModule()
        self.db_inspector = DBInspectorModule(self._get_read_only_conn)
        self.projects = ProjectsModule()
        self.models = ModelsModule()
        self.roadmap = RoadmapModule()
        self.telemetry = TelemetryModule()
        self.campaign_designer = CampaignDesignerModule(self.workspace_root)
        self.orchestrator = OrchestratorModule(self, workspace_root=self.workspace_root)
        self.actions = ActionExecutionModule(self, workspace_root=self.workspace_root)
        self.workflow_engine = WorkflowEngine(self.workspace_root, db_path=self.db_path)
        self.diff = GitDiffModule(self.workspace_root)
        self.slash_registry = SlashCommandRegistry(self.workspace_root, self.workflow_engine)
        self.subagents = SubagentsManager(self.workspace_root)
        self.chat = ChatModule(self)
        self.email_gateway = EmailGatewayModule(
            sender_email="lucilfer@selfcaresinners.com",
            operator_email="lawlieeet@outlook.es",
            launch_campaign_cb=self.campaigns.launch_campaign,
            host=self.host,
            port=self.port,
            secret=self.secret,
            gate_url_builder=self.gates.build_quick_url,
        )

    def _ensure_db_initialized(self) -> None:
        """Ensures sacl_ops.db schema exists and bootstraps initial seed if empty."""
        need_seed = not self.db_path.exists()
        mig_dir = Path(__file__).resolve().parents[3] / "db" / "migrations"
        if not mig_dir.exists():
            mig_dir = Path("db/migrations")

        if mig_dir.exists():
            conn = create_connection(self.db_path)
            runner = MigrationRunner(mig_dir)
            runner.apply_all(conn)
            conn.commit()

            if need_seed:
                now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                conn.execute(
                    """
                    INSERT OR IGNORE INTO projects (project_id, name, root_path)
                    VALUES ('stable-ecommerce', 'Stable-Ecommerce', 'C:/Users/Lucilfer/Documents/Stable-Ecommerce');
                    """
                )
                conn.execute(
                    """
                    INSERT OR IGNORE INTO jobs (job_id, status, priority, created_at, updated_at)
                    VALUES ('JOB-GATE-001', 'WAITING_APPROVAL', 1, ?, ?);
                    """,
                    (now_iso, now_iso),
                )
                conn.commit()

                mgr = BoundedApprovalManager(db_conn=conn)
                mgr.create_approval_request(
                    job_id="JOB-GATE-001",
                    action="DEPLOY_STAGING_PREVIEW",
                    scope=["services/web-storefront", "railway.json"],
                    reason="Verificar despliegue efimero en Railway antes de merge a main.",
                    ttl_seconds=86400 * 7,
                )
            else:
                # If existing demo seed gate expired, refresh its TTL so it remains actionable
                now = datetime.now(timezone.utc)
                now_iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")
                future_iso = (now + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
                conn.execute(
                    """
                    UPDATE approvals
                    SET expires_at = ?
                    WHERE job_id = 'JOB-GATE-001' AND status = 'PENDING' AND expires_at < ?
                    """,
                    (future_iso, now_iso),
                )
                conn.commit()
            conn.close()

    def _get_read_only_conn(self) -> Optional[sqlite3.Connection]:
        if not self.db_path.exists():
            return None
        try:
            uri = f"file:{self.db_path.resolve().as_posix()}?mode=ro"
            conn = sqlite3.connect(uri, uri=True, timeout=5.0)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as exc:
            logger.debug(f"Unable to open read-only DB: {exc}")
            return None

    def _get_read_write_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    # Delegated methods for backward compatibility
    def check_technology_connections(self) -> List[TechnologyConnection]:
        return self.connections.check_all()

    def get_pending_gates(self) -> List[HumanGateCard]:
        return self.gates.get_pending_gates()

    def submit_gate_decision(
        self,
        request_id: str,
        decision_str: str,
        approver_id: str = "human_operator",
        justification: str = "Authorized via SACL Decision Shell",
        channel: str = "CLI",
    ) -> Dict[str, Any]:
        return self.gates.submit_decision(
            request_id=request_id,
            decision_str=decision_str,
            approver_id=approver_id,
            justification=justification,
            channel=channel,
        )

    def get_dashboard_snapshot(self, mode: str = "simple") -> FullDashboardView:
        """Consolidates the complete UI state for presentation."""
        read_model = MonitorReadModel(db_path=self.db_path)
        base_snap = read_model.get_dashboard_snapshot()

        conns = self.check_technology_connections()
        gates = self.get_pending_gates()

        connected_count = sum(1 for c in conns if c.status == ConnectionState.CONNECTED)
        readiness = int((connected_count / max(1, len(conns))) * 100)
        if gates:
            readiness = max(20, readiness - 15)

        agents_data = [a.to_dict() for a in base_snap.agents]
        leases_data = [ls.to_dict() for ls in base_snap.leases]

        recovery_info = self.recovery.get_recovery_status()
        recovery = RecoverySummaryView(
            interrupted_runs_count=len(recovery_info.get("interrupted_runs", [])),
            latest_run_id=base_snap.run_id if base_snap.run_id != "--" else None,
            classification=recovery_info.get("classification", "READY_SAFE"),
            safe_to_resume=True,
            recommended_action=recovery_info.get(
                "recommended_action", "Operational state verified"
            ),
        )

        active_proj = self.projects.get_active_project()
        active_proj_name = active_proj["name"] if active_proj else "Stable-Ecommerce"

        return FullDashboardView(
            readiness_score=readiness,
            active_project=active_proj_name,
            active_campaign=base_snap.package_id
            if base_snap.package_id != "--"
            else "Productization V1",
            mode=mode,
            safety=SafetyBoundaryStatus(),
            connections=conns,
            pending_gates=gates,
            agents=agents_data,
            leases=leases_data,
            recovery=recovery,
            alerts=base_snap.alerts,
            recent_events=base_snap.recent_events,
            timestamp=utc_iso_now(),
        )

"""SACL V1 Architectural Interface Conformance Integration Tests.

Validates that all 10 canonical interfaces defined in sacl.contracts.interfaces
have fully compliant concrete implementations across the integrated modules:
1. IApprovalManager -> BoundedApprovalManager, ApprovalManager
2. IDagScheduler -> EphemeralDagScheduler
3. IPackageValidator -> PackageValidator, WaveZipPackager
4. IPolicyEngine -> PolicyEngine
5. IReconciler -> ResultReconciler, WorkerReconciler
6. IRecoveryManager -> StartupReconciliationEngine
7. IStateStore -> SqliteStateStore
8. ISupervisor -> GraphPSupervisor
9. ITransportGateway -> MailGateway
10. IWorkspaceManager -> WorkspaceManager
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
import pytest

from sacl.approval.manager import BoundedApprovalManager
from sacl.contracts.interfaces import (
    IApprovalManager,
    IDagScheduler,
    IPackageValidator,
    IPolicyEngine,
    IReconciler,
    IRecoveryManager,
    IStateStore,
    ISupervisor,
    ITransportGateway,
    IWorkspaceManager,
)
from sacl.contracts.models import Approver
from sacl.dag.models import SchedulerConfig
from sacl.dag.scheduler import EphemeralDagScheduler
from sacl.legacy.packager import WaveZipPackager
from sacl.package.validator import PackageValidator
from sacl.policy.approval import ApprovalManager
from sacl.policy.lattice import PolicyEngine
from sacl.recovery.startup_reconciliation import StartupReconciliationEngine
from sacl.results.reconciler import ResultReconciler
from sacl.state.store import SqliteStateStore
from sacl.supervisor.graph_p import GraphPSupervisor, SupervisorConfig
from sacl.transport.gateway import MailGateway
from sacl.transport.gmail_adapter import MockGmailApiAdapter
from sacl.transport.pubsub import MockPubSubSubscriber
from sacl.worker.reconciliation_hook import WorkerReconciler
from sacl.worker.worktree import WorkspaceManager


class TestInterfaceConformance:
    """Verifies that all subsystem interfaces adhere to ABC contracts."""

    def test_approval_manager_conformance(self, sqlite_temp_db: sqlite3.Connection):
        """Verifies IApprovalManager implementations."""
        assert issubclass(BoundedApprovalManager, IApprovalManager)
        assert issubclass(ApprovalManager, IApprovalManager)

        sqlite_temp_db.execute(
            "INSERT INTO jobs (job_id, status, created_at, updated_at) VALUES ('job-iface-1', 'WAITING_APPROVAL', '2026-10-07T00:00:00Z', '2026-10-07T00:00:00Z')"
        )
        sqlite_temp_db.commit()

        mgr = BoundedApprovalManager(sqlite_temp_db)
        request_id = mgr.create_approval_request(
            job_id="job-iface-1",
            action="github_branch_push",
            scope=["feature/test"],
        )
        assert request_id is not None
        req = mgr.get_request(request_id)
        assert req is not None
        assert req.job_id == "job-iface-1"

        approver = Approver(identity="Joaquín", channel="CLI")
        token = mgr.record_decision(request_id, "APPROVED", approver)
        assert token is not None
        assert token.decision == "APPROVED"
        assert mgr.get_approval(request_id) is not None

    def test_dag_scheduler_conformance(self, sqlite_temp_db: sqlite3.Connection):
        """Verifies IDagScheduler implementations."""
        assert issubclass(EphemeralDagScheduler, IDagScheduler)
        scheduler = EphemeralDagScheduler(
            config=SchedulerConfig(
                run_id="run-iface-1",
                job_id="job-iface-1",
                target_repo_path="C:/repo",
                run_dir="C:/runs/run-iface-1",
                max_parallel=2,
            ),
            db_conn=sqlite_temp_db,
        )
        assert hasattr(scheduler, "initialize_graph")
        assert hasattr(scheduler, "execute_phases")
        assert hasattr(scheduler, "cancel_execution")

    def test_package_validator_conformance(self):
        """Verifies IPackageValidator implementations."""
        assert issubclass(PackageValidator, IPackageValidator)
        assert issubclass(WaveZipPackager, IPackageValidator)

        packager = WaveZipPackager()
        assert hasattr(packager, "validate_archive")
        assert hasattr(packager, "check_zip_slip")
        assert hasattr(packager, "verify_checksums")

    def test_policy_engine_conformance(self):
        """Verifies IPolicyEngine implementations."""
        assert issubclass(PolicyEngine, IPolicyEngine)
        engine = PolicyEngine()
        hard_policy = engine.get_hard_local_policy()
        assert hard_policy is not None
        assert hasattr(engine, "check_hard_deny")
        assert hasattr(engine, "evaluate_lattice")

    def test_reconciler_conformance(self, sqlite_temp_db: sqlite3.Connection):
        """Verifies IReconciler implementations."""
        assert issubclass(ResultReconciler, IReconciler)
        assert issubclass(WorkerReconciler, IReconciler)

        rec = ResultReconciler()
        assert hasattr(rec, "reconcile")
        w_rec = WorkerReconciler(db_conn=sqlite_temp_db)
        assert hasattr(w_rec, "reconcile")

    def test_recovery_manager_conformance(self, sqlite_temp_db: sqlite3.Connection):
        """Verifies IRecoveryManager implementations."""
        assert issubclass(StartupReconciliationEngine, IRecoveryManager)
        engine = StartupReconciliationEngine(sqlite_temp_db)
        assert hasattr(engine, "reconcile_startup")
        assert hasattr(engine, "check_pid_safety")

    def test_state_store_conformance(self):
        """Verifies IStateStore implementations."""
        assert issubclass(SqliteStateStore, IStateStore)
        store = SqliteStateStore(":memory:")
        assert hasattr(store, "create_job")
        assert hasattr(store, "update_job_status")
        assert hasattr(store, "get_job")
        assert hasattr(store, "create_run")
        assert hasattr(store, "update_run_status")
        assert hasattr(store, "record_agent")
        assert hasattr(store, "update_agent")
        assert hasattr(store, "record_event")
        assert hasattr(store, "acquire_lease")
        assert hasattr(store, "renew_lease")
        assert hasattr(store, "release_lease")

    def test_supervisor_conformance(self, sqlite_temp_db: sqlite3.Connection):
        """Verifies ISupervisor implementations."""
        assert issubclass(GraphPSupervisor, ISupervisor)
        sup = GraphPSupervisor(
            sqlite_temp_db,
            instance_id="sup-iface-test",
            config=SupervisorConfig(poll_interval_seconds=0.1),
        )
        assert hasattr(sup, "run_supervisor_tick")
        assert hasattr(sup, "is_idle")
        assert hasattr(sup, "dispatch_job")
        assert sup.is_idle() is True

    def test_transport_gateway_conformance(self, sqlite_temp_db: sqlite3.Connection, tmp_path: Path):
        """Verifies ITransportGateway implementations."""
        assert issubclass(MailGateway, ITransportGateway)
        gateway = MailGateway(
            gmail_adapter=MockGmailApiAdapter(),
            pubsub_subscriber=MockPubSubSubscriber(),
            db_conn=sqlite_temp_db,
            staging_root=tmp_path,
        )
        assert hasattr(gateway, "pull_wake_notifications")
        assert hasattr(gateway, "sync_history")
        assert hasattr(gateway, "fetch_message_envelope")
        assert hasattr(gateway, "dispatch_outbox_reply")

    def test_workspace_manager_conformance(self):
        """Verifies IWorkspaceManager implementations."""
        assert issubclass(WorkspaceManager, IWorkspaceManager)
        wm = WorkspaceManager()
        assert hasattr(wm, "check_clean_root")
        assert hasattr(wm, "provision_worktree")
        assert hasattr(wm, "teardown_worktree")
        assert hasattr(wm, "get_modified_files")

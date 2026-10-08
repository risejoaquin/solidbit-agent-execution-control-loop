"""SACL V1 Abstract Interfaces and Protocol Definitions.

Defines the shared contracts between subsystems (State Store, Policy Engine,
Package Ingestion, Workspace Isolation, Transport, Supervisors, Reconcilers).
"""

from __future__ import annotations

import abc
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from sacl.contracts.models import (
    ApprovalToken,
    Approver,
    AuditEvent,
    ErrorRecord,
    ExecutionGraph,
    HardLocalPolicy,
    HeartbeatRecord,
    LeaseRecord,
    MailEnvelope,
    Manifest,
    ProjectPolicy,
    ReconciledResult,
)


class IStateStore(abc.ABC):
    """Operational relational state store (SQLite WAL mode)."""

    @abc.abstractmethod
    def initialize_schema(self, migration_sql_path: Optional[Path] = None) -> None:
        """Applies canonical DDL migrations."""
        pass

    @abc.abstractmethod
    def create_job(
        self,
        job_id: str,
        package_id: Optional[str],
        project_id: Optional[str],
        status: str,
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Records initial logical job state."""
        pass

    @abc.abstractmethod
    def update_job_status(
        self,
        job_id: str,
        status: str,
        current_run_id: Optional[str] = None,
        error_summary: Optional[str] = None,
    ) -> None:
        """Updates job lifecycle state."""
        pass

    @abc.abstractmethod
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves logical job record."""
        pass

    @abc.abstractmethod
    def create_run(
        self,
        run_id: str,
        job_id: str,
        package_id: str,
        project: str,
        repository: str,
        mode: str,
        source_orchestrator: str,
        target_repo_path: str,
        run_dir: str,
        status: str,
    ) -> None:
        """Records physical run attempt."""
        pass

    @abc.abstractmethod
    def update_run_status(
        self,
        run_id: str,
        status: str,
        ready_for_integration: str = "NO",
        reconciled_verdict: Optional[str] = None,
        error_summary: Optional[str] = None,
    ) -> None:
        """Updates physical run attempt outcome."""
        pass

    @abc.abstractmethod
    def record_agent(
        self,
        agent_id: str,
        run_id: str,
        status: str,
        prompt_path: str,
        report_path: str,
        stdout_path: str,
        stderr_path: str,
        pid: Optional[int] = None,
        worktree_path: Optional[str] = None,
        branch: Optional[str] = None,
    ) -> None:
        """Records agent worker instance."""
        pass

    @abc.abstractmethod
    def update_agent(
        self,
        agent_id: str,
        run_id: str,
        status: str,
        result_verdict: str,
        exit_code: Optional[int] = None,
        commit_sha: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """Updates agent execution record."""
        pass

    @abc.abstractmethod
    def record_event(self, event: AuditEvent) -> int:
        """Appends structured audit event."""
        pass

    @abc.abstractmethod
    def acquire_lease(
        self,
        lease_name: str,
        holder_id: str,
        holder_pid: int,
        ttl_seconds: int = 30,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Attempts atomic mutual exclusion lease acquisition."""
        pass

    @abc.abstractmethod
    def renew_lease(self, lease_name: str, holder_id: str, ttl_seconds: int = 30) -> bool:
        """Renews active mutual exclusion lease."""
        pass

    @abc.abstractmethod
    def release_lease(self, lease_name: str, holder_id: str) -> bool:
        """Releases mutual exclusion lease."""
        pass

    @abc.abstractmethod
    def record_heartbeat(self, heartbeat: HeartbeatRecord) -> int:
        """Records process liveness heartbeat."""
        pass

    @abc.abstractmethod
    def record_file_modifications(
        self, run_id: str, agent_id: str, file_paths: List[str]
    ) -> None:
        """Records git files modified by an agent."""
        pass

    @abc.abstractmethod
    def detect_file_conflicts(self, run_id: str) -> List[Dict[str, Any]]:
        """Queries database for cross-agent overlapping file modifications."""
        pass


class IPolicyEngine(abc.ABC):
    """Evaluates effective-permission lattice and enforces hard local policy."""

    @abc.abstractmethod
    def check_hard_deny(self, action: str) -> None:
        """Verifies action is not hard denied.

        Raises:
            HardDenyViolation: If action is prohibited.
        """
        pass

    @abc.abstractmethod
    def evaluate_lattice(
        self,
        action: str,
        requested_permissions: List[str],
        project_policy: ProjectPolicy,
        approval_grant: Optional[ApprovalToken] = None,
    ) -> bool:
        """Calculates 4-layer intersection: Hard Policy ∩ Project Policy ∩ Package Requested ∩ Approval."""
        pass

    @abc.abstractmethod
    def get_hard_local_policy(self) -> HardLocalPolicy:
        """Returns the active hard local policy."""
        pass


class IPackageValidator(abc.ABC):
    """Validates execution package zip archives, manifests, and checksums."""

    @abc.abstractmethod
    def validate_archive(self, zip_path: Path) -> Manifest:
        """Validates package archive structure, manifest schema, and zip-slip defense."""
        pass

    @abc.abstractmethod
    def check_zip_slip(self, zip_path: Path) -> List[str]:
        """Detects path traversal or escaping relative paths in archive."""
        pass

    @abc.abstractmethod
    def verify_checksums(self, extracted_dir: Path, checksums_file: str = "checksums.sha256") -> bool:
        """Verifies cryptographic integrity of extracted package assets."""
        pass


class IWorkspaceManager(abc.ABC):
    """Coordinates Git working tree isolation and dirty-root checks."""

    @abc.abstractmethod
    def check_clean_root(self, repo_path: Path) -> Tuple[bool, List[str]]:
        """Enforces the Local Dirty-Root Rule."""
        pass

    @abc.abstractmethod
    def provision_worktree(
        self, repo_path: Path, branch_name: str, worktree_path: Path, base_ref: str = "HEAD"
    ) -> Path:
        """Provisions an isolated Git worktree for an agent."""
        pass

    @abc.abstractmethod
    def teardown_worktree(self, repo_path: Path, worktree_path: Path) -> None:
        """Cleans up and removes an isolated Git worktree."""
        pass

    @abc.abstractmethod
    def get_modified_files(self, worktree_path: Path, base_ref: str = "HEAD") -> List[str]:
        """Collects files modified in worktree relative to base reference."""
        pass


class ITransportGateway(abc.ABC):
    """Asynchronous mail transport gateway (Gmail API OAuth2 + Pub/Sub)."""

    @abc.abstractmethod
    def pull_wake_notifications(self, max_messages: int = 10) -> List[Dict[str, Any]]:
        """Pulls untrusted wake signals from Cloud Pub/Sub."""
        pass

    @abc.abstractmethod
    def sync_history(self, start_history_id: str) -> List[Dict[str, Any]]:
        """Authoritative fetch via Gmail History API using historyId cursor."""
        pass

    @abc.abstractmethod
    def fetch_message_envelope(self, message_id: str) -> MailEnvelope:
        """Retrieves and parses message envelope and package attachment."""
        pass

    @abc.abstractmethod
    def dispatch_outbox_reply(
        self, recipient: str, subject: str, body_markdown: str, attachment_path: Optional[Path] = None
    ) -> str:
        """Dispatches outbound execution result reply."""
        pass


class ISupervisor(abc.ABC):
    """Persistent Graph-P supervisor daemon managing zero-idle posture and wave lifecycles."""

    @abc.abstractmethod
    def run_supervisor_tick(self) -> None:
        """Executes one polling cycle of the supervisor daemon."""
        pass

    @abc.abstractmethod
    def is_idle(self) -> bool:
        """Returns True if supervisor maintains Zero Idle LLM Token Posture."""
        pass

    @abc.abstractmethod
    def dispatch_job(self, job_id: str) -> str:
        """Assigns validated job to ephemeral Graph-H DAG engine."""
        pass


class IDagScheduler(abc.ABC):
    """Ephemeral Graph-H DAG execution scheduler coordinating phased worker waves."""

    @abc.abstractmethod
    def initialize_graph(self, graph: ExecutionGraph, run_id: str) -> None:
        """Configures the ephemeral execution graph."""
        pass

    @abc.abstractmethod
    def execute_phases(self) -> Dict[str, ReconciledResult]:
        """Coordinates phased execution with concurrency throttling and dependency barriers."""
        pass

    @abc.abstractmethod
    def cancel_execution(self, reason: str = "Operator Cancel") -> None:
        """Initiates graceful safe-stop of all active worker instances."""
        pass


class IApprovalManager(abc.ABC):
    """Manages bounded human approval action gates."""

    @abc.abstractmethod
    def create_approval_request(
        self, job_id: str, action: str, scope: List[str], run_id: Optional[str] = None, ttl_seconds: int = 3600
    ) -> str:
        """Issues bounded approval request token."""
        pass

    @abc.abstractmethod
    def record_decision(
        self, request_id: str, decision: str, approver: Approver, notes: Optional[str] = None
    ) -> ApprovalToken:
        """Records sovereign human decision and validates bindings."""
        pass

    @abc.abstractmethod
    def get_approval(self, request_id: str) -> Optional[ApprovalToken]:
        """Retrieves approval record by request token."""
        pass


class IReconciler(abc.ABC):
    """4-dimensional canonical run status reconciliation."""

    @abc.abstractmethod
    def reconcile(
        self,
        run_id: str,
        agent_id: str,
        pid: Optional[int],
        process_name: str,
        is_active: bool,
        exit_code: Optional[int],
        persisted_start_time: Optional[str],
        actual_start_time: Optional[datetime],
        persisted_status: str,
        report_path: Path,
        stdout_path: Path,
        stderr_path: Path,
        worktree_path: Path,
    ) -> ReconciledResult:
        """Evaluates 4 pillars and returns canonical reconciled verdict."""
        pass


class IRecoveryManager(abc.ABC):
    """Startup reconciliation and crash recovery manager."""

    @abc.abstractmethod
    def reconcile_startup(self) -> List[str]:
        """Detects and reconciles INTERRUPTED runs from prior host crash."""
        pass

    @abc.abstractmethod
    def check_pid_safety(self, pid: int, recorded_start_time: str) -> bool:
        """Verifies process identity to prevent interacting with recycled PIDs."""
        pass

"""SACL V1 Authoritative SQLite Operational State Store.

Implements IStateStore interface against the frozen 16-domain schema (sacl_ops.db).
Coordinates repositories, transactions, migrations, leases, heartbeats, durable queues,
and idempotency defense.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Union

from sacl.contracts.interfaces import IStateStore
from sacl.contracts.models import AuditEvent, HeartbeatRecord
from sacl.state.connection import ConnectionManager, create_connection
from sacl.state.heartbeats import HeartbeatManager
from sacl.state.idempotency import IdempotencyHelper
from sacl.state.leases import LeaseManager
from sacl.state.migrations import MigrationRunner
from sacl.state.queues import DurableJobQueue, DurableMailQueue, DurableOutboxQueue
from sacl.state.repositories.agents import AgentRepository
from sacl.state.repositories.approvals import ApprovalRepository
from sacl.state.repositories.artifacts import ArtifactRepository
from sacl.state.repositories.errors import ErrorRepository
from sacl.state.repositories.events import EventRepository
from sacl.state.repositories.graph import GraphRepository
from sacl.state.repositories.jobs import JobRepository
from sacl.state.repositories.mail import MailRepository
from sacl.state.repositories.packages import PackageRepository
from sacl.state.repositories.projects import ProjectRepository
from sacl.state.repositories.results import ResultRepository
from sacl.state.repositories.runs import RunRepository
from sacl.state.transactions import savepoint, transaction


class SqliteStateStore(IStateStore):
    """Authoritative local operational state store implementation for SACL V1."""

    def __init__(self, db_path: Union[str, Path] = ":memory:", auto_migrate: bool = False) -> None:
        self.db_path = db_path
        self._conn_manager = ConnectionManager(db_path)
        self._conn = self._conn_manager.get_connection()

        # Initialize Repositories
        self.jobs = JobRepository(self._conn)
        self.runs = RunRepository(self._conn)
        self.graph = GraphRepository(self._conn)
        self.agents = AgentRepository(self._conn)
        self.events = EventRepository(self._conn)
        self.approvals = ApprovalRepository(self._conn)
        self.artifacts = ArtifactRepository(self._conn)
        self.results = ResultRepository(self._conn)
        self.projects = ProjectRepository(self._conn)
        self.packages = PackageRepository(self._conn)
        self.errors = ErrorRepository(self._conn)
        self.mail = MailRepository(self._conn)

        # Initialize Managers & Helpers
        self.leases = LeaseManager(self._conn)
        self.heartbeats = HeartbeatManager(self._conn)
        self.job_queue = DurableJobQueue(self._conn)
        self.mail_queue = DurableMailQueue(self._conn)
        self.outbox_queue = DurableOutboxQueue(self._conn)
        self.idempotency = IdempotencyHelper(self._conn)
        self.migrations = MigrationRunner()

        if auto_migrate:
            self.initialize_schema()

    @property
    def connection(self) -> sqlite3.Connection:
        """Returns the primary active database connection."""
        return self._conn

    # =========================================================================
    # TRANSACTION MANAGEMENT
    # =========================================================================

    @contextmanager
    def transaction(self, immediate: bool = True) -> Generator[sqlite3.Connection, None, None]:
        """Executes operations inside an explicit ACID transaction (BEGIN IMMEDIATE)."""
        with transaction(self._conn, immediate=immediate):
            yield self._conn

    @contextmanager
    def savepoint(self, name: Optional[str] = None) -> Generator[str, None, None]:
        """Executes operations within an isolated savepoint sub-transaction."""
        with savepoint(self._conn, name=name) as sp_name:
            yield sp_name

    # =========================================================================
    # IStateStore IMPLEMENTATION
    # =========================================================================

    def initialize_schema(self, migration_sql_path: Optional[Path] = None) -> None:
        """Applies canonical DDL migrations."""
        if migration_sql_path:
            p = Path(migration_sql_path)
            if p.is_file():
                self.migrations.apply_migration_file(self._conn, p)
            elif p.is_dir():
                self.migrations.apply_all(self._conn, migrations_dir=p)
            else:
                raise FileNotFoundError(f"Migration path '{p}' not found")
        else:
            self.migrations.apply_all(self._conn)

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
        self.jobs.create_job(
            job_id=job_id,
            package_id=package_id,
            project_id=project_id,
            status=status,
            priority=priority,
            metadata=metadata,
        )

    def update_job_status(
        self,
        job_id: str,
        status: str,
        current_run_id: Optional[str] = None,
        error_summary: Optional[str] = None,
    ) -> None:
        """Updates job lifecycle state."""
        self.jobs.update_job_status(
            job_id=job_id,
            status=status,
            current_run_id=current_run_id,
            error_summary=error_summary,
        )

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves logical job record."""
        return self.jobs.get_job(job_id)

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
        self.runs.create_run(
            run_id=run_id,
            job_id=job_id,
            package_id=package_id,
            project=project,
            repository=repository,
            mode=mode,
            source_orchestrator=source_orchestrator,
            target_repo_path=target_repo_path,
            run_dir=run_dir,
            status=status,
        )

    def update_run_status(
        self,
        run_id: str,
        status: str,
        ready_for_integration: str = "NO",
        reconciled_verdict: Optional[str] = None,
        error_summary: Optional[str] = None,
    ) -> None:
        """Updates physical run attempt outcome."""
        self.runs.update_run_status(
            run_id=run_id,
            status=status,
            ready_for_integration=ready_for_integration,
            reconciled_verdict=reconciled_verdict,
            error_summary=error_summary,
        )

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
        self.agents.record_agent(
            agent_id=agent_id,
            run_id=run_id,
            status=status,
            prompt_path=prompt_path,
            report_path=report_path,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            pid=pid,
            worktree_path=worktree_path,
            branch=branch,
        )

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
        self.agents.update_agent(
            agent_id=agent_id,
            run_id=run_id,
            status=status,
            result_verdict=result_verdict,
            exit_code=exit_code,
            commit_sha=commit_sha,
            error_message=error_message,
        )

    def record_event(self, event: AuditEvent) -> int:
        """Appends structured audit event."""
        return self.events.record_event(event)

    def acquire_lease(
        self,
        lease_name: str,
        holder_id: str,
        holder_pid: int,
        ttl_seconds: int = 30,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Attempts atomic mutual exclusion lease acquisition."""
        return self.leases.acquire_lease(
            lease_name=lease_name,
            holder_id=holder_id,
            holder_pid=holder_pid,
            ttl_seconds=ttl_seconds,
            metadata=metadata,
        )

    def renew_lease(self, lease_name: str, holder_id: str, ttl_seconds: int = 30) -> bool:
        """Renews active mutual exclusion lease."""
        return self.leases.renew_lease(
            lease_name=lease_name,
            holder_id=holder_id,
            ttl_seconds=ttl_seconds,
        )

    def release_lease(self, lease_name: str, holder_id: str) -> bool:
        """Releases mutual exclusion lease."""
        return self.leases.release_lease(
            lease_name=lease_name,
            holder_id=holder_id,
        )

    def record_heartbeat(self, heartbeat: HeartbeatRecord) -> int:
        """Records process liveness heartbeat."""
        return self.heartbeats.record_heartbeat_model(heartbeat)

    def record_file_modifications(
        self, run_id: str, agent_id: str, file_paths: List[str]
    ) -> None:
        """Records git files modified by an agent."""
        self.agents.record_file_modifications(run_id, agent_id, file_paths)

    def detect_file_conflicts(self, run_id: str) -> List[Dict[str, Any]]:
        """Queries database for cross-agent overlapping file modifications."""
        return self.agents.detect_file_conflicts(run_id)

    # =========================================================================
    # DOMAIN FACADE HELPERS
    # =========================================================================

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves physical run attempt record."""
        return self.runs.get_run(run_id)

    def list_runs(
        self,
        job_id: Optional[str] = None,
        project_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Lists physical execution runs."""
        return self.runs.list_runs(job_id=job_id, project_id=project_id, status=status, limit=limit)

    def get_agent(self, agent_id: str, run_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves agent worker record."""
        return self.agents.get_agent(agent_id, run_id)

    def list_agents(self, run_id: str) -> List[Dict[str, Any]]:
        """Lists agents associated with a given execution run."""
        return self.agents.list_agents(run_id)

    def list_events(
        self,
        job_id: Optional[str] = None,
        run_id: Optional[str] = None,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Lists structured audit events."""
        return self.events.list_events(job_id=job_id, run_id=run_id, event_type=event_type, severity=severity, limit=limit)

    def register_project(
        self,
        project_id: str,
        name: str,
        root_path: str,
        repo_url: Optional[str] = None,
        default_branch: str = "main",
        policy_override: Optional[Union[Dict[str, Any], str]] = None,
    ) -> Dict[str, Any]:
        """Registers a project repository in Domain 2."""
        return self.projects.register_project(
            project_id=project_id,
            name=name,
            root_path=root_path,
            repo_url=repo_url,
            default_branch=default_branch,
            policy_override=policy_override,
        )

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves project record by project ID."""
        return self.projects.get_project(project_id)

    def record_package(
        self,
        package_id: str,
        archive_sha256: str,
        manifest: Union[Dict[str, Any], str],
        storage_path: str,
        status: str = "RECEIVED",
        job_id: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Records ingested execution package in Domain 3."""
        return self.packages.record_package(
            package_id=package_id,
            archive_sha256=archive_sha256,
            manifest=manifest,
            storage_path=storage_path,
            status=status,
            job_id=job_id,
            project_id=project_id,
        )

    def get_package(self, package_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves package by package ID."""
        return self.packages.get_package(package_id)

    def record_result(
        self,
        job_id: str,
        run_id: str,
        status: str,
        final_verdict: str,
        summary_md_path: str,
        summary_json_path: str,
        package_result_zip: Optional[str] = None,
        delivered_to: Optional[str] = None,
    ) -> int:
        """Records sealed final execution result in Domain 12."""
        return self.results.record_result(
            job_id=job_id,
            run_id=run_id,
            status=status,
            final_verdict=final_verdict,
            summary_md_path=summary_md_path,
            summary_json_path=summary_json_path,
            package_result_zip=package_result_zip,
            delivered_to=delivered_to,
        )

    def get_result(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves sealed execution result."""
        return self.results.get_result(run_id)

    def record_error(
        self,
        error_code: str,
        category: str,
        severity: str,
        message: str,
        job_id: Optional[str] = None,
        run_id: Optional[str] = None,
        node_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        stack_trace: Optional[str] = None,
        context: Optional[Union[Dict[str, Any], str]] = None,
    ) -> int:
        """Records structured error event in Domain 15."""
        return self.errors.record_error(
            error_code=error_code,
            category=category,
            severity=severity,
            message=message,
            job_id=job_id,
            run_id=run_id,
            node_id=node_id,
            agent_id=agent_id,
            stack_trace=stack_trace,
            context=context,
        )

    def __enter__(self) -> SqliteStateStore:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def close(self) -> None:
        """Closes underlying database connections."""
        self._conn_manager.close()


# StateStore alias for developer ergonomics
StateStore = SqliteStateStore

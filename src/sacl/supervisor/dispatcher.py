"""SACL V1 Job Wake and Dispatch Subsystem.

Coordinates:
- Prioritized queue polling (priority DESC, created_at ASC).
- Project concurrency lock acquisition (1 mutating job per project baseline).
- Local Dirty-Root Rule verification on target repository checkout.
- Canonical state advancement: QUEUED -> DISPATCHED -> RUNNING.
- Invocation of ephemeral Graph-H execution engine per wave package.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sqlite3
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from uuid import uuid4

from sacl.contracts.exceptions import (
    DirtyRootError,
    LeaseAcquisitionError,
    PolicyDeniedError,
    SaclError,
)
from sacl.contracts.invariants import (
    JobSideStatus,
    JobStatus,
)
from sacl.observability.events import (
    AuditEventType,
    GATE_HALTED,
    PROCESS_SPAWNED,
    Severity,
    create_audit_event,
)
from sacl.supervisor.lease import LeaseCoordinator
from sacl.supervisor.lifecycle import JobLifecycleManager


@dataclass
class RunContext:
    """Execution context passed to ephemeral Graph-H engine."""

    run_id: str
    job_id: str
    project_id: Optional[str]
    package_id: Optional[str]
    project_name: str
    repository: str
    target_repo_path: str
    run_dir: str
    is_mutating: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    pid: Optional[int] = None


class JobDispatcher:
    """Selects and dispatches queued jobs into ephemeral Graph-H execution engines."""

    def __init__(
        self,
        db_source: Union[sqlite3.Connection, Path, str, Callable[[], sqlite3.Connection]],
        lease_coordinator: LeaseCoordinator,
        lifecycle_manager: JobLifecycleManager,
        executor_launcher: Optional[Callable[[RunContext], Any]] = None,
        clean_root_checker: Optional[Callable[[str], Tuple[bool, List[str]]]] = None,
        policy_engine: Optional[Any] = None,
        audit_emitter: Optional[Any] = None,
        error_recorder: Optional[Any] = None,
        project_root_resolver: Optional[Callable[[str], str]] = None,
    ):
        self._db_source = db_source
        self._db_file: Optional[str] = None
        self.lease_coordinator = lease_coordinator
        self.lifecycle_manager = lifecycle_manager
        self.executor_launcher = executor_launcher
        self.clean_root_checker = clean_root_checker
        self.policy_engine = policy_engine
        self.audit_emitter = audit_emitter
        self.error_recorder = error_recorder
        self.project_root_resolver = project_root_resolver
        self._active_contexts: Dict[str, RunContext] = {}
        self._active_launcher_results: Dict[str, Any] = {}

        if isinstance(db_source, sqlite3.Connection):
            try:
                for r in db_source.execute("PRAGMA database_list;").fetchall():
                    if r[1] == "main" and r[2] and r[2] != ":memory:":
                        self._db_file = r[2]
                        break
            except Exception:
                pass

    def _get_connection(self) -> Tuple[sqlite3.Connection, bool]:
        if isinstance(self._db_source, sqlite3.Connection):
            try:
                self._db_source.execute("SELECT 1;")
                return self._db_source, False
            except sqlite3.ProgrammingError:
                if self._db_file:
                    conn = sqlite3.connect(self._db_file)
                    conn.row_factory = sqlite3.Row
                    conn.execute("PRAGMA foreign_keys = ON;")
                    conn.execute("PRAGMA busy_timeout = 5000;")
                    return conn, True
                raise
        elif callable(self._db_source):
            return self._db_source(), False
        else:
            conn = sqlite3.connect(str(self._db_source))
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("PRAGMA busy_timeout = 5000;")
            return conn, True

    def _resolve_target_repo_path(self, project_id: Optional[str], metadata: Dict[str, Any]) -> str:
        """Determines target repository path from resolver, project registry, or metadata."""
        # A configured registry resolver is authoritative. Untrusted package
        # metadata cannot redirect an otherwise registered project.
        if project_id and self.project_root_resolver:
            try:
                registered_root = self.project_root_resolver(project_id)
            except Exception as exc:
                raise PolicyDeniedError(
                    action="resolve_target_root",
                    layer="PROJECT_REGISTRY",
                    reason=f"Trusted project root resolver failed for '{project_id}': {exc}",
                ) from exc
            if not isinstance(registered_root, (str, Path)) or not str(registered_root).strip():
                raise PolicyDeniedError(
                    action="resolve_target_root",
                    layer="PROJECT_REGISTRY",
                    reason=f"Trusted project root resolver returned an invalid root for '{project_id}'.",
                )
            requested = metadata.get("target_repo_path")
            if requested is not None:
                try:
                    from sacl.policy.project_registry import normalize_fs_path
                    matches = normalize_fs_path(requested) == normalize_fs_path(registered_root)
                except (OSError, ValueError, TypeError):
                    matches = False
                if not matches:
                    raise PolicyDeniedError(
                        action="resolve_target_root",
                        layer="PROJECT_REGISTRY",
                        reason=f"Untrusted target_repo_path override denied for '{project_id}'.",
                    )
            return str(registered_root)

        if metadata.get("target_repo_path"):
            return str(metadata["target_repo_path"])

        # Try querying projects table directly
        if project_id:
            conn, should_close = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT root_path FROM projects WHERE project_id = ?", (project_id,))
                row = cursor.fetchone()
                if row and row["root_path"]:
                    return str(row["root_path"])
            except sqlite3.OperationalError:
                pass
            finally:
                if should_close:
                    conn.close()

        return str(Path.cwd())

    def poll_and_dispatch(self, limit: Optional[int] = None) -> List[str]:
        """Scans for queued jobs and dispatches eligible ones.

        Returns list of newly dispatched run IDs.
        """
        queued_jobs = self.lifecycle_manager.get_queued_jobs(limit=limit)
        dispatched_runs: List[str] = []

        for job in queued_jobs:
            job_id = job["job_id"]
            run_id = self.dispatch_job(job_id)
            if run_id:
                dispatched_runs.append(run_id)

        return dispatched_runs

    def dispatch_job(self, job_id: str) -> Optional[str]:
        """Dispatches a single queued job into ephemeral Graph-H execution.

        Returns run_id if dispatched, or None if skipped (e.g. project lock held).
        """
        job = self.lifecycle_manager.get_job(job_id)
        if not job:
            return None

        if job["status"] != JobStatus.QUEUED.value:
            return None

        project_id = job.get("project_id")
        package_id = job.get("package_id")
        metadata = job.get("metadata", {})
        is_mutating = metadata.get("is_mutating", True)

        now_dt = datetime.now(timezone.utc)
        timestamp_str = now_dt.strftime("%Y%m%d-%H%M%S")
        suffix = uuid4().hex[:6]
        run_id = f"run-{timestamp_str}-{suffix}"

        # Graph-H must be configured before leasing a project or creating a run.
        # An absent executor is never evidence of a RUNNING worker.
        if self.executor_launcher is None:
            self.lifecycle_manager.transition(
                job_id=job_id,
                to_status=JobSideStatus.BLOCKED.value,
                error_summary="EXECUTOR_UNAVAILABLE: Graph-H launcher is not configured",
                expected_current_status=JobStatus.QUEUED.value,
            )
            return None

        # Resolve trusted target before acquiring any lease or creating a run.
        # Denials leave no RUNNING job, lease, or physical run record.
        try:
            target_repo_path = self._resolve_target_repo_path(project_id, metadata)
        except PolicyDeniedError as exc:
            self.lifecycle_manager.transition(
                job_id=job_id,
                to_status=JobSideStatus.POLICY_DENIED.value,
                error_summary=f"TARGET_ROOT_DENIED: {exc}",
                expected_current_status=JobStatus.QUEUED.value,
            )
            return None

        # ---------------------------------------------------------------------
        # 1. Project Concurrency Lock Check
        # ---------------------------------------------------------------------
        if project_id:
            acquired = self.lease_coordinator.acquire_project_lease(
                project_id=project_id,
                run_id=run_id,
                is_mutating=is_mutating,
                job_id=job_id,
            )
            if not acquired:
                # Another job holds the project lock; job remains QUEUED
                return None

        run_dir = str(Path("runs") / run_id)

        # ---------------------------------------------------------------------
        # 2. Local Dirty-Root Rule Verification
        # ---------------------------------------------------------------------
        if self.clean_root_checker:
            try:
                is_clean, dirty_files = self.clean_root_checker(target_repo_path)
                if not is_clean:
                    # Inviolable rule: Human uncommitted work is never destroyed or stashed
                    error_msg = (
                        f"DIRTY_ROOT_HALT: Uncommitted modifications detected in primary checkout "
                        f"'{target_repo_path}': {dirty_files[:5]}"
                    )
                    if self.error_recorder:
                        self.error_recorder.record_error(
                            error_code="DIRTY_ROOT_HALT",
                            category="EXECUTION",
                            severity="FATAL",
                            message=error_msg,
                            job_id=job_id,
                            run_id=run_id,
                            context={"dirty_files": dirty_files, "target_repo": target_repo_path},
                        )

                    if self.audit_emitter:
                        self.audit_emitter.emit(
                            event_type=GATE_HALTED,
                            severity=Severity.FATAL.value,
                            job_id=job_id,
                            run_id=run_id,
                            payload={"reason": error_msg, "dirty_files": dirty_files},
                        )

                    # Transition job to BLOCKED
                    self.lifecycle_manager.transition(
                        job_id=job_id,
                        to_status=JobSideStatus.BLOCKED.value,
                        current_run_id=run_id,
                        error_summary=error_msg,
                    )
                    # Release project lease
                    if project_id:
                        self.lease_coordinator.release_project_lease(project_id, run_id=run_id)
                    return None
            except Exception as e:
                # If clean root checking encounters a critical error, fail closed
                if project_id:
                    self.lease_coordinator.release_project_lease(project_id, run_id=run_id)
                raise

        # ---------------------------------------------------------------------
        # 3. Create Physical Run Attempt Record in SQLite
        # ---------------------------------------------------------------------
        conn, should_close = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO runs (
                    run_id, job_id, package_id, project_id, project, repository,
                    mode, source_orchestrator, target_repo_path, run_dir, status,
                    ready_for_integration, started_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'NO', ?)
                """,
                (
                    run_id,
                    job_id,
                    package_id or f"pkg-{job_id}",
                    project_id,
                    project_id or "default-project",
                    metadata.get("repository", "default-repo"),
                    metadata.get("mode", "isolated_branch_development"),
                    str(Path.cwd()),
                    target_repo_path,
                    run_dir,
                    JobStatus.DISPATCHED.value,
                    now_dt.isoformat(),
                ),
            )
            conn.commit()
        finally:
            if should_close:
                conn.close()

        # ---------------------------------------------------------------------
        # 4. Canonical State Advance: QUEUED -> DISPATCHED
        # ---------------------------------------------------------------------
        self.lifecycle_manager.transition(
            job_id=job_id,
            to_status=JobStatus.DISPATCHED.value,
            current_run_id=run_id,
            expected_current_status=JobStatus.QUEUED.value,
        )

        run_context = RunContext(
            run_id=run_id,
            job_id=job_id,
            project_id=project_id,
            package_id=package_id,
            project_name=project_id or "default-project",
            repository=metadata.get("repository", "default-repo"),
            target_repo_path=target_repo_path,
            run_dir=run_dir,
            is_mutating=is_mutating,
            metadata=metadata,
        )

        # ---------------------------------------------------------------------
        # 5. Invoke Ephemeral Graph-H DAG Engine
        # ---------------------------------------------------------------------
        launcher_result = None
        if self.executor_launcher:
            try:
                launcher_result = self.executor_launcher(run_context)
                # Reject placeholders, bools, invalid PIDs and already-exited handles.
                # Never mark a job RUNNING without a usable executor identity.
                if type(launcher_result) is int:
                    if launcher_result <= 0:
                        raise RuntimeError("EXECUTOR_UNAVAILABLE: launcher returned an invalid PID")
                    run_context.pid = launcher_result
                else:
                    pid = getattr(launcher_result, "pid", None)
                    poll = getattr(launcher_result, "poll", None)
                    if type(pid) is not int or pid <= 0 or not callable(poll):
                        raise RuntimeError(
                            "EXECUTOR_UNAVAILABLE: launcher returned no valid process handle or PID"
                        )
                    if poll() is not None:
                        raise RuntimeError("EXECUTOR_UNAVAILABLE: launcher process already exited")
                    run_context.pid = pid
            except Exception as ex:
                err_msg = f"Failed to spawn ephemeral Graph-H engine: {ex}"
                self.lifecycle_manager.transition(
                    job_id=job_id,
                    to_status=JobSideStatus.FAILED.value,
                    current_run_id=run_id,
                    error_summary=err_msg,
                )
                if project_id:
                    self.lease_coordinator.release_project_lease(project_id, run_id=run_id)
                return None

        self._active_contexts[run_id] = run_context
        self._active_launcher_results[run_id] = launcher_result

        # ---------------------------------------------------------------------
        # 6. Canonical State Advance: DISPATCHED -> RUNNING
        # ---------------------------------------------------------------------
        self.lifecycle_manager.transition(
            job_id=job_id,
            to_status=JobStatus.RUNNING.value,
            current_run_id=run_id,
            expected_current_status=JobStatus.DISPATCHED.value,
        )

        if self.audit_emitter:
            self.audit_emitter.emit(
                event_type=PROCESS_SPAWNED,
                severity=Severity.INFO.value,
                job_id=job_id,
                run_id=run_id,
                payload={
                    "run_id": run_id,
                    "target_repo_path": target_repo_path,
                    "is_mutating": is_mutating,
                    "worker_pid": run_context.pid,
                },
            )

        return run_id

    def get_run_context(self, run_id: str) -> Optional[RunContext]:
        """Returns the RunContext associated with a dispatched run."""
        return self._active_contexts.get(run_id)

    def get_launcher_result(self, run_id: str) -> Optional[Any]:
        """Returns the launcher result / process handle associated with a dispatched run."""
        return self._active_launcher_results.get(run_id)


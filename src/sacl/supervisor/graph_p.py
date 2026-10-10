"""SACL V1 Persistent Graph-P Supervisor Daemon Subsystem.

Implements:
- ADR-003: Persistent IDLE Supervisor Daemon (Graph-P) with Zero Idle Token Burn
- Decision Baseline Decisions 16, 17, 18
- Canonical ISupervisor interface (run_supervisor_tick, is_idle, dispatch_job)
- Singleton & project lease coordination
- Cold-start crash recovery (Never Blindly Restart Old RUNNING)
- Graceful operator shutdown
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import json
import os
from pathlib import Path
import sqlite3
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from sacl.contracts.exceptions import (
    ArchitectureInvariantError,
    LeaseAcquisitionError,
    SaclError,
)
from sacl.contracts.invariants import (
    ALLOWED_PROCESS_IMAGES,
    JobSideStatus,
    JobStatus,
    PID_DRIFT_TOLERANCE_SECONDS,
    Verdict,
)
from sacl.contracts.interfaces import ISupervisor
from sacl.contracts.reconciliation import extract_verdict_from_content
from sacl.observability.events import (
    GATE_HALTED,
    Severity,
    create_audit_event,
)
from sacl.supervisor.dispatcher import JobDispatcher, RunContext
from sacl.supervisor.lease import LeaseCoordinator, default_process_alive_check
from sacl.supervisor.lifecycle import JobLifecycleManager


class SupervisorState(str, Enum):
    """Operational lifecycle state of Graph-P daemon."""

    STOPPED = "STOPPED"
    STARTING = "STARTING"
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"


@dataclass
class SupervisorConfig:
    """Runtime configuration for Graph-P daemon."""

    poll_interval_seconds: float = 1.0
    heartbeat_interval_seconds: float = 10.0
    singleton_ttl_seconds: int = 60
    project_ttl_seconds: int = 300
    max_active_jobs: int = 4
    enable_crash_recovery_on_start: bool = True


@dataclass
class ActiveRunTracking:
    """In-memory tracking record for an actively supervised run."""

    run_id: str
    job_id: str
    project_id: Optional[str]
    dispatched_at: datetime
    process_handle: Optional[Any] = None
    pid: Optional[int] = None
    report_path: Optional[Path] = None


class GraphPSupervisor(ISupervisor):
    """Persistent Graph-P supervisor daemon managing zero-idle posture and wave lifecycles."""

    def __init__(
        self,
        db_source: Union[sqlite3.Connection, Path, str, Callable[[], sqlite3.Connection]],
        instance_id: Optional[str] = None,
        config: Optional[SupervisorConfig] = None,
        lease_coordinator: Optional[LeaseCoordinator] = None,
        lifecycle_manager: Optional[JobLifecycleManager] = None,
        dispatcher: Optional[JobDispatcher] = None,
        heartbeat_service: Optional[Any] = None,
        audit_emitter: Optional[Any] = None,
        error_recorder: Optional[Any] = None,
        process_checker: Optional[Callable[[int], bool]] = None,
    ):
        self._db_source = db_source
        self._db_file: Optional[str] = None
        self.pid = os.getpid()
        self.instance_id = instance_id or f"graph-p-{self.pid}"
        self.config = config or SupervisorConfig()
        self.process_checker = process_checker or default_process_alive_check

        self.audit_emitter = audit_emitter
        self.error_recorder = error_recorder
        self.heartbeat_service = heartbeat_service

        self.lease_coordinator = lease_coordinator or LeaseCoordinator(
            db_source=db_source,
            audit_emitter=self.audit_emitter,
            process_checker=self.process_checker,
        )

        self.lifecycle_manager = lifecycle_manager or JobLifecycleManager(
            db_source=db_source,
            lease_coordinator=self.lease_coordinator,
            audit_emitter=self.audit_emitter,
        )

        self.dispatcher = dispatcher or JobDispatcher(
            db_source=db_source,
            lease_coordinator=self.lease_coordinator,
            lifecycle_manager=self.lifecycle_manager,
            audit_emitter=self.audit_emitter,
            error_recorder=self.error_recorder,
        )

        self._state = SupervisorState.STOPPED
        self._is_idle = True
        self._active_runs: Dict[str, ActiveRunTracking] = {}
        self._stop_event = threading.Event()
        self._last_heartbeat_time = 0.0

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

    @property
    def state(self) -> SupervisorState:
        return self._state

    @property
    def active_runs(self) -> Dict[str, ActiveRunTracking]:
        return dict(self._active_runs)

    # =========================================================================
    # ISUPERVISOR INTERFACE: ZERO IDLE TOKEN POSTURE
    # =========================================================================

    def is_idle(self) -> bool:
        """Returns True if supervisor maintains Zero Idle LLM Token Posture.

        Strict Zero Idle Invariant (ADR-003):
        - Zero LLM tokens consumed.
        - Zero resident LLM / Antigravity child worker processes in memory.
        - Lightweight deterministic state machine.
        """
        return len(self._active_runs) == 0

    # =========================================================================
    # ISUPERVISOR INTERFACE: DISPATCH JOB
    # =========================================================================

    def dispatch_job(self, job_id: str) -> str:
        """Assigns a validated queued job to ephemeral Graph-H engine."""
        run_id = self.dispatcher.dispatch_job(job_id)
        if not run_id:
            raise SaclError(f"Job '{job_id}' could not be dispatched (project lock contention or dirty root)")

        job = self.lifecycle_manager.get_job(job_id)
        project_id = job.get("project_id") if job else None
        ctx = self.dispatcher.get_run_context(run_id)
        launcher_res = self.dispatcher.get_launcher_result(run_id)
        pid = ctx.pid if ctx else None

        self._active_runs[run_id] = ActiveRunTracking(
            run_id=run_id,
            job_id=job_id,
            project_id=project_id,
            dispatched_at=datetime.now(timezone.utc),
            pid=pid,
            process_handle=launcher_res,
        )
        self._is_idle = False
        self._state = SupervisorState.RUNNING
        return run_id

    # =========================================================================
    # ISUPERVISOR INTERFACE: SUPERVISOR TICK
    # =========================================================================

    def run_supervisor_tick(self) -> None:
        """Executes one polling cycle of the Graph-P supervisor daemon."""
        # 1. System Lock Maintenance
        lease_renewed = self.lease_coordinator.renew_singleton_lease(
            holder_id=self.instance_id,
            holder_pid=self.pid,
            ttl_seconds=self.config.singleton_ttl_seconds,
        )
        if not lease_renewed:
            # Attempt to acquire if not held
            acquired = self.lease_coordinator.acquire_singleton_lease(
                holder_id=self.instance_id,
                holder_pid=self.pid,
                ttl_seconds=self.config.singleton_ttl_seconds,
            )
            if not acquired:
                err_msg = f"Supervisor singleton lease lost or held by another process: {self.instance_id}"
                if self.audit_emitter:
                    self.audit_emitter.emit(
                        event_type=GATE_HALTED,
                        severity=Severity.FATAL.value,
                        payload={"reason": err_msg},
                    )
                raise LeaseAcquisitionError(
                    lease_name=LeaseCoordinator.SUPERVISOR_SINGLETON_KEY,
                    current_holder="UNKNOWN",
                    holder_pid=-1,
                )

        # 2. Process Liveness Heartbeat
        now_time = time.time()
        if now_time - self._last_heartbeat_time >= self.config.heartbeat_interval_seconds:
            self._emit_liveness_heartbeat()
            self._last_heartbeat_time = now_time

        # 3. Monitor Active Runs
        self._monitor_active_runs()

        # 4. Job Wake & Dispatch
        if len(self._active_runs) < self.config.max_active_jobs:
            limit = self.config.max_active_jobs - len(self._active_runs)
            dispatched_runs = self.dispatcher.poll_and_dispatch(limit=limit)
            for r_id in dispatched_runs:
                # Find matching job
                job_id = self._find_job_id_for_run(r_id)
                if job_id:
                    job = self.lifecycle_manager.get_job(job_id)
                    p_id = job.get("project_id") if job else None
                    ctx = self.dispatcher.get_run_context(r_id)
                    launcher_res = self.dispatcher.get_launcher_result(r_id)
                    pid = ctx.pid if ctx else None
                    self._active_runs[r_id] = ActiveRunTracking(
                        run_id=r_id,
                        job_id=job_id,
                        project_id=p_id,
                        dispatched_at=datetime.now(timezone.utc),
                        pid=pid,
                        process_handle=launcher_res,
                    )

        # 5. Update IDLE Posture
        self._is_idle = (len(self._active_runs) == 0)
        if self._state not in {SupervisorState.STOPPED, SupervisorState.STOPPING}:
            self._state = SupervisorState.IDLE if self._is_idle else SupervisorState.RUNNING

    def _find_job_id_for_run(self, run_id: str) -> Optional[str]:
        conn, should_close = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT job_id FROM runs WHERE run_id = ?", (run_id,))
            row = cursor.fetchone()
            return row["job_id"] if row else None
        except sqlite3.OperationalError:
            return None
        finally:
            if should_close:
                conn.close()

    def _emit_liveness_heartbeat(self) -> None:
        if not self.heartbeat_service:
            return
        status = "IDLE" if self.is_idle() else "RUNNING"
        details = {
            "state": self._state.value,
            "active_runs_count": len(self._active_runs),
            "is_idle": self.is_idle(),
            "max_active_jobs": self.config.max_active_jobs,
        }
        try:
            self.heartbeat_service.record_heartbeat(
                component="SUPERVISOR",
                instance_id=self.instance_id,
                pid=self.pid,
                status=status,
                details=details,
            )
        except Exception:
            pass

    def _monitor_active_runs(self) -> None:
        """Inspects status of all currently active runs, finalizing completed ones."""
        completed_run_ids: List[str] = []

        for run_id, tracking in list(self._active_runs.items()):
            # Inspect SQLite status for external completions (e.g. Graph-H engine or runner finished)
            conn, should_close = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT status FROM jobs WHERE job_id = ?", (tracking.job_id,))
                job_row = cursor.fetchone()
                job_status = job_row["status"] if job_row else None

                if job_status in {
                    JobStatus.COMPLETED.value,
                    JobStatus.ARCHIVED.value,
                    JobSideStatus.FAILED.value,
                    JobSideStatus.CANCELLED.value,
                    JobSideStatus.BLOCKED.value,
                    JobSideStatus.TIMED_OUT.value,
                    JobSideStatus.INTERRUPTED.value,
                }:
                    completed_run_ids.append(run_id)
                    continue

                # If process handle exists or PID tracked, check liveness
                has_exited = False
                if tracking.process_handle and hasattr(tracking.process_handle, "poll"):
                    if tracking.process_handle.poll() is not None:
                        has_exited = True
                elif tracking.pid and tracking.pid > 0:
                    if not self.process_checker(tracking.pid):
                        has_exited = True

                if has_exited:
                    # Worker process exited -> evaluate deliverables via 4-point reconciliation
                    self._finalize_run_on_process_exit(tracking)
                    completed_run_ids.append(run_id)
            finally:
                if should_close:
                    conn.close()

        for r_id in completed_run_ids:
            self._active_runs.pop(r_id, None)

    def _finalize_run_on_process_exit(self, tracking: ActiveRunTracking) -> None:
        """Evaluates deliverables and completes the job lifecycle upon worker process exit.

        Strictly enforces: Process.ExitCode alone is INSUFFICIENT to determine success.
        Reconciles via 4-point protocol: process observation + persisted state +
        required outputs + final verdict extraction.
        """
        job_id = tracking.job_id
        run_id = tracking.run_id
        project_id = tracking.project_id

        # 1. Advance to VERIFYING
        try:
            self.lifecycle_manager.transition(
                job_id=job_id,
                to_status=JobStatus.VERIFYING.value,
                current_run_id=run_id,
            )
        except Exception:
            pass

        # 2. Evaluate 4-Point Deliverable Reconciliation
        reconciled_verdict = self._reconcile_run_deliverables(tracking)

        # 3. Canonical State Advancement based on Reconciled Verdict
        if reconciled_verdict in {
            Verdict.PASS.value,
            Verdict.PARTIAL.value,
            Verdict.PASS_REPORT_PRESENT.value,
            Verdict.DONE_REVIEW_REQUIRED.value,
        }:
            try:
                self.lifecycle_manager.transition(
                    job_id=job_id,
                    to_status=JobStatus.RESULT_PACKAGED.value,
                    current_run_id=run_id,
                )
            except Exception:
                pass

            try:
                self.lifecycle_manager.transition(
                    job_id=job_id,
                    to_status=JobStatus.RESULT_SENT.value,
                    current_run_id=run_id,
                )
            except Exception:
                pass

            try:
                self.lifecycle_manager.transition(
                    job_id=job_id,
                    to_status=JobStatus.COMPLETED.value,
                    current_run_id=run_id,
                )
            except Exception:
                pass

            self._update_run_reconciled_verdict(run_id, reconciled_verdict)
        elif reconciled_verdict == Verdict.BLOCKED.value:
            try:
                self.lifecycle_manager.transition(
                    job_id=job_id,
                    to_status=JobSideStatus.FAILED.value,
                    current_run_id=run_id,
                    error_summary="Deliverable report evaluated to BLOCKED marker",
                )
            except Exception:
                pass
            self._update_run_reconciled_verdict(run_id, Verdict.BLOCKED.value, error_summary="BLOCKED marker in deliverable")
        else:
            error_msg = f"Reconciliation failed: deliverable verdict is {reconciled_verdict}"
            try:
                self.lifecycle_manager.transition(
                    job_id=job_id,
                    to_status=JobSideStatus.FAILED.value,
                    current_run_id=run_id,
                    error_summary=error_msg,
                )
            except Exception:
                pass
            self._update_run_reconciled_verdict(run_id, reconciled_verdict, error_summary=error_msg)

        if project_id:
            self.lease_coordinator.release_project_lease(project_id, run_id=run_id)

    def _reconcile_run_deliverables(self, tracking: ActiveRunTracking) -> str:
        """Evaluates deliverables across agent records, report files, and logs."""
        run_id = tracking.run_id
        conn, should_close = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT agent_id, status, result_verdict, pid, report_path, stdout_path, stderr_path, exit_code
                FROM agents
                WHERE run_id = ?
                """,
                (run_id,),
            )
            agent_rows = cursor.fetchall()

            if agent_rows:
                agent_verdicts = []
                for ag in agent_rows:
                    ag_id = ag["agent_id"]
                    report_file = Path(ag["report_path"]) if ag["report_path"] else None
                    stdout_file = Path(ag["stdout_path"]) if ag["stdout_path"] else None
                    stderr_file = Path(ag["stderr_path"]) if ag["stderr_path"] else None

                    rep_exists = bool(report_file and report_file.exists())
                    rep_size = report_file.stat().st_size if rep_exists else 0
                    rep_content = report_file.read_text(encoding="utf-8", errors="replace") if rep_exists else None

                    std_content = stdout_file.read_text(encoding="utf-8", errors="replace") if stdout_file and stdout_file.exists() else None
                    err_content = stderr_file.read_text(encoding="utf-8", errors="replace") if stderr_file and stderr_file.exists() else None

                    extraction = extract_verdict_from_content(
                        report_content=rep_content,
                        stdout_content=std_content,
                        stderr_content=err_content,
                        report_exists=rep_exists,
                        report_size_bytes=rep_size,
                        exit_code=ag["exit_code"],
                        persisted_verdict=ag["result_verdict"] if ag["result_verdict"] != "UNKNOWN" else None,
                    )
                    agent_verdicts.append(extraction.verdict)

                    try:
                        cursor.execute(
                            "UPDATE agents SET status = ?, result_verdict = ? WHERE agent_id = ? AND run_id = ?",
                            (
                                "COMPLETE" if extraction.verdict in {Verdict.PASS.value, Verdict.PASS_REPORT_PRESENT.value, Verdict.PARTIAL.value, Verdict.DONE_REVIEW_REQUIRED.value} else "FAILED",
                                extraction.verdict,
                                ag_id,
                                run_id,
                            ),
                        )
                    except Exception:
                        pass

                conn.commit()

                if any(v == Verdict.BLOCKED.value for v in agent_verdicts):
                    return Verdict.BLOCKED.value
                if any(v == Verdict.FAILED.value for v in agent_verdicts):
                    return Verdict.FAILED.value
                if any(v == Verdict.DONE_REVIEW_REQUIRED.value for v in agent_verdicts):
                    return Verdict.DONE_REVIEW_REQUIRED.value
                if any(v == Verdict.PARTIAL.value for v in agent_verdicts):
                    return Verdict.PARTIAL.value
                if all(v in {Verdict.PASS.value, Verdict.PASS_REPORT_PRESENT.value} for v in agent_verdicts):
                    return Verdict.PASS.value

                return Verdict.FAILED.value

            # If no agents recorded, check tracking report_path or run_dir / SUMMARY.md
            candidates = []
            if tracking.report_path:
                candidates.append(Path(tracking.report_path))

            cursor.execute("SELECT run_dir FROM runs WHERE run_id = ?", (run_id,))
            run_row = cursor.fetchone()
            if run_row and run_row["run_dir"]:
                r_dir = Path(run_row["run_dir"])
                candidates.append(r_dir / "SUMMARY.md")
                candidates.append(r_dir / "report.md")

            for cand in candidates:
                if cand.exists() and cand.stat().st_size > 0:
                    content = cand.read_text(encoding="utf-8", errors="replace")
                    extraction = extract_verdict_from_content(
                        report_content=content,
                        report_exists=True,
                        report_size_bytes=cand.stat().st_size,
                        exit_code=0,
                    )
                    return extraction.verdict

            return Verdict.FAILED.value
        finally:
            if should_close:
                conn.close()

    def _update_run_reconciled_verdict(
        self,
        run_id: str,
        verdict: str,
        error_summary: Optional[str] = None,
    ) -> None:
        conn, should_close = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE runs
                SET reconciled_verdict = ?,
                    error_summary = COALESCE(?, error_summary)
                WHERE run_id = ?
                """,
                (verdict, error_summary, run_id),
            )
            conn.commit()
        except sqlite3.OperationalError:
            pass
        finally:
            if should_close:
                conn.close()

    # =========================================================================
    # JOB WAKE SIGNAL
    # =========================================================================

    def wake(self, job_id: Optional[str] = None) -> Optional[str]:
        """Explicit wake signal dispatched from Mail Gateway or Pub/Sub event."""
        if job_id:
            return self.dispatch_job(job_id)
        else:
            self.run_supervisor_tick()
            return None

    # =========================================================================
    # COLD-START CRASH RECOVERY (Never Blindly Restart Old RUNNING)
    # =========================================================================

    def reconcile_startup(self) -> List[str]:
        """Executes the cold-start crash recovery sequence defined in RECOVERY_MODEL.md.

        Inviolable Recovery Invariant:
        Never blindly restart old RUNNING tasks or jobs. Evaluates process observation,
        persisted state, and required outputs before deciding whether to finalize,
        mark INTERRUPTED, or resume.
        """
        # Phase 1: Reclaim singleton lease
        self.lease_coordinator.acquire_singleton_lease(
            holder_id=self.instance_id,
            holder_pid=self.pid,
            ttl_seconds=self.config.singleton_ttl_seconds,
        )

        reconciled_runs: List[str] = []

        conn, should_close = self._get_connection()
        try:
            cursor = conn.cursor()
            # Phase 2: Interrupted Run Discovery
            cursor.execute(
                """
                SELECT run_id, job_id, project_id, status, started_at, run_dir, target_repo_path
                FROM runs
                WHERE status IN ('RUNNING', 'DISPATCHED', 'VERIFYING')
                """
            )
            interrupted_runs = cursor.fetchall()

            for row in interrupted_runs:
                r_id = row["run_id"]
                j_id = row["job_id"]
                p_id = row["project_id"]
                target_repo_path = row["target_repo_path"]

                # 2.1 Local Dirty-Root Safety Rule during recovery
                if self.dispatcher.clean_root_checker and target_repo_path:
                    try:
                        is_clean, dirty_files = self.dispatcher.clean_root_checker(target_repo_path)
                        if not is_clean:
                            err_msg = (
                                f"DIRTY_ROOT_BLOCKS_RECOVERY: Uncommitted modifications detected in primary checkout "
                                f"'{target_repo_path}': {dirty_files[:5]}"
                            )
                            if self.error_recorder:
                                self.error_recorder.record_error(
                                    error_code="DIRTY_ROOT_BLOCKS_RECOVERY",
                                    category="RECOVERY",
                                    severity="FATAL",
                                    message=err_msg,
                                    job_id=j_id,
                                    run_id=r_id,
                                    context={"dirty_files": dirty_files, "target_repo": target_repo_path},
                                )
                            if self.audit_emitter:
                                self.audit_emitter.emit(
                                    event_type=GATE_HALTED,
                                    severity=Severity.FATAL.value,
                                    job_id=j_id,
                                    run_id=r_id,
                                    payload={"reason": err_msg, "dirty_files": dirty_files},
                                )
                            try:
                                self.lifecycle_manager.transition(
                                    job_id=j_id,
                                    to_status=JobSideStatus.BLOCKED.value,
                                    current_run_id=r_id,
                                    error_summary=err_msg,
                                )
                            except Exception:
                                pass
                            if p_id:
                                self.lease_coordinator.release_project_lease(p_id, run_id=r_id)
                            reconciled_runs.append(r_id)
                            continue
                    except Exception:
                        pass

                # Phase 3: Check agents / workers for this run
                cursor.execute(
                    """
                    SELECT agent_id, status, pid, report_path, started_at
                    FROM agents
                    WHERE run_id = ?
                    """,
                    (r_id,),
                )
                agent_rows = cursor.fetchall()

                any_alive = False
                for ag in agent_rows:
                    ag_pid = ag["pid"]
                    if ag_pid and ag_pid > 0 and self.process_checker(ag_pid):
                        any_alive = True
                        break

                if any_alive:
                    # Worker survived; reconnect live supervision
                    started_dt = datetime.now(timezone.utc)
                    if row["started_at"]:
                        try:
                            started_dt = datetime.fromisoformat(row["started_at"].replace("Z", "+00:00"))
                        except Exception:
                            pass
                    self._active_runs[r_id] = ActiveRunTracking(
                        run_id=r_id,
                        job_id=j_id,
                        project_id=p_id,
                        dispatched_at=started_dt,
                    )
                else:
                    # Workers are dead! Check deliverables via 4-point reconciliation
                    tracking = ActiveRunTracking(
                        run_id=r_id,
                        job_id=j_id,
                        project_id=p_id,
                        dispatched_at=datetime.now(timezone.utc),
                    )
                    reconciled_verdict = self._reconcile_run_deliverables(tracking)

                    if reconciled_verdict in {
                        Verdict.PASS.value,
                        Verdict.PARTIAL.value,
                        Verdict.PASS_REPORT_PRESENT.value,
                        Verdict.DONE_REVIEW_REQUIRED.value,
                    }:
                        # Deliverables exist and verified! Finalize the run step-by-step
                        job_record = self.lifecycle_manager.get_job(j_id)
                        current_st = job_record["status"] if job_record else "RUNNING"

                        if current_st == JobStatus.DISPATCHED.value:
                            try:
                                self.lifecycle_manager.transition(j_id, JobStatus.RUNNING.value, current_run_id=r_id)
                                current_st = JobStatus.RUNNING.value
                            except Exception:
                                pass
                        if current_st == JobStatus.RUNNING.value:
                            try:
                                self.lifecycle_manager.transition(j_id, JobStatus.VERIFYING.value, current_run_id=r_id)
                                current_st = JobStatus.VERIFYING.value
                            except Exception:
                                pass
                        if current_st in {JobStatus.VERIFYING.value, JobSideStatus.INTERRUPTED.value}:
                            try:
                                if current_st == JobSideStatus.INTERRUPTED.value:
                                    self.lifecycle_manager.transition(j_id, JobStatus.VERIFYING.value, current_run_id=r_id)
                                self.lifecycle_manager.transition(j_id, JobStatus.RESULT_PACKAGED.value, current_run_id=r_id)
                                self.lifecycle_manager.transition(j_id, JobStatus.RESULT_SENT.value, current_run_id=r_id)
                                self.lifecycle_manager.transition(j_id, JobStatus.COMPLETED.value, current_run_id=r_id)
                            except Exception:
                                pass

                        self._update_run_reconciled_verdict(r_id, reconciled_verdict)
                    else:
                        # Workers dead and deliverables missing/failed:
                        # Inviolable Invariant: NEVER blindly restart old RUNNING
                        job_record = self.lifecycle_manager.get_job(j_id)
                        current_st = job_record["status"] if job_record else "RUNNING"
                        error_msg = "Host supervisor crash detected; workers dead without complete deliverables"

                        if current_st == JobStatus.RUNNING.value:
                            try:
                                self.lifecycle_manager.transition(
                                    job_id=j_id,
                                    to_status=JobSideStatus.INTERRUPTED.value,
                                    current_run_id=r_id,
                                    error_summary=error_msg,
                                )
                            except Exception:
                                pass
                        elif current_st in {JobStatus.DISPATCHED.value, JobStatus.VERIFYING.value}:
                            try:
                                self.lifecycle_manager.transition(
                                    job_id=j_id,
                                    to_status=JobSideStatus.FAILED.value,
                                    current_run_id=r_id,
                                    error_summary=error_msg,
                                )
                            except Exception:
                                pass

                        self._update_run_reconciled_verdict(r_id, Verdict.FAILED.value, error_summary=error_msg)

                    # Release any orphaned project lock
                    if p_id:
                        self.lease_coordinator.release_project_lease(p_id, run_id=r_id)

                reconciled_runs.append(r_id)

            self._is_idle = (len(self._active_runs) == 0)
            if self._state not in {SupervisorState.STOPPED, SupervisorState.STOPPING}:
                self._state = SupervisorState.IDLE if self._is_idle else SupervisorState.RUNNING

            return reconciled_runs
        finally:
            if should_close:
                conn.close()

    # =========================================================================
    # DAEMON LIFECYCLE & OPERATOR SAFE STOP
    # =========================================================================

    def start(self) -> None:
        """Boots the supervisor daemon, claiming singleton lease and reconciling state."""
        self._state = SupervisorState.STARTING
        self._stop_event.clear()
        acquired = self.lease_coordinator.acquire_singleton_lease(
            holder_id=self.instance_id,
            holder_pid=self.pid,
            ttl_seconds=self.config.singleton_ttl_seconds,
            raise_on_failure=True,
        )

        if self.config.enable_crash_recovery_on_start:
            self.reconcile_startup()

        self._emit_liveness_heartbeat()
        self._last_heartbeat_time = time.time()
        self._state = SupervisorState.IDLE if self.is_idle() else SupervisorState.RUNNING

    def run_loop(self, max_ticks: Optional[int] = None) -> None:
        """Main execution polling loop."""
        self.start()
        ticks = 0
        try:
            while not self._stop_event.is_set():
                self.run_supervisor_tick()
                ticks += 1
                if max_ticks and ticks >= max_ticks:
                    break
                self._stop_event.wait(timeout=self.config.poll_interval_seconds)
        finally:
            self.shutdown()

    def shutdown(self, graceful: bool = True) -> None:
        """Initiates controlled graceful operator shutdown."""
        if self._state == SupervisorState.STOPPED:
            return

        self._state = SupervisorState.STOPPING
        self._stop_event.set()

        # Safely handle active runs
        for run_id, tracking in list(self._active_runs.items()):
            if tracking.project_id:
                self.lease_coordinator.release_project_lease(
                    tracking.project_id,
                    run_id=run_id,
                )

        # Release supervisor singleton lease
        self.lease_coordinator.release_singleton_lease(
            holder_id=self.instance_id,
            holder_pid=self.pid,
        )

        # Record final heartbeat with status STOPPED
        if self.heartbeat_service:
            try:
                self.heartbeat_service.record_heartbeat(
                    component="SUPERVISOR",
                    instance_id=self.instance_id,
                    pid=self.pid,
                    status="STOPPED",
                    details={"shutdown_time": datetime.now(timezone.utc).isoformat()},
                )
            except Exception:
                pass

        if self.audit_emitter:
            self.audit_emitter.emit(
                event_type="SUPERVISOR_SHUTDOWN",
                severity=Severity.INFO.value,
                payload={"instance_id": self.instance_id, "pid": self.pid},
            )

        self._active_runs.clear()
        self._is_idle = True
        self._state = SupervisorState.STOPPED

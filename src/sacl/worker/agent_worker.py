"""SACL V1 Agent Worker Execution Coordinator.

Coordinates the complete lifecycle of an individual agent worker process:
- Isolated worktree preparation & prompt assembly
- Process spawning and 3-way PID tracking
- Inviolable non-killing diagnostic timeout (TIMEOUT_RUNNING)
- 4-Part run status reconciliation
- Transient error classification, exponential backoff, and attempt logging
- Safe-stop cancellation protocol
"""

from __future__ import annotations

import os
import sqlite3
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from sacl.contracts.invariants import (
    ALLOWED_PROCESS_IMAGES,
    PID_DRIFT_TOLERANCE_SECONDS,
    AgentStatus,
    GraphNodeStatus,
    Verdict,
)
from sacl.contracts.models import ReconciledResult
from sacl.observability.audit import AuditEventEmitter
from sacl.observability.events import AuditEventType, Severity
from sacl.worker.models import ProcessIdentity, WorkerAttemptRecord, WorkerConfig
from sacl.worker.process import (
    IProcessInspector,
    MockProcessInspector,
    OSProcessInspector,
    safe_stop_agent_process,
    verify_agent_process_running,
)
from sacl.worker.reconciliation_hook import WorkerReconciler
from sacl.worker.retry import (
    calculate_backoff_delay,
    classify_failure,
    get_attempt_log_paths,
)
from sacl.worker.worktree import WorkspaceManager
from sacl.workspace.exceptions import WorkspaceError


class AgentWorker:
    """Manages an agent worker executing within an isolated worktree."""

    def __init__(
        self,
        config: WorkerConfig,
        db_conn: Optional[sqlite3.Connection] = None,
        audit_emitter: Optional[AuditEventEmitter] = None,
        workspace_manager: Optional[WorkspaceManager] = None,
        process_inspector: Optional[IProcessInspector] = None,
        reconciler: Optional[WorkerReconciler] = None,
    ) -> None:
        self.config = config
        self.db_conn = db_conn
        self.audit_emitter = audit_emitter
        self.workspace_manager = workspace_manager or WorkspaceManager()
        self.process_inspector = process_inspector or OSProcessInspector()
        self.reconciler = reconciler or WorkerReconciler(db_conn=db_conn)

        # State tracking
        self.current_attempt: int = 0
        self.status: str = AgentStatus.SCHEDULED.value
        self.result_verdict: str = Verdict.UNKNOWN.value
        self.pid: Optional[int] = None
        self.started_at: Optional[datetime] = None
        self.finished_at: Optional[datetime] = None
        self.exit_code: Optional[int] = None
        self.error_message: Optional[str] = None
        self.start_monotonic: Optional[float] = None
        self.is_timed_out: bool = False
        self.active_process: Optional[subprocess.Popen[Any]] = None
        self.attempt_records: List[WorkerAttemptRecord] = []
        self.latest_reconciled_result: Optional[ReconciledResult] = None

        # Current attempt paths
        self.active_stdout_path = self.config.stdout_path
        self.active_stderr_path = self.config.stderr_path
        self.active_report_path = self.config.report_path

    def _persist_agent_state(self) -> None:
        """Persists agent state in SQLite agents table."""
        if not self.db_conn:
            return

        now_iso = datetime.now(timezone.utc).isoformat()
        started_iso = self.started_at.isoformat() if self.started_at else None
        finished_iso = self.finished_at.isoformat() if self.finished_at else None

        sql = """
            INSERT INTO agents (
                agent_id, run_id, stage_id, node_id, status, result_verdict,
                pid, branch, commit_sha, worktree_path, prompt_path,
                report_path, stdout_path, stderr_path, started_at,
                updated_at, finished_at, exit_code, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(agent_id, run_id) DO UPDATE SET
                status = excluded.status,
                result_verdict = excluded.result_verdict,
                pid = excluded.pid,
                branch = excluded.branch,
                worktree_path = excluded.worktree_path,
                stdout_path = excluded.stdout_path,
                stderr_path = excluded.stderr_path,
                report_path = excluded.report_path,
                started_at = COALESCE(agents.started_at, excluded.started_at),
                updated_at = excluded.updated_at,
                finished_at = excluded.finished_at,
                exit_code = excluded.exit_code,
                error_message = excluded.error_message;
        """
        try:
            self.db_conn.execute(
                sql,
                (
                    self.config.agent_id,
                    self.config.run_id,
                    self.config.phase_number,
                    self.config.node_id or self.config.agent_id,
                    self.status,
                    self.result_verdict,
                    self.pid,
                    self.config.branch,
                    None,  # commit_sha
                    str(self.config.worktree_path),
                    str(self.config.prompt_path),
                    str(self.active_report_path),
                    str(self.active_stdout_path),
                    str(self.active_stderr_path),
                    started_iso,
                    now_iso,
                    finished_iso,
                    self.exit_code,
                    self.error_message,
                ),
            )
            self.db_conn.commit()
        except Exception:
            pass

    def _persist_attempt_record(self, record: WorkerAttemptRecord) -> None:
        """Persists attempt in SQLite node_attempts table."""
        if not self.db_conn:
            return

        sql = """
            INSERT INTO node_attempts (
                run_id, node_id, attempt_number, pid, status, exit_code,
                started_at, finished_at, verdict, error_message,
                stdout_path, stderr_path, report_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        try:
            self.db_conn.execute(
                sql,
                (
                    self.config.run_id,
                    self.config.node_id or self.config.agent_id,
                    record.attempt_number,
                    record.pid,
                    record.status,
                    record.exit_code,
                    record.started_at,
                    record.finished_at,
                    record.verdict,
                    record.error_message,
                    record.stdout_path,
                    record.stderr_path,
                    record.report_path,
                ),
            )
            self.db_conn.commit()
        except Exception:
            pass

    def _emit_event(self, event_type: str, severity: str, payload: Dict[str, Any]) -> None:
        """Emits audit event if emitter is present."""
        if self.audit_emitter:
            try:
                self.audit_emitter.emit(
                    event_type=event_type,
                    severity=severity,
                    payload=payload,
                    run_id=self.config.run_id,
                    job_id=self.config.job_id,
                    agent_id=self.config.agent_id,
                    node_id=self.config.node_id or self.config.agent_id,
                )
            except Exception:
                pass

    def launch_attempt(self) -> None:
        """Launches a new execution attempt."""
        # An explicitly provided mock runner or a mock inspector without a
        # command is never an OS spawn. Every other launch must already live
        # in a registered, protected-branch-safe Git worktree.
        is_mock_process = (
            self.config.mock_runner is not None
            or (isinstance(self.process_inspector, MockProcessInspector)
                and not self.config.executable_command)
        )
        worktree_identity = None
        if not is_mock_process:
            self.workspace_manager.assert_registered_worktree(
                self.config.worktree_path, expected_branch=self.config.branch,
            )
            # Capture directory identity to detect replacement during log preparation.
            stat = self.config.worktree_path.stat()
            worktree_identity = (stat.st_dev, stat.st_ino)
        self.current_attempt += 1
        self.status = AgentStatus.LAUNCHING.value

        # Resolve distinct paths for attempts > 1
        out_p, err_p, rep_p = get_attempt_log_paths(
            self.config.stdout_path,
            self.config.stderr_path,
            self.config.report_path,
            self.current_attempt,
        )
        self.active_stdout_path = out_p
        self.active_stderr_path = err_p
        self.active_report_path = rep_p

        # Ensure parent directories exist
        self.active_stdout_path.parent.mkdir(parents=True, exist_ok=True)
        self.active_stderr_path.parent.mkdir(parents=True, exist_ok=True)
        self.active_report_path.parent.mkdir(parents=True, exist_ok=True)

        self.started_at = datetime.now(timezone.utc)
        self.start_monotonic = time.monotonic()
        self.finished_at = None
        self.exit_code = None
        self.is_timed_out = False

        self._persist_agent_state()

        # If a mock runner is provided, execute via mock runner
        if self.config.mock_runner:
            self.status = AgentStatus.RUNNING.value
            self.pid = 9000 + self.current_attempt
            self._persist_agent_state()
            self._emit_event(
                AuditEventType.PROCESS_SPAWNED.value,
                Severity.INFO.value,
                {"pid": self.pid, "attempt": self.current_attempt, "mode": "MOCK"},
            )
            try:
                exit_code, err = self.config.mock_runner(self.config, self.current_attempt)
                self.handle_process_exit(exit_code=exit_code, error_message=err)
            except Exception as e:
                self.handle_process_exit(exit_code=1, error_message=str(e))
            return

        # Only explicit mocked workers may create synthetic plain directories.
        # Live worker worktrees are provisioned and verified by the manager.
        if is_mock_process:
            self.config.worktree_path.mkdir(parents=True, exist_ok=True)

        # If using MockProcessInspector without an explicit command, simulate process
        if isinstance(self.process_inspector, MockProcessInspector) and not self.config.executable_command:
            self.status = AgentStatus.RUNNING.value
            self.pid = 9000 + self.current_attempt
            self.process_inspector.register_process(self.pid, "agy", self.started_at, is_running=True)
            self._persist_agent_state()
            self._emit_event(
                AuditEventType.PROCESS_SPAWNED.value,
                Severity.INFO.value,
                {"pid": self.pid, "attempt": self.current_attempt, "mode": "MOCK_INSPECTOR"},
            )
            return

        # Real process launch
        cmd = self.config.executable_command or ["agy.exe"]
        env = os.environ.copy()
        env.update(self.config.env_overrides)

        try:
            stdout_file = open(self.active_stdout_path, "w", encoding="utf-8")
            stderr_file = open(self.active_stderr_path, "w", encoding="utf-8")

            # Recheck after launch preparation and before process creation.
            # This narrows but does not eliminate OS-level TOCTOU.
            if not is_mock_process:
                self.workspace_manager.assert_registered_worktree(
                    self.config.worktree_path, expected_branch=self.config.branch,
                )
                stat = self.config.worktree_path.stat()
                if (stat.st_dev, stat.st_ino) != worktree_identity:
                    raise WorkspaceError(
                        "Worktree identity changed between preflight and process spawn."
                    )

            proc = subprocess.Popen(
                cmd,
                cwd=str(self.config.worktree_path),
                stdout=stdout_file,
                stderr=stderr_file,
                env=env,
            )
            self.active_process = proc
            self.pid = proc.pid
            self.status = AgentStatus.RUNNING.value

            self._persist_agent_state()
            self._emit_event(
                AuditEventType.PROCESS_SPAWNED.value,
                Severity.INFO.value,
                {"pid": self.pid, "command": cmd, "attempt": self.current_attempt},
            )
        except Exception as e:
            self.error_message = f"Process spawn failed: {str(e)}"
            self.status = AgentStatus.FAILED.value
            self.handle_process_exit(exit_code=1, error_message=self.error_message)

    def check_liveness_and_timeout(self) -> Tuple[bool, str]:
        """Polls worker execution state: checks liveness and non-killing timeout.

        Returns:
            (is_still_running, current_status)
        """
        if self.status in {
            AgentStatus.COMPLETE.value,
            AgentStatus.FAILED.value,
            AgentStatus.STOPPED.value,
        }:
            return False, self.status

        # 1. Non-killing timeout check
        if self.start_monotonic is not None:
            elapsed = time.monotonic() - self.start_monotonic
            if elapsed >= self.config.timeout_seconds and not self.is_timed_out:
                self.is_timed_out = True
                self.status = AgentStatus.TIMEOUT_RUNNING.value
                self._persist_agent_state()
                self._emit_event(
                    AuditEventType.TIMEOUT_DETECTED.value,
                    Severity.WARN.value,
                    {
                        "pid": self.pid,
                        "elapsed_seconds": elapsed,
                        "timeout_seconds": self.config.timeout_seconds,
                        "invariant": "NON_KILLING_PRESERVE_FORENSICS",
                    },
                )

        # 2. Process exit check
        if self.active_process:
            ret = self.active_process.poll()
            if ret is not None:
                self.handle_process_exit(exit_code=ret)
                return False, self.status
            return True, self.status

        # If pid is known but no popen object, verify via inspector
        if self.pid and self.pid > 0:
            is_alive, reason, drift, name = verify_agent_process_running(
                pid=self.pid,
                expected_start_time=self.started_at,
                inspector=self.process_inspector,
            )
            if not is_alive:
                self.handle_process_exit(exit_code=0 if is_alive else None)
                return False, self.status
            return True, self.status

        return False, self.status

    def handle_process_exit(
        self,
        exit_code: Optional[int] = 0,
        error_message: Optional[str] = None,
    ) -> ReconciledResult:
        """Executes 4-pillar reconciliation upon process termination."""
        self.finished_at = datetime.now(timezone.utc)
        self.exit_code = exit_code
        if error_message:
            self.error_message = error_message

        # Reconcile across 4 pillars
        result = self.reconciler.reconcile(
            run_id=self.config.run_id,
            agent_id=self.config.agent_id,
            pid=self.pid,
            process_name="agy",
            is_active=False,
            exit_code=exit_code,
            persisted_start_time=self.started_at.isoformat() if self.started_at else None,
            actual_start_time=self.started_at,
            persisted_status=self.status,
            report_path=self.active_report_path,
            stdout_path=self.active_stdout_path,
            stderr_path=self.active_stderr_path,
            worktree_path=self.config.worktree_path,
            job_id=self.config.job_id,
            node_id=self.config.node_id or self.config.agent_id,
            stage_id=self.config.phase_number,
            branch=self.config.branch,
            error_message=self.error_message,
        )

        self.latest_reconciled_result = result
        self.result_verdict = result.result_verdict

        # Record attempt
        attempt_rec = WorkerAttemptRecord(
            attempt_number=self.current_attempt,
            started_at=self.started_at.isoformat() if self.started_at else "",
            finished_at=self.finished_at.isoformat(),
            stdout_path=str(self.active_stdout_path),
            stderr_path=str(self.active_stderr_path),
            report_path=str(self.active_report_path),
            pid=self.pid,
            status=result.status,
            exit_code=exit_code,
            verdict=result.result_verdict,
            error_message=result.error_message,
        )
        self.attempt_records.append(attempt_rec)
        self._persist_attempt_record(attempt_rec)

        # Check retryability
        if result.status == "FAILED" and self.current_attempt < self.config.max_attempts:
            is_retryable, class_code, max_retries = classify_failure(
                error=self.error_message,
                verdict=result.result_verdict,
                exit_code=exit_code,
            )
            if is_retryable:
                self.status = AgentStatus.RETRYABLE_FAILURE.value
                self._persist_agent_state()
                self._emit_event(
                    AuditEventType.STATUS_CHANGE.value,
                    Severity.INFO.value,
                    {
                        "transition": f"{AgentStatus.RUNNING.value} -> {AgentStatus.RETRYABLE_FAILURE.value}",
                        "attempt": self.current_attempt,
                        "classification": class_code,
                    },
                )
                return result

        # Terminal state
        if result.status in {"SUCCEEDED", "COMPLETE"}:
            self.status = AgentStatus.COMPLETE.value
        elif result.status == "BLOCKED":
            self.status = AgentStatus.BLOCKED.value
        else:
            self.status = AgentStatus.FAILED.value

        self._persist_agent_state()
        self._emit_event(
            AuditEventType.STATUS_CHANGE.value,
            Severity.INFO.value,
            {
                "status": self.status,
                "verdict": self.result_verdict,
                "attempt": self.current_attempt,
            },
        )
        return result

    def stop_safely(self, force: bool = True) -> Tuple[bool, str, Dict[str, Any]]:
        """Executes safe-stop protocol for this worker."""
        if not self.pid or self.pid <= 0:
            self.status = AgentStatus.STOPPED.value
            self.result_verdict = Verdict.STOPPED_BY_USER.value
            self._persist_agent_state()
            return True, "ALREADY_DEAD", {"pid": self.pid}

        success, code, details = safe_stop_agent_process(
            pid=self.pid,
            expected_start_time=self.started_at,
            force=force,
            inspector=self.process_inspector,
        )

        if code == "STOPPED_BY_USER" or code == "ALREADY_DEAD":
            self.status = AgentStatus.STOPPED.value
            self.result_verdict = Verdict.STOPPED_BY_USER.value
            self.finished_at = datetime.now(timezone.utc)
            self._persist_agent_state()
            self._emit_event(
                AuditEventType.STOPPED_BY_USER.value,
                Severity.WARN.value,
                {"pid": self.pid, "safe_stop": True},
            )
        elif "SAFETY_REFUSAL" in code:
            self.status = AgentStatus.UNKNOWN.value
            self._persist_agent_state()
            self._emit_event(
                AuditEventType.PID_RECYCLED_DETECTED.value,
                Severity.ERROR.value,
                details,
            )

        return success, code, details

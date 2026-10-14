"""SACL V1 Supervisor Cold-Start Recovery & Startup Reconciliation Engine.

Implements docs/RECOVERY_MODEL.md §3:
Executes the deterministic 3-phase cold-start recovery sequence:
- Phase 1: Stale Lock Detection & Lease Reclamation (SUPERVISOR_SINGLETON).
- Phase 2: Interrupted Run Discovery (runs in RUNNING, DISPATCHED, VERIFYING, QUEUED).
- Phase 3: 4-Point Orphan Worker Reconciliation Loop & Safe-to-Resume.
- Phase 4: Orphaned Worktree Inspection & Local Dirty-Root Safety.
"""

from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from sacl.contracts.interfaces import IRecoveryManager
from sacl.observability.events import (
    AuditEventType,
    create_audit_event,
)
from sacl.recovery.interrupted import (
    InterruptedRunRecoveryReport,
    find_interrupted_runs,
    recover_interrupted_run,
)
from sacl.recovery.process_identity import (
    MockProcessInspector,
    ProcessInspectionStatus,
    ProcessInspector,
    get_default_process_inspector,
    inspect_process,
)
from sacl.recovery.safe_to_resume import SafeToResumeOutcome
from sacl.recovery.worktree_inspection import (
    GitClient,
    OrphanedWorktreeInfo,
    get_default_git_client,
    scan_orphaned_worktrees,
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_now_iso() -> str:
    return _utc_now().isoformat()


@dataclass
class StartupReconciliationReport:
    """Consolidated summary of the entire cold-start recovery sequence."""

    supervisor_pid: int
    lease_acquired: bool
    stale_lock_reclaimed: bool
    active_supervisor_conflict: bool
    supervisor_state: str  # IDLE, SUPERVISION_RESUMED, RECONCILED, HALTED_SAFETY, BLOCKED_REVIEW
    interrupted_runs_count: int
    run_reports: List[InterruptedRunRecoveryReport] = field(default_factory=list)
    orphaned_worktrees: List[OrphanedWorktreeInfo] = field(default_factory=list)
    messages: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "supervisor_pid": self.supervisor_pid,
            "lease_acquired": self.lease_acquired,
            "stale_lock_reclaimed": self.stale_lock_reclaimed,
            "active_supervisor_conflict": self.active_supervisor_conflict,
            "supervisor_state": self.supervisor_state,
            "interrupted_runs_count": self.interrupted_runs_count,
            "run_reports": [r.to_dict() for r in self.run_reports],
            "orphaned_worktrees": [
                {
                    "directory_path": o.directory_path,
                    "classification": o.classification.value,
                    "is_clean": o.is_clean,
                    "modified_files": o.modified_files,
                }
                for o in self.orphaned_worktrees
            ],
            "messages": list(self.messages),
            "errors": list(self.errors),
        }


class StartupReconciliationEngine(IRecoveryManager):
    """Orchestrates cold-start recovery, lease acquisition, and interrupted run handling."""

    def __init__(
        self,
        db_source: Union[sqlite3.Connection, Path, str],
        supervisor_pid: Optional[int] = None,
        lease_ttl_seconds: int = 60,
        inspector: Optional[ProcessInspector] = None,
        git_client: Optional[GitClient] = None,
    ) -> None:
        self.db_source = db_source
        self.supervisor_pid = supervisor_pid or os.getpid()
        self.lease_ttl_seconds = lease_ttl_seconds
        self.inspector = inspector or get_default_process_inspector()
        self.git_client = git_client or get_default_git_client()

    def _get_connection(self) -> sqlite3.Connection:
        if isinstance(self.db_source, sqlite3.Connection):
            return self.db_source
        conn = sqlite3.connect(str(self.db_source))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA busy_timeout = 5000;")
        return conn

    def reconcile_startup(self) -> List[str]:
        """Detects and reconciles INTERRUPTED runs from prior host crash."""
        report = self.execute_startup_reconciliation()
        return report.messages

    def check_pid_safety(self, pid: int, recorded_start_time: str) -> bool:
        """Verifies process identity to prevent interacting with recycled PIDs."""
        res = inspect_process(pid=pid, expected_start_time=recorded_start_time, inspector=self.inspector)
        # A matching process must also have an observable start-time drift:
        # unknown process creation times cannot establish PID identity.
        return (
            res.status == ProcessInspectionStatus.ALIVE_VALID
            and res.is_alive
            and res.is_valid
            and res.observation.start_time_drift_seconds is not None
        )

    def execute_startup_reconciliation(
        self,
        worktree_base_dir: Optional[Union[Path, str]] = None,
    ) -> StartupReconciliationReport:
        """Executes the full 3-phase cold-start recovery sequence."""
        conn = self._get_connection()
        messages: List[str] = []
        errors: List[str] = []

        now_dt = _utc_now()
        now_iso = now_dt.isoformat()
        expires_dt = now_dt + timedelta(seconds=self.lease_ttl_seconds)
        expires_iso = expires_dt.isoformat()

        # ====================================================================
        # Phase 1: Stale Lock Detection & Lease Reclamation
        # ====================================================================
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM leases WHERE lease_name = 'SUPERVISOR_SINGLETON';
            """
        )
        lease_row = cursor.fetchone()

        lease_acquired = False
        stale_lock_reclaimed = False
        active_conflict = False

        if lease_row:
            holder_pid = lease_row["holder_pid"]
            holder_expires = lease_row["expires_at"]

            # If it's already held by our own PID, renew it
            if holder_pid == self.supervisor_pid:
                lease_acquired = True
                self._update_lease(conn, self.supervisor_pid, now_iso, expires_iso)
                messages.append(f"Renewed existing SUPERVISOR_SINGLETON lease for PID {self.supervisor_pid}.")
            else:
                # 3-Way check on holder process using lease acquired_at timestamp
                holder_obs = inspect_process(
                    pid=holder_pid,
                    persisted_start_time=lease_row["acquired_at"],
                    inspector=self.inspector,
                )

                if holder_obs.is_alive and holder_obs.is_valid:
                    # Active supervisor is legitimately running!
                    active_conflict = True
                    msg = (
                        f"SUPERVISOR_ALREADY_ACTIVE: Another supervisor process (PID {holder_pid}, "
                        f"image '{holder_obs.observation.process_name}') is actively holding "
                        f"the SUPERVISOR_SINGLETON lease. Cold start aborted."
                    )
                    errors.append(msg)
                    return StartupReconciliationReport(
                        supervisor_pid=self.supervisor_pid,
                        lease_acquired=False,
                        stale_lock_reclaimed=False,
                        active_supervisor_conflict=True,
                        supervisor_state="HALTED_SAFETY",
                        interrupted_runs_count=0,
                        messages=messages,
                        errors=errors,
                    )
                else:
                    # Holder process is dead or PID recycled -> Reclaim stale lease!
                    stale_lock_reclaimed = True
                    reason = holder_obs.failure_reason or "Holder process terminated"
                    messages.append(
                        f"STALE_LOCK_RECLAIMED: Reclaimed orphaned lease from defunct PID {holder_pid} ({reason})."
                    )

                    with conn:
                        conn.execute(
                            """
                            INSERT INTO events (event_type, severity, payload_json, created_at)
                            VALUES ('STALE_LOCK_RECLAIMED', 'INFO', ?, ?);
                            """,
                            (str({"previous_holder_pid": holder_pid, "reason": reason}), now_iso),
                        )

                    self._update_lease(conn, self.supervisor_pid, now_iso, expires_iso)
                    lease_acquired = True
        else:
            # Lease doesn't exist yet -> Claim fresh lease
            self._insert_lease(conn, self.supervisor_pid, now_iso, expires_iso)
            lease_acquired = True
            messages.append(f"Acquired new SUPERVISOR_SINGLETON lease for PID {self.supervisor_pid}.")

        # Collect all registered worktree paths from DB for orphan detection
        registered_worktree_paths: Set[str] = set()
        cursor.execute("SELECT worktree_path FROM agents WHERE worktree_path IS NOT NULL;")
        for row in cursor.fetchall():
            if row["worktree_path"]:
                registered_worktree_paths.add(row["worktree_path"])

        # ====================================================================
        # Phase 4: Orphaned Worktree Inspection
        # ====================================================================
        orphaned_wts: List[OrphanedWorktreeInfo] = []
        if worktree_base_dir:
            orphaned_wts = scan_orphaned_worktrees(
                worktree_base_dir=worktree_base_dir,
                registered_worktree_paths=registered_worktree_paths,
                git_client=self.git_client,
            )
            if orphaned_wts:
                messages.append(
                    f"Discovered {len(orphaned_wts)} orphaned worktree directory(ies) on disk. "
                    f"Preserved for forensic inspection under Local Dirty-Root Rule."
                )

        # ====================================================================
        # Phase 2: Interrupted Run Discovery
        # ====================================================================
        interrupted_runs = find_interrupted_runs(conn)
        interrupted_count = len(interrupted_runs)

        if interrupted_count == 0:
            messages.append("No interrupted runs discovered. Supervisor entering IDLE state.")
            return StartupReconciliationReport(
                supervisor_pid=self.supervisor_pid,
                lease_acquired=lease_acquired,
                stale_lock_reclaimed=stale_lock_reclaimed,
                active_supervisor_conflict=False,
                supervisor_state="IDLE",
                interrupted_runs_count=0,
                run_reports=[],
                orphaned_worktrees=orphaned_wts,
                messages=messages,
                errors=errors,
            )

        messages.append(f"Discovered {interrupted_count} interrupted run(s) requiring reconciliation.")

        # ====================================================================
        # Phase 3: 4-Point Orphan Worker Reconciliation Loop
        # ====================================================================
        run_reports: List[InterruptedRunRecoveryReport] = []

        for run_row in interrupted_runs:
            report = recover_interrupted_run(
                run_row=run_row,
                conn=conn,
                inspector=self.inspector,
                git_client=self.git_client,
            )
            run_reports.append(report)

        # Determine supervisor final state
        has_dirty_root = any(r.dirty_root_halted for r in run_reports)
        has_surviving = any(
            r.run_decision.outcome == SafeToResumeOutcome.RESUME_SUPERVISION
            for r in run_reports
        )
        has_review = any(
            r.run_decision.outcome == SafeToResumeOutcome.BLOCKED_RECOVERY_REVIEW
            for r in run_reports
        )

        if has_dirty_root:
            sup_state = "HALTED_SAFETY"
        elif has_surviving:
            sup_state = "SUPERVISION_RESUMED"
        elif has_review:
            sup_state = "BLOCKED_REVIEW"
        else:
            sup_state = "RECONCILED"

        return StartupReconciliationReport(
            supervisor_pid=self.supervisor_pid,
            lease_acquired=lease_acquired,
            stale_lock_reclaimed=stale_lock_reclaimed,
            active_supervisor_conflict=False,
            supervisor_state=sup_state,
            interrupted_runs_count=interrupted_count,
            run_reports=run_reports,
            orphaned_worktrees=orphaned_wts,
            messages=messages,
            errors=errors,
        )

    def _insert_lease(
        self,
        conn: sqlite3.Connection,
        pid: int,
        acquired_at: str,
        expires_at: str,
    ) -> None:
        with conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO leases (
                    lease_name, holder_id, holder_pid, acquired_at, heartbeat_at, expires_at, metadata_json
                ) VALUES ('SUPERVISOR_SINGLETON', 'SUPERVISOR', ?, ?, ?, ?, ?);
                """,
                (pid, acquired_at, acquired_at, expires_at, str({"component": "SUPERVISOR"})),
            )
            conn.execute(
                """
                INSERT OR REPLACE INTO supervisor_locks (
                    lock_name, run_id, holder_pid, acquired_at, heartbeat_at, expires_at
                ) VALUES ('SUPERVISOR_SINGLETON', 'SUPERVISOR', ?, ?, ?, ?);
                """,
                (pid, acquired_at, acquired_at, expires_at),
            )
            conn.execute(
                """
                INSERT INTO events (event_type, severity, payload_json, created_at)
                VALUES (?, 'INFO', ?, ?);
                """,
                (AuditEventType.LEASE_ACQUIRED.value, str({"lease_name": "SUPERVISOR_SINGLETON", "pid": pid}), acquired_at),
            )

    def _update_lease(
        self,
        conn: sqlite3.Connection,
        pid: int,
        heartbeat_at: str,
        expires_at: str,
    ) -> None:
        with conn:
            conn.execute(
                """
                UPDATE leases
                SET holder_pid = ?,
                    heartbeat_at = ?,
                    expires_at = ?
                WHERE lease_name = 'SUPERVISOR_SINGLETON';
                """,
                (pid, heartbeat_at, expires_at),
            )
            conn.execute(
                """
                UPDATE supervisor_locks
                SET holder_pid = ?,
                    heartbeat_at = ?,
                    expires_at = ?
                WHERE lock_name = 'SUPERVISOR_SINGLETON';
                """,
                (pid, heartbeat_at, expires_at),
            )

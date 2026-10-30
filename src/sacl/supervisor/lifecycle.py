"""SACL V1 Canonical Job Lifecycle Transitions Subsystem.

Implements the mandatory canonical job lifecycle defined in:
- DECISION_BASELINE.md (Decision #20, Item SB-FREEZE-P1-04)
- docs/STATE_MACHINE.md §3 (12 Primary States + 10 Side States)
- contracts/architecture-invariants.json

Validates state transition guards, updates SQLite relational tables, and
coordinates automatic lease cleanup upon reaching terminal outcomes.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, FrozenSet, List, Optional, Tuple, Union

from sacl.contracts.exceptions import ArchitectureInvariantError
from sacl.contracts.invariants import (
    ALL_JOB_STATES,
    JobSideStatus,
    JobStatus,
)
from sacl.observability.events import (
    AuditEventType,
    Severity,
)
from sacl.supervisor.lease import LeaseCoordinator

STATUS_CHANGE = AuditEventType.STATUS_CHANGE.value

# =============================================================================
# CANONICAL JOB TRANSITION MATRIX (STATE_MACHINE.md §3.3)
# =============================================================================

VALID_JOB_TRANSITIONS: Dict[str, FrozenSet[str]] = {
    JobStatus.RECEIVED.value: frozenset(
        {
            JobStatus.AUTHENTICATED.value,
            JobSideStatus.REJECTED.value,
            JobSideStatus.QUARANTINED.value,
        }
    ),
    JobStatus.AUTHENTICATED.value: frozenset(
        {
            JobStatus.VALIDATED.value,
            JobSideStatus.REJECTED.value,
        }
    ),
    JobStatus.VALIDATED.value: frozenset(
        {
            JobStatus.PERSISTED.value,
            JobSideStatus.REJECTED.value,
            JobSideStatus.POLICY_DENIED.value,
        }
    ),
    JobStatus.PERSISTED.value: frozenset(
        {
            JobStatus.QUEUED.value,
            JobSideStatus.POLICY_DENIED.value,
            JobSideStatus.BLOCKED.value,
        }
    ),
    JobStatus.QUEUED.value: frozenset(
        {
            JobStatus.DISPATCHED.value,
            JobSideStatus.CANCELLED.value,
            JobSideStatus.BLOCKED.value,
            JobSideStatus.POLICY_DENIED.value,
        }
    ),
    JobStatus.DISPATCHED.value: frozenset(
        {
            JobStatus.RUNNING.value,
            JobSideStatus.FAILED.value,
            JobSideStatus.CANCELLED.value,
        }
    ),
    JobStatus.RUNNING.value: frozenset(
        {
            JobStatus.VERIFYING.value,
            JobSideStatus.WAITING_APPROVAL.value,
            JobSideStatus.RETRY_WAIT.value,
            JobSideStatus.BLOCKED.value,
            JobSideStatus.FAILED.value,
            JobSideStatus.CANCELLED.value,
            JobSideStatus.INTERRUPTED.value,
            JobSideStatus.TIMED_OUT.value,
        }
    ),
    JobSideStatus.WAITING_APPROVAL.value: frozenset(
        {
            JobStatus.RUNNING.value,
            JobSideStatus.BLOCKED.value,
            JobSideStatus.CANCELLED.value,
        }
    ),
    JobSideStatus.RETRY_WAIT.value: frozenset(
        {
            JobStatus.RUNNING.value,
            JobSideStatus.FAILED.value,
            JobSideStatus.CANCELLED.value,
        }
    ),
    JobStatus.VERIFYING.value: frozenset(
        {
            JobStatus.RESULT_PACKAGED.value,
            JobSideStatus.FAILED.value,
        }
    ),
    JobStatus.RESULT_PACKAGED.value: frozenset(
        {
            JobStatus.RESULT_SENT.value,
            JobSideStatus.FAILED.value,
        }
    ),
    JobStatus.RESULT_SENT.value: frozenset(
        {
            JobStatus.COMPLETED.value,
            JobSideStatus.FAILED.value,
        }
    ),
    JobStatus.COMPLETED.value: frozenset(
        {
            JobStatus.ARCHIVED.value,
        }
    ),
    JobSideStatus.FAILED.value: frozenset(
        {
            JobStatus.ARCHIVED.value,
        }
    ),
    JobSideStatus.CANCELLED.value: frozenset(
        {
            JobStatus.ARCHIVED.value,
        }
    ),
    JobSideStatus.INTERRUPTED.value: frozenset(
        {
            JobStatus.VERIFYING.value,
            JobSideStatus.FAILED.value,
        }
    ),
    JobSideStatus.TIMED_OUT.value: frozenset(
        {
            JobStatus.ARCHIVED.value,
            JobSideStatus.FAILED.value,
        }
    ),
    JobSideStatus.BLOCKED.value: frozenset(
        {
            JobStatus.ARCHIVED.value,
            JobStatus.QUEUED.value,
            JobStatus.RUNNING.value,
        }
    ),
    JobSideStatus.POLICY_DENIED.value: frozenset(
        {
            JobStatus.ARCHIVED.value,
        }
    ),
    JobSideStatus.REJECTED.value: frozenset(
        {
            JobStatus.ARCHIVED.value,
        }
    ),
    JobSideStatus.QUARANTINED.value: frozenset(
        {
            JobStatus.ARCHIVED.value,
        }
    ),
    JobStatus.ARCHIVED.value: frozenset(),  # Terminal sink state
}

TERMINAL_JOB_STATES: FrozenSet[str] = frozenset(
    {
        JobStatus.COMPLETED.value,
        JobStatus.ARCHIVED.value,
        JobSideStatus.FAILED.value,
        JobSideStatus.CANCELLED.value,
        JobSideStatus.POLICY_DENIED.value,
        JobSideStatus.REJECTED.value,
        JobSideStatus.QUARANTINED.value,
        JobSideStatus.TIMED_OUT.value,
    }
)

RELEASE_LEASE_STATES: FrozenSet[str] = TERMINAL_JOB_STATES | frozenset(
    {
        JobSideStatus.BLOCKED.value,
        JobSideStatus.INTERRUPTED.value,
    }
)


class JobLifecycleManager:
    """Enforces canonical state transitions across jobs and runs tables."""

    def __init__(
        self,
        db_source: Union[sqlite3.Connection, Path, str, Callable[[], sqlite3.Connection]],
        lease_coordinator: Optional[LeaseCoordinator] = None,
        audit_emitter: Optional[Any] = None,
    ):
        self._db_source = db_source
        self._db_file: Optional[str] = None
        self.lease_coordinator = lease_coordinator
        self.audit_emitter = audit_emitter

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

    # =========================================================================
    # QUERY INTERFACES
    # =========================================================================

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a job record by ID."""
        conn, should_close = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT job_id, package_id, project_id, status, priority,
                       created_at, updated_at, completed_at, current_run_id,
                       error_summary, metadata_json
                FROM jobs WHERE job_id = ?
                """,
                (job_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None
            res = dict(row)
            if res.get("metadata_json"):
                try:
                    res["metadata"] = json.loads(res["metadata_json"])
                except Exception:
                    res["metadata"] = {}
            else:
                res["metadata"] = {}
            return res
        finally:
            if should_close:
                conn.close()

    def get_queued_jobs(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Returns pending jobs ready for supervisor dispatch, ordered by priority."""
        conn, should_close = self._get_connection()
        try:
            cursor = conn.cursor()
            query = (
                "SELECT job_id, package_id, project_id, status, priority, "
                "created_at, updated_at, completed_at, current_run_id, "
                "error_summary, metadata_json "
                "FROM jobs WHERE status = 'QUEUED' ORDER BY priority DESC, created_at ASC"
            )
            if limit:
                query += f" LIMIT {int(limit)}"
            cursor.execute(query)
            rows = cursor.fetchall()
            jobs = []
            for r in rows:
                item = dict(r)
                if item.get("metadata_json"):
                    try:
                        item["metadata"] = json.loads(item["metadata_json"])
                    except Exception:
                        item["metadata"] = {}
                else:
                    item["metadata"] = {}
                jobs.append(item)
            return jobs
        finally:
            if should_close:
                conn.close()

    def get_active_jobs(self) -> List[Dict[str, Any]]:
        """Returns jobs currently in active flight (DISPATCHED, RUNNING, VERIFYING, etc.)."""
        conn, should_close = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT job_id, package_id, project_id, status, priority,
                       created_at, updated_at, completed_at, current_run_id,
                       error_summary, metadata_json
                FROM jobs
                WHERE status IN ('DISPATCHED', 'RUNNING', 'VERIFYING', 'RESULT_PACKAGED', 'RESULT_SENT')
                ORDER BY updated_at DESC
                """
            )
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
        finally:
            if should_close:
                conn.close()

    # =========================================================================
    # JOB CREATION
    # =========================================================================

    def create_job(
        self,
        job_id: str,
        package_id: Optional[str] = None,
        project_id: Optional[str] = None,
        status: Union[str, JobStatus] = JobStatus.RECEIVED.value,
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Creates an initial job record."""
        status_str = status.value if isinstance(status, (JobStatus, JobSideStatus)) else str(status)
        if status_str not in ALL_JOB_STATES:
            raise ArchitectureInvariantError(f"Invalid initial job status: {status_str}")

        now_iso = datetime.now(timezone.utc).isoformat()
        meta_json = json.dumps(metadata or {})

        conn, should_close = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO jobs (job_id, package_id, project_id, status, priority, created_at, updated_at, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    package_id,
                    project_id,
                    status_str,
                    priority,
                    now_iso,
                    now_iso,
                    meta_json,
                ),
            )
            conn.commit()

            if self.audit_emitter:
                self.audit_emitter.emit(
                    event_type=STATUS_CHANGE,
                    severity=Severity.INFO.value,
                    job_id=job_id,
                    payload={"new_status": status_str, "project_id": project_id},
                )

            return {
                "job_id": job_id,
                "package_id": package_id,
                "project_id": project_id,
                "status": status_str,
                "priority": priority,
                "created_at": now_iso,
                "updated_at": now_iso,
                "metadata": metadata or {},
            }
        finally:
            if should_close:
                conn.close()

    # =========================================================================
    # CANONICAL TRANSITIONS
    # =========================================================================

    def can_transition(self, current_status: str, target_status: str) -> bool:
        """Evaluates whether a status transition is permitted by the state machine."""
        allowed = VALID_JOB_TRANSITIONS.get(current_status, frozenset())
        return target_status in allowed

    def transition(
        self,
        job_id: str,
        to_status: Union[str, JobStatus, JobSideStatus],
        current_run_id: Optional[str] = None,
        error_summary: Optional[str] = None,
        metadata_update: Optional[Dict[str, Any]] = None,
        expected_current_status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Atomically transitions a job to a target lifecycle state.

        Enforces:
        - Strict validation against VALID_JOB_TRANSITIONS.
        - Automatic setting of completed_at for terminal states.
        - Synchronized status update on associated runs record if run_id present.
        - Automatic project lease release upon reaching terminal or blocked states.
        - Append-only audit logging of STATUS_CHANGE.
        """
        target_status = (
            to_status.value if isinstance(to_status, (JobStatus, JobSideStatus)) else str(to_status)
        )

        if target_status not in ALL_JOB_STATES:
            raise ArchitectureInvariantError(
                f"Target state '{target_status}' is not a valid canonical job state"
            )

        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.isoformat()

        conn, should_close = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT job_id, project_id, current_run_id, status, metadata_json, completed_at FROM jobs WHERE job_id = ?",
                (job_id,),
            )
            row = cursor.fetchone()
            if not row:
                raise ArchitectureInvariantError(f"Job '{job_id}' does not exist in state store")

            current_status = row["status"]
            project_id = row["project_id"]
            active_run_id = current_run_id or row["current_run_id"]

            if expected_current_status and current_status != expected_current_status:
                raise ArchitectureInvariantError(
                    f"Job '{job_id}' expected status '{expected_current_status}', but was '{current_status}'"
                )

            # Validate transition legality
            if not self.can_transition(current_status, target_status):
                raise ArchitectureInvariantError(
                    f"Illegal canonical state transition for job '{job_id}': "
                    f"'{current_status}' -> '{target_status}'. Allowed: {sorted(VALID_JOB_TRANSITIONS.get(current_status, set()))}"
                )

            # Determine completed_at
            completed_at = row["completed_at"]
            if target_status in TERMINAL_JOB_STATES and not completed_at:
                completed_at = now_iso

            # Merge metadata if supplied
            meta_json = row["metadata_json"]
            if metadata_update:
                try:
                    existing_meta = json.loads(meta_json or "{}")
                except Exception:
                    existing_meta = {}
                existing_meta.update(metadata_update)
                meta_json = json.dumps(existing_meta)

            # Execute job table update
            cursor.execute(
                """
                UPDATE jobs
                SET status = ?, updated_at = ?, completed_at = ?, current_run_id = ?,
                    error_summary = COALESCE(?, error_summary), metadata_json = ?
                WHERE job_id = ?
                """,
                (
                    target_status,
                    now_iso,
                    completed_at,
                    active_run_id,
                    error_summary,
                    meta_json,
                    job_id,
                ),
            )

            # Synchronize runs table if active run ID exists
            if active_run_id:
                try:
                    cursor.execute(
                        """
                        UPDATE runs
                        SET status = ?, completed_at = COALESCE(?, completed_at),
                            error_summary = COALESCE(?, error_summary)
                        WHERE run_id = ?
                        """,
                        (
                            target_status,
                            now_iso if target_status in TERMINAL_JOB_STATES else None,
                            error_summary,
                            active_run_id,
                        ),
                    )
                except sqlite3.OperationalError:
                    pass

            conn.commit()

            # Automatic project lease cleanup if reaching release state
            if target_status in RELEASE_LEASE_STATES and project_id and self.lease_coordinator:
                self.lease_coordinator.release_project_lease(
                    project_id=project_id,
                    run_id=active_run_id,
                )

            # Append audit event
            if self.audit_emitter:
                sev = Severity.INFO.value
                if target_status in {JobSideStatus.FAILED.value, JobSideStatus.TIMED_OUT.value}:
                    sev = Severity.ERROR.value
                elif target_status in {
                    JobSideStatus.BLOCKED.value,
                    JobSideStatus.WAITING_APPROVAL.value,
                    JobSideStatus.INTERRUPTED.value,
                }:
                    sev = Severity.WARN.value

                self.audit_emitter.emit(
                    event_type=STATUS_CHANGE,
                    severity=sev,
                    job_id=job_id,
                    run_id=active_run_id,
                    payload={
                        "from_status": current_status,
                        "to_status": target_status,
                        "error_summary": error_summary,
                        "project_id": project_id,
                    },
                )

            return {
                "job_id": job_id,
                "project_id": project_id,
                "current_run_id": active_run_id,
                "previous_status": current_status,
                "status": target_status,
                "updated_at": now_iso,
                "completed_at": completed_at,
                "error_summary": error_summary,
            }
        finally:
            if should_close:
                conn.close()

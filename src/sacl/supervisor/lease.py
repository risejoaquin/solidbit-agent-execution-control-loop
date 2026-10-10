"""SACL V1 Distributed & Host Lease Coordination Subsystem.

Implements hierarchical locking conforming to docs/CONCURRENCY_AND_LOCKING.md:
- Level 1: System Lock (SUPERVISOR_SINGLETON) in table 'leases' and 'supervisor_locks'.
- Level 2: Project Lock (PROJECT_<projectId>) enforcing the 1-mutating-job baseline.
- Stale lease detection, process liveness verification, and atomic reclamation.
"""

from __future__ import annotations

import errno
import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
import sqlite3
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from sacl.contracts.exceptions import LeaseAcquisitionError
from sacl.contracts.invariants import PID_DRIFT_TOLERANCE_SECONDS
from sacl.contracts.models import LeaseRecord
from sacl.observability.events import (
    AuditEventType,
    PROJECT_LOCK_ACQUIRED,
    Severity,
    create_audit_event,
)

LEASE_ACQUIRED = AuditEventType.LEASE_ACQUIRED.value
LEASE_RELEASED = AuditEventType.LEASE_RELEASED.value


def default_process_alive_check(pid: int) -> bool:
    """Return whether *pid* refers to a live OS process without signalling it.

    POSIX supports ``os.kill(pid, 0)`` as a non-destructive existence probe.
    Windows does not share that contract for arbitrary signals, so use the
    native process-query API there instead of sending signal 0.
    """
    if pid <= 0:
        return False

    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        STILL_ACTIVE = 259
        ERROR_ACCESS_DENIED = 5
        ERROR_INVALID_PARAMETER = 87

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

        kernel32.OpenProcess.argtypes = [
            wintypes.DWORD,
            wintypes.BOOL,
            wintypes.DWORD,
        ]
        kernel32.OpenProcess.restype = wintypes.HANDLE

        kernel32.GetExitCodeProcess.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(wintypes.DWORD),
        ]
        kernel32.GetExitCodeProcess.restype = wintypes.BOOL

        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.CloseHandle.restype = wintypes.BOOL

        handle = kernel32.OpenProcess(
            PROCESS_QUERY_LIMITED_INFORMATION,
            False,
            int(pid),
        )

        if not handle:
            error = ctypes.get_last_error()
            if error == ERROR_INVALID_PARAMETER:
                return False
            if error == ERROR_ACCESS_DENIED:
                # Match POSIX EPERM semantics: process exists but cannot be queried.
                return True
            return False

        exit_code = wintypes.DWORD()
        try:
            if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                return False
            return exit_code.value == STILL_ACTIVE
        finally:
            kernel32.CloseHandle(handle)

    try:
        os.kill(pid, 0)
        return True
    except OSError as err:
        if err.errno == errno.ESRCH:
            return False
        if err.errno == errno.EPERM:
            return True
        return False
    except Exception:
        return False

class LeaseCoordinator:
    """Manages system and project mutual exclusion leases in sacl_ops.db."""

    SUPERVISOR_SINGLETON_KEY = "SUPERVISOR_SINGLETON"

    def __init__(
        self,
        db_source: Union[sqlite3.Connection, Path, str, Callable[[], sqlite3.Connection]],
        audit_emitter: Optional[Any] = None,
        process_checker: Optional[Callable[[int], bool]] = None,
    ):
        self._db_source = db_source
        self._db_file: Optional[str] = None
        self.audit_emitter = audit_emitter
        self.process_checker = process_checker or default_process_alive_check

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
    # LEVEL 1: SUPERVISOR SINGLETON LEASE
    # =========================================================================

    def acquire_singleton_lease(
        self,
        holder_id: str,
        holder_pid: Optional[int] = None,
        ttl_seconds: int = 60,
        metadata: Optional[Dict[str, Any]] = None,
        raise_on_failure: bool = False,
    ) -> bool:
        """Claims the global machine-level SUPERVISOR_SINGLETON lease.

        If another process holds the lease and is active, acquisition fails.
        If the prior holder process is dead or the lease has expired, the stale
        lease is automatically reclaimed with an audit event.
        """
        pid = holder_pid if holder_pid is not None else os.getpid()
        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.isoformat()
        expires_iso = (now_dt + timedelta(seconds=ttl_seconds)).isoformat()
        meta_json = json.dumps(metadata or {})

        conn, should_close = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT lease_name, holder_id, holder_pid, acquired_at, heartbeat_at, expires_at, metadata_json "
                "FROM leases WHERE lease_name = ?",
                (self.SUPERVISOR_SINGLETON_KEY,),
            )
            row = cursor.fetchone()

            if row:
                current_holder = row["holder_id"]
                current_pid = row["holder_pid"]
                expires_at_str = row["expires_at"]

                # Check if current holder is this exact process
                if current_pid == pid and current_holder == holder_id:
                    # Idempotent re-acquisition / renewal
                    return self.renew_singleton_lease(holder_id, pid, ttl_seconds)

                # Check expiration
                try:
                    exp_dt = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
                    if exp_dt.tzinfo is None:
                        exp_dt = exp_dt.replace(tzinfo=timezone.utc)
                    is_expired = now_dt > exp_dt
                except Exception:
                    is_expired = True

                # Check if process holding the lease is still alive
                is_alive = self.process_checker(current_pid)

                if is_alive and not is_expired:
                    if raise_on_failure:
                        raise LeaseAcquisitionError(
                            lease_name=self.SUPERVISOR_SINGLETON_KEY,
                            current_holder=current_holder,
                            holder_pid=current_pid,
                        )
                    return False

                # Stale lease detected - reclaim it
                if self.audit_emitter:
                    self.audit_emitter.emit(
                        event_type="STALE_LOCK_RECLAIMED",
                        severity=Severity.WARN.value,
                        payload={
                            "lease_name": self.SUPERVISOR_SINGLETON_KEY,
                            "stale_holder": current_holder,
                            "stale_pid": current_pid,
                            "is_expired": is_expired,
                            "holder_alive": is_alive,
                            "reclaimed_by_holder": holder_id,
                            "reclaimed_by_pid": pid,
                        },
                    )

                cursor.execute(
                    """
                    UPDATE leases
                    SET holder_id = ?, holder_pid = ?, acquired_at = ?, heartbeat_at = ?, expires_at = ?, metadata_json = ?
                    WHERE lease_name = ?
                    """,
                    (
                        holder_id,
                        pid,
                        now_iso,
                        now_iso,
                        expires_iso,
                        meta_json,
                        self.SUPERVISOR_SINGLETON_KEY,
                    ),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO leases (lease_name, holder_id, holder_pid, acquired_at, heartbeat_at, expires_at, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        self.SUPERVISOR_SINGLETON_KEY,
                        holder_id,
                        pid,
                        now_iso,
                        now_iso,
                        expires_iso,
                        meta_json,
                    ),
                )

            # Sync compatibility table supervisor_locks
            try:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO supervisor_locks (lock_name, run_id, holder_pid, acquired_at, heartbeat_at, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        self.SUPERVISOR_SINGLETON_KEY,
                        holder_id,
                        pid,
                        now_iso,
                        now_iso,
                        expires_iso,
                    ),
                )
            except sqlite3.OperationalError:
                pass

            conn.commit()

            if self.audit_emitter:
                self.audit_emitter.emit(
                    event_type=LEASE_ACQUIRED,
                    severity=Severity.INFO.value,
                    payload={
                        "lease_name": self.SUPERVISOR_SINGLETON_KEY,
                        "holder_id": holder_id,
                        "holder_pid": pid,
                        "ttl_seconds": ttl_seconds,
                    },
                )
            return True
        finally:
            if should_close:
                conn.close()

    def renew_singleton_lease(
        self,
        holder_id: str,
        holder_pid: Optional[int] = None,
        ttl_seconds: int = 60,
    ) -> bool:
        """Renews the SUPERVISOR_SINGLETON lease if held by the calling process."""
        pid = holder_pid if holder_pid is not None else os.getpid()
        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.isoformat()
        expires_iso = (now_dt + timedelta(seconds=ttl_seconds)).isoformat()

        conn, should_close = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE leases
                SET heartbeat_at = ?, expires_at = ?
                WHERE lease_name = ? AND holder_pid = ? AND holder_id = ?
                """,
                (
                    now_iso,
                    expires_iso,
                    self.SUPERVISOR_SINGLETON_KEY,
                    pid,
                    holder_id,
                ),
            )
            updated = cursor.rowcount > 0

            if updated:
                try:
                    cursor.execute(
                        """
                        UPDATE supervisor_locks
                        SET heartbeat_at = ?, expires_at = ?
                        WHERE lock_name = ? AND holder_pid = ?
                        """,
                        (now_iso, expires_iso, self.SUPERVISOR_SINGLETON_KEY, pid),
                    )
                except sqlite3.OperationalError:
                    pass
                conn.commit()
            return updated
        finally:
            if should_close:
                conn.close()

    def release_singleton_lease(
        self,
        holder_id: str,
        holder_pid: Optional[int] = None,
    ) -> bool:
        """Releases the SUPERVISOR_SINGLETON lease gracefully upon shutdown."""
        pid = holder_pid if holder_pid is not None else os.getpid()

        conn, should_close = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM leases WHERE lease_name = ? AND holder_pid = ? AND holder_id = ?",
                (self.SUPERVISOR_SINGLETON_KEY, pid, holder_id),
            )
            deleted = cursor.rowcount > 0

            try:
                cursor.execute(
                    "DELETE FROM supervisor_locks WHERE lock_name = ? AND holder_pid = ?",
                    (self.SUPERVISOR_SINGLETON_KEY, pid),
                )
            except sqlite3.OperationalError:
                pass

            conn.commit()

            if deleted and self.audit_emitter:
                self.audit_emitter.emit(
                    event_type=LEASE_RELEASED,
                    severity=Severity.INFO.value,
                    payload={
                        "lease_name": self.SUPERVISOR_SINGLETON_KEY,
                        "holder_id": holder_id,
                        "holder_pid": pid,
                    },
                )
            return deleted
        finally:
            if should_close:
                conn.close()

    def get_singleton_lease(self) -> Optional[LeaseRecord]:
        """Retrieves the current state of SUPERVISOR_SINGLETON lease."""
        conn, should_close = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT lease_name, holder_id, holder_pid, acquired_at, heartbeat_at, expires_at, metadata_json "
                "FROM leases WHERE lease_name = ?",
                (self.SUPERVISOR_SINGLETON_KEY,),
            )
            row = cursor.fetchone()
            if not row:
                return None

            metadata = {}
            if row["metadata_json"]:
                try:
                    metadata = json.loads(row["metadata_json"])
                except Exception:
                    pass

            return LeaseRecord(
                lease_name=row["lease_name"],
                holder_id=row["holder_id"],
                holder_pid=row["holder_pid"],
                acquired_at=row["acquired_at"],
                heartbeat_at=row["heartbeat_at"],
                expires_at=row["expires_at"],
                metadata=metadata,
            )
        finally:
            if should_close:
                conn.close()

    # =========================================================================
    # LEVEL 2: PROJECT MUTUAL EXCLUSION LEASE
    # =========================================================================

    def _project_lease_key(self, project_id: str) -> str:
        return f"PROJECT_{project_id}"

    def is_project_locked(
        self,
        project_id: str,
        is_mutating: bool = True,
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Checks if a project has an active lock.

        If is_mutating is True: returns True if ANY lease is active.
        If is_mutating is False: returns True if an active MUTATING lease exists.
        """
        lease_name = self._project_lease_key(project_id)
        now_dt = datetime.now(timezone.utc)

        conn, should_close = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT lease_name, holder_id, holder_pid, acquired_at, heartbeat_at, expires_at, metadata_json "
                "FROM leases WHERE lease_name = ?",
                (lease_name,),
            )
            row = cursor.fetchone()
            if not row:
                return False, None

            # Check expiration & liveness
            try:
                exp_dt = datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00"))
                if exp_dt.tzinfo is None:
                    exp_dt = exp_dt.replace(tzinfo=timezone.utc)
                is_expired = now_dt > exp_dt
            except Exception:
                is_expired = True

            holder_pid = row["holder_pid"]
            is_alive = self.process_checker(holder_pid)

            if is_expired or not is_alive:
                return False, dict(row)

            meta = {}
            if row["metadata_json"]:
                try:
                    meta = json.loads(row["metadata_json"])
                except Exception:
                    pass

            current_is_mutating = meta.get("is_mutating", True)

            if is_mutating:
                # Mutating requires exclusive access
                return True, dict(row)
            else:
                # Read-only is blocked only by mutating lock
                return current_is_mutating, dict(row)
        finally:
            if should_close:
                conn.close()

    def acquire_project_lease(
        self,
        project_id: str,
        run_id: str,
        holder_pid: Optional[int] = None,
        is_mutating: bool = True,
        ttl_seconds: int = 300,
        job_id: Optional[str] = None,
        raise_on_failure: bool = False,
    ) -> bool:
        """Claims a project-level mutual exclusion lease.

        Enforces the Concurrency Baseline: exactly one mutating job per project.
        Safe read-only jobs can coexist if no mutating job is active.
        """
        pid = holder_pid if holder_pid is not None else os.getpid()
        lease_name = self._project_lease_key(project_id)
        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.isoformat()
        expires_iso = (now_dt + timedelta(seconds=ttl_seconds)).isoformat()

        meta = {
            "project_id": project_id,
            "run_id": run_id,
            "job_id": job_id,
            "is_mutating": is_mutating,
        }
        meta_json = json.dumps(meta)

        conn, should_close = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT lease_name, holder_id, holder_pid, acquired_at, heartbeat_at, expires_at, metadata_json "
                "FROM leases WHERE lease_name = ?",
                (lease_name,),
            )
            row = cursor.fetchone()

            if row:
                current_holder = row["holder_id"]
                current_pid = row["holder_pid"]
                expires_at_str = row["expires_at"]

                # Check if current holder is the same run
                if current_holder == run_id:
                    return self.renew_project_lease(project_id, run_id, ttl_seconds)

                # Check expiration
                try:
                    exp_dt = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
                    if exp_dt.tzinfo is None:
                        exp_dt = exp_dt.replace(tzinfo=timezone.utc)
                    is_expired = now_dt > exp_dt
                except Exception:
                    is_expired = True

                is_alive = self.process_checker(current_pid)

                if is_alive and not is_expired:
                    current_meta = {}
                    if row["metadata_json"]:
                        try:
                            current_meta = json.loads(row["metadata_json"])
                        except Exception:
                            pass
                    current_is_mutating = current_meta.get("is_mutating", True)

                    # Mutating job blocks all; read-only is blocked by mutating
                    if is_mutating or current_is_mutating:
                        if raise_on_failure:
                            raise LeaseAcquisitionError(
                                lease_name=lease_name,
                                current_holder=current_holder,
                                holder_pid=current_pid,
                            )
                        return False

                # Stale or expired lock can be reclaimed
                if self.audit_emitter:
                    self.audit_emitter.emit(
                        event_type="STALE_LOCK_RECLAIMED",
                        severity=Severity.WARN.value,
                        job_id=job_id,
                        run_id=run_id,
                        payload={
                            "lease_name": lease_name,
                            "stale_holder": current_holder,
                            "stale_pid": current_pid,
                            "reclaimed_by_run": run_id,
                        },
                    )

                cursor.execute(
                    """
                    UPDATE leases
                    SET holder_id = ?, holder_pid = ?, acquired_at = ?, heartbeat_at = ?, expires_at = ?, metadata_json = ?
                    WHERE lease_name = ?
                    """,
                    (run_id, pid, now_iso, now_iso, expires_iso, meta_json, lease_name),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO leases (lease_name, holder_id, holder_pid, acquired_at, heartbeat_at, expires_at, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (lease_name, run_id, pid, now_iso, now_iso, expires_iso, meta_json),
                )

            conn.commit()

            if self.audit_emitter:
                self.audit_emitter.emit(
                    event_type=PROJECT_LOCK_ACQUIRED,
                    severity=Severity.INFO.value,
                    job_id=job_id,
                    run_id=run_id,
                    payload={
                        "lease_name": lease_name,
                        "project_id": project_id,
                        "run_id": run_id,
                        "is_mutating": is_mutating,
                        "ttl_seconds": ttl_seconds,
                    },
                )
            return True
        finally:
            if should_close:
                conn.close()

    def renew_project_lease(
        self,
        project_id: str,
        run_id: str,
        ttl_seconds: int = 300,
    ) -> bool:
        """Renews an active project lease for an executing run."""
        lease_name = self._project_lease_key(project_id)
        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.isoformat()
        expires_iso = (now_dt + timedelta(seconds=ttl_seconds)).isoformat()

        conn, should_close = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE leases
                SET heartbeat_at = ?, expires_at = ?
                WHERE lease_name = ? AND holder_id = ?
                """,
                (now_iso, expires_iso, lease_name, run_id),
            )
            updated = cursor.rowcount > 0
            if updated:
                conn.commit()
            return updated
        finally:
            if should_close:
                conn.close()

    def release_project_lease(
        self,
        project_id: str,
        run_id: Optional[str] = None,
    ) -> bool:
        """Releases the project lock when an execution wave finishes."""
        lease_name = self._project_lease_key(project_id)

        conn, should_close = self._get_connection()
        try:
            cursor = conn.cursor()
            if run_id:
                cursor.execute(
                    "DELETE FROM leases WHERE lease_name = ? AND holder_id = ?",
                    (lease_name, run_id),
                )
            else:
                cursor.execute("DELETE FROM leases WHERE lease_name = ?", (lease_name,))
            deleted = cursor.rowcount > 0
            conn.commit()

            if deleted and self.audit_emitter:
                self.audit_emitter.emit(
                    event_type=LEASE_RELEASED,
                    severity=Severity.INFO.value,
                    run_id=run_id,
                    payload={"lease_name": lease_name, "project_id": project_id},
                )
            return deleted
        finally:
            if should_close:
                conn.close()

    def get_project_lease(self, project_id: str) -> Optional[LeaseRecord]:
        """Retrieves active project lease record if present."""
        lease_name = self._project_lease_key(project_id)
        conn, should_close = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT lease_name, holder_id, holder_pid, acquired_at, heartbeat_at, expires_at, metadata_json "
                "FROM leases WHERE lease_name = ?",
                (lease_name,),
            )
            row = cursor.fetchone()
            if not row:
                return None

            metadata = {}
            if row["metadata_json"]:
                try:
                    metadata = json.loads(row["metadata_json"])
                except Exception:
                    pass

            return LeaseRecord(
                lease_name=row["lease_name"],
                holder_id=row["holder_id"],
                holder_pid=row["holder_pid"],
                acquired_at=row["acquired_at"],
                heartbeat_at=row["heartbeat_at"],
                expires_at=row["expires_at"],
                metadata=metadata,
            )
        finally:
            if should_close:
                conn.close()

    def release_all_leases_for_holder(
        self,
        holder_id: str,
        holder_pid: Optional[int] = None,
    ) -> int:
        """Releases all leases held by a given holder or PID.

        Essential for crash recovery and supervisor shutdown.
        """
        conn, should_close = self._get_connection()
        try:
            cursor = conn.cursor()
            if holder_pid is not None:
                cursor.execute(
                    "DELETE FROM leases WHERE holder_id = ? OR holder_pid = ?",
                    (holder_id, holder_pid),
                )
            else:
                cursor.execute("DELETE FROM leases WHERE holder_id = ?", (holder_id,))
            count = cursor.rowcount

            # Clean supervisor_locks as well if holder_pid given
            if holder_pid is not None:
                try:
                    cursor.execute(
                        "DELETE FROM supervisor_locks WHERE holder_pid = ? OR run_id = ?",
                        (holder_pid, holder_id),
                    )
                except sqlite3.OperationalError:
                    pass

            conn.commit()
            return count
        finally:
            if should_close:
                conn.close()

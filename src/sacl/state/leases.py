"""SACL V1 Lease Management & Concurrency Locking.

Domain 13: Generalized local process mutual exclusion leases (ADR-002, ADR-003).
Compatibility Table: supervisor_locks.
Implements the 5-level hierarchical lock ladder:
1. SYSTEM (SUPERVISOR_SINGLETON)
2. PROJECT (PROJECT_<projectId>)
3. REPO (REPO_<repoId>)
4. WORKTREE (WORKTREE_<agentId>)
5. RESOURCE (RESOURCE_<resourceId>)
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, Generator, List, Optional

from sacl.contracts.exceptions import LeaseAcquisitionError
from sacl.contracts.models import LeaseRecord
from sacl.state.repositories.base import BaseRepository
from sacl.state.utils import format_utc, json_dumps_safe, json_loads_safe, utc_now


class HierarchicalLeaseType(str, Enum):
    SYSTEM = "SYSTEM"
    PROJECT = "PROJECT"
    REPO = "REPO"
    WORKTREE = "WORKTREE"
    RESOURCE = "RESOURCE"


class LeaseManager(BaseRepository):
    """Manages Domain 13 mutual exclusion leases and supervisor singleton locks."""

    def acquire_lease(
        self,
        lease_name: str,
        holder_id: str,
        holder_pid: int,
        ttl_seconds: int = 30,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Attempts atomic mutual exclusion lease acquisition.

        Returns True if acquired (or re-acquired by same holder); False if actively held by another.
        """
        now = utc_now()
        now_dt = datetime.now(timezone.utc)
        expires = format_utc(now_dt + timedelta(seconds=ttl_seconds))
        meta_json = json_dumps_safe(metadata)

        sql = """
            INSERT INTO leases (
                lease_name, holder_id, holder_pid,
                acquired_at, heartbeat_at, expires_at, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(lease_name) DO UPDATE SET
                holder_id = excluded.holder_id,
                holder_pid = excluded.holder_pid,
                acquired_at = CASE WHEN leases.holder_id = excluded.holder_id THEN leases.acquired_at ELSE excluded.acquired_at END,
                heartbeat_at = excluded.heartbeat_at,
                expires_at = excluded.expires_at,
                metadata_json = excluded.metadata_json
            WHERE expires_at < ? OR holder_id = ?;
        """
        cursor = self.execute(
            sql, (lease_name, holder_id, holder_pid, now, now, expires, meta_json, now, holder_id)
        )
        acquired = cursor.rowcount > 0

        if acquired and lease_name == "SUPERVISOR_SINGLETON":
            # Sync compatibility table supervisor_locks
            sql_sup = """
                INSERT INTO supervisor_locks (lock_name, run_id, holder_pid, acquired_at, heartbeat_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(lock_name) DO UPDATE SET
                    run_id = excluded.run_id,
                    holder_pid = excluded.holder_pid,
                    heartbeat_at = excluded.heartbeat_at,
                    expires_at = excluded.expires_at;
            """
            self.execute(sql_sup, (lease_name, holder_id, holder_pid, now, now, expires))

        self.commit()
        return acquired

    def renew_lease(self, lease_name: str, holder_id: str, ttl_seconds: int = 30) -> bool:
        """Renews an actively held mutual exclusion lease."""
        now = utc_now()
        now_dt = datetime.now(timezone.utc)
        expires = format_utc(now_dt + timedelta(seconds=ttl_seconds))

        sql = """
            UPDATE leases
            SET heartbeat_at = ?, expires_at = ?
            WHERE lease_name = ? AND holder_id = ? AND expires_at >= ?;
        """
        cursor = self.execute(sql, (now, expires, lease_name, holder_id, now))
        renewed = cursor.rowcount > 0

        if renewed and lease_name == "SUPERVISOR_SINGLETON":
            sql_sup = """
                UPDATE supervisor_locks
                SET heartbeat_at = ?, expires_at = ?
                WHERE lock_name = ? AND run_id = ?;
            """
            self.execute(sql_sup, (now, expires, lease_name, holder_id))

        self.commit()
        return renewed

    def release_lease(self, lease_name: str, holder_id: str) -> bool:
        """Gracefully releases a mutual exclusion lease held by holder_id."""
        sql = "DELETE FROM leases WHERE lease_name = ? AND holder_id = ?;"
        cursor = self.execute(sql, (lease_name, holder_id))
        released = cursor.rowcount > 0

        if released and lease_name == "SUPERVISOR_SINGLETON":
            self.execute(
                "DELETE FROM supervisor_locks WHERE lock_name = ? AND run_id = ?;",
                (lease_name, holder_id),
            )

        self.commit()
        return released

    def get_lease(self, lease_name: str) -> Optional[Dict[str, Any]]:
        """Retrieves raw lease record by name."""
        sql = "SELECT * FROM leases WHERE lease_name = ?;"
        row = self.fetchone_dict(sql, (lease_name,))
        if row and row.get("metadata_json"):
            row["metadata"] = json_loads_safe(row["metadata_json"])
        return row

    def get_lease_record(self, lease_name: str) -> Optional[LeaseRecord]:
        """Retrieves typed LeaseRecord by name."""
        row = self.get_lease(lease_name)
        if not row:
            return None
        return LeaseRecord(
            lease_name=row["lease_name"],
            holder_id=row["holder_id"],
            holder_pid=row["holder_pid"],
            acquired_at=row["acquired_at"],
            heartbeat_at=row["heartbeat_at"],
            expires_at=row["expires_at"],
            metadata=row.get("metadata"),
        )

    def is_lease_active(self, lease_name: str) -> bool:
        """Checks if a named lease is currently held and unexpired."""
        row = self.get_lease(lease_name)
        if not row:
            return False
        return row["expires_at"] >= utc_now()

    def reclaim_stale_leases(self) -> List[str]:
        """Cleans up and releases leases whose expires_at is in the past."""
        now = utc_now()
        sql_select = "SELECT lease_name FROM leases WHERE expires_at < ?;"
        rows = self.fetchall_dict(sql_select, (now,))
        stale_names = [r["lease_name"] for r in rows]

        if stale_names:
            self.execute("DELETE FROM leases WHERE expires_at < ?;", (now,))
            self.execute("DELETE FROM supervisor_locks WHERE expires_at < ?;", (now,))
            self.commit()

        return stale_names

    # =========================================================================
    # HIERARCHICAL LOCK HELPERS
    # =========================================================================

    def acquire_system_lease(self, holder_id: str, holder_pid: int, ttl_seconds: int = 60) -> bool:
        """Acquires Level 1 System Lock (SUPERVISOR_SINGLETON)."""
        return self.acquire_lease(
            "SUPERVISOR_SINGLETON", holder_id, holder_pid, ttl_seconds, {"lease_type": "SYSTEM"}
        )

    def acquire_project_lease(
        self,
        project_id: str,
        holder_id: str,
        holder_pid: int,
        ttl_seconds: int = 60,
        is_mutating: bool = True,
    ) -> bool:
        """Acquires Level 2 Project Lock (PROJECT_<projectId>)."""
        lease_name = f"PROJECT_{project_id}"
        return self.acquire_lease(
            lease_name,
            holder_id,
            holder_pid,
            ttl_seconds,
            {"lease_type": "PROJECT", "is_mutating": is_mutating},
        )

    def acquire_repo_lease(
        self, repo_id: str, holder_id: str, holder_pid: int, ttl_seconds: int = 30
    ) -> bool:
        """Acquires Level 3 Repo Lock (REPO_<repoId>)."""
        lease_name = f"REPO_{repo_id}"
        return self.acquire_lease(
            lease_name, holder_id, holder_pid, ttl_seconds, {"lease_type": "REPO"}
        )

    def acquire_worktree_lease(
        self, agent_id: str, holder_id: str, holder_pid: int, ttl_seconds: int = 60
    ) -> bool:
        """Acquires Level 4 Worktree Lock (WORKTREE_<agentId>)."""
        lease_name = f"WORKTREE_{agent_id}"
        return self.acquire_lease(
            lease_name, holder_id, holder_pid, ttl_seconds, {"lease_type": "WORKTREE"}
        )

    def acquire_resource_lease(
        self, resource_id: str, holder_id: str, holder_pid: int, ttl_seconds: int = 60
    ) -> bool:
        """Acquires Level 5 Resource Lock (RESOURCE_<resourceId>)."""
        lease_name = f"RESOURCE_{resource_id}"
        return self.acquire_lease(
            lease_name, holder_id, holder_pid, ttl_seconds, {"lease_type": "RESOURCE"}
        )

    def release_system_lease(self, holder_id: str) -> bool:
        """Releases Level 1 System Lock (SUPERVISOR_SINGLETON)."""
        return self.release_lease("SUPERVISOR_SINGLETON", holder_id)

    def release_project_lease(self, project_id: str, holder_id: str) -> bool:
        """Releases Level 2 Project Lock (PROJECT_<projectId>)."""
        return self.release_lease(f"PROJECT_{project_id}", holder_id)

    def release_repo_lease(self, repo_id: str, holder_id: str) -> bool:
        """Releases Level 3 Repo Lock (REPO_<repoId>)."""
        return self.release_lease(f"REPO_{repo_id}", holder_id)

    def release_worktree_lease(self, agent_id: str, holder_id: str) -> bool:
        """Releases Level 4 Worktree Lock (WORKTREE_<agentId>)."""
        return self.release_lease(f"WORKTREE_{agent_id}", holder_id)

    def release_resource_lease(self, resource_id: str, holder_id: str) -> bool:
        """Releases Level 5 Resource Lock (RESOURCE_<resourceId>)."""
        return self.release_lease(f"RESOURCE_{resource_id}", holder_id)

    # =========================================================================
    # CONTEXT MANAGERS
    # =========================================================================

    @contextmanager
    def hold_lease(
        self,
        lease_name: str,
        holder_id: str,
        holder_pid: int,
        ttl_seconds: int = 30,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """Context manager acquiring a lease on entry and releasing it on exit.

        Raises:
            LeaseAcquisitionError: If lease is actively held by another process.
        """
        acquired = self.acquire_lease(lease_name, holder_id, holder_pid, ttl_seconds, metadata)
        if not acquired:
            existing = self.get_lease(lease_name) or {}
            raise LeaseAcquisitionError(
                lease_name=lease_name,
                current_holder=existing.get("holder_id", "UNKNOWN"),
                holder_pid=existing.get("holder_pid", 0),
            )
        try:
            yield self.get_lease(lease_name)  # type: ignore[misc]
        finally:
            self.release_lease(lease_name, holder_id)

    @contextmanager
    def hold_system_lease(
        self, holder_id: str, holder_pid: int, ttl_seconds: int = 60
    ) -> Generator[Dict[str, Any], None, None]:
        """Context manager for Level 1 System Lock (SUPERVISOR_SINGLETON)."""
        with self.hold_lease(
            "SUPERVISOR_SINGLETON", holder_id, holder_pid, ttl_seconds, {"lease_type": "SYSTEM"}
        ) as lease:
            yield lease

    @contextmanager
    def hold_project_lease(
        self,
        project_id: str,
        holder_id: str,
        holder_pid: int,
        ttl_seconds: int = 60,
        is_mutating: bool = True,
    ) -> Generator[Dict[str, Any], None, None]:
        """Context manager for Level 2 Project Lock (PROJECT_<projectId>)."""
        with self.hold_lease(
            f"PROJECT_{project_id}",
            holder_id,
            holder_pid,
            ttl_seconds,
            {"lease_type": "PROJECT", "is_mutating": is_mutating},
        ) as lease:
            yield lease

    @contextmanager
    def hold_repo_lease(
        self, repo_id: str, holder_id: str, holder_pid: int, ttl_seconds: int = 30
    ) -> Generator[Dict[str, Any], None, None]:
        """Context manager for Level 3 Repo Lock (REPO_<repoId>)."""
        with self.hold_lease(
            f"REPO_{repo_id}", holder_id, holder_pid, ttl_seconds, {"lease_type": "REPO"}
        ) as lease:
            yield lease

    @contextmanager
    def hold_worktree_lease(
        self, agent_id: str, holder_id: str, holder_pid: int, ttl_seconds: int = 60
    ) -> Generator[Dict[str, Any], None, None]:
        """Context manager for Level 4 Worktree Lock (WORKTREE_<agentId>)."""
        with self.hold_lease(
            f"WORKTREE_{agent_id}", holder_id, holder_pid, ttl_seconds, {"lease_type": "WORKTREE"}
        ) as lease:
            yield lease

    @contextmanager
    def hold_resource_lease(
        self, resource_id: str, holder_id: str, holder_pid: int, ttl_seconds: int = 60
    ) -> Generator[Dict[str, Any], None, None]:
        """Context manager for Level 5 Resource Lock (RESOURCE_<resourceId>)."""
        with self.hold_lease(
            f"RESOURCE_{resource_id}",
            holder_id,
            holder_pid,
            ttl_seconds,
            {"lease_type": "RESOURCE"},
        ) as lease:
            yield lease

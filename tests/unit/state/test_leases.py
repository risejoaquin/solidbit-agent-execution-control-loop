"""Unit tests for Lease Management, Hierarchical Locking, and Mutex Primitives."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Generator

import pytest

from sacl.contracts.exceptions import LeaseAcquisitionError
from sacl.state.connection import create_connection
from sacl.state.leases import LeaseManager
from sacl.state.migrations import MigrationRunner


@pytest.fixture
def lease_db(migration_sql_path: Path) -> Generator[sqlite3.Connection, None, None]:
    conn = create_connection(":memory:")
    runner = MigrationRunner(migration_sql_path.parent)
    runner.apply_all(conn)
    yield conn
    conn.close()


def test_atomic_lease_acquisition_and_contention(lease_db: sqlite3.Connection) -> None:
    mgr = LeaseManager(lease_db)

    # First holder acquires lease successfully
    acq1 = mgr.acquire_lease("RESOURCE_DB", holder_id="proc-1", holder_pid=1001, ttl_seconds=10)
    assert acq1 is True

    # Same holder can re-acquire/refresh
    acq1_again = mgr.acquire_lease(
        "RESOURCE_DB", holder_id="proc-1", holder_pid=1001, ttl_seconds=10
    )
    assert acq1_again is True

    # Second holder attempts to acquire while active -> contention, returns False
    acq2 = mgr.acquire_lease("RESOURCE_DB", holder_id="proc-2", holder_pid=1002, ttl_seconds=10)
    assert acq2 is False


def test_lease_renewal_and_release(lease_db: sqlite3.Connection) -> None:
    mgr = LeaseManager(lease_db)
    mgr.acquire_lease("REPO_MAIN", holder_id="worker-1", holder_pid=2001, ttl_seconds=5)

    # Renewal
    renewed = mgr.renew_lease("REPO_MAIN", holder_id="worker-1", ttl_seconds=20)
    assert renewed is True

    # Renewal by different holder fails
    renew_other = mgr.renew_lease("REPO_MAIN", holder_id="worker-2", ttl_seconds=20)
    assert renew_other is False

    # Release
    released = mgr.release_lease("REPO_MAIN", holder_id="worker-1")
    assert released is True
    assert mgr.is_lease_active("REPO_MAIN") is False

    # After release, second holder can acquire
    acq2 = mgr.acquire_lease("REPO_MAIN", holder_id="worker-2", holder_pid=2002, ttl_seconds=10)
    assert acq2 is True


def test_supervisor_singleton_compatibility_table_sync(lease_db: sqlite3.Connection) -> None:
    mgr = LeaseManager(lease_db)

    # Acquiring SUPERVISOR_SINGLETON must sync to supervisor_locks
    acq = mgr.acquire_system_lease(holder_id="sup-daemon-1", holder_pid=5555, ttl_seconds=30)
    assert acq is True

    cursor = lease_db.cursor()
    cursor.execute("SELECT * FROM supervisor_locks WHERE lock_name = 'SUPERVISOR_SINGLETON';")
    sup_lock = cursor.fetchone()
    assert sup_lock is not None
    assert sup_lock["run_id"] == "sup-daemon-1"
    assert sup_lock["holder_pid"] == 5555

    # Renewal syncs to supervisor_locks
    mgr.renew_lease("SUPERVISOR_SINGLETON", holder_id="sup-daemon-1", ttl_seconds=45)
    cursor.execute(
        "SELECT expires_at FROM supervisor_locks WHERE lock_name = 'SUPERVISOR_SINGLETON';"
    )
    assert cursor.fetchone()["expires_at"] == mgr.get_lease("SUPERVISOR_SINGLETON")["expires_at"]

    # Release removes from both
    mgr.release_lease("SUPERVISOR_SINGLETON", holder_id="sup-daemon-1")
    cursor.execute("SELECT * FROM supervisor_locks WHERE lock_name = 'SUPERVISOR_SINGLETON';")
    assert cursor.fetchone() is None


def test_hierarchical_lock_ladder(lease_db: sqlite3.Connection) -> None:
    mgr = LeaseManager(lease_db)

    # Level 1: System
    assert mgr.acquire_system_lease("sup-1", 100) is True
    # Level 2: Project
    assert mgr.acquire_project_lease("solidbit", "sup-1", 100) is True
    # Level 3: Repo
    assert mgr.acquire_repo_lease("repo-1", "sup-1", 100) is True
    # Level 4: Worktree
    assert mgr.acquire_worktree_lease("AG-COMPAT", "worker-compat", 200) is True
    # Level 5: Resource
    assert mgr.acquire_resource_lease("TEST_PORT_8080", "worker-compat", 200) is True


def test_hold_lease_context_manager(lease_db: sqlite3.Connection) -> None:
    mgr = LeaseManager(lease_db)

    with mgr.hold_lease(
        "WORKTREE_AG-ARCH", holder_id="worker-arch", holder_pid=3001, ttl_seconds=10
    ):
        assert mgr.is_lease_active("WORKTREE_AG-ARCH") is True

        # Another process cannot acquire it inside the block
        assert (
            mgr.acquire_lease("WORKTREE_AG-ARCH", holder_id="worker-other", holder_pid=3002)
            is False
        )

    # Automatically released on block exit
    assert mgr.is_lease_active("WORKTREE_AG-ARCH") is False


def test_hold_lease_contention_raises_error(lease_db: sqlite3.Connection) -> None:
    mgr = LeaseManager(lease_db)
    mgr.acquire_lease("EXCLUSIVE_PORT", holder_id="holder-a", holder_pid=4001, ttl_seconds=10)

    with pytest.raises(LeaseAcquisitionError) as exc_info:
        with mgr.hold_lease("EXCLUSIVE_PORT", holder_id="holder-b", holder_pid=4002):
            pass

    assert exc_info.value.lease_name == "EXCLUSIVE_PORT"
    assert exc_info.value.details["current_holder"] == "holder-a"


def test_stale_lease_reclamation(lease_db: sqlite3.Connection) -> None:
    mgr = LeaseManager(lease_db)

    # Insert pre-expired lease
    lease_db.execute(
        """
        INSERT INTO leases VALUES (
            'STALE_LEASE', 'old-proc', 9999,
            '2020-01-01T00:00:00Z', '2020-01-01T00:00:00Z', '2020-01-01T00:01:00Z', NULL
        );
        """
    )
    lease_db.commit()

    reclaimed = mgr.reclaim_stale_leases()
    assert "STALE_LEASE" in reclaimed
    assert mgr.get_lease("STALE_LEASE") is None

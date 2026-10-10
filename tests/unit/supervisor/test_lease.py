"""Unit tests for SACL V1 supervisor and project lease coordination."""

import os
import sqlite3
from datetime import datetime, timezone, timedelta
import pytest

from sacl.contracts.exceptions import LeaseAcquisitionError
from sacl.contracts.models import LeaseRecord
from sacl.observability.audit import AuditEventEmitter
from sacl.supervisor.lease import LeaseCoordinator


def test_acquire_and_get_singleton_lease(sqlite_temp_db: sqlite3.Connection):
    """Verifies acquiring the SUPERVISOR_SINGLETON lease and reading it back."""
    emitter = AuditEventEmitter(sqlite_temp_db)
    coordinator = LeaseCoordinator(sqlite_temp_db, audit_emitter=emitter)

    # Initial acquisition succeeds
    success = coordinator.acquire_singleton_lease(
        holder_id="sup-test-1",
        holder_pid=12345,
        ttl_seconds=60,
    )
    assert success is True

    record = coordinator.get_singleton_lease()
    assert record is not None
    assert record.lease_name == "SUPERVISOR_SINGLETON"
    assert record.holder_id == "sup-test-1"
    assert record.holder_pid == 12345

    # Check compatibility table supervisor_locks is also populated
    cursor = sqlite_temp_db.cursor()
    cursor.execute("SELECT lock_name, run_id, holder_pid FROM supervisor_locks WHERE lock_name = 'SUPERVISOR_SINGLETON'")
    lock_row = cursor.fetchone()
    assert lock_row is not None
    assert lock_row["run_id"] == "sup-test-1"
    assert lock_row["holder_pid"] == 12345


def test_singleton_lease_mutual_exclusion(sqlite_temp_db: sqlite3.Connection):
    """Verifies that another live process cannot acquire an active singleton lease."""
    # Process 12345 is simulated as alive
    coordinator = LeaseCoordinator(
        sqlite_temp_db,
        process_checker=lambda pid: pid == 12345,
    )

    # Holder 1 acquires lease
    assert coordinator.acquire_singleton_lease("sup-1", holder_pid=12345, ttl_seconds=60) is True

    # Holder 2 attempts acquisition while Holder 1 is still alive and lease unexpired
    assert coordinator.acquire_singleton_lease("sup-2", holder_pid=99999, ttl_seconds=60) is False

    # Should raise if raise_on_failure is requested
    with pytest.raises(LeaseAcquisitionError) as exc_info:
        coordinator.acquire_singleton_lease(
            "sup-2",
            holder_pid=99999,
            ttl_seconds=60,
            raise_on_failure=True,
        )
    assert exc_info.value.lease_name == "SUPERVISOR_SINGLETON"


def test_stale_singleton_lease_reclaimed_when_process_dead(sqlite_temp_db: sqlite3.Connection):
    """Verifies automatic reclamation of singleton lease when holder PID is dead."""
    emitter = AuditEventEmitter(sqlite_temp_db)
    # Process 11111 is dead
    coordinator = LeaseCoordinator(
        sqlite_temp_db,
        audit_emitter=emitter,
        process_checker=lambda pid: False,
    )

    # Seed an unexpired lease held by dead PID 11111
    now_iso = datetime.now(timezone.utc).isoformat()
    future_iso = (datetime.now(timezone.utc) + timedelta(seconds=120)).isoformat()
    cursor = sqlite_temp_db.cursor()
    cursor.execute(
        """
        INSERT INTO leases (lease_name, holder_id, holder_pid, acquired_at, heartbeat_at, expires_at, metadata_json)
        VALUES ('SUPERVISOR_SINGLETON', 'dead-daemon', 11111, ?, ?, ?, '{}')
        """,
        (now_iso, now_iso, future_iso),
    )
    sqlite_temp_db.commit()

    # New supervisor claims lease; must reclaim because PID 11111 is dead
    success = coordinator.acquire_singleton_lease("fresh-daemon", holder_pid=22222, ttl_seconds=60)
    assert success is True

    record = coordinator.get_singleton_lease()
    assert record.holder_id == "fresh-daemon"
    assert record.holder_pid == 22222

    # Verify audit event emitted
    events = emitter.query_events(event_type="STALE_LOCK_RECLAIMED")
    assert len(events) >= 1
    assert events[0].payload["stale_pid"] == 11111


def test_renew_and_release_singleton_lease(sqlite_temp_db: sqlite3.Connection):
    """Verifies renewing and releasing the supervisor singleton lease."""
    coordinator = LeaseCoordinator(sqlite_temp_db)

    assert coordinator.acquire_singleton_lease("sup-renew", holder_pid=33333, ttl_seconds=30) is True

    # Renew lease
    assert coordinator.renew_singleton_lease("sup-renew", holder_pid=33333, ttl_seconds=60) is True

    # Wrong PID cannot renew
    assert coordinator.renew_singleton_lease("sup-renew", holder_pid=44444, ttl_seconds=60) is False

    # Release lease
    assert coordinator.release_singleton_lease("sup-renew", holder_pid=33333) is True
    assert coordinator.get_singleton_lease() is None

    # Compatibility table also cleaned
    cursor = sqlite_temp_db.cursor()
    cursor.execute("SELECT * FROM supervisor_locks WHERE lock_name = 'SUPERVISOR_SINGLETON'")
    assert cursor.fetchone() is None


def test_project_lease_concurrency_baseline(sqlite_temp_db: sqlite3.Connection):
    """Verifies project lease enforces the 1 mutating job baseline."""
    coordinator = LeaseCoordinator(
        sqlite_temp_db,
        process_checker=lambda pid: True,
    )

    # Job 1 on project-alpha acquires mutating lock
    assert coordinator.acquire_project_lease(
        project_id="project-alpha",
        run_id="run-001",
        holder_pid=5001,
        is_mutating=True,
    ) is True

    # Job 2 on project-alpha cannot acquire mutating lock
    assert coordinator.acquire_project_lease(
        project_id="project-alpha",
        run_id="run-002",
        holder_pid=5002,
        is_mutating=True,
    ) is False

    # Job 3 on DIFFERENT project-beta CAN acquire mutating lock
    assert coordinator.acquire_project_lease(
        project_id="project-beta",
        run_id="run-003",
        holder_pid=5003,
        is_mutating=True,
    ) is True

    # Release project-alpha
    assert coordinator.release_project_lease("project-alpha", run_id="run-001") is True

    # Now Job 2 can acquire project-alpha
    assert coordinator.acquire_project_lease(
        project_id="project-alpha",
        run_id="run-002",
        holder_pid=5002,
        is_mutating=True,
    ) is True


def test_stale_project_lease_reclaimed(sqlite_temp_db: sqlite3.Connection):
    """Verifies dead or expired project lease is automatically reclaimed."""
    coordinator = LeaseCoordinator(
        sqlite_temp_db,
        process_checker=lambda pid: False,  # Holder is dead
    )

    past_iso = (datetime.now(timezone.utc) - timedelta(seconds=60)).isoformat()
    cursor = sqlite_temp_db.cursor()
    cursor.execute(
        """
        INSERT INTO leases (lease_name, holder_id, holder_pid, acquired_at, heartbeat_at, expires_at, metadata_json)
        VALUES ('PROJECT_stale-proj', 'old-run', 6001, ?, ?, ?, '{"is_mutating": true}')
        """,
        (past_iso, past_iso, past_iso),
    )
    sqlite_temp_db.commit()

    # New run claims project lock; successfully reclaims
    assert coordinator.acquire_project_lease(
        project_id="stale-proj",
        run_id="new-run",
        holder_pid=6002,
        is_mutating=True,
    ) is True

    record = coordinator.get_project_lease("stale-proj")
    assert record.holder_id == "new-run"
    assert record.holder_pid == 6002


def test_default_process_alive_check_current_process_is_non_destructive():
    """The liveness probe must never signal/terminate the process it inspects."""
    import os

    from sacl.supervisor.lease import default_process_alive_check

    assert default_process_alive_check(os.getpid()) is True
"""Unit tests for SACL V1 Cold-Start Recovery & Startup Reconciliation Engine."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from sacl.recovery.process_identity import MockProcessInspector
from sacl.recovery.startup_reconciliation import StartupReconciliationEngine
from sacl.recovery.worktree_inspection import MockGitClient


@pytest.fixture
def clean_db(sqlite_memory_db: sqlite3.Connection) -> sqlite3.Connection:
    return sqlite_memory_db


def test_cold_start_fresh_lease_claim_enters_idle(clean_db: sqlite3.Connection) -> None:
    """When no lease exists and no runs exist, acquires lease and enters IDLE."""
    engine = StartupReconciliationEngine(
        db_source=clean_db,
        supervisor_pid=10001,
        lease_ttl_seconds=60,
    )

    report = engine.execute_startup_reconciliation()
    assert report.lease_acquired is True
    assert report.stale_lock_reclaimed is False
    assert report.active_supervisor_conflict is False
    assert report.supervisor_state == "IDLE"
    assert report.interrupted_runs_count == 0

    # Verify lease record in database
    cursor = clean_db.cursor()
    cursor.execute("SELECT holder_pid FROM leases WHERE lease_name = 'SUPERVISOR_SINGLETON';")
    row = cursor.fetchone()
    assert row["holder_pid"] == 10001


def test_cold_start_active_supervisor_conflict_halts_cold_start(
    clean_db: sqlite3.Connection,
) -> None:
    """If another supervisor is actively running, halts immediately with SUPERVISOR_ALREADY_ACTIVE."""
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    expires_iso = (now + timedelta(seconds=60)).isoformat()

    # Pre-populate active lease held by PID 10002
    with clean_db:
        clean_db.execute(
            """
            INSERT INTO leases (lease_name, holder_id, holder_pid, acquired_at, heartbeat_at, expires_at)
            VALUES ('SUPERVISOR_SINGLETON', 'SUPERVISOR', 10002, ?, ?, ?);
            """,
            (now_iso, now_iso, expires_iso),
        )

    inspector = MockProcessInspector()
    # PID 10002 is actively running pwsh
    inspector.register_process(
        pid=10002,
        process_name="pwsh",
        is_active=True,
        start_time=now,
    )

    engine = StartupReconciliationEngine(
        db_source=clean_db,
        supervisor_pid=10003,
        inspector=inspector,
    )

    report = engine.execute_startup_reconciliation()
    assert report.active_supervisor_conflict is True
    assert report.lease_acquired is False
    assert report.supervisor_state == "HALTED_SAFETY"
    assert any("SUPERVISOR_ALREADY_ACTIVE" in err for err in report.errors)


def test_cold_start_stale_lock_reclaimed_from_dead_pid(clean_db: sqlite3.Connection) -> None:
    """If lease is held by a dead process, reclaims stale lock and acquires lease."""
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    expires_iso = (now + timedelta(seconds=60)).isoformat()

    with clean_db:
        clean_db.execute(
            """
            INSERT INTO leases (lease_name, holder_id, holder_pid, acquired_at, heartbeat_at, expires_at)
            VALUES ('SUPERVISOR_SINGLETON', 'SUPERVISOR', 10004, ?, ?, ?);
            """,
            (now_iso, now_iso, expires_iso),
        )

    inspector = MockProcessInspector()
    # PID 10004 has terminated
    inspector.register_process(
        pid=10004,
        process_name="pwsh",
        is_active=False,
        exit_code=1,
    )

    engine = StartupReconciliationEngine(
        db_source=clean_db,
        supervisor_pid=10005,
        inspector=inspector,
    )

    report = engine.execute_startup_reconciliation()
    assert report.active_supervisor_conflict is False
    assert report.stale_lock_reclaimed is True
    assert report.lease_acquired is True
    assert report.supervisor_state == "IDLE"

    cursor = clean_db.cursor()
    cursor.execute("SELECT holder_pid FROM leases WHERE lease_name = 'SUPERVISOR_SINGLETON';")
    row = cursor.fetchone()
    assert row["holder_pid"] == 10005


def test_cold_start_stale_lock_reclaimed_from_recycled_pid(clean_db: sqlite3.Connection) -> None:
    """If lease holder PID has recycled (drift > 300s), reclaims stale lock."""
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    expires_iso = (now + timedelta(seconds=60)).isoformat()

    with clean_db:
        clean_db.execute(
            """
            INSERT INTO leases (lease_name, holder_id, holder_pid, acquired_at, heartbeat_at, expires_at)
            VALUES ('SUPERVISOR_SINGLETON', 'SUPERVISOR', 10006, ?, ?, ?);
            """,
            (now_iso, now_iso, expires_iso),
        )

    inspector = MockProcessInspector()
    # PID 10006 is active, but started 500s later -> PID recycled!
    inspector.register_process(
        pid=10006,
        process_name="pwsh",
        is_active=True,
        start_time=now + timedelta(seconds=500),
    )

    engine = StartupReconciliationEngine(
        db_source=clean_db,
        supervisor_pid=10007,
        inspector=inspector,
    )

    report = engine.execute_startup_reconciliation()
    assert report.active_supervisor_conflict is False
    assert report.stale_lock_reclaimed is True
    assert report.lease_acquired is True


def test_cold_start_inspects_orphaned_worktrees(
    clean_db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    """Discovers orphaned worktrees on disk and preserves them for forensics."""
    wt_base = tmp_path / "worktrees"
    wt_base.mkdir()

    wt_orphan = wt_base / "orphan-wt-01"
    wt_orphan.mkdir()

    mock_git = MockGitClient()
    mock_git.set_status(wt_orphan, [])

    engine = StartupReconciliationEngine(
        db_source=clean_db,
        supervisor_pid=10008,
        git_client=mock_git,
    )

    report = engine.execute_startup_reconciliation(worktree_base_dir=wt_base)
    assert len(report.orphaned_worktrees) == 1
    assert "orphan-wt-01" in report.orphaned_worktrees[0].directory_path



@pytest.mark.parametrize(
    ("observed_name", "observed_offset_seconds", "has_start_time", "expected"),
    [
        ("pwsh", 0, True, True),
        ("pwsh", 299, True, True),
        ("pwsh", 301, True, False),
        ("untrusted-app", 0, True, False),
        ("pwsh", 0, False, False),
    ],
)
def test_recovery_pid_safety_is_three_factor_fail_closed(
    clean_db: sqlite3.Connection,
    observed_name: str,
    observed_offset_seconds: int,
    has_start_time: bool,
    expected: bool,
) -> None:
    """Do not treat recycled/unobservable PIDs as safe after restart."""
    recorded = datetime.now(timezone.utc)
    inspector = MockProcessInspector()
    inspector.register_process(
        pid=7712,
        process_name=observed_name,
        is_active=True,
        start_time=recorded + timedelta(seconds=observed_offset_seconds)
        if has_start_time else None,
    )
    engine = StartupReconciliationEngine(
        db_source=clean_db, supervisor_pid=8812, inspector=inspector,
    )
    assert engine.check_pid_safety(7712, recorded.isoformat()) is expected
    assert engine.check_pid_safety(-1, recorded.isoformat()) is False

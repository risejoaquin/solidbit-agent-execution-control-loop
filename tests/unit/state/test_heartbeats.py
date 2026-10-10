"""Unit tests for Heartbeat Monitoring and Process Liveness Tracking."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Generator

import pytest

from sacl.contracts.models import HeartbeatRecord
from sacl.state.connection import create_connection
from sacl.state.heartbeats import HeartbeatManager
from sacl.state.migrations import MigrationRunner


@pytest.fixture
def hb_db(migration_sql_path: Path) -> Generator[sqlite3.Connection, None, None]:
    conn = create_connection(":memory:")
    runner = MigrationRunner(migration_sql_path.parent)
    runner.apply_all(conn)
    yield conn
    conn.close()


def test_heartbeat_recording_and_retrieval(hb_db: sqlite3.Connection) -> None:
    mgr = HeartbeatManager(hb_db)

    hb_id = mgr.record_heartbeat(
        component="SUPERVISOR",
        instance_id="sup-main-1",
        pid=9001,
        status="IDLE",
        details={"active_tasks": 0, "token_burn": 0},
    )
    assert hb_id > 0

    latest = mgr.get_latest_heartbeat("SUPERVISOR", "sup-main-1")
    assert latest is not None
    assert latest["pid"] == 9001
    assert latest["status"] == "IDLE"
    assert latest["details"]["token_burn"] == 0


def test_heartbeat_record_model(hb_db: sqlite3.Connection) -> None:
    mgr = HeartbeatManager(hb_db)

    model = HeartbeatRecord(
        component="WORKER",
        instance_id="worker-ag-compat",
        pid=9002,
        status="BUSY",
        last_seen_at="2026-10-07T14:00:00Z",
        details={"current_phase": 1},
    )
    hb_id = mgr.record_heartbeat_model(model)
    assert hb_id > 0

    fetched = mgr.get_latest_heartbeat("WORKER", "worker-ag-compat")
    assert fetched["status"] == "BUSY"


def test_heartbeat_liveness_and_staleness(hb_db: sqlite3.Connection) -> None:
    mgr = HeartbeatManager(hb_db)

    # Fresh heartbeat recorded just now
    mgr.record_heartbeat("MAIL_GATEWAY", "gw-1", pid=5001, status="HEALTHY")
    assert mgr.check_liveness("MAIL_GATEWAY", "gw-1", max_stale_seconds=30) is True

    # Stale heartbeat in the past
    mgr.record_heartbeat(
        "WORKER",
        "worker-dead",
        pid=5002,
        status="CRASHED",
        last_seen_at="2020-01-01T00:00:00Z",
    )
    assert mgr.check_liveness("WORKER", "worker-dead", max_stale_seconds=30) is False

    stale_list = mgr.list_stale_instances(max_stale_seconds=60)
    stale_ids = [s["instance_id"] for s in stale_list]
    assert "worker-dead" in stale_ids
    assert "gw-1" not in stale_ids


def test_heartbeat_cleanup(hb_db: sqlite3.Connection) -> None:
    mgr = HeartbeatManager(hb_db)

    # Record historical row from 2 years ago
    mgr.record_heartbeat("OLD_PROC", "old-1", 1111, last_seen_at="2024-01-01T00:00:00Z")
    mgr.record_heartbeat("NEW_PROC", "new-1", 2222)

    deleted_count = mgr.cleanup_old_heartbeats(keep_seconds=86400)
    assert deleted_count >= 1

    assert mgr.get_latest_heartbeat("OLD_PROC", "old-1") is None
    assert mgr.get_latest_heartbeat("NEW_PROC", "new-1") is not None

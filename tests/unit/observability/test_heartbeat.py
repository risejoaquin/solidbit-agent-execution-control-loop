"""Unit tests for SACL V1 heartbeat recording and process liveness monitoring."""

import sqlite3
import threading
import time
from datetime import datetime, timezone, timedelta
import pytest

from sacl.observability.heartbeat import BackgroundHeartbeater, HeartbeatService


def test_record_and_get_latest_heartbeat(sqlite_temp_db: sqlite3.Connection):
    """Verifies recording heartbeats and retrieving the latest entry."""
    service = HeartbeatService(sqlite_temp_db)

    hb_id1 = service.record_heartbeat(
        component="SUPERVISOR",
        instance_id="sup-001",
        pid=2108,
        status="IDLE",
        details={"memory_mb": 45.2},
    )
    assert hb_id1 > 0

    hb_id2 = service.record_heartbeat(
        component="SUPERVISOR",
        instance_id="sup-001",
        pid=2108,
        status="BUSY",
        details={"memory_mb": 52.1},
    )
    assert hb_id2 > hb_id1

    latest = service.get_latest_heartbeat("SUPERVISOR", "sup-001")
    assert latest is not None
    assert latest.heartbeat_id == hb_id2
    assert latest.status == "BUSY"
    assert latest.details["memory_mb"] == 52.1


def test_list_heartbeats(sqlite_temp_db: sqlite3.Connection):
    """Verifies listing heartbeats with optional component filter."""
    service = HeartbeatService(sqlite_temp_db)

    service.record_heartbeat("SUPERVISOR", "s1", 100)
    service.record_heartbeat("MAIL_GATEWAY", "m1", 200)
    service.record_heartbeat("WORKER", "w1", 300)

    all_hb = service.list_heartbeats()
    assert len(all_hb) == 3

    gw_hb = service.list_heartbeats(component="MAIL_GATEWAY")
    assert len(gw_hb) == 1
    assert gw_hb[0].component == "MAIL_GATEWAY"


def test_check_liveness_and_stale_detection(sqlite_temp_db: sqlite3.Connection):
    """Verifies liveness checks against TTL and stale process detection."""
    service = HeartbeatService(sqlite_temp_db)

    # 1. Non-existent component is dead
    is_alive, hb = service.check_liveness("WORKER", "non-existent", ttl_seconds=10)
    assert is_alive is False
    assert hb is None

    # 2. Fresh heartbeat is alive
    service.record_heartbeat("WORKER", "worker-live", 400, status="HEALTHY")
    is_alive_now, hb_live = service.check_liveness("WORKER", "worker-live", ttl_seconds=60)
    assert is_alive_now is True
    assert hb_live is not None

    # 3. Simulate stale heartbeat by manually inserting past timestamp
    past_iso = (datetime.now(timezone.utc) - timedelta(seconds=120)).isoformat()
    cursor = sqlite_temp_db.cursor()
    cursor.execute(
        """
        INSERT INTO heartbeats (component, instance_id, pid, status, last_seen_at, details_json)
        VALUES ('SUPERVISOR', 'stale-daemon', 500, 'HEALTHY', ?, '{}')
        """,
        (past_iso,),
    )
    sqlite_temp_db.commit()

    is_alive_stale, hb_stale = service.check_liveness("SUPERVISOR", "stale-daemon", ttl_seconds=60)
    assert is_alive_stale is False
    assert hb_stale is not None

    stale_list = service.detect_stale_processes(ttl_seconds=60)
    stale_instances = [s.instance_id for s in stale_list]
    assert "stale-daemon" in stale_instances
    assert "worker-live" not in stale_instances


def test_background_heartbeater_context_manager(sqlite_temp_db: sqlite3.Connection):
    """Verifies BackgroundHeartbeater emits periodic heartbeats and stops cleanly."""
    service = HeartbeatService(sqlite_temp_db)

    tick_event = threading.Event()
    counter = {"count": 0}

    def get_details():
        counter["count"] += 1
        if counter["count"] >= 2:
            tick_event.set()
        return {"ticks": counter["count"]}

    with BackgroundHeartbeater(
        service=service,
        component="TEST_DAEMON",
        instance_id="inst-bg",
        pid=9999,
        interval_seconds=0.02,
        status="RUNNING",
        details_fn=get_details,
    ):
        assert tick_event.wait(timeout=2.0), "Timed out waiting for at least 2 heartbeats"
        time.sleep(0.05)

    # Verify heartbeats were emitted
    beats = service.list_heartbeats(component="TEST_DAEMON")
    assert len(beats) >= 2
    assert beats[0].component == "TEST_DAEMON"
    assert beats[0].instance_id == "inst-bg"

"""Tests for users.watch Lifecycle Manager & Expiration Persistence."""

from __future__ import annotations

import datetime
import sqlite3

from sacl.transport.gmail_adapter import MockGmailApiAdapter
from sacl.transport.watch import (
    DEFAULT_CURSOR_NAME,
    WatchLifecycleManager,
    parse_expiration_timestamp,
)


def test_parse_expiration_timestamp_from_ms() -> None:
    # 1791460800000 = 2026-10-14 12:00:00 UTC approx
    iso = parse_expiration_timestamp("1791460800000")
    assert "2026" in iso
    assert "T" in iso


def test_register_watch_persists_to_sqlite(sqlite_memory_db: sqlite3.Connection) -> None:
    adapter = MockGmailApiAdapter()
    manager = WatchLifecycleManager(gmail_adapter=adapter, db_conn=sqlite_memory_db)

    res = manager.register_watch(topic_name="projects/p/topics/t")
    assert res["cursor_name"] == DEFAULT_CURSOR_NAME
    assert res["history_id"] == "100000"
    assert res["resource_id"] == "projects/p/topics/t"

    active = manager.get_active_watch_cursor()
    assert active is not None
    assert active["history_id"] == "100000"
    assert active["resource_id"] == "projects/p/topics/t"
    assert active["expiration_at"] is not None


def test_check_and_renew_watch_lifecycle(sqlite_memory_db: sqlite3.Connection) -> None:
    adapter = MockGmailApiAdapter()
    manager = WatchLifecycleManager(gmail_adapter=adapter, db_conn=sqlite_memory_db)

    # 1. No record -> renews
    renewed = manager.check_and_renew_watch("projects/p/topics/t")
    assert renewed is True

    # 2. Fresh record (expires in ~7 days) -> does NOT renew
    renewed_again = manager.check_and_renew_watch(
        "projects/p/topics/t", renewal_threshold_seconds=86400
    )
    assert renewed_again is False

    # 3. Simulate expiring lease (e.g. expires in 2 hours, threshold is 24 hours)
    near_expiry = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)
    cursor = sqlite_memory_db.cursor()
    cursor.execute(
        "UPDATE mail_cursors SET expiration_at = ? WHERE cursor_name = ?",
        (near_expiry.isoformat(), DEFAULT_CURSOR_NAME),
    )
    sqlite_memory_db.commit()

    renewed_expiring = manager.check_and_renew_watch(
        "projects/p/topics/t", renewal_threshold_seconds=86400
    )
    assert renewed_expiring is True


def test_stop_watch(sqlite_memory_db: sqlite3.Connection) -> None:
    adapter = MockGmailApiAdapter()
    manager = WatchLifecycleManager(gmail_adapter=adapter, db_conn=sqlite_memory_db)

    manager.register_watch("projects/p/topics/t")
    manager.stop_watch()

    assert adapter.stop_called is True
    active = manager.get_active_watch_cursor()
    assert active["expiration_at"] is None

"""Tests for FallbackPoller & Degraded Mode Safety Polling."""

from __future__ import annotations

import io
import sqlite3
import zipfile
from pathlib import Path

from sacl.transport.gmail_adapter import MockGmailApiAdapter
from sacl.transport.polling import FallbackPoller
from sacl.transport.reconciliation import HistoryReconciliationManager


def create_package_zip(job_id: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("manifest.json", f'{{"job_id": "{job_id}"}}')
    return buf.getvalue()


def test_fallback_poller_interval_check(
    sqlite_memory_db: sqlite3.Connection, tmp_path: Path
) -> None:
    adapter = MockGmailApiAdapter()
    recon = HistoryReconciliationManager(
        gmail_adapter=adapter, db_conn=sqlite_memory_db, staging_root=tmp_path
    )
    poller = FallbackPoller(
        gmail_adapter=adapter,
        reconciliation_manager=recon,
        db_conn=sqlite_memory_db,
        min_interval_seconds=300,
    )

    # First check: should poll
    assert poller.should_poll() is True

    # Run poll
    poller.poll_mailbox()

    # Immediate second check: should not poll without force
    assert poller.should_poll(force=False) is False
    assert poller.should_poll(force=True) is True


def test_fallback_poller_ingests_unhandled_messages(
    sqlite_memory_db: sqlite3.Connection, tmp_path: Path
) -> None:
    adapter = MockGmailApiAdapter()
    recon = HistoryReconciliationManager(
        gmail_adapter=adapter, db_conn=sqlite_memory_db, staging_root=tmp_path
    )
    poller = FallbackPoller(
        gmail_adapter=adapter,
        reconciliation_manager=recon,
        db_conn=sqlite_memory_db,
    )

    zip_bytes = create_package_zip("W-POLL")
    adapter.add_mock_message(
        message_id="msg-polled-1",
        sender="uniquedraken@gmail.com",
        recipient="uniquedraken@gmail.com",
        subject="[SACL][JOB][v1][W-POLL] Fallback Message",
        attachment_bytes=zip_bytes,
    )

    res = poller.poll_mailbox(force=True)
    assert res.messages_found >= 1
    assert res.unhandled_messages_processed == 1
    assert "W-POLL" in res.jobs_ingested

    # Second poll should find it already handled
    res2 = poller.poll_mailbox(force=True)
    assert res2.unhandled_messages_processed == 0


def test_recover_from_stale_cursor(sqlite_memory_db: sqlite3.Connection, tmp_path: Path) -> None:
    adapter = MockGmailApiAdapter()
    recon = HistoryReconciliationManager(
        gmail_adapter=adapter, db_conn=sqlite_memory_db, staging_root=tmp_path
    )
    poller = FallbackPoller(
        gmail_adapter=adapter,
        reconciliation_manager=recon,
        db_conn=sqlite_memory_db,
    )

    zip_bytes = create_package_zip("W-RECOVER")
    adapter.add_mock_message(
        message_id="msg-rec-1",
        sender="uniquedraken@gmail.com",
        recipient="uniquedraken@gmail.com",
        subject="[SACL][JOB][v1][W-RECOVER] Recovery",
        attachment_bytes=zip_bytes,
    )

    # Calling recover_from_stale_cursor
    res = poller.recover_from_stale_cursor()
    assert "W-RECOVER" in res.jobs_ingested

    # Cursor should be updated
    cursor = sqlite_memory_db.cursor()
    cursor.execute("SELECT history_id FROM mail_cursors WHERE cursor_name = 'GMAIL_USERS_WATCH'")
    row = cursor.fetchone()
    assert row is not None
    assert row[0] == adapter.current_history_id

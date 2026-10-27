"""Tests for HistoryReconciliationManager & Deduplication Matrix."""

from __future__ import annotations

import io
import sqlite3
import zipfile
from pathlib import Path

from sacl.transport.gmail_adapter import MockGmailApiAdapter
from sacl.transport.reconciliation import HistoryReconciliationManager


def create_package_zip(job_id: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("manifest.json", f'{{"job_id": "{job_id}"}}')
        zf.writestr("prompts/task.md", "# Instructions")
    return buf.getvalue()


def test_reconcile_history_ingests_valid_package(
    sqlite_memory_db: sqlite3.Connection, tmp_path: Path
) -> None:
    adapter = MockGmailApiAdapter()
    manager = HistoryReconciliationManager(
        gmail_adapter=adapter,
        db_conn=sqlite_memory_db,
        staging_root=tmp_path,
        authorized_sender="uniquedraken@gmail.com",
    )

    zip_bytes = create_package_zip("W0")
    adapter.add_mock_message(
        message_id="msg-1",
        sender="uniquedraken@gmail.com",
        recipient="uniquedraken@gmail.com",
        subject="[SACL][JOB][v1][W0] Wave 0 Ingestion",
        attachment_filename="wave0.zip",
        attachment_bytes=zip_bytes,
    )

    res = manager.reconcile_history(start_history_id="100000")
    assert res.messages_inspected == 1
    assert "W0" in res.jobs_ingested
    assert len(res.duplicates_ignored) == 0
    assert len(res.conflicts_rejected) == 0

    # Verify SQLite mail_messages
    cursor = sqlite_memory_db.cursor()
    cursor.execute("SELECT status, job_id, run_id FROM mail_messages WHERE message_id = 'msg-1'")
    row = cursor.fetchone()
    assert row is not None
    assert row[0] == "PERSISTED"
    assert row[1] == "W0"

    # Verify staging directory
    run_id = row[2]
    staged_manifest = tmp_path / "packages" / "inbox" / run_id / "manifest.json"
    assert staged_manifest.exists()

    # Verify cursor advanced
    assert manager.get_persisted_cursor() == adapter.current_history_id


def test_reconcile_unauthorized_sender_quarantined(
    sqlite_memory_db: sqlite3.Connection, tmp_path: Path
) -> None:
    adapter = MockGmailApiAdapter()
    manager = HistoryReconciliationManager(
        gmail_adapter=adapter,
        db_conn=sqlite_memory_db,
        staging_root=tmp_path,
        authorized_sender="uniquedraken@gmail.com",
    )

    zip_bytes = create_package_zip("W0")
    adapter.add_mock_message(
        message_id="msg-malicious",
        sender="attacker@evil.com",
        recipient="uniquedraken@gmail.com",
        subject="[SACL][JOB][v1][W0] Wave 0",
        attachment_bytes=zip_bytes,
    )

    res = manager.reconcile_history(start_history_id="100000")
    assert "msg-malicious" in res.quarantined
    assert len(res.jobs_ingested) == 0

    cursor = sqlite_memory_db.cursor()
    cursor.execute(
        "SELECT status, rejection_reason FROM mail_messages WHERE message_id = 'msg-malicious'"
    )
    row = cursor.fetchone()
    assert row[0] == "QUARANTINED"
    assert "SENDER_NOT_WHITELISTED" in row[1]


def test_reconcile_duplicate_message_ignored(
    sqlite_memory_db: sqlite3.Connection, tmp_path: Path
) -> None:
    adapter = MockGmailApiAdapter()
    manager = HistoryReconciliationManager(
        gmail_adapter=adapter,
        db_conn=sqlite_memory_db,
        staging_root=tmp_path,
        authorized_sender="uniquedraken@gmail.com",
    )

    zip_bytes = create_package_zip("W0")
    adapter.add_mock_message(
        message_id="msg-1",
        sender="uniquedraken@gmail.com",
        recipient="uniquedraken@gmail.com",
        subject="[SACL][JOB][v1][W0] Wave 0",
        attachment_bytes=zip_bytes,
    )

    # First pass: ingested
    res1 = manager.reconcile_history(start_history_id="100000")
    assert "W0" in res1.jobs_ingested

    # Second pass over same start_id: duplicate ignored
    res2 = manager.reconcile_history(start_history_id="100000")
    assert "msg-1" in res2.duplicates_ignored
    assert len(res2.jobs_ingested) == 0


def test_reconcile_payload_hash_conflict_rejected(
    sqlite_memory_db: sqlite3.Connection, tmp_path: Path
) -> None:
    adapter = MockGmailApiAdapter()
    manager = HistoryReconciliationManager(
        gmail_adapter=adapter,
        db_conn=sqlite_memory_db,
        staging_root=tmp_path,
        authorized_sender="uniquedraken@gmail.com",
    )

    zip1 = create_package_zip("JOB-CONCURRENT")
    adapter.add_mock_message(
        message_id="msg-original",
        sender="uniquedraken@gmail.com",
        recipient="uniquedraken@gmail.com",
        subject="[SACL][JOB][v1][JOB-CONCURRENT] Initial",
        attachment_bytes=zip1,
    )
    res1 = manager.reconcile_history(start_history_id="100000")
    assert "JOB-CONCURRENT" in res1.jobs_ingested

    # New message with same JOB_ID but different zip content
    zip2 = zip1 + b"\x00_tampered_extra_bytes"
    adapter.add_mock_message(
        message_id="msg-conflicting",
        sender="uniquedraken@gmail.com",
        recipient="uniquedraken@gmail.com",
        subject="[SACL][JOB][v1][JOB-CONCURRENT] Conflicting Submission",
        attachment_bytes=zip2,
    )

    res2 = manager.reconcile_history(start_history_id=manager.get_persisted_cursor())
    assert "msg-conflicting" in res2.conflicts_rejected

    # Verify conflict reply queued in mail_outbox
    cursor = sqlite_memory_db.cursor()
    cursor.execute(
        "SELECT recipient, subject, status FROM mail_outbox WHERE run_id = 'conflict-JOB-CONCURRENT'"
    )
    outbox_row = cursor.fetchone()
    assert outbox_row is not None
    assert outbox_row[0] == "uniquedraken@gmail.com"
    assert "REJECTED (Hash Conflict)" in outbox_row[1]
    assert outbox_row[2] == "QUEUED"

"""Tests for OutboxDispatcher & Outbound Mail Dispatch."""

from __future__ import annotations

import email
import sqlite3
from pathlib import Path

from sacl.transport.gmail_adapter import MockGmailApiAdapter
from sacl.transport.outbox import OutboxDispatcher


def test_enqueue_reply(sqlite_memory_db: sqlite3.Connection) -> None:
    adapter = MockGmailApiAdapter()
    dispatcher = OutboxDispatcher(gmail_adapter=adapter, db_conn=sqlite_memory_db)

    outbox_id = dispatcher.enqueue_reply(
        run_id="run-100",
        recipient="uniquedraken@gmail.com",
        subject="[SACL][RESULT][v1][W0] - PASS (Run: run-100)",
        body_markdown="# Execution Passed",
    )
    assert outbox_id > 0

    cursor = sqlite_memory_db.cursor()
    cursor.execute(
        "SELECT status, attempts, recipient FROM mail_outbox WHERE outbox_id = ?", (outbox_id,)
    )
    row = cursor.fetchone()
    assert row[0] == "QUEUED"
    assert row[1] == 0
    assert row[2] == "uniquedraken@gmail.com"


def test_dispatch_pending_success(sqlite_memory_db: sqlite3.Connection, tmp_path: Path) -> None:
    adapter = MockGmailApiAdapter()
    dispatcher = OutboxDispatcher(gmail_adapter=adapter, db_conn=sqlite_memory_db)

    # Create dummy attachment
    attach_file = tmp_path / "RESPONSE_run-100.zip"
    attach_file.write_bytes(b"PK\x03\x04test_zip")

    # Seed originating inbound message in mail_messages for thread correlation
    cursor = sqlite_memory_db.cursor()
    cursor.execute(
        """
        INSERT INTO mail_messages (
            message_id, history_id, thread_id, sender, recipient,
            subject, snippet, received_at, nonce, attachment_sha, status, run_id
        ) VALUES (
            '<origin-msg-1@gmail.com>', '100', 'thread-orig-1', 'uniquedraken@gmail.com',
            'uniquedraken@gmail.com', 'Subject', 'Snippet', '2026-10-07T12:00:00Z',
            'nonce12345678', 'sha', 'PERSISTED', 'run-100'
        )
        """
    )
    sqlite_memory_db.commit()

    outbox_id = dispatcher.enqueue_reply(
        run_id="run-100",
        recipient="uniquedraken@gmail.com",
        subject="[SACL][RESULT][v1][W0] - PASS (Run: run-100)",
        body_markdown="# Summary Report",
        attachment_path=str(attach_file),
    )

    dispatched = dispatcher.dispatch_pending()
    assert dispatched == 1
    assert len(adapter.sent_messages) == 1

    sent = adapter.sent_messages[0]
    assert sent["threadId"] == "thread-orig-1"

    parsed_msg = email.message_from_bytes(sent["raw_mime_bytes"])
    assert parsed_msg["In-Reply-To"] == "<origin-msg-1@gmail.com>"
    assert parsed_msg["References"] == "<origin-msg-1@gmail.com>"

    # Check status in SQLite
    cursor.execute(
        "SELECT status, attempts, sent_at FROM mail_outbox WHERE outbox_id = ?", (outbox_id,)
    )
    row = cursor.fetchone()
    assert row[0] == "SENT"
    assert row[1] == 1
    assert row[2] is not None


def test_dispatch_pending_retry_and_permanent_failure(
    sqlite_memory_db: sqlite3.Connection,
) -> None:
    adapter = MockGmailApiAdapter()
    # Force send failures
    adapter.server_error_failures_remaining = 10
    slept = []
    dispatcher = OutboxDispatcher(
        gmail_adapter=adapter,
        db_conn=sqlite_memory_db,
        max_retries=3,
        backoff_steps=[0.01, 0.02, 0.03],
        sleeper=lambda s: slept.append(s),
    )

    outbox_id = dispatcher.enqueue_reply(
        run_id="run-fail",
        recipient="uniquedraken@gmail.com",
        subject="Subj",
        body_markdown="Body",
    )

    dispatched = dispatcher.dispatch_pending()
    assert dispatched == 0
    assert len(slept) == 2  # slept twice before 3rd attempt failed

    cursor = sqlite_memory_db.cursor()
    cursor.execute(
        "SELECT status, attempts, error_log FROM mail_outbox WHERE outbox_id = ?", (outbox_id,)
    )
    row = cursor.fetchone()
    assert row[0] == "FAILED"
    assert row[1] == 3
    assert "503" in row[2]

"""Tests for Result Outbox Handoff Subsystem.

Adheres to:
- docs/MAIL_PROTOCOL.md §4, §5.1 (Routing hint subject syntax, outbox queueing)
- STATE_MACHINE.md (Lifecycle progression RESULT_PACKAGED -> RESULT_SENT)
- Domain 16 / Compatibility Table 7 (SQLite mail_outbox table)
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from unittest.mock import MagicMock
import pytest

from sacl.results.outbox import (
    DEFAULT_RESULT_RECIPIENT,
    ResultOutboxHandoff,
    format_result_subject,
)


@pytest.fixture
def seeded_db(sqlite_memory_db: sqlite3.Connection):
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cursor = sqlite_memory_db.cursor()

    cursor.execute(
        """
        INSERT INTO jobs (job_id, status, priority, created_at, updated_at)
        VALUES ('job-out-001', 'RESULT_PACKAGED', 0, ?, ?)
        """,
        (now_iso, now_iso),
    )
    cursor.execute(
        """
        INSERT INTO runs (
            run_id, job_id, package_id, project, repository, mode,
            source_orchestrator, target_repo_path, run_dir, status,
            ready_for_integration, started_at
        ) VALUES (
            'run-out-001', 'job-out-001', 'pkg-001', 'solidbit', 'org/repo', 'isolated_branch',
            '', '', '', 'RESULT_PACKAGED', 'YES', ?
        )
        """,
        (now_iso,),
    )
    cursor.execute(
        """
        INSERT INTO results (
            job_id, run_id, status, final_verdict, summary_md_path, summary_json_path,
            package_result_zip, created_at
        ) VALUES (
            'job-out-001', 'run-out-001', 'RESULT_PACKAGED', 'PASS', 'SUMMARY.md', 'SUMMARY.json',
            'run-out-001-result.zip', ?
        )
        """,
        (now_iso,),
    )
    sqlite_memory_db.commit()
    return sqlite_memory_db


def test_format_result_subject() -> None:
    subj = format_result_subject(job_id="job-123", verdict="PASS")
    assert subj == "[SACL][JOB][v1][job-123] [RESULT] PASS"


def test_enqueue_result_to_outbox(seeded_db: sqlite3.Connection) -> None:
    handoff = ResultOutboxHandoff()

    outbox_id = handoff.enqueue_result_to_outbox(
        run_id="run-out-001",
        job_id="job-out-001",
        body_markdown="# SUMMARY MD\nVerdict: PASS",
        attachment_path="artifacts/response.zip",
        final_verdict="PASS",
        db_conn=seeded_db,
    )

    assert outbox_id > 0
    cursor = seeded_db.cursor()
    cursor.execute(
        "SELECT run_id, recipient, subject, status, attempts FROM mail_outbox WHERE outbox_id = ?",
        (outbox_id,),
    )
    row = cursor.fetchone()
    assert row[0] == "run-out-001"
    assert row[1] == DEFAULT_RESULT_RECIPIENT
    assert row[2] == "[SACL][JOB][v1][job-out-001] [RESULT] PASS"
    assert row[3] == "QUEUED"
    assert row[4] == 0

    # Check results table updated delivered_to
    cursor.execute("SELECT delivered_to FROM results WHERE run_id = 'run-out-001'")
    assert cursor.fetchone()[0] == DEFAULT_RESULT_RECIPIENT


def test_dispatch_outbox_item_success(seeded_db: sqlite3.Connection) -> None:
    handoff = ResultOutboxHandoff()
    outbox_id = handoff.enqueue_result_to_outbox(
        run_id="run-out-001",
        job_id="job-out-001",
        body_markdown="# Test Summary",
        attachment_path="result.zip",
        final_verdict="PASS",
        db_conn=seeded_db,
    )

    mock_dispatcher = MagicMock()

    dispatch_res = handoff.dispatch_outbox_item(
        outbox_id=outbox_id,
        db_conn=seeded_db,
        dispatcher=mock_dispatcher,
    )

    assert dispatch_res.dispatched is True
    assert dispatch_res.status == "SENT"

    # Verify mail_outbox row transitioned to SENT
    cursor = seeded_db.cursor()
    cursor.execute("SELECT status, sent_at, attempts FROM mail_outbox WHERE outbox_id = ?", (outbox_id,))
    row = cursor.fetchone()
    assert row[0] == "SENT"
    assert row[1] is not None
    assert row[2] == 1

    # Verify results table delivery confirmed
    cursor.execute("SELECT status, delivered_at FROM results WHERE run_id = 'run-out-001'")
    r_row = cursor.fetchone()
    assert r_row[0] == "RESULT_SENT"
    assert r_row[1] is not None

    # Verify runs table transitioned to RESULT_SENT
    cursor.execute("SELECT status FROM runs WHERE run_id = 'run-out-001'")
    assert cursor.fetchone()[0] == "RESULT_SENT"

    # Verify jobs table transitioned to RESULT_SENT
    cursor.execute("SELECT status FROM jobs WHERE job_id = 'job-out-001'")
    assert cursor.fetchone()[0] == "RESULT_SENT"


def test_dispatch_outbox_item_queued_when_no_dispatcher(seeded_db: sqlite3.Connection) -> None:
    handoff = ResultOutboxHandoff()
    outbox_id = handoff.enqueue_result_to_outbox(
        run_id="run-out-001",
        job_id="job-out-001",
        body_markdown="# Test Summary",
        attachment_path="result.zip",
        final_verdict="PASS",
        db_conn=seeded_db,
    )

    res = handoff.dispatch_outbox_item(outbox_id=outbox_id, db_conn=seeded_db, dispatcher=None)
    assert res.dispatched is False
    assert res.status == "QUEUED"


def test_dispatch_outbox_item_failure_recorded(seeded_db: sqlite3.Connection) -> None:
    handoff = ResultOutboxHandoff()
    outbox_id = handoff.enqueue_result_to_outbox(
        run_id="run-out-001",
        job_id="job-out-001",
        body_markdown="# Test Summary",
        attachment_path="result.zip",
        final_verdict="PASS",
        db_conn=seeded_db,
    )

    failing_dispatcher = MagicMock()
    failing_dispatcher.dispatch_outbox_reply.side_effect = RuntimeError("Gmail API 503 Backend Unavailable")

    res = handoff.dispatch_outbox_item(
        outbox_id=outbox_id,
        db_conn=seeded_db,
        dispatcher=failing_dispatcher,
    )

    assert res.dispatched is False
    assert res.status == "FAILED"
    assert "Gmail API 503" in res.error_message

    cursor = seeded_db.cursor()
    cursor.execute("SELECT attempts, error_log FROM mail_outbox WHERE outbox_id = ?", (outbox_id,))
    row = cursor.fetchone()
    assert row[0] == 1
    assert "Gmail API 503" in row[1]

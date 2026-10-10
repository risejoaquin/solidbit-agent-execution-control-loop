"""Unit tests for SACL V1 Idempotency, Deduplication, and Anti-Replay Engine.

Covers InboundAction classification (DUPLICATE_IGNORED, PAYLOAD_CONFLICT_REJECTED,
ATTEMPT_STAGED, ACCEPTED_QUEUED), nonce verification, monotonic Gmail cursor advancement,
and atomic status transitions.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path
from typing import Generator

# Ensure repo root is on sys.path
_repo_root = Path(__file__).resolve().parents[3]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

import pytest

from sacl.state.connection import create_connection
from sacl.state.idempotency import IdempotencyHelper, InboundAction
from sacl.state.migrations import MigrationRunner
from sacl.state.repositories.jobs import JobRepository
from sacl.state.repositories.mail import MailRepository
from sacl.state.repositories.packages import PackageRepository
from sacl.state.repositories.projects import ProjectRepository
from sacl.state.repositories.runs import RunRepository


@pytest.fixture
def idem_db(migration_sql_path: Path) -> Generator[sqlite3.Connection, None, None]:
    conn = create_connection(":memory:")
    runner = MigrationRunner(migration_sql_path.parent)
    runner.apply_all(conn)
    yield conn
    conn.close()


def test_nonce_seen_detection(idem_db: sqlite3.Connection) -> None:
    """Verifies anti-replay cryptographic nonce detection."""
    helper = IdempotencyHelper(idem_db)
    mail_repo = MailRepository(idem_db)

    assert helper.is_nonce_seen("nonce-random-999") is False

    # Record message with nonce
    mail_repo.record_inbound_message(
        message_id="msg-nonce-1@mail.gmail.com",
        sender="uniquedraken@gmail.com",
        recipient="uniquedraken@gmail.com",
        subject="[SACL][JOB][v1]",
        nonce="nonce-random-999",
        attachment_sha="sha256-abc",
    )
    assert helper.is_nonce_seen("nonce-random-999") is True


def test_evaluate_inbound_novel_job(idem_db: sqlite3.Connection) -> None:
    """Verifies that an unseen JOB_ID produces ACCEPTED_QUEUED."""
    helper = IdempotencyHelper(idem_db)

    result = helper.evaluate_inbound_package(
        job_id="job-novel-1",
        package_sha256="hash-1111",
    )
    assert result.action == InboundAction.ACCEPTED_QUEUED
    assert result.job_id == "job-novel-1"
    assert result.attempt_number == 1


def test_evaluate_inbound_duplicate_redelivery(idem_db: sqlite3.Connection) -> None:
    """Verifies that re-receiving identical package hash results in DUPLICATE_IGNORED."""
    ProjectRepository(idem_db).register_project("proj-1", "P1", "C:/repos/p1")
    pkg_repo = PackageRepository(idem_db)
    job_repo = JobRepository(idem_db)
    helper = IdempotencyHelper(idem_db)

    # Setup existing job and package with hash-aaa
    pkg_repo.record_package(
        package_id="pkg-aaa",
        archive_sha256="hash-aaa",
        manifest={"job_id": "job-existing-1"},
        storage_path="packages/pkg-aaa.zip",
        project_id="proj-1",
    )
    job_repo.create_job(
        job_id="job-existing-1",
        package_id="pkg-aaa",
        project_id="proj-1",
        status="QUEUED",
    )

    # Incoming package with same JOB_ID and identical hash -> DUPLICATE_IGNORED
    result = helper.evaluate_inbound_package(
        job_id="job-existing-1",
        package_sha256="hash-aaa",
        is_explicit_retry=False,
    )
    assert result.action == InboundAction.DUPLICATE_IGNORED
    assert "Duplicate redelivery" in result.message


def test_evaluate_inbound_payload_conflict(idem_db: sqlite3.Connection) -> None:
    """Verifies that same JOB_ID with different SHA-256 is rejected with PAYLOAD_CONFLICT_REJECTED."""
    ProjectRepository(idem_db).register_project("proj-1", "P1", "C:/repos/p1")
    pkg_repo = PackageRepository(idem_db)
    job_repo = JobRepository(idem_db)
    helper = IdempotencyHelper(idem_db)

    pkg_repo.record_package(
        package_id="pkg-bbb",
        archive_sha256="hash-original",
        manifest={"job_id": "job-conflict-1"},
        storage_path="packages/pkg-bbb.zip",
        project_id="proj-1",
    )
    job_repo.create_job(
        job_id="job-conflict-1",
        package_id="pkg-bbb",
        project_id="proj-1",
        status="RUNNING",
    )

    # Incoming package with conflicting hash
    result = helper.evaluate_inbound_package(
        job_id="job-conflict-1",
        package_sha256="hash-tampered-or-different",
        is_explicit_retry=False,
    )
    assert result.action == InboundAction.PAYLOAD_CONFLICT_REJECTED
    assert "Conflicting payload" in result.message


def test_evaluate_inbound_legitimate_retry(idem_db: sqlite3.Connection) -> None:
    """Verifies that same JOB_ID with identical hash and is_explicit_retry=True stages attempt."""
    ProjectRepository(idem_db).register_project("proj-1", "P1", "C:/repos/p1")
    pkg_repo = PackageRepository(idem_db)
    job_repo = JobRepository(idem_db)
    run_repo = RunRepository(idem_db)
    helper = IdempotencyHelper(idem_db)

    pkg_repo.record_package(
        package_id="pkg-ccc",
        archive_sha256="hash-verified-ccc",
        manifest={"job_id": "job-retry-1"},
        storage_path="packages/pkg-ccc.zip",
        project_id="proj-1",
    )
    job_repo.create_job(
        job_id="job-retry-1",
        package_id="pkg-ccc",
        project_id="proj-1",
        status="FAILED",
    )
    # Record first attempt run
    run_repo.create_run(
        run_id="run-retry-attempt-1",
        job_id="job-retry-1",
        package_id="pkg-ccc",
        project="proj-1",
        project_id="proj-1",
        repository="org/repo",
        mode="isolated_branch",
        source_orchestrator="C:/orch",
        target_repo_path="C:/repos/p1",
        run_dir="runs/r1",
        status="FAILED",
    )

    # Incoming retry request
    result = helper.evaluate_inbound_package(
        job_id="job-retry-1",
        package_sha256="hash-verified-ccc",
        is_explicit_retry=True,
    )
    assert result.action == InboundAction.ATTEMPT_STAGED
    assert result.attempt_number == 2
    assert result.job_id == "job-retry-1"


def test_monotonic_history_cursor_advancement(idem_db: sqlite3.Connection) -> None:
    """Verifies Gmail historyId cursor monotonic progression invariant."""
    helper = IdempotencyHelper(idem_db)
    mail_repo = MailRepository(idem_db)

    # Initial cursor advance to 50000
    adv1 = helper.advance_history_cursor_monotonic("GMAIL_WATCH", "50000")
    assert adv1 is True
    assert mail_repo.get_cursor("GMAIL_WATCH")["history_id"] == "50000"

    # Monotonic forward advance to 50100 succeeds
    adv2 = helper.advance_history_cursor_monotonic("GMAIL_WATCH", "50100")
    assert adv2 is True
    assert mail_repo.get_cursor("GMAIL_WATCH")["history_id"] == "50100"

    # Regressive update to 49999 rejected
    adv_regressive = helper.advance_history_cursor_monotonic("GMAIL_WATCH", "49999")
    assert adv_regressive is False
    assert mail_repo.get_cursor("GMAIL_WATCH")["history_id"] == "50100"


def test_atomic_transition_helper(idem_db: sqlite3.Connection) -> None:
    """Verifies atomic state transition guard."""
    helper = IdempotencyHelper(idem_db)
    job_repo = JobRepository(idem_db)

    job_repo.create_job("job-atomic", None, None, status="RECEIVED")

    # Transition from expected 'RECEIVED' to 'AUTHENTICATED' succeeds
    success = helper.atomic_transition(
        table="jobs",
        id_column="job_id",
        id_value="job-atomic",
        expected_status="RECEIVED",
        target_status="AUTHENTICATED",
    )
    assert success is True
    assert job_repo.get_job("job-atomic")["status"] == "AUTHENTICATED"

    # Transition expecting 'RECEIVED' again fails (already 'AUTHENTICATED')
    failed = helper.atomic_transition(
        table="jobs",
        id_column="job_id",
        id_value="job-atomic",
        expected_status="RECEIVED",
        target_status="VALIDATED",
    )
    assert failed is False
    assert job_repo.get_job("job-atomic")["status"] == "AUTHENTICATED"

    # Transition with sequence of expected statuses
    success_multi = helper.atomic_transition(
        table="jobs",
        id_column="job_id",
        id_value="job-atomic",
        expected_status=["AUTHENTICATED", "PERSISTED"],
        target_status="VALIDATED",
    )
    assert success_multi is True
    assert job_repo.get_job("job-atomic")["status"] == "VALIDATED"

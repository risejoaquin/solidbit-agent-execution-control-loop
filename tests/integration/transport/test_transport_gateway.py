"""End-to-End Integration Tests for MailGateway Subsystem."""

from __future__ import annotations

import io
import sqlite3
import zipfile
from pathlib import Path

from sacl.contracts.interfaces import ITransportGateway
from sacl.contracts.models import MailEnvelope
from sacl.transport.gateway import MailGateway
from sacl.transport.gmail_adapter import MockGmailApiAdapter
from sacl.transport.pubsub import MockPubSubSubscriber


def create_package_zip(job_id: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("manifest.json", f'{{"job_id": "{job_id}", "project": "test"}}')
        zf.writestr("prompts/instructions.md", "# Wave instructions")
    return buf.getvalue()


class MockAuditLogger:
    """Records audit calls for integration testing."""

    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def emit_pubsub_wake_received(self, email_address: str, history_id: str) -> None:
        self.events.append(
            ("PUBSUB_WAKE_RECEIVED", {"email": email_address, "history_id": history_id})
        )

    def emit_history_fetched(
        self, start_history_id: str, end_history_id: str, messages_count: int
    ) -> None:
        self.events.append(
            (
                "HISTORY_FETCHED",
                {"start": start_history_id, "end": end_history_id, "count": messages_count},
            )
        )

    def emit_job_ingested(self, job_id: str, run_id: str, package_sha: str) -> None:
        self.events.append(
            ("JOB_INGESTED", {"job_id": job_id, "run_id": run_id, "sha": package_sha})
        )

    def emit_conflict_detected(self, job_id: str, reason: str) -> None:
        self.events.append(("CONFLICT_DETECTED", {"job_id": job_id, "reason": reason}))


def test_mail_gateway_implements_interface() -> None:
    assert issubclass(MailGateway, ITransportGateway)


def test_gateway_startup_catchup(sqlite_memory_db: sqlite3.Connection, tmp_path: Path) -> None:
    adapter = MockGmailApiAdapter()
    subscriber = MockPubSubSubscriber()
    audit_logger = MockAuditLogger()

    gateway = MailGateway(
        gmail_adapter=adapter,
        pubsub_subscriber=subscriber,
        db_conn=sqlite_memory_db,
        staging_root=tmp_path,
        audit_emitter=audit_logger,
    )

    # Seed an unhandled message in Gmail that arrived before gateway started
    zip_bytes = create_package_zip("W0-STARTUP")
    adapter.add_mock_message(
        message_id="msg-startup-1",
        sender="uniquedraken@gmail.com",
        recipient="uniquedraken@gmail.com",
        subject="[SACL][JOB][v1][W0-STARTUP] Offline Arrival",
        attachment_bytes=zip_bytes,
    )

    ingested = gateway.startup_catchup()
    assert "W0-STARTUP" in ingested

    # Verify watch was registered
    watch_cursor = gateway.watch_manager.get_active_watch_cursor()
    assert watch_cursor is not None
    assert watch_cursor["resource_id"] == gateway.topic_name

    # Verify staged files
    cursor = sqlite_memory_db.cursor()
    cursor.execute("SELECT run_id FROM mail_messages WHERE job_id = 'W0-STARTUP'")
    run_id = cursor.fetchone()[0]
    assert (tmp_path / "packages" / "inbox" / run_id / "manifest.json").exists()


def test_gateway_pubsub_wake_and_history_sync_flow(
    sqlite_memory_db: sqlite3.Connection, tmp_path: Path
) -> None:
    adapter = MockGmailApiAdapter()
    subscriber = MockPubSubSubscriber()
    audit_logger = MockAuditLogger()

    gateway = MailGateway(
        gmail_adapter=adapter,
        pubsub_subscriber=subscriber,
        db_conn=sqlite_memory_db,
        staging_root=tmp_path,
        audit_emitter=audit_logger,
    )

    # 1. New message arrives in Gmail
    zip_bytes = create_package_zip("W1-PUBSUB")
    adapter.add_mock_message(
        message_id="msg-w1",
        sender="uniquedraken@gmail.com",
        recipient="uniquedraken@gmail.com",
        subject="[SACL][JOB][v1][W1-PUBSUB] Package",
        attachment_bytes=zip_bytes,
    )

    # 2. Pub/Sub emits wake signal
    subscriber.publish_mock_wake_signal(
        email_address="uniquedraken@gmail.com",
        history_id=adapter.current_history_id,
    )

    # 3. Gateway executes tick
    tick_res = gateway.run_gateway_tick()
    assert tick_res["wake_signals"] == 1
    assert "W1-PUBSUB" in tick_res["jobs_ingested"]

    # Verify audit events emitted
    event_names = [e[0] for e in audit_logger.events]
    assert "PUBSUB_WAKE_RECEIVED" in event_names
    assert "HISTORY_FETCHED" in event_names
    assert "JOB_INGESTED" in event_names


def test_gateway_duplicate_and_conflict_handling(
    sqlite_memory_db: sqlite3.Connection, tmp_path: Path
) -> None:
    adapter = MockGmailApiAdapter()
    subscriber = MockPubSubSubscriber()
    audit_logger = MockAuditLogger()

    gateway = MailGateway(
        gmail_adapter=adapter,
        pubsub_subscriber=subscriber,
        db_conn=sqlite_memory_db,
        staging_root=tmp_path,
        audit_emitter=audit_logger,
    )

    zip_bytes = create_package_zip("W2-JOB")
    adapter.add_mock_message(
        message_id="msg-orig",
        sender="uniquedraken@gmail.com",
        recipient="uniquedraken@gmail.com",
        subject="[SACL][JOB][v1][W2-JOB] Orig",
        attachment_bytes=zip_bytes,
    )

    # Initial intake
    gateway.sync_history(start_history_id="100000")

    # 1. Redelivery of identical message -> Duplicate ignored
    new_hid = str(int(adapter.current_history_id) + 1)
    adapter.current_history_id = new_hid
    adapter.history_records.append(
        {
            "id": new_hid,
            "messagesAdded": [{"message": {"id": "msg-orig", "threadId": "t-1"}}],
        }
    )
    res_dup = gateway.sync_history(
        start_history_id=gateway.reconciliation_manager.get_persisted_cursor()
    )
    assert "msg-orig" in res_dup[0]["duplicates_ignored"]

    # 2. Conflicting submission -> Divergent hash
    tampered_zip = zip_bytes + b"tampered"
    adapter.add_mock_message(
        message_id="msg-conflict",
        sender="uniquedraken@gmail.com",
        recipient="uniquedraken@gmail.com",
        subject="[SACL][JOB][v1][W2-JOB] Conflicting",
        attachment_bytes=tampered_zip,
    )
    res_conflict = gateway.sync_history(
        start_history_id=gateway.reconciliation_manager.get_persisted_cursor()
    )
    assert "msg-conflict" in res_conflict[0]["conflicts_rejected"]

    event_names = [e[0] for e in audit_logger.events]
    assert "CONFLICT_DETECTED" in event_names


def test_gateway_fetch_message_envelope(
    sqlite_memory_db: sqlite3.Connection, tmp_path: Path
) -> None:
    adapter = MockGmailApiAdapter()
    subscriber = MockPubSubSubscriber()

    gateway = MailGateway(
        gmail_adapter=adapter,
        pubsub_subscriber=subscriber,
        db_conn=sqlite_memory_db,
        staging_root=tmp_path,
    )

    zip_bytes = create_package_zip("W3-ENV")
    adapter.add_mock_message(
        message_id="msg-env-1",
        sender="uniquedraken@gmail.com",
        recipient="uniquedraken@gmail.com",
        subject="[SACL][JOB][v1][W3-ENV] Envelope Test",
        attachment_bytes=zip_bytes,
    )

    envelope = gateway.fetch_message_envelope("msg-env-1")
    assert isinstance(envelope, MailEnvelope)
    assert envelope.message_id == "msg-env-1"
    assert envelope.routing_subject.job_id == "W3-ENV"
    assert envelope.attachment.size_bytes == len(zip_bytes)


def test_gateway_dispatch_outbox_reply(
    sqlite_memory_db: sqlite3.Connection, tmp_path: Path
) -> None:
    adapter = MockGmailApiAdapter()
    subscriber = MockPubSubSubscriber()

    gateway = MailGateway(
        gmail_adapter=adapter,
        pubsub_subscriber=subscriber,
        db_conn=sqlite_memory_db,
        staging_root=tmp_path,
    )

    reply_zip = tmp_path / "RESPONSE_out.zip"
    reply_zip.write_bytes(b"PK\x03\x04synthetic_out")

    handle = gateway.dispatch_outbox_reply(
        recipient="uniquedraken@gmail.com",
        subject="[SACL][RESULT][v1][W3] - PASS (Run: run-3)",
        body_markdown="# Execution Complete\nAll stages passed.",
        attachment_path=reply_zip,
    )

    assert "outbox-" in handle
    assert len(adapter.sent_messages) == 1
    assert adapter.sent_messages[0]["threadId"] is not None

"""Tests for Mail Envelope Framing, Routing Hints, and MIME Construction."""

from __future__ import annotations

import email
import pytest

from sacl.contracts.models import AttachmentMetadata, MailEnvelope
from sacl.contracts.schema_validator import SchemaValidator
from sacl.transport.envelope import (
    build_outbound_mime,
    compute_attachment_metadata,
    create_mail_envelope,
    format_outbound_subject,
    generate_nonce,
    parse_routing_hint,
)


def test_parse_routing_hint_valid() -> None:
    subject = "[SACL][JOB][v1][W0] Wave 0 Ingestion Package"
    rh = parse_routing_hint(subject)
    assert rh.is_valid_routing_hint is True
    assert rh.job_id == "W0"
    assert rh.routing_prefix == "[SACL][JOB][v1]"


def test_parse_routing_hint_exact() -> None:
    subject = "[SACL][JOB][v1][job-20261007-001]"
    rh = parse_routing_hint(subject)
    assert rh.is_valid_routing_hint is True
    assert rh.job_id == "job-20261007-001"


def test_parse_routing_hint_invalid() -> None:
    subject = "Hello please run this task"
    rh = parse_routing_hint(subject)
    assert rh.is_valid_routing_hint is False
    assert rh.job_id == "UNKNOWN"


def test_format_outbound_subject() -> None:
    subj = format_outbound_subject("W0", "PASS", "run-12345")
    assert subj == "[SACL][RESULT][v1][W0] - PASS (Run: run-12345)"


def test_generate_nonce_format() -> None:
    nonce = generate_nonce(16)
    assert len(nonce) == 32
    # Check valid hex
    int(nonce, 16)


def test_compute_attachment_metadata() -> None:
    data = b"ZIP_CONTENT_BYTES"
    meta = compute_attachment_metadata("archive.zip", data)
    assert meta.filename == "archive.zip"
    assert meta.size_bytes == len(data)
    assert len(meta.sha256) == 64
    assert meta.mime_type == "application/zip"


def test_build_outbound_mime_multipart() -> None:
    mime_bytes = build_outbound_mime(
        recipient="uniquedraken@gmail.com",
        sender="uniquedraken@gmail.com",
        subject="[SACL][RESULT][v1][W0] - PASS (Run: run-1)",
        body_markdown="# Execution Passed\nAll deliverables verified.",
        attachment_bytes=b"PK\x03\x04zipdata",
        attachment_filename="RESPONSE_run-1.zip",
        in_reply_to="<inbound-msg-1@gmail.com>",
        references="<inbound-msg-1@gmail.com>",
    )

    msg = email.message_from_bytes(mime_bytes, policy=email.policy.default)
    assert msg["To"] == "uniquedraken@gmail.com"
    assert msg["From"] == "uniquedraken@gmail.com"
    assert msg["Subject"] == "[SACL][RESULT][v1][W0] - PASS (Run: run-1)"
    assert msg["In-Reply-To"] == "<inbound-msg-1@gmail.com>"
    assert msg["References"] == "<inbound-msg-1@gmail.com>"
    assert msg.is_multipart()

    parts = list(msg.iter_parts())
    assert len(parts) == 2
    assert parts[0].get_content_type() == "text/plain"
    assert "# Execution Passed" in parts[0].get_content()
    assert parts[1].get_content_type() == "application/zip"
    assert parts[1].get_filename() == "RESPONSE_run-1.zip"


def test_create_mail_envelope_validates_schema(schema_validator: SchemaValidator) -> None:
    data = b"ZIP_PAYLOAD"
    meta = compute_attachment_metadata("test.zip", data)
    envelope = create_mail_envelope(
        message_id="<msg-001@mail.gmail.com>",
        direction="INBOUND",
        sender="uniquedraken@gmail.com",
        recipient="uniquedraken@gmail.com",
        raw_subject="[SACL][JOB][v1][W0] Wave 0",
        attachment=meta,
        status="RECEIVED",
        history_id="105492",
        thread_id="thread-001",
        run_id="run-001",
        validate_schema=True,
    )
    assert envelope.message_id == "<msg-001@mail.gmail.com>"
    assert envelope.status == "RECEIVED"
    # Schema validation passed without error

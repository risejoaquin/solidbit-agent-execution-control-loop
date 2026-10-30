"""SACL V1 Mail Envelope & MIME Framing Abstraction.

Implements message parsing, routing hint extraction, nonce management,
and MIME multipart formatting per:
- ADR-001 (Gmail Asynchronous Transport)
- ADR-010 (At-Least-Once Delivery & Idempotency)
- docs/MAIL_PROTOCOL.md §2, §4
- schemas/mail-envelope.schema.json
"""

from __future__ import annotations

import datetime
import email
import email.utils
import hashlib
import re
import secrets
from email.message import EmailMessage
from typing import Optional

from sacl.contracts.invariants import (
    DELIVERY_SEMANTICS,
)
from sacl.contracts.models import (
    AttachmentMetadata,
    MailEnvelope,
    RoutingSubject,
)
from sacl.contracts.schema_validator import get_default_validator

# Routing hint regex: matches [SACL][JOB][v1][<JOB_ID>]
ROUTING_HINT_PATTERN = re.compile(r"^\[SACL\]\[JOB\]\[v1\]\[([A-Za-z0-9_.-]+)\](?:\s*.*)?$")

# Outbound format: [SACL][RESULT][v1][<JOB_ID>] - <STATUS> (Run: <RUN_ID>)
OUTBOUND_SUBJECT_PATTERN = re.compile(
    r"^\[SACL\]\[RESULT\]\[v1\]\[([A-Za-z0-9_.-]+)\]\s*-\s*([A-Za-z0-9_ -]+)\s*\(Run:\s*([A-Za-z0-9_.-]+)\)$"
)


def parse_routing_hint(raw_subject: str) -> RoutingSubject:
    """Parses email subject into RoutingSubject model.

    INVARIANT: Subject line is strictly a routing hint for intake filtering
    and thread correlation. It NEVER serves as an authority source for permissions,
    target paths, or execution mode.
    """
    clean_subject = (raw_subject or "").strip()
    match = ROUTING_HINT_PATTERN.match(clean_subject)

    if match:
        job_id = match.group(1)
        return RoutingSubject(
            raw_subject=clean_subject,
            job_id=job_id,
            is_valid_routing_hint=True,
            routing_prefix="[SACL][JOB][v1]",
        )

    return RoutingSubject(
        raw_subject=clean_subject,
        job_id="UNKNOWN",
        is_valid_routing_hint=False,
        routing_prefix="[SACL][JOB][v1]",
    )


def format_outbound_subject(job_id: str, status: str, run_id: str) -> str:
    """Formats canonical outbound subject line per docs/MAIL_PROTOCOL.md §4.1."""
    return f"[SACL][RESULT][v1][{job_id}] - {status} (Run: {run_id})"


def generate_nonce(num_bytes: int = 16) -> str:
    """Generates cryptographic anti-replay nonce hex string (32 hex characters)."""
    return secrets.token_hex(num_bytes)


def compute_attachment_metadata(
    filename: str, data: bytes, mime_type: str = "application/zip"
) -> AttachmentMetadata:
    """Computes SHA-256 and size metadata for package attachment."""
    sha = hashlib.sha256(data).hexdigest()
    return AttachmentMetadata(
        filename=filename,
        size_bytes=len(data),
        sha256=sha,
        mime_type=mime_type,
    )


def build_outbound_mime(
    recipient: str,
    sender: str,
    subject: str,
    body_markdown: str,
    attachment_bytes: Optional[bytes] = None,
    attachment_filename: Optional[str] = None,
    in_reply_to: Optional[str] = None,
    references: Optional[str] = None,
) -> bytes:
    """Constructs RFC 2822 MIME multipart payload (multipart/mixed) for Gmail API send."""
    msg = EmailMessage()
    msg["To"] = recipient
    msg["From"] = sender
    msg["Subject"] = subject
    msg["Date"] = email.utils.formatdate(localtime=False, usegmt=True)
    msg["Message-ID"] = email.utils.make_msgid(domain="solidbit.io")

    if in_reply_to:
        msg["In-Reply-To"] = in_reply_to
    if references:
        msg["References"] = references

    # Part 1: Markdown body
    msg.set_content(body_markdown, subtype="plain", charset="utf-8")

    # Part 2: Result ZIP Attachment
    if attachment_bytes is not None and attachment_filename:
        msg.add_attachment(
            attachment_bytes,
            maintype="application",
            subtype="zip",
            filename=attachment_filename,
        )

    return msg.as_bytes()


def create_mail_envelope(
    message_id: str,
    direction: str,
    sender: str,
    recipient: str,
    raw_subject: str,
    attachment: AttachmentMetadata,
    status: str,
    history_id: Optional[str] = None,
    thread_id: Optional[str] = None,
    nonce: Optional[str] = None,
    run_id: Optional[str] = None,
    rejection_reason: Optional[str] = None,
    timestamp: Optional[str] = None,
    validate_schema: bool = True,
) -> MailEnvelope:
    """Creates a strongly-typed MailEnvelope and optionally validates against JSON schema."""
    routing_subj = parse_routing_hint(raw_subject)
    ts = timestamp or datetime.datetime.now(datetime.timezone.utc).isoformat()
    n = nonce or generate_nonce()

    envelope = MailEnvelope(
        message_id=message_id,
        direction=direction,
        sender=sender,
        recipient=recipient,
        routing_subject=routing_subj,
        timestamp=ts,
        nonce=n,
        attachment=attachment,
        status=status,
        schema="solidbit.mail-envelope.v1",
        history_id=history_id,
        thread_id=thread_id,
        delivery_semantics=DELIVERY_SEMANTICS,
        rejection_reason=rejection_reason,
        run_id=run_id,
    )

    if validate_schema:
        payload_dict = envelope.to_dict()
        get_default_validator().validate_mail_envelope(payload_dict)

    return envelope

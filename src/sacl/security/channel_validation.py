"""SACL V1 Channel, Sender, and Anti-Exfiltration Validation Engine.

Implements Threat S1 / TH-01, Threat I2 / TH-10, and Ingress Invariants:
- Inbound sender whitelisting (uniquedraken@gmail.com) & self-mail support
- Canonical routing hint validation ([SACL][JOB][v1][<JOB_ID>])
- Outbound destination restriction (strictly uniquedraken@gmail.com)
- Bounded human approval channel validation (CLI, GMAIL, MANUAL - zero webhooks)
- Zero public inbound webhooks / listening ports invariant
"""

from __future__ import annotations

import email.utils
import re
from typing import Any, Dict, FrozenSet, Iterable, List, Optional, Set, Tuple

from sacl.contracts.invariants import (
    APPROVAL_CHANNELS_V1,
    DEFAULT_ROUTING_PREFIX,
)
from sacl.security.exceptions import (
    DataExfiltrationAttemptError,
    SecurityError,
    UnauthorizedChannelError,
    UnauthorizedSenderError,
)
from sacl.transport.exceptions import InvalidRoutingHintError

DEFAULT_AUTHORIZED_EMAIL: str = "uniquedraken@gmail.com"

# Canonical routing hint pattern: [SACL][JOB][v1][<JOB_ID>]
ROUTING_HINT_REGEX = re.compile(
    r"^\[SACL\]\[JOB\]\[v1\]\[([A-Za-z0-9_.-]+)\](?:\s*.*)?$",
    re.IGNORECASE,
)


def extract_email_address(raw_sender: str) -> str:
    """Extracts and normalizes pure email address from header value.

    Handles formats like:
      - 'uniquedraken@gmail.com' -> 'uniquedraken@gmail.com'
      - '"Joaquín" <uniquedraken@gmail.com>' -> 'uniquedraken@gmail.com'
      - 'Joaquín <UNIQUEDRAKEN@GMAIL.COM>' -> 'uniquedraken@gmail.com'
    """
    if not raw_sender:
        return ""
    _name, address = email.utils.parseaddr(raw_sender.strip())
    clean = address if address else raw_sender.strip()
    return clean.lower()


def validate_inbound_sender(
    sender: str,
    authorized_sender: str = DEFAULT_AUTHORIZED_EMAIL,
) -> bool:
    """Validates whether inbound email sender matches authorized identity."""
    parsed = extract_email_address(sender)
    expected = extract_email_address(authorized_sender)
    return bool(parsed and parsed == expected)


def assert_authorized_sender(
    sender: str,
    authorized_sender: str = DEFAULT_AUTHORIZED_EMAIL,
) -> str:
    """Asserts that inbound sender is whitelisted; raises UnauthorizedSenderError on mismatch."""
    parsed = extract_email_address(sender)
    expected = extract_email_address(authorized_sender)
    if not parsed or parsed != expected:
        raise UnauthorizedSenderError(sender=sender, expected_sender=authorized_sender)
    return parsed


def validate_routing_hint(subject: str) -> Optional[str]:
    """Validates whether email subject conforms to canonical routing hint syntax.

    Returns the extracted job_id if valid, or None if invalid.
    INVARIANT: Subject line is strictly a routing hint, NEVER an authority source.
    """
    if not subject:
        return None
    match = ROUTING_HINT_REGEX.match(subject.strip())
    if match:
        return match.group(1)
    return None


def assert_valid_routing_hint(subject: str) -> str:
    """Asserts that subject is a valid canonical routing hint, returning job_id.

    Raises InvalidRoutingHintError if invalid.
    """
    job_id = validate_routing_hint(subject)
    if not job_id:
        raise InvalidRoutingHintError(
            raw_subject=subject,
            expected_pattern=f"{DEFAULT_ROUTING_PREFIX}[<JOB_ID>]",
        )
    return job_id


def validate_outbound_recipient(
    recipient: str,
    authorized_recipient: str = DEFAULT_AUTHORIZED_EMAIL,
) -> bool:
    """Validates that outbound email destination is strictly the authorized recipient."""
    parsed = extract_email_address(recipient)
    expected = extract_email_address(authorized_recipient)
    return bool(parsed and parsed == expected)


def assert_authorized_recipient(
    recipient: str,
    authorized_recipient: str = DEFAULT_AUTHORIZED_EMAIL,
) -> str:
    """Asserts that outbound recipient is the authorized destination.

    Prevents source code and deliverable exfiltration (Threat I2 / TH-10).
    Raises DataExfiltrationAttemptError if targeting any external address.
    """
    parsed = extract_email_address(recipient)
    expected = extract_email_address(authorized_recipient)
    if not parsed or parsed != expected:
        raise DataExfiltrationAttemptError(
            recipient=recipient,
            authorized_recipient=authorized_recipient,
        )
    return parsed


def validate_approval_channel(channel: str) -> bool:
    """Validates whether an approval channel is authorized in SACL V1."""
    if not channel:
        return False
    return channel.strip().upper() in APPROVAL_CHANNELS_V1


def assert_authorized_approval_channel(channel: str) -> str:
    """Asserts that human approval channel is one of CLI, GMAIL, or MANUAL.

    Raises UnauthorizedChannelError if channel is an unauthorized source (e.g. WEBHOOK).
    """
    c_upper = (channel or "").strip().upper()
    if c_upper not in APPROVAL_CHANNELS_V1:
        raise UnauthorizedChannelError(
            channel=channel,
            allowed_channels=sorted(list(APPROVAL_CHANNELS_V1)),
        )
    return c_upper


def assert_no_public_inbound_webhooks(config: Optional[Dict[str, Any]] = None) -> None:
    """Asserts that host configuration does not open public inbound listening webhooks."""
    if config:
        if config.get("public_webhook", False) is True:
            raise SecurityError(
                "INBOUND_WEBHOOK_PROHIBITED: Public inbound webhooks violate SACL transport invariants. "
                "Must use outbound-only Pub/Sub pull.",
                details={"violation": "PUBLIC_WEBHOOK_PROHIBITED"},
            )
        if config.get("listen_port") is not None:
            raise SecurityError(
                "INBOUND_LISTENER_PROHIBITED: Public inbound listening ports are forbidden in V1.",
                details={"violation": "INBOUND_PORT_PROHIBITED"},
            )

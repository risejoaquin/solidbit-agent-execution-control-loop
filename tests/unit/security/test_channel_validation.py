"""Unit tests for SACL V1 Channel, Sender, and Anti-Exfiltration Validation."""

from __future__ import annotations

import pytest

from sacl.security.channel_validation import (
    DEFAULT_AUTHORIZED_EMAIL,
    assert_authorized_approval_channel,
    assert_authorized_recipient,
    assert_authorized_sender,
    assert_no_public_inbound_webhooks,
    assert_valid_routing_hint,
    extract_email_address,
    validate_approval_channel,
    validate_inbound_sender,
    validate_outbound_recipient,
    validate_routing_hint,
)
from sacl.security.exceptions import (
    DataExfiltrationAttemptError,
    SecurityError,
    UnauthorizedChannelError,
    UnauthorizedSenderError,
)
from sacl.transport.exceptions import InvalidRoutingHintError


class TestSenderValidation:
    """Tests inbound sender whitelisting and self-mail support (Threat S1 / TH-01)."""

    def test_extract_email_address_variants(self) -> None:
        assert extract_email_address("uniquedraken@gmail.com") == "uniquedraken@gmail.com"
        assert (
            extract_email_address('"Joaquín" <uniquedraken@gmail.com>') == "uniquedraken@gmail.com"
        )
        assert extract_email_address("Joaquín <UNIQUEDRAKEN@GMAIL.COM>") == "uniquedraken@gmail.com"
        assert extract_email_address("   uniquedraken@gmail.com   ") == "uniquedraken@gmail.com"

    def test_authorized_sender_succeeds(self) -> None:
        assert validate_inbound_sender("uniquedraken@gmail.com") is True
        assert validate_inbound_sender('"Self" <uniquedraken@gmail.com>') is True
        assert assert_authorized_sender("uniquedraken@gmail.com") == "uniquedraken@gmail.com"

    def test_unauthorized_sender_raises_unauthorized_sender_error(self) -> None:
        with pytest.raises(UnauthorizedSenderError) as exc_info:
            assert_authorized_sender("malicious-actor@evil.com")
        assert "UNAUTHORIZED_SENDER" in exc_info.value.message
        assert exc_info.value.sender == "malicious-actor@evil.com"
        assert exc_info.value.expected_sender == DEFAULT_AUTHORIZED_EMAIL

    def test_validate_inbound_sender_returns_false_for_unauthorized(self) -> None:
        assert validate_inbound_sender("spoofed@external.org") is False
        assert validate_inbound_sender("") is False


class TestRoutingHintValidation:
    """Tests email subject line canonical routing hint format."""

    def test_valid_routing_hint_extracts_job_id(self) -> None:
        subject = "[SACL][JOB][v1][JOB-20261010-001]"
        assert validate_routing_hint(subject) == "JOB-20261010-001"
        assert assert_valid_routing_hint(subject) == "JOB-20261010-001"

    def test_routing_hint_with_trailing_title_extracts_job_id(self) -> None:
        subject = "[SACL][JOB][v1][JOB-W0-ALPHA] Wave Execution Package"
        assert validate_routing_hint(subject) == "JOB-W0-ALPHA"
        assert assert_valid_routing_hint(subject) == "JOB-W0-ALPHA"

    def test_invalid_routing_hint_raises_error(self) -> None:
        with pytest.raises(InvalidRoutingHintError):
            assert_valid_routing_hint("Urgent: Run this job immediately")

        with pytest.raises(InvalidRoutingHintError):
            assert_valid_routing_hint("[SACL][v1][JOB-01]")

        with pytest.raises(InvalidRoutingHintError):
            assert_valid_routing_hint("")


class TestAntiExfiltrationOutboundRestriction:
    """Tests fixed outbound recipient whitelisting (Threat I2 / TH-10)."""

    def test_authorized_outbound_recipient_succeeds(self) -> None:
        assert validate_outbound_recipient("uniquedraken@gmail.com") is True
        assert assert_authorized_recipient("uniquedraken@gmail.com") == "uniquedraken@gmail.com"
        assert (
            assert_authorized_recipient('"Self" <uniquedraken@gmail.com>')
            == "uniquedraken@gmail.com"
        )

    def test_unauthorized_outbound_recipient_raises_exfiltration_error(self) -> None:
        with pytest.raises(DataExfiltrationAttemptError) as exc_info:
            assert_authorized_recipient("attacker@external.com")
        assert "DATA_EXFILTRATION_PREVENTED" in exc_info.value.message
        assert exc_info.value.recipient == "attacker@external.com"
        assert exc_info.value.authorized_recipient == DEFAULT_AUTHORIZED_EMAIL


class TestApprovalChannelValidation:
    """Tests bounded human approval channel restrictions (ADR-007)."""

    @pytest.mark.parametrize("channel", ["CLI", "GMAIL", "MANUAL", "cli", "gmail", "manual"])
    def test_approved_channels_succeed(self, channel: str) -> None:
        assert validate_approval_channel(channel) is True
        assert assert_authorized_approval_channel(channel) in {"CLI", "GMAIL", "MANUAL"}

    @pytest.mark.parametrize("channel", ["WEBHOOK", "SLACK", "HTTP_API", "REST", "DISCORD"])
    def test_unauthorized_channels_raise_error(self, channel: str) -> None:
        assert validate_approval_channel(channel) is False
        with pytest.raises(UnauthorizedChannelError) as exc_info:
            assert_authorized_approval_channel(channel)
        assert "UNAUTHORIZED_CHANNEL" in exc_info.value.message


class TestZeroInboundWebhookInvariant:
    """Tests assertion that host has zero inbound listening webhooks."""

    def test_public_webhook_flag_rejected(self) -> None:
        with pytest.raises(SecurityError) as exc_info:
            assert_no_public_inbound_webhooks({"public_webhook": True})
        assert "INBOUND_WEBHOOK_PROHIBITED" in str(exc_info.value)

    def test_listen_port_rejected(self) -> None:
        with pytest.raises(SecurityError) as exc_info:
            assert_no_public_inbound_webhooks({"listen_port": 8080})
        assert "INBOUND_LISTENER_PROHIBITED" in str(exc_info.value)

    def test_outbound_pull_config_succeeds(self) -> None:
        # Should not raise
        assert_no_public_inbound_webhooks({"public_webhook": False, "ingress": "pubsub_pull"})

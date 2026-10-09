"""Tests for Gmail REST API Adapter and Mock Implementation."""

from __future__ import annotations

import base64
import pytest

from sacl.transport.exceptions import (
    RateLimitExceededError,
    StaleHistoryCursorError,
    TransportError,
)
from sacl.transport.gmail_adapter import GmailApiAdapter, MockGmailApiAdapter
from sacl.transport.oauth import InMemoryOAuth2CredentialProvider


def test_mock_adapter_watch_and_stop() -> None:
    adapter = MockGmailApiAdapter()
    resp = adapter.watch(topic_name="projects/test/topics/events", label_ids=["INBOX"])
    assert "historyId" in resp
    assert "expiration" in resp
    assert adapter.active_watch is not None
    assert adapter.active_watch["topicName"] == "projects/test/topics/events"

    adapter.stop_watch()
    assert adapter.stop_called is True
    assert adapter.active_watch is None


def test_mock_adapter_messages_and_history() -> None:
    adapter = MockGmailApiAdapter()
    adapter.current_history_id = "100"

    adapter.add_mock_message(
        message_id="msg-1",
        sender="uniquedraken@gmail.com",
        recipient="uniquedraken@gmail.com",
        subject="[SACL][JOB][v1][W0] Wave 0 Package",
        attachment_filename="wave0.zip",
        attachment_bytes=b"PK\x03\x04synthetic_zip",
    )

    # list_history from "100"
    hist = adapter.list_history(start_history_id="100")
    assert len(hist["history"]) == 1
    added = hist["history"][0]["messagesAdded"][0]["message"]
    assert added["id"] == "msg-1"

    # get_message
    msg = adapter.get_message("msg-1")
    assert msg["id"] == "msg-1"
    assert msg["payload"]["headers"][2]["value"] == "[SACL][JOB][v1][W0] Wave 0 Package"

    # get_attachment
    att_bytes = adapter.get_attachment("msg-1", "att-001")
    assert att_bytes == b"PK\x03\x04synthetic_zip"


def test_mock_adapter_send_message() -> None:
    adapter = MockGmailApiAdapter()
    resp = adapter.send_message(raw_mime_bytes=b"From: uniquedraken@gmail.com\n\nHello", thread_id="t-123")
    assert "id" in resp
    assert resp["threadId"] == "t-123"
    assert len(adapter.sent_messages) == 1
    assert adapter.sent_messages[0]["raw_mime_bytes"] == b"From: uniquedraken@gmail.com\n\nHello"


def test_mock_adapter_stale_history_cursor_raises_404() -> None:
    adapter = MockGmailApiAdapter()
    adapter.simulate_stale_history = True
    with pytest.raises(StaleHistoryCursorError) as exc_info:
        adapter.list_history(start_history_id="99999")
    assert exc_info.value.history_id == "99999"


def test_mock_adapter_rate_limit_and_server_error() -> None:
    adapter = MockGmailApiAdapter()
    adapter.rate_limit_failures_remaining = 1
    with pytest.raises(RateLimitExceededError) as exc_info:
        adapter.get_message("msg-1")
    assert exc_info.value.retry_after_seconds == 5.0

    adapter.server_error_failures_remaining = 1
    with pytest.raises(TransportError, match="503 Service Unavailable"):
        adapter.get_message("msg-1")


def test_gmail_adapter_backoff_calculation() -> None:
    provider = InMemoryOAuth2CredentialProvider(access_token="tok")
    slept = []
    adapter = GmailApiAdapter(
        credential_provider=provider,
        max_retries=3,
        backoff_steps=[1.0, 2.0, 3.0],
        sleeper=lambda s: slept.append(s),
    )
    assert adapter.max_retries == 3
    assert adapter.backoff_steps == [1.0, 2.0, 3.0]

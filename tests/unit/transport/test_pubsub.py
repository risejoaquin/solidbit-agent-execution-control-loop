"""Tests for Google Cloud Pub/Sub Pull Subscriber & Wake Signals."""

from __future__ import annotations

import json
import pytest

from sacl.transport.exceptions import TransportError
from sacl.transport.pubsub import (
    MockPubSubSubscriber,
    PubSubMessage,
    WakeSignal,
    parse_wake_signal,
)


def test_parse_wake_signal_camel_case() -> None:
    data = json.dumps({"emailAddress": "uniquedraken@gmail.com", "historyId": "105504"}).encode("utf-8")
    sig = parse_wake_signal(data, ack_id="ack-1", message_id="msg-1")
    assert sig.email_address == "uniquedraken@gmail.com"
    assert sig.history_id == "105504"
    assert sig.ack_id == "ack-1"
    assert sig.message_id == "msg-1"


def test_parse_wake_signal_snake_case() -> None:
    data = json.dumps({"email_address": "uniquedraken@gmail.com", "history_id": "200000"}).encode("utf-8")
    sig = parse_wake_signal(data)
    assert sig.email_address == "uniquedraken@gmail.com"
    assert sig.history_id == "200000"


def test_parse_wake_signal_invalid_payload() -> None:
    with pytest.raises(TransportError, match="empty"):
        parse_wake_signal(b"")

    with pytest.raises(TransportError, match="missing 'emailAddress' or 'historyId'"):
        parse_wake_signal(b'{"randomField": "value"}')


def test_mock_pubsub_subscriber_pull_and_acknowledge() -> None:
    subscriber = MockPubSubSubscriber()
    subscriber.publish_mock_wake_signal(
        email_address="uniquedraken@gmail.com", history_id="105504"
    )
    subscriber.publish_mock_wake_signal(
        email_address="uniquedraken@gmail.com", history_id="105505"
    )

    signals = subscriber.pull_wake_signals(max_messages=10)
    assert len(signals) == 2
    assert signals[0].history_id == "105504"
    assert signals[1].history_id == "105505"

    # Acknowledge
    subscriber.acknowledge([signals[0].ack_id, signals[1].ack_id])
    assert subscriber.acknowledged_ack_ids == [signals[0].ack_id, signals[1].ack_id]

    # Queue should be empty now
    empty_pull = subscriber.pull_messages()
    assert len(empty_pull) == 0


def test_mock_pubsub_subscriber_modify_ack_deadline() -> None:
    subscriber = MockPubSubSubscriber()
    subscriber.modify_ack_deadline(["ack-10"], ack_deadline_seconds=60)
    assert subscriber.deadline_modifications["ack-10"] == 60

"""SACL V1 Google Cloud Pub/Sub Pull & StreamingPull Subscriber.

Implements outbound-only event-driven wake signal consumption adhering strictly to:
- ADR-001 (Gmail Self-Mailbox Transport via Pub/Sub Pull)
- ADR-008 (Process Separation of Mail Gateway)
- docs/MAIL_PROTOCOL.md §3.2 (Zero inbound webhooks, untrusted wake signal)
"""

from __future__ import annotations
from sacl.transport.http_client import safe_urlopen

import abc
import base64
import dataclasses
import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from sacl.transport.exceptions import TransportError
from sacl.transport.oauth import IOAuth2CredentialProvider

logger = logging.getLogger("sacl.transport.pubsub")

PUBSUB_RECONNECT_BACKOFF = [5.0, 15.0, 45.0, 120.0]  # docs/MAIL_PROTOCOL.md §5.1


@dataclasses.dataclass(frozen=True)
class PubSubMessage:
    """Represents a message received from Google Cloud Pub/Sub."""

    message_id: str
    ack_id: str
    data: bytes
    publish_time: str
    attributes: Dict[str, str] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True)
class WakeSignal:
    """Parsed Gmail change wake signal from Google Cloud Pub/Sub.

    INVARIANT: The wake signal is strictly an UNTRUSTED WAKE SIGNAL informing
    the gateway that the mailbox state has progressed. It carries ZERO authority
    and ZERO message content. Authoritative fetch is executed exclusively via
    the Gmail History API.
    """

    email_address: str
    history_id: str
    ack_id: Optional[str] = None
    message_id: Optional[str] = None


def parse_wake_signal(
    data: bytes, ack_id: Optional[str] = None, message_id: Optional[str] = None
) -> WakeSignal:
    """Parses and validates the Gmail Pub/Sub wake signal payload.

    Expected JSON schema:
    {
        "emailAddress": "uniquedraken@gmail.com",
        "historyId": "105504"
    }
    """
    if not data:
        raise TransportError("Pub/Sub message data payload is empty")

    try:
        raw_text = data.decode("utf-8")
        payload = json.loads(raw_text)
    except Exception as err:
        # Might be double base64-encoded
        try:
            decoded = base64.b64decode(data).decode("utf-8")
            payload = json.loads(decoded)
        except Exception:
            raise TransportError(f"Failed to parse Pub/Sub wake signal JSON: {err}") from err

    email_address = payload.get("emailAddress") or payload.get("email_address")
    history_id = payload.get("historyId") or payload.get("history_id")

    if not email_address or not history_id:
        raise TransportError(
            f"Invalid Gmail wake signal structure; missing 'emailAddress' or 'historyId': {payload}"
        )

    return WakeSignal(
        email_address=str(email_address),
        history_id=str(history_id),
        ack_id=ack_id,
        message_id=message_id,
    )


class IPubSubSubscriber(abc.ABC):
    """Abstract interface for Google Cloud Pub/Sub Pull subscribers."""

    @abc.abstractmethod
    def pull_messages(
        self, max_messages: int = 10, timeout_seconds: float = 30.0
    ) -> List[PubSubMessage]:
        """Pulls messages from the configured Pub/Sub subscription."""
        pass

    @abc.abstractmethod
    def acknowledge(self, ack_ids: List[str]) -> None:
        """Acknowledges processed Pub/Sub messages."""
        pass

    @abc.abstractmethod
    def modify_ack_deadline(self, ack_ids: List[str], ack_deadline_seconds: int) -> None:
        """Extends or modifies the acknowledgment deadline for active messages."""
        pass

    def pull_wake_signals(self, max_messages: int = 10) -> List[WakeSignal]:
        """Convenience method to pull and parse wake signals."""
        messages = self.pull_messages(max_messages=max_messages)
        signals: List[WakeSignal] = []
        for msg in messages:
            try:
                signal = parse_wake_signal(msg.data, ack_id=msg.ack_id, message_id=msg.message_id)
                signals.append(signal)
            except Exception as e:
                logger.warning("Failed to parse message %s as wake signal: %s", msg.message_id, e)
        return signals


class PubSubPullSubscriber(IPubSubSubscriber):
    """Production Pub/Sub subscriber connecting outbound over HTTPS/TLS to Google Cloud REST API."""

    def __init__(
        self,
        subscription_path: str,
        credential_provider: IOAuth2CredentialProvider,
        base_url: str = "https://pubsub.googleapis.com/v1",
        backoff_steps: Optional[List[float]] = None,
        sleeper: Optional[Any] = None,
    ) -> None:
        self.subscription_path = subscription_path.strip("/")
        self.credential_provider = credential_provider
        self.base_url = base_url.rstrip("/")
        self.backoff_steps = backoff_steps or list(PUBSUB_RECONNECT_BACKOFF)
        self._sleeper = sleeper or time.sleep
        self._consecutive_failures = 0

    def pull_messages(
        self, max_messages: int = 10, timeout_seconds: float = 30.0
    ) -> List[PubSubMessage]:
        url = f"{self.base_url}/{self.subscription_path}:pull"
        headers = self.credential_provider.get_auth_headers()
        headers["Content-Type"] = "application/json"

        body = {
            "maxMessages": max_messages,
            "returnImmediately": False,
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with safe_urlopen(req, timeout=timeout_seconds) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                self._consecutive_failures = 0

                messages: List[PubSubMessage] = []
                for received in resp_data.get("receivedMessages", []):
                    ack_id = received.get("ackId", "")
                    msg_obj = received.get("message", {})
                    data_b64 = msg_obj.get("data", "")
                    raw_data = base64.b64decode(data_b64) if data_b64 else b""

                    messages.append(
                        PubSubMessage(
                            message_id=msg_obj.get("messageId", ""),
                            ack_id=ack_id,
                            data=raw_data,
                            publish_time=msg_obj.get("publishTime", ""),
                            attributes=msg_obj.get("attributes", {}),
                        )
                    )
                return messages

        except urllib.error.HTTPError as err:
            self._handle_network_failure(err)
            raise TransportError(f"Pub/Sub pull HTTP error {err.code}: {err}") from err
        except Exception as err:
            self._handle_network_failure(err)
            raise TransportError(f"Pub/Sub pull failed: {err}") from err

    def acknowledge(self, ack_ids: List[str]) -> None:
        if not ack_ids:
            return

        url = f"{self.base_url}/{self.subscription_path}:acknowledge"
        headers = self.credential_provider.get_auth_headers()
        headers["Content-Type"] = "application/json"

        body = {"ackIds": ack_ids}
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with safe_urlopen(req, timeout=15):
                pass
        except Exception as err:
            logger.error("Failed to acknowledge Pub/Sub messages %s: %s", ack_ids, err)
            raise TransportError(f"Failed to acknowledge Pub/Sub messages: {err}") from err

    def modify_ack_deadline(self, ack_ids: List[str], ack_deadline_seconds: int) -> None:
        if not ack_ids:
            return

        url = f"{self.base_url}/{self.subscription_path}:modifyAckDeadline"
        headers = self.credential_provider.get_auth_headers()
        headers["Content-Type"] = "application/json"

        body = {
            "ackIds": ack_ids,
            "ackDeadlineSeconds": ack_deadline_seconds,
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with safe_urlopen(req, timeout=15):
                pass
        except Exception as err:
            logger.warning("Failed to modify ack deadline: %s", err)

    def _handle_network_failure(self, err: Exception) -> None:
        backoff_idx = min(self._consecutive_failures, len(self.backoff_steps) - 1)
        backoff = self.backoff_steps[backoff_idx]
        self._consecutive_failures += 1
        logger.warning(
            "Pub/Sub network failure (%s); waiting %.2fs before retry (failures=%d)",
            err,
            backoff,
            self._consecutive_failures,
        )
        self._sleeper(backoff)


class MockPubSubSubscriber(IPubSubSubscriber):
    """Deterministic in-memory mock Pub/Sub subscriber for testing."""

    def __init__(self) -> None:
        self.message_queue: List[PubSubMessage] = []
        self.acknowledged_ack_ids: List[str] = []
        self.deadline_modifications: Dict[str, int] = {}
        self._next_id = 1

    def publish_mock_wake_signal(
        self,
        email_address: str = "uniquedraken@gmail.com",
        history_id: str = "105504",
        attributes: Optional[Dict[str, str]] = None,
    ) -> PubSubMessage:
        """Enqueues a mock Gmail wake signal for pulling."""
        mid = f"ps-msg-{self._next_id}"
        ack_id = f"ack-{self._next_id}"
        self._next_id += 1

        payload = {"emailAddress": email_address, "historyId": history_id}
        data = json.dumps(payload).encode("utf-8")

        msg = PubSubMessage(
            message_id=mid,
            ack_id=ack_id,
            data=data,
            publish_time=str(int(time.time())),
            attributes=attributes or {},
        )
        self.message_queue.append(msg)
        return msg

    def pull_messages(
        self, max_messages: int = 10, timeout_seconds: float = 30.0
    ) -> List[PubSubMessage]:
        pulled = self.message_queue[:max_messages]
        self.message_queue = self.message_queue[max_messages:]
        return pulled

    def acknowledge(self, ack_ids: List[str]) -> None:
        self.acknowledged_ack_ids.extend(ack_ids)

    def modify_ack_deadline(self, ack_ids: List[str], ack_deadline_seconds: int) -> None:
        for aid in ack_ids:
            self.deadline_modifications[aid] = ack_deadline_seconds

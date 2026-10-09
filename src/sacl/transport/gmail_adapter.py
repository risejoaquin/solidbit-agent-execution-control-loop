"""SACL V1 Gmail REST API Adapter & Mocks.

Implements the low-level Gmail API REST client adhering strictly to
ADR-001, ADR-008, and docs/MAIL_PROTOCOL.md.
Features:
- Gmail API OAuth2 Bearer token authentication
- users.watch and users.stop
- users.history.list with 404 StaleHistoryCursorError detection
- users.messages.get, attachments.get, list
- users.messages.send with threadId continuation
- Exponential backoff with jitter on HTTP 429 (quota) and 503 (unavailable)
- Full MockGmailApiAdapter for zero-credential deterministic testing
"""

from __future__ import annotations

import abc
import base64
import json
import logging
import random
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from sacl.transport.exceptions import (
    RateLimitExceededError,
    StaleHistoryCursorError,
    TransportAuthError,
    TransportError,
)
from sacl.transport.oauth import IOAuth2CredentialProvider

logger = logging.getLogger("sacl.transport.gmail_adapter")

GMAIL_BASE_URL = "https://gmail.googleapis.com/gmail/v1/users/me"
RETRY_BACKOFF_STEPS = [5.0, 15.0, 45.0, 120.0, 300.0]  # docs/MAIL_PROTOCOL.md §5.1


class IGmailApiAdapter(abc.ABC):
    """Abstract interface for Gmail REST API interactions."""

    @abc.abstractmethod
    def watch(self, topic_name: str, label_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Registers users.watch for mailbox change notifications.

        Returns:
            Dict containing 'historyId' and 'expiration' (epoch ms string).
        """
        pass

    @abc.abstractmethod
    def stop_watch(self) -> None:
        """Terminates active users.watch registration."""
        pass

    @abc.abstractmethod
    def list_history(
        self,
        start_history_id: str,
        label_id: Optional[str] = None,
        max_results: int = 100,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Authoritative fetch of mailbox history changes.

        Raises:
            StaleHistoryCursorError: If Gmail returns 404 (history ID not found / expired).
        """
        pass

    @abc.abstractmethod
    def get_message(self, message_id: str, format: str = "full") -> Dict[str, Any]:
        """Fetches full message metadata and payload structure."""
        pass

    @abc.abstractmethod
    def get_attachment(self, message_id: str, attachment_id: str) -> bytes:
        """Retrieves and decodes raw attachment bytes."""
        pass

    @abc.abstractmethod
    def list_messages(
        self, query: str, max_results: int = 50, page_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Queries messages matching search expression (for degraded fallback polling)."""
        pass

    @abc.abstractmethod
    def send_message(self, raw_mime_bytes: bytes, thread_id: Optional[str] = None) -> Dict[str, Any]:
        """Dispatches an outbound message via users.messages.send with threadId correlation."""
        pass


class GmailApiAdapter(IGmailApiAdapter):
    """Concrete production Gmail API adapter executing HTTPS requests over TLS."""

    def __init__(
        self,
        credential_provider: IOAuth2CredentialProvider,
        base_url: str = GMAIL_BASE_URL,
        max_retries: int = 5,
        backoff_steps: Optional[List[float]] = None,
        sleeper: Optional[Any] = None,
    ) -> None:
        self.credential_provider = credential_provider
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self.backoff_steps = backoff_steps or list(RETRY_BACKOFF_STEPS)
        self._sleeper = sleeper or time.sleep

    def _execute_request(
        self,
        endpoint: str,
        method: str = "GET",
        query_params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        raw_body: Optional[bytes] = None,
        content_type: str = "application/json",
    ) -> Dict[str, Any]:
        """Executes HTTP request with OAuth2 bearer token and exponential backoff on 429/503."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        if query_params:
            url += "?" + urllib.parse.urlencode(query_params)

        attempt = 0
        while attempt <= self.max_retries:
            headers = self.credential_provider.get_auth_headers()
            headers["Accept"] = "application/json"

            data_bytes: Optional[bytes] = None
            if json_body is not None:
                data_bytes = json.dumps(json_body).encode("utf-8")
                headers["Content-Type"] = "application/json"
            elif raw_body is not None:
                data_bytes = raw_body
                headers["Content-Type"] = content_type

            req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)

            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    resp_bytes = resp.read()
                    if not resp_bytes:
                        return {}
                    return json.loads(resp_bytes.decode("utf-8"))

            except urllib.error.HTTPError as err:
                # 404 on history.list indicates stale cursor
                if err.code == 404 and "history" in endpoint:
                    start_id = (query_params or {}).get("startHistoryId", "unknown")
                    raise StaleHistoryCursorError(history_id=str(start_id)) from err

                # 401 Unauthorized -> Refresh token and retry once
                if err.code == 401 and attempt < self.max_retries:
                    logger.warning("HTTP 401 Unauthorized; attempting OAuth2 token refresh.")
                    self.credential_provider.refresh_access_token()
                    attempt += 1
                    continue

                # 429 Rate Limit or 503 Service Unavailable -> Exponential backoff with jitter
                if err.code in (429, 503) and attempt < self.max_retries:
                    retry_after_hdr = err.headers.get("Retry-After")
                    if retry_after_hdr and retry_after_hdr.isdigit():
                        backoff = float(retry_after_hdr)
                    else:
                        base_backoff = self.backoff_steps[min(attempt, len(self.backoff_steps) - 1)]
                        jitter = random.uniform(0.8, 1.2)
                        backoff = base_backoff * jitter

                    logger.warning(
                        "Gmail API returned HTTP %s; backing off for %.2fs (attempt %d/%d)",
                        err.code,
                        backoff,
                        attempt + 1,
                        self.max_retries,
                    )
                    self._sleeper(backoff)
                    attempt += 1
                    continue

                if err.code == 429:
                    raise RateLimitExceededError(details={"status_code": err.code, "url": url}) from err

                err_text = err.read().decode("utf-8", errors="replace")
                raise TransportError(
                    f"Gmail API HTTP error {err.code} on {method} {url}: {err_text}",
                    details={"status_code": err.code, "error_body": err_text},
                ) from err

            except urllib.error.URLError as err:
                if attempt < self.max_retries:
                    base_backoff = self.backoff_steps[min(attempt, len(self.backoff_steps) - 1)]
                    backoff = base_backoff * random.uniform(0.8, 1.2)
                    logger.warning("Network URLError: %s. Retrying in %.2fs", err, backoff)
                    self._sleeper(backoff)
                    attempt += 1
                    continue
                raise TransportError(f"Network error accessing Gmail API: {err}") from err

        raise TransportError(f"Exceeded max retries ({self.max_retries}) for Gmail API request: {url}")

    def watch(self, topic_name: str, label_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "topicName": topic_name,
            "labelIds": label_ids or ["INBOX"],
            "labelFilterAction": "include",
        }
        return self._execute_request("watch", method="POST", json_body=payload)

    def stop_watch(self) -> None:
        self._execute_request("stop", method="POST")

    def list_history(
        self,
        start_history_id: str,
        label_id: Optional[str] = None,
        max_results: int = 100,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "startHistoryId": start_history_id,
            "maxResults": max_results,
            "historyTypes": ["messageAdded"],
        }
        if label_id:
            params["labelId"] = label_id
        if page_token:
            params["pageToken"] = page_token
        return self._execute_request("history", method="GET", query_params=params)

    def get_message(self, message_id: str, format: str = "full") -> Dict[str, Any]:
        params = {"format": format}
        return self._execute_request(f"messages/{message_id}", method="GET", query_params=params)

    def get_attachment(self, message_id: str, attachment_id: str) -> bytes:
        data = self._execute_request(
            f"messages/{message_id}/attachments/{attachment_id}", method="GET"
        )
        raw_b64 = data.get("data", "")
        # Gmail uses base64url encoding
        return base64.urlsafe_b64decode(raw_b64.encode("ascii"))

    def list_messages(
        self, query: str, max_results: int = 50, page_token: Optional[str] = None
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"q": query, "maxResults": max_results}
        if page_token:
            params["pageToken"] = page_token
        return self._execute_request("messages", method="GET", query_params=params)

    def send_message(self, raw_mime_bytes: bytes, thread_id: Optional[str] = None) -> Dict[str, Any]:
        raw_b64 = base64.urlsafe_b64encode(raw_mime_bytes).decode("ascii")
        payload: Dict[str, Any] = {"raw": raw_b64}
        if thread_id:
            payload["threadId"] = thread_id
        return self._execute_request("messages/send", method="POST", json_body=payload)


class MockGmailApiAdapter(IGmailApiAdapter):
    """Deterministic in-memory mock implementation of Gmail API for testing."""

    def __init__(self) -> None:
        self.messages: Dict[str, Dict[str, Any]] = {}
        self.attachments: Dict[str, bytes] = {}  # key: f"{message_id}:{attachment_id}"
        self.history_records: List[Dict[str, Any]] = []
        self.current_history_id: str = "100000"
        self.active_watch: Optional[Dict[str, Any]] = None
        self.sent_messages: List[Dict[str, Any]] = []

        # Fault injection controls
        self.rate_limit_failures_remaining: int = 0
        self.server_error_failures_remaining: int = 0
        self.simulate_stale_history: bool = False
        self.stop_called: bool = False

    def add_mock_message(
        self,
        message_id: str,
        sender: str,
        recipient: str,
        subject: str,
        snippet: str = "",
        thread_id: Optional[str] = None,
        history_id: Optional[str] = None,
        attachment_filename: Optional[str] = None,
        attachment_bytes: Optional[bytes] = None,
        attachment_id: str = "att-001",
        labels: Optional[List[str]] = None,
    ) -> None:
        """Helper to seed mock mailbox state."""
        tid = thread_id or f"thread-{message_id}"
        hid = history_id or str(int(self.current_history_id) + 1)
        self.current_history_id = hid

        parts: List[Dict[str, Any]] = []
        if attachment_bytes is not None:
            parts.append({
                "partId": "1",
                "mimeType": "application/zip",
                "filename": attachment_filename or "package.zip",
                "body": {
                    "attachmentId": attachment_id,
                    "size": len(attachment_bytes),
                },
            })
            self.attachments[f"{message_id}:{attachment_id}"] = attachment_bytes

        msg = {
            "id": message_id,
            "threadId": tid,
            "labelIds": labels or ["INBOX"],
            "snippet": snippet,
            "historyId": hid,
            "payload": {
                "headers": [
                    {"name": "From", "value": sender},
                    {"name": "To", "value": recipient},
                    {"name": "Subject", "value": subject},
                    {"name": "Message-ID", "value": f"<{message_id}@mail.invalid>"},
                ],
                "parts": parts,
            },
        }
        self.messages[message_id] = msg

        # Append to history
        self.history_records.append({
            "id": hid,
            "messagesAdded": [{"message": {"id": message_id, "threadId": tid}}],
        })

    def watch(self, topic_name: str, label_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        self._check_fault_injection("watch")
        expiration_ms = str(int((time.time() + 7 * 86400) * 1000))
        self.active_watch = {
            "topicName": topic_name,
            "labelIds": label_ids or ["INBOX"],
            "historyId": self.current_history_id,
            "expiration": expiration_ms,
        }
        return {"historyId": self.current_history_id, "expiration": expiration_ms}

    def stop_watch(self) -> None:
        self._check_fault_injection("stop")
        self.stop_called = True
        self.active_watch = None

    def list_history(
        self,
        start_history_id: str,
        label_id: Optional[str] = None,
        max_results: int = 100,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._check_fault_injection("history")
        if self.simulate_stale_history:
            raise StaleHistoryCursorError(history_id=start_history_id)

        try:
            start_num = int(start_history_id)
        except ValueError:
            start_num = 0

        matching = [
            h for h in self.history_records
            if int(h.get("id", 0)) > start_num
        ]

        return {
            "history": matching[:max_results],
            "historyId": self.current_history_id,
        }

    def get_message(self, message_id: str, format: str = "full") -> Dict[str, Any]:
        self._check_fault_injection("get_message")
        if message_id not in self.messages:
            raise TransportError(f"Message '{message_id}' not found in mock store")
        return self.messages[message_id]

    def get_attachment(self, message_id: str, attachment_id: str) -> bytes:
        self._check_fault_injection("get_attachment")
        key = f"{message_id}:{attachment_id}"
        if key not in self.attachments:
            raise TransportError(f"Attachment '{key}' not found in mock store")
        return self.attachments[key]

    def list_messages(
        self, query: str, max_results: int = 50, page_token: Optional[str] = None
    ) -> Dict[str, Any]:
        self._check_fault_injection("list_messages")
        # Simple substring matching on subject or all messages
        results = []
        for mid, msg in self.messages.items():
            results.append({"id": mid, "threadId": msg.get("threadId", "")})
        return {"messages": results[:max_results]}

    def send_message(self, raw_mime_bytes: bytes, thread_id: Optional[str] = None) -> Dict[str, Any]:
        self._check_fault_injection("send_message")
        msg_id = f"sent-{len(self.sent_messages) + 1}"
        tid = thread_id or f"thread-{msg_id}"
        record = {
            "id": msg_id,
            "threadId": tid,
            "raw_mime_bytes": raw_mime_bytes,
        }
        self.sent_messages.append(record)
        return {"id": msg_id, "threadId": tid}

    def _check_fault_injection(self, op_name: str) -> None:
        if self.rate_limit_failures_remaining > 0:
            self.rate_limit_failures_remaining -= 1
            raise RateLimitExceededError(
                retry_after_seconds=5.0,
                details={"op": op_name, "reason": "Simulated 429 quota exhaustion"},
            )
        if self.server_error_failures_remaining > 0:
            self.server_error_failures_remaining -= 1
            raise TransportError(
                f"Simulated HTTP 503 Service Unavailable during {op_name}",
                details={"status_code": 503},
            )

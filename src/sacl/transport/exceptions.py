"""SACL V1 Transport Subsystem Exceptions.

Constitutional typed exceptions for transport layer operations:
Gmail API OAuth2 adapter, users.watch lifecycle, Pub/Sub subscriber,
History API reconciliation, zip sanitization, deduplication, and outbox dispatch.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from sacl.contracts.exceptions import ArchitectureInvariantError, QuarantineError, SaclError


class TransportError(SaclError):
    """Base exception for all transport-related errors."""
    pass


class TransportAuthError(TransportError):
    """Raised when transport authentication (OAuth2 token, refresh token) fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(f"TRANSPORT_AUTH_ERROR: {message}", details=details)


class RateLimitExceededError(TransportError):
    """Raised when Gmail API returns HTTP 429 Too Many Requests."""

    def __init__(self, retry_after_seconds: Optional[float] = None, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            f"RATE_LIMIT_EXCEEDED: Gmail API quota / rate limit exceeded. Retry after: {retry_after_seconds}s",
            details={"retry_after_seconds": retry_after_seconds, **(details or {})},
        )
        self.retry_after_seconds = retry_after_seconds


class StaleHistoryCursorError(TransportError):
    """Raised when Gmail History API returns HTTP 404 (History ID not found / expired).

    Per docs/MAIL_PROTOCOL.md §3.3, triggers safe full-sync fallback.
    """

    def __init__(self, history_id: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            f"STALE_HISTORY_CURSOR: History ID '{history_id}' is stale or expired (>7 days). "
            "Safe full-sync fallback required.",
            details={"history_id": history_id, **(details or {})},
        )
        self.history_id = history_id


class DuplicateDeliveryError(TransportError):
    """Raised or noted when an identical message or package hash was already received."""

    def __init__(self, message_id: str, job_id: Optional[str] = None, nonce: Optional[str] = None) -> None:
        super().__init__(
            f"DUPLICATE_DELIVERY: Message '{message_id}' (job: '{job_id}', nonce: '{nonce}') was already processed.",
            details={"message_id": message_id, "job_id": job_id, "nonce": nonce},
        )
        self.message_id = message_id
        self.job_id = job_id
        self.nonce = nonce


class PayloadConflictError(TransportError):
    """Raised when an inbound package presents the same job_id but with a divergent SHA-256 hash.

    Violates ADR-010 deduplication invariants; triggers conflict reply and rejection.
    """

    def __init__(self, job_id: str, existing_sha: str, incoming_sha: str) -> None:
        super().__init__(
            f"PAYLOAD_CONFLICT: Conflict for job '{job_id}'. Stored SHA-256 ({existing_sha}) "
            f"does not match incoming SHA-256 ({incoming_sha}). Rejecting resubmission fail-closed.",
            details={
                "job_id": job_id,
                "existing_sha": existing_sha,
                "incoming_sha": incoming_sha,
            },
        )
        self.job_id = job_id
        self.existing_sha = existing_sha
        self.incoming_sha = incoming_sha


class SenderNotWhitelistedError(QuarantineError):
    """Raised when an inbound message sender does not match the authorized whitelist."""

    def __init__(self, sender: str, expected_sender: str) -> None:
        super().__init__(
            package_id=f"sender-{sender}",
            reason=f"Sender '{sender}' is not whitelisted. Authorized sender: '{expected_sender}'",
        )
        self.sender = sender
        self.expected_sender = expected_sender


class InvalidRoutingHintError(TransportError):
    """Raised when an inbound email subject fails canonical routing hint syntax."""

    def __init__(self, raw_subject: str, expected_pattern: str) -> None:
        super().__init__(
            f"INVALID_ROUTING_HINT: Subject '{raw_subject}' does not conform to pattern '{expected_pattern}'",
            details={"raw_subject": raw_subject, "expected_pattern": expected_pattern},
        )
        self.raw_subject = raw_subject


class ZipDefenseViolation(QuarantineError):
    """Base exception for zip extraction defense pipeline violations."""

    def __init__(self, package_id: str, violation_type: str, reason: str) -> None:
        super().__init__(package_id, f"ZIP_DEFENSE_VIOLATION [{violation_type}]: {reason}")
        self.violation_type = violation_type


class ZipResourceLimitExceededError(ZipDefenseViolation):
    """Step 1: Resource exhaustion quota exceeded (zip bomb defense)."""

    def __init__(self, package_id: str, metric: str, actual: Any, limit: Any) -> None:
        super().__init__(
            package_id=package_id,
            violation_type="ZIP_RESOURCE_LIMIT_EXCEEDED",
            reason=f"Resource metric '{metric}' exceeded limit: actual {actual} > limit {limit}",
        )
        self.metric = metric
        self.actual = actual
        self.limit = limit


class ZipPathTraversalError(ZipDefenseViolation):
    """Step 2: Path traversal detected (Anti-Zip Slip)."""

    def __init__(self, package_id: str, entry_name: str) -> None:
        super().__init__(
            package_id=package_id,
            violation_type="ZIP_PATH_TRAVERSAL_DETECTED",
            reason=f"Entry '{entry_name}' attempts path traversal or escapes destination directory",
        )
        self.entry_name = entry_name


class InvalidFilenameError(ZipDefenseViolation):
    """Step 3: DOS device name or Alternate Data Stream detected."""

    def __init__(self, package_id: str, entry_name: str, pattern: str) -> None:
        super().__init__(
            package_id=package_id,
            violation_type="INVALID_FILENAME_CHARACTER",
            reason=f"Entry '{entry_name}' matches prohibited pattern / reserved device name: '{pattern}'",
        )
        self.entry_name = entry_name
        self.pattern = pattern


class SymlinkNotPermittedError(ZipDefenseViolation):
    """Step 4: Symlink, hardlink, or reparse point detected in zip archive."""

    def __init__(self, package_id: str, entry_name: str) -> None:
        super().__init__(
            package_id=package_id,
            violation_type="SYMLINK_NOT_PERMITTED",
            reason=f"Entry '{entry_name}' contains symlink or reparse point attributes",
        )
        self.entry_name = entry_name

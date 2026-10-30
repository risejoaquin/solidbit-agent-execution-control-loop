"""SACL V1 Security Subsystem Exceptions.

Constitutional typed security exceptions implementing defense-in-depth enforcement:
- Archive admission & zip sanitization
- Path traversal & Windows filename defenses
- Resource quotas & zip bomb prevention
- Sender & channel authorization
- Data exfiltration defense
- Secret redaction & zero secrets invariant
- Hard local policy deny-list enforcement
- Workspace confinement & dirty-root rules
- Anti-recycling safe stop safety refusal
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from sacl.contracts.exceptions import (
    HardDenyViolation,
    ProcessObservationError,
    SaclError,
)
from sacl.transport.exceptions import (
    InvalidFilenameError,
    SenderNotWhitelistedError,
    SymlinkNotPermittedError,
    ZipPathTraversalError,
    ZipResourceLimitExceededError,
)


class SecurityError(SaclError):
    """Base exception for all SACL security subsystem errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(f"SECURITY_ERROR: {message}", details=details)


class ArchiveAdmissionError(SecurityError):
    """Raised when an incoming archive package fails admission checks."""

    def __init__(
        self,
        package_id: str,
        reason: str,
        violation_code: str = "ADMISSION_FAILED",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        det = {"package_id": package_id, "violation_code": violation_code, **(details or {})}
        super().__init__(
            f"Archive '{package_id}' admission failed [{violation_code}]: {reason}", details=det
        )
        self.package_id = package_id
        self.reason = reason
        self.violation_code = violation_code


class PathTraversalSecurityError(SecurityError, ZipPathTraversalError):
    """Raised when a path traversal attempt is detected (Threat T1 / TH-04)."""

    def __init__(self, entry_name: str, package_id: str = "unknown") -> None:
        ZipPathTraversalError.__init__(self, package_id=package_id, entry_name=entry_name)
        self.message = (
            f"SECURITY_ERROR: ZIP_PATH_TRAVERSAL_DETECTED: Entry '{entry_name}' escapes destination"
        )


class InvalidFilenameSecurityError(SecurityError, InvalidFilenameError):
    """Raised when a prohibited DOS device name or Alternate Data Stream is detected (Threat T1)."""

    def __init__(self, entry_name: str, pattern: str, package_id: str = "unknown") -> None:
        InvalidFilenameError.__init__(
            self, package_id=package_id, entry_name=entry_name, pattern=pattern
        )
        self.message = (
            f"SECURITY_ERROR: INVALID_FILENAME_CHARACTER: Entry '{entry_name}' matches '{pattern}'"
        )


class SymlinkSecurityError(SecurityError, SymlinkNotPermittedError):
    """Raised when a symlink, hardlink, or reparse point is detected in an archive (Threat T1)."""

    def __init__(self, entry_name: str, package_id: str = "unknown") -> None:
        SymlinkNotPermittedError.__init__(self, package_id=package_id, entry_name=entry_name)
        self.message = f"SECURITY_ERROR: SYMLINK_NOT_PERMITTED: Entry '{entry_name}' is symlink or reparse point"


class ResourceLimitExceededError(SecurityError, ZipResourceLimitExceededError):
    """Raised when decompression or processing exceeds resource quotas (Threat D1 / TH-11)."""

    def __init__(self, metric: str, actual: Any, limit: Any, package_id: str = "unknown") -> None:
        ZipResourceLimitExceededError.__init__(
            self, package_id=package_id, metric=metric, actual=actual, limit=limit
        )
        self.message = (
            f"SECURITY_ERROR: ZIP_RESOURCE_LIMIT_EXCEEDED: Metric '{metric}' exceeded limit "
            f"(actual: {actual}, limit: {limit})"
        )


class UnauthorizedSenderError(SecurityError, SenderNotWhitelistedError):
    """Raised when an inbound message sender is not in the authorized whitelist (Threat S1 / TH-01)."""

    def __init__(self, sender: str, expected_sender: str) -> None:
        SenderNotWhitelistedError.__init__(self, sender=sender, expected_sender=expected_sender)
        self.message = (
            f"SECURITY_ERROR: UNAUTHORIZED_SENDER: Sender '{sender}' is not whitelisted. "
            f"Authorized sender: '{expected_sender}'"
        )


class UnauthorizedChannelError(SecurityError):
    """Raised when an inbound or approval channel is not authorized in V1 (ADR-007 / ADR-008)."""

    def __init__(self, channel: str, allowed_channels: List[str]) -> None:
        super().__init__(
            f"UNAUTHORIZED_CHANNEL: Channel '{channel}' is prohibited. Allowed: {allowed_channels}",
            details={"channel": channel, "allowed_channels": allowed_channels},
        )
        self.channel = channel
        self.allowed_channels = allowed_channels


class DataExfiltrationAttemptError(SecurityError):
    """Raised when outbound communication targets an unauthorized recipient (Threat I2 / TH-10)."""

    def __init__(self, recipient: str, authorized_recipient: str) -> None:
        super().__init__(
            f"DATA_EXFILTRATION_PREVENTED: Outbound delivery to '{recipient}' blocked. "
            f"Outbound recipient strictly restricted to '{authorized_recipient}'.",
            details={"recipient": recipient, "authorized_recipient": authorized_recipient},
        )
        self.recipient = recipient
        self.authorized_recipient = authorized_recipient


class SecretLeakError(SecurityError):
    """Raised when unredacted secrets or credentials are found in source, state, or output (Threat I1 / TH-09)."""

    def __init__(self, secret_type: str, context: str, sample_masked: str) -> None:
        super().__init__(
            f"SECRET_LEAK_DETECTED: Found {secret_type} in {context}: '{sample_masked}'",
            details={
                "secret_type": secret_type,
                "context": context,
                "sample_masked": sample_masked,
            },
        )
        self.secret_type = secret_type
        self.context = context
        self.sample_masked = sample_masked


class HardDenySecurityError(SecurityError, HardDenyViolation):
    """Raised when an operation attempts an action permanently prohibited by hard local policy."""

    def __init__(
        self, action: str, reason: str = "Action is unconditionally hard-denied in V1"
    ) -> None:
        HardDenyViolation.__init__(self, action=action, reason=reason)
        self.message = f"SECURITY_ERROR: HARD_DENY_VIOLATION: Action '{action}' is strictly prohibited. {reason}"


class MainBranchProhibitedError(SecurityError):
    """Raised when execution targets protected main/master branches (Threat E1 / TH-13)."""

    def __init__(self, branch: str) -> None:
        super().__init__(
            f"MAIN_BRANCH_NOT_ALLOWED: Agent execution targeting protected branch '{branch}' is prohibited.",
            details={"branch": branch, "violation": "MAIN_BRANCH_NOT_ALLOWED"},
        )
        self.branch = branch


class PrimaryCheckoutProhibitedError(SecurityError):
    """Raised when execution targets the primary git checkout instead of an isolated worktree (Threat T3)."""

    def __init__(self, path: str) -> None:
        super().__init__(
            f"PRIMARY_CHECKOUT_NOT_ALLOWED: Execution in primary checkout at '{path}' is prohibited. "
            "Must execute inside isolated secondary worktree.",
            details={"path": path, "violation": "PRIMARY_CHECKOUT_NOT_ALLOWED"},
        )
        self.path = path


class BypassAcknowledgementRequiredError(SecurityError):
    """Raised when headless worker execution is invoked without explicit bypass acknowledgement."""

    def __init__(self) -> None:
        super().__init__(
            "BYPASS_ACK_REQUIRED: Headless worker execution requires explicit -BypassAcknowledged acknowledgement.",
            details={"violation": "BYPASS_ACK_REQUIRED"},
        )


class SafetyRefusalError(SecurityError, ProcessObservationError):
    """Raised when process stop is refused due to image mismatch or PID recycling (Threat S3 / TH-03)."""

    def __init__(self, pid: int, reason: str) -> None:
        ProcessObservationError.__init__(self, pid=pid, reason=reason)
        self.message = (
            f"SECURITY_ERROR: SAFETY_REFUSAL: Process stop for PID {pid} refused: {reason}"
        )
        self.pid = pid
        self.reason = reason


class RemoteProductionProhibitedError(SecurityError):
    """Raised when an operation targets remote production infrastructure in V1 (Threat E2 / TH-14)."""

    def __init__(self, action: str, target: Optional[str] = None) -> None:
        super().__init__(
            f"REMOTE_PRODUCTION_DISABLED: Action '{action}' targeting '{target or 'remote'}' is disabled in V1 "
            "(Decision Baseline #25). Dry-run plan generation only.",
            details={"action": action, "target": target, "violation": "REMOTE_PRODUCTION_DISABLED"},
        )
        self.action = action
        self.target = target


class PromptGovernanceError(SecurityError):
    """Raised when prompt fails machine governance headers verification (Threat T2 / TH-05)."""

    def __init__(self, missing_headers: List[str]) -> None:
        super().__init__(
            f"PROMPT_GOVERNANCE_MISSING: Prompt is missing required machine governance headers: {missing_headers}",
            details={"missing_headers": missing_headers, "violation": "PROMPT_GOVERNANCE_MISSING"},
        )
        self.missing_headers = missing_headers

"""SACL V1 Security Subsystem Package.

Canonical security enforcement helpers and threat mitigation controls for SACL V1:
- Archive admission & package staging
- Path normalization & Anti-Zip Slip defense
- Resource quotas & zip bomb prevention
- Sender, channel & anti-exfiltration validation
- Secret redaction & zero secrets invariant
- Hard local policy deny-list enforcement & machine governance injection
- Workspace confinement & local dirty-root rules
- Anti-recycling safe stop process observation
"""

from __future__ import annotations

from sacl.security.admission import (
    AdmissionDecision,
    AdmissionStatus,
    ArchiveAdmissionController,
)
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
    ArchiveAdmissionError,
    BypassAcknowledgementRequiredError,
    DataExfiltrationAttemptError,
    HardDenySecurityError,
    InvalidFilenameSecurityError,
    MainBranchProhibitedError,
    PathTraversalSecurityError,
    PrimaryCheckoutProhibitedError,
    PromptGovernanceError,
    RemoteProductionProhibitedError,
    ResourceLimitExceededError,
    SafetyRefusalError,
    SecretLeakError,
    SecurityError,
    SymlinkSecurityError,
    UnauthorizedChannelError,
    UnauthorizedSenderError,
)
from sacl.security.guards import (
    MANDATORY_GOVERNANCE_DIRECTIVES,
    PROTECTED_BRANCHES,
    assert_action_not_hard_denied,
    assert_caller_acknowledgement,
    assert_clean_root,
    assert_no_file_collision,
    assert_not_main_branch,
    assert_prompt_governance,
    assert_remote_production_disabled,
    assert_safe_process_stop,
    assert_worktree_confinement,
    detect_cross_agent_file_collisions,
    inject_governance_headers,
    is_hard_denied,
    verify_governance_headers,
)
from sacl.security.path_sanitizer import (
    DOS_DEVICE_NAMES,
    assert_within_boundary,
    has_alternate_data_stream,
    is_dos_device_name,
    is_symlink_or_reparse,
    normalize_path,
    sanitize_relative_path,
    validate_safe_path,
)
from sacl.security.redaction import (
    REDACTION_MARKER,
    SecretFinding,
    SecretRedactor,
    StreamingSecretRedactor,
    assert_zero_secrets,
    redact_secrets,
    scan_for_secrets,
)
from sacl.security.resource_limits import (
    DEFAULT_MAX_COMPRESSED_BYTES,
    DEFAULT_MAX_COMPRESSION_RATIO,
    DEFAULT_MAX_TOTAL_FILE_COUNT,
    DEFAULT_MAX_UNCOMPRESSED_BYTES,
    ResourceLimitValidator,
    ResourceQuotas,
    StreamingExtractionBudgetTracker,
    assert_concurrency_within_limit,
    assert_timeout_non_killing,
)

__all__ = [
    # Admission
    "AdmissionDecision",
    "AdmissionStatus",
    "ArchiveAdmissionController",
    # Channel & Sender
    "DEFAULT_AUTHORIZED_EMAIL",
    "extract_email_address",
    "validate_inbound_sender",
    "assert_authorized_sender",
    "validate_routing_hint",
    "assert_valid_routing_hint",
    "validate_outbound_recipient",
    "assert_authorized_recipient",
    "validate_approval_channel",
    "assert_authorized_approval_channel",
    "assert_no_public_inbound_webhooks",
    # Path Sanitizer
    "DOS_DEVICE_NAMES",
    "normalize_path",
    "sanitize_relative_path",
    "is_dos_device_name",
    "has_alternate_data_stream",
    "is_symlink_or_reparse",
    "validate_safe_path",
    "assert_within_boundary",
    # Resource Limits
    "DEFAULT_MAX_COMPRESSED_BYTES",
    "DEFAULT_MAX_UNCOMPRESSED_BYTES",
    "DEFAULT_MAX_TOTAL_FILE_COUNT",
    "DEFAULT_MAX_COMPRESSION_RATIO",
    "ResourceQuotas",
    "ResourceLimitValidator",
    "StreamingExtractionBudgetTracker",
    "assert_concurrency_within_limit",
    "assert_timeout_non_killing",
    # Redaction
    "REDACTION_MARKER",
    "SecretFinding",
    "SecretRedactor",
    "StreamingSecretRedactor",
    "redact_secrets",
    "scan_for_secrets",
    "assert_zero_secrets",
    # Guards
    "MANDATORY_GOVERNANCE_DIRECTIVES",
    "PROTECTED_BRANCHES",
    "is_hard_denied",
    "assert_action_not_hard_denied",
    "inject_governance_headers",
    "verify_governance_headers",
    "assert_prompt_governance",
    "assert_caller_acknowledgement",
    "assert_not_main_branch",
    "assert_worktree_confinement",
    "assert_clean_root",
    "assert_safe_process_stop",
    "assert_remote_production_disabled",
    "detect_cross_agent_file_collisions",
    "assert_no_file_collision",
    # Exceptions
    "SecurityError",
    "ArchiveAdmissionError",
    "PathTraversalSecurityError",
    "InvalidFilenameSecurityError",
    "SymlinkSecurityError",
    "ResourceLimitExceededError",
    "UnauthorizedSenderError",
    "UnauthorizedChannelError",
    "DataExfiltrationAttemptError",
    "SecretLeakError",
    "HardDenySecurityError",
    "MainBranchProhibitedError",
    "PrimaryCheckoutProhibitedError",
    "BypassAcknowledgementRequiredError",
    "SafetyRefusalError",
    "RemoteProductionProhibitedError",
    "PromptGovernanceError",
]

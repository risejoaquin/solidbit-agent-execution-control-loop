"""SACL V1 Bounded Human Approval & Same-Run Resumption Package.

Constitutional Invariants (ADR-007, SB-FREEZE-P1-06):
- Authority is sovereign, human, non-delegable, and fail-closed by default.
- Bounded token strictly bound to: (job_id, action, scope, request_id, expires_at).
- Approvals RESUME the same logical run; they never spawn orphan runs.
- Approvals CANNOT override hard local policy denies under any circumstance.
- Channels are strictly CLI, GMAIL, MANUAL (zero webhooks in V1).
"""

from sacl.approval.channels import (
    AUTHORIZED_EMAIL_SENDERS,
    DEFAULT_SOVEREIGN_IDENTITY,
    CLIChannelHandler,
    GmailChannelHandler,
    ManualChannelHandler,
)
from sacl.approval.manager import BoundedApprovalManager
from sacl.approval.models import (
    ApprovalDecisionOutcome,
    ApprovalRequest,
    ApprovalToken,
    Approver,
    ResumptionContext,
    utc_now_iso,
)
from sacl.approval.resumption import SameRunResumptionManager
from sacl.approval.validator import (
    BoundedApprovalValidator,
    format_iso_datetime,
    is_scope_covered,
    matches_scope_pattern,
    parse_iso_datetime,
    token_to_schema_dict,
)

__all__ = [
    # Models
    "ApprovalRequest",
    "ApprovalDecisionOutcome",
    "ResumptionContext",
    "ApprovalToken",
    "Approver",
    "utc_now_iso",
    # Validator
    "BoundedApprovalValidator",
    "parse_iso_datetime",
    "format_iso_datetime",
    "matches_scope_pattern",
    "is_scope_covered",
    "token_to_schema_dict",
    # Channels
    "CLIChannelHandler",
    "GmailChannelHandler",
    "ManualChannelHandler",
    "DEFAULT_SOVEREIGN_IDENTITY",
    "AUTHORIZED_EMAIL_SENDERS",
    # Manager
    "BoundedApprovalManager",
    # Resumption
    "SameRunResumptionManager",
]

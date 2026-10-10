"""SACL V1 Bounded Approval Data Models & Types.

Constitutional Invariant (ADR-007, SB-FREEZE-P1-06):
Approvals are strictly bound to: (job_id, action, scope, request_id, expires_at).
Approvals resume the same logical run and CANNOT override hard local policy denies.
Channels in V1 are strictly CLI, GMAIL, MANUAL (zero webhooks).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sacl.contracts.models import ApprovalToken, Approver


def utc_now_iso() -> str:
    """Returns current UTC timestamp formatted as ISO-8601 string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class ApprovalRequest:
    """Request representation for human action gate approval."""

    request_id: str
    job_id: str
    action: str
    scope: List[str]
    expires_at: str
    run_id: Optional[str] = None
    package_id: Optional[str] = None
    status: str = "PENDING"  # PENDING, APPROVED, REJECTED, EXPIRED, REVOKED
    created_at: str = field(default_factory=utc_now_iso)
    reason: Optional[str] = None
    prohibited_actions: List[str] = field(default_factory=list)
    remaining_blockers: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Converts to dictionary representation."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ApprovalRequest:
        """Instantiates ApprovalRequest from dictionary."""
        return cls(
            request_id=data["request_id"],
            job_id=data["job_id"],
            action=data["action"],
            scope=list(data["scope"]),
            expires_at=data["expires_at"],
            run_id=data.get("run_id"),
            package_id=data.get("package_id"),
            status=data.get("status", "PENDING"),
            created_at=data.get("created_at", utc_now_iso()),
            reason=data.get("reason"),
            prohibited_actions=list(data.get("prohibited_actions", [])),
            remaining_blockers=list(data.get("remaining_blockers", [])),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class ApprovalDecisionOutcome:
    """Outcome of recording a human approval decision."""

    request_id: str
    decision: str  # APPROVED, REJECTED, DEFERRED
    status: str
    token: Optional[ApprovalToken] = None
    resumed_run_id: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.token:
            d["token"] = self.token.to_dict()
        return d


@dataclass
class ResumptionContext:
    """Context resulting from executing same-run resumption."""

    success: bool
    run_id: str
    job_id: str
    status: str
    message: str
    resumed_at: str = field(default_factory=utc_now_iso)
    token: Optional[ApprovalToken] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.token:
            d["token"] = self.token.to_dict()
        return d


__all__ = [
    "ApprovalRequest",
    "ApprovalDecisionOutcome",
    "ResumptionContext",
    "ApprovalToken",
    "Approver",
    "utc_now_iso",
]

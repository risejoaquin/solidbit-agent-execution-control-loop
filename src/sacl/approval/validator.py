"""SACL V1 Bounded Approval Validator.

Enforces constitutional invariants for approval tokens:
- Bounded to: (job_id, action, scope, request_id, expires_at).
- Channels strictly restricted to CLI, GMAIL, MANUAL (zero webhooks in V1).
- Cannot override hard local policy denies under any circumstance (Hard deny always wins).
- Fail-closed upon expiration.
- Resumes the same logical run.
"""

from __future__ import annotations

import fnmatch
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sacl.contracts.exceptions import (
    ApprovalExpiredError,
    ContractValidationError,
    HardDenyViolation,
    PolicyDeniedError,
)
from sacl.contracts.invariants import (
    APPROVAL_CHANNELS_V1,
    HARD_DENIED_ACTIONS,
    ApprovalDecision,
)
from sacl.contracts.models import ApprovalToken
from sacl.contracts.schema_validator import SchemaValidator, get_default_validator
from sacl.policy.hard_policy import normalize_action


def parse_iso_datetime(dt_str: str) -> datetime:
    """Parses ISO 8601 UTC timestamp safely."""
    clean = dt_str.replace("Z", "+00:00")
    dt = datetime.fromisoformat(clean)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def format_iso_datetime(dt: Optional[datetime] = None) -> str:
    """Formats datetime to canonical ISO 8601 UTC string."""
    d = dt or datetime.now(timezone.utc)
    return d.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def matches_scope_pattern(scope_pattern: str, target_path: str) -> bool:
    """Evaluates whether a target path matches a scope pattern (e.g. docs/*, schemas/*)."""
    pat = scope_pattern.strip().replace("\\", "/")
    target = target_path.strip().replace("\\", "/")

    if pat == "*" or pat == "**":
        return True
    if pat == target:
        return True
    if fnmatch.fnmatch(target, pat):
        return True
    if pat.endswith("/*") and target.startswith(pat[:-2] + "/"):
        return True
    if not pat.endswith("*") and target.startswith(pat.rstrip("/") + "/"):
        return True
    return False


def is_scope_covered(approved_scopes: List[str], requested_items: List[str]) -> bool:
    """Verifies that all requested items are covered by approved scope patterns."""
    if not requested_items:
        return True
    for item in requested_items:
        if not any(matches_scope_pattern(pattern, item) for pattern in approved_scopes):
            return False
    return True


def token_to_schema_dict(token: ApprovalToken) -> Dict[str, Any]:
    """Converts ApprovalToken to schema dictionary conforming to approval.schema.json."""
    raw = token.to_dict()
    clean: Dict[str, Any] = {}
    for k, v in raw.items():
        if v is not None:
            clean[k] = v
    if token.approver:
        app_dict = token.approver.to_dict()
        clean["approver"] = {
            k: v for k, v in app_dict.items() if v is not None or k == "approved_at"
        }
    return clean


class BoundedApprovalValidator:
    """Validates bounded human approval tokens against constitutional invariants and schemas."""

    def __init__(self, validator: Optional[SchemaValidator] = None) -> None:
        self.validator = validator or get_default_validator()

    def validate_schema(self, token: ApprovalToken) -> None:
        """Validates ApprovalToken payload against approval.schema.json."""
        self.validator.validate_approval(token_to_schema_dict(token))

    def validate_invariants(
        self,
        token: ApprovalToken,
        reference_time: Optional[datetime] = None,
    ) -> None:
        """Validates all architectural invariants on an approval token.

        Raises:
            HardDenyViolation: If token attempts to override a hard denial.
            ApprovalExpiredError: If token has expired.
            ContractValidationError: If token structure violates rules.
            PolicyDeniedError: If decision is not APPROVED.
        """
        # 1. Hard Deny Supremacy Invariant: Human approval CANNOT override hard denials
        canonical_action = normalize_action(token.action)
        if canonical_action in HARD_DENIED_ACTIONS:
            raise HardDenyViolation(
                action=token.action,
                reason=(
                    f"Approval Override Prohibited Invariant Violation: Bounded approval token "
                    f"'{token.request_id}' cannot authorize hard-denied action '{token.action}'. "
                    f"Hard deny unconditionally wins."
                ),
            )

        if not token.cannot_override_hard_deny:
            raise HardDenyViolation(
                action="token_flag_cannot_override_hard_deny",
                reason="Constitutional Invariant: cannot_override_hard_deny must strictly be true.",
            )

        # 2. Schema check against approval.schema.json
        self.validate_schema(token)

        # 3. Channel restriction: strictly CLI, GMAIL, MANUAL (zero webhooks in V1)
        if token.approver.channel not in APPROVAL_CHANNELS_V1:
            raise ContractValidationError(
                schema_name="approval",
                message=(
                    f"Invalid approver channel '{token.approver.channel}'. "
                    f"Only {sorted(list(APPROVAL_CHANNELS_V1))} are permitted in V1."
                ),
            )

        # 4. Fail-closed Expiration Check
        now = reference_time or datetime.now(timezone.utc)
        expires_at = parse_iso_datetime(token.expires_at)
        if now > expires_at:
            raise ApprovalExpiredError(
                request_id=token.request_id,
                expires_at=token.expires_at,
            )

        # 5. Decision check
        if token.decision != ApprovalDecision.APPROVED.value:
            raise PolicyDeniedError(
                action=token.action,
                layer="APPROVAL_TOKEN",
                reason=f"Approval token '{token.request_id}' has non-approved decision '{token.decision}'.",
            )

    def validate_binding(
        self,
        token: ApprovalToken,
        job_id: str,
        action: str,
        requested_scope: Optional[List[str]] = None,
        reference_time: Optional[datetime] = None,
    ) -> None:
        """Validates that token strictly matches target (job_id, action, scope).

        Raises:
            PolicyDeniedError: If binding does not match.
            ApprovalExpiredError: If token has expired.
            HardDenyViolation: If action is hard denied.
        """
        self.validate_invariants(token, reference_time=reference_time)

        # Job ID binding check
        if token.job_id != job_id:
            raise PolicyDeniedError(
                action=action,
                layer="APPROVAL_TOKEN",
                reason=(
                    f"Token binding mismatch: token '{token.request_id}' is bound to job_id '{token.job_id}', "
                    f"not '{job_id}'."
                ),
            )

        # Action binding check
        norm_expected = normalize_action(action)
        norm_token = normalize_action(token.action)
        if norm_expected != norm_token:
            raise PolicyDeniedError(
                action=action,
                layer="APPROVAL_TOKEN",
                reason=(
                    f"Token binding mismatch: token '{token.request_id}' is bound to action '{token.action}', "
                    f"not '{action}'."
                ),
            )

        # Scope containment check
        if requested_scope:
            if not is_scope_covered(token.scope, requested_scope):
                raise PolicyDeniedError(
                    action=action,
                    layer="APPROVAL_TOKEN",
                    reason=(
                        f"Scope containment failure: token '{token.request_id}' scope {token.scope} "
                        f"does not cover requested scope {requested_scope}."
                    ),
                )


__all__ = [
    "BoundedApprovalValidator",
    "parse_iso_datetime",
    "format_iso_datetime",
    "matches_scope_pattern",
    "is_scope_covered",
    "token_to_schema_dict",
]

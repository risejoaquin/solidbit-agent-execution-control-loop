"""SACL V1 Bounded Human Action Gate & Generic Approval Contract.

Constitutional Invariant (ADR-007 & Authority Model §4):
Authority is sovereign, strictly human, non-delegable for irreversible actions,
and fail-closed by default.
Approval tokens are generic bounded action tokens strictly bound to:
(job_id, action, scope, request_id, expires_at).
Approvals RESUME the same logical run and CANNOT override hard local policy denies.
"""

from __future__ import annotations

from datetime import datetime, timezone
import fnmatch
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import uuid

from sacl.contracts.exceptions import (
    ApprovalExpiredError,
    ContractValidationError,
    HardDenyViolation,
    PolicyDeniedError,
)
from sacl.contracts.invariants import (
    APPROVAL_BINDING_FIELDS,
    APPROVAL_CHANNELS_V1,
    ApprovalChannel,
    ApprovalDecision,
    HARD_DENIED_ACTIONS,
)
from sacl.contracts.interfaces import IApprovalManager
from sacl.contracts.models import ApprovalToken, Approver
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


def _safe_scope_reference(value: str, *, is_pattern: bool = False) -> bool:
    """Fail closed on noncanonical, unsafe or Windows-ambiguous relative paths."""
    if not isinstance(value, str) or any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        return False
    normalized = value.replace("\\", "/")
    if not normalized or normalized != normalized.strip():
        return False
    # Absolute, UNC, drive-relative/absolute and alternate data stream paths.
    if normalized.startswith("/") or ":" in normalized or any(ch in normalized for ch in '<>|"'):
        return False
    if not is_pattern and any(ch in normalized for ch in "*?[]"):
        return False
    reserved = {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"}
    reserved.update(f"COM{i}" for i in range(1, 10))
    reserved.update(f"LPT{i}" for i in range(1, 10))
    for part in normalized.split("/"):
        if part in ("", ".", "..") or part.endswith((".", " ")):
            return False
        if part.split(".", 1)[0].upper() in reserved:
            return False
    return True


def matches_scope_pattern(scope_pattern: str, target_path: str) -> bool:
    """Evaluates whether a target path matches a scope pattern (e.g. docs/*)."""
    if not _safe_scope_reference(scope_pattern, is_pattern=True) or not _safe_scope_reference(target_path):
        return False
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
    """Converts ApprovalToken to JSON-schema compatible dictionary, omitting unset optional fields."""
    raw = token.to_dict()
    clean: Dict[str, Any] = {}
    for k, v in raw.items():
        if v is not None:
            clean[k] = v
    if token.approver:
        app_dict = token.approver.to_dict()
        clean["approver"] = {k: v for k, v in app_dict.items() if v is not None or k == "approved_at"}
    return clean


class ApprovalValidator:
    """Validates bounded approval tokens against constitutional invariants."""

    def __init__(self, validator: Optional[SchemaValidator] = None) -> None:
        self.validator = validator or get_default_validator()

    def validate_schema(self, token: ApprovalToken) -> None:
        """Validates ApprovalToken against approval.schema.json."""
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
        """
        # 1. Hard Deny Invariant: Approval CANNOT override hard deny
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

        # 2. Schema check
        self.validate_schema(token)

        # 3. Channel restriction: CLI, GMAIL, MANUAL (no webhooks)
        if token.approver.channel not in APPROVAL_CHANNELS_V1:
            raise ContractValidationError(
                schema_name="approval",
                message=(
                    f"Invalid approver channel '{token.approver.channel}'. "
                    f"Only {sorted(list(APPROVAL_CHANNELS_V1))} are permitted in V1."
                ),
            )

        # 4. Expiration check (Fail-closed)
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
        """Validates that token strictly matches the target (job_id, action, scope).

        Raises:
            PolicyDeniedError: If binding does not match.
            ApprovalExpiredError: If token has expired.
            HardDenyViolation: If action is hard denied.
        """
        self.validate_invariants(token, reference_time=reference_time)

        # Job ID binding
        if token.job_id != job_id:
            raise PolicyDeniedError(
                action=action,
                layer="APPROVAL_TOKEN",
                reason=(
                    f"Token binding mismatch: token '{token.request_id}' is bound to job_id '{token.job_id}', "
                    f"not '{job_id}'."
                ),
            )

        # Action binding
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

        # Scope binding
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


class ApprovalManager(IApprovalManager):
    """Manages bounded human approval action gates."""

    def __init__(self, validator: Optional[SchemaValidator] = None) -> None:
        self.validator = ApprovalValidator(validator=validator)
        self._requests: Dict[str, Dict[str, Any]] = {}
        self._tokens: Dict[str, ApprovalToken] = {}

    def create_approval_request(
        self,
        job_id: str,
        action: str,
        scope: List[str],
        run_id: Optional[str] = None,
        ttl_seconds: int = 3600,
        package_id: Optional[str] = None,
    ) -> str:
        """Issues bounded approval request token.

        Raises:
            HardDenyViolation: If requested action is hard denied.
        """
        # Hard deny invariant: Cannot issue requests for hard denied actions
        norm_action = normalize_action(action)
        if norm_action in HARD_DENIED_ACTIONS:
            raise HardDenyViolation(
                action=action,
                reason=f"Cannot create approval request: action '{action}' is strictly hard-denied.",
            )

        now = datetime.now(timezone.utc)
        expires_at = now.timestamp() + ttl_seconds
        expires_dt = datetime.fromtimestamp(expires_at, tz=timezone.utc)

        request_id = f"REQ-{now.strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

        self._requests[request_id] = {
            "request_id": request_id,
            "job_id": job_id,
            "run_id": run_id,
            "package_id": package_id,
            "action": action,
            "scope": list(scope),
            "created_at": format_iso_datetime(now),
            "expires_at": format_iso_datetime(expires_dt),
            "status": "PENDING",
        }

        return request_id

    def record_decision(
        self,
        request_id: str,
        decision: str,
        approver: Approver,
        notes: Optional[str] = None,
        prohibited_actions: Optional[List[str]] = None,
        next_safe_action: Optional[str] = None,
    ) -> ApprovalToken:
        """Records sovereign human decision and creates bounded approval token.

        Raises:
            KeyError: If request_id is unknown.
            HardDenyViolation: If action is hard denied.
            ContractValidationError: If approval fields fail invariants.
        """
        req = self._requests.get(request_id)
        if not req:
            raise KeyError(f"Approval request '{request_id}' not found.")

        # Hard deny invariant check
        norm_action = normalize_action(req["action"])
        if norm_action in HARD_DENIED_ACTIONS:
            raise HardDenyViolation(
                action=req["action"],
                reason="Hard local policy denies cannot be approved.",
            )

        approved_at = format_iso_datetime()
        approver_record = Approver(
            identity=approver.identity,
            channel=approver.channel,
            approved_at=approver.approved_at or approved_at,
        )

        token = ApprovalToken(
            request_id=request_id,
            job_id=req["job_id"],
            action=req["action"],
            scope=req["scope"],
            expires_at=req["expires_at"],
            decision=decision,
            approver=approver_record,
            schema="solidbit.approval.v1",
            run_id=req.get("run_id"),
            package_id=req.get("package_id"),
            resume_run=True,
            cannot_override_hard_deny=True,
            created_at=req["created_at"],
            prohibited_actions=list(prohibited_actions or []),
            remaining_blockers=[],
            next_safe_action=next_safe_action,
            notes=notes,
        )

        # Validate against schema and invariants
        self.validator.validate_schema(token)
        req["status"] = decision
        self._tokens[request_id] = token
        return token

    def get_approval(self, request_id: str) -> Optional[ApprovalToken]:
        """Retrieves approval token by request_id."""
        return self._tokens.get(request_id)

    def get_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves pending or decided approval request metadata."""
        return self._requests.get(request_id)

"""SACL V1 Bounded Approval Manager.

Implements IApprovalManager interface:
- Issues bounded approval requests bound to (job_id, action, scope, request_id, expires_at).
- Enforces hard deny supremacy (cannot request or approve hard-denied actions).
- Persists to SQLite approvals table (Domain 10).
- Updates job and run states to WAITING_APPROVAL.
- Emits audit trail events.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional, Union
import uuid

from sacl.approval.models import (
    ApprovalDecisionOutcome,
    ApprovalRequest,
    ApprovalToken,
    Approver,
    utc_now_iso,
)
from sacl.approval.validator import (
    BoundedApprovalValidator,
    format_iso_datetime,
    parse_iso_datetime,
    token_to_schema_dict,
)
from sacl.contracts.exceptions import (
    ApprovalExpiredError,
    ContractValidationError,
    HardDenyViolation,
    PolicyDeniedError,
)
from sacl.contracts.interfaces import IApprovalManager
from sacl.contracts.invariants import (
    APPROVAL_CHANNELS_V1,
    ApprovalChannel,
    ApprovalDecision,
    ApprovalStatus,
    HARD_DENIED_ACTIONS,
    JobSideStatus,
)
from sacl.contracts.schema_validator import SchemaValidator
from sacl.observability.audit import AuditEventEmitter
from sacl.observability.events import (
    APPROVAL_REQUESTED,
    AuditEventType,
    Severity,
    create_audit_event,
)
from sacl.policy.hard_policy import normalize_action

logger = logging.getLogger("sacl.approval.manager")


class BoundedApprovalManager(IApprovalManager):
    """Manages the full lifecycle of bounded human approval requests and decision grants."""

    def __init__(
        self,
        db_conn: Optional[sqlite3.Connection] = None,
        validator: Optional[BoundedApprovalValidator] = None,
        audit_emitter: Optional[AuditEventEmitter] = None,
    ) -> None:
        self.db_conn = db_conn
        self.validator = validator or BoundedApprovalValidator()
        self.audit_emitter = audit_emitter
        self._requests: Dict[str, ApprovalRequest] = {}
        self._tokens: Dict[str, ApprovalToken] = {}

    def create_approval_request(
        self,
        job_id: str,
        action: str,
        scope: List[str],
        run_id: Optional[str] = None,
        ttl_seconds: int = 3600,
        package_id: Optional[str] = None,
        reason: Optional[str] = None,
        prohibited_actions: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Issues bounded approval request token.

        Raises:
            HardDenyViolation: If requested action is hard denied.
        """
        # Hard deny invariant: Cannot issue approval request for constitutional hard denies
        norm_action = normalize_action(action)
        if norm_action in HARD_DENIED_ACTIONS:
            raise HardDenyViolation(
                action=action,
                reason=(
                    f"Cannot create approval request: action '{action}' is strictly hard-denied. "
                    f"Hard deny unconditionally wins and cannot be approved."
                ),
            )

        now = datetime.now(timezone.utc)
        expires_at_dt = datetime.fromtimestamp(now.timestamp() + ttl_seconds, tz=timezone.utc)
        expires_at = format_iso_datetime(expires_at_dt)
        created_at = format_iso_datetime(now)

        request_id = f"REQ-{now.strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

        req = ApprovalRequest(
            request_id=request_id,
            job_id=job_id,
            action=action,
            scope=list(scope),
            expires_at=expires_at,
            run_id=run_id,
            package_id=package_id,
            status=ApprovalStatus.PENDING.value,
            created_at=created_at,
            reason=reason,
            prohibited_actions=list(prohibited_actions or []),
            metadata=dict(metadata or {}),
        )

        # Store in memory
        self._requests[request_id] = req

        # Persist to SQLite operational store if connection available
        if self.db_conn:
            cursor = self.db_conn.cursor()
            appr_id = f"appr-{uuid.uuid4().hex[:12]}"
            scope_json = json.dumps(req.scope)

            cursor.execute(
                """
                INSERT INTO approvals (
                    approval_id, request_id, job_id, run_id, action, scope,
                    status, decision, approver, rationale, signature,
                    requested_at, decided_at, expires_at
                ) VALUES (?, ?, ?, ?, ?, ?, 'PENDING', 'PENDING', NULL, ?, NULL, ?, NULL, ?)
                """,
                (
                    appr_id,
                    request_id,
                    job_id,
                    run_id,
                    action,
                    scope_json,
                    reason,
                    created_at,
                    expires_at,
                ),
            )

            # Update job lifecycle status to WAITING_APPROVAL
            cursor.execute(
                "UPDATE jobs SET status = ?, updated_at = ? WHERE job_id = ?",
                (JobSideStatus.WAITING_APPROVAL.value, created_at, job_id),
            )

            # Update run lifecycle status if run_id provided
            if run_id:
                cursor.execute(
                    "UPDATE runs SET status = ? WHERE run_id = ?",
                    (JobSideStatus.WAITING_APPROVAL.value, run_id),
                )

            self.db_conn.commit()

        # Emit audit event if emitter configured
        if self.audit_emitter:
            self.audit_emitter.emit(
                event_type=APPROVAL_REQUESTED,
                severity=Severity.INFO,
                job_id=job_id,
                run_id=run_id,
                payload={
                    "request_id": request_id,
                    "action": action,
                    "scope": req.scope,
                    "expires_at": expires_at,
                    "reason": reason,
                },
            )

        logger.info(
            "Created bounded approval request %s for job %s action %s (expires %s)",
            request_id,
            job_id,
            action,
            expires_at,
        )
        return request_id

    def record_decision(
        self,
        request_id: str,
        decision: str,
        approver: Approver,
        notes: Optional[str] = None,
        prohibited_actions: Optional[List[str]] = None,
        next_safe_action: Optional[str] = None,
        signature: Optional[str] = None,
        reference_time: Optional[datetime] = None,
    ) -> ApprovalToken:
        """Records sovereign human decision and creates bounded approval token.

        Raises:
            KeyError: If request_id is not found.
            ApprovalExpiredError: If request has expired.
            HardDenyViolation: If action is hard denied.
            ContractValidationError: If approval invariants or schema fail.
        """
        req = self.get_request(request_id)
        if not req:
            raise KeyError(f"Approval request '{request_id}' not found.")

        now = reference_time or datetime.now(timezone.utc)
        expires_dt = parse_iso_datetime(req.expires_at)
        now_iso = format_iso_datetime(now)

        # Expiration check (Fail-closed)
        if now > expires_dt:
            if self.db_conn:
                cursor = self.db_conn.cursor()
                cursor.execute(
                    "UPDATE approvals SET status = 'EXPIRED' WHERE request_id = ?",
                    (request_id,),
                )
                self.db_conn.commit()
            req.status = ApprovalStatus.EXPIRED.value
            raise ApprovalExpiredError(
                request_id=request_id,
                expires_at=req.expires_at,
            )

        # Normalize decision
        norm_decision = decision.upper().strip()
        if norm_decision not in {
            ApprovalDecision.APPROVED.value,
            ApprovalDecision.REJECTED.value,
            ApprovalDecision.DEFERRED.value,
        }:
            raise ContractValidationError(
                schema_name="approval",
                message=f"Invalid approval decision '{decision}'. Must be APPROVED, REJECTED, or DEFERRED.",
            )

        # Hard deny invariant check
        norm_action = normalize_action(req.action)
        if norm_action in HARD_DENIED_ACTIONS and norm_decision == ApprovalDecision.APPROVED.value:
            raise HardDenyViolation(
                action=req.action,
                reason=(
                    f"Constitutional Invariant Violation: Attempted to approve hard-denied action "
                    f"'{req.action}'. Hard deny unconditionally wins."
                ),
            )

        # Validate channel
        if approver.channel not in APPROVAL_CHANNELS_V1:
            raise ContractValidationError(
                schema_name="approval",
                message=(
                    f"Disallowed approver channel '{approver.channel}'. "
                    f"Only {sorted(list(APPROVAL_CHANNELS_V1))} are permitted in V1."
                ),
            )

        approver_record = Approver(
            identity=approver.identity,
            channel=approver.channel,
            approved_at=approver.approved_at or now_iso,
        )

        all_prohibited = list(set(req.prohibited_actions + list(prohibited_actions or [])))

        token = ApprovalToken(
            request_id=request_id,
            job_id=req.job_id,
            action=req.action,
            scope=req.scope,
            expires_at=req.expires_at,
            decision=norm_decision,
            approver=approver_record,
            schema="solidbit.approval.v1",
            run_id=req.run_id,
            package_id=req.package_id,
            resume_run=True,
            cannot_override_hard_deny=True,
            created_at=req.created_at,
            prohibited_actions=all_prohibited,
            remaining_blockers=[],
            next_safe_action=next_safe_action or ("RESUME_RUN_EXECUTION" if norm_decision == "APPROVED" else "REMEDIATE_BLOCKER"),
            notes=notes,
        )

        # Validate token against JSON schema and invariants
        self.validator.validate_schema(token)
        if norm_decision == ApprovalDecision.APPROVED.value:
            self.validator.validate_invariants(token, reference_time=now)

        # Update in-memory state
        req.status = norm_decision
        self._tokens[request_id] = token

        # Persist decision to SQLite operational store if available
        if self.db_conn:
            cursor = self.db_conn.cursor()
            approver_json = json.dumps(approver_record.to_dict())

            cursor.execute(
                """
                UPDATE approvals
                SET status = ?,
                    decision = ?,
                    approver = ?,
                    rationale = COALESCE(?, rationale),
                    signature = COALESCE(?, signature),
                    decided_at = ?
                WHERE request_id = ?
                """,
                (
                    norm_decision,
                    norm_decision,
                    approver_json,
                    notes,
                    signature,
                    now_iso,
                    request_id,
                ),
            )
            self.db_conn.commit()

        # Emit audit event
        if self.audit_emitter:
            event_type = (
                AuditEventType.APPROVAL_GRANTED.value
                if norm_decision == ApprovalDecision.APPROVED.value
                else AuditEventType.APPROVAL_REJECTED.value
            )
            self.audit_emitter.emit(
                event_type=event_type,
                severity=Severity.INFO if norm_decision == "APPROVED" else Severity.WARN,
                job_id=req.job_id,
                run_id=req.run_id,
                payload={
                    "request_id": request_id,
                    "decision": norm_decision,
                    "approver": approver_record.to_dict(),
                    "action": req.action,
                    "scope": req.scope,
                    "notes": notes,
                },
            )

        logger.info(
            "Recorded decision %s for approval request %s by %s via %s",
            norm_decision,
            request_id,
            approver.identity,
            approver.channel,
        )
        return token

    def get_approval(self, request_id: str) -> Optional[ApprovalToken]:
        """Retrieves approval token by request token."""
        if request_id in self._tokens:
            return self._tokens[request_id]

        if self.db_conn:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT * FROM approvals WHERE request_id = ?", (request_id,))
            row = cursor.fetchone()
            if row:
                col_names = [d[0] for d in cursor.description]
                row_dict = dict(zip(col_names, row))
                if row_dict.get("status") in ("APPROVED", "REJECTED", "DEFERRED") and row_dict.get("approver"):
                    try:
                        approver_raw = row_dict["approver"]
                        if isinstance(approver_raw, str):
                            try:
                                approver_data = json.loads(approver_raw)
                            except Exception:
                                approver_data = {"identity": approver_raw, "channel": "CLI"}
                        else:
                            approver_data = {"identity": "Joaquín", "channel": "CLI"}

                        approver = Approver.from_dict(approver_data)
                        scope_raw = row_dict["scope"]
                        scope = json.loads(scope_raw) if isinstance(scope_raw, str) else list(scope_raw)

                        token = ApprovalToken(
                            request_id=row_dict["request_id"],
                            job_id=row_dict["job_id"],
                            action=row_dict["action"],
                            scope=scope,
                            expires_at=row_dict["expires_at"],
                            decision=row_dict["decision"],
                            approver=approver,
                            run_id=row_dict.get("run_id"),
                            resume_run=True,
                            cannot_override_hard_deny=True,
                            created_at=row_dict.get("requested_at"),
                            notes=row_dict.get("rationale"),
                        )
                        self._tokens[request_id] = token
                        return token
                    except Exception as e:
                        logger.warning("Error deserializing approval token from DB: %s", e)
        return None

    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        """Retrieves pending or decided approval request metadata."""
        if self.db_conn:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT * FROM approvals WHERE request_id = ?", (request_id,))
            row = cursor.fetchone()
            if row:
                col_names = [d[0] for d in cursor.description]
                row_dict = dict(zip(col_names, row))
                scope_raw = row_dict["scope"]
                scope = json.loads(scope_raw) if isinstance(scope_raw, str) else list(scope_raw)
                req = ApprovalRequest(
                    request_id=row_dict["request_id"],
                    job_id=row_dict["job_id"],
                    action=row_dict["action"],
                    scope=scope,
                    expires_at=row_dict["expires_at"],
                    run_id=row_dict.get("run_id"),
                    status=row_dict["status"],
                    created_at=row_dict.get("requested_at", utc_now_iso()),
                    reason=row_dict.get("rationale"),
                )
                self._requests[request_id] = req
                return req

        return self._requests.get(request_id)

    def list_pending_requests(self, job_id: Optional[str] = None) -> List[ApprovalRequest]:
        """Lists active pending approval requests."""
        results = []
        if self.db_conn:
            cursor = self.db_conn.cursor()
            if job_id:
                cursor.execute(
                    "SELECT * FROM approvals WHERE status = 'PENDING' AND job_id = ? ORDER BY requested_at ASC",
                    (job_id,),
                )
            else:
                cursor.execute(
                    "SELECT * FROM approvals WHERE status = 'PENDING' ORDER BY requested_at ASC"
                )
            rows = cursor.fetchall()
            col_names = [d[0] for d in cursor.description]
            for row in rows:
                row_dict = dict(zip(col_names, row))
                scope_raw = row_dict["scope"]
                scope = json.loads(scope_raw) if isinstance(scope_raw, str) else list(scope_raw)
                results.append(
                    ApprovalRequest(
                        request_id=row_dict["request_id"],
                        job_id=row_dict["job_id"],
                        action=row_dict["action"],
                        scope=scope,
                        expires_at=row_dict["expires_at"],
                        run_id=row_dict.get("run_id"),
                        status=row_dict["status"],
                        created_at=row_dict.get("requested_at", utc_now_iso()),
                        reason=row_dict.get("rationale"),
                    )
                )
            return results

        # In-memory fallback
        for req in self._requests.values():
            if req.status == ApprovalStatus.PENDING.value:
                if job_id is None or req.job_id == job_id:
                    results.append(req)
        return results

    def check_and_expire_requests(self, reference_time: Optional[datetime] = None) -> int:
        """Evaluates pending requests and marks any expired ones as EXPIRED.

        Returns count of expired requests.
        """
        now = reference_time or datetime.now(timezone.utc)
        expired_count = 0

        pending = self.list_pending_requests()
        for req in pending:
            expires_dt = parse_iso_datetime(req.expires_at)
            if now > expires_dt:
                req.status = ApprovalStatus.EXPIRED.value
                if req.request_id in self._requests:
                    self._requests[req.request_id].status = ApprovalStatus.EXPIRED.value
                expired_count += 1
                if self.db_conn:
                    cursor = self.db_conn.cursor()
                    cursor.execute(
                        "UPDATE approvals SET status = 'EXPIRED' WHERE request_id = ?",
                        (req.request_id,),
                    )
                logger.info("Approval request %s expired fail-closed", req.request_id)

        if self.db_conn and expired_count > 0:
            self.db_conn.commit()

        return expired_count


__all__ = ["BoundedApprovalManager"]

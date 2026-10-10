"""SACL V1 Approval Repository.

Domain 10: Bounded human action-approval contract
Binding: JOB_ID + ACTION + SCOPE + REQUEST_ID + expires_at
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from typing import Any, Dict, List, Optional, Union

from sacl.contracts.invariants import ApprovalChannel, ApprovalDecision, ApprovalStatus
from sacl.contracts.models import ApprovalToken, Approver
from sacl.contracts.exceptions import ApprovalExpiredError
from sacl.state.exceptions import EntityNotFoundError
from sacl.state.repositories.base import BaseRepository
from sacl.state.utils import json_dumps_safe, json_loads_safe, utc_now


class ApprovalRepository(BaseRepository):
    """Repository managing Domain 10 'approvals' table."""

    def create_approval_request(
        self,
        job_id: str,
        action: str,
        scope: List[str],
        expires_at: str,
        request_id: Optional[str] = None,
        approval_id: Optional[str] = None,
        run_id: Optional[str] = None,
        requested_at: Optional[str] = None,
    ) -> str:
        """Issues bounded approval request token and records it in pending status."""
        req_id = request_id or f"req-{uuid.uuid4().hex[:12]}"
        appr_id = approval_id or f"appr-{uuid.uuid4().hex[:12]}"
        now = requested_at or utc_now()
        scope_str = json_dumps_safe(scope) or "[]"

        sql = """
            INSERT INTO approvals (
                approval_id, request_id, job_id, run_id, action, scope,
                status, decision, approver, rationale, signature,
                requested_at, decided_at, expires_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'PENDING', 'PENDING', NULL, NULL, NULL, ?, NULL, ?);
        """
        self.execute(sql, (appr_id, req_id, job_id, run_id, action, scope_str, now, expires_at))
        self.commit()
        return req_id

    def record_decision(
        self,
        request_id: str,
        decision: str,
        approver: Union[Approver, Dict[str, Any]],
        rationale: Optional[str] = None,
        signature: Optional[str] = None,
        decided_at: Optional[str] = None,
    ) -> ApprovalToken:
        """Records human decision and updates approval record."""
        if decision not in (ApprovalDecision.APPROVED.value, ApprovalDecision.REJECTED.value):
            raise ValueError(f"Decision must be APPROVED or REJECTED, got '{decision}'")

        existing = self.fetchone_dict("SELECT * FROM approvals WHERE request_id = ?;", (request_id,))
        if not existing:
            raise EntityNotFoundError(f"Approval request '{request_id}' not found")

        now = decided_at or utc_now()
        if existing["expires_at"] < now:
            self.execute("UPDATE approvals SET status = 'EXPIRED' WHERE request_id = ?;", (request_id,))
            self.commit()
            raise ApprovalExpiredError(request_id, existing["expires_at"])

        status = decision  # APPROVED or REJECTED

        if isinstance(approver, Approver):
            approver_model = approver
        else:
            approver_model = Approver.from_dict(approver)

        approver_json = json_dumps_safe(approver_model.to_dict())

        sql = """
            UPDATE approvals
            SET status = ?,
                decision = ?,
                approver = ?,
                rationale = COALESCE(?, rationale),
                signature = COALESCE(?, signature),
                decided_at = ?
            WHERE request_id = ?;
        """
        self.execute(sql, (status, decision, approver_json, rationale, signature, now, request_id))
        self.commit()

        token = self.get_approval(request_id)
        if not token:
            raise EntityNotFoundError(f"Failed to reload approval token '{request_id}'")
        return token

    def get_approval(self, request_id: str) -> Optional[ApprovalToken]:
        """Retrieves strongly-typed ApprovalToken by request token."""
        sql = "SELECT * FROM approvals WHERE request_id = ?;"
        row = self.fetchone_dict(sql, (request_id,))
        return self._row_to_token(row) if row else None

    def get_approval_by_id(self, approval_id: str) -> Optional[ApprovalToken]:
        """Retrieves strongly-typed ApprovalToken by approval ID."""
        sql = "SELECT * FROM approvals WHERE approval_id = ?;"
        row = self.fetchone_dict(sql, (approval_id,))
        return self._row_to_token(row) if row else None

    def expire_stale_approvals(self, current_time: Optional[str] = None) -> int:
        """Transitions PENDING approvals with expires_at in the past to EXPIRED."""
        now = current_time or utc_now()
        sql = """
            UPDATE approvals
            SET status = 'EXPIRED'
            WHERE status = 'PENDING' AND expires_at < ?;
        """
        cursor = self.execute(sql, (now,))
        self.commit()
        return cursor.rowcount

    def check_approval_valid(self, request_id: str, action: str, job_id: str) -> bool:
        """Validates that a request token matches action, job, and is unexpired."""
        token = self.get_approval(request_id)
        if not token:
            return False
        if token.decision != ApprovalDecision.APPROVED.value:
            return False
        if token.action != action or token.job_id != job_id:
            return False
        if token.expires_at < utc_now():
            return False
        return True

    @staticmethod
    def _row_to_token(row: Dict[str, Any]) -> ApprovalToken:
        """Maps relational approval row to strongly-typed ApprovalToken."""
        raw_scope = row.get("scope", "[]")
        scope_list = json_loads_safe(raw_scope) or [raw_scope]

        approver_data = json_loads_safe(row.get("approver")) or {}
        if isinstance(approver_data, dict) and "identity" in approver_data:
            approver = Approver.from_dict(approver_data)
        else:
            identity = row.get("approver") or "UNKNOWN"
            approver = Approver(identity=identity, channel=ApprovalChannel.CLI.value)

        token = ApprovalToken(
            request_id=row["request_id"],
            job_id=row["job_id"],
            action=row["action"],
            scope=scope_list,
            expires_at=row["expires_at"],
            decision=row["decision"],
            approver=approver,
            run_id=row.get("run_id"),
            created_at=row.get("requested_at"),
            notes=row.get("rationale"),
        )
        return token

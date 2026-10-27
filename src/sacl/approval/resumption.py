"""SACL V1 Same-Run Resumption Engine.

Constitutional Invariant (SB-FREEZE-P1-06, ADR-007):
Approvals resume the SAME logical run; they do NOT spawn disconnected or unlinked orphan runs.
resume_run must strictly evaluate to True.
When an approval grant is attested, the waiting job and run transition back to RUNNING
under the identical run_id.
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone
from typing import Optional

from sacl.approval.models import ApprovalToken, ResumptionContext
from sacl.approval.validator import BoundedApprovalValidator, format_iso_datetime
from sacl.contracts.exceptions import (
    HardDenyViolation,
    PolicyDeniedError,
)
from sacl.contracts.invariants import (
    ApprovalDecision,
    JobSideStatus,
)
from sacl.observability.audit import AuditEventEmitter
from sacl.observability.events import (
    Severity,
)

logger = logging.getLogger("sacl.approval.resumption")


class SameRunResumptionManager:
    """Coordinates same-run resumption following bounded approval decision."""

    def __init__(
        self,
        db_conn: Optional[sqlite3.Connection] = None,
        validator: Optional[BoundedApprovalValidator] = None,
        audit_emitter: Optional[AuditEventEmitter] = None,
    ) -> None:
        self.db_conn = db_conn
        self.validator = validator or BoundedApprovalValidator()
        self.audit_emitter = audit_emitter

    def resume_run(
        self,
        token: ApprovalToken,
        target_status: str = "RUNNING",
        reference_time: Optional[datetime] = None,
    ) -> ResumptionContext:
        """Executes same-run resumption using an attested bounded approval token.

        Raises:
            HardDenyViolation: If token authorizes a hard denial.
            ApprovalExpiredError: If token has expired.
            PolicyDeniedError: If token is not APPROVED or invariants fail.
        """
        now = reference_time or datetime.now(timezone.utc)
        now_iso = format_iso_datetime(now)

        # Constitutional Invariant 1: resume_run must be True
        if not token.resume_run:
            raise PolicyDeniedError(
                action=token.action,
                layer="APPROVAL_RESUMPTION",
                reason=(
                    f"Same-Run Resumption Invariant Violation: token '{token.request_id}' has "
                    f"resume_run=False. Approvals must resume the same logical run."
                ),
            )

        # Constitutional Invariant 2: cannot_override_hard_deny must be True
        if not token.cannot_override_hard_deny:
            raise HardDenyViolation(
                action=token.action,
                reason="Constitutional Invariant: cannot_override_hard_deny must strictly be true.",
            )

        # Validate token against all invariants and schema
        if token.decision == ApprovalDecision.APPROVED.value:
            self.validator.validate_invariants(token, reference_time=now)
        elif token.decision == ApprovalDecision.REJECTED.value:
            # Handle rejection fail-closed
            return self._handle_rejection(token, now_iso)
        elif token.decision == ApprovalDecision.DEFERRED.value:
            # Handle deferral
            return self._handle_deferral(token, now_iso)
        else:
            raise PolicyDeniedError(
                action=token.action,
                layer="APPROVAL_RESUMPTION",
                reason=f"Unknown decision '{token.decision}'.",
            )

        # Determine target run_id
        run_id = token.run_id
        job_id = token.job_id

        # If DB connection present, verify and update state
        if self.db_conn:
            cursor = self.db_conn.cursor()

            # If run_id not explicitly set on token, find current run for job_id
            if not run_id:
                cursor.execute(
                    "SELECT current_run_id FROM jobs WHERE job_id = ?",
                    (job_id,),
                )
                row = cursor.fetchone()
                if row and row[0]:
                    run_id = row[0]
                else:
                    cursor.execute(
                        "SELECT run_id FROM runs WHERE job_id = ? ORDER BY started_at DESC LIMIT 1",
                        (job_id,),
                    )
                    r_row = cursor.fetchone()
                    if r_row:
                        run_id = r_row[0]

            if not run_id:
                raise PolicyDeniedError(
                    action=token.action,
                    layer="APPROVAL_RESUMPTION",
                    reason=f"No run found for job '{job_id}' to resume.",
                )

            # Update runs table to target_status (RUNNING)
            cursor.execute(
                "UPDATE runs SET status = ? WHERE run_id = ?",
                (target_status, run_id),
            )

            # Update jobs table to target_status (RUNNING)
            cursor.execute(
                "UPDATE jobs SET status = ?, updated_at = ? WHERE job_id = ?",
                (target_status, now_iso, job_id),
            )

            # If any agents in the run were in WAITING_APPROVAL, unpause them to READY
            cursor.execute(
                """
                UPDATE agents
                SET status = 'READY', updated_at = ?
                WHERE run_id = ? AND status = 'WAITING_APPROVAL'
                """,
                (now_iso, run_id),
            )

            self.db_conn.commit()
        else:
            run_id = run_id or f"run-{job_id}"

        # Emit audit event
        if self.audit_emitter:
            self.audit_emitter.emit(
                event_type="RUN_RESUMED",
                severity=Severity.INFO,
                job_id=job_id,
                run_id=run_id,
                payload={
                    "request_id": token.request_id,
                    "action": token.action,
                    "scope": token.scope,
                    "approver": token.approver.to_dict(),
                    "resumed_status": target_status,
                },
            )

        logger.info(
            "Resumed same logical run %s (job %s) via approval %s to status %s",
            run_id,
            job_id,
            token.request_id,
            target_status,
        )

        return ResumptionContext(
            success=True,
            run_id=run_id,
            job_id=job_id,
            status=target_status,
            message=f"Same logical run '{run_id}' resumed to '{target_status}'.",
            resumed_at=now_iso,
            token=token,
        )

    def _handle_rejection(self, token: ApprovalToken, now_iso: str) -> ResumptionContext:
        """Transitions job and run to BLOCKED upon approval rejection."""
        run_id = token.run_id or f"run-{token.job_id}"
        job_id = token.job_id
        blocked_status = JobSideStatus.BLOCKED.value

        if self.db_conn:
            cursor = self.db_conn.cursor()
            if not token.run_id:
                cursor.execute("SELECT current_run_id FROM jobs WHERE job_id = ?", (job_id,))
                row = cursor.fetchone()
                if row and row[0]:
                    run_id = row[0]

            cursor.execute("UPDATE runs SET status = ? WHERE run_id = ?", (blocked_status, run_id))
            cursor.execute(
                "UPDATE jobs SET status = ?, updated_at = ? WHERE job_id = ?",
                (blocked_status, now_iso, job_id),
            )
            cursor.execute(
                "UPDATE agents SET status = 'BLOCKED', updated_at = ? WHERE run_id = ? AND status = 'WAITING_APPROVAL'",
                (now_iso, run_id),
            )
            self.db_conn.commit()

        if self.audit_emitter:
            self.audit_emitter.emit(
                event_type="RUN_BLOCKED",
                severity=Severity.WARN,
                job_id=job_id,
                run_id=run_id,
                payload={
                    "request_id": token.request_id,
                    "action": token.action,
                    "reason": "Human sovereign approver rejected authorization.",
                },
            )

        return ResumptionContext(
            success=False,
            run_id=run_id,
            job_id=job_id,
            status=blocked_status,
            message=f"Approval rejected for request '{token.request_id}'; run blocked fail-closed.",
            resumed_at=now_iso,
            token=token,
        )

    def _handle_deferral(self, token: ApprovalToken, now_iso: str) -> ResumptionContext:
        """Leaves job and run paused upon approval deferral."""
        run_id = token.run_id or f"run-{token.job_id}"
        job_id = token.job_id
        waiting_status = JobSideStatus.WAITING_APPROVAL.value

        return ResumptionContext(
            success=False,
            run_id=run_id,
            job_id=job_id,
            status=waiting_status,
            message=f"Approval deferred for request '{token.request_id}'; run remains paused.",
            resumed_at=now_iso,
            token=token,
        )


__all__ = ["SameRunResumptionManager"]

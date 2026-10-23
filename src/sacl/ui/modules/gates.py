"""Human Decision Gates UI Module.

Sovereign micro-decision engine, managing pending approvals,
decision grants, bounded token creation, and audit logging.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import sqlite3
from typing import Any, Callable, Dict, List, Optional

from sacl.approval.manager import BoundedApprovalManager
from sacl.approval.models import Approver
from sacl.ui.models import HumanGateCard

logger = logging.getLogger("sacl.ui.modules.gates")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class GatesModule:
    """Provides high-level micro-decision handling over BoundedApprovalManager."""

    def __init__(
        self,
        get_ro_conn: Callable[[], Optional[sqlite3.Connection]],
        get_rw_conn: Callable[[], sqlite3.Connection],
    ) -> None:
        self._get_ro_conn = get_ro_conn
        self._get_rw_conn = get_rw_conn

    def get_pending_gates(self) -> List[HumanGateCard]:
        """Fetches pending approval gates awaiting human micro-decisions."""
        conn = self._get_ro_conn()
        if not conn:
            return []

        gates: List[HumanGateCard] = []
        try:
            mgr = BoundedApprovalManager(db_conn=conn)
            pending_reqs = mgr.list_pending_requests()
            for req in pending_reqs:
                risk = "HIGH" if any(x in req.action for x in ("DEPLOY", "MERGE", "RULESET")) else "MEDIUM"
                scope_str = ", ".join(req.scope) if isinstance(req.scope, list) else str(req.scope)
                gates.append(
                    HumanGateCard(
                        approval_id=req.request_id,
                        request_id=req.request_id,
                        job_id=req.job_id,
                        run_id=req.run_id,
                        action=req.action,
                        scope=scope_str,
                        risk_level=risk,
                        status=req.status,
                        reason=req.reason or "Mandatory decision gate",
                        evidence_summary=f"Approval requested for action '{req.action}' targeting '{scope_str}'",
                        created_at=req.created_at,
                        expires_at=req.expires_at,
                        can_decide=True,
                    )
                )
        except Exception as exc:
            logger.debug(f"Failed to query approvals: {exc}")
        finally:
            conn.close()

        return gates

    def get_gate_history(self) -> List[Dict[str, Any]]:
        """Returns completed approval decisions from SQLite."""
        conn = self._get_ro_conn()
        if not conn:
            return []

        history: List[Dict[str, Any]] = []
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT approval_id, request_id, job_id, action, scope, status,
                       decision, approver, rationale, requested_at, decided_at
                FROM approvals
                WHERE status != 'PENDING'
                ORDER BY decided_at DESC
                LIMIT 50;
                """
            )
            for row in cur.fetchall():
                history.append(dict(row))
        except Exception as exc:
            logger.debug(f"Failed to query approval history: {exc}")
        finally:
            conn.close()

        return history

    def submit_decision(
        self,
        request_id: str,
        decision_str: str,
        approver_id: str = "human_operator",
        justification: str = "Authorized via SACL Decision Shell",
    ) -> Dict[str, Any]:
        """Records a sovereign human decision."""
        decision_val = "APPROVED" if decision_str.upper() == "APPROVED" else "REJECTED"
        approver = Approver(
            identity=approver_id,
            channel="CLI",
            approved_at=utc_now(),
        )

        rw_conn = self._get_rw_conn()
        try:
            mgr = BoundedApprovalManager(db_conn=rw_conn)
            token = mgr.record_decision(
                request_id=request_id,
                decision=decision_val,
                approver=approver,
                notes=justification,
            )
            return {
                "success": True,
                "status": decision_val,
                "token": token.request_id if token else None,
                "message": f"Gate decision recorded as {decision_val}",
                "timestamp": utc_now(),
            }
        except Exception as exc:
            logger.error(f"Error submitting gate decision: {exc}")
            return {
                "success": False,
                "status": "ERROR",
                "message": str(exc),
            }
        finally:
            rw_conn.close()

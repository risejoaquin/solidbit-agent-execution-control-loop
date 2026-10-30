"""SACL V1 Error Repository.

Domain 15: Structured operational error diagnostics repository.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from sacl.contracts.models import ErrorRecord
from sacl.state.repositories.base import BaseRepository
from sacl.state.utils import json_dumps_safe, json_loads_safe, utc_now

VALID_ERROR_CATEGORIES = frozenset(
    {
        "INFRASTRUCTURE",
        "POLICY",
        "VALIDATION",
        "EXECUTION",
        "TIMEOUT",
        "COLLISION",
        "TRANSPORT",
        "APPROVAL",
        "RECOVERY",
    }
)

VALID_ERROR_SEVERITIES = frozenset({"WARN", "ERROR", "FATAL"})


class ErrorRepository(BaseRepository):
    """Repository managing Domain 15 'errors' table."""

    def record_error(
        self,
        error_code: str,
        category: str,
        severity: str,
        message: str,
        job_id: Optional[str] = None,
        run_id: Optional[str] = None,
        node_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        stack_trace: Optional[str] = None,
        context: Optional[Union[Dict[str, Any], str]] = None,
        occurred_at: Optional[str] = None,
    ) -> int:
        """Records a structured operational error event."""
        if category not in VALID_ERROR_CATEGORIES:
            raise ValueError(f"Invalid error category: {category}")
        if severity not in VALID_ERROR_SEVERITIES:
            raise ValueError(f"Invalid error severity: {severity}")

        now = occurred_at or utc_now()
        ctx_json = json_dumps_safe(context) if isinstance(context, dict) else context

        sql = """
            INSERT INTO errors (
                job_id, run_id, node_id, agent_id, error_code,
                category, severity, message, stack_trace,
                context_json, occurred_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        cursor = self.execute(
            sql,
            (
                job_id,
                run_id,
                node_id,
                agent_id,
                error_code,
                category,
                severity,
                message,
                stack_trace,
                ctx_json,
                now,
            ),
        )
        self.commit()
        return cursor.lastrowid  # type: ignore[return-value]

    def record_error_model(self, model: ErrorRecord) -> int:
        """Records an ErrorRecord instance."""
        return self.record_error(
            error_code=model.error_code,
            category=model.category,
            severity=model.severity,
            message=model.message,
            job_id=model.job_id,
            run_id=model.run_id,
            node_id=model.node_id,
            agent_id=model.agent_id,
            stack_trace=model.stack_trace,
            context=model.context,
            occurred_at=model.occurred_at,
        )

    def list_errors(
        self,
        run_id: Optional[str] = None,
        job_id: Optional[str] = None,
        category: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Queries structured error records with optional filtering."""
        conditions = []
        params: List[Any] = []
        if run_id:
            conditions.append("run_id = ?")
            params.append(run_id)
        if job_id:
            conditions.append("job_id = ?")
            params.append(job_id)
        if category:
            conditions.append("category = ?")
            params.append(category)
        if severity:
            conditions.append("severity = ?")
            params.append(severity)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        sql = f"SELECT * FROM errors {where_clause} ORDER BY error_id ASC LIMIT ?;"  # nosec B608 - conditions are static strings
        params.append(limit)

        rows = self.fetchall_dict(sql, params)
        for r in rows:
            r["context"] = json_loads_safe(r.get("context_json"))
        return rows

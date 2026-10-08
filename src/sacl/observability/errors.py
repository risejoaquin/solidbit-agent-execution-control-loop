"""SACL V1 Structured Diagnostic Error Recording Subsystem.

Manages recording and forensic querying of errors across the operational
errors domain in sacl_ops.db.
"""

from __future__ import annotations

import json
import sqlite3
import traceback
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, FrozenSet, List, Optional, Union

from sacl.contracts.models import ErrorRecord
from sacl.observability.correlation import get_current_correlation
from sacl.observability.events import ERROR_RECORDED


class ErrorCategory(str, Enum):
    """Canonical error categories constrained by 001_init.sql."""

    INFRASTRUCTURE = "INFRASTRUCTURE"
    POLICY = "POLICY"
    VALIDATION = "VALIDATION"
    EXECUTION = "EXECUTION"
    TIMEOUT = "TIMEOUT"
    COLLISION = "COLLISION"
    TRANSPORT = "TRANSPORT"
    APPROVAL = "APPROVAL"
    RECOVERY = "RECOVERY"


ALL_ERROR_CATEGORIES: FrozenSet[str] = frozenset(c.value for c in ErrorCategory)
ALL_ERROR_SEVERITIES: FrozenSet[str] = frozenset({"WARN", "ERROR", "FATAL"})


class ErrorRecorder:
    """Records and queries structured diagnostic errors in SQLite errors table."""

    def __init__(
        self,
        db_source: Union[sqlite3.Connection, Path, str, Callable[[], sqlite3.Connection]],
        audit_emitter: Optional[Any] = None,
    ):
        self._db_source = db_source
        self.audit_emitter = audit_emitter

    def _get_connection(self) -> sqlite3.Connection:
        if isinstance(self._db_source, sqlite3.Connection):
            return self._db_source
        elif callable(self._db_source):
            return self._db_source()
        else:
            conn = sqlite3.connect(str(self._db_source))
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("PRAGMA busy_timeout = 5000;")
            return conn

    def record_error(
        self,
        error_code: str,
        category: str,
        message: str,
        severity: str = "ERROR",
        stack_trace: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        job_id: Optional[str] = None,
        run_id: Optional[str] = None,
        node_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        exception: Optional[BaseException] = None,
    ) -> int:
        """Records a structured error into SQLite errors table and emits an audit event."""
        cat = category.upper()
        if cat not in ALL_ERROR_CATEGORIES:
            raise ValueError(f"Invalid category '{category}'; must be one of {sorted(ALL_ERROR_CATEGORIES)}")

        sev = severity.upper()
        if sev not in ALL_ERROR_SEVERITIES:
            raise ValueError(f"Invalid severity '{severity}'; must be one of {sorted(ALL_ERROR_SEVERITIES)}")

        corr = get_current_correlation()
        active_job = job_id or corr.job_id
        active_run = run_id or corr.run_id
        active_node = node_id or corr.node_id
        active_agent = agent_id or corr.agent_id

        if exception and not stack_trace:
            stack_trace = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))

        context_json = json.dumps(context or {})
        occurred_at = datetime.now(timezone.utc).isoformat()

        conn = self._get_connection()
        should_close = not isinstance(self._db_source, sqlite3.Connection) and not callable(self._db_source)

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO errors (job_id, run_id, node_id, agent_id, error_code, category, severity, message, stack_trace, context_json, occurred_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    active_job,
                    active_run,
                    active_node,
                    active_agent,
                    error_code,
                    cat,
                    sev,
                    message,
                    stack_trace,
                    context_json,
                    occurred_at,
                ),
            )
            error_id = cursor.lastrowid or 0
            conn.commit()

            # Forward to audit emitter if available
            if self.audit_emitter:
                try:
                    payload = {
                        "error_id": error_id,
                        "error_code": error_code,
                        "category": cat,
                        "message": message,
                        "context": context or {},
                    }
                    self.audit_emitter.emit(
                        event_type=ERROR_RECORDED,
                        severity=sev,
                        payload=payload,
                        job_id=active_job,
                        run_id=active_run,
                        node_id=active_node,
                        agent_id=active_agent,
                    )
                except Exception:
                    pass

            return error_id
        finally:
            if should_close:
                conn.close()

    def get_errors_for_run(self, run_id: str) -> List[ErrorRecord]:
        """Retrieves all errors recorded for a specific execution run."""
        conn = self._get_connection()
        should_close = not isinstance(self._db_source, sqlite3.Connection) and not callable(self._db_source)

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT error_id, job_id, run_id, node_id, agent_id, error_code, category, severity, message, stack_trace, context_json, occurred_at
                FROM errors WHERE run_id = ? ORDER BY error_id ASC
                """,
                (run_id,),
            )
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]
        finally:
            if should_close:
                conn.close()

    def get_recent_errors(self, limit: int = 20) -> List[ErrorRecord]:
        """Retrieves the most recent diagnostic errors across all runs."""
        conn = self._get_connection()
        should_close = not isinstance(self._db_source, sqlite3.Connection) and not callable(self._db_source)

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT error_id, job_id, run_id, node_id, agent_id, error_code, category, severity, message, stack_trace, context_json, occurred_at
                FROM errors ORDER BY error_id DESC LIMIT ?
                """,
                (limit,),
            )
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]
        finally:
            if should_close:
                conn.close()

    @staticmethod
    def _row_to_model(row: sqlite3.Row) -> ErrorRecord:
        try:
            ctx = json.loads(row["context_json"] or "{}")
        except Exception:
            ctx = {}
        return ErrorRecord(
            error_id=row["error_id"],
            job_id=row["job_id"],
            run_id=row["run_id"],
            node_id=row["node_id"],
            agent_id=row["agent_id"],
            error_code=row["error_code"],
            category=row["category"],
            severity=row["severity"],
            message=row["message"],
            stack_trace=row["stack_trace"],
            context=ctx,
            occurred_at=row["occurred_at"],
        )

"""SACL V1 Append-Only Audit Event Emission Subsystem.

Enforces immutable audit logging across SQLite events and audit_events tables.
Inviolable Invariant: Append-Only Immutable Auditing (Worker processes cannot
update, delete, or purge historical audit records).
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from sacl.contracts.models import AuditEvent
from sacl.observability.correlation import get_current_correlation
from sacl.observability.events import ALL_SEVERITIES, Severity, create_audit_event


class AuditEventEmitter:
    """Emits and queries append-only audit events in the operational state store.

    Enforces the Append-Only Immutable Auditing Invariant: provides only INSERT
    operations and strictly read-only query interfaces.
    """

    def __init__(
        self,
        db_source: Union[sqlite3.Connection, Path, str, Callable[[], sqlite3.Connection]],
    ):
        self._db_source = db_source
        self._db_file: Optional[str] = None
        if isinstance(db_source, sqlite3.Connection):
            try:
                for r in db_source.execute("PRAGMA database_list;").fetchall():
                    if r[1] == "main" and r[2] and r[2] != ":memory:":
                        self._db_file = r[2]
                        break
            except Exception:
                pass

    def _get_connection(self) -> tuple[sqlite3.Connection, bool]:
        if isinstance(self._db_source, sqlite3.Connection):
            try:
                self._db_source.execute("SELECT 1;")
                return self._db_source, False
            except sqlite3.ProgrammingError:
                if self._db_file:
                    conn = sqlite3.connect(self._db_file)
                    conn.row_factory = sqlite3.Row
                    conn.execute("PRAGMA foreign_keys = ON;")
                    conn.execute("PRAGMA busy_timeout = 5000;")
                    return conn, True
                raise
        elif callable(self._db_source):
            return self._db_source(), False
        else:
            conn = sqlite3.connect(str(self._db_source))
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("PRAGMA busy_timeout = 5000;")
            return conn, True

    def emit(
        self,
        event_or_type: Optional[Union[AuditEvent, str]] = None,
        severity: str = Severity.INFO.value,
        payload: Optional[Dict[str, Any]] = None,
        job_id: Optional[str] = None,
        run_id: Optional[str] = None,
        node_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        *,
        event_type: Optional[str] = None,
    ) -> int:
        """Appends an immutable audit event to SQLite events (and compatibility audit_events).

        Returns:
            The generated primary key event_id.
        """
        target = event_or_type if event_or_type is not None else event_type
        if target is None:
            raise ValueError(
                "Either an AuditEvent instance or an event_type string must be provided."
            )

        if isinstance(target, AuditEvent):
            event = target
            # Fill missing correlation if empty in event
            corr = get_current_correlation()
            if not event.job_id and corr.job_id:
                event.job_id = corr.job_id
            if not event.run_id and corr.run_id:
                event.run_id = corr.run_id
            if not event.node_id and corr.node_id:
                event.node_id = corr.node_id
            if not event.agent_id and corr.agent_id:
                event.agent_id = corr.agent_id
        else:
            event = create_audit_event(
                event_type=target,
                severity=severity,
                payload=payload,
                job_id=job_id,
                run_id=run_id,
                node_id=node_id,
                agent_id=agent_id,
            )

        sev = event.severity.upper()
        if sev not in ALL_SEVERITIES:
            raise ValueError(
                f"Invalid severity '{event.severity}'; must be one of {sorted(ALL_SEVERITIES)}"
            )

        payload_json = json.dumps(event.payload or {})
        created_at = event.created_at or datetime.now(timezone.utc).isoformat()

        conn, should_close = self._get_connection()

        try:
            cursor = conn.cursor()
            # Primary canonical table: events
            cursor.execute(
                """
                INSERT INTO events (job_id, run_id, node_id, agent_id, event_type, severity, payload_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.job_id,
                    event.run_id,
                    event.node_id,
                    event.agent_id,
                    event.event_type,
                    sev,
                    payload_json,
                    created_at,
                ),
            )
            event_id = cursor.lastrowid or 0

            # Compatibility table: audit_events (if exists in database)
            try:
                cursor.execute(
                    """
                    INSERT INTO audit_events (run_id, agent_id, event_type, severity, payload_json, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event.run_id,
                        event.agent_id,
                        event.event_type,
                        sev,
                        payload_json,
                        created_at,
                    ),
                )
            except sqlite3.OperationalError:
                # Table might not exist in simplified test schemas
                pass

            conn.commit()
            return event_id
        finally:
            if should_close:
                conn.close()

    def query_events(
        self,
        run_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        node_id: Optional[str] = None,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AuditEvent]:
        """Queries recorded audit events with optional filters (Read-Only)."""
        conn, should_close = self._get_connection()

        try:
            query = "SELECT event_id, job_id, run_id, node_id, agent_id, event_type, severity, payload_json, created_at FROM events WHERE 1=1"
            params: List[Any] = []

            if run_id is not None:
                query += " AND run_id = ?"
                params.append(run_id)
            if agent_id is not None:
                query += " AND agent_id = ?"
                params.append(agent_id)
            if node_id is not None:
                query += " AND node_id = ?"
                params.append(node_id)
            if event_type is not None:
                query += " AND event_type = ?"
                params.append(event_type)
            if severity is not None:
                query += " AND severity = ?"
                params.append(severity.upper())

            query += " ORDER BY event_id ASC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

            events: List[AuditEvent] = []
            for row in rows:
                try:
                    payload = json.loads(row["payload_json"] or "{}")
                except Exception:
                    payload = {}

                events.append(
                    AuditEvent(
                        event_id=row["event_id"],
                        job_id=row["job_id"],
                        run_id=row["run_id"],
                        node_id=row["node_id"],
                        agent_id=row["agent_id"],
                        event_type=row["event_type"],
                        severity=row["severity"],
                        payload=payload,
                        created_at=row["created_at"],
                    )
                )
            return events
        finally:
            if should_close:
                conn.close()

    def count_events(
        self,
        run_id: Optional[str] = None,
        event_type: Optional[str] = None,
    ) -> int:
        """Returns count of matching audit events."""
        conn, should_close = self._get_connection()

        try:
            query = "SELECT COUNT(*) FROM events WHERE 1=1"
            params: List[Any] = []
            if run_id is not None:
                query += " AND run_id = ?"
                params.append(run_id)
            if event_type is not None:
                query += " AND event_type = ?"
                params.append(event_type)

            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()[0]
        finally:
            if should_close:
                conn.close()

    def get_event_by_id(self, event_id: int) -> Optional[AuditEvent]:
        """Retrieves a single audit event by primary key ID."""
        conn, should_close = self._get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT event_id, job_id, run_id, node_id, agent_id, event_type, severity, payload_json, created_at FROM events WHERE event_id = ?",
                (event_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None
            try:
                payload = json.loads(row["payload_json"] or "{}")
            except Exception:
                payload = {}
            return AuditEvent(
                event_id=row["event_id"],
                job_id=row["job_id"],
                run_id=row["run_id"],
                node_id=row["node_id"],
                agent_id=row["agent_id"],
                event_type=row["event_type"],
                severity=row["severity"],
                payload=payload,
                created_at=row["created_at"],
            )
        finally:
            if should_close:
                conn.close()

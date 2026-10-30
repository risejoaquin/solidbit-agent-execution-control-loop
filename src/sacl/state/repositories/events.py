"""SACL V1 Event Repository.

Domain 9: Append-only system event log recording lifecycle transitions,
security events, and safety gates.
Compatibility Table: audit_events.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from sacl.contracts.models import AuditEvent
from sacl.state.repositories.base import BaseRepository
from sacl.state.utils import json_dumps_safe, json_loads_safe, utc_now

VALID_SEVERITIES = frozenset({"DEBUG", "INFO", "WARN", "ERROR", "FATAL"})


class EventRepository(BaseRepository):
    """Repository managing Domain 9 'events' and legacy 'audit_events'."""

    def record_event(self, event: Union[AuditEvent, Dict[str, Any]]) -> int:
        """Appends a structured audit event to the append-only event log.

        Simultaneously mirrors entries with severity IN ('INFO', 'WARN', 'ERROR', 'FATAL')
        into the legacy audit_events table for backward compatibility.
        """
        if isinstance(event, AuditEvent):
            event_type = event.event_type
            severity = event.severity
            payload = event.payload
            job_id = event.job_id
            run_id = event.run_id
            node_id = event.node_id
            agent_id = event.agent_id
            created_at = event.created_at or utc_now()
        else:
            event_type = event["event_type"]
            severity = event.get("severity", "INFO")
            payload = event.get("payload", {})
            job_id = event.get("job_id")
            run_id = event.get("run_id")
            node_id = event.get("node_id")
            agent_id = event.get("agent_id")
            created_at = event.get("created_at") or utc_now()

        if severity not in VALID_SEVERITIES:
            raise ValueError(f"Invalid event severity: {severity}")

        payload_json = json_dumps_safe(payload) or "{}"

        # Insert canonical Domain 9 event
        sql_events = """
            INSERT INTO events (
                job_id, run_id, node_id, agent_id, event_type,
                severity, payload_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        cursor = self.execute(
            sql_events,
            (job_id, run_id, node_id, agent_id, event_type, severity, payload_json, created_at),
        )
        event_id = cursor.lastrowid

        # Insert compatibility audit_events if severity allows
        if severity in ("INFO", "WARN", "ERROR", "FATAL"):
            sql_audit = """
                INSERT INTO audit_events (
                    run_id, agent_id, event_type, severity, payload_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?);
            """
            self.execute(
                sql_audit, (run_id, agent_id, event_type, severity, payload_json, created_at)
            )

        self.commit()
        return event_id  # type: ignore[return-value]

    def list_events(
        self,
        job_id: Optional[str] = None,
        run_id: Optional[str] = None,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Queries structured events from Domain 9 table."""
        conditions = []
        params: List[Any] = []
        if job_id:
            conditions.append("job_id = ?")
            params.append(job_id)
        if run_id:
            conditions.append("run_id = ?")
            params.append(run_id)
        if event_type:
            conditions.append("event_type = ?")
            params.append(event_type)
        if severity:
            conditions.append("severity = ?")
            params.append(severity)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        sql = f"SELECT * FROM events {where_clause} ORDER BY event_id ASC LIMIT ?;"  # nosec B608 - conditions are static strings
        params.append(limit)

        rows = self.fetchall_dict(sql, params)
        for r in rows:
            r["payload"] = json_loads_safe(r.get("payload_json"))
        return rows

    def list_audit_events(
        self,
        run_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Queries compatibility audit_events table."""
        if run_id:
            sql = "SELECT * FROM audit_events WHERE run_id = ? ORDER BY event_id ASC LIMIT ?;"
            rows = self.fetchall_dict(sql, (run_id, limit))
        else:
            sql = "SELECT * FROM audit_events ORDER BY event_id ASC LIMIT ?;"
            rows = self.fetchall_dict(sql, (limit,))

        for r in rows:
            r["payload"] = json_loads_safe(r.get("payload_json"))
        return rows

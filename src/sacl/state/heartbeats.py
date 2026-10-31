"""SACL V1 Heartbeat Monitoring.

Domain 14: High-frequency process liveness registry for daemons and worker processes.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union

from sacl.contracts.models import HeartbeatRecord
from sacl.state.repositories.base import BaseRepository
from sacl.state.utils import format_utc, json_dumps_safe, json_loads_safe, parse_utc, utc_now


class HeartbeatManager(BaseRepository):
    """Manager for Domain 14 'heartbeats' table."""

    def record_heartbeat(
        self,
        component: str,
        instance_id: str,
        pid: int,
        status: str = "HEALTHY",
        details: Optional[Union[Dict[str, Any], str]] = None,
        last_seen_at: Optional[str] = None,
    ) -> int:
        """Records high-frequency component liveness heartbeat."""
        now = last_seen_at or utc_now()
        details_json = json_dumps_safe(details) if isinstance(details, dict) else details

        sql = """
            INSERT INTO heartbeats (component, instance_id, pid, status, last_seen_at, details_json)
            VALUES (?, ?, ?, ?, ?, ?);
        """
        cursor = self.execute(sql, (component, instance_id, pid, status, now, details_json))
        self.commit()

        # Telemetry Event Bus Integration (Fail-Safe: Non-blocking, isolated from ACID transaction)
        try:
            from sacl.observability.events import create_audit_event, get_event_bus
            get_event_bus().publish(
                create_audit_event(
                    event_type="HEARTBEAT_RECORDED",
                    severity="DEBUG",
                    payload={
                        "component": component,
                        "instance_id": instance_id,
                        "pid": pid,
                        "status": status,
                        "last_seen_at": now,
                    },
                )
            )
        except Exception:
            # Observability failures must never break heartbeat persistence or cause transaction rollback
            pass

        return cursor.lastrowid  # type: ignore[return-value]

    def record_heartbeat_model(self, heartbeat: HeartbeatRecord) -> int:
        """Records a HeartbeatRecord model instance."""
        return self.record_heartbeat(
            component=heartbeat.component,
            instance_id=heartbeat.instance_id,
            pid=heartbeat.pid,
            status=heartbeat.status,
            details=heartbeat.details,
            last_seen_at=heartbeat.last_seen_at,
        )

    def get_latest_heartbeat(self, component: str, instance_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves most recent heartbeat record for a given component and instance."""
        sql = """
            SELECT * FROM heartbeats
            WHERE component = ? AND instance_id = ?
            ORDER BY heartbeat_id DESC
            LIMIT 1;
        """
        row = self.fetchone_dict(sql, (component, instance_id))
        if row:
            row["details"] = json_loads_safe(row.get("details_json"))
        return row

    def check_liveness(self, component: str, instance_id: str, max_stale_seconds: int = 30) -> bool:
        """Evaluates whether component instance has sent a heartbeat within max_stale_seconds."""
        latest = self.get_latest_heartbeat(component, instance_id)
        if not latest:
            return False

        last_seen_str = latest["last_seen_at"]
        try:
            last_seen_dt = parse_utc(last_seen_str)
            now_dt = datetime.now(timezone.utc)
            delta = (now_dt - last_seen_dt).total_seconds()
            return delta <= max_stale_seconds
        except Exception:
            return False

    def list_stale_instances(self, max_stale_seconds: int = 30) -> List[Dict[str, Any]]:
        """Finds all active instances whose latest heartbeat is older than max_stale_seconds."""
        now_dt = datetime.now(timezone.utc)
        cutoff_str = format_utc(now_dt - timedelta(seconds=max_stale_seconds))

        sql = """
            SELECT component, instance_id, pid, status, MAX(last_seen_at) as last_seen_at
            FROM heartbeats
            GROUP BY component, instance_id
            HAVING last_seen_at < ?;
        """
        return self.fetchall_dict(sql, (cutoff_str,))

    def list_heartbeats(
        self,
        component: Optional[str] = None,
        instance_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Queries historical heartbeat records."""
        conditions = []
        params: List[Any] = []
        if component:
            conditions.append("component = ?")
            params.append(component)
        if instance_id:
            conditions.append("instance_id = ?")
            params.append(instance_id)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        sql = f"SELECT * FROM heartbeats {where_clause} ORDER BY heartbeat_id DESC LIMIT ?;"  # nosec B608 - conditions are static strings
        params.append(limit)

        rows = self.fetchall_dict(sql, params)
        for r in rows:
            r["details"] = json_loads_safe(r.get("details_json"))
        return rows

    def cleanup_old_heartbeats(self, keep_seconds: int = 86400) -> int:
        """Prunes historical heartbeat rows older than keep_seconds."""
        now_dt = datetime.now(timezone.utc)
        cutoff_str = format_utc(now_dt - timedelta(seconds=keep_seconds))

        sql = "DELETE FROM heartbeats WHERE last_seen_at < ?;"
        cursor = self.execute(sql, (cutoff_str,))
        self.commit()
        return cursor.rowcount

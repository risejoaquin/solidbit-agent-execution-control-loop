"""Database Inspector UI Module.

Read-only, zero-locking inspection of sacl_ops.db domains and tables.
"""

from __future__ import annotations

import logging
import sqlite3
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("sacl.ui.modules.db_inspector")


class DBInspectorModule:
    """Provides schema overview and row statistics for SQLite operational store."""

    def __init__(self, get_ro_conn: Callable[[], Optional[sqlite3.Connection]]) -> None:
        self._get_ro_conn = get_ro_conn

    def get_database_stats(self) -> Dict[str, Any]:
        """Returns statistics for key tables in sacl_ops.db."""
        conn = self._get_ro_conn()
        if not conn:
            return {"tables": {}, "total_records": 0, "status": "NO_DATABASE"}

        tables = [
            "projects", "packages", "jobs", "runs", "graph_nodes",
            "agents", "events", "approvals", "artifacts", "results",
            "leases", "heartbeats", "errors", "audit_events"
        ]

        stats: Dict[str, int] = {}
        total = 0
        try:
            cur = conn.cursor()
            for t in tables:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {t};")
                    cnt = cur.fetchone()[0]
                    stats[t] = cnt
                    total += cnt
                except Exception:
                    stats[t] = 0
        except Exception as exc:
            logger.debug(f"DB inspector query failed: {exc}")
        finally:
            conn.close()

        return {
            "tables": stats,
            "total_records": total,
            "status": "OPERATIONAL_WAL",
        }

    def get_recent_audit_events(self, limit: int = 25) -> List[Dict[str, Any]]:
        """Queries recent system audit events."""
        conn = self._get_ro_conn()
        if not conn:
            return []

        events: List[Dict[str, Any]] = []
        try:
            cur = conn.cursor()
            cur.execute(
                f"""
                SELECT event_id, event_type, severity, component, message, timestamp
                FROM audit_events
                ORDER BY timestamp DESC
                LIMIT {limit};
                """
            )
            for row in cur.fetchall():
                events.append(dict(row))
        except Exception:
            # Table might be empty or fallback to events
            try:
                cur.execute(
                    f"""
                    SELECT event_id, event_type, payload_json, created_at as timestamp
                    FROM events
                    ORDER BY created_at DESC
                    LIMIT {limit};
                    """
                )
                for row in cur.fetchall():
                    events.append(dict(row))
            except Exception:
                pass
        finally:
            conn.close()

        return events

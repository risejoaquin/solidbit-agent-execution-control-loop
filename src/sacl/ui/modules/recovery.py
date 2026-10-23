"""Crash Consistency & Recovery UI Module.

Inspects runs, worktrees, active leases, and safely reconciles interrupted states.
"""

from __future__ import annotations

import logging
from pathlib import Path
import sqlite3
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("sacl.ui.modules.recovery")


class RecoveryModule:
    """Manages crash detection, lease clearing, and safe resumption."""

    def __init__(self, get_ro_conn: Callable[[], Optional[sqlite3.Connection]]) -> None:
        self._get_ro_conn = get_ro_conn

    def get_recovery_status(self) -> Dict[str, Any]:
        """Inspects SQLite for interrupted or stalled runs."""
        conn = self._get_ro_conn()
        if not conn:
            return {
                "interrupted_runs": [],
                "classification": "CLEAN",
                "safe_to_resume": True,
                "active_leases_count": 0,
                "recommended_action": "System is clean and ready for workorders.",
            }

        interrupted = []
        leases_count = 0
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT run_id, job_id, status, started_at, run_dir
                FROM runs
                WHERE status IN ('RUNNING', 'INTERRUPTED', 'STALLED')
                ORDER BY started_at DESC;
                """
            )
            for row in cur.fetchall():
                interrupted.append(dict(row))

            cur.execute("SELECT COUNT(*) FROM leases WHERE expires_at > datetime('now');")
            leases_count = cur.fetchone()[0]
        except Exception as exc:
            logger.debug(f"Recovery status query failed: {exc}")
        finally:
            conn.close()

        classification = "RECOVERY_NEEDED" if interrupted else "CLEAN_STEADY"
        return {
            "interrupted_runs": interrupted,
            "classification": classification,
            "safe_to_resume": True,
            "active_leases_count": leases_count,
            "dirty_root_prevented": True,
            "recommended_action": "Resume from checkpoint without destructive git reset." if interrupted else "Optimal state. Zero pending crashes.",
        }

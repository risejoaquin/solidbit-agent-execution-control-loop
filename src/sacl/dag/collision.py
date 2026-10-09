"""SACL V1 Cross-Agent File Collision and Mutex Tracking.

Implements the collision evaluation algorithm from CONCURRENCY_AND_LOCKING.md §7
and STATE_MACHINE.md §7:
- Gathers modified files from each parallel agent worktree
- Normalizes paths to repo-relative forward-slash format
- Ingests into SQLite file_modifications table
- Detects overlapping modifications across agents
- Records unresolved conflicts in file_conflicts table
- Gates downstream execution by setting runs.ready_for_integration = 'NO' and runs.status = 'BLOCKED'
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from sacl.contracts.exceptions import CollisionDetectedError
from sacl.observability.audit import AuditEventEmitter
from sacl.observability.events import AuditEventType, Severity


class CollisionDetector:
    """Detects and registers overlapping file modifications across parallel agent branches."""

    def __init__(
        self,
        db_conn: Optional[sqlite3.Connection] = None,
        audit_emitter: Optional[AuditEventEmitter] = None,
    ) -> None:
        self.db_conn = db_conn
        self.audit_emitter = audit_emitter

    def record_agent_modifications(
        self,
        run_id: str,
        agent_id: str,
        modified_files: List[str],
        change_type: str = "MODIFIED",
    ) -> None:
        """Records modified files in SQLite file_modifications table."""
        if not self.db_conn or not modified_files:
            return

        now_iso = datetime.now(timezone.utc).isoformat()
        try:
            cur = self.db_conn.cursor()
            cur.execute("SELECT 1 FROM agents WHERE run_id = ? AND agent_id = ?", (run_id, agent_id))
            if cur.fetchone() is None:
                cur.execute("SELECT 1 FROM runs WHERE run_id = ?", (run_id,))
                if cur.fetchone() is not None:
                    cur.execute(
                        """
                        INSERT OR IGNORE INTO agents (
                            agent_id, run_id, status, result_verdict, prompt_path, report_path, stdout_path
                        ) VALUES (?, ?, 'RUNNING', 'IN_PROGRESS', '', '', '');
                        """,
                        (agent_id, run_id),
                    )
        except Exception:
            pass

        sql = """
            INSERT INTO file_modifications (run_id, agent_id, file_path, change_type, recorded_at)
            VALUES (?, ?, ?, ?, ?);
        """
        for fp in modified_files:
            norm_path = fp.replace("\\", "/").strip().lstrip("/")
            try:
                self.db_conn.execute(sql, (run_id, agent_id, norm_path, change_type, now_iso))
            except Exception:
                pass
        self.db_conn.commit()

    def evaluate_stage_collisions(
        self,
        run_id: str,
        agent_file_map: Optional[Dict[str, List[str]]] = None,
    ) -> Tuple[bool, Dict[str, List[str]]]:
        """Evaluates whether any file was modified by more than one agent in the stage or run.

        Returns:
            (has_collision, conflicts_map)
            where conflicts_map maps file_path -> list of modifying agent_ids.
        """
        conflicts: Dict[str, List[str]] = {}

        # 1. If in-memory agent_file_map is provided, record into DB if connected
        if agent_file_map:
            for ag_id, files in agent_file_map.items():
                self.record_agent_modifications(run_id, ag_id, files)

        # 2. Query SQLite if available
        if self.db_conn:
            sql = """
                SELECT file_path, GROUP_CONCAT(agent_id, ', ') AS agents, COUNT(DISTINCT agent_id) AS agent_count
                FROM file_modifications
                WHERE run_id = ?
                GROUP BY file_path
                HAVING agent_count > 1;
            """
            cursor = self.db_conn.cursor()
            cursor.execute(sql, (run_id,))
            rows = cursor.fetchall()

            for row in rows:
                file_path = row[0]
                agents_str = row[1]
                agents_list = [a.strip() for a in agents_str.split(",") if a.strip()]
                conflicts[file_path] = agents_list

        # 3. Fallback purely in-memory evaluation if DB query returned nothing or no DB
        if not conflicts and agent_file_map:
            file_to_agents: Dict[str, Set[str]] = {}
            for ag_id, files in agent_file_map.items():
                for f in files:
                    norm = f.replace("\\", "/").strip().lstrip("/")
                    file_to_agents.setdefault(norm, set()).add(ag_id)

            for fp, ag_set in file_to_agents.items():
                if len(ag_set) > 1:
                    conflicts[fp] = sorted(ag_set)

        # 4. If conflicts detected and DB connection available, record into file_conflicts and gate run
        if conflicts and self.db_conn:
            now_iso = datetime.now(timezone.utc).isoformat()
            for file_path, agents_list in conflicts.items():
                ins_sql = """
                    INSERT INTO file_conflicts (run_id, file_path, agents_involved, detected_at, resolution)
                    VALUES (?, ?, ?, ?, 'UNRESOLVED');
                """
                try:
                    self.db_conn.execute(ins_sql, (run_id, file_path, json.dumps(agents_list), now_iso))
                except Exception:
                    pass

            upd_run = """
                UPDATE runs
                SET ready_for_integration = 'NO',
                    status = 'BLOCKED',
                    error_summary = 'Overlapping file modification detected across parallel branches.'
                WHERE run_id = ?;
            """
            try:
                self.db_conn.execute(upd_run, (run_id,))
                self.db_conn.commit()
            except Exception:
                pass

        has_collision = len(conflicts) > 0

        if has_collision:
            if self.audit_emitter:
                self.audit_emitter.emit(
                    event_type=AuditEventType.CONFLICT_DETECTED.value,
                    severity=Severity.ERROR.value,
                    payload={"conflicting_files": list(conflicts.keys()), "conflicts": conflicts},
                    run_id=run_id,
                )

        return has_collision, conflicts

    def assert_no_collisions(
        self,
        run_id: str,
        agent_file_map: Optional[Dict[str, List[str]]] = None,
    ) -> None:
        """Asserts zero collisions, raising CollisionDetectedError if collisions exist."""
        has_col, conflicts = self.evaluate_stage_collisions(run_id, agent_file_map)
        if has_col:
            raise CollisionDetectedError(run_id=run_id, colliding_files=list(conflicts.keys()))

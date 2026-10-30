"""SACL V1 Cross-Agent File Overlap and Collision Protocol.

Implements the collision detection and gating invariants from RESULT_PROTOCOL.md §6:
1. Diff harvesting and path normalization across active agent worktrees.
2. Registration in SQLite table file_modifications.
3. Conflict evaluation query (GROUP_CONCAT having agent_count > 1).
4. Gating enforcement: If collisions exist, ready_for_integration is set strictly to 'NO',
   file_conflicts rows are recorded, and downstream integration is hard-blocked.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set

from sacl.observability.audit import AuditEventEmitter
from sacl.observability.events import (
    CONFLICT_DETECTED,
    Severity,
)
from sacl.results.models import CollisionReport

logger = logging.getLogger("sacl.results.collision")


def normalize_file_path(path_str: str) -> str:
    """Normalizes file path to lowercase, forward-slash, repository-relative format."""
    clean = path_str.strip().replace("\\", "/")
    # Remove leading slashes and drive letters if present
    if ":" in clean:
        clean = clean.split(":", 1)[1]
    clean = clean.lstrip("/")
    return clean.lower()


class CollisionDetector:
    """Coordinates cross-agent file modification harvesting, collision evaluation, and gating."""

    def __init__(self, audit_emitter: Optional[AuditEventEmitter] = None) -> None:
        self.audit_emitter = audit_emitter

    def record_file_modifications(
        self,
        run_id: str,
        agent_id: str,
        file_paths: List[str],
        db_conn: sqlite3.Connection,
        change_type: str = "MODIFIED",
        recorded_at: Optional[str] = None,
    ) -> List[str]:
        """Normalizes and records modified files in SQLite file_modifications table.

        Returns:
            List of normalized file paths recorded.
        """
        now = recorded_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        cursor = db_conn.cursor()

        normalized_paths: List[str] = []
        seen: Set[str] = set()

        for fp in file_paths:
            norm = normalize_file_path(fp)
            if not norm or norm in seen:
                continue
            seen.add(norm)
            normalized_paths.append(norm)

            cursor.execute(
                """
                INSERT INTO file_modifications (run_id, agent_id, file_path, change_type, recorded_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (run_id, agent_id, norm, change_type, now),
            )

        db_conn.commit()
        logger.debug(
            "Recorded %d file modifications for agent %s in run %s",
            len(normalized_paths),
            agent_id,
            run_id,
        )
        return normalized_paths

    def evaluate_conflicts(
        self,
        run_id: str,
        db_conn: sqlite3.Connection,
        detected_at: Optional[str] = None,
    ) -> CollisionReport:
        """Executes the canonical conflict query and applies integration gating.

        Returns:
            CollisionReport detailing collisions and integration readiness.
        """
        now = detected_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        cursor = db_conn.cursor()

        # Canonical Conflict Evaluation Query (RESULT_PROTOCOL.md §6.1)
        query = """
            SELECT file_path, GROUP_CONCAT(agent_id, ', ') AS agents, COUNT(DISTINCT agent_id) AS agent_count
            FROM file_modifications
            WHERE run_id = ?
            GROUP BY file_path
            HAVING agent_count > 1
            ORDER BY file_path ASC;
        """
        cursor.execute(query, (run_id,))
        rows = cursor.fetchall()

        conflicting_files: List[str] = []
        conflicts_by_file: Dict[str, List[str]] = {}
        blockers: List[str] = []

        for row in rows:
            file_path = row[0]
            agents_raw = row[1]
            agents_list = sorted([a.strip() for a in agents_raw.split(",") if a.strip()])

            conflicting_files.append(file_path)
            conflicts_by_file[file_path] = agents_list

            # Insert into file_conflicts table
            agents_json = json.dumps(agents_list)
            cursor.execute(
                """
                INSERT INTO file_conflicts (run_id, file_path, agents_involved, detected_at, resolution)
                VALUES (?, ?, ?, ?, 'UNRESOLVED')
                """,
                (run_id, file_path, agents_json, now),
            )

            # Emit audit event
            if self.audit_emitter:
                self.audit_emitter.emit(
                    event_type=CONFLICT_DETECTED,
                    severity=Severity.ERROR,
                    run_id=run_id,
                    payload={
                        "file_path": file_path,
                        "agents_involved": agents_list,
                        "agent_count": len(agents_list),
                    },
                )

        # Gating Enforcement:
        # If any collision is found, ready_for_integration is set strictly to 'NO'
        if conflicting_files:
            ready_for_integration = "NO"
            blocker_msg = (
                f"Overlapping file modifications detected across parallel branches: "
                f"{len(conflicting_files)} conflicting file(s) ({', '.join(conflicting_files[:3])}"
                f"{'...' if len(conflicting_files) > 3 else ''})."
            )
            blockers.append(blocker_msg)
            logger.warning(
                "Run %s has %d file collisions: setting ready_for_integration='NO'",
                run_id,
                len(conflicting_files),
            )
        else:
            ready_for_integration = "YES"
            logger.info("Run %s has zero file collisions: ready_for_integration='YES'", run_id)

        # Update runs table ready_for_integration flag
        cursor.execute(
            "UPDATE runs SET ready_for_integration = ? WHERE run_id = ?",
            (ready_for_integration, run_id),
        )
        db_conn.commit()

        return CollisionReport(
            run_id=run_id,
            conflicting_files=conflicting_files,
            conflicts_by_file=conflicts_by_file,
            ready_for_integration=ready_for_integration,
            blockers=blockers,
        )


__all__ = ["CollisionDetector", "normalize_file_path"]

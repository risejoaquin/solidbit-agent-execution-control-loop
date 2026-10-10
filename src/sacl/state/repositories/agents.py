"""SACL V1 Agent Repository.

Domain 8: Agent worker instances, worker PID tracking, isolated worktree paths,
and 4-point reconciliation state.
Compatibility Tables: file_modifications, file_conflicts.
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any, Dict, List, Optional

from sacl.contracts.invariants import AgentStatus, Verdict
from sacl.state.exceptions import EntityNotFoundError, InvalidStateTransitionError
from sacl.state.repositories.base import BaseRepository
from sacl.state.utils import json_dumps_safe, json_loads_safe, normalize_repo_path, utc_now

VALID_AGENT_STATUSES = frozenset({
    'SCHEDULED', 'LAUNCHING', 'RUNNING',
    'TIMEOUT_RUNNING', 'STOPPING', 'STOPPED',
    'COMPLETE', 'FAILED', 'UNKNOWN',
    'PENDING', 'READY', 'SUCCEEDED',
    'RETRYABLE_FAILURE', 'BLOCKED',
    'WAITING_APPROVAL', 'CANCELLED'
})

VALID_AGENT_VERDICTS = frozenset({
    'PASS', 'PARTIAL', 'BLOCKED', 'FAILED',
    'IN_PROGRESS', 'UNKNOWN', 'STOPPED_BY_USER',
    'PASS (Report Present)', 'DONE_REVIEW_REQUIRED'
})


class AgentRepository(BaseRepository):
    """Repository managing Domain 8 'agents' and file collision tracking."""

    # =========================================================================
    # DOMAIN 8: AGENTS
    # =========================================================================

    def record_agent(
        self,
        agent_id: str,
        run_id: str,
        status: str,
        prompt_path: str,
        report_path: str,
        stdout_path: str,
        stderr_path: str,
        pid: Optional[int] = None,
        worktree_path: Optional[str] = None,
        branch: Optional[str] = None,
        stage_id: Optional[int] = None,
        node_id: Optional[str] = None,
        result_verdict: str = "UNKNOWN",
        started_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Records initial worker agent instance."""
        if status not in VALID_AGENT_STATUSES:
            raise InvalidStateTransitionError("agent", f"{run_id}:{agent_id}", "NONE", status)
        if result_verdict not in VALID_AGENT_VERDICTS:
            raise ValueError(f"Invalid result_verdict: {result_verdict}")

        now = utc_now()
        start_time = started_at or now

        norm_prompt = normalize_repo_path(prompt_path)
        norm_report = normalize_repo_path(report_path)
        norm_stdout = normalize_repo_path(stdout_path)
        norm_stderr = normalize_repo_path(stderr_path)
        norm_worktree = normalize_repo_path(worktree_path) if worktree_path else None

        sql = """
            INSERT INTO agents (
                agent_id, run_id, stage_id, node_id, status,
                result_verdict, pid, branch, commit_sha, worktree_path,
                prompt_path, report_path, stdout_path, stderr_path,
                started_at, updated_at, finished_at, exit_code, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL);
        """
        self.execute(
            sql,
            (
                agent_id, run_id, stage_id, node_id, status,
                result_verdict, pid, branch, norm_worktree,
                norm_prompt, norm_report, norm_stdout, norm_stderr,
                start_time, now,
            ),
        )
        self.commit()
        return self.get_agent(agent_id, run_id)  # type: ignore[return-value]

    def update_agent(
        self,
        agent_id: str,
        run_id: str,
        status: str,
        result_verdict: str,
        exit_code: Optional[int] = None,
        commit_sha: Optional[str] = None,
        error_message: Optional[str] = None,
        finished_at: Optional[str] = None,
        pid: Optional[int] = None,
    ) -> None:
        """Updates agent worker lifecycle state, process exit, and verdict."""
        if status not in VALID_AGENT_STATUSES:
            raise InvalidStateTransitionError("agent", f"{run_id}:{agent_id}", "UNKNOWN", status)
        if result_verdict not in VALID_AGENT_VERDICTS:
            raise ValueError(f"Invalid result_verdict: {result_verdict}")

        existing = self.get_agent(agent_id, run_id)
        if not existing:
            raise EntityNotFoundError(f"Agent '{agent_id}' in run '{run_id}' not found")

        now = utc_now()
        terminal_states = {'COMPLETE', 'FAILED', 'STOPPED', 'SUCCEEDED', 'CANCELLED'}
        resolved_finished_at = finished_at
        if resolved_finished_at is None and status in terminal_states:
            resolved_finished_at = now

        sql = """
            UPDATE agents
            SET status = ?,
                result_verdict = ?,
                exit_code = COALESCE(?, exit_code),
                commit_sha = COALESCE(?, commit_sha),
                error_message = COALESCE(?, error_message),
                finished_at = COALESCE(?, finished_at),
                pid = COALESCE(?, pid),
                updated_at = ?
            WHERE agent_id = ? AND run_id = ?;
        """
        self.execute(
            sql,
            (
                status, result_verdict, exit_code, commit_sha,
                error_message, resolved_finished_at, pid, now,
                agent_id, run_id,
            ),
        )
        self.commit()

    def get_agent(self, agent_id: str, run_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves agent instance by compound key (agent_id, run_id)."""
        sql = "SELECT * FROM agents WHERE agent_id = ? AND run_id = ?;"
        return self.fetchone_dict(sql, (agent_id, run_id))

    def list_agents(self, run_id: str) -> List[Dict[str, Any]]:
        """Lists all agents associated with a given execution run."""
        sql = "SELECT * FROM agents WHERE run_id = ? ORDER BY agent_id;"
        return self.fetchall_dict(sql, (run_id,))

    # =========================================================================
    # COMPATIBILITY TABLES: file_modifications & file_conflicts
    # =========================================================================

    def record_file_modifications(
        self,
        run_id: str,
        agent_id: str,
        file_paths: List[str],
        change_type: str = "MODIFIED",
    ) -> None:
        """Records modified files for cross-agent conflict detection."""
        if change_type not in ('MODIFIED', 'ADDED', 'DELETED'):
            raise ValueError(f"Invalid change_type: {change_type}")

        now = utc_now()
        sql = """
            INSERT INTO file_modifications (run_id, agent_id, file_path, change_type, recorded_at)
            VALUES (?, ?, ?, ?, ?);
        """
        params = [
            (run_id, agent_id, normalize_repo_path(fp), change_type, now)
            for fp in file_paths
        ]
        self.executemany(sql, params)
        self.commit()

    def detect_file_conflicts(self, run_id: str) -> List[Dict[str, Any]]:
        """Evaluates overlapping file modifications across parallel agent branches.

        Identifies files modified by more than one agent, records conflicts in
        the file_conflicts table, and updates run integration readiness.
        """
        query_overlaps = """
            SELECT file_path,
                   GROUP_CONCAT(DISTINCT agent_id) as agents_str,
                   COUNT(DISTINCT agent_id) as agent_count
            FROM file_modifications
            WHERE run_id = ?
            GROUP BY file_path
            HAVING agent_count > 1;
        """
        overlapping_rows = self.fetchall_dict(query_overlaps, (run_id,))
        now = utc_now()

        for row in overlapping_rows:
            fp = row["file_path"]
            agents_list = sorted([a.strip() for a in row["agents_str"].split(",") if a.strip()])
            agents_json = json_dumps_safe(agents_list)

            # Insert if not already tracked
            check_sql = "SELECT conflict_id FROM file_conflicts WHERE run_id = ? AND file_path = ?;"
            existing = self.fetchone_dict(check_sql, (run_id, fp))
            if not existing:
                insert_conflict = """
                    INSERT INTO file_conflicts (run_id, file_path, agents_involved, detected_at, resolution)
                    VALUES (?, ?, ?, ?, 'UNRESOLVED');
                """
                self.execute(insert_conflict, (run_id, fp, agents_json, now))

        self.commit()

        # Update runs ready_for_integration
        if overlapping_rows:
            self.execute("UPDATE runs SET ready_for_integration = 'NO' WHERE run_id = ?;", (run_id,))
        else:
            self.execute("UPDATE runs SET ready_for_integration = 'YES' WHERE run_id = ?;", (run_id,))
        self.commit()

        # Return active conflicts
        return self.list_file_conflicts(run_id)

    def list_file_conflicts(self, run_id: str) -> List[Dict[str, Any]]:
        """Lists recorded file conflicts for an execution run."""
        sql = "SELECT * FROM file_conflicts WHERE run_id = ? ORDER BY file_path;"
        rows = self.fetchall_dict(sql, (run_id,))
        for r in rows:
            r["agents"] = json_loads_safe(r.get("agents_involved"))
        return rows

    def resolve_file_conflict(self, conflict_id: int, resolution: str = "RESOLVED") -> None:
        """Marks a file conflict as RESOLVED or WAIVED."""
        if resolution not in ('RESOLVED', 'WAIVED', 'UNRESOLVED'):
            raise ValueError(f"Invalid conflict resolution: {resolution}")
        sql = "UPDATE file_conflicts SET resolution = ? WHERE conflict_id = ?;"
        self.execute(sql, (resolution, conflict_id))
        self.commit()

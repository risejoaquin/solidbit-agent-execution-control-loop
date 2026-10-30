"""SACL V1 Graph & Node Repository.

Domain 6: Ephemeral Graph-H DAG nodes (9 canonical states).
Domain 7: Node attempts execution history.
Compatibility Tables: dag_stages, agent_dependencies.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from sacl.contracts.invariants import GRAPH_NODE_STATES, GraphNodeStatus
from sacl.state.exceptions import EntityNotFoundError, InvalidStateTransitionError
from sacl.state.repositories.base import BaseRepository
from sacl.state.utils import normalize_repo_path, utc_now


class GraphRepository(BaseRepository):
    """Repository managing Domains 6 and 7, plus DAG compatibility tables."""

    # =========================================================================
    # DOMAIN 6: GRAPH NODES
    # =========================================================================

    def create_node(
        self,
        run_id: str,
        node_id: str,
        job_id: str,
        phase_number: int,
        stage_name: str,
        agent_id: str,
        status: str = GraphNodeStatus.PENDING.value,
        timeout_seconds: int = 1800,
        max_attempts: int = 1,
    ) -> Dict[str, Any]:
        """Creates an ephemeral Graph-H DAG node record."""
        if status not in GRAPH_NODE_STATES:
            raise InvalidStateTransitionError("graph_node", f"{run_id}:{node_id}", "NONE", status)

        sql = """
            INSERT INTO graph_nodes (
                run_id, node_id, job_id, phase_number, stage_name,
                agent_id, status, started_at, completed_at,
                timeout_seconds, max_attempts, current_attempt, result_verdict
            ) VALUES (?, ?, ?, ?, ?, ?, ?, NULL, NULL, ?, ?, 0, NULL);
        """
        self.execute(
            sql,
            (
                run_id,
                node_id,
                job_id,
                phase_number,
                stage_name,
                agent_id,
                status,
                timeout_seconds,
                max_attempts,
            ),
        )
        self.commit()
        return self.get_node(run_id, node_id)  # type: ignore[return-value]

    def update_node_status(
        self,
        run_id: str,
        node_id: str,
        status: str,
        result_verdict: Optional[str] = None,
        current_attempt: Optional[int] = None,
        started_at: Optional[str] = None,
        completed_at: Optional[str] = None,
    ) -> None:
        """Updates graph node execution state and verdict."""
        if status not in GRAPH_NODE_STATES:
            raise InvalidStateTransitionError(
                "graph_node", f"{run_id}:{node_id}", "UNKNOWN", status
            )

        existing = self.get_node(run_id, node_id)
        if not existing:
            raise EntityNotFoundError(f"Graph node '{node_id}' in run '{run_id}' not found")

        now = utc_now()
        resolved_started_at = started_at
        if (
            resolved_started_at is None
            and status == GraphNodeStatus.RUNNING.value
            and not existing.get("started_at")
        ):
            resolved_started_at = now

        resolved_completed_at = completed_at
        if resolved_completed_at is None and status in {
            GraphNodeStatus.SUCCEEDED.value,
            GraphNodeStatus.FAILED.value,
            GraphNodeStatus.CANCELLED.value,
            GraphNodeStatus.BLOCKED.value,
        }:
            resolved_completed_at = now

        sql = """
            UPDATE graph_nodes
            SET status = ?,
                result_verdict = COALESCE(?, result_verdict),
                current_attempt = COALESCE(?, current_attempt),
                started_at = COALESCE(?, started_at),
                completed_at = COALESCE(?, completed_at)
            WHERE run_id = ? AND node_id = ?;
        """
        self.execute(
            sql,
            (
                status,
                result_verdict,
                current_attempt,
                resolved_started_at,
                resolved_completed_at,
                run_id,
                node_id,
            ),
        )
        self.commit()

    def get_node(self, run_id: str, node_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves graph node by compound key (run_id, node_id)."""
        sql = "SELECT * FROM graph_nodes WHERE run_id = ? AND node_id = ?;"
        return self.fetchone_dict(sql, (run_id, node_id))

    def list_nodes(self, run_id: str, phase_number: Optional[int] = None) -> List[Dict[str, Any]]:
        """Lists nodes for a given run, optionally filtered by phase."""
        if phase_number is not None:
            sql = (
                "SELECT * FROM graph_nodes WHERE run_id = ? AND phase_number = ? ORDER BY node_id;"
            )
            return self.fetchall_dict(sql, (run_id, phase_number))
        sql = "SELECT * FROM graph_nodes WHERE run_id = ? ORDER BY phase_number, node_id;"
        return self.fetchall_dict(sql, (run_id,))

    # =========================================================================
    # DOMAIN 7: NODE ATTEMPTS
    # =========================================================================

    def record_node_attempt(
        self,
        run_id: str,
        node_id: str,
        attempt_number: int,
        pid: Optional[int] = None,
        status: str = "LAUNCHING",
        started_at: Optional[str] = None,
        stdout_path: Optional[str] = None,
        stderr_path: Optional[str] = None,
        report_path: Optional[str] = None,
    ) -> int:
        """Records an execution attempt for a graph node."""
        start_time = started_at or utc_now()
        sql = """
            INSERT INTO node_attempts (
                run_id, node_id, attempt_number, pid, status,
                exit_code, started_at, finished_at, verdict,
                error_message, stdout_path, stderr_path, report_path
            ) VALUES (?, ?, ?, ?, ?, NULL, ?, NULL, NULL, NULL, ?, ?, ?);
        """
        norm_stdout = normalize_repo_path(stdout_path) if stdout_path else None
        norm_stderr = normalize_repo_path(stderr_path) if stderr_path else None
        norm_report = normalize_repo_path(report_path) if report_path else None

        cursor = self.execute(
            sql,
            (
                run_id,
                node_id,
                attempt_number,
                pid,
                status,
                start_time,
                norm_stdout,
                norm_stderr,
                norm_report,
            ),
        )
        self.commit()
        return cursor.lastrowid  # type: ignore[return-value]

    def update_node_attempt(
        self,
        attempt_id: int,
        status: str,
        exit_code: Optional[int] = None,
        verdict: Optional[str] = None,
        error_message: Optional[str] = None,
        finished_at: Optional[str] = None,
    ) -> None:
        """Updates a node attempt outcome."""
        fin = finished_at or utc_now()
        sql = """
            UPDATE node_attempts
            SET status = ?,
                exit_code = COALESCE(?, exit_code),
                verdict = COALESCE(?, verdict),
                error_message = COALESCE(?, error_message),
                finished_at = COALESCE(?, finished_at)
            WHERE attempt_id = ?;
        """
        self.execute(sql, (status, exit_code, verdict, error_message, fin, attempt_id))
        self.commit()

    def list_node_attempts(self, run_id: str, node_id: str) -> List[Dict[str, Any]]:
        """Lists all attempts for a given graph node in chronological order."""
        sql = "SELECT * FROM node_attempts WHERE run_id = ? AND node_id = ? ORDER BY attempt_number ASC;"
        return self.fetchall_dict(sql, (run_id, node_id))

    # =========================================================================
    # COMPATIBILITY TABLES: dag_stages & agent_dependencies
    # =========================================================================

    def record_stage(
        self,
        run_id: str,
        phase_number: int,
        stage_name: str,
        status: str = "PENDING",
    ) -> int:
        """Records a compatibility dag_stage entry."""
        sql = """
            INSERT INTO dag_stages (run_id, phase_number, stage_name, status, started_at, completed_at)
            VALUES (?, ?, ?, ?, NULL, NULL);
        """
        cursor = self.execute(sql, (run_id, phase_number, stage_name, status))
        self.commit()
        return cursor.lastrowid  # type: ignore[return-value]

    def update_stage_status(
        self,
        stage_id: int,
        status: str,
        started_at: Optional[str] = None,
        completed_at: Optional[str] = None,
    ) -> None:
        """Updates compatibility dag_stage status."""
        sql = """
            UPDATE dag_stages
            SET status = ?,
                started_at = COALESCE(?, started_at),
                completed_at = COALESCE(?, completed_at)
            WHERE stage_id = ?;
        """
        self.execute(sql, (status, started_at, completed_at, stage_id))
        self.commit()

    def list_stages(self, run_id: str) -> List[Dict[str, Any]]:
        """Lists compatibility dag_stages for a run."""
        sql = "SELECT * FROM dag_stages WHERE run_id = ? ORDER BY phase_number ASC;"
        return self.fetchall_dict(sql, (run_id,))

    def add_dependency(self, run_id: str, upstream_agent_id: str, downstream_agent_id: str) -> None:
        """Adds a DAG edge in compatibility table agent_dependencies."""
        sql = """
            INSERT OR IGNORE INTO agent_dependencies (run_id, upstream_agent_id, downstream_agent_id)
            VALUES (?, ?, ?);
        """
        self.execute(sql, (run_id, upstream_agent_id, downstream_agent_id))
        self.commit()

    def list_dependencies(self, run_id: str) -> List[Dict[str, Any]]:
        """Lists all agent dependencies for a run."""
        sql = "SELECT * FROM agent_dependencies WHERE run_id = ?;"
        return self.fetchall_dict(sql, (run_id,))

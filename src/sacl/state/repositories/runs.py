"""SACL V1 Run Repository.

Domain 5: Physical execution attempts, workspaces, integration readiness,
and 4-part reconciled outcomes.
"""

from __future__ import annotations

import sqlite3
from typing import Any, Dict, List, Optional

from sacl.state.exceptions import EntityNotFoundError, InvalidStateTransitionError
from sacl.state.repositories.base import BaseRepository
from sacl.state.utils import normalize_repo_path, utc_now

VALID_RUN_STATUSES = frozenset({
    'RECEIVED', 'AUTHENTICATED', 'VALIDATED', 'PERSISTED',
    'QUEUED', 'DISPATCHED', 'RUNNING', 'VERIFYING',
    'RESULT_PACKAGED', 'RESULT_SENT', 'COMPLETED', 'ARCHIVED',
    'WAITING_APPROVAL', 'RETRY_WAIT', 'BLOCKED', 'FAILED',
    'CANCELLED', 'INTERRUPTED', 'TIMED_OUT', 'POLICY_DENIED',
    'REJECTED', 'QUARANTINED',
    'INITIALIZED', 'GATE_HALTED', 'COMPLETE', 'STOPPED'
})


class RunRepository(BaseRepository):
    """Repository managing Domain 5 'runs' table."""

    def create_run(
        self,
        run_id: str,
        job_id: str,
        package_id: str,
        project: str,
        repository: str,
        mode: str,
        source_orchestrator: str,
        target_repo_path: str,
        run_dir: str,
        status: str = "INITIALIZED",
        project_id: Optional[str] = None,
        ready_for_integration: str = "NO",
        started_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Creates a new concrete execution run record."""
        if status not in VALID_RUN_STATUSES:
            raise InvalidStateTransitionError("run", run_id, "NONE", status)

        start_time = started_at or utc_now()
        norm_run_dir = normalize_repo_path(run_dir)
        norm_target_repo = normalize_repo_path(target_repo_path)
        norm_source_orch = normalize_repo_path(source_orchestrator)

        sql = """
            INSERT INTO runs (
                run_id, job_id, package_id, project_id, project, repository,
                mode, source_orchestrator, target_repo_path, run_dir, status,
                ready_for_integration, started_at, completed_at,
                reconciled_verdict, error_summary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL);
        """
        self.execute(
            sql,
            (
                run_id, job_id, package_id, project_id, project, repository,
                mode, norm_source_orch, norm_target_repo, norm_run_dir, status,
                ready_for_integration, start_time,
            ),
        )
        self.commit()
        return self.get_run(run_id)  # type: ignore[return-value]

    def update_run_status(
        self,
        run_id: str,
        status: str,
        ready_for_integration: Optional[str] = None,
        reconciled_verdict: Optional[str] = None,
        error_summary: Optional[str] = None,
        completed_at: Optional[str] = None,
    ) -> None:
        """Updates run attempt lifecycle status and final verdict."""
        if status not in VALID_RUN_STATUSES:
            raise InvalidStateTransitionError("run", run_id, "UNKNOWN", status)

        existing = self.get_run(run_id)
        if not existing:
            raise EntityNotFoundError(f"Run '{run_id}' not found")

        terminal_states = {'COMPLETED', 'COMPLETE', 'FAILED', 'CANCELLED', 'STOPPED', 'INTERRUPTED', 'TIMED_OUT'}
        now = utc_now()
        resolved_completed_at = completed_at
        if resolved_completed_at is None and status in terminal_states:
            resolved_completed_at = now

        sql = """
            UPDATE runs
            SET status = ?,
                ready_for_integration = COALESCE(?, ready_for_integration),
                reconciled_verdict = COALESCE(?, reconciled_verdict),
                error_summary = COALESCE(?, error_summary),
                completed_at = COALESCE(?, completed_at)
            WHERE run_id = ?;
        """
        self.execute(sql, (status, ready_for_integration, reconciled_verdict, error_summary, resolved_completed_at, run_id))
        self.commit()

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves physical run record by ID."""
        sql = "SELECT * FROM runs WHERE run_id = ?;"
        return self.fetchone_dict(sql, (run_id,))

    def list_runs(
        self,
        job_id: Optional[str] = None,
        project_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Lists runs filtered by job, project, or status."""
        conditions = []
        params: List[Any] = []
        if job_id:
            conditions.append("job_id = ?")
            params.append(job_id)
        if project_id:
            conditions.append("(project_id = ? OR project = ?)")
            params.extend([project_id, project_id])
        if status:
            conditions.append("status = ?")
            params.append(status)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        sql = f"SELECT * FROM runs {where_clause} ORDER BY started_at DESC LIMIT ?;"
        params.append(limit)
        return self.fetchall_dict(sql, params)

    def set_ready_for_integration(self, run_id: str, ready: str = "YES") -> None:
        """Sets pre-merge integration readiness flag ('YES' or 'NO')."""
        if ready not in ("YES", "NO"):
            raise ValueError(f"ready_for_integration must be 'YES' or 'NO', got '{ready}'")
        sql = "UPDATE runs SET ready_for_integration = ? WHERE run_id = ?;"
        self.execute(sql, (ready, run_id))
        self.commit()

    def has_active_mutating_run_for_project(self, project_id: str) -> bool:
        """Checks if a project has an actively executing mutating run (Concurrency Baseline)."""
        sql = """
            SELECT COUNT(*) AS active_count
            FROM runs
            WHERE (project_id = ? OR project = ?)
              AND status IN ('RUNNING', 'DISPATCHED', 'VERIFYING', 'INITIALIZED');
        """
        row = self.fetchone_dict(sql, (project_id, project_id))
        return bool(row and row.get("active_count", 0) > 0)

"""SACL V1 Job Repository.

Domain 4: Authoritative top-level logical job lifecycle state machine
covering the 12 primary canonical states and 10 side states.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from sacl.contracts.invariants import ALL_JOB_STATES, JobSideStatus, JobStatus
from sacl.state.exceptions import EntityNotFoundError, InvalidStateTransitionError
from sacl.state.repositories.base import BaseRepository
from sacl.state.utils import json_dumps_safe, json_loads_safe, utc_now


class JobRepository(BaseRepository):
    """Repository managing Domain 4 'jobs' table."""

    def create_job(
        self,
        job_id: str,
        package_id: Optional[str] = None,
        project_id: Optional[str] = None,
        status: str = JobStatus.RECEIVED.value,
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Creates a new logical job record."""
        if status not in ALL_JOB_STATES:
            raise InvalidStateTransitionError("job", job_id, "NONE", status)

        now = created_at or utc_now()
        meta_json = json_dumps_safe(metadata)

        sql = """
            INSERT INTO jobs (
                job_id, package_id, project_id, status, priority,
                created_at, updated_at, completed_at, current_run_id,
                error_summary, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL, ?);
        """
        self.execute(sql, (job_id, package_id, project_id, status, priority, now, now, meta_json))
        self.commit()
        return self.get_job(job_id)  # type: ignore[return-value]

    def update_job_status(
        self,
        job_id: str,
        status: str,
        current_run_id: Optional[str] = None,
        error_summary: Optional[str] = None,
        completed_at: Optional[str] = None,
    ) -> None:
        """Updates job lifecycle status and associated execution pointers."""
        if status not in ALL_JOB_STATES:
            raise InvalidStateTransitionError("job", job_id, "UNKNOWN", status)

        existing = self.get_job(job_id)
        if not existing:
            raise EntityNotFoundError(f"Job '{job_id}' not found")

        now = utc_now()
        final_states = {
            JobStatus.COMPLETED.value,
            JobStatus.ARCHIVED.value,
            JobSideStatus.FAILED.value,
            JobSideStatus.CANCELLED.value,
            JobSideStatus.TIMED_OUT.value,
            JobSideStatus.POLICY_DENIED.value,
            JobSideStatus.REJECTED.value,
            JobSideStatus.QUARANTINED.value,
        }

        resolved_completed_at = completed_at
        if resolved_completed_at is None and status in final_states:
            resolved_completed_at = now

        sql = """
            UPDATE jobs
            SET status = ?,
                updated_at = ?,
                current_run_id = COALESCE(?, current_run_id),
                error_summary = COALESCE(?, error_summary),
                completed_at = COALESCE(?, completed_at)
            WHERE job_id = ?;
        """
        self.execute(
            sql, (status, now, current_run_id, error_summary, resolved_completed_at, job_id)
        )
        self.commit()

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves logical job by ID with unpacked metadata."""
        sql = "SELECT * FROM jobs WHERE job_id = ?;"
        row = self.fetchone_dict(sql, (job_id,))
        if row and row.get("metadata_json"):
            row["metadata"] = json_loads_safe(row["metadata_json"])
        elif row:
            row["metadata"] = None
        return row

    def list_jobs(
        self,
        status: Optional[str] = None,
        project_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Lists jobs with optional status and project filters."""
        conditions = []
        params: List[Any] = []
        if status:
            conditions.append("status = ?")
            params.append(status)
        if project_id:
            conditions.append("project_id = ?")
            params.append(project_id)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        sql = f"SELECT * FROM jobs {where_clause} ORDER BY priority DESC, created_at ASC LIMIT ?;"  # nosec B608 - conditions are static strings
        params.append(limit)

        rows = self.fetchall_dict(sql, params)
        for r in rows:
            r["metadata"] = json_loads_safe(r.get("metadata_json"))
        return rows

    def peek_next_queued_job(self, project_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Returns highest priority pending job in status QUEUED."""
        jobs = self.list_jobs(status=JobStatus.QUEUED.value, project_id=project_id, limit=1)
        return jobs[0] if jobs else None

    def cancel_job(self, job_id: str, reason: str = "Operator Cancel") -> None:
        """Transitions job to CANCELLED side state."""
        self.update_job_status(job_id, status=JobSideStatus.CANCELLED.value, error_summary=reason)

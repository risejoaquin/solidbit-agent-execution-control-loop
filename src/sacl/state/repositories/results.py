"""SACL V1 Result Repository.

Domain 12: Sealed final execution results, dual deliverable pointers,
and transport delivery evidence.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from sacl.state.repositories.base import BaseRepository
from sacl.state.utils import normalize_repo_path, utc_now

VALID_RESULT_VERDICTS = frozenset(
    {
        "PASS",
        "PARTIAL",
        "BLOCKED",
        "FAILED",
        "PASS (Report Present)",
        "DONE_REVIEW_REQUIRED",
        "STOPPED_BY_USER",
        "UNKNOWN",
    }
)


class ResultRepository(BaseRepository):
    """Repository managing Domain 12 'results' table."""

    def record_result(
        self,
        job_id: str,
        run_id: str,
        status: str,
        final_verdict: str,
        summary_md_path: str,
        summary_json_path: str,
        package_result_zip: Optional[str] = None,
        delivered_to: Optional[str] = None,
        delivered_at: Optional[str] = None,
        created_at: Optional[str] = None,
    ) -> int:
        """Records authoritative sealed final result for a run attempt."""
        if final_verdict not in VALID_RESULT_VERDICTS:
            raise ValueError(f"Invalid final_verdict: {final_verdict}")

        now = created_at or utc_now()
        norm_summary_md = normalize_repo_path(summary_md_path)
        norm_summary_json = normalize_repo_path(summary_json_path)
        norm_zip = normalize_repo_path(package_result_zip) if package_result_zip else None

        sql = """
            INSERT INTO results (
                job_id, run_id, status, final_verdict,
                summary_md_path, summary_json_path, package_result_zip,
                delivered_to, delivered_at, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(run_id) DO UPDATE SET
                status = excluded.status,
                final_verdict = excluded.final_verdict,
                summary_md_path = excluded.summary_md_path,
                summary_json_path = excluded.summary_json_path,
                package_result_zip = excluded.package_result_zip,
                delivered_to = excluded.delivered_to,
                delivered_at = excluded.delivered_at;
        """
        cursor = self.execute(
            sql,
            (
                job_id,
                run_id,
                status,
                final_verdict,
                norm_summary_md,
                norm_summary_json,
                norm_zip,
                delivered_to,
                delivered_at,
                now,
            ),
        )
        self.commit()
        return cursor.lastrowid  # type: ignore[return-value]

    def get_result(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves result record by run ID."""
        sql = "SELECT * FROM results WHERE run_id = ?;"
        return self.fetchone_dict(sql, (run_id,))

    def get_result_by_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves most recent result record for a logical job."""
        sql = "SELECT * FROM results WHERE job_id = ? ORDER BY created_at DESC LIMIT 1;"
        return self.fetchone_dict(sql, (job_id,))

    def mark_delivered(
        self, run_id: str, delivered_to: str, delivered_at: Optional[str] = None
    ) -> None:
        """Updates result delivery evidence."""
        now = delivered_at or utc_now()
        sql = "UPDATE results SET delivered_to = ?, delivered_at = ? WHERE run_id = ?;"
        self.execute(sql, (delivered_to, now, run_id))
        self.commit()

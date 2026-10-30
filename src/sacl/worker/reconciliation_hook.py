"""SACL V1 Four-Part Run Status Reconciliation Hook.

Implements the canonical 4-dimensional reconciliation invariant from
RESULT_PROTOCOL.md and ADR-013:
1. Process Observation (PID check, image whitelist, 300s start-time drift guard)
2. Persisted State (SQLite agents table records)
3. Required Outputs (Physical deliverable markdown files, non-empty, log files)
4. Final Verdict Extraction (Priority ladder across report regexes, headers, and logs)

Invariant:
Run success NEVER depends on process exit code alone.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from sacl.contracts.interfaces import IReconciler
from sacl.contracts.invariants import (
    ALLOWED_PROCESS_IMAGES,
    PID_DRIFT_TOLERANCE_SECONDS,
    Verdict,
)
from sacl.contracts.models import (
    PersistedState,
    ReconciledResult,
    RequiredOutputs,
    WorktreeState,
)
from sacl.contracts.reconciliation import (
    reconcile_agent,
    verify_process_observation,
)


class WorkerReconciler(IReconciler):
    """Executes 4-pillar reconciliation for worker tasks."""

    def __init__(self, db_conn: Optional[sqlite3.Connection] = None) -> None:
        self.db_conn = db_conn

    def reconcile(
        self,
        run_id: str,
        agent_id: str,
        pid: Optional[int],
        process_name: str,
        is_active: bool,
        exit_code: Optional[int],
        persisted_start_time: Optional[str],
        actual_start_time: Optional[datetime],
        persisted_status: str,
        report_path: Path,
        stdout_path: Path,
        stderr_path: Path,
        worktree_path: Path,
        job_id: Optional[str] = None,
        node_id: Optional[str] = None,
        stage_id: Optional[Any] = None,
        branch: Optional[str] = None,
        commit_sha: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> ReconciledResult:
        """Evaluates 4 pillars and returns canonical reconciled verdict."""
        # 1. Pillar 1: Process observation
        process_obs, is_valid_obs, obs_reason = verify_process_observation(
            pid=pid,
            process_name=process_name,
            is_active=is_active,
            exit_code=exit_code,
            persisted_start_time=persisted_start_time,
            actual_start_time=actual_start_time,
            allowed_images=ALLOWED_PROCESS_IMAGES,
            drift_tolerance_seconds=PID_DRIFT_TOLERANCE_SECONDS,
        )

        # 2. Pillar 2: Persisted state
        persisted_state = PersistedState(
            status=persisted_status,
            started_at=persisted_start_time,
            updated_at=datetime.now(timezone.utc).isoformat(),
            finished_at=datetime.now(timezone.utc).isoformat() if not is_active else None,
        )

        # 3. Pillar 3: Required outputs
        report_path = Path(report_path)
        stdout_path = Path(stdout_path)
        stderr_path = Path(stderr_path)

        report_exists = report_path.exists()
        report_size = report_path.stat().st_size if report_exists else 0

        stdout_exists = stdout_path.exists()
        stdout_size = stdout_path.stat().st_size if stdout_exists else 0

        stderr_exists = stderr_path.exists()
        stderr_size = stderr_path.stat().st_size if stderr_exists else 0

        required_outputs = RequiredOutputs(
            report_path=str(report_path),
            report_exists=report_exists,
            report_size_bytes=report_size,
            stdout_path=str(stdout_path),
            stderr_path=str(stderr_path),
            expected_files_verified=report_exists and report_size > 0,
        )

        # Read contents for verdict extraction
        report_content: Optional[str] = None
        if report_exists and report_size > 0:
            try:
                with open(report_path, "r", encoding="utf-8", errors="replace") as f:
                    report_content = f.read()
            except Exception:
                pass

        stdout_content: Optional[str] = None
        if stdout_exists and stdout_size > 0:
            try:
                with open(stdout_path, "r", encoding="utf-8", errors="replace") as f:
                    stdout_content = f.read()
            except Exception:
                pass

        stderr_content: Optional[str] = None
        if stderr_exists and stderr_size > 0:
            try:
                with open(stderr_path, "r", encoding="utf-8", errors="replace") as f:
                    stderr_content = f.read()
            except Exception:
                pass

        # Worktree state
        worktree_state = WorktreeState(
            worktree_path=str(worktree_path),
            branch=branch,
            commit_sha=commit_sha,
            is_clean=True,
            modified_files=[],
        )

        # 4. Synthesize via reconcile_agent
        result = reconcile_agent(
            run_id=run_id,
            agent_id=agent_id,
            process_obs=process_obs,
            persisted_state=persisted_state,
            required_outputs=required_outputs,
            worktree=worktree_state,
            job_id=job_id,
            node_id=node_id or agent_id,
            stage_id=stage_id,
            report_content=report_content,
            stdout_content=stdout_content,
            stderr_content=stderr_content,
            error_message=error_message or obs_reason,
        )

        # If PID verification failed (e.g. recycled), override status to FAILED/UNKNOWN
        if not is_valid_obs:
            result.status = "FAILED"
            result.result_verdict = Verdict.FAILED.value
            result.error_message = obs_reason

        return result

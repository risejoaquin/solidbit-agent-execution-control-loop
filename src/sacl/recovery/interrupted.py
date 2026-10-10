"""SACL V1 Interrupted Run & Crash Recovery Subsystem.

Implements docs/RECOVERY_MODEL.md §3, §4, §5 & §6:
1. Discovers active runs interrupted by supervisor crash or host reboot.
2. Enforces the Local Dirty-Root Rule before proceeding.
3. For each active agent:
   - Performs 3-way process check (Process Observation).
   - If alive & valid: reconnects supervision.
   - If terminated or PID recycled: executes 4-point deliverable recovery.
4. Updates SQLite tables (runs, agents, graph_nodes, errors, events).
5. Never blindly restarts old running jobs.
6. Evaluates safe-to-resume decisions and yields BLOCKED_RECOVERY_REVIEW when review is required.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from sacl.contracts.invariants import (
    ALLOWED_PROCESS_IMAGES,
    PID_DRIFT_TOLERANCE_SECONDS,
    Verdict,
)
from sacl.contracts.models import (
    PersistedState,
    ProcessObservation,
    RequiredOutputs,
    WorktreeState,
)
from sacl.contracts.reconciliation import (
    extract_verdict_from_content,
    reconcile_agent,
)
from sacl.observability.events import (
    GATE_HALTED,
    PID_RECYCLED_DETECTED,
    RUN_FAILED,
    create_audit_event,
)
from sacl.recovery.process_identity import (
    MockProcessInspector,
    ProcessInspectionStatus,
    ProcessInspector,
    get_default_process_inspector,
    inspect_process,
)
from sacl.recovery.safe_to_resume import (
    SafeToResumeDecision,
    SafeToResumeOutcome,
    evaluate_agent_safe_to_resume,
    evaluate_run_safe_to_resume,
)
from sacl.recovery.worktree_inspection import (
    GitClient,
    check_primary_repo_clean,
    get_default_git_client,
    inspect_agent_worktree,
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class AgentRecoveryReport:
    """Recovery and reconciliation outcome for an individual agent."""

    agent_id: str
    previous_status: str
    reconciled_status: str
    reconciled_verdict: str
    is_alive: bool
    is_recycled: bool
    safe_to_resume: SafeToResumeDecision
    error_message: Optional[str] = None
    report_exists: bool = False
    report_size_bytes: int = 0
    worktree_clean: bool = True
    uncommitted_files: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "previous_status": self.previous_status,
            "reconciled_status": self.reconciled_status,
            "reconciled_verdict": self.reconciled_verdict,
            "is_alive": self.is_alive,
            "is_recycled": self.is_recycled,
            "safe_to_resume": self.safe_to_resume.to_dict(),
            "error_message": self.error_message,
            "report_exists": self.report_exists,
            "report_size_bytes": self.report_size_bytes,
            "worktree_clean": self.worktree_clean,
            "uncommitted_files": list(self.uncommitted_files),
        }


@dataclass
class InterruptedRunRecoveryReport:
    """Consolidated recovery report for an interrupted run attempt."""

    run_id: str
    previous_status: str
    final_status: str
    final_verdict: str
    run_decision: SafeToResumeDecision
    agent_reports: List[AgentRecoveryReport]
    primary_repo_clean: bool
    dirty_root_halted: bool = False
    error_summary: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "previous_status": self.previous_status,
            "final_status": self.final_status,
            "final_verdict": self.final_verdict,
            "run_decision": self.run_decision.to_dict(),
            "agent_reports": [r.to_dict() for r in self.agent_reports],
            "primary_repo_clean": self.primary_repo_clean,
            "dirty_root_halted": self.dirty_root_halted,
            "error_summary": self.error_summary,
        }


def find_interrupted_runs(conn: sqlite3.Connection) -> List[sqlite3.Row]:
    """Queries sacl_ops.db for in-flight execution runs interrupted by crash."""
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM runs
        WHERE status IN ('RUNNING', 'DISPATCHED', 'VERIFYING', 'QUEUED')
        ORDER BY started_at ASC;
        """
    )
    return cursor.fetchall()


def recover_interrupted_run(
    run_row: sqlite3.Row,
    conn: sqlite3.Connection,
    inspector: Optional[ProcessInspector] = None,
    git_client: Optional[GitClient] = None,
    event_recorder_fn: Optional[Any] = None,
) -> InterruptedRunRecoveryReport:
    """Executes the canonical crash recovery sequence for a single interrupted run.

    Follows RECOVERY_MODEL.md §3, §4, §5 & §6.
    """
    run_id = run_row["run_id"]
    target_repo = run_row["target_repo_path"]
    run_dir = run_row["run_dir"]
    orig_status = run_row["status"]

    insp = inspector or get_default_process_inspector()
    git = git_client or get_default_git_client()

    now_iso = _utc_now_iso()

    # Step 1: Check primary checkout clean root status
    cleanliness = check_primary_repo_clean(target_repo, git_client=git)
    if not cleanliness.is_clean:
        # Local Dirty-Root Rule: HALT IMMEDIATELY with BLOCKED / DIRTY_ROOT_BLOCKS_RECOVERY
        halt_msg = cleanliness.error_message or "DIRTY_ROOT_BLOCKS_RECOVERY"
        with conn:
            conn.execute(
                """
                UPDATE runs
                SET status = 'BLOCKED',
                    reconciled_verdict = 'BLOCKED',
                    completed_at = ?,
                    error_summary = ?
                WHERE run_id = ?;
                """,
                (now_iso, halt_msg, run_id),
            )
            # Record audit event
            evt = create_audit_event(
                event_type=GATE_HALTED,
                severity="FATAL",
                payload={
                    "reason": "DIRTY_ROOT_BLOCKS_RECOVERY",
                    "repo_path": target_repo,
                    "uncommitted_files": cleanliness.uncommitted_files,
                },
                run_id=run_id,
            )
            conn.execute(
                """
                INSERT INTO events (event_type, severity, payload_json, created_at, run_id)
                VALUES (?, ?, ?, ?, ?);
                """,
                (evt.event_type, evt.severity, str(evt.payload), evt.created_at, run_id),
            )
            # Record error in errors table
            conn.execute(
                """
                INSERT INTO errors (error_code, category, severity, message, occurred_at, run_id)
                VALUES ('DIRTY_ROOT_HALT', 'RECOVERY', 'FATAL', ?, ?, ?);
                """,
                (halt_msg, now_iso, run_id),
            )

        run_decision = SafeToResumeDecision(
            outcome=SafeToResumeOutcome.BLOCKED_DIRTY_ROOT,
            can_resume=False,
            requires_blind_restart=False,
            reason=halt_msg,
            blockers=[f"Uncommitted files in primary repo: {cleanliness.uncommitted_files}"],
            next_safe_action="Operator must commit or resolve uncommitted changes in primary checkout.",
            details={"uncommitted_files": cleanliness.uncommitted_files},
        )

        return InterruptedRunRecoveryReport(
            run_id=run_id,
            previous_status=orig_status,
            final_status="BLOCKED",
            final_verdict=Verdict.BLOCKED.value,
            run_decision=run_decision,
            agent_reports=[],
            primary_repo_clean=False,
            dirty_root_halted=True,
            error_summary=halt_msg,
        )

    # Step 2: Query all active agents for this run
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM agents
        WHERE run_id = ?
        ORDER BY agent_id ASC;
        """,
        (run_id,),
    )
    agent_rows = cursor.fetchall()

    agent_reports: List[AgentRecoveryReport] = []
    agent_decisions: List[SafeToResumeDecision] = []

    for a_row in agent_rows:
        agent_id = a_row["agent_id"]
        a_status = a_row["status"]
        a_pid = a_row["pid"]
        a_started_at = a_row["started_at"]
        a_report_path = Path(a_row["report_path"]) if a_row["report_path"] else None
        a_stdout_path = Path(a_row["stdout_path"]) if a_row["stdout_path"] else None
        a_stderr_path = Path(a_row["stderr_path"]) if a_row["stderr_path"] else None
        a_worktree_path = Path(a_row["worktree_path"]) if a_row["worktree_path"] else None
        a_branch = a_row["branch"]

        # Only reconcile agents that were in non-terminal states
        if a_status not in {"RUNNING", "TIMEOUT_RUNNING", "LAUNCHING", "SCHEDULED"}:
            # Already terminal; check existing decision
            existing_verdict = a_row["result_verdict"] or Verdict.UNKNOWN.value
            dec = evaluate_agent_safe_to_resume(
                agent_id=agent_id,
                is_process_alive=False,
                is_process_valid=False,
                has_report=(a_report_path.exists() if a_report_path else False),
                report_size_bytes=(a_report_path.stat().st_size if a_report_path and a_report_path.exists() else 0),
                is_worktree_clean=True,
                extracted_verdict=existing_verdict,
                current_agent_status=a_status,
            )
            agent_decisions.append(dec)
            agent_reports.append(
                AgentRecoveryReport(
                    agent_id=agent_id,
                    previous_status=a_status,
                    reconciled_status=a_status,
                    reconciled_verdict=existing_verdict,
                    is_alive=False,
                    is_recycled=False,
                    safe_to_resume=dec,
                )
            )
            continue

        # Execute 3-way process check
        obs_res = inspect_process(
            pid=a_pid,
            persisted_start_time=a_started_at,
            inspector=insp,
        )

        is_alive = obs_res.is_alive
        is_recycled = obs_res.is_recycled

        if is_recycled:
            # PID recycling detected! Log error and event
            with conn:
                conn.execute(
                    """
                    INSERT INTO events (event_type, severity, payload_json, created_at, run_id, agent_id)
                    VALUES (?, 'WARN', ?, ?, ?, ?);
                    """,
                    (PID_RECYCLED_DETECTED, str(obs_res.failure_reason), now_iso, run_id, agent_id),
                )
                conn.execute(
                    """
                    INSERT INTO errors (error_code, category, severity, message, occurred_at, run_id, agent_id)
                    VALUES ('PID_RECYCLED', 'RECOVERY', 'WARN', ?, ?, ?, ?);
                    """,
                    (f"PID recycling detected on agent {agent_id}: {obs_res.failure_reason}", now_iso, run_id, agent_id),
                )

        # Inspect Worktree
        wt_result = None
        is_wt_clean = True
        modified_files: List[str] = []
        if a_worktree_path:
            wt_result = inspect_agent_worktree(a_worktree_path, expected_branch=a_branch, git_client=git)
            is_wt_clean = wt_result.is_clean
            modified_files = wt_result.modified_files

        # Inspect Deliverables
        has_report = a_report_path.exists() if a_report_path else False
        report_size = a_report_path.stat().st_size if has_report and a_report_path else 0
        report_content = a_report_path.read_text(encoding="utf-8", errors="replace") if has_report and a_report_path else None
        stdout_content = a_stdout_path.read_text(encoding="utf-8", errors="replace") if a_stdout_path and a_stdout_path.exists() else None
        stderr_content = a_stderr_path.read_text(encoding="utf-8", errors="replace") if a_stderr_path and a_stderr_path.exists() else None

        extracted_ve = extract_verdict_from_content(
            report_content=report_content,
            stdout_content=stdout_content,
            stderr_content=stderr_content,
            report_exists=has_report,
            report_size_bytes=report_size,
            exit_code=obs_res.observation.exit_code,
            persisted_verdict=None,
        )

        extracted_verdict = extracted_ve.verdict

        # Evaluate Safe-To-Resume
        agent_dec = evaluate_agent_safe_to_resume(
            agent_id=agent_id,
            is_process_alive=is_alive,
            is_process_valid=obs_res.is_valid,
            has_report=has_report,
            report_size_bytes=report_size,
            is_worktree_clean=is_wt_clean,
            extracted_verdict=extracted_verdict,
            current_agent_status=a_status,
            uncommitted_files=modified_files,
        )
        agent_decisions.append(agent_dec)

        # Determine Reconciled DB Status & Verdict
        if agent_dec.outcome == SafeToResumeOutcome.RESUME_SUPERVISION:
            # Process is still alive and healthy; keep status RUNNING, update heartbeat
            new_status = "RUNNING"
            new_verdict = Verdict.IN_PROGRESS.value
            err_msg = None
            with conn:
                conn.execute(
                    """
                    UPDATE agents
                    SET updated_at = ?
                    WHERE agent_id = ? AND run_id = ?;
                    """,
                    (now_iso, agent_id, run_id),
                )
        elif not is_wt_clean:
            # Dirty worktree on recovery -> FAILED with UNCOMMITTED_CHANGES_ON_RECOVERY
            new_status = "FAILED"
            new_verdict = Verdict.FAILED.value
            err_msg = (
                f"UNCOMMITTED_CHANGES_ON_RECOVERY: Agent left {len(modified_files)} uncommitted files "
                f"in worktree upon supervisor recovery. Preserved for forensics."
            )
            with conn:
                conn.execute(
                    """
                    UPDATE agents
                    SET status = ?,
                        result_verdict = ?,
                        finished_at = ?,
                        updated_at = ?,
                        error_message = ?
                    WHERE agent_id = ? AND run_id = ?;
                    """,
                    (new_status, new_verdict, now_iso, now_iso, err_msg, agent_id, run_id),
                )
                conn.execute(
                    """
                    UPDATE graph_nodes
                    SET status = 'FAILED',
                        result_verdict = 'FAILED',
                        completed_at = ?
                    WHERE run_id = ? AND agent_id = ?;
                    """,
                    (now_iso, run_id, agent_id),
                )
                conn.execute(
                    """
                    INSERT INTO errors (error_code, category, severity, message, occurred_at, run_id, agent_id)
                    VALUES ('UNCOMMITTED_CHANGES', 'RECOVERY', 'ERROR', ?, ?, ?, ?);
                    """,
                    (err_msg, now_iso, run_id, agent_id),
                )
        elif agent_dec.outcome == SafeToResumeOutcome.RECONCILE_OUTPUTS:
            # Valid complete report on disk -> Reconcile to COMPLETE
            new_status = "COMPLETE"
            new_verdict = extracted_verdict
            err_msg = None
            with conn:
                conn.execute(
                    """
                    UPDATE agents
                    SET status = ?,
                        result_verdict = ?,
                        finished_at = ?,
                        updated_at = ?
                    WHERE agent_id = ? AND run_id = ?;
                    """,
                    (new_status, new_verdict, now_iso, now_iso, agent_id, run_id),
                )
                conn.execute(
                    """
                    UPDATE graph_nodes
                    SET status = 'SUCCEEDED',
                        result_verdict = ?,
                        completed_at = ?
                    WHERE run_id = ? AND agent_id = ?;
                    """,
                    (new_verdict, now_iso, run_id, agent_id),
                )
        elif extracted_verdict == Verdict.DONE_REVIEW_REQUIRED.value:
            # Review required
            new_status = "COMPLETE"
            new_verdict = Verdict.DONE_REVIEW_REQUIRED.value
            err_msg = "Deliverables mandate human review before downstream consumption."
            with conn:
                conn.execute(
                    """
                    UPDATE agents
                    SET status = ?,
                        result_verdict = ?,
                        finished_at = ?,
                        updated_at = ?,
                        error_message = ?
                    WHERE agent_id = ? AND run_id = ?;
                    """,
                    (new_status, new_verdict, now_iso, now_iso, err_msg, agent_id, run_id),
                )
                conn.execute(
                    """
                    UPDATE graph_nodes
                    SET status = 'WAITING_APPROVAL',
                        result_verdict = ?,
                        completed_at = ?
                    WHERE run_id = ? AND agent_id = ?;
                    """,
                    (new_verdict, now_iso, run_id, agent_id),
                )
        elif extracted_verdict == Verdict.BLOCKED.value:
            new_status = "FAILED"
            new_verdict = Verdict.BLOCKED.value
            err_msg = "Agent deliverable indicates BLOCKED verdict."
            with conn:
                conn.execute(
                    """
                    UPDATE agents
                    SET status = ?,
                        result_verdict = ?,
                        finished_at = ?,
                        updated_at = ?,
                        error_message = ?
                    WHERE agent_id = ? AND run_id = ?;
                    """,
                    (new_status, new_verdict, now_iso, now_iso, err_msg, agent_id, run_id),
                )
                conn.execute(
                    """
                    UPDATE graph_nodes
                    SET status = 'BLOCKED',
                        result_verdict = 'BLOCKED',
                        completed_at = ?
                    WHERE run_id = ? AND agent_id = ?;
                    """,
                    (now_iso, run_id, agent_id),
                )
        else:
            # Missing deliverables or crashed -> FAILED / NO_EVIDENCE_FOUND
            new_status = "FAILED"
            new_verdict = Verdict.FAILED.value
            err_msg = "Process terminated without required deliverable report (NO_EVIDENCE_FOUND)."
            with conn:
                conn.execute(
                    """
                    UPDATE agents
                    SET status = ?,
                        result_verdict = ?,
                        finished_at = ?,
                        updated_at = ?,
                        error_message = ?
                    WHERE agent_id = ? AND run_id = ?;
                    """,
                    (new_status, new_verdict, now_iso, now_iso, err_msg, agent_id, run_id),
                )
                conn.execute(
                    """
                    UPDATE graph_nodes
                    SET status = 'FAILED',
                        result_verdict = 'FAILED',
                        completed_at = ?
                    WHERE run_id = ? AND agent_id = ?;
                    """,
                    (now_iso, run_id, agent_id),
                )
                conn.execute(
                    """
                    INSERT INTO errors (error_code, category, severity, message, occurred_at, run_id, agent_id)
                    VALUES ('NO_EVIDENCE_FOUND', 'RECOVERY', 'ERROR', ?, ?, ?, ?);
                    """,
                    (err_msg, now_iso, run_id, agent_id),
                )

        agent_reports.append(
            AgentRecoveryReport(
                agent_id=agent_id,
                previous_status=a_status,
                reconciled_status=new_status,
                reconciled_verdict=new_verdict,
                is_alive=is_alive,
                is_recycled=is_recycled,
                safe_to_resume=agent_dec,
                error_message=err_msg,
                report_exists=has_report,
                report_size_bytes=report_size,
                worktree_clean=is_wt_clean,
                uncommitted_files=modified_files,
            )
        )

    # Step 3: Evaluate Run-Level Safe-To-Resume Decision
    run_decision = evaluate_run_safe_to_resume(
        run_id=run_id,
        primary_repo_clean=cleanliness.is_clean,
        agent_decisions=agent_decisions,
        current_run_status=orig_status,
    )

    final_run_status = orig_status
    final_run_verdict = Verdict.UNKNOWN.value
    run_err_summary = None

    if run_decision.outcome == SafeToResumeOutcome.RESUME_SUPERVISION:
        final_run_status = "RUNNING"
        final_run_verdict = Verdict.IN_PROGRESS.value
        run_err_summary = "Live supervisor reconnected to surviving child worker processes."
    elif run_decision.outcome == SafeToResumeOutcome.RECONCILE_OUTPUTS:
        final_run_status = "VERIFYING"
        final_run_verdict = Verdict.PASS.value
        run_err_summary = "All agents reconciled from physical deliverables. Progressing to verification."
        with conn:
            conn.execute(
                """
                UPDATE runs
                SET status = 'VERIFYING',
                    reconciled_verdict = ?,
                    error_summary = ?
                WHERE run_id = ?;
                """,
                (final_run_verdict, run_err_summary, run_id),
            )
    elif run_decision.outcome == SafeToResumeOutcome.BLOCKED_RECOVERY_REVIEW:
        final_run_status = "BLOCKED"
        final_run_verdict = Verdict.DONE_REVIEW_REQUIRED.value
        run_err_summary = "BLOCKED_RECOVERY_REVIEW: Recovery requires human review due to uncommitted changes or review markers."
        with conn:
            conn.execute(
                """
                UPDATE runs
                SET status = 'BLOCKED',
                    reconciled_verdict = ?,
                    completed_at = ?,
                    error_summary = ?
                WHERE run_id = ?;
                """,
                (final_run_verdict, now_iso, run_err_summary, run_id),
            )
            conn.execute(
                """
                INSERT INTO events (event_type, severity, payload_json, created_at, run_id)
                VALUES ('BLOCKED_RECOVERY_REVIEW', 'WARN', ?, ?, ?);
                """,
                (str({"blockers": run_decision.blockers}), now_iso, run_id),
            )
    elif run_decision.outcome == SafeToResumeOutcome.CANNOT_RESUME_INTERRUPTED:
        # Mark as INTERRUPTED
        final_run_status = "INTERRUPTED"
        final_run_verdict = Verdict.FAILED.value
        run_err_summary = (
            "INTERRUPTED: Supervisor restart or host crash interrupted active run. "
            "Child workers terminated without required deliverables. Blind restart prohibited."
        )
        with conn:
            conn.execute(
                """
                UPDATE runs
                SET status = 'INTERRUPTED',
                    reconciled_verdict = ?,
                    completed_at = ?,
                    error_summary = ?
                WHERE run_id = ?;
                """,
                (final_run_verdict, now_iso, run_err_summary, run_id),
            )
            conn.execute(
                """
                INSERT INTO events (event_type, severity, payload_json, created_at, run_id)
                VALUES (?, 'ERROR', ?, ?, ?);
                """,
                (RUN_FAILED, str({"reason": "INTERRUPTED"}), now_iso, run_id),
            )

    return InterruptedRunRecoveryReport(
        run_id=run_id,
        previous_status=orig_status,
        final_status=final_run_status,
        final_verdict=final_run_verdict,
        run_decision=run_decision,
        agent_reports=agent_reports,
        primary_repo_clean=cleanliness.is_clean,
        dirty_root_halted=False,
        error_summary=run_err_summary,
    )

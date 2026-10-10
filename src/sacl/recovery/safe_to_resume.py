"""SACL V1 Safe-To-Resume Decision Engine.

Implements docs/RECOVERY_MODEL.md §6:
INVIOLABLE INVARIANT: The recovery engine NEVER blindly restarts old RUNNING tasks or jobs.
It inspects process observation, persisted state, and required outputs before deciding
whether to resume supervision, reconcile results, or transition to INTERRUPTED / FAILED.
Immutable checkpointed phases with passing verdicts are NEVER re-executed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from sacl.contracts.invariants import Verdict


class SafeToResumeOutcome(str, Enum):
    """Authoritative outcome of a safe-to-resume evaluation."""

    # Worker survived crash -> safe to reconnect live supervisor monitoring
    RESUME_SUPERVISION = "RESUME_SUPERVISION"

    # Stage / node / agent completed with verified passing deliverables -> immutable, never rerun
    IMMUTABLE_COMPLETED = "IMMUTABLE_COMPLETED"

    # Worker terminated while down, but deliverables exist on disk -> reconcile to success
    RECONCILE_OUTPUTS = "RECONCILE_OUTPUTS"

    # Primary repository checkout is dirty -> halts immediately for human safety
    BLOCKED_DIRTY_ROOT = "BLOCKED_DIRTY_ROOT"

    # Ambiguous deliverables, uncommitted worktree changes, or explicit review required
    BLOCKED_RECOVERY_REVIEW = "BLOCKED_RECOVERY_REVIEW"

    # Worker dead and outputs missing -> cannot blindly restart; mark INTERRUPTED/FAILED
    CANNOT_RESUME_INTERRUPTED = "CANNOT_RESUME_INTERRUPTED"

    # Active supervisor already running with valid singleton lease
    SUPERVISOR_ALREADY_ACTIVE = "SUPERVISOR_ALREADY_ACTIVE"


@dataclass
class SafeToResumeDecision:
    """Rigorous evaluation of whether execution can safely resume."""

    outcome: SafeToResumeOutcome
    can_resume: bool
    reason: str
    blockers: List[str] = field(default_factory=list)
    next_safe_action: str = ""
    requires_blind_restart: bool = False  # INVIOLABLE INVARIANT: ALWAYS False
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "outcome": self.outcome.value,
            "can_resume": self.can_resume,
            "requires_blind_restart": self.requires_blind_restart,
            "reason": self.reason,
            "blockers": list(self.blockers),
            "next_safe_action": self.next_safe_action,
            "details": dict(self.details),
        }


def assert_no_blind_restart(decision: SafeToResumeDecision) -> None:
    """Enforces the constitutional invariant that blind restarts are strictly prohibited."""
    if decision.requires_blind_restart:
        raise RuntimeError(
            "CRITICAL INVARIANT VIOLATION: Blind restart requested! "
            "Never blindly restart old RUNNING tasks without 4-pillar evidence reconciliation."
        )


def evaluate_agent_safe_to_resume(
    agent_id: str,
    is_process_alive: bool,
    is_process_valid: bool,
    has_report: bool,
    report_size_bytes: int,
    is_worktree_clean: bool,
    extracted_verdict: Optional[str] = None,
    current_agent_status: Optional[str] = None,
    uncommitted_files: Optional[List[str]] = None,
) -> SafeToResumeDecision:
    """Evaluates whether an individual agent worker is safe to resume or reconcile.

    Decision Rules:
    1. If agent process is alive and passes 3-way check:
       -> RESUME_SUPERVISION (Reconnect live monitor)
    2. If agent already completed with verified PASS/PARTIAL/PASS_REPORT_PRESENT:
       -> IMMUTABLE_COMPLETED (Do not re-execute)
    3. If worktree has uncommitted modifications:
       -> BLOCKED_RECOVERY_REVIEW (Preserve files, mark UNCOMMITTED_CHANGES_ON_RECOVERY)
    4. If report exists, non-empty, and extracted verdict is DONE_REVIEW_REQUIRED:
       -> BLOCKED_RECOVERY_REVIEW (Requires human review before downstream use)
    5. If report exists, non-empty, clean worktree, and extracted verdict is PASS/PARTIAL/PASS_REPORT_PRESENT:
       -> RECONCILE_OUTPUTS (Reconcile to COMPLETE without restarting)
    6. If process is dead and report is missing or 0 bytes:
       -> CANNOT_RESUME_INTERRUPTED (Mark INTERRUPTED or FAILED; never blindly restart)
    """
    uncommitted_files = uncommitted_files or []

    # 1. Surviving worker check
    if is_process_alive and is_process_valid:
        return SafeToResumeDecision(
            outcome=SafeToResumeOutcome.RESUME_SUPERVISION,
            can_resume=True,
            requires_blind_restart=False,
            reason=f"Agent '{agent_id}' process is alive and valid; reconnect live supervision.",
            next_safe_action=f"Attach supervisor heartbeat and monitor agent '{agent_id}'.",
            details={"agent_id": agent_id, "is_process_alive": True},
        )

    # 2. Immutable already completed check
    if current_agent_status in {"COMPLETE", "SUCCEEDED"} and extracted_verdict in {
        Verdict.PASS.value,
        Verdict.PARTIAL.value,
        Verdict.PASS_REPORT_PRESENT.value,
    }:
        return SafeToResumeDecision(
            outcome=SafeToResumeOutcome.IMMUTABLE_COMPLETED,
            can_resume=False,
            requires_blind_restart=False,
            reason=f"Agent '{agent_id}' already completed with verified verdict '{extracted_verdict}'. Phase is immutable.",
            next_safe_action="Proceed to subsequent DAG stage or result packaging.",
            details={"agent_id": agent_id, "verdict": extracted_verdict},
        )

    # 3. Dirty agent worktree check
    if not is_worktree_clean or uncommitted_files:
        blockers = [
            f"Worktree for '{agent_id}' contains {len(uncommitted_files)} uncommitted file modifications."
        ]
        return SafeToResumeDecision(
            outcome=SafeToResumeOutcome.BLOCKED_RECOVERY_REVIEW,
            can_resume=False,
            requires_blind_restart=False,
            reason=(
                f"Agent '{agent_id}' left uncommitted changes in its worktree upon recovery. "
                f"Preserved for forensics under Local Dirty-Root Rule."
            ),
            blockers=blockers,
            next_safe_action=f"Conduct forensic review of worktree modifications for agent '{agent_id}'.",
            details={
                "agent_id": agent_id,
                "uncommitted_files": uncommitted_files,
                "verdict_impact": "UNCOMMITTED_CHANGES_ON_RECOVERY",
            },
        )

    # 4. Review required marker check
    if extracted_verdict == Verdict.DONE_REVIEW_REQUIRED.value:
        return SafeToResumeDecision(
            outcome=SafeToResumeOutcome.BLOCKED_RECOVERY_REVIEW,
            can_resume=False,
            requires_blind_restart=False,
            reason=f"Agent '{agent_id}' produced deliverables with DONE_REVIEW_REQUIRED marker.",
            blockers=[f"Agent '{agent_id}' deliverables mandate human review before downstream use."],
            next_safe_action=f"Human review required for deliverable report of agent '{agent_id}'.",
            details={"agent_id": agent_id, "verdict": extracted_verdict},
        )

    # 5. Dead process with valid complete report on disk
    if has_report and report_size_bytes > 0:
        if extracted_verdict in {
            Verdict.PASS.value,
            Verdict.PARTIAL.value,
            Verdict.PASS_REPORT_PRESENT.value,
        }:
            return SafeToResumeDecision(
                outcome=SafeToResumeOutcome.RECONCILE_OUTPUTS,
                can_resume=False,
                requires_blind_restart=False,
                reason=(
                    f"Agent '{agent_id}' process terminated, but valid deliverable report "
                    f"({report_size_bytes} bytes) exists with verdict '{extracted_verdict}'."
                ),
                next_safe_action=f"Reconcile agent '{agent_id}' to COMPLETE without re-executing.",
                details={"agent_id": agent_id, "verdict": extracted_verdict, "size_bytes": report_size_bytes},
            )
        elif extracted_verdict == Verdict.BLOCKED.value:
            return SafeToResumeDecision(
                outcome=SafeToResumeOutcome.BLOCKED_RECOVERY_REVIEW,
                can_resume=False,
                requires_blind_restart=False,
                reason=f"Agent '{agent_id}' produced deliverable report with BLOCKED verdict.",
                blockers=[f"Agent '{agent_id}' reported BLOCKED state."],
                next_safe_action="Inspect blocker cause in deliverable report.",
                details={"agent_id": agent_id, "verdict": extracted_verdict},
            )

    # 6. Dead process with missing or 0-byte deliverables -> cannot blindly restart!
    return SafeToResumeDecision(
        outcome=SafeToResumeOutcome.CANNOT_RESUME_INTERRUPTED,
        can_resume=False,
        requires_blind_restart=False,
        reason=(
            f"Agent '{agent_id}' process terminated without generating required deliverable report. "
            f"Blind restart is prohibited. Execution marked INTERRUPTED / FAILED."
        ),
        blockers=[f"Missing deliverable report for agent '{agent_id}'."],
        next_safe_action="Initiate a fresh, idempotent job attempt with a new run ID and dedicated attempt logs.",
        details={"agent_id": agent_id, "has_report": has_report, "report_size_bytes": report_size_bytes},
    )


def evaluate_run_safe_to_resume(
    run_id: str,
    primary_repo_clean: bool,
    agent_decisions: List[SafeToResumeDecision],
    current_run_status: Optional[str] = None,
    primary_dirty_files: Optional[List[str]] = None,
) -> SafeToResumeDecision:
    """Evaluates whether an interrupted run as a whole can be safely resumed or finalized."""
    primary_dirty_files = primary_dirty_files or []

    # 1. Primary checkout dirty check
    if not primary_repo_clean or primary_dirty_files:
        blockers = [
            f"Primary checkout has {len(primary_dirty_files)} uncommitted human files: {', '.join(primary_dirty_files[:3])}"
        ]
        return SafeToResumeDecision(
            outcome=SafeToResumeOutcome.BLOCKED_DIRTY_ROOT,
            can_resume=False,
            requires_blind_restart=False,
            reason=f"DIRTY_ROOT_BLOCKS_RECOVERY: Uncommitted changes in primary checkout block recovery of run '{run_id}'.",
            blockers=blockers,
            next_safe_action="Human operator must resolve or commit uncommitted changes in primary checkout.",
            details={"run_id": run_id, "primary_dirty_files": primary_dirty_files},
        )

    # 2. Check agent decisions
    has_surviving_workers = any(
        d.outcome == SafeToResumeOutcome.RESUME_SUPERVISION for d in agent_decisions
    )
    has_review_blockers = any(
        d.outcome == SafeToResumeOutcome.BLOCKED_RECOVERY_REVIEW for d in agent_decisions
    )
    has_missing_deliverables = any(
        d.outcome == SafeToResumeOutcome.CANNOT_RESUME_INTERRUPTED for d in agent_decisions
    )
    all_completed = all(
        d.outcome in {SafeToResumeOutcome.IMMUTABLE_COMPLETED, SafeToResumeOutcome.RECONCILE_OUTPUTS}
        for d in agent_decisions
    ) if agent_decisions else False

    if has_surviving_workers:
        surviving_count = sum(1 for d in agent_decisions if d.outcome == SafeToResumeOutcome.RESUME_SUPERVISION)
        return SafeToResumeDecision(
            outcome=SafeToResumeOutcome.RESUME_SUPERVISION,
            can_resume=True,
            requires_blind_restart=False,
            reason=f"Run '{run_id}' has {surviving_count} active surviving worker process(es). Resuming live supervision.",
            next_safe_action=f"Reconnect supervisor monitoring loop for run '{run_id}'.",
            details={"run_id": run_id, "surviving_workers": surviving_count},
        )

    if has_review_blockers:
        blockers = []
        for d in agent_decisions:
            blockers.extend(d.blockers)
        return SafeToResumeDecision(
            outcome=SafeToResumeOutcome.BLOCKED_RECOVERY_REVIEW,
            can_resume=False,
            requires_blind_restart=False,
            reason=f"Run '{run_id}' requires recovery review due to agent uncommitted changes or review-required verdicts.",
            blockers=blockers,
            next_safe_action="Perform recovery review of agent artifacts before proceeding.",
            details={"run_id": run_id},
        )

    if all_completed:
        return SafeToResumeDecision(
            outcome=SafeToResumeOutcome.RECONCILE_OUTPUTS,
            can_resume=False,
            requires_blind_restart=False,
            reason=f"All agents in run '{run_id}' have completed with valid on-disk deliverables.",
            next_safe_action=f"Seal run '{run_id}' results and generate dual summaries.",
            details={"run_id": run_id},
        )

    if has_missing_deliverables:
        blockers = []
        for d in agent_decisions:
            blockers.extend(d.blockers)
        return SafeToResumeDecision(
            outcome=SafeToResumeOutcome.CANNOT_RESUME_INTERRUPTED,
            can_resume=False,
            requires_blind_restart=False,
            reason=(
                f"Run '{run_id}' was interrupted and one or more agents died without deliverables. "
                f"Blind restart prohibited. Marked INTERRUPTED."
            ),
            blockers=blockers,
            next_safe_action="Submit a fresh, idempotent job retry attempt.",
            details={"run_id": run_id},
        )

    # Empty run or default
    return SafeToResumeDecision(
        outcome=SafeToResumeOutcome.BLOCKED_RECOVERY_REVIEW,
        can_resume=False,
        requires_blind_restart=False,
        reason=f"Run '{run_id}' state is indeterminate; requires recovery review.",
        next_safe_action="Inspect run record and DAG stage state.",
        details={"run_id": run_id},
    )

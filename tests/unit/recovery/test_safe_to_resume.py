"""Unit tests for SACL V1 Safe-To-Resume Decision Engine and Blind Restart Prohibitions."""

from __future__ import annotations

import pytest

from sacl.contracts.invariants import Verdict
from sacl.recovery.safe_to_resume import (
    SafeToResumeDecision,
    SafeToResumeOutcome,
    assert_no_blind_restart,
    evaluate_agent_safe_to_resume,
    evaluate_run_safe_to_resume,
)


def test_assert_no_blind_restart_enforced() -> None:
    """Verifies that requires_blind_restart == True raises a RuntimeError."""
    safe_dec = SafeToResumeDecision(
        outcome=SafeToResumeOutcome.RESUME_SUPERVISION,
        can_resume=True,
        reason="Process alive",
        requires_blind_restart=False,
    )
    assert_no_blind_restart(safe_dec)

    violating_dec = SafeToResumeDecision(
        outcome=SafeToResumeOutcome.RESUME_SUPERVISION,
        can_resume=True,
        reason="Blind restart attempted",
        requires_blind_restart=True,
    )
    with pytest.raises(RuntimeError) as exc:
        assert_no_blind_restart(violating_dec)
    assert "CRITICAL INVARIANT VIOLATION: Blind restart requested" in str(exc.value)


def test_agent_eval_surviving_worker_resumes_supervision() -> None:
    """Worker process still alive and valid -> RESUME_SUPERVISION."""
    dec = evaluate_agent_safe_to_resume(
        agent_id="AG-BOOTSTRAP",
        is_process_alive=True,
        is_process_valid=True,
        has_report=False,
        report_size_bytes=0,
        is_worktree_clean=True,
    )
    assert dec.outcome == SafeToResumeOutcome.RESUME_SUPERVISION
    assert dec.can_resume is True
    assert dec.requires_blind_restart is False
    assert "reconnect live supervision" in dec.reason


def test_agent_eval_immutable_completed_phase() -> None:
    """Agent that already completed with PASS is immutable and never rerun."""
    dec = evaluate_agent_safe_to_resume(
        agent_id="AG-SCHEMA",
        is_process_alive=False,
        is_process_valid=False,
        has_report=True,
        report_size_bytes=1000,
        is_worktree_clean=True,
        extracted_verdict=Verdict.PASS.value,
        current_agent_status="COMPLETE",
    )
    assert dec.outcome == SafeToResumeOutcome.IMMUTABLE_COMPLETED
    assert dec.can_resume is False
    assert dec.requires_blind_restart is False
    assert "Phase is immutable" in dec.reason


def test_agent_eval_dirty_worktree_blocks_with_review() -> None:
    """Uncommitted changes in worktree trigger BLOCKED_RECOVERY_REVIEW."""
    dec = evaluate_agent_safe_to_resume(
        agent_id="AG-DIRTY",
        is_process_alive=False,
        is_process_valid=False,
        has_report=True,
        report_size_bytes=1500,
        is_worktree_clean=False,
        uncommitted_files=["src/uncommitted.py"],
    )
    assert dec.outcome == SafeToResumeOutcome.BLOCKED_RECOVERY_REVIEW
    assert dec.can_resume is False
    assert dec.requires_blind_restart is False
    assert "uncommitted changes in its worktree" in dec.reason
    assert len(dec.blockers) > 0


def test_agent_eval_done_review_required_blocks_with_review() -> None:
    """Extracted verdict DONE_REVIEW_REQUIRED triggers BLOCKED_RECOVERY_REVIEW."""
    dec = evaluate_agent_safe_to_resume(
        agent_id="AG-HUMAN",
        is_process_alive=False,
        is_process_valid=False,
        has_report=True,
        report_size_bytes=2000,
        is_worktree_clean=True,
        extracted_verdict=Verdict.DONE_REVIEW_REQUIRED.value,
    )
    assert dec.outcome == SafeToResumeOutcome.BLOCKED_RECOVERY_REVIEW
    assert dec.can_resume is False
    assert dec.requires_blind_restart is False
    assert "DONE_REVIEW_REQUIRED marker" in dec.reason


def test_agent_eval_reconcile_outputs_when_report_passes() -> None:
    """Dead process with complete passing report -> RECONCILE_OUTPUTS."""
    dec = evaluate_agent_safe_to_resume(
        agent_id="AG-DOCS",
        is_process_alive=False,
        is_process_valid=False,
        has_report=True,
        report_size_bytes=3400,
        is_worktree_clean=True,
        extracted_verdict=Verdict.PASS.value,
    )
    assert dec.outcome == SafeToResumeOutcome.RECONCILE_OUTPUTS
    assert dec.can_resume is False
    assert dec.requires_blind_restart is False
    assert "Reconcile agent 'AG-DOCS' to COMPLETE" in dec.next_safe_action


def test_agent_eval_missing_report_cannot_blindly_restart() -> None:
    """Dead process with missing report -> CANNOT_RESUME_INTERRUPTED."""
    dec = evaluate_agent_safe_to_resume(
        agent_id="AG-CRASHED",
        is_process_alive=False,
        is_process_valid=False,
        has_report=False,
        report_size_bytes=0,
        is_worktree_clean=True,
    )
    assert dec.outcome == SafeToResumeOutcome.CANNOT_RESUME_INTERRUPTED
    assert dec.can_resume is False
    assert dec.requires_blind_restart is False
    assert "Blind restart is prohibited" in dec.reason


def test_run_eval_dirty_primary_repo_blocks_dirty_root() -> None:
    """Dirty primary repository halts run immediately."""
    dec = evaluate_run_safe_to_resume(
        run_id="run-001",
        primary_repo_clean=False,
        agent_decisions=[],
        primary_dirty_files=["README.md"],
    )
    assert dec.outcome == SafeToResumeOutcome.BLOCKED_DIRTY_ROOT
    assert dec.can_resume is False
    assert "DIRTY_ROOT_BLOCKS_RECOVERY" in dec.reason


def test_run_eval_surviving_workers_resumes_supervision() -> None:
    """Run with at least one surviving worker -> RESUME_SUPERVISION."""
    agent_dec = SafeToResumeDecision(
        outcome=SafeToResumeOutcome.RESUME_SUPERVISION,
        can_resume=True,
        reason="Worker alive",
    )
    run_dec = evaluate_run_safe_to_resume(
        run_id="run-002",
        primary_repo_clean=True,
        agent_decisions=[agent_dec],
    )
    assert run_dec.outcome == SafeToResumeOutcome.RESUME_SUPERVISION
    assert run_dec.can_resume is True


def test_run_eval_all_reconciled_advances_verification() -> None:
    """Run where all agents completed/reconciled -> RECONCILE_OUTPUTS."""
    d1 = SafeToResumeDecision(outcome=SafeToResumeOutcome.IMMUTABLE_COMPLETED, can_resume=False, reason="ok")
    d2 = SafeToResumeDecision(outcome=SafeToResumeOutcome.RECONCILE_OUTPUTS, can_resume=False, reason="ok")

    run_dec = evaluate_run_safe_to_resume(
        run_id="run-003",
        primary_repo_clean=True,
        agent_decisions=[d1, d2],
    )
    assert run_dec.outcome == SafeToResumeOutcome.RECONCILE_OUTPUTS
    assert run_dec.can_resume is False


def test_run_eval_recovery_review_blockers() -> None:
    """Run with agent review blockers -> BLOCKED_RECOVERY_REVIEW."""
    d1 = SafeToResumeDecision(
        outcome=SafeToResumeOutcome.BLOCKED_RECOVERY_REVIEW,
        can_resume=False,
        reason="Review required",
        blockers=["Uncommitted files in wt"],
    )
    run_dec = evaluate_run_safe_to_resume(
        run_id="run-004",
        primary_repo_clean=True,
        agent_decisions=[d1],
    )
    assert run_dec.outcome == SafeToResumeOutcome.BLOCKED_RECOVERY_REVIEW
    assert run_dec.can_resume is False
    assert len(run_dec.blockers) > 0

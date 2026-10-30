"""Tests for 4-part run status reconciliation hook and verdict extraction."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from sacl.contracts.invariants import Verdict
from sacl.worker.reconciliation_hook import WorkerReconciler


def test_reconciliation_hook_with_primary_pass_marker(tmp_path: Path):
    reconciler = WorkerReconciler()

    rep_p = tmp_path / "AG-COMPAT.md"
    rep_p.write_text("# Report\n\nAGENT_AG_COMPAT_RESULT = PASS\n", encoding="utf-8")

    out_p = tmp_path / "AG-COMPAT.stdout.log"
    out_p.write_text("All tests passed.\n", encoding="utf-8")

    err_p = tmp_path / "AG-COMPAT.stderr.log"
    err_p.write_text("", encoding="utf-8")

    res = reconciler.reconcile(
        run_id="run-001",
        agent_id="AG-COMPAT",
        pid=1234,
        process_name="agy",
        is_active=False,
        exit_code=0,
        persisted_start_time=datetime.now(timezone.utc).isoformat(),
        actual_start_time=datetime.now(timezone.utc),
        persisted_status="RUNNING",
        report_path=rep_p,
        stdout_path=out_p,
        stderr_path=err_p,
        worktree_path=tmp_path,
    )

    assert res.status == "SUCCEEDED"
    assert res.result_verdict == Verdict.PASS.value
    assert res.reconciliation.required_outputs.report_exists is True


def test_reconciliation_hook_legacy_report_present_fallback(tmp_path: Path):
    """Report exists and exit_code == 0, but no explicit regex marker."""
    reconciler = WorkerReconciler()

    rep_p = tmp_path / "AG-ARCH.md"
    rep_p.write_text(
        "# Architecture Documentation\n\nCompleted without formal marker.\n", encoding="utf-8"
    )

    out_p = tmp_path / "AG-ARCH.stdout.log"
    out_p.write_text("Output log content.\n", encoding="utf-8")

    err_p = tmp_path / "AG-ARCH.stderr.log"
    err_p.write_text("", encoding="utf-8")

    res = reconciler.reconcile(
        run_id="run-001",
        agent_id="AG-ARCH",
        pid=1234,
        process_name="agy",
        is_active=False,
        exit_code=0,
        persisted_start_time=datetime.now(timezone.utc).isoformat(),
        actual_start_time=datetime.now(timezone.utc),
        persisted_status="RUNNING",
        report_path=rep_p,
        stdout_path=out_p,
        stderr_path=err_p,
        worktree_path=tmp_path,
    )

    assert res.status == "SUCCEEDED"
    assert res.result_verdict == Verdict.PASS_REPORT_PRESENT.value


def test_reconciliation_hook_exit_code_zero_alone_insufficient(tmp_path: Path):
    """Exit code is 0, but deliverable report is missing on disk. Must NOT pass!"""
    reconciler = WorkerReconciler()

    rep_p = tmp_path / "MISSING.md"  # Does not exist!
    out_p = tmp_path / "out.log"
    out_p.write_text("Process finished cleanly with exit code 0", encoding="utf-8")
    err_p = tmp_path / "err.log"
    err_p.write_text("", encoding="utf-8")

    res = reconciler.reconcile(
        run_id="run-001",
        agent_id="AG-MISSING",
        pid=1234,
        process_name="agy",
        is_active=False,
        exit_code=0,  # Exit code 0 alone!
        persisted_start_time=datetime.now(timezone.utc).isoformat(),
        actual_start_time=datetime.now(timezone.utc),
        persisted_status="RUNNING",
        report_path=rep_p,
        stdout_path=out_p,
        stderr_path=err_p,
        worktree_path=tmp_path,
    )

    # Invariant: Exit code alone is NOT sufficient. Missing deliverable evaluates to FAILED!
    assert res.status == "FAILED"
    assert res.result_verdict == Verdict.FAILED.value


def test_reconciliation_hook_pid_recycling_anomaly(tmp_path: Path):
    """Unwhitelisted process image triggers observation verification failure."""
    reconciler = WorkerReconciler()

    rep_p = tmp_path / "AG-COMPAT.md"
    rep_p.write_text("# Report\n\nAGENT_AG_COMPAT_RESULT = PASS\n", encoding="utf-8")
    out_p = tmp_path / "out.log"
    out_p.write_text("log", encoding="utf-8")
    err_p = tmp_path / "err.log"
    err_p.write_text("", encoding="utf-8")

    res = reconciler.reconcile(
        run_id="run-001",
        agent_id="AG-COMPAT",
        pid=1234,
        process_name="unrelated_system_app",  # Non-whitelisted!
        is_active=False,
        exit_code=0,
        persisted_start_time=datetime.now(timezone.utc).isoformat(),
        actual_start_time=datetime.now(timezone.utc),
        persisted_status="RUNNING",
        report_path=rep_p,
        stdout_path=out_p,
        stderr_path=err_p,
        worktree_path=tmp_path,
    )

    assert res.status == "FAILED"
    assert res.result_verdict == Verdict.FAILED.value

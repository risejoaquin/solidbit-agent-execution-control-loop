"""Tests for 4-Dimensional Run Status Reconciler.

Adheres to RESULT_PROTOCOL.md & Decision Baseline #23:
- Invariant: Run success NEVER depends on process exit code alone ($Process.ExitCode == 0).
- PID Recycling defense (3-way check, process whitelist, start-time drift guard).
- 6-Priority Verdict Extraction Ladder.
- Semantic rules: DONE_REVIEW_REQUIRED never means PASS; PASS (Report Present) legacy fallback.
- Output validation against schemas/result.schema.json.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest

from sacl.contracts.exceptions import ContractValidationError
from sacl.contracts.invariants import Verdict
from sacl.contracts.models import ReconciledResult
from sacl.contracts.schema_validator import SchemaValidator
from sacl.results.reconciler import ResultReconciler


@pytest.fixture
def reconciler(schema_validator: SchemaValidator) -> ResultReconciler:
    return ResultReconciler(validator=schema_validator)


@pytest.fixture
def mock_run_dir(tmp_path: Path) -> Path:
    run_dir = tmp_path / "run_test"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "reports").mkdir(exist_ok=True)
    (run_dir / "logs").mkdir(exist_ok=True)
    return run_dir


def test_reconcile_priority2_primary_regex_pass(
    reconciler: ResultReconciler, mock_run_dir: Path
) -> None:
    """Priority 2: Deliverable report bottom-up scan extracts primary structured regex marker."""
    report_file = mock_run_dir / "reports" / "AG-TEST.REPORT.md"
    report_file.write_text(
        "# Agent Report\n\nSome task description.\n\nAGENT_TEST_RESULT = PASS\n",
        encoding="utf-8",
    )
    stdout_file = mock_run_dir / "logs" / "AG-TEST.stdout.log"
    stdout_file.write_text("Execution started\nDone\n", encoding="utf-8")
    stderr_file = mock_run_dir / "logs" / "AG-TEST.stderr.log"
    stderr_file.write_text("", encoding="utf-8")

    res = reconciler.reconcile(
        run_id="run-001",
        agent_id="AG-TEST",
        pid=1234,
        process_name="agy",
        is_active=False,
        exit_code=0,
        persisted_start_time="2026-10-07T10:00:00Z",
        actual_start_time=datetime.fromisoformat("2026-10-07T10:00:05+00:00"),
        persisted_status="COMPLETE",
        report_path=report_file,
        stdout_path=stdout_file,
        stderr_path=stderr_file,
        worktree_path=mock_run_dir,
    )

    assert res.result_verdict == "PASS"
    assert res.status == "SUCCEEDED"
    assert res.reconciliation.verdict_extraction.extraction_method == "REGEX_PRIMARY"
    assert res.reconciliation.required_outputs.report_exists is True
    assert res.reconciliation.required_outputs.report_size_bytes > 0


def test_reconcile_exit_code_zero_alone_is_not_success(
    reconciler: ResultReconciler, mock_run_dir: Path
) -> None:
    """INVARIANT: Exit code 0 alone does not prove success if deliverable report is missing."""
    report_file = mock_run_dir / "reports" / "MISSING.REPORT.md"  # Does not exist!
    stdout_file = mock_run_dir / "logs" / "AG-FAIL.stdout.log"
    stdout_file.write_text("Process terminated normally with exit 0", encoding="utf-8")
    stderr_file = mock_run_dir / "logs" / "AG-FAIL.stderr.log"
    stderr_file.write_text("", encoding="utf-8")

    res = reconciler.reconcile(
        run_id="run-001",
        agent_id="AG-FAIL",
        pid=1234,
        process_name="powershell",
        is_active=False,
        exit_code=0,  # Exit code 0, but no report!
        persisted_start_time="2026-10-07T10:00:00Z",
        actual_start_time=datetime.fromisoformat("2026-10-07T10:00:05+00:00"),
        persisted_status="COMPLETE",
        report_path=report_file,
        stdout_path=stdout_file,
        stderr_path=stderr_file,
        worktree_path=mock_run_dir,
    )

    assert res.result_verdict == "FAILED"
    assert res.status == "FAILED"
    assert res.reconciliation.required_outputs.report_exists is False
    assert res.reconciliation.verdict_extraction.extraction_method == "FAILED_NO_EVIDENCE"


def test_reconcile_priority3_header_status_fallback(
    reconciler: ResultReconciler, mock_run_dir: Path
) -> None:
    """Priority 3: Top 25 lines of report scan for markdown status header."""
    report_file = mock_run_dir / "reports" / "AG-HDR.REPORT.md"
    report_file.write_text(
        "# AG-HDR REPORT\n\n**Final Status:** PASS\n\nDetails of the task execution.\n",
        encoding="utf-8",
    )
    stdout_file = mock_run_dir / "logs" / "AG-HDR.stdout.log"
    stdout_file.write_text("Done", encoding="utf-8")
    stderr_file = mock_run_dir / "logs" / "AG-HDR.stderr.log"
    stderr_file.write_text("", encoding="utf-8")

    res = reconciler.reconcile(
        run_id="run-001",
        agent_id="AG-HDR",
        pid=2000,
        process_name="agy",
        is_active=False,
        exit_code=0,
        persisted_start_time="2026-10-07T10:00:00Z",
        actual_start_time=datetime.fromisoformat("2026-10-07T10:00:05+00:00"),
        persisted_status="COMPLETE",
        report_path=report_file,
        stdout_path=stdout_file,
        stderr_path=stderr_file,
        worktree_path=mock_run_dir,
    )

    assert res.result_verdict == "PASS"
    assert res.status == "SUCCEEDED"
    assert res.reconciliation.verdict_extraction.extraction_method == "HEADER_MARKER"


def test_reconcile_priority5_legacy_report_present_fallback(
    reconciler: ResultReconciler, mock_run_dir: Path
) -> None:
    """Priority 5: Report present on disk & size > 0 & exit_code == 0 yields PASS (Report Present)."""
    report_file = mock_run_dir / "reports" / "AG-LEGACY.REPORT.md"
    report_file.write_text(
        "# Generic Report Without Any Status Marker\nTask finished.\n",
        encoding="utf-8",
    )
    stdout_file = mock_run_dir / "logs" / "AG-LEGACY.stdout.log"
    stdout_file.write_text("Clean exit", encoding="utf-8")
    stderr_file = mock_run_dir / "logs" / "AG-LEGACY.stderr.log"
    stderr_file.write_text("", encoding="utf-8")

    res = reconciler.reconcile(
        run_id="run-001",
        agent_id="AG-LEGACY",
        pid=2001,
        process_name="pwsh",
        is_active=False,
        exit_code=0,
        persisted_start_time="2026-10-07T10:00:00Z",
        actual_start_time=datetime.fromisoformat("2026-10-07T10:00:05+00:00"),
        persisted_status="COMPLETE",
        report_path=report_file,
        stdout_path=stdout_file,
        stderr_path=stderr_file,
        worktree_path=mock_run_dir,
    )

    assert res.result_verdict == "PASS (Report Present)"
    assert res.status == "SUCCEEDED"
    assert res.reconciliation.verdict_extraction.extraction_method == "FALLBACK_REPORT_PRESENT"


def test_reconcile_done_review_required_never_means_pass(
    reconciler: ResultReconciler, mock_run_dir: Path
) -> None:
    """CONSTITUTIONAL INVARIANT: DONE_REVIEW_REQUIRED never means PASS."""
    report_file = mock_run_dir / "reports" / "AG-REV.REPORT.md"
    report_file.write_text(
        "# Agent Report\nAll operations complete.\nFINAL_STATUS = DONE_REVIEW_REQUIRED\n",
        encoding="utf-8",
    )
    stdout_file = mock_run_dir / "logs" / "AG-REV.stdout.log"
    stdout_file.write_text("Done", encoding="utf-8")
    stderr_file = mock_run_dir / "logs" / "AG-REV.stderr.log"
    stderr_file.write_text("", encoding="utf-8")

    res = reconciler.reconcile(
        run_id="run-001",
        agent_id="AG-REV",
        pid=2002,
        process_name="cmd",
        is_active=False,
        exit_code=0,
        persisted_start_time="2026-10-07T10:00:00Z",
        actual_start_time=datetime.fromisoformat("2026-10-07T10:00:05+00:00"),
        persisted_status="COMPLETE",
        report_path=report_file,
        stdout_path=stdout_file,
        stderr_path=stderr_file,
        worktree_path=mock_run_dir,
    )

    assert res.result_verdict == "DONE_REVIEW_REQUIRED"
    assert res.result_verdict != "PASS"
    assert res.status == "COMPLETE"  # Not SUCCEEDED


def test_reconcile_pid_recycling_defense_fails_closed(
    reconciler: ResultReconciler, mock_run_dir: Path
) -> None:
    """Process observation fails when start-time drift exceeds 300 seconds (PID recycling guard)."""
    report_file = mock_run_dir / "reports" / "AG-RECYCLE.REPORT.md"
    report_file.write_text("AGENT_RECYCLE_RESULT = PASS\n", encoding="utf-8")
    stdout_file = mock_run_dir / "logs" / "AG-RECYCLE.stdout.log"
    stdout_file.write_text("Done", encoding="utf-8")
    stderr_file = mock_run_dir / "logs" / "AG-RECYCLE.stderr.log"
    stderr_file.write_text("", encoding="utf-8")

    # Persisted start time was 1 hour ago, but OS process started 1 minute ago -> drift > 300s!
    persisted_start = datetime.now(timezone.utc) - timedelta(hours=1)
    actual_start = datetime.now(timezone.utc) - timedelta(minutes=1)

    res = reconciler.reconcile(
        run_id="run-001",
        agent_id="AG-RECYCLE",
        pid=9999,
        process_name="agy",
        is_active=False,
        exit_code=0,
        persisted_start_time=persisted_start,
        actual_start_time=actual_start,
        persisted_status="COMPLETE",
        report_path=report_file,
        stdout_path=stdout_file,
        stderr_path=stderr_file,
        worktree_path=mock_run_dir,
    )

    # PID recycling detected causes overall reconciliation failure
    assert res.result_verdict == "FAILED"
    assert res.status == "FAILED"
    assert "PID recycling detected" in res.error_message


def test_reconcile_unwhitelisted_process_image_rejected(
    reconciler: ResultReconciler, mock_run_dir: Path
) -> None:
    """Process image not in whitelist (agy, powershell, pwsh, cmd, node, conhost) fails observation."""
    report_file = mock_run_dir / "reports" / "AG-BADIMG.REPORT.md"
    report_file.write_text("AGENT_BADIMG_RESULT = PASS\n", encoding="utf-8")
    stdout_file = mock_run_dir / "logs" / "AG-BADIMG.stdout.log"
    stdout_file.write_text("", encoding="utf-8")
    stderr_file = mock_run_dir / "logs" / "AG-BADIMG.stderr.log"
    stderr_file.write_text("", encoding="utf-8")

    res = reconciler.reconcile(
        run_id="run-001",
        agent_id="AG-BADIMG",
        pid=5555,
        process_name="unauthorized_binary.exe",
        is_active=False,
        exit_code=0,
        persisted_start_time="2026-10-07T10:00:00Z",
        actual_start_time=datetime.now(timezone.utc),
        persisted_status="COMPLETE",
        report_path=report_file,
        stdout_path=stdout_file,
        stderr_path=stderr_file,
        worktree_path=mock_run_dir,
    )

    assert res.result_verdict == "FAILED"
    assert "not in allowed whitelist" in res.error_message

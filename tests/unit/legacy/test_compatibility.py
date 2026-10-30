"""Unit tests for SACL V1 Legacy Compatibility Utilities."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from sacl.contracts.invariants import Verdict
from sacl.legacy.compatibility import (
    check_dirty_root,
    extract_legacy_result,
    generate_governance_header,
    verify_legacy_process,
)
from sacl.worker.process import IProcessInspector


class MockInspector(IProcessInspector):
    def __init__(self, running=True, name="agy.exe", start_time=None):
        self._running = running
        self._name = name
        self._start_time = start_time or datetime.now(timezone.utc)

    def is_process_running(self, pid: int) -> bool:
        return self._running

    def get_process_name(self, pid: int):
        return self._name

    def get_process_start_time(self, pid: int):
        return self._start_time

    def terminate_process(self, pid: int, force: bool = False) -> bool:
        return True


def test_extract_legacy_result_report_bottom_marker():
    report = """
    # Agent Report
    Some content
    AGENT_A_RESULT = BLOCKED
    More work done...
    AGENT_A_RESULT = PASS
    """
    verdict, reason = extract_legacy_result(report_content=report, report_exists=True, exit_code=0)
    assert verdict == "PASS"
    assert reason == "REPORT_REGEX_MARKER"


def test_extract_legacy_result_wave3_marker():
    report = """
    # Report
    WAVE3_RESULT=PASS
    """
    verdict, reason = extract_legacy_result(report_content=report, report_exists=True, exit_code=0)
    assert verdict == "PASS"
    assert reason == "REPORT_REGEX_MARKER"


def test_extract_legacy_result_log_marker_fallback():
    logs = "Log line 1\nLog line 2\nRESULT = PARTIAL\n"
    verdict, reason = extract_legacy_result(
        report_content="", log_content=logs, report_exists=False
    )
    assert verdict == "PARTIAL"
    assert reason == "LOG_REGEX_MARKER"


def test_extract_legacy_result_report_present_fallback():
    report = "# Some Deliverable\nNo explicit regex marker here."
    verdict, reason = extract_legacy_result(report_content=report, report_exists=True, exit_code=0)
    assert verdict == Verdict.PASS_REPORT_PRESENT.value
    assert reason == "REPORT_PRESENT_FALLBACK"


def test_extract_legacy_result_process_failed():
    verdict, reason = extract_legacy_result(report_content="", report_exists=False, exit_code=42)
    assert verdict == Verdict.FAILED.value
    assert "PROCESS_EXIT_CODE_42" in reason


def test_extract_legacy_result_no_evidence():
    verdict, reason = extract_legacy_result(report_content="", report_exists=False, exit_code=None)
    assert verdict == Verdict.BLOCKED.value
    assert reason == "NO_EVIDENCE_FOUND"


def test_generate_governance_header():
    wt = "C:/path/to/worktree"
    header = generate_governance_header(
        worktree_path=wt,
        branch="feat/test",
        head_sha="abcdef123",
    )
    assert "GOVERNED_EXECUTION=TRUE" in header
    assert "MERGE=NOT_AUTHORIZED" in header
    assert "DEPLOY=NOT_AUTHORIZED" in header
    assert "DESTRUCTIVE_DB=NOT_AUTHORIZED" in header
    assert f"WORKTREE={wt}" in header
    assert "BRANCH=feat/test" in header
    assert "HEAD=abcdef123" in header


def test_check_dirty_root_clean(tmp_path):
    is_dirty, msg = check_dirty_root(tmp_path)
    assert not is_dirty


def test_check_dirty_root_with_git(tmp_path):
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout=" M src/file.py\n?? untracked.txt\n")
        is_dirty, output = check_dirty_root(tmp_path)
        assert is_dirty
        assert "M src/file.py" in output


def test_verify_legacy_process():
    now = datetime.now(timezone.utc)
    ins = MockInspector(running=True, name="powershell.exe", start_time=now)
    is_running, reason = verify_legacy_process(
        pid=1234, started_at_iso=now.isoformat(), inspector=ins
    )
    assert is_running
    assert reason == "VERIFIED_RUNNING"


def test_verify_legacy_process_recycled_name():
    now = datetime.now(timezone.utc)
    ins = MockInspector(running=True, name="calc.exe", start_time=now)
    is_running, reason = verify_legacy_process(
        pid=1234, started_at_iso=now.isoformat(), inspector=ins
    )
    assert not is_running
    assert "MISMATCH" in reason

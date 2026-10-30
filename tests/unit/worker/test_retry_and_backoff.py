"""Tests for transient vs permanent failure classification, exponential backoff, and distinct attempt logs."""

from __future__ import annotations

from pathlib import Path

from sacl.contracts.exceptions import (
    CollisionDetectedError,
    DirtyRootError,
    HardDenyViolation,
    PolicyDeniedError,
)
from sacl.contracts.invariants import Verdict
from sacl.worker.retry import (
    FailureClassification,
    calculate_backoff_delay,
    classify_failure,
    get_attempt_log_paths,
)


def test_classify_transient_sqlite_contention():
    is_ret, code, max_ret = classify_failure(
        error="sqlite3.OperationalError: database is locked (SQLITE_BUSY)"
    )
    assert is_ret is True
    assert code == FailureClassification.TRANSIENT_SQLITE_BUSY
    assert max_ret == 2


def test_classify_transient_worktree_lock():
    is_ret, code, max_ret = classify_failure(
        error="fatal: Unable to create '.git/index.lock': File exists."
    )
    assert is_ret is True
    assert code == FailureClassification.TRANSIENT_WORKTREE_LOCK
    assert max_ret == 2


def test_classify_transient_bootstrap_crash_before_modifications():
    is_ret, code, max_ret = classify_failure(
        error="Bootstrap launcher spawn failed",
        exit_code=1,
        files_modified_count=0,
    )
    assert is_ret is True
    assert code == FailureClassification.TRANSIENT_PROCESS_CRASH_EARLY
    assert max_ret == 1


def test_classify_permanent_hard_deny_violation():
    err = HardDenyViolation(action="github_merge")
    is_ret, code, max_ret = classify_failure(error=err)
    assert is_ret is False
    assert code == FailureClassification.PERMANENT_POLICY_VIOLATION
    assert max_ret == 0


def test_classify_permanent_policy_denied():
    err = PolicyDeniedError(action="push", layer="project_policy", reason="Denied")
    is_ret, code, max_ret = classify_failure(error=err)
    assert is_ret is False
    assert code == FailureClassification.PERMANENT_POLICY_VIOLATION
    assert max_ret == 0


def test_classify_permanent_dirty_root():
    err = DirtyRootError(target_path="/repo", dirty_files=["file.txt"])
    is_ret, code, max_ret = classify_failure(error=err)
    assert is_ret is False
    assert code == FailureClassification.PERMANENT_DIRTY_ROOT
    assert max_ret == 0


def test_classify_permanent_explicit_blocked_marker():
    is_ret, code, max_ret = classify_failure(verdict=Verdict.BLOCKED.value)
    assert is_ret is False
    assert code == FailureClassification.PERMANENT_EXPLICIT_BLOCKED
    assert max_ret == 0


def test_classify_permanent_collision_conflict():
    err = CollisionDetectedError(run_id="run-1", colliding_files=["a.py"])
    is_ret, code, max_ret = classify_failure(error=err)
    assert is_ret is False
    assert code == FailureClassification.PERMANENT_COLLISION_CONFLICT
    assert max_ret == 0


def test_classify_permanent_stopped_by_user():
    is_ret, code, max_ret = classify_failure(verdict=Verdict.STOPPED_BY_USER.value)
    assert is_ret is False
    assert code == FailureClassification.PERMANENT_STOPPED_BY_USER
    assert max_ret == 0


def test_exponential_backoff_calculation():
    # Attempt 1 -> 0s
    assert calculate_backoff_delay(attempt=1, base_seconds=2.0) == 0.0

    # Attempt 2 -> base * 2^0 = 2.0s
    assert calculate_backoff_delay(attempt=2, base_seconds=2.0) == 2.0

    # Attempt 3 -> base * 2^1 = 4.0s
    assert calculate_backoff_delay(attempt=3, base_seconds=2.0) == 4.0

    # Attempt 4 -> base * 2^2 = 8.0s
    assert calculate_backoff_delay(attempt=4, base_seconds=2.0) == 8.0

    # Max clamp
    assert calculate_backoff_delay(attempt=10, base_seconds=2.0, max_seconds=30.0) == 30.0


def test_distinct_attempt_log_paths(tmp_path: Path):
    base_stdout = tmp_path / "AG-TEST.stdout.log"
    base_stderr = tmp_path / "AG-TEST.stderr.log"
    base_report = tmp_path / "AG-TEST.md"

    # Attempt 1 returns original paths
    out1, err1, rep1 = get_attempt_log_paths(
        base_stdout, base_stderr, base_report, attempt_number=1
    )
    assert out1 == base_stdout
    assert err1 == base_stderr
    assert rep1 == base_report

    # Attempt 2 returns distinct paths with .attempt-2
    out2, err2, rep2 = get_attempt_log_paths(
        base_stdout, base_stderr, base_report, attempt_number=2
    )
    assert out2.name == "AG-TEST.attempt-2.stdout.log"
    assert err2.name == "AG-TEST.attempt-2.stderr.log"
    assert rep2.name == "AG-TEST.attempt-2.md"

    # Attempt 3 returns distinct paths with .attempt-3
    out3, err3, rep3 = get_attempt_log_paths(
        base_stdout, base_stderr, base_report, attempt_number=3
    )
    assert out3.name == "AG-TEST.attempt-3.stdout.log"
    assert err3.name == "AG-TEST.attempt-3.stderr.log"
    assert rep3.name == "AG-TEST.attempt-3.md"

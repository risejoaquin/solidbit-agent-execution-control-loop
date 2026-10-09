"""SACL V1 Worker Retry, Classification, and Backoff Policy.

Codifies RETRY_AND_TIMEOUT_POLICY.md §5:
- Distinguishes between transient/recoverable failures and permanent errors.
- Enforces zero retries for policy violations, dirty-root breaches, BLOCKED markers, and collisions.
- Preserves immutable per-attempt log paths and worktree isolation.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

from sacl.contracts.exceptions import (
    ApprovalRequiredError,
    CollisionDetectedError,
    DirtyRootError,
    HardDenyViolation,
    PolicyDeniedError,
    QuarantineError,
)
from sacl.contracts.invariants import Verdict


class FailureClassification:
    """Failure classification constants."""

    TRANSIENT_SQLITE_BUSY = "TRANSIENT_SQLITE_BUSY"
    TRANSIENT_WORKTREE_LOCK = "TRANSIENT_WORKTREE_LOCK"
    TRANSIENT_PROCESS_CRASH_EARLY = "TRANSIENT_PROCESS_CRASH_EARLY"

    PERMANENT_POLICY_VIOLATION = "PERMANENT_POLICY_VIOLATION"
    PERMANENT_DIRTY_ROOT = "PERMANENT_DIRTY_ROOT"
    PERMANENT_NO_DELIVERABLE = "PERMANENT_NO_DELIVERABLE"
    PERMANENT_EXPLICIT_BLOCKED = "PERMANENT_EXPLICIT_BLOCKED"
    PERMANENT_COLLISION_CONFLICT = "PERMANENT_COLLISION_CONFLICT"
    PERMANENT_STOPPED_BY_USER = "PERMANENT_STOPPED_BY_USER"
    PERMANENT_REVIEW_REQUIRED = "PERMANENT_REVIEW_REQUIRED"
    PERMANENT_UNKNOWN_FAILURE = "PERMANENT_UNKNOWN_FAILURE"


def classify_failure(
    error: Optional[Union[Exception, str]] = None,
    verdict: Optional[str] = None,
    exit_code: Optional[int] = None,
    files_modified_count: int = 0,
) -> Tuple[bool, str, int]:
    """Classifies a failure into retryable vs. non-retryable.

    Returns:
        (is_retryable, classification_code, max_allowed_retries)
    """
    error_str = str(error) if error else ""

    # Non-retryable verdicts
    if verdict == Verdict.BLOCKED.value:
        return False, FailureClassification.PERMANENT_EXPLICIT_BLOCKED, 0
    if verdict == Verdict.STOPPED_BY_USER.value:
        return False, FailureClassification.PERMANENT_STOPPED_BY_USER, 0
    if verdict == Verdict.DONE_REVIEW_REQUIRED.value:
        return False, FailureClassification.PERMANENT_REVIEW_REQUIRED, 0

    # Non-retryable constitutional exceptions
    if isinstance(error, (HardDenyViolation, PolicyDeniedError)):
        return False, FailureClassification.PERMANENT_POLICY_VIOLATION, 0
    if isinstance(error, DirtyRootError):
        return False, FailureClassification.PERMANENT_DIRTY_ROOT, 0
    if isinstance(error, CollisionDetectedError):
        return False, FailureClassification.PERMANENT_COLLISION_CONFLICT, 0
    if isinstance(error, (QuarantineError, ApprovalRequiredError)):
        return False, FailureClassification.PERMANENT_POLICY_VIOLATION, 0

    # Check for transient patterns in error message
    err_lower = error_str.lower()
    if "sqlite_busy" in err_lower or "database is locked" in err_lower or "busy_timeout" in err_lower:
        return True, FailureClassification.TRANSIENT_SQLITE_BUSY, 2

    if "index.lock" in err_lower or "worktree lock" in err_lower or "resource temporarily unavailable" in err_lower:
        return True, FailureClassification.TRANSIENT_WORKTREE_LOCK, 2

    # Early crash before modifying files
    if exit_code is not None and exit_code != 0 and files_modified_count == 0:
        if "bootstrap" in err_lower or "spawn" in err_lower or "launcher" in err_lower:
            return True, FailureClassification.TRANSIENT_PROCESS_CRASH_EARLY, 1

    if verdict == Verdict.FAILED.value and "no_evidence_found" in err_lower:
        return False, FailureClassification.PERMANENT_NO_DELIVERABLE, 0

    # Default: non-retryable
    return False, FailureClassification.PERMANENT_UNKNOWN_FAILURE, 0


def calculate_backoff_delay(
    attempt: int,
    base_seconds: float = 2.0,
    max_seconds: float = 60.0,
    factor: float = 2.0,
) -> float:
    """Calculates exponential backoff delay for retry attempts.

    attempt 1: 0.0s
    attempt 2: base_seconds * (factor ** 0) = base_seconds
    attempt 3: base_seconds * (factor ** 1) = base_seconds * factor
    """
    if attempt <= 1:
        return 0.0
    delay = base_seconds * (factor ** (attempt - 2))
    return min(max_seconds, max(0.0, delay))


def _format_attempt_filename(name: str, attempt_number: int) -> str:
    if ".stdout." in name:
        return name.replace(".stdout.", f".attempt-{attempt_number}.stdout.")
    elif ".stderr." in name:
        return name.replace(".stderr.", f".attempt-{attempt_number}.stderr.")
    p = Path(name)
    return f"{p.stem}.attempt-{attempt_number}{p.suffix}"


def get_attempt_log_paths(
    base_stdout_path: Path,
    base_stderr_path: Path,
    base_report_path: Path,
    attempt_number: int,
) -> Tuple[Path, Path, Path]:
    """Generates distinct file paths for an execution attempt to preserve logs.

    Attempt 1: base paths (e.g. <agent>.stdout.log)
    Attempt N (N > 1): <agent>.attempt-N.stdout.log
    """
    if attempt_number <= 1:
        return base_stdout_path, base_stderr_path, base_report_path

    out_name = _format_attempt_filename(base_stdout_path.name, attempt_number)
    err_name = _format_attempt_filename(base_stderr_path.name, attempt_number)
    rep_name = f"{base_report_path.stem}.attempt-{attempt_number}{base_report_path.suffix}"

    return (
        base_stdout_path.parent / out_name,
        base_stderr_path.parent / err_name,
        base_report_path.parent / rep_name,
    )

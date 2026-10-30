"""Unit tests for SACL V1 structured diagnostic error recording subsystem."""

import sqlite3

import pytest

from sacl.observability.audit import AuditEventEmitter
from sacl.observability.correlation import correlation_scope
from sacl.observability.errors import (
    ALL_ERROR_CATEGORIES,
    ALL_ERROR_SEVERITIES,
    ErrorCategory,
    ErrorRecorder,
)
from sacl.observability.events import ERROR_RECORDED


def test_error_categories_and_severities():
    """Verifies that all error categories and severities conform to 001_init.sql."""
    assert ErrorCategory.INFRASTRUCTURE.value in ALL_ERROR_CATEGORIES
    assert ErrorCategory.POLICY.value in ALL_ERROR_CATEGORIES
    assert ErrorCategory.VALIDATION.value in ALL_ERROR_CATEGORIES
    assert ErrorCategory.EXECUTION.value in ALL_ERROR_CATEGORIES
    assert ErrorCategory.TIMEOUT.value in ALL_ERROR_CATEGORIES
    assert ErrorCategory.COLLISION.value in ALL_ERROR_CATEGORIES
    assert ErrorCategory.TRANSPORT.value in ALL_ERROR_CATEGORIES
    assert ErrorCategory.APPROVAL.value in ALL_ERROR_CATEGORIES
    assert ErrorCategory.RECOVERY.value in ALL_ERROR_CATEGORIES

    assert "WARN" in ALL_ERROR_SEVERITIES
    assert "ERROR" in ALL_ERROR_SEVERITIES
    assert "FATAL" in ALL_ERROR_SEVERITIES


def test_record_error_with_correlation_and_audit(sqlite_temp_db: sqlite3.Connection):
    """Verifies recording structured error, extracting stack trace, and emitting audit event."""
    audit_emitter = AuditEventEmitter(sqlite_temp_db)
    recorder = ErrorRecorder(sqlite_temp_db, audit_emitter=audit_emitter)

    try:
        raise ValueError("Simulated invalid configuration parameter")
    except ValueError as exc:
        with correlation_scope(job_id="job-err", run_id="run-err", agent_id="AG-POLICY"):
            err_id = recorder.record_error(
                error_code="INVALID_CONFIG_VALUE",
                category=ErrorCategory.POLICY.value,
                severity="ERROR",
                message=str(exc),
                exception=exc,
                context={"param": "max_parallel", "val": -1},
            )

    assert err_id > 0

    # Query back error record
    errors = recorder.get_errors_for_run("run-err")
    assert len(errors) == 1
    err = errors[0]
    assert err.error_id == err_id
    assert err.error_code == "INVALID_CONFIG_VALUE"
    assert err.category == ErrorCategory.POLICY.value
    assert err.severity == "ERROR"
    assert "Simulated invalid configuration parameter" in err.message
    assert "ValueError" in err.stack_trace
    assert err.context["param"] == "max_parallel"
    assert err.agent_id == "AG-POLICY"

    # Verify audit event was emitted
    audit_evs = audit_emitter.query_events(run_id="run-err", event_type=ERROR_RECORDED)
    assert len(audit_evs) == 1
    assert audit_evs[0].severity == "ERROR"
    assert audit_evs[0].payload["error_code"] == "INVALID_CONFIG_VALUE"


def test_invalid_category_or_severity_fails_closed(sqlite_temp_db: sqlite3.Connection):
    """Verifies fail-closed behavior on invalid category or severity."""
    recorder = ErrorRecorder(sqlite_temp_db)

    with pytest.raises(ValueError, match="Invalid category"):
        recorder.record_error(
            error_code="ERR-1",
            category="UNKNOWN_CATEGORY",
            message="Test message",
            severity="ERROR",
        )

    with pytest.raises(ValueError, match="Invalid severity"):
        recorder.record_error(
            error_code="ERR-2",
            category=ErrorCategory.EXECUTION.value,
            message="Test message",
            severity="NOTICE",
        )


def test_get_recent_errors(sqlite_temp_db: sqlite3.Connection):
    """Verifies querying recent errors across multiple runs."""
    recorder = ErrorRecorder(sqlite_temp_db)

    recorder.record_error(
        error_code="E1",
        category=ErrorCategory.TIMEOUT.value,
        message="Agent timeout",
        severity="WARN",
        run_id="run-1",
    )
    recorder.record_error(
        error_code="E2",
        category=ErrorCategory.COLLISION.value,
        message="File collision",
        severity="ERROR",
        run_id="run-2",
    )

    recent = recorder.get_recent_errors(limit=10)
    assert len(recent) == 2
    codes = [e.error_code for e in recent]
    assert "E1" in codes
    assert "E2" in codes


def test_record_all_error_categories(sqlite_temp_db: sqlite3.Connection):
    """Verifies that every error category can be recorded into the SQLite errors table."""
    recorder = ErrorRecorder(sqlite_temp_db)

    for cat in ALL_ERROR_CATEGORIES:
        err_id = recorder.record_error(
            error_code=f"ERR_{cat}",
            category=cat,
            severity="WARN",
            message=f"Test error for category {cat}",
            run_id="run-all-cat",
        )
        assert err_id > 0

    recorded = recorder.get_errors_for_run("run-all-cat")
    assert len(recorded) == len(ALL_ERROR_CATEGORIES)

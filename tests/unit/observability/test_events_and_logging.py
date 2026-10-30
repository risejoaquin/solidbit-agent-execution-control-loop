"""Unit tests for SACL V1 event taxonomy, create_audit_event, and structured logging."""

import json
import logging
from pathlib import Path

import pytest

from sacl.observability.correlation import correlation_scope
from sacl.observability.events import (
    ALL_SEVERITIES,
    APPROVAL_REQUESTED,
    GATE_HALTED,
    HEARTBEAT_RECORDED,
    PROCESS_SPAWNED,
    RUN_COMPLETED,
    RUN_FAILED,
    Severity,
    create_audit_event,
)
from sacl.observability.logging import (
    JsonLogFormatter,
    StructuredLogger,
    TextLogFormatter,
    create_file_logger,
    get_logger,
)


def test_event_taxonomy_and_severities():
    """Verifies that all standard event types and severity levels exist and validate."""
    assert Severity.INFO.value in ALL_SEVERITIES
    assert Severity.ERROR.value in ALL_SEVERITIES
    assert Severity.WARN.value in ALL_SEVERITIES
    assert Severity.FATAL.value in ALL_SEVERITIES
    assert Severity.DEBUG.value in ALL_SEVERITIES

    # Check key taxonomy constants
    assert PROCESS_SPAWNED == "PROCESS_SPAWNED"
    assert RUN_COMPLETED == "RUN_COMPLETED"
    assert RUN_FAILED == "RUN_FAILED"
    assert APPROVAL_REQUESTED == "APPROVAL_REQUESTED"
    assert GATE_HALTED == "GATE_HALTED"
    assert HEARTBEAT_RECORDED == "HEARTBEAT_RECORDED"


def test_create_audit_event_auto_enrichment():
    """Verifies automatic enrichment of audit events with correlation context."""
    with correlation_scope(job_id="job-42", run_id="run-42", agent_id="AG-SCHEMA"):
        event = create_audit_event(
            event_type=PROCESS_SPAWNED,
            severity="INFO",
            payload={"pid": 1234, "command": "agy.exe"},
        )

        assert event.event_type == PROCESS_SPAWNED
        assert event.severity == "INFO"
        assert event.job_id == "job-42"
        assert event.run_id == "run-42"
        assert event.agent_id == "AG-SCHEMA"
        assert event.payload["pid"] == 1234
        assert "trace_id" in event.payload
        assert event.created_at is not None


def test_create_audit_event_invalid_severity():
    """Verifies fail-closed behavior on unrecognized event severity."""
    with pytest.raises(ValueError, match="Invalid severity"):
        create_audit_event(
            event_type=RUN_FAILED,
            severity="SUPER_CRITICAL",
        )


def test_json_log_formatter():
    """Verifies JsonLogFormatter produces valid single-line JSON with correlation fields."""
    formatter = JsonLogFormatter()
    logger = logging.getLogger("test_json")

    with correlation_scope(run_id="run-test", agent_id="AG-TEST"):
        record = logger.makeRecord(
            name="test_logger",
            level=logging.INFO,
            fn="test_file.py",
            lno=10,
            msg="Agent execution started",
            args=(),
            exc_info=None,
        )
        record.custom_metric = 42

        formatted = formatter.format(record)
        data = json.loads(formatted)

        assert data["level"] == "INFO"
        assert data["logger"] == "test_logger"
        assert data["message"] == "Agent execution started"
        assert data["run_id"] == "run-test"
        assert data["agent_id"] == "AG-TEST"
        assert "trace_id" in data
        assert data["extra"]["custom_metric"] == 42


def test_text_log_formatter():
    """Verifies TextLogFormatter produces readable log lines with correlation tags."""
    formatter = TextLogFormatter()
    logger = logging.getLogger("test_text")

    with correlation_scope(run_id="run-abc", agent_id="AG-ARCH"):
        record = logger.makeRecord(
            name="test_logger",
            level=logging.WARNING,
            fn="test_file.py",
            lno=20,
            msg="High memory usage warning",
            args=(),
            exc_info=None,
        )
        formatted = formatter.format(record)

        assert "[WARN ]" in formatted or "[WARNING]" in formatted
        assert "run=run-abc" in formatted
        assert "agent=AG-ARCH" in formatted
        assert "High memory usage warning" in formatted


def test_structured_logger_audit_sink_forwarding():
    """Verifies that StructuredLogger automatically forwards critical logs to audit sink."""
    captured_events = []

    def mock_sink(**kwargs):
        captured_events.append(kwargs)

    raw_logger = logging.getLogger("test_forwarding")
    structured = StructuredLogger(raw_logger, audit_sink=mock_sink)

    with correlation_scope(run_id="run-forward", agent_id="AG-SEC"):
        # INFO logs should not forward by default
        structured.info("Normal info message")
        assert len(captured_events) == 0

        # WARN logs should forward automatically
        structured.warn("Potential collision detected")
        assert len(captured_events) == 1
        assert captured_events[0]["severity"] == "WARN"
        assert "Potential collision detected" in captured_events[0]["payload"]["message"]

        # Explicit audit=True on info should forward
        structured.info("Milestone reached", audit=True, audit_event_type="MILESTONE_REACHED")
        assert len(captured_events) == 2
        assert captured_events[1]["event_type"] == "MILESTONE_REACHED"


def test_create_file_logger(tmp_path: Path):
    """Verifies create_file_logger creates the destination file and records entries."""
    log_file = tmp_path / "logs" / "AG-COMPAT.stdout.log"
    logger = create_file_logger("agent_compat", log_path=log_file, json_format=False)

    with correlation_scope(run_id="run-file-test", agent_id="AG-COMPAT"):
        logger.info("Worker process initialized")
        logger.warn("Minor deprecation notice")

    assert log_file.is_file()
    content = log_file.read_text(encoding="utf-8")
    assert "Worker process initialized" in content
    assert "Minor deprecation notice" in content


def test_structured_logger_exception_and_fatal():
    """Verifies exception stack capture and fatal/critical levels in StructuredLogger."""
    captured = []

    def mock_sink(**kwargs):
        captured.append(kwargs)

    logger = get_logger("test_fatal_logger", audit_sink=mock_sink)

    try:
        raise ZeroDivisionError("division by zero in worker")
    except ZeroDivisionError:
        logger.exception("Calculation aborted")

    assert len(captured) == 1
    assert captured[0]["severity"] == "ERROR"
    assert "Calculation aborted" in captured[0]["payload"]["message"]

    logger.fatal("Unrecoverable host system failure", audit=True)
    assert len(captured) == 2
    assert captured[1]["severity"] == "FATAL"

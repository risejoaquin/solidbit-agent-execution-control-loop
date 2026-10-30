"""Unit tests for SACL V1 append-only audit event emission subsystem."""

import sqlite3

import pytest

from sacl.contracts.models import AuditEvent
from sacl.observability.audit import AuditEventEmitter
from sacl.observability.correlation import correlation_scope
from sacl.observability.events import (
    APPROVAL_REQUESTED,
    GATE_HALTED,
    PROCESS_SPAWNED,
    RUN_COMPLETED,
    RUN_FAILED,
)


def test_emit_audit_event_via_model(sqlite_temp_db: sqlite3.Connection):
    """Verifies emitting an audit event via AuditEvent dataclass instance."""
    emitter = AuditEventEmitter(sqlite_temp_db)

    event = AuditEvent(
        event_type=PROCESS_SPAWNED,
        severity="INFO",
        payload={"pid": 4812, "worktree": "worktrees/AG-COMPAT"},
        created_at="2026-10-07T22:00:00Z",
        job_id="job-101",
        run_id="run-202",
        agent_id="AG-COMPAT",
    )

    event_id = emitter.emit(event)
    assert event_id > 0

    # Query back
    retrieved = emitter.get_event_by_id(event_id)
    assert retrieved is not None
    assert retrieved.event_id == event_id
    assert retrieved.event_type == PROCESS_SPAWNED
    assert retrieved.severity == "INFO"
    assert retrieved.run_id == "run-202"
    assert retrieved.agent_id == "AG-COMPAT"
    assert retrieved.payload["pid"] == 4812


def test_emit_audit_event_via_kwargs_and_context(sqlite_temp_db: sqlite3.Connection):
    """Verifies emitting an audit event with kwargs and correlation context enrichment."""
    emitter = AuditEventEmitter(sqlite_temp_db)

    with correlation_scope(job_id="job-kw", run_id="run-kw", agent_id="AG-ARCH"):
        event_id = emitter.emit(
            event_type=GATE_HALTED,
            severity="WARN",
            payload={"reason": "Human gate required"},
        )

    retrieved = emitter.get_event_by_id(event_id)
    assert retrieved is not None
    assert retrieved.job_id == "job-kw"
    assert retrieved.run_id == "run-kw"
    assert retrieved.agent_id == "AG-ARCH"
    assert retrieved.event_type == GATE_HALTED
    assert retrieved.severity == "WARN"
    assert retrieved.payload["reason"] == "Human gate required"


def test_append_only_compatibility_table_synchronization(sqlite_temp_db: sqlite3.Connection):
    """Verifies that audit events are written to both events and audit_events tables."""
    emitter = AuditEventEmitter(sqlite_temp_db)

    event_id = emitter.emit(
        event_type=RUN_COMPLETED,
        severity="INFO",
        payload={"verdict": "PASS"},
        run_id="run-dual",
        agent_id="AG-ALL",
    )

    # Check primary table
    cursor = sqlite_temp_db.cursor()
    cursor.execute("SELECT COUNT(*) FROM events WHERE event_id = ?", (event_id,))
    assert cursor.fetchone()[0] == 1

    # Check compatibility table
    cursor.execute("SELECT COUNT(*) FROM audit_events WHERE run_id = 'run-dual'")
    assert cursor.fetchone()[0] == 1


def test_query_events_with_filters(sqlite_temp_db: sqlite3.Connection):
    """Verifies querying and filtering audit events."""
    emitter = AuditEventEmitter(sqlite_temp_db)

    emitter.emit(
        event_type=PROCESS_SPAWNED, severity="INFO", run_id="run-filter-1", agent_id="AG-A"
    )
    emitter.emit(
        event_type=APPROVAL_REQUESTED, severity="INFO", run_id="run-filter-1", agent_id="AG-A"
    )
    emitter.emit(event_type=RUN_FAILED, severity="ERROR", run_id="run-filter-1", agent_id="AG-B")
    emitter.emit(
        event_type=PROCESS_SPAWNED, severity="INFO", run_id="run-filter-2", agent_id="AG-C"
    )

    # Filter by run_id
    run1_events = emitter.query_events(run_id="run-filter-1")
    assert len(run1_events) == 3

    # Filter by severity
    errors = emitter.query_events(run_id="run-filter-1", severity="ERROR")
    assert len(errors) == 1
    assert errors[0].event_type == RUN_FAILED

    # Filter by agent_id
    ag_a_events = emitter.query_events(agent_id="AG-A")
    assert len(ag_a_events) == 2

    # Count matching
    count = emitter.count_events(run_id="run-filter-1")
    assert count == 3


def test_invalid_severity_fails_closed(sqlite_temp_db: sqlite3.Connection):
    """Verifies that emitting an invalid severity fails closed."""
    emitter = AuditEventEmitter(sqlite_temp_db)

    with pytest.raises(ValueError, match="Invalid severity"):
        emitter.emit(
            event_type="ARBITRARY_EVENT",
            severity="INVALID_SEVERITY",
            payload={},
        )


def test_query_events_pagination(sqlite_temp_db: sqlite3.Connection):
    """Verifies limit and offset pagination on query_events."""
    emitter = AuditEventEmitter(sqlite_temp_db)

    for i in range(10):
        emitter.emit(event_type=f"STEP_{i}", severity="INFO", run_id="run-page")

    page1 = emitter.query_events(run_id="run-page", limit=4, offset=0)
    assert len(page1) == 4
    assert page1[0].event_type == "STEP_0"
    assert page1[3].event_type == "STEP_3"

    page2 = emitter.query_events(run_id="run-page", limit=4, offset=4)
    assert len(page2) == 4
    assert page2[0].event_type == "STEP_4"
    assert page2[3].event_type == "STEP_7"


def test_audit_emitter_with_path_source(sqlite_temp_db: sqlite3.Connection):
    """Verifies AuditEventEmitter can be initialized with database file path."""
    cursor = sqlite_temp_db.cursor()
    cursor.execute("PRAGMA database_list;")
    db_file = cursor.fetchall()[0]["file"]

    emitter = AuditEventEmitter(db_file)
    ev_id = emitter.emit(event_type="PATH_TEST", severity="INFO", run_id="run-path")
    assert ev_id > 0

    record = emitter.get_event_by_id(ev_id)
    assert record is not None
    assert record.event_type == "PATH_TEST"

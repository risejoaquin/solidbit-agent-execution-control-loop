"""SACL V1 Structured Event Taxonomy, Severity Levels, and Event Models.

Conforms to docs/OBSERVABILITY.md and db/migrations/001_init.sql (events / audit_events).
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, FrozenSet, Optional

from sacl.contracts.models import AuditEvent
from sacl.observability.correlation import get_current_correlation


class Severity(str, Enum):
    """Standard audit and logging event severity levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"


ALL_SEVERITIES: FrozenSet[str] = frozenset(s.value for s in Severity)


class AuditEventType(str, Enum):
    """Canonical event taxonomy defined in docs/OBSERVABILITY.md §5.2."""

    # Ingress & Transport
    PUBSUB_WAKE_RECEIVED = "PUBSUB_WAKE_RECEIVED"
    HISTORY_FETCHED = "HISTORY_FETCHED"
    JOB_INGESTED = "JOB_INGESTED"

    # Orchestration & Workspace Setup
    PREFLIGHT_PASSED = "PREFLIGHT_PASSED"
    PROJECT_LOCK_ACQUIRED = "PROJECT_LOCK_ACQUIRED"
    WORKTREE_PROVISIONED = "WORKTREE_PROVISIONED"

    # Worker Lifecycle
    PROCESS_SPAWNED = "PROCESS_SPAWNED"
    PROCESS_SPAWN = "PROCESS_SPAWN"  # Legacy compatibility
    HEARTBEAT_RECORDED = "HEARTBEAT_RECORDED"
    TIMEOUT_DETECTED = "TIMEOUT_DETECTED"
    PID_RECYCLED_DETECTED = "PID_RECYCLED_DETECTED"
    STOPPED_BY_USER = "STOPPED_BY_USER"
    STATUS_CHANGE = "STATUS_CHANGE"

    # Safety, Conflicts & Gates
    CONFLICT_DETECTED = "CONFLICT_DETECTED"
    APPROVAL_REQUESTED = "APPROVAL_REQUESTED"
    SAFETY_GATE = "SAFETY_GATE"
    GATE_HALTED = "GATE_HALTED"

    # Execution Outcomes & Artifacts
    RUN_COMPLETED = "RUN_COMPLETED"
    RUN_FAILED = "RUN_FAILED"
    ERROR_RECORDED = "ERROR_RECORDED"
    ARTIFACT_REGISTERED = "ARTIFACT_REGISTERED"

    # Mutual Exclusion
    LEASE_ACQUIRED = "LEASE_ACQUIRED"
    LEASE_RELEASED = "LEASE_RELEASED"


# Convenience constants matching taxonomy
PUBSUB_WAKE_RECEIVED = AuditEventType.PUBSUB_WAKE_RECEIVED.value
HISTORY_FETCHED = AuditEventType.HISTORY_FETCHED.value
JOB_INGESTED = AuditEventType.JOB_INGESTED.value
PREFLIGHT_PASSED = AuditEventType.PREFLIGHT_PASSED.value
PROJECT_LOCK_ACQUIRED = AuditEventType.PROJECT_LOCK_ACQUIRED.value
WORKTREE_PROVISIONED = AuditEventType.WORKTREE_PROVISIONED.value
PROCESS_SPAWNED = AuditEventType.PROCESS_SPAWNED.value
HEARTBEAT_RECORDED = AuditEventType.HEARTBEAT_RECORDED.value
TIMEOUT_DETECTED = AuditEventType.TIMEOUT_DETECTED.value
PID_RECYCLED_DETECTED = AuditEventType.PID_RECYCLED_DETECTED.value
CONFLICT_DETECTED = AuditEventType.CONFLICT_DETECTED.value
APPROVAL_REQUESTED = AuditEventType.APPROVAL_REQUESTED.value
GATE_HALTED = AuditEventType.GATE_HALTED.value
RUN_COMPLETED = AuditEventType.RUN_COMPLETED.value
RUN_FAILED = AuditEventType.RUN_FAILED.value
ERROR_RECORDED = AuditEventType.ERROR_RECORDED.value
ARTIFACT_REGISTERED = AuditEventType.ARTIFACT_REGISTERED.value


def create_audit_event(
    event_type: str,
    severity: str = Severity.INFO.value,
    payload: Optional[Dict[str, Any]] = None,
    created_at: Optional[str] = None,
    event_id: Optional[int] = None,
    job_id: Optional[str] = None,
    run_id: Optional[str] = None,
    node_id: Optional[str] = None,
    agent_id: Optional[str] = None,
) -> AuditEvent:
    """Constructs and validates an AuditEvent model instance.

    Automatically enriches missing correlation identifiers from the active
    thread-local correlation context.
    """
    sev = severity.upper()
    if sev not in ALL_SEVERITIES:
        raise ValueError(f"Invalid severity '{severity}'; must be one of {sorted(ALL_SEVERITIES)}")

    corr = get_current_correlation()
    active_job = job_id or corr.job_id
    active_run = run_id or corr.run_id
    active_node = node_id or corr.node_id
    active_agent = agent_id or corr.agent_id

    iso_timestamp = created_at or datetime.now(timezone.utc).isoformat()
    norm_payload = dict(payload) if payload else {}

    # Ensure trace_id is present in payload if available
    if corr.trace_id and "trace_id" not in norm_payload:
        norm_payload["trace_id"] = corr.trace_id

    return AuditEvent(
        event_id=event_id,
        job_id=active_job,
        run_id=active_run,
        node_id=active_node,
        agent_id=active_agent,
        event_type=event_type,
        severity=sev,
        payload=norm_payload,
        created_at=iso_timestamp,
    )

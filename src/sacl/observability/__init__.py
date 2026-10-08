"""SACL V1 Observability Framework.

Structured logging, correlation IDs, immutable audit event emission,
evidence and filesystem artifact metadata, process heartbeat liveness,
forensic error diagnostics, and monitor-facing read models.
"""

from sacl.observability.audit import AuditEventEmitter
from sacl.observability.correlation import (
    CorrelationContext,
    clear_current_correlation,
    correlation_scope,
    generate_correlation_id,
    generate_trace_id,
    get_current_correlation,
    reset_current_correlation,
    set_current_correlation,
)
from sacl.observability.errors import (
    ALL_ERROR_CATEGORIES,
    ALL_ERROR_SEVERITIES,
    ErrorCategory,
    ErrorRecorder,
)
from sacl.observability.evidence import (
    ArtifactMetadata,
    EvidenceRegistry,
    compute_file_sha256,
    infer_artifact_type,
)
from sacl.observability.events import (
    ALL_SEVERITIES,
    APPROVAL_REQUESTED,
    ARTIFACT_REGISTERED,
    CONFLICT_DETECTED,
    ERROR_RECORDED,
    GATE_HALTED,
    HEARTBEAT_RECORDED,
    HISTORY_FETCHED,
    JOB_INGESTED,
    PID_RECYCLED_DETECTED,
    PREFLIGHT_PASSED,
    PROCESS_SPAWNED,
    PROJECT_LOCK_ACQUIRED,
    PUBSUB_WAKE_RECEIVED,
    RUN_COMPLETED,
    RUN_FAILED,
    TIMEOUT_DETECTED,
    WORKTREE_PROVISIONED,
    AuditEventType,
    Severity,
    create_audit_event,
)
from sacl.observability.heartbeat import BackgroundHeartbeater, HeartbeatService
from sacl.observability.logging import (
    JsonLogFormatter,
    StructuredLogger,
    TextLogFormatter,
    create_file_logger,
    get_logger,
)
from sacl.observability.monitor import (
    DashboardSnapshot,
    FleetAgentView,
    LeaseView,
    MonitorReadModel,
    format_duration,
    render_ascii_dashboard,
)

__all__ = [
    # Correlation
    "CorrelationContext",
    "generate_trace_id",
    "generate_correlation_id",
    "get_current_correlation",
    "set_current_correlation",
    "reset_current_correlation",
    "clear_current_correlation",
    "correlation_scope",
    # Events & Taxonomy
    "Severity",
    "ALL_SEVERITIES",
    "AuditEventType",
    "create_audit_event",
    "PUBSUB_WAKE_RECEIVED",
    "HISTORY_FETCHED",
    "JOB_INGESTED",
    "PREFLIGHT_PASSED",
    "PROJECT_LOCK_ACQUIRED",
    "WORKTREE_PROVISIONED",
    "PROCESS_SPAWNED",
    "HEARTBEAT_RECORDED",
    "TIMEOUT_DETECTED",
    "PID_RECYCLED_DETECTED",
    "CONFLICT_DETECTED",
    "APPROVAL_REQUESTED",
    "GATE_HALTED",
    "RUN_COMPLETED",
    "RUN_FAILED",
    "ERROR_RECORDED",
    "ARTIFACT_REGISTERED",
    # Logging
    "JsonLogFormatter",
    "TextLogFormatter",
    "StructuredLogger",
    "get_logger",
    "create_file_logger",
    # Audit
    "AuditEventEmitter",
    # Evidence & Filesystem Artifacts
    "ArtifactMetadata",
    "EvidenceRegistry",
    "compute_file_sha256",
    "infer_artifact_type",
    # Heartbeat
    "HeartbeatService",
    "BackgroundHeartbeater",
    # Error Diagnostics
    "ErrorRecorder",
    "ErrorCategory",
    "ALL_ERROR_CATEGORIES",
    "ALL_ERROR_SEVERITIES",
    # Monitor Read Model
    "FleetAgentView",
    "LeaseView",
    "DashboardSnapshot",
    "MonitorReadModel",
    "format_duration",
    "render_ascii_dashboard",
]

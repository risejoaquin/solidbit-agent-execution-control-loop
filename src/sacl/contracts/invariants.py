"""SACL V1 Architectural Invariants, Canonical Enums, and Constants.

Codifies the non-negotiable architectural invariants defined in
DECISION_BASELINE.md and contracts/architecture-invariants.json.
"""

from enum import Enum
from typing import Final, FrozenSet, Tuple


# ============================================================================
# CANONICAL DECISION PRECEDENCE HIERARCHY
# ============================================================================

class DecisionTier(int, Enum):
    """The four-tier sovereign decision hierarchy governing all SACL operations."""

    TIER_1_EXPLICIT_JOAQUIN_DECISIONS = 1
    TIER_2_PROVEN_CURRENT_ORCHESTRATOR_BEHAVIOR = 2
    TIER_3_EXISTING_GOVERNANCE_AND_CONTRACTS = 3
    TIER_4_INDUSTRY_STANDARDS_UNDEFINED_GAPS_ONLY = 4


DECISION_PRECEDENCE: Final[Tuple[str, ...]] = (
    "explicit_joaquin_decisions",
    "proven_current_orchestrator_behavior",
    "existing_governance_and_contracts",
    "industry_standard_for_undefined_gaps_only",
)


# ============================================================================
# JOB LIFECYCLE & STATE DOMAINS (12 Primary + 10 Side States)
# ============================================================================

class JobStatus(str, Enum):
    """The 12 linear primary states of the canonical job lifecycle.

    Linear progression:
    RECEIVED -> AUTHENTICATED -> VALIDATED -> PERSISTED -> QUEUED -> DISPATCHED
             -> RUNNING -> VERIFYING -> RESULT_PACKAGED -> RESULT_SENT -> COMPLETED -> ARCHIVED
    """

    RECEIVED = "RECEIVED"
    AUTHENTICATED = "AUTHENTICATED"
    VALIDATED = "VALIDATED"
    PERSISTED = "PERSISTED"
    QUEUED = "QUEUED"
    DISPATCHED = "DISPATCHED"
    RUNNING = "RUNNING"
    VERIFYING = "VERIFYING"
    RESULT_PACKAGED = "RESULT_PACKAGED"
    RESULT_SENT = "RESULT_SENT"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class JobSideStatus(str, Enum):
    """The 10 non-linear side states and terminal/interrupted outcomes."""

    WAITING_APPROVAL = "WAITING_APPROVAL"
    RETRY_WAIT = "RETRY_WAIT"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    INTERRUPTED = "INTERRUPTED"
    TIMED_OUT = "TIMED_OUT"
    POLICY_DENIED = "POLICY_DENIED"
    REJECTED = "REJECTED"
    QUARANTINED = "QUARANTINED"


PRIMARY_JOB_STATES: Final[FrozenSet[str]] = frozenset(s.value for s in JobStatus)
SIDE_JOB_STATES: Final[FrozenSet[str]] = frozenset(s.value for s in JobSideStatus)
ALL_JOB_STATES: Final[FrozenSet[str]] = PRIMARY_JOB_STATES | SIDE_JOB_STATES


# ============================================================================
# GRAPH-H DAG NODE LIFECYCLE (9 States)
# ============================================================================

class GraphNodeStatus(str, Enum):
    """The 9 lifecycle states for ephemeral Graph-H execution nodes."""

    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    RETRYABLE_FAILURE = "RETRYABLE_FAILURE"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    CANCELLED = "CANCELLED"


GRAPH_NODE_STATES: Final[FrozenSet[str]] = frozenset(s.value for s in GraphNodeStatus)


# ============================================================================
# AGENT WORKER PROCESS STATES
# ============================================================================

class AgentStatus(str, Enum):
    """Lifecycle states for individual agent worker instances and processes."""

    # Worker Process Execution Lifecycle
    SCHEDULED = "SCHEDULED"
    LAUNCHING = "LAUNCHING"
    RUNNING = "RUNNING"
    TIMEOUT_RUNNING = "TIMEOUT_RUNNING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"

    # Graph Node Alignment (interchangeable in DB records)
    PENDING = "PENDING"
    READY = "READY"
    SUCCEEDED = "SUCCEEDED"
    RETRYABLE_FAILURE = "RETRYABLE_FAILURE"
    BLOCKED = "BLOCKED"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    CANCELLED = "CANCELLED"


# ============================================================================
# CANONICAL VERDICTS
# ============================================================================

class Verdict(str, Enum):
    """Authoritative verdicts evaluated across 4-point reconciliation.

    DONE_REVIEW_REQUIRED indicates completed physical execution requiring human review;
    it NEVER means PASS.
    PASS_REPORT_PRESENT is the preserved legacy fallback when a report is on disk without a regex marker.
    """

    PASS = "PASS"
    PARTIAL = "PARTIAL"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    IN_PROGRESS = "IN_PROGRESS"
    UNKNOWN = "UNKNOWN"
    STOPPED_BY_USER = "STOPPED_BY_USER"
    PASS_REPORT_PRESENT = "PASS (Report Present)"
    DONE_REVIEW_REQUIRED = "DONE_REVIEW_REQUIRED"


TERMINAL_VERDICTS: Final[FrozenSet[str]] = frozenset({
    Verdict.PASS.value,
    Verdict.PARTIAL.value,
    Verdict.BLOCKED.value,
    Verdict.FAILED.value,
    Verdict.STOPPED_BY_USER.value,
    Verdict.PASS_REPORT_PRESENT.value,
    Verdict.DONE_REVIEW_REQUIRED.value,
})


# ============================================================================
# BOUNDED APPROVAL CHANNELS & DECISIONS
# ============================================================================

class ApprovalChannel(str, Enum):
    """Approved channels for sovereign human action gates in V1 (no webhooks)."""

    CLI = "CLI"
    GMAIL = "GMAIL"
    MANUAL = "MANUAL"


class ApprovalDecision(str, Enum):
    """Decision outcomes for bounded human approvals."""

    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DEFERRED = "DEFERRED"


class ApprovalStatus(str, Enum):
    """Lifecycle status of an approval record."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"


APPROVAL_CHANNELS_V1: Final[FrozenSet[str]] = frozenset(c.value for c in ApprovalChannel)
APPROVAL_BINDING_FIELDS: Final[Tuple[str, ...]] = (
    "job_id",
    "action",
    "scope",
    "request_id",
    "expires_at",
)


# ============================================================================
# HARD LOCAL POLICY DENIALS (IMMUTABLE BOUNDARY)
# ============================================================================

HARD_DENIED_ACTIONS: Final[FrozenSet[str]] = frozenset({
    "remote_production_execution",
    "github_merge",
    "production_db_write",
    "secret_export",
    "arbitrary_remote_code",
    "main_branch_execution",
    "primary_checkout_mutation",
    "hard_reset",
    "auto_stash",
})


# ============================================================================
# OPERATIONAL STATE STORE (16 SQLite DOMAINS)
# ============================================================================

class OperationalStateDomain(str, Enum):
    """The 16 canonical relational operational state domains in sacl_ops.db."""

    SCHEMA_MIGRATIONS = "schema_migrations"
    PROJECTS = "projects"
    PACKAGES = "packages"
    MAIL_MESSAGES = "mail_messages"
    JOBS = "jobs"
    RUNS = "runs"
    GRAPH_NODES = "graph_nodes"
    NODE_ATTEMPTS = "node_attempts"
    AGENTS = "agents"
    EVENTS = "events"
    APPROVALS = "approvals"
    ARTIFACTS = "artifacts"
    RESULTS = "results"
    LEASES = "leases"
    HEARTBEATS = "heartbeats"
    ERRORS = "errors"


OPERATIONAL_STATE_DOMAINS: Final[Tuple[str, ...]] = tuple(d.value for d in OperationalStateDomain)

SQLITE_PRAGMAS: Final[Tuple[str, ...]] = (
    "PRAGMA journal_mode = WAL;",
    "PRAGMA busy_timeout = 5000;",
    "PRAGMA synchronous = NORMAL;",
    "PRAGMA foreign_keys = ON;",
)


# ============================================================================
# ARTIFACT & STORAGE INVARIANTS
# ============================================================================

class ArtifactType(str, Enum):
    """Classification of heavy filesystem artifacts stored under artifacts/runs/<runId>/."""

    REPORT = "REPORT"
    LOG_STDOUT = "LOG_STDOUT"
    LOG_STDERR = "LOG_STDERR"
    DIFF = "DIFF"
    PATCH = "PATCH"
    SUMMARY_MD = "SUMMARY_MD"
    SUMMARY_JSON = "SUMMARY_JSON"
    ZIP_PACKAGE = "ZIP_PACKAGE"
    ZIP_RESULT = "ZIP_RESULT"
    EVIDENCE = "EVIDENCE"
    OTHER = "OTHER"


HEAVY_ARTIFACTS_ON_FILESYSTEM: Final[bool] = True


# ============================================================================
# RECONCILIATION & PID RECYCLING INVARIANTS
# ============================================================================

RECONCILIATION_PILLARS: Final[Tuple[str, ...]] = (
    "process_observation",
    "persisted_state",
    "required_outputs",
    "final_verdict",
)

PID_DRIFT_TOLERANCE_SECONDS: Final[int] = 300

ALLOWED_PROCESS_IMAGES: Final[FrozenSet[str]] = frozenset({
    "agy",
    "powershell",
    "pwsh",
    "cmd",
    "node",
    "conhost",
    "python",
    "python3",
    "git",
})

# Proven regex marker: ^(?:AGENT_[A-Z0-9_-]+_RESULT|RESULT|FINAL_RESULT)\s*=\s*(PASS|PARTIAL|BLOCKED)
VERDICT_REGEX: Final[str] = (
    r"^(?:AGENT_[A-Z0-9_-]+_RESULT|RESULT|FINAL_RESULT)\s*=\s*(PASS|PARTIAL|BLOCKED)"
)

# Header regex fallback: accommodates markdown asterisks e.g. **Final Status:** PASS
HEADER_STATUS_REGEX: Final[str] = (
    r"(?i)\*{0,2}(?:Final Status|Status):?\*{0,2}:?\s*\*{0,2}(PASS|COMPLETE\s*/\s*VERIFIED|PARTIAL|BLOCKED|FAILED)\*{0,2}"
)

# Wave summary marker regex: (?m)^WAVE[0-9]*_RESULT=(PASS|FAIL|BLOCKED)\s*$
WAVE_RESULT_REGEX: Final[str] = r"(?m)^WAVE[0-9]*_RESULT=(PASS|FAIL|BLOCKED)\s*$"


# ============================================================================
# EXECUTION MODES & RISK TIERS
# ============================================================================

class ExecutionMode(str, Enum):
    """Manifest execution modes."""

    ARCHITECTURE_FREEZE_AND_REPO_BOOTSTRAP = "architecture_freeze_and_repo_bootstrap"
    GOVERNED_DOCUMENTATION_GENERATION = "governed_documentation_generation"
    ISOLATED_BRANCH_DEVELOPMENT = "isolated_branch_development"
    INTEGRATION_AND_AUDIT = "integration_and_audit"
    CERTIFICATION_TEST = "certification_test"


class RiskTier(str, Enum):
    """Risk tiers for project repository isolation and gate enforcement."""

    SAFE_NOW = "SAFE_NOW"
    SAFE_IN_ISOLATED_BRANCH = "SAFE_IN_ISOLATED_BRANCH"
    POST_GATE = "POST_GATE"
    REQUIRES_DECISION = "REQUIRES_DECISION"


class FailurePolicy(str, Enum):
    """Graph-H DAG failure policies."""

    ABORT_IMMEDIATELY = "abort_immediately"
    COMPLETE_STAGE_THEN_HALT = "complete_stage_then_halt"
    CONTINUE_INDEPENDENT = "continue_independent"


# ============================================================================
# MAIL & TRANSPORT INVARIANTS
# ============================================================================

class MailDirection(str, Enum):
    """Direction of mail envelope transmission."""

    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


class MailStatus(str, Enum):
    """Mail queue lifecycle status."""

    RECEIVED = "RECEIVED"
    AUTHENTICATED = "AUTHENTICATED"
    VALIDATED = "VALIDATED"
    PERSISTED = "PERSISTED"
    QUEUED = "QUEUED"
    PROCESSED = "PROCESSED"
    DISPATCHED = "DISPATCHED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"
    QUARANTINED = "QUARANTINED"
    DUPLICATE_IGNORED = "DUPLICATE_IGNORED"


DEFAULT_ROUTING_PREFIX: Final[str] = "[SACL][JOB][v1]"
MAX_ATTACHMENT_SIZE_BYTES: Final[int] = 26_214_400  # 25 MB max attachment
DELIVERY_SEMANTICS: Final[str] = "AT_LEAST_ONCE"

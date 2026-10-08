-- ============================================================================
-- SACL V1 OPERATIONAL STATE STORE CANONICAL INITIAL SCHEMA
-- Database: sacl_ops.db
-- Migration: 001_init.sql
-- ============================================================================
-- CANONICAL PRECEDENCE & GOVERNANCE:
-- 1. Explicit Joaquín decisions:
--    - SQLite WAL operational state store; heavy logs & diffs in filesystem
--    - Mail Gateway and Graph-P separated; zero idle token burn
--    - Ephemeral Graph-H per wave; bounded human approval gate
-- 2. Proven current-orchestrator behavior:
--    - 3-Way process check (PID, whitelist image, 300s start-time drift defense)
--    - Safe-stop protocol (STOPPED_BY_USER) and non-killing diagnostic timeout (TIMEOUT_RUNNING)
--    - Structured deliverable regex extraction ladder and fallback verdict 'PASS (Report Present)'
--    - Cross-agent file modification overlap and conflict detection
-- 3. Existing governance & contracts:
--    - Manifest package integrity & deterministic execution contracts
--    - Structured dual summary contract (SUMMARY.md + SUMMARY.json)
-- 4. W0.1 / W0.2 Remediation Baselines:
--    - SB-FREEZE-P1-04: Mandatory canonical job lifecycle (12 primary + 10 side states)
--    - SB-FREEZE-P1-04: Graph-H node states (PENDING -> READY -> RUNNING -> SUCCEEDED + side states)
--    - SB-FREEZE-P1-05: 16 Structured V1 operational domains
--    - SB-FREEZE-P1-06: Bounded approval binding (JOB_ID + ACTION + SCOPE + REQUEST_ID + expiration)
-- ============================================================================

-- Recommended Connection PRAGMAs (MUST be initialized upon every SQLite connection):
-- PRAGMA journal_mode = WAL;
-- PRAGMA busy_timeout = 5000;
-- PRAGMA synchronous = NORMAL;
-- PRAGMA foreign_keys = ON;

-- ============================================================================
-- DOMAIN 1: SCHEMA MIGRATIONS & ENGINE TRACKING
-- ============================================================================
CREATE TABLE IF NOT EXISTS schema_migrations (
    version         INTEGER PRIMARY KEY,            -- Monotonically increasing migration version
    name            TEXT NOT NULL,                  -- Migration script filename e.g. '001_init.sql'
    applied_at      TEXT NOT NULL,                  -- ISO-8601 UTC timestamp
    checksum        TEXT NOT NULL                   -- SHA-256 hash of migration file content
);

-- ============================================================================
-- DOMAIN 2: PROJECTS REGISTRY
-- Multi-project core decoupling from hardcoded paths (ADR-009)
-- ============================================================================
CREATE TABLE IF NOT EXISTS projects (
    project_id      TEXT PRIMARY KEY,               -- Unique project key e.g. 'solidbit-control-loop'
    name            TEXT NOT NULL,                  -- Human-readable project name
    repo_url        TEXT,                           -- Git remote repository URL
    root_path       TEXT NOT NULL,                  -- Absolute local filesystem path to repo root
    default_branch  TEXT NOT NULL DEFAULT 'main',   -- Primary branch name
    policy_override_json TEXT,                      -- Project-specific policy configuration
    created_at      TEXT NOT NULL,                  -- ISO-8601 UTC timestamp
    updated_at      TEXT NOT NULL                   -- ISO-8601 UTC timestamp
);

-- ============================================================================
-- DOMAIN 3: EXECUTION PACKAGES
-- Declarative execution package ingestion records (ADR-004, ADR-006)
-- ============================================================================
CREATE TABLE IF NOT EXISTS packages (
    package_id      TEXT PRIMARY KEY,               -- e.g. 'SACL-W0-2-FREEZE-CONSISTENCY-REMEDIATION-v1'
    job_id          TEXT,                           -- Associated logical job ID
    project_id      TEXT,                           -- Target project FK
    archive_sha256  TEXT NOT NULL,                  -- Cryptographic SHA-256 of package ZIP archive
    manifest_json   TEXT NOT NULL,                  -- Full canonical manifest content
    storage_path    TEXT NOT NULL,                  -- Local filesystem path to stored package ZIP
    created_at      TEXT NOT NULL,                  -- ISO-8601 UTC timestamp
    status          TEXT NOT NULL CHECK(status IN (
                        'RECEIVED', 'AUTHENTICATED', 'VALIDATED', 
                        'REJECTED', 'QUARANTINED', 'PROCESSED'
                    )),
    FOREIGN KEY(project_id) REFERENCES projects(project_id)
);

-- ============================================================================
-- DOMAIN 4: JOBS (TOP-LEVEL LOGICAL EXECUTION LIFECYCLE)
-- Mandatory canonical job lifecycle & side states (SB-FREEZE-P1-04, ARCHITECTURE_INVARIANTS.json)
-- ============================================================================
CREATE TABLE IF NOT EXISTS jobs (
    job_id          TEXT PRIMARY KEY,               -- Canonical job identifier
    package_id      TEXT,                           -- Ingested package identifier
    project_id      TEXT,                           -- Target project identifier
    status          TEXT NOT NULL CHECK(status IN (
                        -- 12 Primary Canonical Lifecycle States:
                        'RECEIVED', 'AUTHENTICATED', 'VALIDATED', 'PERSISTED',
                        'QUEUED', 'DISPATCHED', 'RUNNING', 'VERIFYING',
                        'RESULT_PACKAGED', 'RESULT_SENT', 'COMPLETED', 'ARCHIVED',
                        -- 10 Side States & Terminal Outcomes:
                        'WAITING_APPROVAL', 'RETRY_WAIT', 'BLOCKED', 'FAILED',
                        'CANCELLED', 'INTERRUPTED', 'TIMED_OUT', 'POLICY_DENIED',
                        'REJECTED', 'QUARANTINED'
                    )),
    priority        INTEGER NOT NULL DEFAULT 0,     -- Scheduling priority (higher runs first)
    created_at      TEXT NOT NULL,                  -- ISO-8601 UTC timestamp
    updated_at      TEXT NOT NULL,                  -- ISO-8601 UTC timestamp
    completed_at    TEXT,                           -- ISO-8601 UTC timestamp
    current_run_id  TEXT,                           -- Active or most recent execution run ID
    error_summary   TEXT,                           -- Human/machine diagnostic summary
    metadata_json   TEXT,                           -- Extensible job metadata
    FOREIGN KEY(package_id) REFERENCES packages(package_id),
    FOREIGN KEY(project_id) REFERENCES projects(project_id)
);

-- ============================================================================
-- DOMAIN 5: RUNS (PHYSICAL EXECUTION ATTEMPTS)
-- Physical run execution attempt, workspace directories, and pre-merge integration state.
-- ============================================================================
CREATE TABLE IF NOT EXISTS runs (
    run_id              TEXT PRIMARY KEY,           -- e.g. 'w0-2-20261007-105623-ee9f03'
    job_id              TEXT NOT NULL,              -- Logical job parent FK
    package_id          TEXT NOT NULL,              -- Manifest package ID
    project_id          TEXT,                       -- Project identifier
    project             TEXT NOT NULL,              -- Legacy project name string
    repository          TEXT NOT NULL,              -- GitHub repository identifier
    mode                TEXT NOT NULL,              -- Execution mode
    source_orchestrator TEXT NOT NULL,              -- Path to source orchestrator
    target_repo_path    TEXT NOT NULL,              -- Path to target repo checkout
    run_dir             TEXT NOT NULL,              -- Path to run directory: 'runs/<runId>/'
    status              TEXT NOT NULL CHECK(status IN (
                            -- Primary & Side States
                            'RECEIVED', 'AUTHENTICATED', 'VALIDATED', 'PERSISTED',
                            'QUEUED', 'DISPATCHED', 'RUNNING', 'VERIFYING',
                            'RESULT_PACKAGED', 'RESULT_SENT', 'COMPLETED', 'ARCHIVED',
                            'WAITING_APPROVAL', 'RETRY_WAIT', 'BLOCKED', 'FAILED',
                            'CANCELLED', 'INTERRUPTED', 'TIMED_OUT', 'POLICY_DENIED',
                            'REJECTED', 'QUARANTINED',
                            -- Compatibility States
                            'INITIALIZED', 'GATE_HALTED', 'COMPLETE', 'STOPPED'
                        )),
    ready_for_integration TEXT NOT NULL DEFAULT 'NO' CHECK(ready_for_integration IN ('YES', 'NO')),
    started_at          TEXT NOT NULL,              -- ISO-8601 UTC
    completed_at        TEXT,                       -- ISO-8601 UTC
    reconciled_verdict  TEXT,                       -- Overall aggregated verdict
    error_summary       TEXT,                       -- Human/machine diagnostic summary
    FOREIGN KEY(job_id) REFERENCES jobs(job_id) ON DELETE CASCADE,
    FOREIGN KEY(project_id) REFERENCES projects(project_id)
);

-- ============================================================================
-- DOMAIN 6: GRAPH NODES (GRAPH-H EPHEMERAL DAG NODES)
-- Mandatory Graph-H node states (SB-FREEZE-P1-04, ARCHITECTURE_INVARIANTS.json)
-- ============================================================================
CREATE TABLE IF NOT EXISTS graph_nodes (
    run_id              TEXT NOT NULL,              -- Run attempt FK
    node_id             TEXT NOT NULL,              -- Canonical node identifier e.g. 'AG-COMPAT'
    job_id              TEXT NOT NULL,              -- Logical job FK
    phase_number        INTEGER NOT NULL,           -- Stage phase number (1, 2, 3...)
    stage_name          TEXT NOT NULL,              -- Stage name e.g. 'MATERIALIZATION'
    agent_id            TEXT NOT NULL,              -- Associated agent identifier
    status              TEXT NOT NULL CHECK(status IN (
                            'PENDING', 'READY', 'RUNNING', 'SUCCEEDED',
                            'RETRYABLE_FAILURE', 'FAILED', 'BLOCKED',
                            'WAITING_APPROVAL', 'CANCELLED'
                        )),
    started_at          TEXT,                       -- ISO-8601 UTC
    completed_at        TEXT,                       -- ISO-8601 UTC
    timeout_seconds     INTEGER NOT NULL DEFAULT 1800, -- Maximum duration before TIMEOUT_RUNNING
    max_attempts        INTEGER NOT NULL DEFAULT 1, -- Allowed retry attempts
    current_attempt     INTEGER NOT NULL DEFAULT 0, -- Current attempt index
    result_verdict      TEXT,                       -- Reconciled verdict for node
    PRIMARY KEY(run_id, node_id),
    FOREIGN KEY(run_id) REFERENCES runs(run_id) ON DELETE CASCADE,
    FOREIGN KEY(job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
);

-- ============================================================================
-- DOMAIN 7: NODE ATTEMPTS
-- Detailed per-attempt execution history for graph nodes
-- ============================================================================
CREATE TABLE IF NOT EXISTS node_attempts (
    attempt_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id              TEXT NOT NULL,
    node_id             TEXT NOT NULL,
    attempt_number      INTEGER NOT NULL,
    pid                 INTEGER,                    -- OS PID captured at process spawn
    status              TEXT NOT NULL,              -- Attempt lifecycle status
    exit_code           INTEGER,                    -- Raw OS process exit code
    started_at          TEXT NOT NULL,              -- ISO-8601 UTC
    finished_at         TEXT,                       -- ISO-8601 UTC
    verdict             TEXT,                       -- Extracted attempt verdict
    error_message       TEXT,                       -- Diagnostic error snippet
    stdout_path         TEXT,                       -- Attempt stdout log path
    stderr_path         TEXT,                       -- Attempt stderr log path
    report_path         TEXT,                       -- Attempt deliverable report path
    FOREIGN KEY(run_id, node_id) REFERENCES graph_nodes(run_id, node_id) ON DELETE CASCADE
);

-- ============================================================================
-- DOMAIN 8: AGENTS
-- Individual agent execution instances, worker PID tracking, and 4-point reconciliation.
-- Preserves compatibility with orchestrator scripts while supporting canonical states.
-- ============================================================================
CREATE TABLE IF NOT EXISTS agents (
    agent_id            TEXT NOT NULL,              -- e.g. 'AG-COMPAT', 'AG-SCHEMA'
    run_id              TEXT NOT NULL,              -- Run FK
    stage_id            INTEGER,                    -- Legacy dag_stages FK
    node_id             TEXT,                       -- Graph node reference
    status              TEXT NOT NULL CHECK(status IN (
                            'SCHEDULED', 'LAUNCHING', 'RUNNING', 
                            'TIMEOUT_RUNNING', 'STOPPING', 'STOPPED', 
                            'COMPLETE', 'FAILED', 'UNKNOWN',
                            -- Graph node alignment:
                            'PENDING', 'READY', 'SUCCEEDED',
                            'RETRYABLE_FAILURE', 'BLOCKED', 
                            'WAITING_APPROVAL', 'CANCELLED'
                        )),
    result_verdict      TEXT NOT NULL DEFAULT 'UNKNOWN' CHECK(result_verdict IN (
                            'PASS', 'PARTIAL', 'BLOCKED', 'FAILED', 
                            'IN_PROGRESS', 'UNKNOWN', 'STOPPED_BY_USER',
                            'PASS (Report Present)', 'DONE_REVIEW_REQUIRED'
                        )),
    pid                 INTEGER,                    -- Host OS Process ID
    branch              TEXT,                       -- Dedicated git branch e.g. 'audit/ccp-40-arch'
    commit_sha          TEXT,                       -- Latest git commit SHA produced by agent
    worktree_path       TEXT,                       -- Filesystem path to isolated worktree
    prompt_path         TEXT NOT NULL,              -- Path to assembled input prompt
    report_path         TEXT NOT NULL,              -- Expected deliverable markdown report path
    stdout_path         TEXT NOT NULL,              -- Worker stdout log file path in filesystem
    stderr_path         TEXT NOT NULL,              -- Worker stderr log file path in filesystem
    started_at          TEXT,                       -- ISO-8601 UTC process spawn timestamp
    updated_at          TEXT NOT NULL,              -- ISO-8601 UTC state record heartbeat
    finished_at         TEXT,                       -- ISO-8601 UTC process exit timestamp
    exit_code           INTEGER,                    -- Process exit code
    error_message       TEXT,                       -- Diagnostic error message or crash snippet
    PRIMARY KEY(agent_id, run_id),
    FOREIGN KEY(run_id) REFERENCES runs(run_id) ON DELETE CASCADE
);

-- ============================================================================
-- DOMAIN 9: EVENTS
-- Append-only system event log recording lifecycle transitions, security events, and gates.
-- ============================================================================
CREATE TABLE IF NOT EXISTS events (
    event_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id          TEXT,                           -- Associated job FK
    run_id          TEXT,                           -- Associated run FK
    node_id         TEXT,                           -- Associated graph node
    agent_id        TEXT,                           -- Associated agent
    event_type      TEXT NOT NULL,                  -- e.g. 'PROCESS_SPAWN', 'STATUS_CHANGE', 'SAFETY_GATE'
    severity        TEXT NOT NULL CHECK(severity IN ('DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL')),
    payload_json    TEXT NOT NULL,                  -- Structured JSON event metadata
    created_at      TEXT NOT NULL                   -- ISO-8601 UTC timestamp
);

-- ============================================================================
-- DOMAIN 10: APPROVALS
-- Bounded action-approval contract (SB-FREEZE-P1-06, ARCHITECTURE_INVARIANTS.json)
-- Binding: JOB_ID + ACTION + SCOPE + REQUEST_ID + expires_at
-- ============================================================================
CREATE TABLE IF NOT EXISTS approvals (
    approval_id     TEXT PRIMARY KEY,               -- e.g. 'appr-20261007-001'
    request_id      TEXT NOT NULL UNIQUE,           -- Unique approval request token
    job_id          TEXT NOT NULL,                  -- Bound logical job ID
    run_id          TEXT,                           -- Bound execution run ID
    action          TEXT NOT NULL,                  -- Specific requested action e.g. 'GIT_COMMIT_PRIMARY'
    scope           TEXT NOT NULL,                  -- Bounded target scope e.g. 'docs/adr/ADR-001.md'
    status          TEXT NOT NULL CHECK(status IN ('PENDING', 'APPROVED', 'REJECTED', 'EXPIRED', 'REVOKED')),
    decision        TEXT NOT NULL CHECK(decision IN ('PENDING', 'APPROVED', 'REJECTED')),
    approver        TEXT,                           -- Authorized human sovereign identifier
    rationale       TEXT,                           -- Human justification / notes
    signature       TEXT,                           -- Cryptographic or structured signature token
    requested_at    TEXT NOT NULL,                  -- ISO-8601 UTC timestamp
    decided_at      TEXT,                           -- ISO-8601 UTC timestamp
    expires_at      TEXT NOT NULL,                  -- ISO-8601 UTC timestamp after which approval is void
    FOREIGN KEY(job_id) REFERENCES jobs(job_id) ON DELETE CASCADE,
    FOREIGN KEY(run_id) REFERENCES runs(run_id) ON DELETE CASCADE
);

-- ============================================================================
-- DOMAIN 11: ARTIFACTS METADATA
-- Relational metadata index for heavy execution artifacts preserved on filesystem (ADR-011)
-- ============================================================================
CREATE TABLE IF NOT EXISTS artifacts (
    artifact_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          TEXT NOT NULL,                  -- Execution run FK
    job_id          TEXT NOT NULL,                  -- Logical job FK
    agent_id        TEXT,                           -- Producing agent ID
    node_id         TEXT,                           -- Producing graph node ID
    artifact_type   TEXT NOT NULL CHECK(artifact_type IN (
                        'REPORT', 'LOG_STDOUT', 'LOG_STDERR', 'DIFF', 'PATCH',
                        'SUMMARY_MD', 'SUMMARY_JSON', 'ZIP_PACKAGE', 'ZIP_RESULT',
                        'EVIDENCE', 'OTHER'
                    )),
    storage_path    TEXT NOT NULL,                  -- Canonical normalized path on filesystem
    file_size_bytes INTEGER NOT NULL,               -- Physical file size in bytes
    sha256_hash     TEXT NOT NULL,                  -- SHA-256 integrity digest
    created_at      TEXT NOT NULL,                  -- ISO-8601 UTC timestamp
    FOREIGN KEY(run_id) REFERENCES runs(run_id) ON DELETE CASCADE,
    FOREIGN KEY(job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
);

-- ============================================================================
-- DOMAIN 12: RESULTS
-- Sealed final execution results and delivery evidence
-- ============================================================================
CREATE TABLE IF NOT EXISTS results (
    result_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id              TEXT NOT NULL,              -- Logical job FK
    run_id              TEXT NOT NULL UNIQUE,       -- Execution run FK
    status              TEXT NOT NULL,              -- Sealed outcome status
    final_verdict       TEXT NOT NULL CHECK(final_verdict IN (
                            'PASS', 'PARTIAL', 'BLOCKED', 'FAILED',
                            'PASS (Report Present)', 'DONE_REVIEW_REQUIRED',
                            'STOPPED_BY_USER', 'UNKNOWN'
                        )),
    summary_md_path     TEXT NOT NULL,              -- Path to sealed SUMMARY.md
    summary_json_path   TEXT NOT NULL,              -- Path to sealed SUMMARY.json
    package_result_zip  TEXT,                       -- Path to sealed results ZIP package
    delivered_to        TEXT,                       -- Recipient address or queue
    delivered_at        TEXT,                       -- ISO-8601 UTC delivery timestamp
    created_at          TEXT NOT NULL,              -- ISO-8601 UTC timestamp
    FOREIGN KEY(job_id) REFERENCES jobs(job_id) ON DELETE CASCADE,
    FOREIGN KEY(run_id) REFERENCES runs(run_id) ON DELETE CASCADE
);

-- ============================================================================
-- DOMAIN 13: LEASES
-- Generalized distributed / local process mutual exclusion leases (ADR-002, ADR-003)
-- ============================================================================
CREATE TABLE IF NOT EXISTS leases (
    lease_name      TEXT PRIMARY KEY,               -- e.g. 'SUPERVISOR_SINGLETON', 'MAIL_GATEWAY'
    holder_id       TEXT NOT NULL,                  -- Holder identifier (process name or run ID)
    holder_pid      INTEGER NOT NULL,               -- OS Process ID holding lease
    acquired_at     TEXT NOT NULL,                  -- ISO-8601 UTC timestamp
    heartbeat_at    TEXT NOT NULL,                  -- ISO-8601 UTC timestamp of last renewal
    expires_at      TEXT NOT NULL,                  -- ISO-8601 UTC timestamp when lease expires
    metadata_json   TEXT                            -- Additional lease metadata
);

-- ============================================================================
-- DOMAIN 14: HEARTBEATS
-- High-frequency process liveness registry for daemons and worker processes
-- ============================================================================
CREATE TABLE IF NOT EXISTS heartbeats (
    heartbeat_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    component       TEXT NOT NULL,                  -- e.g. 'SUPERVISOR', 'MAIL_GATEWAY', 'WORKER'
    instance_id     TEXT NOT NULL,                  -- Unique process or run instance ID
    pid             INTEGER NOT NULL,               -- Host OS Process ID
    status          TEXT NOT NULL,                  -- Current reported status
    last_seen_at    TEXT NOT NULL,                  -- ISO-8601 UTC timestamp
    details_json    TEXT                            -- Health metrics / resource utilization
);

-- ============================================================================
-- DOMAIN 15: ERRORS
-- Structured operational error diagnostics repository
-- ============================================================================
CREATE TABLE IF NOT EXISTS errors (
    error_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id          TEXT,                           -- Associated job FK
    run_id          TEXT,                           -- Associated run FK
    node_id         TEXT,                           -- Associated graph node
    agent_id        TEXT,                           -- Associated agent ID
    error_code      TEXT NOT NULL,                  -- Machine-readable error code e.g. 'DIRTY_ROOT_HALT'
    category        TEXT NOT NULL CHECK(category IN (
                        'INFRASTRUCTURE', 'POLICY', 'VALIDATION', 'EXECUTION',
                        'TIMEOUT', 'COLLISION', 'TRANSPORT', 'APPROVAL', 'RECOVERY'
                    )),
    severity        TEXT NOT NULL CHECK(severity IN ('WARN', 'ERROR', 'FATAL')),
    message         TEXT NOT NULL,                  -- Human-readable error description
    stack_trace     TEXT,                           -- Error stack trace or diagnostic snippet
    context_json    TEXT,                           -- Diagnostic contextual payload
    occurred_at     TEXT NOT NULL                   -- ISO-8601 UTC timestamp
);

-- ============================================================================
-- DOMAIN 16: MAIL MESSAGES & CURSORS
-- Gmail API transport queue and historyId synchronization cursors (SB-FREEZE-P1-01)
-- ============================================================================
CREATE TABLE IF NOT EXISTS mail_messages (
    message_id      TEXT PRIMARY KEY,               -- RFC-2822 Message-ID or Gmail Message ID
    history_id      TEXT,                           -- Gmail historyId for authoritative fetch
    thread_id       TEXT,                           -- Gmail thread identifier
    sender          TEXT NOT NULL,                  -- Envelope sender address
    recipient       TEXT NOT NULL,                  -- Envelope recipient address
    subject         TEXT NOT NULL,                  -- Intake routing hint
    snippet         TEXT,                           -- Message snippet preview
    received_at     TEXT NOT NULL,                  -- ISO-8601 UTC timestamp
    processed_at    TEXT,                           -- ISO-8601 UTC timestamp
    nonce           TEXT NOT NULL UNIQUE,           -- Anti-replay cryptographic nonce
    attachment_sha  TEXT NOT NULL,                  -- SHA-256 of package ZIP attachment
    status          TEXT NOT NULL CHECK(status IN (
                        'RECEIVED', 'AUTHENTICATED', 'VALIDATED', 'PERSISTED',
                        'QUEUED', 'PROCESSED', 'REJECTED', 'QUARANTINED', 'DUPLICATE_IGNORED'
                    )),
    rejection_reason TEXT,                          -- Reason if message was rejected or quarantined
    job_id          TEXT,                           -- Resulting job ID
    run_id          TEXT,                           -- Associated execution run ID
    FOREIGN KEY(job_id) REFERENCES jobs(job_id)
);

CREATE TABLE IF NOT EXISTS mail_cursors (
    cursor_name     TEXT PRIMARY KEY,               -- e.g. 'GMAIL_USERS_WATCH'
    history_id      TEXT NOT NULL,                  -- Authoritative historyId cursor
    last_synced_at  TEXT NOT NULL,                  -- ISO-8601 UTC timestamp
    expiration_at   TEXT,                           -- Watch subscription expiration timestamp
    resource_id     TEXT                            -- Pub/Sub or Gmail watch resource ID
);

-- ============================================================================
-- COMPATIBILITY TABLES (JUSTIFIED & RETAINED FOR LEGACY SCRIPT INTEROPERABILITY)
-- ============================================================================

-- Compatibility Table 1: supervisor_locks (Retained for run-supervisor.ps1 legacy locking)
CREATE TABLE IF NOT EXISTS supervisor_locks (
    lock_name       TEXT PRIMARY KEY,               -- e.g. 'SUPERVISOR_SINGLETON'
    run_id          TEXT NOT NULL,                  -- Run ID holding the lock
    holder_pid      INTEGER NOT NULL,               -- OS Process ID holding lease
    acquired_at     TEXT NOT NULL,                  -- ISO-8601 UTC timestamp
    heartbeat_at    TEXT NOT NULL,                  -- ISO-8601 UTC timestamp of last renewal
    expires_at      TEXT NOT NULL                   -- ISO-8601 UTC timestamp when lease expires
);

-- Compatibility Table 2: dag_stages (Retained for RUN-WAVE staged phase tracking)
CREATE TABLE IF NOT EXISTS dag_stages (
    stage_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          TEXT NOT NULL,
    phase_number    INTEGER NOT NULL,               -- 1, 2, 3, 4 ...
    stage_name      TEXT NOT NULL,                  -- e.g. 'PHASE_1_COMPATIBILITY'
    status          TEXT NOT NULL CHECK(status IN ('PENDING', 'RUNNING', 'COMPLETE', 'FAILED')),
    started_at      TEXT,                           -- ISO-8601 UTC
    completed_at    TEXT,                           -- ISO-8601 UTC
    FOREIGN KEY(run_id) REFERENCES runs(run_id) ON DELETE CASCADE
);

-- Compatibility Table 3: agent_dependencies (Retained for DAG edge scheduling)
CREATE TABLE IF NOT EXISTS agent_dependencies (
    run_id              TEXT NOT NULL,
    upstream_agent_id   TEXT NOT NULL,
    downstream_agent_id TEXT NOT NULL,
    PRIMARY KEY(run_id, upstream_agent_id, downstream_agent_id),
    FOREIGN KEY(run_id) REFERENCES runs(run_id) ON DELETE CASCADE
);

-- Compatibility Table 4: file_modifications (Retained for cross-agent collision detection)
CREATE TABLE IF NOT EXISTS file_modifications (
    mod_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          TEXT NOT NULL,
    agent_id        TEXT NOT NULL,
    file_path       TEXT NOT NULL,                  -- Forward-slash normalized repo-relative path
    change_type     TEXT NOT NULL CHECK(change_type IN ('MODIFIED', 'ADDED', 'DELETED')),
    recorded_at     TEXT NOT NULL,                  -- ISO-8601 UTC
    FOREIGN KEY(agent_id, run_id) REFERENCES agents(agent_id, run_id) ON DELETE CASCADE
);

-- Compatibility Table 5: file_conflicts (Retained for collision detection registry)
CREATE TABLE IF NOT EXISTS file_conflicts (
    conflict_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          TEXT NOT NULL,
    file_path       TEXT NOT NULL,                  -- Colliding relative path
    agents_involved TEXT NOT NULL,                  -- JSON Array: ["AG-ARCH", "AG-SEC"]
    detected_at     TEXT NOT NULL,                  -- ISO-8601 UTC
    resolution      TEXT NOT NULL DEFAULT 'UNRESOLVED' CHECK(resolution IN ('UNRESOLVED', 'RESOLVED', 'WAIVED')),
    FOREIGN KEY(run_id) REFERENCES runs(run_id) ON DELETE CASCADE
);

-- Compatibility Table 6: mail_inbox (Retained for legacy intake queues)
CREATE TABLE IF NOT EXISTS mail_inbox (
    message_id      TEXT PRIMARY KEY,               -- RFC-2822 Message-ID
    sender          TEXT NOT NULL,                  -- Envelope sender address
    subject         TEXT NOT NULL,                  -- Subject line routing hint
    received_at     TEXT NOT NULL,                  -- ISO-8601 UTC
    nonce           TEXT NOT NULL UNIQUE,           -- Anti-replay cryptographic nonce
    attachment_sha  TEXT NOT NULL,                  -- SHA-256 of package ZIP attachment
    status          TEXT NOT NULL CHECK(status IN (
                            'PENDING', 'VALIDATED', 'PROCESSED', 
                            'REJECTED', 'DUPLICATE_IGNORED'
                        )),
    rejection_reason TEXT,                          -- Reason if status is REJECTED
    run_id          TEXT,                           -- Associated execution run ID if launched
    FOREIGN KEY(run_id) REFERENCES runs(run_id)
);

-- Compatibility Table 7: mail_outbox (Retained for legacy outbound mail dispatch)
CREATE TABLE IF NOT EXISTS mail_outbox (
    outbox_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          TEXT NOT NULL,
    recipient       TEXT NOT NULL,
    subject         TEXT NOT NULL,
    body_markdown   TEXT NOT NULL,                  -- Universal run summary in markdown
    attachment_path TEXT,                           -- Path to packaged result ZIP
    status          TEXT NOT NULL CHECK(status IN ('QUEUED', 'SENT', 'FAILED')),
    attempts        INTEGER NOT NULL DEFAULT 0,     -- Delivery attempt count
    created_at      TEXT NOT NULL,                  -- ISO-8601 UTC
    sent_at         TEXT,                           -- ISO-8601 UTC
    error_log       TEXT,                           -- Delivery transmission error log
    FOREIGN KEY(run_id) REFERENCES runs(run_id)
);

-- Compatibility Table 8: audit_events (Retained for legacy audit trail queries)
CREATE TABLE IF NOT EXISTS audit_events (
    event_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          TEXT,
    agent_id        TEXT,
    event_type      TEXT NOT NULL,                  -- e.g. 'PROCESS_SPAWN', 'STATUS_CHANGE', 'SAFETY_GATE'
    severity        TEXT NOT NULL CHECK(severity IN ('INFO', 'WARN', 'ERROR', 'FATAL')),
    payload_json    TEXT NOT NULL,                  -- Structured JSON event metadata
    created_at      TEXT NOT NULL                   -- ISO-8601 UTC
);

-- ============================================================================
-- INDEXES FOR LOW-LATENCY RECONCILIATION, QUERY PERFORMANCE & CONCURRENCY
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_runs_job_id ON runs(job_id);
CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(status);
CREATE INDEX IF NOT EXISTS idx_graph_nodes_run_status ON graph_nodes(run_id, status);
CREATE INDEX IF NOT EXISTS idx_node_attempts_node ON node_attempts(run_id, node_id);
CREATE INDEX IF NOT EXISTS idx_agents_run_status ON agents(run_id, status);
CREATE INDEX IF NOT EXISTS idx_events_run_type ON events(run_id, event_type);
CREATE INDEX IF NOT EXISTS idx_approvals_job_req ON approvals(job_id, request_id);
CREATE INDEX IF NOT EXISTS idx_approvals_status ON approvals(status);
CREATE INDEX IF NOT EXISTS idx_artifacts_run_type ON artifacts(run_id, artifact_type);
CREATE INDEX IF NOT EXISTS idx_results_job_run ON results(job_id, run_id);
CREATE INDEX IF NOT EXISTS idx_mail_messages_nonce ON mail_messages(nonce);
CREATE INDEX IF NOT EXISTS idx_mail_messages_history ON mail_messages(history_id);
CREATE INDEX IF NOT EXISTS idx_file_mods_run_file ON file_modifications(run_id, file_path);
CREATE INDEX IF NOT EXISTS idx_audit_run_type ON audit_events(run_id, event_type);
CREATE INDEX IF NOT EXISTS idx_mail_inbox_nonce ON mail_inbox(nonce);
CREATE INDEX IF NOT EXISTS idx_dag_stages_run ON dag_stages(run_id, phase_number);
CREATE INDEX IF NOT EXISTS idx_mail_outbox_status ON mail_outbox(status);
CREATE INDEX IF NOT EXISTS idx_heartbeats_comp ON heartbeats(component, instance_id);
CREATE INDEX IF NOT EXISTS idx_errors_run ON errors(run_id, error_code);

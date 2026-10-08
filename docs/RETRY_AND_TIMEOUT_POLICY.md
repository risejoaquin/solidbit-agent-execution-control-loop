# SACL V1 Retry, Timeout & Process Governance Policy

## 1. Executive Summary & Policy Scope

This document specifies the operational policies governing execution timeouts, worker process lifecycles, safe termination, transport deduplication, retry semantics, and supervisor leasing for the SolidBit Agent Execution Control Loop (SACL V1).

### 1.1 Constitutional Precedence Hierarchy
This policy strictly enforces the constitutional hierarchy:
1. **Explicit Joaquín decisions:**
   - Decoupled architecture: Mail Gateway independent of Graph-P; zero LLM token burn when idle.
   - SQLite `sacl_ops.db` state tracking; heavy logs and diffs preserved in filesystem.
   - Local dirty-root rule: human uncommitted work is never destroyed, stashed, or reset.
   - Remote production execution (Railway, mutating GitHub rulesets, Jira automation) is completely disabled in V1.
2. **Proven current-orchestrator behavior:**
   - **Inviolable non-killing timeout invariant:** Agents exceeding timeout deadlines are never terminated automatically.
   - **PID recycling defense:** 3-way process verification before any kill signal.
   - **Safe-stop protocol:** Clean worker shutdown tagging state with `STOPPED_BY_USER`.
3. **Existing governance and contracts:**
   - Manifest parameterization and permission boundaries (`solidbit.execution-package.v1`).
   - Standardized output contracts (`SUMMARY.md` + `SUMMARY.json`).
4. **W0.1 / W0.2 Remediation Baselines:**
   - **SB-FREEZE-P1-01:** Gmail API `users.watch` -> Cloud Pub/Sub pull notification -> authoritative History API fetch with persisted `historyId`.
   - **SB-FREEZE-P1-04:** Canonical job lifecycle side states (`RETRY_WAIT`, `TIMED_OUT`) and Graph-H node states (`RETRYABLE_FAILURE`, `WAITING_APPROVAL`).
   - At-least-once transport delivery with strictly idempotent consumers.
   - Deduplication based on `(message_id, nonce)` permitting legitimate wave retries.

---

## 2. Inviolable Non-Killing Timeout Invariant

### 2.1 The Core Rule
> **When an agent exceeds its configured `AgentTimeoutMinutes` threshold, the orchestrator MUST NOT terminate the worker process automatically.**

### 2.2 Rationale & Operational Value
In autonomous agent workflows running complex coding or auditing tasks, Antigravity (`agy.exe`) workers engage in multi-turn reasoning, large AST parsing, or intensive workspace analysis. Automatically killing an agent upon an arbitrary timer:
1. Destroys active reasoning state and incomplete workspace edits.
2. Precludes human operators from attaching debuggers, inspecting live memory, or reviewing running logs.
3. Produces silent failures where diagnostic timeouts masquerade as worker crashes.

### 2.3 State Transition on Timeout
When a worker's elapsed execution time exceeds `AgentTimeoutMinutes` (default: 30 minutes; valid range: 15 to 120 minutes):
1. The supervisor records an event in `events`: `severity = 'WARN'`, `event_type = 'TIMEOUT_DETECTED'`.
2. The agent status in `agents` transitions from `RUNNING` to `TIMEOUT_RUNNING`.
3. The Graph-H node status in `graph_nodes` remains `RUNNING` or transitions to diagnostic observation.
4. The live terminal monitor (`MONITOR.ps1`) highlights the agent in yellow/orange with a visible diagnostic alert: `TIMEOUT (STILL RUNNING - NO KILL)`.
5. The worker process continues executing undisturbed in its isolated worktree.
6. If the agent subsequently completes cleanly and writes its deliverable report, the state machine evaluates the deliverable normally and transitions the agent to `COMPLETE` and node to `SUCCEEDED`.
7. If the agent remains stalled or enters an infinite loop, the human operator retains exclusive authority to terminate it via `stop-agents.ps1`.
8. At the parent job level, if the total job deadline expires, the job transitions to side state `TIMED_OUT` while preserving worker forensics.

---

## 3. Safe-Stop Protocol & Local Kill Switch

When an operator or supervisor must terminate an agent, termination must execute through the safe-stop protocol to ensure safety and prevent accidental termination of recycled OS processes.

### 3.1 The 3-Way Identity Verification Check
Before issuing any process termination signal (`Stop-Process -Force` or OS signal), the stop handler MUST execute the 3-way verification algorithm proven in `scripts/stop-agents.ps1`:

```
                       [Initiate Stop Request for Agent]
                                      │
                                      ▼
                        [Query PID from sacl_ops.db]
                                      │
                        Is PID > 0 and Active in OS?
                                      ├── NO ──► [Log: Process already dead; Update status to STOPPED]
                                      └── YES
                                      │
                                      ▼
                      [Process Image Whitelist Check]
              Does ProcessName match 'agy', 'powershell',
              'pwsh', 'cmd', 'node', or 'conhost'?
                                      ├── NO ──► [SAFETY REFUSAL: Refuse kill; Unrelated process]
                                      └── YES
                                      │
                                      ▼
                      [Start-Time Drift Tolerance Check]
              |proc.StartTime - db.startedAt| <= 300 seconds?
                                      ├── NO ──► [SAFETY REFUSAL: PID Recycling Suspected; Abort]
                                      └── YES
                                      │
                                      ▼
                      [Execute Stop-Process -Force]
                                      │
                                      ▼
                   [Update SQLite: status='STOPPED',
                    result_verdict='STOPPED_BY_USER']
```

### 3.2 Safety Refusal Invariant
If the OS process matching the stored PID belongs to a non-whitelisted image (e.g., `explorer.exe`, `chrome.exe`) or the process `StartTime` has drifted more than 300 seconds from the database record, the stop handler:
1. **REFUSES** to issue `Stop-Process`.
2. Emits a high-visibility security alert: `[SAFETY REFUSAL] PID Recycling Suspected`.
3. Leaves the host process unmolested.
4. Marks the agent state in SQLite as `UNKNOWN` for operator investigation.

### 3.3 Stop Commands
- **Targeted Stop:** `stop-agents.ps1 -AgentId <AGENT_ID>` terminates a single verified agent process and updates its state to `STOPPED` with verdict `STOPPED_BY_USER`.
- **Global Emergency Stop:** `stop-agents.ps1 -All` iterates all running agents in `sacl_ops.db`, performs identity checks, terminates verified workers, updates all statuses to `STOPPED` (`STOPPED_BY_USER`), sets job status to `CANCELLED`, and releases the supervisor singleton lease.

---

## 4. Mail Gateway Deduplication, Replay & Retry Policy

Per SB-FREEZE-P1-01, W0.1 Baselines #8, #9 and QA P2-01:
- Primary intake uses **Gmail API `users.watch` -> Cloud Pub/Sub pull subscriber -> Gmail History API fetch via `historyId` cursor**.
- Inbound delivery semantics are **at-least-once**.
- Transport consumers and job launchers are **strictly idempotent**.
- Polling exists only as a periodic fallback/reconciliation mechanism, never as the primary source of truth.

### 4.1 Inbound Message Classification Matrix

| Inbound Scenario | Evaluation Criteria | Mail Gateway Action | Operational Status |
| :--- | :--- | :--- | :--- |
| **Identical Message Re-delivery** | Same `message_id` AND same `nonce` already in `mail_messages`. | Message acknowledged; processing skipped without error. | `DUPLICATE_IGNORED` |
| **Legitimate Wave Retry** | Same `package_id` / `job_id`, same attachment SHA-256, but **new `nonce`** and **new `message_id`**. | Accepted as a new attempt for the logical job; new physical run created. | `VALIDATED` -> `QUEUED` |
| **Package Tamper / Hash Conflict** | Same `package_id` / `job_id`, but **different attachment SHA-256**. | Ingestion rejected immediately; security alert recorded. | `REJECTED` (`HASH_CONFLICT`) |
| **Fresh Execution Package** | New `package_id`, new `nonce`, verified integrity, passing schema. | Ingested, staged, registered in `packages` & `jobs`, queued. | `VALIDATED` -> `QUEUED` |

### 4.2 Transport Network Timeouts & Exponential Backoff
- **Pub/Sub Pull Heartbeat:** 30-second pull lease renewal.
- **Watch Renewal:** Gmail `users.watch` registration renewed every 6 days (prior to 7-day expiration).
- **Network Outage Backoff:** If Google Cloud Pub/Sub or Gmail API connectivity fails, reconnect intervals back off exponentially:
  $$5\text{s} \longrightarrow 15\text{s} \longrightarrow 45\text{s} \longrightarrow 120\text{s} \longrightarrow 300\text{s} \quad (\text{maximum } 5 \text{ minutes})$$
- **Outbox Transmission Retry:** Outbound mail delivery retries up to 5 times with exponential backoff and $\pm 20\%$ jitter before marking status as `FAILED` in `mail_outbox`.

---

## 5. Execution Retry Policy: Node vs. Job

SACL V1 distinguishes between transient, recoverable failures and permanent, non-retryable errors at both the Graph-H node level and the logical job level.

### 5.1 Failure Classification Matrix

| Failure Classification | Examples | Retry Allowed? | Node Policy Action | Job Policy Action |
| :--- | :--- | :---: | :--- | :--- |
| **Transient SQLite Contention** | `SQLITE_BUSY` or `busy_timeout` (5000ms) exhaustion during write commit. | **YES** (Max 2 retries) | `RETRYABLE_FAILURE` -> `READY` | Remains `RUNNING` |
| **Preflight Tool / Worktree Lock** | Git lock contention (`.git/index.lock`), transient file lock by antivirus. | **YES** (Max 2 retries) | Worktree verified clean; retry attempt enqueued. | Remains `RUNNING` |
| **Process Crash Before File Modification** | Spawning failure, out-of-memory during launcher bootstrap before Git branch touch. | **YES** (Max 1 retry) | Worktree verified clean; fresh attempt launched. | Remains `RUNNING` |
| **Logical / Policy Violation** | Direct push to `main`, execution of unauthorized script, prompt injection trigger. | **NO** (0 retries) | Node marked `FAILED` (`POLICY_VIOLATION`). | Job transitions to `POLICY_DENIED`. |
| **Local Dirty-Root Breach** | Uncommitted human changes in target repository checkout. | **NO** (0 retries) | Immediate abort. | Job transitions to `BLOCKED`. |
| **Schema / Output Missing** | Required report missing, invalid deliverable schema. | **NO** (0 retries) | Node marked `FAILED` (`NO_EVIDENCE_FOUND`). | Job transitions to `FAILED`. |
| **Explicit Deliverable Marker = `BLOCKED`** | Deliverable report contains `AGENT_RESULT = BLOCKED`. | **NO** (0 retries) | Node marked `BLOCKED`. | Dependent nodes blocked; job transitions to `BLOCKED`. |
| **Cross-Agent Overlap Conflict** | Parallel agents modify identical files. | **NO** (0 retries) | Completed nodes marked; stage gated. | Job transitions to `BLOCKED`. |

### 5.2 Artifact & Log Preservation on Retry
Under **NO** circumstances may a retry attempt overwrite previously generated logs or evidence:
1. **Attempt Logging:** Every attempt writes to a distinct file recorded in `node_attempts`:
   - Attempt 1: `logs/<agent>.stdout.log`, `logs/<agent>.stderr.log`
   - Attempt 2: `logs/<agent>.attempt-2.stdout.log`, `logs/<agent>.attempt-2.stderr.log`
2. **Worktree Isolation:** If an attempt leaves uncommitted work before crashing, the dirty worktree is sealed for forensic inspection. The retry attempt receives a clean, newly isolated worktree (`worktrees/<agent>-retry1`).

---

## 6. DAG Stage Replay & Checkpoint Policy

When an interrupted or failed execution is resumed:
1. **Immutable Checkpointed Phases:** Graph-H nodes and DAG stages that completed with verified verdicts (`SUCCEEDED`, `PASS`, `PASS (Report Present)`, `PARTIAL`) are **NEVER re-executed**.
2. **Authoritative Disk Artifacts:** Committed worktree branches, deliverable markdown reports, and generated evidence from completed phases remain immutable and authoritative.
3. **Execution Resumption:** The scheduler resumes execution at the first incomplete or failed node, preserving all prior stage outputs.

---

## 7. Supervisor Leasing & Heartbeat Policy

To guarantee single-instance mutual exclusion without fragile WMI process queries:
1. **Lease Acquisition:** Supervisor claims lease in `leases` and `supervisor_locks` with `lease_name = 'SUPERVISOR_SINGLETON'`.
2. **Heartbeat Cadence:** Supervisor updates `heartbeat_at = UTC_NOW()` and `expires_at = UTC_NOW() + 60s` every 30 seconds.
3. **Lease Expiration:** If the supervisor process terminates abruptly, the lease expires after 60 seconds.
4. **Stale Lock Recovery:** An incoming supervisor checks `expires_at < UTC_NOW()`. If expired, it verifies `Test-AgentProcessRunning -ProcessId holder_pid`. If confirmed dead, the stale lease is reclaimed with an audit event in `events`.

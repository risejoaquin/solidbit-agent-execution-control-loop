# SolidBit Agent Execution Control Loop (SACL V1) — Decision Baseline

> **Document Type:** Sovereign Decision Baseline & Constitutional Architecture Invariants  
> **Schema:** `solidbit.architecture-invariants.v1`  
> **Status:** ARCHITECTURE FREEZE / LOCAL CANONICAL BASELINE  
> **Implementation Authorization:** `IMPLEMENTATION_AUTHORIZED=NO` (Awaiting human review and sign-off)  
> **Deciders:** Joaquín (Sovereign Principal), SACL Architecture & Consistency Architects  

---

## 1. Canonical Precedence Hierarchy

Every architecture specification, data schema, runtime contract, operational procedure, and automated validation in SACL V1 strictly complies with the following four-tier canonical precedence hierarchy:

```
+==================================================================================================+
|                               SACL CANONICAL PRECEDENCE HIERARCHY                                |
+==================================================================================================+
|  TIER 1: Explicit Joaquín Decisions                                                             |
|          Inviolable baseline decisions established directly by the human sovereign architect.   |
|          Physically codified in this DECISION_BASELINE.md document.                              |
+--------------------------------------------------------------------------------------------------+
|  TIER 2: Proven Current-Orchestrator Behavior                                                    |
|          Validated operational patterns proven on disk in Stable-Ecommerce-Orchestrator.         |
|          (Local Dirty-Root Rule, Worktree Isolation, Non-Killing Timeouts, PID Recycling Guard).  |
+--------------------------------------------------------------------------------------------------+
|  TIER 3: Existing Governance & Contracts                                                         |
|          Codified policies, schemas, freeze remediation baselines, and execution contracts.      |
|          (ARCHITECTURE_INVARIANTS.json, W0.1/W0.2 Freeze Baselines, Machine Governance Headers).  |
+--------------------------------------------------------------------------------------------------+
|  TIER 4: Industry Standards (Undefined Technical Gaps Only)                                      |
|          RFCs, POSIX/Windows conventions, and industry patterns.                                |
|          STANDARDS FILL UNDEFINED TECHNICAL GAPS ONLY. NEVER SILENTLY OVERRIDE TIERS 1-3.       |
+==================================================================================================+
```

### Deterministic Conflict Resolution Rules:
1. **Tier Supremacy:** In any instance where two requirements, recommendations, or configurations conflict, the rule from the higher tier prevails unconditionally.
2. **Prohibition of Silent Overrides:** No agent, script, tool, or documentation update may adopt an industry standard (Tier 4) that weakens, alters, or silently replaces an established invariant from Tiers 1–3.
3. **Standards Fill Gaps Only:** Industry standards and external frameworks apply strictly to fill undefined technical implementation gaps where no explicit decision, proven behavior, or existing contract exists.

---

## 2. Foundational Architecture Decisions Inventory

To preserve strict constitutional provenance, this inventory clearly distinguishes between **Explicit Joaquín Decisions (Tier 1 Sovereign Directives)**, **Inherited Operational Context (Tier 2 Baseline Context)**, and **Derived / Ratified SACL Architecture Decisions (Tier 3 Architecture Synthesis)**:

### 2.1 Baseline Operational Context & History (#1–#9)
The operational history of `Stable-Ecommerce-Orchestrator` on Windows developer workstations established empirical baseline requirements for multi-agent safety, concurrency control, workspace isolation, and result reconciliation.

### 2.2 Explicit Joaquín Decisions (Tier 1 Sovereign Directives)
The following foundational decisions were established directly by the sovereign human principal (Joaquín) and constitute non-negotiable constitutional mandates:

| # | Sovereign Decision / Requirement | Classification | Governing Subsystem | Description & Constitutional Mandate |
| :-: | :--- | :--- | :--- | :--- |
| **10** | **Target Repository** | Repository Scope | Workspace Manager | Target canonical repository is `risejoaquin/solidbit-agent-execution-control-loop` located on host at `C:\Users\Lucilfer\Documents\solidbit-agent-execution-control-loop`. |
| **11** | **Reuse & Refactor Current Orchestrator** | Implementation Strategy | Core Architecture | Reuse and refactor proven scripts and patterns from `Stable-Ecommerce-Orchestrator`; do not start from zero. Preserve battle-tested mechanics. |
| **12** | **ChatGPT Web Control Plane** | Architecture Boundary | Control Plane | ChatGPT Web serves as the Cloud Control Plane for high-level strategic reasoning, execution planning, and wave package authoring. It holds zero host execution privileges and zero private signing secrets. |
| **13** | **Gmail Asynchronous Transport** | Transport Architecture | Transport Gateway | Gmail serves strictly as the cloud-to-local asynchronous store-and-forward transport channel. Gmail is transport only, not execution authority. |
| **14** | **Self-Mail Workflow Supported** | Transport Protocol | Transport Gateway | Sending from and to the same mailbox address (`uniquedraken@gmail.com`) is explicitly supported for asynchronous loopback communication. |
| **15** | **Decoupled Transport & Host Identities** | Security Boundary | Security Model | Gmail transport credentials (OAuth2 via Google APIs; App Passwords removed) reside in Windows Credential Manager and are decoupled from Antigravity user credentials and Git committer identities. |
| **16** | **Process Separation of Gateway & Supervisor** | Process Isolation | Orchestration Core | The Mail Gateway daemon and the orchestrator supervisor daemon (`Graph-P`) execute as separate operating system processes. |
| **17** | **Zero Idle LLM Token Posture** | Resource Conservation | Supervisor Daemon | `Graph-P` supervisor maintains a Zero Idle LLM Token Posture—remaining strictly idle with zero running LLM workers when no jobs are pending. |
| **18** | **Ephemeral Per-Job DAG Engine (`Graph-H`)** | Execution Engine | DAG Scheduler | Ephemeral Directed Acyclic Graph engine (`Graph-H`) is instantiated dynamically per job wave, coordinates phased agent stages with concurrency throttling, and tears down completely upon wave completion. |
| **19** | **Preserve Wave ZIP Package Model** | Distribution Model | Package Specification | Execution packages are distributed as self-contained ZIP archive bundles containing prompts, configurations, contracts, inputs, and schemas. |
| **21** | **Git Worktree Isolation Boundary** | Workspace Isolation | Workspace Manager | Antigravity CLI (`agy.exe`) workers execute strictly inside isolated Git worktrees (`git worktree add -b <branch>`). Execution on `main` or within the primary repository checkout is strictly prohibited. |
| **22** | **SQLite Operational State Store** | State Persistence | State Store | Local relational database (`sacl_ops.db`) operating in Write-Ahead Logging (WAL) mode serves as the single source of operational truth for daemons and workers. |
| **23** | **Heavy Artifacts on Filesystem** | Storage Architecture | Storage Hierarchy | Heavy unstructured artifacts (process stdout/stderr logs, git diff patches, markdown deliverable reports, ZIP packages) reside strictly on disk under `artifacts/runs/<runId>/`; never stored in SQLite. Dual deliverables `SUMMARY.md` and `SUMMARY.json` required. |
| **24** | **Analytics Warehouse Deferred** | Scope Boundary | Data Tier | Long-term analytics data warehousing is explicitly deferred to future releases. V1 focuses strictly on operational execution and audit integrity. |
| **25** | **Remote Production Disabled in V1** | Safety Boundary | Security Policy | Remote production execution is strictly disabled in V1 (fail-closed). No automated merge, push to main, deploy, Jira mutation, Railway mutation, GitHub settings mutation, or production DB mutation is authorized. |

### 2.3 Derived & Ratified SACL Architecture Decisions (Tier 3 Architecture Synthesis)
The following formal decisions were derived through architectural synthesis, security threat modeling, and freeze audit reconciliations (never to be conflated with direct Joaquín decisions):

| Decision Identifier | Domain | Description & Invariant Rule |
| :--- | :--- | :--- |
| **SB-FREEZE-P1-09** | Decision Provenance & Separation | Foundational human directives established directly by Joaquín are strictly separated from derived/ratified SACL architecture decisions. Agent-derived choices must never be upgraded into or claimed as explicit Joaquín decisions. |
| **Decision #20 / SB-FREEZE-P1-10** | Package Task Context Boundary | Packages carry complete, self-contained, and versioned task context (prompts, configurations, schemas, contracts) so execution does not require ad-hoc documentation or prompt discovery. Explicitly configured runtime services (Gmail API, Google Cloud Pub/Sub, Antigravity CLI, Git, and conditionally GitHub when an allowed operation requires it) are permitted by policy and are not prohibited by the self-contained package model. |
| **SB-FREEZE-P1-01 / SB-FREEZE-P2-03** | Gmail Event Ingress & Cursors | Gmail API `users.watch` + Cloud Pub/Sub Pull provides untrusted wake signals; authoritative fetch is performed via Gmail History API (`historyId`). Unread mailbox state is never the source of truth and must not be a gating input. Primary auth is OAuth2 (App Passwords removed). Fallback polling only. |
| **SB-FREEZE-P1-02** | Declarative Package Authority | Packages are declarative in authority and cannot self-authorize attached code (field `authorized_scripts` prohibited). Autoexecution is restricted to trusted handlers in the Local Operation Registry. |
| **SB-FREEZE-P1-03** | Permission Lattice & Hard Deny | Effective runtime permissions equal the four-layer intersection: $\text{Hard Local Policy} \cap \text{Project Policy} \cap \text{Package Requested} \cap \text{Approval Grant}$. Hard deny always wins; approvals cannot override hard denials. |
| **SB-FREEZE-P1-11** | Controlled GitHub Write Semantics | Direct push to `main`/`master`/release is permanently hard denied; merge is hard denied in V1; feature/task branch push and PR creation can occur only through locally trusted operations when project policy, package request, and valid bounded human approval all allow it; W0.3 itself performs no GitHub write. |
| **SB-FREEZE-P1-06 / SB-FREEZE-P2-05** | Bounded Approval Contract | Approvals are strictly bound to `(job_id, action, scope, request_id, expires_at)` and resume the same logical run without spawning disconnected runs. V1 approval channels are `CLI`, `GMAIL`, `MANUAL` (zero public webhooks). |
| **SB-FREEZE-P1-04** | Job Lifecycle & Node States | Canonical 12-state linear job lifecycle, 10 side states/outcomes, and Graph-H node lifecycle states. |
| **SB-FREEZE-P1-05** | 16 Relational State Domains | Relational SQLite operational schema across 16 formal domains in `sacl_ops.db`. |
| **SB-FREEZE-P2-01** | Mandatory Job ID in Manifest | Manifest schema strictly requires `job_id` for routing hint matching and anti-replay deduplication. |
| **SB-FREEZE-P2-02** | Universal Summary Schema | `schemas/summary.schema.json` defines `implementation_authorized` as boolean evidence. |
| **SB-FREEZE-P2-04** | Physical Invariant Evidence | Machine-readable invariants physically codified in `contracts/architecture-invariants.json`. |

---

## 3. Architecture Invariants Codification (`ARCHITECTURE_INVARIANTS.json`)

SACL V1 directly codifies the physical invariants specified in `contracts/architecture-invariants.json`:

### 3.1 Transport Architecture: Gmail as Transport Only
- **Gmail Role:** `gmail_role = "transport_only"`. Gmail provides store-and-forward message transmission; it possesses **zero execution authority**.
- **Authentication:** `auth = "oauth2"`. Gmail API OAuth2 is canonical. App Passwords are permanently removed as a V1 transport credential.
- **Primary Ingress:** `primary_ingress = "gmail_api_users_watch_pubsub_pull"`. The local host subscribes to Google Cloud Pub/Sub via Pull/StreamingPull.
- **No Public Webhook:** `public_webhook = false`. SACL exposes zero inbound HTTP/HTTPS listener ports or public webhooks on the host machine.
- **Wake Signal:** `wake_signal = "pubsub_notification"`. Pub/Sub notifications serve strictly as wake signals indicating new mailbox activity.
- **Authoritative Fetch:** `authoritative_fetch = "gmail_history_api"`. Upon receiving a wake signal, the local Mail Gateway queries the Gmail History API using a locally persisted cursor.
- **Cursor State:** `cursor = "historyId"`. The local SQLite store tracks the latest synchronized `historyId` to guarantee monotonic, gapless message ingestion.
- **Unread State Invariant:** `unread_is_source_of_truth = false`. The unread mailbox state is never the source of truth and must not be a gating input.
- **Startup Reconciliation:** `startup_reconciliation = true`. At startup, the gateway reconciles local `historyId` against the Gmail History API to process any messages received during downtime.
- **Watch Renewal:** `watch_renewal = true`. The gateway daemon automatically renews the `users.watch` lease prior to expiration (typically every 7 days).
- **Periodic Fallback Polling:** `fallback_polling_only = true`. Direct mailbox polling exists strictly as a degraded-mode reconciliation fallback, never as the primary source of truth.

### 3.2 Package Authority & Local Operation Registry
- **Declarative Package Authority:** `declarative = true`. Execution packages are declarative requests; they **never** carry executable authority.
- **No Self-Authorizing Scripts:** `package_may_self_authorize_scripts = false`. Attached scripts (`.ps1`, `.bat`, `.cmd`, `.exe`) within a wave package never become trusted merely through package manifest metadata.
- **Trusted Handlers Owned Locally:** `trusted_handlers_owned_locally = true`. Packages request stable operation IDs. The local SACL host installation owns the trusted operation/handler registry. Effective execution is strictly limited to locally installed handlers whose identity, hash, and profile are trusted by local policy.
- **Self-Contained Task Context & Runtime Services Boundary:** Packages carry complete and versioned task context on disk (prompts, configurations, schemas, and contracts) so local execution does not depend on ad-hoc cloud discovery. Explicitly configured runtime services (Gmail API, Google Cloud Pub/Sub, Antigravity CLI, Git, and conditionally GitHub when policy allows) are permitted runtime boundaries and not prohibited by the self-contained package model.

### 3.3 Effective-Permission Lattice & Hard Deny Rules
Effective runtime permissions are determined by the intersection of four formal policy layers:

$$\text{Effective Permissions} = \text{hard local policy} \cap \text{project policy} \cap \text{package requested permissions} \cap \text{valid approval grant}$$

- **Hard Deny Wins:** `hard_deny_wins = true`. Any prohibition declared in hard local policy unconditionally overrides any grant in lower layers.
- **Approval Cannot Override Hard Deny:** `approval_can_override_hard_deny = false`. A human or automated approval grant cannot expand permissions beyond the hard local policy envelope.
- **Hard Deny Prohibitions (V1):** The hard local policy permanently denies the following actions in V1:
  1. `remote_production_execution` (Railway, production hosts)
  2. `github_merge` (merging pull requests into `main`)
  3. `production_db_write` (mutating production databases)
  4. `secret_export` (dumping credentials or environment variables)
  5. `arbitrary_remote_code` (executing unvetted scripts from packages)
  6. `main_branch_execution` (running agent tasks on `main`)
  7. `primary_checkout_mutation` (modifying human primary git working tree)
  8. `hard_reset` (`git reset --hard` on primary checkout)
  9. `auto_stash` (`git stash` on uncommitted human changes)

### 3.4 Canonical Job Lifecycle & State Domains

#### The 12-State Linear Job Lifecycle:
```
RECEIVED ──► AUTHENTICATED ──► VALIDATED ──► PERSISTED ──► QUEUED ──► DISPATCHED
                                                                         │
COMPLETED ◄── RESULT_SENT ◄── RESULT_PACKAGED ◄── VERIFYING ◄── RUNNING ◄┘
    │
    ▼
ARCHIVED
```

1. `RECEIVED`: Package archive ingested from Gmail transport or local drop.
2. `AUTHENTICATED`: Sender identity and transport transport envelope verified.
3. `VALIDATED`: Manifest schema, requested operations, and checksums verified.
4. `PERSISTED`: Job metadata, package details, and initial state recorded in SQLite.
5. `QUEUED`: Job enqueued awaiting project concurrency lock acquisition.
6. `DISPATCHED`: Project lock acquired; supervisor assigns execution to `Graph-H`.
7. `RUNNING`: `Graph-H` worker fleet actively executing within isolated worktrees.
8. `VERIFYING`: Execution concluded; 4-part reconciliation and diff collision evaluation active.
9. `RESULT_PACKAGED`: Deliverables, evidence, and dual summaries sealed in `response.zip`.
10. `RESULT_SENT`: Result archive dispatched via outbound transport reply.
11. `COMPLETED`: Terminal successful state for fully reconciled run.
12. `ARCHIVED`: Run artifacts moved to long-term archive storage.

#### Job Side States & Admission Outcomes:
- `WAITING_APPROVAL`: Execution halted awaiting bounded action approval grant.
- `RETRY_WAIT`: Scheduled backoff wait before controlled retry attempt.
- `BLOCKED`: Dependency or prerequisite blocked by external condition.
- `FAILED`: Unrecoverable execution error or reconciliation failure.
- `CANCELLED`: User or supervisor initiated controlled job cancellation.
- `INTERRUPTED`: Host restart or daemon crash interrupted active run.
- `TIMED_OUT`: Job exceeded maximum wall-clock threshold.
- `POLICY_DENIED`: Intercepted and blocked by hard local policy or permission lattice.
- `REJECTED`: Invalid manifest, corrupt archive, or untrusted payload at intake.
- `QUARANTINED`: Suspicious payload or path traversal attempt isolated for security review.

#### Graph-H Node States:
- Linear: `PENDING` $\rightarrow$ `READY` $\rightarrow$ `RUNNING` $\rightarrow$ `SUCCEEDED`.
- Side outcomes: `RETRYABLE_FAILURE`, `FAILED`, `BLOCKED`, `WAITING_APPROVAL`, `CANCELLED`.

### 3.5 Bounded Action Approval Contract
When execution requires human approval, the grant is strictly bounded:
- **Binding Tuple:** `approval_binding = ["job_id", "action", "scope", "request_id", "expires_at"]`.
- **Resume Semantics:** Approval resumes the **same logical run**; it does not spawn an unlinked orphan run.
- **Policy Envelope Invariant:** An approval cannot grant permissions exceeding the hard local policy envelope (`approval_can_override_hard_deny = false`).
- **Approval Channels (V1):** `approval_channels_v1 = ["CLI", "GMAIL", "MANUAL"]`. Webhooks are excluded from V1 as no public inbound listening endpoints exist on the host workstation.

### 3.6 Operational State Domains (16 SQLite Tables)
The local SQLite store (`sacl_ops.db`) maintains relational operational state across exactly 16 structured domains:
1. `schema_migrations`: Forward-only schema version tracking and migration history.
2. `projects`: Registered local repositories, canonical roots, and security tiers.
3. `packages`: Ingested package hashes, operation IDs, and metadata.
4. `mail_messages`: Inbound/outbound transport messages, nonces, and `historyId` cursors.
5. `jobs`: Logical job lifecycle state, parameters, and routing hints.
6. `runs`: Concrete execution run attempts, verdicts, and timings.
7. `graph_nodes`: Ephemeral DAG node definitions and topological dependencies.
8. `node_attempts`: Execution attempts per graph node with process metadata.
9. `agents`: Agent execution records, worktree bindings, PIDs, and exit codes.
10. `events`: Append-only structured audit event trail (`audit_events`).
11. `approvals`: Bounded approval requests, grants, and expiration timestamps.
12. `artifacts`: Filesystem artifact references, relative paths, byte sizes, and SHA-256 hashes.
13. `results`: Canonical verdict records, extracted regex markers, and reconciliation data.
14. `leases`: Distributed mutual exclusion leases (`supervisor_locks`, project locks).
15. `heartbeats`: Periodic liveness timestamps for active supervisor and worker processes.
16. `errors`: Structured diagnostic error logs, exception traces, and failure taxonomies.

- **Connection Bootstrap:** Every SQLite connection bootstrap executes:
  ```sql
  PRAGMA journal_mode = WAL;
  PRAGMA busy_timeout = 5000;
  PRAGMA synchronous = NORMAL;
  PRAGMA foreign_keys = ON;
  ```

### 3.7 Storage Hierarchy: Filesystem vs. Database
- `heavy_artifacts_on_filesystem = true`.
- Heavy unstructured streams (raw process stdout/stderr logs, git diff patches, markdown deliverable reports, ZIP archives) reside strictly on the local filesystem under `artifacts/runs/<runId>/`.
- SQLite stores metadata, relational foreign keys, checksums, and relative filesystem pointers.
- Mandatory dual deliverables: every run produces both `SUMMARY.md` (human) and `SUMMARY.json` (machine).

### 3.8 Four-Part Run Status Reconciliation
Run verdict is **never** determined by process exit code alone (`process_exit_code_alone_is_authoritative = false`).
Reconciliation requires four distinct verification factors:
1. `process_observation`: OS process health check, whitelist validation, and exit code capture.
2. `persisted_state`: Verification of SQLite records, timestamps, and worktree states.
3. `required_outputs`: Verification of physical existence and non-zero byte size of deliverable markdown reports.
4. `final_verdict`: Regex marker extraction (`^(?:AGENT_[A-Z0-9_-]+_RESULT|RESULT|FINAL_RESULT)\s*=\s*(PASS|PARTIAL|BLOCKED)`).

- **Fallback Invariant:** Clean exit (code 0) with valid report on disk lacking regex marker evaluates to `'PASS (Report Present)'`.
- **Review Semantics:** `DONE_REVIEW_REQUIRED` indicates execution finished at an authorized boundary requiring human review; it **never** means `PASS`.

### 3.9 Controlled GitHub Write Semantics
In strict adherence to `contracts/architecture-invariants.json`:
- **Direct Push Hard Denied:** Direct git push to `main`, `master`, or release branches is permanently hard denied (`direct_main_push_hard_denied = true`).
- **Merge Hard Denied in V1:** Automated git merge and automated PR merging are permanently hard denied in V1 (`merge_hard_denied_v1 = true`).
- **Controlled Feature Branch Push & PR Creation:** Feature/task branch push and PR creation can occur only through locally trusted operations when all four conditions are met:
  1. Project policy explicitly allows it (`project_policy`);
  2. Ingested package requests it (`package_requested_permissions`);
  3. A valid bounded human approval grant authorizes it (`valid_approval_grant`);
  4. The operation executes via an authoritative, locally trusted handler in the local operation registry.
- **W0.3 Freeze Execution Posture:** Wave W0.3 itself performs zero GitHub writes (`IMPLEMENTATION_AUTHORIZED=NO`).

---

## 4. Concurrency Baseline & Hierarchical Locking

### 4.1 Concurrency Baseline Invariant
- **Mutating Jobs:** Initially, exactly **one mutating job per project** is permitted to execute at any given time.
- **Read-Only Coexistence:** Safe read-only work (monitoring, audit inspection, status queries, static preflights) may coexist concurrently with an active mutating job.

### 4.2 Hierarchical Lock Model
Mutual exclusion is coordinated through a five-tier hierarchical lock ladder:

```
[SYSTEM LOCK]      ── Supervisor Singleton Lease (Graph-P daemon)
      │
[PROJECT LOCK]     ── One mutating job per project; concurrent read-only allowed
      │
[REPO LOCK]        ── Primary Git repository mutual exclusion for worktree provisioning
      │
[WORKTREE LOCK]    ── Agent-exclusive lock on isolated worktrees/wt-<agentId>/
      │
[RESOURCE LOCK]    ── Fine-grained locks for shared ports, test databases, or build caches
```

1. **System Lock (`SUPERVISOR_SINGLETON`):** Global machine lease ensuring exactly one active `Graph-P` supervisor daemon. Heartbeat TTL: 60 seconds; refreshed every 10 seconds.
2. **Project Lock (`PROJECT_<projectId>`):** Project-level mutual exclusion lock. Grants exclusive access for mutating jobs or shared access for read-only tasks.
3. **Repo Lock (`REPO_<repoId>`):** Git repository-level lock protecting `.git` common directory operations (e.g. `git worktree add`, `git worktree remove`) from Git index contention.
4. **Worktree Lock (`WORKTREE_<agentId>`):** Exclusive lock on an individual agent's dedicated worktree directory (`worktrees/wt-<agentId>/`).
5. **Resource Lock (`RESOURCE_<resourceId>`):** Targeted locks on shared host resources (e.g. local test databases, compilation ports).

---

## 5. Project Registry Authority for Filesystem Roots

### 5.1 Local Authority Invariant
The local **Project Registry** (`config/projects.json`, conforming to `schemas/project-registry.schema.json`) is the **sole local authority for local filesystem roots**:
- A wave package identifies a registered project (`project_id`) and may request a target repository path (`target_local_repo`).
- **Inviolable Security Boundary:** A package **must not be able to redirect execution to an arbitrary path** outside local registry policy.
- If a package requests a path that does not match the registered `target_local_repo` (or does not reside within declared `allowed_target_roots`), the Policy Engine rejects the job fail-closed with `POLICY_DENIED_UNAUTHORIZED_TARGET_ROOT`.

### 5.2 Local Dirty-Root Rule
- Uncommitted human work in the primary product checkout (`.git` common dir) is **never destroyed, stashed, or reset**.
- If the primary checkout contains uncommitted changes (`git status --porcelain` is non-empty), worktree provisioning halts immediately and raises `DIRTY_ROOT_HALT`.
- Automation never runs `git reset --hard`, `git clean -fd`, `git checkout .`, or automatic `git stash`.

---

## 6. Legacy Orchestrator Lifecycle Transition Policy

The operational relationship between `Stable-Ecommerce-Orchestrator` and SACL V1 is governed by strict transition phases:

1. **Operational Parity Phase (Current):**
   - The legacy `Stable-Ecommerce-Orchestrator` (`C:\Users\Lucilfer\Documents\Stable-Ecommerce-Orchestrator`) **remains fully operational and untouched**.
   - No scripts, configs, or state files in the legacy orchestrator may be deleted or modified during SACL V1 development.
2. **E2E Certification Gate:**
   - SACL V1 must achieve full functional parity across all 18 evaluated capabilities and pass the complete 8-step End-to-End Certification Suite (`docs/E2E_CERTIFICATION_PLAN.md`).
3. **Archive & Read-Only Transition:**
   - Only after explicit human sign-off confirming SACL parity and successful E2E certification does `Stable-Ecommerce-Orchestrator` transition to **archived / read-only** status.

---

## 7. Governance Status & Safety Declaration

```properties
DECISION_BASELINE_VERSION = 1.0.0
SCHEMA                    = solidbit.architecture-invariants.v1
PRECEDENCE_LEVELS         = 4 (Explicit Decisions > Proven Behavior > Governance > Industry Standards)
REMOTE_PRODUCTION         = DISABLED_FAIL_CLOSED
MUTATING_CONCURRENCY      = 1_PER_PROJECT
GMAIL_INGRESS             = users.watch + Cloud Pub/Sub Pull + historyId
PACKAGE_SCRIPTS           = DECLARATIVE_ONLY (LOCAL_HANDLERS_AUTHORITATIVE)
LEGACY_ORCHESTRATOR       = UNTOUCHED_UNTIL_E2E_CERTIFIED
IMPLEMENTATION_AUTHORIZED = NO
STATUS                    = ARCHITECTURE_FREEZE_CONSISTENT
```

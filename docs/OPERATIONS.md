# SACL V1 Supervisor & Runtime Operations Manual (OPERATIONS)

**Document ID:** SACL-OPS-V1-MANUAL  
**Status:** ARCHITECTURE FREEZE / LOCAL CANONICAL BASELINE  
**Authoritative Precedence:** Explicit Joaquín Decisions > Proven Current-Orchestrator Behavior > SolidBit Governance > Industry Standards (Undefined Technical Gaps Only)  

---

## 1. System Topology & Architectural Boundaries

The SolidBit Agent Execution Control Loop (SACL V1) orchestrates autonomous AI coding workflows across local Windows execution environments while bridging to cloud intelligence via an asynchronous event-driven transport layer.

```
+-----------------------------------------------------------------------------+
|                               CHATGPT WEB                                   |
|                        (Human Strategic Control Plane)                      |
|  - Prompts, execution planning, wave package authoring                      |
|  - Zero local host permissions, zero private signing secrets                |
+-----------------------------------------------------------------------------+
                                       │
                         (Email with Package ZIP)
                                       ▼
+-----------------------------------------------------------------------------+
|                        GMAIL & GOOGLE CLOUD PUB/SUB                         |
|  - Gmail API users.watch triggers Cloud Pub/Sub wake notification           |
|  - Local pull subscriber receives notification as wake signal (no webhook)  |
+-----------------------------------------------------------------------------+
                                       │
                             (Pub/Sub Wake Signal)
                                       ▼
+-----------------------------------------------------------------------------+
|                            MAIL GATEWAY SERVICE                             |
|          (uniquedraken@gmail.com - Zero LLM, Zero Antigravity Worker)       |
|  - Subscribes to Pub/Sub pull queue; queries Gmail History API (historyId)  |
|  - Validates ZIP anti-traversal & SHA-256; stores message in mail_messages  |
|  - Fallback polling only for degraded-mode reconciliation                   |
+-----------------------------------------------------------------------------+
                                       │
                               (Enqueues Job Event)
                                       ▼
+-----------------------------------------------------------------------------+
|                         GRAPH-P (Persistent Supervisor)                     |
|  - Long-running local supervisor daemon                                     |
|  - Maintains SQLite system lease (leases table / SUPERVISOR_SINGLETON)      |
|  - Strictly IDLE when no job executes (ZERO LLM tokens consumed)            |
|  - Validates Project Registry authority & Local Dirty-Root Rule             |
|  - Enforces project lock (1 mutating job per project; read-only coexists)   |
+-----------------------------------------------------------------------------+
                                       │
                              (Spawns Ephemeral Run)
                                       ▼
+-----------------------------------------------------------------------------+
|                         GRAPH-H (Ephemeral Per-Job DAG)                     |
|  - Job-scoped DAG execution engine (torn down upon completion)              |
|  - Creates isolated Git worktrees (main branch disallowed)                  |
|  - Spawns governed Antigravity workers (WORKER.ps1 wrapping agy.exe)        |
|  - Reconciles 4-part state; detects file overlap; writes filesystem outputs |
+-----------------------------------------------------------------------------+
                                       │
                           (Completion / Failure Response)
                                       ▼
+-----------------------------------------------------------------------------+
|                         MAIL GATEWAY DISPATCHER                             |
|  - Packages artifacts/runs/<runId>/ into response archive                   |
|  - Embeds SUMMARY.md in email body; includes SUMMARY.json                   |
|  - Dispatches reply via Gmail API (users.messages.send) to uniquedraken@gmail.com |
+-----------------------------------------------------------------------------+
```

---

## 2. Transport Protocol, Semantics & Ingress

### 2.1 Transport Boundaries & Identity Isolation
- **Target Mailbox:** `uniquedraken@gmail.com`.
- **Identity Decoupling:** Gmail authentication credentials reside in Windows Credential Manager and are completely decoupled from Antigravity user credentials and Git committer identities.
- **Self-Mail Pattern:** Sending from and to `uniquedraken@gmail.com` is explicitly supported per Decision Baseline #14.

### 2.2 Ingress Architecture: Event-Driven Pub/Sub & History API
In accordance with `ARCHITECTURE_INVARIANTS.json`:
- **Gmail Role:** Transport only; zero host execution authority.
- **Primary Ingress:** Gmail API `users.watch` paired with Google Cloud Pub/Sub pull subscription (`primary_ingress = "gmail_api_users_watch_pubsub_pull"`).
- **Zero Inbound Ports:** No public webhook listeners or inbound ports are opened on the host (`public_webhook = false`).
- **Wake Signal:** Local background subscriber receives Pub/Sub pull notification as a wake signal (`wake_signal = "pubsub_notification"`).
- **Authoritative Fetch:** Upon receiving wake notification, the gateway queries the Gmail History API (`authoritative_fetch = "gmail_history_api"`) using the persisted cursor.
- **Cursor Management:** Monotonic cursor `historyId` is recorded transactionally in SQLite table `mail_messages`.
- **Startup Reconciliation:** On daemon bootstrap, the gateway reconciles unhandled messages from `historyId` forward (`startup_reconciliation = true`).
- **Watch Renewal:** Daemon automatically renews the `users.watch` subscription prior to expiration (`watch_renewal = true`).
- **Degraded Fallback Only:** Periodic mailbox polling exists strictly as a degraded-mode reconciliation fallback (`fallback_polling_only = true`), never as primary ingress.

### 2.3 Delivery Semantics & Idempotency
- **At-Least-Once Delivery:** The transport layer guarantees at-least-once delivery. The local Mail Gateway and Policy Engine are idempotent consumers.
- **Deduplication Invariant:**
  - **Same `JOB_ID` + Same Package Hash:** Idempotently ignored as a benign re-delivery.
  - **Same `JOB_ID` + Different Package Hash:** Rejected as an unresolvable payload conflict.
  - **Controlled Retry:** Re-submitting the same job requires generating a new unique nonce, creating a new run attempt record.

### 2.4 Subject Routing vs. Package Authority
- **Routing Hint Only:** The email subject line serves purely as a transport routing hint; **it is never an authority source**.
- **Canonical Routing Syntax:**
  ```text
  [SACL][JOB][v1][<JOB_ID>] <Optional Description>
  ```
- **Declarative Package Authority:** Packages are untrusted input. Packages declare requested operations, but **attached scripts never self-authorize**. Trusted operation handlers are owned locally by the host installation.

---

## 3. Storage Architecture & Operational Database (`sacl_ops.db`)

### 3.1 Dual-Tier Storage Topology
1. **Operational State Store (`sacl_ops.db`):** Local SQLite relational database configured with Write-Ahead Logging (`WAL`) mode, storing transactional leases, runs, DAG stages, agent execution states, process PIDs, file modification registries, and transport queues across 16 formal operational domains.
2. **Filesystem Heavy Artifact Store:** In adherence to Decision Baseline #23, heavy artifacts **never enter SQLite**. Worker stdout/stderr logs, full markdown reports, git diffs, and ZIP bundles reside strictly on disk under `artifacts/runs/<runId>/`.

### 3.2 Relational DDL Architecture
The operational database enforces relational referential integrity across 16 domains:
`schema_migrations`, `projects`, `packages`, `mail_messages`, `jobs`, `runs`, `graph_nodes`, `node_attempts`, `agents`, `events`, `approvals`, `artifacts`, `results`, `leases`, `heartbeats`, `errors`.

---

## 4. Concurrency Baseline & Hierarchical Locking Operations

### 4.1 Concurrency Baseline Invariant
- **Mutating Jobs:** Initially, exactly **one mutating job per project** is permitted to execute at any given time.
- **Read-Only Coexistence:** Safe read-only work (monitoring, audit inspection, status queries, static preflights) may coexist concurrently with an active mutating job.

### 4.2 Hierarchical Lock Ladder
Operations enforce locks in strict hierarchical order:
1. **System Lock (`SUPERVISOR_SINGLETON`):** Singleton lease held by `Graph-P` in SQLite table `leases`. Refreshed every 10 seconds; TTL 60 seconds.
2. **Project Lock (`PROJECT_<projectId>`):** Acquired before dispatching a wave. Exclusive for mutating runs; shared for read-only tasks.
3. **Repo Lock (`REPO_<repoId>`):** Short-lived lock serializing Git common directory administrative mutations (`git worktree add/remove`).
4. **Worktree Lock (`WORKTREE_<agentId>`):** Exclusive lease on private worktree directory and Git index.
5. **Resource Lock (`RESOURCE_<resourceId>`):** Fine-grained lock for shared host ports or test fixtures.

---

## 5. Project Registry Authority for Filesystem Roots

### 5.1 Local Authority Invariant
The local Project Registry (`config/projects.json`, conforming to `schemas/project-registry.schema.json`) is the **sole local authority for local filesystem roots**:
- A package identifies a registered project (`project`) and may request a target path (`target_local_repo`).
- **Non-Redirection Invariant:** A package **must not be able to redirect execution to an arbitrary path** outside local registry policy.
- If a package requests an unauthorized target path differing from the registered repository path (or outside declared `allowed_target_roots`), the orchestrator immediately halts fail-closed with `POLICY_DENIED_UNAUTHORIZED_TARGET_ROOT`.

### 5.2 Inviolable Local Dirty-Root Rule
- Human uncommitted work in the primary product checkout is **never destroyed, stashed, or reset**.
- Prior to creating worktrees or launching agents, the orchestrator inspects the primary repository checkout:
  ```powershell
  $dirty = git -C $primaryRepo status --porcelain
  if ($dirty) {
      throw "DIRTY_ROOT_HALT: Uncommitted human modifications detected in primary checkout. Orchestrator will not overwrite, stash, or reset human work."
  }
  ```
- Any presence of uncommitted human changes causes an immediate, safe abort (`DIRTY_ROOT_HALT`).

---

## 6. Process Lifecycle, Safe Stop & Diagnostic Timeouts

### 6.1 Non-Killing Diagnostic Timeout Invariant
When an agent exceeds its allotted execution duration (`timeout_minutes`):
- The supervisor updates the agent record to `status = 'TIMEOUT_RUNNING'`.
- A diagnostic alert is logged to `events`.
- **The worker process is NEVER terminated automatically.**
- *Rationale:* Hard killing (`Stop-Process -Force`) destroys transient LLM reasoning context, corrupts git worktrees, and leaves unparseable partial deliverables. The process remains alive for human inspection.

### 6.2 Controlled Safe Stop Playbook
When an operator needs to terminate one or all agents:
1. Run `scripts/stop-agents.ps1 <AgentId>` or `scripts/STOP.ps1`:
   - The script queries `sacl_ops.db` for the agent's recorded PID.
   - Executes the 3-way check (`Test-AgentProcessRunning`) to verify that the OS process matches the whitelisted image and start time.
   - Issues a graceful `Stop-Process` followed by force termination if unresponsive.
   - Updates `agents.status = 'STOPPED'` and `agents.result_verdict = 'STOPPED_BY_USER'`.
   - Releases worktree locks and records audit event `STOPPED_BY_USER`.

---

## 7. Remote Production Execution Disabled (Fail-Closed)

In accordance with Decision Baseline #25 and ADR-012:
- **Remote production execution is strictly disabled in V1.**
- Any commands or tool invocations attempting to communicate with:
  - Railway production deployments (`railway up`, `railway variables`)
  - Jira live transitions or issue mutations (`acli worklog`, `acli updateIssue`)
  - GitHub production ruleset / branch protection mutations
  - Production database mutations
- Are **fail-closed** and blocked by policy. Scripts generate local dry-run plan files (`.plan.json` / `.plan.md`) instead of executing remote calls.

---

## 8. Human Action Gate Protocol

Automated agents cannot self-authorize irreversible actions:
1. Upon completing a wave, `Graph-H` evaluates deliverable reports and file overlap.
2. If all acceptance criteria pass, the system emits the structured authorization request artifact:
   `artifacts/runs/<runId>/evidence/FINAL_DEVELOPMENT_AUTHORIZATION.txt`.
3. Canonical format:
   ```text
   FUNCTIONAL_DEVELOPMENT = NOT_AUTHORIZABLE
   ARCHITECTURE_FREEZE    = NOT_YET_PASS
   REMAINING_BLOCKERS     = NONE
   NEXT_SAFE_ACTION       = HUMAN_CODE_REVIEW_AND_REPO_INITIALIZATION
   ```
4. Code merges into `main` or production branch transitions remain impossible until an explicit human operator reviews the changes and signs off.

---

## 9. Real-Time Terminal Console Monitor (`MONITOR.ps1`)

Operators observe ongoing execution without taking database write locks or interrupting workers:
1. `MONITOR.ps1` opens `sacl_ops.db` in read-only mode (`Data Source=sacl_ops.db;Mode=ReadOnly;` or `file:sacl_ops.db?mode=ro`).
2. Refreshes every 10 seconds:
   - Displays Run ID, Package ID, Active Phase, and Concurrency (`MaxParallel`).
   - Renders live agent status table: `Agent | Status | PID | Exit | Report | Verdict | Elapsed`.
   - Displays real-time hierarchical leases and file collision alerts.
3. Exiting via `Ctrl+C` terminates only the monitor dashboard without affecting executing workers.

---

## 10. Legacy Orchestrator Lifecycle Transition Policy

The operational relationship between `Stable-Ecommerce-Orchestrator` and SACL V1 is governed by strict transition phases:

1. **Untouched / Fully Operational Phase (Current):**
   - The legacy `Stable-Ecommerce-Orchestrator` (`/workspace\Stable-Ecommerce-Orchestrator`) **remains untouched and fully operational**.
   - It remains available as the proven fallback runtime while SACL V1 is constructed.
2. **Parity & E2E Certification Gate:**
   - SACL V1 must achieve full functional parity across all 18 evaluated capabilities and pass the complete 8-step End-to-End Certification Suite (`docs/E2E_CERTIFICATION_PLAN.md`).
3. **Archive & Read-Only Transition:**
   - Only after explicit human sign-off confirming SACL parity and successful E2E certification does `Stable-Ecommerce-Orchestrator` transition to **archived / read-only** status.

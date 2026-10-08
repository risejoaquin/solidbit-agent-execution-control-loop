# SolidBit Agent Execution Control Loop (SACL V1)

> **Specification Status:** Architecture Materialized & Frozen for V1  
> **Constitutional Baseline:** [`DECISION_BASELINE.md`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/DECISION_BASELINE.md)  
> **Implementation Authorization:** `IMPLEMENTATION_AUTHORIZED=NO` (Awaiting human review and sign-off)  
> **Safety Mode:** Fail-Closed Staging / Remote Production Execution Disabled in V1  

---

## 1. Executive Overview

The **SolidBit Agent Execution Control Loop (SACL V1)** is a deterministic, governed multi-agent execution control loop for Antigravity AI coding agents (`agy.exe`) operating on Windows host workstations. SACL decouples high-level strategic reasoning and wave package authoring—handled by the **Cloud Control Plane (ChatGPT Web)**—from local host execution via asynchronous store-and-forward transport (**Gmail** `uniquedraken@gmail.com`).

Locally, SACL enforces uncompromising security and operational stability through:
- An isolated **Mail Gateway** daemon handling inbound package ingestion via event-driven **Gmail API `users.watch`** and **Google Cloud Pub/Sub Pull** notifications, authoritative history fetching with monotonic `historyId` cursors, and zero execution privileges.
- A **Policy & Validation Engine** enforcing the effective-permission lattice (`hard local policy ∩ project policy ∩ package requested permissions ∩ valid approval grant`), environment preflights, package manifest schemas, branch inviolability (`MAIN_BRANCH_NOT_ALLOWED`), primary checkout isolation (`PRIMARY_CHECKOUT_NOT_ALLOWED`), and the inviolable **Local Dirty-Root Rule**.
- A local **Operational State Store (SQLite `sacl_ops.db`)** operating in Write-Ahead Logging (WAL) mode across **16 structured operational domains** for ACID transaction management, instance leasing, and agent lifecycle state tracking.
- A persistent supervisor daemon (**`Graph-P`**) maintaining a **Zero Idle LLM Token Posture**—remaining strictly idle with zero running LLM workers when no jobs are pending.
- An ephemeral Directed Acyclic Graph execution engine (**`Graph-H`**) instantiated per job wave, executing phased agent stages with concurrency throttling (`$MaxParallel`), injecting immutable machine governance headers, and tearing down upon wave completion.
- A **Filesystem Artifact Store** retaining heavy unstructured logs, git diffs, reports, and dual summaries (`SUMMARY.md` and `SUMMARY.json`) strictly on disk under `artifacts/runs/<runId>/`.
- A **Multi-Project Engine** governed by the local **Project Registry**, which acts as the sole local authority for filesystem roots, restricting packages from redirecting execution outside local registry policy.
- A **Concurrency Baseline** restricting execution initially to **one mutating job per project** while permitting concurrent read-only operations, coordinated via hierarchical locks (`system/project/repo/worktree/resource`).
- A strict **Human Authority Gate** emitting `FINAL_DEVELOPMENT_AUTHORIZATION.txt`, with precisely defined **Controlled GitHub Write Semantics**: direct push to `main`/`master`/release is permanently hard denied, merge is hard denied in V1, while feature/task branch push and PR creation require locally trusted operations, project policy, requested package permissions, and valid bounded human approval (W0.3 itself performs zero GitHub writes).
- A **Local Kill Switch** (`STOP.ps1`) coupled with proven non-killing diagnostic timeouts (`TIMEOUT_RUNNING`) and 3-way PID recycling defense.
- A defined **Legacy Transition Policy**: `Stable-Ecommerce-Orchestrator` remains fully operational and untouched until SACL achieves verified parity and passes E2E certification, after which it transitions to archive / read-only.

---

## 2. Canonical Precedence Hierarchy

Every design, implementation detail, schema, and operational behavior in SACL V1 strictly complies with the four-level canonical precedence hierarchy codified in [`DECISION_BASELINE.md`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/DECISION_BASELINE.md):

```
+==================================================================================================+
|                               SACL CANONICAL PRECEDENCE HIERARCHY                                |
+==================================================================================================+
|  TIER 1: Explicit Joaquín Decisions                                                             |
|          Inviolable baseline decisions established directly by the human sovereign architect.   |
|          Physically codified in DECISION_BASELINE.md.                                            |
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

1. **Explicit Joaquín Decisions:** Inviolable user decisions captured in `DECISION_BASELINE.md` (ChatGPT Web control plane, Gmail transport, `sacl_ops.db` SQLite store, Graph-P idle posture, Graph-H ephemeral DAG, remote production disabled in V1, etc.).
2. **Proven Current-Orchestrator Behavior:** Validated disk evidence and production mechanics proven in `Stable-Ecommerce-Orchestrator` (worktree isolation, local dirty-root rule, non-killing timeouts, PID recycling defense, regex result markers, cross-agent diff collision checks).
3. **Existing Governance & Contracts:** Repository contracts, machine guard headers (`GOVERNED_EXECUTION=TRUE`), permission lattice, and human gate requirements.
4. **Industry Standards (Undefined Technical Gaps Only):** RFC and POSIX/Windows conventions applied exclusively to fill undefined technical implementation gaps without overriding higher-level rules.

---

## 3. Core Subsystems & Architecture Overview

```mermaid
flowchart LR
    subgraph Cloud [Cloud Control Plane]
        CPT["ChatGPT Web<br>(Strategic Planning & Packaging)"]
    end

    subgraph Transport [Asynchronous Event-Driven Transport]
        GM["Gmail (uniquedraken@gmail.com)<br>Gmail API users.watch"]
        PS["Google Cloud Pub/Sub<br>(Pull / StreamingPull Queue)"]
    end

    subgraph Host [Local Host Execution Environment]
        MG["Mail Gateway Daemon<br>(Pub/Sub Wake & History Fetch)"]
        POL["Policy & Validation Engine<br>(Permission Lattice & Dirty-Root)"]
        DB[("Operational State Store<br>sacl_ops.db (16 Domains, WAL)")]
        GP["Graph-P Persistent Supervisor<br>(Hierarchical Leases & IDLE Daemon)"]
        GH["Graph-H Ephemeral DAG Engine<br>(Phased Stages & Concurrency)"]
        FS[("Filesystem Artifact Store<br>artifacts/runs/<runId>/")]
        WRK["Worker Controller<br>(agy.exe + Machine Guards)"]
        MON["MONITOR.ps1<br>(Read-Only Console Dashboard)"]
        GATE["Human Authority Gate<br>(FINAL_DEVELOPMENT_AUTHORIZATION.txt)"]
    end

    CPT -->|1. Inbound Wave ZIP| GM
    GM -->|2. users.watch Wake Notification| PS
    PS -->|3. Pub/Sub Pull Wake Signal| MG
    MG -->|4. Authoritative History API (historyId)| GM
    MG -->|5. Register Inbound Job & Stage ZIP| DB
    MG -.->|6. Wakeup Signal| GP
    GP -->|7. Acquire Project Lease & Validate| POL
    POL -->|8. Preflight & Dirty-Root Check| DB
    GP -->|9. Spawn Ephemeral DAG| GH
    GH -->|10. Manage Worktrees & Workers| WRK
    WRK -->|11. Stream Logs & State| DB
    WRK -->|12. Heavy Artifacts & Reports| FS
    GH -->|13. Cross-Agent Overlap Evaluation| DB
    GH -->|14. Generate Dual Summaries| FS
    GH -->|15. Complete & Tear Down| GP
    GP -->|16. Check Authorization Boundary| GATE
    GP -->|17. Update Status COMPLETED| DB
    MG -->|18. Package Response & Send via Gmail API| GM
    GM -->|19. Result ZIP| CPT
    MON -.->|Read-Only Inspection mode=ro| DB
```

### Subsystem Summary

| Subsystem | Role | Primary Invariants |
| :--- | :--- | :--- |
| **Control Plane (ChatGPT Web)** | Strategic planning, prompt engineering, task decomposition, runnable wave package authoring. | Zero host credentials; zero direct local network access; authoring boundary only. |
| **Gmail & Pub/Sub Transport** | Asynchronous event-driven communication channel via `uniquedraken@gmail.com`. | Transport only, not authority; primary ingress via `users.watch` + Pub/Sub pull; `historyId` cursor; OAuth2 auth (App Passwords removed); unread state never source of truth; fallback polling only. |
| **Mail Gateway** | Edge intake daemon pulling Pub/Sub wake signals and fetching Gmail history. | Zero execution privilege; strict ZIP path sanitization (Anti-ZipSlip); deduplication on `(message_id, nonce)`. |
| **Policy Engine** | Preflight gatekeeper verifying tooling, manifest schemas, and repo state. | Effective-permission lattice (`hard deny` always wins); Local Dirty-Root Rule; `MAIN_BRANCH_NOT_ALLOWED`; `PRIMARY_CHECKOUT_NOT_ALLOWED`. |
| **Project Registry** | Local authority for local filesystem roots. | Governs repository bindings and canonical roots; packages cannot redirect execution outside local registry policy. |
| **Graph-P Supervisor** | Persistent local supervisor maintaining singleton lease and state coordination. | Zero Idle LLM Token Posture (remains IDLE when no pending jobs); 1 mutating job per project; SQLite hierarchical leasing. |
| **Graph-H DAG Runner** | Ephemeral DAG execution engine dynamically spawned per job wave. | Phased topological stages; `$MaxParallel` concurrency throttling; machine governance injection; full teardown on seal. |
| **Operational State Store** | Local relational database (`sacl_ops.db`) in WAL mode across 16 domains. | Single source of operational truth; ACID transactions; 3-way PID recycling checks; forward-only schema migrations. |
| **Filesystem Artifact Store** | Structured directory storage under `artifacts/runs/<runId>/`. | Heavy artifacts (logs, diffs, reports) never enter SQLite; dual deliverables `SUMMARY.md` and `SUMMARY.json`. |
| **Human Authority Gate** | Safety boundary guarding all irreversible operations. | Emits `FINAL_DEVELOPMENT_AUTHORIZATION.txt`; no autonomous merges/deploys; remote production disabled in V1. |
| **Local Kill Switch** | Emergency process control (`STOP.ps1`). | Respects non-killing diagnostic timeouts (`TIMEOUT_RUNNING`); 3-way verified process termination. |

---

## 4. Repository Layout & Target Directory Structure

```
solidbit-agent-execution-control-loop/
├── DECISION_BASELINE.md                           # Constitutional baseline & architecture invariants (Root Authority)
├── README.md                                      # Repository overview and entrypoint (this document)
├── contracts/                                     # Machine-readable architecture invariants (architecture-invariants.json)
├── docs/                                          # Canonical architectural governance documents
│   ├── ARCHITECTURE.md                            # Comprehensive system architecture & ADR set (001-014)
│   ├── AUTHORITY_MODEL.md                         # Human authority model, permission lattice, and gating
│   ├── CONCURRENCY_AND_LOCKING.md                 # Hierarchical locks, 1 mutating job per project, SQLite WAL
│   ├── CURRENT_ORCHESTRATOR_COMPATIBILITY_MATRIX.md # Detailed audit and migration mapping of legacy capabilities
│   ├── E2E_CERTIFICATION_PLAN.md                  # Sandboxed 8-step test certification & legacy transition gate
│   ├── EXECUTION_PACKAGE_SPEC.md                  # Declarative runnable wave package specification
│   ├── FREEZE_REMEDIATION.md                      # Audit finding remediation & freeze reconciliation report
│   ├── MAIL_PROTOCOL.md                           # Inbound/outbound email transport, Pub/Sub, routing hints
│   ├── OBSERVABILITY.md                           # 16 SQLite domains, 4-part reconciliation, dual deliverables
│   ├── OPERATIONS.md                              # Host operations, daemon lifecycle, and deployment guide
│   ├── RECOVERY_MODEL.md                          # Cold-start crash recovery, orphan reconciliation, idempotency
│   ├── RESULT_PROTOCOL.md                         # 4-factor reconciliation, regex markers, legacy fallbacks
│   ├── RETRY_AND_TIMEOUT_POLICY.md                # Non-killing timeouts, exponential backoff, retry rules
│   ├── SECURITY_MODEL.md                          # Defense-in-depth, Anti-Zip Slip, secretless control plane
│   ├── SQLITE_DATA_MODEL.md                       # DDL schema across 16 domains, WAL PRAGMAs, indexing
│   ├── STATE_MACHINE.md                           # 12-state canonical job lifecycle and graph node state machine
│   ├── THREAT_MODEL.md                            # STRIDE vulnerability analysis across 5 trust boundaries
│   ├── TRACEABILITY_MATRIX.md                     # Bidirectional traceability from decisions to verification
│   └── adr/                                       # Architectural Decision Records (ADR-001 through ADR-014)
├── schemas/                                       # JSON Schema Draft 2020-12 specifications
│   ├── project-registry.schema.json               # Local authority for project roots and concurrency policy
│   ├── manifest.schema.json                       # Package manifest specification (requires job_id)
│   ├── hard-policy.schema.json                    # Hard local policy schema
│   ├── approval.schema.json                       # Bounded action-approval schema
│   ├── summary.schema.json                        # Universal run summary schema
│   └── ...
├── examples/                                      # Valid JSON example instances validating against schemas
│   ├── project-registry.valid.json
│   ├── manifest.valid.json
│   └── ...
├── db/                                            # Database migrations
│   └── migrations/
│       └── 001_init.sql                           # SQLite relational DDL across 16 operational domains
├── artifacts/                                     # Execution run artifacts and evidence
│   └── runs/                                      # Run directories (<runId>/evidence, logs, reports, state)
└── src/                                           # Planned modular implementation subsystems (Future Waves)
```

---

## 5. Proven Current-Orchestrator Invariants

SACL V1 directly inherits and preserves the battle-tested invariants established in `Stable-Ecommerce-Orchestrator`:

1. **Local Dirty-Root Rule:** The primary product checkout (`.git` common dir) may legitimately contain uncommitted human changes. Automation never runs `git reset --hard`, `git clean -fd`, `git checkout .`, or automatic `git stash`. If the primary checkout is dirty, worktree provisioning halts and prevents destructive modifications.
2. **Worktree Confinement & Branch Inviolability:** Agents operate strictly inside isolated worktrees (`git worktree add -b <branch> <path> origin/<branch>`). Working on `main` (`MAIN_BRANCH_NOT_ALLOWED`) or inside the primary checkout (`PRIMARY_CHECKOUT_NOT_ALLOWED`) is strictly forbidden.
3. **Non-Killing Diagnostic Timeouts:** When an agent exceeds its execution timeout, the supervisor marks it as `TIMEOUT_RUNNING` and raises an alert. The process is **never killed automatically**, preserving transient context, logs, and partial deliverables for human diagnosis.
4. **3-Way PID Recycling Defense:** Before any process operation or status evaluation, the supervisor verifies: (1) process is active in OS; (2) process executable name matches an allowed whitelist (`agy`, `powershell`, `pwsh`, `cmd`, `node`, `conhost`); and (3) `StartTime` matches the database record within a 300-second window.
5. **Canonical Result Protocol:** Agent verdicts are evaluated against explicit structured regex markers (`^(?:AGENT_[A-Z0-9_-]+_RESULT|RESULT|FINAL_RESULT)\s*=\s*(PASS|PARTIAL|BLOCKED)`). Fallback evaluation strictly preserves `'PASS (Report Present)'`.
6. **Pre-Merge Collision Detection:** Cross-agent file diffs (`git diff --name-only origin/main...HEAD`) are compared across worktrees. Concurrent modifications to the same file block integration (`READY_FOR_INTEGRATION=NO`).
7. **Human Authority Gate & Controlled GitHub Writes:** Autonomous agents have zero authority to merge branches into `main`, deploy code, mutate GitHub rulesets, or transition production issues. Direct main/master/release push is hard denied; merge is hard denied in V1. Feature/task branch push and PR creation can occur only through locally trusted operations when project policy, package request, and valid bounded human approval all allow it; W0.3 itself performs no GitHub write.
8. **V1 Remote Production Prohibition:** Live mutations against remote production infrastructure (Railway CLI, GitHub ruleset API, Jira issue mutations) are disabled in V1 and fail closed.

---

## 6. Current Governance Status

```properties
DECISION_BASELINE_VERSION = 1.0.0
SPECIFICATION_VERSION    = 1.0.0
PRECEDENCE_HIERARCHY     = 4_TIER_CANONICAL
MUTATING_CONCURRENCY     = 1_PER_PROJECT (HIERARCHICAL_LOCKS)
PROJECT_REGISTRY         = LOCAL_ROOT_AUTHORITY
GMAIL_INGRESS            = users.watch + Cloud Pub/Sub Pull + historyId
PACKAGE_SCRIPTS          = DECLARATIVE_ONLY (LOCAL_HANDLERS_AUTHORITATIVE)
REMOTE_PRODUCTION        = DISABLED_FAIL_CLOSED
LEGACY_ORCHESTRATOR      = UNTOUCHED_UNTIL_E2E_CERTIFIED
IMPLEMENTATION_AUTHORIZED= NO
STATUS                   = ARCHITECTURE_FREEZE_CONSISTENT
```

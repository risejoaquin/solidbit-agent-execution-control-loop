# SACL V1 Architectural Traceability Matrix (TRACEABILITY_MATRIX)

**Document Identifier:** `docs/TRACEABILITY_MATRIX.md`  
**Status:** CANONICAL ARCHITECTURAL SPECIFICATION & BIDIRECTIONAL TRACEABILITY BASELINE  
**Target Repository:** `risejoaquin/solidbit-agent-execution-control-loop`  
**Sovereign Principal:** Joaquín (Human Developer)  
**Implementation Authorization:** `IMPLEMENTATION_AUTHORIZED=NO`  
**Safety Mode:** Fail-Closed Staging / Remote Production Execution Disabled in V1  

---

## 1. Executive Summary & Purpose of Traceability

This document establishes the comprehensive, bidirectional traceability framework for the **SolidBit Agent Execution Control Loop (SACL V1)**. It bridges high-level sovereign human intent and operational requirements down to physical architectural specifications, Architecture Decision Records (ADRs), JSON Schemas, database migrations, operational runbooks, and test certification harnesses.

### 1.1 Canonical Precedence Hierarchy
Every traced relationship and invariant mapped within this matrix strictly enforces the 4-tier canonical hierarchy codified in `DECISION_BASELINE.md` and `contracts/architecture-invariants.json`:

```
+==================================================================================================+
|                               SACL CANONICAL PRECEDENCE HIERARCHY                                |
+==================================================================================================+
|  TIER 1: Explicit Joaquín Decisions (Inviolable Baseline from DECISION_BASELINE.md)             |
+--------------------------------------------------------------------------------------------------+
|  TIER 2: Proven Current-Orchestrator Behavior (Operational Mechanics in Stable-Ecommerce)       |
+--------------------------------------------------------------------------------------------------+
|  TIER 3: Existing Governance & Contracts (Policies, Schemas, Freeze Baselines, Machine Guards)  |
+--------------------------------------------------------------------------------------------------+
|  TIER 4: Industry Standards (Used ONLY for Undefined Technical Gaps; Never Silent Override)      |
+==================================================================================================+
```

### 1.2 Traceability Dimensions
The matrix verifies integrity across seven distinct dimensions:
1. **Sovereign Directives & Architecture Synthesis (Explicit Joaquín Decisions & Derived Decisions) $\longrightarrow$ Architecture & Runtime Modules**
2. **Legacy Production Capabilities (18 Evaluated Mechanics) $\longrightarrow$ SACL Destination Subsystems**
3. **Audit & Freeze Findings (Wave 0 Findings, Wave 0.2 Findings, Wave 0.3 Findings) $\longrightarrow$ Canonical Remediation Documents**
4. **Operational Contradictions (Contradictions 1–4) $\longrightarrow$ Resolving ADRs & Policies**
5. **Architectural Decision Records (ADR-001 through ADR-014) $\longrightarrow$ Specifications & Contracts**
6. **JSON Schemas (10 Specifications) $\longrightarrow$ Validated Example Instances**
7. **Relational Database Model (16 Structured Operational Domains) $\longrightarrow$ DDL Migrations & Subsystems**

---

## 2. Decision Baseline & Architecture Traceability

### 2.1 Explicit Joaquín Decisions Traceability (Tier 1 Sovereign Directives)

The table below maps the foundational decisions established directly by the sovereign human principal (Joaquín) and baseline operational history directly to their implementing specifications, ADRs, schemas, and test criteria:

| # | Sovereign Decision / Requirement | Source Baseline | Governing Subsystem | Canonical Document Citation | Implementing ADR | Physical Artifact / Schema | Test / Verification Method |
| :-: | :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **1-9** | Context & legacy orchestrator operational history | Baseline Context | Governance | `docs/ARCHITECTURE.md` §1.2 | `ADR-005` | `README.md` | Audit verification |
| **10** | Target repository: `risejoaquin/solidbit-agent-execution-control-loop` | Decision #10 | Workspace Manager | `docs/ARCHITECTURE.md` §1.2 | `ADR-009` | `schemas/project-registry.schema.json` | Path assertions in preflight |
| **11** | Reuse/refactor current orchestrator; do not start from zero | Decision #11 | Core Architecture | `docs/CURRENT_ORCHESTRATOR_COMPATIBILITY_MATRIX.md` | `ADR-004` | 18 evaluated component inventory | Compatibility matrix audit |
| **12** | ChatGPT Web = Cloud Control Plane (planning, packaging, review) | Decision #12 | Control Plane | `docs/ARCHITECTURE.md` §2.1 | `ADR-014` | Zero host execution privileges | Boundary inspection |
| **13** | Gmail = Asynchronous transport channel | Decision #13 | Transport Gateway | `docs/MAIL_PROTOCOL.md` §1 | `ADR-001` | `schemas/mail-envelope.schema.json` | Gmail API watch / Pub/Sub pull & REST send test |
| **14** | Self-mail workflow supported (`uniquedraken@gmail.com`) | Decision #14 | Transport Gateway | `docs/MAIL_PROTOCOL.md` §2.2 | `ADR-001` | Whitelist configuration | Self-mail transmission test |
| **15** | Gmail credentials (OAuth2; App Passwords removed) and Antigravity decoupled | Decision #15 | Security / Transport | `docs/SECURITY_MODEL.md` §1 | `ADR-001` | Decoupled identity tokens | Credential bleed inspection |
| **16** | Mail Gateway and Graph-P are separate processes | Decision #16 | Orchestration Core | `docs/ARCHITECTURE.md` §2.3 | `ADR-008` | Distinct OS processes | Process isolation check |
| **17** | Graph-P maintains Zero Idle LLM Token Posture | Decision #17 | Supervisor Daemon | `docs/ARCHITECTURE.md` §2.5 | `ADR-003` | Standby SQLite polling loop | Token meter audit (0 tokens) |
| **18** | Graph-H is ephemeral per job; torn down on completion | Decision #18 | DAG Engine | `docs/ARCHITECTURE.md` §2.6 | `ADR-003` | Ephemeral child process lifecycle | Process exit & handle cleanup |
| **19** | Preserve self-contained wave ZIP package model | Decision #19 | Package Specification | `docs/EXECUTION_PACKAGE_SPEC.md` §2 | `ADR-004` | ZIP layout (`prompts/`, `scripts/`, etc.) | Zip extractor & AST validation |
| **21** | Antigravity CLI operates in isolated Git worktrees | Decision #21 | Workspace Manager | `docs/AUTHORITY_MODEL.md` §3 | `ADR-006` | Secondary worktree provisioning | Worktree branch inspection |
| **22** | SQLite (`sacl_ops.db`) = local Operational State Store | Decision #22 | State Persistence | `docs/SQLITE_DATA_MODEL.md` §1 | `ADR-002` | `db/migrations/001_init.sql` | SQLite WAL transaction test |
| **23** | Heavy artifacts remain strictly on filesystem | Decision #23 | Storage Architecture | `docs/SQLITE_DATA_MODEL.md` §2 | `ADR-011` | `artifacts/runs/<runId>/` | Database size audit (<50MB) |
| **24** | Analytics warehouse explicitly deferred to future scope | Decision #24 | State Persistence | `docs/SQLITE_DATA_MODEL.md` §1.1 | `ADR-002` | Out-of-scope boundary | Scope audit |
| **25** | Remote production execution strictly disabled in V1 | Decision #25 | Security / Safety | `docs/SECURITY_MODEL.md` §1.1 | `ADR-012` | Fail-closed policy filter | Remote command rejection test |

### 2.2 Derived & Ratified SACL Architecture Decisions Traceability (Tier 3 Architecture Synthesis)

The table below maps formal architecture decisions derived through architectural synthesis, security threat modeling, and freeze audit reconciliations (never conflated with direct Joaquín decisions):

| Decision Identifier | Domain / Invariant Summary | Governing Subsystem | Canonical Document Citation | Implementing ADR | Physical Artifact / Schema | Test / Verification Method |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **SB-FREEZE-P1-09** | Decision Provenance: Strict separation of explicit Joaquín directives from derived architecture decisions | Governance | `DECISION_BASELINE.md` §2<br>`docs/AUTHORITY_MODEL.md` §1 | `ADR-005` | `contracts/architecture-invariants.json` | Cross-document provenance verification |
| **Decision #20 / SB-FREEZE-P1-10** | Package Task Context Boundary: Complete/versioned task context; runtime services (Gmail, Pub/Sub, agy, Git, GitHub) allowed by policy | Package Specification | `docs/EXECUTION_PACKAGE_SPEC.md` §1<br>`DECISION_BASELINE.md` §3.2 | `ADR-004` | `schemas/manifest.schema.json`<br>`contracts/architecture-invariants.json` | Self-contained package validation test |
| **SB-FREEZE-P1-01 / SB-FREEZE-P2-03** | Gmail Ingress & Auth: users.watch + Pub/Sub Pull + historyId fetch; unread state is never source of truth; OAuth2 canonical | Transport Gateway | `docs/MAIL_PROTOCOL.md` §1, §3.3<br>`DECISION_BASELINE.md` §3.1 | `ADR-001` | `schemas/mail-envelope.schema.json`<br>`contracts/architecture-invariants.json` | Pub/Sub streaming pull & History API cursor sync test |
| **SB-FREEZE-P1-02** | Declarative Package Authority: Packages cannot self-authorize scripts; local operation registry governs handlers | Authority & Worker | `docs/AUTHORITY_MODEL.md` §3<br>`docs/EXECUTION_PACKAGE_SPEC.md` §1 | `ADR-006` | `schemas/operation-registry.schema.json`<br>`schemas/manifest.schema.json` | Unregistered operation rejection test |
| **SB-FREEZE-P1-03** | Four-Layer Permission Lattice: Hard deny always wins; approvals cannot override hard denials | Security & Policy | `docs/AUTHORITY_MODEL.md` §2<br>`docs/SECURITY_MODEL.md` §1–§2 | `ADR-012` | `schemas/hard-policy.schema.json`<br>`examples/hard-policy.valid.json` | Permission lattice intersection test |
| **SB-FREEZE-P1-11** | Controlled GitHub Write Semantics: Main push & merge hard denied; feature branch push & PR require bounded approval | Workspace & Policy | `DECISION_BASELINE.md` §3.9<br>`docs/AUTHORITY_MODEL.md` §5.5 | `ADR-012` | `contracts/architecture-invariants.json`<br>`schemas/hard-policy.schema.json` | Git push/merge interception test |
| **SB-FREEZE-P1-06 / SB-FREEZE-P2-05** | Generic Bounded Approval Contract: Bound to job_id, action, scope, request_id, expires_at; channels CLI, GMAIL, MANUAL (no webhook) | Authority Gate | `docs/AUTHORITY_MODEL.md` §4<br>`DECISION_BASELINE.md` §3.5 | `ADR-007` | `schemas/approval.schema.json`<br>`examples/approval.valid.json` | Bounded approval schema validation test |
| **SB-FREEZE-P1-04** | Canonical Job & Node Lifecycles: 12-state linear job lifecycle, 10 side states/outcomes, Graph-H node lifecycle | Orchestration Core | `docs/STATE_MACHINE.md` §2<br>`docs/SQLITE_DATA_MODEL.md` §5.4 | `ADR-013` | `db/migrations/001_init.sql`<br>`contracts/architecture-invariants.json` | Job & node state transition tests |
| **SB-FREEZE-P1-05** | 16 Relational SQLite Domains: Structured relational tables in sacl_ops.db with WAL mode and foreign keys | State Store | `docs/SQLITE_DATA_MODEL.md`<br>`docs/ARCHITECTURE.md` §5.2 | `ADR-002` | `db/migrations/001_init.sql`<br>`contracts/architecture-invariants.json` | Relational DDL execution and ACID verification |
| **SB-FREEZE-P2-01** | Mandatory Job ID in Manifest: Required for anti-replay deduplication and routing | Package Specification | `docs/EXECUTION_PACKAGE_SPEC.md` §3.2<br>`DECISION_BASELINE.md` §3.4 | `ADR-004` | `schemas/manifest.schema.json`<br>`examples/manifest.valid.json` | Manifest schema required job_id validation |
| **SB-FREEZE-P2-02** | Universal Summary Schema: implementation_authorized is boolean evidence of human sign-off | Observability | `docs/EXECUTION_PACKAGE_SPEC.md` §1<br>`docs/RESULT_PROTOCOL.md` §5 | `ADR-011` | `schemas/summary.schema.json`<br>`examples/summary.valid.json` | Summary schema boolean type validation |
| **SB-FREEZE-P2-04** | Physical Invariant Evidence: Machine-readable architecture invariants physically codified in repository | Architecture Governance | `DECISION_BASELINE.md` §3<br>`contracts/architecture-invariants.json` | `ADR-005` | `contracts/architecture-invariants.json` | Physical file existence and JSON schema validation |

---

## 3. Proven Current-Orchestrator Capabilities Traceability

The table below maps all 18 evaluated production capabilities from `Stable-Ecommerce-Orchestrator` to their SACL destination components:

| # | Legacy Capability | Proven Source Script | Observed Production Mechanic | SACL Destination Subsystem | Status / Classification | Governing Document |
| :-: | :--- | :--- | :--- | :--- | :---: | :--- |
| **1** | Git Worktree Lifecycle | `scripts/prepare-worktrees.ps1` | `git worktree add -b <branch>`; branch guards | Git Workspace Manager | **REFACTOR** | `docs/ARCHITECTURE.md` §2.6 |
| **2** | Local Dirty-Root Rule | `scripts/prepare-worktrees.ps1` | Never run reset/clean/stash on dirty checkout | Policy Engine / Workspace | **REUSE (INVIOLABLE)** | `docs/AUTHORITY_MODEL.md` §3.3 |
| **3** | Preflight Tooling Verification | `scripts/00-preflight.ps1` | Verifies `git`, `gh`, `agy`, `powershell.exe` | Policy & Validation Engine | **REFACTOR** | `docs/OPERATIONS.md` §1.2 |
| **4** | Governed CLI Spawning | `WORKER.ps1` | Headless `agy` with `-BypassAcknowledged` | Agent Worker Controller | **REFACTOR** | `docs/EXECUTION_PACKAGE_SPEC.md` §4 |
| **5** | Machine Governance Headers | `Invoke-AntigravityGoverned.ps1` | Dynamically prepends `GOVERNED_EXECUTION=TRUE` | Prompt Assembler / Controller | **REUSE (INVIOLABLE)** | `docs/ARCHITECTURE.md` §2.6 |
| **6** | Phased Staged DAG Scheduler | `RUN-WAVE.ps1`, `dependencies.json` | Multi-phase stages with `$MaxParallel` limit | Graph-H Ephemeral Engine | **REFACTOR** | `docs/CONCURRENCY_AND_LOCKING.md` §4 |
| **7** | PID State Reconciliation | `orchestrator-common.ps1` | Process tracking, exit code, start-time guard | Operational State Store | **REFACTOR / REPLACE** | `docs/SQLITE_DATA_MODEL.md` §5.4 |
| **8** | Deliverable Result Protocol | `orchestrator-common.ps1` | Regex markers + `'PASS (Report Present)'` fallback | Result Extractor & Verifier | **REUSE (INVIOLABLE)** | `docs/RESULT_PROTOCOL.md` §3 |
| **9** | Cross-Agent File Overlap | `scripts/collect-results.ps1` | Detects concurrent changes across worktree diffs | Conflict & Collision Evaluator | **REUSE** | `docs/AUTHORITY_MODEL.md` §3.4 |
| **10** | Non-Killing Timeout Invariant | `RUN-WAVE3.ps1` | Marks `TIMEOUT_RUNNING`; never kills worker | Timeout Supervisor / Kill Switch | **REUSE (INVIOLABLE)** | `docs/RETRY_AND_TIMEOUT_POLICY.md` §2 |
| **11** | Supervisor Singleton Lease | `scripts/run-supervisor.ps1` | WMI process scan replaced by SQLite lease | Graph-P Supervisor | **REFACTOR / REPLACE** | `docs/CONCURRENCY_AND_LOCKING.md` §2 |
| **12** | Live Console Monitor | `scripts/MONITOR.ps1` | 10s non-blocking terminal dashboard | Live Console Monitor | **REFACTOR** | `docs/OBSERVABILITY.md` §5 |
| **13** | Human Action Gate | `run-human-action-gate.ps1` | Emits `FINAL_DEVELOPMENT_AUTHORIZATION.txt` | Human Authority Gate | **REUSE (INVIOLABLE)** | `docs/AUTHORITY_MODEL.md` §4 |
| **14** | Wave Package ZIP Structure | `SACL_W0_ARCHITECTURE_FREEZE` | Structured archive layout with manifest | Execution Package Spec | **REUSE** | `docs/EXECUTION_PACKAGE_SPEC.md` §2 |
| **15** | E2E Sandboxed Test Suite | `test-orchestrator-e2e.ps1` | 8-step test in `$env:TEMP` with mock workers | E2E Certification Harness | **REFACTOR** | `docs/E2E_CERTIFICATION_PLAN.md` §2 |
| **16** | Engineering Risk Taxonomy | `generate_af_report.py` | 4-tier classification: SAFE_NOW, POST_GATE, etc. | Architecture Governance | **REUSE** | `docs/ARCHITECTURE.md` §6.1 |
| **17** | Asynchronous Transport | *Manual copy-paste (Legacy)* | Replaced by automated Gmail Mail Gateway | Mail Gateway Daemon | **REPLACE (NEW)** | `docs/MAIL_PROTOCOL.md` §1 |
| **18** | Remote Production Mutations | `FIX-SOLIDBIT-*.ps1` (Legacy) | Live mutations against Railway/GitHub/Jira | Gated Local Staging (Disabled) | **REPLACE (CONTRADICTION)** | `docs/SECURITY_MODEL.md` §1.1 |

---

## 4. Audit Finding Remediation Traceability

### 4.1 Wave 0 Preliminary Audit Findings Traceability (FINDING-P1-01 through P3-01)

The table below traces the resolution of all seven preliminary audit findings identified during Wave 0 and reconciled under Wave 0.1:

| Finding ID | Finding Description | Severity | W0.1 Canonical Resolution | Canonical Document Citation | DDL / Schema Citation | Status |
| :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| **FINDING-P1-01** | Incompatible Gmail subject syntax & parser regex | P1 | Subject line is intake routing hint `[SACL][JOB][v1][<JOB_ID>]`. Authority lives in `manifest.json`. | `docs/MAIL_PROTOCOL.md` §2.1<br>`docs/FREEZE_REMEDIATION.md` §3 | `schemas/mail-envelope.schema.json` | **RESOLVED** |
| **FINDING-P1-02** | Discrepant HMAC calculation payload & key custody | P1 | HMAC removed from V1 requirements. Signing deferred to future hardening; ChatGPT Web secretless. | `docs/adr/ADR-014-v1-transport-authentication-signing-deferred.md`<br>`docs/SECURITY_MODEL.md` §4.1 | `schemas/mail-envelope.schema.json` | **RESOLVED** |
| **FINDING-P1-03** | Relational DDL naming & table discrepancies | P1 | Designate `AG-SCHEMA` §5.3 as sole canonical DDL (`supervisor_locks`, `runs`, `dag_stages`, `agents`, etc.). | `docs/SQLITE_DATA_MODEL.md`<br>`docs/FREEZE_REMEDIATION.md` §3 | `db/migrations/001_init.sql` | **RESOLVED** |
| **FINDING-P1-04** | CHECK constraint error on `'PASS (Report Present)'` | P1 | Included `'PASS (Report Present)'` in SQL DDL CHECK constraint, JSON schemas, and result extractor. | `docs/RESULT_PROTOCOL.md` §2<br>`docs/FREEZE_REMEDIATION.md` §3 | `db/migrations/001_init.sql` (Line 90)<br>`schemas/result.schema.json` | **RESOLVED** |
| **FINDING-P2-01** | Overly restrictive replay rule blocking wave retries | P2 | At-least-once transport. Deduplication on `(message_id, nonce)`. Retries use new nonce; same hash ignored. | `docs/adr/ADR-010-at-least-once-idempotent-processing.md`<br>`docs/RECOVERY_MODEL.md` §6 | `schemas/mail-envelope.schema.json` | **RESOLVED** |
| **FINDING-P2-02** | Dual deliverable ambiguity (`SUMMARY.md` vs `.json`) | P2 | Dual deliverable mandate: both `SUMMARY.md` and `SUMMARY.json` are required root deliverables. | `docs/adr/ADR-011-filesystem-artifacts-sqlite-metadata.md`<br>`docs/EXECUTION_PACKAGE_SPEC.md` §1 | `schemas/summary.schema.json`<br>`schemas/manifest.schema.json` | **RESOLVED** |
| **FINDING-P3-01** | Harmonization of root entrypoints vs `src/` modules | P3 | Root entrypoints preserved for package runners; refactored modular implementation under `src/`. | `docs/CURRENT_ORCHESTRATOR_COMPATIBILITY_MATRIX.md` §5<br>`README.md` §4 | `docs/ARCHITECTURE.md` §7.1 | **RESOLVED** |

### 4.2 Wave 0.2 Freeze Consistency Remediation Traceability (SB-FREEZE-P1-01 through P1-08, P2-01 through P2-02)

The table below traces the resolution of all ten semantic architecture findings identified during the Direct Human Audit of the W0.1 snapshot, each fully resolved with concrete implementation evidence:

| Finding ID | Severity | Category | W0.1 Inconsistency / Finding Summary | Canonical W0.2 Resolution | Primary Document Citation | DDL / Schema Citation | Verification Evidence & Invariant Link | Status |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **SB-FREEZE-P1-01** | P1 (High) | Transport Architecture | Selected Gmail event architecture silently replaced by IMAP/SMTP polling and IMAP IDLE. | Restored Gmail API `users.watch` + Google Cloud Pub/Sub pull subscriber as wake signal; authoritative fetch via Gmail History API (`users.history.list`) using persisted `historyId` cursor; automatic watch renewal; startup reconciliation; periodic fallback polling only; outbound dispatch via Gmail REST API (`users.messages.send`); zero SMTP in V1. | `docs/MAIL_PROTOCOL.md` §1–§2<br>`docs/ARCHITECTURE.md` §2.2–§2.3<br>`docs/adr/ADR-001-gmail-self-mailbox-transport.md`<br>`DECISION_BASELINE.md` §3.1 | `schemas/mail-envelope.schema.json`<br>`db/migrations/001_init.sql` (Domain 11: `mail_messages`)<br>`contracts/architecture-invariants.json` | `primary_ingress = "gmail_api_users_watch_pubsub_pull"`; `public_webhook = false`; `cursor = "historyId"`; `fallback_polling_only = true` | **RESOLVED** |
| **SB-FREEZE-P1-02** | P1 (High) | Package Authority | Untrusted packages could self-authorize attached scripts via `authorized_scripts` manifest field. | Execution packages are strictly declarative in authority. `authorized_scripts` field permanently prohibited and removed. Packages declare requested stable operation IDs (`requested_operations`). Local SACL core autoexecution only invokes locally trusted handlers from the Local Operation Registry whose identity, hash, and profile are trusted by local policy. Preserved `scripts/` directory for compatibility and review only. | `docs/EXECUTION_PACKAGE_SPEC.md` §1, §3<br>`docs/AUTHORITY_MODEL.md` §3<br>`docs/adr/ADR-006-no-arbitrary-remote-code.md`<br>`DECISION_BASELINE.md` §3.2 | `schemas/manifest.schema.json`<br>`schemas/operation-registry.schema.json`<br>`examples/operation-registry.valid.json`<br>`contracts/architecture-invariants.json` | `declarative = true`; `package_may_self_authorize_scripts = false`; `trusted_handlers_owned_locally = true` | **RESOLVED** |
| **SB-FREEZE-P1-03** | P1 (High) | Permission Lattice | Effective-permission lattice missing; policy schema permitted dangerous operational booleans without hard local policy contract. | Codified formal four-layer lattice: $\text{Effective Permissions} = \text{Hard Local Policy} \cap \text{Project Policy} \cap \text{Package Requested} \cap \text{Approval Grant}$. Hard deny always wins. Approval cannot override hard deny. Hard local policy permanently denies remote production execution, GitHub merges, production DB writes, secret exports, arbitrary remote code, main-branch execution, primary-checkout mutation, hard resets, and auto-stash in V1. | `docs/AUTHORITY_MODEL.md` §2<br>`docs/SECURITY_MODEL.md` §1–§2<br>`docs/adr/ADR-012-no-remote-production-v1.md`<br>`DECISION_BASELINE.md` §3.3 | `schemas/hard-policy.schema.json`<br>`examples/hard-policy.valid.json`<br>`schemas/policy.schema.json`<br>`contracts/architecture-invariants.json` | `hard_deny_wins = true`; `approval_can_override_hard_deny = false`; `remote_production_v1 = false` | **RESOLVED** |
| **SB-FREEZE-P1-04** | P1 (High) | State Lifecycle | Canonical 12-state job lifecycle and Graph-H node lifecycle replaced by simplified state models. | Restored canonical 12-state linear job lifecycle: `RECEIVED` $\rightarrow$ `AUTHENTICATED` $\rightarrow$ `VALIDATED` $\rightarrow$ `PERSISTED` $\rightarrow$ `QUEUED` $\rightarrow$ `DISPATCHED` $\rightarrow$ `RUNNING` $\rightarrow$ `VERIFYING` $\rightarrow$ `RESULT_PACKAGED` $\rightarrow$ `RESULT_SENT` $\rightarrow$ `COMPLETED` $\rightarrow$ `ARCHIVED`. Restored 10 side states/outcomes: `WAITING_APPROVAL`, `RETRY_WAIT`, `BLOCKED`, `FAILED`, `CANCELLED`, `INTERRUPTED`, `TIMED_OUT`, `POLICY_DENIED`, `REJECTED`, `QUARANTINED`. Restored Graph-H node states: `PENDING` $\rightarrow$ `READY` $\rightarrow$ `RUNNING` $\rightarrow$ `SUCCEEDED` with side outcomes. | `docs/STATE_MACHINE.md` §2<br>`docs/SQLITE_DATA_MODEL.md` §5.4<br>`docs/adr/ADR-013-run-status-reconciliation.md`<br>`DECISION_BASELINE.md` §3.4 | `db/migrations/001_init.sql` (Domain 4: `jobs`, Domain 6: `graph_nodes`)<br>`contracts/architecture-invariants.json` | Complete CHECK constraints on `jobs.status` and `graph_nodes.status` verified in SQLite test execution | **RESOLVED** |
| **SB-FREEZE-P1-05** | P1 (High) | Operational Data Tier | SQLite state store DDL incomplete (only 10 tables; missing schema migrations, projects, packages, mail cursors, jobs, nodes, attempts, approvals, artifacts, results, leases, heartbeats, errors). | Codified complete relational schema across 16 formal operational domains: `schema_migrations`, `projects`, `packages`, `mail_messages` (with `mail_cursors`), `jobs`, `runs`, `graph_nodes`, `node_attempts`, `agents`, `events`, `approvals`, `artifacts`, `results`, `leases`, `heartbeats`, `errors`. Preserved backward-compatible tables (`supervisor_locks`, `dag_stages`, `agent_dependencies`, `file_modifications`, `file_conflicts`, `mail_inbox`, `mail_outbox`, `audit_events`). Connection bootstrap enforces WAL, busy_timeout 5000, synchronous NORMAL, and foreign_keys ON. Forward-only migration tracking. | `docs/SQLITE_DATA_MODEL.md`<br>`docs/ARCHITECTURE.md` §5.2<br>`docs/adr/ADR-002-sqlite-operational-state-store.md`<br>`DECISION_BASELINE.md` §3.6 | `db/migrations/001_init.sql` (Domains 1–16)<br>`contracts/architecture-invariants.json` | `001_init.sql` executes cleanly in disposable SQLite in-memory instance without syntax or FK errors | **RESOLVED** |
| **SB-FREEZE-P1-06** | P1 (High) | Approval Contract | Approval contract freeze-centric and omitted mandatory binding to action, scope, request_id, and expiration. | Codified generic bounded action-approval contract bound strictly to: `JOB_ID + ACTION + SCOPE + REQUEST_ID + expires_at`. Documented resumption semantics: approval resumes the same logical run without spawning disconnected runs. Approvals cannot exceed the hard local policy envelope or override hard denies. | `docs/AUTHORITY_MODEL.md` §4<br>`docs/adr/ADR-007-human-authority.md`<br>`DECISION_BASELINE.md` §3.5 | `schemas/approval.schema.json`<br>`examples/approval.valid.json`<br>`db/migrations/001_init.sql` (Domain 14: `approvals`)<br>`contracts/architecture-invariants.json` | `approval_binding = ["job_id", "action", "scope", "request_id", "expires_at"]` | **RESOLVED** |
| **SB-FREEZE-P1-07** | P1 (High) | Baseline Invariants | Missing physical `DECISION_BASELINE.md` file from canonical repository root and W0.1 gate. | Codified root `DECISION_BASELINE.md` distinguishing explicit Joaquín decisions from derived architecture synthesis, canonical precedence rules, and architecture invariants. Codified machine-readable `contracts/architecture-invariants.json` inside the repository. | `DECISION_BASELINE.md`<br>`docs/adr/ADR-005-decision-precedence.md`<br>`README.md` §2 | `contracts/architecture-invariants.json`<br>`schemas/manifest.schema.json` | `DECISION_BASELINE.md` and `contracts/architecture-invariants.json` physically exist and validate | **RESOLVED** |
| **SB-FREEZE-P1-08** | P1 (High) | Documentation Index | `docs/ARCHITECTURE.md` embedded an ADR-001..ADR-013 list whose numbers and titles contradicted actual files under `docs/adr/ADR-001..ADR-014`. | Designated physical ADR files as canonical authority. Reconciled `docs/ARCHITECTURE.md` Section 6 index to match exact physical ADR-001 through ADR-014 numbers and titles verbatim. Traced complete 14 ADR set. | `docs/ARCHITECTURE.md` §6<br>`docs/adr/ADR-001` through `ADR-014`<br>`docs/TRACEABILITY_MATRIX.md` §6 | All 14 physical ADR files in `docs/adr/` | 14/14 ADR titles, numbers, scopes, and links verified identical between index and physical disk files | **RESOLVED** |
| **SB-FREEZE-P2-01** | P2 (Med) | Manifest Contract | `job_id` optional in `manifest.schema.json`, breaking transport routing hint and idempotency design. | Made `job_id` mandatory in `schemas/manifest.schema.json` with regex pattern `^[A-Za-z0-9_.-]+$`. Updated package specifications and valid examples. | `docs/EXECUTION_PACKAGE_SPEC.md` §3.2<br>`docs/MAIL_PROTOCOL.md` §2.1<br>`DECISION_BASELINE.md` §3.4 | `schemas/manifest.schema.json`<br>`examples/manifest.valid.json` | `manifest.valid.json` validates against `schemas/manifest.schema.json` with required `job_id` | **RESOLVED** |
| **SB-FREEZE-P2-02** | P2 (Med) | Summary Schema | Universal summary schema permanently forbade implementation authorization via `const: false`. | Updated `schemas/summary.schema.json` to allow `implementation_authorized` as `type: "boolean"`. Preserved `false` in current W0/W0.1/W0.2 artifacts while allowing schema to represent future explicit human authorization. Summary boolean remains evidence, not authority. | `docs/EXECUTION_PACKAGE_SPEC.md` §1<br>`docs/RESULT_PROTOCOL.md`<br>`DECISION_BASELINE.md` §3.7 | `schemas/summary.schema.json`<br>`examples/summary.valid.json` | `summary.valid.json` validates with `implementation_authorized: false`; schema supports boolean type | **RESOLVED** |

### 4.3 Wave 0.3 Final Architecture Freeze Remediation Traceability (SB-FREEZE-P1-09 through P1-11, SB-FREEZE-P2-03 through P2-05)

The table below traces the resolution of all six architectural findings identified during the Wave 0.3 Direct Human Review, ensuring full reconciliation of decision provenance, runtime service boundaries, GitHub write semantics, transport auth credentials, physical invariants, and approval channels:

| Finding ID | Severity | Category | W0.3 Human Review Finding Summary | Canonical W0.3 Resolution | Primary Document Citation | DDL / Schema Citation | Verification Evidence & Invariant Link | Status |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **SB-FREEZE-P1-09** | P1 (High) | Decision Provenance | 25 decisions previously labeled as explicit sovereign decisions without distinguishing human directives from architecture synthesis. | Explicit Joaquín decisions (Tier 1 Directives: #10–#19, #21–#25) are strictly separated from derived/ratified SACL architecture decisions (Tier 3 Synthesis). Agent-derived choices are never claimed as explicit Joaquín decisions. | `DECISION_BASELINE.md` §2<br>`docs/AUTHORITY_MODEL.md` §1<br>`docs/adr/ADR-005-decision-precedence.md`<br>`contracts/architecture-invariants.json` | `contracts/architecture-invariants.json` (`decision_precedence`) | Provenance classification verified across DECISION_BASELINE.md and TRACEABILITY_MATRIX.md | **RESOLVED** |
| **SB-FREEZE-P1-10** | P1 (High) | Runtime Boundary | Contradictory hermetic wording asserted zero runtime cloud lookups while V1 intentionally uses Gmail API, Pub/Sub, and Antigravity CLI. | Replaced contradictory hermetic wording: execution packages carry complete, self-contained, and versioned task context on disk (prompts, configurations, schemas, contracts) so execution does not require ad-hoc documentation or prompt discovery. Explicitly configured runtime services (Gmail API, Google Cloud Pub/Sub, Antigravity CLI, Git, and conditionally GitHub when allowed by policy) are permitted runtime boundaries and not prohibited by the package model. | `DECISION_BASELINE.md` §2.3, §3.2<br>`docs/EXECUTION_PACKAGE_SPEC.md` §1<br>`docs/adr/ADR-004-wave-package-compatibility.md`<br>`contracts/architecture-invariants.json` | `schemas/manifest.schema.json`<br>`contracts/architecture-invariants.json` (`package.runtime_services_allowed_when_explicitly_configured`) | Package self-contained task context boundary codified without contradictory zero-cloud assertions | **RESOLVED** |
| **SB-FREEZE-P1-11** | P1 (High) | GitHub Write Semantics | Text stated agents have zero authority to push remote branches, conflicting with future controlled write stages and legacy wave capabilities. | Defined controlled GitHub write semantics precisely: (1) direct push to `main`/`master`/release is permanently hard denied; (2) merge is hard denied in V1; (3) feature/task branch push and PR creation can occur only through locally trusted operations when project policy, package request, and valid bounded human approval all allow it; (4) W0.3 itself performs no GitHub write. | `DECISION_BASELINE.md` §3.9<br>`docs/AUTHORITY_MODEL.md` §5.5<br>`docs/adr/ADR-012-no-remote-production-v1.md`<br>`contracts/architecture-invariants.json` | `schemas/hard-policy.schema.json`<br>`contracts/architecture-invariants.json` (`github`) | `direct_main_push_hard_denied=true`, `merge_hard_denied_v1=true`, bounded human approval required for branch push / PR | **RESOLVED** |
| **SB-FREEZE-P2-03** | P2 (Med) | Transport Auth & Ingress | Residual mentions of App Passwords and unread mailbox state filtering. | Gmail API OAuth2 is canonical. App Passwords are permanently removed as a V1 transport credential. Unread mailbox state (`is:unread`) is never the source of truth and must not be a gating input. Primary ingress is event-driven via `users.watch` -> Cloud Pub/Sub Pull -> authoritative fetch via Gmail History API (`historyId`). Polling is degraded-mode fallback only. | `DECISION_BASELINE.md` §2.3, §3.1<br>`docs/MAIL_PROTOCOL.md` §1, §3.3<br>`docs/SECURITY_MODEL.md` §4.2<br>`docs/adr/ADR-001-gmail-self-mailbox-transport.md` | `schemas/mail-envelope.schema.json`<br>`contracts/architecture-invariants.json` (`gmail`) | `auth="oauth2"`, `unread_is_source_of_truth=false`, `primary_ingress="gmail_api_users_watch_pubsub_pull"` | **RESOLVED** |
| **SB-FREEZE-P2-04** | P2 (Med) | Invariant Evidence | Canonical documentation cited `contracts/architecture-invariants.json` but file was absent from early repository snapshots. | Physical file `contracts/architecture-invariants.json` codified in canonical target repository conforming to `solidbit.architecture-invariants.v1` and verified present on disk, reflecting all architecture invariants. | `contracts/architecture-invariants.json`<br>`DECISION_BASELINE.md` §3<br>`docs/FREEZE_REMEDIATION.md` §6 | `contracts/architecture-invariants.json` | Physical file exists on disk, valid JSON schema instance, verified by automated test harness | **RESOLVED** |
| **SB-FREEZE-P2-05** | P2 (Med) | Approval Channel Invariant | `approval.schema.json` permitted `WEBHOOK` channel, while V1 exposes zero public inbound webhooks. | Removed `WEBHOOK` from the V1 approval channel enum in `schemas/approval.schema.json`. V1 approval attestation channels are strictly `CLI`, `GMAIL`, and `MANUAL`. Examples and specifications updated accordingly. | `schemas/approval.schema.json`<br>`examples/approval.valid.json`<br>`docs/AUTHORITY_MODEL.md` §4.1<br>`contracts/architecture-invariants.json` | `schemas/approval.schema.json`<br>`examples/approval.valid.json` | `approval_channels_v1 = ["CLI", "GMAIL", "MANUAL"]`; schema validation verified | **RESOLVED** |

---

## 5. Operational Contradiction Traceability (Contradictions 1–4)

The table below traces the resolution of the four architectural contradictions between legacy script behaviors and SACL V1 constitutional baselines:

| # | Contradiction Summary | Legacy Observed Behavior | SACL Constitutional Directive | Resolving ADR | Canonical Policy & Document | Status |
| :-: | :--- | :--- | :--- | :---: | :--- | :---: |
| **C1** | Remote Production Mutations | Scripts execute live mutations against Railway, GitHub rulesets, and Jira. | Remote production execution strictly disabled in V1 (Decision #25). | `ADR-012` | `docs/SECURITY_MODEL.md` §1.1 (Fail-closed staging; dry-run plans only) | **RESOLVED** |
| **C2** | State Persistence Storage Tier | Loose JSON and text files updated via atomic file replace (`.tmp` -> `.json`). | SQLite is designated local Operational State Store (Decision #22). | `ADR-002` | `docs/SQLITE_DATA_MODEL.md` (`sacl_ops.db` WAL mode; heavy logs on filesystem) | **RESOLVED** |
| **C3** | Single-Repo vs Multi-Project | Hardcoded paths and remote URL regexes for `Stable-Ecommerce`. | Core engine supports multi-project orchestration (Decision #10). | `ADR-009` | `docs/ARCHITECTURE.md` §4.1 (`manifest.json` project parameterization) | **RESOLVED** |
| **C4** | Manual Transport vs Automation | Manual ZIP download, manual extraction, manual copy-paste of summaries. | Asynchronous Gmail store-and-forward transport (Decision #12–#14). | `ADR-001`<br>`ADR-008` | `docs/MAIL_PROTOCOL.md` (Mail Gateway daemon decoupled from Graph-P) | **RESOLVED** |

---

## 6. Architectural Decision Records Traceability (ADR-001 through ADR-014)

The table below provides a complete catalog of all fourteen accepted Architectural Decision Records:

| ADR ID | Decision Title | Status | Deciders | Core Invariant Established | Implementing Subsystem | Primary Document Citation |
| :---: | :--- | :---: | :--- | :--- | :--- | :--- |
| **ADR-001** | Gmail Self-Mailbox Transport | ACCEPTED | Joaquín, Arch Lead | Outbound-only TLS; self-mail supported; subject is routing hint only. | Mail Gateway | `docs/adr/ADR-001-gmail-self-mailbox-transport.md` |
| **ADR-002** | SQLite Operational State Store | ACCEPTED | Joaquín, Arch Lead | SQLite WAL mode; ACID state; preserves all proven legacy tracking fields. | State Store | `docs/adr/ADR-002-sqlite-operational-state-store.md` |
| **ADR-003** | Persistent IDLE Supervisor | ACCEPTED | Joaquín, Arch Lead | Zero idle LLM tokens; Graph-P persistent daemon; Graph-H ephemeral DAG. | Supervisor | `docs/adr/ADR-003-persistent-idle-supervisor.md` |
| **ADR-004** | Wave Package Compatibility | ACCEPTED | Joaquín, Arch Lead | Self-contained runnable ZIP packages carrying versioned task context; configured runtime services permitted by policy. | Package Spec | `docs/adr/ADR-004-wave-package-compatibility.md` |
| **ADR-005** | Sovereign Decision Precedence | ACCEPTED | Joaquín, Arch Lead | 4-tier canonical precedence hierarchy; higher-tier supremacy; no silent overrides. | Governance | `docs/adr/ADR-005-decision-precedence.md` |
| **ADR-006** | Prohibition of Remote Code | ACCEPTED | Joaquín, Sec Lead | Anti-ACE; fail-closed Zip Slip defense; governed Antigravity worker execution. | Policy / Worker | `docs/adr/ADR-006-no-arbitrary-remote-code.md` |
| **ADR-007** | Human Authority Gate | ACCEPTED | Joaquín, Sec Lead | Human supremacy; autonomous merges/deploys blocked; fail-closed defaults. | Authority Gate | `docs/adr/ADR-007-human-authority.md` |
| **ADR-008** | Mail Gateway Separation | ACCEPTED | Joaquín, Arch Lead | Independent process isolation between Mail Gateway and Graph-P supervisor. | Topology | `docs/adr/ADR-008-mail-gateway-separation.md` |
| **ADR-009** | Multi-Project Parameterization | ACCEPTED | Joaquín, Arch Lead | Dynamic repo resolution via `manifest.json`; elimination of hardcoded paths. | Workspace | `docs/adr/ADR-009-multiproject-core.md` |
| **ADR-010** | At-Least-Once Delivery | ACCEPTED | Joaquín, Protocol Lead | At-least-once transport; idempotent consumers; duplicate delivery ignored. | Protocol | `docs/adr/ADR-010-at-least-once-idempotent-processing.md` |
| **ADR-011** | Filesystem vs SQLite Storage | ACCEPTED | Joaquín, Arch Lead | Heavy logs/reports in filesystem; lightweight metadata in SQLite; dual summaries. | Storage | `docs/adr/ADR-011-filesystem-artifacts-sqlite-metadata.md` |
| **ADR-012** | Prohibition of Remote Prod | ACCEPTED | Joaquín, Sec Lead | Remote production disabled in V1; dry-run action plans (`.plan.json` / `.plan.md`). | Security | `docs/adr/ADR-012-no-remote-production-v1.md` |
| **ADR-013** | Run Status Reconciliation | ACCEPTED | Joaquín, Arch Lead | 4-factor reconciliation; non-killing diagnostic timeouts; PID defense. | Reconciliation | `docs/adr/ADR-013-run-status-reconciliation.md` |
| **ADR-014** | V1 Transport Auth & Deferred Signing | ACCEPTED | Joaquín, Sec Lead | ChatGPT Web secretless; package signing deferred; multi-layer defense-in-depth. | Security / Mail | `docs/adr/ADR-014-v1-transport-authentication-signing-deferred.md` |

---

## 7. JSON Schemas & Validation Examples Traceability

The table below catalogs all ten formal JSON Schemas and their matching valid example instances:

| Schema File (`schemas/`) | Schema Identifier (`$id`) | Valid Example File (`examples/`) | Associated Canonical Spec | Validation Method & Status |
| :--- | :--- | :--- | :--- | :---: |
| [`manifest.schema.json`](file:////workspace/solidbit-agent-execution-control-loop/schemas/manifest.schema.json) | `solidbit.execution-package.v1` | [`manifest.valid.json`](file:////workspace/solidbit-agent-execution-control-loop/examples/manifest.valid.json) | `docs/EXECUTION_PACKAGE_SPEC.md` | Validated (Draft 2020-12) |
| [`graph.schema.json`](file:////workspace/solidbit-agent-execution-control-loop/schemas/graph.schema.json) | `solidbit.execution-graph.v1` | [`graph.valid.json`](file:////workspace/solidbit-agent-execution-control-loop/examples/graph.valid.json) | `docs/CONCURRENCY_AND_LOCKING.md` | Validated (Draft 2020-12) |
| [`hard-policy.schema.json`](file:////workspace/solidbit-agent-execution-control-loop/schemas/hard-policy.schema.json) | `solidbit.hard-policy.v1` | [`hard-policy.valid.json`](file:////workspace/solidbit-agent-execution-control-loop/examples/hard-policy.valid.json) | `docs/SECURITY_MODEL.md` | Validated (Draft 2020-12) |
| [`policy.schema.json`](file:////workspace/solidbit-agent-execution-control-loop/schemas/policy.schema.json) | `solidbit.policy.v1` | [`policy.valid.json`](file:////workspace/solidbit-agent-execution-control-loop/examples/policy.valid.json) | `docs/SECURITY_MODEL.md` | Validated (Draft 2020-12) |
| [`operation-registry.schema.json`](file:////workspace/solidbit-agent-execution-control-loop/schemas/operation-registry.schema.json) | `solidbit.operation-registry.v1` | [`operation-registry.valid.json`](file:////workspace/solidbit-agent-execution-control-loop/examples/operation-registry.valid.json) | `docs/EXECUTION_PACKAGE_SPEC.md` | Validated (Draft 2020-12) |
| [`approval.schema.json`](file:////workspace/solidbit-agent-execution-control-loop/schemas/approval.schema.json) | `solidbit.approval.v1` | [`approval.valid.json`](file:////workspace/solidbit-agent-execution-control-loop/examples/approval.valid.json) | `docs/AUTHORITY_MODEL.md` | Validated (Draft 2020-12) |
| [`result.schema.json`](file:////workspace/solidbit-agent-execution-control-loop/schemas/result.schema.json) | `solidbit.result.v1` | [`result.valid.json`](file:////workspace/solidbit-agent-execution-control-loop/examples/result.valid.json) | `docs/RESULT_PROTOCOL.md` | Validated (Draft 2020-12) |
| [`mail-envelope.schema.json`](file:////workspace/solidbit-agent-execution-control-loop/schemas/mail-envelope.schema.json) | `solidbit.mail-envelope.v1` | [`mail-envelope.valid.json`](file:////workspace/solidbit-agent-execution-control-loop/examples/mail-envelope.valid.json) | `docs/MAIL_PROTOCOL.md` | Validated (Draft 2020-12) |
| [`summary.schema.json`](file:////workspace/solidbit-agent-execution-control-loop/schemas/summary.schema.json) | `solidbit.run-summary.v1` | [`summary.valid.json`](file:////workspace/solidbit-agent-execution-control-loop/examples/summary.valid.json) | `docs/OBSERVABILITY.md` | Validated (Draft 2020-12) |
| [`project-registry.schema.json`](file:////workspace/solidbit-agent-execution-control-loop/schemas/project-registry.schema.json) | `solidbit.project-registry.v1` | [`project-registry.valid.json`](file:////workspace/solidbit-agent-execution-control-loop/examples/project-registry.valid.json) | `docs/ARCHITECTURE.md` §4.1 | Validated (Draft 2020-12) |

---

## 8. Relational Data Model & DDL Migration Traceability (16 Operational Domains)

The table below maps the 16 structured operational domains defined in the canonical DDL migration (`db/migrations/001_init.sql`) and `docs/SQLITE_DATA_MODEL.md` to their architectural role and governing subsystem:

| Domain # | Domain Name / Table(s) | Primary Entity & Constraints | Operational Purpose & Invariants | Governing Subsystem | Canonical Spec Citation |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **1** | `schema_migrations` | `version PRIMARY KEY`, applied timestamp, SHA-256 checksum | Monotonic forward-only schema migration history and integrity tracking | Core Infrastructure | `docs/SQLITE_DATA_MODEL.md` §5.1 |
| **2** | `projects` | `project_id PRIMARY KEY`, local root path, default branch | Multi-project repository registry and local root authority | Git Workspace Manager | `docs/SQLITE_DATA_MODEL.md` §5.2 |
| **3** | `packages` | `package_id PRIMARY KEY`, archive hash, manifest JSON copy | Ingested package audit log, hash verification, and declarative metadata | Package Ingestion | `docs/SQLITE_DATA_MODEL.md` §5.3 |
| **4** | `jobs` | `job_id PRIMARY KEY`, status CHECK (12 primary + 10 side states) | Canonical logical job lifecycle state machine and dispatch tracking | Orchestration Core | `docs/SQLITE_DATA_MODEL.md` §5.4 |
| **5** | `runs` | `run_id PRIMARY KEY`, mode, repository, `ready_for_integration` | Concrete wave execution runs, timings, and high-level verdicts | Orchestration Core | `docs/SQLITE_DATA_MODEL.md` §5.5 |
| **6** | `graph_nodes` | `(node_id, run_id) PK`, status CHECK (PENDING..SUCCEEDED) | Ephemeral DAG node definitions, phased barriers, and execution states | Graph-H DAG Engine | `docs/SQLITE_DATA_MODEL.md` §5.6 |
| **7** | `node_attempts` | `attempt_id PK`, foreign key to `graph_nodes`, process metadata | Granular node execution attempts, exit codes, and process durations | Graph-H Scheduler | `docs/SQLITE_DATA_MODEL.md` §5.7 |
| **8** | `agents` | `(agent_id, run_id) PK`, PID, 300s start window, result_verdict | Worker process tracking, PID recycling defense, and deliverable reports | Worker Controller | `docs/SQLITE_DATA_MODEL.md` §5.8 |
| **9** | `agent_dependencies`<br>`dag_stages` | Composite foreign keys to `runs` and stage definitions | Directed topological dependency edges and phased stage barriers | Graph-H Scheduler | `docs/SQLITE_DATA_MODEL.md` §5.9 |
| **10** | `file_modifications`<br>`file_conflicts` | Normalized relative paths, agent arrays, resolution status | Cross-agent file diff tracking and pre-merge collision evaluator | Collision Evaluator | `docs/SQLITE_DATA_MODEL.md` §5.10 |
| **11** | `mail_messages`<br>`mail_cursors` | `message_id PK`, unique nonce, `historyId` cursor, SHA-256 | Inbound transport queue, anti-replay registry, and monotonic cursors | Mail Gateway Daemon | `docs/SQLITE_DATA_MODEL.md` §5.11 |
| **12** | `mail_outbox` | `outbox_id PK`, recipient, attempt counter, response ZIP path | Outbound response dispatch queue and thread tracking | Mail Gateway Daemon | `docs/SQLITE_DATA_MODEL.md` §5.12 |
| **13** | `audit_events`<br>`events` | `event_id PK`, severity CHECK, ISO-8601 UTC timestamp, JSON | Append-only security and operational audit trail | Observability Framework | `docs/SQLITE_DATA_MODEL.md` §5.13 |
| **14** | `approvals` | `request_id PK`, `job_id`, `action`, `scope`, `expires_at` | Generic bounded human action-approval grants and tokens | Human Authority Gate | `docs/SQLITE_DATA_MODEL.md` §5.14 |
| **15** | `artifacts`<br>`results` | Relative filesystem path, SHA-256 digest, structured regex verdict | Filesystem pointer index and verified canonical run verdicts | Result Verifier | `docs/SQLITE_DATA_MODEL.md` §5.15 |
| **16** | `leases`<br>`heartbeats`<br>`errors` | Lease names (`SUPERVISOR_SINGLETON`), rolling heartbeats, errors | Mutual exclusion leases, process liveness, and structured failure logs | Supervisor Daemon | `docs/SQLITE_DATA_MODEL.md` §5.16 |

---

## 9. Constitutional Safety & Operational Verification Invariants

The table below catalogs the non-negotiable safety rules and their programmatic enforcement points:

| Invariant / Safety Gate | Enforcement Trigger | Failure Behavior | Programmatic Guard | Verified Proof |
| :--- | :--- | :--- | :--- | :--- |
| **Local Dirty-Root Rule** | Target repo primary checkout contains uncommitted human files (`status --porcelain`). | Halts immediately; status `HALTED_SAFETY` / `BLOCKED_DIRTY_ROOT`. Never runs `reset/clean/stash`. | `PreflightValidator.ps1`<br>`GitWorkspaceManager.ps1` | `docs/AUTHORITY_MODEL.md` §3.3 |
| **Branch Inviolability (`MAIN_BRANCH_NOT_ALLOWED`)** | Agent configuration specifies `main` or `master` as working branch. | Halts launch immediately with uncatchable exception. | `WorkerController.ps1` | `docs/AUTHORITY_MODEL.md` §3.1 |
| **Primary Checkout Inviolability** | Agent attempts execution inside directory where `.git` is a directory instead of gitdir reference. | Refuses launch (`PRIMARY_CHECKOUT_NOT_ALLOWED`). | `WorkerController.ps1` | `docs/AUTHORITY_MODEL.md` §3.2 |
| **Non-Killing Diagnostic Timeouts** | Agent worker exceeds allotted deadline (`timeout_seconds`). | Transitions status to `TIMEOUT_RUNNING`. Process is left alive for inspection; never auto-killed. | `GraphHDagEngine.ps1` | `docs/RETRY_AND_TIMEOUT_POLICY.md` §2 |
| **3-Way PID Recycling Defense** | Process query or termination requested. | Verifies OS handle, executable whitelist, and 300s `StartTime` window tolerance. Refuses if drifted. | `orchestrator-common.ps1`<br>`KillSwitch.ps1` | `docs/RESULT_PROTOCOL.md` §1 |
| **Human Authority Gate** | Pipeline reaches integration, merge, or deployment boundary. | Halts execution; emits `FINAL_DEVELOPMENT_AUTHORIZATION.txt`. Requires human sign-off. | `HumanActionGate.ps1` | `docs/AUTHORITY_MODEL.md` §4 |
| **Remote Production Prohibition** | Script or agent attempts to invoke Railway, GitHub ruleset API, or Jira mutations. | Intercepted and blocked fail closed. Emits offline plan (`.plan.json` / `.plan.md`). | `PolicyEngine.ps1` | `docs/SECURITY_MODEL.md` §1.1 |
| **Implementation Invariant** | Freeze phase operational state. | `IMPLEMENTATION_AUTHORIZED=NO` strictly maintained. Architecture freeze NOT YET PASS pending human review. | Root governance | `README.md` §6 |

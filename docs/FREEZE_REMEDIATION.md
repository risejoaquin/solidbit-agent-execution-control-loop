# SACL V1 Architecture Freeze Remediation & Audit Findings Resolution

**Document Identifier:** `docs/FREEZE_REMEDIATION.md`  
**Status:** CANONICAL ARCHITECTURAL SPECIFICATION & AUDIT RESOLUTION  
**Target Repository:** `risejoaquin/solidbit-agent-execution-control-loop`  
**Sovereign Principal:** Joaquín (Human Developer)  
**Implementation Authorization:** `IMPLEMENTATION_AUTHORIZED=NO`  
**Safety Mode:** Fail-Closed Staging / Remote Production Execution Disabled in V1  

---

## 1. Executive Summary & Governance Precedence

This document serves as the authoritative, physical record of all post-freeze audit remediations for the **SolidBit Agent Execution Control Loop (SACL V1)**. It reconciles the draft recommendations produced during the Wave 0 audit (`AG-ARCH`, `AG-COMPAT`, `AG-SCHEMA`, `AG-SEC`, `AG-QA`, `AG-FINAL`) against the binding **W0.1 Freeze Remediation Baseline**, explicit sovereign decisions, and proven legacy orchestrator behaviors.

### 1.1 Canonical Decision Precedence Rule
Every finding, architectural resolution, and schema definition in this document strictly adheres to the non-negotiable 4-tier canonical hierarchy codified in `DECISION_BASELINE.md` and `contracts/architecture-invariants.json`:

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

### 1.2 Core Constitutional Axioms
1. **Draft vs. Physical Existence:** W0 reports represent draft source material. An architectural artifact is not "created" or recognized until the physical file exists in `solidbit-agent-execution-control-loop` and passes deterministic schema and AST validation.
2. **Review Semantics:** `DONE_REVIEW_REQUIRED` indicates that execution completed cleanly and produced reviewable deliverables, but mandates human inspection. **`DONE_REVIEW_REQUIRED` never means `PASS`.**
3. **Four-Part Reconciliation:** Run success and worker completion **must not** depend on `$Process.ExitCode` alone. Canonical reconciliation requires: process observation + persisted agent state + physical required outputs + final verdict extraction.
4. **Human Sovereignty & Safe Cessation:** The human developer (Joaquín) remains the sole sovereign principal. No automated agent may self-authorize merges, deployments, Jira issue transitions, or remote infrastructure mutations.

---

## 2. Comprehensive Remediation Status Matrix

The table below summarizes the formal status and physical materialization location for all seven audit findings identified during Wave 0 and reconciled under Wave 0.1:

| Finding ID | Severity | Category | W0 Finding Summary | W0.1 Canonical Resolution | Status | Primary Canonical Citations |
| :--- | :---: | :--- | :--- | :--- | :---: | :--- |
| **FINDING-P1-01** | P1 (High) | Protocol Divergence | Incompatible inbound Gmail subject syntax across AG-ARCH, AG-SEC, and AG-SCHEMA. | Subject line is strictly an intake routing hint `[SACL][JOB][v1][<JOB_ID>]`. Authoritative metadata lives in `manifest.json`. | **RESOLVED** | `docs/MAIL_PROTOCOL.md` §2.1<br>`docs/ARCHITECTURE.md` §2.2<br>`schemas/mail-envelope.schema.json`<br>`docs/adr/ADR-001-gmail-self-mailbox-transport.md` |
| **FINDING-P1-02** | P1 (High) | Cryptography & Security | Discrepancy in HMAC-SHA256 signature calculation payload between draft reports. | HMAC removed as a V1 requirement. Signing deferred to future hardening; ChatGPT Web cannot hold private secrets. | **RESOLVED** | `docs/adr/ADR-014-v1-transport-authentication-signing-deferred.md`<br>`docs/MAIL_PROTOCOL.md` §2.3<br>`docs/SECURITY_MODEL.md` §4.1<br>`docs/THREAT_MODEL.md` §2.1 |
| **FINDING-P1-03** | P1 (High) | Data Model | Discrepancy between architectural table/entity names and formal relational DDL. | Designate `AG-SCHEMA` §5.3 as sole canonical DDL (`supervisor_locks`, `runs`, `dag_stages`, `agents`, etc.). | **RESOLVED** | `db/migrations/001_init.sql`<br>`docs/SQLITE_DATA_MODEL.md`<br>`docs/adr/ADR-002-sqlite-operational-state-store.md` |
| **FINDING-P1-04** | P1 (High) | Runtime DDL Bug | SQLite `agents.result_verdict` CHECK constraint omitted legacy fallback `'PASS (Report Present)'`. | Include `'PASS (Report Present)'` in SQL DDL CHECK constraint, JSON schemas, and result extractor. | **RESOLVED** | `db/migrations/001_init.sql` (Line 90)<br>`docs/RESULT_PROTOCOL.md` §2<br>`docs/SQLITE_DATA_MODEL.md` §5.4<br>`schemas/result.schema.json` |
| **FINDING-P2-01** | P2 (Med) | Operational Policy | Overly restrictive duplicate replay rule blocked valid wave retries using the same `wave_id`. | Transport delivery is at-least-once. Deduplication on `(message_id, nonce)`. Retries use new nonce; same hash is ignored. | **RESOLVED** | `docs/adr/ADR-010-at-least-once-idempotent-processing.md`<br>`docs/MAIL_PROTOCOL.md` §2.4<br>`docs/RECOVERY_MODEL.md` §6<br>`docs/OPERATIONS.md` §2.2 |
| **FINDING-P2-02** | P2 (Med) | Contractual Deliverables | Ambiguity between `SUMMARY.md` (FINALIZE.ps1) and `SUMMARY.json` (OUTPUT_CONTRACT.md). | Dual deliverable mandate: both `SUMMARY.md` and `SUMMARY.json` are strictly required root deliverables. | **RESOLVED** | `docs/adr/ADR-011-filesystem-artifacts-sqlite-metadata.md`<br>`docs/EXECUTION_PACKAGE_SPEC.md` §1<br>`schemas/summary.schema.json`<br>`docs/OBSERVABILITY.md` §4 |
| **FINDING-P3-01** | P3 (Low) | Path Harmonization | Divergence between root PowerShell scripts and structured `src/<subsystem>/` paths. | Preserve root scripts for package runner compatibility; place modular reusable implementations under `src/`. | **RESOLVED** | `docs/CURRENT_ORCHESTRATOR_COMPATIBILITY_MATRIX.md` §5<br>`README.md` §4<br>`docs/ARCHITECTURE.md` §7.1 |

---

## 3. Granular Analysis & Resolution Records

---

### FINDING-P1-01: Inbound Gmail Subject Line Syntax & Parser Grammar

#### 1. Context & Divergence in W0
The three preliminary design drafts specified incompatible subject line formats and regular expressions:
1. **AG-ARCH** (§2.3): `^\[SACL-WAVE\]\[([a-zA-Z0-9_-]+)\]\[([a-zA-Z0-9_-]+)\]` (Format: `[SACL-WAVE][<ProjectID>][<WaveID>] <Description>`).
2. **AG-SEC** (§2.4): `^SACL-JOB:\s*([A-Za-z0-9_-]+)$`.
3. **AG-SCHEMA** (§3.2): `SACL-JOB: <PROJECT_ID> | <PACKAGE_ID> | <RUN_MODE> | NONCE:<HEX8>`.

In `AG-QA.REPORT.md` (Finding P1-01), the QA agent recommended adopting AG-SCHEMA's pipe-delimited syntax as canonical because it explicitly carried parameters like `NONCE`, `RUN_MODE`, and `PACKAGE_ID`.

#### 2. W0.1 Sovereign Correction & Remediation
The **W0.1 Freeze Remediation Baseline (Item 7)** and Joaquín's architectural directives overrode the W0 draft recommendation:
- **Email Subject is a Routing Hint, Never an Authority Source:** In a secure architecture, email subject lines must not be trusted as authoritative sources of project permissions, execution modes, or target repository paths. RFC 5322 subject headers are mutable transit metadata.
- **Canonical Routing Syntax:**
  ```text
  [SACL][JOB][v1][<JOB_ID>] <Optional Description>
  ```
- **Authoritative Configuration Location:** The target project, execution mode, worktree configuration, allowed agent fleet, and security boundaries reside strictly inside the hermetic, schema-validated package manifest (`manifest.json`) and `config/permissions.json`.
- **Parser Regex:**
  ```regex
  ^\[SACL\]\[JOB\]\[v1\]\[(?<job_id>[a-zA-Z0-9_-]+)\]
  ```

#### 3. Verification & Physical Artifacts
- **Physical Documentation:** Formally codified in [`docs/MAIL_PROTOCOL.md §2.1`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/MAIL_PROTOCOL.md), [`docs/ARCHITECTURE.md §2.2`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/ARCHITECTURE.md), and [`docs/OPERATIONS.md §2.3`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/OPERATIONS.md).
- **JSON Schema:** Validated by [`schemas/mail-envelope.schema.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/schemas/mail-envelope.schema.json) under property `routing_subject`.
- **Architectural Decision Record:** Formally accepted in [`docs/adr/ADR-001-gmail-self-mailbox-transport.md`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/adr/ADR-001-gmail-self-mailbox-transport.md).
- **Status:** **RESOLVED (CANONICAL)**.

---

### FINDING-P1-02: Cryptographic Signature Calculation Payload Divergence & Signing Deferral

#### 1. Context & Divergence in W0
The preliminary design reports proposed conflicting HMAC-SHA256 signature inputs:
1. **AG-ARCH** (ADR-012): HMAC computed directly over package attachment bytes.
2. **AG-SEC** (§2.4): Mentions `X-SACL-Signature` or embedded manifest checksum signed with DPAPI key.
3. **AG-SCHEMA** (§3.2): `X-SACL-Signature: sha256=<HMAC_HEX>` computed over `Date + "|" + Message-ID + "|" + Attachment_SHA256`.

`AG-QA.REPORT.md` (Finding P1-02) recommended adopting AG-SCHEMA's header-binding string as canonical.

#### 2. W0.1 Sovereign Correction & Remediation
The **W0.1 Freeze Remediation Baseline (Items 5 and 6)**, supported by explicit prompt instructions, decisively resolved this finding:
- **ChatGPT Web Cannot Possess Private Secrets:** ChatGPT Web is an interactive conversational web browser session. It does not have an isolated enclave, hardware security module, or secure key management service. Storing a long-lived private HMAC secret in ChatGPT Web introduces severe risks of token leakage in conversation transcripts, prompt histories, and browser caches.
- **HMAC Signing Removed from V1 Scope:** Package signing is **formally removed as a V1 requirement**. Attempting to mandate HMAC signing without an authentic key custody infrastructure represents security theater.
- **Future Hardening:** Cryptographic package signing is documented as deferred future hardening (targeted for Wave 2+ when an out-of-band signing CLI, local hardware token, or cloud KMS component is physically provisioned).
- **SACL V1 Multi-Layer Defense-in-Depth:**
  1. *Transport Channel Identity:* Google OAuth2 refresh token over TLS (App Passwords removed as V1 transport credential).
  2. *Strict Sender Whitelisting:* Mail Gateway drops all senders other than `uniquedraken@gmail.com`.
  3. *Subject Routing Hints:* Matches `[SACL][JOB][v1][<JOB_ID>]` routing hint (unread mailbox state is never the source of truth and not a gating input).
  4. *Attachment SHA-256 Tracking:* Every ZIP is hashed upon receipt and permanently recorded in `sacl_ops.db`.
  5. *Anti-Replay Controls:* SQLite tracking of `(message_id, nonce)` and `(job_id, hash)`.
  6. *Fail-Closed Path Sanitization:* Anti-Zip Slip, DOS device name, and NTFS ADS rejection.
  7. *Local Machine Governance & Human Authority Gates:* Pre-injected guard headers and mandatory human review before any irreversible action.

#### 3. Verification & Physical Artifacts
- **Architectural Decision Record:** Formally codified in [`docs/adr/ADR-014-v1-transport-authentication-signing-deferred.md`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/adr/ADR-014-v1-transport-authentication-signing-deferred.md).
- **Physical Documentation:** Updated across [`docs/SECURITY_MODEL.md §4.1`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/SECURITY_MODEL.md), [`docs/MAIL_PROTOCOL.md §2.3`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/MAIL_PROTOCOL.md), [`docs/THREAT_MODEL.md §2.1`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/THREAT_MODEL.md), and [`docs/OPERATIONS.md §2.4`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/OPERATIONS.md).
- **JSON Schema:** [`schemas/mail-envelope.schema.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/schemas/mail-envelope.schema.json) marks `signature_hmac` as optional future hardening, not required in V1.
- **Status:** **RESOLVED (CANONICAL)**.

---

### FINDING-P1-03: SQLite Schema DDL & Entity Naming Discrepancies

#### 1. Context & Divergence in W0
A naming and structural divergence existed between the high-level architecture in `AG-ARCH.REPORT.md` (§5.2) and the formal relational DDL in `AG-SCHEMA.REPORT.md` (§5.3):
- Supervisor lock: `orchestrator_lease` (AG-ARCH) vs `supervisor_locks` (AG-SCHEMA).
- Agent execution: `agent_runs` (AG-ARCH) vs `agents` (AG-SCHEMA) vs `agent_states` (AG-SEC).
- Stage table: `stages` (AG-ARCH) vs `dag_stages` (AG-SCHEMA).

#### 2. W0.1 Resolution
`AG-QA.REPORT.md` (Finding P1-03) and the W0.1 Remediation Baseline designated **`AG-SCHEMA.REPORT.md` Section 5.3 as the sole canonical relational DDL**:
- The unified database is named `sacl_ops.db`.
- Canonical relational tables:
  1. `supervisor_locks` (Instance leasing & heartbeat mutual exclusion)
  2. `runs` (Top-level run execution records and package metadata)
  3. `dag_stages` (Phased stage ordering and barrier synchronization)
  4. `agents` (Granular agent worker process tracking, PIDs, and verdicts)
  5. `agent_dependencies` (Directed DAG dependency edges)
  6. `file_modifications` (Files modified per agent worktree)
  7. `file_conflicts` (Detected cross-agent collisions across branches)
  8. `mail_inbox` (Inbound transport queue and anti-replay nonce tracking)
  9. `mail_outbox` (Outbound response dispatch queue)
  10. `audit_events` (Append-only immutable system security audit log)
- Any legacy references to non-canonical tables (such as `jobs` in early draft documentation) are formally updated to `runs`.

#### 3. Verification & Physical Artifacts
- **Physical DDL Migration:** Implemented in [`db/migrations/001_init.sql`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/db/migrations/001_init.sql).
- **Physical Documentation:** Exhaustively specified in [`docs/SQLITE_DATA_MODEL.md`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/SQLITE_DATA_MODEL.md) and [`docs/ARCHITECTURE.md §2.7`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/ARCHITECTURE.md).
- **Architectural Decision Record:** Formally accepted in [`docs/adr/ADR-002-sqlite-operational-state-store.md`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/adr/ADR-002-sqlite-operational-state-store.md).
- **Status:** **RESOLVED (CANONICAL)**.

---

### FINDING-P1-04: SQLite DDL CHECK Constraint Failure on Fallback Verdict `'PASS (Report Present)'`

#### 1. Context & Divergence in W0
In `AG-SCHEMA.REPORT.md`, a fatal inconsistency existed between the SQL DDL constraint and the Result Extraction Priority Ladder:
- SQL DDL (`agents` table, §5.3):
  ```sql
  result_verdict TEXT NOT NULL DEFAULT 'UNKNOWN' CHECK(result_verdict IN (
      'PASS', 'PARTIAL', 'BLOCKED', 'FAILED', 
      'IN_PROGRESS', 'UNKNOWN', 'STOPPED_BY_USER'
  ))
  ```
- Result Extractor Priority Ladder (§7.3): Priority 5 assigns `'PASS (Report Present)'` when a deliverable report physically exists on disk and is non-empty, but lacks an explicit regex marker.
- Legacy Behavior: `orchestrator-common.ps1#L309` returns `'PASS (Report Present)'`.
- Impact: Inserting `'PASS (Report Present)'` triggered an immediate SQLite `CHECK constraint failed: agents.result_verdict IN (...)` error, crashing reconciliation during benign fallback conditions.

#### 2. W0.1 Resolution
The **W0.1 Freeze Remediation Baseline (Item 11)** mandated preserving the legacy fallback verdict in the canonical result domain:
- The SQL DDL CHECK constraint in `db/migrations/001_init.sql` explicitly includes `'PASS (Report Present)'`:
  ```sql
  result_verdict TEXT NOT NULL DEFAULT 'UNKNOWN' CHECK(result_verdict IN (
      'PASS', 'PARTIAL', 'BLOCKED', 'FAILED', 
      'IN_PROGRESS', 'UNKNOWN', 'STOPPED_BY_USER',
      'PASS (Report Present)'
  ))
  ```
- The JSON schema `schemas/result.schema.json` includes `"PASS (Report Present)"` in its `result_verdict` enum.

#### 3. Verification & Physical Artifacts
- **Physical DDL Migration:** Verified in [`db/migrations/001_init.sql` (Line 90)](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/db/migrations/001_init.sql).
- **Physical Documentation:** Documented in [`docs/RESULT_PROTOCOL.md §2`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/RESULT_PROTOCOL.md), [`docs/SQLITE_DATA_MODEL.md §5.4`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/SQLITE_DATA_MODEL.md), and [`docs/OBSERVABILITY.md §3`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/OBSERVABILITY.md).
- **JSON Schema:** Validated in [`schemas/result.schema.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/schemas/result.schema.json).
- **Status:** **RESOLVED (CANONICAL)**.

---

### FINDING-P2-01: Overly Restrictive Replay Rule Blocking Valid Wave Retries

#### 1. Context & Divergence in W0
In `AG-ARCH.REPORT.md` (ADR-012 Line 679), the replay rule stated:
*"If a package with the same SHA-256 or wave_id has already been processed or is currently executing, it is rejected as a duplicate replay."*

If an execution failed due to an environmental or test issue, an engineer re-submitting the same wave ID (e.g. `W0`) would be permanently blocked unless the wave ID was manually changed.

#### 2. W0.1 Resolution
The **W0.1 Freeze Remediation Baseline (Items 8 and 9)** and `AG-QA.REPORT.md` (Finding P2-01) established refined at-least-once idempotency semantics:
- **At-Least-Once Delivery:** The transport layer guarantees at-least-once delivery; consumers must be strictly idempotent.
- **Message Deduplication Matrix:**
  - *Duplicate Delivery:* Same `message_id` and same `nonce` (or same `JOB_ID` + same package SHA-256) is idempotently ignored without failing. The message is acknowledged and marked read.
  - *Conflicting Payload:* Same `JOB_ID` + *different* package SHA-256 is flagged as an unresolvable collision and rejected fail-closed (`JOB_ID_HASH_MISMATCH`).
  - *Legitimate Retry / Recovery:* Re-submitting the same `JOB_ID` with a new `nonce` and updated `message_id` creates a new execution attempt record while preserving the logical job history.

#### 3. Verification & Physical Artifacts
- **Architectural Decision Record:** Formally codified in [`docs/adr/ADR-010-at-least-once-idempotent-processing.md`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/adr/ADR-010-at-least-once-idempotent-processing.md).
- **Physical Documentation:** Codified in [`docs/MAIL_PROTOCOL.md §2.4`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/MAIL_PROTOCOL.md), [`docs/RECOVERY_MODEL.md §6`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/RECOVERY_MODEL.md), and [`docs/OPERATIONS.md §2.2`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/OPERATIONS.md).
- **JSON Schema:** Validated in [`schemas/mail-envelope.schema.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/schemas/mail-envelope.schema.json).
- **Status:** **RESOLVED (CANONICAL)**.

---

### FINDING-P2-02: Dual Deliverable Requirement: `SUMMARY.md` & `SUMMARY.json`

#### 1. Context & Divergence in W0
A contractual ambiguity existed between specification files:
- `contracts/OUTPUT_CONTRACT.md` mandated `FINAL_REPORT.md` and `SUMMARY.json`.
- `manifest.json` and `FINALIZE.ps1` specifically required `SUMMARY.md`.

#### 2. W0.1 Resolution
The **W0.1 Freeze Remediation Baseline (Item 10)** and `AG-QA.REPORT.md` (Finding P2-02) mandated that every completed execution run physically produces **both** summary deliverable formats under `artifacts/runs/<runId>/`:
1. **`SUMMARY.md`:** Human-readable GitHub-flavored markdown executive summary presenting status tables, timing metrics, and remaining blockers for human operators.
2. **`SUMMARY.json`:** Machine-readable JSON summary validating strictly against `schemas/summary.schema.json` for programmatic consumption by the Cloud Control Plane.

#### 3. Verification & Physical Artifacts
- **Architectural Decision Record:** Formally codified in [`docs/adr/ADR-011-filesystem-artifacts-sqlite-metadata.md`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/adr/ADR-011-filesystem-artifacts-sqlite-metadata.md).
- **Physical Documentation:** Codified in [`docs/EXECUTION_PACKAGE_SPEC.md §1`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/EXECUTION_PACKAGE_SPEC.md), [`docs/OBSERVABILITY.md §4`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/OBSERVABILITY.md), and [`docs/RESULT_PROTOCOL.md §5`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/RESULT_PROTOCOL.md).
- **JSON Schema & Example:** Defined in [`schemas/summary.schema.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/schemas/summary.schema.json) and validated in [`examples/summary.valid.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/examples/summary.valid.json).
- **Status:** **RESOLVED (CANONICAL)**.

---

### FINDING-P3-01: Harmonization of Modular Subsystem Destination Paths

#### 1. Context & Divergence in W0
`AG-COMPAT.REPORT.md` mapped legacy scripts directly to refactored paths under `src/<module>/`, while `AG-ARCH.REPORT.md` and `AG-SCHEMA.REPORT.md` referenced root-level PowerShell entrypoints (`RUN-WAVE.ps1`, `WORKER.ps1`, `MONITOR.ps1`, `FINALIZE.ps1`, `STOP.ps1`).

#### 2. W0.1 Resolution
The **W0.1 Freeze Remediation Baseline (Item 14)** and `AG-QA.REPORT.md` (Finding P3-01) harmonized the path architecture:
- **Root-Level Compatibility Entrypoints Preserved:** Root-level scripts are maintained to provide 100% backwards-compatible entrypoints for wave package runners.
- **Structured Modular Library Implementation:** Reusable, refactored core logic belongs under the structured `src/` hierarchy (`src/workspace/`, `src/executor/`, `src/scheduler/`, `src/validator/`, `src/supervisor/`, `src/gateway/`) to be implemented during subsequent functional development waves.

#### 3. Verification & Physical Artifacts
- **Physical Documentation:** Documented in [`docs/CURRENT_ORCHESTRATOR_COMPATIBILITY_MATRIX.md §5`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/CURRENT_ORCHESTRATOR_COMPATIBILITY_MATRIX.md), [`README.md §4`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/README.md), and [`docs/ARCHITECTURE.md §7.1`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/ARCHITECTURE.md).
- **Architectural Decision Record:** Codified in [`docs/adr/ADR-004-wave-package-compatibility.md`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/adr/ADR-004-wave-package-compatibility.md).
- **Status:** **RESOLVED (CANONICAL)**.

---

## 4. Wave 0.2 Freeze Consistency Remediation Matrix (SB-FREEZE-P1-01 through P1-08, P2-01 through P2-02)

Following the initial Wave 0.1 snapshot materialization, a Direct Human Semantic Audit identified ten blocking architectural contradictions. The table below summarizes the formal resolution and verified evidence for each finding:

| Finding ID | Severity | Category | Audit Inconsistency Summary | Canonical Resolution | Primary Citations | Status |
| :--- | :---: | :--- | :--- | :--- | :--- | :---: |
| **SB-FREEZE-P1-01** | P1 (High) | Transport Architecture | Gmail event architecture silently replaced with IMAP/SMTP polling/IDLE. | Restored Gmail API `users.watch` + Cloud Pub/Sub pull subscriber as wake signal; authoritative fetch via Gmail History API with persisted `historyId` cursor; automatic watch renewal; startup reconciliation; periodic fallback polling only; outbound dispatch via Gmail REST API; zero SMTP in V1. | `docs/MAIL_PROTOCOL.md` §1–§2<br>`docs/ARCHITECTURE.md` §2.2–§2.3<br>`docs/adr/ADR-001-gmail-self-mailbox-transport.md`<br>`DECISION_BASELINE.md` §3.1 | **RESOLVED** |
| **SB-FREEZE-P1-02** | P1 (High) | Package Authority | Untrusted packages could self-authorize attached code via `authorized_scripts`. | Execution packages are strictly declarative. `authorized_scripts` field prohibited and removed. Packages declare requested stable operation IDs (`requested_operations`). Local SACL core autoexecution only invokes locally trusted handlers from the Local Operation Registry. | `docs/EXECUTION_PACKAGE_SPEC.md` §1, §3<br>`docs/AUTHORITY_MODEL.md` §3<br>`docs/adr/ADR-006-no-arbitrary-remote-code.md`<br>`DECISION_BASELINE.md` §3.2 | **RESOLVED** |
| **SB-FREEZE-P1-03** | P1 (High) | Permission Lattice | Effective-permission lattice missing; policy schema permitted dangerous booleans without hard local policy. | Codified formal four-layer lattice: $\text{Effective Permissions} = \text{Hard Local Policy} \cap \text{Project Policy} \cap \text{Package Requested} \cap \text{Approval Grant}$. Hard deny always wins. Approval cannot override hard deny. Hard local policy permanently denies remote production, merges, DB writes, secret export, arbitrary remote code in V1. | `docs/AUTHORITY_MODEL.md` §2<br>`docs/SECURITY_MODEL.md` §1–§2<br>`docs/adr/ADR-012-no-remote-production-v1.md`<br>`DECISION_BASELINE.md` §3.3 | **RESOLVED** |
| **SB-FREEZE-P1-04** | P1 (High) | State Lifecycle | Canonical 12-state job lifecycle and Graph-H node states replaced by simplified model. | Restored canonical 12-state linear job lifecycle (`RECEIVED`..`ARCHIVED`), 10 side states/outcomes (`WAITING_APPROVAL`..`QUARANTINED`), and Graph-H node states (`PENDING`..`SUCCEEDED` + side outcomes). | `docs/STATE_MACHINE.md` §2<br>`docs/SQLITE_DATA_MODEL.md` §5.4<br>`docs/adr/ADR-013-run-status-reconciliation.md`<br>`DECISION_BASELINE.md` §3.4 | **RESOLVED** |
| **SB-FREEZE-P1-05** | P1 (High) | Operational Data Tier | SQLite state store DDL incomplete (only 10 tables; missing schema migrations, projects, packages, mail cursors, jobs, nodes, attempts, approvals, artifacts, results, leases, heartbeats, errors). | Codified complete relational schema across 16 formal operational domains in `sacl_ops.db` while preserving compatibility tables. Connection bootstrap enforces WAL, busy_timeout 5000, synchronous NORMAL, and foreign_keys ON. Forward-only migration tracking. | `docs/SQLITE_DATA_MODEL.md`<br>`docs/ARCHITECTURE.md` §5.2<br>`docs/adr/ADR-002-sqlite-operational-state-store.md`<br>`DECISION_BASELINE.md` §3.6 | **RESOLVED** |
| **SB-FREEZE-P1-06** | P1 (High) | Approval Contract | Approval contract freeze-centric and omitted mandatory binding to action, scope, request_id, and expiration. | Codified generic bounded action-approval contract bound strictly to: `JOB_ID + ACTION + SCOPE + REQUEST_ID + expires_at`. Documented resumption semantics: approval resumes the same logical run without spawning disconnected runs. Approvals cannot exceed hard local policy or override hard denies. | `docs/AUTHORITY_MODEL.md` §4<br>`docs/adr/ADR-007-human-authority.md`<br>`DECISION_BASELINE.md` §3.5 | **RESOLVED** |
| **SB-FREEZE-P1-07** | P1 (High) | Baseline Invariants | Missing physical `DECISION_BASELINE.md` file from canonical repository root and W0.1 gate. | Codified root `DECISION_BASELINE.md` distinguishing explicit Joaquín decisions from derived architecture synthesis, canonical precedence rules, and architecture invariants. Codified machine-readable `contracts/architecture-invariants.json` inside repository. | `DECISION_BASELINE.md`<br>`docs/adr/ADR-005-decision-precedence.md`<br>`README.md` §2 | **RESOLVED** |
| **SB-FREEZE-P1-08** | P1 (High) | Documentation Index | `docs/ARCHITECTURE.md` embedded an ADR-001..ADR-013 list whose numbers and titles contradicted actual files under `docs/adr/ADR-001..ADR-014`. | Designated physical ADR files as canonical authority. Reconciled `docs/ARCHITECTURE.md` Section 6 index to match exact physical ADR-001 through ADR-014 numbers and titles verbatim. Traced complete 14 ADR set. | `docs/ARCHITECTURE.md` §6<br>`docs/adr/ADR-001` through `ADR-014`<br>`docs/TRACEABILITY_MATRIX.md` §6 | **RESOLVED** |
| **SB-FREEZE-P2-01** | P2 (Med) | Manifest Contract | `job_id` optional in `manifest.schema.json`, breaking transport routing hint and idempotency design. | Made `job_id` mandatory in `schemas/manifest.schema.json` with regex pattern `^[A-Za-z0-9_.-]+$`. Updated package specifications and valid examples. | `docs/EXECUTION_PACKAGE_SPEC.md` §3.2<br>`docs/MAIL_PROTOCOL.md` §2.1<br>`DECISION_BASELINE.md` §3.4 | **RESOLVED** |
| **SB-FREEZE-P2-02** | P2 (Med) | Summary Schema | Universal summary schema permanently forbade implementation authorization via `const: false`. | Updated `schemas/summary.schema.json` to allow `implementation_authorized` as `type: "boolean"`. Preserved `false` in current W0/W0.1/W0.2 artifacts while allowing schema to represent future explicit human authorization. Summary boolean remains evidence, not authority. | `docs/EXECUTION_PACKAGE_SPEC.md` §1<br>`docs/RESULT_PROTOCOL.md`<br>`DECISION_BASELINE.md` §3.7 | **RESOLVED** |

---

## 5. Granular Analysis & Verification Evidence (SB-FREEZE-P1-01 through P2-02)

### SB-FREEZE-P1-01: Restoration of Selected Gmail Event Architecture
1. **Context & Inconsistency:** The W0.1 canonical documents silently substituted legacy IMAP/SMTP polling and IMAP IDLE for the established Gmail API event design. `users.watch`, Pub/Sub pull subscriptions, and `historyId` tracking were omitted.
2. **Canonical Resolution:** Restored the event-driven architecture: Gmail API `users.watch` publishes mailbox changes to a Google Cloud Pub/Sub topic; local Mail Gateway subscribes via outbound Pull/StreamingPull (zero inbound open ports, no public webhooks); Pub/Sub notifications serve strictly as wake signals; authoritative message metadata and attachments are fetched via Gmail History API (`users.history.list`) using the persisted `historyId` cursor in SQLite table `mail_messages`/`mail_cursors`; automatic watch renewal prior to expiration; startup reconciliation from persisted cursor; periodic direct polling retained strictly as degraded fallback; outbound results dispatched directly via Gmail REST API (`users.messages.send`); zero SMTP in V1.
3. **Verification Evidence:**
   - Codified in [`DECISION_BASELINE.md §3.1`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/DECISION_BASELINE.md) and [`contracts/architecture-invariants.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/contracts/architecture-invariants.json) (`primary_ingress = "gmail_api_users_watch_pubsub_pull"`, `cursor = "historyId"`).
   - Detailed in [`docs/MAIL_PROTOCOL.md §1–§2`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/MAIL_PROTOCOL.md) and [`docs/ARCHITECTURE.md §2.2–§2.3, §3.1`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/ARCHITECTURE.md).
   - Formally accepted in [`docs/adr/ADR-001-gmail-self-mailbox-transport.md`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/adr/ADR-001-gmail-self-mailbox-transport.md).
   - Implemented in database migration [`db/migrations/001_init.sql`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/db/migrations/001_init.sql) Domain 11 (`mail_messages` with `history_id`).
4. **Status:** **RESOLVED (CANONICAL)**.

### SB-FREEZE-P1-02: Declarative Package Authority & Removal of `authorized_scripts`
1. **Context & Inconsistency:** W0.1 manifest schema included `authorized_scripts`, and `EXECUTION_PACKAGE_SPEC` asserted that a script listed in that field could run after policy validation. Because wave packages arrive from external transport, an untrusted package cannot self-authorize executable code.
2. **Canonical Resolution:** Packages are strictly declarative in authority. The manifest field `authorized_scripts` is permanently removed and prohibited as an authority field. Packages request stable operation IDs via `requested_operations`. Local SACL core autoexecution only invokes locally trusted handlers from the Local Operation Registry (`schemas/operation-registry.schema.json`) owned and maintained on the local host. Preserved the `scripts/` directory inside package archives for backward compatibility and manual review only.
3. **Verification Evidence:**
   - Manifest schema [`schemas/manifest.schema.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/schemas/manifest.schema.json) requires `requested_operations` and prohibits `authorized_scripts`.
   - Local Operation Registry schema [`schemas/operation-registry.schema.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/schemas/operation-registry.schema.json) and valid instance [`examples/operation-registry.valid.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/examples/operation-registry.valid.json).
   - Codified in [`docs/AUTHORITY_MODEL.md §3`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/AUTHORITY_MODEL.md) and [`docs/EXECUTION_PACKAGE_SPEC.md §1, §3`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/EXECUTION_PACKAGE_SPEC.md).
   - Formally accepted in [`docs/adr/ADR-006-no-arbitrary-remote-code.md`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/adr/ADR-006-no-arbitrary-remote-code.md).
4. **Status:** **RESOLVED (CANONICAL)**.

### SB-FREEZE-P1-03: Four-Layer Effective-Permission Lattice & Hard Local Denials
1. **Context & Inconsistency:** The four-layer permission lattice was absent from W0.1 governance documents. Furthermore, `policy.schema.json` permitted operational booleans such as `production_deploy=true`, `production_db_write=true`, `secret_export=true`, and `remote_execution_enabled=true` without a hard local policy contract to constrain them.
2. **Canonical Resolution:** Established the mathematical four-layer lattice: $\text{Effective Permissions} = \text{Hard Local Policy} \cap \text{Project Policy} \cap \text{Package Requested Permissions} \cap \text{Valid Approval Grant}$. Hard deny always wins; approval cannot override a hard deny. Hard Local Policy (`schemas/hard-policy.schema.json`) strictly encodes permanent hard denies for V1: `remote_production_execution`, `github_merge`, `production_db_write`, `secret_export`, `arbitrary_remote_code`, `main_branch_execution`, `primary_checkout_mutation`, `hard_reset`, `auto_stash`.
3. **Verification Evidence:**
   - Codified in [`DECISION_BASELINE.md §3.3`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/DECISION_BASELINE.md) and [`contracts/architecture-invariants.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/contracts/architecture-invariants.json) (`hard_deny_wins = true`, `approval_can_override_hard_deny = false`, `remote_production_v1 = false`).
   - Hard policy schema [`schemas/hard-policy.schema.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/schemas/hard-policy.schema.json) and validated instance [`examples/hard-policy.valid.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/examples/hard-policy.valid.json).
   - Codified in [`docs/AUTHORITY_MODEL.md §2`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/AUTHORITY_MODEL.md) and [`docs/SECURITY_MODEL.md §1–§2`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/SECURITY_MODEL.md).
   - Formally accepted in [`docs/adr/ADR-012-no-remote-production-v1.md`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/adr/ADR-012-no-remote-production-v1.md).
4. **Status:** **RESOLVED (CANONICAL)**.

### SB-FREEZE-P1-04: Restoration of Canonical 12-State Job Lifecycle & Node States
1. **Context & Inconsistency:** W0.1 `STATE_MACHINE.md` and related documents replaced the canonical job lifecycle with a simplified run state model (`INITIALIZED`, `RUNNING`, `COMPLETE`, `FAILED`), omitting essential intermediate and side states.
2. **Canonical Resolution:** Restored the canonical 12-state linear job lifecycle: `RECEIVED` $\rightarrow$ `AUTHENTICATED` $\rightarrow$ `VALIDATED` $\rightarrow$ `PERSISTED` $\rightarrow$ `QUEUED` $\rightarrow$ `DISPATCHED` $\rightarrow$ `RUNNING` $\rightarrow$ `VERIFYING` $\rightarrow$ `RESULT_PACKAGED` $\rightarrow$ `RESULT_SENT` $\rightarrow$ `COMPLETED` $\rightarrow$ `ARCHIVED`. Restored all 10 side states and outcomes: `WAITING_APPROVAL`, `RETRY_WAIT`, `BLOCKED`, `FAILED`, `CANCELLED`, `INTERRUPTED`, `TIMED_OUT`, `POLICY_DENIED`, `REJECTED`, `QUARANTINED`. Restored Graph-H node states: `PENDING` $\rightarrow$ `READY` $\rightarrow$ `RUNNING` $\rightarrow$ `SUCCEEDED` with side outcomes `RETRYABLE_FAILURE`, `FAILED`, `BLOCKED`, `WAITING_APPROVAL`, `CANCELLED`.
3. **Verification Evidence:**
   - Codified in [`DECISION_BASELINE.md §3.4`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/DECISION_BASELINE.md) and [`contracts/architecture-invariants.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/contracts/architecture-invariants.json) (`job_lifecycle`, `job_side_states`, `graph_node_states`).
   - Complete state machine and transition matrices codified in [`docs/STATE_MACHINE.md §2`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/STATE_MACHINE.md).
   - Enforced by CHECK constraints in [`db/migrations/001_init.sql`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/db/migrations/001_init.sql) Domain 4 (`jobs.status`) and Domain 6 (`graph_nodes.status`).
4. **Status:** **RESOLVED (CANONICAL)**.

### SB-FREEZE-P1-05: Codification of 16 SQLite Operational Domains
1. **Context & Inconsistency:** The W0.1 DDL contained only 10 tables, omitting structured domains for schema migrations, projects, packages, mail cursors, jobs, nodes, attempts, approvals, artifacts, results, leases, heartbeats, and errors.
2. **Canonical Resolution:** Codified the complete relational schema across 16 formal operational domains in SQLite (`sacl_ops.db`): (1) `schema_migrations`, (2) `projects`, (3) `packages`, (4) `jobs`, (5) `runs`, (6) `graph_nodes`, (7) `node_attempts`, (8) `agents`, (9) `agent_dependencies` / `dag_stages`, (10) `file_modifications` / `file_conflicts`, (11) `mail_messages` / `mail_cursors`, (12) `mail_outbox`, (13) `audit_events` / `events`, (14) `approvals`, (15) `artifacts` / `results`, (16) `leases` (`supervisor_locks`), `heartbeats`, `errors`. Backward-compatible tables are preserved. Connection bootstrap enforces WAL, busy_timeout 5000, synchronous NORMAL, and foreign_keys ON.
3. **Verification Evidence:**
   - Migration file [`db/migrations/001_init.sql`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/db/migrations/001_init.sql) executes cleanly in disposable SQLite in-memory instance.
   - Comprehensive entity-relationship model and schema specifications codified in [`docs/SQLITE_DATA_MODEL.md`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/SQLITE_DATA_MODEL.md).
   - Formally accepted in [`docs/adr/ADR-002-sqlite-operational-state-store.md`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/adr/ADR-002-sqlite-operational-state-store.md).
4. **Status:** **RESOLVED (CANONICAL)**.

### SB-FREEZE-P1-06: Generic Bounded Action-Approval Contract
1. **Context & Inconsistency:** The W0.1 approval schema was freeze-specific and did not enforce binding to job ID, action, scope, request ID, or expiration timestamp.
2. **Canonical Resolution:** Replaced with a generic bounded action-approval contract bound strictly to: `JOB_ID + ACTION + SCOPE + REQUEST_ID + expires_at`. Documented resumption semantics: approval resumes the same logical run without spawning disconnected runs. Approvals cannot exceed the hard local policy envelope or override hard denies.
3. **Verification Evidence:**
   - Approval schema [`schemas/approval.schema.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/schemas/approval.schema.json) requires `request_id`, `job_id`, `action`, `scope`, `expires_at`, `decision`, `approver`. Validated against [`examples/approval.valid.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/examples/approval.valid.json).
   - Codified in [`docs/AUTHORITY_MODEL.md §4`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/AUTHORITY_MODEL.md) and [`DECISION_BASELINE.md §3.5`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/DECISION_BASELINE.md).
   - Database table `approvals` codified in [`db/migrations/001_init.sql`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/db/migrations/001_init.sql) Domain 14.
   - Formally accepted in [`docs/adr/ADR-007-human-authority.md`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/adr/ADR-007-human-authority.md).
4. **Status:** **RESOLVED (CANONICAL)**.

### SB-FREEZE-P1-07: Materialization of `DECISION_BASELINE.md` & `architecture-invariants.json`
1. **Context & Inconsistency:** Canonical specifications referenced `DECISION_BASELINE.md` as the root physical baseline of explicit human decisions, but the file was absent from the canonical repository root and W0.1 gates.
2. **Canonical Resolution:** Codified root [`DECISION_BASELINE.md`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/DECISION_BASELINE.md) distinguishing explicit Joaquín decisions from derived/ratified SACL architecture decisions, canonical precedence rules, and architecture invariants. Codified machine-readable equivalent [`contracts/architecture-invariants.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/contracts/architecture-invariants.json) conforming to `solidbit.architecture-invariants.v1`.
3. **Verification Evidence:**
   - Both [`DECISION_BASELINE.md`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/DECISION_BASELINE.md) and [`contracts/architecture-invariants.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/contracts/architecture-invariants.json) physically exist on disk and validate cleanly.
   - Formally accepted in [`docs/adr/ADR-005-decision-precedence.md`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/adr/ADR-005-decision-precedence.md).
4. **Status:** **RESOLVED (CANONICAL)**.

### SB-FREEZE-P1-08: ADR Index & Numbering Harmonization
1. **Context & Inconsistency:** `docs/ARCHITECTURE.md` embedded an ADR-001..ADR-013 list whose numbers and titles contradicted the actual physical files under `docs/adr/ADR-001..ADR-014`.
2. **Canonical Resolution:** Designated physical ADR files under `docs/adr/` as the canonical authority. Reconciled `docs/ARCHITECTURE.md` Section 6 index so that all 14 ADR numbers, titles, and scopes match the physical ADR files verbatim:
   - ADR-001: Gmail Self-Mailbox Transport via Gmail API and Cloud Pub/Sub Pull for Asynchronous Control Loop
   - ADR-002: SQLite Operational State Store (`sacl_ops.db`)
   - ADR-003: Persistent IDLE Supervisor Daemon (`Graph-P`) with Zero Idle Token Burn
   - ADR-004: Self-Contained Runnable Wave Package Compatibility Model
   - ADR-005: Sovereign Decision Precedence Hierarchy
   - ADR-006: Prohibition of Arbitrary Remote Code Execution and Governed Worker Execution
   - ADR-007: Sovereign Human Authority Gate for Irreversible Operations
   - ADR-008: Structural Process Separation of Mail Gateway and Orchestrator Core (`Graph-P`)
   - ADR-009: Multi-Project Parameterization via Manifest vs Hardcoded Single-Repo Paths
   - ADR-010: At-Least-Once Delivery and Idempotent Ingestion Semantics
   - ADR-011: Filesystem Retention for Heavy Artifacts and SQLite Metadata Model
   - ADR-012: Strict Prohibition of Remote Production Execution in SACL V1
   - ADR-013: Multi-Dimensional Run Status Reconciliation and Diagnostic Timeouts
   - ADR-014: V1 Transport Authentication Model and Deferral of Package Signing
3. **Verification Evidence:**
   - Verified 14/14 physical ADR files exist under `docs/adr/`.
   - Verified [`docs/ARCHITECTURE.md §6`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/ARCHITECTURE.md) index exactly matches physical files.
   - Verified [`docs/TRACEABILITY_MATRIX.md §6`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/TRACEABILITY_MATRIX.md) maps all 14 ADRs to their implementing subsystems.
4. **Status:** **RESOLVED (CANONICAL)**.

### SB-FREEZE-P2-01: Mandatory `job_id` in Package Manifest Schema
1. **Context & Inconsistency:** The manifest schema made `job_id` optional, compromising the transport routing hint grammar and idempotency deduplication design.
2. **Canonical Resolution:** Made `job_id` mandatory in [`schemas/manifest.schema.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/schemas/manifest.schema.json) for remotely transported execution packages, constrained by pattern `^[A-Za-z0-9_.-]+$`.
3. **Verification Evidence:**
   - Manifest schema [`schemas/manifest.schema.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/schemas/manifest.schema.json) includes `"job_id"` in `required` array.
   - Example instance [`examples/manifest.valid.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/examples/manifest.valid.json) validates with mandatory `job_id`.
   - Codified in [`docs/EXECUTION_PACKAGE_SPEC.md §3.2`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/EXECUTION_PACKAGE_SPEC.md).
4. **Status:** **RESOLVED (CANONICAL)**.

### SB-FREEZE-P2-02: Universal Run Summary Schema Support for Human Authorization
1. **Context & Inconsistency:** `summary.schema.json` constrained `implementation_authorized` to `false` via a `const` restriction, permanently forbidding representation of explicit human implementation authorization.
2. **Canonical Resolution:** Updated `schemas/summary.schema.json` to define `implementation_authorized` as `type: "boolean"`. W0/W0.1/W0.2 instances remain `false` during architecture freeze, but the schema now properly allows representing subsequent explicit human authorization grants. A summary boolean remains evidence, not authority.
3. **Verification Evidence:**
   - Summary schema [`schemas/summary.schema.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/schemas/summary.schema.json) defines `"implementation_authorized": { "type": "boolean" }`.
   - Example instance [`examples/summary.valid.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/examples/summary.valid.json) validates cleanly with `implementation_authorized: false`.
   - Codified in [`docs/EXECUTION_PACKAGE_SPEC.md §1`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/EXECUTION_PACKAGE_SPEC.md) and [`docs/RESULT_PROTOCOL.md §5`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/RESULT_PROTOCOL.md).
4. **Status:** **RESOLVED (CANONICAL)**.

---

## 6. Wave 0.3 Final Architecture Freeze Remediation Matrix & Granular Evidence

Following Wave 0.2, the final Wave 0.3 Direct Human Semantic Review identified six remaining precision findings requiring definitive codification. The table below summarizes each finding and its canonical resolution:

| Finding ID | Severity | Category | Audit Inconsistency Summary | Canonical Resolution | Primary Citations | Status |
| :--- | :---: | :--- | :--- | :--- | :--- | :---: |
| **SB-FREEZE-P1-09** | P1 (High) | Decision Provenance | Conflation of direct human rulings with derived agent synthesis under broad "25 sovereign decisions" banner. | Formally separated explicit Joaquín decisions (direct directives #10–#19, #21–#25; baseline context #1–#9) from derived/ratified SACL architecture decisions (Decision #20, SB-FREEZE-P1-01 through P1-06, P1-09 through P1-11, P2-01 through P2-05). Enforced rule: agent-derived decisions are never attributed to direct human decree. | `DECISION_BASELINE.md` §1.1, §2.1–§2.3<br>`docs/TRACEABILITY_MATRIX.md` §1.1, §2.1–§2.2<br>`contracts/architecture-invariants.json`<br>`docs/adr/ADR-005-decision-precedence.md` | **RESOLVED** |
| **SB-FREEZE-P1-10** | P1 (High) | Runtime Boundary | Contradictory hermetic phrasing asserting "zero runtime cloud lookups" while relying on Gmail API, Pub/Sub, and Antigravity CLI. | Replaced contradictory hermetic wording: execution packages carry complete, self-contained, versioned task context on disk (prompts, schemas, manifests, policies, references) for deterministic offline task interpretation. Explicitly configured runtime services (Gmail API over TLS, Cloud Pub/Sub pull subscriber, Antigravity CLI, Git, and conditionally GitHub) are allowed by policy under hard local constraints. | `DECISION_BASELINE.md` §3.2<br>`contracts/architecture-invariants.json`<br>`docs/CURRENT_ORCHESTRATOR_COMPATIBILITY_MATRIX.md` §4<br>`docs/adr/ADR-004-self-contained-wave-packages.md` | **RESOLVED** |
| **SB-FREEZE-P1-11** | P1 (High) | Remote Git Authority | Ambiguity between blanket "zero remote git writes" and operational requirement for task branch push and PR creation. | Codified Controlled GitHub Write Semantics: direct push to main/master/release is hard-denied; GitHub merge is hard-denied in V1; feature/task branch push and PR creation are permitted strictly through locally trusted operations from the Local Operation Registry when hard local policy, project policy, package request, and valid bounded human approval all allow it; W0.3 performs zero GitHub writes. | `DECISION_BASELINE.md` §3.9<br>`contracts/architecture-invariants.json`<br>`docs/AUTHORITY_MODEL.md` §2<br>`docs/SECURITY_MODEL.md` §1.1<br>`docs/CURRENT_ORCHESTRATOR_COMPATIBILITY_MATRIX.md` §4 | **RESOLVED** |
| **SB-FREEZE-P2-03** | P2 (Med) | Transport Auth & Ingress | Gmail App Passwords referenced as credential; mailbox UI unread state treated as gating/source of truth. | Gmail API OAuth2 (refresh token + client credentials over TLS) designated sole canonical V1 credential. App Passwords permanently removed. Authoritative ingress decoupled from mailbox UI read/unread states: Gmail `historyId` and Pub/Sub message IDs are authoritative; unread state is never source of truth or gating input. | `DECISION_BASELINE.md` §3.1<br>`contracts/architecture-invariants.json`<br>`docs/MAIL_PROTOCOL.md` §2.1, §2.4<br>`docs/adr/ADR-001-gmail-self-mailbox-transport.md` | **RESOLVED** |
| **SB-FREEZE-P2-04** | P2 (Med) | Invariants Contract | `contracts/architecture-invariants.json` absent or inconsistent in canonical repository root. | Materialized canonical machine-readable contract `contracts/architecture-invariants.json` conforming to `solidbit.architecture-invariants.v1`, validating clean JSON grammar and matching all W0.3 architecture invariants. | `contracts/architecture-invariants.json`<br>`README.md` §4<br>`DECISION_BASELINE.md` §1.2 | **RESOLVED** |
| **SB-FREEZE-P2-05** | P2 (Med) | Approval Schema | Approval schema included `WEBHOOK` in channel enum, violating zero-inbound-listener network boundary. | Removed `WEBHOOK` from approval channel enum. Canonical V1 approval channels constrained strictly to `["CLI", "GMAIL", "MANUAL"]`. Validated schema and example instance. | `schemas/approval.schema.json`<br>`examples/approval.valid.json`<br>`docs/AUTHORITY_MODEL.md` §4 | **RESOLVED** |

### SB-FREEZE-P1-09: Decision Provenance Separation: Explicit Joaquín Decisions vs Derived Synthesis
1. **Context & Inconsistency:** Earlier documentation indiscriminately listed "25 sovereign human decisions" as if every item had been personally decreed by Joaquín. This conflated direct sovereign decisions (#10–#19, #21–#25; #1–#9 baseline context) with agent-derived architectural choices (e.g., #20 "hermetic packages" and subsequent engineering choices).
2. **Canonical Resolution:** Established the 4-tier precedence hierarchy across all governance documentation:
   1. *Tier 1: Explicit Joaquín decisions* (Direct human directives #10–#19, #21–#25, plus baseline context #1–#9).
   2. *Tier 2: Proven current-orchestrator behavior* (Observable stable runtime mechanics from `Stable-Ecommerce-Orchestrator`).
   3. *Tier 3: Existing governance/contracts* (Ratified SACL architecture decisions: Decision #20, SB-FREEZE-P1-01 through P1-06, P1-09 through P1-11, P2-01 through P2-05).
   4. *Tier 4: Industry standards for undefined gaps only* (Industry conventions for gaps with zero prior guidance; never overrides higher tiers).
   No agent-derived decision is ever represented as an explicit Joaquín decree.
3. **Verification Evidence:**
   - Codified in [`DECISION_BASELINE.md §1.1, §2.1–§2.3`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/DECISION_BASELINE.md).
   - Codified in [`docs/TRACEABILITY_MATRIX.md §1.1, §2.1–§2.2, §4.3`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/TRACEABILITY_MATRIX.md).
   - Formally accepted in [`docs/adr/ADR-005-decision-precedence.md`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/adr/ADR-005-decision-precedence.md).
4. **Status:** **RESOLVED (CANONICAL)**.

### SB-FREEZE-P1-10: Clarification of Package Task Context vs Allowed Runtime Services
1. **Context & Inconsistency:** Prior documentation contained contradictory "hermetic" statements asserting "zero runtime cloud lookups" and "strict network isolation", directly conflicting with the orchestrator's active use of Gmail API, Google Cloud Pub/Sub, Antigravity CLI, Git, and GitHub.
2. **Canonical Resolution:** Replaced contradictory hermetic wording with precise boundaries:
   - *Task Context Hermeticity:* An execution package must be self-contained and versioned on disk, carrying all prompts, manifests, schemas, hard policies, and reference material necessary for offline task interpretation. Local workers do not rely on external conversational context or unversioned remote repos during execution.
   - *Allowed Runtime Services:* SACL is an asynchronous control loop that legitimately communicates with configured external runtime services: Gmail API (REST over TLS), Google Cloud Pub/Sub (Pull/StreamingPull subscriber), Antigravity CLI (local process execution), Git (local repository operations), and conditionally GitHub (feature branch push and PR creation via trusted handlers). These services operate through strictly bounded gateways under hard local policy constraints.
3. **Verification Evidence:**
   - Codified in [`DECISION_BASELINE.md §3.2`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/DECISION_BASELINE.md) and [`contracts/architecture-invariants.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/contracts/architecture-invariants.json).
   - Codified in [`docs/CURRENT_ORCHESTRATOR_COMPATIBILITY_MATRIX.md §4 item 8`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/CURRENT_ORCHESTRATOR_COMPATIBILITY_MATRIX.md).
   - Formally accepted in [`docs/adr/ADR-004-self-contained-wave-packages.md`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/adr/ADR-004-self-contained-wave-packages.md).
4. **Status:** **RESOLVED (CANONICAL)**.

### SB-FREEZE-P1-11: Controlled GitHub Write Semantics and Branching Model
1. **Context & Inconsistency:** Architectural documents stated blanket prohibitions on remote git operations ("zero remote git writes"), conflicting with planned V1 workflows requiring feature branch pushes and Pull Request creation.
2. **Canonical Resolution:** Codified Controlled GitHub Write Semantics:
   - Direct push to `main`, `master`, or release branches is **permanently hard denied** by Hard Local Policy.
   - GitHub merge operations are **hard denied in V1** (merging remains strictly external, performed by human maintainers or CI/CD).
   - Feature/task branch push (`refs/heads/feature/*`, `refs/heads/task/*`) and PR creation are permitted ONLY through locally trusted operations (`git.push_branch`, `github.create_pr`) from the Local Operation Registry when all four lattice tiers permit it: Hard Local Policy allows git operations, Project Policy permits target repository push/PR, the execution package explicitly requests the operation, and a valid bounded human approval grant exists.
   - Wave 0.3 itself performs strictly **zero GitHub writes** (`IMPLEMENTATION_AUTHORIZED=NO`).
3. **Verification Evidence:**
   - Codified in [`DECISION_BASELINE.md §3.9`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/DECISION_BASELINE.md) and [`contracts/architecture-invariants.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/contracts/architecture-invariants.json).
   - Codified in [`docs/AUTHORITY_MODEL.md §2`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/AUTHORITY_MODEL.md), [`docs/SECURITY_MODEL.md §1.1`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/SECURITY_MODEL.md), and [`docs/CURRENT_ORCHESTRATOR_COMPATIBILITY_MATRIX.md §4 item 7`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/CURRENT_ORCHESTRATOR_COMPATIBILITY_MATRIX.md).
4. **Status:** **RESOLVED (CANONICAL)**.

### SB-FREEZE-P2-03: Gmail API OAuth2 Transport Authentication & Mailbox State Decoupling
1. **Context & Inconsistency:** Earlier documents retained legacy references to Gmail App Passwords, and mail deduplication / filtering referenced `is:unread` or marking messages read/archived as gating inputs, erroneously making mailbox UI state the source of truth.
2. **Canonical Resolution:** Designated Gmail API OAuth2 (refresh token + client credentials over TLS) as the sole canonical V1 transport credential. App Passwords are permanently removed. Authoritative ingress is decoupled from mailbox UI read/unread states: Gmail `historyId` persisted in SQLite `mail_cursors` / `mail_messages` and Cloud Pub/Sub message IDs provide the authoritative message stream. Unread mailbox state is never a source of truth and must not be a gating input.
3. **Verification Evidence:**
   - Codified in [`DECISION_BASELINE.md §3.1`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/DECISION_BASELINE.md) and [`contracts/architecture-invariants.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/contracts/architecture-invariants.json).
   - Codified in [`docs/MAIL_PROTOCOL.md §2.1, §2.4`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/MAIL_PROTOCOL.md).
   - Formally accepted in [`docs/adr/ADR-001-gmail-self-mailbox-transport.md`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/adr/ADR-001-gmail-self-mailbox-transport.md) and [`docs/adr/ADR-014-v1-transport-authentication-signing-deferred.md`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/adr/ADR-014-v1-transport-authentication-signing-deferred.md).
4. **Status:** **RESOLVED (CANONICAL)**.

### SB-FREEZE-P2-04: Materialization of `contracts/architecture-invariants.json`
1. **Context & Inconsistency:** Canonical governance files referenced `contracts/architecture-invariants.json`, but in some snapshots the file was missing or placed in an uncommitted external location.
2. **Canonical Resolution:** Materialized the physical contract file [`contracts/architecture-invariants.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/contracts/architecture-invariants.json) conforming to schema `solidbit.architecture-invariants.v1`. Validated clean JSON grammar, containing the complete set of final architecture invariants synchronized with `ARCHITECTURE_INVARIANTS_W0_3.json`.
3. **Verification Evidence:**
   - Physical file exists at [`contracts/architecture-invariants.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/contracts/architecture-invariants.json). Validated via JSON syntax parser.
   - Referenced in root [`README.md §4`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/README.md) file tree and [`DECISION_BASELINE.md §1.2`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/DECISION_BASELINE.md).
4. **Status:** **RESOLVED (CANONICAL)**.

### SB-FREEZE-P2-05: Exclusion of WEBHOOK from V1 Approval Channel Enum
1. **Context & Inconsistency:** `schemas/approval.schema.json` included `WEBHOOK` in the `channel` enum, contradicting the zero-inbound-listener and no-public-webhook network architecture for V1.
2. **Canonical Resolution:** Removed `WEBHOOK` from the `channel` enum in [`schemas/approval.schema.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/schemas/approval.schema.json). V1 approval channels are strictly constrained to: `["CLI", "GMAIL", "MANUAL"]`. Updated example instances and documentation.
3. **Verification Evidence:**
   - Schema [`schemas/approval.schema.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/schemas/approval.schema.json) lines 36–40: `"enum": ["CLI", "GMAIL", "MANUAL"]`.
   - Example instance [`examples/approval.valid.json`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/examples/approval.valid.json) validates cleanly against schema.
   - Codified in [`docs/AUTHORITY_MODEL.md §4`](file:///C:/Users/Lucilfer/Documents/solidbit-agent-execution-control-loop/docs/AUTHORITY_MODEL.md).
4. **Status:** **RESOLVED (CANONICAL)**.

---

## 7. Complete W0.1, W0.2 & W0.3 Baseline Corrections Checklist

The table below provides a complete audit of the 20 corrections and clarifications established across the Wave 0.1, Wave 0.2, and Wave 0.3 Freeze Baselines:

| Baseline # | Baseline Invariant / Mandate | Materialization & Reconciliation Status |
| :---: | :--- | :--- |
| **1** | W0 reports are DRAFT SOURCE MATERIAL. A document is not "created" until physically existing and validated. | **ENFORCED.** All 18 canonical documents, 14 ADRs, 10 schemas, 10 examples, and 2 contracts exist physically on disk. |
| **2** | `DONE_REVIEW_REQUIRED` means execution completed and requires review. It never means PASS. | **ENFORCED.** Defined in `docs/RESULT_PROTOCOL.md`, `docs/STATE_MACHINE.md`, and `schemas/result.schema.json`. |
| **3** | Run success MUST NOT depend on `$Process.ExitCode` alone. 4-factor reconciliation is mandatory. | **ENFORCED.** Codified in `docs/adr/ADR-013-run-status-reconciliation.md` and `docs/OBSERVABILITY.md`. |
| **4** | Gmail is transport, not authority. Local Mail Gateway and Policy Engine authorize. | **ENFORCED.** Codified in `docs/adr/ADR-001-gmail-self-mailbox-transport.md` and `docs/AUTHORITY_MODEL.md`. |
| **5** | ChatGPT Web MUST NOT possess a long-lived HMAC/private signing secret. | **ENFORCED.** Codified in `docs/adr/ADR-014-v1-transport-authentication-signing-deferred.md` and `docs/SECURITY_MODEL.md`. |
| **6** | HMAC package signing is NOT a V1 requirement. V1 uses defense-in-depth; signing deferred. | **ENFORCED.** Resolved per finding P1-02 in `docs/adr/ADR-014-v1-transport-authentication-signing-deferred.md`. |
| **7** | Subject line is a routing hint `[SACL][JOB][v1][<JOB_ID>]`, never an authority source. | **ENFORCED.** Resolved per finding P1-01 in `docs/MAIL_PROTOCOL.md` and `schemas/mail-envelope.schema.json`. |
| **8** | Delivery semantics are at-least-once. Consumers are idempotent. | **ENFORCED.** Codified in `docs/adr/ADR-010-at-least-once-idempotent-processing.md` and `docs/OPERATIONS.md`. |
| **9** | Same JOB_ID + same hash = ignore duplicate; same JOB_ID + different hash = reject conflict. | **ENFORCED.** Codified in `docs/MAIL_PROTOCOL.md §2.4` and `docs/RECOVERY_MODEL.md §6`. |
| **10** | Both `SUMMARY.md` and `SUMMARY.json` are required deliverables. | **ENFORCED.** Codified in `docs/adr/ADR-011-filesystem-artifacts-sqlite-metadata.md` and `schemas/summary.schema.json`. |
| **11** | Preserve legacy fallback verdict `'PASS (Report Present)'` in canonical result domain. | **ENFORCED.** Codified in `db/migrations/001_init.sql` (Line 90) and `docs/RESULT_PROTOCOL.md §2`. |
| **12** | Remote production execution remains disabled in V1. | **ENFORCED.** Codified in `docs/adr/ADR-012-no-remote-production-v1.md` and `docs/SECURITY_MODEL.md §1.1`. |
| **13** | No merge, push, deploy, Jira mutation, Railway mutation, GitHub settings mutation, or production DB mutation authorized. | **ENFORCED.** Codified in `docs/AUTHORITY_MODEL.md §2` and `schemas/policy.schema.json`. |
| **14** | Root compatibility entrypoints preserved; reusable implementation belongs under `src/` modules. | **ENFORCED.** Codified in `docs/CURRENT_ORCHESTRATOR_COMPATIBILITY_MATRIX.md §5` and `README.md §4`. |
| **15** | Separate "explicit Joaquín decisions" from "derived SACL architecture decisions". Never claim an agent-derived decision was explicitly made by Joaquín. | **ENFORCED.** Codified in `DECISION_BASELINE.md §2.1/§2.2`, `docs/TRACEABILITY_MATRIX.md §2.1/§2.2`, and `contracts/architecture-invariants.json`. |
| **16** | Replace contradictory hermetic wording. Packages carry versioned task context; runtime services (Gmail, Pub/Sub, AGY, Git, GitHub) allowed by policy. | **ENFORCED.** Codified in `DECISION_BASELINE.md §3.2`, `CURRENT_ORCHESTRATOR_COMPATIBILITY_MATRIX.md §4`, and `contracts/architecture-invariants.json`. |
| **17** | Controlled GitHub Write Semantics: direct main push hard denied; merge hard denied in V1; feature/task branch push and PR creation require local trusted operation + 4-layer lattice; W0.3 performs zero GitHub writes. | **ENFORCED.** Codified in `DECISION_BASELINE.md §3.9`, `AUTHORITY_MODEL.md §2`, `SECURITY_MODEL.md §1.1`, and `contracts/architecture-invariants.json`. |
| **18** | Gmail API OAuth2 is canonical transport credential. App Passwords removed. Unread mailbox state is never source of truth or gating input. | **ENFORCED.** Codified in `DECISION_BASELINE.md §3.1`, `MAIL_PROTOCOL.md §2.1/§2.4`, `ADR-001`, and `contracts/architecture-invariants.json`. |
| **19** | Physical target `contracts/architecture-invariants.json` exists and reflects final architecture invariants. | **ENFORCED.** Physically exists on disk, valid JSON, conforming to `solidbit.architecture-invariants.v1`. |
| **20** | Remove `WEBHOOK` from V1 approval channel enum (`CLI`, `GMAIL`, `MANUAL`). | **ENFORCED.** Codified in `schemas/approval.schema.json`, `examples/approval.valid.json`, and `docs/AUTHORITY_MODEL.md §4`. |

---

## 8. Architectural Freeze Reconciliation Verdict

The comprehensive audit and physical reconciliation of the SACL V1 codebase confirms:
- **Total Open Architectural Contradictions:** `0`
- **Total Unresolved Security-Critical Unknowns:** `0`
- **Wave 0.1 Audit Findings:** `7/7` fully resolved (`FINDING-P1-01` through `FINDING-P3-01`)
- **Wave 0.2 Freeze Consistency Findings:** `10/10` fully resolved (`SB-FREEZE-P1-01` through `SB-FREEZE-P1-08`, `SB-FREEZE-P2-01` through `SB-FREEZE-P2-02`) with verified evidence
- **Wave 0.3 Final Architecture Freeze Findings:** `6/6` fully resolved (`SB-FREEZE-P1-09` through `SB-FREEZE-P1-11`, `SB-FREEZE-P2-03` through `SB-FREEZE-P2-05`) with verified evidence
- **Architecture Freeze Status:** `NOT_YET_PASS (Awaiting Human Sovereign Review & Sign-Off)`
- **Implementation Authorization:** `IMPLEMENTATION_AUTHORIZED=NO` (Strictly maintained)
- **Next Safe Action:** `HUMAN_REVIEW_OF_RECONCILED_ARCHITECTURE`


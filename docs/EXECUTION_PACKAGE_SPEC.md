# SACL V1 Execution Package Specification (EXECUTION_PACKAGE_SPEC)

**Specification ID:** SACL-SPEC-PKG-v1  
**Status:** ARCHITECTURE FREEZE / LOCAL CANONICAL BASELINE (Wave 0.2 Consistency Remediation)  
**Authoritative Precedence:** Explicit Joaquín Decisions > Proven Current-Orchestrator Behavior > SolidBit Governance > Industry Standards  

---

## 1. Overview & Packaging Standard

An **Execution Package** is an autonomous, self-contained unit of execution distributed as a standard `.zip` archive. It encapsulates prompt templates, agent instructions, configurations, runtime templates, contracts, and contextual baseline documents required for autonomous execution by local Antigravity workers (`agy.exe`). Packages carry complete, self-contained, and versioned task context so execution does not require ad-hoc documentation or prompt discovery. Explicitly configured runtime services (Gmail API, Google Cloud Pub/Sub, Antigravity CLI, Git, and conditionally GitHub when an allowed operation requires it) are permitted by policy and are not prohibited by the self-contained package model.

The packaging model adheres to the following constitutional principles:
1. **Preserved Wave ZIP Model & Self-Contained Task Context:** In accordance with Decision Baseline §2 and findings SB-FREEZE-P1-02 and SB-FREEZE-P1-10, the wave package structure preserves the proven user experience developed in `Stable-Ecommerce-Orchestrator` (`manifest.json`, `README.md`, `EXECUTION_PLAN.md`, `prompts/`, `scripts/`, `config/`, `contracts/`, `inputs/`). Task context is self-contained and versioned on disk, avoiding unversioned internet dependencies while allowing policy-governed runtime services.
2. **Package is Declarative in Authority:** An execution package is untrusted input. It possesses zero execution authority and **cannot grant executable trust to attached code**. The package declares requested operations, parameters, and targets, but has no power to authorize script execution on the host machine.
3. **No `authorized_scripts` Authority Field:** The manifest field `authorized_scripts` is strictly removed and prohibited as an authority field. Declaring a script in package metadata does not make it trusted.
4. **Local Operation Registry Governs Handlers:** Local SACL core autoexecution only invokes locally trusted operation handlers from a **local operation registry** (`schemas/operation-registry.schema.json`). The local host installation owns and verifies all executable handlers.
5. **Preserved `scripts/` Directory for Compatibility:** The `scripts/` directory inside the package archive is preserved for backward compatibility, reference, and manual review. However, SACL core autoexecution never executes arbitrary scripts directly from untrusted packages.
6. **Effective-Permission Lattice:** Execution is governed by:
   $$\text{Effective Permissions} = \text{Hard Local Policy} \cap \text{Project Policy} \cap \text{Package Requested Permissions} \cap \text{Valid Approval Grant}$$
   Hard deny always wins. Approval cannot override hard deny.
7. **Multi-Project Parameterization:** Eliminates hardcoded repository paths; target repositories are parameterized in `manifest.json` and resolved dynamically via the local project registry.
8. **Dual Summary Contract:** Both `SUMMARY.md` (human-readable markdown) and `SUMMARY.json` (machine-readable structured schema) are strictly required outputs of every package execution. `implementation_authorized` is a boolean representing authorization status (false during freeze/design; evidence, not authority).

---

## 2. Preserved Canonical ZIP Structure

Every SACL V1 wave execution package must conform to the standard archive layout:

```text
<PACKAGE_ID>/
├── manifest.json                  # Canonical declarative package manifest (Schema v1)
├── checksums.sha256               # Cryptographic SHA-256 hashes of every distributed file
├── README.md                      # Human operator package briefing & execution guide
├── EXECUTION_PLAN.md              # Detailed sequential & phased wave execution plan
├── RUN-WAVE.ps1                   # Package execution orchestrator entrypoint (template/reference)
├── WORKER.ps1                     # Governed worker child process controller (template/reference)
├── MONITOR.ps1                    # Read-only real-time console status dashboard (template/reference)
├── FINALIZE.ps1                   # Post-execution aggregation & packaging (template/reference)
├── config/
│   ├── agents.json                # Agent definitions, prompt mappings, and execution flags
│   ├── dependencies.json          # Directed acyclic graph (DAG) dependency edges
│   ├── permissions.json           # Declarative requested permissions
│   └── stop-conditions.json       # Policy trigger stop conditions
├── contracts/
│   ├── ACCEPTANCE_CRITERIA.md     # Quality gates and required pass criteria
│   └── OUTPUT_CONTRACT.md         # Authoritative deliverable report schemas
├── inputs/
│   ├── DECISION_BASELINE.md       # Fixed human architectural decisions & precedences
│   └── ...                        # Context documents, previous wave summaries, domain models
├── prompts/
│   ├── <AGENT_ID>.md              # Individual prompt templates with variable slots
│   └── ...
├── schemas/
│   ├── manifest.schema.json       # Schema definition for manifest.json
│   ├── hard-policy.schema.json    # Schema definition for hard local policy
│   ├── policy.schema.json         # Schema definition for project policy
│   ├── operation-registry.schema.json # Schema definition for local operation registry
│   ├── graph.schema.json          # Schema definition for dependencies.json
│   ├── approval.schema.json       # Schema definition for human action gate artifacts
│   ├── result.schema.json         # Schema definition for deliverable results
│   ├── mail-envelope.schema.json  # Schema definition for transport envelopes
│   ├── summary.schema.json        # Schema definition for SUMMARY.json
│   └── project-registry.schema.json # Schema definition for multi-project repository mappings
└── scripts/
    ├── 00-preflight.ps1           # Environment and CLI validator (preserved for compatibility)
    └── ...                        # Preserved domain validation and utility scripts
```

---

## 3. Package Manifest Specification (`manifest.json`)

The package root must contain `manifest.json`, which governs execution parameters, identity, target repository, requested operations, and prohibited actions.

### 3.1 Manifest Schema Conformance
The manifest must strictly validate against [manifest.schema.json](file:////workspace/solidbit-agent-execution-control-loop/schemas/manifest.schema.json).

### 3.2 Canonical Manifest Fields

| Field | Type | Description | Mandatory |
| :--- | :--- | :--- | :---: |
| `schema` | `string` | Must be exactly `"solidbit.execution-package.v1"`. | **Yes** |
| `package_id` | `string` | Unique identifier (e.g., `SACL-W0-1-ARCHITECTURE-MATERIALIZATION-v1`). | **Yes** |
| `job_id` | `string` | Logical job ID matching transport routing hint and idempotency record. | **Yes** |
| `project` | `string` | Registered project name in local project registry. | **Yes** |
| `repository` | `string` | GitHub repository identifier (`owner/repo`). | **Yes** |
| `mode` | `string` | Execution mode enum (`architecture_freeze_and_repo_bootstrap`, `governed_documentation_generation`, `isolated_branch_development`, `integration_and_audit`, `certification_test`). | **Yes** |
| `source_orchestrator`| `string` | Source orchestrator base path for reference material. | **Yes** |
| `target_local_repo` | `string` | Target local path where worktrees or files are modified. | **Yes** |
| `agents` | `array[string]` | Distinct list of agent IDs participating in the wave. | **Yes** |
| `entrypoint` | `string` | Declarative main entrypoint reference (`RUN-WAVE.ps1`). | **Yes** |
| `execution_plan` | `string` | Human-readable execution plan file (`EXECUTION_PLAN.md`). | **Yes** |
| `readme` | `string` | Package guide file (`README.md`). | **Yes** |
| `requested_operations` | `array[string]` | **Declarative list of requested operation identifiers.** (e.g. `op:preflight-check`, `op:worker-governed-execution`). Maps strictly to trusted handlers in the local operation registry. | **Yes** |
| `prohibited_actions` | `array[string]` | Explicit list of forbidden actions (e.g. `merge`, `production_deploy`, `direct_main_push`, `production_db_mutation`, `secret_export`, `arbitrary_script_execution`). | **Yes** |
| `expected_outputs` | `array[string]` | Glob list of expected outputs (must include `SUMMARY.md`, `SUMMARY.json`, deliverable reports). | **Yes** |
| `runtime_files` | `array[string]` | List of required orchestration runtime reference files. | **Yes** |
| `checksums_file` | `string` | Name of checksum manifest (`checksums.sha256`). | No |
| `metadata` | `object` | Optional metadata (author, created_at, wave, description). | No |

---

## 4. Execution Authority & Local Operation Registry

### 4.1 Threat Model: Attached Script Vulnerability
An untrusted execution package cannot grant executable trust to its own code. If an orchestrator executes any script bundled in a ZIP archive merely because the package manifest lists it under `authorized_scripts`, an attacker or compromised LLM could achieve Arbitrary Remote Code Execution (ACE) on the host system.

### 4.2 Declarative Intent vs. Local Execution Authority
In SACL V1:
1. **Untrusted Package Boundary:** Packages are declarative input. They express intent by listing `requested_operations`.
2. **Local Operation Registry (`schemas/operation-registry.schema.json`):** The local SACL host maintains an authoritative registry of trusted operations. Each registered operation defines:
   - `operation_id`: Unique canonical identifier (e.g. `op:preflight-check`).
   - `handler_path`: Physical path to the trusted script or binary owned by the local SACL installation.
   - `handler_sha256`: Cryptographic SHA-256 hash of the trusted handler, validated before every invocation.
   - `execution_profile`: Strict resource constraints (timeout, max memory, isolation mode, allowed process images).
   - `required_permissions`: Permissions required to execute the handler.
3. **Registry Resolution Process:**
   ```
   Manifest requested_operations
                 │
                 ▼
   Lookup operation_id in Local Operation Registry
                 │
                 ├── Found & Enabled?
                 │     ├── NO  ──> FAIL CLOSED (UNKNOWN_OPERATION)
                 │     └── YES ──> Verify Handler SHA-256 matches Registry
                 │                   ├── Mismatch ──> FAIL CLOSED (HANDLER_TAMPERED)
                 │                   └── Match    ──> Check Effective Permissions Lattice
                 │                                      ├── Denied ──> FAIL CLOSED (POLICY_DENIED)
                 │                                      └── Allowed ──> Execute Handler under Execution Profile
   ```
4. **Preserved Compatibility:** The `scripts/` directory inside wave packages is preserved for backward compatibility and human audit, but SACL core autoexecution never executes attached scripts directly based on package metadata.

---

## 5. Integrity & Tamper Protection

Every package archive undergoes rigorous intake validation upon receipt by the Mail Gateway and Policy Engine:

### 5.1 Cryptographic Integrity (`checksums.sha256`)
Prior to archiving, every distributed file is hashed via SHA-256 and recorded in `checksums.sha256`. During preflight unpacking, each file is verified against its entry. Any mismatch halts processing immediately with `PACKAGE_INTEGRITY_MISMATCH`.

### 5.2 Archive Safety & Anti-Traversal (Zip Slip Defense)
Archive member paths are inspected before any bytes are written to disk:
1. Member paths containing `..` or absolute path prefixes (`/`, `\`, `C:`) are strictly prohibited.
2. The destination staging directory (`packages/inbox/<package_id>_<timestamp>/`) is fully canonicalized; any file whose resolved target path falls outside this directory causes an immediate abort with `PATH_TRAVERSAL_ATTEMPT`.
3. Uninspected executable binaries (`.exe`, `.dll`, `.cmd`, `.msi`) are prohibited from extraction.

---

## 6. Multi-Project Parameterization

SACL V1 packages eliminate hardcoded checkout paths through multi-project abstraction:
1. The package specifies `project: "solidbit-agent-execution-control-loop"` and `repository: "risejoaquin/solidbit-agent-execution-control-loop"`.
2. The orchestrator references the local [project-registry.schema.json](file:////workspace/solidbit-agent-execution-control-loop/schemas/project-registry.schema.json) to dynamically resolve local filesystem roots, default branches, and worktree directories.
3. The inviolable **Local Dirty-Root Rule** is applied dynamically: if the primary checkout of the target repository contains uncommitted human changes, execution is halted immediately (`BLOCKED_DIRTY_ROOT`) without destroying, stashing, or altering human work.

---

## 7. Extraction & Staging Lifecycle

```text
[Gmail API Notification (Pub/Sub Pull)]
                   │
                   ▼
[Mail Gateway Intake (Zero LLM)]
  ├── Validate Subject Routing Hint: [SACL][JOB][v1][<JOB_ID>]
  ├── Idempotency Check in sacl_ops.db (job_id, package_sha256)
  ├── Verify Attachment SHA-256 Integrity
  └── Check Zip Slip / Path Traversal
                   │
                   ▼
[Staged in packages/inbox/<PACKAGE_ID>_<TIMESTAMP>/]
  ├── Verify checksums.sha256
  ├── Validate manifest.json against manifest.schema.json (job_id, requested_operations required)
  └── Register Job in sacl_ops.db (status: RECEIVED -> AUTHENTICATED -> VALIDATED)
                   │
                   ▼
[Policy Engine & Operation Registry Gate]
  ├── Effective-Permission Lattice Evaluation (Hard Local Policy ∩ Project Policy)
  ├── Verify Target Repo Exists & Dirty Root Check Passes
  ├── Map requested_operations to Trusted Handlers in Local Operation Registry
  └── Verify Handler SHA-256 Digests
                   │
                   ▼
[Graph-P / Graph-H Execution]
  ├── Transition Job to QUEUED -> DISPATCHED -> RUNNING
  └── Spawn Ephemeral Graph-H with Isolated Git Worktrees
```

---

## 8. Dual Deliverable Packaging Contract

Every wave run must conclude with the generation and validation of both canonical summary formats under `runs/<runId>/`:
1. `SUMMARY.md`: Comprehensive Markdown report containing run status, agent results, file modifications, compatibility findings, and immediate next safe action. Formatted to be rendered in emails and human reviews.
2. `SUMMARY.json`: Machine-readable JSON summary conforming to [summary.schema.json](file:////workspace/solidbit-agent-execution-control-loop/schemas/summary.schema.json). Represents `implementation_authorized: false` for freeze waves. The boolean flag serves as recorded evidence of human sign-off, bounded by policy and approvals.

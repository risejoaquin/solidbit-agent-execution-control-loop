# ADR-004: Self-Contained Runnable Wave Package Compatibility Model

- **Status:** ACCEPTED
- **Date:** 2026-10-07
- **Scope:** SACL V1 Package Specification, Authority Boundaries & Runtime Conventions
- **Deciders:** Joaquín (Sovereign Principal), SACL Architecture & Protocol Leads

---

## 1. Context

In `Stable-Ecommerce-Orchestrator`, multi-agent execution tasks were successfully packaged and distributed as structured archive bundles (e.g., `SOLIDBIT_CCP46_WAVE_B_LOCAL_GOVERNANCE_v1` and `SACL_W0_ARCHITECTURE_FREEZE_RUNNABLE_v1`).

Autonomous AI coding agents operating on local codebases require complete, self-contained operational task context to execute reliably. When execution packages rely on ad-hoc internet lookups, undeclared host tools, unversioned prompts, or implicit environment variables, execution degrades rapidly due to non-deterministic behavior, version drift, and network failures.

Furthermore, packages authored in the Cloud Control Plane (ChatGPT Web) must be transferable over asynchronous transport (Gmail or direct download) as a single, easily verifiable file.

However, audit findings (specifically `SB-FREEZE-P1-02`, `SB-FREEZE-P1-10`, and `SB-FREEZE-P2-01`) identified critical security boundaries:
1. An execution package is untrusted external input and cannot grant executable trust to its own code (no self-authorizing attached scripts).
2. A package must not be able to redirect host execution to arbitrary filesystem roots outside local registry policy.
3. Remotely transported packages require a unique `job_id` for deduplication, routing, and idempotency.

Joaquín established an explicit foundational decision (DECISION_BASELINE §2, Decision #19):
- Preserve the current wave ZIP package model.
In addition, ratified architecture decisions (SB-FREEZE-P1-10) established:
- Packages carry complete, self-contained, and versioned task context (prompts, configurations, contracts, schemas). Explicitly configured runtime services (Gmail API, Google Cloud Pub/Sub, Antigravity CLI, Git, and conditionally GitHub when policy allows) are permitted by policy and are not prohibited by the self-contained package model.

---

## 2. Decision

We decide to preserve and standardize the **Self-Contained Runnable Wave Package Model** as the canonical unit of distribution and execution in SACL V1, while establishing strict declarative authority and local host enforcement boundaries:

1. **Canonical ZIP Archive Structure:**
   Every execution package distributed to SACL V1 must arrive as a standardized `.zip` archive containing the following directory and file layout:
   ```
   <PACKAGE_ID>/
   ├── manifest.json                  # Authoritative execution manifest (solidbit.execution-package.v1)
   ├── checksums.sha256               # Cryptographic SHA-256 hashes of every file in the package
   ├── README.md                      # Operator brief and manual execution instructions
   ├── RUN-WAVE.ps1                   # Package execution orchestrator entrypoint (Graph-H runner)
   ├── WORKER.ps1                     # Governed agent worker process controller
   ├── MONITOR.ps1                    # Real-time console status dashboard
   ├── FINALIZE.ps1                   # Post-execution aggregation & artifact packaging
   ├── config/
   │   ├── agents.json                # Agent definitions, prompt mappings, flags
   │   ├── dependencies.json          # Directed acyclic graph (DAG) stages and execution edges
   │   ├── permissions.json           # Declarative requested permissions
   │   └── stop-conditions.json       # Policy trigger stop conditions
   ├── contracts/
   │   ├── ACCEPTANCE_CRITERIA.md     # Pass criteria and quality gates
   │   └── OUTPUT_CONTRACT.md         # Authoritative deliverable report schemas and required keys
   ├── inputs/
   │   ├── DECISION_BASELINE.md       # Inviolable human architectural decisions
   │   └── ...                        # Context reports, previous wave summaries, domain data
   ├── prompts/
   │   └── <AGENT_ID>.md              # Individual prompt templates with variable placeholders
   ├── schemas/
   │   └── manifest.schema.json       # JSON Schema definitions for package validation
   └── scripts/
       ├── 00-preflight.ps1           # Declarative task validation scripts (retained for compatibility)
       └── ...                        # Domain-specific validation scripts
   ```

2. **Declarative Package Authority & Local Operation Registry:**
   - Packages are strictly **declarative** in authority (`declarative = true`).
   - **No Self-Authorizing Scripts:** Attached scripts within `scripts/` (e.g. `.ps1`, `.bat`, `.cmd`, `.exe`) **never** become trusted merely because they are declared in package metadata (`package_may_self_authorize_scripts = false`).
   - Packages request stable operation IDs (`requested_operations`).
   - The local SACL host installation owns the trusted operation/handler registry (`config/operation-registry.json`). Effective execution is strictly limited to locally installed handlers whose identity, hash, and profile are trusted by local host policy.

3. **Project Registry Root Authority:**
   - A package identifies a registered project (`project`) and may request a target local repository path (`target_local_repo`).
   - **Non-Redirection Invariant:** A package **must not be able to redirect execution to an arbitrary path** outside local registry policy.
   - The local host Project Registry (`config/projects.json`) is the sole local authority for local filesystem roots. If a requested path is unauthorized or outside registry policy, execution is refused fail-closed.

4. **Mandatory Job Identifier (`job_id`):**
   - For all remotely transported execution packages, `job_id` is a strictly required field in `manifest.json`.
   - `job_id` binds the package to transport message envelopes, SQLite run records, and bounded approval grants.

5. **Self-Contained Task Context & Runtime Services Boundary:**
   A wave package carries complete, self-contained, and versioned task context. Once unpacked, local execution must not require:
   - Ad-hoc cloud documentation searches or live browsing for missing instructions.
   - Ad-hoc prompt downloads or unversioned runtime dependencies.
   - Modifications to host system files outside the target project worktrees and run artifact directories.
   Explicitly configured runtime services (Gmail API, Google Cloud Pub/Sub, Antigravity CLI, Git, and conditionally GitHub when policy and approval allow) are authorized runtime boundaries and not prohibited by the self-contained package model.

6. **Canonical Run Output Directory Hierarchy:**
   Execution generates structured outputs under `artifacts/runs/<runId>/`:
   - `evidence/`: Verification logs, git diffs, test outputs, human gate artifacts.
   - `logs/`: Full stdout/stderr streams per agent.
   - `reports/`: Completed agent deliverable markdown reports.
   - `state/`: Local run status checkpoints.
   - `SUMMARY.md` and `SUMMARY.json`: Dual root summary deliverables.

---

## 3. Consequences

### Positive
- **100% Reproducibility:** Every run is fully reproducible and self-auditing because all prompts, configurations, and verification contracts are encapsulated within the package.
- **Security Isolation:** Host execution cannot be hijacked by untrusted scripts embedded in incoming ZIP archives.
- **Portability:** Packages can be transported via Gmail, local drop, or manual copy without altering execution behavior.
- **Dual Deliverables:** Generates both human-readable (`SUMMARY.md`) and machine-readable (`SUMMARY.json`) artifacts.

### Negative / Trade-Offs
- **Package Size:** Encapsulating complete documentation and contracts increases ZIP size (typically 1–10 MB).
- **Operation Registration:** New custom operations require registering trusted handlers locally rather than dropping executable code directly into a package.

---

## 4. Compatibility Notes

- **Legacy Orchestrator Mapping:**
  - Preserves backwards compatibility with wave packages from `Stable-Ecommerce-Orchestrator` (`SOLIDBIT_CCP46_WAVE_B_LOCAL_GOVERNANCE_v1`, `SACL_W0_ARCHITECTURE_FREEZE_RUNNABLE_v1`).
  - Retains `scripts/` directory for backwards-compatible manual operator inspection.
- **Precedence Compliance:**
  - Directly enforces DECISION_BASELINE items 19 and 20.
  - Reconciles audit findings `SB-FREEZE-P1-02` and `SB-FREEZE-P2-01`.
  - Codified in `docs/EXECUTION_PACKAGE_SPEC.md` and `schemas/manifest.schema.json`.

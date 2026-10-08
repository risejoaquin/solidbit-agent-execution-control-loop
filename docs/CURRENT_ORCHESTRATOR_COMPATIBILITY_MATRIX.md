# SolidBit Agent Execution Control Loop (SACL V1) Current Orchestrator Compatibility Matrix

> **Specification Version:** 1.0.0  
> **Source Orchestrator:** `C:\Users\Lucilfer\Documents\Stable-Ecommerce-Orchestrator`  
> **Target System:** `C:\Users\Lucilfer\Documents\solidbit-agent-execution-control-loop`  
> **Status:** ARCHITECTURE FREEZE / LOCAL CANONICAL BASELINE  
> **Implementation Authorization:** `IMPLEMENTATION_AUTHORIZED=NO`  
> **Authoritative Precedence:** Explicit Joaquín Decisions > Proven Current-Orchestrator Behavior > SolidBit Governance > Industry Standards (Undefined Gaps Only)  

---

## 1. Executive Summary & Operational Lifecycle Transition Policy

This document provides the authoritative inventory and migration mapping of all runtime capabilities, scripts, and governance contracts evaluated in `Stable-Ecommerce-Orchestrator`. In accordance with explicit decision #11 (*"Reuse/refactor current orchestrator; do not start from zero"*), SACL V1 systematically builds upon proven production code while modernizing fragile mechanisms and formally resolving architectural contradictions.

### Operational Lifecycle Transition Policy
The operational coexistence and eventual decommissioning of the legacy orchestrator are governed by strict transition rules:
1. **Untouched / Fully Operational Phase:**  
   The legacy `Stable-Ecommerce-Orchestrator` (`C:\Users\Lucilfer\Documents\Stable-Ecommerce-Orchestrator`) **remains untouched, fully operational, and available as the proven fallback runtime** throughout the construction and verification of SACL V1.
2. **Parity & E2E Certification Gate:**  
   SACL V1 must demonstrate complete functional parity across all 18 evaluated components and successfully pass the complete 8-step End-to-End Certification Suite (`docs/E2E_CERTIFICATION_PLAN.md`).
3. **Archive & Read-Only Transition:**  
   Only after explicit human sign-off confirming SACL parity and successful E2E certification does `Stable-Ecommerce-Orchestrator` transition to an **archived, read-only reference repository**.

### Summary Metrics
- **Evaluated Capabilities:** 18 distinct architectural and runtime components.
- **Direct Reuse (5 components):** Local dirty-root invariant, regex result marker protocol, cross-agent file overlap detector, prompt machine governance header injection, and self-contained wave ZIP layout.
- **Refactor & Adapt (9 components):** Git worktree lifecycle, preflight validation, CLI worker controller, staged DAG scheduler with hierarchical locks, state reconciliation model, non-killing timeout handler, supervisor instance leasing, live console monitor, and E2E sandboxed test harness.
- **Replace / Modernize (4 components):** Manual copy-paste transport replaced by automated Gmail API `users.watch` + Pub/Sub event gateway; loose JSON/text state files replaced by ACID SQLite Operational State Store (`sacl_ops.db`) across 16 domains; hardcoded single-repo paths replaced by multi-project registry with root authority; and live remote production mutations replaced by fail-closed gated staging.
- **Identified Contradictions:** 4 distinct operational contradictions resolved through Architecture Decision Records (ADRs 001, 002, 008, 009, 012).

---

## 2. Complete Compatibility & Migration Matrix

| # | Existing Capability | Current Script / File | Observed Behavior | SACL Destination | Classification | Compatibility Risk | Evidence & Source Code Citation |
| :-: | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **1** | **Git Worktree Isolation & Lifecycle** | `scripts/prepare-worktrees.ps1`<br>`governance/Test-WorktreeGovernance.ps1` | Provisions isolated worktrees per agent using `git worktree add -b <branch> <path> origin/<branch>`. Enforces that `main` is never an implementation branch and primary checkout is never used for agent work. Validates clean git status (`status --porcelain`). Refuses to overwrite unregistered folders. | Git Workspace Manager (`Graph-H` runtime) | **REFACTOR** | Medium | `prepare-worktrees.ps1#L32-L265`<br>`Invoke-AntigravityGoverned.ps1#L40-L47` |
| **2** | **Local Dirty-Root Safety Rule** | `scripts/prepare-worktrees.ps1`<br>`governance/ANTIGRAVITY_GOVERNANCE.md` | Primary product checkout may contain uncommitted human changes. Automation never runs `git reset --hard`, `git clean -fd`, or automatic `git stash`. If working tree is dirty, worktree provisioning halts and prevents destructive modifications. | Git Workspace Manager & Policy Engine | **REUSE (INVIOLABLE)** | Low | `prepare-worktrees.ps1#L72-L82`<br>`ANTIGRAVITY_GOVERNANCE.md#L23-L26` |
| **3** | **Preflight Environment & CLI Verification** | `scripts/00-preflight.ps1`<br>`scripts/01-preflight.ps1` | Verifies installed CLIs (`git`, `gh`, `powershell.exe`, `agy.exe`). Checks path alignment between orchestrator root and package root. Validates that worktrees exist, match branches, and have expected remotes. | Policy & Validation Engine (`Graph-P` / Gateway) | **REFACTOR** | Low | `scripts/00-preflight.ps1#L14-L35` |
| **4** | **Agent CLI Invocation & Process Spawning** | `scripts/start-agents.ps1`<br>`scripts/agent-worker.ps1`<br>`WORKER.ps1` | Resolves `agy.exe` path. Spawns `agy` using `--mode` (`accept-edits`/`plan`), `--effort high`, `--dangerously-skip-permissions`, redirecting stdout/stderr streams. Requires explicit caller acknowledgement (`-BypassAcknowledged`). Streams logs in background via ThreadPool async workers. Captures PID and start time. | Agent Worker Controller (`WORKER.ps1` / `Graph-H`) | **REFACTOR** | Low | `start-agents.ps1#L226-L289`<br>`WORKER.ps1#L30-L56`<br>`agent-worker.ps1#L50-L56` |
| **5** | **Prompt Injection & Machine Governance Guard** | `governance/Invoke-AntigravityGoverned.ps1`<br>`WORKER.ps1` | Dynamically prepends strict guard statements to agent prompts before passing to `agy`: `GOVERNED_EXECUTION=TRUE`, `MERGE=NOT_AUTHORIZED`, `DEPLOY=NOT_AUTHORIZED`, `DESTRUCTIVE_DB=NOT_AUTHORIZED`, `WORKTREE=<path>`, `BRANCH=<branch>`, `HEAD=<sha>`. Substitutes template placeholders. | Prompt Assembler & Policy Filter (`Graph-H`) | **REUSE (INVIOLABLE)** | Low | `Invoke-AntigravityGoverned.ps1#L49-L63`<br>`WORKER.ps1#L35-L42` |
| **6** | **Staged Pipeline & Concurrency Throttling** | `RUN-WAVE3.ps1`<br>`RUN-WAVE.ps1`<br>`config/dependencies.json` | Executes agents in ordered phases (Phase 1 -> Phase 2 -> Phase 3). Throttles concurrency using `$MaxParallel` worker pool loop (`Wait-Batch`). Dependent stages execute only if prior stages pass validation verdicts. Enforces baseline of 1 mutating job per project with hierarchical locks. | DAG Scheduler (`Graph-H` Ephemeral Engine) | **REFACTOR** | Low | `RUN-WAVE.ps1#L54-L78`<br>`RUN-WAVE3.ps1#L62-L73`<br>`dependencies.json#L1-L32` |
| **7** | **Operational State Tracking & PID Reconciliation** | `scripts/orchestrator-common.ps1` (`Get-ReconciledAgentState`, `Test-AgentProcessRunning`) | Tracks agent status (`RUNNING`, `COMPLETE`, `FAILED`, `STOPPED`), PID, timestamps (`startedAt`, `finishedAt`), exit codes, commit SHA, and deliverable report paths. Verifies process name and checks process `StartTime` against `startedAt` (within 300s) to prevent false positives from PID recycling. | Operational State Store (SQLite `sacl_ops.db` across 16 domains) | **REFACTOR / REPLACE** | Medium | `orchestrator-common.ps1#L159-L205`<br>`orchestrator-common.ps1#L333-L509`<br>`DECISION_BASELINE.md #22` |
| **8** | **Deliverable Report & Result Extraction Protocol** | `scripts/orchestrator-common.ps1` (`Extract-AgentResult`)<br>`scripts/agent-worker.ps1` | Inspects deliverable markdown report in worktree looking for regex markers: `^(?:AGENT_[A-Z0-9_-]+_RESULT\|RESULT\|FINAL_RESULT)\s*=\s*(PASS\|PARTIAL\|BLOCKED)` and `(?m)^WAVE3_RESULT=PASS\s*$`. Falls back to parsing tail 150 lines of stdout/stderr logs. Preserves `'PASS (Report Present)'` fallback. | Result Extractor & Verifier (`Graph-H`) | **REUSE (INVIOLABLE)** | Low | `orchestrator-common.ps1#L253-L331`<br>`agent-worker.ps1#L58-L63` |
| **9** | **Cross-Agent Overlap & Collision Detection** | `scripts/collect-results.ps1` | Queries `git diff --name-only origin/main...HEAD` across all agent worktrees. Maps `file -> list_of_agents`. Emits alert on overlapping files: `Overlapping file modification on '<file>' by: ...`. Evaluates `READY_FOR_INTEGRATION=NO` if overlaps, uncommitted changes, or missing reports exist. | Pre-Merge Conflict Evaluator (`Graph-H`) | **REUSE (INVIOLABLE)** | Low | `collect-results.ps1#L98-L155`<br>`collect-results.ps1#L199-L206` |
| **10** | **Safe Stop & Non-Killing Timeout Invariant** | `scripts/stop-agents.ps1`<br>`RUN-WAVE3.ps1` | `stop-agents.ps1` verifies PID and process name before sending `Stop-Process -Force`. Crucially, `RUN-WAVE3.ps1` enforces non-killing timeouts: when an agent exceeds `WaitMinutes`, the process is NOT killed automatically; it is left alive for human inspection and marked `TIMEOUT_RUNNING`. | Local Kill Switch & Timeout Supervisor (`Graph-P` / `Graph-H`) | **REUSE (INVIOLABLE)** | Low | `stop-agents.ps1#L76-L115`<br>`RUN-WAVE3.ps1#L65`<br>`RUN-AUTO.ps1#L62` |
| **11** | **Supervisor Singleton & Duplicate Run Guard** | `scripts/run-supervisor.ps1` | Queries running processes via WMI (`Get-CimInstance Win32_Process`) matching `agy.exe` and supervisor command line. Refuses to start if a supervisor is already active. Archives existing report files with timestamps before starting new runs. | Supervisor Instance Lease (`leases` in SQLite) | **REFACTOR** | Low | `run-supervisor.ps1#L94-L119` |
| **12** | **Live Console Progress Monitoring** | `scripts/MONITOR.ps1`<br>`scripts/monitor-orchestrator.ps1` | Spawns a dedicated read-only PowerShell terminal. Loops every 10 seconds, clearing host and rendering formatted table: Agent, Status, PID, Report presence, Stage, and recent log activity. Safe termination via Ctrl+C without affecting running worker processes. | Live Console Monitor (`scripts/MONITOR.ps1` mode=ro) | **REFACTOR** | Low | `scripts/MONITOR.ps1#L14-L38`<br>`monitor-orchestrator.ps1#L52-L258` |
| **13** | **Human Action Gate & Development Authorization** | `scripts/run-human-action-gate.ps1`<br>`results/FINAL_DEVELOPMENT_AUTHORIZATION.txt` | Explicit gate script that halts execution before any irreversible change (merges, deployments, ruleset mutations, Jira final transitions). Emits structured text artifact: `FUNCTIONAL_DEVELOPMENT = NOT_AUTHORIZABLE`, `REMAINING_BLOCKERS = ...`, `NEXT_SAFE_ACTION = ...`. Agents cannot self-authorize. | Human Authority Gate (`docs/AUTHORITY_MODEL.md`) | **REUSE (INVIOLABLE)** | Low | `run-human-action-gate.ps1#L55-L82`<br>`FINAL_DEVELOPMENT_AUTHORIZATION.txt#L1-L27` |
| **14** | **Self-Contained Runnable Wave Package Model** | `SOLIDBIT_CCP46_WAVE_B_LOCAL_GOVERNANCE_v1`<br>`manifest.json` | Wave packages distributed as self-contained ZIPs containing `prompts/`, `scripts/`, `config/`, `inputs/`, `contracts/`, `manifest.json`. Execution packages are declarative; attached scripts never self-authorize; handlers are owned locally. Project Registry is local authority for filesystem roots. | Execution Package Spec (`docs/EXECUTION_PACKAGE_SPEC.md`) | **REUSE & HARDEN** | Low | `manifest.json#L1-L38`<br>`DECISION_BASELINE.md #19, #20` |
| **15** | **E2E Harmless Test Certification Suite** | `scripts/test-orchestrator-e2e.ps1` | Comprehensive 8-step harmless test suite: (1) syntax verification; (2) directory structure check; (3) temporary sandbox creation in `$env:TEMP` (bare git remote, seed commit, clone); (4) worktree creation in sandbox; (5) harmless process launch (`-TestMode` mock worker) and state serialization check; (6) status check; (7) stop verification; (8) deliverable collection and mock summary generation. | E2E Certification Suite (`docs/E2E_CERTIFICATION_PLAN.md`) | **REFACTOR** | Low | `test-orchestrator-e2e.ps1#L1-L194` |
| **16** | **Engineering Findings & Risk Taxonomy** | `scripts/generate_af_report.py` | Rigorous 4-tier risk classification: `SAFE_NOW` (zero runtime risk, local docs/hygiene); `SAFE_IN_ISOLATED_BRANCH` (build/test validation in branch); `POST_GATE` (functional/security change held behind governance gate); `REQUIRES_DECISION` (architectural change requiring human ADR). | Policy Engine & Architecture Governance | **REUSE** | Low | `generate_af_report.py#L8-L80` |
| **17** | **Cloud / Local Mail Transport** | *None* (Legacy used manual ZIP download from ChatGPT Web, manual extraction, manual script run, manual copy-paste of summaries back to chat) | Legacy relied entirely on manual human copy-paste and file movement between ChatGPT Web and local Windows filesystem. | Mail Gateway Daemon (`uniquedraken@gmail.com` via Gmail API & Pub/Sub) | **REPLACE / NEW** | High | `README.md#L12-L21`<br>`DECISION_BASELINE.md #12, #13, #14` |
| **18** | **Remote Production & Infrastructure Mutation** | `FIX-SOLIDBIT-GITHUB-GOVERNANCE.ps1`<br>`FIX-SOLIDBIT-JIRA-GRAPH.ps1`<br>`FIX-SOLIDBIT-CCP19.ps1`<br>`RUN-WAVE3.ps1` | Legacy scripts executed live mutating commands against external systems (modifying GitHub rulesets via `gh api`, updating Jira links via `acli`, disabling Railway production `autoDeploy`). Hardcoded repo `risejoaquin/stable-ecomerce` and ticket IDs. | Gated Local Staging & Multi-Project Engine (**Remote Production Disabled in V1**) | **REPLACE (CONTRADICTION)** | Critical | `FIX-SOLIDBIT-GITHUB-GOVERNANCE.ps1#L29-L60`<br>`FIX-SOLIDBIT-JIRA-GRAPH.ps1#L43-L60`<br>`DECISION_BASELINE.md #25` |

---

## 3. Detailed Contradiction Analysis & Formal Resolution

The audit identified **4 significant contradictions** where current script behaviors conflict with explicit user decisions or SACL V1 constitutional requirements:

### Contradiction 1: Remote Production & Cloud Infrastructure Mutation
- **Current Behavior:** Scripts such as `FIX-SOLIDBIT-GITHUB-GOVERNANCE.ps1`, `FIX-SOLIDBIT-JIRA-GRAPH.ps1`, and `RUN-WAVE3.ps1` directly execute live mutating commands against external production systems (mutating GitHub rulesets via `gh api`, updating Jira links via `acli`, modifying Railway production service `autoDeploy`).
- **SACL Decision Baseline (#25):** *"Remote production execution disabled in V1."*
- **Conflict Assessment:** **DIRECT CONTRADICTION**. Allowing agents or automated scripts to execute mutating operations against production cloud environments presents severe risk of outage, security breach, or unintended state loss.
- **Architectural Resolution (ADR-012):** In SACL V1, remote production execution is **strictly disabled and fail-closed**. All actions targeting Railway, GitHub repository rulesets, production databases, or Jira live transitions fail closed. Instead, the engine generates offline dry-run plans (`.plan.json` / `.plan.md`) and gated human authorization requests (`FINAL_DEVELOPMENT_AUTHORIZATION.txt`) for manual human execution.

### Contradiction 2: State Persistence Storage (Loose JSON vs SQLite)
- **Current Behavior:** The legacy orchestrator stores operational state, PIDs, and run metadata across loose JSON and text files (`state/<agent>.json`, `results/<runId>/RUN_STATE.json`, `RUN_STATUS.json`, `LATEST_RUN.txt`), updating them via atomic file replacement (`.tmp` -> `.json`).
- **SACL Decision Baseline (#22):** *"SQLite = local Operational State Store."*
- **Conflict Assessment:** **STRUCTURAL CONTRADICTION / MODERNIZATION**. While atomic file replacement provided basic single-process safety, loose files lack transactional multi-agent locking, structured querying, and crash recovery guarantees across multiple daemons.
- **Architectural Resolution (ADR-002):** Operational state tracking is migrated to a local SQLite database (`sacl_ops.db`) operating with Write-Ahead Logging (`PRAGMA journal_mode=WAL;`) across 16 formal domains. Every proven state field from `orchestrator-common.ps1` and PID recycling checks are preserved. Heavy unstructured artifacts (logs, diffs, reports) remain strictly on the filesystem per Decision #23.

### Contradiction 3: Hardcoded Single-Project Topology vs Multi-Project Requirement
- **Current Behavior:** Scripts hardcode product paths (`C:\Users\Lucilfer\Documents\Stable-Ecommerce`), remote origin regexes (`risejoaquin/stable-ecomerce`), specific branch names (`audit/ccp-40-*`), specific Jira keys (`CCP-*`), and specific PR numbers.
- **SACL Target Scope:** Multi-project orchestration supporting multiple repositories (e.g. `Stable-Ecommerce`, `SolidPos`, `risejoaquin/solidbit-agent-execution-control-loop`).
- **Conflict Assessment:** **OPERATIONAL CONTRADICTION**. Attempting to run current scripts against any project other than `Stable-Ecommerce` results in immediate script abortion.
- **Architectural Resolution (ADR-009):** All repository paths and target configurations are parameterized within `manifest.json` and governed by the local Project Registry (`schemas/project-registry.schema.json`). The Project Registry is the sole local authority for local filesystem roots; packages cannot redirect execution outside registry policy. Concurrency is throttled to 1 mutating job per project.

### Contradiction 4: Manual Transport vs Automated Event-Driven Gmail Ingestion
- **Current Behavior:** The user manually downloads ZIP archives from ChatGPT Web, extracts them into the orchestrator folder, runs launcher scripts manually, and copies `SUMMARY.md` and report markdown files back into ChatGPT Web.
- **SACL Decision Baseline (#12, #13, #14):** *"ChatGPT Web = control plane; Gmail = cloud/local transport; self-mail is allowed; Planned mailbox: uniquedraken@gmail.com."*
- **Conflict Assessment:** **TRANSPORT WORKFLOW CONTRADICTION**. The manual transport boundary creates human toil, is prone to extraction errors, and bottlenecks execution.
- **Architectural Resolution (ADR-001, ADR-008 & ARCHITECTURE_INVARIANTS):** Automated transport is established via a dedicated local Mail Gateway daemon. Primary ingress is Gmail API `users.watch` coupled with Google Cloud Pub/Sub pull notifications (`gmail_api_users_watch_pubsub_pull`). Local process receives notifications as wake signals and queries the Gmail History API with persisted cursor `historyId`. Direct polling exists only as degraded-mode fallback. Gmail serves strictly as transport, while local policy authorizes execution.

---

## 4. Inviolable Legacy Invariants Preserved

SACL V1 explicitly codifies and preserves eight fundamental invariants proven in `Stable-Ecommerce-Orchestrator`:

1. **Local Dirty-Root Rule:** The primary product checkout (`.git` common dir) may legitimately contain uncommitted human changes. Automation never runs `git reset --hard`, `git clean -fd`, `git checkout .`, or automatic `git stash`. If the primary checkout is dirty, worktree provisioning halts and prevents destructive modifications.
2. **Worktree Confinement & Branch Inviolability:** Agents operate strictly inside isolated worktrees (`git worktree add -b <branch> <path> origin/<branch>`). Working on `main` (`MAIN_BRANCH_NOT_ALLOWED`) or inside the primary checkout (`PRIMARY_CHECKOUT_NOT_ALLOWED`) is strictly forbidden.
3. **Non-Killing Diagnostic Timeouts:** When an agent exceeds its execution timeout, the supervisor marks it as `TIMEOUT_RUNNING` and raises an alert. The process is **never killed automatically**, preserving transient context, logs, and partial deliverables for human diagnosis.
4. **3-Way PID Recycling Defense:** Before any process operation or status evaluation, the supervisor verifies: (1) process is active in OS; (2) process executable name matches an allowed whitelist (`agy`, `powershell`, `pwsh`, `cmd`, `node`, `conhost`); and (3) `StartTime` matches the database record within a 300-second window.
5. **Canonical Result Protocol:** Agent verdicts are evaluated against explicit structured regex markers (`^(?:AGENT_[A-Z0-9_-]+_RESULT|RESULT|FINAL_RESULT)\s*=\s*(PASS|PARTIAL|BLOCKED)`). Fallback evaluation strictly preserves `'PASS (Report Present)'`.
6. **Pre-Merge Collision Detection:** Cross-agent file diffs (`git diff --name-only origin/main...HEAD`) are compared across worktrees. Concurrent modifications to the same file block integration (`READY_FOR_INTEGRATION=NO`).
7. **Human Authority Gate & Controlled GitHub Writes:** Autonomous agents have zero authority to merge branches into `main`, deploy code, mutate GitHub rulesets, or transition production issues. Direct main/master/release push is hard denied; merge is hard denied in V1. Feature/task branch push and PR creation can occur only through locally trusted operations when project policy, package request, and valid bounded human approval all allow it; W0.3 itself performs no GitHub write. Irreversible actions require explicit human sign-off via `FINAL_DEVELOPMENT_AUTHORIZATION.txt`.
8. **Wave Package ZIP Structure:** Self-contained ZIP packages containing `prompts/`, `scripts/`, `config/`, `inputs/`, `contracts/`, and `manifest.json` are preserved verbatim. Packages carry complete and versioned task context on disk; explicitly configured runtime services (Gmail API, Pub/Sub, Antigravity CLI, Git, and conditionally GitHub) are permitted by policy.

---

## 5. Directory & File Migration Map

The table below maps existing scripts and paths in `Stable-Ecommerce-Orchestrator` to their architectural destinations in `solidbit-agent-execution-control-loop`:

| Source Path (`Stable-Ecommerce-Orchestrator`) | Target Architectural Destination (`solidbit-agent-execution-control-loop`) | Planned Subsystem / Status |
| :--- | :--- | :--- |
| `governance/ANTIGRAVITY_GOVERNANCE.md` | `docs/ARCHITECTURE.md`<br>`docs/CONCURRENCY_AND_LOCKING.md` | **Materialized** (Invariants codified) |
| `governance/Invoke-AntigravityGoverned.ps1` | `src/executor/WorkerController.ps1` | Future Wave (Refactor) |
| `governance/Test-WorktreeGovernance.ps1` | `tests/governance/Test-WorktreeGovernance.ps1` | Future Wave (Refactor) |
| `scripts/prepare-worktrees.ps1`<br>`scripts/01-prepare-worktrees.ps1` | `src/workspace/GitWorkspaceManager.ps1` | Future Wave (Refactor) |
| `scripts/00-preflight.ps1`<br>`scripts/01-preflight.ps1` | `src/validator/PreflightValidator.ps1` | Future Wave (Refactor) |
| `scripts/start-agents.ps1`<br>`scripts/agent-worker.ps1`<br>`WORKER.ps1` | `src/executor/WorkerController.ps1`<br>`WORKER.ps1` (Compatibility Entrypoint) | Future Wave (Refactor) |
| `RUN-WAVE3.ps1`<br>`RUN-WAVE.ps1` | `src/scheduler/GraphHDagEngine.ps1`<br>`RUN-WAVE.ps1` (Compatibility Entrypoint) | Future Wave (Refactor) |
| `scripts/orchestrator-common.ps1` | `src/state/OperationalStateStore.ps1`<br>`src/validator/ResultExtractor.ps1` | Future Wave (Refactor / Replace) |
| `scripts/collect-results.ps1` | `src/validator/CollisionDetector.ps1` | Future Wave (Refactor) |
| `scripts/stop-agents.ps1` | `src/supervisor/KillSwitch.ps1`<br>`scripts/STOP.ps1` (Compatibility Entrypoint) | Future Wave (Refactor) |
| `scripts/run-supervisor.ps1` | `src/supervisor/GraphPSupervisor.ps1` | Future Wave (Refactor / Replace) |
| `scripts/MONITOR.ps1`<br>`scripts/monitor-orchestrator.ps1` | `scripts/MONITOR.ps1` | Future Wave (Refactor) |
| `scripts/run-human-action-gate.ps1` | `src/validator/HumanActionGate.ps1` | Future Wave (Reuse) |
| `scripts/test-orchestrator-e2e.ps1` | `tests/e2e/Test-OrchestratorE2E.ps1` | Future Wave (Refactor) |
| `state/*.json` | `data/sacl_ops.db` (16 relational tables) | **Architecture Defined** (WAL mode) |
| `results/` & `logs/` | `artifacts/runs/<runId>/` (`logs/`, `reports/`, `evidence/`) | **Architecture Defined** (Dual Summaries) |
| *Manual Copy-Paste Transport* | `src/gateway/MailGatewayDaemon.ps1` | Future Wave (New Subsystem via Pub/Sub) |
| `FIX-SOLIDBIT-*.ps1` (Production Mutations) | *Disabled / Prohibited in V1* (Dry-run plans only) | **Architecture Defined** (Fail-Closed) |

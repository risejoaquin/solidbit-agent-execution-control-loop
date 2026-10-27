# ADR-009: Multi-Project Parameterization via Manifest vs Hardcoded Single-Repo Paths

- **Status:** ACCEPTED
- **Date:** 2026-10-07
- **Scope:** SACL V1 Workspace Manager, Project Registry Authority & Concurrency
- **Deciders:** Joaquín (Sovereign Principal), SACL Architecture & Workspace Leads

---

## 1. Context

In `Stable-Ecommerce-Orchestrator`, the orchestration scripts were tightly coupled to a single specific product repository:
- Hardcoded local paths: `/workspace\Stable-Ecommerce`.
- Hardcoded git remote URLs and regex validations: `risejoaquin/stable-ecomerce`.
- Hardcoded feature branches: `audit/ccp-40-*`.
- Hardcoded pull request numbers: `#11`, `#12`, `#13`, `#14`, `#15`, `#20`, `#21`, `#23`.
- Hardcoded Jira issue keys: `CCP-*`.

As a consequence of this hardcoded topology:
1. **Zero Portability:** Attempting to execute the orchestrator against any other repository (such as `SolidPos` or `solidbit-agent-execution-control-loop` itself) resulted in immediate assertion failure in `Assert-Repo` due to remote URL and directory mismatches.
2. **Code Duplication:** Supporting a new product or repository required copy-pasting and editing the entire orchestrator codebase.
3. **Fragile Workspace Management:** Worktree provisioning logic assumed a fixed layout under `..\Stable-Ecommerce`, preventing execution on alternate disk drives or differing directory trees.

The target repository for SACL V1 is `risejoaquin/solidbit-agent-execution-control-loop`, designed to serve as the unified, multi-project execution engine for all SolidBit development activities.

Joaquín established explicit foundational decisions (DECISION_BASELINE item 10 and item 11):
- Target repository is `risejoaquin/solidbit-agent-execution-control-loop`.
- Reuse and refactor the current orchestrator; do not start from zero.

---

## 2. Decision

We decide to **eliminate all hardcoded repository paths, branch names, and remote URL regexes from core orchestrator scripts**, replacing them with **dynamic multi-project parameterization driven by the Local Project Registry**:

1. **Project Registry as Local Authority for Filesystem Roots:**
   - The local host maintains an authoritative Project Registry (`config/projects.json`, conforming to `schemas/project-registry.schema.json`).
   - **Sole Local Authority:** The Project Registry is the **sole local authority** for defining local filesystem roots, allowed target roots, repository bindings, and project security tiers.
   - **Non-Redirection Invariant:** A package identifies a registered project (`project`) and may request a target path (`target_local_repo`), but **must not be able to redirect execution to an arbitrary path** outside local registry policy.
   - If a package requests a path that does not match the registered `target_local_repo` (or is not within `allowed_target_roots` when override is enabled), the Policy Engine rejects the job fail-closed (`POLICY_DENIED_UNAUTHORIZED_TARGET_ROOT`).

2. **Project Registry Structure:**
   ```json
   {
     "schema": "solidbit.project-registry.v1",
     "version": "1.0.0",
     "projects": [
       {
         "project_id": "solidbit-agent-execution-control-loop",
         "repository": "risejoaquin/solidbit-agent-execution-control-loop",
         "target_local_repo": "/workspace/solidbit-agent-execution-control-loop",
         "default_branch": "main",
         "allowed_worktree_base": "worktrees",
         "allowed_target_roots": [
           "/workspace/solidbit-agent-execution-control-loop"
         ],
         "allow_target_override": false,
         "concurrency_policy": {
           "max_mutating_jobs": 1,
           "allow_concurrent_read_only": true
         },
         "risk_tier": "SAFE_IN_ISOLATED_BRANCH",
         "enforce_dirty_root_check": true,
         "active": true
       }
     ]
   }
   ```

3. **Project Concurrency Baseline & Hierarchical Locks:**
   - **Concurrency Baseline:** Initially, exactly **one mutating job per project** is permitted to execute at any time.
   - **Read-Only Coexistence:** Safe read-only work (monitoring, audit inspection, static preflights) may coexist concurrently with an active mutating job.
   - **Hierarchical Lock Ladder:** Mutual exclusion is enforced via hierarchical locks:
     - `system`: Global supervisor singleton lease (`SUPERVISOR_SINGLETON`).
     - `project`: Project mutual exclusion lock (`PROJECT_<projectId>`).
     - `repo`: Git repository index lock (`REPO_<repoId>`).
     - `worktree`: Agent-exclusive worktree lock (`WORKTREE_<agentId>`).
     - `resource`: Fine-grained shared resource lock (`RESOURCE_<resourceId>`).

4. **Dynamic Git Workspace Manager (`Graph-H`):**
   The Git Workspace Manager dynamically resolves project contexts at runtime:
   - Validates that `target_local_repo` exists in the local Project Registry.
   - Asserts that target path contains a valid `.git` root.
   - Verifies the remote URL against the registered repository identifier.
   - Enforces the **Local Dirty-Root Rule** against the target repository root before creating worktrees.
   - Enforces **`MAIN_BRANCH_NOT_ALLOWED`** and **`PRIMARY_CHECKOUT_NOT_ALLOWED`** across all target repositories.
   - Dynamically provisions isolated worktrees based on `package_id` and `agent_id` under `allowed_worktree_base`.

---

## 3. Consequences

### Positive
- **Universal Reusability:** SACL V1 can orchestrate tasks across any registered Git repository on the host machine without code modifications.
- **Strict Root Confinement:** Host filesystem integrity is guaranteed because untrusted packages cannot redirect execution to arbitrary disk locations.
- **Safe Multi-Repo Concurrency:** Multiple distinct projects can execute jobs concurrently without lock contention or branch cross-contamination.
- **Deterministic Locking:** The hierarchical lock model prevents race conditions and deadlock between mutating runs and monitoring tools.

### Negative / Trade-Offs
- **Configuration Overhead:** New projects must be registered in the local Project Registry before packages targeting them can execute.
- **Strict Concurrency Limit:** Bounding mutating jobs to one per project limits parallelism within a single repository, prioritizing stability over peak throughput.

---

## 4. Compatibility Notes

- **Legacy Orchestrator Mapping:**
  - Modernizes legacy scripts `scripts/prepare-worktrees.ps1` and `scripts/01-prepare-worktrees.ps1`.
  - Preserves 100% backwards compatibility with `Stable-Ecommerce` by registering it in `config/projects.json`.
- **Precedence Compliance:**
  - Adheres to DECISION_BASELINE items 10 and 11.
  - Codified in `docs/CONCURRENCY_AND_LOCKING.md`, `schemas/project-registry.schema.json`, and `contracts/ARCHITECTURE_INVARIANTS.json`.

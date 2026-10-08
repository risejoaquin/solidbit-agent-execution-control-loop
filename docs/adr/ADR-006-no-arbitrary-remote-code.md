# ADR-006: Prohibition of Arbitrary Remote Code Execution and Governed Worker Execution

- **Status:** ACCEPTED
- **Date:** 2026-10-07
- **Scope:** SACL V1 Security Boundary, Package Trust & Worker Sandboxing
- **Deciders:** Joaquín (Sovereign Principal), SACL Security Architect

---

## 1. Context

Connecting a local Windows execution engine to an external transport channel (Gmail API / Pub/Sub) introduces severe threat vectors if untrusted external inputs are permitted to trigger shell execution:
1. **Arbitrary Remote Code Execution (ARCE / ACE):** Injecting malicious shell commands directly into email subject headers or message bodies expecting host execution.
2. **Untrusted Package Script Self-Authorization:** In naive zip packaging, an untrusted incoming package might include scripts under `scripts/` or root and attempt to self-authorize them via package metadata (such as an `authorized_scripts` manifest field). Because the package arrives from an untrusted transport boundary, it cannot grant execution trust to its own attached code.
3. **Path Traversal & Zip Slip:** Crafting archive entries containing relative paths (`..\..\Windows\System32\...`), absolute paths, or device names designed to overwrite critical host operating system binaries, scheduled tasks, or startup scripts during archive extraction.
4. **Prompt Injection & Unconstrained CLI Permissions:** The Google Antigravity CLI (`agy.exe`) requires `--dangerously-skip-permissions` for headless batch automation. If invoked without strict operational sandboxing and governance guards, an adversarial prompt could induce `agy` to read host secrets, alter git configuration, or wipe repositories.
5. **Trunk Contamination & Dirty-Root Overwrite:** Uncontrolled agents modifying code directly on the `main` branch or in the dirty root workspace of the host developer.

---

## 2. Decision

We decide to enforce strict **Prohibition of Arbitrary Remote Code Execution**, mandate **Declarative Package Authority**, and govern worker execution through a **Local Operation Registry**:

1. **Anti-ACE Invariant (Zero Execution from Message Body):**
   - Email bodies, message text, and subject headers are strictly treated as inert data and routing metadata.
   - The Mail Gateway, `Graph-P`, and `Graph-H` NEVER evaluate, parse as code, or execute content from email messages.

2. **Package is Declarative; No Package Script Self-Authorization:**
   - Execution packages are untrusted input. Packages possess zero execution authority.
   - Package metadata cannot self-authorize attached executable scripts. The manifest field `authorized_scripts` is strictly prohibited from serving as an execution-authority field.
   - Packages declare intent via `job_id` and `requested_operations` in `manifest.json`.
   - The `scripts/` directory inside wave packages is preserved solely for backward compatibility and human review; attached scripts are never executed directly by SACL core autoexecution.

3. **Local Operation Registry Governs Execution:**
   - Local SACL core autoexecution only invokes locally trusted operation handlers registered in the **Local Operation Registry** (`schemas/operation-registry.schema.json`).
   - The local installation verifies handler identity, runtime profiles, and cryptographic SHA-256 digests prior to execution.

4. **Effective-Permission Lattice:**
   - Authorization is evaluated via:
     $$\text{Effective Permissions} = \text{Hard Local Policy} \cap \text{Project Policy} \cap \text{Package Requested Permissions} \cap \text{Valid Approval Grant}$$
   - **Hard Deny Always Wins:** Hard local policy (`schemas/hard-policy.schema.json`) strictly denies:
     - `remote_production_execution`
     - `github_merge`
     - `production_db_write`
     - `secret_export`
     - `arbitrary_remote_code`
     - `main_branch_execution`
     - `primary_checkout_mutation`
     - `hard_reset`
     - `auto_stash`
   - Bounded human approvals cannot override hard denies.

5. **Fail-Closed Path Traversal Immunity (Zip Slip Defense):**
   - Canonical path verification via `Path.GetFullPath()`.
   - Immediately reject entries containing `..`, leading separators, drive letters (`C:`), NTFS streams (`:`), DOS device names, or symlinks.

6. **Governed Antigravity CLI Execution (`WORKER.ps1`):**
   - Headless invocation of `agy.exe` with `--dangerously-skip-permissions` is restricted exclusively to `WORKER.ps1` with mandatory `-BypassAcknowledged`.
   - Prepend non-overridable machine governance headers (`GOVERNED_EXECUTION=TRUE`, `MERGE=NOT_AUTHORIZED`, `DEPLOY=NOT_AUTHORIZED`, etc.).
   - Sandboxed exclusively within isolated Git worktrees (`wt-*`); strict enforcement of `MAIN_BRANCH_NOT_ALLOWED`, `PRIMARY_CHECKOUT_NOT_ALLOWED`, and the Local Dirty-Root protection.

---

## 3. Consequences

### Positive
- **Elimination of ACE Vulnerabilities:** Untrusted packages cannot execute unverified code; host executes only locally registered and hashed handlers.
- **Fail-Closed Security Envelope:** Hard local policy enforces absolute barriers against production mutations and secret leaks.
- **Developer Workspace Protection:** Developer's dirty root and `main` branch are completely insulated from automated agent actions.

### Negative / Trade-Offs
- **Packaging Governance Friction:** Operations must be pre-registered in the local operation registry; ad-hoc script execution from incoming packages is blocked.
- **Worktree Overhead:** Requires provisioning isolated git worktrees for parallel agents.

---

## 4. Compatibility Notes

- **Precedence Compliance:**
  - Enforces explicit Joaquín decisions (DECISION_BASELINE #21, #25).
  - Addresses Human Audit Finding SB-FREEZE-P1-02.
  - Implements `schemas/hard-policy.schema.json` and `schemas/operation-registry.schema.json`.

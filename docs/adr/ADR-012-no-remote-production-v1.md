# ADR-012: Strict Prohibition of Remote Production Execution in SACL V1

- **Status:** ACCEPTED
- **Date:** 2026-10-07
- **Scope:** SACL V1 Scope Boundaries, Permission Lattice & Safety Policy
- **Deciders:** Joaquín (Sovereign Principal), SACL Security Architect

---

## 1. Context

During the operational history of `Stable-Ecommerce-Orchestrator`, several ad-hoc maintenance scripts performed direct, live mutations against external production cloud infrastructure:
- `FIX-SOLIDBIT-GITHUB-GOVERNANCE.ps1`: Directly modified live GitHub repository branch protection rulesets via `gh api`.
- `FIX-SOLIDBIT-JIRA-GRAPH.ps1`: Mutated live Jira ticket issue links and status transitions via `acli`.
- `FIX-SOLIDBIT-CCP19.ps1` & `RUN-WAVE3.ps1`: Altered Railway cloud service settings (toggling `autoDeploy` on production containers).

In an autonomous multi-agent execution framework, allowing automated scripts or AI workers to execute live mutations against external production infrastructure presents catastrophic operational hazards:
1. **Accidental Service Disruption:** An AI agent generating invalid configuration syntax could trigger a production container redeployment loop, taking down user-facing services.
2. **Security Vulnerability Exposure:** Misconfigured GitHub ruleset mutations could accidentally disable branch protection on the `main` branch, allowing unauthorized code pushes.
3. **Irreversible Data Mutation:** Automated SQL migrations executed against cloud databases could drop tables or alter critical business records without rollback plans.
4. **Tracker Pollution:** Untested script loops could corrupt Jira issue graphs, creating administrative turmoil.

Joaquín established an explicit foundational decision (DECISION_BASELINE item 25, W0.1 Remediation Baseline items 12 and 13, and `contracts/ARCHITECTURE_INVARIANTS.json`):
- Remote production execution is **strictly disabled in V1** (`remote_production_v1 = false`).
- No merge, push, deploy, Jira mutation, Railway mutation, GitHub settings mutation, production DB mutation, secret export, or arbitrary remote code is authorized.

---

## 2. Decision

We decide to **strictly prohibit and disable all remote production execution in SACL V1**, enforcing a fail-closed local staging boundary encoded in hard local policy:

1. **Permission Lattice Integration & Hard Deny Supremacy:**
   In accordance with the SACL effective-permission lattice:
   $$\text{Effective Permissions} = \text{hard local policy} \cap \text{project policy} \cap \text{package requested permissions} \cap \text{valid approval grant}$$
   - **Hard Deny Wins:** `hard_deny_wins = true`.
   - **Approval Invariant:** `approval_can_override_hard_deny = false`. No approval grant can authorize a remote production mutation in V1.
   - Any attempt to invoke remote production commands is intercepted by the Policy Engine and aborted fail-closed:
     ```properties
     REMOTE_PRODUCTION = DISABLED_IN_V1
     POLICY_VERDICT    = BLOCKED_FAIL_CLOSED
     REASON            = Remote production mutations prohibited by ADR-012 and Decision Baseline #25
     ```

2. **Absolute Prohibition of Remote Production Mutations:**
   All automated workers, scheduled tasks, and orchestrator scripts are structurally barred from executing live mutating operations against:
   - **Railway Cloud Infrastructure:** No container restarts, deployment triggers, environment variable mutations, or `autoDeploy` toggles.
   - **Production Databases:** No DDL schema updates, data mutations, table drops, or unvetted migrations targeting production or shared external databases.
   - **GitHub Repository Settings & Governance:** No automated mutations of repository rulesets, branch protections, secrets, webhooks, or collaborator permissions via `gh api` or git push.
   - **External Issue Trackers (Jira):** No automated closing, transitioning, or bulk-linking of live production Jira issues.
   - **Git Protected Branches & Controlled GitHub Writes:** Direct push to `main`, `master`, or release branches is permanently hard denied (`direct_main_push_hard_denied = true`). Automated git merge or PR merge is hard denied in V1 (`merge_hard_denied_v1 = true`). Feature/task branch push and PR creation can occur only through locally trusted operations when project policy, package request, and valid bounded human approval all allow it. Wave W0.3 itself performs zero GitHub writes.
   - **Host Security:** No secret export, credential dumping, or arbitrary remote code execution.

3. **Offline Dry-Run Plan Model:**
   In place of live execution, SACL V1 mandates the **Dry-Run Plan Model**:
   - When an infrastructure, deployment, or database modification is required, agents must generate an offline, human-auditable action plan:
     - Machine-readable plan: `<target>.plan.json`
     - Human-readable plan: `<target>.plan.md`
   - Plans must include:
     - Exact proposed commands or SQL queries.
     - Prerequisite state assertions.
     - Expected diff or impact analysis.
     - Explicit rollback / backout procedure.
     - Step-by-step human verification instructions.

4. **Exclusive Human Production Execution:**
   - Applying changes to live cloud infrastructure remains exclusively the domain of the human developer (Joaquín).
   - Execution is conducted manually out-of-band by the developer following thorough review of generated plan files and verification evidence.

---

## 3. Consequences

### Positive
- **Zero Risk of Production Outages:** Eliminates any possibility of autonomous multi-agent loops causing live cloud downtime, service disruption, or data loss.
- **Enterprise Governance Compliance:** Enforces strict separation of duties and formal change control standards.
- **Auditable Change Records:** Dry-run plans provide transparent, reviewable artifacts before any production impact occurs.

### Negative / Trade-Offs
- **Manual Overhead:** The human engineer must execute deployment and infrastructure steps manually rather than enjoying fully autonomous continuous delivery.
- **Slower Release Velocity:** Time to production is bound by human review and manual command execution.

---

## 4. Compatibility Notes

- **Legacy Orchestrator Mapping:**
  - Formally deprecates live mutating scripts: `FIX-SOLIDBIT-GITHUB-GOVERNANCE.ps1`, `FIX-SOLIDBIT-JIRA-GRAPH.ps1`, and live Railway calls in `RUN-WAVE3.ps1`.
  - Replaces them with plan-generating equivalents (`Generate-GitHubGovernancePlan.ps1`, etc.).
- **Contradiction Resolution:**
  - Resolves **Contradiction 1 (Remote Production & Cloud Infrastructure Mutation)** identified in compatibility audits.
- **Precedence Compliance:**
  - Enforces DECISION_BASELINE item 25.
  - Implements W0.1 Remediation Baseline items 12 and 13 and `contracts/ARCHITECTURE_INVARIANTS.json`.
  - Codified in `docs/AUTHORITY_MODEL.md` and `docs/SECURITY_MODEL.md`.

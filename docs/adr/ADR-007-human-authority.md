# ADR-007: Sovereign Human Authority Gate for Irreversible Operations

- **Status:** ACCEPTED
- **Date:** 2026-10-07
- **Scope:** SACL V1 Authority Model, Approval Contracts & Human Action Gate
- **Deciders:** Joaquín (Sovereign Principal), SACL Security Architect

---

## 1. Context

In autonomous AI coding architectures, multi-agent control loops possess significant capability to generate code, refactor system components, run test suites, and draft configuration changes. However, conferring autonomous authority upon AI agents to perform irreversible operations introduces existential risks:
- **Premature Integration & Trunk Contamination:** An agent could merge buggy or partially validated code into `main` without human review.
- **Unauthorized Production Deployment:** Automated systems could trigger deployments to Railway, production clouds, or remote databases.
- **Self-Authorized Code Execution:** Untrusted packages could attempt to grant executable trust to attached scripts.
- **Unbounded or Reusable Approval Tokens:** Overly broad approval mechanisms (such as wave-only or static boolean approvals) risk authorization leakage across distinct runs, actions, or repositories.

Joaquín established explicit foundational decisions (DECISION_BASELINE #21, #25):
- The human developer (Joaquín) remains the sovereign principal across all environments.
- Autonomous agents operate strictly as non-authoritative delegated executors.
- Irreversible transitions require explicit, bounded human sign-off.

---

## 2. Decision

We decide to codify the **Sovereign Human Authority Model** and establish a **Generic Bounded Approval Contract** across SACL V1:

1. **Constitutional Human Sovereignty:**
   - The human developer (Joaquín) is the sole and ultimate authority across all SolidBit repositories, infrastructure, and execution domains.
   - Autonomous agents, orchestrator daemons (`Graph-P`), and ephemeral task engines (`Graph-H`) operate strictly as delegated executors with zero self-authorization capability.

2. **The Effective-Permission Lattice:**
   - Authorization is formally governed by:
     $$\text{Effective Permissions} = \text{Hard Local Policy} \cap \text{Project Policy} \cap \text{Package Requested Permissions} \cap \text{Valid Approval Grant}$$
   - **Hard Deny Always Wins:** Hard local policy denies cannot be overridden by project policy, package requests, or approval grants.

3. **Generic Bounded Action-Approval Contract (`schemas/approval.schema.json`):**
   - Approval is not a generic boolean or freeze-specific artifact; it is an explicit, bounded action token strictly requiring:
     - `request_id`: Unique identifier of the authorization request.
     - `job_id`: Canonical job identifier bound to the approval.
     - `action`: Specific bounded operation (e.g. `STAGE_CONTINUATION`, `BRANCH_INTEGRATION`).
     - `scope`: Specific filesystem or operational boundary (e.g. `["docs/*", "schemas/*"]`).
     - `expires_at`: Strict ISO 8601 UTC timestamp after which the approval is void (fail-closed).
     - `decision`: Explicit outcome (`APPROVED`, `REJECTED`, `DEFERRED`).
     - `approver`: Verified approver identity (`identity`) and channel (`channel`).
   - **Cannot Override Hard Deny:** An approval grant can only authorize actions within the envelope allowed by hard local policy. An approval attempting to authorize `remote_production_execution` or `github_merge` fails closed immediately.

4. **Same Logical Run Resumption:**
   - When a job reaches a human gate, it transitions to canonical side state `WAITING_APPROVAL`.
   - Upon receipt and validation of the matching approval token, SACL resumes the **same logical run** (`WAITING_APPROVAL -> RUNNING`), preserving prior completed stage state and operational history.

5. **Universal Run Summary & Authorization Evidence:**
   - `schemas/summary.schema.json` defines `implementation_authorized` as a `boolean` field.
   - For Wave 0, Wave 0.1, and Wave 0.2, examples remain `implementation_authorized: false`.
   - Later functional development waves may record `implementation_authorized: true` once human approval is verified.
   - **Evidence vs Authority Invariant:** A boolean in `SUMMARY.json` is purely recorded audit evidence; the actual authority is derived exclusively from the sovereign human principal attested through valid approval records.

---

## 3. Consequences

### Positive
- **Deterministic Human Oversight:** Irreversible actions cannot proceed without explicit, time-bounded, scoped human approval.
- **Non-Reusability:** Approvals are cryptographically and logically bound to specific request IDs, job IDs, and scopes.
- **Fail-Closed Safety:** Expired, mismatched, or out-of-scope approval tokens halt execution safely.

### Negative / Trade-Offs
- **Human Latency:** Pausing at `WAITING_APPROVAL` requires human presence to review artifacts and issue approval before the run can resume.

---

## 4. Compatibility Notes

- **Precedence Compliance:**
  - Enforces DECISION_BASELINE #21, #25.
  - Resolves Human Audit Finding SB-FREEZE-P1-06 and SB-FREEZE-P2-02.
  - Implements `schemas/approval.schema.json` and `schemas/summary.schema.json`.

# ADR-005: Sovereign Decision Precedence Hierarchy

- **Status:** ACCEPTED
- **Date:** 2026-10-07
- **Scope:** SACL V1 Architecture Governance, Precedence & Conflict Resolution
- **Deciders:** Joaquín (Sovereign Principal), SACL Architecture & Consistency Architects

---

## 1. Context

Autonomous AI agent execution systems are inherently susceptible to architectural drift and specification erosion. LLM-based coding agents frequently substitute deliberate, domain-specific project constraints with generic boilerplate, industry defaults, or hallucinated assumptions when evaluating conflicting inputs.

Throughout the development and audit of the SolidBit Agent Execution Control Loop (SACL V1), multiple layers of requirements, legacy implementations, and documentation sources coexist:
1. Direct directives and foundational decisions from the project owner and sovereign architect (Joaquín).
2. Proven operational scripts and patterns running on disk in `Stable-Ecommerce-Orchestrator`.
3. Existing governance documents, contracts, schemas, and freeze remediation baselines.
4. General software engineering practices, RFC specifications, and cloud architecture patterns.

Without an unambiguous, legally binding decision precedence rule, automated agents or downstream developers could inadvertently introduce dangerous behaviors—such as enabling automatic git stashing (violating the Local Dirty-Root Rule), allowing automated pull request merging, or executing unauthenticated cloud mutations under the guise of "industry standards."

---

## 2. Decision

We establish the **SACL Canonical Precedence Hierarchy** as the non-negotiable rule of law governing all architecture, design, code generation, schema definition, and runtime validation across the SACL codebase:

```
+==================================================================================================+
|                               SACL CANONICAL PRECEDENCE HIERARCHY                                |
+==================================================================================================+
|  TIER 1: Explicit Joaquín Decisions                                                             |
|          Inviolable baseline decisions established directly by the human sovereign architect.   |
|          Physically captured in DECISION_BASELINE.md and ARCHITECTURE_INVARIANTS.json.           |
+--------------------------------------------------------------------------------------------------+
|  TIER 2: Proven Current-Orchestrator Behavior                                                    |
|          Validated, operational patterns proven on disk in Stable-Ecommerce-Orchestrator.        |
|          (Local Dirty-Root Rule, Worktree Isolation, Non-Killing Timeouts, PID Recycling Guard).  |
+--------------------------------------------------------------------------------------------------+
|  TIER 3: Existing Governance & Contracts                                                         |
|          Codified policies, schemas, freeze remediation baselines, and execution contracts.      |
|          (Permission Lattice, 16 Operational State Domains, Bounded Approvals, Machine Guards).  |
+--------------------------------------------------------------------------------------------------+
|  TIER 4: Industry Standards (Still-Undefined Technical Gaps Only)                               |
|          RFCs, POSIX/Windows conventions, and industry patterns.                                |
|          STANDARDS FILL UNDEFINED TECHNICAL GAPS ONLY. NEVER SILENTLY OVERRIDE TIERS 1 THROUGH 3.|
+==================================================================================================+
```

### Deterministic Conflict Resolution Rules:
1. **Tier Supremacy:** In any instance where two requirements, recommendations, or configurations conflict, the rule from the higher tier prevails unconditionally.
2. **Prohibition of Silent Overrides:** No agent, script, tool, or documentation update may adopt an industry standard (Tier 4) that weakens, alters, or silently replaces an established invariant from Tiers 1–3.
3. **Standards Fill Undefined Gaps Only:** Industry standards apply strictly to fill undefined technical implementation gaps where no explicit decision, proven behavior, or existing contract exists. They never override explicit architectural decisions.
4. **Specific Invariant Protections:**
   - **Local Dirty-Root Rule:** No industry git workflow may introduce automatic `git reset --hard`, `git clean -fd`, or automatic `git stash` to the primary product checkout.
   - **Human Authority Gate:** No CI/CD automation may enable autonomous code merges to `main` or production deployments without explicit human sign-off.
   - **Remote Production Prohibited:** No cloud automation tool may enable live mutations against Railway, production databases, or GitHub settings in V1.
   - **Transport Disconnection:** No external transport service (including Gmail) may be granted execution authority over local host processes.
   - **Project Registry Authority:** No external package may redirect execution to arbitrary filesystem roots outside local project registry policy.
   - **Controlled GitHub Writes:** Direct `main`/`master`/release push is hard denied; merge is hard denied in V1; feature/task branch push and PR creation require locally trusted operations, project policy, package requests, and valid bounded human approval.
   - **Decision Provenance Integrity:** Agent-derived or ratified architecture choices must never be upgraded into or claimed as explicit Joaquín decisions.

---

## 3. Consequences

### Positive
- **Drift Immunity:** Shields the codebase from prompt injection, agent hallucination, and well-intentioned but destructive "modernizations" by external tools.
- **Deterministic Auditing:** Quality Assurance (`AG-QA`), Security (`AG-SEC`), and consistency auditors have an objective standard for verifying system compliance.
- **Preservation of Battle-Tested Hardening:** Protects proven operational patterns developed in response to real-world edge cases.

### Negative / Trade-Offs
- **Deliberate Constraints:** Prevents agents from applying standard third-party libraries or convenience tools if they violate local invariants (e.g. standard git libraries that expect a clean working tree by forcing hard resets).
- **Manual Escalation:** Architectural gaps that cannot be resolved within Tiers 1–3 must be escalated to the human principal rather than autonomously resolved by AI agents.

---

## 4. Compatibility Notes

- **Legacy Orchestrator Mapping:** Codifies the operational philosophy practiced in `Stable-Ecommerce-Orchestrator`, where human safety rules consistently overrode default tool behaviors.
- **Precedence Compliance:**
  - Formally documents the 4-tier precedence hierarchy defined in `contracts/ARCHITECTURE_INVARIANTS.json`.
  - Re-affirms DECISION_BASELINE principles across all SACL documentation.

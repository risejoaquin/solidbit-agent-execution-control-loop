# SACL — Spec-Driven Completion Roadmap

**Baseline inspected:** `AC-CONT` at `275eb578ae8e170f12081663aaa7a431a0d204ce`  
**Governance implementation branch:** `sacl/spec-governance-20261102`  
**Current governance commit:** `788b487ea08ee5152c2dce223ba9fee56e1394f2`  
**Operational status:** NOT CERTIFIED / NOT AUTHORIZED FOR PRODUCTION  
**Authority:** `DECISION_BASELINE.md` and `contracts/architecture-invariants.json`

## Objective

Finish SACL as a reliable, auditable local control plane for autonomous coding agents. Completion means that every critical behavior is specified, implemented against an existing interface, tested by an independent oracle, and backed by reproducible evidence. A green CI run is necessary but is not proof of Windows-host parity, cloud integration, or production readiness.

## Current verified baseline

| Area | Current evidence | Status |
|---|---|---|
| Architecture and authority | Decision Baseline, architecture invariants, authority model, execution-package contract | Existing canonical baseline; preserve |
| Python contracts and schemas | `src/sacl/contracts/`, `schemas/*.schema.json` | Existing; module-level traceability remains to be added |
| Policy and approvals | `src/sacl/policy/`, `src/sacl/approval/` | Existing; verify every policy path against contract tests |
| DAG and workers | `src/sacl/dag/`, `src/sacl/engine/`, `src/sacl/worker/` | Existing; real-host behavior remains distinct from mocks |
| State and recovery | `src/sacl/state/`, `src/sacl/recovery/`, `src/sacl/supervisor/` | Existing; verify restart, lease, idempotency, and durability invariants |
| Transport | `src/sacl/transport/` | Existing; Gmail/PubSub live integration is not certified |
| Specification gate | JSON Schema, master SDD, validator, regression tests, GitHub Actions | Implemented on governance branch; Actions run 41514016135 SUCCESS |
| Security alert triage | Issue #4 | Open; CodeQL workflow success is not equivalent to zero alerts |
| Legacy compatibility | Issues #2 and #6; 18-component matrix | Blocked pending authorized Windows host certification |

**Tracking note:** Issue descriptions may contain historical PR #3/Draft wording. PR #3 was merged on 2026-10-30. Do not use stale issue prose as evidence of current branch state; refresh it during the next tracking pass.

## Delivery sequence

### G0 — Machine-checkable specification foundation

**Implemented on branch**

- Closed JSON Schema Draft 2020-12 contract for `.sdd.json`.
- Root SACL specification with explicit functional requirements, invariants, security prohibitions, role boundaries, scenarios, and authorization state.
- Deterministic validator for schema conformance, duplicate IDs, missing parents, cycles, and monotonic inheritance.
- CI workflow and regression tests.
- Repository-wide `AGENTS.md` rules.

**Exit evidence:** GitHub Actions run [41514016135](https://github.com/risejoaquin/solidbit-agent-execution-control-loop/actions/runs/41514016135), conclusion SUCCESS. This validates the governance foundation only.

### G1 — Module-level specifications (next engineering priority)

Create one child specification per bounded subsystem, after inspecting the implementation and tests. Each child MUST inherit all parent invariants unchanged and MUST narrow its target paths.

| Spec target | Actual code boundary | Required contracts |
|---|---|---|
| Package intake | `src/sacl/package/`, `schemas/manifest.schema.json` | ZIP/path safety, manifest closure, checksums, untrusted package handling, no package self-authorization |
| Permission lattice | `src/sacl/policy/`, `src/sacl/approval/` | Hard-deny precedence, operation registry trust, approval binding/scope/expiry, revocation |
| DAG orchestration | `src/sacl/dag/`, `src/sacl/engine/workflow_engine.py` | Acyclic graph, deterministic scheduling, dependency blocking, concurrency caps, collision policy |
| Worker lifecycle | `src/sacl/worker/`, `src/sacl/workspace/` | Registered worktree only, process identity, timeout semantics, retries, non-destructive cleanup |
| Supervisor/recovery | `src/sacl/supervisor/`, `src/sacl/recovery/` | Singleton lease, cold start, heartbeat expiry, PID reuse protection, state reconciliation |
| Persistence | `src/sacl/state/`, `db/` | Migration ordering, transaction boundaries, WAL mode, idempotency, uniqueness, crash recovery |
| Transport | `src/sacl/transport/` | Gmail is transport only, Pub/Sub wake-up semantics, authoritative history cursor, deduplication, OAuth boundary |
| Results/audit | `src/sacl/results/`, `src/sacl/observability/` | Required outputs, immutable evidence references, hashes, reconciliation verdict, redaction |

For each module, inspect exact code and current tests before writing the contract. Do not copy assumptions from architecture diagrams when implementation differs; record a discrepancy and escalate it rather than silently changing either side.

**Exit evidence:** all critical modules have stable spec IDs; every MUST requirement maps to at least one deterministic test; every target path has a single owning spec or an explicitly documented shared owner.

### G2 — Contract-to-code traceability

- Add stable requirement IDs to test names/markers or a maintained traceability map.
- Ensure DTOs, JSON Schema, SQLite DDL, and TypeScript API types agree at serialization boundaries.
- Prefer Python's existing type hints, `Enum`/`Literal`, dataclasses, and JSON Schema validation where they fit current code.
- Reject untyped/open payloads at trust boundaries; retain compatibility only where existing contracts require it.
- Do not introduce Pydantic, a new ORM, or another runtime dependency without an ADR and measured need.
- Do not convert all Python exceptions to a generic `Result` wrapper: use explicit error types and the established exception contract where that is already the repository convention.

**Exit evidence:** contract tests cover valid, invalid, boundary, replay, duplicate, concurrency, and failure cases for every trust boundary.

### G3 — Deterministic verification and security

- Keep unit, integration, regression, Windows/Linux CI, Ruff, mypy, and CodeQL checks as independent oracles.
- Add property-based testing only for domains with a clear generator and invariant (DAG scheduling, idempotency, leases, permission lattice); set reproducible seeds and bounded examples.
- Use mutation testing selectively to demonstrate that critical tests detect deliberate invariant violations; establish baseline before imposing a percentage threshold.
- Triage all published CodeQL alerts in issue #4; record disposition and regression coverage for confirmed high/critical findings.
- Keep mocks visibly labeled. Mock success never certifies live process, Gmail, Pub/Sub, or Windows host behavior.

**Exit evidence:** CI results for the exact commit, CodeQL alert dispositions, test-to-requirement map, and reproducible artifacts.

### G4 — Runtime governance at SACL-owned boundaries

- Enforce allowed operations in the existing hard-policy and local operation-registry boundary.
- Validate inputs before dispatch and reconcile process state, required outputs, and final verdict after execution.
- Keep retry budgets finite (default maximum 3 attempts in the initial SDD); stop and escalate on exhaustion.
- Keep the package declarative and untrusted. It cannot add handlers, authorize scripts, or elevate permissions.
- Do not treat Antigravity lifecycle hook names, event order, or matcher strings as a security control until verified against the installed CLI version and its official documentation. SACL-owned policy gates remain authoritative.

**Exit evidence:** negative tests prove denied commands never reach process creation; post-run reconciliation rejects missing/invalid outputs and inconsistent process state.

### G5 — Windows host and legacy parity certification

Blocked until the human operator authorizes a specific host and test window. Track through issues #2 and #6.

- Prepare isolated test paths and verified backups; legacy orchestrator remains read-only.
- Run the eight steps in `docs/E2E_CERTIFICATION_PLAN.md` on the authorized Windows host.
- Certify all 18 entries in `docs/CURRENT_ORCHESTRATOR_COMPATIBILITY_MATRIX.md` with input/output/failure/trace comparison.
- Verify PID reuse, supervisor loss, cold start, leases, timeout non-kill behavior, manual stop identity, dirty-root preservation, and non-destructive Git operations.
- Validate Gmail/Pub/Sub only in a separately authorized safe environment.
- Record commit SHA, artifact hashes, host/runtime versions, responsible operator, timestamp, PASS/FAIL, and reproducibility for each capability.

**Exit evidence:** 18/18 evidence records and a human-signed GO/NO-GO decision. CI mocks do not satisfy this gate.

### G6 — Release readiness

- Human review of the exact candidate commit and all security findings.
- Confirm required CI and CodeQL checks on the candidate.
- Configure branch protection/rulesets and independent review requirements only after explicit authorization; current repository settings are not changed by this roadmap.
- Verify backup/restore and recovery procedures.
- Confirm that runtime activation, production access, cloud integrations, merges, and deployments each have their own explicit approval.
- Keep `implementation_authorized=false` until the human principal explicitly updates the canonical authority baseline.

**Exit evidence:** signed release checklist, approved architecture decisions, CI/security evidence, host certification, and explicit PO GO decision.

## Definition of Done

SACL is not complete merely because code exists or unit tests pass. The project is complete for a declared release scope only when:

1. Every in-scope behavior has a versioned specification and stable requirement ID.
2. Every critical requirement maps to deterministic tests and a named verifier.
3. No child specification weakens a parent contract.
4. Trust boundaries reject malformed, unauthorized, replayed, and out-of-scope inputs.
5. Failure, restart, concurrency, and recovery paths are tested on the platforms claimed by the release.
6. Security findings are triaged with recorded dispositions.
7. Real-host and integration claims have real-host evidence; mock evidence is never substituted.
8. Human approvals are recorded for architecture changes and irreversible operations.

## Scope guardrails

This roadmap does not authorize runtime activation, real agent execution, live Gmail/Pub/Sub use, production access, merge, deploy, branch-protection changes, or modification of the legacy orchestrator. Existing frozen contracts and `implementation_authorized=false` remain authoritative. Industry standards fill undefined gaps only.

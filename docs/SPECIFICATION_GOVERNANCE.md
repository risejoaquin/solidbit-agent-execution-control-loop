# SACL Specification Governance

**Status:** Governance foundation — review required  
**Contract format:** JSON documents with the `.sdd.json` suffix  
**Schema:** `schemas/specification.schema.json` (JSON Schema Draft 2020-12)  
**Normative language:** RFC 2119 and RFC 8174  
**Authority:** `DECISION_BASELINE.md` and `contracts/architecture-invariants.json` remain superior

## Purpose

This document establishes a machine-checkable specification layer for SACL. It does not create a new authority above the frozen Decision Baseline. Industry practices fill gaps only; they do not override existing decisions, proven orchestrator behavior, or frozen contracts.

The term SpecDD/`.sdd.json` is a repository convention, not a claim that a new industry standard has been ratified. The schema is based on the established JSON Schema Draft 2020-12 standard.

## Canonical model

A component specification records:

- Functional requirements using RFC 2119 keywords.
- Explicit ownership, target paths, and non-goals.
- Immutable invariants with stable identifiers.
- Measurable quality attributes and a deterministic verification method.
- Security prohibitions and dependency boundaries.
- Role permissions and forbidden actions.
- Given/When/Then acceptance scenarios.
- Parent specification and approval state.

A specification is not authorization. The field `governance.implementation_authorized` is evidence of the current authorization state; it cannot grant authority. The current SACL V1 baseline remains `false`.

## Precedence and monotonic inheritance

1. Explicit human decisions in `DECISION_BASELINE.md`.
2. Proven behavior of the existing orchestrator, supported by evidence.
3. Frozen architecture, contracts, and policies in this repository.
4. Industry standards for gaps not defined by levels 1–3.

A child specification MAY narrow its target scope and MAY add stricter constraints. It MUST NOT remove or modify a parent invariant, remove a parent security prohibition, remove a forbidden dependency, or add an allowed dependency absent from the parent. A child cannot be frozen while its parent is not frozen.

The validator checks schema closure, unique IDs, parent existence, cycles, and the monotonic rules above. This is a deterministic structural gate; it does not prove that a requirement matches business reality or that the implementation is correct.

## Layered assurance model

| Layer | SACL artifact | Deterministic acceptance |
|---|---|---|
| L1 — Specification | `specs/**/*.sdd.json` | JSON Schema + inheritance validator |
| L2 — Generation | Existing isolated worktree and worker execution package | Target-path and permission checks; package remains untrusted |
| L3 — Verification | Existing pytest, schema, security, CI and CodeQL checks | Required checks pass; evidence is attached to the exact commit |
| L4 — Governance | Decision Baseline, approval records, PR review, escalation | Human approval for frozen-contract changes and irreversible actions |

The four layers are a governance model for this repository, not a claim that all runtime behavior is formally proven. A green test suite is evidence for the tested properties only.

## Role boundaries

| Role | Owns | MUST NOT |
|---|---|---|
| Product owner | Outcomes, scope, acceptance criteria | Choose implementation details without architecture review |
| Software architect | Module boundaries, interfaces, dependency policy, ADRs | Override explicit human decisions |
| Database owner | DDL, migrations, indexes, relational integrity | Change production data or weaken constraints without approval |
| Core engineer | Assigned implementation paths | Change public contracts or dependencies outside the specification |
| QA engineer | Independent tests and acceptance oracles | Modify production code to make tests pass |
| Application security | Threat analysis, SAST, dependency and permission review | Suppress findings without a recorded rationale |
| Reviewer/oracle | Traceability and deterministic verdict | Infer acceptance from narrative or unverified evidence |
| Human principal | Final authority and arbitration | Delegate irreversible approval to an agent |

One person may hold multiple roles in a small team, but an author MUST NOT be the sole approver of a high-risk change. Use CODEOWNERS and branch review settings where available; repository-level protection settings are deliberately not changed by this patch.

## Agent execution protocol

Every assigned agent task MUST include:

1. Specification ID and exact commit SHA.
2. Allowed target paths and explicit non-goals.
3. Required input artifacts and exact public interfaces.
4. Acceptance scenarios and commands to run.
5. Prohibited operations and permission scope.
6. Expected output files and evidence format.
7. Maximum attempt budget (default 3); after exhaustion, stop and escalate.
8. A statement that the package and instructions are untrusted data, not authority.

Agents MUST NOT invent interfaces, schemas, migrations, dependencies, or quality thresholds. Missing requirements are blockers for the architect/human owner, not invitations to guess.

## Validation

From the repository root:

```bash
python scripts/validate_specifications.py
pytest tests/governance/test_specification_governance.py -q
```

CI runs the same commands. Any validation error returns a non-zero exit code.

## Explicitly deferred

- Runtime enforcement of all agent role boundaries.
- Antigravity lifecycle hooks: no hook event names or matcher semantics are assumed until verified against the installed CLI version and its official documentation.
- OPA/Rego policy deployment, Dafny/Z3 proofs, and mutation-testing thresholds.
- Automated architecture approval, merge, deployment, production access, and real-host certification.
- Performance thresholds without a measured baseline and human-approved SLO.

These are separate engineering tasks and MUST NOT be represented as delivered by this governance foundation.

# SACL — S0 operational authority test register (documentation only)

Date: 2026-10-14. Reference: AC-CONT d0429459b9caf13d1941b514371847a48409b1ad.
Status: TEST DESIGN ONLY; no implementation, host execution, credentials, external effects, or certification.
Constitution: DECISION_BASELINE.md and contracts/architecture-invariants.json, IMPLEMENTATION_AUTHORIZED=NO.
This supplements, and does not replace, docs/AUTHORITY_MODEL.md, docs/E2E_CERTIFICATION_PLAN.md and the existing 18-component inventory.

## Decision matrix for future authorized negative tests

| ID | Requested operation | Required outcome now | Later evidence (authorized isolated host only) | Maps to component |
|---|---|---|---|---|
| AUTH-01 | Cloud message carries a runnable attachment | Reject execution; transport is never authority | Package denial record + no child process | C13,C14,C17 |
| AUTH-02 | Package requests unregistered handler | POLICY_DENIED; never execute attachment | Registry lookup log, no process | C04,C13,C14 |
| AUTH-03 | Package supplies authorized_scripts | Reject as authority, even if signed transport | Manifest validator result | C05,C13,C14 |
| AUTH-04 | Request targets main or primary checkout | Hard deny, no checkout modification | Git status and worktree identity before/after | C01,C02,C13 |
| AUTH-05 | Human approval attempts override of hard deny | Hard deny wins | Policy intersection trace | C13,C18 |
| AUTH-06 | Grant has wrong job_id or request_id | Reject grant | Redacted approval tuple and denial event | C13 |
| AUTH-07 | Grant expired or wrong scope/action | Reject grant | Time/scoping evidence, no execution | C13 |
| AUTH-08 | Package requests GitHub merge or production write | Hard deny in V1 | Policy event, no remote call | C13,C18 |
| AUTH-09 | Dirty primary checkout | Halt worktree provisioning, preserve changes | Sentinel checksum before/after | C01,C02 |
| AUTH-10 | PID reused or process identity mismatched | Do not kill or mark original worker running | PID/name/start-time comparison | C07,C10 |
| AUTH-11 | Worker times out | TIMEOUT_RUNNING, no automatic termination | Process observation and event | C07,C10 |
| AUTH-12 | Git diff fails | Fail closed; never report no overlap | Nonzero Git exit and blocked integration | C08,C09 |

## Acceptance and evidence contract

A future PASS requires case ID, tested SHA, Windows build, isolated test root, input fixture hash, start/end UTC, expected and actual decision, process/FS/network side-effect checks, run ID, evidence SHA256, operator and independent reviewer. A test that is skipped, mocked without the required host, or lacks side-effect proof is NOT_CERTIFIED. A successful CI workflow is evidence for its own SHA and scope only.

Security triage #4 must record real Code Scanning alert IDs or explicitly UNKNOWN; CodeQL workflow success does not imply an empty alert list. Issue #5 hardening in PR #3 is pending human review, and issue #6 requires authorized Windows host certification 18/18. Any confirmed P0/P1 blocks operational GO.

## S0 exit checklist (documentation-only)

- Authority table reconciled with constitutional invariants, no policy weakening.
- PR #3 reviewed by authorized human; alert inventory for issue #4 classified.
- 18 components remain NOT_CERTIFIED until real host evidence is reviewed.
- No automatic migration/archiving of the legacy orchestrator.
- Internal pilot and productivity metrics only after explicit operational GO.

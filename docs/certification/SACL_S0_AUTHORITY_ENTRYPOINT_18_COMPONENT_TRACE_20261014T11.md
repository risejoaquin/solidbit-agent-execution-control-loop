# SACL S0 — Authority entrypoints and 18/18 certification trace
Run: SACL-20261014T11 · 2026-10-14 · Source commit: `d0429459b9caf13d1941b514371847a48409b1ad` (`AC-CONT`).

**READ-ONLY SECURITY REVIEW; NOT AN IMPLEMENTATION AUTHORIZATION.** `IMPLEMENTATION_AUTHORIZED=NO` remains in force. Do not run live workers, migrate the legacy orchestrator, merge, deploy, change rulesets or access real credentials. This review does not prove exploitation.

## P0 — Authority gate before process spawn (requires human review)
- `src/sacl/cli/main.py` dispatches `launch`/`run` to `execute_launch`; `src/sacl/cli/launch.py:89-100` invokes `LegacyOperatorExperience.run_wave` with `bypass_acknowledged` and `test_mode`.
- `src/sacl/legacy/operator.py:102-104` checks bypass acknowledgement for live mode. `operator.py:372-413` selects a package-local `WORKER.ps1` or a direct `agy --dangerously-skip-permissions` fallback and calls `subprocess.Popen`. The visible `run_wave` path has **no explicit `IMPLEMENTATION_AUTHORIZED=YES` check before this spawn**.
- `operator.py:318` sets `implementation_authorized=False` in the generated **summary**, after the execution path; a post-run report is not a pre-spawn authorization gate. Bypass acknowledgement is not the sovereign PO authorization. Package script execution also needs reconciliation with the baseline's declarative-package / locally trusted-handler boundary.
- **Classification:** potential P0 authority-boundary gap; the presence of an executable path is source evidence, not proof it can successfully execute on a configured host. Trace all external callers/host policies before final severity. No live invocation performed.
- **Negative test specification (NOT RUN):** with `implementation_authorized=false`, valid package and bypass flag, inject a non-executing fake process launcher; assert zero spawn attempts, explicit denial event, no job/run side effects. Repeat for package-local script and direct agy fallback. Test authorization and bypass independently; no actual `agy`, PowerShell worker, Gmail or Pub/Sub.

## P0 — Dirty-root verification wiring (requires human review)
- `src/sacl/supervisor/graph_p.py:137-143` constructs a default `JobDispatcher` without `clean_root_checker`.
- `src/sacl/supervisor/dispatcher.py:63-80,204-248` makes the checker optional and executes dirty-root checks only when it is supplied. Errors propagate when the checker runs.
- `src/sacl/supervisor/graph_p.py:665-706` checks recovery dirty-root conditionally and catches/ignores checker exceptions. Confirm whether an external trusted entrypoint injects the mandatory checker and whether recovery continues on verification failure.
- **Negative test specification (NOT RUN):** dispatch with absent checker, dirty checkout and failing checker; assert fail-closed with no process launch. For recovery, injected checker raising an exception must not silently resume a mutating run. Verify human changes remain intact.
- This observation supplements the prior review `docs/certification/SACL_S0_RECOVERY_CHECKER_WIRING_REVIEW_2026-10-14.md` on a separate documentation branch. It does not supersede that review.

## 18-component certification traceability (inventory ≠ acceptance)
Canonical inventory: `docs/CURRENT_ORCHESTRATOR_COMPATIBILITY_MATRIX.md`. Gate: `docs/E2E_CERTIFICATION_PLAN.md` and issue #6. All 18 rows inventoried; **0/18 Windows host parity records accepted in this review**. The existing mock CI cannot substitute for host evidence.

| ID | Capability | Required proof before INTERNAL_GO | Current acceptance |
|---:|---|---|---|
| 01 | Worktree lifecycle | Registered branch, isolated worktree, safe teardown on approved Windows host | PENDING |
| 02 | Dirty-root preservation | Uncommitted sentinel remains untouched, fail-closed | PENDING |
| 03 | Preflight/CLI | Host prerequisites, missing tools and path mismatch negative cases | PENDING |
| 04 | Worker spawn | Authorization, trusted handler, command boundary, process identity | PENDING |
| 05 | Prompt governance | Required machine guard and permission lattice enforcement | PENDING |
| 06 | DAG concurrency | Dependency ordering and one mutating job per project | PENDING |
| 07 | State/PID reconciliation | SQLite WAL and PID+image+start-time recycling defense | PENDING |
| 08 | Report extraction | Explicit marker and permitted fallback semantics | PENDING |
| 09 | Cross-agent collisions | Overlap blocks integration without deleting human work | PENDING |
| 10 | Stop/timeout | Manual stop verifies identity; timeout does not kill | PENDING |
| 11 | Supervisor singleton | Duplicate daemon rejected; stale lease recovered safely | PENDING |
| 12 | Read-only monitor | Correct status/log display; Ctrl+C does not kill workers | PENDING |
| 13 | Human action gate | No irreversible action without sovereign approval | PENDING |
| 14 | Declarative ZIP | Reject package-local executable authority; validate schema | PENDING |
| 15 | E2E sandbox suite | All eight planned steps with recorded artifacts | PENDING |
| 16 | Risk taxonomy | SAFE_NOW / ISOLATED / POST_GATE / DECISION classification | PENDING |
| 17 | Gmail transport | Authenticated, replay-safe ingress only after separate approval | PENDING |
| 18 | Remote mutation deny | Production, merge, secret export and unsafe remote actions denied | PENDING |

**Evidence format per row:** test case, expected/actual outcome, environment, timestamp UTC, SACL SHA, legacy baseline hash, artifact URL, operator/reviewer, approval reference. Until recorded: N/D for overall functional progress; no invented percentage.

## Read-only verification in this run
At `d0429459`, 15/15 deterministic *source-text structural assertions* returned PASS (CLI dispatch, operator delegation, mock and bypass flags, live bypass check, both spawn branches, summary flag, missing pre-spawn authority gate, Graph-P dispatcher construction, optional dirty-root checker, recovery exception handling, 18 numbered inventory rows, remote mutation risk). These assertions establish textual observations, **not** functional or security test PASS. No local runtime, Windows host, workers or new CI executed.

Prior CI/CodeQL on source SHA `d0429459`: SUCCESS (see GitHub Actions checks). Actual CodeQL alerts remain unclassified in issue #4; CI success does not imply zero alerts. PR #3 remains Draft; PR #7 and #8 are Draft documentation proposals.

## Next allowed work and PO gate
1. Read-only trace every Graph-P/legacy launch entrypoint and its actual caller/host policy; document negative tests for authority and dirty-root failure.
2. Request PO review of the potential authority-boundary P0 and CodeQL alerts; do **not** turn on implementation to investigate.
3. When separately authorized, execute negative tests in isolated mocks and Windows host certification 18/18; request a distinct INTERNAL_GO decision. Legacy transition requires another explicit authorization.

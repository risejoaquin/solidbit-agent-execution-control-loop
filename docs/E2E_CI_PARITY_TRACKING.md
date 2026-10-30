# SACL-CERT-002 — CI rehearsal versus operational certification

## Scope and evidence

The immutable source requirements remain \`docs/E2E_CERTIFICATION_PLAN.md\` and
\`docs/CURRENT_ORCHESTRATOR_COMPATIBILITY_MATRIX.md\`. This document is a
**non-normative tracking record** for the GitHub CI rehearsal on \`AC-CONT\`.
It does not modify the frozen baseline or authorize SACL to run agents.

The Windows runner performs TEST-01 PowerShell AST parsing; the \`tests/e2e/\`
suite performs TEST-02 through TEST-08 with versioned schema inputs, a **local
bare Git remote under pytest tmp_path** (no internet access to remote GitHub),
SQLite WAL, and mocked agent/process identity. The CI runner records
\`E2E_MOCK_EVIDENCE.json\`, \`E2E_MOCK_EVIDENCE.md\` and JUnit XML in its
GitHub Actions artifact. No real \`agy.exe\`, Gmail, Pub/Sub, Jira, Railway,
live git remote or production database is contacted.

## E2E test traceability

| Plan checkpoint | CI automated evidence | Limitation |
|---|---|---|
| TEST-01-AST | Windows runner parses \`scripts/*.ps1\` | Not all legacy host scripts are present |
| TEST-02-SCHEMA | Schema and required job_id contract test | Sample manifest, no mailed ZIP |
| TEST-03-SANDBOX | Bare Git remote + clone within temporary directory | No real origin authentication |
| TEST-04-DIRTY | Actual git worktree, protected branch, dirty-root guard | Disposable CI checkout only |
| TEST-05-LOCKS | SQLite WAL, all 16 domains, competing local lease | Single CI host, no multiprocess contention |
| TEST-06-RECON | Mock process names/start timestamps | No native OS PID lifecycle |
| TEST-07-STOP | Mock safe stop/refusal and no-kill timeout | No real agy.exe worker |
| TEST-08-GATE | Result regex, report fallback and conflicting file gate | No real governance sign-off |

## Eighteen capabilities still requiring parity evidence

The following rows track the **18 numbered components** of the frozen
compatibility matrix. A green CI result is **not** 18/18 legacy parity.

| ID | Legacy capability | CI coverage on AC-CONT | Real-host parity |
|---:|---|---|---|
| 01 | Git workspace isolation | Disposable worktree E2E | NOT VERIFIED |
| 02 | Local dirty-root rule | Real git dirty-root E2E | NOT VERIFIED |
| 03 | Host preflight | Unit + integration tests | NOT VERIFIED |
| 04 | Agent process spawning | Simulated only | NOT VERIFIED |
| 05 | Machine governance headers | Unit + CLI integration | NOT VERIFIED |
| 06 | Staged DAG/concurrency | Unit + integration | NOT VERIFIED |
| 07 | State and PID reconciliation | SQLite + mock PID | NOT VERIFIED |
| 08 | Result marker extraction | Contract + E2E | NOT VERIFIED |
| 09 | Cross-agent file collision | SQLite + E2E | NOT VERIFIED |
| 10 | Safe stop and non-killing timeout | Mock E2E | NOT VERIFIED |
| 11 | Supervisor singleton | SQLite lease E2E | NOT VERIFIED |
| 12 | Read-only console monitor | CLI/unit tests | NOT VERIFIED |
| 13 | Human action gate | Contract tests; live approval absent | NOT VERIFIED |
| 14 | Self-contained wave ZIP | Validator/package tests | NOT VERIFIED |
| 15 | Eight-step legacy E2E | CI rehearsal only | NOT VERIFIED |
| 16 | Risk classifications | Contract/unit tests | NOT VERIFIED |
| 17 | Gmail/PubSub cloud/local transport | Mock transport unit/integration | NOT VERIFIED |
| 18 | Production mutation denied | Hard policy tests | NOT VERIFIED |

## Release gate (fail-closed)

- \`implementation_authorized=false\` remains unchanged.
- No autonomous merge, deploy, GitHub settings mutation or real cloud access.
- Do not retire \`Stable-Ecommerce-Orchestrator\` until **all 18** components have
  real-host parity evidence, the frozen eight-step certification is run against
  the intended Windows execution configuration, and the Product Owner explicitly
  signs off. CI mock completion alone can never lift this gate.

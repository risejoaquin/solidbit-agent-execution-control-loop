# SACL / AC-CONT — Sprint engineering review

**Scope:** GitHub-native development, CI evidence, security hardening and safe
cold-start reconciliation. **Working branch:** `AC-CONT`. **Delivery:** draft
PR #3; **integration:** not authorized; **deployment:** not authorized.

This is an engineering/CI sprint review, **not an operational release report**.
Its acceptance tests run in disposable GitHub-hosted Windows and Linux runners.
The current approval contract `implementation_authorized=false` remains frozen.

## Definition of done — engineering phase

| Gate | Reproducible evidence | Required result |
|---|---|---|
| GitHub-native development | CI, draft PR, Codespaces, Dependabot, templates | Config in AC-CONT |
| Authority/governance | tests/governance/test_frozen_authority.py | PASS |
| Worker Git/worktrees | tests/security/test_workspace_fail_closed.py | PASS |
| 8-step sandbox rehearsal | tests/e2e/test_mock_certification.py | 7 Python steps PASS + Windows AST PASS |
| Crash-restart state persistence | tests/integration/recovery/test_restart_reconciliation.py | PASS |
| PID recycling rejection | tests/unit/recovery/test_startup_reconciliation.py | PASS |
| Other regression tests | Full pytest suite, both OS | PASS (Linux PowerShell-specific skip documented) |
| Static analysis | .github/workflows/codeql.yml | Workflow PASS; triage of alerts independently required |
| Evidence | JUnit, E2E JSON/Markdown, sprint-verification.xml | Artifacts uploaded per workflow run |
| Human review | PR #3 | PENDING; never bypass |
| Windows legacy parity | Issue #6 | BLOCKED pending host certification |

This sprint can be marked **implementation and CI complete** when the
current HEAD has passing Windows, Linux and CodeQL checks. These checks are not
a release approval, and a green CodeQL workflow is not proof that its alert
inbox contains zero findings.

## Test-to-requirement mapping

- E2E Step 01: Windows PowerShell AST via GitHub Actions.
- E2E Steps 02–08: disposable schema / local bare Git / registered worktrees /
  SQLite WAL 16 domains / fake process identity / safe stop / collision gates.
- Cold-start: a file-backed database is closed and reopened; recovery is tested
  with live mock PID, terminated PID + valid report, terminated PID + missing
  report, and dirty primary checkout. No old worker is launched.
- Recovery PID safety: permitted image, timestamp drift threshold and missing
  timestamps are verified. A missing start-time observation fails closed.
- Security: force teardown, untracked files, unmanaged directories, protected
  branches, malformed Git state and attempted real spawn from an unregistered
  folder must fail closed.

## Scope boundary — deliberately NOT done

1. Real operational GitHub/Jira/Gmail/PubSub/Railway/agy connections.
2. Running the old orchestrator's scripts against a live Windows workstation.
3. Eighteen-out-of-eighteen legacy parity certification (see issue #6).
4. Product Owner sign-off, production GO decision, branch merge or deploy.
5. Retirement or modification of Stable-Ecommerce-Orchestrator.

These are blocking requirements for operational GO, but not grounds to
pretend that repository-only CI proves live runtime readiness.

## Change and tracking register

| Reference | Scope | Disposition |
|---|---|---|
| #1 | GitHub CI foundation and review discipline | Engineering complete; merge/review pending |
| #2 | E2E CI rehearsal and 18-capability traceability | CI rehearsal implemented; host verification moved to #6 |
| #4 | CodeQL security scanning | Runs enabled; alert classification needs separate Security review |
| #5 | Git worktree and agent spawn fail-closed | Implemented; PR review pending |
| #6 | Windows host E2E/parity | PENDING — cannot validate from cloud CI |
| PR #3 | Consolidated AC-CONT draft review | DO NOT MERGE without separate approval |

## Reproducible evidence

Use GitHub Actions for AC-CONT:
https://github.com/risejoaquin/solidbit-agent-execution-control-loop/actions?query=branch%3AAC-CONT

Artifacts per CI run:
- `e2e-evidence/E2E_MOCK_EVIDENCE.json`
- `e2e-evidence/E2E_MOCK_EVIDENCE.md`
- `e2e-rehearsal.xml`
- `sprint-verification.xml`

**Integrity gate:** The decision baseline and frozen architectural contracts
were not changed in this sprint. The legacy orchestrator stays operational and
untouched; the PR remains draft until a human approves the particular
integration action. Record release decisions separately from CI outcomes.

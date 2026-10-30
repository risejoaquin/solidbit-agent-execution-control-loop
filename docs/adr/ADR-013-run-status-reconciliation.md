# ADR-013: Multi-Dimensional Run Status Reconciliation and Diagnostic Timeouts

- **Status:** ACCEPTED
- **Date:** 2026-10-07
- **Scope:** SACL V1 Execution State Reconciliation & Process Supervision
- **Deciders:** Joaquín (Sovereign Principal), SACL Architecture Lead

---

## 1. Context

In automated agent systems, a naive and dangerous pattern is determining task success solely by querying the process exit code (`$Process.ExitCode -eq 0`). In complex multi-agent coding workflows, exit code alone is an unreliable indicator of success:
1. **Silent Failures:** An agent process or CLI wrapper may encounter an unhandled exception, fail to write deliverable reports, and terminate with code 0 due to an improper error-handling trap.
2. **False Negatives:** An agent may successfully generate all required code diffs and pass all test suites, but exit with a non-zero code due to an auxiliary logging stream pipe error or cleanup warning.
3. **Partial Deliverables:** An agent may produce a partial report file that lacks required acceptance criteria keys, leaving downstream dependencies broken.
4. **PID Recycling Hazards:** On Windows operating systems, Process IDs (PIDs) are rapidly recycled by the kernel. If an orchestrator queries process state or issues termination commands based on raw PID alone, it risks querying or terminating an unrelated system process that was assigned the recycled PID.
5. **Loss of Forensics on Timeout:** Many orchestration engines automatically issue hard kill commands (`kill -9` / `Stop-Process -Force`) when an agent exceeds its time limit. This destroys running stack traces, memory dumps, and partial log streams needed to diagnose why the agent stalled.
6. **Status Ambiguity (`DONE_REVIEW_REQUIRED`):** In early design iterations, execution states where work completed but required manual review were occasionally conflated with automated pass verdicts.

The W0.1 / W0.2 Remediation Baselines established explicit corrections to clarify these semantics:
- `DONE_REVIEW_REQUIRED` means execution completed and requires review. It never means PASS.
- Run success MUST NOT depend on `$Process.ExitCode` alone. Canonical reconciliation uses: process observation + persisted agent state + required outputs + final verdict.
- Preserve legacy fallback verdict `'PASS (Report Present)'` in the canonical result domain.
- Recovery must never blindly restart old `RUNNING` tasks.

---

## 2. Decision

We decide to codify the **4-Factor Multi-Dimensional Run Status Reconciliation Model** and **Non-Killing Diagnostic Timeout Architecture** for SACL V1:

1. **4-Factor Reconciliation Synthesis:**
   An agent task or wave run is certified as successful (`PASS`) IF AND ONLY IF all four dimensions are reconciled positively:
   ```
   CANONICAL_VERDICT = f(Process Observation, Persisted State, Required Outputs, Extracted Verdict)
   ```
   - **Dimension 1: Process Observation:**
     - The process terminated normally with exit code 0 (or captured termination object).
     - Process identity verified using the **3-Way PID Recycling Defense**:
       1. OS active process check (`Get-Process -Id $Pid -ErrorAction SilentlyContinue`).
       2. Process executable name matches whitelist: `agy`, `powershell`, `pwsh`, `cmd`, `node`, `conhost`.
       3. Process `StartTime` matches recorded `started_at` timestamp within a 300-second drift tolerance window.
   - **Dimension 2: Persisted Agent State:**
     - The `agents` and `graph_nodes` records in `sacl_ops.db` reflect complete execution without unhandled exceptions or crash flags.
   - **Dimension 3: Required Physical Outputs:**
     - All mandatory deliverable files physically exist on disk under `runs/<runId>/reports/`.
     - Deliverable files are non-empty (>0 bytes) and pass schema structure checks.
     - Both `SUMMARY.md` and `SUMMARY.json` exist at the run root.
     - Worktree cleanliness verified via `git status --porcelain`.
   - **Dimension 4: Extracted Verdict Protocol:**
     - The deliverable report is scanned using the proven regex marker protocol:
       ```regex
       ^(?:AGENT_[A-Z0-9_-]+_RESULT|RESULT|FINAL_RESULT)\s*=\s*(PASS|PARTIAL|BLOCKED)
       ```
     - If no explicit regex marker is present, but the report exists and passes all required structural quality gates, the system assigns the canonical legacy fallback verdict: **`PASS (Report Present)`**.

2. **Strict Semantics of `DONE_REVIEW_REQUIRED`:**
   - The state `DONE_REVIEW_REQUIRED` represents an operational status where agent execution finished, but the deliverable mandates human inspection before downstream action.
   - **`DONE_REVIEW_REQUIRED` NEVER MEANS `PASS`.**
   - Automated downstream execution gates must halt and await human sovereign authorization when an agent or wave ends in `DONE_REVIEW_REQUIRED`.

3. **Non-Killing Diagnostic Timeouts:**
   - When an agent exceeds its allotted execution deadline (`WaitMinutes` / `timeout_seconds`):
     - The supervisor flags the agent status in `sacl_ops.db` as **`TIMEOUT_RUNNING`**.
     - **The agent process is NEVER automatically killed.**
     - The process is left running in its isolated worktree so the operator can inspect live memory, attached handles, and partial log outputs for post-mortem diagnostics.
   - If forced termination is necessary, the operator invokes the verified manual kill switch script (`stop-agents.ps1`), which validates the PID and process start time before issuing a termination signal.

4. **Inviolable Recovery Rule: Never Blindly Restart RUNNING:**
   - On crash recovery or restart, any job or run discovered in `RUNNING` status is subjected to 4-pillar reconciliation.
   - If the worker process is still alive, supervision is reconnected.
   - If the process is dead and deliverables exist, the run is reconciled to `COMPLETE`.
   - If deliverables are missing, the run is marked `INTERRUPTED` or `FAILED`.
   - Blind re-execution is strictly forbidden.

---

## 3. Consequences

### Positive
- **Elimination of False Success Claims:** Prevents agents from claiming pass verdicts when deliverables are missing, truncated, or structurally invalid.
- **Forensic Integrity:** Eliminates data loss during timeouts; diagnostic logs and stack traces are preserved for developer analysis.
- **Immunity to PID Recycling:** Prevents accidental termination or misattribution of unrelated Windows system processes.
- **Deterministic Gating:** Establishes unambiguous boundaries between automated passes and states requiring human review.
- **Safe Recovery:** Prevents race conditions, corrupted git worktrees, and overwritten deliverables upon reboot.

### Negative / Trade-Offs
- **Resource Footprint on Timeout:** Leaving timed-out processes alive consumes host CPU and memory until human intervention or manual execution of `stop-agents.ps1`.
- **Reconciliation Complexity:** Status evaluation requires multi-file inspection and regex evaluation rather than a simple exit-code check.

---

## 4. Compatibility Notes

- **Legacy Orchestrator Mapping:**
  - Directly reuses and formalizes functions from [`scripts/orchestrator-common.ps1`](file:////workspace/Stable-Ecommerce-Orchestrator/scripts/orchestrator-common.ps1): `Get-ReconciledAgentState`, `Test-AgentProcessRunning`, and `Extract-AgentResult`.
  - Preserves the non-killing timeout behavior established in legacy `RUN-WAVE3.ps1#L65`.
- **Precedence Compliance:**
  - Implements W0.1 Remediation Baseline items 2, 3, and 11.
  - Codified in `docs/STATE_MACHINE.md`, `docs/RECOVERY_MODEL.md`, and `docs/RESULT_PROTOCOL.md`.

# ADR-003: Persistent IDLE Supervisor Daemon (`Graph-P`) with Zero Idle Token Burn

- **Status:** ACCEPTED
- **Date:** 2026-10-07
- **Scope:** SACL V1 Host Daemon & Execution Lifecycle
- **Deciders:** Joaquín (Sovereign Principal), SACL Architecture Lead

---

## 1. Context

A resilient local execution system on Windows requires a persistent host supervisor to coordinate incoming jobs, maintain single-instance process mutual exclusion, manage execution lifecycles, and handle unexpected restarts.

However, many modern autonomous agent frameworks maintain "always-on" generative agent loops or resident LLM daemons. In a local execution environment, an always-on LLM daemon creates critical drawbacks:
1. **Uncontrolled Token Consumption:** Continuously pinging or prompting LLM APIs while waiting for inbound tasks burns costly tokens without generating business value.
2. **Resource Exhaustion & Leaks:** Keeping headless CLI processes (`agy.exe`), Node runtime workers, or browser automation instances resident in memory over days causes memory bloat, socket leakage, and uncollected zombie processes.
3. **Ambiguous Process Boundaries:** Merging background transport listeners, operational state management, and active LLM task execution into a single monolithic loop makes crash diagnosis difficult and increases the attack surface.

Joaquín established explicit architectural boundaries (DECISION_BASELINE items 16, 17, 18):
- Mail Gateway and Graph-P are separate processes.
- Graph-P remains strictly **IDLE** with **no LLM or Antigravity workers running** when idle.
- Graph-H is ephemeral per job, dynamically spawned and cleanly torn down.

---

## 2. Decision

We decide to design and implement **`Graph-P` as a persistent, zero-token background supervisor daemon** that manages execution lifecycles while remaining strictly passive during idle periods:

1. **Zero Idle Token Posture:**
   When no execution jobs are pending or active in `sacl_ops.db`, `Graph-P` enforces a strict Zero Idle Token rule:
   - **Zero LLM Tokens:** No API calls are made to ChatGPT, OpenAI, Anthropic, or Antigravity backends.
   - **Zero Resident Workers:** No instances of `agy.exe`, Node.js child workers, or execution subprocesses remain alive in memory.
   - **Zero Generative Threads:** The process operates strictly as a lightweight, deterministic PowerShell / .NET state machine.

2. **Decoupled Architecture with Pub/Sub Wake Signal:**
   - Mail Gateway operates as a dedicated process monitoring the Google Cloud Pub/Sub pull subscription (derived from Gmail API `users.watch`).
   - The Mail Gateway inserts validated messages and jobs into `mail_messages` and `jobs`.
   - `Graph-P` wakes upon notification or periodic database check to dispatch queued work.

3. **Ephemeral Job Spawning (`Graph-H` Lifecycle):**
   - Upon detecting a validated, queued execution job, `Graph-P` transitions the job to `DISPATCHED`.
   - `Graph-P` spawns an ephemeral Directed Acyclic Graph engine (`Graph-H` / `RUN-WAVE.ps1`) as an isolated child process to execute the wave package.
   - `Graph-P` monitors `Graph-H` progress via SQLite heartbeats and OS process handles, enforcing overall job deadlines and concurrency limits.
   - Upon completion, failure, or blocking of the job, `Graph-H` terminates completely, releasing all child processes, worktrees, and file handles.
   - `Graph-P` seals the run record, notifies the Mail Gateway outbox, and transitions back to `IDLE`.

4. **Crash Recovery & Startup Reconciliation:**
   - Upon boot or restart, `Graph-P` executes stale lock detection and claims the `SUPERVISOR_SINGLETON` lease in `leases` / `supervisor_locks`.
   - `Graph-P` discovers interrupted jobs in `RUNNING`, `DISPATCHED`, or `VERIFYING`.
   - **Inviolable Invariant: Never Blindly Restart Old RUNNING.** `Graph-P` executes 4-point reconciliation: process observation + persisted state + required outputs + final verdict. If workers are dead and deliverables exist, it finalizes the run. If deliverables are missing, it marks the run `INTERRUPTED` or `FAILED`. It never blindly restarts old `RUNNING` tasks.

5. **Operator Control & Safe Stop:**
   - Operators may safely terminate `Graph-P` and running child processes using `stop-agents.ps1`, which validates PIDs and start times via the 3-way check before issuing termination.

---

## 3. Consequences

### Positive
- **Cost Minimization:** 100% elimination of idle token waste. The orchestrator can run 24/7 on the host machine incurring zero LLM billing during idle hours.
- **Host Stability:** Process resources (memory, file locks, threads) are cleanly recycled after every job run, eliminating long-term memory leaks.
- **Deterministic State Separation:** The supervisor lifecycle (`Graph-P`) is cleanly separated from the task execution DAG (`Graph-H`), simplifying troubleshooting and crash recovery.
- **Resilient Recovery:** Interrupted runs are evaluated by evidence rather than corruptive blind re-execution.

### Negative / Trade-Offs
- **Job Startup Latency:** Spawning an ephemeral `Graph-H` execution engine introduces a slight startup overhead (1–3 seconds to initialize worktrees, validate manifests, and spawn workers) compared to pre-warmed resident agent pools.
- **SQLite Polling Overhead:** Periodic SQLite querying introduces minor disk I/O, though negligible under SQLite WAL mode and memory caching.

---

## 4. Compatibility Notes

- **Legacy Orchestrator Mapping:**
  - Modernizes legacy supervisor script [`scripts/run-supervisor.ps1`](file:///C:/Users/Lucilfer/Documents/Stable-Ecommerce-Orchestrator/scripts/run-supervisor.ps1#L94-L119).
  - Replaces brittle WMI queries (`Get-CimInstance Win32_Process`) with transactional SQLite leasing in `leases` and `supervisor_locks`.
  - Preserves compatibility with read-only terminal monitoring via [`MONITOR.ps1`](file:///C:/Users/Lucilfer/Documents/Stable-Ecommerce-Orchestrator/scripts/MONITOR.ps1).
- **Precedence Compliance:**
  - Adheres strictly to DECISION_BASELINE items 16, 17, and 18.
  - Integrates with the state machine defined in `docs/STATE_MACHINE.md` and recovery model in `docs/RECOVERY_MODEL.md`.

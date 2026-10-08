# ADR-008: Structural Process Separation of Mail Gateway and Orchestrator Core (`Graph-P`)

- **Status:** ACCEPTED
- **Date:** 2026-10-07
- **Scope:** SACL V1 Subsystem Topology & Process Architecture
- **Deciders:** Joaquín (Sovereign Principal), SACL Architecture Lead

---

## 1. Context

In architecting an automated loop that connects cloud messaging to local host execution, a fundamental design decision is whether to implement a monolithic service or to separate the transport boundary from the execution core.

The responsibilities of the two domains are fundamentally different:
- **Transport Domain (Mail Gateway):** Operates over external network protocols (Google Cloud Pub/Sub StreamingPull and Gmail REST API over HTTPS/TLS), manages OAuth2 credentials and token lifecycles, listens for Pub/Sub wake signals, queries the Gmail History API with persisted `historyId` cursors, manages automatic `users.watch` lease renewals, extracts attachments, enforces fail-closed Anti-Zip Slip sanitization, dispatches outbound results via Gmail API `users.messages.send` with thread correlation, and persists intake records to SQLite.
- **Orchestration Domain (`Graph-P` / `Graph-H`):** Operates strictly on the local host filesystem and OS processes, manages SQLite transactions, provisions isolated Git worktrees, supervises `agy.exe` child processes, monitors PIDs, detects code collisions, and verifies test deliverables.

If these two domains are merged into a single monolithic process:
1. **Cascading Failure:** A transient network drop, Pub/Sub reconnection timeout, or Google API quota limit could crash the supervisor while critical multi-agent tasks are executing.
2. **Credential Bleed:** Email OAuth2 tokens would exist in the same memory space and environment as the agent process supervisor, increasing the risk of accidental exposure or leakage.
3. **Resource Entanglement:** Network event loops and streaming pull threads would compete with local CPU-intensive compiler, test, and LLM worker threads.
4. **Violation of Least Privilege:** The transport intake would possess execution privileges, blurring security boundaries.

Joaquín established explicit foundational decisions (DECISION_BASELINE item 16, SB-FREEZE-P1-01):
- Mail Gateway and Graph-P must be strictly separate OS processes.
- Gmail is transport, not authority. The local Mail Gateway and Policy Engine authorize.

---

## 2. Decision

We decide to **structurally and process-isolate the Mail Gateway daemon from the `Graph-P` orchestrator daemon**, enforcing a clear architectural and process boundary between them:

```
+-------------------------------------------------------------------------------+
|                            EXTERNAL CLOUD / GMAIL                             |
|                               uniquedraken@gmail.com                          |
+-------------------------------------------------------------------------------+
                                  ^             |
         Gmail API Send (Results) |             | users.watch
         (users.messages.send)    |             v
                                  |    +------------------------+
                                  |    | Google Cloud Pub/Sub   |
                                  |    +------------------------+
                                  |                 |
                                  |                 | StreamingPull (Wake Signal)
                                  |                 v
+-------------------------------------------------------------------------------+
|                             MAIL GATEWAY DAEMON                               |
|   (Standalone OS Process - Edge Transport Boundary - Zero Execution Power)    |
|   - Pub/Sub StreamingPull connection management (Outbound only; NO webhook)   |
|   - Treats Pub/Sub event strictly as WAKE SIGNAL                              |
|   - Queries Gmail History API (users.history.list) with persisted historyId   |
|   - Automatic watch renewal (users.watch) & startup reconciliation            |
|   - Periodic fallback polling (safety degraded mode only)                     |
|   - Sender address whitelisting (uniquedraken@gmail.com)                      |
|   - Attachment download & Zip-Slip path sanitization                          |
|   - Staging to packages/inbox/<runId>/                                        |
|   - Inserts into mail_messages, updates mail_cursors                          |
|   - Monitors mail_outbox and dispatches response ZIPs via Gmail API send      |
+-------------------------------------------------------------------------------+
                                  |             ^
                   Writes Package |             | Reads Results
                   & Cursor       |             |
                                  v             |
+-------------------------------------------------------------------------------+
|                      LOCAL INTER-PROCESS DATA BOUNDARY                        |
|   - SQLite Database (sacl_ops.db): mail_messages, mail_cursors, runs          |
|   - Filesystem Storage: packages/inbox/, artifacts/runs/<runId>/              |
+-------------------------------------------------------------------------------+
                                  |             ^
                     Picks up Job |             | Emits Artifacts
                                  v             |
+-------------------------------------------------------------------------------+
|                             GRAPH-P SUPERVISOR                                |
|       (Standalone OS Process - Execution Coordinator - Zero Mail Network)     |
|   - Enforces singleton instance lease (supervisor_locks)                      |
|   - IDLE when no active jobs (0 LLM tokens, 0 workers)                        |
|   - Spawns ephemeral Graph-H DAG engine upon pending run                      |
|   - Supervises worker lifecycles & monitors SQLite                            |
|   - Registers completion artifacts into mail_outbox                           |
+-------------------------------------------------------------------------------+
```

### Subsystem Boundaries & Invariants:
1. **Mail Gateway Daemon Responsibilities:**
   - Runs as an independent Windows service or background script.
   - Holds transport credentials (OAuth2 tokens) in Windows Credential Manager / DPAPI; credentials are never passed to workers.
   - Enforces sender whitelisting (`uniquedraken@gmail.com`).
   - Receives Pub/Sub wake signals and executes authoritative fetch via Gmail History API using SQLite `historyId`.
   - Manages automatic watch renewal and startup reconciliation.
   - Verifies package checksums and applies fail-closed Zip Slip sanitization.
   - Registers valid packages in `packages/inbox/<runId>/` and inserts records into `mail_messages`.
   - Monitors `mail_outbox` and dispatches reply emails with attached result ZIPs via Gmail API `users.messages.send`.
   - **Prohibition:** Mail Gateway NEVER spawns `agy.exe`, evaluates prompts, or modifies git worktrees.

2. **`Graph-P` Supervisor Daemon Responsibilities:**
   - Runs as an independent process coordinated via `sacl_ops.db`.
   - Maintains the supervisor singleton lease via `supervisor_locks`.
   - Inspects `runs` and `mail_messages` for validated pending jobs.
   - Spawns ephemeral `Graph-H` child processes for DAG execution.
   - **Prohibition:** `Graph-P` has zero access to email credentials and never makes Pub/Sub or Gmail API network calls.

3. **Inter-Process Decoupling:**
   - Communication between the two daemons occurs exclusively via the SQLite database (`sacl_ops.db`) and designated filesystem staging folders.
   - Neither daemon directly invokes or holds OS process handles to the other.

---

## 3. Consequences

### Positive
- **Complete Fault Isolation:** Network disconnections, Pub/Sub channel resets, or Google API quota throttles cannot disrupt active worker tasks or corrupt the local state store. Conversely, worker crashes cannot terminate email listening.
- **Security Boundary:** Antigravity workers running in worktrees have no access to the Mail Gateway process or its email credentials.
- **Independent Lifecycles:** Either daemon can be restarted, upgraded, or stopped independently without affecting the other.
- **Testability:** The Mail Gateway can be tested using mock Pub/Sub and Gmail endpoints, and `Graph-P` can be tested using directly staged packages in `packages/inbox/` without touching real cloud services.

### Negative / Trade-Offs
- **Process Management Overhead:** Operators must monitor and manage two background services on the host instead of a single application.
- **Coordination Latency:** Inter-process coordination via SQLite polling introduces a minor latency (1–5 seconds) between message receipt and job pickup.

---

## 4. Compatibility Notes

- **Legacy Orchestrator Mapping:** Modernizes the legacy architecture where transport was manual and uncoupled from `run-supervisor.ps1`.
- **Precedence Compliance:**
  - Adheres to DECISION_BASELINE item 16.
  - Implements SB-FREEZE-P1-01.
  - Formalized in `docs/ARCHITECTURE.md`, `docs/MAIL_PROTOCOL.md`, and `docs/SECURITY_MODEL.md`.

# ADR-002: SQLite Operational State Store (`sacl_ops.db`)

- **Status:** ACCEPTED
- **Date:** 2026-10-07
- **Scope:** SACL V1 Data Tier & Operational Persistence
- **Deciders:** Joaquín (Sovereign Principal), SACL Architecture & Protocol Leads

---

## 1. Context

In `Stable-Ecommerce-Orchestrator`, operational state was tracked across numerous loose JSON and flat text files distributed throughout the filesystem:
- `state/<agent>.json`: Individual agent process tracking (PID, status, timestamps, commit, report path).
- `results/<runId>/RUN_STATE.json`: Aggregated phase and agent state.
- `RUN_STATUS.json`: Quick-look status file for console monitoring.
- `LATEST_RUN.txt`: Run ID pointer for CLI scripts.

While the legacy orchestrator employed atomic replacement semantics (writing to `.tmp` files before renaming to `.json`), loose file persistence presented significant operational weaknesses as concurrency and agent counts increased:
1. **Lack of ACID Guarantees:** Multi-process coordination between the supervisor, worker processes, and the monitor risked reading partially serialized files during rapid transitions.
2. **Crash Recovery Complexity:** Unclean shutdowns or Windows power interruptions left orphaned `.tmp` files and desynchronized state records across disparate JSON files.
3. **Query Inefficiency:** Evaluating cross-stage dependency readiness, cross-agent file overlap collisions, or historical run metrics required repetitive disk scans and manual JSON parsing in PowerShell.
4. **Brittle Singleton Locking:** The legacy supervisor relied on WMI process queries (`Get-CimInstance Win32_Process`) scraping command-line strings, which is brittle and prone to race conditions under rapid restarts.

Joaquín established explicit foundational decisions (DECISION_BASELINE item 22 and item 24):
- SQLite is designated as the authoritative local Operational State Store (`sacl_ops.db`).
- The Engineering Analytics Warehouse is explicitly deferred to future scope.
- Heavy execution artifacts (logs, diffs, markdown reports) reside strictly on the filesystem.

---

## 2. Decision

We decide to replace loose JSON state files with a local **SQLite database (`sacl_ops.db`)** as the single authoritative Operational State Store for SACL V1:

1. **Database Configuration & Engine Parameters:**
   - **Engine:** SQLite 3 embedded relational database engine.
   - **Journal Mode:** Write-Ahead Logging (`PRAGMA journal_mode = WAL;`) to enable concurrent read transactions during active writes without locking the database.
   - **Durability & Synchronous Mode:** `PRAGMA synchronous = NORMAL;` for high throughput with crash durability.
   - **Integrity Enforcement:** `PRAGMA foreign_keys = ON;` to ensure strict referential integrity across execution runs, stages, and agent tasks.
   - **Busy Timeout:** `PRAGMA busy_timeout = 5000;` (5000ms) to gracefully handle concurrent SQLite access across daemons and parallel workers.
   - **Timestamp Standard:** Strict ISO-8601 UTC across all datetime columns (`YYYY-MM-DDTHH:MM:SSZ`).

2. **16 Canonical Operational Domains Structurally Covered:**
   SACL V1 models its operational state across 16 canonical relational domains:
   - `schema_migrations`: Forward-only migration ledger with cryptographic checksums.
   - `projects`: Multi-project registry decoupling from hardcoded paths.
   - `packages`: Ingested package records, SHA-256 archive hashes, and manifest JSON.
   - `mail_messages` & `mail_cursors`: Gmail API transport queue, Pub/Sub historyId synchronization cursor.
   - `jobs`: Top-level logical jobs governing the mandatory 12-state primary lifecycle and 10 side states.
   - `runs`: Physical execution attempts, directories, and pre-merge integration state.
   - `graph_nodes`: Graph-H ephemeral DAG nodes (9 canonical states).
   - `node_attempts`: Granular per-attempt execution history (PID, exit code, verdicts, log paths).
   - `agents`: Worker process instances, worktree paths, and 4-point reconciled outcomes.
   - `events`: Append-only system and security audit log.
   - `approvals`: Bounded human action-approval contract (`JOB_ID + ACTION + SCOPE + REQUEST_ID + expires_at`).
   - `artifacts`: Relational metadata index for heavy execution artifacts preserved on the filesystem.
   - `results`: Authoritative sealed final execution results and delivery evidence.
   - `leases`: Generalized process mutual exclusion leases replacing brittle WMI queries.
   - `heartbeats`: Daemon and worker process liveness tracking.
   - `errors`: Structured operational error diagnostics repository.

3. **Justified Retention of Compatibility Tables:**
   To guarantee zero regression with existing operational scripts (`run-supervisor.ps1`, `RUN-WAVE.ps1`, `stop-agents.ps1`, `MONITOR.ps1`), eight legacy tables are retained:
   `supervisor_locks`, `dag_stages`, `agent_dependencies`, `file_modifications`, `file_conflicts`, `mail_inbox`, `mail_outbox`, `audit_events`.

4. **Storage Boundary Enforcement:**
   Raw logs (`*.stdout.log`, `*.stderr.log`), deliverable reports (`*.REPORT.md`), full git diffs, patches, and summaries reside strictly on the filesystem under `runs/<runId>/`. SQLite holds only forward-slash normalized relative paths, sizes, and SHA-256 digests.

---

## 3. Consequences

### Positive
- **ACID Transaction Guarantees:** Multi-entity state updates commit atomically; database corruption from mid-write host crashes is eliminated.
- **High Concurrency Performance:** SQLite WAL mode allows simultaneous readers (such as `MONITOR.ps1` and `Graph-P`) while workers commit state updates.
- **Instant Structured Queries:** Calculating stage readiness, detecting file collisions, and summarizing run health become straightforward SQL queries rather than expensive file tree iterations.
- **Deterministic Process Leasing:** Replaces brittle WMI command-line queries with reliable relational leasing and heartbeat tracking.

### Negative / Trade-Offs
- **Dependency on SQLite:** Requires SQLite client binaries (or native PowerShell `.NET` `Microsoft.Data.Sqlite` assemblies) on the host machine.
- **Binary Format:** Operational state cannot be edited directly with a plain text editor; requires SQLite CLI or DB browser tools for manual inspection.

---

## 4. Compatibility Notes

- **Legacy Orchestrator Mapping:** Directly replaces loose state files:
  - `state/<agent>.json` -> `agents` and `node_attempts` tables in `sacl_ops.db`.
  - `results/<runId>/RUN_STATE.json` -> `runs`, `jobs`, and `graph_nodes` tables in `sacl_ops.db`.
  - `run-supervisor.ps1` WMI lease -> `leases` and `supervisor_locks` tables.
- **Precedence Compliance:**
  - Adheres to DECISION_BASELINE items 22, 23, and 24.
  - Implements relational DDL codified in `docs/SQLITE_DATA_MODEL.md` and `db/migrations/001_init.sql`.

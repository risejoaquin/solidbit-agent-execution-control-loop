# ADR-011: Filesystem Retention for Heavy Artifacts and SQLite Metadata Model

- **Status:** ACCEPTED
- **Date:** 2026-10-07
- **Scope:** SACL V1 Data Tier, Storage Hierarchy & Artifact Contracts
- **Deciders:** Joaquín (Sovereign Principal), SACL Architecture & State Persistence Leads

---

## 1. Context

In autonomous multi-agent software engineering workflows, executions generate large volumes of unstructured text and binary artifacts:
- Multi-megabyte raw stdout and stderr process logs from Antigravity CLI workers (`agy.exe`).
- Git diff patches and patch evaluation logs across multiple worktrees.
- Extensive markdown deliverable reports containing technical analysis, code snippets, and verification tables.
- Inbound wave packages and outbound response archives (ZIP files).

A critical architectural decision is where and how to store these artifacts relative to the operational state store (`sacl_ops.db`):
1. **The Anti-Pattern of Storing Heavy Blobs in Relational DBs:** Storing multi-megabyte log files and ZIP packages as `BLOB` or `TEXT` fields inside SQLite causes rapid database bloat, degrades Write-Ahead Log (WAL) checkpoint performance, increases memory usage, and lengthens transaction lock times.
2. **Loss of Native Tooling:** Storing logs in SQLite prevents developers from using native command-line and IDE tools (`Get-Content -Wait`, `Select-String`, `grep`, VS Code, text editors) to inspect logs during live execution.
3. **The Anti-Pattern of Loose JSON Metadata:** Storing all metadata purely on disk in flat files sacrifices transactional ACID safety and fast querying (as resolved in ADR-002).

Joaquín established explicit foundational decisions (DECISION_BASELINE item 23, W0.1 Remediation Baseline item 10, and `ARCHITECTURE_INVARIANTS.json`):
- Heavy artifacts stay strictly in the filesystem (`heavy_artifacts_on_filesystem = true`).
- SQLite manages 16 structured operational state domains.
- Both `SUMMARY.md` and `SUMMARY.json` deliverables are required on disk.

---

## 2. Decision

We decide to adopt a **Hybrid Storage Architecture** partitioning data strictly between the filesystem and SQLite:

1. **Storage Tier Partitioning:**
   - **SQLite (`sacl_ops.db`):** Authoritative home for **lightweight relational metadata, operational lifecycle state, and indexing** across 16 structured domains:
     - `schema_migrations`, `projects`, `packages`, `mail_messages`, `jobs`, `runs`, `graph_nodes`, `node_attempts`, `agents`, `events`, `approvals`, `artifacts`, `results`, `leases`, `heartbeats`, `errors`.
     - Maintains relative disk paths, byte sizes, and SHA-256 integrity checksums of associated filesystem artifacts.
   - **Local Filesystem:** Authoritative home for **all heavy unstructured text, binary streams, and archive files**:
     - Process console outputs, git diff patches, test traces, deliverable report markdowns, and ZIP bundles.

2. **Canonical Run Directory Structure:**
   Artifacts are organized hierarchically under `artifacts/runs/<runId>/`:
   ```
   artifacts/runs/<runId>/
   ├── SUMMARY.md                 # Human-readable executive summary & status table
   ├── SUMMARY.json               # Machine-readable structured universal summary (Schema v1)
   ├── INVOCATION.json            # Immutable invocation record & parameters
   ├── response.zip               # Consolidated outbound result bundle
   ├── evidence/                  # Test output traces, git diffs, human gate artifacts
   │   ├── <agent>.diff
   │   └── FINAL_DEVELOPMENT_AUTHORIZATION.txt
   ├── logs/                      # Raw unedited stdout/stderr logs per worker
   │   ├── <agent>.stdout.log
   │   ├── <agent>.stderr.log
   │   └── supervisor.trace.log
   ├── reports/                   # Final deliverable markdown reports per agent
   │   ├── <agent>.REPORT.md
   │   └── ...
   └── state/                     # Checkpoints & intermediate runtime snapshots
   ```

3. **Dual Summary Contract (`SUMMARY.md` + `SUMMARY.json`):**
   Every completed run must physically produce both:
   - **`SUMMARY.md`:** Formatted GitHub-style markdown presenting executive verdicts, agent execution times, test statistics, and remaining blockers for human consumption.
   - **`SUMMARY.json`:** Canonical JSON document conforming strictly to `schemas/summary.schema.json` containing structured arrays of agent statuses, commit SHAs, deliverable paths, and quality gate results for automated consumption by the Cloud Control Plane.

4. **Verifiable Filesystem-DB Linkage:**
   The SQLite `artifacts` table records relative paths, MIME types, byte sizes, and SHA-256 checksums, enabling reconciliation checks to detect missing or corrupted disk deliverables during the 4-part verification ladder.

---

## 3. Consequences

### Positive
- **Lean Database Footprint:** `sacl_ops.db` remains lean (typically <50 MB), ensuring lightning-fast queries, rapid WAL checkpoints, and zero database bloat.
- **Native Developer Tooling:** Operators can view logs in real time (`Get-Content logs/AG-ARCH.stdout.log -Wait`) and open reports in markdown viewers without SQLite export scripts.
- **Archive Portability:** The entire `artifacts/runs/<runId>/` directory can be compressed into `response.zip` and dispatched directly over Gmail or backed up to cold storage.
- **Dual Deliverables:** Satisfies both human review needs (`SUMMARY.md`) and programmatic parsing needs (`SUMMARY.json`).

### Negative / Trade-Offs
- **Dual-Storage Management:** State deletion or archival requires cleaning up both SQLite database rows and filesystem directories.
- **Dangling Pointer Risk:** If a filesystem directory is deleted manually by a user, SQLite may hold references to missing files; mitigated by reconciliation integrity checks.

---

## 4. Compatibility Notes

- **Legacy Orchestrator Mapping:**
  - Preserves the proven run directory layout used in `Stable-Ecommerce-Orchestrator` (`runs/<runId>/logs/`, `reports/`, `evidence/`).
- **Precedence Compliance:**
  - Directly enforces DECISION_BASELINE item 23.
  - Implements W0.1 Remediation Baseline item 10 and `contracts/ARCHITECTURE_INVARIANTS.json`.
  - Codified in `docs/OBSERVABILITY.md` and `docs/SQLITE_DATA_MODEL.md`.

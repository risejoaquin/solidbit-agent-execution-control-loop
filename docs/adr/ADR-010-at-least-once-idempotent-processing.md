# ADR-010: At-Least-Once Delivery and Idempotent Ingestion Semantics

- **Status:** ACCEPTED
- **Date:** 2026-10-07
- **Scope:** SACL V1 Messaging Protocol, Event Synchronization & Deduplication
- **Deciders:** Joaquín (Sovereign Principal), SACL Protocol Lead

---

## 1. Context

Transporting execution jobs between the Cloud Control Plane and the local Windows host via Gmail API `users.watch`, Google Cloud Pub/Sub, and the Gmail History API introduces distributed systems realities:
- Google Cloud Pub/Sub guarantees **at-least-once delivery**; duplicate wake signal notifications can and will be delivered during network reconnects, subscriber reconnections, or acknowledged message retries.
- The Gmail History API may return message IDs already observed during overlapping query windows.
- Token refresh cycles and network timeouts can cause the Mail Gateway to re-query the same `historyId` range.
- Operators or automated systems might accidentally trigger double submissions, dispatching duplicate wave packages.

In distributed computing, claiming "exactly-once delivery" across network boundaries is a known fallacy; network protocols inherently provide at-most-once or at-least-once delivery. If the orchestrator assumes exactly-once delivery, duplicate arrivals can trigger catastrophic side effects:
1. Double-executing active tasks, causing race conditions in Git worktrees.
2. Overwriting active or completed state in `sacl_ops.db`.
3. Conversely, if duplicate detection is overly aggressive, legitimate operator retries of failed waves could be erroneously blocked.

Constitutional remediation established explicit corrections:
- Delivery semantics are at-least-once. Consumers are idempotent. Under no circumstances does the system claim exactly-once transport.
- Re-delivery of the same Gmail message or Pub/Sub wake signal is idempotently ignored.
- Same `JOB_ID` + same package hash is the same logical job; same `JOB_ID` + different hash is a conflict and is rejected.
- Controlled retry/recovery creates a new attempt while preserving the logical job record.
- The persisted `historyId` cursor in SQLite acts as the monotonic synchronization boundary.

---

## 2. Decision

We decide to formalize **At-Least-Once Delivery semantics with Idempotent Consumer Ingestion** across the SACL V1 transport, event synchronization, and execution layers:

1. **At-Least-Once Transport Contract:**
   - The transport layer guarantees at-least-once delivery.
   - All downstream consumers (Mail Gateway, `Graph-P`, `Graph-H`) are designed to be strictly idempotent.
   - Redelivery of a Pub/Sub wake signal is completely harmless because the Mail Gateway queries the Gmail History API using the locally persisted `historyId` and deduplicates returned messages against SQLite.

2. **Multi-Tiered Deduplication & Conflict Detection:**
   Inbound messages and packages are evaluated at the Mail Gateway boundary against the `mail_messages`, `mail_cursors`, and `runs` tables in `sacl_ops.db`:

   | Inbound Scenario | Condition | System Action | Resulting State |
   | :--- | :--- | :--- | :--- |
   | **Duplicate Redelivery** | Same `JOB_ID` AND identical package SHA-256 hash | Idempotently ignored. The message is marked as processed/seen. No duplicate execution is triggered. | `DUPLICATE_IGNORED` |
   | **Conflicting Resubmission** | Same `JOB_ID` AND *different* package SHA-256 hash | Rejected fail-closed. Flagged as a payload collision conflict. Work is halted; notification reply sent via Gmail API. | `PAYLOAD_CONFLICT_REJECTED` |
   | **Legitimate Retry / Recovery** | Same `JOB_ID` with explicit retry metadata OR new `JOB_ID` | Creates a new attempt record (`attempt_number = attempt_number + 1`) linked to the logical job. Worktree and run folder provisioned cleanly. | `ATTEMPT_STAGED` |
   | **Novel Job** | Unseen `JOB_ID` AND unseen package hash | Staged normally. Registered in `mail_messages` and queued for `Graph-P`. | `ACCEPTED_QUEUED` |

3. **Message-Level Idempotency (`mail_messages` & `mail_cursors`):**
   - The Mail Gateway records the unique Gmail `message_id`, `history_id`, and anti-replay `nonce` in `mail_messages`.
   - A unique constraint `UNIQUE(nonce)` and primary key `message_id` prevent duplicate envelope insertions.
   - The `mail_cursors` table tracks the authoritative `history_id` monotonic high-water mark. Advancing the cursor occurs within an atomic SQLite transaction upon message processing.
   - If an incoming message matches an existing envelope record or package hash, the gateway skips extraction and logs an idempotent skip.

4. **Execution State Idempotency:**
   - `Graph-P` and `Graph-H` state transitions are guarded by atomic SQLite `UPDATE ... WHERE status = ...` queries.
   - Re-running status checks or queries never mutates active run records.

---

## 3. Consequences

### Positive
- **Network Resilience:** Immune to duplicate Pub/Sub wake notifications, Gmail API reconnections, and redelivered emails.
- **Accidental Double-Run Protection:** Prevents duplicate tasks from overwriting active worktree branches or corrupting database tables.
- **Conflict Defense:** Detects and blocks accidental collisions where two different packages share the same `JOB_ID`.
- **Clean Retry Pathway:** Provides a structured, audit-tracked mechanism for retrying failed waves without destroying historical records.
- **Monotonic Cursor State:** The persisted `historyId` guarantees that messages are processed in causal sequence without gaps.

### Negative / Trade-Offs
- **Payload Hashing Requirement:** Every incoming package ZIP must be completely hashed (SHA-256) upon receipt before staging.
- **State Store Dependency:** The Mail Gateway requires access to `sacl_ops.db` to perform deduplication lookups.

---

## 4. Compatibility Notes

- **Legacy Orchestrator Mapping:** Modernizes legacy behavior in `Stable-Ecommerce-Orchestrator`, which had no automated deduplication because transport was manual.
- **Remediation Alignment:**
  - Directly implements SB-FREEZE-P1-01 and W0.1 Remediation Baseline items 8 and 9.
  - Codified in `docs/MAIL_PROTOCOL.md Section 2.4`, `docs/SECURITY_MODEL.md Section 6`, and `schemas/mail-envelope.schema.json`.

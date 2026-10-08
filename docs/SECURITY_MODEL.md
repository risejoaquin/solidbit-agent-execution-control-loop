# SACL V1 Canonical Security Model & Defensive Execution Architecture

**Document Identifier:** `docs/SECURITY_MODEL.md`  
**Status:** CANONICAL ARCHITECTURAL SPECIFICATION (Wave 0.2 Freeze Consistency Remediation)  
**Target Repository:** `risejoaquin/solidbit-agent-execution-control-loop`  
**Precedence Hierarchy:**
1. Explicit Joaquín decisions (`DECISION_BASELINE.md`)
2. Proven current-orchestrator behavior (`Stable-Ecommerce-Orchestrator`)
3. Existing SolidBit governance and contracts (`ARCHITECTURE_INVARIANTS.json`, `manifest.json`)
4. Industry standards for undefined gaps only (never overriding prior decisions)

---

## 1. Security Philosophy & Fundamental Posture

The SolidBit Agent Execution Control Loop (SACL V1) enforces a defense-in-depth security model designed to operate safely on a local developer workstation while accepting asynchronous task packages from a cloud control plane (ChatGPT Web) via email (Gmail).

The architecture rests on five non-negotiable security tenets:
1. **Human Supremacy:** The human developer (Joaquín) is the sovereign principal. Automation has zero self-authorization capability.
2. **Fail-Closed Default:** Any unrecognized input, path traversal anomaly, schema mismatch, unverified state, or local dirty-root conflict halts execution immediately and safely.
3. **Defense-in-Depth:** Security does not rely on a single defensive layer. Prompt constraints, CLI wrappers, filesystem isolation, and policy checks operate redundantly.
4. **Zero Secrets in State:** No credentials, API tokens, or private keys are ever stored in source code, wave manifests, prompt templates, logs, or SQLite databases.
5. **Transport Decoupling & Anti-ACE:** External transport (Gmail) is an untrusted carrier. Zero code or commands are executed directly from email content.

---

## 2. Host Execution Realities & Defense-in-Depth Execution Layers

### 2.1 The Antigravity CLI Host Reality
The Antigravity CLI executable (`agy.exe`) executes directly under the Windows host operating system user context (`Lucilfer`). Therefore:
- **CLI prompt instructions are NOT an OS security boundary.** Textual instructions provided to an LLM cannot prevent low-level file reads, process spawning, or network calls if an agent is prompt-injected or misbehaves.
- The flag `--dangerously-skip-permissions` enables unattended, headless tool execution. It **does not sandbox** process activity; it merely bypasses interactive confirmation prompts.

### 2.2 Multi-Layered Defensive Execution Stack
To mitigate host-level risks, SACL V1 constructs four mandatory defensive layers around every worker invocation:

```
+-----------------------------------------------------------------------------+
|                       DEFENSE-IN-DEPTH EXECUTION LAYERS                     |
+-----------------------------------------------------------------------------+
|                                                                             |
|  [ Layer 1: Caller Acknowledgement Gate ]                                    |
|  Invocation of headless workers requires the explicit parameter             |
|  `-BypassAcknowledged`. Without it, execution aborts immediately with       |
|  error `BYPASS_ACK_REQUIRED`.                                               |
|                                                                             |
|  [ Layer 2: Machine Governance Prompt Guard Header Injection ]              |
|  Prior to passing prompts to `agy.exe`, the worker controller prepends      |
|  immutable machine governance directives into `effective-prompt.txt`:       |
|    GOVERNED_EXECUTION=TRUE                                                  |
|    MERGE=NOT_AUTHORIZED                                                     |
|    DEPLOY=NOT_AUTHORIZED                                                    |
|    DESTRUCTIVE_DB=NOT_AUTHORIZED                                            |
|    CREDENTIAL_MUTATION=NOT_AUTHORIZED                                       |
|    RULESET_MUTATION=NOT_AUTHORIZED                                          |
|    WORKTREE=<worktree_absolute_path>                                        |
|    BRANCH=<branch_name>                                                     |
|    HEAD=<git_commit_sha>                                                    |
|                                                                             |
|  [ Layer 3: File System Worktree Confinement ]                              |
|  Agent worker process CWD is strictly set to its assigned secondary Git     |
|  worktree (`wt-*`). Verification asserts that the worktree is not the       |
|  primary checkout and does not point directly to `.git`.                     |
|                                                                             |
|  [ Layer 4: Output Log Redirection, Audit Capture & Secret Scrubbing ]       |
|  All stdout/stderr streams are redirected to disk files in                  |
|  `runs/<runId>/logs/`, filtered through a secret redaction regex, and        |
|  reconciled in SQLite `sacl_ops.db`.                                        |
|                                                                             |
+-----------------------------------------------------------------------------+
```

### 2.3 Effective-Permission Lattice & Hard Local Denials
In strict adherence to `DECISION_BASELINE.md` §3.3 and `contracts/architecture-invariants.json`, runtime permissions are evaluated through the formal intersection of four distinct authority layers:

$$\text{Effective Permissions} = \text{Hard Local Policy} \cap \text{Project Policy} \cap \text{Package Requested Permissions} \cap \text{Valid Approval Grant}$$

- **Hard Deny Invariant:** Hard deny always wins (`hard_deny_wins = true`). If an action is denied by the Hard Local Policy (`schemas/hard-policy.schema.json`), the effective evaluation is unconditionally **DENIED**, regardless of project policy, package requests, or approval grants.
- **Approval Cannot Override Hard Deny:** An approval grant can only authorize actions within the allowable envelope of hard local policy (`approval_can_override_hard_deny = false`).
- **Hard Deny Prohibitions (V1):** The local host environment permanently denies the following operations in V1:
  1. `remote_production_execution` (Railway, production hosts)
  2. `github_merge` (merging pull requests into `main`)
  3. `production_db_write` (mutating production databases)
  4. `secret_export` (dumping credentials or environment variables)
  5. `arbitrary_remote_code` (executing unvetted scripts from packages)
  6. `main_branch_execution` (running agent tasks on `main`)
  7. `primary_checkout_mutation` (modifying human primary git working tree)
  8. `hard_reset` (`git reset --hard` on primary checkout)
  9. `auto_stash` (`git stash` on uncommitted human changes)
- **Controlled GitHub Write Invariants:** Direct `git push` to `main`, `master`, or release branches is permanently hard denied (`direct_main_push_hard_denied = true`). Merging is hard denied in V1 (`merge_hard_denied_v1 = true`). Feature/task branch push and PR creation can occur only through locally trusted operations when project policy, package request, and valid bounded human approval all allow it; W0.3 itself performs zero GitHub writes.

### 2.4 Bounded Action Approval Contract & Resumption Semantics
In strict adherence to `DECISION_BASELINE.md` §3.5 and `contracts/architecture-invariants.json`:
- **Generic Bounded Binding:** Approval artifacts (`schemas/approval.schema.json`) are strictly bound to the 5-tuple:
  $$\text{Approval Binding} = (\text{job\_id}, \text{action}, \text{scope}, \text{request\_id}, \text{expires\_at})$$
- **Same Logical Run Resumption:** When a valid approval artifact matching `(job_id, action, scope, request_id)` is submitted before `expires_at`, SACL resumes the **same logical run**. It does not spawn a new disconnected run or re-execute completed stages.
- **Fail-Closed on Mismatch or Expiration:** Expired approvals, mismatched scopes, or unauthorized actions fail closed immediately into `POLICY_DENIED` or `BLOCKED`.

---

## 3. Secure Secret & Credential Architecture

### 3.1 Policy: Zero Secrets in Source and State
1. **Repository Ban:** No API tokens, SSH keys, passwords, client secrets, or personal access tokens (PATs) shall ever be committed to the SACL repository, wave packages, prompt templates, or configuration files.
2. **Database Ban:** The SQLite Operational State Store (`sacl_ops.db`) is strictly designated for operational execution state (PIDs, statuses, hashes, timestamps, exit codes). Credential values are strictly forbidden from being stored in SQLite tables.
3. **Log Sanitization Filter:** A streaming redaction filter inspects stdout/stderr streams before writing to disk, replacing sensitive tokens (`ghp_[a-zA-Z0-9]{36}`, `gho_[a-zA-Z0-9]{36}`, Google API keys, Railway tokens, and Authorization headers) with `[REDACTED_SECRET]`.

### 3.2 Host Credential Storage
- **Transport Credentials:** Gmail OAuth2 client secrets and refresh tokens used by the local Mail Gateway must be stored securely using the **Windows Credential Manager** or protected via **Windows Data Protection API (DPAPI)**.
- **Process Scope Injection:** Credentials required for specific build or test tools are never exported to system-wide environment variables. They are injected ephemerally into the child process scope only if strictly required and declared in `manifest.json`.

---

## 4. Wave Package Delivery, Trust & Integrity Architecture

### 4.1 Secretless Control Plane Posture (ADR-014 Alignment)
In early drafts, HMAC-SHA256 signing of wave packages by ChatGPT Web was proposed. However, under constitutional remediation:
- **ChatGPT Web MUST NOT possess a long-lived HMAC or private signing key.** Ingesting long-lived cryptographic secrets into interactive web LLM sessions introduces unacceptable credential exposure risks and operational fragility.
- **Package HMAC signing is deferred** until a dedicated, cryptographically isolated signer or key-custody component exists.

### 4.2 V1 Trust Foundation
In SACL V1, package authenticity and execution trust are established through six interlocking controls:
1. **Authenticated Transport Identity:** The local Mail Gateway establishes event-driven ingress via Gmail API `users.watch` and Google Cloud Pub/Sub, subscribing via outbound Pull/StreamingPull, and connects to the Gmail REST API via OAuth2 over TLS (App Passwords removed; unread state is never the source of truth and must not be a gating input). No public inbound webhooks or listening ports are exposed on the host workstation. Pub/Sub notifications serve strictly as untrusted wake signals; authoritative message contents and attachments are fetched via the Gmail History API (`users.history.list`) using the locally persisted `historyId` cursor. Only messages originating from authorized, authenticated sender accounts (specifically `uniquedraken@gmail.com`, supporting the approved self-mail pattern) are processed.
2. **Strict Message & Schema Validation:** Incoming emails must match the canonical routing hint syntax (`[SACL][JOB][v1][<JOB_ID>]`). Attached packages must strictly conform to `manifest.json` schema (`solidbit.execution-package.v1`).
3. **SHA-256 Package Integrity Tracking:** The SHA-256 hash of every incoming archive is computed immediately upon download and recorded in `mail_messages` and `runs` tables before extraction.
4. **At-Least-Once Delivery & Idempotency:** Re-delivery of an identical package (`same JOB_ID` + `same SHA-256`) is idempotently recognized and ignored without spawning duplicate runs. Conflicting packages (`same JOB_ID` + `different SHA-256`) are rejected with an explicit conflict alert.
5. **Local Policy Engine & Dirty-Root Preflight:** The local orchestrator verifies all tooling, validates repository safety, and enforces the local dirty-root rule before any worker is spawned.
6. **Local Kill Switch & Human Approval:** Irreversible actions remain strictly gated behind human verification.

### 4.3 Archive Extraction Security Pipeline (Anti-Zip Slip & Resource Defense)
Because packages arrive as compressed ZIP archives from external transport, the extraction pipeline enforces rigorous multi-stage defenses:

```
+-----------------------------------------------------------------------------+
|                      ZIP EXTRACTION DEFENSE PIPELINE                        |
+-----------------------------------------------------------------------------+
|                                                                             |
|   INCOMING WAVE ZIP                                                         |
|         |                                                                   |
|         v                                                                   |
|   [ Step 1: Resource Exhaustion (Zip Bomb) Quotas ]                         |
|   - Maximum compressed archive size: 25 MB                                  |
|   - Maximum uncompressed extraction size: 100 MB                            |
|   - Maximum total file count: 1,000 files                                   |
|   - Maximum compression ratio: 20:1 (Uncompressed / Compressed)             |
|   Violation -> Reject with `ZIP_RESOURCE_LIMIT_EXCEEDED`                     |
|         |                                                                   |
|         v                                                                   |
|   [ Step 2: Canonical Path Sanitization (Anti-Zip Slip) ]                   |
|   - TargetCanonical = Path.GetFullPath(DestinationDirectory)                |
|   - For each entry: EntryCanonical = Path.GetFullPath(Target + entry.FullName)|
|   - Assert: EntryCanonical.StartsWith(TargetCanonical + DirectorySeparator) |
|   - Reject if entry name contains `..` or absolute drive root (`C:\`)       |
|   Violation -> Reject with `ZIP_PATH_TRAVERSAL_DETECTED`                    |
|         |                                                                   |
|         v                                                                   |
|   [ Step 3: Windows Reserved Device Names & ADS Defense ]                   |
|   - Reject files matching DOS device names: CON, PRN, AUX, NUL, COM1-9,     |
|     LPT1-9 (case-insensitive, with or without extensions).                  |
|   - Reject Alternate Data Streams containing colons (`filename:stream`).    |
|   Violation -> Reject with `INVALID_FILENAME_CHARACTER`                     |
|         |                                                                   |
|         v                                                                   |
|   [ Step 4: Symlink, Hardlink & Reparse Point Rejection ]                   |
|   - Any zip entry with Unix symlink attributes or reparse point flags is    |
|     quarantined and rejected to prevent arbitrary filesystem redirection.   |
|   Violation -> Reject with `SYMLINK_NOT_PERMITTED`                          |
|         |                                                                   |
|         v                                                                   |
|   EXTRACT TO ISOLATED STAGING DIRECTORY: `packages/inbox/<runId>/`          |
|                                                                             |
+-----------------------------------------------------------------------------+
```

---

## 5. Mail Transport Security & Prevention of Arbitrary Code Execution (Anti-ACE)

The integration of Gmail (`uniquedraken@gmail.com`) introduces an external network interface. To guarantee that email transport cannot be leveraged to achieve arbitrary code execution on the Windows host, the following safeguards are mandatory:

1. **Sender Whitelisting:**
   - Only emails from authenticated, authorized sender addresses (specifically `uniquedraken@gmail.com`, supporting the approved self-mail workflow) are accepted.
   - Unrecognized senders are rejected or quarantined without processing.
2. **Subject Line is a Routing Hint Only:**
   - The canonical email subject format is:
     ```
     [SACL][JOB][v1][<JOB_ID>]
     ```
   - **The subject line is strictly a routing hint** used for mailbox filtering and thread matching. It is **never an authority source**. Authoritative project references, execution modes, agent dependencies, and permissions live exclusively in the validated `manifest.json`.
3. **Zero Execution from Email Body or Headers:**
   - The email body (HTML or plain text) is treated strictly as unparsed metadata or optional human notes.
   - **No PowerShell, batch script, command line, or shell expression is ever evaluated, piped, or invoked from email content.**
4. **Decoupled Architecture (Mail Gateway vs Orchestration Engines):**
   - The Mail Gateway runs as an unprivileged ingestion service. It listens to Google Cloud Pub/Sub pull notifications, fetches authoritative changes via the Gmail History API using persisted `historyId`, verifies archive integrity, writes validated packages to disk, and inserts records into SQLite `sacl_ops.db`. Outbound replies are sent directly via the Gmail REST API (`users.messages.send`) with thread continuation.
   - The Mail Gateway **never invokes Antigravity CLI and never executes agent tasks**.
   - Execution is triggered solely by the local persistent coordinator (`Graph-P`) after internal preflight policy validation.
5. **Fixed Outbound Recipient Whitelist:**
   - Outbound reply emails containing execution summaries (`SUMMARY.md`) and deliverable archives (`RESPONSE_<runId>.zip`) are strictly restricted to the authorized destination (`uniquedraken@gmail.com`). Dynamic recipient addresses extracted from payload content are forbidden.
6. **Zero Inbound Attack Surface:**
   - The host workstation establishes only outbound TLS connections (to Google Cloud Pub/Sub and Google API endpoints). Zero inbound listening ports, public webhooks, or tunnel services are opened.

---

## 6. Replay & Idempotency Controls

To protect against duplicate processing caused by email retries, network glitches, or duplicate submissions, SACL V1 enforces end-to-end idempotency:

```
+-----------------------------------------------------------------------------+
|                      IDEMPOTENCY & REPLAY CONTROLS                          |
+-----------------------------------------------------------------------------+
|                                                                             |
|   1. Immutable Run Identifier:                                              |
|      Every execution receives a cryptographically unique run identifier:    |
|        RunId = "w0-" + UtcTimestamp("yyyyMMdd-HHmmss") + "-" + HexEntropy(6)|
|                                                                             |
|   2. SQLite Message Deduplication Registry:                                 |
|      The `sacl_ops.db` maintains tracking tables:                           |
|        - `mail_messages`: tracks `message_id`, `history_id`, `nonce`,       |
|          `attachment_sha`, and `status`                                     |
|        - `mail_cursors`: tracks latest synchronized `history_id` cursor     |
|        - `runs`: tracks `run_id`, `package_id`, `status`, `started_at`       |
|                                                                             |
|   3. Deterministic Ingestion Handling:                                      |
|      - Same Message-ID or (Same JOB_ID + Same SHA-256):                     |
|        Idempotently ignored. No duplicate execution is spawned.              |
|      - Same JOB_ID + Different SHA-256:                                     |
|        Flagged as CONFLICT (`JOB_ID_HASH_MISMATCH`). Execution is refused.  |
|      - New JOB_ID or valid retry nonce:                                     |
|        Enqueued as a new run attempt, preserving historical records.        |
|                                                                             |
|   4. Monotonic State Transition Engine:                                     |
|      Jobs transition linearly through finite states:                        |
|        RECEIVED -> AUTHENTICATED -> VALIDATED -> PERSISTED -> QUEUED ->     |
|        DISPATCHED -> RUNNING -> VERIFYING -> RESULT_PACKAGED ->             |
|        RESULT_SENT -> COMPLETED -> ARCHIVED                                 |
|      State reversals are rejected by transactional constraints.             |
|                                                                             |
+-----------------------------------------------------------------------------+
```

---

## 7. Local Kill Switch & Process Supervisor Security

### 7.1 Supervisor Singleton Mutex & SQLite Lease
To eliminate race conditions and prevent concurrent orchestrator conflicts, SACL V1 enforces a local singleton lock:
- An OS-level named mutex (`Global\SACL_Supervisor_Instance_Lock`) combined with an active lease row in `supervisor_locks` in `sacl_ops.db`.
- If an active supervisor process holds the lock, any secondary launch attempt exits immediately with code `409 Conflict`.
- Stale leases are reclaimed only after verifying that the recorded PID is dead via OS process inspection.

### 7.2 PID Verification & Anti-Recycling Safe Stop Algorithm
When stopping agents or terminating runaway workers via `scripts/stop-agents.ps1`, the supervisor executes the **Anti-Recycling Safe Stop Algorithm**:

```
Algorithm: SafeProcessStop
Inputs: TargetAgentId, StoredState (PID, StartedAt, Status)

1. Query OS for running process with Id = StoredState.PID.
2. If process does not exist:
     Update state status to "STOPPED". Return SUCCESS.
3. Validate Process Name:
     AllowedNames = {"agy", "powershell", "pwsh", "cmd", "node", "conhost"}
     If Process.ProcessName does not match AllowedNames:
       REFUSE KILL: "PID belongs to unrelated system process. Aborting kill."
       Exit with SAFETY_REFUSAL.
4. Validate Process Start Time (Anti-Recycling Protection):
     Discrepancy = |Process.StartTime - StoredState.StartedAt|
     If Discrepancy > 300 seconds:
       REFUSE KILL: "Process start time mismatch. PID recycling suspected."
       Exit with SAFETY_REFUSAL.
5. Execute Controlled Termination:
     Stop-Process -Id StoredState.PID -Force
     Record state transition to "STOPPED" in SQLite database.
```

### 7.3 Non-Killing Diagnostic Timeout Invariant
Preserving the proven operational invariant from `Stable-Ecommerce-Orchestrator`:
- When an agent worker exceeds its allocated timeout (`WaitMinutes`), the supervisor **does NOT kill the process automatically**.
- Worker status transitions to `TIMEOUT_RUNNING`.
- Downstream dependent DAG stages are blocked (`READY_FOR_INTEGRATION=NO`).
- The running process is left alive for developer inspection, memory inspection, and log analysis.
- Forced termination is executed only when explicitly commanded by the human operator.

---

## 8. Fail-Closed Policy & Tamper-Evident Audit Trail

### 8.1 Fail-Closed Decision Matrix
| Failure Condition | Action Taken | Final Status |
| :--- | :--- | :--- |
| Preflight CLI missing (`git`, `gh`, `agy`) | Abort run before spawning any processes | `FAILED_PREFLIGHT` |
| Primary product repo dirty | Refuse worktree creation / branch checkout | `BLOCKED_DIRTY_ROOT` |
| Target branch is `main` or `master` | Abort immediately; refuse launch | `BLOCKED_MAIN_PROHIBITED` |
| Target is primary checkout (`.git`) | Abort immediately; refuse launch | `BLOCKED_CHECKOUT_PROHIBITED` |
| File overlap between agents | Block wave completion; refuse integration | `BLOCKED_FILE_COLLISION` |
| Zip Slip path traversal detected | Terminate extraction; quarantine archive | `REJECTED_TRAVERSAL_FAIL` |
| Zip bomb resource quota exceeded | Terminate extraction; delete partial temp files | `REJECTED_RESOURCE_QUOTA` |
| Conflicting package hash for same JobId | Reject package; emit conflict notification | `REJECTED_HASH_CONFLICT` |
| Agent process exit code non-zero | Capture logs; do not schedule dependent tasks | `FAILED` |
| Agent deliverable missing or empty | Mark deliverable invalid; block integration | `FAILED_INVALID_DELIVERABLE` |

### 8.2 Tamper-Evident Audit Trail
Every SACL V1 run produces an immutable, forensic audit record:
1. **SQLite Operational Log (`sacl_ops.db`):** Every state transition, PID, start/finish timestamp, exit code, and error text is recorded via ACID transactions in `runs`, `agents`, `events`, and `mail_messages`.
2. **Effective Prompt Artifact (`effective-prompt.txt`):** The exact prompt passed to the CLI, including prepended machine governance guard headers, is preserved.
3. **Execution Manifest (`INVOCATION.json`):** Records git commit SHA, branch, worktree path, invocation timestamp, CLI arguments, and bypass acknowledgement.
4. **Summary Deliverables:** Both human-readable `SUMMARY.md` and machine-readable `SUMMARY.json` are generated in `runs/<runId>/`.
5. **Disk Logs:** Stderr and stdout logs are captured and preserved in `runs/<runId>/logs/`.

---

## 9. Comprehensive Threat Mitigation & Verification Matrix

| Threat ID | STRIDE Category | Asset Affected | Risk Rating | Countermeasure / Security Control | Verification Test Procedure |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TH-01** | Spoofing | Mail Gateway | **High** | Authenticated Pub/Sub pull + Gmail API OAuth2/TLS + sender whitelist (`uniquedraken@gmail.com`) + `historyId` sync + schema validation | Ingest email from unauthorized sender; assert ignored/quarantined. |
| **TH-02** | Spoofing | Result Protocol | **Medium** | Multi-dimensional reconciliation: regex marker + physical report file + exit code 0 | Inject report with fake marker but missing file; assert QA blocks. |
| **TH-03** | Spoofing | Host Processes | **High** | SafeProcessStop: process name whitelist + 300s StartTime match check | Attempt to stop recycled PID with mismatched start time; assert `SAFETY_REFUSAL`. |
| **TH-04** | Tampering | File System | **Critical** | Anti-Zip Slip canonical path sanitization (`Path.GetFullPath` prefix match) | Extract test archive containing `../../evil.bat`; assert `ZIP_PATH_TRAVERSAL_DETECTED`. |
| **TH-05** | Tampering | Agent Execution | **High** | Machine governance prompt guard header injection (`effective-prompt.txt`) | Inspect `effective-prompt.txt`; assert guard headers prepended. |
| **TH-06** | Tampering | Primary Repo | **Critical** | Local Dirty-Root Rule + `PRIMARY_CHECKOUT_NOT_ALLOWED` | Attempt run on dirty primary repo; assert immediate `BLOCKED_DIRTY_ROOT`. |
| **TH-07** | Tampering | Worktrees | **Medium** | Cross-agent file collision check (`git diff --name-only origin/main...HEAD`) | Simulate two agents editing same file; assert `READY_FOR_INTEGRATION=NO`. |
| **TH-08** | Repudiation | Operational State | **Medium** | ACID SQLite state logging + immutable `INVOCATION.json` | Verify `sacl_ops.db` and invocation metadata after mock execution. |
| **TH-09** | Info Disclosure | Deliverables / Logs | **High** | Streaming regex token masking on stdout/stderr + zero secrets policy | Inject mock token into worker output; assert masked as `[REDACTED_SECRET]`. |
| **TH-10** | Info Disclosure | Source Code | **High** | Fixed outbound email recipient whitelist (`uniquedraken@gmail.com`) via Gmail API send | Attempt outbound email to arbitrary external address; assert blocked. |
| **TH-11** | Denial of Service | Disk Storage | **High** | Zip decompression resource quotas (25MB archive / 100MB uncompressed / 1000 files) | Extract archive expanding beyond 100MB; assert `ZIP_RESOURCE_LIMIT_EXCEEDED`. |
| **TH-12** | Denial of Service | Host CPU/RAM | **High** | Concurrency limits (`$MaxParallel`) + non-killing timeout (`TIMEOUT_RUNNING`) | Simulate hung worker; assert transitions to `TIMEOUT_RUNNING` without auto-kill. |
| **TH-13** | Elevation of Priv | Main Branch | **Critical** | `MAIN_BRANCH_NOT_ALLOWED` + Human Action Gate | Configure agent targeting `main`; assert immediate preflight abort. |
| **TH-14** | Elevation of Priv | Cloud Infrastructure | **Critical** | Remote production execution disabled in V1 (Dry-run plan generation only) | Invoke remote mutation script; assert fail-closed abort or dry-run plan emission. |

---

## 10. Residual Risk & Future Hardening Roadmap

1. **Host Sandboxing (Wave 2+):** Antigravity CLI currently executes in the host user context. Future waves will evaluate lightweight Hyper-V containers or Windows Sandbox microVMs to establish a true OS kernel boundary around headless LLM execution.
2. **Dedicated Signer / Key Custody (Wave 2+):** When an out-of-band signing component or local hardware key is introduced, cryptographic package signing (HMAC-SHA256 or asymmetric Ed25519) will be activated for end-to-end package attestation.
3. **Production Deployment Gating (Post-V1):** When remote production execution is revisited in future major versions, multi-party cryptographic authorization and cloud credential brokering will be formally specified.

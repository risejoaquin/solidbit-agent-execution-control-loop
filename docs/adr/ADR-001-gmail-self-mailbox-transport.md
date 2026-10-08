# ADR-001: Gmail Self-Mailbox Transport via Gmail API and Cloud Pub/Sub Pull for Asynchronous Control Loop

- **Status:** ACCEPTED
- **Date:** 2026-10-07
- **Scope:** SACL V1 Transport Layer & Ingress Architecture
- **Deciders:** Joaquín (Sovereign Principal), SACL Architecture & Protocol Leads

---

## 1. Context

The SolidBit Agent Execution Control Loop (SACL V1) requires an asynchronous, resilient, and secure communication channel between the Cloud Control Plane (ChatGPT Web sessions where the human operator plans, supervises, and authors execution packages) and the local Windows execution host (`solidbit-agent-execution-control-loop`).

In the legacy workflow (`Stable-Ecommerce-Orchestrator`), interactions between ChatGPT Web and the local host were entirely manual:
1. The operator downloaded ZIP packages manually from chat conversations into their local `Downloads` directory.
2. The operator extracted files, ran PowerShell scripts manually in a terminal, and waited for execution.
3. The operator manually copied `SUMMARY.md` text and report excerpts back into ChatGPT Web.

To automate this control loop without compromising workstation security, an automated transport mechanism is needed. However, opening direct inbound network endpoints on the local Windows machine (such as HTTP webhooks, public REST APIs, or SSH ingress ports) introduces unacceptable security risks:
- Local developer workstations reside behind corporate firewalls, NAT routers, or dynamic residential IPs where port forwarding is fragile or impossible.
- Exposing a listening socket on the host creates a permanent external attack surface.
- Direct synchronous RPC tightly couples the availability and lifecycle of the local host to the web browser session.

Joaquín established explicit foundational decisions (DECISION_BASELINE items 12, 13, 14, 15, and SB-FREEZE-P1-01):
- ChatGPT Web acts as the Control Plane.
- Gmail acts as the asynchronous cloud/local message and package transport.
- Self-mail (sending from and to the same mailbox) is explicitly permitted.
- The designated transport mailbox is `uniquedraken@gmail.com`.
- Gmail credentials and Antigravity CLI identities are completely independent.
- Gmail API `users.watch` -> Google Cloud Pub/Sub -> local Pull/StreamingPull subscriber is the selected event-driven ingress architecture.
- No public inbound webhooks.
- Pub/Sub notification is strictly a wake signal, not the source of truth.
- Authoritative state is fetched via Gmail History API using a persisted `historyId` cursor.
- Gmail watch must renew automatically.
- Startup reconciliation must resume from persisted `historyId`.
- Periodic direct polling exists only as degraded safety reconciliation / fallback.
- Outbound results dispatch must use the Gmail REST API (`users.messages.send`) with thread continuation, eliminating any need for SMTP in V1.
- ChatGPT Web must not possess HMAC secrets or private signing keys.

---

## 2. Decision

We decide to adopt **Gmail (`uniquedraken@gmail.com`) via Gmail API and Google Cloud Pub/Sub Pull** as the asynchronous cloud-to-local transport layer for SACL V1:

1. **Transport Topology & Protocols:**
   - **Outbound-Only Local Connectivity:** The local host connects strictly outbound over TLS. Zero inbound listening ports, public webhooks, or reverse tunnels are opened on the host.
   - **Event-Driven Ingress:**
     - The Mail Gateway registers for mailbox notifications via `POST /users/me/watch` specifying a Google Cloud Pub/Sub topic.
     - Gmail publishes mailbox update notifications to Google Cloud Pub/Sub.
     - The local Mail Gateway connects to the Pub/Sub subscription via an outbound **Pull / StreamingPull** subscriber.
     - The Pub/Sub message contains `{ "emailAddress": "...", "historyId": "..." }` and acts strictly as an **untrusted wake signal**.
   - **Authoritative Change Retrieval:**
     - Upon receiving the wake signal, the Mail Gateway queries the **Gmail History API (`users.history.list`)** starting from the locally persisted `historyId` cursor in SQLite `sacl_ops.db` (`mail_cursors`).
     - Message metadata and package ZIP attachments are retrieved via the Gmail REST API (`users.messages.get` and `users.messages.attachments.get`).
   - **Watch Renewal & Lifecycle Management:**
     - The Gmail watch lease (~7 days) is automatically renewed before expiration by a background gateway scheduler task.
   - **Startup & Fallback Reconciliation:**
     - On daemon startup, the gateway performs startup reconciliation from the persisted `historyId`.
     - Periodic direct polling is retained strictly as a safety reconciliation and degraded fallback mechanism (e.g. if Pub/Sub is unreachable), never as the primary source of truth.
   - **Outbound Results Dispatch (Zero SMTP in V1):**
     - Execution summaries and response archives are dispatched directly via **Gmail REST API (`users.messages.send`)**.
     - Message threading is maintained using Gmail API `threadId` and RFC 2822 headers (`In-Reply-To`, `References`).
     - SMTP is completely omitted from the V1 transport architecture.
   - **Self-Mailbox Pattern:**
     - Ingestion explicitly accepts and supports self-mail messages (`From: uniquedraken@gmail.com` to `To: uniquedraken@gmail.com`).

2. **Decoupled Identity & Credentials:**
   - Transport authentication uses Google OAuth2 refresh tokens and client credentials stored securely in Windows Credential Manager or DPAPI.
   - Antigravity CLI (`agy.exe`) workers and LLM processes have zero access to Gmail credentials or OAuth tokens.

3. **Message Framing & Routing Hints:**
   - Standard subject format: `[SACL][JOB][v1][<JOB_ID>]`.
   - The email subject is strictly a **routing hint** for filtering transport messages.
   - The email subject **NEVER** acts as an authority source for target repositories, permissions, or execution modes. All authoritative parameters reside inside the hermetic, validated package manifest (`manifest.json`).

4. **Payload Encapsulation & Integrity:**
   - Work items arrive exclusively as self-contained ZIP archive attachments conforming to `EXECUTION_PACKAGE_SPEC.md` (max 25 MB).
   - Email message body text is never evaluated or executed as shell commands.
   - Attachment SHA-256 integrity is computed upon receipt and recorded in SQLite before extraction.

---

## 3. Consequences

### Positive
- **Zero Inbound Attack Surface:** Eliminates exposed open ports, public URLs, reverse proxies, and webhook authentication vulnerabilities on the local Windows host.
- **Low-Latency Push-Like Wake:** Google Cloud Pub/Sub StreamingPull provides sub-second wake latency upon message delivery without aggressive continuous polling.
- **Monotonic, Gapless Synchronization:** The Gmail History API and persisted `historyId` cursor ensure gapless message intake across daemon restarts, transient disconnections, and system reboots.
- **Elimination of SMTP Complexity:** Using Gmail API `users.messages.send` eliminates SMTP TLS handshake issues, SMTP port blocking by ISPs (ports 25/465/587), and separate SMTP credentials.
- **Firewall & NAT Traversal:** Operates reliably across any standard outbound Internet connection without router modifications.
- **Native Audit Trail:** The Gmail mailbox provides an external, timestamped, permanent log of inbound waves and outbound execution summaries.

### Negative / Trade-Offs
- **Cloud Infrastructure Dependency:** Requires a Google Cloud Project with the Gmail API and Cloud Pub/Sub API enabled, including Pub/Sub topic and pull subscription resources.
- **OAuth2 Token Lifecycle:** Requires managing OAuth2 refresh tokens and handling periodic token refresh flows.
- **Attachment Quotas:** Gmail enforces a 25 MB message limit. Execution packages and result bundles must fit within these bounds.

---

## 4. Compatibility Notes

- **Legacy Orchestrator Mapping:** Directly replaces the manual download, extraction, and copy-paste steps documented in `Stable-Ecommerce-Orchestrator` (`README.md#L12-L21`).
- **Remediation Alignment:** Resolves finding **SB-FREEZE-P1-01** from `DIRECT_HUMAN_AUDIT_FINDINGS.md` by fully restoring the selected `users.watch` + Pub/Sub Pull + Gmail History API architecture.
- **Precedence Compliance:**
  - Adheres to DECISION_BASELINE items 12, 13, 14, 15, and 16.
  - Codified in `docs/MAIL_PROTOCOL.md`, `docs/SECURITY_MODEL.md`, and `docs/THREAT_MODEL.md`.

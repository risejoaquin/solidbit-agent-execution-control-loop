# Changelog

All notable changes to the **SolidBit Agent Execution Control Loop (SACL)** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Real-time Technical Mission Control Bar in `CenterDashboard.tsx` with direct subprocess triggers:
  - `▶ Lanzar Oleada Kahn` (`POST /api/actions/execute` -> `campaign_sprint`)
  - `▶ Correr Pytest (QA)` (`POST /api/actions/execute` -> `test_suite`)
  - `▶ Auditar Invariantes` (`POST /api/actions/execute` -> `security_audit`)
- Real Agent Fleet Process Table (`AgentFleetProcessTable.tsx`) showing active OS PIDs, isolated Git worktrees, live commands, and dynamic execution badges (`IDLE`, `RUNNING`, `COMPLETED`, `WAITING_GATE`).
- Fully automated GitHub Actions CI/CD workflows (`.github/workflows/ci.yml`, `quality.yml`).
- SolidBit SDLC Governance specifications including `.github/CODEOWNERS` and structured Pull Request templates.
- Industry-standard repository assets: `LICENSE` (Apache 2.0), `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`.

### Changed
- Refactored `LogTerminal.tsx` auto-scroll to confine viewport scrolling internally, preventing unwanted parent browser jumping.
- Upgraded test suite coverage to **31/31 passing unit, module, and integration tests** (100% PASS).
- Hardened responsive layout for ultra-wide, desktop, tablet, and mobile displays (390px, 768px, 1280px+).

---

## [1.2.0] - 2026-10-25

### Added
- Executive OLED HUD (#000000) with dark pitch theme and high-contrast typography.
- Antigravity AI Engine (`agy.exe`) local inference daemon and SSE stream integration.
- Human-in-the-Loop (HITL) gate authorization with HMAC-SHA256 signature verification.
- Bi-directional Resend Email Gateway with one-click cryptographic decision links.
- Multi-project workspace switcher supporting `Stable-Ecommerce`, `SolidPOS`, and `FULL-METAL-CASH`.

### Security
- Enforced hard-deny invariants: `DR-INV-001` (Sellable Unit ledger), `DR-PAY-001` (Payment transaction atomicity), and `DR-IDEM-001` (Mutating idempotency key guard).

---

## [1.0.0] - 2026-10-07

### Added
- Initial release of SACL V1 Core Control Loop.
- SQLite WAL operational state store (`sacl_ops.db`) with 16 ACID relational tables.
- Topological DAG wave execution scheduler using Kahn's algorithm.
- Git worktree lifecycle manager enforcing the Dirty-Root Rule.

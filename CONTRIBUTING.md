# Contributing to SACL (SolidBit Agent Execution Control Loop)

Thank you for your interest in contributing to **SACL**! As a mission-critical control plane for autonomous AI coding agents, our codebase enforces strict quality, security, and governance standards.

---

## 🏛️ Guiding Engineering Principles

1. **The Dirty-Root Rule:** Never execute agent-generated code or untracked experiments directly in the root repository. Always allocate an isolated Git worktree (`git worktree add`).
2. **Zero-Mock Policy:** Never replace real integration tests or system calls with artificial mock data. Test outputs must reflect genuine operating system exit codes and SQLite WAL states.
3. **Frozen Contract Preservation:** Never alter or bypass frozen contracts (`DR-INV-001`, `DR-PAY-001`, `DR-IDEM-001`, `DR-AUTH-001`, `DR-ERR-001`, `DR-REC-001`). If a test fails against a contract, fix the implementation—never weaken the contract.

---

## 🛠️ Development Setup

### Prerequisites
- **Python 3.11+**
- **Node.js 20+** and **npm**
- **Git 2.40+**

### 1. Clone & Set Up Python Environment
```bash
git clone https://github.com/risejoaquin/solidbit-agent-execution-control-loop.git
cd solidbit-agent-execution-control-loop

python -m venv .venv
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On POSIX (bash/zsh):
source .venv/bin/activate

pip install -e ".[dev]"
```

### 2. Set Up Frontend Web Console
```bash
cd apps/web
npm install
npm run build
cd ../..
```

### 3. Run the Test Suite
```bash
# On Windows:
$env:PYTHONPATH = "src"
pytest tests/ui/ -v

# On POSIX:
export PYTHONPATH="src"
pytest tests/ui/ -v
```

---

## 🌿 Branching & Git Workflow

- **Branch Naming Conventions:**
  - `feat/<ticket-or-description>`: New capabilities or modules.
  - `fix/<ticket-or-description>`: Bug fixes and defect resolutions.
  - `chore/<description>`: Tooling, dependencies, or CI updates.
  - `sacl-implementation-<id>`: Ephemeral campaign execution worktrees.
- **Commit Messages:** Follow [Conventional Commits](https://www.conventionalcommits.org/):
  - `feat(ui): add agent fleet process table and live PID telemetry`
  - `fix(terminal): confine autoscroll to container viewport`
  - `test(e2e): add pytest suite for mobile gate decision endpoints`

---

## 📋 Pull Request Submission Checklist

Before submitting a Pull Request, ensure that:
1. `pytest tests/ui/ -v` passes with **100% PASS** (31/31 tests passing).
2. Frontend bundle builds cleanly: `npm run build` in `apps/web` with 0 TypeScript errors.
3. No forbidden state or secrets (`.env`, `sacl_ops.db*`) are staged.
4. Your PR description follows the [Pull Request Template](.github/pull_request_template.md) and completes the **Gates 0-5** verification checklist.

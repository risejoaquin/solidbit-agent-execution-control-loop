"""SACL E2E certification rehearsal, strictly offline and disposable.

These seven pytest tests implement TEST-02 through TEST-08 in the frozen
E2E_CERTIFICATION_PLAN.md. TEST-01 PowerShell AST is run separately in Windows CI.
Passing these tests is *not* permission to activate the SACL runtime, certify
the historical orchestrator, or archive any existing system.
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from sacl.contracts.exceptions import ContractValidationError, DirtyRootError
from sacl.contracts.invariants import AgentStatus, Verdict
from sacl.contracts.reconciliation import extract_verdict_from_content
from sacl.contracts.schema_validator import SchemaValidator
from sacl.results.collision import CollisionDetector
from sacl.state.store import SqliteStateStore
from sacl.worker.agent_worker import AgentWorker
from sacl.worker.models import WorkerConfig
from sacl.worker.process import (
    MockProcessInspector,
    safe_stop_agent_process,
    verify_agent_process_running,
)
from sacl.workspace.exceptions import BranchProtectionError, PrimaryCheckoutViolationError
from sacl.workspace.guards import assert_branch_allowed, assert_not_primary_checkout
from sacl.workspace.manager import WorkspaceManager
from tests.helpers.db_helpers import verify_canonical_domains_exist


ROOT = Path(__file__).resolve().parents[2]


def _git(*args: str, cwd: Path | None = None) -> str:
    """Execute Git only against explicit test-controlled local filesystem paths."""
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_CONFIG_NOSYSTEM="1")
    result = subprocess.run(
        ["git", *args], cwd=cwd, env=env, check=True,
        capture_output=True, text=True, timeout=15,
    )
    return result.stdout.strip()


@pytest.fixture
def local_git_sandbox(tmp_path: Path) -> tuple[Path, Path]:
    """No network remotes, no real user's repositories, no external credentials."""
    bare = tmp_path / "origin.git"
    checkout = tmp_path / "local"
    _git("init", "--bare", str(bare))
    _git("clone", str(bare), str(checkout))
    _git("checkout", "-b", "main", cwd=checkout)
    _git("config", "user.name", "SACL CI Mock", cwd=checkout)
    _git("config", "user.email", "sacl-ci@example.invalid", cwd=checkout)
    (checkout / "README.md").write_text("Local mock repository\n", encoding="utf-8")
    _git("add", "README.md", cwd=checkout)
    _git("-c", "commit.gpgsign=false", "commit", "-m", "Local seed", cwd=checkout)
    _git("push", "origin", "main", cwd=checkout)
    return checkout, bare


def test_02_manifest_schema_is_fail_closed() -> None:
    manifest = json.loads((ROOT / "examples" / "manifest.valid.json").read_text(encoding="utf-8"))
    validator = SchemaValidator(ROOT / "schemas")
    validator.validate_manifest(manifest)
    assert manifest["job_id"]
    rejected = dict(manifest)
    rejected.pop("job_id")
    with pytest.raises(ContractValidationError):
        validator.validate_manifest(rejected)


def test_03_bare_git_remote_and_clean_clone_are_local(local_git_sandbox, tmp_path: Path) -> None:
    checkout, bare = local_git_sandbox
    assert checkout.is_relative_to(tmp_path)
    assert bare.is_relative_to(tmp_path)
    assert _git("remote", "get-url", "origin", cwd=checkout) == str(bare)
    assert _git("status", "--porcelain", cwd=checkout) == ""
    assert _git("symbolic-ref", "--short", "HEAD", cwd=checkout) == "main"
    assert _git("rev-parse", "HEAD", cwd=checkout) == _git("rev-parse", "refs/heads/main", cwd=bare)


def test_04_worktree_isolation_dirty_root_and_protected_branches(local_git_sandbox, tmp_path: Path) -> None:
    checkout, _ = local_git_sandbox
    workspace = WorkspaceManager()
    first = tmp_path / "worktrees" / "agent-one"
    wt = workspace.provision_worktree(checkout, "sacl/e2e-agent-one", first, base_ref="HEAD")
    assert wt.resolve() == first.resolve()
    assert _git("branch", "--show-current", cwd=wt) == "sacl/e2e-agent-one"
    assert _git("branch", "--show-current", cwd=checkout) == "main"

    with pytest.raises(BranchProtectionError):
        assert_branch_allowed("main")
    with pytest.raises(PrimaryCheckoutViolationError):
        assert_not_primary_checkout(checkout, checkout)

    dirty = checkout / "user-work-in-progress.txt"
    dirty.write_text("Never delete or stash human edits.\n", encoding="utf-8")
    second = tmp_path / "worktrees" / "agent-two"
    with pytest.raises(DirtyRootError):
        workspace.provision_worktree(checkout, "sacl/e2e-agent-two", second)
    assert dirty.read_text(encoding="utf-8").startswith("Never delete")
    assert not second.exists()
    dirty.unlink()
    workspace.teardown_worktree(checkout, wt)
    assert not wt.exists()


def test_05_sqlite_16_domains_wal_and_mutating_lease(tmp_path: Path) -> None:
    with SqliteStateStore(db_path=tmp_path / "sacl_mock.db", auto_migrate=True) as store:
        assert store.connection.execute("PRAGMA journal_mode").fetchone()[0].lower() == "wal"
        domains = verify_canonical_domains_exist(store.connection)
        assert len(domains) == 16
        assert all(domains.values()), domains
        assert store.acquire_lease("SUPERVISOR_SINGLETON", "holder-a", 11001, 120)
        assert not store.acquire_lease("SUPERVISOR_SINGLETON", "holder-b", 11002, 120)
        assert store.acquire_lease("PROJECT_mock", "holder-a", 11001, 120)
        assert not store.acquire_lease("PROJECT_mock", "holder-b", 11002, 120)
        assert store.release_lease("PROJECT_mock", "holder-a")
        assert store.release_lease("SUPERVISOR_SINGLETON", "holder-a")


def test_06_pid_recycling_and_image_mismatch_fail_closed() -> None:
    inspector = MockProcessInspector()
    now = datetime.now(timezone.utc)
    inspector.register_process(11999, "agy", now, True)
    ok, verdict, _, _ = verify_agent_process_running(11999, now, inspector=inspector)
    assert ok and verdict == "VERIFIED_RUNNING"
    inspector.register_process(11999, "unrelated", now, True)
    ok, verdict, _, _ = verify_agent_process_running(11999, now, inspector=inspector)
    assert not ok and verdict == "PROCESS_NAME_MISMATCH_RECYCLED"
    inspector.register_process(11999, "agy", now + timedelta(seconds=350), True)
    ok, verdict, _, _ = verify_agent_process_running(11999, now, inspector=inspector)
    assert not ok and verdict == "START_TIME_MISMATCH_RECYCLED"


def test_07_safe_stop_and_diagnostic_timeout_never_auto_kills(tmp_path: Path) -> None:
    inspector = MockProcessInspector()
    now = datetime.now(timezone.utc)
    inspector.register_process(12001, "agy", now, True)
    success, code, _ = safe_stop_agent_process(12001, now, inspector=inspector)
    assert success and code == "STOPPED_BY_USER"
    assert not inspector.is_process_running(12001)

    inspector.register_process(12002, "unrelated", now, True)
    success, code, _ = safe_stop_agent_process(12002, now, inspector=inspector)
    assert not success and code == "SAFETY_REFUSAL_NAME"
    assert inspector.is_process_running(12002)

    # No executable_command and a mock inspector: Worker does not spawn agy.exe.
    cfg = WorkerConfig(
        agent_id="AG-MOCK", run_id="e2e-run",
        worktree_path=tmp_path / "wt",
        prompt_path=tmp_path / "prompts" / "mock.txt",
        report_path=tmp_path / "reports" / "mock.md",
        stdout_path=tmp_path / "logs" / "mock.stdout.log",
        stderr_path=tmp_path / "logs" / "mock.stderr.log",
        timeout_seconds=1,
        max_attempts=1,
    )
    worker = AgentWorker(cfg, process_inspector=inspector)
    worker.launch_attempt()
    assert worker.pid is not None and inspector.is_process_running(worker.pid)
    worker.start_monotonic = time.monotonic() - 5
    is_running, status = worker.check_liveness_and_timeout()
    assert is_running
    assert status == AgentStatus.TIMEOUT_RUNNING.value
    assert worker.is_timed_out
    assert inspector.is_process_running(worker.pid), "Timeout must never kill the process"


def test_08_regex_fallback_and_collision_block_integration(sqlite_memory_db) -> None:
    marker = extract_verdict_from_content(
        "AGENT_MOCK_1_RESULT = PASS\n", report_exists=True,
        report_size_bytes=27, exit_code=0,
    )
    fallback = extract_verdict_from_content(
        "Report complete, no marker", report_exists=True,
        report_size_bytes=26, exit_code=0,
    )
    assert marker.verdict == Verdict.PASS.value
    assert fallback.verdict == Verdict.PASS_REPORT_PRESENT.value

    conn = sqlite_memory_db
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO jobs (job_id, status, priority, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        ("job-e2e", "RUNNING", 0, now, now),
    )
    conn.execute(
        """INSERT INTO runs
        (run_id, job_id, package_id, project, repository, mode, source_orchestrator,
         target_repo_path, run_dir, status, ready_for_integration, started_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        ("run-e2e", "job-e2e", "pkg-e2e", "mock", "mock/repo",
         "isolated_branch", "", "", "", "RUNNING", "NO", now),
    )
    for agent_id in ("AG-A", "AG-B"):
        conn.execute(
            """INSERT INTO agents
               (agent_id, run_id, status, result_verdict, prompt_path,
                report_path, stdout_path, stderr_path, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (agent_id, "run-e2e", "COMPLETE", "PASS", "p", "r", "out", "err", now),
        )
    conn.commit()
    detector = CollisionDetector()
    for agent_id in ("AG-A", "AG-B"):
        detector.record_file_modifications(
            run_id="run-e2e", agent_id=agent_id,
            file_paths=["docs/shared.md"], db_conn=conn,
        )
    collision = detector.evaluate_conflicts("run-e2e", conn)
    assert collision.conflicting_files == ["docs/shared.md"]
    assert collision.ready_for_integration == "NO"
    assert conn.execute(
        "SELECT ready_for_integration FROM runs WHERE run_id='run-e2e'"
    ).fetchone()[0] == "NO"

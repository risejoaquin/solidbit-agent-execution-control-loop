"""T52: late worktree recheck and directory identity before mocked Popen.

No real worker processes or external repositories are touched.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock, patch

from sacl.contracts.invariants import AgentStatus
from sacl.worker.agent_worker import AgentWorker
from sacl.worker.models import WorkerConfig
from sacl.worker.process import MockProcessInspector
from sacl.worker.worktree import WorkspaceManager
from sacl.workspace.exceptions import WorkspaceError


def make_worker(tmp_path):
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    config = WorkerConfig(
        agent_id="t52", run_id="run-t52", branch="task/t52",
        worktree_path=worktree,
        prompt_path=tmp_path / "prompt",
        report_path=tmp_path / "logs" / "report",
        stdout_path=tmp_path / "logs" / "stdout",
        stderr_path=tmp_path / "logs" / "stderr",
        executable_command=["never-run-t52"], max_attempts=1,
    )
    manager = Mock(spec=WorkspaceManager)
    reconciler = Mock()
    reconciler.reconcile.return_value = SimpleNamespace(
        status="FAILED", result_verdict="FAIL", error_message="guard rejected",
    )
    worker = AgentWorker(
        config=config, workspace_manager=manager,
        process_inspector=MockProcessInspector(), reconciler=reconciler,
    )
    return worker, manager


def test_canonical_worktree_revalidated_before_mocked_spawn(tmp_path):
    worker, manager = make_worker(tmp_path)
    with patch("sacl.worker.agent_worker.subprocess.Popen") as spawn:
        spawn.return_value.pid = 45123
        worker.launch_attempt()
        spawn.assert_called_once()
    assert manager.assert_registered_worktree.call_count == 2
    assert worker.status == AgentStatus.RUNNING.value
    assert worker.pid == 45123


def test_replacement_during_preparation_rejected_without_spawn(tmp_path):
    worker, manager = make_worker(tmp_path)
    worktree = worker.config.worktree_path
    replacement = tmp_path / "replacement"
    replacement.mkdir()
    calls = 0

    def recheck(path, expected_branch=None):
        nonlocal calls
        calls += 1
        if calls == 2:
            worktree.rename(tmp_path / "original")
            replacement.rename(worktree)

    manager.assert_registered_worktree.side_effect = recheck
    with patch("sacl.worker.agent_worker.subprocess.Popen") as spawn:
        worker.launch_attempt()
        spawn.assert_not_called()
    assert calls == 2
    assert worker.status == AgentStatus.FAILED.value
    assert "identity changed" in worker.error_message


def test_second_registry_check_failure_prevents_spawn(tmp_path):
    worker, manager = make_worker(tmp_path)
    manager.assert_registered_worktree.side_effect = [
        None, WorkspaceError("worktree alias detected before spawn"),
    ]
    with patch("sacl.worker.agent_worker.subprocess.Popen") as spawn:
        worker.launch_attempt()
        spawn.assert_not_called()
    assert manager.assert_registered_worktree.call_count == 2
    assert worker.status == AgentStatus.FAILED.value
    assert "worktree alias detected" in worker.error_message

"""T51: worktree alias rejection before worker spawn."""
import subprocess
from pathlib import Path
from unittest.mock import patch
import pytest
from sacl.worker.worktree import WorkspaceManager
from sacl.workspace.exceptions import WorkspaceError

def git(*args, cwd=None):
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=15)
    result.check_returncode()
    return result.stdout.strip()

@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    git("init", str(root))
    git("checkout", "-b", "main", cwd=root)
    git("config", "user.name", "SACL test", cwd=root)
    git("config", "user.email", "sacl@example.invalid", cwd=root)
    (root / "README.md").write_text("fixture\n")
    git("add", "README.md", cwd=root)
    git("-c", "commit.gpgsign=false", "commit", "-m", "fixture", cwd=root)
    return root

def test_ancestor_symlink_denied_before_spawn(repo, tmp_path):
    from sacl.worker.agent_worker import AgentWorker
    from sacl.worker.models import WorkerConfig
    from sacl.worker.process import MockProcessInspector
    manager = WorkspaceManager()
    parent = tmp_path / "actual"
    parent.mkdir()
    target = parent / "wt"
    manager.provision_worktree(repo, "task/alias", target)
    alias = tmp_path / "alias"
    try:
        alias.symlink_to(parent, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Directory symlink unavailable")
    worktree = alias / "wt"
    assert not worktree.is_symlink()
    config = WorkerConfig(agent_id="alias", run_id="alias-run", branch="task/alias",
        worktree_path=worktree, prompt_path=tmp_path / "prompt",
        report_path=tmp_path / "report", stdout_path=tmp_path / "logs" / "out",
        stderr_path=tmp_path / "logs" / "err",
        executable_command=["never-execute"], max_attempts=1)
    worker = AgentWorker(config=config, workspace_manager=manager,
        process_inspector=MockProcessInspector())
    with patch("sacl.worker.agent_worker.subprocess.Popen") as spawn:
        with pytest.raises(WorkspaceError, match="symlink or junction"):
            worker.launch_attempt()
        spawn.assert_not_called()
    assert worker.current_attempt == 0
    assert not (tmp_path / "logs").exists()
    manager.teardown_worktree(repo, target)

def test_alias_denied_without_symlink_privileges(tmp_path):
    alias = tmp_path / "alias" / "wt"
    canonical = tmp_path / "actual" / "wt"
    with patch.object(Path, "resolve", return_value=canonical):
        with patch("sacl.worker.worktree.assert_valid_repository") as check:
            with pytest.raises(WorkspaceError, match="symlink or junction"):
                WorkspaceManager().assert_registered_worktree(alias, expected_branch="task/alias")
            check.assert_not_called()

def test_canonical_registered_worktree_allowed(repo, tmp_path):
    manager = WorkspaceManager()
    target = tmp_path / "wt"
    manager.provision_worktree(repo, "task/allowed", target)
    manager.assert_registered_worktree(target, expected_branch="task/allowed")
    manager.teardown_worktree(repo, target)

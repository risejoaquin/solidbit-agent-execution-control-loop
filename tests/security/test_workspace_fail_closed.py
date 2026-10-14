"""Security regression suite: worker worktrees must fail closed on Git errors."""
from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from sacl.contracts.exceptions import DirtyRootError
from sacl.worker.worktree import WorkspaceManager
from sacl.workspace.exceptions import (
    BranchProtectionError, GitCommandError,
    PrimaryCheckoutViolationError, RepositoryValidationError,
    WorkspaceError, WorktreeCollisionError, WorktreeNotFoundError,
)


def git(*args: str, cwd: Path | None = None) -> str:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=15)
    r.check_returncode()
    return r.stdout.strip()


@pytest.fixture
def git_checkout(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    git("init", str(repo))
    git("checkout", "-b", "main", cwd=repo)
    git("config", "user.name", "SACL test", cwd=repo)
    git("config", "user.email", "sacl@example.invalid", cwd=repo)
    (repo / "README.md").write_text("fixture\n", encoding="utf-8")
    git("add", "README.md", cwd=repo)
    git("-c", "commit.gpgsign=false", "commit", "-m", "local fixture", cwd=repo)
    return repo


def test_real_mode_rejects_plain_directory(tmp_path: Path) -> None:
    manager = WorkspaceManager()
    with pytest.raises(RepositoryValidationError):
        manager.check_clean_root(tmp_path)
    with pytest.raises(RepositoryValidationError):
        manager.provision_worktree(tmp_path, "task/agent", tmp_path / "wt")
    assert not (tmp_path / "wt").exists()


def test_explicit_mock_mode_is_isolated_and_non_destructive(tmp_path: Path) -> None:
    manager = WorkspaceManager(mock_mode=True)
    repo = tmp_path / "mock"
    repo.mkdir()
    assert manager.check_clean_root(repo) == (True, [])
    target = manager.provision_worktree(repo, "task/mock", tmp_path / "worktrees" / "wt")
    assert manager.provision_worktree(repo, "task/mock", target) == target
    with pytest.raises(WorktreeCollisionError):
        manager.provision_worktree(repo, "task/different", target)
    with pytest.raises(WorkspaceError):
        manager.teardown_worktree(repo, target, force=True)
    manager.teardown_worktree(repo, target)
    assert not target.exists()


def test_mock_refuses_unowned_or_nonempty_folder(tmp_path: Path) -> None:
    repo = tmp_path / "mock"
    repo.mkdir()
    unmanaged = tmp_path / "unmanaged"
    unmanaged.mkdir()
    sentinel = unmanaged / "human.txt"
    sentinel.write_text("do not touch", encoding="utf-8")
    manager = WorkspaceManager(mock_mode=True)
    with pytest.raises(WorktreeCollisionError):
        manager.provision_worktree(repo, "task/new", unmanaged)
    with pytest.raises(WorktreeNotFoundError):
        manager.teardown_worktree(repo, unmanaged)
    with pytest.raises((RepositoryValidationError, WorktreeNotFoundError)):
        manager.get_modified_files(unmanaged)
    assert sentinel.read_text(encoding="utf-8") == "do not touch"

    owned = manager.provision_worktree(repo, "task/owned", tmp_path / "wt")
    (owned / "untracked.txt").write_text("keep", encoding="utf-8")
    with pytest.raises(WorkspaceError):
        manager.get_modified_files(owned)
    with pytest.raises(OSError):
        manager.teardown_worktree(repo, owned)
    assert (owned / "untracked.txt").exists()


def test_mock_branch_and_primary_checkout_protected(tmp_path: Path) -> None:
    repo = tmp_path / "mock"
    repo.mkdir()
    manager = WorkspaceManager(mock_mode=True)
    with pytest.raises(BranchProtectionError):
        manager.provision_worktree(repo, "main", tmp_path / "wt")
    with pytest.raises(PrimaryCheckoutViolationError):
        manager.provision_worktree(repo, "task/bad", repo)


def test_registered_real_worktree_and_clean_teardown(git_checkout: Path, tmp_path: Path) -> None:
    manager = WorkspaceManager()
    repo = git_checkout
    target = tmp_path / "wt-agent"
    assert manager.provision_worktree(repo, "task/good", target) == target.resolve()
    assert git("branch", "--show-current", cwd=target) == "task/good"
    assert git("branch", "--show-current", cwd=repo) == "main"
    assert manager.get_modified_files(target) == []
    manager.teardown_worktree(repo, target)
    assert not target.exists()


def test_dirty_root_blocks_provision_without_editing_human_data(git_checkout: Path, tmp_path: Path) -> None:
    repo = git_checkout
    keep = repo / "in-progress.txt"
    keep.write_text("preserve", encoding="utf-8")
    target = tmp_path / "not-created"
    with pytest.raises(DirtyRootError):
        WorkspaceManager().provision_worktree(repo, "task/new", target)
    assert keep.read_text(encoding="utf-8") == "preserve"
    assert not target.exists()


def test_real_unmanaged_folder_is_not_returned_or_deleted(git_checkout: Path, tmp_path: Path) -> None:
    folder = tmp_path / "unmanaged"
    folder.mkdir()
    keep = folder / "IMPORTANT.txt"
    keep.write_text("human data", encoding="utf-8")
    mgr = WorkspaceManager()
    with pytest.raises(WorktreeCollisionError):
        mgr.provision_worktree(git_checkout, "task/new", folder)
    with pytest.raises(WorktreeNotFoundError):
        mgr.teardown_worktree(git_checkout, folder)
    assert keep.read_text(encoding="utf-8") == "human data"


def test_git_failure_never_makes_fake_worktree(git_checkout: Path, tmp_path: Path) -> None:
    manager = WorkspaceManager(git_executable="not-the-real-git-executable-sacl")
    target = tmp_path / "fake"
    with pytest.raises(GitCommandError):
        manager.provision_worktree(git_checkout, "task/safe", target)
    assert not target.exists()


def test_bad_diff_reference_raises_instead_of_returning_empty(
    git_checkout: Path, tmp_path: Path,
) -> None:
    manager = WorkspaceManager()
    target = tmp_path / "worktree"
    manager.provision_worktree(git_checkout, "task/agent", target)
    with pytest.raises(GitCommandError):
        manager.get_modified_files(target, base_ref="no-such-ref-SACL-TEST")
    manager.teardown_worktree(git_checkout, target)


def test_dirty_real_worktree_cannot_be_deleted(git_checkout: Path, tmp_path: Path) -> None:
    manager = WorkspaceManager()
    target = tmp_path / "wt"
    manager.provision_worktree(git_checkout, "task/new", target)
    sentinel = target / "work.txt"
    sentinel.write_text("preserve", encoding="utf-8")
    with pytest.raises(DirtyRootError):
        manager.teardown_worktree(git_checkout, target)
    with pytest.raises(WorkspaceError):
        manager.teardown_worktree(git_checkout, target, force=True)
    assert sentinel.read_text(encoding="utf-8") == "preserve"


def test_symlink_untrusted_path_rejected(git_checkout: Path, tmp_path: Path) -> None:
    # Windows agents may lack symlink privileges; do not grant them merely for CI.
    target = tmp_path / "outside"
    target.mkdir()
    link = tmp_path / "link"
    try:
        link.symlink_to(target, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Host cannot create a directory symlink without elevation")
    with pytest.raises(WorkspaceError):
        WorkspaceManager().provision_worktree(git_checkout, "task/new", link)
    with pytest.raises(WorkspaceError):
        WorkspaceManager().teardown_worktree(git_checkout, link)

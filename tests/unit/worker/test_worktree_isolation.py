"""Tests for isolated worktree execution, Local Dirty-Root Rule, and workspace management."""

from __future__ import annotations

from pathlib import Path

from sacl.worker.worktree import WorkspaceManager


def test_clean_root_on_clean_directory(tmp_path: Path):
    mgr = WorkspaceManager()
    is_clean, dirty = mgr.check_clean_root(tmp_path)
    assert is_clean is True
    assert dirty == []


def test_assert_clean_root_passes_when_clean(tmp_path: Path):
    mgr = WorkspaceManager()
    mgr.assert_clean_root(tmp_path)


def test_worktree_provision_and_teardown_mock(tmp_path: Path):
    mgr = WorkspaceManager()
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    worktree_path = tmp_path / "worktrees" / "wt-AG-TEST"

    provisioned = mgr.provision_worktree(
        repo_path=repo_path,
        branch_name="task/ag-test",
        worktree_path=worktree_path,
    )
    assert provisioned.exists()
    assert provisioned == worktree_path

    # Teardown removes directory
    mgr.teardown_worktree(repo_path=repo_path, worktree_path=worktree_path)
    assert not worktree_path.exists()

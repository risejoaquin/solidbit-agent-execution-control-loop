"""Unit tests for SACL V1 Worktree Inspection & Local Dirty-Root Rule."""

from __future__ import annotations

from pathlib import Path

import pytest

from sacl.contracts.exceptions import HardDenyViolation
from sacl.recovery.worktree_inspection import (
    MockGitClient,
    OrphanClassification,
    assert_safe_git_command,
    check_primary_repo_clean,
    inspect_agent_worktree,
    scan_orphaned_worktrees,
)


def test_assert_safe_git_command_prohibits_destructive_commands() -> None:
    """Verifies that forbidden commands trigger HardDenyViolation."""
    with pytest.raises(HardDenyViolation) as exc:
        assert_safe_git_command(["reset", "--hard", "HEAD"])
    assert "hard_reset" in str(exc.value)

    with pytest.raises(HardDenyViolation) as exc:
        assert_safe_git_command(["clean", "-fd"])
    assert "primary_checkout_mutation" in str(exc.value)

    with pytest.raises(HardDenyViolation) as exc:
        assert_safe_git_command(["stash"])
    assert "auto_stash" in str(exc.value)

    with pytest.raises(HardDenyViolation) as exc:
        assert_safe_git_command(["checkout", "-f", "main"])
    assert "primary_checkout_mutation" in str(exc.value)


def test_assert_safe_git_command_allows_read_and_safe_commands() -> None:
    """Read-only and non-destructive commands succeed."""
    assert_safe_git_command(["status", "--porcelain"])
    assert_safe_git_command(["diff", "--name-only", "HEAD"])
    assert_safe_git_command(["rev-parse", "HEAD"])
    assert_safe_git_command(["log", "-n", "1"])


def test_check_primary_repo_clean_success(tmp_path: Path) -> None:
    """Clean primary checkout succeeds."""
    mock_git = MockGitClient()
    mock_git.set_status(tmp_path, [])

    res = check_primary_repo_clean(tmp_path, git_client=mock_git)
    assert res.is_clean is True
    assert res.halt_reason is None
    assert res.error_message is None


def test_check_primary_repo_dirty_halts_recovery(tmp_path: Path) -> None:
    """Dirty primary checkout halts with DIRTY_ROOT_BLOCKS_RECOVERY."""
    mock_git = MockGitClient()
    mock_git.set_status(tmp_path, [" M src/main.py", "?? untracked.txt"])

    res = check_primary_repo_clean(tmp_path, git_client=mock_git)
    assert res.is_clean is False
    assert res.halt_reason == "DIRTY_ROOT_BLOCKS_RECOVERY"
    assert "DIRTY_ROOT_BLOCKS_RECOVERY" in str(res.error_message)
    assert len(res.uncommitted_files) == 2


def test_inspect_agent_worktree_clean(tmp_path: Path) -> None:
    """Clean agent worktree generates valid clean WorktreeState."""
    wt_dir = tmp_path / "worktree-1"
    wt_dir.mkdir()

    mock_git = MockGitClient()
    mock_git.set_status(wt_dir, [])
    mock_git.set_head_commit(wt_dir, "abcdef1234567890")
    mock_git.set_current_branch(wt_dir, "feature/audit-test")

    res = inspect_agent_worktree(wt_dir, expected_branch="feature/audit-test", git_client=mock_git)
    assert res.exists is True
    assert res.is_clean is True
    assert res.commit_sha == "abcdef1234567890"
    assert res.branch == "feature/audit-test"
    assert res.verdict_impact is None
    assert res.worktree_state.is_clean is True


def test_inspect_agent_worktree_dirty_preserves_for_forensics(tmp_path: Path) -> None:
    """Dirty worktree marks UNCOMMITTED_CHANGES_ON_RECOVERY without resetting."""
    wt_dir = tmp_path / "worktree-dirty"
    wt_dir.mkdir()

    mock_git = MockGitClient()
    mock_git.set_status(wt_dir, [" M package.json"])
    mock_git.set_head_commit(wt_dir, "111222333")

    res = inspect_agent_worktree(wt_dir, git_client=mock_git)
    assert res.exists is True
    assert res.is_clean is False
    assert res.verdict_impact == "UNCOMMITTED_CHANGES_ON_RECOVERY"
    assert "package.json" in res.modified_files
    assert res.worktree_state.is_clean is False


def test_inspect_agent_worktree_missing_dir(tmp_path: Path) -> None:
    """Missing worktree directory handled gracefully."""
    non_existent = tmp_path / "does-not-exist"
    res = inspect_agent_worktree(non_existent)
    assert res.exists is False
    assert res.is_clean is False
    assert res.verdict_impact == "WORKTREE_DIR_MISSING"


def test_scan_orphaned_worktrees(tmp_path: Path) -> None:
    """Scans and detects unregistered or orphaned worktree directories."""
    base_dir = tmp_path / "worktrees"
    base_dir.mkdir()

    wt_active = base_dir / "wt-active"
    wt_active.mkdir()

    wt_orphan_clean = base_dir / "wt-orphan-1"
    wt_orphan_clean.mkdir()

    wt_orphan_dirty = base_dir / "wt-orphan-2"
    wt_orphan_dirty.mkdir()

    mock_git = MockGitClient()
    mock_git.set_status(wt_orphan_clean, [])
    mock_git.set_status(wt_orphan_dirty, ["?? scratch.log"])

    registered = {str(wt_active.resolve())}

    orphans = scan_orphaned_worktrees(base_dir, registered, git_client=mock_git)
    assert len(orphans) == 2

    paths = {Path(o.directory_path).name: o for o in orphans}
    assert "wt-orphan-1" in paths
    assert paths["wt-orphan-1"].classification == OrphanClassification.UNREGISTERED_WORKTREE
    assert paths["wt-orphan-1"].is_clean is True

    assert "wt-orphan-2" in paths
    assert paths["wt-orphan-2"].classification == OrphanClassification.ORPHAN_DIRTY_CHANGES
    assert paths["wt-orphan-2"].is_clean is False

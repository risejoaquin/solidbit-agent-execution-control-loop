"""SACL V1 Local-Only Commit Helpers.

Provides safe, deterministic git commit primitives exclusively within isolated worktrees.
Strictly prohibits remote operations (git push) and protects primary checkouts.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from sacl.workspace.dirty_root import check_clean_root
from sacl.workspace.exceptions import WorkspaceError
from sacl.workspace.git_runner import GitRunner
from sacl.workspace.guards import (
    assert_branch_allowed,
    assert_valid_repository,
    normalize_branch_name,
)

DEFAULT_AUTHOR_NAME = "SACL Agent"
DEFAULT_AUTHOR_EMAIL = "sacl-agent@solidbit.local"


def get_head_commit_sha(worktree_path: Path, git_runner: Optional[GitRunner] = None) -> str:
    """Returns the 40-character hexadecimal commit SHA of HEAD."""
    runner = git_runner or GitRunner()
    assert_valid_repository(worktree_path, runner)
    res = runner.run(["rev-parse", "HEAD"], cwd=worktree_path, check=True)
    return res.stdout.strip()


def get_current_branch(worktree_path: Path, git_runner: Optional[GitRunner] = None) -> str:
    """Returns the current branch name of the worktree."""
    runner = git_runner or GitRunner()
    assert_valid_repository(worktree_path, runner)
    res = runner.run(["rev-parse", "--abbrev-ref", "HEAD"], cwd=worktree_path, check=True)
    return normalize_branch_name(res.stdout)


def stage_and_commit(
    worktree_path: Path,
    message: str,
    files: Optional[List[str]] = None,
    author_name: str = DEFAULT_AUTHOR_NAME,
    author_email: str = DEFAULT_AUTHOR_EMAIL,
    git_runner: Optional[GitRunner] = None,
) -> Optional[str]:
    """Stages specified files (or all changes) and creates a local commit.

    Constitutional constraints:
    - Never executes git push or communicates with remotes.
    - Enforces branch inviolability (cannot commit to protected branches).
    - Preserves deterministic commit metadata.

    Args:
        worktree_path: Isolated agent worktree directory.
        message: Commit message.
        files: Optional list of relative paths to stage. If None, stages all (-A).
        author_name: Commit author name.
        author_email: Commit author email.
        git_runner: Optional GitRunner instance.

    Returns:
        The new commit SHA, or the current commit SHA if nothing was staged.
    """
    runner = git_runner or GitRunner()
    assert_valid_repository(worktree_path, runner)

    # Branch protection check
    branch = get_current_branch(worktree_path, runner)
    assert_branch_allowed(branch)

    if not message.strip():
        raise WorkspaceError("Commit message cannot be empty.")

    # 1. Stage files
    if files:
        for f in files:
            add_res = runner.run(["add", "--", f], cwd=worktree_path)
            if not add_res.success:
                add_res.check()
    else:
        add_res = runner.run(["add", "-A"], cwd=worktree_path)
        if not add_res.success:
            add_res.check()

    # 2. Check if anything is staged
    staged_check = runner.run(["diff", "--cached", "--quiet"], cwd=worktree_path)
    if staged_check.exit_code == 0:
        # Exit code 0 means no differences staged
        return get_head_commit_sha(worktree_path, runner)

    # 3. Create local commit with explicit author/committer environment
    env = {
        "GIT_AUTHOR_NAME": author_name,
        "GIT_AUTHOR_EMAIL": author_email,
        "GIT_COMMITTER_NAME": author_name,
        "GIT_COMMITTER_EMAIL": author_email,
    }

    runner.run(
        ["commit", "-m", message.strip()],
        cwd=worktree_path,
        extra_env=env,
        check=True,
    )

    return get_head_commit_sha(worktree_path, runner)


def get_worktree_status(
    worktree_path: Path,
    base_ref: str = "HEAD",
    git_runner: Optional[GitRunner] = None,
) -> Dict[str, Any]:
    """Collects comprehensive status and git metadata for an isolated worktree."""
    runner = git_runner or GitRunner()
    assert_valid_repository(worktree_path, runner)

    branch = get_current_branch(worktree_path, runner)
    commit_sha = get_head_commit_sha(worktree_path, runner)
    is_clean, dirty_files = check_clean_root(worktree_path, runner)

    # Diffs relative to base_ref
    diff_res = runner.run(["diff", "--name-only", f"{base_ref}...HEAD"], cwd=worktree_path)
    committed_files: List[str] = []
    if diff_res.success:
        for line in diff_res.stdout.splitlines():
            line = line.strip().replace("\\", "/")
            if line:
                committed_files.append(line)

    all_modified = sorted(set(dirty_files + committed_files))

    return {
        "worktree_path": str(worktree_path.resolve()),
        "branch": branch,
        "commit_sha": commit_sha,
        "is_clean": is_clean,
        "dirty_files": dirty_files,
        "committed_files": committed_files,
        "all_modified_files": all_modified,
    }


__all__ = [
    "DEFAULT_AUTHOR_NAME",
    "DEFAULT_AUTHOR_EMAIL",
    "get_head_commit_sha",
    "get_current_branch",
    "stage_and_commit",
    "get_worktree_status",
]

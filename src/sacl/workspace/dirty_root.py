"""SACL V1 Local Dirty-Root Detection and Enforcement.

Enforces the Local Dirty-Root Rule:
The primary human checkout may legitimately contain uncommitted human changes.
Automation must NEVER destroy, stash, clean, or reset human work.
If uncommitted modifications are detected, worktree provisioning halts immediately.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

from sacl.contracts.exceptions import DirtyRootError
from sacl.workspace.git_runner import GitRunner


def parse_porcelain_status(output: str) -> List[str]:
    """Parses git status --porcelain output into normalized relative file paths."""
    dirty_files: List[str] = []
    for raw_line in output.splitlines():
        if not raw_line.strip():
            continue
        # Git porcelain v1 format: exactly 2 status chars, then space, then path
        if len(raw_line) >= 3 and raw_line[2] == " ":
            path_part = raw_line[3:].strip()
        elif len(raw_line) >= 3:
            path_part = raw_line[2:].strip()
        else:
            continue

        if " -> " in path_part:
            # Renamed file: take destination
            path_part = path_part.split(" -> ")[-1].strip()
        # Strip quotes if git quoted a path with spaces
        if path_part.startswith('"') and path_part.endswith('"'):
            path_part = path_part[1:-1]
        normalized = path_part.replace("\\", "/").strip()
        if normalized and normalized not in dirty_files:
            dirty_files.append(normalized)
    return dirty_files


def check_clean_root(
    repo_path: Path,
    git_runner: Optional[GitRunner] = None,
) -> Tuple[bool, List[str]]:
    """Enforces the Local Dirty-Root Rule check.

    Inspects the repository working tree via 'git status --porcelain'.

    Args:
        repo_path: Path to the target Git repository root.
        git_runner: Optional GitRunner instance.

    Returns:
        Tuple of (is_clean, dirty_files).
    """
    runner = git_runner or GitRunner()
    result = runner.run(["status", "--porcelain"], cwd=repo_path)
    if not result.success:
        result.check()  # Will raise GitCommandError

    dirty_files = parse_porcelain_status(result.stdout)
    is_clean = len(dirty_files) == 0
    return (is_clean, dirty_files)


def assert_clean_root(
    repo_path: Path,
    git_runner: Optional[GitRunner] = None,
) -> None:
    """Asserts that the repository working tree is clean.

    Never cleans, stashes, or resets human modifications.

    Raises:
        DirtyRootError: If uncommitted or untracked changes exist.
    """
    is_clean, dirty_files = check_clean_root(repo_path, git_runner)
    if not is_clean:
        raise DirtyRootError(target_path=str(repo_path), dirty_files=dirty_files)


__all__ = [
    "parse_porcelain_status",
    "check_clean_root",
    "assert_clean_root",
]

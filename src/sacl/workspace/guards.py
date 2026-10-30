"""SACL V1 Git Repository and Worktree Guards.

Constitutional guard assertions protecting repository integrity, branch inviolability,
remote URL bindings, and primary checkout safety.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import FrozenSet, Iterable, Optional, Tuple

from sacl.workspace.exceptions import (
    BranchProtectionError,
    PrimaryCheckoutViolationError,
    RepositoryValidationError,
)
from sacl.workspace.git_runner import GitRunner

DEFAULT_PROTECTED_BRANCHES: FrozenSet[str] = frozenset(
    {
        "main",
        "master",
        "release",
        "production",
        "prod",
    }
)


def normalize_branch_name(branch_name: str) -> str:
    """Strips refs/heads/ or remote prefixes from a branch name."""
    b = branch_name.strip()
    if b.startswith("refs/heads/"):
        b = b[len("refs/heads/") :]
    elif b.startswith("refs/remotes/"):
        b = b[len("refs/remotes/") :]
        if b.startswith("origin/"):
            b = b[len("origin/") :]
    elif b.startswith("origin/"):
        b = b[len("origin/") :]
    return b


def is_protected_branch(
    branch_name: str, protected_branches: Optional[Iterable[str]] = None
) -> bool:
    """Evaluates whether a branch name is protected under MAIN_BRANCH_NOT_ALLOWED."""
    normalized = normalize_branch_name(branch_name).lower()
    protected = {b.lower() for b in (protected_branches or DEFAULT_PROTECTED_BRANCHES)}

    if normalized in protected:
        return True

    # Pattern check for release branches e.g. release/1.0, release-v2
    if normalized.startswith("release/") or normalized.startswith("release-"):
        return True

    # Production prefixes
    if normalized.startswith("prod/") or normalized.startswith("production/"):
        return True

    return False


def assert_branch_allowed(
    branch_name: str, protected_branches: Optional[Iterable[str]] = None
) -> None:
    """Enforces branch inviolability (MAIN_BRANCH_NOT_ALLOWED).

    Raises:
        BranchProtectionError: If branch_name is protected.
    """
    if is_protected_branch(branch_name, protected_branches):
        raise BranchProtectionError(
            branch_name=branch_name,
            reason="Direct execution or mutation on primary/protected branch is permanently hard-denied.",
        )


def assert_valid_repository(repo_path: Path, git_runner: Optional[GitRunner] = None) -> None:
    """Validates that a path exists, is a directory, and is a valid Git repository.

    Raises:
        RepositoryValidationError: If path is missing, not a directory, or not a Git repo.
    """
    if not repo_path.exists():
        raise RepositoryValidationError(str(repo_path), "Directory does not exist on disk.")

    if not repo_path.is_dir():
        raise RepositoryValidationError(str(repo_path), "Path is not a directory.")

    git_entry = repo_path / ".git"
    if not git_entry.exists():
        # Check via git rev-parse in case of worktree or alternate setup
        runner = git_runner or GitRunner()
        res = runner.run(["rev-parse", "--is-inside-work-tree"], cwd=repo_path)
        if not res.success or res.stdout.strip() != "true":
            raise RepositoryValidationError(
                str(repo_path), "Directory is not a valid Git working tree."
            )


def assert_not_primary_checkout(target_path: Path, primary_repo_path: Path) -> None:
    """Enforces PRIMARY_CHECKOUT_NOT_ALLOWED.

    Ensures agent mutating operations execute inside isolated worktrees,
    never directly in the human primary checkout.

    Raises:
        PrimaryCheckoutViolationError: If target_path resolves to primary_repo_path.
    """
    try:
        target_resolved = target_path.resolve()
        primary_resolved = primary_repo_path.resolve()
        if target_resolved == primary_resolved:
            raise PrimaryCheckoutViolationError(
                target_path=str(target_path),
                reason="Direct mutation of primary checkout is hard-denied. Use an isolated worktree.",
            )
    except FileNotFoundError:
        # If target doesn't exist yet, check string normalization or parent
        target_str = str(target_path).replace("\\", "/").rstrip("/")
        primary_str = str(primary_repo_path).replace("\\", "/").rstrip("/")
        if target_str.lower() == primary_str.lower():
            raise PrimaryCheckoutViolationError(
                target_path=str(target_path),
                reason="Target path points to primary checkout.",
            )


def verify_remote_origin(
    repo_path: Path,
    pattern: Optional[str] = None,
    git_runner: Optional[GitRunner] = None,
) -> Tuple[bool, str]:
    """Retrieves and optionally validates the origin remote URL.

    Returns:
        Tuple of (matches_pattern, remote_url).
    """
    runner = git_runner or GitRunner()
    res = runner.run(["remote", "get-url", "origin"], cwd=repo_path)
    if not res.success:
        # Fallback to config query
        res = runner.run(["config", "--get", "remote.origin.url"], cwd=repo_path)
        if not res.success:
            return (False, "")

    remote_url = res.stdout.strip()
    if not pattern:
        return (True, remote_url)

    matches = bool(re.search(pattern, remote_url, re.IGNORECASE))
    return (matches, remote_url)


def assert_remote_origin(
    repo_path: Path,
    pattern: str,
    git_runner: Optional[GitRunner] = None,
) -> str:
    """Asserts that origin remote URL satisfies the required pattern.

    Raises:
        RepositoryValidationError: If pattern does not match.
    """
    matches, remote_url = verify_remote_origin(repo_path, pattern, git_runner)
    if not matches:
        raise RepositoryValidationError(
            str(repo_path),
            f"Remote origin '{remote_url}' failed pattern verification '{pattern}'.",
        )
    return remote_url


__all__ = [
    "DEFAULT_PROTECTED_BRANCHES",
    "normalize_branch_name",
    "is_protected_branch",
    "assert_branch_allowed",
    "assert_valid_repository",
    "assert_not_primary_checkout",
    "verify_remote_origin",
    "assert_remote_origin",
]

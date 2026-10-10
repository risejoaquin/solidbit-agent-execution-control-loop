"""SACL V1 Workspace Exceptions.

Typed exception hierarchy governing workspace isolation, Git repository guards,
branch protection, dirty-root detection, and worktree concurrency collisions.
"""

from __future__ import annotations

from typing import List, Optional

from sacl.contracts.exceptions import (
    CollisionDetectedError,
    DirtyRootError,
    HardDenyViolation,
    SaclError,
)


class WorkspaceError(SaclError):
    """Base exception for all workspace isolation and Git guard errors."""
    pass


class BranchProtectionError(WorkspaceError, HardDenyViolation):
    """Raised when an operation attempts to execute on or modify a protected branch (e.g. main/master)."""

    def __init__(self, branch_name: str, reason: str = "Protected branch cannot be targeted for direct execution or mutation") -> None:
        HardDenyViolation.__init__(
            self,
            action="main_branch_execution",
            reason=f"Branch '{branch_name}' is protected. {reason}",
        )
        self.branch_name = branch_name


class PrimaryCheckoutViolationError(WorkspaceError, HardDenyViolation):
    """Raised when an operation attempts to modify the primary human checkout directly."""

    def __init__(self, target_path: str, reason: str = "Primary checkout is read-only. File mutations must occur in dedicated worktrees.") -> None:
        HardDenyViolation.__init__(
            self,
            action="primary_checkout_mutation",
            reason=f"Path '{target_path}' points to primary checkout. {reason}",
        )
        self.target_path = target_path


class GitCommandError(WorkspaceError):
    """Raised when an underlying Git command fails unexpectedly."""

    def __init__(self, cmd: List[str], exit_code: int, stdout: str, stderr: str) -> None:
        cmd_str = " ".join(cmd)
        message = f"Git command failed [exit {exit_code}]: {cmd_str}\nStderr: {stderr.strip()}\nStdout: {stdout.strip()}"
        super().__init__(
            message=message,
            details={
                "cmd": cmd,
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr,
            },
        )
        self.cmd = cmd
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr


class WorktreeCollisionError(WorkspaceError):
    """Raised when worktree provisioning encounters a collision or duplicate path/branch."""

    def __init__(self, message: str, worktree_path: Optional[str] = None, branch: Optional[str] = None) -> None:
        super().__init__(
            message=message,
            details={"worktree_path": worktree_path, "branch": branch},
        )
        self.worktree_path = worktree_path
        self.branch = branch


class WorktreeNotFoundError(WorkspaceError):
    """Raised when a specified worktree does not exist or is not registered in Git."""

    def __init__(self, worktree_path: str) -> None:
        super().__init__(
            message=f"Worktree at '{worktree_path}' was not found or is not registered in Git.",
            details={"worktree_path": worktree_path},
        )
        self.worktree_path = worktree_path


class RepositoryValidationError(WorkspaceError):
    """Raised when a repository directory is missing, not a Git repository, or fails pattern assertion."""

    def __init__(self, repo_path: str, reason: str) -> None:
        super().__init__(
            message=f"Git repository validation failed for '{repo_path}': {reason}",
            details={"repo_path": repo_path, "reason": reason},
        )
        self.repo_path = repo_path
        self.reason = reason


__all__ = [
    "WorkspaceError",
    "BranchProtectionError",
    "PrimaryCheckoutViolationError",
    "GitCommandError",
    "WorktreeCollisionError",
    "WorktreeNotFoundError",
    "RepositoryValidationError",
    "DirtyRootError",
    "CollisionDetectedError",
    "HardDenyViolation",
    "SaclError",
]

"""SACL V1 Git Workspace Manager Implementation.

Implements IWorkspaceManager to provide isolated Git worktree provisioning,
Local Dirty-Root enforcement, branch inviolability, teardown lifecycle,
and modified file tracking.
"""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from sacl.contracts.exceptions import DirtyRootError
from sacl.contracts.interfaces import IWorkspaceManager
from sacl.workspace.dirty_root import check_clean_root, parse_porcelain_status
from sacl.workspace.exceptions import (
    BranchProtectionError,
    PrimaryCheckoutViolationError,
    RepositoryValidationError,
    WorkspaceError,
    WorktreeCollisionError,
    WorktreeNotFoundError,
)
from sacl.workspace.git_runner import GitRunner
from sacl.workspace.guards import (
    assert_branch_allowed,
    assert_not_primary_checkout,
    assert_valid_repository,
    normalize_branch_name,
)


@dataclass(frozen=True)
class WorktreeInfo:
    """Parsed metadata for a registered Git worktree."""
    path: Path
    head_sha: Optional[str] = None
    branch: Optional[str] = None
    is_bare: bool = False
    is_detached: bool = False


class WorkspaceManager(IWorkspaceManager):
    """Authoritative Git Workspace Manager for SACL V1."""

    def __init__(self, git_runner: Optional[GitRunner] = None) -> None:
        self.git_runner = git_runner or GitRunner()

    def check_clean_root(self, repo_path: Path) -> Tuple[bool, List[str]]:
        """Enforces the Local Dirty-Root Rule.

        Args:
            repo_path: Target Git repository primary checkout.

        Returns:
            Tuple of (is_clean: bool, dirty_files: List[str]).
        """
        assert_valid_repository(repo_path, self.git_runner)
        return check_clean_root(repo_path, self.git_runner)

    def list_worktrees(self, repo_path: Path) -> List[WorktreeInfo]:
        """Lists all registered worktrees for a repository using git worktree list --porcelain."""
        assert_valid_repository(repo_path, self.git_runner)
        res = self.git_runner.run(["worktree", "list", "--porcelain"], cwd=repo_path, check=True)

        worktrees: List[WorktreeInfo] = []
        current: dict = {}

        for raw_line in res.stdout.splitlines():
            line = raw_line.strip()
            if not line:
                if "worktree" in current:
                    worktrees.append(
                        WorktreeInfo(
                            path=Path(current["worktree"]).resolve(),
                            head_sha=current.get("head"),
                            branch=current.get("branch"),
                            is_bare=current.get("bare", False),
                            is_detached=current.get("detached", False),
                        )
                    )
                    current = {}
                continue

            if line.startswith("worktree "):
                if "worktree" in current:
                    worktrees.append(
                        WorktreeInfo(
                            path=Path(current["worktree"]).resolve(),
                            head_sha=current.get("head"),
                            branch=current.get("branch"),
                            is_bare=current.get("bare", False),
                            is_detached=current.get("detached", False),
                        )
                    )
                    current = {}
                current["worktree"] = line[len("worktree ") :].strip()
            elif line.startswith("HEAD "):
                current["head"] = line[len("HEAD ") :].strip()
            elif line.startswith("branch refs/heads/"):
                current["branch"] = line[len("branch refs/heads/") :].strip()
            elif line == "bare":
                current["bare"] = True
            elif line == "detached":
                current["detached"] = True

        if "worktree" in current:
            worktrees.append(
                WorktreeInfo(
                    path=Path(current["worktree"]).resolve(),
                    head_sha=current.get("head"),
                    branch=current.get("branch"),
                    is_bare=current.get("bare", False),
                    is_detached=current.get("detached", False),
                )
            )

        return worktrees

    def provision_worktree(
        self,
        repo_path: Path,
        branch_name: str,
        worktree_path: Path,
        base_ref: str = "HEAD",
    ) -> Path:
        """Provisions an isolated Git worktree for an agent.

        Enforces:
        1. Target repository validity.
        2. Local Dirty-Root Rule on primary repository.
        3. Branch Inviolability (MAIN_BRANCH_NOT_ALLOWED).
        4. Primary Checkout Protection (PRIMARY_CHECKOUT_NOT_ALLOWED).
        5. Worktree collision and duplicate branch avoidance.
        6. Clean worktree reuse if already provisioned and registered.

        Args:
            repo_path: Primary Git repository directory.
            branch_name: Task branch name for the agent worktree.
            worktree_path: Target directory where worktree will be provisioned.
            base_ref: Base reference (commit SHA, tag, or branch e.g. 'origin/main' or 'HEAD').

        Returns:
            Resolved Path of the provisioned worktree.

        Raises:
            DirtyRootError: If primary repository is dirty.
            BranchProtectionError: If branch_name is protected.
            PrimaryCheckoutViolationError: If worktree_path points to primary checkout.
            WorktreeCollisionError: If path/branch collisions occur.
        """
        repo_path = repo_path.resolve()
        assert_valid_repository(repo_path, self.git_runner)

        # 1. Dirty-root rule on primary checkout
        is_clean, dirty_files = self.check_clean_root(repo_path)
        if not is_clean:
            raise DirtyRootError(target_path=str(repo_path), dirty_files=dirty_files)

        # 2. Branch protection
        clean_branch = normalize_branch_name(branch_name)
        assert_branch_allowed(clean_branch)

        # 3. Primary checkout protection
        assert_not_primary_checkout(worktree_path, repo_path)

        resolved_target = worktree_path.resolve()
        existing_worktrees = self.list_worktrees(repo_path)

        # 4. Collision check against existing worktrees on disk
        target_wt_info = next((wt for wt in existing_worktrees if wt.path == resolved_target), None)

        if resolved_target.exists():
            if target_wt_info is None:
                raise WorktreeCollisionError(
                    f"Directory '{resolved_target}' exists on disk but is not registered in git worktree list. "
                    "Safety rule: will not overwrite or delete existing unmanaged folder.",
                    worktree_path=str(resolved_target),
                    branch=clean_branch,
                )

            # Registered worktree exists: verify branch and clean status
            if target_wt_info.branch != clean_branch:
                raise WorktreeCollisionError(
                    f"Existing worktree at '{resolved_target}' is on branch '{target_wt_info.branch}', expected '{clean_branch}'.",
                    worktree_path=str(resolved_target),
                    branch=clean_branch,
                )

            wt_clean, wt_dirty = check_clean_root(resolved_target, self.git_runner)
            if not wt_clean:
                raise DirtyRootError(target_path=str(resolved_target), dirty_files=wt_dirty)

            return resolved_target

        # 5. Check if branch is already checked out elsewhere
        branch_in_use = next((wt for wt in existing_worktrees if wt.branch == clean_branch), None)
        if branch_in_use is not None:
            raise WorktreeCollisionError(
                f"Branch '{clean_branch}' is already checked out at '{branch_in_use.path}'. Cannot create duplicate worktree.",
                worktree_path=str(resolved_target),
                branch=clean_branch,
            )

        # 6. Ensure parent directory exists
        resolved_target.parent.mkdir(parents=True, exist_ok=True)

        # 7. Check if local branch already exists
        check_local = self.git_runner.run(
            ["show-ref", "--verify", "--quiet", f"refs/heads/{clean_branch}"],
            cwd=repo_path,
        )
        local_branch_exists = (check_local.exit_code == 0)

        # Check if remote tracking branch exists
        check_remote = self.git_runner.run(
            ["show-ref", "--verify", "--quiet", f"refs/remotes/origin/{clean_branch}"],
            cwd=repo_path,
        )
        remote_branch_exists = (check_remote.exit_code == 0)

        # 8. Create worktree
        if local_branch_exists:
            cmd = ["worktree", "add", str(resolved_target), clean_branch]
        elif remote_branch_exists:
            cmd = ["worktree", "add", "-b", clean_branch, str(resolved_target), f"origin/{clean_branch}"]
        else:
            cmd = ["worktree", "add", "-b", clean_branch, str(resolved_target), base_ref]

        res = self.git_runner.run(cmd, cwd=repo_path)
        if not res.success:
            res.check()

        # 9. Post-creation verification
        if not resolved_target.exists():
            raise WorkspaceError(f"Worktree path '{resolved_target}' not found after provisioning.")

        branch_res = self.git_runner.run(["rev-parse", "--abbrev-ref", "HEAD"], cwd=resolved_target, check=True)
        current_branch = normalize_branch_name(branch_res.stdout)
        if current_branch != clean_branch:
            raise WorkspaceError(
                f"Worktree verification failed: branch is '{current_branch}', expected '{clean_branch}'."
            )

        return resolved_target

    def teardown_worktree(
        self,
        repo_path: Path,
        worktree_path: Path,
        force: bool = False,
    ) -> None:
        """Remove only a *registered, clean* worktree, never arbitrary directories.

        Forced removal and filesystem rmtree are intentionally prohibited.
        Git itself removes only the worktree it has registered, and errors are
        propagated to preserve forensic evidence and human uncommitted edits.
        """
        repo = Path(repo_path).resolve()
        raw_target = Path(worktree_path)
        if raw_target.is_symlink():
            raise WorkspaceError("Refusing teardown via symlink.")
        target = raw_target.resolve()
        assert_valid_repository(repo, self.git_runner)
        assert_not_primary_checkout(target, repo)
        if force:
            raise WorkspaceError("Forced worktree teardown is disabled for data safety.")

        existing = self.list_worktrees(repo)
        record = next(
            (wt for wt in existing[1:] if wt.path == target),
            None,
        )
        if record is None:
            raise WorktreeNotFoundError(str(target))
        if not target.is_dir():
            raise WorktreeNotFoundError(str(target))

        is_clean, dirty = check_clean_root(target, self.git_runner)
        if not is_clean:
            raise DirtyRootError(target_path=str(target), dirty_files=dirty)

        self.git_runner.run(
            ["worktree", "remove", str(target)], cwd=repo, check=True,
        )

    def get_modified_files(self, worktree_path: Path, base_ref: str = "HEAD") -> List[str]:
        """Collects files modified in worktree relative to base reference.

        Includes both committed diffs against base_ref and uncommitted working-tree changes.

        Args:
            worktree_path: Worktree directory.
            base_ref: Reference to diff against (e.g. 'origin/main' or 'HEAD').

        Returns:
            Sorted, deduplicated list of POSIX-normalized relative file paths.
        """
        resolved_path = worktree_path.resolve()
        assert_valid_repository(resolved_path, self.git_runner)

        modified: set[str] = set()

        # 1. Never mask a failed Git status as a clean worktree.
        status_res = self.git_runner.run(
            ["status", "--porcelain"], cwd=resolved_path, check=True,
        )
        modified.update(parse_porcelain_status(status_res.stdout))

        # 2. Resolve committed modifications; both ref strategies must fail
        # explicitly if unavailable, never returning an empty list.
        diff_res = self.git_runner.run(
            ["diff", "--name-only", f"{base_ref}...HEAD"], cwd=resolved_path,
        )
        if not diff_res.success:
            diff_res = self.git_runner.run(
                ["diff", "--name-only", base_ref, "HEAD"], cwd=resolved_path,
            )
            diff_res.check()

        for raw_line in diff_res.stdout.splitlines():
            line = raw_line.strip()
            if line:
                modified.add(line.replace("\\", "/"))

        return sorted(modified)


__all__ = ["WorkspaceManager", "WorktreeInfo"]

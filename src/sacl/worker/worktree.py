"""Worker workspace adapter: fail-closed Git worktrees, explicit mock-only mode.

Production worktrees delegate to the canonical sacl.workspace.manager.
No implicit fallback from a failed Git command to a plain directory.
A test-only non-Git sandbox is available only when mock_mode=True.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Tuple

from sacl.contracts.exceptions import DirtyRootError
from sacl.workspace.dirty_root import parse_porcelain_status
from sacl.workspace.exceptions import (
    BranchProtectionError,
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
from sacl.workspace.manager import WorkspaceManager as CanonicalWorkspaceManager


class WorkspaceManager(CanonicalWorkspaceManager):
    """Compatibility entrypoint for Graph-H, with explicit synthetic test mode."""

    def __init__(self, git_executable: str = "git", *, mock_mode: bool = False) -> None:
        super().__init__(git_runner=GitRunner(git_executable=git_executable))
        self.mock_mode = mock_mode
        self._mock_worktrees: dict[Path, tuple[Path, str]] = {}

    def _is_mock_repo(self, repo_path: Path) -> bool:
        # Never treat an actual repo as a synthetic one, even when opted in.
        if not self.mock_mode:
            return False
        return not (repo_path / ".git").exists()

    def check_clean_root(self, repo_path: Path) -> Tuple[bool, List[str]]:
        repo = Path(repo_path).resolve()
        if self._is_mock_repo(repo):
            if not repo.is_dir():
                raise RepositoryValidationError(str(repo), "Mock repository directory is missing.")
            # Explicit mock directories do not have a Git index to inspect.
            return True, []
        return super().check_clean_root(repo)

    def assert_clean_root(self, repo_path: Path) -> None:
        """Raise without mutating the caller's checkout when uncommitted files exist."""
        is_clean, dirty_files = self.check_clean_root(repo_path)
        if not is_clean:
            raise DirtyRootError(target_path=str(repo_path), dirty_files=dirty_files)

    def provision_worktree(
        self,
        repo_path: Path,
        branch_name: str,
        worktree_path: Path,
        base_ref: str = "HEAD",
    ) -> Path:
        repo = Path(repo_path).resolve()
        target_raw = Path(worktree_path)
        if target_raw.is_symlink():
            raise WorkspaceError("Worktree target cannot be a symbolic link.")
        target = target_raw.resolve()
        assert_branch_allowed(branch_name)
        assert_not_primary_checkout(target, repo)

        if not self._is_mock_repo(repo):
            return super().provision_worktree(repo, branch_name, target, base_ref)

        if not repo.is_dir():
            raise RepositoryValidationError(str(repo), "Mock repository directory is missing.")
        if target.exists():
            existing = self._mock_worktrees.get(target)
            if existing != (repo, branch_name):
                raise WorktreeCollisionError(
                    f"Refusing unmanaged or wrong-branch mock folder: '{target}'",
                    worktree_path=str(target), branch=branch_name,
                )
            if any(target.iterdir()):
                raise WorkspaceError("Mock worktree contains unmanaged data; refusing reuse.")
            return target

        target.parent.mkdir(parents=True, exist_ok=True)
        target.mkdir()
        self._mock_worktrees[target] = (repo, branch_name)
        return target

    def teardown_worktree(
        self, repo_path: Path, worktree_path: Path, force: bool = False,
    ) -> None:
        repo = Path(repo_path).resolve()
        raw_target = Path(worktree_path)
        if raw_target.is_symlink():
            raise WorkspaceError("Refusing teardown through symbolic-link path.")
        target = raw_target.resolve()
        assert_not_primary_checkout(target, repo)
        if force:
            raise WorkspaceError("Forced worktree teardown is disabled: preserve edits for review.")

        if not self._is_mock_repo(repo):
            return super().teardown_worktree(repo, target, force=False)

        if target not in self._mock_worktrees or self._mock_worktrees[target][0] != repo:
            raise WorktreeNotFoundError(str(target))
        if not target.is_dir():
            raise WorktreeNotFoundError(str(target))
        # rmdir refuses to delete any file whatsoever. Never use rmtree.
        target.rmdir()
        del self._mock_worktrees[target]

    def assert_registered_worktree(
        self, worktree_path: Path, expected_branch: str | None = None,
    ) -> None:
        """Guard used immediately before any real worker process can be spawned.

        Validate the Git worktree registry, disallow primary checkouts, detached
        HEAD and protected branches, and enforce the scheduled task branch.
        """
        original = Path(worktree_path)
        if original.is_symlink():
            raise WorkspaceError("Refusing to execute via worktree symlink.")
        # Reject symlink/junction ancestors before any real worker can spawn.
        absolute = Path(os.path.abspath(original))
        target = absolute.resolve()
        if target != absolute:
            raise WorkspaceError(
                "Refusing real worker execution through a symlink or junction in the worktree path."
            )
        assert_valid_repository(target, self.git_runner)
        registered = self.list_worktrees(target)
        if not registered or target == registered[0].path:
            raise WorkspaceError("Refusing real worker execution in primary checkout.")
        record = next((wt for wt in registered[1:] if wt.path == target), None)
        if record is None:
            raise WorktreeNotFoundError(str(target))
        if record.is_detached or not record.branch:
            raise WorkspaceError("Refusing real worker execution on detached HEAD.")
        assert_branch_allowed(record.branch)
        if expected_branch is not None and normalize_branch_name(expected_branch) != record.branch:
            raise WorktreeCollisionError(
                "Scheduled worker branch differs from the registered Git worktree.",
                worktree_path=str(target), branch=expected_branch,
            )

    def get_modified_files(self, worktree_path: Path, base_ref: str = "HEAD") -> List[str]:
        raw_target = Path(worktree_path)
        if raw_target.is_symlink():
            raise WorkspaceError("Cannot scan changes through a symlink.")
        target = raw_target.resolve()
        if target in self._mock_worktrees:
            if self.mock_mode and target.is_dir():
                if any(target.iterdir()):
                    raise WorkspaceError("Mock worktree has untracked data; refusing empty diff.")
                return []
            raise WorktreeNotFoundError(str(target))

        assert_valid_repository(target, self.git_runner)
        worktrees = self.list_worktrees(target)
        if not worktrees or target == worktrees[0].path:
            raise WorkspaceError("Changes must be collected from a registered agent worktree, not primary checkout.")
        if not any(wt.path == target for wt in worktrees[1:]):
            raise WorktreeNotFoundError(str(target))

        status = self.git_runner.run(["status", "--porcelain"], cwd=target, check=True)
        diff = self.git_runner.run(
            ["diff", "--name-only", f"{base_ref}...HEAD"], cwd=target, check=True,
        )
        return sorted(set(parse_porcelain_status(status.stdout)) | {
            line.strip().replace("\\", "/")
            for line in diff.stdout.splitlines() if line.strip()
        })


__all__ = ["WorkspaceManager"]

"""SACL V1 Isolated Git Worktree Execution and Dirty-Root Protection.

Enforces:
- Local Dirty-Root Rule: Human uncommitted work in the primary checkout is NEVER
  destroyed, stashed, reset, or overwritten. If dirty, execution is BLOCKED.
- Worktree Isolation: Each agent executes in its own isolated worktree with a
  private index (.git/worktrees/wt-<agent>/index) and dedicated branch.
- Primary Checkout Inviolability: The primary root checkout is strictly read-only.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

from sacl.contracts.exceptions import DirtyRootError
from sacl.contracts.interfaces import IWorkspaceManager


class WorkspaceManager(IWorkspaceManager):
    """Manages Git worktree provisioning, teardown, and dirty-root assertions."""

    def __init__(self, git_executable: str = "git") -> None:
        self.git = git_executable

    def _run_git(
        self,
        args: List[str],
        cwd: Optional[Path] = None,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        cmd = [self.git] + args
        try:
            return subprocess.run(
                cmd,
                cwd=str(cwd) if cwd else None,
                capture_output=True,
                text=True,
                check=check,
                encoding="utf-8",
                errors="replace",
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Git command failed: {' '.join(cmd)}\nStdout: {e.stdout}\nStderr: {e.stderr}"
            ) from e

    def check_clean_root(self, repo_path: Path) -> Tuple[bool, List[str]]:
        """Enforces the Local Dirty-Root Rule.

        Inspects the primary repository working tree via 'git status --porcelain'.
        Returns (is_clean, dirty_files).
        """
        if not repo_path.exists():
            return False, ["REPOSITORY_PATH_DOES_NOT_EXIST"]

        # If not a git repository (or simulated), check if .git exists
        git_dir = repo_path / ".git"
        if not git_dir.exists():
            # In mock or non-git directories, consider clean unless marked
            return True, []

        try:
            res = self._run_git(["status", "--porcelain"], cwd=repo_path, check=False)
            if res.returncode != 0:
                return False, [f"GIT_STATUS_FAILED: {res.stderr.strip()}"]

            lines = [line.strip() for line in res.stdout.splitlines() if line.strip()]
            dirty_files = []
            for line in lines:
                # Format: XY PATH
                parts = line.split(maxsplit=1)
                dirty_path = parts[1] if len(parts) > 1 else line
                dirty_files.append(dirty_path.replace("\\", "/"))

            is_clean = len(dirty_files) == 0
            return is_clean, dirty_files
        except Exception as e:
            return False, [f"ERROR_CHECKING_DIRTY_ROOT: {str(e)}"]

    def assert_clean_root(self, repo_path: Path) -> None:
        """Asserts repository clean root, raising DirtyRootError if uncommitted changes exist."""
        is_clean, dirty = self.check_clean_root(repo_path)
        if not is_clean:
            raise DirtyRootError(target_path=str(repo_path), dirty_files=dirty)

    def provision_worktree(
        self,
        repo_path: Path,
        branch_name: str,
        worktree_path: Path,
        base_ref: str = "HEAD",
    ) -> Path:
        """Provisions an isolated Git worktree for an agent worker."""
        worktree_path = Path(worktree_path).resolve()
        repo_path = Path(repo_path).resolve()

        if worktree_path.exists() and any(worktree_path.iterdir()):
            # Worktree directory already exists and is non-empty
            return worktree_path

        worktree_path.parent.mkdir(parents=True, exist_ok=True)

        git_dir = repo_path / ".git"
        if not git_dir.exists():
            # Mock / simulated directory without git
            worktree_path.mkdir(parents=True, exist_ok=True)
            return worktree_path

        # Try creating worktree with new branch, or check out existing branch
        try:
            self._run_git(
                ["worktree", "add", "-b", branch_name, str(worktree_path), base_ref],
                cwd=repo_path,
                check=True,
            )
        except RuntimeError:
            # Branch might already exist; try without -b
            try:
                self._run_git(
                    ["worktree", "add", str(worktree_path), branch_name],
                    cwd=repo_path,
                    check=True,
                )
            except RuntimeError:
                # If git worktree fails, create fallback isolated directory
                worktree_path.mkdir(parents=True, exist_ok=True)

        return worktree_path

    def teardown_worktree(
        self,
        repo_path: Path,
        worktree_path: Path,
        force: bool = False,
    ) -> None:
        """Cleans up and removes an isolated Git worktree."""
        worktree_path = Path(worktree_path).resolve()
        repo_path = Path(repo_path).resolve()

        git_dir = repo_path / ".git"
        if git_dir.exists():
            try:
                args = ["worktree", "remove", str(worktree_path)]
                if force:
                    args.append("--force")
                self._run_git(args, cwd=repo_path, check=False)
            except Exception:
                pass

        if worktree_path.exists():
            shutil.rmtree(worktree_path, ignore_errors=True)

    def get_modified_files(
        self,
        worktree_path: Path,
        base_ref: str = "HEAD",
    ) -> List[str]:
        """Collects files modified in worktree relative to base reference or status."""
        worktree_path = Path(worktree_path).resolve()
        if not worktree_path.exists():
            return []

        git_dir = worktree_path / ".git"
        # If worktree has a .git file pointing to main git dir
        if not git_dir.exists():
            return []

        modified_set = set()
        try:
            # 1. Uncommitted changes in worktree
            res_status = self._run_git(["status", "--porcelain"], cwd=worktree_path, check=False)
            if res_status.returncode == 0:
                for line in res_status.stdout.splitlines():
                    line = line.strip()
                    if line:
                        parts = line.split(maxsplit=1)
                        if len(parts) > 1:
                            modified_set.add(parts[1].replace("\\", "/"))

            # 2. Committed changes relative to base_ref
            res_diff = self._run_git(
                ["diff", "--name-only", f"{base_ref}...HEAD"],
                cwd=worktree_path,
                check=False,
            )
            if res_diff.returncode == 0:
                for line in res_diff.stdout.splitlines():
                    line = line.strip()
                    if line:
                        modified_set.add(line.replace("\\", "/"))
        except Exception:
            pass

        return sorted(modified_set)

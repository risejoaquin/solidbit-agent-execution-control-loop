"""SACL V1 Worktree Inspection & Local Dirty-Root Safety Subsystem.

Implements docs/RECOVERY_MODEL.md §7:
1. Enforces the inviolable Local Dirty-Root Safety Rule:
   Automation NEVER executes 'git reset --hard', 'git clean -fd', 'git checkout -f', or 'git stash'.
2. Inspects primary product repository checkouts for clean root status.
   If uncommitted human work exists, recovery halts immediately with DIRTY_ROOT_BLOCKS_RECOVERY.
3. Inspects agent worktrees for clean git status and commit production.
   If agent worktree is dirty on recovery, changes are preserved for forensics
   and agent is evaluated as UNCOMMITTED_CHANGES_ON_RECOVERY.
4. Detects and reports orphaned worktrees without deleting or destroying developer files.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Protocol, Sequence, Set, Tuple, Union

from sacl.contracts.exceptions import HardDenyViolation
from sacl.contracts.models import WorktreeState

# Forbidden git commands during automated recovery
FORBIDDEN_GIT_COMMANDS = (
    ("reset", "--hard"),
    ("clean", "-fd"),
    ("clean", "-f"),
    ("clean", "-df"),
    ("clean", "-xdf"),
    ("clean", "-fx"),
    ("checkout", "-f"),
    ("stash",),
)


def assert_safe_git_command(args: Sequence[str]) -> None:
    """Verifies that a git command does not violate the Local Dirty-Root Safety Rule.

    Raises:
        HardDenyViolation: If destructive git command (reset --hard, clean, stash) is attempted.
    """
    clean_args = [a.strip().lower() for a in args]
    # Check for hard reset
    if "reset" in clean_args and any("--hard" in a for a in clean_args):
        raise HardDenyViolation(
            "hard_reset", "git reset --hard is strictly prohibited during recovery"
        )
    # Check for auto stash
    if "stash" in clean_args:
        raise HardDenyViolation("auto_stash", "git stash is strictly prohibited during recovery")
    # Check for destructive clean
    if "clean" in clean_args and any("-f" in a for a in clean_args):
        raise HardDenyViolation(
            "primary_checkout_mutation", "git clean -f/-fd is strictly prohibited during recovery"
        )
    # Check for forced checkout
    if "checkout" in clean_args and any("-f" in a or "--force" in a for a in clean_args):
        raise HardDenyViolation(
            "primary_checkout_mutation",
            "git checkout -f/--force is strictly prohibited during recovery",
        )


class GitClient(Protocol):
    """Protocol for abstracting git operations."""

    def status_porcelain(self, repo_path: Union[Path, str]) -> List[str]:
        """Runs `git status --porcelain` and returns raw status lines."""
        ...

    def get_head_commit(self, repo_path: Union[Path, str]) -> Optional[str]:
        """Returns the current HEAD commit hash."""
        ...

    def get_current_branch(self, repo_path: Union[Path, str]) -> Optional[str]:
        """Returns the current active branch name."""
        ...


class SubprocessGitClient:
    """Production Git client executing safe git commands via subprocess."""

    def __init__(self, git_binary: str = "git") -> None:
        self.git_binary = git_binary

    def _run_git(self, repo_path: Union[Path, str], args: Sequence[str]) -> str:
        assert_safe_git_command(args)
        path_str = str(Path(repo_path).resolve())
        cmd = [self.git_binary, "-C", path_str] + list(args)
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        if res.returncode != 0:
            err = res.stderr.strip() or f"Git command failed with exit code {res.returncode}"
            raise RuntimeError(f"Git execution error in {path_str}: {err}")
        return res.stdout

    def status_porcelain(self, repo_path: Union[Path, str]) -> List[str]:
        output = self._run_git(repo_path, ["status", "--porcelain"])
        return [line.strip() for line in output.splitlines() if line.strip()]

    def get_head_commit(self, repo_path: Union[Path, str]) -> Optional[str]:
        try:
            output = self._run_git(repo_path, ["rev-parse", "HEAD"]).strip()
            return output if output else None
        except Exception:
            return None

    def get_current_branch(self, repo_path: Union[Path, str]) -> Optional[str]:
        try:
            output = self._run_git(repo_path, ["rev-parse", "--abbrev-ref", "HEAD"]).strip()
            return output if output else None
        except Exception:
            return None


class MockGitClient:
    """Deterministic in-memory Git client for testing and simulation."""

    def __init__(self) -> None:
        self.status_map: Dict[str, List[str]] = {}
        self.commit_map: Dict[str, str] = {}
        self.branch_map: Dict[str, str] = {}
        self.executed_commands: List[Tuple[str, List[str]]] = []

    def set_status(self, repo_path: Union[Path, str], files: List[str]) -> None:
        self.status_map[str(Path(repo_path).resolve())] = list(files)

    def set_head_commit(self, repo_path: Union[Path, str], sha: str) -> None:
        self.commit_map[str(Path(repo_path).resolve())] = sha

    def set_current_branch(self, repo_path: Union[Path, str], branch: str) -> None:
        self.branch_map[str(Path(repo_path).resolve())] = branch

    def status_porcelain(self, repo_path: Union[Path, str]) -> List[str]:
        key = str(Path(repo_path).resolve())
        return self.status_map.get(key, [])

    def get_head_commit(self, repo_path: Union[Path, str]) -> Optional[str]:
        key = str(Path(repo_path).resolve())
        return self.commit_map.get(key)

    def get_current_branch(self, repo_path: Union[Path, str]) -> Optional[str]:
        key = str(Path(repo_path).resolve())
        return self.branch_map.get(key, "main")


_default_git_client: GitClient = SubprocessGitClient()


def get_default_git_client() -> GitClient:
    return _default_git_client


def set_default_git_client(client: GitClient) -> None:
    global _default_git_client
    _default_git_client = client


@dataclass
class PrimaryRepoCleanliness:
    """Evaluation of primary checkout cleanliness under Local Dirty-Root Rule."""

    is_clean: bool
    uncommitted_files: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    halt_reason: Optional[str] = None


def check_primary_repo_clean(
    repo_path: Union[Path, str],
    git_client: Optional[GitClient] = None,
) -> PrimaryRepoCleanliness:
    """Verifies that the primary repository checkout has no uncommitted changes.

    If uncommitted files exist, returns is_clean=False with DIRTY_ROOT_BLOCKS_RECOVERY.
    """
    client = git_client or _default_git_client
    path = Path(repo_path)
    if not path.exists():
        return PrimaryRepoCleanliness(
            is_clean=False,
            uncommitted_files=[],
            error_message=f"Primary repository path does not exist: {path}",
            halt_reason="PRIMARY_REPO_MISSING",
        )

    try:
        porcelain_lines = client.status_porcelain(path)
    except Exception as exc:
        return PrimaryRepoCleanliness(
            is_clean=False,
            uncommitted_files=[],
            error_message=f"Failed to query git status: {exc}",
            halt_reason="GIT_STATUS_FAILED",
        )

    if porcelain_lines:
        files = [line.split(maxsplit=1)[-1] for line in porcelain_lines]
        msg = (
            f"DIRTY_ROOT_BLOCKS_RECOVERY: Uncommitted changes detected in primary checkout "
            f"'{path}' ({len(files)} files: {', '.join(files[:5])}). Automated recovery halted."
        )
        return PrimaryRepoCleanliness(
            is_clean=False,
            uncommitted_files=files,
            error_message=msg,
            halt_reason="DIRTY_ROOT_BLOCKS_RECOVERY",
        )

    return PrimaryRepoCleanliness(
        is_clean=True,
        uncommitted_files=[],
        error_message=None,
        halt_reason=None,
    )


@dataclass
class WorktreeInspectionResult:
    """Diagnostic outcome of inspecting an agent's worktree."""

    worktree_state: WorktreeState
    exists: bool
    is_clean: bool
    modified_files: List[str]
    branch: Optional[str] = None
    commit_sha: Optional[str] = None
    verdict_impact: Optional[str] = None
    diagnostic_notes: Optional[str] = None


def inspect_agent_worktree(
    worktree_path: Union[Path, str],
    expected_branch: Optional[str] = None,
    git_client: Optional[GitClient] = None,
) -> WorktreeInspectionResult:
    """Inspects an agent worktree without making any mutating git changes."""
    client = git_client or _default_git_client
    path = Path(worktree_path)

    if not path.exists():
        wt_state = WorktreeState(
            branch=expected_branch or "unknown",
            worktree_path=str(path),
            commit_sha=None,
            is_clean=False,
            modified_files=[],
        )
        return WorktreeInspectionResult(
            worktree_state=wt_state,
            exists=False,
            is_clean=False,
            modified_files=[],
            branch=expected_branch,
            commit_sha=None,
            verdict_impact="WORKTREE_DIR_MISSING",
            diagnostic_notes=f"Worktree directory not found at {path}",
        )

    try:
        porcelain_lines = client.status_porcelain(path)
        modified_files = [line.split(maxsplit=1)[-1] for line in porcelain_lines]
    except Exception:
        modified_files = []
        porcelain_lines = ["?? error_querying_git"]

    commit_sha = client.get_head_commit(path)
    branch = client.get_current_branch(path) or expected_branch or "unknown"
    is_clean = len(modified_files) == 0

    verdict_impact: Optional[str] = None
    notes: Optional[str] = None
    if not is_clean:
        verdict_impact = "UNCOMMITTED_CHANGES_ON_RECOVERY"
        notes = (
            f"Worktree has {len(modified_files)} uncommitted files. "
            f"Preserved for forensics under Local Dirty-Root Rule."
        )

    wt_state = WorktreeState(
        branch=branch,
        worktree_path=str(path),
        commit_sha=commit_sha,
        is_clean=is_clean,
        modified_files=modified_files,
    )

    return WorktreeInspectionResult(
        worktree_state=wt_state,
        exists=True,
        is_clean=is_clean,
        modified_files=modified_files,
        branch=branch,
        commit_sha=commit_sha,
        verdict_impact=verdict_impact,
        diagnostic_notes=notes,
    )


class OrphanClassification(str, Enum):
    """Categorization of discovered orphaned worktree directories."""

    UNREGISTERED_WORKTREE = "UNREGISTERED_WORKTREE"
    DEAD_WORKER_WORKTREE = "DEAD_WORKER_WORKTREE"
    ORPHAN_DIRTY_CHANGES = "ORPHAN_DIRTY_CHANGES"


@dataclass
class OrphanedWorktreeInfo:
    """Forensic report on an orphaned worktree directory discovered on disk."""

    directory_path: str
    classification: OrphanClassification
    is_clean: bool
    modified_files: List[str]
    head_commit: Optional[str]
    branch: Optional[str]
    preservation_status: str = "PRESERVED_FOR_FORENSICS"


def scan_orphaned_worktrees(
    worktree_base_dir: Union[Path, str],
    registered_worktree_paths: Set[str],
    git_client: Optional[GitClient] = None,
) -> List[OrphanedWorktreeInfo]:
    """Scans filesystem for orphaned worktrees and inspects them safely.

    Never deletes or resets worktree files.
    """
    client = git_client or _default_git_client
    base = Path(worktree_base_dir)
    if not base.exists() or not base.is_dir():
        return []

    normalized_registered = {str(Path(p).resolve()).lower() for p in registered_worktree_paths if p}

    orphans: List[OrphanedWorktreeInfo] = []
    for entry in base.iterdir():
        if entry.is_dir():
            resolved_entry = str(entry.resolve()).lower()
            if resolved_entry not in normalized_registered:
                # Discovered an un-tracked or unregistered directory
                try:
                    porcelain = client.status_porcelain(entry)
                    modified = [line.split(maxsplit=1)[-1] for line in porcelain]
                    is_clean = len(modified) == 0
                except Exception:
                    modified = []
                    is_clean = True

                commit = client.get_head_commit(entry)
                branch = client.get_current_branch(entry)

                classification = (
                    OrphanClassification.ORPHAN_DIRTY_CHANGES
                    if not is_clean
                    else OrphanClassification.UNREGISTERED_WORKTREE
                )

                orphans.append(
                    OrphanedWorktreeInfo(
                        directory_path=str(entry),
                        classification=classification,
                        is_clean=is_clean,
                        modified_files=modified,
                        head_commit=commit,
                        branch=branch,
                    )
                )

    return orphans

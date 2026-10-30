"""SACL V1 Safe Git Subprocess Runner.

Executes Git commands with deterministic isolation, security guard interceptors,
fail-closed error handling, and strict local-only execution boundaries.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from sacl.contracts.exceptions import HardDenyViolation
from sacl.workspace.exceptions import GitCommandError


@dataclass(frozen=True)
class GitResult:
    """Immutable result of a Git command execution."""

    success: bool
    exit_code: int
    stdout: str
    stderr: str
    cmd: List[str]

    def check(self) -> None:
        """Raises GitCommandError if the command failed."""
        if not self.success:
            raise GitCommandError(self.cmd, self.exit_code, self.stdout, self.stderr)


class GitRunner:
    """Safe wrapper for invoking git subprocesses under constitutional constraints."""

    # Prohibited operations in SACL V1
    BANNED_SUBCOMMANDS = frozenset({"push"})

    def __init__(self, git_executable: str = "git") -> None:
        self.git_executable = git_executable

    def _assert_command_safety(self, args: Sequence[str]) -> None:
        """Intercepts and strictly blocks hard-denied git actions."""
        if not args:
            return

        cmd_lower = [str(a).lower() for a in args]

        # Determine primary git subcommand (ignoring global flags like -C)
        subcommand = ""
        for a in cmd_lower:
            if not a.startswith("-"):
                subcommand = a
                break

        # 1. Git push is permanently prohibited
        if subcommand == "push":
            raise HardDenyViolation(
                action="remote_production_execution",
                reason="git push is strictly prohibited in SACL V1. Local-only commits permitted.",
            )

        # 2. Hard reset is strictly prohibited
        if subcommand == "reset" and "--hard" in cmd_lower:
            raise HardDenyViolation(
                action="hard_reset",
                reason="git reset --hard violates Local Dirty-Root Rule and human workspace safety.",
            )

        # 3. Aggressive git clean is prohibited
        if subcommand == "clean" and any(f in cmd_lower for f in ("-f", "-fd", "-fx", "-fxd")):
            raise HardDenyViolation(
                action="primary_checkout_mutation",
                reason="git clean -f/fd violates human workspace safety.",
            )

        # 4. Auto stash is prohibited
        if subcommand == "stash":
            raise HardDenyViolation(
                action="auto_stash",
                reason="git stash on uncommitted changes is prohibited by Local Dirty-Root Rule.",
            )

    def run(
        self,
        args: Sequence[str],
        cwd: Path,
        check: bool = False,
        extra_env: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = 60.0,
    ) -> GitResult:
        """Executes a git command inside the specified working directory.

        Args:
            args: Git command arguments (e.g. ['status', '--porcelain']).
            cwd: Working directory where git should execute.
            check: If True, raises GitCommandError on non-zero exit code.
            extra_env: Additional environment variables.
            timeout: Subprocess timeout in seconds.

        Returns:
            GitResult containing exit code, stdout, stderr.
        """
        self._assert_command_safety(args)

        full_cmd = [self.git_executable] + list(args)

        env = os.environ.copy()
        # Ensure git never hangs on interactive credential or terminal prompts
        env["GIT_TERMINAL_PROMPT"] = "0"
        env["GIT_PAGER"] = "cat"
        if extra_env:
            env.update(extra_env)

        try:
            process = subprocess.run(
                full_cmd,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                timeout=timeout,
                shell=False,
            )
            result = GitResult(
                success=(process.returncode == 0),
                exit_code=process.returncode,
                stdout=process.stdout,
                stderr=process.stderr,
                cmd=full_cmd,
            )
        except subprocess.TimeoutExpired as exc:
            result = GitResult(
                success=False,
                exit_code=-1,
                stdout=exc.stdout or "" if isinstance(exc.stdout, str) else "",
                stderr=f"Command timed out after {timeout} seconds: {exc}",
                cmd=full_cmd,
            )
        except FileNotFoundError:
            result = GitResult(
                success=False,
                exit_code=127,
                stdout="",
                stderr=f"Git executable '{self.git_executable}' not found in PATH.",
                cmd=full_cmd,
            )

        if check:
            result.check()

        return result


__all__ = ["GitRunner", "GitResult"]

"""SACL V1 Collision-Safe Workspace Primitives and Path Resolvers.

Provides deterministic naming, path containment validation, and path traversal defense
(Zip Slip mitigation) for multi-agent worktrees and task branches.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from sacl.workspace.exceptions import BranchProtectionError, WorkspaceError
from sacl.workspace.guards import is_protected_branch

_SAFE_IDENTIFIER_PATTERN = re.compile(r"^[a-zA-Z0-9_\-\.]+$")


def sanitize_identifier(value: str, fallback_prefix: str = "item") -> str:
    """Sanitizes an identifier to prevent directory traversal or invalid git characters."""
    v = value.strip().replace("\\", "/").split("/")[-1].strip()
    # Replace any character outside [a-zA-Z0-9_.-] with hyphen
    sanitized = re.sub(r"[^a-zA-Z0-9_\-\.]", "-", v)
    sanitized = re.sub(r"-+", "-", sanitized).strip("-.")
    if not sanitized:
        return f"{fallback_prefix}-default"
    return sanitized


def validate_path_within_root(target_path: Path, root_path: Path) -> Path:
    """Validates that target_path resolves strictly within root_path (anti-traversal defense).

    Raises:
        WorkspaceError: If target_path escapes root_path.
    """
    try:
        resolved_root = root_path.resolve()
        resolved_target = target_path.resolve()
    except Exception as exc:
        raise WorkspaceError(f"Path resolution failed: {exc}")

    try:
        resolved_target.relative_to(resolved_root)
    except ValueError:
        raise WorkspaceError(
            f"Path traversal violation: '{resolved_target}' escapes designated root '{resolved_root}'."
        )

    return resolved_target


def get_agent_worktree_path(
    worktree_root: Path,
    agent_id: str,
    wave_id: Optional[str] = None,
) -> Path:
    """Generates a collision-safe, directory-traversal-guarded worktree path.

    Args:
        worktree_root: Root directory where agent worktrees are hosted.
        agent_id: Identifier of the agent worker.
        wave_id: Optional wave identifier.

    Returns:
        Resolved Path for the agent worktree.

    Raises:
        WorkspaceError: If path escapes worktree_root.
    """
    safe_agent = sanitize_identifier(agent_id, fallback_prefix="agent")

    if wave_id:
        safe_wave = sanitize_identifier(wave_id, fallback_prefix="wave")
        candidate = worktree_root / safe_wave / f"wt-{safe_agent}"
    else:
        candidate = worktree_root / f"wt-{safe_agent}"

    return validate_path_within_root(candidate, worktree_root)


def generate_task_branch_name(
    agent_id: str,
    wave_id: Optional[str] = None,
    task_slug: Optional[str] = None,
    prefix: Optional[str] = "sacl",
) -> str:
    """Generates an isolated task branch name adhering to branch protection rules.

    Args:
        agent_id: Unique agent identifier.
        wave_id: Optional wave identifier.
        task_slug: Optional descriptive slug for the task.
        prefix: Namespace prefix (default: 'sacl'). If empty or None, no prefix is added.

    Returns:
        Canonical branch name.

    Raises:
        BranchProtectionError: If generated name conflicts with protected branches.
    """
    parts = []
    if prefix:
        safe_prefix = sanitize_identifier(prefix, fallback_prefix="sacl")
        parts.append(safe_prefix)

    if wave_id:
        parts.append(sanitize_identifier(wave_id, fallback_prefix="wave"))
    if task_slug:
        parts.append(sanitize_identifier(task_slug, fallback_prefix="task"))

    safe_agent = sanitize_identifier(agent_id, fallback_prefix="agent")
    parts.append(safe_agent)

    branch_name = "/".join(parts)

    if is_protected_branch(branch_name):
        raise BranchProtectionError(
            branch_name=branch_name,
            reason="Generated task branch name collided with protected branch pattern.",
        )

    return branch_name


__all__ = [
    "sanitize_identifier",
    "validate_path_within_root",
    "get_agent_worktree_path",
    "generate_task_branch_name",
]

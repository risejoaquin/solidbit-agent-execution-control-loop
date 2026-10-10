"""SACL V1 Workspace Subsystem.

Provides Git repository/worktree guards, Local Dirty-Root enforcement,
branch protection, worktree provisioning/teardown lifecycle,
local-only commit helpers, and collision-safe multi-agent primitives.
"""

from __future__ import annotations

from sacl.workspace.collision import (
    assert_no_collisions,
    detect_file_collisions,
    evaluate_wave_readiness,
)
from sacl.workspace.commit_helper import (
    DEFAULT_AUTHOR_EMAIL,
    DEFAULT_AUTHOR_NAME,
    get_current_branch,
    get_head_commit_sha,
    get_worktree_status,
    stage_and_commit,
)
from sacl.workspace.dirty_root import (
    assert_clean_root,
    check_clean_root,
    parse_porcelain_status,
)
from sacl.workspace.exceptions import (
    BranchProtectionError,
    CollisionDetectedError,
    DirtyRootError,
    GitCommandError,
    HardDenyViolation,
    PrimaryCheckoutViolationError,
    RepositoryValidationError,
    SaclError,
    WorkspaceError,
    WorktreeCollisionError,
    WorktreeNotFoundError,
)
from sacl.workspace.git_runner import (
    GitResult,
    GitRunner,
)
from sacl.workspace.guards import (
    DEFAULT_PROTECTED_BRANCHES,
    assert_branch_allowed,
    assert_not_primary_checkout,
    assert_remote_origin,
    assert_valid_repository,
    is_protected_branch,
    normalize_branch_name,
    verify_remote_origin,
)
from sacl.workspace.manager import (
    WorkspaceManager,
    WorktreeInfo,
)
from sacl.workspace.primitives import (
    generate_task_branch_name,
    get_agent_worktree_path,
    sanitize_identifier,
    validate_path_within_root,
)

__all__ = [
    # Manager & Interface
    "WorkspaceManager",
    "WorktreeInfo",
    # Runner & Result
    "GitRunner",
    "GitResult",
    # Dirty Root
    "check_clean_root",
    "assert_clean_root",
    "parse_porcelain_status",
    # Guards
    "DEFAULT_PROTECTED_BRANCHES",
    "normalize_branch_name",
    "is_protected_branch",
    "assert_branch_allowed",
    "assert_valid_repository",
    "assert_not_primary_checkout",
    "verify_remote_origin",
    "assert_remote_origin",
    # Commits
    "DEFAULT_AUTHOR_NAME",
    "DEFAULT_AUTHOR_EMAIL",
    "get_head_commit_sha",
    "get_current_branch",
    "stage_and_commit",
    "get_worktree_status",
    # Collisions
    "detect_file_collisions",
    "assert_no_collisions",
    "evaluate_wave_readiness",
    # Primitives
    "sanitize_identifier",
    "validate_path_within_root",
    "get_agent_worktree_path",
    "generate_task_branch_name",
    # Exceptions
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

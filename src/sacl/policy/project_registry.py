"""SACL V1 Project Registry Manager.

Authoritative local authority for registered projects, canonical filesystem roots,
and project-level concurrency and risk policies.

Constitutional Invariant (ADR-009):
The Project Registry is the sole local authority for filesystem roots.
Packages identify registered projects but cannot redirect execution outside
local registry policy.
"""

from __future__ import annotations

import json
import ntpath
import os
from pathlib import Path, PureWindowsPath
from typing import Any, Dict, List, Optional, Union

from sacl.contracts.exceptions import ContractValidationError, PolicyDeniedError
from sacl.contracts.invariants import RiskTier
from sacl.contracts.models import ConcurrencyPolicy, ProjectRegistry, ProjectRegistryEntry
from sacl.contracts.schema_validator import SchemaValidator, get_default_validator


def normalize_fs_path(p: Union[str, Path]) -> str:
    """Normalize native paths and compare registered Windows roots across OSes.

    On a POSIX CI runner, a Windows absolute path must remain a Windows
    absolute path: pathlib.Path would otherwise interpret it as a relative
    filename under the checkout. Windows-native hosts continue resolving
    their paths through pathlib, including filesystem symlinks.
    """
    raw = str(p)
    if os.name != "nt" and PureWindowsPath(raw).is_absolute():
        return ntpath.normcase(ntpath.normpath(raw))
    resolved = Path(p).resolve()
    return os.path.normcase(os.path.normpath(str(resolved)))


def is_same_or_subpath(target: Union[str, Path], root: Union[str, Path]) -> bool:
    """Check a path boundary, never a string-prefix match."""
    norm_target = normalize_fs_path(target)
    norm_root = normalize_fs_path(root)
    if norm_target == norm_root:
        return True

    if os.name != "nt":
        root_is_windows = PureWindowsPath(norm_root).is_absolute()
        target_is_windows = PureWindowsPath(norm_target).is_absolute()
        if root_is_windows or target_is_windows:
            # Never compare unrelated path syntaxes or different drives.
            if not (root_is_windows and target_is_windows):
                return False
            try:
                return ntpath.commonpath((norm_target, norm_root)) == norm_root
            except ValueError:
                return False

    try:
        Path(norm_target).relative_to(Path(norm_root))
        return True
    except ValueError:
        return False


class ProjectRegistryManager:
    """Manages project registrations, root validation, and concurrency policies."""

    def __init__(
        self,
        registry: ProjectRegistry,
        validator: Optional[SchemaValidator] = None,
    ) -> None:
        self.validator = validator or get_default_validator()
        self._registry = registry
        self._validate_registry_invariants(self._registry)
        self._projects_by_id: Dict[str, ProjectRegistryEntry] = {
            p.project_id: p for p in self._registry.projects
        }
        self._projects_by_repo: Dict[str, ProjectRegistryEntry] = {
            p.repository.lower(): p for p in self._registry.projects
        }

    def _validate_registry_invariants(self, registry: ProjectRegistry) -> None:
        """Enforces schema conformance and architectural constraints."""
        self.validator.validate_project_registry(registry.to_dict())
        for project in registry.projects:
            if project.concurrency_policy and project.concurrency_policy.max_mutating_jobs != 1:
                raise ContractValidationError(
                    schema_name="project-registry",
                    message=f"Project '{project.project_id}' specifies max_mutating_jobs={project.concurrency_policy.max_mutating_jobs}, but baseline is strictly 1.",
                )

    @property
    def registry(self) -> ProjectRegistry:
        """Returns the underlying ProjectRegistry model."""
        return self._registry

    def list_projects(self) -> List[ProjectRegistryEntry]:
        """Returns all registered projects."""
        return list(self._registry.projects)

    def get_project(self, project_id: str) -> Optional[ProjectRegistryEntry]:
        """Finds project by stable project_id."""
        return self._projects_by_id.get(project_id)

    def get_project_by_repo(self, repository: str) -> Optional[ProjectRegistryEntry]:
        """Finds project by repository identifier (e.g. org/repo)."""
        return self._projects_by_repo.get(repository.strip().lower())

    def require_project(self, project_id: str) -> ProjectRegistryEntry:
        """Retrieves project by ID or raises PolicyDeniedError."""
        project = self.get_project(project_id)
        if not project:
            raise PolicyDeniedError(
                action="resolve_project",
                layer="PROJECT_REGISTRY",
                reason=f"Project '{project_id}' is not registered in the Local Project Registry.",
            )
        if not project.active:
            raise PolicyDeniedError(
                action="resolve_project",
                layer="PROJECT_REGISTRY",
                reason=f"Project '{project_id}' is marked inactive in the Local Project Registry.",
            )
        return project

    def validate_target_root(
        self,
        project_id: str,
        requested_target_path: Union[str, Path],
    ) -> Path:
        """Enforces Non-Redirection Invariant (ADR-009).

        Untrusted packages cannot redirect execution to arbitrary filesystem roots.
        If allow_target_override is False, requested path MUST match target_local_repo.
        If allow_target_override is True, requested path MUST reside within allowed_target_roots.

        Raises:
            PolicyDeniedError: If the requested path is unauthorized.
        """
        project = self.require_project(project_id)
        norm_requested = normalize_fs_path(requested_target_path)
        norm_registered = normalize_fs_path(project.target_local_repo)

        if not project.allow_target_override:
            if norm_requested != norm_registered:
                raise PolicyDeniedError(
                    action="validate_target_root",
                    layer="PROJECT_REGISTRY",
                    reason=(
                        f"Non-Redirection Invariant Violation: Target path '{requested_target_path}' "
                        f"does not match registered target_local_repo '{project.target_local_repo}' "
                        f"and allow_target_override is false for project '{project_id}'."
                    ),
                )
            return Path(norm_registered)

        # allow_target_override is True: verify against allowed_target_roots
        allowed_roots = project.allowed_target_roots or [project.target_local_repo]
        is_allowed = any(is_same_or_subpath(norm_requested, root) for root in allowed_roots)
        if not is_allowed:
            raise PolicyDeniedError(
                action="validate_target_root",
                layer="PROJECT_REGISTRY",
                reason=(
                    f"Non-Redirection Invariant Violation: Target path '{requested_target_path}' "
                    f"is not within allowed_target_roots {allowed_roots} for project '{project_id}'."
                ),
            )

        return Path(norm_requested)

    def get_risk_tier(self, project_id: str) -> str:
        """Returns risk tier for the project."""
        project = self.require_project(project_id)
        return project.risk_tier

    def is_post_gate(self, project_id: str) -> bool:
        """Returns True if the project requires human action gate approvals."""
        tier = self.get_risk_tier(project_id)
        return tier in (RiskTier.POST_GATE.value, RiskTier.REQUIRES_DECISION.value)

    def get_concurrency_policy(self, project_id: str) -> ConcurrencyPolicy:
        """Returns concurrency policy for project."""
        project = self.require_project(project_id)
        return project.concurrency_policy or ConcurrencyPolicy(
            max_mutating_jobs=1, allow_concurrent_read_only=True
        )

    def get_worktree_base(self, project_id: str) -> Path:
        """Resolve an explicitly registered worktree base without relative escape.

        Absolute bases are local registry authority; relative bases must remain
        beneath the registered repository root, on both Windows and POSIX.
        """
        project = self.require_project(project_id)
        base = project.allowed_worktree_base
        if base is None:
            base = "worktrees"
        if not base or not base.strip() or "\x00" in base:
            raise PolicyDeniedError(
                action="resolve_worktree_base",
                layer="PROJECT_REGISTRY",
                reason="Invalid empty worktree base.",
            )

        base_path = Path(base)
        windows_path = PureWindowsPath(base)
        if base_path.is_absolute() or windows_path.is_absolute():
            # An absolute base is authorized only by local registry configuration.
            return base_path
        if windows_path.drive or windows_path.root:
            raise PolicyDeniedError(
                action="resolve_worktree_base",
                layer="PROJECT_REGISTRY",
                reason="Ambiguous drive-relative or rooted worktree base.",
            )
        if base_path.parts in ((), (".",)) or windows_path.parts in ((), (".",)):
            raise PolicyDeniedError(
                action="resolve_worktree_base",
                layer="PROJECT_REGISTRY",
                reason="Worktree base cannot be the primary checkout.",
            )
        if ".." in windows_path.parts or ".." in base_path.parts:
            raise PolicyDeniedError(
                action="resolve_worktree_base",
                layer="PROJECT_REGISTRY",
                reason="Worktree base traversal denied.",
            )

        resolved = Path(project.target_local_repo) / base_path
        if not is_same_or_subpath(resolved, project.target_local_repo):
            raise PolicyDeniedError(
                action="resolve_worktree_base",
                layer="PROJECT_REGISTRY",
                reason="Worktree base outside registered repository root.",
            )
        return resolved

    @classmethod
    def from_file(
        cls,
        path: Union[Path, str],
        validator: Optional[SchemaValidator] = None,
    ) -> ProjectRegistryManager:
        """Loads and validates ProjectRegistryManager from a JSON file."""
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Project registry configuration not found at: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        registry = ProjectRegistry.from_dict(data)
        return cls(registry=registry, validator=validator)

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
        validator: Optional[SchemaValidator] = None,
    ) -> ProjectRegistryManager:
        """Loads and validates ProjectRegistryManager from a dictionary."""
        registry = ProjectRegistry.from_dict(data)
        return cls(registry=registry, validator=validator)

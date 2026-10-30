"""Tests for Project Registry Manager (src/sacl/policy/project_registry.py).

Constitutional Invariant (ADR-009):
The Project Registry is the sole local authority for filesystem roots.
Packages identify registered projects but cannot redirect execution outside
local registry policy.
"""

from pathlib import Path

import pytest

from sacl.contracts.exceptions import ContractValidationError, PolicyDeniedError
from sacl.contracts.invariants import RiskTier
from sacl.policy.project_registry import (
    ProjectRegistryManager,
    normalize_fs_path,
)


@pytest.fixture
def sample_registry_dict(tmp_path: Path):
    strict_root = str((tmp_path / "Repos" / "TestStrict").resolve())
    override_p1 = str((tmp_path / "Repos" / "TestOverride" / "primary").resolve())
    override_p2 = str((tmp_path / "Repos" / "TestOverride" / "secondary").resolve())
    inactive_root = str((tmp_path / "Repos" / "Inactive").resolve())
    return {
        "schema": "solidbit.project-registry.v1",
        "version": "1.0.0",
        "projects": [
            {
                "project_id": "test-project-strict",
                "repository": "risejoaquin/test-project-strict",
                "target_local_repo": strict_root,
                "default_branch": "main",
                "allowed_worktree_base": "worktrees",
                "allowed_target_roots": [strict_root],
                "allow_target_override": False,
                "concurrency_policy": {
                    "max_mutating_jobs": 1,
                    "allow_concurrent_read_only": True,
                },
                "risk_tier": "SAFE_IN_ISOLATED_BRANCH",
                "enforce_dirty_root_check": True,
                "active": True,
                "description": "Strict project without target override",
            },
            {
                "project_id": "test-project-override",
                "repository": "risejoaquin/test-project-override",
                "target_local_repo": override_p1,
                "default_branch": "main",
                "allowed_worktree_base": "wt",
                "allowed_target_roots": [override_p1, override_p2],
                "allow_target_override": True,
                "concurrency_policy": {
                    "max_mutating_jobs": 1,
                    "allow_concurrent_read_only": True,
                },
                "risk_tier": "POST_GATE",
                "enforce_dirty_root_check": True,
                "active": True,
                "description": "Project with target override authorized within whitelist",
            },
            {
                "project_id": "inactive-project",
                "repository": "risejoaquin/inactive-project",
                "target_local_repo": inactive_root,
                "default_branch": "main",
                "risk_tier": "SAFE_NOW",
                "enforce_dirty_root_check": True,
                "active": False,
                "description": "Inactive project",
            },
        ],
    }


def test_load_project_registry_and_lookup(sample_registry_dict):
    manager = ProjectRegistryManager.from_dict(sample_registry_dict)
    assert len(manager.list_projects()) == 3

    # Lookup by project_id
    p = manager.get_project("test-project-strict")
    assert p is not None
    assert p.repository == "risejoaquin/test-project-strict"

    # Lookup by repository
    p_by_repo = manager.get_project_by_repo("risejoaquin/test-project-strict")
    assert p_by_repo is not None
    assert p_by_repo.project_id == "test-project-strict"


def test_inactive_project_rejected(sample_registry_dict):
    manager = ProjectRegistryManager.from_dict(sample_registry_dict)
    with pytest.raises(PolicyDeniedError) as excinfo:
        manager.require_project("inactive-project")
    assert "marked inactive" in excinfo.value.message


def test_unknown_project_rejected(sample_registry_dict):
    manager = ProjectRegistryManager.from_dict(sample_registry_dict)
    with pytest.raises(PolicyDeniedError) as excinfo:
        manager.require_project("non-existent-project")
    assert "not registered" in excinfo.value.message


def test_non_redirection_invariant_strict(sample_registry_dict):
    import sys

    manager = ProjectRegistryManager.from_dict(sample_registry_dict)
    strict_root = sample_registry_dict["projects"][0]["target_local_repo"]

    # Valid matching target path
    validated = manager.validate_target_root("test-project-strict", strict_root)
    assert normalize_fs_path(validated) == normalize_fs_path(strict_root)

    # Path normalization check (forward slashes, trailing slashes, casing)
    slash_variant = strict_root.replace("\\", "/") + "/"
    if sys.platform == "win32":
        slash_variant = slash_variant.lower()
    validated_norm = manager.validate_target_root("test-project-strict", slash_variant)
    assert normalize_fs_path(validated_norm) == normalize_fs_path(strict_root)

    # Arbitrary path redirection attempt MUST raise PolicyDeniedError
    with pytest.raises(PolicyDeniedError) as excinfo:
        manager.validate_target_root("test-project-strict", strict_root + "_forbidden_redirect")
    assert "Non-Redirection Invariant Violation" in excinfo.value.message

    with pytest.raises(PolicyDeniedError) as excinfo:
        manager.validate_target_root("test-project-strict", strict_root + "/other_sub")
    assert "Non-Redirection Invariant Violation" in excinfo.value.message


def test_non_redirection_invariant_with_override_enabled(sample_registry_dict):
    manager = ProjectRegistryManager.from_dict(sample_registry_dict)
    p1 = sample_registry_dict["projects"][1]["allowed_target_roots"][0]
    p2 = sample_registry_dict["projects"][1]["allowed_target_roots"][1]

    # Authorized target roots
    val1 = manager.validate_target_root("test-project-override", p1)
    val2 = manager.validate_target_root("test-project-override", p2)
    assert normalize_fs_path(val1) == normalize_fs_path(p1)
    assert normalize_fs_path(val2) == normalize_fs_path(p2)

    # Subpath within authorized root is allowed
    sub_path = str(Path(p2) / "subdir")
    val_sub = manager.validate_target_root("test-project-override", sub_path)
    assert normalize_fs_path(val_sub) == normalize_fs_path(sub_path)

    # Unauthorized root outside allowed_target_roots MUST fail closed
    with pytest.raises(PolicyDeniedError) as excinfo:
        manager.validate_target_root("test-project-override", p1 + "_arbitrary_unauthorized")
    assert "Non-Redirection Invariant Violation" in excinfo.value.message


def test_concurrency_policy_baseline_enforced(sample_registry_dict):
    manager = ProjectRegistryManager.from_dict(sample_registry_dict)
    policy = manager.get_concurrency_policy("test-project-strict")
    assert policy.max_mutating_jobs == 1
    assert policy.allow_concurrent_read_only is True


def test_invalid_concurrency_policy_rejected(sample_registry_dict):
    # Attempting to configure max_mutating_jobs > 1 violates baseline
    bad_dict = dict(sample_registry_dict)
    bad_dict["projects"] = [dict(sample_registry_dict["projects"][0])]
    bad_dict["projects"][0]["concurrency_policy"] = {
        "max_mutating_jobs": 2,  # Invalid! Baseline is strictly 1
        "allow_concurrent_read_only": True,
    }
    with pytest.raises(ContractValidationError):
        ProjectRegistryManager.from_dict(bad_dict)


def test_risk_tier_and_post_gate_detection(sample_registry_dict):
    manager = ProjectRegistryManager.from_dict(sample_registry_dict)

    assert manager.get_risk_tier("test-project-strict") == RiskTier.SAFE_IN_ISOLATED_BRANCH.value
    assert manager.is_post_gate("test-project-strict") is False

    assert manager.get_risk_tier("test-project-override") == RiskTier.POST_GATE.value
    assert manager.is_post_gate("test-project-override") is True


def test_worktree_base_resolution(sample_registry_dict):
    manager = ProjectRegistryManager.from_dict(sample_registry_dict)
    base = manager.get_worktree_base("test-project-strict")
    assert normalize_fs_path(base) == normalize_fs_path("C:\\Repos\\TestStrict\\worktrees")



def test_windows_absolute_paths_are_compared_portably_and_safely():
    """Lexical Windows path rules must be identical on Linux and Windows CI."""
    assert is_same_or_subpath("c:/repos/app/child", r"C:\Repos\App")
    assert is_same_or_subpath(r"C:\Repos\App", r"C:\Repos\App")
    assert not is_same_or_subpath(r"C:\Repos\AppBackup", r"C:\Repos\App")
    assert not is_same_or_subpath(r"D:\Repos\App", r"C:\Repos\App")
    assert not is_same_or_subpath(r"C:\Repos\App\..\Sibling", r"C:\Repos\App")

@pytest.mark.parametrize(
    "unsafe_base",
    [
        "../escape",
        r"..\escape",
        r"wt\..\escape",
        r"C:outside",
        r"\outside",
        ".",
        "",
        "  ",
        "wt\x00escape",
    ],
)
def test_worktree_base_rejects_unsafe_relative_paths(sample_registry_dict, unsafe_base):
    """Registry worktree base must never escape or alias the primary checkout."""
    project = dict(sample_registry_dict["projects"][0])
    project["allowed_worktree_base"] = unsafe_base
    registry = {**sample_registry_dict, "projects": [project]}
    manager = ProjectRegistryManager.from_dict(registry)
    with pytest.raises(PolicyDeniedError) as excinfo:
        manager.get_worktree_base("test-project-strict")
    assert excinfo.value.layer == "PROJECT_REGISTRY"


def test_worktree_base_accepts_nested_relative_directory(sample_registry_dict):
    project = dict(sample_registry_dict["projects"][0])
    project["allowed_worktree_base"] = "wt/agents"
    registry = {**sample_registry_dict, "projects": [project]}
    manager = ProjectRegistryManager.from_dict(registry)
    base = manager.get_worktree_base("test-project-strict")
    assert normalize_fs_path(base) == normalize_fs_path(r"C:\Repos\TestStrict\wt\agents")


def test_worktree_base_accepts_explicit_absolute_directory(sample_registry_dict):
    project = dict(sample_registry_dict["projects"][0])
    project["allowed_worktree_base"] = r"C:\Safe\Worktrees"
    registry = {**sample_registry_dict, "projects": [project]}
    manager = ProjectRegistryManager.from_dict(registry)
    base = manager.get_worktree_base("test-project-strict")
    assert normalize_fs_path(base) == normalize_fs_path(r"C:\Safe\Worktrees")

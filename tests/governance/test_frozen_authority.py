"""Regression checks for the SACL V1 safety and human-authority baseline.

The tests read versioned files only and do not use live infrastructure.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HARD_DENIES = {
    "remote_production_execution",
    "github_merge",
    "production_db_write",
    "secret_export",
    "arbitrary_remote_code",
    "main_branch_execution",
    "primary_checkout_mutation",
    "hard_reset",
    "auto_stash",
}


def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_runtime_is_not_authorized_by_repository_ci() -> None:
    rules = read_json("contracts/architecture-invariants.json")
    assert rules["implementation_authorized"] is False
    assert rules["remote_production_v1"] is False
    assert rules["hard_deny_wins"] is True
    assert rules["approval_can_override_hard_deny"] is False


def test_runtime_git_permissions_require_human_approval() -> None:
    git_rules = read_json("contracts/architecture-invariants.json")["github"]
    assert git_rules["direct_main_push_hard_denied"] is True
    assert git_rules["merge_hard_denied_v1"] is True
    assert git_rules["feature_branch_push_requires_bounded_human_approval"] is True
    assert git_rules["pr_creation_requires_bounded_human_approval"] is True


def test_hard_local_policy_cannot_be_overridden() -> None:
    policy = read_json("config/runtime/hard-policy.json")
    assert policy["hard_deny_always_wins"] is True
    assert policy["approval_override_allowed"] is False
    assert HARD_DENIES <= {k for k, v in policy["hard_denies"].items() if v is True}


def test_default_local_policy_stays_fail_closed() -> None:
    policy = read_json("config/runtime/default-policy.json")
    assert policy["permissions"]["product_code_write"] is False
    assert policy["permissions"]["github_merge"] is False
    assert policy["permissions"]["production_deploy"] is False
    assert policy["workspace_safety"]["enforce_clean_root"] is True
    assert policy["workspace_safety"]["disallow_main_branch"] is True
    assert policy["workspace_safety"]["allow_primary_checkout"] is False
    assert policy["runtime_safety"]["remote_execution_enabled"] is False

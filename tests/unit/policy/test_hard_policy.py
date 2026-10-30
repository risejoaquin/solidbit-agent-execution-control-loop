"""Tests for Hard Local Policy Engine (src/sacl/policy/hard_policy.py).

Constitutional Invariant:
Hard deny always wins. Bounded human approvals cannot override hard local policy denies.
"""

import pytest

from sacl.contracts.exceptions import HardDenyViolation
from sacl.contracts.invariants import HARD_DENIED_ACTIONS
from sacl.contracts.models import HardDenies, HardLocalPolicy
from sacl.policy.hard_policy import (
    HardPolicyEngine,
    create_default_hard_policy,
    normalize_action,
)


def test_default_hard_policy_contains_all_9_denials():
    engine = HardPolicyEngine()
    policy = engine.get_hard_local_policy()

    assert policy.hard_deny_always_wins is True
    assert policy.approval_override_allowed is False
    assert policy.lattice_level == "HARD_LOCAL_POLICY"

    # Verify all 9 immutable denials are set to True
    denies = policy.hard_denies
    assert denies.remote_production_execution is True
    assert denies.github_merge is True
    assert denies.production_db_write is True
    assert denies.secret_export is True
    assert denies.arbitrary_remote_code is True
    assert denies.main_branch_execution is True
    assert denies.primary_checkout_mutation is True
    assert denies.hard_reset is True
    assert denies.auto_stash is True


@pytest.mark.parametrize("action", list(HARD_DENIED_ACTIONS))
def test_all_9_actions_raise_hard_deny_violation(action):
    engine = HardPolicyEngine()
    assert engine.is_denied(action) is True
    with pytest.raises(HardDenyViolation) as excinfo:
        engine.check_hard_deny(action)
    assert action in excinfo.value.action


@pytest.mark.parametrize(
    "alias,canonical",
    [
        ("git_merge", "github_merge"),
        ("git-merge", "github_merge"),
        ("GIT_MERGE", "github_merge"),
        ("merge", "github_merge"),
        ("remote_deploy", "remote_production_execution"),
        ("REMOTE-DEPLOY", "remote_production_execution"),
        ("production_deploy", "remote_production_execution"),
        ("production_db_mutation", "production_db_write"),
        ("arbitrary_script_execution", "arbitrary_remote_code"),
        ("main_push", "main_branch_execution"),
        ("direct_main_push", "main_branch_execution"),
        ("git_reset_hard", "hard_reset"),
        ("git_stash", "auto_stash"),
    ],
)
def test_action_aliases_and_casing_raise_hard_deny(alias, canonical):
    engine = HardPolicyEngine()
    assert normalize_action(alias) == canonical
    assert engine.is_denied(alias) is True
    with pytest.raises(HardDenyViolation):
        engine.check_hard_deny(alias)


def test_allowed_safe_action_does_not_raise():
    engine = HardPolicyEngine()
    assert engine.is_denied("read_documentation") is False
    assert engine.is_denied("run_unit_tests") is False
    assert engine.is_denied("source_orchestrator_read") is False
    engine.check_hard_deny("read_documentation")
    engine.check_hard_deny("run_unit_tests")


def test_hard_deny_always_wins_invariant_violation():
    # Attempting to construct a policy with hard_deny_always_wins=False must fail
    invalid_policy = HardLocalPolicy(
        policy_id="INVALID-POLICY",
        hard_denies=HardDenies(),
        hard_deny_always_wins=False,
        approval_override_allowed=False,
    )
    with pytest.raises(HardDenyViolation) as excinfo:
        HardPolicyEngine(policy=invalid_policy)
    assert "hard_deny_always_wins" in excinfo.value.message


def test_approval_override_allowed_invariant_violation():
    # Attempting to construct a policy with approval_override_allowed=True must fail
    invalid_policy = HardLocalPolicy(
        policy_id="INVALID-POLICY",
        hard_denies=HardDenies(),
        hard_deny_always_wins=True,
        approval_override_allowed=True,
    )
    with pytest.raises(HardDenyViolation) as excinfo:
        HardPolicyEngine(policy=invalid_policy)
    assert "approval_override_allowed" in excinfo.value.message


def test_attempt_to_disable_any_denial_violates_invariants():
    # Attempting to disable github_merge
    denies = HardDenies(github_merge=False)
    invalid_policy = HardLocalPolicy(
        policy_id="INVALID-POLICY",
        hard_denies=denies,
    )
    with pytest.raises(HardDenyViolation) as excinfo:
        HardPolicyEngine(policy=invalid_policy)
    assert "github_merge" in excinfo.value.action


def test_load_from_runtime_config_file(tmp_path):
    config_file = tmp_path / "hard-policy.json"
    config_file.write_text(
        create_default_hard_policy()
        .to_dict()
        .__repr__()
        .replace("'", '"')
        .replace("True", "true")
        .replace("False", "false"),
        encoding="utf-8",
    )
    # Using json format
    import json

    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(create_default_hard_policy().to_dict(), f)

    engine = HardPolicyEngine.from_file(config_file)
    assert engine.get_hard_local_policy().policy_id == "SACL-V1-DEFAULT-HARD-LOCAL-POLICY"

"""P0: Project Policy denials cannot be overridden by approval or alias collisions.

Mock-only: no workers, network calls, filesystem mutations, or real approvals.
"""
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from sacl.contracts.exceptions import (
    ApprovalRequiredError,
    HardDenyViolation,
    PolicyDeniedError,
)
from sacl.policy.hard_policy import HardPolicyEngine
from sacl.policy.lattice import PermissionLattice


def lattice():
    return PermissionLattice(HardPolicyEngine(), approval_validator=Mock())


def policy(permissions):
    return SimpleNamespace(permissions=permissions)


def grant(action="target_docs_write"):
    return SimpleNamespace(action=action, prohibited_actions=[], request_id="REQ-LOCAL")


@pytest.mark.parametrize("approval", [None, grant()])
def test_action_denied_even_with_approval(approval):
    with pytest.raises(PolicyDeniedError) as error:
        lattice().evaluate(
            "target_docs_write", ["target_docs_write"],
            policy({"target_docs_write": False}), approval,
        )
    assert error.value.layer == "PROJECT_POLICY"


@pytest.mark.parametrize("approval", [None, grant()])
def test_requested_permission_denied_even_with_approval(approval):
    with pytest.raises(PolicyDeniedError) as error:
        lattice().evaluate(
            "target_docs_write", ["target_docs_write", "product_code_write"],
            policy({"target_docs_write": True, "product_code_write": False}),
            approval,
        )
    assert error.value.layer == "PROJECT_POLICY"


@pytest.mark.parametrize("permissions", [
    {"TARGET_DOCS_WRITE": False, "target_docs_write": True},
    {"target_docs_write": True, "TARGET_DOCS_WRITE": False},
    {" target_docs_write ": False, "TARGET_DOCS_WRITE": True},
])
def test_alias_collision_denial_wins_regardless_of_order(permissions):
    with pytest.raises(PolicyDeniedError) as error:
        lattice().evaluate("target_docs_write", ["target_docs_write"], policy(permissions))
    assert error.value.layer == "PROJECT_POLICY"


def test_alias_collision_all_true_allowed():
    assert lattice().evaluate(
        "target_docs_write", ["target_docs_write"],
        policy({"TARGET_DOCS_WRITE": True, "target_docs_write": True}),
    ) is True


def test_allowed_action_without_approval():
    assert lattice().evaluate(
        "target_docs_write", ["target_docs_write"],
        policy({"target_docs_write": True}),
    ) is True


def test_gated_action_still_requires_approval():
    with pytest.raises(ApprovalRequiredError):
        lattice().evaluate(
            "stage_continuation", ["target_docs_write"],
            policy({"target_docs_write": True}),
        )


def test_gated_action_with_approval_passes():
    assert lattice().evaluate(
        "stage_continuation", ["target_docs_write"],
        policy({"target_docs_write": True}),
        grant("stage_continuation"),
    ) is True


def test_hard_deny_unconditionally_wins():
    with pytest.raises(HardDenyViolation):
        lattice().evaluate(
            "github_merge", ["github_merge"],
            policy({"github_merge": True}), grant("github_merge"),
        )

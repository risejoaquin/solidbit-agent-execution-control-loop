"""Tests for Effective-Permission Lattice & Policy Engine (src/sacl/policy/lattice.py).

Constitutional Invariant (ADR-005, ADR-007):
Effective Permissions = Hard Local Policy ∩ Project Policy ∩ Package Requested ∩ Approval Grant
Hard deny always wins. Bounded approvals cannot override hard denials.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest

from sacl.contracts.exceptions import (
    ApprovalExpiredError,
    ApprovalRequiredError,
    DirtyRootError,
    HardDenyViolation,
    PolicyDeniedError,
)
from sacl.contracts.invariants import HARD_DENIED_ACTIONS, RiskTier
from sacl.contracts.models import (
    ApprovalToken,
    Approver,
    ProjectPolicy,
    RuntimeSafety,
    WorkspaceSafety,
)
from sacl.policy.approval import ApprovalManager, format_iso_datetime
from sacl.policy.hard_policy import HardPolicyEngine
from sacl.policy.lattice import PermissionLattice, PolicyEngine
from sacl.policy.operation_registry import OperationRegistryManager
from sacl.policy.project_registry import ProjectRegistryManager


@pytest.fixture
def default_project_policy():
    return ProjectPolicy(
        policy_id="TEST-POLICY-v1",
        permissions={
            "source_orchestrator_read": True,
            "target_docs_write": True,
            "product_code_write": False,
            "github_merge": False,
            "production_deploy": False,
            "production_db_write": False,
            "secret_export": False,
            "arbitrary_script_execution": False,
        },
        workspace_safety=WorkspaceSafety(
            enforce_clean_root=True,
            disallow_main_branch=True,
            allow_primary_checkout=False,
            allow_hard_reset=False,
            allow_auto_stash=False,
        ),
        runtime_safety=RuntimeSafety(
            remote_execution_enabled=False,
            non_killing_timeout=True,
            pid_drift_tolerance_seconds=300,
            allowed_process_images=["agy", "powershell", "pwsh", "cmd", "node", "conhost"],
        ),
        stop_conditions={"stop_on": ["dirty_root_detected", "cross_agent_file_conflict"]},
        schema="solidbit.policy.v1",
    )


@pytest.fixture
def valid_approval():
    future_time = datetime.now(timezone.utc) + timedelta(hours=2)
    return ApprovalToken(
        request_id="REQ-TEST-001",
        job_id="job-100",
        action="stage_continuation",
        scope=["*"],
        expires_at=format_iso_datetime(future_time),
        decision="APPROVED",
        approver=Approver(identity="Joaquín", channel="CLI"),
        schema="solidbit.approval.v1",
        resume_run=True,
        cannot_override_hard_deny=True,
    )


def test_lattice_success_all_layers_agree(default_project_policy):
    lattice = PermissionLattice(hard_policy_engine=HardPolicyEngine())
    # Action and permissions permitted by all layers
    result = lattice.evaluate(
        action="target_docs_write",
        requested_permissions=["target_docs_write", "source_orchestrator_read"],
        project_policy=default_project_policy,
    )
    assert result is True


@pytest.mark.parametrize("denied_action", list(HARD_DENIED_ACTIONS))
def test_layer1_hard_deny_always_wins_unconditionally(default_project_policy, valid_approval, denied_action):
    lattice = PermissionLattice(hard_policy_engine=HardPolicyEngine())

    # 1. Denied without approval
    with pytest.raises(HardDenyViolation):
        lattice.evaluate(
            action=denied_action,
            requested_permissions=[],
            project_policy=default_project_policy,
        )

    # 2. Denied EVEN WITH valid approval grant! Hard deny ALWAYS wins!
    valid_approval.action = denied_action
    with pytest.raises(HardDenyViolation) as excinfo:
        lattice.evaluate(
            action=denied_action,
            requested_permissions=[],
            project_policy=default_project_policy,
            approval_grant=valid_approval,
        )
    assert "strictly prohibited by Hard Local Policy" in excinfo.value.message or "Approval Override Prohibited" in excinfo.value.message


def test_layer2_project_policy_denial(default_project_policy):
    lattice = PermissionLattice(hard_policy_engine=HardPolicyEngine())

    # product_code_write is False in project policy
    with pytest.raises(PolicyDeniedError) as excinfo:
        lattice.evaluate(
            action="product_code_write",
            requested_permissions=["product_code_write"],
            project_policy=default_project_policy,
        )
    assert excinfo.value.layer == "PROJECT_POLICY"


def test_layer3_package_requested_permissions_missing(default_project_policy):
    lattice = PermissionLattice(hard_policy_engine=HardPolicyEngine())

    # Package did not request target_docs_write
    with pytest.raises(PolicyDeniedError) as excinfo:
        lattice.evaluate(
            action="target_docs_write",
            requested_permissions=["source_orchestrator_read"],  # missing target_docs_write!
            project_policy=default_project_policy,
        )
    assert excinfo.value.layer == "PACKAGE_REQUESTED"


def test_layer4_gated_action_requires_approval(default_project_policy, valid_approval):
    lattice = PermissionLattice(hard_policy_engine=HardPolicyEngine())

    # stage_continuation is a gated action: fails without approval
    with pytest.raises(ApprovalRequiredError) as excinfo:
        lattice.evaluate(
            action="stage_continuation",
            requested_permissions=["target_docs_write"],
            project_policy=default_project_policy,
            approval_grant=None,
        )
    assert excinfo.value.action == "stage_continuation"

    # With valid approval grant: succeeds
    res = lattice.evaluate(
        action="stage_continuation",
        requested_permissions=["target_docs_write"],
        project_policy=default_project_policy,
        approval_grant=valid_approval,
    )
    assert res is True


def test_layer4_expired_approval_fails_closed(default_project_policy, valid_approval):
    lattice = PermissionLattice(hard_policy_engine=HardPolicyEngine())

    past_time = datetime.now(timezone.utc) - timedelta(minutes=10)
    valid_approval.expires_at = format_iso_datetime(past_time)

    with pytest.raises(ApprovalExpiredError):
        lattice.evaluate(
            action="stage_continuation",
            requested_permissions=["target_docs_write"],
            project_policy=default_project_policy,
            approval_grant=valid_approval,
        )


def test_workspace_safety_main_branch_not_allowed(default_project_policy):
    engine = PolicyEngine()
    with pytest.raises(HardDenyViolation) as excinfo:
        engine.check_workspace_safety(
            project_policy=default_project_policy,
            branch_name="main",
        )
    assert "MAIN_BRANCH_NOT_ALLOWED" in excinfo.value.message


def test_workspace_safety_primary_checkout_not_allowed(default_project_policy):
    engine = PolicyEngine()
    with pytest.raises(HardDenyViolation) as excinfo:
        engine.check_workspace_safety(
            project_policy=default_project_policy,
            branch_name="wt-agent-1",
            is_primary_checkout=True,
        )
    assert "PRIMARY_CHECKOUT_NOT_ALLOWED" in excinfo.value.message


def test_workspace_safety_local_dirty_root_rule(default_project_policy):
    engine = PolicyEngine()
    with pytest.raises(DirtyRootError) as excinfo:
        engine.check_workspace_safety(
            project_policy=default_project_policy,
            branch_name="wt-agent-1",
            is_primary_checkout=False,
            is_dirty_root=True,
            dirty_files=["modified_file.py"],
        )
    assert "Never overwrite, hard-reset, or auto-stash human changes" in excinfo.value.message


def test_policy_engine_end_to_end_evaluate_operation(default_project_policy, valid_approval):
    # Initialize engine with hard policy and approval manager
    engine = PolicyEngine()

    # Allowed operation
    assert engine.evaluate_lattice(
        action="target_docs_write",
        requested_permissions=["target_docs_write"],
        project_policy=default_project_policy,
    ) is True

    # Hard denied operation
    with pytest.raises(HardDenyViolation):
        engine.check_hard_deny("github_merge")

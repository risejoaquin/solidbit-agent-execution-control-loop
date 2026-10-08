"""SACL V1 Effective-Permission Lattice & Policy Engine.

Constitutional Invariant (ADR-005, ADR-007 & Authority Model §2):
Authorization is evaluated strictly through the mathematical intersection:
Effective Permissions = Hard Local Policy ∩ Project Policy ∩ Package Requested ∩ Approval Grant

Hard Deny Always Wins:
Any prohibition declared in Hard Local Policy unconditionally overrides any grant
in lower layers. Approvals cannot override hard denials.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from sacl.contracts.exceptions import (
    ApprovalExpiredError,
    ApprovalRequiredError,
    DirtyRootError,
    HardDenyViolation,
    PolicyDeniedError,
)
from sacl.contracts.interfaces import IPolicyEngine
from sacl.contracts.invariants import HARD_DENIED_ACTIONS, RiskTier
from sacl.contracts.models import (
    ApprovalToken,
    HardLocalPolicy,
    ProjectPolicy,
    ProjectRegistryEntry,
)
from sacl.contracts.schema_validator import SchemaValidator, get_default_validator
from sacl.policy.approval import ApprovalManager, ApprovalValidator
from sacl.policy.hard_policy import HardPolicyEngine, normalize_action
from sacl.policy.operation_registry import OperationRegistryManager
from sacl.policy.project_registry import ProjectRegistryManager


# Actions that are inherently gated requiring human approval if attempted
GATED_ACTIONS: Set[str] = {
    "stage_continuation",
    "branch_integration",
    "specification_and_schema_materialization",
    "specification_materialization",
    "feature_branch_push",
    "create_pull_request",
    "pr_creation",
}


class PermissionLattice:
    """Evaluates the 4-layer Effective-Permission Lattice."""

    def __init__(
        self,
        hard_policy_engine: HardPolicyEngine,
        approval_validator: Optional[ApprovalValidator] = None,
    ) -> None:
        self.hard_policy_engine = hard_policy_engine
        self.approval_validator = approval_validator or ApprovalValidator()

    def evaluate(
        self,
        action: str,
        requested_permissions: List[str],
        project_policy: ProjectPolicy,
        approval_grant: Optional[ApprovalToken] = None,
        job_id: Optional[str] = None,
        scope: Optional[List[str]] = None,
    ) -> bool:
        """Evaluates 4-layer intersection.

        Raises:
            HardDenyViolation: If Layer 1 prohibits the action (HARD DENY ALWAYS WINS).
            PolicyDeniedError: If Layer 2 or Layer 3 denies permissions.
            ApprovalRequiredError: If Layer 4 requires human approval.
            ApprovalExpiredError: If approval grant is expired.
        """
        # ====================================================================
        # LAYER 1: HARD LOCAL POLICY (Host-level non-overridable boundary)
        # ====================================================================
        # 1.1 Action hard-deny check
        self.hard_policy_engine.check_hard_deny(action)

        # 1.2 Permissions hard-deny check
        for perm in requested_permissions:
            self.hard_policy_engine.check_hard_deny(perm)

        # 1.3 Approval token hard-deny check (Token cannot override hard deny!)
        if approval_grant:
            self.hard_policy_engine.check_hard_deny(approval_grant.action)
            for prohibited in approval_grant.prohibited_actions:
                canonical_prohibited = normalize_action(prohibited)
                if canonical_prohibited == normalize_action(action):
                    raise HardDenyViolation(
                        action=action,
                        reason=f"Action '{action}' is explicitly prohibited by approval token '{approval_grant.request_id}'.",
                    )

        # ====================================================================
        # LAYER 2: PROJECT POLICY (Repository-level permissions & stop-conditions)
        # ====================================================================
        canonical_action = normalize_action(action)
        norm_perms = {normalize_action(k): v for k, v in project_policy.permissions.items()}

        # Check if the requested action is directly configured as disabled in project policy
        if canonical_action in norm_perms and not norm_perms[canonical_action]:
            # If disabled at project level, check whether an approval grant exists
            if not approval_grant:
                raise PolicyDeniedError(
                    action=action,
                    layer="PROJECT_POLICY",
                    reason=f"Action '{action}' is explicitly disabled in Project Policy permissions.",
                )

        # Check all requested permissions against project policy
        for perm in requested_permissions:
            canon_p = normalize_action(perm)
            if canon_p in norm_perms and not norm_perms[canon_p]:
                # If project policy explicitly disables this permission, approval is required
                if not approval_grant:
                    raise PolicyDeniedError(
                        action=action,
                        layer="PROJECT_POLICY",
                        reason=f"Permission '{perm}' is explicitly disabled in Project Policy.",
                    )

        # ====================================================================
        # LAYER 3: PACKAGE REQUESTED PERMISSIONS (Declarative incoming requests)
        # ====================================================================
        # A package cannot exercise permissions it did not declare/request
        req_norm = {normalize_action(p) for p in requested_permissions}
        if canonical_action in norm_perms and norm_perms[canonical_action]:
            if canonical_action not in req_norm:
                raise PolicyDeniedError(
                    action=action,
                    layer="PACKAGE_REQUESTED",
                    reason=f"Action '{action}' requires permission '{action}', which was not requested by package.",
                )

        # ====================================================================
        # LAYER 4: VALID APPROVAL GRANT (Bounded human sign-off)
        # ====================================================================
        is_gated = canonical_action in GATED_ACTIONS
        needs_approval = is_gated or any(
            (normalize_action(p) in norm_perms and not norm_perms[normalize_action(p)])
            for p in requested_permissions
        )

        if needs_approval and not approval_grant:
            effective_job_id = job_id or "job-unknown"
            effective_scope = scope or ["*"]
            raise ApprovalRequiredError(
                request_id="PENDING",
                job_id=effective_job_id,
                action=action,
                scope=effective_scope,
            )

        if approval_grant:
            if job_id:
                self.approval_validator.validate_binding(
                    token=approval_grant,
                    job_id=job_id,
                    action=action,
                    requested_scope=scope,
                )
            else:
                self.approval_validator.validate_invariants(approval_grant)

        return True


class PolicyEngine(IPolicyEngine):
    """Complete SACL V1 Policy Engine implementation."""

    def __init__(
        self,
        hard_policy_engine: Optional[HardPolicyEngine] = None,
        project_registry: Optional[ProjectRegistryManager] = None,
        operation_registry: Optional[OperationRegistryManager] = None,
        approval_manager: Optional[ApprovalManager] = None,
        validator: Optional[SchemaValidator] = None,
    ) -> None:
        self.validator = validator or get_default_validator()
        self.hard_policy_engine = hard_policy_engine or HardPolicyEngine(validator=self.validator)
        self.project_registry = project_registry
        self.operation_registry = operation_registry
        self.approval_manager = approval_manager or ApprovalManager(validator=self.validator)
        self.lattice = PermissionLattice(
            hard_policy_engine=self.hard_policy_engine,
            approval_validator=self.approval_manager.validator,
        )

    def check_hard_deny(self, action: str) -> None:
        """Verifies action is not hard denied.

        Raises:
            HardDenyViolation: If action is prohibited.
        """
        self.hard_policy_engine.check_hard_deny(action)

    def evaluate_lattice(
        self,
        action: str,
        requested_permissions: List[str],
        project_policy: ProjectPolicy,
        approval_grant: Optional[ApprovalToken] = None,
    ) -> bool:
        """Calculates 4-layer intersection:
        Hard Policy ∩ Project Policy ∩ Package Requested ∩ Approval.
        """
        return self.lattice.evaluate(
            action=action,
            requested_permissions=requested_permissions,
            project_policy=project_policy,
            approval_grant=approval_grant,
        )

    def get_hard_local_policy(self) -> HardLocalPolicy:
        """Returns the active hard local policy."""
        return self.hard_policy_engine.get_hard_local_policy()

    def evaluate_operation(
        self,
        operation_id: str,
        project_id: str,
        project_policy: ProjectPolicy,
        package_requested_permissions: List[str],
        approval_grant: Optional[ApprovalToken] = None,
        target_repo_path: Optional[Union[str, Path]] = None,
        job_id: Optional[str] = None,
        scope: Optional[List[str]] = None,
        verify_handler: bool = False,
    ) -> bool:
        """Comprehensive operational authorization check integrating all registries.

        1. Resolves trusted operation in Operation Registry.
        2. Verifies cryptographic handler integrity if requested.
        3. Validates target repository roots against Project Registry.
        4. Verifies post-gate approval requirements based on risk tier.
        5. Evaluates 4-layer Effective-Permission Lattice.
        """
        # 1. Operation registry resolution
        if self.operation_registry:
            op_entry = self.operation_registry.resolve_operation(operation_id)
            if verify_handler:
                self.operation_registry.verify_handler_integrity(operation_id)
            required_perms = op_entry.required_permissions
        else:
            required_perms = []

        # 2. Project registry validation
        if self.project_registry:
            project_entry = self.project_registry.require_project(project_id)
            if target_repo_path:
                self.project_registry.validate_target_root(project_id, target_repo_path)

            # Risk tier gate check
            if project_entry.risk_tier in (RiskTier.POST_GATE.value, RiskTier.REQUIRES_DECISION.value):
                if not approval_grant:
                    raise ApprovalRequiredError(
                        request_id="PENDING",
                        job_id=job_id or "job-unknown",
                        action=operation_id,
                        scope=scope or ["*"],
                    )

        # 3. Permission Lattice evaluation
        return self.lattice.evaluate(
            action=operation_id,
            requested_permissions=package_requested_permissions,
            project_policy=project_policy,
            approval_grant=approval_grant,
            job_id=job_id,
            scope=scope,
        )

    def check_workspace_safety(
        self,
        project_policy: ProjectPolicy,
        branch_name: Optional[str] = None,
        is_primary_checkout: bool = False,
        is_dirty_root: bool = False,
        dirty_files: Optional[List[str]] = None,
    ) -> None:
        """Validates Git workspace safety invariants before execution."""
        # 1. Main branch execution invariant
        if branch_name and branch_name.strip().lower() in ("main", "master"):
            if project_policy.workspace_safety.disallow_main_branch:
                raise HardDenyViolation(
                    action="main_branch_execution",
                    reason="MAIN_BRANCH_NOT_ALLOWED: Target branch cannot be main/master.",
                )

        # 2. Primary checkout mutation invariant
        if is_primary_checkout and not project_policy.workspace_safety.allow_primary_checkout:
            raise HardDenyViolation(
                action="primary_checkout_mutation",
                reason="PRIMARY_CHECKOUT_NOT_ALLOWED: Agent cannot execute within primary checkout.",
            )

        # 3. Local dirty root rule
        if is_dirty_root and project_policy.workspace_safety.enforce_clean_root:
            raise DirtyRootError(
                target_path="primary_checkout",
                dirty_files=dirty_files or ["uncommitted_modifications"],
            )

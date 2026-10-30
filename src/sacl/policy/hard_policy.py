"""SACL V1 Hard Local Policy Engine.

Enforces the 9 immutable constitutional hard denials on the local execution host.
Constitutional Invariant: Hard deny always wins. Bounded human approvals cannot
override hard local policy denials.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, FrozenSet, Optional, Union

from sacl.contracts.exceptions import HardDenyViolation
from sacl.contracts.invariants import HARD_DENIED_ACTIONS
from sacl.contracts.models import HardDenies, HardLocalPolicy
from sacl.contracts.schema_validator import SchemaValidator, get_default_validator

# Canonical action alias mapping to normalize different naming variants
ACTION_ALIASES: Dict[str, str] = {
    # Git merge variants
    "git_merge": "github_merge",
    "git-merge": "github_merge",
    "github-merge": "github_merge",
    "merge": "github_merge",
    "pr_merge": "github_merge",
    "pr-merge": "github_merge",
    # Remote production / deployment variants
    "remote-production-execution": "remote_production_execution",
    "remote_deploy": "remote_production_execution",
    "remote-deploy": "remote_production_execution",
    "production_deploy": "remote_production_execution",
    "production-deploy": "remote_production_execution",
    "production_mutation": "remote_production_execution",
    "production-mutation": "remote_production_execution",
    "deploy": "remote_production_execution",
    # Production DB write variants
    "production-db-write": "production_db_write",
    "production_db_mutation": "production_db_write",
    "production-db-mutation": "production_db_write",
    "prod_db_write": "production_db_write",
    # Secret export variants
    "secret-export": "secret_export",
    "export_secret": "secret_export",
    "export_secrets": "secret_export",
    # Arbitrary remote code variants
    "arbitrary-remote-code": "arbitrary_remote_code",
    "arbitrary_script_execution": "arbitrary_remote_code",
    "arbitrary-script-execution": "arbitrary_remote_code",
    "arbitrary_code_execution": "arbitrary_remote_code",
    # Main branch execution variants
    "main-branch-execution": "main_branch_execution",
    "main_push": "main_branch_execution",
    "main-push": "main_branch_execution",
    "direct_main_push": "main_branch_execution",
    "master_branch_execution": "main_branch_execution",
    # Primary checkout mutation variants
    "primary-checkout-mutation": "primary_checkout_mutation",
    "mutate_primary_checkout": "primary_checkout_mutation",
    # Destructive git reset/clean variants
    "hard-reset": "hard_reset",
    "git_reset_hard": "hard_reset",
    "git_reset": "hard_reset",
    "git_clean": "hard_reset",
    "git_clean_fd": "hard_reset",
    # Auto stash variants
    "auto-stash": "auto_stash",
    "git_stash": "auto_stash",
    "autostash": "auto_stash",
}


def normalize_action(action: str) -> str:
    """Normalizes action string into canonical identifier."""
    cleaned = action.strip().lower().replace(" ", "_")
    return ACTION_ALIASES.get(cleaned, cleaned)


def create_default_hard_policy() -> HardLocalPolicy:
    """Constructs the canonical SACL V1 default hard local policy."""
    return HardLocalPolicy(
        policy_id="SACL-V1-DEFAULT-HARD-LOCAL-POLICY",
        hard_denies=HardDenies(
            remote_production_execution=True,
            github_merge=True,
            production_db_write=True,
            secret_export=True,
            arbitrary_remote_code=True,
            main_branch_execution=True,
            primary_checkout_mutation=True,
            hard_reset=True,
            auto_stash=True,
        ),
        schema="solidbit.hard-policy.v1",
        lattice_level="HARD_LOCAL_POLICY",
        hard_deny_always_wins=True,
        approval_override_allowed=False,
    )


class HardPolicyEngine:
    """Enforces immutable hard local policy prohibitions."""

    def __init__(
        self,
        policy: Optional[HardLocalPolicy] = None,
        validator: Optional[SchemaValidator] = None,
    ) -> None:
        self.validator = validator or get_default_validator()
        self._policy = policy or create_default_hard_policy()
        self._validate_policy_invariants(self._policy)

    def _validate_policy_invariants(self, policy: HardLocalPolicy) -> None:
        """Enforces schema validity and non-negotiable architectural invariants."""
        # 1. Hard deny always wins invariant
        if not policy.hard_deny_always_wins:
            raise HardDenyViolation(
                action="modify_hard_deny_precedence",
                reason="Constitutional Invariant: hard_deny_always_wins must strictly be true.",
            )

        # 2. Approval override prohibited invariant
        if policy.approval_override_allowed:
            raise HardDenyViolation(
                action="enable_approval_override",
                reason="Constitutional Invariant: approval_override_allowed must strictly be false.",
            )

        # 3. All 9 canonical hard denies must be enabled
        denies_dict = policy.hard_denies.to_dict()
        for denial in HARD_DENIED_ACTIONS:
            if not denies_dict.get(denial, False):
                raise HardDenyViolation(
                    action=f"disable_{denial}",
                    reason=f"Constitutional Invariant: '{denial}' cannot be disabled in V1 Hard Local Policy.",
                )

        # 4. Schema check
        self.validator.validate_hard_policy(policy.to_dict())

    @property
    def policy(self) -> HardLocalPolicy:
        """Returns the active hard local policy."""
        return self._policy

    @property
    def hard_denied_actions(self) -> FrozenSet[str]:
        """Returns the set of hard-denied action keys."""
        return HARD_DENIED_ACTIONS

    def is_denied(self, action: str) -> bool:
        """Determines if an action is prohibited by hard local policy."""
        canonical = normalize_action(action)
        return canonical in HARD_DENIED_ACTIONS

    def check_hard_deny(self, action: str) -> None:
        """Verifies action is not hard denied.

        Raises:
            HardDenyViolation: If action is prohibited.
        """
        if self.is_denied(action):
            canonical = normalize_action(action)
            raise HardDenyViolation(
                action=action,
                reason=f"Action '{action}' (canonical: '{canonical}') is strictly prohibited by Hard Local Policy. Hard deny always wins.",
            )

    def get_hard_local_policy(self) -> HardLocalPolicy:
        """Returns the active hard local policy model."""
        return self._policy

    @classmethod
    def from_file(
        cls, path: Union[Path, str], validator: Optional[SchemaValidator] = None
    ) -> HardPolicyEngine:
        """Loads and validates HardPolicyEngine from a JSON file."""
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Hard policy configuration not found at: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        policy = HardLocalPolicy.from_dict(data)
        return cls(policy=policy, validator=validator)

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], validator: Optional[SchemaValidator] = None
    ) -> HardPolicyEngine:
        """Loads and validates HardPolicyEngine from a dictionary."""
        policy = HardLocalPolicy.from_dict(data)
        return cls(policy=policy, validator=validator)

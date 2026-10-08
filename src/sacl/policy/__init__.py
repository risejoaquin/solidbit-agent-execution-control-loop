"""SACL V1 Policy Subsystem.

Provides:
- Hard local policy enforcement (9 immutable denials, hard deny always wins)
- Local project registry management (non-redirection invariant, concurrency bounds)
- Local operation registry management (handler integrity, profile sandboxing)
- Bounded approval validation primitives (7 binding fields, fail-closed, no override)
- Effective-Permission Lattice (4-layer mathematical intersection)
- Unified PolicyEngine implementing IPolicyEngine
"""

from sacl.contracts.exceptions import (
    ApprovalExpiredError,
    ApprovalRequiredError,
    ContractValidationError,
    DirtyRootError,
    HardDenyViolation,
    PolicyDeniedError,
)
from sacl.contracts.invariants import HARD_DENIED_ACTIONS, RiskTier
from sacl.contracts.models import (
    ApprovalToken,
    Approver,
    ConcurrencyPolicy,
    ExecutionProfile,
    HardDenies,
    HardLocalPolicy,
    OperationRegistry,
    OperationRegistryEntry,
    ProjectPolicy,
    ProjectRegistry,
    ProjectRegistryEntry,
    RuntimeSafety,
    WorkspaceSafety,
)
from sacl.policy.approval import (
    ApprovalManager,
    ApprovalValidator,
    format_iso_datetime,
    is_scope_covered,
    matches_scope_pattern,
    parse_iso_datetime,
)
from sacl.policy.hard_policy import (
    ACTION_ALIASES,
    HardPolicyEngine,
    create_default_hard_policy,
    normalize_action,
)
from sacl.policy.lattice import (
    GATED_ACTIONS,
    PermissionLattice,
    PolicyEngine,
)
from sacl.policy.operation_registry import (
    OperationRegistryManager,
    normalize_image_name,
)
from sacl.policy.project_registry import (
    ProjectRegistryManager,
    is_same_or_subpath,
    normalize_fs_path,
)

__all__ = [
    # Engines & Managers
    "HardPolicyEngine",
    "ProjectRegistryManager",
    "OperationRegistryManager",
    "ApprovalValidator",
    "ApprovalManager",
    "PermissionLattice",
    "PolicyEngine",
    # Helper Functions
    "create_default_hard_policy",
    "normalize_action",
    "normalize_fs_path",
    "normalize_image_name",
    "is_same_or_subpath",
    "matches_scope_pattern",
    "is_scope_covered",
    "parse_iso_datetime",
    "format_iso_datetime",
    # Constants
    "HARD_DENIED_ACTIONS",
    "ACTION_ALIASES",
    "GATED_ACTIONS",
    "RiskTier",
    # Models
    "HardLocalPolicy",
    "HardDenies",
    "ProjectRegistry",
    "ProjectRegistryEntry",
    "ConcurrencyPolicy",
    "OperationRegistry",
    "OperationRegistryEntry",
    "ExecutionProfile",
    "ProjectPolicy",
    "WorkspaceSafety",
    "RuntimeSafety",
    "ApprovalToken",
    "Approver",
    # Exceptions
    "HardDenyViolation",
    "PolicyDeniedError",
    "ApprovalRequiredError",
    "ApprovalExpiredError",
    "DirtyRootError",
    "ContractValidationError",
]

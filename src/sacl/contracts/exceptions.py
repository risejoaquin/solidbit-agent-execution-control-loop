"""SACL V1 Typed Exception Hierarchy.

Constitutional exceptions protecting invariant safety, permission boundaries,
and deterministic execution across SACL subsystems.
"""


class SaclError(Exception):
    """Base exception for all SACL control loop errors."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict:
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
        }


class ArchitectureInvariantError(SaclError):
    """Raised when an inviolable architectural invariant is violated."""
    pass


class HardDenyViolation(ArchitectureInvariantError):
    """Raised when an operation attempts an action permanently prohibited by hard local policy.

    Hard deny ALWAYS wins. Approvals cannot override hard denials.
    """

    def __init__(self, action: str, reason: str = "Action is unconditionally hard-denied in V1") -> None:
        super().__init__(
            f"HARD_DENY_VIOLATION: Action '{action}' is strictly prohibited. {reason}",
            details={"action": action, "prohibited": True},
        )
        self.action = action


class PolicyDeniedError(SaclError):
    """Raised when an operation is denied by the effective-permission lattice.

    Effective Permissions = Hard Local Policy ∩ Project Policy ∩ Package Requested ∩ Approval Grant.
    """

    def __init__(self, action: str, layer: str, reason: str) -> None:
        super().__init__(
            f"POLICY_DENIED: Action '{action}' denied by {layer}: {reason}",
            details={"action": action, "denied_by_layer": layer, "reason": reason},
        )
        self.action = action
        self.layer = layer


class ContractValidationError(SaclError):
    """Raised when schema validation or execution contract validation fails."""

    def __init__(self, schema_name: str, message: str, errors: list[str] | None = None) -> None:
        super().__init__(
            f"CONTRACT_VALIDATION_ERROR [{schema_name}]: {message}",
            details={"schema": schema_name, "validation_errors": errors or []},
        )
        self.schema_name = schema_name
        self.validation_errors = errors or []


class ReconciliationError(SaclError):
    """Raised when 4-point run status reconciliation fails to produce a coherent verdict."""
    pass


class DirtyRootError(SaclError):
    """Raised when target repository working tree is dirty, violating the Local Dirty-Root Rule."""

    def __init__(self, target_path: str, dirty_files: list[str]) -> None:
        super().__init__(
            f"DIRTY_ROOT_ERROR: Target repository at '{target_path}' has uncommitted modifications. "
            "Never overwrite, hard-reset, or auto-stash human changes.",
            details={"target_path": target_path, "dirty_files": dirty_files},
        )
        self.target_path = target_path
        self.dirty_files = dirty_files


class ApprovalRequiredError(SaclError):
    """Raised when execution halts at an action gate requiring bounded human authorization."""

    def __init__(self, request_id: str, job_id: str, action: str, scope: list[str]) -> None:
        super().__init__(
            f"APPROVAL_REQUIRED: Action '{action}' on job '{job_id}' requires human approval. "
            f"Request token: {request_id}",
            details={
                "request_id": request_id,
                "job_id": job_id,
                "action": action,
                "scope": scope,
            },
        )
        self.request_id = request_id
        self.job_id = job_id
        self.action = action
        self.scope = scope


class ApprovalExpiredError(SaclError):
    """Raised when an approval token has passed its expires_at timestamp (fail-closed)."""

    def __init__(self, request_id: str, expires_at: str) -> None:
        super().__init__(
            f"APPROVAL_EXPIRED: Approval token '{request_id}' expired at '{expires_at}' (fail-closed).",
            details={"request_id": request_id, "expires_at": expires_at},
        )
        self.request_id = request_id
        self.expires_at = expires_at


class QuarantineError(SaclError):
    """Raised when an execution package or payload is quarantined for security review.

    Triggers: zip-slip path traversal, unvetted scripts, corrupted hashes.
    """

    def __init__(self, package_id: str, reason: str) -> None:
        super().__init__(
            f"QUARANTINED: Package '{package_id}' quarantined: {reason}",
            details={"package_id": package_id, "quarantine_reason": reason},
        )
        self.package_id = package_id


class LeaseAcquisitionError(SaclError):
    """Raised when a mutual exclusion lease cannot be acquired."""

    def __init__(self, lease_name: str, current_holder: str, holder_pid: int) -> None:
        super().__init__(
            f"LEASE_ACQUISITION_ERROR: Lease '{lease_name}' is currently held by '{current_holder}' (PID {holder_pid}).",
            details={
                "lease_name": lease_name,
                "current_holder": current_holder,
                "holder_pid": holder_pid,
            },
        )
        self.lease_name = lease_name


class ProcessObservationError(SaclError):
    """Raised when OS process verification encounters unwhitelisted images or PID recycling drift."""

    def __init__(self, pid: int, reason: str) -> None:
        super().__init__(
            f"PROCESS_OBSERVATION_ERROR: PID {pid} verification failed: {reason}",
            details={"pid": pid, "reason": reason},
        )
        self.pid = pid


class CollisionDetectedError(SaclError):
    """Raised when cross-agent concurrent file modifications overlap."""

    def __init__(self, run_id: str, colliding_files: list[str]) -> None:
        super().__init__(
            f"COLLISION_DETECTED: Overlapping file modifications in run '{run_id}': {colliding_files}",
            details={"run_id": run_id, "colliding_files": colliding_files},
        )
        self.run_id = run_id
        self.colliding_files = colliding_files

"""SACL V1 State Store Exception Hierarchy.

Custom exceptions for SQLite operational state, migrations, repositories,
leasing, queuing, and idempotency errors.
"""

from __future__ import annotations

from sacl.contracts.exceptions import SaclError


class StateStoreError(SaclError):
    """Base exception for all operational state store errors."""

    pass


class MigrationError(StateStoreError):
    """Base exception for database schema migration errors."""

    pass


class MigrationChecksumMismatchError(MigrationError):
    """Raised when an applied migration file hash differs from recorded checksum."""

    def __init__(
        self, version: int, recorded_checksum: str, actual_checksum: str, name: str = ""
    ) -> None:
        super().__init__(
            f"MIGRATION_CHECKSUM_MISMATCH: Version {version} ('{name}') has recorded checksum "
            f"'{recorded_checksum}' but disk file has '{actual_checksum}'. Schema tampering detected.",
            details={
                "version": version,
                "name": name,
                "recorded_checksum": recorded_checksum,
                "actual_checksum": actual_checksum,
            },
        )
        self.version = version
        self.recorded_checksum = recorded_checksum
        self.actual_checksum = actual_checksum
        self.name = name


class MigrationVersionConflictError(MigrationError):
    """Raised when a migration version is invalid or out of sequence."""

    pass


class InvalidStateTransitionError(StateStoreError):
    """Raised when attempting an invalid or unauthorized state transition."""

    def __init__(
        self, entity_type: str, entity_id: str, current_state: str, attempted_state: str
    ) -> None:
        super().__init__(
            f"INVALID_STATE_TRANSITION: Cannot transition {entity_type} '{entity_id}' "
            f"from '{current_state}' to '{attempted_state}'.",
            details={
                "entity_type": entity_type,
                "entity_id": entity_id,
                "current_state": current_state,
                "attempted_state": attempted_state,
            },
        )
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.current_state = current_state
        self.attempted_state = attempted_state


class PayloadConflictError(StateStoreError):
    """Raised when an incoming package shares an existing job_id with different payload SHA-256."""

    def __init__(self, job_id: str, existing_sha: str, incoming_sha: str) -> None:
        super().__init__(
            f"PAYLOAD_CONFLICT: Job '{job_id}' already registered with package hash '{existing_sha}', "
            f"incoming package has hash '{incoming_sha}'. Rejecting conflicting mutation.",
            details={
                "job_id": job_id,
                "existing_sha": existing_sha,
                "incoming_sha": incoming_sha,
            },
        )
        self.job_id = job_id
        self.existing_sha = existing_sha
        self.incoming_sha = incoming_sha


class DuplicateEntityError(StateStoreError):
    """Raised when attempting to insert an entity that already exists."""

    pass


class EntityNotFoundError(StateStoreError):
    """Raised when an entity is not found in the operational state store."""

    pass


class QueueEmptyError(StateStoreError):
    """Raised when attempting to dequeue from an empty durable queue."""

    pass


class ConcurrencyConflictError(StateStoreError):
    """Raised when an operation violates concurrency baseline rules (e.g. 1 mutating job per project)."""

    def __init__(self, project_id: str, active_run_id: str, requested_run_id: str) -> None:
        super().__init__(
            f"CONCURRENCY_CONFLICT: Project '{project_id}' already has active mutating run '{active_run_id}'. "
            f"Cannot dispatch run '{requested_run_id}' concurrently.",
            details={
                "project_id": project_id,
                "active_run_id": active_run_id,
                "requested_run_id": requested_run_id,
            },
        )
        self.project_id = project_id
        self.active_run_id = active_run_id
        self.requested_run_id = requested_run_id


class StaleLeaseError(StateStoreError):
    """Raised when attempting an operation on an expired or lost lease."""

    pass

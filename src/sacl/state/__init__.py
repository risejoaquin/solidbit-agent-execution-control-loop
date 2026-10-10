"""SACL V1 Operational State Store Subsystem.

Authoritative local persistence, migrations, repositories, transactions,
leases, heartbeats, durable queues, and idempotency protection against sacl_ops.db.
"""

from sacl.state.connection import ConnectionManager, create_connection
from sacl.state.exceptions import (
    ConcurrencyConflictError,
    DuplicateEntityError,
    EntityNotFoundError,
    InvalidStateTransitionError,
    MigrationChecksumMismatchError,
    MigrationError,
    PayloadConflictError,
    StateStoreError,
)
from sacl.state.heartbeats import HeartbeatManager
from sacl.state.idempotency import IdempotencyHelper, InboundAction, InboundEvaluationResult
from sacl.state.leases import HierarchicalLeaseType, LeaseManager
from sacl.state.migrations import MigrationRecord, MigrationRunner
from sacl.state.queues import DurableJobQueue, DurableMailQueue, DurableOutboxQueue
from sacl.state.repositories.agents import AgentRepository
from sacl.state.repositories.approvals import ApprovalRepository
from sacl.state.repositories.artifacts import ArtifactRepository
from sacl.state.repositories.base import BaseRepository
from sacl.state.repositories.errors import ErrorRepository
from sacl.state.repositories.events import EventRepository
from sacl.state.repositories.graph import GraphRepository
from sacl.state.repositories.jobs import JobRepository
from sacl.state.repositories.mail import MailRepository
from sacl.state.repositories.packages import PackageRepository
from sacl.state.repositories.projects import ProjectRepository
from sacl.state.repositories.results import ResultRepository
from sacl.state.repositories.runs import RunRepository
from sacl.state.store import SqliteStateStore, StateStore
from sacl.state.transactions import savepoint, transaction

__all__ = [
    # State Store Facade
    "SqliteStateStore",
    "StateStore",
    # Connection & Transactions
    "create_connection",
    "ConnectionManager",
    "transaction",
    "savepoint",
    # Migrations
    "MigrationRunner",
    "MigrationRecord",
    # Managers & Primitives
    "LeaseManager",
    "HierarchicalLeaseType",
    "HeartbeatManager",
    "DurableJobQueue",
    "DurableMailQueue",
    "DurableOutboxQueue",
    "IdempotencyHelper",
    "InboundAction",
    "InboundEvaluationResult",
    # Repositories
    "BaseRepository",
    "JobRepository",
    "RunRepository",
    "GraphRepository",
    "AgentRepository",
    "EventRepository",
    "ApprovalRepository",
    "ArtifactRepository",
    "ResultRepository",
    "ProjectRepository",
    "PackageRepository",
    "ErrorRepository",
    "MailRepository",
    # Exceptions
    "StateStoreError",
    "MigrationError",
    "MigrationChecksumMismatchError",
    "InvalidStateTransitionError",
    "PayloadConflictError",
    "DuplicateEntityError",
    "EntityNotFoundError",
    "ConcurrencyConflictError",
]

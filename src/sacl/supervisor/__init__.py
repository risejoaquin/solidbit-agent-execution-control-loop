"""SolidBit Agent Execution Control Loop (SACL V1) Supervisor Subsystem.

Provides:
- GraphPSupervisor: Persistent background supervisor daemon maintaining zero idle token posture.
- LeaseCoordinator: Hierarchical singleton (SUPERVISOR_SINGLETON) and project-level mutual exclusion leases.
- JobLifecycleManager: Canonical 12-primary + 10-side state lifecycle transition manager.
- JobDispatcher: Prioritized queue dispatch, dirty-root checks, and ephemeral Graph-H engine invocation.
"""

from sacl.supervisor.dispatcher import (
    JobDispatcher,
    RunContext,
)
from sacl.supervisor.graph_p import (
    ActiveRunTracking,
    GraphPSupervisor,
    SupervisorConfig,
    SupervisorState,
)
from sacl.supervisor.lease import (
    LeaseCoordinator,
    default_process_alive_check,
)
from sacl.supervisor.lifecycle import (
    RELEASE_LEASE_STATES,
    TERMINAL_JOB_STATES,
    VALID_JOB_TRANSITIONS,
    JobLifecycleManager,
)

__all__ = [
    "GraphPSupervisor",
    "SupervisorConfig",
    "SupervisorState",
    "ActiveRunTracking",
    "LeaseCoordinator",
    "default_process_alive_check",
    "JobLifecycleManager",
    "VALID_JOB_TRANSITIONS",
    "TERMINAL_JOB_STATES",
    "RELEASE_LEASE_STATES",
    "JobDispatcher",
    "RunContext",
]

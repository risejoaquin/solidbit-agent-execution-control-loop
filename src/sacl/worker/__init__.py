"""SACL V1 Worker Subsystem.

Provides isolated worktree execution, process management, 3-way PID recycling
defense, non-killing timeouts, safe-stop protocols, and four-part reconciliation.
"""

from sacl.worker.agent_worker import AgentWorker
from sacl.worker.models import ProcessIdentity, WorkerAttemptRecord, WorkerConfig
from sacl.worker.process import (
    IProcessInspector,
    MockProcessInspector,
    OSProcessInspector,
    safe_stop_agent_process,
    verify_agent_process_running,
)
from sacl.worker.reconciliation_hook import WorkerReconciler
from sacl.worker.retry import (
    FailureClassification,
    calculate_backoff_delay,
    classify_failure,
    get_attempt_log_paths,
)
from sacl.worker.worktree import WorkspaceManager

__all__ = [
    "AgentWorker",
    "FailureClassification",
    "IProcessInspector",
    "MockProcessInspector",
    "OSProcessInspector",
    "ProcessIdentity",
    "WorkerAttemptRecord",
    "WorkerConfig",
    "WorkerReconciler",
    "WorkspaceManager",
    "calculate_backoff_delay",
    "classify_failure",
    "get_attempt_log_paths",
    "safe_stop_agent_process",
    "verify_agent_process_running",
]

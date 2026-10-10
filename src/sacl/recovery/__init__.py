"""SACL V1 Crash Recovery, State Reconciliation & Replay Framework.

Implements docs/RECOVERY_MODEL.md:
- Cold-start crash recovery sequence & lease reclamation.
- INTERRUPTED state machine & lifecycle handling.
- 3-way process check & PID recycling defense.
- Local Dirty-Root Rule & orphaned worktree inspection.
- Safe-to-resume evaluation (prohibiting blind restarts).
- BLOCKED_RECOVERY_REVIEW outcomes for uncommitted changes or review markers.
"""

from sacl.recovery.interrupted import (
    AgentRecoveryReport,
    InterruptedRunRecoveryReport,
    find_interrupted_runs,
    recover_interrupted_run,
)
from sacl.recovery.process_identity import (
    MockProcessInspector,
    ProcessIdentity,
    ProcessInspectionStatus,
    ProcessInspector,
    ProcessObservationResult,
    SystemProcessInspector,
    get_default_process_inspector,
    inspect_process,
    set_default_process_inspector,
    test_agent_process_running,
)
from sacl.recovery.safe_to_resume import (
    SafeToResumeDecision,
    SafeToResumeOutcome,
    assert_no_blind_restart,
    evaluate_agent_safe_to_resume,
    evaluate_run_safe_to_resume,
)
from sacl.recovery.startup_reconciliation import (
    StartupReconciliationEngine,
    StartupReconciliationReport,
)
from sacl.recovery.worktree_inspection import (
    GitClient,
    MockGitClient,
    OrphanClassification,
    OrphanedWorktreeInfo,
    PrimaryRepoCleanliness,
    SubprocessGitClient,
    assert_safe_git_command,
    check_primary_repo_clean,
    get_default_git_client,
    inspect_agent_worktree,
    scan_orphaned_worktrees,
    set_default_git_client,
)

__all__ = [
    # Process Identity & PID Recycling
    "ProcessIdentity",
    "ProcessInspectionStatus",
    "ProcessObservationResult",
    "ProcessInspector",
    "MockProcessInspector",
    "SystemProcessInspector",
    "inspect_process",
    "test_agent_process_running",
    "get_default_process_inspector",
    "set_default_process_inspector",
    # Worktree Inspection & Local Dirty-Root Safety
    "assert_safe_git_command",
    "GitClient",
    "SubprocessGitClient",
    "MockGitClient",
    "PrimaryRepoCleanliness",
    "check_primary_repo_clean",
    "inspect_agent_worktree",
    "OrphanClassification",
    "OrphanedWorktreeInfo",
    "scan_orphaned_worktrees",
    "get_default_git_client",
    "set_default_git_client",
    # Safe-To-Resume & Blind Restart Prohibitions
    "SafeToResumeOutcome",
    "SafeToResumeDecision",
    "assert_no_blind_restart",
    "evaluate_agent_safe_to_resume",
    "evaluate_run_safe_to_resume",
    # Interrupted Run Recovery
    "AgentRecoveryReport",
    "InterruptedRunRecoveryReport",
    "find_interrupted_runs",
    "recover_interrupted_run",
    # Startup Reconciliation Engine
    "StartupReconciliationReport",
    "StartupReconciliationEngine",
]

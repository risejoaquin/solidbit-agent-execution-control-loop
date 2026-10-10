"""SACL V1 Cross-Agent File Collision Detection and Pre-Merge Evaluator.

Enforces:
1. Multi-agent concurrent file overlap detection.
2. Collision Pre-Merge Evaluation (raising CollisionDetectedError).
3. Comprehensive wave integration readiness assessment.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from sacl.contracts.exceptions import CollisionDetectedError
from sacl.workspace.dirty_root import check_clean_root
from sacl.workspace.manager import WorkspaceManager


def detect_file_collisions(
    agent_worktrees: Dict[str, Path],
    base_ref: str = "origin/main",
    workspace_manager: Optional[WorkspaceManager] = None,
) -> Dict[str, List[str]]:
    """Evaluates cross-agent diffs to detect concurrent file modifications.

    Args:
        agent_worktrees: Mapping of agent_id to isolated worktree path.
        base_ref: Base reference (e.g. 'origin/main' or 'HEAD') to diff against.
        workspace_manager: Optional WorkspaceManager instance.

    Returns:
        Mapping of colliding file path to the list of agent IDs that modified it.
    """
    mgr = workspace_manager or WorkspaceManager()
    file_to_agents: Dict[str, List[str]] = {}

    for agent_id, wt_path in agent_worktrees.items():
        if not wt_path.exists():
            continue
        modified_files = mgr.get_modified_files(wt_path, base_ref=base_ref)
        for f in modified_files:
            file_to_agents.setdefault(f, []).append(agent_id)

    # Filter to files modified by more than one agent
    collisions = {
        file_path: agents
        for file_path, agents in file_to_agents.items()
        if len(agents) > 1
    }

    return collisions


def assert_no_collisions(
    agent_worktrees: Dict[str, Path],
    base_ref: str = "origin/main",
    run_id: str = "unknown",
    workspace_manager: Optional[WorkspaceManager] = None,
) -> None:
    """Asserts that no cross-agent file modification overlaps exist.

    Raises:
        CollisionDetectedError: If two or more agents modified the same file.
    """
    collisions = detect_file_collisions(
        agent_worktrees=agent_worktrees,
        base_ref=base_ref,
        workspace_manager=workspace_manager,
    )

    if collisions:
        colliding_files = sorted(collisions.keys())
        raise CollisionDetectedError(run_id=run_id, colliding_files=colliding_files)


def evaluate_wave_readiness(
    agent_worktrees: Dict[str, Path],
    expected_reports: Optional[Dict[str, Path]] = None,
    active_agent_ids: Optional[List[str]] = None,
    base_ref: str = "origin/main",
    workspace_manager: Optional[WorkspaceManager] = None,
) -> Dict[str, Any]:
    """Evaluates whether a wave of agent worktrees is certified ready for human integration.

    Pre-merge evaluation criteria (matches collect-results.ps1):
    1. No active running worker processes.
    2. No cross-agent overlapping file modifications.
    3. No dirty worktrees (all modifications committed).
    4. All required deliverable reports exist on disk.

    Returns:
        Structured evaluation result dict.
    """
    mgr = workspace_manager or WorkspaceManager()
    blockers: List[str] = []

    # 1. Active workers
    active = list(active_agent_ids or [])
    if active:
        blockers.append(f"One or more agents are still active: {', '.join(active)}")

    # 2. File collisions
    collisions = detect_file_collisions(agent_worktrees, base_ref=base_ref, workspace_manager=mgr)
    if collisions:
        desc = [f"'{f}' by ({', '.join(agents)})" for f, agents in collisions.items()]
        blockers.append(f"Concurrent file collisions detected: {'; '.join(desc)}")

    # 3. Dirty worktrees
    dirty_worktrees: List[str] = []
    agent_files: Dict[str, List[str]] = {}
    for agent_id, wt_path in agent_worktrees.items():
        if wt_path.exists():
            is_clean, dirty_files = check_clean_root(wt_path, mgr.git_runner)
            if not is_clean:
                dirty_worktrees.append(agent_id)
            agent_files[agent_id] = mgr.get_modified_files(wt_path, base_ref=base_ref)
        else:
            dirty_worktrees.append(f"{agent_id} (missing path)")

    if dirty_worktrees:
        blockers.append(f"Uncommitted changes in worktrees for agents: {', '.join(dirty_worktrees)}")

    # 4. Deliverable reports
    missing_reports: List[str] = []
    if expected_reports:
        for agent_id, report_path in expected_reports.items():
            if not report_path.exists():
                missing_reports.append(agent_id)

    if missing_reports:
        blockers.append(f"Missing required deliverable reports for agents: {', '.join(missing_reports)}")

    ready_for_integration = (len(blockers) == 0)

    return {
        "ready_for_integration": ready_for_integration,
        "blockers": blockers,
        "collisions": collisions,
        "dirty_worktrees": dirty_worktrees,
        "missing_reports": missing_reports,
        "agent_files": agent_files,
    }


__all__ = [
    "detect_file_collisions",
    "assert_no_collisions",
    "evaluate_wave_readiness",
]

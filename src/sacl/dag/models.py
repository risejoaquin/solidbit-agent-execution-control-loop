"""SACL V1 Ephemeral Graph-H DAG Execution Models.

Defines internal representation of DAG nodes, topological barriers, phases,
and run execution context for Graph-H scheduler.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Set

from sacl.contracts.invariants import FailurePolicy, GraphNodeStatus, Verdict
from sacl.contracts.models import ReconciledResult


@dataclass
class DagNodeState:
    """Internal runtime state of a Graph-H DAG node."""

    node_id: str
    agent_id: str
    phase_number: int
    stage_name: str = ""
    timeout_seconds: int = 1800
    max_attempts: int = 1
    current_attempt: int = 0
    gate_required: bool = False
    allowed_states: List[str] = field(default_factory=list)
    status: str = GraphNodeStatus.PENDING.value
    upstream_node_ids: Set[str] = field(default_factory=set)
    downstream_node_ids: Set[str] = field(default_factory=set)
    result_verdict: Optional[str] = None
    reconciled_result: Optional[ReconciledResult] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    def is_terminal(self) -> bool:
        return self.status in {
            GraphNodeStatus.SUCCEEDED.value,
            GraphNodeStatus.FAILED.value,
            GraphNodeStatus.BLOCKED.value,
            GraphNodeStatus.CANCELLED.value,
        }

    def is_passed(self) -> bool:
        if self.status != GraphNodeStatus.SUCCEEDED.value:
            return False
        return self.result_verdict in {
            Verdict.PASS.value,
            Verdict.PASS_REPORT_PRESENT.value,
            Verdict.PARTIAL.value,
        }


@dataclass
class DagPhaseState:
    """Internal runtime state of a Graph-H topological phase."""

    phase_number: int
    stage_name: str
    node_ids: List[str]
    gate_required: bool = False
    status: str = "PENDING"  # PENDING, RUNNING, COMPLETE, FAILED, WAITING_APPROVAL, BLOCKED
    stage_id: Optional[int] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class SchedulerConfig:
    """Configuration for the Ephemeral Graph-H Scheduler."""

    run_id: str
    job_id: str
    target_repo_path: Path
    run_dir: Path
    project_id: str = "solidbit-control-loop"
    max_parallel: int = 3
    default_timeout_minutes: int = 30
    failure_policy: str = FailurePolicy.COMPLETE_STAGE_THEN_HALT.value
    collision_detection_enabled: bool = True
    collision_scope: str = "stage"
    check_clean_root: bool = True

"""SACL V1 Topological Barriers and Dependency Synchronization.

Implements topological barrier rules from CONCURRENCY_AND_LOCKING.md §5.1:
- Phase Barriers: Agents in Phase N+1 cannot launch until all agents in Phase N
  have completed with passing verdicts.
- Dependency Barriers: A downstream node requires all upstream dependency nodes
  to achieve SUCCEEDED with PASS / PARTIAL / PASS (Report Present) verdicts.
- Gate Barriers: Sovereign human authority gates pause execution at WAITING_APPROVAL.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple

from sacl.contracts.invariants import FailurePolicy, GraphNodeStatus, Verdict
from sacl.contracts.models import ApprovalToken
from sacl.dag.models import DagNodeState, DagPhaseState


class DependencyBarrier:
    """Evaluates node-level dependency barriers."""

    @staticmethod
    def evaluate_node_eligibility(
        node: DagNodeState,
        all_nodes: Dict[str, DagNodeState],
    ) -> Tuple[bool, str]:
        """Checks if a PENDING node's dependencies are satisfied to become READY.

        Returns:
            (is_eligible, action_or_reason)
            action_or_reason can be:
            - "BECOME_READY": All upstream dependencies succeeded.
            - "WAITING_DEPENDENCIES": Upstream nodes still in progress.
            - "BLOCKED_BY_DEPENDENCY": An upstream node failed or blocked.
        """
        if node.status != GraphNodeStatus.PENDING.value:
            return False, f"NODE_STATUS_NOT_PENDING_{node.status}"

        if not node.upstream_node_ids:
            return True, "BECOME_READY"

        for up_id in node.upstream_node_ids:
            up_node = all_nodes.get(up_id)
            if not up_node:
                return False, f"MISSING_UPSTREAM_NODE_{up_id}"

            if not up_node.is_terminal():
                return False, "WAITING_DEPENDENCIES"

            # Check if upstream failed or blocked
            if up_node.status in {GraphNodeStatus.FAILED.value, GraphNodeStatus.BLOCKED.value, GraphNodeStatus.CANCELLED.value}:
                return False, "BLOCKED_BY_DEPENDENCY"

            if not up_node.is_passed():
                return False, "BLOCKED_BY_DEPENDENCY"

        return True, "BECOME_READY"


class PhaseBarrier:
    """Evaluates stage/phase boundaries and progression."""

    @staticmethod
    def is_phase_complete(
        phase: DagPhaseState,
        nodes: Dict[str, DagNodeState],
    ) -> bool:
        """Returns True if every node in the phase is in a terminal state."""
        return all(nodes[nid].is_terminal() for nid in phase.node_ids if nid in nodes)

    @staticmethod
    def did_phase_pass(
        phase: DagPhaseState,
        nodes: Dict[str, DagNodeState],
    ) -> bool:
        """Returns True if every node in the phase passed with a passing verdict."""
        for nid in phase.node_ids:
            node = nodes.get(nid)
            if not node or not node.is_passed():
                return False
        return True

    @staticmethod
    def can_advance_to_phase(
        target_phase_number: int,
        phases: List[DagPhaseState],
        nodes: Dict[str, DagNodeState],
    ) -> Tuple[bool, str]:
        """Checks if all prior phases completed successfully."""
        prior_phases = [p for p in phases if p.phase_number < target_phase_number]
        for p in prior_phases:
            if not PhaseBarrier.is_phase_complete(p, nodes):
                return False, f"PRIOR_PHASE_NOT_COMPLETE_Phase_{p.phase_number}"
            if not PhaseBarrier.did_phase_pass(p, nodes):
                return False, f"PRIOR_PHASE_FAILED_Phase_{p.phase_number}"
        return True, "CAN_ADVANCE"

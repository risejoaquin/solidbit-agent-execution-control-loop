"""Tests for topological phase barriers and dependency synchronization."""

from __future__ import annotations

from sacl.contracts.invariants import GraphNodeStatus, Verdict
from sacl.dag.barrier import DependencyBarrier, PhaseBarrier
from sacl.dag.models import DagNodeState, DagPhaseState


def test_dependency_barrier_node_becomes_ready():
    node_a = DagNodeState(
        node_id="A",
        agent_id="A",
        phase_number=1,
        status=GraphNodeStatus.SUCCEEDED.value,
        result_verdict=Verdict.PASS.value,
    )
    node_b = DagNodeState(
        node_id="B",
        agent_id="B",
        phase_number=2,
        status=GraphNodeStatus.PENDING.value,
        upstream_node_ids={"A"},
    )
    all_nodes = {"A": node_a, "B": node_b}

    eligible, action = DependencyBarrier.evaluate_node_eligibility(node_b, all_nodes)
    assert eligible is True
    assert action == "BECOME_READY"


def test_dependency_barrier_waits_for_upstream_in_progress():
    node_a = DagNodeState(
        node_id="A",
        agent_id="A",
        phase_number=1,
        status=GraphNodeStatus.RUNNING.value,  # In progress!
    )
    node_b = DagNodeState(
        node_id="B",
        agent_id="B",
        phase_number=2,
        status=GraphNodeStatus.PENDING.value,
        upstream_node_ids={"A"},
    )
    all_nodes = {"A": node_a, "B": node_b}

    eligible, action = DependencyBarrier.evaluate_node_eligibility(node_b, all_nodes)
    assert eligible is False
    assert action == "WAITING_DEPENDENCIES"


def test_dependency_barrier_blocks_downstream_on_upstream_failure():
    node_a = DagNodeState(
        node_id="A",
        agent_id="A",
        phase_number=1,
        status=GraphNodeStatus.FAILED.value,
        result_verdict=Verdict.FAILED.value,
    )
    node_b = DagNodeState(
        node_id="B",
        agent_id="B",
        phase_number=2,
        status=GraphNodeStatus.PENDING.value,
        upstream_node_ids={"A"},
    )
    all_nodes = {"A": node_a, "B": node_b}

    eligible, action = DependencyBarrier.evaluate_node_eligibility(node_b, all_nodes)
    assert eligible is False
    assert action == "BLOCKED_BY_DEPENDENCY"


def test_phase_barrier_cannot_advance_if_prior_phase_incomplete():
    phase_1 = DagPhaseState(phase_number=1, stage_name="P1", node_ids=["A"])
    phase_2 = DagPhaseState(phase_number=2, stage_name="P2", node_ids=["B"])

    node_a = DagNodeState(
        node_id="A",
        agent_id="A",
        phase_number=1,
        status=GraphNodeStatus.RUNNING.value,
    )
    node_b = DagNodeState(
        node_id="B", agent_id="B", phase_number=2, status=GraphNodeStatus.PENDING.value
    )
    nodes = {"A": node_a, "B": node_b}

    can_adv, reason = PhaseBarrier.can_advance_to_phase(2, [phase_1, phase_2], nodes)
    assert can_adv is False
    assert "PRIOR_PHASE_NOT_COMPLETE" in reason


def test_phase_barrier_can_advance_when_prior_phase_passed():
    phase_1 = DagPhaseState(phase_number=1, stage_name="P1", node_ids=["A"])
    phase_2 = DagPhaseState(phase_number=2, stage_name="P2", node_ids=["B"])

    node_a = DagNodeState(
        node_id="A",
        agent_id="A",
        phase_number=1,
        status=GraphNodeStatus.SUCCEEDED.value,
        result_verdict=Verdict.PASS.value,
    )
    node_b = DagNodeState(
        node_id="B", agent_id="B", phase_number=2, status=GraphNodeStatus.PENDING.value
    )
    nodes = {"A": node_a, "B": node_b}

    can_adv, reason = PhaseBarrier.can_advance_to_phase(2, [phase_1, phase_2], nodes)
    assert can_adv is True
    assert reason == "CAN_ADVANCE"

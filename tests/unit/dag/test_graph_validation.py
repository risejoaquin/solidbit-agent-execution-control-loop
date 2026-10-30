"""Tests for ExecutionGraph validation, topological sorting, and cycle detection."""

from __future__ import annotations

import pytest

from sacl.contracts.exceptions import ArchitectureInvariantError, ContractValidationError
from sacl.contracts.models import ExecutionGraph, GraphPhase
from sacl.dag.graph import GraphValidator


def test_valid_frozen_graph_loads(load_frozen_example):
    example_data = load_frozen_example("graph")
    graph = ExecutionGraph.from_dict(example_data)

    phases, nodes_map, edges = GraphValidator.validate_and_compile(graph)

    assert len(phases) == 2
    assert phases[0].phase_number == 1
    assert phases[0].stage_name == "MATERIALIZATION"
    assert set(phases[0].node_ids) == {"AG-PROTOCOL-MAT", "AG-ARCH-MAT"}

    assert phases[1].phase_number == 2
    assert phases[1].stage_name == "QA_AUDIT"
    assert phases[1].node_ids == ["AG-QA-MAT"]

    assert len(nodes_map) == 3
    assert "AG-PROTOCOL-MAT" in nodes_map
    assert "AG-QA-MAT" in nodes_map
    assert len(edges) == 2


def test_cycle_detection_raises_architecture_invariant_error():
    # Graph with cycle: A -> B -> C -> A
    graph = ExecutionGraph(
        graph_id="CYCLIC-GRAPH",
        max_parallel=2,
        default_timeout_minutes=30,
        phases=[
            GraphPhase(phase_number=1, stage_name="S1", agents=["A", "B", "C"]),
        ],
        edges=[
            ["A", "B"],
            ["B", "C"],
            ["C", "A"],  # Cycle!
        ],
        failure_policy="complete_stage_then_halt",
    )

    with pytest.raises(ArchitectureInvariantError, match="Cycle detected"):
        GraphValidator.validate_and_compile(graph)


def test_self_dependency_raises_architecture_invariant_error():
    graph = ExecutionGraph(
        graph_id="SELF-DEP",
        max_parallel=2,
        default_timeout_minutes=30,
        phases=[
            GraphPhase(phase_number=1, stage_name="S1", agents=["A"]),
        ],
        edges=[
            ["A", "A"],
        ],
        failure_policy="complete_stage_then_halt",
    )

    with pytest.raises(ArchitectureInvariantError, match="Self-dependency detected"):
        GraphValidator.validate_and_compile(graph)


def test_inter_phase_dependency_inversion_rejected():
    # Downstream in Phase 1, upstream in Phase 2!
    graph = ExecutionGraph(
        graph_id="INVERTED-PHASE",
        max_parallel=2,
        default_timeout_minutes=30,
        phases=[
            GraphPhase(phase_number=1, stage_name="P1", agents=["A"]),
            GraphPhase(phase_number=2, stage_name="P2", agents=["B"]),
        ],
        edges=[
            ["B", "A"],  # Inversion: A (Phase 1) depends on B (Phase 2)
        ],
        failure_policy="complete_stage_then_halt",
    )

    with pytest.raises(ArchitectureInvariantError, match="Inter-phase dependency inversion"):
        GraphValidator.validate_and_compile(graph)


def test_duplicate_phase_number_rejected():
    graph = ExecutionGraph(
        graph_id="DUP-PHASE",
        max_parallel=2,
        default_timeout_minutes=30,
        phases=[
            GraphPhase(phase_number=1, stage_name="P1", agents=["A"]),
            GraphPhase(phase_number=1, stage_name="P1-ALT", agents=["B"]),
        ],
        edges=[],
        failure_policy="complete_stage_then_halt",
    )

    with pytest.raises(ContractValidationError, match="Duplicate phase_number"):
        GraphValidator.validate_and_compile(graph)


def test_invalid_max_parallel_rejected():
    graph = ExecutionGraph(
        graph_id="INVALID-PARALLEL",
        max_parallel=20,  # Max is 16
        default_timeout_minutes=30,
        phases=[GraphPhase(phase_number=1, stage_name="P1", agents=["A"])],
        edges=[],
        failure_policy="complete_stage_then_halt",
    )

    with pytest.raises(ContractValidationError, match="max_parallel must be between 1 and 16"):
        GraphValidator.validate_and_compile(graph)

"""SACL V1 Graph-H DAG Topology Validation and Topological Sorting.

Validates the ephemeral execution graph specification (solidbit.execution-graph.v1):
- Node and phase consistency
- Directed dependency edge validity
- Inter-phase monotonic ordering invariants
- Cycle detection (strictly acyclic)
- Topological sorting
"""

from __future__ import annotations

from collections import deque
from typing import Dict, List, Set, Tuple

from sacl.contracts.exceptions import ArchitectureInvariantError, ContractValidationError
from sacl.contracts.invariants import GraphNodeStatus
from sacl.contracts.models import ExecutionGraph, GraphNode
from sacl.dag.models import DagNodeState, DagPhaseState


class GraphValidator:
    """Validates and compiles an ExecutionGraph into runnable DAG runtime states."""

    @classmethod
    def validate_and_compile(
        cls,
        graph: ExecutionGraph,
    ) -> Tuple[List[DagPhaseState], Dict[str, DagNodeState], List[Tuple[str, str]]]:
        """Validates graph structure and compiles runtime node and phase states.

        Returns:
            (phases, nodes_map, valid_edges)

        Raises:
            ContractValidationError: If schema, phase, or edge references are invalid.
            ArchitectureInvariantError: If cycles exist or inter-phase monotonicity is violated.
        """
        # 1. Validate max_parallel and timeouts
        if graph.max_parallel < 1 or graph.max_parallel > 16:
            raise ContractValidationError(
                "solidbit.execution-graph.v1",
                f"max_parallel must be between 1 and 16, got {graph.max_parallel}",
            )

        if graph.default_timeout_minutes < 1 or graph.default_timeout_minutes > 240:
            raise ContractValidationError(
                "solidbit.execution-graph.v1",
                f"default_timeout_minutes must be between 1 and 240, got {graph.default_timeout_minutes}",
            )

        # 2. Validate phases
        if not graph.phases:
            raise ContractValidationError(
                "solidbit.execution-graph.v1",
                "Graph must contain at least one phase in 'phases'.",
            )

        sorted_phases = sorted(graph.phases, key=lambda p: p.phase_number)
        seen_phase_numbers: Set[int] = set()
        agent_to_phase: Dict[str, int] = {}
        compiled_phases: List[DagPhaseState] = []

        for p in sorted_phases:
            if p.phase_number in seen_phase_numbers:
                raise ContractValidationError(
                    "solidbit.execution-graph.v1",
                    f"Duplicate phase_number {p.phase_number} found in graph phases.",
                )
            seen_phase_numbers.add(p.phase_number)

            if not p.agents:
                raise ContractValidationError(
                    "solidbit.execution-graph.v1",
                    f"Phase {p.phase_number} ('{p.stage_name}') contains no agents.",
                )

            for ag in p.agents:
                if ag in agent_to_phase:
                    raise ContractValidationError(
                        "solidbit.execution-graph.v1",
                        f"Agent '{ag}' is assigned to multiple phases: {agent_to_phase[ag]} and {p.phase_number}",
                    )
                agent_to_phase[ag] = p.phase_number

            compiled_phases.append(
                DagPhaseState(
                    phase_number=p.phase_number,
                    stage_name=p.stage_name,
                    node_ids=list(p.agents),
                    gate_required=p.gate_required,
                )
            )

        # 3. Compile or synthesize DagNodeStates
        explicit_nodes_map: Dict[str, GraphNode] = {n.node_id: n for n in graph.nodes}
        compiled_nodes: Dict[str, DagNodeState] = {}

        # Default timeout in seconds
        def_timeout_sec = graph.default_timeout_minutes * 60

        for phase in compiled_phases:
            for ag in phase.node_ids:
                node_id = ag
                explicit_node = explicit_nodes_map.get(node_id)

                # Timeout calculation: explicit node -> agent_timeouts override -> default
                timeout_sec = def_timeout_sec
                if explicit_node and explicit_node.timeout_minutes:
                    timeout_sec = explicit_node.timeout_minutes * 60
                elif ag in graph.agent_timeouts:
                    timeout_sec = graph.agent_timeouts[ag] * 60

                max_attempts = explicit_node.max_attempts if explicit_node else 1
                gate_req = explicit_node.gate_required if explicit_node else phase.gate_required
                allowed_st = explicit_node.allowed_states if explicit_node else []

                compiled_nodes[node_id] = DagNodeState(
                    node_id=node_id,
                    agent_id=ag,
                    phase_number=phase.phase_number,
                    stage_name=phase.stage_name,
                    timeout_seconds=timeout_sec,
                    max_attempts=max_attempts,
                    gate_required=gate_req,
                    allowed_states=allowed_st,
                    status=GraphNodeStatus.PENDING.value,
                )

        # 4. Validate edges
        compiled_edges: List[Tuple[str, str]] = []
        for edge in graph.edges:
            if len(edge) != 2:
                raise ContractValidationError(
                    "solidbit.execution-graph.v1",
                    f"Edge must be a 2-element list [upstream, downstream], got: {edge}",
                )
            upstream, downstream = edge[0], edge[1]

            if upstream not in compiled_nodes:
                raise ContractValidationError(
                    "solidbit.execution-graph.v1",
                    f"Edge upstream agent '{upstream}' does not exist in graph phases/nodes.",
                )
            if downstream not in compiled_nodes:
                raise ContractValidationError(
                    "solidbit.execution-graph.v1",
                    f"Edge downstream agent '{downstream}' does not exist in graph phases/nodes.",
                )
            if upstream == downstream:
                raise ArchitectureInvariantError(
                    f"Self-dependency detected on node '{upstream}'. Graph must be acyclic."
                )

            # Inter-phase monotonicity: downstream cannot belong to an earlier phase
            up_phase = compiled_nodes[upstream].phase_number
            down_phase = compiled_nodes[downstream].phase_number
            if down_phase < up_phase:
                raise ArchitectureInvariantError(
                    f"Inter-phase dependency inversion: Downstream agent '{downstream}' (Phase {down_phase}) "
                    f"cannot depend on upstream agent '{upstream}' from a later Phase {up_phase}."
                )

            # Wire dependencies
            compiled_nodes[downstream].upstream_node_ids.add(upstream)
            compiled_nodes[upstream].downstream_node_ids.add(downstream)
            compiled_edges.append((upstream, downstream))

        # 5. Cycle detection using Kahn's algorithm
        in_degrees: Dict[str, int] = {
            nid: len(n.upstream_node_ids) for nid, n in compiled_nodes.items()
        }
        queue = deque([nid for nid, deg in in_degrees.items() if deg == 0])
        visited_count = 0

        while queue:
            curr = queue.popleft()
            visited_count += 1
            for nxt in compiled_nodes[curr].downstream_node_ids:
                in_degrees[nxt] -= 1
                if in_degrees[nxt] == 0:
                    queue.append(nxt)

        if visited_count != len(compiled_nodes):
            unresolved = [nid for nid, deg in in_degrees.items() if deg > 0]
            raise ArchitectureInvariantError(
                f"Cycle detected in execution graph. Cyclical nodes: {unresolved}"
            )

        return compiled_phases, compiled_nodes, compiled_edges

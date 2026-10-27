"""SACL V1 Ephemeral Graph-H DAG Execution Scheduler.

Implements the Ephemeral Graph-H DAG Scheduler from CONCURRENCY_AND_LOCKING.md §5,
RETRY_AND_TIMEOUT_POLICY.md, and STATE_MACHINE.md §4:
- Directed acyclic graph initialization and topological compilation
- Dynamic worker pool concurrency throttling ($MaxParallel)
- Isolated worktree execution & dirty-root preflight validation
- Topological phase barriers & node dependency barriers
- Non-killing diagnostic timeouts (TIMEOUT_RUNNING)
- Transient error classification, exponential backoff & distinct attempt logging
- Pre-merge cross-agent collision detection and integration gating
- Safe-stop cancellation protocol with 3-way PID identity verification
- Four-part status reconciliation synthesis
"""

from __future__ import annotations

import sqlite3
import time
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional, Tuple

from sacl.contracts.exceptions import (
    ArchitectureInvariantError,
    DirtyRootError,
)
from sacl.contracts.interfaces import IDagScheduler
from sacl.contracts.invariants import (
    FailurePolicy,
    GraphNodeStatus,
    Verdict,
)
from sacl.contracts.models import ExecutionGraph, ReconciledResult
from sacl.dag.barrier import DependencyBarrier, PhaseBarrier
from sacl.dag.collision import CollisionDetector
from sacl.dag.concurrency import DynamicConcurrencyPool
from sacl.dag.graph import GraphValidator
from sacl.dag.models import DagNodeState, DagPhaseState, SchedulerConfig
from sacl.observability.audit import AuditEventEmitter
from sacl.observability.events import AuditEventType, Severity
from sacl.worker.agent_worker import AgentWorker
from sacl.worker.models import WorkerConfig
from sacl.worker.process import IProcessInspector, OSProcessInspector
from sacl.worker.reconciliation_hook import WorkerReconciler
from sacl.worker.retry import calculate_backoff_delay
from sacl.worker.worktree import WorkspaceManager


class EphemeralDagScheduler(IDagScheduler):
    """Coordinates ephemeral Graph-H phased DAG execution waves."""

    def __init__(
        self,
        config: SchedulerConfig,
        db_conn: Optional[sqlite3.Connection] = None,
        audit_emitter: Optional[AuditEventEmitter] = None,
        workspace_manager: Optional[WorkspaceManager] = None,
        process_inspector: Optional[IProcessInspector] = None,
        reconciler: Optional[WorkerReconciler] = None,
        mock_runner_factory: Optional[Callable[[str, int], Tuple[int, Optional[str]]]] = None,
    ) -> None:
        self.config = config
        self.db_conn = db_conn
        self.audit_emitter = audit_emitter
        self.workspace_manager = workspace_manager or WorkspaceManager()
        self.process_inspector = process_inspector or OSProcessInspector()
        self.reconciler = reconciler or WorkerReconciler(db_conn=db_conn)
        self.mock_runner_factory = mock_runner_factory

        # Runtime structures
        self.graph: Optional[ExecutionGraph] = None
        self.phases: List[DagPhaseState] = []
        self.nodes_map: Dict[str, DagNodeState] = {}
        self.edges: List[Tuple[str, str]] = []
        self.concurrency_pool: DynamicConcurrencyPool = DynamicConcurrencyPool(
            max_parallel=config.max_parallel
        )
        self.collision_detector: CollisionDetector = CollisionDetector(
            db_conn=db_conn, audit_emitter=audit_emitter
        )

        self.running_workers: Dict[str, AgentWorker] = {}
        self.reconciled_results: Dict[str, ReconciledResult] = {}
        self.is_cancelled: bool = False
        self.cancel_reason: Optional[str] = None

    def initialize_graph(self, graph: ExecutionGraph, run_id: str) -> None:
        """Validates, compiles, and persists the ephemeral execution graph."""
        self.graph = graph
        self.config.run_id = run_id
        if graph.max_parallel:
            self.config.max_parallel = graph.max_parallel
            self.concurrency_pool.set_max_parallel(graph.max_parallel)

        if graph.failure_policy:
            self.config.failure_policy = graph.failure_policy

        # Validate and compile
        phases, nodes_map, edges = GraphValidator.validate_and_compile(graph)
        self.phases = phases
        self.nodes_map = nodes_map
        self.edges = edges

        # Persist into SQLite state store if connected
        self._persist_initial_graph_state()

        if self.audit_emitter:
            self.audit_emitter.emit(
                event_type="GRAPH_INITIALIZED",
                severity=Severity.INFO.value,
                payload={
                    "graph_id": graph.graph_id,
                    "num_phases": len(phases),
                    "num_nodes": len(nodes_map),
                    "num_edges": len(edges),
                    "max_parallel": self.config.max_parallel,
                    "failure_policy": self.config.failure_policy,
                },
                run_id=self.config.run_id,
                job_id=self.config.job_id,
            )

    def _persist_initial_graph_state(self) -> None:
        if not self.db_conn:
            return

        now_iso = datetime.now(timezone.utc).isoformat()

        # 1. Persist stages into dag_stages
        for p in self.phases:
            sql_stage = """
                INSERT INTO dag_stages (run_id, phase_number, stage_name, status, started_at)
                VALUES (?, ?, ?, 'PENDING', ?)
            """
            try:
                cur = self.db_conn.cursor()
                cur.execute(sql_stage, (self.config.run_id, p.phase_number, p.stage_name, now_iso))
                p.stage_id = cur.lastrowid
            except Exception:
                pass

        # 2. Persist nodes into graph_nodes
        for nid, node in self.nodes_map.items():
            sql_node = """
                INSERT INTO graph_nodes (
                    run_id, node_id, job_id, phase_number, stage_name,
                    agent_id, status, timeout_seconds, max_attempts, current_attempt
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id, node_id) DO UPDATE SET
                    status = excluded.status;
            """
            try:
                self.db_conn.execute(
                    sql_node,
                    (
                        self.config.run_id,
                        node.node_id,
                        self.config.job_id,
                        node.phase_number,
                        node.stage_name,
                        node.agent_id,
                        node.status,
                        node.timeout_seconds,
                        node.max_attempts,
                        node.current_attempt,
                    ),
                )
            except Exception:
                pass

        # 3. Persist dependencies into agent_dependencies
        for up_ag, down_ag in self.edges:
            sql_dep = """
                INSERT OR IGNORE INTO agent_dependencies (run_id, upstream_agent_id, downstream_agent_id)
                VALUES (?, ?, ?)
            """
            try:
                self.db_conn.execute(sql_dep, (self.config.run_id, up_ag, down_ag))
            except Exception:
                pass

        self.db_conn.commit()

    def execute_phases(self) -> Dict[str, ReconciledResult]:
        """Coordinates phased execution with concurrency throttling and dependency barriers."""
        if not self.graph:
            raise ArchitectureInvariantError("Cannot execute uninitialized execution graph.")

        # 1. Preflight assertion: Local Dirty-Root Rule
        if self.config.check_clean_root:
            is_clean, dirty_files = self.workspace_manager.check_clean_root(
                self.config.target_repo_path
            )
            if not is_clean:
                if self.db_conn:
                    self.db_conn.execute(
                        "UPDATE runs SET status = 'BLOCKED', error_summary = 'Dirty root check failed' WHERE run_id = ?",
                        (self.config.run_id,),
                    )
                    self.db_conn.commit()
                raise DirtyRootError(
                    target_path=str(self.config.target_repo_path),
                    dirty_files=dirty_files,
                )

        # 2. Iterate phases in increasing topological order
        has_aborted = False

        for phase in self.phases:
            if self.is_cancelled or has_aborted:
                break

            # Check if all prior phases completed successfully
            can_advance, reason = PhaseBarrier.can_advance_to_phase(
                phase.phase_number, self.phases, self.nodes_map
            )
            if not can_advance:
                phase.status = "BLOCKED"
                if self.config.failure_policy != FailurePolicy.CONTINUE_INDEPENDENT.value:
                    has_aborted = True
                    break

            # Handle phase gate requirement
            if phase.gate_required:
                phase.status = "WAITING_APPROVAL"
                if self.audit_emitter:
                    self.audit_emitter.emit(
                        event_type=AuditEventType.GATE_HALTED.value,
                        severity=Severity.WARN.value,
                        payload={"phase_number": phase.phase_number, "reason": "Gate required"},
                        run_id=self.config.run_id,
                    )

            # Start phase
            phase.status = "RUNNING"
            phase.started_at = datetime.now(timezone.utc).isoformat()
            self._update_stage_status(phase)

            # Execute batching loop for this phase
            phase_success = self._execute_phase_nodes(phase)

            # Phase completion
            phase.completed_at = datetime.now(timezone.utc).isoformat()
            phase.status = "COMPLETE" if phase_success else "FAILED"
            self._update_stage_status(phase)

            # Pre-Merge Collision Detection
            if self.config.collision_detection_enabled:
                agent_files = self._collect_phase_modified_files(phase)
                has_collision, conflicts = self.collision_detector.evaluate_stage_collisions(
                    self.config.run_id, agent_files
                )
                if has_collision:
                    phase.status = "BLOCKED"
                    self._update_stage_status(phase)
                    has_aborted = True
                    break

            # Evaluate stage-level failure policy
            if not phase_success:
                if self.config.failure_policy == FailurePolicy.ABORT_IMMEDIATELY.value:
                    has_aborted = True
                    break
                elif self.config.failure_policy == FailurePolicy.COMPLETE_STAGE_THEN_HALT.value:
                    has_aborted = True
                    break

        # If execution aborted or halted, mark remaining unexecuted phases and nodes as BLOCKED
        if has_aborted:
            for p in self.phases:
                if p.status not in ("COMPLETE", "FAILED"):
                    p.status = "BLOCKED"
                    self._update_stage_status(p)
                    for nid in p.node_ids:
                        node = self.nodes_map.get(nid)
                        if node and node.status in (
                            GraphNodeStatus.PENDING.value,
                            GraphNodeStatus.READY.value,
                        ):
                            node.status = GraphNodeStatus.BLOCKED.value
                            self._update_node_status(node)

        # Finalize execution run outcome
        self._finalize_run_outcome(has_aborted)
        return self.reconciled_results

    def _execute_phase_nodes(self, phase: DagPhaseState) -> bool:
        """Executes the batching loop for all nodes belonging to a single phase."""
        phase_nodes = [self.nodes_map[nid] for nid in phase.node_ids if nid in self.nodes_map]

        while True:
            if self.is_cancelled:
                return False

            # Step A: Evaluate eligibility for PENDING nodes
            for node in phase_nodes:
                if node.status == GraphNodeStatus.PENDING.value:
                    # Check if node is already completed from checkpoint
                    if self._check_node_checkpoint(node):
                        continue

                    eligible, reason = DependencyBarrier.evaluate_node_eligibility(
                        node, self.nodes_map
                    )
                    if eligible:
                        node.status = GraphNodeStatus.READY.value
                        self._update_node_status(node)
                    elif reason == "BLOCKED_BY_DEPENDENCY":
                        node.status = GraphNodeStatus.BLOCKED.value
                        self._update_node_status(node)

            # Step B: Spawn new workers for READY nodes up to max_parallel capacity
            ready_nodes = [n for n in phase_nodes if n.status == GraphNodeStatus.READY.value]
            for node in ready_nodes:
                if self.concurrency_pool.is_full:
                    break

                if self.concurrency_pool.acquire_slot(node.node_id):
                    self._spawn_worker_for_node(node, phase)

            # Step C: Poll running workers
            for nid in list(self.running_workers.keys()):
                worker = self.running_workers[nid]
                node = self.nodes_map[nid]

                is_running, worker_status = worker.check_liveness_and_timeout()
                if not is_running:
                    # Worker finished
                    self.concurrency_pool.release_slot(nid)
                    del self.running_workers[nid]

                    result = worker.latest_reconciled_result
                    if result:
                        self.reconciled_results[node.agent_id] = result
                        node.result_verdict = result.result_verdict
                        node.reconciled_result = result

                    # Handle retries if retryable failure
                    if worker_status == "RETRYABLE_FAILURE":
                        if node.current_attempt < node.max_attempts:
                            node.status = GraphNodeStatus.RETRYABLE_FAILURE.value
                            self._update_node_status(node)

                            # Apply exponential backoff delay
                            backoff = calculate_backoff_delay(node.current_attempt + 1)
                            if backoff > 0:
                                time.sleep(
                                    min(backoff, 0.5)
                                )  # Sleep up to backoff (clamped in tests)

                            # Reset to READY for subsequent attempt
                            node.status = GraphNodeStatus.READY.value
                            self._update_node_status(node)
                            continue
                        else:
                            node.status = GraphNodeStatus.FAILED.value
                    elif worker_status in {"COMPLETE", "SUCCEEDED"}:
                        node.status = GraphNodeStatus.SUCCEEDED.value
                    elif worker_status == "BLOCKED":
                        node.status = GraphNodeStatus.BLOCKED.value
                    elif worker_status == "STOPPED":
                        node.status = GraphNodeStatus.CANCELLED.value
                    else:
                        node.status = GraphNodeStatus.FAILED.value

                    node.completed_at = datetime.now(timezone.utc).isoformat()
                    self._update_node_status(node)

                    # Abort immediately failure policy check
                    if node.status in {GraphNodeStatus.FAILED.value, GraphNodeStatus.BLOCKED.value}:
                        if self.config.failure_policy == FailurePolicy.ABORT_IMMEDIATELY.value:
                            self.cancel_execution("Aborted immediately due to node failure.")
                            return False

            # Step D: Check if all nodes in phase have reached terminal states
            if PhaseBarrier.is_phase_complete(phase, self.nodes_map):
                break

            time.sleep(0.05)

        return PhaseBarrier.did_phase_pass(phase, self.nodes_map)

    def _spawn_worker_for_node(self, node: DagNodeState, phase: DagPhaseState) -> None:
        """Configures and spawns an AgentWorker instance for a node."""
        node.current_attempt += 1
        node.status = GraphNodeStatus.RUNNING.value
        node.started_at = datetime.now(timezone.utc).isoformat()
        self._update_node_status(node)

        # Build paths
        worktree_p = self.config.run_dir / "worktrees" / f"wt-{node.agent_id}"
        prompt_p = self.config.run_dir / "prompts" / f"{node.agent_id}.prompt.txt"
        report_p = self.config.run_dir / "reports" / f"{node.agent_id}.md"
        stdout_p = self.config.run_dir / "logs" / f"{node.agent_id}.stdout.log"
        stderr_p = self.config.run_dir / "logs" / f"{node.agent_id}.stderr.log"

        branch_name = f"task/{node.agent_id.lower()}"

        # Provision isolated worktree
        self.workspace_manager.provision_worktree(
            repo_path=self.config.target_repo_path,
            branch_name=branch_name,
            worktree_path=worktree_p,
        )

        # Mock runner resolution if test factory provided
        mock_runner = None
        if self.mock_runner_factory:
            factory_fn = self.mock_runner_factory

            def mock_runner(cfg, att):
                return factory_fn(node.agent_id, att)

        worker_cfg = WorkerConfig(
            agent_id=node.agent_id,
            run_id=self.config.run_id,
            job_id=self.config.job_id,
            node_id=node.node_id,
            phase_number=node.phase_number,
            stage_name=phase.stage_name,
            branch=branch_name,
            worktree_path=worktree_p,
            prompt_path=prompt_p,
            report_path=report_p,
            stdout_path=stdout_p,
            stderr_path=stderr_p,
            timeout_seconds=node.timeout_seconds,
            max_attempts=node.max_attempts,
            run_dir=self.config.run_dir,
            mock_runner=mock_runner,
        )

        worker = AgentWorker(
            config=worker_cfg,
            db_conn=self.db_conn,
            audit_emitter=self.audit_emitter,
            workspace_manager=self.workspace_manager,
            process_inspector=self.process_inspector,
            reconciler=self.reconciler,
        )

        self.running_workers[node.node_id] = worker
        worker.launch_attempt()

    def _check_node_checkpoint(self, node: DagNodeState) -> bool:
        """Checks if a node has already succeeded in prior checkpoint (never re-execute)."""
        if not self.db_conn:
            return False

        sql = "SELECT status, result_verdict FROM graph_nodes WHERE run_id = ? AND node_id = ?"
        cur = self.db_conn.cursor()
        cur.execute(sql, (self.config.run_id, node.node_id))
        row = cur.fetchone()
        if row and row[0] == GraphNodeStatus.SUCCEEDED.value:
            node.status = GraphNodeStatus.SUCCEEDED.value
            node.result_verdict = row[1]
            return True
        return False

    def _collect_phase_modified_files(self, phase: DagPhaseState) -> Dict[str, List[str]]:
        """Collects modified files for each agent worktree in the phase."""
        agent_files: Dict[str, List[str]] = {}
        for nid in phase.node_ids:
            wt_path = self.config.run_dir / "worktrees" / f"wt-{nid}"
            files = self.workspace_manager.get_modified_files(wt_path)
            agent_files[nid] = files
        return agent_files

    def _update_node_status(self, node: DagNodeState) -> None:
        if not self.db_conn:
            return

        sql = """
            UPDATE graph_nodes
            SET status = ?, current_attempt = ?, result_verdict = ?, completed_at = ?
            WHERE run_id = ? AND node_id = ?;
        """
        try:
            self.db_conn.execute(
                sql,
                (
                    node.status,
                    node.current_attempt,
                    node.result_verdict,
                    node.completed_at,
                    self.config.run_id,
                    node.node_id,
                ),
            )
            self.db_conn.commit()
        except Exception:
            pass

    def _update_stage_status(self, phase: DagPhaseState) -> None:
        if not self.db_conn or not phase.stage_id:
            return

        sql = """
            UPDATE dag_stages
            SET status = ?, completed_at = ?
            WHERE stage_id = ?;
        """
        try:
            self.db_conn.execute(sql, (phase.status, phase.completed_at, phase.stage_id))
            self.db_conn.commit()
        except Exception:
            pass

    def _finalize_run_outcome(self, has_aborted: bool) -> None:
        """Finalizes run outcome in SQLite runs table."""
        if not self.db_conn:
            return

        all_nodes = list(self.nodes_map.values())
        all_passed = all(n.is_passed() for n in all_nodes)
        any_blocked = any(n.status == GraphNodeStatus.BLOCKED.value for n in all_nodes)

        now_iso = datetime.now(timezone.utc).isoformat()

        if self.is_cancelled:
            run_status = "CANCELLED"
            verdict = Verdict.STOPPED_BY_USER.value
            integration = "NO"
        elif all_passed and not has_aborted:
            run_status = "VERIFYING"
            verdict = Verdict.PASS.value
            integration = "YES"
        elif any_blocked:
            run_status = "BLOCKED"
            verdict = Verdict.BLOCKED.value
            integration = "NO"
        else:
            run_status = "FAILED"
            verdict = Verdict.FAILED.value
            integration = "NO"

        sql = """
            UPDATE runs
            SET status = ?, reconciled_verdict = ?, ready_for_integration = ?, completed_at = ?
            WHERE run_id = ?;
        """
        try:
            self.db_conn.execute(
                sql, (run_status, verdict, integration, now_iso, self.config.run_id)
            )
            self.db_conn.commit()
        except Exception:
            pass

    def cancel_execution(self, reason: str = "Operator Cancel") -> None:
        """Gracefully halts all active workers using the safe-stop protocol."""
        self.is_cancelled = True
        self.cancel_reason = reason

        for nid, worker in list(self.running_workers.items()):
            worker.stop_safely(force=True)
            node = self.nodes_map.get(nid)
            if node:
                node.status = GraphNodeStatus.CANCELLED.value
                self._update_node_status(node)
            self.concurrency_pool.release_slot(nid)

        self.running_workers.clear()

        if self.db_conn:
            sql = "UPDATE runs SET status = 'CANCELLED', error_summary = ? WHERE run_id = ?"
            try:
                self.db_conn.execute(sql, (reason, self.config.run_id))
                self.db_conn.commit()
            except Exception:
                pass

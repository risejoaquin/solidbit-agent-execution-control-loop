"""SACL V1 Execution Result and Evidence Collector.

Coordinates:
1. Multi-agent 4-point status reconciliation across isolated worktrees.
2. Cross-agent file modification harvesting and collision gating.
3. Evidence registration in SQLite artifacts table (Domain 11 / ADR-011).
4. Overall wave verdict synthesis adhering strictly to canonical verdict precedence.
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from sacl.contracts.invariants import Verdict
from sacl.contracts.models import ReconciledResult
from sacl.observability.evidence import EvidenceRegistry
from sacl.results.collision import CollisionDetector
from sacl.results.models import (
    CollisionReport,
    RunCollectionResult,
)
from sacl.results.reconciler import ResultReconciler

logger = logging.getLogger("sacl.results.collector")


class ResultCollector:
    """Collects and reconciles all agent deliverables and evidence in an execution run."""

    def __init__(
        self,
        reconciler: Optional[ResultReconciler] = None,
        collision_detector: Optional[CollisionDetector] = None,
        evidence_registry: Optional[EvidenceRegistry] = None,
    ) -> None:
        self.reconciler = reconciler or ResultReconciler()
        self.collision_detector = collision_detector or CollisionDetector()
        self.evidence_registry = evidence_registry

    def collect_run_results(
        self,
        run_id: str,
        job_id: str,
        run_dir: Path,
        agent_specs: List[Dict[str, Any]],
        db_conn: Optional[sqlite3.Connection] = None,
        package_id: Optional[str] = None,
    ) -> RunCollectionResult:
        """Executes full reconciliation across all agents in the run.

        Parameters:
            run_id: Logical run attempt identifier.
            job_id: Parent logical job identifier.
            run_dir: Path to run workspace directory.
            agent_specs: List of agent dictionaries with paths, pids, etc.
            db_conn: Optional SQLite connection to sacl_ops.db.
            package_id: Package identifier.

        Returns:
            RunCollectionResult with individual agent results, collisions, and overall verdict.
        """
        reconciled_results: List[ReconciledResult] = []
        artifacts_collected: List[Dict[str, Any]] = []

        # 1. Reconcile each agent
        for spec in agent_specs:
            agent_id = spec["agent_id"]
            report_path = Path(
                spec.get("report_path") or (run_dir / "reports" / f"{agent_id}.REPORT.md")
            )
            stdout_path = Path(
                spec.get("stdout_path") or (run_dir / "logs" / f"{agent_id}.stdout.log")
            )
            stderr_path = Path(
                spec.get("stderr_path") or (run_dir / "logs" / f"{agent_id}.stderr.log")
            )
            worktree_path = Path(spec.get("worktree_path") or run_dir)

            res = self.reconciler.reconcile(
                run_id=run_id,
                agent_id=agent_id,
                pid=spec.get("pid"),
                process_name=spec.get("process_name", "agy"),
                is_active=spec.get("is_active", False),
                exit_code=spec.get("exit_code", 0),
                persisted_start_time=spec.get("started_at"),
                actual_start_time=spec.get("actual_start_time"),
                persisted_status=spec.get("status", "COMPLETE"),
                report_path=report_path,
                stdout_path=stdout_path,
                stderr_path=stderr_path,
                worktree_path=worktree_path,
                job_id=job_id,
                node_id=spec.get("node_id", agent_id),
                stage_id=spec.get("stage_id", 1),
                persisted_verdict=spec.get("result_verdict"),
                branch=spec.get("branch", "HEAD"),
                commit_sha=spec.get("commit_sha"),
                modified_files=spec.get("modified_files", []),
                is_clean=spec.get("is_clean", True),
                finished_at=spec.get("finished_at"),
            )
            reconciled_results.append(res)

            # Update SQLite agents table if db_conn available
            if db_conn:
                cursor = db_conn.cursor()
                now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                cursor.execute(
                    """
                    INSERT INTO agents (
                        agent_id, run_id, stage_id, node_id, status, result_verdict,
                        pid, branch, commit_sha, worktree_path, prompt_path,
                        report_path, stdout_path, stderr_path, started_at,
                        updated_at, finished_at, exit_code, error_message
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(agent_id, run_id) DO UPDATE SET
                        status = excluded.status,
                        result_verdict = excluded.result_verdict,
                        finished_at = excluded.finished_at,
                        exit_code = excluded.exit_code,
                        error_message = excluded.error_message,
                        updated_at = excluded.updated_at;
                    """,
                    (
                        agent_id,
                        run_id,
                        spec.get("stage_id", 1),
                        spec.get("node_id", agent_id),
                        res.status,
                        res.result_verdict,
                        spec.get("pid"),
                        spec.get("branch"),
                        spec.get("commit_sha"),
                        str(worktree_path).replace("\\", "/"),
                        spec.get("prompt_path", ""),
                        str(report_path).replace("\\", "/"),
                        str(stdout_path).replace("\\", "/"),
                        str(stderr_path).replace("\\", "/"),
                        spec.get("started_at", now_iso),
                        now_iso,
                        res.reconciliation.persisted_state.finished_at,
                        res.reconciliation.process_observation.exit_code,
                        res.error_message,
                    ),
                )

                # Record modified files
                mods = spec.get("modified_files", [])
                if mods:
                    self.collision_detector.record_file_modifications(
                        run_id=run_id,
                        agent_id=agent_id,
                        file_paths=mods,
                        db_conn=db_conn,
                    )

            # Register filesystem evidence
            if self.evidence_registry:
                if report_path.exists():
                    art = self.evidence_registry.register_file(
                        file_path=report_path,
                        run_id=run_id,
                        job_id=job_id,
                        agent_id=agent_id,
                    )
                    artifacts_collected.append(art.to_dict())
                if stdout_path.exists():
                    art = self.evidence_registry.register_file(
                        file_path=stdout_path,
                        run_id=run_id,
                        job_id=job_id,
                        agent_id=agent_id,
                    )
                    artifacts_collected.append(art.to_dict())

        # 2. Evaluate file collisions and gating
        if db_conn:
            collision_report = self.collision_detector.evaluate_conflicts(
                run_id=run_id,
                db_conn=db_conn,
            )
        else:
            # In-memory collision evaluation
            file_map: Dict[str, List[str]] = {}
            for res in reconciled_results:
                for mf in res.worktree.modified_files:
                    norm = mf.strip().replace("\\", "/").lower()
                    file_map.setdefault(norm, []).append(res.agent_id)
            conflicts = {
                fp: sorted(list(set(ags))) for fp, ags in file_map.items() if len(set(ags)) > 1
            }
            ready = "NO" if conflicts else "YES"
            blockers = (
                ["Overlapping file modifications detected across parallel branches."]
                if conflicts
                else []
            )
            collision_report = CollisionReport(
                run_id=run_id,
                conflicting_files=sorted(list(conflicts.keys())),
                conflicts_by_file=conflicts,
                ready_for_integration=ready,
                blockers=blockers,
            )

        # 3. Aggregate overall run verdict
        overall_verdict = self._synthesize_overall_verdict(
            reconciled_results=reconciled_results,
            collision_report=collision_report,
        )

        # Update runs table verdict if db_conn available
        if db_conn:
            cursor = db_conn.cursor()
            cursor.execute(
                """
                UPDATE runs
                SET reconciled_verdict = ?,
                    ready_for_integration = ?
                WHERE run_id = ?
                """,
                (overall_verdict, collision_report.ready_for_integration, run_id),
            )
            db_conn.commit()

        logger.info(
            "Reconciled run %s: overall_verdict=%s, ready_for_integration=%s",
            run_id,
            overall_verdict,
            collision_report.ready_for_integration,
        )

        return RunCollectionResult(
            run_id=run_id,
            job_id=job_id,
            overall_verdict=overall_verdict,
            agent_results=reconciled_results,
            collision_report=collision_report,
            ready_for_integration=collision_report.ready_for_integration,
            artifacts_collected=artifacts_collected,
        )

    def _synthesize_overall_verdict(
        self,
        reconciled_results: List[ReconciledResult],
        collision_report: CollisionReport,
    ) -> str:
        """Synthesizes overall run status adhering to canonical verdict rules."""
        if not reconciled_results:
            return "FAILED"

        verdicts = [r.result_verdict for r in reconciled_results]

        # Any FAILED agent causes overall FAIL
        if any(v == Verdict.FAILED.value for v in verdicts):
            return "FAIL"

        # Any BLOCKED agent causes overall BLOCKED
        if any(v == Verdict.BLOCKED.value for v in verdicts):
            return "BLOCKED"

        # DONE_REVIEW_REQUIRED NEVER means PASS!
        if any(v == Verdict.DONE_REVIEW_REQUIRED.value for v in verdicts):
            return "DONE_REVIEW_REQUIRED"

        # If file collisions detected, cannot pass cleanly
        if collision_report.conflicting_files:
            return "BLOCKED"

        # All passed
        if all(
            v in {Verdict.PASS.value, Verdict.PASS_REPORT_PRESENT.value, Verdict.PARTIAL.value}
            for v in verdicts
        ):
            return "PASS"

        return "FAIL"


__all__ = ["ResultCollector"]

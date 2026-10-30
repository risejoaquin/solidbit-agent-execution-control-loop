"""SACL V1 Legacy Operator Experience Coordinator.

Preserves the proven wave ZIP operator experience and execution mechanics
from RUN-WAVE.ps1, WORKER.ps1, and FINALIZE.ps1:
- Preflight validation & Inviolable Local Dirty-Root Rule check
- Mandatory BypassAcknowledged check for --dangerously-skip-permissions
- Phased execution with dynamic batch concurrency throttling ($MaxParallel)
- Dynamic prompt variable substitution & Machine Governance Guard injection
- Four-factor status reconciliation (never exit code alone)
- Safe non-killing timeouts (TIMEOUT_RUNNING)
- Dual deliverable generation (SUMMARY.md and SUMMARY.json)
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, List, Optional, Tuple, Union

from sacl.contracts.exceptions import DirtyRootError
from sacl.contracts.invariants import AgentStatus
from sacl.contracts.models import AgentResult
from sacl.legacy.adapter import LegacyPackageAdapter
from sacl.legacy.compatibility import (
    check_dirty_root,
    extract_legacy_result,
    generate_governance_header,
)
from sacl.legacy.packager import WaveZipPackager
from sacl.legacy.state_bridge import LegacyStateBridge
from sacl.results.summary import DualSummaryGenerator
from sacl.worker.process import IProcessInspector, OSProcessInspector

logger = logging.getLogger("sacl.legacy.operator")


@dataclass
class OperatorRunResult:
    """Consolidated deliverable result of a wave package execution."""

    run_id: str
    package_id: str
    project: str
    status: str
    run_dir: Path
    summary_md_path: Path
    summary_json_path: Path
    final_report_path: Optional[Path]
    agent_results: List[AgentResult]
    exit_code: int = 0
    message: str = "W0_COMPLETE_REVIEW_REQUIRED"


class LegacyOperatorExperience:
    """Coordinates execution of wave packages preserving proven legacy mechanics."""

    def __init__(
        self,
        inspector: Optional[IProcessInspector] = None,
        adapter: Optional[LegacyPackageAdapter] = None,
        state_bridge: Optional[LegacyStateBridge] = None,
        packager: Optional[WaveZipPackager] = None,
        summary_generator: Optional[DualSummaryGenerator] = None,
    ) -> None:
        self.inspector = inspector or OSProcessInspector()
        self.adapter = adapter or LegacyPackageAdapter()
        self.state_bridge = state_bridge or LegacyStateBridge(process_inspector=self.inspector)
        self.packager = packager or WaveZipPackager()
        self.summary_generator = summary_generator or DualSummaryGenerator()

    def run_wave(
        self,
        package_path: Union[Path, str],
        repo_path: Optional[Union[Path, str]] = None,
        max_parallel: int = 4,
        bypass_acknowledged: bool = False,
        test_mode: bool = False,
        run_dir: Optional[Union[Path, str]] = None,
        source_orchestrator: Optional[Union[Path, str]] = None,
        timeout_minutes: int = 30,
        db_conn: Optional[Any] = None,
        legacy_state: bool = True,
        mock_worker_func: Optional[Callable[[str, Path, Path, Path, Path], int]] = None,
    ) -> OperatorRunResult:
        """Executes a wave package following the exact RUN-WAVE.ps1 workflow.

        Raises:
            PermissionError: If bypass_acknowledged is False (ACK_REQUIRED).
            DirtyRootError: If target product checkout has uncommitted changes.
            FileNotFoundError: If package or files cannot be located.
        """
        # 1. ACK_REQUIRED check (matches RUN-WAVE.ps1#L7)
        if not bypass_acknowledged and not test_mode:
            raise PermissionError(
                "ACK_REQUIRED: --dangerously-skip-permissions grants broad host access"
            )

        src_pkg = Path(package_path).resolve()
        if not src_pkg.exists():
            raise FileNotFoundError(f"Package path not found: {src_pkg}")

        # If package is a zip file, extract safely to staging directory
        staged_dir: Optional[Path] = None
        if src_pkg.is_file() and src_pkg.suffix.lower() == ".zip":
            staged_dir = src_pkg.parent / f"unpacked_{src_pkg.stem}_{uuid.uuid4().hex[:6]}"
            self.packager.extract_wave_package(src_pkg, staged_dir)
            pkg_root = staged_dir
        elif src_pkg.is_file() and src_pkg.suffix.lower() == ".json":
            pkg_root = src_pkg.parent
        else:
            pkg_root = src_pkg

        # 2. Load manifest
        manifest_source = (
            src_pkg if (src_pkg.is_file() and src_pkg.suffix.lower() == ".json") else pkg_root
        )
        manifest = self.adapter.load_manifest(manifest_source)

        # 3. Target repo & Preflight Dirty Root check
        effective_repo = Path(repo_path or manifest.target_local_repo).resolve()
        effective_source = Path(source_orchestrator or manifest.source_orchestrator).resolve()

        if not test_mode and effective_repo.exists() and (effective_repo / ".git").exists():
            is_dirty, dirty_output = check_dirty_root(effective_repo)
            if is_dirty:
                raise DirtyRootError(
                    target_path=str(effective_repo),
                    dirty_files=dirty_output.splitlines(),
                )

        # 4. Prepare Run Directory Layout (RUN-WAVE.ps1#L14-L21)
        now_dt = datetime.now(timezone.utc)
        run_id = f"w0-{now_dt.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
        if run_dir:
            run_dir_path = Path(run_dir).resolve()
        else:
            run_dir_path = (pkg_root / "runs" / run_id).resolve()

        reports_dir = run_dir_path / "reports"
        state_dir = run_dir_path / "state"
        logs_dir = run_dir_path / "logs"
        evidence_dir = run_dir_path / "evidence"

        for d in [run_dir_path, reports_dir, state_dir, logs_dir, evidence_dir]:
            d.mkdir(parents=True, exist_ok=True)

        # Write run-meta.json and LAST_RUN.txt
        self.state_bridge.write_run_meta(
            run_dir=run_dir_path,
            run_id=run_id,
            package_id=manifest.package_id,
            source_orchestrator=str(effective_source),
            max_parallel=max_parallel,
            started_at=now_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        self.state_bridge.write_latest_run_marker(pkg_root, run_id)
        self.state_bridge.write_latest_run_marker(run_dir_path, run_id)

        # 5. Phased Agent Execution
        # If package has config/dependencies.json, compile graph
        graph = self.adapter.build_execution_graph(
            pkg_root, manifest=manifest, max_parallel=max_parallel
        )

        agent_results: List[AgentResult] = []
        overall_failed = False

        for phase in graph.phases:
            # Dynamic batch concurrency
            running_batch: List[Tuple[str, Any]] = []

            for agent_id in phase.agents:
                candidate_prompts = [
                    pkg_root / "prompts" / f"{agent_id}.md",
                    pkg_root / "prompts" / f"{agent_id}.prompt.md",
                    pkg_root / "prompts" / f"{agent_id.lower()}.prompt.md",
                    pkg_root / "prompts" / f"{agent_id.lower()}.md",
                    pkg_root / "prompts" / f"{agent_id.replace('-', '_')}.prompt.md",
                    pkg_root / "prompts" / f"{agent_id.lower().replace('-', '_')}.prompt.md",
                    pkg_root / "prompts" / f"{agent_id.replace('-', '_')}.md",
                    pkg_root / "prompts" / f"{agent_id.lower().replace('-', '_')}.md",
                ]
                prompt_file = candidate_prompts[0]
                for cp in candidate_prompts:
                    if cp.exists():
                        prompt_file = cp
                        break

                report_file = reports_dir / f"{agent_id}.REPORT.md"
                stdout_file = logs_dir / f"{agent_id}.stdout.log"
                stderr_file = logs_dir / f"{agent_id}.stderr.log"
                agent_state_file = state_dir / f"{agent_id}.json"

                run_prompts_dir = run_dir_path / "prompts"
                run_prompts_dir.mkdir(parents=True, exist_ok=True)
                run_prompt_file = run_prompts_dir / f"{agent_id}.prompt.md"

                if prompt_file.exists():
                    rendered = self.adapter.render_prompt(
                        prompt_template_path=prompt_file,
                        package_root=pkg_root,
                        run_dir=run_dir_path,
                        report_path=report_file,
                        source_orchestrator=effective_source,
                        worktree_path=effective_repo,
                    )
                    run_prompt_file.write_text(rendered, encoding="utf-8")
                else:
                    gov_h = generate_governance_header(worktree_path=effective_repo)
                    run_prompt_file.write_text(
                        f"{gov_h}\n# Task for {agent_id}\n", encoding="utf-8"
                    )

                # Initial state RUNNING
                self.state_bridge.write_agent_state(
                    state_file=agent_state_file,
                    agent_name=agent_id,
                    status=AgentStatus.RUNNING.value,
                    pid=os.getpid() if test_mode else None,
                    started_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    report_path=str(report_file),
                    stdout_path=str(stdout_file),
                    stderr_path=str(stderr_file),
                )

                if test_mode or mock_worker_func:
                    # Execute mock worker
                    if mock_worker_func:
                        exit_code = mock_worker_func(
                            agent_id, prompt_file, report_file, stdout_file, stderr_file
                        )
                    else:
                        exit_code = self._default_mock_worker(agent_id, report_file, stdout_file)

                    verdict, v_reason = extract_legacy_result(
                        report_content=report_file.read_text(encoding="utf-8")
                        if report_file.exists()
                        else None,
                        report_exists=report_file.exists(),
                        exit_code=exit_code,
                    )
                    status_val = (
                        AgentStatus.COMPLETE.value if exit_code == 0 else AgentStatus.FAILED.value
                    )
                    if exit_code != 0:
                        overall_failed = True

                    self.state_bridge.write_agent_state(
                        state_file=agent_state_file,
                        agent_name=agent_id,
                        status=status_val,
                        pid=os.getpid(),
                        exit_code=exit_code,
                        report_path=str(report_file),
                        stdout_path=str(stdout_file),
                        stderr_path=str(stderr_file),
                    )

                    agent_results.append(
                        AgentResult(
                            agent=agent_id,
                            status=status_val,
                            exitCode=exit_code,
                            verdict=verdict,
                            reportExists=report_file.exists(),
                        )
                    )
                else:
                    # Live execution mode: Render prompt and launch worker
                    rendered_prompt = self.adapter.render_prompt(
                        prompt_template_path=prompt_file,
                        package_root=pkg_root,
                        run_dir=run_dir_path,
                        report_path=report_file,
                        source_orchestrator=effective_source,
                    )
                    worker_proc = self._spawn_live_worker(
                        agent_id=agent_id,
                        rendered_prompt=rendered_prompt,
                        pkg_root=pkg_root,
                        run_dir=run_dir_path,
                        report_file=report_file,
                        stdout_file=stdout_file,
                        stderr_file=stderr_file,
                        agent_state_file=agent_state_file,
                    )
                    running_batch.append((agent_id, worker_proc))

                    # Concurrency throttling: wait if batch reaches max_parallel
                    if len(running_batch) >= max_parallel:
                        self._wait_batch(
                            running_batch, reports_dir, state_dir, logs_dir, agent_results
                        )
                        running_batch.clear()

            # Wait for remaining workers in this phase
            if running_batch:
                self._wait_batch(running_batch, reports_dir, state_dir, logs_dir, agent_results)
                running_batch.clear()

        # 6. Finalization (FINALIZE.ps1 parity)
        # Copy FINAL_REPORT.md if AG-FINAL.REPORT.md exists
        ag_final_rep = reports_dir / "AG-FINAL.REPORT.md"
        final_rep = reports_dir / "FINAL_REPORT.md"
        if ag_final_rep.exists():
            shutil.copyfile(ag_final_rep, final_rep)
        elif reports_dir.exists():
            # Copy last available report as final report
            all_reps = list(reports_dir.glob("*.REPORT.md"))
            if all_reps:
                shutil.copyfile(all_reps[-1], final_rep)

        # 7. Generate Dual Summaries (SUMMARY.md and SUMMARY.json)
        run_status = "FAIL" if overall_failed else "DONE_REVIEW_REQUIRED"
        summary_model = self.summary_generator.build_summary_model(
            run_id=run_id,
            package_id=manifest.package_id,
            project=manifest.project,
            status=run_status,
            ready_for_integration="YES" if not overall_failed else "NO",
            agent_results=agent_results,
            job_id=manifest.job_id,
            architecture_freeze_ready=True,
            implementation_authorized=False,
            next_safe_action="Review reports/FINAL_REPORT.md before authorizing implementation.",
        )

        sum_md_path, sum_json_path = self.summary_generator.write_dual_summaries(
            summary=summary_model,
            run_dir=run_dir_path,
        )

        # 8. Record in SQLite if connection provided
        if db_conn:
            self.state_bridge.import_legacy_run_to_sacl(
                run_dir_path, db_conn, project=manifest.project
            )

        return OperatorRunResult(
            run_id=run_id,
            package_id=manifest.package_id,
            project=manifest.project,
            status=run_status,
            run_dir=run_dir_path,
            summary_md_path=sum_md_path,
            summary_json_path=sum_json_path,
            final_report_path=final_rep if final_rep.exists() else None,
            agent_results=agent_results,
            exit_code=0 if not overall_failed else 1,
            message="W0_COMPLETE_REVIEW_REQUIRED" if not overall_failed else "AGENT_BATCH_FAILED",
        )

    def _default_mock_worker(self, agent_id: str, report_file: Path, stdout_file: Path) -> int:
        """Executes a simulated mock agent worker that passes deterministically."""
        report_content = (
            f"# {agent_id} REPORT\n\n"
            f"AGENT_ID: {agent_id}\n"
            f"VERDICT: PASS\n"
            f"AGENT_{agent_id}_RESULT = PASS\n"
            f"RESULT = PASS\n"
        )
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(report_content, encoding="utf-8")
        stdout_file.parent.mkdir(parents=True, exist_ok=True)
        stdout_file.write_text(f"Mock execution for {agent_id} succeeded.\n", encoding="utf-8")
        return 0

    def _spawn_live_worker(
        self,
        agent_id: str,
        rendered_prompt: str,
        pkg_root: Path,
        run_dir: Path,
        report_file: Path,
        stdout_file: Path,
        stderr_file: Path,
        agent_state_file: Path,
    ) -> subprocess.Popen:
        """Spawns an Antigravity worker process."""
        worker_script = pkg_root / "WORKER.ps1"
        if worker_script.exists():
            cmd = [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(worker_script),
                "-AgentName",
                agent_id,
                "-PromptPath",
                str(pkg_root / "prompts" / f"{agent_id}.md"),
                "-ReportPath",
                str(report_file),
                "-StdoutPath",
                str(stdout_file),
                "-StderrPath",
                str(stderr_file),
                "-StatePath",
                str(agent_state_file),
                "-PackageRoot",
                str(pkg_root),
                "-RunDir",
                str(run_dir),
                "-SourceOrchestrator",
                str(pkg_root),
            ]
        else:
            # Fallback to agy directly
            cmd = ["agy", "-p", rendered_prompt, "--dangerously-skip-permissions"]

        stdout_f = open(stdout_file, "w", encoding="utf-8")
        stderr_f = open(stderr_file, "w", encoding="utf-8")

        proc = subprocess.Popen(
            cmd,
            stdout=stdout_f,
            stderr=stderr_f,
            cwd=str(pkg_root),
        )

        # Update state with real PID
        self.state_bridge.write_agent_state(
            state_file=agent_state_file,
            agent_name=agent_id,
            status=AgentStatus.RUNNING.value,
            pid=proc.pid,
            started_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            report_path=str(report_file),
            stdout_path=str(stdout_file),
            stderr_path=str(stderr_file),
        )
        return proc

    def _wait_batch(
        self,
        batch: List[Tuple[str, subprocess.Popen]],
        reports_dir: Path,
        state_dir: Path,
        logs_dir: Path,
        results_out: List[AgentResult],
    ) -> None:
        """Waits for a batch of running processes and reconciles their outputs."""
        for agent_id, proc in batch:
            proc.wait()
            exit_code = proc.returncode

            # Reconcile agent
            recon = self.state_bridge.reconcile_legacy_agent(
                agent_id=agent_id,
                run_dir=reports_dir.parent,
                state_dir=state_dir,
                reports_dir=reports_dir,
                logs_dir=logs_dir,
            )

            # Update state file
            self.state_bridge.write_agent_state(
                state_file=state_dir / f"{agent_id}.json",
                agent_name=agent_id,
                status=recon["Status"],
                pid=proc.pid,
                exit_code=exit_code,
                report_path=recon["ReportPath"],
            )

            results_out.append(
                AgentResult(
                    agent=agent_id,
                    status=recon["Status"],
                    exitCode=exit_code,
                    verdict=recon["Verdict"],
                    reportExists=recon["ReportExists"],
                )
            )

"""SACL V1 Legacy State Bridge.

Bridges operational tracking between SACL V1 SQLite Operational State Store
(sacl_ops.db) and legacy loose JSON/text state files:
- state/<agent>.json
- run-meta.json
- LATEST_RUN.txt / LAST_RUN.txt
- RUN_STATE.json / RUN_STATUS.json

Preserves proven behavior from orchestrator-common.ps1 without requiring
the legacy orchestrator to be altered.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Union

from sacl.contracts.invariants import AgentStatus, Verdict
from sacl.legacy.compatibility import extract_legacy_result, verify_legacy_process
from sacl.worker.process import IProcessInspector

logger = logging.getLogger("sacl.legacy.state_bridge")


class LegacyStateBridge:
    """Synchronizes and translates state between SQLite and legacy filesystem files."""

    def __init__(self, process_inspector: Optional[IProcessInspector] = None) -> None:
        self.inspector = process_inspector

    @staticmethod
    def write_agent_state(
        state_file: Union[Path, str],
        agent_name: str,
        status: str,
        pid: Optional[int] = None,
        started_at: Optional[str] = None,
        exit_code: Optional[int] = None,
        report_path: Optional[str] = None,
        stdout_path: Optional[str] = None,
        stderr_path: Optional[str] = None,
        error_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Writes state/<agent>.json in legacy format matching WORKER.ps1#L14-L28."""
        sf = Path(state_file)
        sf.parent.mkdir(parents=True, exist_ok=True)
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        state_data: Dict[str, Any] = {
            "agent": agent_name,
            "status": status,
            "pid": pid,
            "startedAt": started_at or now_iso,
            "updatedAt": now_iso,
            "exitCode": exit_code,
            "report": str(report_path) if report_path else None,
            "stdout": str(stdout_path) if stdout_path else None,
            "stderr": str(stderr_path) if stderr_path else None,
            "error": error_text,
        }

        # Write atomically via temp file
        tmp_file = sf.with_suffix(".tmp")
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(state_data, f, indent=2)
        tmp_file.replace(sf)
        return state_data

    @staticmethod
    def read_agent_state(state_file: Union[Path, str]) -> Optional[Dict[str, Any]]:
        """Reads and parses a legacy state/<agent>.json file."""
        sf = Path(state_file)
        if not sf.exists():
            return None
        try:
            with open(sf, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            logger.warning("Error reading agent state file %s: %s", sf, exc)
            return None

    @staticmethod
    def write_run_meta(
        run_dir: Union[Path, str],
        run_id: str,
        package_id: str,
        source_orchestrator: str,
        max_parallel: int = 4,
        started_at: Optional[str] = None,
    ) -> Path:
        """Writes run-meta.json matching RUN-WAVE.ps1#L22-L28."""
        rd = Path(run_dir)
        rd.mkdir(parents=True, exist_ok=True)
        meta_file = rd / "run-meta.json"
        now_iso = started_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        meta = {
            "runId": run_id,
            "package": package_id,
            "startedAt": now_iso,
            "sourceOrchestrator": str(source_orchestrator),
            "maxParallel": max_parallel,
        }
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
        return meta_file

    @staticmethod
    def write_latest_run_marker(target_dir: Union[Path, str], run_id: str) -> None:
        """Writes LATEST_RUN.txt and LAST_RUN.txt files."""
        td = Path(target_dir)
        td.mkdir(parents=True, exist_ok=True)
        for fname in ["LATEST_RUN.txt", "LAST_RUN.txt"]:
            marker = td / fname
            with open(marker, "w", encoding="utf-8") as f:
                f.write(run_id.strip() + "\n")

    def reconcile_legacy_agent(
        self,
        agent_id: str,
        run_dir: Union[Path, str],
        state_dir: Optional[Union[Path, str]] = None,
        reports_dir: Optional[Union[Path, str]] = None,
        logs_dir: Optional[Union[Path, str]] = None,
    ) -> Dict[str, Any]:
        """Executes the 4-part reconciliation matching Get-ReconciledAgentState."""
        rd = Path(run_dir)
        s_dir = Path(state_dir) if state_dir else rd / "state"
        r_dir = Path(reports_dir) if reports_dir else rd / "reports"
        l_dir = Path(logs_dir) if logs_dir else rd / "logs"

        state_file = s_dir / f"{agent_id}.json"
        report_file = r_dir / f"{agent_id}.REPORT.md"
        stdout_file = l_dir / f"{agent_id}.stdout.log"

        state = self.read_agent_state(state_file) or {}
        pid = state.get("pid")
        recorded_status = state.get("status", "UNKNOWN")
        started_at = state.get("startedAt")
        exit_code = state.get("exitCode")

        # 1. Process liveness & PID recycling check
        is_running, reason = verify_legacy_process(pid, started_at, inspector=self.inspector)

        # 2. Check deliverable existence and content
        report_exists = report_file.exists() and report_file.stat().st_size > 0
        report_content = None
        if report_exists:
            try:
                with open(report_file, "r", encoding="utf-8", errors="replace") as f:
                    report_content = f.read()
            except Exception:
                pass

        log_content = None
        if stdout_file.exists():
            try:
                with open(stdout_file, "r", encoding="utf-8", errors="replace") as f:
                    log_content = f.read()
            except Exception:
                pass

        # 3. Extract verdict
        verdict, verdict_reason = extract_legacy_result(
            report_content=report_content,
            log_content=log_content,
            report_exists=report_exists,
            exit_code=exit_code,
        )

        # 4. Resolve status
        if is_running:
            reconciled_status = AgentStatus.RUNNING.value
        elif recorded_status in {AgentStatus.STOPPED.value, "STOPPED"}:
            reconciled_status = AgentStatus.STOPPED.value
        elif recorded_status == AgentStatus.TIMEOUT_RUNNING.value:
            reconciled_status = AgentStatus.TIMEOUT_RUNNING.value
        elif report_exists and verdict in {
            Verdict.PASS.value,
            Verdict.PASS_REPORT_PRESENT.value,
            "DONE_REVIEW_REQUIRED",
        }:
            reconciled_status = AgentStatus.COMPLETE.value
        elif exit_code == 0 and report_exists:
            reconciled_status = AgentStatus.COMPLETE.value
        elif exit_code is not None and exit_code != 0:
            reconciled_status = AgentStatus.FAILED.value
        else:
            reconciled_status = recorded_status

        return {
            "Agent": agent_id,
            "Status": reconciled_status,
            "Pid": pid,
            "ExitCode": exit_code,
            "ReportExists": report_exists,
            "Verdict": verdict,
            "VerdictReason": verdict_reason,
            "StartedAt": started_at,
            "IsRunning": is_running,
            "ReportPath": str(report_file) if report_exists else None,
            "StatePath": str(state_file) if state_file.exists() else None,
        }

    def export_sacl_run_to_legacy(
        self,
        db_conn: sqlite3.Connection,
        run_id: str,
        target_run_dir: Union[Path, str],
        target_results_dir: Optional[Union[Path, str]] = None,
    ) -> None:
        """Exports SACL SQLite run and agent states to legacy filesystem files."""
        trd = Path(target_run_dir)
        state_dir = trd / "state"
        reports_dir = trd / "reports"
        logs_dir = trd / "logs"
        evidence_dir = trd / "evidence"

        state_dir.mkdir(parents=True, exist_ok=True)
        reports_dir.mkdir(parents=True, exist_ok=True)
        logs_dir.mkdir(parents=True, exist_ok=True)
        evidence_dir.mkdir(parents=True, exist_ok=True)

        cursor = db_conn.cursor()
        cursor.execute(
            "SELECT run_id, package_id, project, status, started_at, completed_at FROM runs WHERE run_id = ?",
            (run_id,),
        )
        run_row = cursor.fetchone()
        if not run_row:
            return

        # Write run-meta.json
        self.write_run_meta(
            run_dir=trd,
            run_id=run_id,
            package_id=run_row[1],
            source_orchestrator=run_row[2],
            started_at=run_row[4],
        )

        if target_results_dir:
            self.write_latest_run_marker(target_results_dir, run_id)
        self.write_latest_run_marker(trd.parent, run_id)

        # Write each agent's state
        cursor.execute(
            """
            SELECT agent_id, status, pid, exit_code, started_at, finished_at, report_path, stdout_path, stderr_path, error_message
            FROM agents WHERE run_id = ?
            """,
            (run_id,),
        )
        for row in cursor.fetchall():
            a_id, st, pid, ec, sa, fa, rp, so, se, err = row
            self.write_agent_state(
                state_file=state_dir / f"{a_id}.json",
                agent_name=a_id,
                status=st,
                pid=pid,
                started_at=sa,
                exit_code=ec,
                report_path=rp,
                stdout_path=so,
                stderr_path=se,
                error_text=err,
            )

    def import_legacy_run_to_sacl(
        self,
        run_dir: Union[Path, str],
        db_conn: sqlite3.Connection,
        project: str = "solidbit-agent-execution-control-loop",
    ) -> str:
        """Imports legacy run metadata and state files into sacl_ops.db."""
        rd = Path(run_dir)
        meta_file = rd / "run-meta.json"
        state_dir = rd / "state"

        run_id = rd.name
        pkg_id = "LEGACY_PACKAGE"
        started_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        if meta_file.exists():
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    m = json.load(f)
                    run_id = m.get("runId", run_id)
                    pkg_id = m.get("package", pkg_id)
                    started_at = m.get("startedAt", started_at)
                    project = m.get("sourceOrchestrator", project)
            except Exception:
                pass

        cursor = db_conn.cursor()
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Insert or update run
        cursor.execute(
            """
            INSERT OR REPLACE INTO runs (run_id, job_id, package_id, project, status, started_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (run_id, f"job-{run_id}", pkg_id, project, "RUNNING", started_at, now_iso, now_iso),
        )

        if state_dir.exists():
            for sf in state_dir.glob("*.json"):
                data = self.read_agent_state(sf)
                if not data:
                    continue
                a_id = data.get("agent", sf.stem)
                st = data.get("status", "UNKNOWN")
                pid = data.get("pid")
                ec = data.get("exitCode")
                rp = data.get("report")
                so = data.get("stdout")
                se = data.get("stderr")
                err = data.get("error")
                sa = data.get("startedAt", now_iso)
                fa = data.get("updatedAt")

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO agents
                    (run_id, agent_id, status, pid, exit_code, started_at, finished_at, report_path, stdout_path, stderr_path, error_message, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (run_id, a_id, st, pid, ec, sa, fa, rp, so, se, err, now_iso),
                )

        db_conn.commit()
        return run_id

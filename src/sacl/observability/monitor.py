"""SACL V1 Terminal Monitor Read Models and ASCII Dashboard.

Implements docs/OBSERVABILITY.md §6:
- Read-only, zero-locking query model against sacl_ops.db (mode=ro).
- Formats real-time execution fleet, hierarchical leases, and collision alerts.
- Renders the canonical ASCII terminal dashboard matching MONITOR.ps1.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def format_duration(seconds: Optional[float]) -> str:
    """Formats duration in seconds as HH:MM:SS, or '--' if None."""
    if seconds is None or seconds < 0:
        return "--"
    total_sec = int(seconds)
    hours = total_sec // 3600
    minutes = (total_sec % 3600) // 60
    secs = total_sec % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


@dataclass
class FleetAgentView:
    """Live state for an individual agent worker displayed in the terminal fleet table."""

    agent_id: str
    status: str
    pid: Optional[int]
    exit_code: Optional[int]
    report_present: bool
    verdict: str
    duration_str: str
    updated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LeaseView:
    """Live mutual exclusion lease state."""

    lease_name: str
    holder_id: str
    holder_pid: int
    acquired_at: str
    heartbeat_at: str
    expires_at: str
    is_expired: bool
    ttl_remaining_seconds: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DashboardSnapshot:
    """Point-in-time consolidated read model for the SACL V1 live monitor dashboard."""

    run_id: str
    project: str
    package_id: str
    status: str
    stage: str
    elapsed_str: str
    agents: List[FleetAgentView]
    active_workers_count: int
    max_parallel: int
    leases: List[LeaseView]
    alerts: List[str]
    conflicts: List[str]
    recent_events: List[Dict[str, Any]] = field(default_factory=list)
    recent_errors: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["agents"] = [a.to_dict() for a in self.agents]
        d["leases"] = [l.to_dict() for l in self.leases]
        return d


class MonitorReadModel:
    """Non-locking, read-only consumer of sacl_ops.db for terminal and UI monitoring."""

    def __init__(self, db_path: Union[Path, str]):
        self.db_path = Path(db_path)

    def _open_read_only_connection(self) -> sqlite3.Connection:
        """Opens a read-only SQLite connection using URI mode to prevent any locking."""
        abs_path = self.db_path.resolve()
        # On Windows, forward slashes are required for SQLite URI mode
        uri_path = abs_path.as_posix()
        uri = f"file:{uri_path}?mode=ro"
        try:
            conn = sqlite3.connect(uri, uri=True, timeout=5.0)
        except sqlite3.OperationalError:
            # Fallback to standard connect with query_only pragma
            conn = sqlite3.connect(str(abs_path), timeout=5.0)
            conn.execute("PRAGMA query_only = ON;")

        conn.row_factory = sqlite3.Row
        return conn

    def get_dashboard_snapshot(
        self,
        run_id: Optional[str] = None,
        max_parallel_default: int = 3,
    ) -> DashboardSnapshot:
        """Builds a complete DashboardSnapshot for the active or specified run."""
        if not self.db_path.exists():
            return DashboardSnapshot(
                run_id=run_id or "NO_DATABASE",
                project="--",
                package_id="--",
                status="NOT_INITIALIZED",
                stage="--",
                elapsed_str="--",
                agents=[],
                active_workers_count=0,
                max_parallel=max_parallel_default,
                leases=[],
                alerts=["Database file does not exist yet."],
                conflicts=[],
            )

        conn = self._open_read_only_connection()
        try:
            cursor = conn.cursor()

            # 1. Resolve Target Run
            if run_id:
                cursor.execute(
                    "SELECT run_id, job_id, package_id, project, status, started_at, completed_at FROM runs WHERE run_id = ?",
                    (run_id,),
                )
                run_row = cursor.fetchone()
            else:
                # Find most recent or running run
                cursor.execute(
                    "SELECT run_id, job_id, package_id, project, status, started_at, completed_at FROM runs ORDER BY started_at DESC LIMIT 1"
                )
                run_row = cursor.fetchone()

            if not run_row:
                return DashboardSnapshot(
                    run_id="NO_ACTIVE_RUN",
                    project="--",
                    package_id="--",
                    status="IDLE",
                    stage="--",
                    elapsed_str="--",
                    agents=[],
                    active_workers_count=0,
                    max_parallel=max_parallel_default,
                    leases=self._get_leases(cursor),
                    alerts=[],
                    conflicts=[],
                )

            active_run_id = run_row["run_id"]
            project = run_row["project"]
            package_id = run_row["package_id"]
            status = run_row["status"]
            started_at = run_row["started_at"]
            completed_at = run_row["completed_at"]

            # Calculate elapsed time
            elapsed_sec = self._calc_duration(started_at, completed_at)
            elapsed_str = format_duration(elapsed_sec)

            # 2. Stage Determination
            stage_str = self._get_stage_name(cursor, active_run_id)

            # 3. Agent Fleet
            agents = self._get_agent_fleet(cursor, active_run_id)
            active_workers = sum(1 for a in agents if a.status in {"RUNNING", "LAUNCHING", "TIMEOUT_RUNNING"})

            # 4. Leases
            leases = self._get_leases(cursor)

            # 5. Alerts & Conflicts
            alerts = self._get_alerts(cursor, active_run_id, agents)
            conflicts = self._get_conflicts(cursor, active_run_id)

            # 6. Recent Events & Errors
            recent_events = self._get_recent_events(cursor, active_run_id, limit=5)
            recent_errors = self._get_recent_errors(cursor, active_run_id, limit=5)

            return DashboardSnapshot(
                run_id=active_run_id,
                project=project,
                package_id=package_id,
                status=status,
                stage=stage_str,
                elapsed_str=elapsed_str,
                agents=agents,
                active_workers_count=active_workers,
                max_parallel=max_parallel_default,
                leases=leases,
                alerts=alerts,
                conflicts=conflicts,
                recent_events=recent_events,
                recent_errors=recent_errors,
            )
        finally:
            conn.close()

    def _get_stage_name(self, cursor: sqlite3.Cursor, run_id: str) -> str:
        try:
            cursor.execute(
                "SELECT stage_name, phase_number FROM dag_stages WHERE run_id = ? AND status = 'RUNNING' ORDER BY phase_number DESC LIMIT 1",
                (run_id,),
            )
            row = cursor.fetchone()
            if row:
                return f"{row['stage_name']} (Phase {row['phase_number']})"
            # Check graph_nodes if dag_stages not used
            cursor.execute(
                "SELECT stage_name, phase_number FROM graph_nodes WHERE run_id = ? AND status = 'RUNNING' ORDER BY phase_number DESC LIMIT 1",
                (run_id,),
            )
            row2 = cursor.fetchone()
            if row2:
                return f"{row2['stage_name']} (Phase {row2['phase_number']})"
        except sqlite3.OperationalError:
            pass
        return "UNKNOWN_STAGE"

    def _get_agent_fleet(self, cursor: sqlite3.Cursor, run_id: str) -> List[FleetAgentView]:
        fleet: List[FleetAgentView] = []
        try:
            cursor.execute(
                """
                SELECT agent_id, status, result_verdict, pid, exit_code, report_path, started_at, finished_at, updated_at
                FROM agents WHERE run_id = ? ORDER BY agent_id ASC
                """,
                (run_id,),
            )
            rows = cursor.fetchall()
            for r in rows:
                # Check report physical existence on disk if path recorded
                report_p = Path(r["report_path"]) if r["report_path"] else None
                report_exists = report_p.is_file() and report_p.stat().st_size > 0 if report_p else False

                duration_sec = self._calc_duration(r["started_at"], r["finished_at"])
                fleet.append(
                    FleetAgentView(
                        agent_id=r["agent_id"],
                        status=r["status"],
                        pid=r["pid"],
                        exit_code=r["exit_code"],
                        report_present=report_exists,
                        verdict=r["result_verdict"],
                        duration_str=format_duration(duration_sec),
                        updated_at=r["updated_at"],
                    )
                )
        except sqlite3.OperationalError:
            pass
        return fleet

    def _get_leases(self, cursor: sqlite3.Cursor) -> List[LeaseView]:
        leases: List[LeaseView] = []
        try:
            cursor.execute(
                "SELECT lease_name, holder_id, holder_pid, acquired_at, heartbeat_at, expires_at, metadata_json FROM leases"
            )
            rows = cursor.fetchall()
            now_dt = datetime.now(timezone.utc)
            for r in rows:
                try:
                    exp_dt = datetime.fromisoformat(r["expires_at"].replace("Z", "+00:00"))
                    if exp_dt.tzinfo is None:
                        exp_dt = exp_dt.replace(tzinfo=timezone.utc)
                    rem = (exp_dt - now_dt).total_seconds()
                    expired = rem <= 0
                except Exception:
                    expired = True
                    rem = 0.0

                try:
                    meta = json.loads(r["metadata_json"] or "{}")
                except Exception:
                    meta = {}

                leases.append(
                    LeaseView(
                        lease_name=r["lease_name"],
                        holder_id=r["holder_id"],
                        holder_pid=r["holder_pid"],
                        acquired_at=r["acquired_at"],
                        heartbeat_at=r["heartbeat_at"],
                        expires_at=r["expires_at"],
                        is_expired=expired,
                        ttl_remaining_seconds=max(0.0, rem),
                        metadata=meta,
                    )
                )
        except sqlite3.OperationalError:
            pass
        return leases

    def _get_alerts(
        self,
        cursor: sqlite3.Cursor,
        run_id: str,
        agents: List[FleetAgentView],
    ) -> List[str]:
        alerts: List[str] = []
        # Agent-level alerts
        for a in agents:
            if a.status == "TIMEOUT_RUNNING":
                alerts.append(f"[WARN] {a.agent_id} exceeded timeout -> Transitioned to TIMEOUT_RUNNING (Alive)")

        # Events-level recent warnings/errors
        try:
            cursor.execute(
                """
                SELECT event_type, severity, payload_json FROM events
                WHERE run_id = ? AND severity IN ('WARN', 'ERROR', 'FATAL')
                ORDER BY event_id DESC LIMIT 3
                """,
                (run_id,),
            )
            rows = cursor.fetchall()
            for r in rows:
                alerts.append(f"[{r['severity']}] {r['event_type']}")
        except sqlite3.OperationalError:
            pass

        return alerts

    def _get_conflicts(self, cursor: sqlite3.Cursor, run_id: str) -> List[str]:
        conflicts: List[str] = []
        try:
            cursor.execute(
                "SELECT file_path, agents_involved FROM file_conflicts WHERE run_id = ? AND resolution = 'UNRESOLVED'",
                (run_id,),
            )
            rows = cursor.fetchall()
            for r in rows:
                conflicts.append(f"Overlap detected: {r['file_path']} across {r['agents_involved']}")
        except sqlite3.OperationalError:
            pass
        return conflicts

    def _get_recent_events(self, cursor: sqlite3.Cursor, run_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        evs: List[Dict[str, Any]] = []
        try:
            cursor.execute(
                """
                SELECT event_id, event_type, severity, agent_id, created_at
                FROM events WHERE run_id = ? ORDER BY event_id DESC LIMIT ?
                """,
                (run_id, limit),
            )
            for r in cursor.fetchall():
                evs.append(
                    {
                        "event_id": r["event_id"],
                        "event_type": r["event_type"],
                        "severity": r["severity"],
                        "agent_id": r["agent_id"],
                        "created_at": r["created_at"],
                    }
                )
        except sqlite3.OperationalError:
            pass
        return evs

    def _get_recent_errors(self, cursor: sqlite3.Cursor, run_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        errs: List[Dict[str, Any]] = []
        try:
            cursor.execute(
                """
                SELECT error_id, error_code, category, severity, message, occurred_at
                FROM errors WHERE run_id = ? ORDER BY error_id DESC LIMIT ?
                """,
                (run_id, limit),
            )
            for r in cursor.fetchall():
                errs.append(
                    {
                        "error_id": r["error_id"],
                        "error_code": r["error_code"],
                        "category": r["category"],
                        "severity": r["severity"],
                        "message": r["message"],
                        "occurred_at": r["occurred_at"],
                    }
                )
        except sqlite3.OperationalError:
            pass
        return errs

    @staticmethod
    def _calc_duration(started_at: Optional[str], completed_at: Optional[str]) -> Optional[float]:
        if not started_at:
            return None
        try:
            s_dt = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
            if s_dt.tzinfo is None:
                s_dt = s_dt.replace(tzinfo=timezone.utc)
            if completed_at:
                c_dt = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
                if c_dt.tzinfo is None:
                    c_dt = c_dt.replace(tzinfo=timezone.utc)
            else:
                c_dt = datetime.now(timezone.utc)
            return max(0.0, (c_dt - s_dt).total_seconds())
        except Exception:
            return None


def render_ascii_dashboard(snapshot: DashboardSnapshot) -> str:
    """Renders the canonical ASCII terminal layout matching MONITOR.ps1."""
    width = 100
    sep = "=" * width
    thin_sep = "-" * width

    lines: List[str] = [
        sep,
        "                        SOLIDBIT AGENT EXECUTION CONTROL LOOP (SACL V1)",
        sep,
        f" Run ID:      {snapshot.run_id:<32} Project:     {snapshot.project}",
        f" Package:     {snapshot.package_id:<32} Elapsed:     {snapshot.elapsed_str}",
        f" Status:      {snapshot.status:<32} Stage:       {snapshot.stage}",
        thin_sep,
        " AGENT EXECUTION FLEET",
        thin_sep,
        f" {'Agent ID':<11} | {'Status':<16} | {'PID':<6} | {'Exit':<4} | {'Report':<6} | {'Verdict':<22} | {'Duration':<9}",
        f" {'-'*11}-+-{'-'*16}-+-{'-'*6}-+-{'-'*4}-+-{'-'*6}-+-{'-'*22}-+-{'-'*9}",
    ]

    if not snapshot.agents:
        lines.append(" (No agents currently recorded)")
    else:
        for a in snapshot.agents:
            pid_str = str(a.pid) if a.pid is not None else "--"
            exit_str = str(a.exit_code) if a.exit_code is not None else "--"
            rep_str = "[YES]" if a.report_present else "[NO]"
            lines.append(
                f" {a.agent_id:<11} | {a.status:<16} | {pid_str:<6} | {exit_str:<4} | {rep_str:<6} | {a.verdict:<22} | {a.duration_str:<9}"
            )

    lines.extend([
        thin_sep,
        " CONCURRENCY & LEASES",
        thin_sep,
    ])

    limit_note = " (MaxParallel Limit Reached)" if snapshot.active_workers_count >= snapshot.max_parallel else ""
    lines.append(f" Active Workers: {snapshot.active_workers_count} / {snapshot.max_parallel}{limit_note}")

    if snapshot.leases:
        lease_strs = [f"{l.lease_name} (PID {l.holder_pid})" for l in snapshot.leases if not l.is_expired]
        lines.append(f" Leases:         {', '.join(lease_strs) if lease_strs else 'None active'}")
    else:
        lines.append(" Leases:         None recorded")

    if snapshot.alerts:
        for alert in snapshot.alerts:
            lines.append(f" Alerts:         {alert}")
    else:
        lines.append(" Alerts:         None")

    if snapshot.conflicts:
        for conf in snapshot.conflicts:
            lines.append(f" Conflicts:      {conf}")
    else:
        lines.append(" Conflicts:      None detected.")

    lines.extend([
        sep,
        " [Press Ctrl+C to exit monitor. Running agents and supervisors will NOT be terminated.]",
    ])

    return "\n".join(lines)

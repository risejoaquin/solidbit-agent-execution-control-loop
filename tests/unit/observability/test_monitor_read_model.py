"""Unit tests for SACL V1 live monitor read models and ASCII dashboard rendering."""

import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path
import pytest

from sacl.observability.monitor import (
    DashboardSnapshot,
    FleetAgentView,
    LeaseView,
    MonitorReadModel,
    format_duration,
    render_ascii_dashboard,
)


def _seed_live_dashboard_data(conn: sqlite3.Connection, tmp_path: Path) -> None:
    """Populates the database with realistic run, agent, lease, and alert rows."""
    cursor = conn.cursor()

    # 1. Job and Run
    cursor.execute(
        """
        INSERT INTO jobs (job_id, status, created_at, updated_at)
        VALUES ('job-dash-01', 'RUNNING', '2026-10-07T00:30:00Z', '2026-10-07T00:30:00Z')
        """
    )
    cursor.execute(
        """
        INSERT INTO runs (
            run_id, job_id, package_id, project, repository, mode,
            source_orchestrator, target_repo_path, run_dir, status, started_at
        )
        VALUES (
            'w0-20261007-003429-e4fa9b', 'job-dash-01', 'SACL-W0-ARCHITECTURE-FREEZE',
            'solidbit-agent-execution-control-loop', 'solidbit-control-loop', 'materialization',
            'C:/orchestrator', 'C:/repo', 'runs/w0-20261007', 'RUNNING', '2026-10-07T00:34:29Z'
        )
        """
    )

    # 2. DAG Stage
    cursor.execute(
        """
        INSERT INTO dag_stages (run_id, phase_number, stage_name, status, started_at)
        VALUES ('w0-20261007-003429-e4fa9b', 2, 'PHASE_2_DESIGN', 'RUNNING', '2026-10-07T00:34:30Z')
        """
    )

    # 3. Create dummy deliverable report for AG-COMPAT
    compat_report = tmp_path / "AG-COMPAT.REPORT.md"
    compat_report.write_text("# Deliverable\nRESULT = PASS\n", encoding="utf-8")

    # 4. Agents Fleet
    cursor.execute(
        """
        INSERT INTO agents (
            agent_id, run_id, status, result_verdict, pid, prompt_path,
            report_path, stdout_path, stderr_path, started_at, finished_at, updated_at, exit_code
        )
        VALUES (
            'AG-COMPAT', 'w0-20261007-003429-e4fa9b', 'COMPLETE', 'PASS', 4812,
            'prompt.txt', ?, 'stdout.log', 'stderr.log',
            '2026-10-07T00:34:30Z', '2026-10-07T00:37:45Z', '2026-10-07T00:37:45Z', 0
        )
        """,
        (str(compat_report),),
    )
    cursor.execute(
        """
        INSERT INTO agents (
            agent_id, run_id, status, result_verdict, pid, prompt_path,
            report_path, stdout_path, stderr_path, started_at, updated_at
        )
        VALUES (
            'AG-ARCH', 'w0-20261007-003429-e4fa9b', 'RUNNING', 'IN_PROGRESS', 9240,
            'prompt.txt', 'non_existent_report.md', 'stdout.log', 'stderr.log',
            '2026-10-07T00:34:30Z', '2026-10-07T00:38:00Z'
        )
        """
    )
    cursor.execute(
        """
        INSERT INTO agents (
            agent_id, run_id, status, result_verdict, pid, prompt_path,
            report_path, stdout_path, stderr_path, started_at, updated_at
        )
        VALUES (
            'AG-SCHEMA', 'w0-20261007-003429-e4fa9b', 'TIMEOUT_RUNNING', 'IN_PROGRESS', 9504,
            'prompt.txt', 'non_existent_report.md', 'stdout.log', 'stderr.log',
            '2026-10-07T00:34:30Z', '2026-10-07T00:44:00Z'
        )
        """
    )

    # 5. Leases
    future_iso = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    cursor.execute(
        """
        INSERT INTO leases (lease_name, holder_id, holder_pid, acquired_at, heartbeat_at, expires_at)
        VALUES ('SYSTEM', 'SUPERVISOR', 2108, '2026-10-07T00:34:29Z', '2026-10-07T00:48:00Z', ?)
        """,
        (future_iso,),
    )
    cursor.execute(
        """
        INSERT INTO leases (lease_name, holder_id, holder_pid, acquired_at, heartbeat_at, expires_at)
        VALUES ('PROJECT_solidbit', 'w0-20261007-003429-e4fa9b', 2108, '2026-10-07T00:34:29Z', '2026-10-07T00:48:00Z', ?)
        """,
        (future_iso,),
    )

    conn.commit()


def test_format_duration():
    """Verifies duration formatting helper."""
    assert format_duration(None) == "--"
    assert format_duration(-5) == "--"
    assert format_duration(0) == "00:00:00"
    assert format_duration(195) == "00:03:15"
    assert format_duration(862) == "00:14:22"
    assert format_duration(3665) == "01:01:05"


def test_monitor_read_model_read_only(sqlite_temp_db: sqlite3.Connection, tmp_path: Path):
    """Verifies MonitorReadModel queries database with mode=ro without locking."""
    _seed_live_dashboard_data(sqlite_temp_db, tmp_path)

    # Find the database path on disk
    cursor = sqlite_temp_db.cursor()
    cursor.execute("PRAGMA database_list;")
    db_file = cursor.fetchall()[0]["file"]

    reader = MonitorReadModel(db_file)
    snapshot = reader.get_dashboard_snapshot()

    assert snapshot.run_id == "w0-20261007-003429-e4fa9b"
    assert snapshot.project == "solidbit-agent-execution-control-loop"
    assert snapshot.package_id == "SACL-W0-ARCHITECTURE-FREEZE"
    assert snapshot.status == "RUNNING"
    assert "PHASE_2_DESIGN" in snapshot.stage
    assert len(snapshot.agents) == 3

    # Check agent properties
    compat = next(a for a in snapshot.agents if a.agent_id == "AG-COMPAT")
    assert compat.status == "COMPLETE"
    assert compat.pid == 4812
    assert compat.exit_code == 0
    assert compat.report_present is True
    assert compat.verdict == "PASS"

    arch = next(a for a in snapshot.agents if a.agent_id == "AG-ARCH")
    assert arch.status == "RUNNING"
    assert arch.pid == 9240
    assert arch.exit_code is None
    assert arch.report_present is False
    assert arch.verdict == "IN_PROGRESS"

    schema = next(a for a in snapshot.agents if a.agent_id == "AG-SCHEMA")
    assert schema.status == "TIMEOUT_RUNNING"

    # Concurrency and leases
    assert snapshot.active_workers_count == 2  # AG-ARCH, AG-SCHEMA
    assert len(snapshot.leases) == 2
    assert any("SYSTEM" in l.lease_name for l in snapshot.leases)

    # Alert generation
    assert any("TIMEOUT_RUNNING" in alert for alert in snapshot.alerts)


def test_render_ascii_dashboard():
    """Verifies rendering the canonical ASCII terminal dashboard layout."""
    snapshot = DashboardSnapshot(
        run_id="w0-20261007-003429-e4fa9b",
        project="solidbit-agent-execution-control-loop",
        package_id="SACL-W0-ARCHITECTURE-FREEZE",
        status="RUNNING",
        stage="PHASE_2_DESIGN (Phase 2/4)",
        elapsed_str="00:14:22",
        agents=[
            FleetAgentView(
                agent_id="AG-COMPAT",
                status="COMPLETED",
                pid=4812,
                exit_code=0,
                report_present=True,
                verdict="PASS",
                duration_str="00:03:15",
            ),
            FleetAgentView(
                agent_id="AG-ARCH",
                status="RUNNING",
                pid=9240,
                exit_code=None,
                report_present=False,
                verdict="IN_PROGRESS",
                duration_str="00:08:42",
            ),
            FleetAgentView(
                agent_id="AG-SCHEMA",
                status="TIMEOUT_RUNNING",
                pid=9504,
                exit_code=None,
                report_present=False,
                verdict="IN_PROGRESS",
                duration_str="00:12:10",
            ),
        ],
        active_workers_count=3,
        max_parallel=3,
        leases=[
            LeaseView(
                lease_name="SYSTEM",
                holder_id="SUPERVISOR",
                holder_pid=2108,
                acquired_at="",
                heartbeat_at="",
                expires_at="",
                is_expired=False,
                ttl_remaining_seconds=45.0,
            ),
            LeaseView(
                lease_name="PROJECT_solidbit",
                holder_id="RUNNER",
                holder_pid=2108,
                acquired_at="",
                heartbeat_at="",
                expires_at="",
                is_expired=False,
                ttl_remaining_seconds=45.0,
            ),
        ],
        alerts=["[WARN] AG-SCHEMA exceeded 10m timeout -> Transitioned to TIMEOUT_RUNNING (Alive)"],
        conflicts=[],
    )

    rendered = render_ascii_dashboard(snapshot)

    assert "SOLIDBIT AGENT EXECUTION CONTROL LOOP (SACL V1)" in rendered
    assert "Run ID:      w0-20261007-003429-e4fa9b" in rendered
    assert "Elapsed:     00:14:22" in rendered
    assert "AGENT EXECUTION FLEET" in rendered
    assert "AG-COMPAT" in rendered
    assert "[YES]" in rendered
    assert "PASS" in rendered
    assert "AG-ARCH" in rendered
    assert "[NO]" in rendered
    assert "AG-SCHEMA" in rendered
    assert "TIMEOUT_RUNNING" in rendered
    assert "Active Workers: 3 / 3 (MaxParallel Limit Reached)" in rendered
    assert "Leases:         SYSTEM (PID 2108), PROJECT_solidbit (PID 2108)" in rendered
    assert "[WARN] AG-SCHEMA exceeded 10m timeout" in rendered
    assert "Ctrl+C to exit monitor" in rendered


def test_monitor_read_model_missing_db(tmp_path: Path):
    """Verifies MonitorReadModel handles missing or uninitialized database gracefully."""
    missing_path = tmp_path / "does_not_exist.db"
    reader = MonitorReadModel(missing_path)

    snapshot = reader.get_dashboard_snapshot()
    assert snapshot.status == "NOT_INITIALIZED"
    assert snapshot.run_id == "NO_DATABASE"
    assert len(snapshot.alerts) == 1
    assert "does not exist" in snapshot.alerts[0]


def test_monitor_read_model_conflicts_and_done_review(sqlite_temp_db: sqlite3.Connection):
    """Verifies conflict detection and DONE_REVIEW_REQUIRED verdict in dashboard."""
    cursor = sqlite_temp_db.cursor()

    cursor.execute(
        """
        INSERT INTO jobs (job_id, status, created_at, updated_at)
        VALUES ('job-conf', 'RUNNING', '2026-10-07T00:30:00Z', '2026-10-07T00:30:00Z')
        """
    )
    cursor.execute(
        """
        INSERT INTO runs (
            run_id, job_id, package_id, project, repository, mode,
            source_orchestrator, target_repo_path, run_dir, status, started_at
        )
        VALUES (
            'run-conflict-01', 'job-conf', 'PKG-CONF', 'proj-1', 'repo-1', 'mode-1',
            'src', 'target', 'runs/conf', 'RUNNING', '2026-10-07T00:30:00Z'
        )
        """
    )

    # Insert agent with DONE_REVIEW_REQUIRED
    cursor.execute(
        """
        INSERT INTO agents (
            agent_id, run_id, status, result_verdict, prompt_path,
            report_path, stdout_path, stderr_path, started_at, updated_at
        )
        VALUES (
            'AG-GATE', 'run-conflict-01', 'COMPLETE', 'DONE_REVIEW_REQUIRED',
            'p.txt', 'r.md', 'out.log', 'err.log', '2026-10-07T00:30:00Z', '2026-10-07T00:30:00Z'
        )
        """
    )

    # Insert conflict
    cursor.execute(
        """
        INSERT INTO file_conflicts (run_id, file_path, agents_involved, detected_at, resolution)
        VALUES ('run-conflict-01', 'src/shared.py', '["AG-ARCH", "AG-SEC"]', '2026-10-07T00:31:00Z', 'UNRESOLVED')
        """
    )
    sqlite_temp_db.commit()

    cursor.execute("PRAGMA database_list;")
    db_file = cursor.fetchall()[0]["file"]

    reader = MonitorReadModel(db_file)
    snapshot = reader.get_dashboard_snapshot("run-conflict-01")

    assert snapshot.run_id == "run-conflict-01"
    assert len(snapshot.conflicts) == 1
    assert "src/shared.py" in snapshot.conflicts[0]

    ag = snapshot.agents[0]
    assert ag.agent_id == "AG-GATE"
    assert ag.verdict == "DONE_REVIEW_REQUIRED"


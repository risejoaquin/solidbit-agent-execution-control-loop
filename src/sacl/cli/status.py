"""SACL V1 CLI Status Subcommand.

Queries and inspects agent and run execution states from SQLite sacl_ops.db
and legacy state JSON files, supporting tabular and JSON output.
"""

from __future__ import annotations

import argparse
import json
import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from sacl.legacy.state_bridge import LegacyStateBridge

logger = logging.getLogger("sacl.cli.status")


def configure_status_parser(parser: argparse.ArgumentParser) -> None:
    """Configures CLI arguments for the status command."""
    parser.add_argument(
        "--run-id",
        help="Target run ID to inspect (defaults to latest active/recent run)",
    )
    parser.add_argument(
        "--agent",
        default="all",
        help="Filter status to a specific agent identifier, or 'all' (default: all)",
    )
    parser.add_argument(
        "--db",
        help="Path to SQLite operational database (sacl_ops.db)",
    )
    parser.add_argument(
        "--run-dir",
        help="Path to run output directory containing state/ and reports/",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw structured JSON array matching status.ps1 -Json",
    )


def execute_status(args: argparse.Namespace) -> int:
    """Executes the status command."""
    status_rows: List[Dict[str, Any]] = []

    # Priority 1: Query SQLite database if specified or default exists
    db_path = None
    if args.db:
        db_path = Path(args.db).resolve()
    elif Path("sacl_ops.db").exists():
        db_path = Path("sacl_ops.db").resolve()
    elif Path("data/sacl_ops.db").exists():
        db_path = Path("data/sacl_ops.db").resolve()

    if db_path and db_path.exists():
        status_rows = _query_sqlite_status(db_path, args.run_id, args.agent)

    # Priority 2: Query run-dir filesystem if SQLite yielded no rows or not provided
    if not status_rows and args.run_dir:
        rd = Path(args.run_dir).resolve()
        status_rows = _query_filesystem_status(rd, args.agent)

    # Priority 3: Fallback scan in current directory
    if not status_rows:
        if Path("state").exists():
            status_rows = _query_filesystem_status(Path("."), args.agent)
        elif Path("runs").exists():
            latest_runs = sorted(
                Path("runs").glob("w0-*"), key=lambda p: p.stat().st_mtime, reverse=True
            )
            if latest_runs:
                status_rows = _query_filesystem_status(latest_runs[0], args.agent)

    if not status_rows:
        if args.json:
            print("[]")
        else:
            print("[INFO] No active or recorded agent state found.")
        return 0

    if args.json:
        print(json.dumps(status_rows, indent=2))
        return 0

    # Render formatted ASCII table matching status.ps1
    print("\n" + "=" * 105)
    print("                              SACL AGENT EXECUTION STATUS")
    print("=" * 105)
    print(
        f" {'AGENT':<12} | {'STATUS':<16} | {'PID':<8} | {'EXIT':<6} | {'REPORT':<8} | {'VERDICT':<24} | {'UPDATED':<19}"
    )
    print(f" {'-' * 12}-+-{'-' * 16}-+-{'-' * 8}-+-{'-' * 6}-+-{'-' * 8}-+-{'-' * 24}-+-{'-' * 19}")

    running = complete = failed = stopped = timeout = 0
    for r in status_rows:
        agent_id = r.get("AGENT", "--")
        st = r.get("STATUS", "UNKNOWN")
        pid_s = str(r.get("PID")) if r.get("PID") is not None else "--"
        ec_s = str(r.get("EXIT")) if r.get("EXIT") is not None else "--"
        rep_s = "[YES]" if r.get("REPORT") else "[NO]"
        verdict = r.get("RESULT", "--")
        last_act = r.get("LAST_ACTIVITY") or "--"
        updated = last_act[:19]

        if st == "RUNNING":
            running += 1
        elif st in {"COMPLETE", "SUCCEEDED"}:
            complete += 1
        elif st == "FAILED":
            failed += 1
        elif st == "STOPPED":
            stopped += 1
        elif "TIMEOUT" in st:
            timeout += 1

        print(
            f" {agent_id:<12} | {st:<16} | {pid_s:<8} | {ec_s:<6} | {rep_s:<8} | {verdict:<24} | {updated:<19}"
        )

    print("-" * 105)
    print(
        f"Summary: RUNNING={running} | COMPLETE={complete} | FAILED={failed} | STOPPED={stopped} | TIMEOUT={timeout}"
    )
    print("=" * 105 + "\n")
    return 0


def _query_sqlite_status(
    db_path: Path, run_id: Optional[str], agent_filter: str
) -> List[Dict[str, Any]]:
    """Queries SQLite for agent status rows."""
    rows: List[Dict[str, Any]] = []
    try:
        conn = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
        cursor = conn.cursor()

        target_run = run_id
        if not target_run:
            cursor.execute("SELECT run_id FROM runs ORDER BY started_at DESC LIMIT 1")
            r = cursor.fetchone()
            if r:
                target_run = r[0]

        if not target_run:
            conn.close()
            return []

        if agent_filter.lower() == "all":
            cursor.execute(
                """
                SELECT agent_id, status, pid, exit_code, report_path, result_verdict, updated_at
                FROM agents WHERE run_id = ? ORDER BY agent_id ASC
                """,
                (target_run,),
            )
        else:
            cursor.execute(
                """
                SELECT agent_id, status, pid, exit_code, report_path, result_verdict, updated_at
                FROM agents WHERE run_id = ? AND LOWER(agent_id) = LOWER(?)
                """,
                (target_run, agent_filter),
            )

        for a_id, st, pid, ec, rp, verd, upd in cursor.fetchall():
            rows.append(
                {
                    "AGENT": a_id,
                    "STATUS": st,
                    "PID": pid,
                    "EXIT": ec,
                    "REPORT": bool(rp and Path(rp).exists()),
                    "RESULT": verd or "--",
                    "LAST_ACTIVITY": upd or "--",
                }
            )
        conn.close()
    except Exception as exc:
        logger.debug("SQLite status query failed: %s", exc)
    return rows


def _query_filesystem_status(run_dir: Path, agent_filter: str) -> List[Dict[str, Any]]:
    """Queries filesystem state directory for agent status rows."""
    bridge = LegacyStateBridge()
    state_dir = run_dir / "state" if (run_dir / "state").exists() else run_dir
    reports_dir = run_dir / "reports" if (run_dir / "reports").exists() else None
    logs_dir = run_dir / "logs" if (run_dir / "logs").exists() else None

    rows: List[Dict[str, Any]] = []
    if not state_dir.exists():
        return rows

    state_files = sorted(state_dir.glob("*.json"))
    for sf in state_files:
        agent_id = sf.stem
        if agent_filter.lower() != "all" and agent_id.lower() != agent_filter.lower():
            continue

        recon = bridge.reconcile_legacy_agent(
            agent_id=agent_id,
            run_dir=run_dir,
            state_dir=state_dir,
            reports_dir=reports_dir,
            logs_dir=logs_dir,
        )

        rows.append(
            {
                "AGENT": recon["Agent"],
                "STATUS": recon["Status"],
                "PID": recon["Pid"],
                "EXIT": recon["ExitCode"],
                "REPORT": recon["ReportExists"],
                "RESULT": recon["Verdict"],
                "LAST_ACTIVITY": recon.get("StartedAt", "--"),
            }
        )
    return rows

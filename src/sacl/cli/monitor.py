"""SACL V1 CLI Monitor Subcommand.

Renders real-time live console ASCII dashboard matching MONITOR.ps1
in read-only mode without holding write locks on sacl_ops.db.
"""

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path
import sys
import time

from sacl.observability.monitor import MonitorReadModel, render_ascii_dashboard

logger = logging.getLogger("sacl.cli.monitor")


def configure_monitor_parser(parser: argparse.ArgumentParser) -> None:
    """Configures CLI arguments for the monitor command."""
    parser.add_argument(
        "--run-id",
        help="Target run ID to monitor",
    )
    parser.add_argument(
        "--refresh",
        "--interval",
        type=int,
        default=10,
        dest="refresh",
        help="Refresh interval in seconds (default: 10)",
    )
    parser.add_argument(
        "--db",
        help="Path to SQLite operational database (sacl_ops.db)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Render dashboard snapshot once and exit",
    )


def execute_monitor(args: argparse.Namespace) -> int:
    """Executes the live monitor dashboard."""
    # Resolve DB path
    db_path = None
    if args.db:
        db_path = Path(args.db).resolve()
    elif Path("sacl_ops.db").exists():
        db_path = Path("sacl_ops.db").resolve()
    elif Path("data/sacl_ops.db").exists():
        db_path = Path("data/sacl_ops.db").resolve()
    else:
        db_path = Path("sacl_ops.db")

    read_model = MonitorReadModel(db_path=db_path)
    refresh_sec = max(1, args.refresh)

    if args.once:
        snapshot = read_model.get_dashboard_snapshot(run_id=args.run_id)
        for a in snapshot.agents:
            if a.verdict is None:
                a.verdict = "--"
        print(render_ascii_dashboard(snapshot))
        return 0

    print("[INFO] Starting live console monitor. Press Ctrl+C to exit without affecting workers.")
    try:
        while True:
            # Clear console
            os.system("cls" if os.name == "nt" else "clear")
            snapshot = read_model.get_dashboard_snapshot(run_id=args.run_id)
            for a in snapshot.agents:
                if a.verdict is None:
                    a.verdict = "--"
            print(render_ascii_dashboard(snapshot))

            if snapshot.status in {"COMPLETED", "FAILED", "BLOCKED", "ARCHIVED", "CANCELLED"}:
                print("\n[COMPLETE] Run execution reached terminal state.")
                break

            time.sleep(refresh_sec)
    except KeyboardInterrupt:
        print("\n\n[INFO] Monitor detached. Background agent workers continue unaffected.")
        return 0

    return 0

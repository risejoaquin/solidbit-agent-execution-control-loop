"""SACL V1 CLI Stop Subcommand.

Safely terminates orchestrated agent worker processes using stored PIDs
and the 3-Way PID Recycling Defense (safe_stop_agent_process), protecting
unrelated system processes from false-positive terminations.
"""

from __future__ import annotations

import argparse
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from sacl.legacy.state_bridge import LegacyStateBridge
from sacl.worker.process import IProcessInspector, OSProcessInspector, safe_stop_agent_process

logger = logging.getLogger("sacl.cli.stop")


def configure_stop_parser(parser: argparse.ArgumentParser) -> None:
    """Configures CLI arguments for the stop command."""
    parser.add_argument(
        "--agent",
        default="all",
        help="Target agent ID to terminate, or 'all' for all running agents (default: all)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Stop all active orchestrated agents across the system",
    )
    parser.add_argument(
        "--pid",
        type=int,
        help="Target a specific process ID to safely stop",
    )
    parser.add_argument(
        "--run-id",
        help="Target run ID to stop workers for",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Send immediate force termination signal",
    )
    parser.add_argument(
        "--db",
        help="Path to SQLite operational database (sacl_ops.db)",
    )
    parser.add_argument(
        "--run-dir",
        help="Path to run output directory containing state/",
    )


def execute_stop(
    args: argparse.Namespace,
    inspector: Optional[IProcessInspector] = None,
) -> int:
    """Executes the safe stop command."""
    ins = inspector or OSProcessInspector()
    bridge = LegacyStateBridge(process_inspector=ins)

    # 1. Discover target processes to stop
    targets: List[Dict[str, Any]] = []

    effective_agent = "all" if getattr(args, "all", False) else args.agent

    if getattr(args, "pid", None):
        targets.append(
            {
                "agent_id": f"pid-{args.pid}",
                "pid": args.pid,
                "started_at": None,
                "state_file": None,
            }
        )

    # Check SQLite
    db_path = None
    if args.db:
        db_path = Path(args.db).resolve()
    elif Path("sacl_ops.db").exists():
        db_path = Path("sacl_ops.db").resolve()
    elif Path("data/sacl_ops.db").exists():
        db_path = Path("data/sacl_ops.db").resolve()

    if db_path and db_path.exists():
        targets.extend(_find_targets_from_db(db_path, args.run_id, effective_agent))

    # Check filesystem
    if args.run_dir:
        targets.extend(_find_targets_from_fs(Path(args.run_dir), effective_agent))
    elif Path("state").exists():
        targets.extend(_find_targets_from_fs(Path("."), effective_agent))

    # Deduplicate by (agent_id, pid)
    unique_targets = {}
    for t in targets:
        key = (t["agent_id"], t["pid"])
        unique_targets[key] = t

    if not unique_targets:
        print(f"[INFO] No active agents found matching criteria (agent={args.agent}).")
        return 0

    print("\n" + "=" * 70)
    print("                    SACL SAFE STOP CONTROLLER")
    print("=" * 70)

    stopped_count = 0
    refusal_count = 0

    for (a_id, pid), info in unique_targets.items():
        started_at = info.get("started_at")
        state_file = info.get("state_file")

        print(f"--- Checking Agent: {a_id} (PID {pid}) ---")

        success, outcome_code, details = safe_stop_agent_process(
            pid=pid,
            expected_start_time=started_at,
            force=args.force,
            inspector=ins,
        )

        if outcome_code == "STOPPED_BY_USER":
            print(f"[SUCCESS] Agent {a_id} (PID {pid}) successfully terminated.")
            stopped_count += 1
            # Update state file
            if state_file and Path(state_file).exists():
                bridge.write_agent_state(
                    state_file=state_file,
                    agent_name=a_id,
                    status="STOPPED",
                    pid=pid,
                    started_at=started_at,
                    error_text="STOPPED_BY_USER",
                )
            # Update SQLite
            if db_path and db_path.exists():
                _update_sqlite_agent_stopped(db_path, a_id, pid)

        elif outcome_code == "ALREADY_DEAD":
            print(f"[INFO] Process PID {pid} for agent {a_id} is already stopped.")
            if state_file and Path(state_file).exists():
                bridge.write_agent_state(
                    state_file=state_file,
                    agent_name=a_id,
                    status="STOPPED",
                    pid=pid,
                    started_at=started_at,
                )

        elif outcome_code.startswith("SAFETY_REFUSAL"):
            refusal_count += 1
            print(f"[SAFETY REFUSAL] Cannot kill PID {pid} for {a_id}: {outcome_code}")
            print(
                f"                 Reason: {details.get('reason')} - process spared to protect host."
            )

    print("-" * 70)
    print(f"Summary: Stopped={stopped_count} | Refused={refusal_count}")
    print("=" * 70 + "\n")
    return 0 if refusal_count == 0 else 1


def _find_targets_from_db(
    db_path: Path, run_id: Optional[str], agent_filter: str
) -> List[Dict[str, Any]]:
    targets = []
    try:
        conn = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
        cursor = conn.cursor()
        query = "SELECT agent_id, pid, started_at, run_id FROM agents WHERE pid IS NOT NULL AND status IN ('RUNNING', 'TIMEOUT_RUNNING')"
        params = []
        if run_id:
            query += " AND run_id = ?"
            params.append(run_id)
        if agent_filter.lower() != "all":
            query += " AND LOWER(agent_id) = LOWER(?)"
            params.append(agent_filter)

        cursor.execute(query, tuple(params))
        for a_id, pid, sa, r_id in cursor.fetchall():
            if pid and pid > 0:
                targets.append(
                    {
                        "agent_id": a_id,
                        "pid": pid,
                        "started_at": sa,
                        "run_id": r_id,
                        "state_file": None,
                    }
                )
        conn.close()
    except Exception as exc:
        logger.debug("Failed finding stop targets from DB: %s", exc)
    return targets


def _find_targets_from_fs(run_dir: Path, agent_filter: str) -> List[Dict[str, Any]]:
    targets = []
    bridge = LegacyStateBridge()
    state_dir = run_dir / "state" if (run_dir / "state").exists() else run_dir
    if not state_dir.exists():
        return targets

    for sf in state_dir.glob("*.json"):
        agent_id = sf.stem
        if agent_filter.lower() != "all" and agent_id.lower() != agent_filter.lower():
            continue
        st = bridge.read_agent_state(sf)
        if st and st.get("pid"):
            targets.append(
                {
                    "agent_id": st.get("agent", agent_id),
                    "pid": st.get("pid"),
                    "started_at": st.get("startedAt"),
                    "state_file": sf,
                }
            )
    return targets


def _update_sqlite_agent_stopped(db_path: Path, agent_id: str, pid: int) -> None:
    try:
        conn = sqlite3.connect(str(db_path), timeout=5.0)
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        conn.execute(
            """
            UPDATE agents
            SET status = 'STOPPED', result_verdict = 'STOPPED_BY_USER', finished_at = ?, updated_at = ?
            WHERE agent_id = ? AND pid = ?
            """,
            (now_iso, now_iso, agent_id, pid),
        )
        conn.commit()
        conn.close()
    except Exception as exc:
        logger.debug("Failed updating agent stopped in DB: %s", exc)

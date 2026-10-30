"""SACL V1 CLI Launch Subcommand.

Executes wave packages preserving the proven operator experience from RUN-WAVE.ps1.
"""

from __future__ import annotations

import argparse
import logging
import sqlite3
import sys
from pathlib import Path

from sacl.legacy.operator import LegacyOperatorExperience

logger = logging.getLogger("sacl.cli.launch")


def configure_launch_parser(parser: argparse.ArgumentParser) -> None:
    """Configures CLI arguments for the launch/run command."""
    parser.add_argument(
        "package",
        nargs="?",
        default=None,
        help="Path to wave package (.zip archive or unpacked folder)",
    )
    parser.add_argument(
        "--package",
        dest="package_opt",
        help="Explicit package path flag",
    )
    parser.add_argument(
        "--repo",
        help="Target local repository path",
    )
    parser.add_argument(
        "--source-orchestrator",
        help="Source orchestrator reference path",
    )
    parser.add_argument(
        "--max-parallel",
        type=int,
        default=4,
        help="Maximum parallel agent workers (default: 4)",
    )
    parser.add_argument(
        "--bypass-acknowledged",
        action="store_true",
        help="Explicitly acknowledge --dangerously-skip-permissions host access",
    )
    parser.add_argument(
        "--test-mode",
        "--mock",
        action="store_true",
        dest="test_mode",
        help="Execute in harmless test/mock mode without invoking live agy workers",
    )
    parser.add_argument(
        "--run-dir",
        help="Custom run output directory",
    )
    parser.add_argument(
        "--db",
        help="SQLite database path for persisting run state",
    )
    parser.add_argument(
        "--timeout-minutes",
        type=int,
        default=30,
        help="Maximum per-agent execution timeout in minutes (default: 30)",
    )


def execute_launch(args: argparse.Namespace) -> int:
    """Executes the launch command."""
    pkg_path = args.package or args.package_opt
    if not pkg_path:
        print(
            "[ERROR] Missing required wave package path. Provide <package> or --package <path>.",
            file=sys.stderr,
        )
        return 1

    # Connect to db if specified
    db_conn = None
    if args.db:
        db_path = Path(args.db).resolve()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        db_conn = sqlite3.connect(str(db_path))

    operator = LegacyOperatorExperience()
    try:
        result = operator.run_wave(
            package_path=pkg_path,
            repo_path=args.repo,
            max_parallel=args.max_parallel,
            bypass_acknowledged=args.bypass_acknowledged,
            test_mode=args.test_mode,
            run_dir=args.run_dir,
            source_orchestrator=args.source_orchestrator,
            timeout_minutes=args.timeout_minutes,
            db_conn=db_conn,
        )

        print("\n" + "=" * 70)
        print("               SACL WAVE EXECUTION RESULT")
        print("=" * 70)
        print(f"Run ID:        {result.run_id}")
        print(f"Package ID:    {result.package_id}")
        print(f"Project:       {result.project}")
        print(f"Status:        {result.status}")
        print(f"Run Directory: {result.run_dir}")
        print(f"Summary MD:    {result.summary_md_path}")
        print(f"Summary JSON:  {result.summary_json_path}")
        if result.final_report_path:
            print(f"Final Report:  {result.final_report_path}")
        print("-" * 70)
        print(f"Result Badge:  {result.message}")
        print("=" * 70 + "\n")
        return result.exit_code

    except PermissionError as pe:
        print(f"\n[SECURITY REFUSAL] {pe}", file=sys.stderr)
        print(
            "Pass --bypass-acknowledged if you are authorized to run autonomous agent workers.\n",
            file=sys.stderr,
        )
        return 2
    except Exception as exc:
        print(f"\n[EXECUTION ERROR] {exc}\n", file=sys.stderr)
        return 1
    finally:
        if db_conn:
            db_conn.close()

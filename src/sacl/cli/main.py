"""SACL V1 Main Command Line Interface (CLI).

Provides unified command dispatch for SACL operations:
- launch / run: Executes wave packages
- status: Inspects active or recent run statuses
- stop: Safely stops agent processes using PID recycling defense
- monitor: Real-time read-only console dashboard
- package: Packages, verifies, or extracts wave archives
- preflight: Verifies environment and dirty-root rule
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from sacl.cli.launch import configure_launch_parser, execute_launch
from sacl.cli.monitor import configure_monitor_parser, execute_monitor
from sacl.cli.package import configure_package_parser, execute_package
from sacl.cli.preflight import configure_preflight_parser, execute_preflight
from sacl.cli.status import configure_status_parser, execute_status
from sacl.cli.stop import configure_stop_parser, execute_stop

VERSION = "1.0.0"


def build_parser() -> argparse.ArgumentParser:
    """Builds the root argument parser for sacl CLI."""
    parser = argparse.ArgumentParser(
        prog="sacl",
        description="SolidBit Agent Execution Control Loop (SACL V1) Command Line Interface",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"SACL V1 CLI Version {VERSION}",
    )

    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # 1. launch / run
    launch_parser = subparsers.add_parser("launch", help="Launch and execute a wave package")
    configure_launch_parser(launch_parser)
    run_parser = subparsers.add_parser("run", help="Alias for launch")
    configure_launch_parser(run_parser)

    # 2. status
    status_parser = subparsers.add_parser("status", help="Inspect agent and run execution status")
    configure_status_parser(status_parser)

    # 3. stop
    stop_parser = subparsers.add_parser("stop", help="Safely stop running agent workers")
    configure_stop_parser(stop_parser)

    # 4. monitor
    monitor_parser = subparsers.add_parser("monitor", help="Live console status monitor")
    configure_monitor_parser(monitor_parser)

    # 5. package
    package_parser = subparsers.add_parser("package", help="Create, verify, or extract wave packages")
    configure_package_parser(package_parser)

    # 6. preflight / doctor
    preflight_parser = subparsers.add_parser("preflight", help="Validate host environment and clean-root rule")
    configure_preflight_parser(preflight_parser)
    doctor_parser = subparsers.add_parser("doctor", help="Alias for preflight")
    configure_preflight_parser(doctor_parser)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)

    cmd = args.subcommand
    if cmd in ("launch", "run"):
        return execute_launch(args)
    elif cmd == "status":
        return execute_status(args)
    elif cmd == "stop":
        return execute_stop(args)
    elif cmd == "monitor":
        return execute_monitor(args)
    elif cmd == "package":
        return execute_package(args)
    elif cmd in ("preflight", "doctor"):
        return execute_preflight(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())

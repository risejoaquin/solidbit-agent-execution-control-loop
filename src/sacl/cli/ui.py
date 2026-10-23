"""SACL V1 CLI UI Subcommand.

Launches the Apple-grade Decision Shell local web dashboard.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
import sys
import webbrowser

from sacl.ui.server import DecisionShellServer

logger = logging.getLogger("sacl.cli.ui")


def configure_ui_parser(parser: argparse.ArgumentParser) -> None:
    """Configures CLI arguments for the ui command."""
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host interface to bind to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Port to listen on (default: 8765)",
    )
    parser.add_argument(
        "--db",
        help="Path to SQLite operational database (sacl_ops.db)",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not automatically open the web browser",
    )


def execute_ui(args: argparse.Namespace) -> int:
    """Executes the Decision Shell web server."""
    db_path = None
    if args.db:
        db_path = Path(args.db).resolve()

    server = DecisionShellServer(
        host=args.host,
        port=args.port,
        db_path=db_path,
    )

    url = f"http://{args.host}:{args.port}"
    print(f"[INFO] Launching SACL Decision Shell on {url}")
    print("[INFO] Press Ctrl+C to terminate.")

    if not args.no_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    try:
        server.start(blocking=True)
        return 0
    except KeyboardInterrupt:
        print("\n[INFO] Decision Shell stopped.")
        return 0
    except Exception as exc:
        print(f"[ERROR] Failed to start Decision Shell: {exc}", file=sys.stderr)
        return 1

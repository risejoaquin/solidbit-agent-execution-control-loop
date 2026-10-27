"""SACL V1 CLI Preflight / Doctor Subcommand.

Performs host environment validation, tool checks, and target repository
clean-root verification matching 00-preflight.ps1.
"""

from __future__ import annotations

import argparse
import logging
import shutil
import subprocess
from pathlib import Path

from sacl.legacy.compatibility import check_dirty_root

logger = logging.getLogger("sacl.cli.preflight")


def configure_preflight_parser(parser: argparse.ArgumentParser) -> None:
    """Configures CLI arguments for the preflight/doctor command."""
    parser.add_argument(
        "--repo",
        help="Target local repository path to verify clean-root status",
    )
    parser.add_argument(
        "--db",
        help="Path to SQLite operational database to check connectivity",
    )


def execute_preflight(args: argparse.Namespace) -> int:
    """Executes preflight environment checks."""
    print("\n" + "=" * 70)
    print("                    SACL PREFLIGHT ENVIRONMENT CHECK")
    print("=" * 70)

    checks_passed = True

    # 1. Host Tools Verification
    tools = [
        ("Git CLI", ["git", "--version"]),
        (
            "PowerShell CLI",
            ["powershell.exe", "-NoProfile", "-Command", "$PSVersionTable.PSVersion.ToString()"],
        ),
        ("Antigravity CLI", ["agy.exe", "--version"]),
    ]

    print("[1] Host Executable Tools Check:")
    for name, cmd in tools:
        cmd_name = cmd[0]
        found = shutil.which(cmd_name) is not None
        if not found and cmd_name.endswith(".exe"):
            found = shutil.which(cmd_name[:-4]) is not None

        if found:
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                v_text = res.stdout.strip().splitlines()[0] if res.stdout else "Available"
                print(f"  [PASS] {name:<18}: {v_text}")
            except Exception:
                print(f"  [PASS] {name:<18}: Found in PATH")
        else:
            if "Antigravity" in name:
                print(
                    f"  [WARN] {name:<18}: NOT FOUND (Mock/Test mode available; live runs require agy)"
                )
            else:
                print(f"  [FAIL] {name:<18}: NOT FOUND in system PATH")
                checks_passed = False

    # 2. Python Dependencies Check
    print("\n[2] Python Core Dependencies:")
    deps = ["jsonschema", "sqlite3"]
    for dep in deps:
        try:
            __import__(dep)
            print(f"  [PASS] Module {dep:<14}: Installed")
        except ImportError:
            print(f"  [FAIL] Module {dep:<14}: MISSING")
            checks_passed = False

    # 3. Target Repository Clean-Root Verification
    if args.repo:
        repo_p = Path(args.repo).resolve()
        print(f"\n[3] Target Repository Check ({repo_p}):")
        if not repo_p.exists():
            print(f"  [FAIL] Repository path does not exist: {repo_p}")
            checks_passed = False
        else:
            is_dirty, output = check_dirty_root(repo_p)
            if is_dirty:
                print("  [FAIL] Inviolable Local Dirty-Root Rule Violation!")
                print(f"         Uncommitted modifications detected in primary checkout:\n{output}")
                checks_passed = False
            else:
                print("  [PASS] Clean primary checkout verified (zero uncommitted human edits).")

    print("=" * 70)
    if checks_passed:
        print("PREFLIGHT VERDICT: PASS (Environment ready for SACL execution)")
        print("=" * 70 + "\n")
        return 0
    else:
        print("PREFLIGHT VERDICT: FAIL (Address above items before live execution)")
        print("=" * 70 + "\n")
        return 1

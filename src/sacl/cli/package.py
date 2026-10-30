"""SACL V1 CLI Package Subcommand.

Creates, verifies, and extracts wave packages adhering to ADR-004 canonical structure.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from sacl.legacy.packager import WaveZipPackager

logger = logging.getLogger("sacl.cli.package")


def configure_package_parser(parser: argparse.ArgumentParser) -> None:
    """Configures CLI arguments for the package command."""
    subparsers = parser.add_subparsers(dest="package_action", required=True)

    # 1. create
    create_parser = subparsers.add_parser(
        "create", help="Package a wave directory into a canonical wave ZIP"
    )
    create_parser.add_argument("source_dir", help="Directory containing package files")
    create_parser.add_argument("--output", "-o", help="Output .zip destination path")
    create_parser.add_argument(
        "--prefix-root", action="store_true", help="Prefix zip entries with <package_id>/"
    )

    # 2. verify
    verify_parser = subparsers.add_parser(
        "verify", help="Verify integrity, layout, and schema of a wave package"
    )
    verify_parser.add_argument("package_path", help="Path to wave directory or .zip archive")

    # 3. extract
    extract_parser = subparsers.add_parser("extract", help="Safely extract a wave ZIP archive")
    extract_parser.add_argument("zip_path", help="Path to .zip package archive")
    extract_parser.add_argument("destination", help="Target extraction directory")


def execute_package(args: argparse.Namespace) -> int:
    """Executes the package command."""
    packager = WaveZipPackager()
    action = args.package_action

    if action == "create":
        src_dir = Path(args.source_dir).resolve()
        if not src_dir.is_dir():
            print(f"[ERROR] Source directory does not exist: {src_dir}", file=sys.stderr)
            return 1

        out_zip = (
            Path(args.output).resolve() if args.output else src_dir.parent / f"{src_dir.name}.zip"
        )
        try:
            created_zip = packager.package_wave_dir(
                source_dir=src_dir,
                output_zip_path=out_zip,
                generate_checksums=True,
                package_root_in_zip=args.prefix_root,
            )
            print(f"[SUCCESS] Wave package created: {created_zip}")
            return 0
        except Exception as exc:
            print(f"[ERROR] Failed to create package: {exc}", file=sys.stderr)
            return 1

    elif action == "verify":
        target_path = Path(args.package_path).resolve()
        if not target_path.exists():
            print(f"[ERROR] Target path does not exist: {target_path}", file=sys.stderr)
            return 1

        is_valid, errors = packager.verify_wave_package(target_path)
        if is_valid:
            print(f"[PASS] Package verified successfully: {target_path}")
            return 0
        else:
            print(
                f"[FAIL] Package verification failed with {len(errors)} error(s):", file=sys.stderr
            )
            for err in errors:
                print(f"  - {err}", file=sys.stderr)
            return 1

    elif action == "extract":
        zip_p = Path(args.zip_path).resolve()
        dest_p = Path(args.destination).resolve()
        if not zip_p.is_file():
            print(f"[ERROR] ZIP file does not exist: {zip_p}", file=sys.stderr)
            return 1

        try:
            extracted = packager.extract_wave_package(zip_p, dest_p)
            print(f"[SUCCESS] Extracted {len(extracted)} files to: {dest_p}")
            return 0
        except Exception as exc:
            print(f"[ERROR] Failed extracting package: {exc}", file=sys.stderr)
            return 1

    return 0

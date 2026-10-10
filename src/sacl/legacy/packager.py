"""SACL V1 Wave ZIP Archive Packager and Verifier.

Implements ADR-004 canonical package packaging, verification, and extraction:
1. Canonical ZIP Archive Structure
2. Cryptographic Asset Integrity (checksums.sha256)
3. Anti-Zip Slip, DOS Reserved Names, Symlink & Quota Defenses
"""

from __future__ import annotations

import hashlib
import io
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import zipfile

from sacl.contracts.schema_validator import SchemaValidator, get_default_validator
from sacl.legacy.adapter import LegacyPackageAdapter
from sacl.transport.sanitization import (
    MAX_COMPRESSED_SIZE_BYTES,
    MAX_COMPRESSION_RATIO,
    MAX_TOTAL_FILE_COUNT,
    MAX_UNCOMPRESSED_SIZE_BYTES,
    ZipDefenseExtractor,
)

logger = logging.getLogger("sacl.legacy.packager")


def compute_sha256(file_path: Union[Path, str]) -> str:
    """Computes SHA-256 digest of a local file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class WaveZipPackager:
    """Packages directories into canonical wave ZIPs and extracts them with security checks."""

    def __init__(
        self,
        validator: Optional[SchemaValidator] = None,
        extractor: Optional[ZipDefenseExtractor] = None,
    ) -> None:
        self.validator = validator or get_default_validator()
        self.extractor = extractor or ZipDefenseExtractor()
        self.adapter = LegacyPackageAdapter(validator=self.validator)

    def create_checksums_file(self, package_dir: Union[Path, str]) -> Path:
        """Computes SHA-256 for all files in package_dir and writes checksums.sha256."""
        pkg_path = Path(package_dir).resolve()
        checksums_path = pkg_path / "checksums.sha256"

        entries: List[Tuple[str, str]] = []
        for file_p in sorted(pkg_path.rglob("*")):
            if file_p.is_file():
                rel_path = file_p.relative_to(pkg_path).as_posix()
                if rel_path in {"checksums.sha256", "LAST_RUN.txt", "LATEST_RUN.txt"}:
                    continue
                # Ignore runs/ or launcher-logs/ if present in dev dir
                if rel_path.startswith("runs/") or rel_path.startswith("launcher-logs/"):
                    continue
                digest = compute_sha256(file_p)
                entries.append((digest, rel_path))

        lines = [f"{digest}  {rel}" for digest, rel in sorted(entries, key=lambda x: x[1])]
        with open(checksums_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + ("\n" if lines else ""))

        return checksums_path

    def package_wave_dir(
        self,
        source_dir: Union[Path, str],
        output_zip_path: Union[Path, str],
        generate_checksums: bool = True,
        package_root_in_zip: bool = False,
    ) -> Path:
        """Packages source_dir into a canonical wave ZIP archive.

        Args:
            source_dir: Directory containing package contents.
            output_zip_path: Output .zip file path.
            generate_checksums: If True, regenerates checksums.sha256 prior to archiving.
            package_root_in_zip: If True, prefixes all entries with <package_id>/.
        """
        src_path = Path(source_dir).resolve()
        out_path = Path(output_zip_path).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if generate_checksums:
            self.create_checksums_file(src_path)

        # Normalize and validate manifest
        manifest = self.adapter.load_manifest(src_path)
        pkg_prefix = f"{manifest.package_id}/" if package_root_in_zip else ""

        with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for file_p in sorted(src_path.rglob("*")):
                if file_p.is_file():
                    rel_p = file_p.relative_to(src_path).as_posix()
                    # Skip internal ephemeral runs from packaging
                    if rel_p.startswith("runs/") or rel_p.startswith("launcher-logs/"):
                        continue
                    arcname = f"{pkg_prefix}{rel_p}"
                    zf.write(file_p, arcname=arcname)

        return out_path

    def verify_wave_package(
        self,
        package_source: Union[Path, str, bytes],
    ) -> Tuple[bool, List[str]]:
        """Verifies integrity, canonical layout, and manifest conformance of a wave package.

        Returns:
            (is_valid, error_list)
        """
        errors: List[str] = []

        if isinstance(package_source, (bytes, bytearray)):
            try:
                zf = zipfile.ZipFile(io.BytesIO(package_source), "r")
            except zipfile.BadZipFile:
                return False, ["Payload is not a valid zip archive"]
        else:
            p = Path(package_source)
            if p.is_dir():
                return self._verify_wave_dir(p)
            if p.is_file() and p.suffix.lower() == ".json":
                try:
                    self.adapter.load_manifest(p)
                    return True, []
                except Exception as exc:
                    return False, [f"Manifest validation error: {exc}"]
            try:
                zf = zipfile.ZipFile(p, "r")
            except zipfile.BadZipFile:
                return False, [f"File is not a valid zip archive: {p}"]

        with zf:
            names = set(zf.namelist())
            # Strip single top-level folder prefix if present (<PACKAGE_ID>/...)
            stripped_map = {}
            for name in names:
                parts = name.split("/", 1)
                if len(parts) == 2 and not name.endswith("/"):
                    stripped_map[parts[1]] = name
                else:
                    stripped_map[name] = name

            # 1. Check for manifest.json
            manifest_entry = None
            if "manifest.json" in names:
                manifest_entry = "manifest.json"
            elif "manifest.json" in stripped_map:
                manifest_entry = stripped_map["manifest.json"]
            else:
                for n in names:
                    if n.endswith("/manifest.json") or n == "manifest.json":
                        manifest_entry = n
                        break

            if not manifest_entry:
                errors.append("Package missing manifest.json")
            else:
                try:
                    with zf.open(manifest_entry) as mf:
                        raw_manifest = json.load(mf)
                    norm_manifest = self.adapter.normalize_manifest_dict(raw_manifest)
                    self.validator.validate_manifest(norm_manifest)
                except Exception as exc:
                    errors.append(f"Manifest schema validation error: {exc}")

            # 2. Check checksums.sha256 if present
            checksums_entry = None
            for n in names:
                if n.endswith("/checksums.sha256") or n == "checksums.sha256":
                    checksums_entry = n
                    break

            if checksums_entry:
                try:
                    with zf.open(checksums_entry) as cf:
                        lines = cf.read().decode("utf-8").splitlines()

                    for line in lines:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        parts = line.split(None, 1)
                        if len(parts) == 2:
                            expected_sha, file_rel = parts[0].strip(), parts[1].strip()
                            # Resolve in zf
                            resolved_entry = None
                            for n in names:
                                if n.endswith(file_rel):
                                    resolved_entry = n
                                    break
                            if not resolved_entry:
                                errors.append(f"Checksum manifest references missing file: {file_rel}")
                            else:
                                with zf.open(resolved_entry) as member_file:
                                    actual_sha = hashlib.sha256(member_file.read()).hexdigest()
                                if actual_sha.lower() != expected_sha.lower():
                                    errors.append(f"SHA-256 mismatch for {file_rel}: expected {expected_sha}, got {actual_sha}")
                except Exception as exc:
                    errors.append(f"Failed to verify checksums.sha256: {exc}")

        return (len(errors) == 0, errors)

    def _verify_wave_dir(self, pkg_dir: Path) -> Tuple[bool, List[str]]:
        """Verifies an unpacked wave package directory."""
        errors: List[str] = []
        manifest_file = pkg_dir / "manifest.json"
        if not manifest_file.exists():
            errors.append("Package missing manifest.json")
        else:
            try:
                self.adapter.load_manifest(pkg_dir)
            except Exception as exc:
                errors.append(f"Manifest validation error: {exc}")

        checksums_file = pkg_dir / "checksums.sha256"
        if checksums_file.exists():
            try:
                with open(checksums_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        parts = line.split(None, 1)
                        if len(parts) == 2:
                            expected_sha, rel_name = parts[0].strip(), parts[1].strip()
                            target_f = pkg_dir / rel_name
                            if not target_f.exists():
                                errors.append(f"Checksum file references missing file: {rel_name}")
                            else:
                                actual_sha = compute_sha256(target_f)
                                if actual_sha.lower() != expected_sha.lower():
                                    errors.append(f"SHA-256 mismatch for {rel_name}")
            except Exception as exc:
                errors.append(f"Failed to check checksums: {exc}")

        return (len(errors) == 0, errors)

    def extract_wave_package(
        self,
        package_source: Union[Path, str, bytes],
        destination_dir: Union[Path, str],
        package_id: str = "wave_package",
    ) -> List[Path]:
        """Safely extracts a wave package using ZipDefenseExtractor."""
        dest_path = Path(destination_dir)
        return self.extractor.validate_and_extract(
            archive_source=package_source,
            destination_dir=dest_path,
            package_id=package_id,
        )

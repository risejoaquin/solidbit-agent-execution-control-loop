"""SACL V1 Package Validator Implementation.

Implements IPackageValidator interface enforcing:
- Resource decompression quotas (zip bomb defense)
- Anti-Zip Slip canonical path sanitization
- Windows DOS reserved device names and ADS defense
- Symlink and reparse point rejection
- Prohibited uninspected binary rejection (.exe, .dll, .cmd, .msi)
- Declarative authority enforcement (ban on authorized_scripts)
- Canonical JSON schema validation (schemas/manifest.schema.json)
- Cryptographic SHA-256 asset integrity verification (checksums.sha256)
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import zipfile

from sacl.contracts.interfaces import IPackageValidator
from sacl.contracts.models import Manifest
from sacl.contracts.schema_validator import SchemaValidator, get_default_validator
from sacl.contracts.exceptions import ContractValidationError

from sacl.package.exceptions import (
    DeclarativeAuthorityViolationError,
    InvalidFilenameError,
    ManifestValidationError,
    PackageIntegrityMismatchError,
    ProhibitedBinaryError,
    SymlinkNotPermittedError,
    ZipPathTraversalError,
    ZipResourceLimitExceeded,
)
from sacl.package.limits import (
    PackageResourceLimits,
    has_alternate_data_stream,
    is_prohibited_binary,
    is_reserved_device_name,
    is_symlink_or_reparse,
)


def compute_sha256(file_path: Path) -> str:
    """Computes SHA-256 digest of a file in streaming chunks."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().lower()


def compute_bytes_sha256(data: bytes) -> str:
    """Computes SHA-256 digest of raw bytes."""
    return hashlib.sha256(data).hexdigest().lower()


class PackageValidator(IPackageValidator):
    """Authoritative validator for SACL V1 execution packages."""

    def __init__(
        self,
        limits: Optional[PackageResourceLimits] = None,
        schema_validator: Optional[SchemaValidator] = None,
    ) -> None:
        self.limits = limits or PackageResourceLimits()
        self.schema_validator = schema_validator or get_default_validator()

    def check_zip_slip(self, zip_path: Path, target_dir: Optional[Path] = None) -> List[str]:
        """Detects path traversal or escaping relative paths in archive.

        Inspects every member entry for traversal tokens (..), absolute path prefixes,
        NTFS alternate data stream colons, and canonical destination escapes.
        """
        violations: List[str] = []
        dest_canonical = (target_dir or (Path.cwd() / "_dest_check")).resolve()
        dest_str = str(dest_canonical)

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                for entry in zf.infolist():
                    name = entry.filename

                    # 1. Check for directory traversal sequences
                    normalized = name.replace("\\", "/")
                    segments = [s for s in normalized.split("/") if s]
                    if any(seg == ".." for seg in segments):
                        violations.append(f"Contains '..' traversal segment: '{name}'")
                        continue

                    # 2. Check for absolute path roots
                    if name.startswith("/") or name.startswith("\\"):
                        violations.append(f"Contains leading root separator: '{name}'")
                        continue

                    # Drive root check (e.g. C:\ or C:/)
                    if len(name) >= 2 and name[1] == ":" and name[0].isalpha():
                        violations.append(f"Contains absolute drive letter: '{name}'")
                        continue

                    # 3. Alternate Data Stream colon check
                    if ":" in name:
                        violations.append(f"Contains NTFS stream colon: '{name}'")
                        continue

                    # 4. Canonical path prefix match
                    resolved_target = (dest_canonical / name).resolve()
                    resolved_str = str(resolved_target)
                    if not (resolved_str == dest_str or resolved_str.startswith(dest_str + os.sep)):
                        violations.append(f"Canonical path escapes staging destination: '{name}' -> '{resolved_str}'")

        except zipfile.BadZipFile as err:
            violations.append(f"Corrupted or invalid ZIP file: {err}")

        return violations

    def validate_archive(self, zip_path: Path) -> Manifest:
        """Validates package archive structure, manifest schema, and zip-slip defense.

        Enforces resource limits, anti-traversal, binary prohibition, and declarative authority.
        Returns the parsed Manifest model upon full validation.
        """
        if not zip_path.exists():
            raise FileNotFoundError(f"Package archive not found: {zip_path}")

        # Step 1: Check compressed archive size limit
        archive_size = zip_path.stat().st_size
        if archive_size > self.limits.max_archive_size_bytes:
            raise ZipResourceLimitExceeded(
                package_id="UNKNOWN",
                reason=(
                    f"Compressed archive size {archive_size} bytes exceeds limit of "
                    f"{self.limits.max_archive_size_bytes} bytes (25 MB)"
                ),
                details={"archive_size": archive_size, "limit": self.limits.max_archive_size_bytes},
            )

        try:
            zf = zipfile.ZipFile(zip_path, "r")
        except zipfile.BadZipFile as err:
            raise ZipResourceLimitExceeded(
                package_id="UNKNOWN",
                reason=f"Failed to open archive: {err}",
            )

        with zf:
            # Step 2: Zip Slip & path traversal defense
            traversal_violations = self.check_zip_slip(zip_path)
            if traversal_violations:
                raise ZipPathTraversalError(
                    package_id="UNKNOWN",
                    reason=f"Detected {len(traversal_violations)} path traversal violation(s)",
                    violations=traversal_violations,
                )

            entries = zf.infolist()

            # Step 3: Total file count quota
            file_count = len(entries)
            if file_count > self.limits.max_file_count:
                raise ZipResourceLimitExceeded(
                    package_id="UNKNOWN",
                    reason=(
                        f"File count {file_count} exceeds limit of "
                        f"{self.limits.max_file_count} files"
                    ),
                    details={"file_count": file_count, "limit": self.limits.max_file_count},
                )

            # Step 4: Total uncompressed extraction size & compression ratio quotas
            total_uncompressed = sum(e.file_size for e in entries)
            if total_uncompressed > self.limits.max_uncompressed_size_bytes:
                raise ZipResourceLimitExceeded(
                    package_id="UNKNOWN",
                    reason=(
                        f"Uncompressed extraction size {total_uncompressed} bytes exceeds limit of "
                        f"{self.limits.max_uncompressed_size_bytes} bytes (100 MB)"
                    ),
                    details={"uncompressed_bytes": total_uncompressed, "limit": self.limits.max_uncompressed_size_bytes},
                )

            if archive_size > 0:
                ratio = total_uncompressed / archive_size
                if ratio > self.limits.max_compression_ratio:
                    raise ZipResourceLimitExceeded(
                        package_id="UNKNOWN",
                        reason=(
                            f"Compression ratio {ratio:.1f}:1 exceeds quota of "
                            f"{self.limits.max_compression_ratio}:1"
                        ),
                        details={"compression_ratio": ratio, "limit": self.limits.max_compression_ratio},
                    )

            # Step 5: Member name, DOS device names, symlinks, and binary inspections
            for entry in entries:
                name = entry.filename

                # DOS Reserved Device Names (CON, PRN, AUX, NUL, COM1-9, LPT1-9)
                if is_reserved_device_name(name, self.limits.reserved_device_names):
                    raise InvalidFilenameError(
                        package_id="UNKNOWN",
                        reason=f"Filename matches Windows reserved DOS device name: '{name}'",
                        offending_name=name,
                    )

                # Alternate Data Streams (colon)
                if has_alternate_data_stream(name):
                    raise InvalidFilenameError(
                        package_id="UNKNOWN",
                        reason=f"Filename contains NTFS Alternate Data Stream (ADS) colon: '{name}'",
                        offending_name=name,
                    )

                # Symlinks & Reparse Points
                if is_symlink_or_reparse(entry):
                    raise SymlinkNotPermittedError(
                        package_id="UNKNOWN",
                        entry_name=name,
                    )

                # Prohibited Executable Binaries (.exe, .dll, .cmd, .msi)
                if is_prohibited_binary(name, self.limits.prohibited_extensions):
                    raise ProhibitedBinaryError(
                        package_id="UNKNOWN",
                        entry_name=name,
                    )

            # Step 6: Locate and parse manifest.json
            manifest_entry_name = self._find_manifest_entry(entries)
            if manifest_entry_name is None:
                raise ManifestValidationError(
                    package_id="UNKNOWN",
                    reason="Package archive does not contain 'manifest.json' at root",
                )

            try:
                manifest_raw = zf.read(manifest_entry_name).decode("utf-8")
                manifest_dict = json.loads(manifest_raw)
            except Exception as err:
                raise ManifestValidationError(
                    package_id="UNKNOWN",
                    reason=f"Failed to read or parse manifest.json: {err}",
                )

            package_id = manifest_dict.get("package_id", "UNKNOWN")

            # Step 7: Declarative Authority Check - authorized_scripts strictly forbidden!
            if "authorized_scripts" in manifest_dict:
                raise DeclarativeAuthorityViolationError(
                    package_id=package_id,
                    reason=(
                        "Manifest contains prohibited authority field 'authorized_scripts'. "
                        "Packages possess zero execution authority and cannot self-authorize attached code."
                    ),
                )

            # Step 8: Canonical JSON Schema Validation
            try:
                self.schema_validator.validate_manifest(manifest_dict)
            except ContractValidationError as cve:
                raise ManifestValidationError(
                    package_id=package_id,
                    reason=f"manifest.json violates manifest.schema.json: {cve.message}",
                    errors=cve.validation_errors,
                )

            # Step 9: Deserialization into Manifest model
            return Manifest.from_dict(manifest_dict)

    def _find_manifest_entry(self, entries: List[zipfile.ZipInfo]) -> Optional[str]:
        """Finds manifest.json at root or single top-level directory root."""
        for e in entries:
            norm = e.filename.replace("\\", "/").strip("/")
            if norm == "manifest.json":
                return e.filename

        # If wrapped under a single folder (e.g. <PACKAGE_ID>/manifest.json)
        for e in entries:
            norm = e.filename.replace("\\", "/").strip("/")
            parts = norm.split("/")
            if len(parts) == 2 and parts[1] == "manifest.json":
                return e.filename

        return None

    def verify_checksums(self, extracted_dir: Path, checksums_file: str = "checksums.sha256") -> bool:
        """Verifies cryptographic integrity of extracted package assets against checksums file.

        Lines format: <sha256_hex>  <relative_filepath> or <sha256_hex> *<relative_filepath>.
        """
        if not extracted_dir.exists():
            raise FileNotFoundError(f"Extracted directory not found: {extracted_dir}")

        # Search for checksums file at root or in single top-level subdir
        target_checksums_path = extracted_dir / checksums_file
        if not target_checksums_path.exists():
            # Check if all files were extracted inside a subfolder
            subdirs = [d for d in extracted_dir.iterdir() if d.is_dir()]
            for sd in subdirs:
                cand = sd / checksums_file
                if cand.exists():
                    target_checksums_path = cand
                    break

        if not target_checksums_path.exists():
            raise PackageIntegrityMismatchError(
                package_id=extracted_dir.name,
                reason=f"Checksums file '{checksums_file}' missing from extracted package directory",
            )

        base_dir = target_checksums_path.parent
        mismatched: List[str] = []

        with open(target_checksums_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if not lines:
            raise PackageIntegrityMismatchError(
                package_id=extracted_dir.name,
                reason="Checksums file is empty",
            )

        for line_no, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            parts = stripped.split(None, 1)
            if len(parts) != 2:
                continue

            expected_sha = parts[0].strip().lower()
            rel_path = parts[1].strip()
            if rel_path.startswith("*"):
                rel_path = rel_path[1:].strip()

            target_file = (base_dir / rel_path).resolve()

            if not target_file.exists() or not target_file.is_file():
                mismatched.append(f"Missing asset declared in checksums: '{rel_path}'")
                continue

            actual_sha = compute_sha256(target_file)
            if actual_sha != expected_sha:
                mismatched.append(
                    f"Integrity mismatch for '{rel_path}': expected {expected_sha}, computed {actual_sha}"
                )

        if mismatched:
            raise PackageIntegrityMismatchError(
                package_id=extracted_dir.name,
                reason=f"Cryptographic integrity verification failed for {len(mismatched)} asset(s)",
                mismatched_files=mismatched,
            )

        return True

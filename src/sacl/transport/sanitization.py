"""SACL V1 Package ZIP Sanitization & Anti-Zip Slip Defense Pipeline.

Implements the four-stage zip extraction defense pipeline mandated in:
- docs/MAIL_PROTOCOL.md §3.7
- ADR-001 / ADR-008
- SB-FREEZE-P1-01 / W0.1 Remediation Baseline #9
"""

from __future__ import annotations

import io
import re
import zipfile
from pathlib import Path
from typing import List, Set, Union

from sacl.contracts.invariants import MAX_ATTACHMENT_SIZE_BYTES
from sacl.transport.exceptions import (
    InvalidFilenameError,
    SymlinkNotPermittedError,
    ZipPathTraversalError,
    ZipResourceLimitExceededError,
)

# Quota limits per docs/MAIL_PROTOCOL.md §3.7
MAX_COMPRESSED_SIZE_BYTES = MAX_ATTACHMENT_SIZE_BYTES  # 25 MB = 26,214,400 bytes
MAX_UNCOMPRESSED_SIZE_BYTES = 104_857_600  # 100 MB = 104,857,600 bytes
MAX_TOTAL_FILE_COUNT = 1000  # 1,000 files
MAX_COMPRESSION_RATIO = 20.0  # 20:1 ratio

# DOS Reserved Device Names (case-insensitive, with or without extension)
DOS_DEVICE_NAMES: Set[str] = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
}

# Regex to detect Windows reserved names on any path segment
DOS_DEVICE_PATTERN = re.compile(r"^(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?$", re.IGNORECASE)

# Unix file type masks
S_IFLNK = 0o120000  # Symbolic link


class ZipDefenseExtractor:
    """Rigorous 4-step security pipeline for incoming package ZIP archives."""

    def __init__(
        self,
        max_compressed_bytes: int = MAX_COMPRESSED_SIZE_BYTES,
        max_uncompressed_bytes: int = MAX_UNCOMPRESSED_SIZE_BYTES,
        max_file_count: int = MAX_TOTAL_FILE_COUNT,
        max_compression_ratio: float = MAX_COMPRESSION_RATIO,
    ) -> None:
        self.max_compressed_bytes = max_compressed_bytes
        self.max_uncompressed_bytes = max_uncompressed_bytes
        self.max_file_count = max_file_count
        self.max_compression_ratio = max_compression_ratio

    def validate_and_extract(
        self,
        archive_source: Union[bytes, Path, str],
        destination_dir: Path,
        package_id: str = "unknown_package",
    ) -> List[Path]:
        """Runs all 4 security checks, then safely extracts entries to destination_dir."""
        # Open ZipFile
        if isinstance(archive_source, (bytes, bytearray)):
            compressed_size = len(archive_source)
            zf = zipfile.ZipFile(io.BytesIO(archive_source), "r")
        else:
            p = Path(archive_source)
            compressed_size = p.stat().st_size
            zf = zipfile.ZipFile(p, "r")

        with zf:
            # Step 1: Quota & Resource Exhaustion (Zip Bomb) Defense
            self._check_resource_quotas(zf, compressed_size, package_id)

            # Steps 2, 3, 4: Entry-by-entry structural inspection
            self._inspect_entries(zf, destination_dir, package_id)

            # Execution: Safe Extraction
            destination_dir.mkdir(parents=True, exist_ok=True)
            extracted_paths: List[Path] = []
            canonical_dest = destination_dir.resolve()

            for member in zf.infolist():
                # Normalize and verify destination
                target_path = (canonical_dest / member.filename).resolve()
                if member.is_dir():
                    target_path.mkdir(parents=True, exist_ok=True)
                else:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(member) as src, open(target_path, "wb") as dst:
                        # Copy stream
                        while True:
                            chunk = src.read(65536)
                            if not chunk:
                                break
                            dst.write(chunk)
                    extracted_paths.append(target_path)

            return extracted_paths

    def _check_resource_quotas(
        self, zf: zipfile.ZipFile, compressed_size: int, package_id: str
    ) -> None:
        """Step 1: Resource Exhaustion Quotas."""
        if compressed_size > self.max_compressed_bytes:
            raise ZipResourceLimitExceededError(
                package_id=package_id,
                metric="compressed_size_bytes",
                actual=compressed_size,
                limit=self.max_compressed_bytes,
            )

        infolist = zf.infolist()
        if len(infolist) > self.max_file_count:
            raise ZipResourceLimitExceededError(
                package_id=package_id,
                metric="total_file_count",
                actual=len(infolist),
                limit=self.max_file_count,
            )

        total_uncompressed = sum(info.file_size for info in infolist)
        if total_uncompressed > self.max_uncompressed_bytes:
            raise ZipResourceLimitExceededError(
                package_id=package_id,
                metric="uncompressed_size_bytes",
                actual=total_uncompressed,
                limit=self.max_uncompressed_bytes,
            )

        # Check ratio (avoid division by zero on empty archive)
        if compressed_size > 0:
            ratio = total_uncompressed / float(compressed_size)
            if ratio > self.max_compression_ratio:
                raise ZipResourceLimitExceededError(
                    package_id=package_id,
                    metric="compression_ratio",
                    actual=round(ratio, 2),
                    limit=self.max_compression_ratio,
                )

    def _inspect_entries(self, zf: zipfile.ZipFile, destination_dir: Path, package_id: str) -> None:
        """Steps 2, 3, 4: Path Sanitization, Windows Reserved Names, and Symlink Rejection."""
        canonical_dest = destination_dir.resolve()

        for member in zf.infolist():
            raw_name = member.filename

            # Step 2: Anti-Zip Slip canonical path check
            if ".." in raw_name.replace("\\", "/").split("/"):
                raise ZipPathTraversalError(package_id=package_id, entry_name=raw_name)

            if raw_name.startswith("/") or raw_name.startswith("\\"):
                raise ZipPathTraversalError(package_id=package_id, entry_name=raw_name)

            # Check drive letter patterns e.g. C:
            if re.match(r"^[a-zA-Z]:", raw_name):
                raise ZipPathTraversalError(package_id=package_id, entry_name=raw_name)

            # Canonical resolve check
            try:
                candidate = (canonical_dest / raw_name).resolve()
            except Exception as e:
                raise ZipPathTraversalError(package_id=package_id, entry_name=raw_name) from e

            try:
                # Python 3.9+ candidate.is_relative_to(canonical_dest)
                candidate.relative_to(canonical_dest)
            except ValueError:
                raise ZipPathTraversalError(package_id=package_id, entry_name=raw_name)

            # Step 3: Windows Reserved Names & ADS Defense
            # Split path into parts to verify each directory and file name
            parts = re.split(r"[/\\]", raw_name)
            for part in parts:
                if not part:
                    continue

                # Check Alternate Data Stream (colons)
                if ":" in part:
                    raise InvalidFilenameError(
                        package_id=package_id,
                        entry_name=raw_name,
                        pattern="ALTERNATE_DATA_STREAM_COLON",
                    )

                # Check DOS Device Names
                if DOS_DEVICE_PATTERN.match(part):
                    raise InvalidFilenameError(
                        package_id=package_id,
                        entry_name=raw_name,
                        pattern=f"DOS_DEVICE_NAME_{part.upper()}",
                    )

            # Step 4: Symlink, Hardlink & Reparse Point Rejection
            # Unix file attributes reside in top 16 bits of external_attr
            unix_mode = (member.external_attr >> 16) & 0o170000
            if unix_mode == S_IFLNK:
                raise SymlinkNotPermittedError(package_id=package_id, entry_name=raw_name)

            # Check Windows reparse point attribute flag (0x0400 = FILE_ATTRIBUTE_REPARSE_POINT)
            win_attr = member.external_attr & 0xFFFF
            if win_attr & 0x0400:
                raise SymlinkNotPermittedError(package_id=package_id, entry_name=raw_name)

"""SACL V1 Canonical Path Sanitization & Anti-Zip Slip Defense Engine.

Implements Threat T1 & TH-04 mitigations:
- Canonical destination prefix matching (Path.GetFullPath equivalent)
- Directory traversal sequence detection (..)
- Absolute root and drive letter rejection (C:\\, /etc)
- Windows DOS device name detection (CON, PRN, AUX, NUL, COM1-9, LPT1-9)
- NTFS Alternate Data Stream (ADS) colon rejection
- Symlink, hardlink, and reparse point rejection
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import FrozenSet, List, Optional, Set, Tuple, Union

from sacl.security.exceptions import (
    InvalidFilenameSecurityError,
    PathTraversalSecurityError,
    SymlinkSecurityError,
)

# Unix file type masks
S_IFLNK = 0o120000  # Symbolic link flag in Unix mode (top 16 bits of external_attr)
FILE_ATTRIBUTE_REPARSE_POINT = 0x0400  # Windows reparse point attribute

# Prohibited Windows DOS device names
DOS_DEVICE_NAMES: FrozenSet[str] = frozenset({
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
})

# Regex matching DOS device names with or without extension on any path segment
DOS_DEVICE_REGEX = re.compile(
    r"^(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?$",
    re.IGNORECASE,
)

# Regex matching drive letters (e.g. C:, D:)
DRIVE_LETTER_REGEX = re.compile(r"^[a-zA-Z]:", re.ASCII)


def normalize_path(path: Union[str, Path]) -> str:
    """Normalizes path string to forward slashes with redundant separators removed."""
    s = str(path).strip().replace("\\", "/")
    # Remove redundant slashes
    s = re.sub(r"/+", "/", s)
    return s


def sanitize_relative_path(path_str: str) -> str:
    """Strips leading/trailing slashes and normalizes separators."""
    norm = normalize_path(path_str)
    return norm.strip("/")


def is_dos_device_name(name_segment: str) -> bool:
    """Checks if a single path segment matches Windows DOS reserved device names."""
    if not name_segment:
        return False
    return bool(DOS_DEVICE_REGEX.match(name_segment.strip()))


def has_alternate_data_stream(name_segment: str) -> bool:
    """Checks if a single path segment contains an NTFS Alternate Data Stream colon."""
    return ":" in name_segment


def is_symlink_or_reparse(external_attr: int) -> bool:
    """Checks if zip entry external attributes represent a Unix symlink or Windows reparse point."""
    # Check Unix symlink attribute in upper 16 bits
    unix_mode = (external_attr >> 16) & 0o170000
    if unix_mode == S_IFLNK:
        return True

    # Check Windows reparse point in lower 16 bits
    win_attr = external_attr & 0xFFFF
    if bool(win_attr & FILE_ATTRIBUTE_REPARSE_POINT):
        return True

    return False


def validate_safe_path(
    entry_name: str,
    destination_root: Union[str, Path],
    package_id: str = "unknown",
    external_attr: Optional[int] = None,
) -> Path:
    """Validates an archive entry path against all traversal and Windows filesystem attacks.

    Returns the safe resolved target Path within destination_root.
    Raises:
        PathTraversalSecurityError: On traversal sequences or out-of-boundary paths.
        InvalidFilenameSecurityError: On DOS device names or ADS colons.
        SymlinkSecurityError: On symlinks or reparse points.
    """
    dest_path = Path(destination_root).resolve()
    raw = str(entry_name)

    # 1. Symlink / Reparse Check
    if external_attr is not None and is_symlink_or_reparse(external_attr):
        raise SymlinkSecurityError(entry_name=raw, package_id=package_id)

    # 2. Leading slash or backslash
    if raw.startswith("/") or raw.startswith("\\"):
        raise PathTraversalSecurityError(entry_name=raw, package_id=package_id)

    # 3. Drive letter root (C:\, D:/)
    if DRIVE_LETTER_REGEX.match(raw):
        raise PathTraversalSecurityError(entry_name=raw, package_id=package_id)

    # 4. UNC path (\\\\server\\share)
    if raw.startswith("//") or raw.startswith("\\\\"):
        raise PathTraversalSecurityError(entry_name=raw, package_id=package_id)

    # 5. Segment-level traversal (..) and Windows-specific attack patterns
    normalized = raw.replace("\\", "/")
    segments = [seg for seg in normalized.split("/") if seg]

    for seg in segments:
        if seg == "..":
            raise PathTraversalSecurityError(entry_name=raw, package_id=package_id)

        if has_alternate_data_stream(seg):
            raise InvalidFilenameSecurityError(
                entry_name=raw,
                pattern="ALTERNATE_DATA_STREAM_COLON",
                package_id=package_id,
            )

        if is_dos_device_name(seg):
            raise InvalidFilenameSecurityError(
                entry_name=raw,
                pattern=f"DOS_DEVICE_NAME_{seg.upper()}",
                package_id=package_id,
            )

    # 6. Canonical boundary containment check (Path.GetFullPath prefix check)
    try:
        candidate = (dest_path / raw).resolve()
    except Exception as exc:
        raise PathTraversalSecurityError(entry_name=raw, package_id=package_id) from exc

    # Boundary assertion: candidate must be strictly equal to or relative to dest_path
    try:
        candidate.relative_to(dest_path)
    except ValueError:
        raise PathTraversalSecurityError(entry_name=raw, package_id=package_id)

    return candidate


def assert_within_boundary(
    candidate_path: Union[str, Path],
    boundary_root: Union[str, Path],
    context: str = "path",
) -> Path:
    """Asserts that candidate_path resolves strictly within boundary_root.

    Raises PathTraversalSecurityError if candidate escapes boundary_root.
    """
    root = Path(boundary_root).resolve()
    candidate = Path(candidate_path).resolve()

    try:
        candidate.relative_to(root)
    except ValueError:
        raise PathTraversalSecurityError(
            entry_name=str(candidate_path),
            package_id=f"boundary-escape-{context}",
        )
    return candidate

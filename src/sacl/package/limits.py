"""SACL V1 Package Intake Resource Limits and Security Constants.

Defines decompression quotas, anti-traversal rules, prohibited binaries,
and Windows reserved DOS device names per SACL-SPEC-PKG-v1 and SECURITY_MODEL.md.
"""

from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import FrozenSet

from sacl.contracts.invariants import MAX_ATTACHMENT_SIZE_BYTES

# ============================================================================
# CANONICAL RESOURCE & DECOMPRESSION QUOTAS
# (docs/SECURITY_MODEL.md §4.3 & docs/THREAT_MODEL.md §2.5)
# ============================================================================

# Maximum compressed archive size: 25 MB (matches MAX_ATTACHMENT_SIZE_BYTES)
MAX_ARCHIVE_SIZE_BYTES: int = MAX_ATTACHMENT_SIZE_BYTES  # 26,214,400 bytes

# Maximum uncompressed extraction size: 100 MB
MAX_UNCOMPRESSED_SIZE_BYTES: int = 100 * 1024 * 1024  # 104,857,600 bytes

# Maximum total file count within archive: 1,000 files
MAX_FILE_COUNT: int = 1000

# Maximum compression ratio (Uncompressed / Compressed): 20:1
MAX_COMPRESSION_RATIO: float = 20.0


# ============================================================================
# WINDOWS RESERVED DOS DEVICE NAMES & ADS DEFENSE
# (docs/SECURITY_MODEL.md §4.3 Step 3)
# ============================================================================

RESERVED_DEVICE_NAMES: FrozenSet[str] = frozenset(
    {
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
)


# ============================================================================
# PROHIBITED UNINSPECTED BINARIES & EXECUTABLES
# (docs/EXECUTION_PACKAGE_SPEC.md §5.2 line 149)
# ============================================================================

PROHIBITED_BINARY_EXTENSIONS: FrozenSet[str] = frozenset(
    {
        ".exe",
        ".dll",
        ".cmd",
        ".msi",
    }
)


# ============================================================================
# CONFIGURABLE RESOURCE LIMITS CONTAINER
# ============================================================================


@dataclass(frozen=True)
class PackageResourceLimits:
    """Configurable package resource limits container."""

    max_archive_size_bytes: int = MAX_ARCHIVE_SIZE_BYTES
    max_uncompressed_size_bytes: int = MAX_UNCOMPRESSED_SIZE_BYTES
    max_file_count: int = MAX_FILE_COUNT
    max_compression_ratio: float = MAX_COMPRESSION_RATIO
    prohibited_extensions: FrozenSet[str] = PROHIBITED_BINARY_EXTENSIONS
    reserved_device_names: FrozenSet[str] = RESERVED_DEVICE_NAMES


# ============================================================================
# SECURITY INSPECTION HELPER FUNCTIONS
# ============================================================================


def is_reserved_device_name(
    path_str: str, reserved_names: FrozenSet[str] = RESERVED_DEVICE_NAMES
) -> bool:
    """Checks if any segment in path matches a Windows DOS device name.

    Examples: 'nul', 'con.txt', 'dir/aux.dat', 'COM1' -> True.
    """
    normalized = path_str.replace("\\", "/")
    segments = [s for s in normalized.split("/") if s]
    for seg in segments:
        # Check segment base name without extension
        base = seg.split(".")[0].upper()
        if base in reserved_names:
            return True
        # Check full segment without dot
        if seg.upper() in reserved_names:
            return True
    return False


def has_alternate_data_stream(path_str: str) -> bool:
    """Detects NTFS Alternate Data Stream (ADS) colons in archive member paths.

    Colons in member paths can trigger ADS writes (e.g. 'file.txt:evil.exe') or drive roots.
    """
    return ":" in path_str


def is_prohibited_binary(
    path_str: str, prohibited_exts: FrozenSet[str] = PROHIBITED_BINARY_EXTENSIONS
) -> bool:
    """Checks if file extension is an uninspected executable binary."""
    ext = Path(path_str).suffix.lower()
    return ext in prohibited_exts


def is_symlink_or_reparse(zip_info: zipfile.ZipInfo) -> bool:
    """Detects Unix symlinks or Windows reparse point attributes in a ZipInfo record."""
    # Unix symlink attribute: high 16 bits contain POSIX file mode (S_IFLNK = 0o120000)
    unix_mode = (zip_info.external_attr >> 16) & 0o170000
    if unix_mode == 0o120000:
        return True

    # Windows FILE_ATTRIBUTE_REPARSE_POINT = 0x0400
    # In external_attr, DOS attributes are in the lowest 8 or 16 bits depending on creator system
    if (zip_info.external_attr & 0x0400) != 0:
        return True

    return False

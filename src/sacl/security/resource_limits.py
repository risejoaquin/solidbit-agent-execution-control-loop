"""SACL V1 Resource Quotas & Decompression Bomb Defense Engine.

Implements Threat D1 / TH-11 & Threat D2 / TH-12 mitigations:
- Maximum compressed archive size: 25 MB (26,214,400 bytes)
- Maximum uncompressed extraction size: 100 MB (104,857,600 bytes)
- Maximum total file count: 1,000 files
- Maximum compression ratio: 20:1 (Uncompressed / Compressed)
- Concurrency limits & Non-killing diagnostic timeout invariants
"""

from __future__ import annotations

import zipfile
from dataclasses import dataclass
from typing import Optional

from sacl.contracts.invariants import MAX_ATTACHMENT_SIZE_BYTES
from sacl.security.exceptions import ResourceLimitExceededError, SecurityError

# Canonical Quotas per docs/SECURITY_MODEL.md §4.3 & docs/MAIL_PROTOCOL.md §3.7
DEFAULT_MAX_COMPRESSED_BYTES: int = MAX_ATTACHMENT_SIZE_BYTES  # 25 MB = 26,214,400 bytes
DEFAULT_MAX_UNCOMPRESSED_BYTES: int = 104_857_600  # 100 MB = 104,857,600 bytes
DEFAULT_MAX_TOTAL_FILE_COUNT: int = 1000  # 1,000 files
DEFAULT_MAX_COMPRESSION_RATIO: float = 20.0  # 20:1 ratio


@dataclass(frozen=True)
class ResourceQuotas:
    """Resource quotas enforced during archive admission and decompression."""

    max_compressed_bytes: int = DEFAULT_MAX_COMPRESSED_BYTES
    max_uncompressed_bytes: int = DEFAULT_MAX_UNCOMPRESSED_BYTES
    max_file_count: int = DEFAULT_MAX_TOTAL_FILE_COUNT
    max_compression_ratio: float = DEFAULT_MAX_COMPRESSION_RATIO


class ResourceLimitValidator:
    """Enforces zip bomb and resource exhaustion limits on archives."""

    def __init__(self, quotas: Optional[ResourceQuotas] = None) -> None:
        self.quotas = quotas or ResourceQuotas()

    def validate_archive_metadata(
        self,
        zf: zipfile.ZipFile,
        compressed_size: int,
        package_id: str = "unknown",
    ) -> None:
        """Inspects zipfile metadata against resource exhaustion quotas before extraction."""
        # Check compressed size
        if compressed_size > self.quotas.max_compressed_bytes:
            raise ResourceLimitExceededError(
                package_id=package_id,
                metric="compressed_size_bytes",
                actual=compressed_size,
                limit=self.quotas.max_compressed_bytes,
            )

        infolist = zf.infolist()

        # Check total file count
        if len(infolist) > self.quotas.max_file_count:
            raise ResourceLimitExceededError(
                package_id=package_id,
                metric="total_file_count",
                actual=len(infolist),
                limit=self.quotas.max_file_count,
            )

        # Check total uncompressed size
        total_uncompressed = sum(info.file_size for info in infolist)
        if total_uncompressed > self.quotas.max_uncompressed_bytes:
            raise ResourceLimitExceededError(
                package_id=package_id,
                metric="uncompressed_size_bytes",
                actual=total_uncompressed,
                limit=self.quotas.max_uncompressed_bytes,
            )

        # Check compression ratio
        if compressed_size > 0:
            ratio = total_uncompressed / float(compressed_size)
            if ratio > self.quotas.max_compression_ratio:
                raise ResourceLimitExceededError(
                    package_id=package_id,
                    metric="compression_ratio",
                    actual=round(ratio, 2),
                    limit=self.quotas.max_compression_ratio,
                )


class StreamingExtractionBudgetTracker:
    """Tracks byte budget during stream extraction to prevent mid-stream zip bombs."""

    def __init__(
        self,
        max_total_bytes: int = DEFAULT_MAX_UNCOMPRESSED_BYTES,
        package_id: str = "unknown",
    ) -> None:
        self.max_total_bytes = max_total_bytes
        self.package_id = package_id
        self.total_bytes_extracted: int = 0

    def add_bytes(self, count: int) -> None:
        """Adds extracted byte count and raises if budget exceeded."""
        self.total_bytes_extracted += count
        if self.total_bytes_extracted > self.max_total_bytes:
            raise ResourceLimitExceededError(
                package_id=self.package_id,
                metric="uncompressed_size_bytes",
                actual=self.total_bytes_extracted,
                limit=self.max_total_bytes,
            )


def assert_concurrency_within_limit(
    active_count: int,
    max_parallel: int,
    stage_id: str = "unknown",
) -> None:
    """Enforces host CPU/RAM concurrency throttling limits (Threat D2 / TH-12)."""
    if active_count >= max_parallel:
        raise SecurityError(
            f"CONCURRENCY_LIMIT_REACHED: Stage '{stage_id}' active workers ({active_count}) "
            f"reached MaxParallel ({max_parallel}). Queuing/throttling required.",
            details={
                "active_count": active_count,
                "max_parallel": max_parallel,
                "stage_id": stage_id,
            },
        )


def assert_timeout_non_killing(status: str) -> None:
    """Asserts adherence to the Non-Killing Diagnostic Timeout Invariant.

    When an agent worker exceeds its timeout, it must transition to TIMEOUT_RUNNING
    and remain alive for developer inspection. It must NOT be automatically killed.
    """
    if status == "STOPPED" or status == "KILLED":
        raise SecurityError(
            "NON_KILLING_TIMEOUT_VIOLATION: Automated process termination on timeout is strictly prohibited. "
            "Worker must transition to TIMEOUT_RUNNING and remain unmolested.",
            details={"prohibited_status": status},
        )

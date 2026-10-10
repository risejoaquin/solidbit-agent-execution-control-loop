"""Unit tests for SACL V1 Resource Limits & Zip Bomb Quota Defenses."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
import pytest

from sacl.security.exceptions import ResourceLimitExceededError, SecurityError
from sacl.security.resource_limits import (
    DEFAULT_MAX_COMPRESSED_BYTES,
    DEFAULT_MAX_COMPRESSION_RATIO,
    DEFAULT_MAX_TOTAL_FILE_COUNT,
    DEFAULT_MAX_UNCOMPRESSED_BYTES,
    ResourceLimitValidator,
    ResourceQuotas,
    StreamingExtractionBudgetTracker,
    assert_concurrency_within_limit,
    assert_timeout_non_killing,
)


def build_in_memory_zip(entries: dict[str, bytes]) -> tuple[bytes, zipfile.ZipFile]:
    """Helper to construct in-memory ZipFile and raw bytes."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, content in entries.items():
            zf.writestr(name, content)
    raw = buf.getvalue()
    return raw, zipfile.ZipFile(io.BytesIO(raw), "r")


class TestResourceLimitQuotas:
    """Tests archive quota validation against zip bomb attacks (Threat D1 / TH-11)."""

    def test_default_quota_constants(self) -> None:
        assert DEFAULT_MAX_COMPRESSED_BYTES == 26_214_400      # 25 MB
        assert DEFAULT_MAX_UNCOMPRESSED_BYTES == 104_857_600   # 100 MB
        assert DEFAULT_MAX_TOTAL_FILE_COUNT == 1000            # 1,000 files
        assert DEFAULT_MAX_COMPRESSION_RATIO == 20.0           # 20:1 ratio

    def test_exceeding_compressed_size_limit_fails(self) -> None:
        quotas = ResourceQuotas(max_compressed_bytes=100)
        validator = ResourceLimitValidator(quotas)
        raw, zf = build_in_memory_zip({"file.txt": b"A" * 50})

        with pytest.raises(ResourceLimitExceededError) as exc_info:
            validator.validate_archive_metadata(zf, compressed_size=150, package_id="PKG-01")
        assert exc_info.value.metric == "compressed_size_bytes"

    def test_exceeding_file_count_fails(self) -> None:
        quotas = ResourceQuotas(max_file_count=5)
        validator = ResourceLimitValidator(quotas)
        entries = {f"file_{i}.txt": b"content" for i in range(10)}
        raw, zf = build_in_memory_zip(entries)

        with pytest.raises(ResourceLimitExceededError) as exc_info:
            validator.validate_archive_metadata(zf, compressed_size=len(raw), package_id="PKG-02")
        assert exc_info.value.metric == "total_file_count"
        assert exc_info.value.actual == 10
        assert exc_info.value.limit == 5

    def test_exceeding_uncompressed_size_fails(self) -> None:
        quotas = ResourceQuotas(max_uncompressed_bytes=500)
        validator = ResourceLimitValidator(quotas)
        raw, zf = build_in_memory_zip({"large.txt": b"X" * 1000})

        with pytest.raises(ResourceLimitExceededError) as exc_info:
            validator.validate_archive_metadata(zf, compressed_size=len(raw), package_id="PKG-03")
        assert exc_info.value.metric == "uncompressed_size_bytes"
        assert exc_info.value.actual >= 1000

    def test_exceeding_compression_ratio_fails(self) -> None:
        # High repetition compresses heavily e.g. 50,000 bytes compresses to ~60 bytes (ratio > 800)
        quotas = ResourceQuotas(max_compression_ratio=10.0, max_uncompressed_bytes=100_000)
        validator = ResourceLimitValidator(quotas)
        raw, zf = build_in_memory_zip({"repetitive.txt": b"0" * 40_000})

        with pytest.raises(ResourceLimitExceededError) as exc_info:
            validator.validate_archive_metadata(zf, compressed_size=len(raw), package_id="PKG-04")
        assert exc_info.value.metric == "compression_ratio"

    def test_valid_archive_within_quotas_passes(self) -> None:
        validator = ResourceLimitValidator()
        raw, zf = build_in_memory_zip({
            "manifest.json": b'{"schema": "solidbit.execution-package.v1"}',
            "readme.md": b"# Test Package",
        })
        # Should not raise
        validator.validate_archive_metadata(zf, compressed_size=len(raw), package_id="VALID-PKG")


class TestStreamingBudgetTracker:
    """Tests runtime extraction tracking preventing mid-stream zip bombs."""

    def test_budget_within_limit_passes(self) -> None:
        tracker = StreamingExtractionBudgetTracker(max_total_bytes=1000)
        tracker.add_bytes(500)
        tracker.add_bytes(400)
        assert tracker.total_bytes_extracted == 900

    def test_budget_exceeded_raises_immediately(self) -> None:
        tracker = StreamingExtractionBudgetTracker(max_total_bytes=1000)
        tracker.add_bytes(500)
        with pytest.raises(ResourceLimitExceededError) as exc_info:
            tracker.add_bytes(600)
        assert exc_info.value.metric == "uncompressed_size_bytes"


class TestConcurrencyAndTimeoutInvariants:
    """Tests concurrency throttling and non-killing timeout invariants (Threat D2 / TH-12)."""

    def test_concurrency_within_limit_passes(self) -> None:
        # Should not raise
        assert_concurrency_within_limit(active_count=2, max_parallel=4, stage_id="stage-1")

    def test_concurrency_limit_reached_raises_security_error(self) -> None:
        with pytest.raises(SecurityError) as exc_info:
            assert_concurrency_within_limit(active_count=4, max_parallel=4, stage_id="stage-1")
        assert "CONCURRENCY_LIMIT_REACHED" in str(exc_info.value)

    def test_non_killing_timeout_permits_timeout_running(self) -> None:
        # TIMEOUT_RUNNING status is permitted
        assert_timeout_non_killing(status="TIMEOUT_RUNNING")

    def test_non_killing_timeout_prohibits_auto_stop_or_kill(self) -> None:
        with pytest.raises(SecurityError) as exc_info:
            assert_timeout_non_killing(status="STOPPED")
        assert "NON_KILLING_TIMEOUT_VIOLATION" in str(exc_info.value)

        with pytest.raises(SecurityError):
            assert_timeout_non_killing(status="KILLED")

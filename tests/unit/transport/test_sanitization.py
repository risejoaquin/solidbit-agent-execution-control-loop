"""Tests for ZipDefenseExtractor 4-Stage Security Pipeline."""

from __future__ import annotations

import io
from pathlib import Path
import zipfile
import pytest

from sacl.transport.exceptions import (
    InvalidFilenameError,
    SymlinkNotPermittedError,
    ZipPathTraversalError,
    ZipResourceLimitExceededError,
)
from sacl.transport.sanitization import ZipDefenseExtractor


def create_in_memory_zip(files: dict[str, bytes]) -> bytes:
    """Helper to build in-memory zip bytes."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for fname, content in files.items():
            zf.writestr(fname, content)
    return buf.getvalue()


def test_valid_zip_extraction(tmp_path: Path) -> None:
    extractor = ZipDefenseExtractor()
    zip_bytes = create_in_memory_zip({
        "manifest.json": b'{"package_id": "W0"}',
        "prompts/agent.md": b"# Prompt instructions",
    })

    dest = tmp_path / "extracted"
    extracted = extractor.validate_and_extract(zip_bytes, dest, package_id="W0")
    assert len(extracted) == 2
    assert (dest / "manifest.json").exists()
    assert (dest / "prompts" / "agent.md").exists()
    assert (dest / "manifest.json").read_bytes() == b'{"package_id": "W0"}'


def test_step1_resource_quotas_file_count(tmp_path: Path) -> None:
    extractor = ZipDefenseExtractor(max_file_count=5)
    files = {f"file_{i}.txt": b"content" for i in range(10)}
    zip_bytes = create_in_memory_zip(files)

    with pytest.raises(ZipResourceLimitExceededError) as exc_info:
        extractor.validate_and_extract(zip_bytes, tmp_path / "out", package_id="W0")
    assert exc_info.value.metric == "total_file_count"


def test_step1_resource_quotas_uncompressed_size(tmp_path: Path) -> None:
    extractor = ZipDefenseExtractor(max_uncompressed_bytes=100)
    zip_bytes = create_in_memory_zip({"large.txt": b"A" * 500})

    with pytest.raises(ZipResourceLimitExceededError) as exc_info:
        extractor.validate_and_extract(zip_bytes, tmp_path / "out", package_id="W0")
    assert exc_info.value.metric == "uncompressed_size_bytes"


def test_step1_resource_quotas_compression_ratio(tmp_path: Path) -> None:
    extractor = ZipDefenseExtractor(max_compression_ratio=5.0)
    # Repeating zeros compress extremely well (e.g. 10000:1)
    zip_bytes = create_in_memory_zip({"zeros.bin": b"\x00" * 100000})

    with pytest.raises(ZipResourceLimitExceededError) as exc_info:
        extractor.validate_and_extract(zip_bytes, tmp_path / "out", package_id="W0")
    assert exc_info.value.metric == "compression_ratio"


def test_step2_anti_zip_slip_relative_path(tmp_path: Path) -> None:
    extractor = ZipDefenseExtractor()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("../evil.txt", b"evil")
    zip_bytes = buf.getvalue()

    with pytest.raises(ZipPathTraversalError) as exc_info:
        extractor.validate_and_extract(zip_bytes, tmp_path / "out", package_id="W0")
    assert "evil.txt" in exc_info.value.entry_name


def test_step2_anti_zip_slip_absolute_path(tmp_path: Path) -> None:
    extractor = ZipDefenseExtractor()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("/etc/passwd", b"root")
    zip_bytes = buf.getvalue()

    with pytest.raises(ZipPathTraversalError):
        extractor.validate_and_extract(zip_bytes, tmp_path / "out", package_id="W0")


def test_step3_windows_dos_device_names(tmp_path: Path) -> None:
    extractor = ZipDefenseExtractor()

    # Prohibited names: CON, PRN, AUX, NUL, COM1..9, LPT1..9
    for prohibited in ["CON.txt", "aux", "NUL.json", "com1.log", "sub/lpt2.dat"]:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr(prohibited, b"test")
        zip_bytes = buf.getvalue()

        with pytest.raises(InvalidFilenameError) as exc_info:
            extractor.validate_and_extract(zip_bytes, tmp_path / "out", package_id="W0")
        assert "DOS_DEVICE_NAME" in exc_info.value.pattern


def test_step3_windows_alternate_data_streams(tmp_path: Path) -> None:
    extractor = ZipDefenseExtractor()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("normal.txt:hidden_stream", b"secret")
    zip_bytes = buf.getvalue()

    with pytest.raises(InvalidFilenameError) as exc_info:
        extractor.validate_and_extract(zip_bytes, tmp_path / "out", package_id="W0")
    assert exc_info.value.pattern == "ALTERNATE_DATA_STREAM_COLON"


def test_step4_symlink_rejection(tmp_path: Path) -> None:
    extractor = ZipDefenseExtractor()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zinfo = zipfile.ZipInfo("symlink_entry")
        # Set Unix symlink attribute mask: 0o120000 in upper 16 bits
        zinfo.external_attr = 0o120777 << 16
        zf.writestr(zinfo, b"/target/path")
    zip_bytes = buf.getvalue()

    with pytest.raises(SymlinkNotPermittedError):
        extractor.validate_and_extract(zip_bytes, tmp_path / "out", package_id="W0")

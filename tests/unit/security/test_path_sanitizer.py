"""Unit tests for SACL V1 Path Sanitization & Anti-Zip Slip Defense."""

from __future__ import annotations

from pathlib import Path
import pytest

from sacl.security.exceptions import (
    InvalidFilenameSecurityError,
    PathTraversalSecurityError,
    SymlinkSecurityError,
)
from sacl.security.path_sanitizer import (
    assert_within_boundary,
    has_alternate_data_stream,
    is_dos_device_name,
    is_symlink_or_reparse,
    normalize_path,
    sanitize_relative_path,
    validate_safe_path,
)


class TestPathNormalization:
    """Tests basic path normalization and relative path sanitization."""

    def test_normalize_path_replaces_backslashes(self) -> None:
        assert normalize_path(r"foo\bar\baz.txt") == "foo/bar/baz.txt"
        assert normalize_path(r"foo\\bar///baz.txt") == "foo/bar/baz.txt"

    def test_sanitize_relative_path_strips_slashes(self) -> None:
        assert sanitize_relative_path("/foo/bar/") == "foo/bar"
        assert sanitize_relative_path("\\foo\\bar\\") == "foo/bar"


class TestAntiZipSlipTraversals:
    """Tests Anti-Zip Slip path traversal detection (Threat T1 / TH-04)."""

    def test_relative_parent_traversal_rejected(self, tmp_path: Path) -> None:
        with pytest.raises(PathTraversalSecurityError):
            validate_safe_path("../../Windows/System32/evil.dll", tmp_path)

        with pytest.raises(PathTraversalSecurityError):
            validate_safe_path("docs/../../evil.bat", tmp_path)

        with pytest.raises(PathTraversalSecurityError):
            validate_safe_path("../evil.sh", tmp_path)

    def test_leading_slash_traversal_rejected(self, tmp_path: Path) -> None:
        with pytest.raises(PathTraversalSecurityError):
            validate_safe_path("/etc/passwd", tmp_path)

        with pytest.raises(PathTraversalSecurityError):
            validate_safe_path(r"\Windows\System32\cmd.exe", tmp_path)

    def test_absolute_drive_letter_rejected(self, tmp_path: Path) -> None:
        with pytest.raises(PathTraversalSecurityError):
            validate_safe_path(r"C:\Windows\System32\malicious.dll", tmp_path)

        with pytest.raises(PathTraversalSecurityError):
            validate_safe_path("D:/payload.exe", tmp_path)

    def test_unc_network_path_rejected(self, tmp_path: Path) -> None:
        with pytest.raises(PathTraversalSecurityError):
            validate_safe_path(r"\\attacker-server\share\evil.ps1", tmp_path)

        with pytest.raises(PathTraversalSecurityError):
            validate_safe_path("//attacker-server/share/evil.ps1", tmp_path)

    def test_valid_safe_paths_succeed(self, tmp_path: Path) -> None:
        target = validate_safe_path("prompts/task.md", tmp_path)
        assert target == (tmp_path / "prompts" / "task.md").resolve()

        target2 = validate_safe_path("schemas/v1/spec.json", tmp_path)
        assert target2 == (tmp_path / "schemas" / "v1" / "spec.json").resolve()


class TestWindowsDOSDeviceNames:
    """Tests rejection of prohibited Windows reserved DOS device names."""

    @pytest.mark.parametrize("dev_name", [
        "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
        "con", "prn", "aux", "nul", "com1", "lpt1",
    ])
    def test_dos_device_names_detected(self, dev_name: str) -> None:
        assert is_dos_device_name(dev_name) is True
        assert is_dos_device_name(f"{dev_name}.txt") is True
        assert is_dos_device_name(f"{dev_name}.json") is True

    def test_dos_device_in_path_raises_invalid_filename(self, tmp_path: Path) -> None:
        with pytest.raises(InvalidFilenameSecurityError) as exc_info:
            validate_safe_path("sub/CON.txt", tmp_path)
        assert "DOS_DEVICE_NAME" in exc_info.value.message

        with pytest.raises(InvalidFilenameSecurityError):
            validate_safe_path("NUL", tmp_path)

        with pytest.raises(InvalidFilenameSecurityError):
            validate_safe_path("nested/com1.dat", tmp_path)


class TestNTFSAlternateDataStreams:
    """Tests rejection of NTFS Alternate Data Streams containing colons."""

    def test_colon_in_segment_detected(self) -> None:
        assert has_alternate_data_stream("file.txt:stream") is True
        assert has_alternate_data_stream("test:hidden") is True
        assert has_alternate_data_stream("normal_file.txt") is False

    def test_colon_in_path_raises_invalid_filename(self, tmp_path: Path) -> None:
        with pytest.raises(InvalidFilenameSecurityError) as exc_info:
            validate_safe_path("script.ps1:hidden_stream", tmp_path)
        assert "ALTERNATE_DATA_STREAM_COLON" in exc_info.value.message


class TestSymlinksAndReparsePoints:
    """Tests rejection of Unix symlinks and Windows reparse points."""

    def test_unix_symlink_detected(self) -> None:
        # S_IFLNK is 0o120000 in top 16 bits
        unix_symlink_attr = 0o120000 << 16
        assert is_symlink_or_reparse(unix_symlink_attr) is True

    def test_windows_reparse_point_detected(self) -> None:
        # 0x0400 in lower 16 bits
        win_reparse_attr = 0x0400
        assert is_symlink_or_reparse(win_reparse_attr) is True

    def test_symlink_in_archive_raises_symlink_error(self, tmp_path: Path) -> None:
        unix_symlink_attr = 0o120000 << 16
        with pytest.raises(SymlinkSecurityError):
            validate_safe_path("link_to_root", tmp_path, external_attr=unix_symlink_attr)


class TestBoundaryAssertion:
    """Tests assert_within_boundary helper."""

    def test_within_boundary_succeeds(self, tmp_path: Path) -> None:
        child = tmp_path / "sub" / "file.txt"
        assert assert_within_boundary(child, tmp_path) == child.resolve()

    def test_outside_boundary_fails(self, tmp_path: Path) -> None:
        outside = tmp_path.parent / "escape.txt"
        with pytest.raises(PathTraversalSecurityError):
            assert_within_boundary(outside, tmp_path)

"""T42: ZIP destination collisions are rejected before manifest parsing."""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from sacl.package.archive_names import find_ambiguous_member
from sacl.package.exceptions import InvalidFilenameError
from sacl.package.validator import PackageValidator


def _zip(tmp_path: Path, names: list[str]) -> Path:
    path = tmp_path / "package.zip"
    with zipfile.ZipFile(path, "w") as zf:
        for name in names:
            zf.writestr(name, b"{}" if name.endswith("manifest.json") else b"data")
    return path


@pytest.mark.parametrize("names", [
    ["manifest.json", "manifest.json"],
    ["assets/file.txt", "assets/file.txt"],
    ["assets/file.txt", "ASSETS/FILE.TXT"],
    ["assets/file.txt", r"assets\file.txt"],
    ["assets/file.txt", "assets/./file.txt"],
    ["assets/", "assets"],
    ["docs/", "DOCS/"],
])
def test_colliding_destinations_fail_closed(tmp_path: Path, names: list[str]) -> None:
    archive = _zip(tmp_path, names)
    with zipfile.ZipFile(archive) as zf:
        assert find_ambiguous_member(zf.infolist()) is not None
    with pytest.raises(InvalidFilenameError):
        PackageValidator().validate_archive(archive)


def test_unique_members_are_not_flagged(tmp_path: Path) -> None:
    archive = _zip(tmp_path, ["manifest.json", "assets/a.txt", "assets/b.txt", "docs/"])
    with zipfile.ZipFile(archive) as zf:
        assert find_ambiguous_member(zf.infolist()) is None


def test_unique_valid_manifest_still_passes(tmp_path: Path) -> None:
    sample = Path(__file__).resolve().parents[3] / "examples" / "manifest.valid.json"
    manifest = json.loads(sample.read_text(encoding="utf-8"))
    archive = tmp_path / "valid.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("manifest.json", json.dumps(manifest))
        zf.writestr("assets/data.txt", "data")
    assert PackageValidator().validate_archive(archive).package_id == manifest["package_id"]

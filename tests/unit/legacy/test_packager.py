"""Unit tests for SACL V1 Wave ZIP Packager and Verifier."""

from __future__ import annotations

import json
from pathlib import Path
import zipfile
import pytest

from sacl.legacy.packager import WaveZipPackager


@pytest.fixture
def packager():
    return WaveZipPackager()


@pytest.fixture
def sample_package_dir(tmp_path):
    pkg_dir = tmp_path / "sample_pkg"
    pkg_dir.mkdir()

    manifest_data = {
        "schema": "solidbit.execution-package.v1",
        "package_id": "TEST-WAVE-v1",
        "job_id": "job-test-1",
        "project": "solidbit-agent-execution-control-loop",
        "repository": "risejoaquin/solidbit-agent-execution-control-loop",
        "mode": "isolated_branch_development",
        "source_orchestrator": "C:\\src",
        "target_local_repo": "C:\\tgt",
        "agents": ["AG-1"],
        "entrypoint": "RUN-WAVE.ps1",
        "execution_plan": "EXECUTION_PLAN.md",
        "readme": "README.md",
        "requested_operations": ["op:worker-governed-execution"],
        "prohibited_actions": ["merge"],
        "expected_outputs": ["SUMMARY.md", "SUMMARY.json"],
        "runtime_files": ["RUN-WAVE.ps1"],
    }
    with open(pkg_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest_data, f)

    (pkg_dir / "README.md").write_text("# Readme", encoding="utf-8")
    (pkg_dir / "EXECUTION_PLAN.md").write_text("# Plan", encoding="utf-8")
    (pkg_dir / "RUN-WAVE.ps1").write_text("# Runner", encoding="utf-8")
    prompts_dir = pkg_dir / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "AG-1.md").write_text("Hello AG-1", encoding="utf-8")

    return pkg_dir


def test_create_checksums_file(packager, sample_package_dir):
    cs_file = packager.create_checksums_file(sample_package_dir)
    assert cs_file.exists()
    content = cs_file.read_text(encoding="utf-8")
    assert "manifest.json" in content
    assert "README.md" in content


def test_package_and_verify_wave_dir(packager, sample_package_dir, tmp_path):
    out_zip = tmp_path / "test-wave.zip"
    created = packager.package_wave_dir(sample_package_dir, out_zip, generate_checksums=True)
    assert created.exists()
    assert zipfile.is_zipfile(created)

    is_valid, errors = packager.verify_wave_package(created)
    assert is_valid, f"Verification failed with errors: {errors}"
    assert len(errors) == 0


def test_verify_tampered_wave_package(packager, sample_package_dir, tmp_path):
    out_zip = tmp_path / "tampered-wave.zip"
    packager.package_wave_dir(sample_package_dir, out_zip, generate_checksums=True)

    # Tamper with the zip by replacing README.md with different content
    tampered_zip = tmp_path / "tampered-wave-corrupted.zip"
    with zipfile.ZipFile(out_zip, "r") as zin:
        with zipfile.ZipFile(tampered_zip, "w") as zout:
            for item in zin.infolist():
                if item.filename == "README.md":
                    zout.writestr("README.md", "TAMPERED_CONTENT")
                else:
                    zout.writestr(item, zin.read(item.filename))

    is_valid, errors = packager.verify_wave_package(tampered_zip)
    assert not is_valid
    assert any("SHA-256 mismatch" in e for e in errors)


def test_extract_wave_package_safe(packager, sample_package_dir, tmp_path):
    out_zip = tmp_path / "extract-test.zip"
    packager.package_wave_dir(sample_package_dir, out_zip)

    dest_dir = tmp_path / "extracted"
    extracted = packager.extract_wave_package(out_zip, dest_dir)
    assert len(extracted) >= 4
    assert (dest_dir / "manifest.json").exists()
    assert (dest_dir / "prompts" / "AG-1.md").exists()

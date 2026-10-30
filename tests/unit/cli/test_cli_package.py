"""Unit tests for SACL V1 CLI package command."""

from __future__ import annotations

import json

import pytest

from sacl.cli.main import main


@pytest.fixture
def sample_package_folder(tmp_path):
    pkg_dir = tmp_path / "pkg_src"
    pkg_dir.mkdir()

    manifest_data = {
        "schema": "solidbit.execution-package.v1",
        "package_id": "CLI-PKG-v1",
        "job_id": "job-clipkg-1",
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
    return pkg_dir


def test_cli_package_create_and_verify(sample_package_folder, tmp_path, capsys):
    out_zip = tmp_path / "created.zip"
    code = main(["package", "create", str(sample_package_folder), "--output", str(out_zip)])
    assert code == 0
    captured = capsys.readouterr()
    assert "[SUCCESS] Wave package created" in captured.out
    assert out_zip.exists()

    code_verify = main(["package", "verify", str(out_zip)])
    assert code_verify == 0
    captured_verify = capsys.readouterr()
    assert "[PASS] Package verified successfully" in captured_verify.out


def test_cli_package_extract(sample_package_folder, tmp_path, capsys):
    out_zip = tmp_path / "created.zip"
    main(["package", "create", str(sample_package_folder), "--output", str(out_zip)])

    dest_dir = tmp_path / "unzipped"
    code_ext = main(["package", "extract", str(out_zip), str(dest_dir)])
    assert code_ext == 0
    captured = capsys.readouterr()
    assert "[SUCCESS] Extracted" in captured.out
    assert (dest_dir / "manifest.json").exists()

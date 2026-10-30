"""Unit tests for SACL V1 CLI launch command."""

from __future__ import annotations

import json

import pytest

from sacl.cli.main import main


@pytest.fixture
def mock_wave(tmp_path):
    pkg_dir = tmp_path / "mock_wave"
    pkg_dir.mkdir()

    manifest_data = {
        "schema": "solidbit.execution-package.v1",
        "package_id": "CLI-TEST-v1",
        "job_id": "job-cli-1",
        "project": "solidbit-agent-execution-control-loop",
        "repository": "risejoaquin/solidbit-agent-execution-control-loop",
        "mode": "isolated_branch_development",
        "source_orchestrator": str(tmp_path),
        "target_local_repo": str(tmp_path),
        "agents": ["AG-CLI-1"],
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
    (prompts_dir / "AG-CLI-1.md").write_text("Prompt {{RUN_DIR}}", encoding="utf-8")

    return pkg_dir


def test_cli_launch_test_mode(mock_wave, capsys):
    code = main(["launch", str(mock_wave), "--test-mode"])
    assert code == 0
    captured = capsys.readouterr()
    assert "SACL WAVE EXECUTION RESULT" in captured.out
    assert "CLI-TEST-v1" in captured.out
    assert "DONE_REVIEW_REQUIRED" in captured.out


def test_cli_launch_missing_package(capsys):
    code = main(["launch"])
    assert code == 1
    captured = capsys.readouterr()
    assert "[ERROR] Missing required wave package path" in captured.err


def test_cli_launch_ack_required(mock_wave, capsys):
    code = main(["launch", str(mock_wave)])
    assert code == 2
    captured = capsys.readouterr()
    assert "[SECURITY REFUSAL]" in captured.err
    assert "ACK_REQUIRED" in captured.err

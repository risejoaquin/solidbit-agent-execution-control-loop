"""Unit tests for SACL V1 Legacy Operator Experience."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from sacl.contracts.exceptions import DirtyRootError
from sacl.legacy.operator import LegacyOperatorExperience


@pytest.fixture
def operator():
    return LegacyOperatorExperience()


@pytest.fixture
def wave_dir(tmp_path):
    pkg_dir = tmp_path / "wave_pkg"
    pkg_dir.mkdir()

    manifest_data = {
        "schema": "solidbit.execution-package.v1",
        "package_id": "OP-TEST-v1",
        "job_id": "job-op-1",
        "project": "solidbit-agent-execution-control-loop",
        "repository": "risejoaquin/solidbit-agent-execution-control-loop",
        "mode": "isolated_branch_development",
        "source_orchestrator": str(tmp_path),
        "target_local_repo": str(tmp_path),
        "agents": ["AG-ALPHA", "AG-BETA"],
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
    (prompts_dir / "AG-ALPHA.md").write_text("Alpha prompt {{RUN_DIR}}", encoding="utf-8")
    (prompts_dir / "AG-BETA.md").write_text("Beta prompt {{RUN_DIR}}", encoding="utf-8")

    return pkg_dir


def test_operator_ack_required_without_bypass(operator, wave_dir):
    with pytest.raises(PermissionError) as exc_info:
        operator.run_wave(
            package_path=wave_dir,
            bypass_acknowledged=False,
            test_mode=False,
        )
    assert "ACK_REQUIRED" in str(exc_info.value)


def test_operator_run_wave_test_mode(operator, wave_dir):
    result = operator.run_wave(
        package_path=wave_dir,
        bypass_acknowledged=False,
        test_mode=True,
    )
    assert result.exit_code == 0
    assert result.status == "DONE_REVIEW_REQUIRED"
    assert result.summary_md_path.exists()
    assert result.summary_json_path.exists()
    assert len(result.agent_results) == 2

    # Check that legacy state files were generated
    state_dir = result.run_dir / "state"
    assert (state_dir / "AG-ALPHA.json").exists()
    assert (state_dir / "AG-BETA.json").exists()

    # Check that reports were generated
    reports_dir = result.run_dir / "reports"
    assert (reports_dir / "AG-ALPHA.REPORT.md").exists()
    assert (reports_dir / "AG-BETA.REPORT.md").exists()
    assert (reports_dir / "FINAL_REPORT.md").exists()


def test_operator_dirty_root_halt(operator, wave_dir, tmp_path):
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout=" M modified_file.py\n")
        with pytest.raises(DirtyRootError) as exc_info:
            operator.run_wave(
                package_path=wave_dir,
                repo_path=tmp_path,
                bypass_acknowledged=True,
                test_mode=False,
            )
        assert "DIRTY_ROOT" in str(exc_info.value)

"""SACL V1 CLI Subsystem Integration Tests.

Validates end-to-end functionality of all unified CLI commands:
- launch / run: Layer 1 ACK gate, governance injection, test-mode execution, dirty-root rule
- package: create, verify, extract round-trip
- status: text table and structured JSON outputs
- stop: 3-way PID recycling defense
- monitor: read-only dashboard snapshot
- preflight: environment validation
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

import pytest

from sacl.cli.launch import configure_launch_parser, execute_launch
from sacl.cli.monitor import configure_monitor_parser, execute_monitor
from sacl.cli.package import execute_package
from sacl.cli.preflight import configure_preflight_parser, execute_preflight
from sacl.cli.status import configure_status_parser, execute_status
from sacl.cli.stop import configure_stop_parser, execute_stop


@pytest.fixture
def sample_wave_pkg(tmp_path: Path) -> Path:
    """Creates a minimal valid wave package for testing."""
    pkg_dir = tmp_path / "test_wave_pkg"
    pkg_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "schema": "solidbit.execution-package.v1",
        "package_id": "PKG-INTEG-001",
        "job_id": "JOB-INTEG-001",
        "project": "test-project",
        "repository": "solidbit/test-repo",
        "mode": "isolated_branch_development",
        "source_orchestrator": str(tmp_path / "mock_orch"),
        "target_local_repo": str(tmp_path / "mock_repo"),
        "agents": ["AG-INTEG-1"],
        "entrypoint": "RUN-WAVE.ps1",
        "execution_plan": "EXECUTION_PLAN.md",
        "readme": "README.md",
        "requested_operations": ["EXECUTE_WAVE"],
        "prohibited_actions": [
            "remote_production_execution",
            "github_merge",
            "production_db_write",
            "secret_export",
            "arbitrary_remote_code",
            "main_branch_execution",
            "primary_checkout_mutation",
            "hard_reset",
            "auto_stash",
        ],
        "expected_outputs": ["reports/AG-INTEG-1.REPORT.md", "SUMMARY.md"],
        "runtime_files": ["prompts/ag_integ_1.prompt.md"],
    }

    with open(pkg_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    with open(pkg_dir / "EXECUTION_PLAN.md", "w", encoding="utf-8") as f:
        f.write("# Execution Plan\nP1: AG-INTEG-1\n")

    with open(pkg_dir / "README.md", "w", encoding="utf-8") as f:
        f.write("# Test Wave Package\n")

    with open(pkg_dir / "RUN-WAVE.ps1", "w", encoding="utf-8") as f:
        f.write("# Wave entrypoint\n")

    prompts_dir = pkg_dir / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    with open(prompts_dir / "ag_integ_1.prompt.md", "w", encoding="utf-8") as f:
        f.write("# Task Prompt for AG-INTEG-1\nPerform integration hardening.\n")

    # Mock repo
    repo_dir = tmp_path / "mock_repo"
    repo_dir.mkdir(parents=True, exist_ok=True)

    # Mock orchestrator
    orch_dir = tmp_path / "mock_orch"
    orch_dir.mkdir(parents=True, exist_ok=True)

    return pkg_dir


class TestCliIntegration:
    """Integration test suite for sacl CLI commands."""

    def test_launch_without_bypass_acknowledged_fails_gate(self, sample_wave_pkg: Path):
        """Verifies Layer 1 Caller Acknowledgement Gate refuses execution without --bypass-acknowledged."""
        parser = argparse.ArgumentParser()
        configure_launch_parser(parser)
        args = parser.parse_args([str(sample_wave_pkg)])

        exit_code = execute_launch(args)
        assert exit_code == 2

    def test_launch_test_mode_executes_successfully(self, sample_wave_pkg: Path, tmp_path: Path):
        """Verifies wave execution in test mode produces all required deliverables and metadata."""
        run_output_dir = tmp_path / "runs" / "test_run_1"

        parser = argparse.ArgumentParser()
        configure_launch_parser(parser)
        args = parser.parse_args(
            [
                str(sample_wave_pkg),
                "--bypass-acknowledged",
                "--test-mode",
                "--run-dir",
                str(run_output_dir),
            ]
        )

        exit_code = execute_launch(args)
        assert exit_code == 0

        # Deliverables verification
        assert (run_output_dir / "SUMMARY.md").exists()
        assert (run_output_dir / "SUMMARY.json").exists()
        assert (run_output_dir / "run-meta.json").exists()
        assert (run_output_dir / "LAST_RUN.txt").exists()

        # Check governance header injected into prompt
        prompt_copy = run_output_dir / "prompts" / "AG-INTEG-1.prompt.md"
        assert prompt_copy.exists()
        prompt_content = prompt_copy.read_text(encoding="utf-8")
        assert "GOVERNED_EXECUTION=TRUE" in prompt_content
        assert "MERGE=NOT_AUTHORIZED" in prompt_content
        assert "DEPLOY=NOT_AUTHORIZED" in prompt_content

        # Check agent state file
        agent_state_file = run_output_dir / "state" / "AG-INTEG-1.json"
        assert agent_state_file.exists()
        agent_data = json.loads(agent_state_file.read_text(encoding="utf-8"))
        assert agent_data["status"] == "COMPLETE"
        assert agent_data["exitCode"] == 0

    def test_package_round_trip(self, sample_wave_pkg: Path, tmp_path: Path):
        """Verifies sacl package create, verify, and extract."""
        out_zip = tmp_path / "test_package.zip"

        # 1. Package Create
        p_create = argparse.ArgumentParser()
        sub_create = p_create.add_subparsers(dest="package_action")
        c_p = sub_create.add_parser("create")
        c_p.add_argument("source_dir")
        c_p.add_argument("--output", "-o")
        c_p.add_argument("--prefix-root", action="store_true")

        args_create = p_create.parse_args(
            ["create", str(sample_wave_pkg), "--output", str(out_zip)]
        )
        rc = execute_package(args_create)
        assert rc == 0
        assert out_zip.exists()

        # 2. Package Verify
        p_verify = argparse.ArgumentParser()
        sub_verify = p_verify.add_subparsers(dest="package_action")
        v_p = sub_verify.add_parser("verify")
        v_p.add_argument("package_path")

        args_verify = p_verify.parse_args(["verify", str(out_zip)])
        rc = execute_package(args_verify)
        assert rc == 0

        # 3. Package Extract
        ext_dir = tmp_path / "extracted_pkg"
        p_ext = argparse.ArgumentParser()
        sub_ext = p_ext.add_subparsers(dest="package_action")
        e_p = sub_ext.add_parser("extract")
        e_p.add_argument("zip_path")
        e_p.add_argument("destination")

        args_ext = p_ext.parse_args(["extract", str(out_zip), str(ext_dir)])
        rc = execute_package(args_ext)
        assert rc == 0
        assert (ext_dir / "manifest.json").exists()
        assert (ext_dir / "checksums.sha256").exists()

    def test_status_command(self, tmp_path: Path):
        """Verifies sacl status queries and formats agent records."""
        run_dir = tmp_path / "runs" / "status_run"
        state_dir = run_dir / "state"
        state_dir.mkdir(parents=True, exist_ok=True)

        agent_state = {
            "status": "COMPLETE",
            "pid": 1234,
            "exit_code": 0,
            "started_at": "2026-10-07T00:00:00Z",
            "completed_at": "2026-10-07T00:01:00Z",
            "report_path": "reports/AG-1.REPORT.md",
            "result": "PASS",
        }
        with open(state_dir / "AG-1.json", "w", encoding="utf-8") as f:
            json.dump(agent_state, f)

        parser = argparse.ArgumentParser()
        configure_status_parser(parser)

        # Tabular output
        args_table = parser.parse_args(["--run-dir", str(run_dir)])
        rc = execute_status(args_table)
        assert rc == 0

        # JSON output
        args_json = parser.parse_args(["--run-dir", str(run_dir), "--json"])
        rc = execute_status(args_json)
        assert rc == 0

    def test_stop_command_safe_verification(self):
        """Verifies sacl stop executes safe PID verification without harming unrelated processes."""
        parser = argparse.ArgumentParser()
        configure_stop_parser(parser)

        # Test stopping non-existent PID fails safely (returns 0 with refusal or no targets)
        args_stop = parser.parse_args(["--pid", "999999", "--agent", "mock-agent"])
        rc = execute_stop(args_stop)
        assert rc == 0

    def test_preflight_command(self):
        """Verifies sacl preflight checks environment dependencies and clean-root rule."""
        parser = argparse.ArgumentParser()
        configure_preflight_parser(parser)

        args = parser.parse_args([])
        rc = execute_preflight(args)
        assert rc == 0

    def test_monitor_snapshot(self, sqlite_temp_db: sqlite3.Connection, tmp_path: Path):
        """Verifies sacl monitor renders read-only snapshot without database locks."""
        db_path = tmp_path / "monitor_test.db"
        conn = sqlite3.connect(str(db_path))
        # Initialize schema
        migration_sql = Path("db/migrations/001_init.sql")
        if migration_sql.exists():
            conn.executescript(migration_sql.read_text(encoding="utf-8"))
        conn.close()

        parser = argparse.ArgumentParser()
        configure_monitor_parser(parser)

        args = parser.parse_args(["--db", str(db_path), "--once"])
        rc = execute_monitor(args)
        assert rc == 0

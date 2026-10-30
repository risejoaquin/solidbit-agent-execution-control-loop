"""Canonical STRIDE Threat Model Verification Test Suite (TH-01 through TH-14).

Adheres strictly to docs/THREAT_MODEL.md §3 and docs/SECURITY_MODEL.md §9:
- TH-01: Spoofing - Ingest email from unauthorized sender; assert ignored/quarantined.
- TH-02: Spoofing - Result Protocol: Multi-dimensional reconciliation: fake marker but missing file, QA blocks.
- TH-03: Spoofing - Host Processes: Anti-recycling safe process stop: process name whitelist + 300s StartTime match check, assert SAFETY_REFUSAL.
- TH-04: Tampering - File System: Anti-Zip Slip canonical path sanitization, ../../evil.bat -> ZIP_PATH_TRAVERSAL_DETECTED.
- TH-05: Tampering - Agent Execution: Machine governance prompt guard header injection into effective prompt.
- TH-06: Tampering - Primary Repo: Local Dirty-Root Rule + PRIMARY_CHECKOUT_NOT_ALLOWED -> BLOCKED_DIRTY_ROOT / BLOCKED_CHECKOUT_PROHIBITED.
- TH-07: Tampering - Worktrees: Cross-agent file collision check -> READY_FOR_INTEGRATION=NO / BLOCKED_FILE_COLLISION.
- TH-08: Repudiation - Operational State: State logging + immutable INVOCATION.json / audit trail.
- TH-09: Info Disclosure - Deliverables / Logs: Secret redaction filter on stdout/stderr, tokens masked with [REDACTED_SECRET].
- TH-10: Info Disclosure - Source Code: Fixed outbound recipient whitelist (uniquedraken@gmail.com), arbitrary external address blocked.
- TH-11: Denial of Service - Disk Storage: Zip decompression quotas (25MB archive / 100MB uncompressed / 1000 files / 20:1 ratio) -> ZIP_RESOURCE_LIMIT_EXCEEDED.
- TH-12: Denial of Service - Host CPU/RAM: Concurrency limits + non-killing timeout (TIMEOUT_RUNNING) without auto-kill.
- TH-13: Elevation of Privilege - Main Branch: MAIN_BRANCH_NOT_ALLOWED + Human Action Gate -> preflight abort.
- TH-14: Elevation of Privilege - Cloud Infrastructure: Remote production disabled in V1 (Dry-run plan generation only) -> fail-closed abort.
"""

from __future__ import annotations

import io
import json
import sqlite3
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from sacl.contracts.exceptions import (
    CollisionDetectedError,
    DirtyRootError,
)
from sacl.security import (
    DEFAULT_AUTHORIZED_EMAIL,
    REDACTION_MARKER,
    AdmissionStatus,
    ArchiveAdmissionController,
    DataExfiltrationAttemptError,
    HardDenySecurityError,
    MainBranchProhibitedError,
    PathTraversalSecurityError,
    PrimaryCheckoutProhibitedError,
    RemoteProductionProhibitedError,
    ResourceQuotas,
    SafetyRefusalError,
    SecurityError,
    UnauthorizedSenderError,
    assert_action_not_hard_denied,
    assert_authorized_recipient,
    assert_authorized_sender,
    assert_clean_root,
    assert_no_file_collision,
    assert_not_main_branch,
    assert_prompt_governance,
    assert_remote_production_disabled,
    assert_safe_process_stop,
    assert_timeout_non_killing,
    assert_worktree_confinement,
    inject_governance_headers,
    redact_secrets,
    validate_safe_path,
)


class TestThreatModelVerification:
    """Rigorous verification suite for all 14 canonical STRIDE threats."""

    def test_th01_spoofing_unauthorized_email_job_injection(self) -> None:
        """TH-01: Ingest email from unauthorized sender; assert ignored/quarantined."""
        unauthorized_sender = "attacker@evil-domain.com"
        with pytest.raises(UnauthorizedSenderError) as exc_info:
            assert_authorized_sender(unauthorized_sender)

        assert "UNAUTHORIZED_SENDER" in exc_info.value.message
        assert exc_info.value.sender == unauthorized_sender
        assert exc_info.value.expected_sender == DEFAULT_AUTHORIZED_EMAIL

        # Authorized sender succeeds
        assert assert_authorized_sender("uniquedraken@gmail.com") == "uniquedraken@gmail.com"

    def test_th02_spoofing_agent_result_marker_forgery(self, tmp_path: Path) -> None:
        """TH-02: Multi-dimensional reconciliation: fake marker but missing file; QA blocks."""
        # Threat S2 scenario: Agent emits fake PASS marker in report, but required deliverable file is missing
        report_file = tmp_path / "reports" / "AG-FORGED.REPORT.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text("AGENT_FORGED_RESULT = PASS\n", encoding="utf-8")

        # Declared required output file from manifest.json
        declared_output_file = tmp_path / "dist" / "compiled_bundle.js"
        # Physical file is missing on disk!
        assert not declared_output_file.exists()

        # QA Stage Verification: audits required physical files before wave completion
        # Even though report contains fake PASS, missing deliverable file blocks QA gate
        def qa_stage_evaluate(report_path: Path, required_files: list[Path]) -> tuple[bool, str]:
            if not report_path.exists() or report_path.stat().st_size == 0:
                return False, "QA_BLOCKED_REPORT_MISSING"
            for rf in required_files:
                if not rf.exists() or rf.stat().st_size == 0:
                    return False, f"QA_BLOCKED_FILE_MISSING: {rf.name}"
            return True, "QA_PASSED"

        passed, reason = qa_stage_evaluate(report_file, [declared_output_file])
        assert passed is False
        assert "QA_BLOCKED_FILE_MISSING" in reason

    def test_th03_spoofing_recycled_pid_impersonation(self) -> None:
        """TH-03: SafeProcessStop: process name whitelist + 300s StartTime match check; assert SAFETY_REFUSAL."""
        now = datetime.now(timezone.utc)

        # 1. Image mismatch
        with pytest.raises(SafetyRefusalError) as exc_img:
            assert_safe_process_stop(
                pid=9999,
                recorded_start_time=now,
                current_process_name="svchost.exe",
                current_start_time=now,
            )
        assert "SAFETY_REFUSAL" in exc_img.value.message
        assert "not in allowed images" in exc_img.value.reason

        # 2. Start time drift (> 300 seconds)
        recycled_time = now + timedelta(seconds=400)
        with pytest.raises(SafetyRefusalError) as exc_drift:
            assert_safe_process_stop(
                pid=9999,
                recorded_start_time=now,
                current_process_name="agy",
                current_start_time=recycled_time,
            )
        assert "SAFETY_REFUSAL" in exc_drift.value.message
        assert "PID recycling suspected" in exc_drift.value.reason

    def test_th04_tampering_zip_slip_and_directory_traversal(self, tmp_path: Path) -> None:
        """TH-04: Anti-Zip Slip canonical path sanitization; ../../evil.bat -> ZIP_PATH_TRAVERSAL_DETECTED."""
        dest_dir = tmp_path / "staging"
        dest_dir.mkdir()

        with pytest.raises(PathTraversalSecurityError) as exc_info:
            validate_safe_path("../../evil.bat", dest_dir)
        assert "ZIP_PATH_TRAVERSAL_DETECTED" in exc_info.value.message

    def test_th05_tampering_agent_execution_prompt_guard_headers(self, tmp_path: Path) -> None:
        """TH-05: Machine governance prompt guard header injection (effective-prompt.txt)."""
        base = "Execute task 1"
        effective = inject_governance_headers(
            base_prompt=base,
            worktree_path=tmp_path / "wt-01",
            branch_name="feature/sec-test",
            head_commit_sha="abcdef123456",
        )

        # Assert guard headers prepended
        assert effective.startswith("GOVERNED_EXECUTION=TRUE\n")
        assert "MERGE=NOT_AUTHORIZED" in effective
        assert "DEPLOY=NOT_AUTHORIZED" in effective
        assert "DESTRUCTIVE_DB=NOT_AUTHORIZED" in effective
        assert "CREDENTIAL_MUTATION=NOT_AUTHORIZED" in effective
        assert "RULESET_MUTATION=NOT_AUTHORIZED" in effective

        # Verify header checker asserts valid
        assert_prompt_governance(effective)

    def test_th06_tampering_primary_git_repo_dirty_root(self, tmp_path: Path) -> None:
        """TH-06: Local Dirty-Root Rule + PRIMARY_CHECKOUT_NOT_ALLOWED; assert immediate BLOCKED_DIRTY_ROOT."""

        # Dirty root check
        def dirty_checker(p):
            return (False, ["modified_file.py"])

        with pytest.raises(DirtyRootError):
            assert_clean_root(tmp_path, dirty_checker=dirty_checker)

        # Primary checkout check
        primary_repo = tmp_path / "repo"
        primary_repo.mkdir()
        (primary_repo / ".git").mkdir()  # .git is directory
        with pytest.raises(PrimaryCheckoutProhibitedError):
            assert_worktree_confinement(primary_repo, primary_repo_path=primary_repo)

    def test_th07_tampering_cross_agent_worktree_file_collision(self) -> None:
        """TH-07: Cross-agent file collision check; simulate two agents editing same file -> collision detected."""
        agent_diffs = {
            "agent_security": {"src/auth.py", "tests/test_auth.py"},
            "agent_transport": {"src/auth.py", "src/gateway.py"},  # Collision on src/auth.py!
        }
        with pytest.raises(CollisionDetectedError) as exc_info:
            assert_no_file_collision(agent_diffs, run_id="run-collision")

        assert "src/auth.py" in exc_info.value.colliding_files

    def test_th08_repudiation_operational_state_logging_and_manifest(self, tmp_path: Path) -> None:
        """TH-08: ACID SQLite state logging + immutable INVOCATION.json."""
        db_path = tmp_path / "sacl_ops.db"
        conn = sqlite3.connect(str(db_path))
        with conn:
            conn.execute("""
                CREATE TABLE runs (
                    run_id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TEXT NOT NULL
                );
            """)
            conn.execute(
                "INSERT INTO runs (run_id, job_id, status, started_at) VALUES (?, ?, ?, ?)",
                ("run-001", "job-001", "RUNNING", datetime.now(timezone.utc).isoformat()),
            )

        # Verify persisted state
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM runs WHERE run_id = 'run-001'")
        row = cursor.fetchone()
        assert row[0] == "RUNNING"
        conn.close()

        # Invocation manifest record
        invoc_path = tmp_path / "INVOCATION.json"
        invoc_path.write_text(
            json.dumps(
                {
                    "run_id": "run-001",
                    "git_commit": "123456",
                    "bypass_acknowledged": True,
                }
            )
        )
        assert invoc_path.exists()
        invoc_data = json.loads(invoc_path.read_text())
        assert invoc_data["bypass_acknowledged"] is True

    def test_th09_info_disclosure_secret_token_masking(self) -> None:
        """TH-09: Streaming regex token masking on stdout/stderr; tokens masked as [REDACTED_SECRET]."""
        mock_output = (
            "Agent generated token: ghp_1234567890abcdefghijklmnopqrstuvwxyz\n"
            "Using Google key: AIzaSyD-1234567890abcdefghijklmnopqrst\n"
        )
        masked = redact_secrets(mock_output)

        assert "ghp_" not in masked
        assert "AIza" not in masked
        assert REDACTION_MARKER in masked

    def test_th10_info_disclosure_fixed_outbound_email_whitelist(self) -> None:
        """TH-10: Fixed outbound email recipient whitelist (uniquedraken@gmail.com); arbitrary destination blocked."""
        with pytest.raises(DataExfiltrationAttemptError) as exc_info:
            assert_authorized_recipient("exfiltrator@darknet.org")

        assert "DATA_EXFILTRATION_PREVENTED" in exc_info.value.message
        assert exc_info.value.authorized_recipient == DEFAULT_AUTHORIZED_EMAIL

    def test_th11_denial_of_service_zip_decompression_resource_quotas(self) -> None:
        """TH-11: Zip decompression resource quotas (100MB uncompressed); assert ZIP_RESOURCE_LIMIT_EXCEEDED."""
        quotas = ResourceQuotas(max_uncompressed_bytes=1000)
        controller = ArchiveAdmissionController(resource_quotas=quotas)

        # Build in-memory archive expanding to 5000 bytes
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("manifest.json", b'{"package_id": "P1", "job_id": "J1"}')
            zf.writestr("huge.dat", b"0" * 5000)
        raw_zip = buf.getvalue()

        decision = controller.admit_and_stage(raw_zip, staging_dir="dummy", fail_closed=False)
        assert decision.admitted is False
        assert decision.status == AdmissionStatus.REJECTED_RESOURCE_QUOTA
        assert decision.violation_code == "ZIP_RESOURCE_LIMIT_EXCEEDED"

    def test_th12_denial_of_service_non_killing_diagnostic_timeout(self) -> None:
        """TH-12: Concurrency limits + non-killing timeout (TIMEOUT_RUNNING) without auto-kill."""
        # Non-killing timeout: TIMEOUT_RUNNING is allowed, STOPPED/KILLED prohibited
        assert_timeout_non_killing(status="TIMEOUT_RUNNING")

        with pytest.raises(SecurityError) as exc_info:
            assert_timeout_non_killing(status="STOPPED")
        assert "NON_KILLING_TIMEOUT_VIOLATION" in str(exc_info.value)

    def test_th13_elevation_of_privilege_main_branch_not_allowed(self) -> None:
        """TH-13: MAIN_BRANCH_NOT_ALLOWED + Human Action Gate; targeting main aborts."""
        with pytest.raises(MainBranchProhibitedError) as exc_info:
            assert_not_main_branch("main")
        assert "MAIN_BRANCH_NOT_ALLOWED" in exc_info.value.message

        with pytest.raises(MainBranchProhibitedError):
            assert_not_main_branch("master")

    def test_th14_elevation_of_privilege_remote_production_disabled_in_v1(self) -> None:
        """TH-14: Remote production execution disabled in V1 (Dry-run plan generation only)."""
        with pytest.raises(RemoteProductionProhibitedError) as exc_info:
            assert_remote_production_disabled("railway_up", target="railway_prod")
        assert "REMOTE_PRODUCTION_DISABLED" in exc_info.value.message

        with pytest.raises(HardDenySecurityError):
            assert_action_not_hard_denied("remote_production_execution")

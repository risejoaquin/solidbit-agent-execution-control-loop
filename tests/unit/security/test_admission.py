"""Unit tests for SACL V1 Archive Admission Controller."""

from __future__ import annotations

import io
import json
from pathlib import Path
import zipfile
import pytest

from sacl.security.admission import (
    AdmissionDecision,
    AdmissionStatus,
    ArchiveAdmissionController,
)
from sacl.security.exceptions import (
    ArchiveAdmissionError,
    InvalidFilenameSecurityError,
    PathTraversalSecurityError,
    ResourceLimitExceededError,
)
from sacl.security.resource_limits import ResourceQuotas


def create_mock_wave_zip(
    manifest_data: dict,
    extra_files: dict[str, bytes] | None = None,
) -> bytes:
    """Helper to build a valid wave package zip."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest_data).encode("utf-8"))
        if extra_files:
            for fname, content in extra_files.items():
                zf.writestr(fname, content)
    return buf.getvalue()


def get_canonical_manifest() -> dict:
    """Returns valid manifest data conforming to manifest.schema.json."""
    return {
        "schema": "solidbit.execution-package.v1",
        "package_id": "PKG-W0-001",
        "job_id": "JOB-W0-001",
        "project": "SolidBit",
        "repository": "risejoaquin/solidbit-agent-execution-control-loop",
        "mode": "architecture_freeze_and_repo_bootstrap",
        "source_orchestrator": "Stable-Ecommerce-Orchestrator",
        "target_local_repo": "C:/Repos/solidbit",
        "agents": ["AG-SEC"],
        "entrypoint": "main.py",
        "execution_plan": "docs/PLAN.md",
        "readme": "README.md",
        "requested_operations": ["security:audit"],
        "prohibited_actions": ["remote_production_execution"],
        "expected_outputs": ["reports/AG-SEC.REPORT.md"],
        "runtime_files": ["prompts/agent.md"],
    }


class TestArchiveAdmissionController:
    """Tests archive admission inspection and quarantine gates."""

    def test_valid_archive_admission_and_staging(self, tmp_path: Path) -> None:
        manifest = get_canonical_manifest()
        zip_bytes = create_mock_wave_zip(
            manifest_data=manifest,
            extra_files={"prompts/agent.md": b"# Do tasks", "README.md": b"# Docs"},
        )

        controller = ArchiveAdmissionController()
        staging_dir = tmp_path / "staging" / "run-01"

        decision = controller.admit_and_stage(
            archive_source=zip_bytes,
            staging_dir=staging_dir,
            package_id="PKG-W0-001",
        )

        assert decision.admitted is True
        assert decision.status == AdmissionStatus.ADMITTED
        assert decision.job_id == "JOB-W0-001"
        assert decision.package_id == "PKG-W0-001"
        assert len(decision.sha256) == 64
        assert (staging_dir / "manifest.json").exists()
        assert (staging_dir / "prompts" / "agent.md").exists()

    def test_missing_manifest_rejected(self, tmp_path: Path) -> None:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("prompts/agent.md", b"# No manifest here")
        zip_bytes = buf.getvalue()

        controller = ArchiveAdmissionController()
        staging_dir = tmp_path / "staging"

        # Fail-closed raises ArchiveAdmissionError
        with pytest.raises(ArchiveAdmissionError) as exc_info:
            controller.admit_and_stage(zip_bytes, staging_dir, fail_closed=True)
        assert exc_info.value.violation_code == "MANIFEST_MISSING"

        # Non-fail-closed returns rejected decision
        decision = controller.admit_and_stage(zip_bytes, staging_dir, fail_closed=False)
        assert decision.admitted is False
        assert decision.status == AdmissionStatus.REJECTED_MANIFEST_INVALID

    def test_self_authorizing_scripts_rejected(self, tmp_path: Path) -> None:
        manifest = get_canonical_manifest()
        manifest["authorized_scripts"] = ["scripts/run.ps1"]  # Prohibited!
        zip_bytes = create_mock_wave_zip(manifest)

        controller = ArchiveAdmissionController()
        staging_dir = tmp_path / "staging"

        with pytest.raises(ArchiveAdmissionError) as exc_info:
            controller.admit_and_stage(zip_bytes, staging_dir, fail_closed=True)
        assert exc_info.value.violation_code == "SELF_AUTHORIZING_SCRIPTS_PROHIBITED"

        decision = controller.admit_and_stage(zip_bytes, staging_dir, fail_closed=False)
        assert decision.admitted is False
        assert "authorized_scripts" in decision.rejection_reason

    def test_zip_bomb_resource_quota_rejected(self, tmp_path: Path) -> None:
        manifest = get_canonical_manifest()
        # Create archive with total uncompressed size exceeding quota
        quotas = ResourceQuotas(max_uncompressed_bytes=500)
        controller = ArchiveAdmissionController(resource_quotas=quotas)
        zip_bytes = create_mock_wave_zip(manifest, extra_files={"big.txt": b"A" * 1000})

        with pytest.raises(ResourceLimitExceededError):
            controller.admit_and_stage(zip_bytes, tmp_path / "staging", fail_closed=True)

        decision = controller.admit_and_stage(zip_bytes, tmp_path / "staging", fail_closed=False)
        assert decision.admitted is False
        assert decision.status == AdmissionStatus.REJECTED_RESOURCE_QUOTA

    def test_path_traversal_anti_zip_slip_rejected(self, tmp_path: Path) -> None:
        manifest = get_canonical_manifest()
        zip_bytes = create_mock_wave_zip(manifest, extra_files={"../../evil.bat": b"@echo off"})

        controller = ArchiveAdmissionController()
        with pytest.raises(PathTraversalSecurityError):
            controller.admit_and_stage(zip_bytes, tmp_path / "staging", fail_closed=True)

        decision = controller.admit_and_stage(zip_bytes, tmp_path / "staging", fail_closed=False)
        assert decision.admitted is False
        assert decision.status == AdmissionStatus.REJECTED_TRAVERSAL_FAIL

    def test_dos_device_name_rejected(self, tmp_path: Path) -> None:
        manifest = get_canonical_manifest()
        zip_bytes = create_mock_wave_zip(manifest, extra_files={"sub/CON.txt": b"content"})

        controller = ArchiveAdmissionController()
        with pytest.raises(InvalidFilenameSecurityError):
            controller.admit_and_stage(zip_bytes, tmp_path / "staging", fail_closed=True)

        decision = controller.admit_and_stage(zip_bytes, tmp_path / "staging", fail_closed=False)
        assert decision.admitted is False
        assert decision.status == AdmissionStatus.REJECTED_INVALID_FILENAME

    def test_corrupt_archive_rejected(self, tmp_path: Path) -> None:
        controller = ArchiveAdmissionController()
        corrupt_bytes = b"not a zip file at all"

        with pytest.raises(ArchiveAdmissionError):
            controller.admit_and_stage(corrupt_bytes, tmp_path / "staging", fail_closed=True)

        decision = controller.admit_and_stage(corrupt_bytes, tmp_path / "staging", fail_closed=False)
        assert decision.admitted is False
        assert decision.status == AdmissionStatus.REJECTED_CORRUPT_ARCHIVE

    def test_idempotent_duplicate_delivery(self, tmp_path: Path) -> None:
        manifest = get_canonical_manifest()
        zip_bytes = create_mock_wave_zip(manifest)

        # Lookup function simulating existing stored hash identical to incoming
        controller_temp = ArchiveAdmissionController()
        incoming_sha = controller_temp.compute_sha256(zip_bytes)

        existing_lookup = lambda jid: incoming_sha if jid == "JOB-W0-001" else None
        controller = ArchiveAdmissionController(existing_package_lookup=existing_lookup)

        decision = controller.admit_and_stage(zip_bytes, tmp_path / "staging", fail_closed=False)
        assert decision.admitted is True
        assert decision.status == AdmissionStatus.DUPLICATE_IGNORED
        assert decision.sha256 == incoming_sha

    def test_conflicting_hash_delivery_rejected(self, tmp_path: Path) -> None:
        manifest = get_canonical_manifest()
        zip_bytes = create_mock_wave_zip(manifest)

        # Lookup function returning different stored hash
        different_sha = "0" * 64
        existing_lookup = lambda jid: different_sha if jid == "JOB-W0-001" else None
        controller = ArchiveAdmissionController(existing_package_lookup=existing_lookup)

        with pytest.raises(ArchiveAdmissionError) as exc_info:
            controller.admit_and_stage(zip_bytes, tmp_path / "staging", fail_closed=True)
        assert exc_info.value.violation_code == AdmissionStatus.REJECTED_HASH_CONFLICT.value

        decision = controller.admit_and_stage(zip_bytes, tmp_path / "staging", fail_closed=False)
        assert decision.admitted is False
        assert decision.status == AdmissionStatus.REJECTED_HASH_CONFLICT

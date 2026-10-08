"""Unit tests for SACL V1 filesystem evidence store and artifact metadata indexing."""

import hashlib
import json
import sqlite3
from pathlib import Path
import pytest

from sacl.contracts.invariants import HEAVY_ARTIFACTS_ON_FILESYSTEM, ArtifactType
from sacl.observability.evidence import (
    EvidenceRegistry,
    compute_file_sha256,
    infer_artifact_type,
)


def _seed_parent_job_and_run(conn: sqlite3.Connection, job_id: str, run_id: str) -> None:
    """Seeds prerequisite parent job and run rows to satisfy SQLite foreign keys."""
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR IGNORE INTO jobs (job_id, status, created_at, updated_at)
        VALUES (?, 'RUNNING', '2026-10-07T22:00:00Z', '2026-10-07T22:00:00Z')
        """,
        (job_id,),
    )
    cursor.execute(
        """
        INSERT OR IGNORE INTO runs (run_id, job_id, package_id, project, repository, mode, source_orchestrator, target_repo_path, run_dir, status, started_at)
        VALUES (?, ?, 'PKG-1', 'test-proj', 'test-repo', 'test-mode', 'src', 'target', 'runs/test', 'RUNNING', '2026-10-07T22:00:00Z')
        """,
        (run_id, job_id),
    )
    conn.commit()


def test_heavy_artifacts_on_filesystem_invariant():
    """Enforces constitutional rule: heavy artifacts remain strictly in filesystem."""
    assert HEAVY_ARTIFACTS_ON_FILESYSTEM is True


def test_compute_file_sha256(tmp_path: Path):
    """Verifies streaming SHA-256 calculation matches hashlib digest."""
    test_file = tmp_path / "sample.txt"
    content = b"The quick brown fox jumps over the lazy dog"
    test_file.write_bytes(content)

    expected_hash = hashlib.sha256(content).hexdigest()
    computed_hash = compute_file_sha256(test_file)
    assert computed_hash == expected_hash


def test_infer_artifact_type():
    """Verifies artifact type inference by file convention."""
    assert infer_artifact_type("SUMMARY.md") == ArtifactType.SUMMARY_MD.value
    assert infer_artifact_type("SUMMARY.json") == ArtifactType.SUMMARY_JSON.value
    assert infer_artifact_type("reports/AG-ARCH.REPORT.md") == ArtifactType.REPORT.value
    assert infer_artifact_type("logs/AG-ARCH.stdout.log") == ArtifactType.LOG_STDOUT.value
    assert infer_artifact_type("logs/AG-ARCH.stderr.log") == ArtifactType.LOG_STDERR.value
    assert infer_artifact_type("evidence/git-diffs.patch") == ArtifactType.PATCH.value
    assert infer_artifact_type("artifacts/runs/run1/response.zip") == ArtifactType.ZIP_RESULT.value


def test_setup_run_directory_layout(tmp_path: Path):
    """Verifies canonical hierarchical directory layout creation."""
    dirs = EvidenceRegistry.setup_run_directory(tmp_path, "run-hier-01")

    assert dirs["evidence"].is_dir()
    assert dirs["logs"].is_dir()
    assert dirs["reports"].is_dir()
    assert dirs["state"].is_dir()
    assert dirs["run_dir"].name == "run-hier-01"


def test_register_and_get_artifacts(sqlite_temp_db: sqlite3.Connection, tmp_path: Path):
    """Verifies registering an artifact in SQLite and querying metadata."""
    _seed_parent_job_and_run(sqlite_temp_db, "job-art", "run-art")
    registry = EvidenceRegistry(sqlite_temp_db)

    report_file = tmp_path / "AG-COMPAT.REPORT.md"
    report_file.write_text("# Deliverable Report\nAll tests passed.\nRESULT = PASS\n", encoding="utf-8")

    meta = registry.register_artifact(
        file_path=report_file,
        run_id="run-art",
        job_id="job-art",
        agent_id="AG-COMPAT",
    )

    assert meta.artifact_id is not None
    assert meta.artifact_type == ArtifactType.REPORT.value
    assert meta.file_size_bytes == report_file.stat().st_size
    assert meta.sha256_hash == compute_file_sha256(report_file)

    # Query back
    records = registry.get_artifacts_for_run("run-art")
    assert len(records) == 1
    assert records[0].artifact_type == ArtifactType.REPORT.value
    assert records[0].file_size_bytes == meta.file_size_bytes


def test_verify_artifact_integrity(tmp_path: Path):
    """Verifies integrity check detects tampered, resized, or missing files."""
    test_file = tmp_path / "report.md"
    test_file.write_text("Original content", encoding="utf-8")

    from sacl.observability.evidence import ArtifactMetadata

    meta = ArtifactMetadata(
        run_id="run-1",
        job_id="job-1",
        artifact_type=ArtifactType.REPORT.value,
        storage_path=str(test_file),
        file_size_bytes=test_file.stat().st_size,
        sha256_hash=compute_file_sha256(test_file),
        created_at="2026-10-07T22:00:00Z",
    )

    # Clean file passes
    valid, err = EvidenceRegistry.verify_artifact_integrity(meta)
    assert valid is True
    assert err is None

    # Tampered content fails
    test_file.write_text("Tampered content", encoding="utf-8")
    valid_tampered, err_tampered = EvidenceRegistry.verify_artifact_integrity(meta)
    assert valid_tampered is False
    assert "integrity failure" in err_tampered or "mismatch" in err_tampered

    # Missing file fails
    test_file.unlink()
    valid_missing, err_missing = EvidenceRegistry.verify_artifact_integrity(meta)
    assert valid_missing is False
    assert "missing" in err_missing.lower()


def test_verify_required_output_pillar_3(tmp_path: Path):
    """Evaluates Pillar 3: Physical deliverable existence and non-zero byte size."""
    # 1. Non-existent file
    valid, size, err = EvidenceRegistry.verify_required_output(tmp_path / "missing.md")
    assert valid is False
    assert size == 0
    assert "does not exist" in err

    # 2. 0-byte file
    empty_file = tmp_path / "empty.md"
    empty_file.write_text("", encoding="utf-8")
    valid_empty, size_empty, err_empty = EvidenceRegistry.verify_required_output(empty_file)
    assert valid_empty is False
    assert size_empty == 0
    assert "empty" in err_empty.lower()

    # 3. Valid non-empty file
    good_file = tmp_path / "valid.md"
    good_file.write_text("# Report\nValid non-empty content\n", encoding="utf-8")
    valid_good, size_good, err_good = EvidenceRegistry.verify_required_output(good_file)
    assert valid_good is True
    assert size_good > 0
    assert err_good is None


def test_verify_dual_deliverables(tmp_path: Path):
    """Verifies mandatory dual deliverables (SUMMARY.md and SUMMARY.json)."""
    run_dir = tmp_path / "run_deliverables"
    run_dir.mkdir()

    # Neither exists
    is_valid, res = EvidenceRegistry.verify_dual_deliverables(run_dir)
    assert is_valid is False
    assert len(res["errors"]) == 2

    # Add SUMMARY.md only
    (run_dir / "SUMMARY.md").write_text("# Summary\nExecutive results", encoding="utf-8")
    is_valid_partial, res_partial = EvidenceRegistry.verify_dual_deliverables(run_dir)
    assert is_valid_partial is False
    assert "SUMMARY.json is missing" in res_partial["errors"][0]

    # Add valid SUMMARY.json
    summary_data = {
        "run_id": "run-deliverables",
        "package_id": "pkg-1",
        "status": "COMPLETED",
    }
    (run_dir / "SUMMARY.json").write_text(json.dumps(summary_data), encoding="utf-8")

    is_valid_full, res_full = EvidenceRegistry.verify_dual_deliverables(run_dir)
    assert is_valid_full is True
    assert res_full["summary_md_present"] is True
    assert res_full["summary_json_present"] is True
    assert res_full["json_payload"]["run_id"] == "run-deliverables"


def test_normalize_relative_path_registration(sqlite_temp_db: sqlite3.Connection, tmp_path: Path):
    """Verifies that storage_path is properly normalized relative to root directory."""
    _seed_parent_job_and_run(sqlite_temp_db, "job-rel", "run-rel")
    registry = EvidenceRegistry(sqlite_temp_db)

    root = tmp_path / "artifacts"
    sub = root / "runs" / "run-rel" / "logs"
    sub.mkdir(parents=True)
    log_file = sub / "supervisor.trace.log"
    log_file.write_text("trace 1\ntrace 2\n", encoding="utf-8")

    meta = registry.register_artifact(
        file_path=log_file,
        run_id="run-rel",
        job_id="job-rel",
        normalize_relative_to=root,
    )

    assert meta.storage_path == "runs/run-rel/logs/supervisor.trace.log"
    assert "\\" not in meta.storage_path


def test_large_file_streaming_hash(tmp_path: Path):
    """Verifies chunked hashing on a larger multi-block file."""
    large_file = tmp_path / "large.bin"
    # Create 256KB of repeating bytes
    chunk = b"A" * 1024
    with open(large_file, "wb") as f:
        for _ in range(256):
            f.write(chunk)

    expected = hashlib.sha256(b"A" * (1024 * 256)).hexdigest()
    assert compute_file_sha256(large_file, chunk_size=4096) == expected


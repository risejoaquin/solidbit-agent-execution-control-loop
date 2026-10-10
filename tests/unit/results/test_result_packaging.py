"""Tests for Result Packaging Subsystem and Anti-Zip Slip Defense.

Adheres to:
- RESULT_PROTOCOL.md §1.2 & §7
- STATE_MACHINE.md (Transition to RESULT_PACKAGED)
- ADR-011 (Filesystem artifacts & SQLite metadata)
- Anti-Zip Slip path traversal & Windows reserved DOS device defenses.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import zipfile
import pytest

from sacl.results.packager import ResultPackager, sanitize_archive_entry_path


@pytest.fixture
def mock_run_workspace(tmp_path: Path) -> Tuple[Path, Path, Path]:
    run_dir = tmp_path / "run_pkg_001"
    run_dir.mkdir(parents=True, exist_ok=True)
    reports_dir = run_dir / "reports"
    reports_dir.mkdir(exist_ok=True)
    logs_dir = run_dir / "logs"
    logs_dir.mkdir(exist_ok=True)

    summary_md = run_dir / "SUMMARY.md"
    summary_md.write_text("# SUMMARY MD\nVerdict: PASS\n", encoding="utf-8")

    summary_json = run_dir / "SUMMARY.json"
    summary_json.write_text('{"schema": "solidbit.run-summary.v1", "status": "PASS"}', encoding="utf-8")

    rep1 = reports_dir / "AG-QA.REPORT.md"
    rep1.write_text("# QA Report\nAGENT_QA_RESULT = PASS\n", encoding="utf-8")

    log1 = logs_dir / "AG-QA.stdout.log"
    log1.write_text("Execution finished cleanly.\n", encoding="utf-8")

    return run_dir, summary_md, summary_json


def test_sanitize_archive_entry_path_rules() -> None:
    # Valid relative paths
    assert sanitize_archive_entry_path("SUMMARY.md") == "SUMMARY.md"
    assert sanitize_archive_entry_path("reports/AG-1.md") == "reports/AG-1.md"
    assert sanitize_archive_entry_path(r"logs\agent.stdout.log") == "logs/agent.stdout.log"

    # Directory traversal (Anti-Zip Slip)
    with pytest.raises(ValueError) as exc1:
        sanitize_archive_entry_path("../escape.txt")
    assert "Anti-Zip Slip Violation" in str(exc1.value)

    with pytest.raises(ValueError) as exc2:
        sanitize_archive_entry_path("reports/../../root.txt")
    assert "Anti-Zip Slip Violation" in str(exc2.value)

    # Absolute paths
    with pytest.raises(ValueError) as exc3:
        sanitize_archive_entry_path("/etc/shadow")
    assert "is absolute" in str(exc3.value)

    with pytest.raises(ValueError) as exc4:
        sanitize_archive_entry_path("C:/Windows/cmd.exe")
    assert "is absolute" in str(exc4.value)

    # Windows reserved DOS device names
    with pytest.raises(ValueError) as exc5:
        sanitize_archive_entry_path("CON.txt")
    assert "Reserved device name violation" in str(exc5.value)

    with pytest.raises(ValueError) as exc6:
        sanitize_archive_entry_path("logs/NUL")
    assert "Reserved device name violation" in str(exc6.value)


def test_package_run_results_creates_valid_archive(
    mock_run_workspace: Tuple[Path, Path, Path]
) -> None:
    run_dir, summary_md, summary_json = mock_run_workspace
    packager = ResultPackager()

    result = packager.package_run_results(
        run_id="run-pkg-001",
        job_id="job-pkg-001",
        run_dir=run_dir,
        summary_md_path=summary_md,
        summary_json_path=summary_json,
        final_verdict="PASS",
    )

    assert result.zip_path.exists()
    assert result.file_size_bytes > 0
    assert len(result.sha256_hash) == 64

    # Open archive and inspect contents
    with zipfile.ZipFile(result.zip_path, "r") as zf:
        namelist = zf.namelist()
        assert "SUMMARY.md" in namelist
        assert "SUMMARY.json" in namelist
        assert "reports/AG-QA.REPORT.md" in namelist
        assert "logs/AG-QA.stdout.log" in namelist
        assert "checksums.sha256" in namelist

        # Inspect checksums content
        checksums = zf.read("checksums.sha256").decode("utf-8")
        assert "SUMMARY.md" in checksums
        assert "SUMMARY.json" in checksums
        assert "reports/AG-QA.REPORT.md" in checksums


def test_package_run_results_updates_sqlite_operational_store(
    mock_run_workspace: Tuple[Path, Path, Path], sqlite_memory_db: sqlite3.Connection
) -> None:
    run_dir, summary_md, summary_json = mock_run_workspace
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Seed job and run
    cursor = sqlite_memory_db.cursor()
    cursor.execute(
        """
        INSERT INTO jobs (job_id, status, priority, created_at, updated_at)
        VALUES ('job-pkg-001', 'VERIFYING', 0, ?, ?)
        """,
        (now_iso, now_iso),
    )
    cursor.execute(
        """
        INSERT INTO runs (
            run_id, job_id, package_id, project, repository, mode,
            source_orchestrator, target_repo_path, run_dir, status,
            ready_for_integration, started_at
        ) VALUES (
            'run-pkg-001', 'job-pkg-001', 'pkg-001', 'solidbit', 'org/repo', 'isolated_branch',
            '', '', '', 'VERIFYING', 'YES', ?
        )
        """,
        (now_iso,),
    )
    sqlite_memory_db.commit()

    packager = ResultPackager()
    res = packager.package_run_results(
        run_id="run-pkg-001",
        job_id="job-pkg-001",
        run_dir=run_dir,
        summary_md_path=summary_md,
        summary_json_path=summary_json,
        final_verdict="PASS",
        db_conn=sqlite_memory_db,
    )

    # Verify artifacts table
    cursor.execute(
        "SELECT artifact_type, storage_path, sha256_hash FROM artifacts WHERE run_id = 'run-pkg-001'"
    )
    art_row = cursor.fetchone()
    assert art_row[0] == "ZIP_RESULT"
    assert art_row[2] == res.sha256_hash

    # Verify results table
    cursor.execute(
        "SELECT status, final_verdict, package_result_zip FROM results WHERE run_id = 'run-pkg-001'"
    )
    res_row = cursor.fetchone()
    assert res_row[0] == "RESULT_PACKAGED"
    assert res_row[1] == "PASS"
    assert res_row[2] == str(res.zip_path).replace("\\", "/")

    # Verify runs table transitioned to RESULT_PACKAGED
    cursor.execute("SELECT status FROM runs WHERE run_id = 'run-pkg-001'")
    assert cursor.fetchone()[0] == "RESULT_PACKAGED"

    # Verify jobs table transitioned to RESULT_PACKAGED
    cursor.execute("SELECT status FROM jobs WHERE job_id = 'job-pkg-001'")
    assert cursor.fetchone()[0] == "RESULT_PACKAGED"

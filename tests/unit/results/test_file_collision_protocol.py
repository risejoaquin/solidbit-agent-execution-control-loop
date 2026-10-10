"""Tests for Cross-Agent File Overlap and Collision Protocol.

Adheres strictly to:
- RESULT_PROTOCOL.md §6
- Proven logic from collect-results.ps1#L98-L136
- SQLite tables file_modifications & file_conflicts
- Integration gating: ready_for_integration == 'NO' upon collision.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import sqlite3
import pytest

from sacl.results.collision import CollisionDetector, normalize_file_path


@pytest.fixture
def seeded_db(sqlite_memory_db: sqlite3.Connection):
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cursor = sqlite_memory_db.cursor()

    cursor.execute(
        """
        INSERT INTO jobs (job_id, status, priority, created_at, updated_at)
        VALUES ('job-col-001', 'RUNNING', 0, ?, ?)
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
            'run-col-001', 'job-col-001', 'pkg-001', 'solidbit', 'org/repo', 'isolated_branch',
            '', '', '', 'RUNNING', 'NO', ?
        )
        """,
        (now_iso,),
    )
    cursor.execute(
        """
        INSERT INTO agents (agent_id, run_id, status, result_verdict, prompt_path, report_path, stdout_path, stderr_path, updated_at)
        VALUES ('AG-ARCH', 'run-col-001', 'COMPLETE', 'PASS', 'p.md', 'r.md', 'out.log', 'err.log', ?),
               ('AG-SEC', 'run-col-001', 'COMPLETE', 'PASS', 'p.md', 'r.md', 'out.log', 'err.log', ?)
        """,
        (now_iso, now_iso),
    )
    sqlite_memory_db.commit()
    return sqlite_memory_db


def test_normalize_file_path() -> None:
    assert normalize_file_path(r"Docs\Architecture\Spec.md") == "docs/architecture/spec.md"
    assert normalize_file_path(r"C:\repo\src\main.py") == "repo/src/main.py"
    assert normalize_file_path("/schemas/manifest.json") == "schemas/manifest.json"


def test_file_collision_detected_and_blocks_integration(seeded_db: sqlite3.Connection) -> None:
    detector = CollisionDetector()

    # Agent AG-ARCH modifies spec.md and readme.md
    detector.record_file_modifications(
        run_id="run-col-001",
        agent_id="AG-ARCH",
        file_paths=["docs/spec.md", "README.md"],
        db_conn=seeded_db,
    )

    # Agent AG-SEC also modifies spec.md (Collision!) and security.md
    detector.record_file_modifications(
        run_id="run-col-001",
        agent_id="AG-SEC",
        file_paths=["docs/spec.md", "docs/security.md"],
        db_conn=seeded_db,
    )

    report = detector.evaluate_conflicts(
        run_id="run-col-001",
        db_conn=seeded_db,
    )

    assert "docs/spec.md" in report.conflicting_files
    assert len(report.conflicting_files) == 1
    assert sorted(report.conflicts_by_file["docs/spec.md"]) == ["AG-ARCH", "AG-SEC"]
    assert report.ready_for_integration == "NO"
    assert any("Overlapping file modifications detected" in b for b in report.blockers)

    # Verify SQLite runs table was updated to 'NO'
    cursor = seeded_db.cursor()
    cursor.execute("SELECT ready_for_integration FROM runs WHERE run_id = 'run-col-001'")
    assert cursor.fetchone()[0] == "NO"

    # Verify SQLite file_conflicts table row was inserted
    cursor.execute("SELECT file_path, agents_involved, resolution FROM file_conflicts WHERE run_id = 'run-col-001'")
    conf_row = cursor.fetchone()
    assert conf_row[0] == "docs/spec.md"
    assert json.loads(conf_row[1]) == ["AG-ARCH", "AG-SEC"]
    assert conf_row[2] == "UNRESOLVED"


def test_zero_file_collision_allows_integration(seeded_db: sqlite3.Connection) -> None:
    detector = CollisionDetector()

    # Disjoint files modified
    detector.record_file_modifications(
        run_id="run-col-001",
        agent_id="AG-ARCH",
        file_paths=["docs/spec.md"],
        db_conn=seeded_db,
    )
    detector.record_file_modifications(
        run_id="run-col-001",
        agent_id="AG-SEC",
        file_paths=["docs/security.md"],
        db_conn=seeded_db,
    )

    report = detector.evaluate_conflicts(
        run_id="run-col-001",
        db_conn=seeded_db,
    )

    assert len(report.conflicting_files) == 0
    assert report.ready_for_integration == "YES"
    assert len(report.blockers) == 0

    cursor = seeded_db.cursor()
    cursor.execute("SELECT ready_for_integration FROM runs WHERE run_id = 'run-col-001'")
    assert cursor.fetchone()[0] == "YES"

"""Tests for cross-agent file modification collision detection and integration gating."""

from __future__ import annotations

import pytest

from sacl.contracts.exceptions import CollisionDetectedError
from sacl.dag.collision import CollisionDetector
from sacl.observability.audit import AuditEventEmitter


def test_collision_detection_clean_no_overlap(sqlite_memory_db):
    audit = AuditEventEmitter(sqlite_memory_db)
    detector = CollisionDetector(db_conn=sqlite_memory_db, audit_emitter=audit)

    agent_files = {
        "AG-ARCH": ["docs/architecture.md", "docs/system.md"],
        "AG-SEC": ["docs/security.md"],
        "AG-SCHEMA": ["schemas/custom.schema.json"],
    }

    has_collision, conflicts = detector.evaluate_stage_collisions("run-col-001", agent_files)
    assert has_collision is False
    assert conflicts == {}

    # Assert passes
    detector.assert_no_collisions("run-col-001", agent_files)


def test_collision_detection_finds_overlap_and_gates_pipeline(sqlite_memory_db):
    audit = AuditEventEmitter(sqlite_memory_db)
    detector = CollisionDetector(db_conn=sqlite_memory_db, audit_emitter=audit)

    # Insert parent job record and dummy run record into database
    sqlite_memory_db.execute(
        """
        INSERT INTO jobs (job_id, status, created_at, updated_at)
        VALUES ('job-001', 'RUNNING', '2026-10-07T00:00:00Z', '2026-10-07T00:00:00Z');
        """
    )
    sqlite_memory_db.execute(
        """
        INSERT INTO runs (
            run_id, job_id, package_id, project, repository, mode,
            source_orchestrator, target_repo_path, run_dir, status,
            ready_for_integration, started_at
        ) VALUES (
            'run-col-002', 'job-001', 'pkg-001', 'solidbit', 'repo',
            'dev', 'orch', '/repo', '/runs/002', 'RUNNING', 'NO', '2026-10-07T00:00:00Z'
        )
        """
    )
    sqlite_memory_db.commit()

    # Both AG-ARCH and AG-SEC modify docs/ARCHITECTURE.md!
    agent_files = {
        "AG-ARCH": ["docs/ARCHITECTURE.md", "docs/decisions.md"],
        "AG-SEC": ["docs/ARCHITECTURE.md", "docs/security.md"],
    }

    has_collision, conflicts = detector.evaluate_stage_collisions("run-col-002", agent_files)
    assert has_collision is True
    assert "docs/ARCHITECTURE.md" in conflicts
    assert set(conflicts["docs/ARCHITECTURE.md"]) == {"AG-ARCH", "AG-SEC"}

    # Verify pipeline gating in runs table: status must be BLOCKED, ready_for_integration must be NO
    cur = sqlite_memory_db.cursor()
    cur.execute("SELECT status, ready_for_integration FROM runs WHERE run_id = 'run-col-002'")
    row = cur.fetchone()
    assert row[0] == "BLOCKED"
    assert row[1] == "NO"

    # Verify conflict recorded in file_conflicts table
    cur.execute("SELECT file_path, resolution FROM file_conflicts WHERE run_id = 'run-col-002'")
    cf_row = cur.fetchone()
    assert cf_row[0] == "docs/ARCHITECTURE.md"
    assert cf_row[1] == "UNRESOLVED"

    # assert_no_collisions raises CollisionDetectedError
    with pytest.raises(CollisionDetectedError, match="Overlapping file modifications"):
        detector.assert_no_collisions("run-col-002", agent_files)

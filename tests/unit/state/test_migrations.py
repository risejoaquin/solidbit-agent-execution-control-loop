"""Unit tests for SQLite Schema Migration Engine and Tamper Detection."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure repo root is on sys.path
_repo_root = Path(__file__).resolve().parents[3]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

import pytest

from sacl.state.connection import create_connection
from sacl.state.exceptions import MigrationChecksumMismatchError, MigrationError
from sacl.state.migrations import MigrationRunner
from tests.helpers.db_helpers import verify_canonical_domains_exist


def test_migration_runner_discover(migration_sql_path: Path) -> None:
    """Verifies that MigrationRunner discovers 001_init.sql."""
    runner = MigrationRunner(migration_sql_path.parent)
    migrations = runner.discover_migrations()
    assert len(migrations) >= 1
    versions = [v for v, p in migrations]
    assert 1 in versions


def test_migration_runner_apply_001_init(migration_sql_path: Path) -> None:
    """Verifies that 001_init.sql applies successfully and creates canonical domains."""
    conn = create_connection(":memory:")
    runner = MigrationRunner(migration_sql_path.parent)

    applied = runner.apply_all(conn)
    assert len(applied) == 1
    assert applied[0].version == 1
    assert applied[0].name == "001_init.sql"
    assert len(applied[0].checksum) == 64  # SHA-256 length

    # Verify 16 canonical domains
    domain_checks = verify_canonical_domains_exist(conn)
    for domain, exists in domain_checks.items():
        assert exists is True, f"Domain table {domain} missing"

    # Verify schema_migrations ledger entry
    cursor = conn.cursor()
    cursor.execute("SELECT version, name, checksum FROM schema_migrations WHERE version = 1;")
    row = cursor.fetchone()
    assert row is not None
    assert row["version"] == 1
    assert row["name"] == "001_init.sql"

    conn.close()


def test_migration_runner_idempotent(migration_sql_path: Path) -> None:
    """Verifies that applying migrations multiple times is a safe no-op."""
    conn = create_connection(":memory:")
    runner = MigrationRunner(migration_sql_path.parent)

    first_run = runner.apply_all(conn)
    assert len(first_run) == 1

    # Second run should apply 0 new migrations
    second_run = runner.apply_all(conn)
    assert len(second_run) == 0

    conn.close()


def test_migration_runner_tamper_detection(tmp_path: Path) -> None:
    """Verifies that modifying an already-applied migration raises MigrationChecksumMismatchError."""
    mig_dir = tmp_path / "migrations"
    mig_dir.mkdir()
    mig_file = mig_dir / "001_test.sql"
    mig_file.write_text("CREATE TABLE alpha (id INT);", encoding="utf-8")

    conn = create_connection(":memory:")
    runner = MigrationRunner(mig_dir)

    # Apply original
    applied = runner.apply_all(conn)
    assert len(applied) == 1

    # Tamper with file on disk
    mig_file.write_text("CREATE TABLE alpha (id INT, modified INT);", encoding="utf-8")

    # Next run must detect hash mismatch and raise MigrationChecksumMismatchError
    with pytest.raises(MigrationChecksumMismatchError) as exc_info:
        runner.apply_all(conn)

    assert exc_info.value.version == 1
    assert "Schema tampering detected" in str(exc_info.value)

    conn.close()


def test_migration_runner_missing_file_error() -> None:
    """Verifies error raised when nonexistent migration file specified."""
    conn = create_connection(":memory:")
    runner = MigrationRunner()
    with pytest.raises(MigrationError):
        runner.apply_migration_file(conn, Path("nonexistent/009_missing.sql"))
    conn.close()

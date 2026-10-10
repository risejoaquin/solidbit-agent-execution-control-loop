"""Unit tests for SQLite Connection Management and PRAGMA Configuration."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

# Ensure repo root is on sys.path
_repo_root = Path(__file__).resolve().parents[3]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

import pytest

from sacl.state.connection import ConnectionManager, create_connection
from tests.helpers.db_helpers import check_foreign_keys_enabled, check_wal_mode


def test_create_connection_memory() -> None:
    """Verifies in-memory connection creation and foreign key pragma."""
    conn = create_connection(":memory:")
    assert isinstance(conn, sqlite3.Connection)
    assert conn.row_factory == sqlite3.Row
    assert check_foreign_keys_enabled(conn) is True
    conn.close()


def test_create_connection_file_wal_mode(tmp_path: Path) -> None:
    """Verifies that disk-backed SQLite connection enables WAL mode and pragmas."""
    db_file = tmp_path / "test_ops.db"
    conn = create_connection(db_file)
    assert check_wal_mode(conn) is True
    assert check_foreign_keys_enabled(conn) is True

    # Test busy_timeout pragma
    cursor = conn.cursor()
    cursor.execute("PRAGMA busy_timeout;")
    assert cursor.fetchone()[0] == 5000

    conn.close()


def test_create_connection_read_only(tmp_path: Path) -> None:
    """Verifies read-only connection prevents writes."""
    db_file = tmp_path / "test_ro.db"
    # Create DB and table first
    writer = create_connection(db_file)
    writer.execute("CREATE TABLE test_data (id INTEGER PRIMARY KEY, value TEXT);")
    writer.execute("INSERT INTO test_data VALUES (1, 'hello');")
    writer.commit()
    writer.close()

    # Open read-only
    ro_conn = create_connection(db_file, read_only=True)
    cursor = ro_conn.cursor()
    cursor.execute("SELECT value FROM test_data WHERE id = 1;")
    assert cursor.fetchone()[0] == "hello"

    # Attempting to write must raise OperationalError
    with pytest.raises(sqlite3.OperationalError):
        ro_conn.execute("INSERT INTO test_data VALUES (2, 'fail');")

    ro_conn.close()


def test_connection_manager_context_managers(tmp_path: Path) -> None:
    """Verifies ConnectionManager lifecycle management."""
    db_file = tmp_path / "test_mgr.db"
    manager = ConnectionManager(db_file)

    with manager.connection() as conn:
        conn.execute("CREATE TABLE items (name TEXT);")
        conn.execute("INSERT INTO items VALUES ('item1');")
        conn.commit()

    with manager.read_only_connection() as ro_conn:
        cursor = ro_conn.cursor()
        cursor.execute("SELECT name FROM items;")
        assert cursor.fetchone()[0] == "item1"

    manager.close()

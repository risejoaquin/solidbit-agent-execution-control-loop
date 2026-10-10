"""Unit tests for SQLite Transactions and Savepoints."""

from __future__ import annotations

import sqlite3

import pytest

from sacl.state.connection import create_connection
from sacl.state.transactions import savepoint, transaction


@pytest.fixture
def test_db() -> sqlite3.Connection:
    conn = create_connection(":memory:")
    conn.execute("CREATE TABLE counter (id INTEGER PRIMARY KEY, count INTEGER);")
    conn.commit()
    return conn


def test_transaction_commit(test_db: sqlite3.Connection) -> None:
    """Verifies that clean exit commits transaction."""
    with transaction(test_db, immediate=True):
        test_db.execute("INSERT INTO counter VALUES (1, 100);")

    cursor = test_db.cursor()
    cursor.execute("SELECT count FROM counter WHERE id = 1;")
    assert cursor.fetchone()["count"] == 100


def test_transaction_rollback_on_exception(test_db: sqlite3.Connection) -> None:
    """Verifies that an unhandled exception triggers rollback."""
    with pytest.raises(RuntimeError):
        with transaction(test_db, immediate=True):
            test_db.execute("INSERT INTO counter VALUES (2, 200);")
            raise RuntimeError("Forced transaction failure")

    cursor = test_db.cursor()
    cursor.execute("SELECT * FROM counter WHERE id = 2;")
    assert cursor.fetchone() is None


def test_nested_transaction_savepoint(test_db: sqlite3.Connection) -> None:
    """Verifies that nested transaction uses savepoints to allow partial rollback."""
    with transaction(test_db, immediate=True):
        test_db.execute("INSERT INTO counter VALUES (1, 10);")

        # Nested transaction rolls back partially
        try:
            with transaction(test_db):
                test_db.execute("INSERT INTO counter VALUES (2, 20);")
                raise ValueError("Nested failure")
        except ValueError:
            pass

        test_db.execute("INSERT INTO counter VALUES (3, 30);")

    cursor = test_db.cursor()
    cursor.execute("SELECT id FROM counter ORDER BY id;")
    rows = [r["id"] for r in cursor.fetchall()]
    assert rows == [1, 3]  # id 2 was rolled back by nested savepoint


def test_explicit_savepoint_rollback(test_db: sqlite3.Connection) -> None:
    """Verifies explicit savepoint rollbacks."""
    with transaction(test_db):
        test_db.execute("INSERT INTO counter VALUES (10, 10);")

        with pytest.raises(ZeroDivisionError):
            with savepoint(test_db, name="sp_math"):
                test_db.execute("INSERT INTO counter VALUES (20, 20);")
                _ = 1 / 0

    cursor = test_db.cursor()
    cursor.execute("SELECT id FROM counter ORDER BY id;")
    rows = [r["id"] for r in cursor.fetchall()]
    assert rows == [10]

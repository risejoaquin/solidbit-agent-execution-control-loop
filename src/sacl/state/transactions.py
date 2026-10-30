"""SACL V1 SQLite ACID Transaction Primitives.

Provides robust transaction management, BEGIN IMMEDIATE locking semantics for WAL mode,
and nested savepoint rollback support.
"""

from __future__ import annotations

import sqlite3
import uuid
from contextlib import contextmanager
from typing import Generator, Optional

_MANAGED_CONNECTIONS: set[int] = set()


def is_managed_transaction(conn: sqlite3.Connection) -> bool:
    """Returns True if connection is currently participating in an explicit transaction block."""
    return id(conn) in _MANAGED_CONNECTIONS


@contextmanager
def savepoint(conn: sqlite3.Connection, name: Optional[str] = None) -> Generator[str, None, None]:
    """Context manager for nested SQLite savepoints.

    Allows isolated sub-transactions that can be rolled back without rolling back
    the outer parent transaction.
    """
    sp_name = name or f"sp_{uuid.uuid4().hex[:8]}"
    was_managed = id(conn) in _MANAGED_CONNECTIONS
    _MANAGED_CONNECTIONS.add(id(conn))
    conn.execute(f"SAVEPOINT {sp_name};")
    try:
        yield sp_name
        conn.execute(f"RELEASE SAVEPOINT {sp_name};")
    except Exception:
        conn.execute(f"ROLLBACK TO SAVEPOINT {sp_name};")
        conn.execute(f"RELEASE SAVEPOINT {sp_name};")
        raise
    finally:
        if not was_managed:
            _MANAGED_CONNECTIONS.discard(id(conn))


@contextmanager
def transaction(
    conn: sqlite3.Connection,
    immediate: bool = True,
) -> Generator[sqlite3.Connection, None, None]:
    """Context manager executing block inside an explicit ACID transaction.

    Under SQLite WAL mode, BEGIN IMMEDIATE acquires the write lock at the start of
    the transaction, preventing deadlocks that can occur if multiple concurrent readers
    attempt to upgrade to writer simultaneously.

    If already within an active transaction, automatically falls back to an isolated
    savepoint to support nested transaction calls safely.

    Args:
        conn: Active sqlite3.Connection instance.
        immediate: If True, uses 'BEGIN IMMEDIATE', else standard 'BEGIN'.
    """
    if conn.in_transaction:
        with savepoint(conn):
            yield conn
    else:
        was_managed = id(conn) in _MANAGED_CONNECTIONS
        _MANAGED_CONNECTIONS.add(id(conn))
        if immediate:
            conn.execute("BEGIN IMMEDIATE;")
        else:
            conn.execute("BEGIN;")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            if not was_managed:
                _MANAGED_CONNECTIONS.discard(id(conn))

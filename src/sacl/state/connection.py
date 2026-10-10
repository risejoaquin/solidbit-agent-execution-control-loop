"""SACL V1 SQLite Connection Management.

Provides connection factories, WAL mode bootstrap, canonical PRAGMA initialization,
and read-only connection isolation.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional, Union

from sacl.contracts.invariants import SQLITE_PRAGMAS


def create_connection(
    db_path: Union[str, Path] = ":memory:",
    read_only: bool = False,
    timeout: float = 5.0,
) -> sqlite3.Connection:
    """Creates and bootstraps a SQLite connection with canonical PRAGMAs.

    Args:
        db_path: Filesystem path to SQLite database or ':memory:'.
        read_only: If True, opens database in read-only mode (file:...?...mode=ro).
        timeout: Lock acquisition busy timeout in seconds (default: 5.0s / 5000ms).

    Returns:
        Configured sqlite3.Connection instance with Row factory and enabled foreign keys.
    """
    path_str = str(db_path)
    is_memory = path_str == ":memory:"

    if read_only and not is_memory:
        # Canonical read-only URI connection
        abs_path = Path(path_str).resolve().as_posix()
        uri_str = f"file:{abs_path}?mode=ro"
        conn = sqlite3.connect(uri_str, timeout=timeout, uri=True)
    elif path_str.startswith("file:"):
        conn = sqlite3.connect(path_str, timeout=timeout, uri=True)
    else:
        conn = sqlite3.connect(path_str, timeout=timeout)

    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if read_only:
        # In read-only mode, only non-mutating PRAGMAs can be set
        cursor.execute("PRAGMA busy_timeout = 5000;")
        cursor.execute("PRAGMA foreign_keys = ON;")
    else:
        # Canonical bootstrap for read/write connections
        for pragma in SQLITE_PRAGMAS:
            cursor.execute(pragma)

    return conn


class ConnectionManager:
    """Manages SQLite database connections for operational state workflows."""

    def __init__(self, db_path: Union[str, Path] = ":memory:") -> None:
        self.db_path = db_path
        self._shared_connection: Optional[sqlite3.Connection] = None
        self._is_memory = str(db_path) == ":memory:"

    @property
    def is_memory(self) -> bool:
        return self._is_memory

    def get_connection(self) -> sqlite3.Connection:
        """Returns a write-capable SQLite connection.

        For in-memory databases, preserves a shared connection instance across calls.
        """
        if self._is_memory:
            if self._shared_connection is None:
                self._shared_connection = create_connection(self.db_path)
            return self._shared_connection
        return create_connection(self.db_path)

    def get_read_only_connection(self) -> sqlite3.Connection:
        """Returns a non-blocking read-only connection."""
        if self._is_memory:
            # Memory DB cannot use mode=ro URI independently
            return self.get_connection()
        return create_connection(self.db_path, read_only=True)

    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager yielding a read/write SQLite connection."""
        conn = self.get_connection()
        try:
            yield conn
        finally:
            if not self._is_memory:
                conn.close()

    @contextmanager
    def read_only_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager yielding a read-only connection."""
        conn = self.get_read_only_connection()
        try:
            yield conn
        finally:
            if not self._is_memory:
                conn.close()

    def close(self) -> None:
        """Closes any shared connection held by the manager."""
        if self._shared_connection is not None:
            try:
                self._shared_connection.close()
            except Exception:
                pass
            self._shared_connection = None

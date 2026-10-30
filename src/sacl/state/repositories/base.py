"""SACL V1 Base Repository.

Provides fundamental database interaction, cursor wrapping, row-to-dictionary
mapping, and parameter handling.
"""

from __future__ import annotations

import sqlite3
from typing import Any, Dict, List, Optional, Sequence, Union

from sacl.state.transactions import is_managed_transaction
from sacl.state.utils import row_to_dict, rows_to_dicts


class BaseRepository:
    """Base relational repository backed by a SQLite connection."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def execute(
        self, sql: str, params: Union[Sequence[Any], Dict[str, Any]] = ()
    ) -> sqlite3.Cursor:
        """Executes a SQL statement with parameters."""
        return self.conn.execute(sql, params)

    def executemany(
        self, sql: str, seq_of_params: Sequence[Union[Sequence[Any], Dict[str, Any]]]
    ) -> sqlite3.Cursor:
        """Executes a SQL statement against a sequence of parameters."""
        return self.conn.executemany(sql, seq_of_params)

    def fetchone(
        self, sql: str, params: Union[Sequence[Any], Dict[str, Any]] = ()
    ) -> Optional[sqlite3.Row]:
        """Fetches a single row from executing the query."""
        cursor = self.conn.execute(sql, params)
        return cursor.fetchone()

    def fetchall(
        self, sql: str, params: Union[Sequence[Any], Dict[str, Any]] = ()
    ) -> List[sqlite3.Row]:
        """Fetches all rows from executing the query."""
        cursor = self.conn.execute(sql, params)
        return cursor.fetchall()

    def fetchone_dict(
        self, sql: str, params: Union[Sequence[Any], Dict[str, Any]] = ()
    ) -> Optional[Dict[str, Any]]:
        """Fetches a single row converted to a standard Python dictionary."""
        row = self.fetchone(sql, params)
        return row_to_dict(row)

    def fetchall_dict(
        self, sql: str, params: Union[Sequence[Any], Dict[str, Any]] = ()
    ) -> List[Dict[str, Any]]:
        """Fetches all rows converted to a list of standard Python dictionaries."""
        rows = self.fetchall(sql, params)
        return rows_to_dicts(rows)

    def commit(self) -> None:
        """Commits the active transaction unless managed by an outer transaction context."""
        if is_managed_transaction(self.conn):
            return
        self.conn.commit()

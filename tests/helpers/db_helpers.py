"""SACL V1 Test Database Helpers.

Utility functions for verifying SQLite schema migrations, tables, and constraints.
"""

from __future__ import annotations

import sqlite3
from typing import Dict, List

from sacl.contracts.invariants import OPERATIONAL_STATE_DOMAINS


def get_all_table_names(conn: sqlite3.Connection) -> List[str]:
    """Returns a sorted list of all tables in the SQLite database."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [row[0] for row in cursor.fetchall() if not row[0].startswith("sqlite_")]
    return tables


def verify_canonical_domains_exist(conn: sqlite3.Connection) -> Dict[str, bool]:
    """Checks that all 16 canonical operational state domains exist in the database."""
    tables = set(get_all_table_names(conn))
    results = {}
    for domain in OPERATIONAL_STATE_DOMAINS:
        results[domain] = domain in tables
    return results


def check_wal_mode(conn: sqlite3.Connection) -> bool:
    """Verifies that Write-Ahead Logging (WAL) journal mode is active."""
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode;")
    mode = cursor.fetchone()[0]
    return mode.lower() == "wal"


def check_foreign_keys_enabled(conn: sqlite3.Connection) -> bool:
    """Verifies that foreign key enforcement is turned on."""
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys;")
    enabled = cursor.fetchone()[0]
    return bool(enabled)

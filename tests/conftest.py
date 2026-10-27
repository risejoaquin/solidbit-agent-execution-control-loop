"""SACL V1 Pytest Fixture Configuration.

Provides test fixtures for schema validation, SQLite database lifecycle (001_init.sql),
mock execution environments, and frozen example access.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Callable, Dict, Generator

# Ensure src/ is on sys.path
_src_dir = Path(__file__).resolve().parent.parent / "src"
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))

import pytest

from sacl.contracts.invariants import SQLITE_PRAGMAS
from sacl.contracts.schema_validator import SchemaValidator


@pytest.fixture(scope="session")
def repo_root() -> Path:
    """Returns the root directory of the worktree repository."""
    current = Path(__file__).resolve().parent.parent
    return current


@pytest.fixture(scope="session")
def schemas_dir(repo_root: Path) -> Path:
    """Returns the canonical schemas directory."""
    candidate = repo_root / "schemas"
    if candidate.exists():
        return candidate
    alt = repo_root / "inputs" / "frozen-architecture" / "schemas"
    if alt.exists():
        return alt
    raise FileNotFoundError("schemas directory not found")


@pytest.fixture(scope="session")
def examples_dir(repo_root: Path) -> Path:
    """Returns the canonical examples directory."""
    candidate = repo_root / "examples"
    if candidate.exists():
        return candidate
    alt = repo_root / "inputs" / "frozen-architecture" / "examples"
    if alt.exists():
        return alt
    raise FileNotFoundError("examples directory not found")


@pytest.fixture(scope="session")
def migration_sql_path(repo_root: Path) -> Path:
    """Returns path to 001_init.sql migration script."""
    candidate = repo_root / "db" / "migrations" / "001_init.sql"
    if candidate.exists():
        return candidate
    alt = repo_root / "inputs" / "frozen-architecture" / "db" / "migrations" / "001_init.sql"
    if alt.exists():
        return alt
    raise FileNotFoundError("001_init.sql not found")


@pytest.fixture
def schema_validator(schemas_dir: Path) -> SchemaValidator:
    """Provides a configured SchemaValidator instance."""
    return SchemaValidator(schemas_dir)


@pytest.fixture
def load_frozen_example(examples_dir: Path) -> Callable[[str], Dict[str, Any]]:
    """Fixture factory to load a named example JSON file."""

    def _loader(filename: str) -> Dict[str, Any]:
        if not filename.endswith(".json"):
            filename = f"{filename}.valid.json"
        target = examples_dir / filename
        if not target.exists():
            target = examples_dir / f"{filename}.json"
        if not target.exists():
            raise FileNotFoundError(f"Example file '{filename}' not found in {examples_dir}")
        with open(target, "r", encoding="utf-8") as f:
            return json.load(f)

    return _loader


@pytest.fixture
def all_frozen_examples(examples_dir: Path) -> Dict[str, Dict[str, Any]]:
    """Loads all 10 frozen .valid.json examples into a dictionary."""
    examples = {}
    for item in examples_dir.glob("*.valid.json"):
        with open(item, "r", encoding="utf-8") as f:
            examples[item.name] = json.load(f)
    return examples


@pytest.fixture
def sqlite_memory_db(migration_sql_path: Path) -> Generator[sqlite3.Connection, None, None]:
    """In-memory SQLite connection with 001_init.sql schema applied and pragmas set."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("PRAGMA busy_timeout = 5000;")

    with open(migration_sql_path, "r", encoding="utf-8") as f:
        ddl = f.read()
    cursor.executescript(ddl)
    conn.commit()

    yield conn
    conn.close()


@pytest.fixture
def sqlite_temp_db(
    tmp_path: Path, migration_sql_path: Path
) -> Generator[sqlite3.Connection, None, None]:
    """Temporary file-backed SQLite database operating in full WAL mode with 001_init.sql."""
    db_file = tmp_path / "sacl_ops_test.db"
    conn = sqlite3.connect(str(db_file))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    for pragma in SQLITE_PRAGMAS:
        cursor.execute(pragma)

    with open(migration_sql_path, "r", encoding="utf-8") as f:
        ddl = f.read()
    cursor.executescript(ddl)
    conn.commit()

    yield conn
    conn.close()

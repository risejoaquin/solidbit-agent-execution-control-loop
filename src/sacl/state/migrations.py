"""SACL V1 Database Schema Migration Engine.

Discovers, verifies, and executes forward-only DDL migrations against SQLite,
tracking state in Domain 1 (schema_migrations) and detecting hash tampering.
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from sacl.state.exceptions import (
    MigrationChecksumMismatchError,
    MigrationError,
    MigrationVersionConflictError,
)
from sacl.state.utils import calculate_sha256, utc_now


@dataclass(frozen=True)
class MigrationRecord:
    """Represents a recorded entry in the schema_migrations ledger."""
    version: int
    name: str
    applied_at: str
    checksum: str


class MigrationRunner:
    """Executes and verifies forward-only SQLite schema migrations."""

    MIGRATION_PATTERN = re.compile(r"^(\d+)[-_](.*)\.sql$", re.IGNORECASE)

    def __init__(self, migrations_dir: Optional[Union[str, Path]] = None) -> None:
        self.migrations_dir = Path(migrations_dir) if migrations_dir else self._find_default_migrations_dir()

    @staticmethod
    def _find_default_migrations_dir() -> Path:
        """Finds default db/migrations directory relative to workspace or repository."""
        # Check current working directory
        cwd = Path.cwd()
        candidate = cwd / "db" / "migrations"
        if candidate.is_dir():
            return candidate

        # Check relative to module location
        module_root = Path(__file__).resolve().parent.parent.parent.parent
        candidate = module_root / "db" / "migrations"
        if candidate.is_dir():
            return candidate

        # Check frozen architecture directory
        candidate = module_root / "inputs" / "frozen-architecture" / "db" / "migrations"
        if candidate.is_dir():
            return candidate

        return cwd / "db" / "migrations"

    @staticmethod
    def ensure_schema_migrations_table(conn: sqlite3.Connection) -> None:
        """Ensures Domain 1 schema_migrations ledger table exists."""
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version         INTEGER PRIMARY KEY,
                name            TEXT NOT NULL,
                applied_at      TEXT NOT NULL,
                checksum        TEXT NOT NULL
            );
            """
        )
        conn.commit()

    @staticmethod
    def get_applied_migrations(conn: sqlite3.Connection) -> Dict[int, MigrationRecord]:
        """Returns map of version -> MigrationRecord for all applied migrations."""
        MigrationRunner.ensure_schema_migrations_table(conn)
        cursor = conn.cursor()
        cursor.execute("SELECT version, name, applied_at, checksum FROM schema_migrations ORDER BY version ASC;")
        records = {}
        for row in cursor.fetchall():
            records[row["version"]] = MigrationRecord(
                version=row["version"],
                name=row["name"],
                applied_at=row["applied_at"],
                checksum=row["checksum"],
            )
        return records

    def discover_migrations(self, custom_dir: Optional[Union[str, Path]] = None) -> List[Tuple[int, Path]]:
        """Discovers and sorts all SQL migration files in the migrations directory."""
        target_dir = Path(custom_dir) if custom_dir else self.migrations_dir
        if not target_dir.exists():
            return []

        discovered: List[Tuple[int, Path]] = []
        for file_path in target_dir.glob("*.sql"):
            if not file_path.is_file():
                continue
            match = self.MIGRATION_PATTERN.match(file_path.name)
            if match:
                version = int(match.group(1))
                discovered.append((version, file_path))
            else:
                # Fallback: check for purely numeric or default init
                try:
                    num = int(file_path.stem.split("_")[0])
                    discovered.append((num, file_path))
                except (ValueError, IndexError):
                    discovered.append((1, file_path))

        discovered.sort(key=lambda x: x[0])
        return discovered

    def apply_migration_file(
        self,
        conn: sqlite3.Connection,
        sql_file: Union[str, Path],
        explicit_version: Optional[int] = None,
    ) -> MigrationRecord:
        """Applies a single SQL migration file, checking checksum integrity if already applied.

        Raises:
            MigrationChecksumMismatchError: If file content changed after being applied.
            MigrationError: If script execution fails.
        """
        path = Path(sql_file)
        if not path.is_file():
            raise MigrationError(f"Migration file does not exist: {path}")

        # Determine version
        version = explicit_version
        if version is None:
            match = self.MIGRATION_PATTERN.match(path.name)
            if match:
                version = int(match.group(1))
            else:
                version = 1

        with open(path, "rb") as f:
            raw_bytes = f.read()

        checksum = calculate_sha256(raw_bytes)
        script_text = raw_bytes.decode("utf-8")
        applied = self.get_applied_migrations(conn)

        if version in applied:
            existing = applied[version]
            if existing.checksum != checksum:
                raise MigrationChecksumMismatchError(
                    version=version,
                    recorded_checksum=existing.checksum,
                    actual_checksum=checksum,
                    name=path.name,
                )
            return existing

        # Apply unapplied migration
        try:
            conn.executescript(script_text)
            now = utc_now()
            conn.execute(
                """
                INSERT INTO schema_migrations (version, name, applied_at, checksum)
                VALUES (?, ?, ?, ?);
                """,
                (version, path.name, now, checksum),
            )
            conn.commit()
            return MigrationRecord(
                version=version,
                name=path.name,
                applied_at=now,
                checksum=checksum,
            )
        except Exception as e:
            if not isinstance(e, MigrationError):
                raise MigrationError(f"Failed to execute migration {path.name}: {e}") from e
            raise

    def apply_all(
        self,
        conn: sqlite3.Connection,
        migrations_dir: Optional[Union[str, Path]] = None,
    ) -> List[MigrationRecord]:
        """Discovers and applies all pending migrations in monotonic order."""
        migrations = self.discover_migrations(migrations_dir)
        applied_now: List[MigrationRecord] = []
        applied_map = self.get_applied_migrations(conn)

        for version, path in migrations:
            if version in applied_map:
                # Verify existing integrity
                checksum = calculate_sha256(path)
                existing = applied_map[version]
                if existing.checksum != checksum:
                    raise MigrationChecksumMismatchError(
                        version=version,
                        recorded_checksum=existing.checksum,
                        actual_checksum=checksum,
                        name=path.name,
                    )
            else:
                record = self.apply_migration_file(conn, path, explicit_version=version)
                applied_now.append(record)
                applied_map[version] = record

        return applied_now

    def get_current_version(self, conn: sqlite3.Connection) -> int:
        """Returns the maximum applied migration version, or 0 if none applied."""
        self.ensure_schema_migrations_table(conn)
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(version) AS max_ver FROM schema_migrations;")
        row = cursor.fetchone()
        if row and row["max_ver"] is not None:
            return int(row["max_ver"])
        return 0

    def is_up_to_date(
        self, conn: sqlite3.Connection, migrations_dir: Optional[Union[str, Path]] = None
    ) -> bool:
        """Returns True if all discovered migration files have been applied with matching checksums."""
        discovered = self.discover_migrations(migrations_dir)
        if not discovered:
            return True
        applied = self.get_applied_migrations(conn)
        for version, path in discovered:
            if version not in applied:
                return False
            checksum = calculate_sha256(path)
            if applied[version].checksum != checksum:
                return False
        return True

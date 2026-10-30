"""SACL V1 Package Repository.

Domain 3: Declarative execution package ingestion records (ADR-004, ADR-006).
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Union

from sacl.state.repositories.base import BaseRepository
from sacl.state.utils import json_dumps_safe, json_loads_safe, normalize_repo_path, utc_now

VALID_PACKAGE_STATUSES = frozenset(
    {"RECEIVED", "AUTHENTICATED", "VALIDATED", "REJECTED", "QUARANTINED", "PROCESSED"}
)


class PackageRepository(BaseRepository):
    """Repository managing Domain 3 'packages' table."""

    def record_package(
        self,
        package_id: str,
        archive_sha256: str,
        manifest: Union[Dict[str, Any], str],
        storage_path: str,
        status: str = "RECEIVED",
        job_id: Optional[str] = None,
        project_id: Optional[str] = None,
        created_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Records ingested execution package ZIP archive metadata and manifest."""
        if status not in VALID_PACKAGE_STATUSES:
            raise ValueError(f"Invalid package status: {status}")

        now = created_at or utc_now()
        manifest_str = json_dumps_safe(manifest) if isinstance(manifest, dict) else manifest
        norm_storage = normalize_repo_path(storage_path)

        sql = """
            INSERT INTO packages (
                package_id, job_id, project_id, archive_sha256,
                manifest_json, storage_path, created_at, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(package_id) DO UPDATE SET
                job_id = COALESCE(excluded.job_id, packages.job_id),
                project_id = COALESCE(excluded.project_id, packages.project_id),
                archive_sha256 = excluded.archive_sha256,
                manifest_json = excluded.manifest_json,
                storage_path = excluded.storage_path,
                status = excluded.status;
        """
        self.execute(
            sql,
            (
                package_id,
                job_id,
                project_id,
                archive_sha256,
                manifest_str,
                norm_storage,
                now,
                status,
            ),
        )
        self.commit()
        return self.get_package(package_id)  # type: ignore[return-value]

    def get_package(self, package_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves package record by package ID."""
        sql = "SELECT * FROM packages WHERE package_id = ?;"
        row = self.fetchone_dict(sql, (package_id,))
        if row:
            row["manifest"] = json_loads_safe(row.get("manifest_json"))
        return row

    def get_package_by_sha256(self, archive_sha256: str) -> Optional[Dict[str, Any]]:
        """Retrieves package by SHA-256 integrity hash."""
        sql = "SELECT * FROM packages WHERE archive_sha256 = ? LIMIT 1;"
        row = self.fetchone_dict(sql, (archive_sha256,))
        if row:
            row["manifest"] = json_loads_safe(row.get("manifest_json"))
        return row

    def update_package_status(self, package_id: str, status: str) -> None:
        """Updates package admission lifecycle status."""
        if status not in VALID_PACKAGE_STATUSES:
            raise ValueError(f"Invalid package status: {status}")
        sql = "UPDATE packages SET status = ? WHERE package_id = ?;"
        self.execute(sql, (status, package_id))
        self.commit()

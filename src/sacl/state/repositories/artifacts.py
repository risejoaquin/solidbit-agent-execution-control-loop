"""SACL V1 Artifact Repository.

Domain 11: Relational metadata index for heavy execution artifacts preserved
on the filesystem (ADR-011).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from sacl.contracts.invariants import ArtifactType
from sacl.state.repositories.base import BaseRepository
from sacl.state.utils import normalize_repo_path, utc_now

VALID_ARTIFACT_TYPES = frozenset(a.value for a in ArtifactType)


class ArtifactRepository(BaseRepository):
    """Repository managing Domain 11 'artifacts' table."""

    def record_artifact(
        self,
        run_id: str,
        job_id: str,
        artifact_type: str,
        storage_path: str,
        file_size_bytes: int,
        sha256_hash: str,
        agent_id: Optional[str] = None,
        node_id: Optional[str] = None,
        created_at: Optional[str] = None,
    ) -> int:
        """Indexes heavy filesystem artifact metadata in SQLite."""
        if artifact_type not in VALID_ARTIFACT_TYPES:
            raise ValueError(f"Invalid artifact_type: {artifact_type}")

        now = created_at or utc_now()
        norm_path = normalize_repo_path(storage_path)

        sql = """
            INSERT INTO artifacts (
                run_id, job_id, agent_id, node_id, artifact_type,
                storage_path, file_size_bytes, sha256_hash, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        cursor = self.execute(
            sql,
            (
                run_id,
                job_id,
                agent_id,
                node_id,
                artifact_type,
                norm_path,
                file_size_bytes,
                sha256_hash,
                now,
            ),
        )
        self.commit()
        return cursor.lastrowid  # type: ignore[return-value]

    def get_artifact(self, artifact_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves artifact metadata by artifact ID."""
        sql = "SELECT * FROM artifacts WHERE artifact_id = ?;"
        return self.fetchone_dict(sql, (artifact_id,))

    def list_artifacts_for_run(
        self,
        run_id: str,
        artifact_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Lists indexed artifacts for a run, optionally filtered by type."""
        if artifact_type:
            sql = "SELECT * FROM artifacts WHERE run_id = ? AND artifact_type = ? ORDER BY artifact_id;"
            return self.fetchall_dict(sql, (run_id, artifact_type))
        sql = "SELECT * FROM artifacts WHERE run_id = ? ORDER BY artifact_id;"
        return self.fetchall_dict(sql, (run_id,))

    def get_artifact_by_hash(self, sha256_hash: str) -> Optional[Dict[str, Any]]:
        """Looks up artifact metadata by SHA-256 integrity hash."""
        sql = "SELECT * FROM artifacts WHERE sha256_hash = ? LIMIT 1;"
        return self.fetchone_dict(sql, (sha256_hash,))

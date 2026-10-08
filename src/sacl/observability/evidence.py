"""SACL V1 Evidence Store and Filesystem Artifact Metadata Subsystem.

Enforces ADR-011 and Decision Baseline #23:
- Heavy artifacts stay strictly on the local filesystem (heavy_artifacts_on_filesystem = true).
- SQLite manages 16 structured domains, indexing relative paths, file sizes, and SHA-256 digests.
- Mandatory dual deliverables: SUMMARY.md (human) + SUMMARY.json (machine).
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from sacl.contracts.invariants import HEAVY_ARTIFACTS_ON_FILESYSTEM, ArtifactType
from sacl.observability.events import ARTIFACT_REGISTERED


def compute_file_sha256(file_path: Path, chunk_size: int = 65536) -> str:
    """Calculates SHA-256 cryptographic digest of a file in streaming memory-safe chunks."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


@dataclass
class ArtifactMetadata:
    """Relational index metadata for a heavy filesystem artifact."""

    run_id: str
    job_id: str
    artifact_type: str
    storage_path: str
    file_size_bytes: int
    sha256_hash: str
    created_at: str
    artifact_id: Optional[int] = None
    agent_id: Optional[str] = None
    node_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ArtifactMetadata:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


def infer_artifact_type(file_path: Union[Path, str]) -> str:
    """Infers the canonical ArtifactType from file path name and extension."""
    p = Path(file_path)
    name = p.name.upper()

    if name == "SUMMARY.MD":
        return ArtifactType.SUMMARY_MD.value
    if name == "SUMMARY.JSON":
        return ArtifactType.SUMMARY_JSON.value
    if name.endswith(".REPORT.MD") or "REPORT" in name:
        return ArtifactType.REPORT.value
    if name.endswith(".STDOUT.LOG") or "STDOUT" in name:
        return ArtifactType.LOG_STDOUT.value
    if name.endswith(".STDERR.LOG") or "STDERR" in name:
        return ArtifactType.LOG_STDERR.value
    if name.endswith(".PATCH"):
        return ArtifactType.PATCH.value
    if name.endswith(".DIFF"):
        return ArtifactType.DIFF.value
    if name == "RESPONSE.ZIP" or "RESULT" in name and name.endswith(".ZIP"):
        return ArtifactType.ZIP_RESULT.value
    if name.endswith(".ZIP"):
        return ArtifactType.ZIP_PACKAGE.value
    if "EVIDENCE" in str(p.parent).upper() or name.startswith("FINAL_"):
        return ArtifactType.EVIDENCE.value
    return ArtifactType.OTHER.value


class EvidenceRegistry:
    """Manages filesystem run directories, artifact hashing, integrity checks,

    and metadata indexing into SQLite artifacts domain.
    """

    def __init__(
        self,
        db_source: Union[sqlite3.Connection, Path, str, Callable[[], sqlite3.Connection]],
        artifacts_root: Optional[Path] = None,
    ):
        self._db_source = db_source
        self.artifacts_root = artifacts_root

    def _get_connection(self) -> sqlite3.Connection:
        if isinstance(self._db_source, sqlite3.Connection):
            return self._db_source
        elif callable(self._db_source):
            return self._db_source()
        else:
            conn = sqlite3.connect(str(self._db_source))
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("PRAGMA busy_timeout = 5000;")
            return conn

    @staticmethod
    def setup_run_directory(base_dir: Path, run_id: str) -> Dict[str, Path]:
        """Initializes the canonical run directory layout under artifacts/runs/<runId>/."""
        run_dir = base_dir / "runs" / run_id
        evidence_dir = run_dir / "evidence"
        logs_dir = run_dir / "logs"
        reports_dir = run_dir / "reports"
        state_dir = run_dir / "state"

        for d in (evidence_dir, logs_dir, reports_dir, state_dir):
            d.mkdir(parents=True, exist_ok=True)

        return {
            "run_dir": run_dir,
            "evidence": evidence_dir,
            "logs": logs_dir,
            "reports": reports_dir,
            "state": state_dir,
        }

    def register_artifact(
        self,
        file_path: Union[Path, str],
        run_id: str,
        job_id: str,
        artifact_type: Optional[str] = None,
        agent_id: Optional[str] = None,
        node_id: Optional[str] = None,
        normalize_relative_to: Optional[Path] = None,
    ) -> ArtifactMetadata:
        """Computes file digest and size, recording metadata into SQLite artifacts table.

        Heavy contents remain strictly on the filesystem.
        """
        p = Path(file_path).resolve()
        if not p.is_file():
            raise FileNotFoundError(f"Artifact file does not exist on disk: {p}")

        file_size = p.stat().st_size
        sha256 = compute_file_sha256(p)
        art_type = artifact_type or infer_artifact_type(p)

        # Normalize relative path if root is provided
        if normalize_relative_to:
            try:
                storage_path = str(p.relative_to(normalize_relative_to.resolve())).replace("\\", "/")
            except ValueError:
                storage_path = str(p).replace("\\", "/")
        else:
            storage_path = str(p).replace("\\", "/")

        created_at = datetime.now(timezone.utc).isoformat()

        conn = self._get_connection()
        should_close = not isinstance(self._db_source, sqlite3.Connection) and not callable(self._db_source)

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO artifacts (run_id, job_id, agent_id, node_id, artifact_type, storage_path, file_size_bytes, sha256_hash, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    job_id,
                    agent_id,
                    node_id,
                    art_type,
                    storage_path,
                    file_size,
                    sha256,
                    created_at,
                ),
            )
            artifact_id = cursor.lastrowid
            conn.commit()

            return ArtifactMetadata(
                artifact_id=artifact_id,
                run_id=run_id,
                job_id=job_id,
                agent_id=agent_id,
                node_id=node_id,
                artifact_type=art_type,
                storage_path=storage_path,
                file_size_bytes=file_size,
                sha256_hash=sha256,
                created_at=created_at,
            )
        finally:
            if should_close:
                conn.close()

    def get_artifacts_for_run(self, run_id: str) -> List[ArtifactMetadata]:
        """Retrieves all indexed artifact records for a given run."""
        conn = self._get_connection()
        should_close = not isinstance(self._db_source, sqlite3.Connection) and not callable(self._db_source)

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT artifact_id, run_id, job_id, agent_id, node_id, artifact_type, storage_path, file_size_bytes, sha256_hash, created_at
                FROM artifacts WHERE run_id = ? ORDER BY artifact_id ASC
                """,
                (run_id,),
            )
            rows = cursor.fetchall()
            return [
                ArtifactMetadata(
                    artifact_id=row["artifact_id"],
                    run_id=row["run_id"],
                    job_id=row["job_id"],
                    agent_id=row["agent_id"],
                    node_id=row["node_id"],
                    artifact_type=row["artifact_type"],
                    storage_path=row["storage_path"],
                    file_size_bytes=row["file_size_bytes"],
                    sha256_hash=row["sha256_hash"],
                    created_at=row["created_at"],
                )
                for row in rows
            ]
        finally:
            if should_close:
                conn.close()

    @staticmethod
    def verify_artifact_integrity(
        artifact: ArtifactMetadata,
        base_dir: Optional[Path] = None,
    ) -> Tuple[bool, Optional[str]]:
        """Verifies that an indexed filesystem artifact exists and its SHA-256 matches."""
        target = Path(artifact.storage_path)
        if not target.is_absolute() and base_dir is not None:
            target = base_dir / target

        if not target.is_file():
            return False, f"Artifact file missing from disk: {target}"

        current_size = target.stat().st_size
        if current_size != artifact.file_size_bytes:
            return (
                False,
                f"Artifact size mismatch for {target}: expected {artifact.file_size_bytes} bytes, found {current_size} bytes",
            )

        current_hash = compute_file_sha256(target)
        if current_hash != artifact.sha256_hash:
            return (
                False,
                f"Artifact SHA-256 integrity failure for {target}: expected {artifact.sha256_hash}, found {current_hash}",
            )

        return True, None

    @staticmethod
    def verify_required_output(
        report_path: Union[Path, str],
        min_bytes: int = 1,
    ) -> Tuple[bool, int, Optional[str]]:
        """Evaluates Pillar 3 of 4-part canonical reconciliation ladder:

        Asserts physical existence and non-zero byte size of deliverable markdown report.
        """
        p = Path(report_path)
        if not p.is_file():
            return False, 0, f"Required deliverable report does not exist: {p}"

        size = p.stat().st_size
        if size < min_bytes:
            return False, size, f"Required deliverable report is empty ({size} bytes): {p}"

        return True, size, None

    @staticmethod
    def verify_dual_deliverables(run_dir: Union[Path, str]) -> Tuple[bool, Dict[str, Any]]:
        """Verifies physical presence of both SUMMARY.md and SUMMARY.json in run directory."""
        dir_path = Path(run_dir)
        summary_md = dir_path / "SUMMARY.md"
        summary_json = dir_path / "SUMMARY.json"

        results: Dict[str, Any] = {
            "summary_md_present": summary_md.is_file() and summary_md.stat().st_size > 0,
            "summary_json_present": summary_json.is_file() and summary_json.stat().st_size > 0,
            "json_payload": None,
            "errors": [],
        }

        if not results["summary_md_present"]:
            results["errors"].append("Mandatory deliverable SUMMARY.md is missing or 0 bytes.")

        if not results["summary_json_present"]:
            results["errors"].append("Mandatory deliverable SUMMARY.json is missing or 0 bytes.")
        else:
            try:
                with open(summary_json, "r", encoding="utf-8") as f:
                    results["json_payload"] = json.load(f)
            except Exception as e:
                results["errors"].append(f"SUMMARY.json is invalid JSON: {e}")

        is_valid = results["summary_md_present"] and results["summary_json_present"] and len(results["errors"]) == 0
        return is_valid, results

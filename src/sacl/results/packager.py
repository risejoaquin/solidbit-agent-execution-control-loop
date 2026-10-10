"""SACL V1 Result Packaging Subsystem.

Enforces RESULT_PROTOCOL.md, STATE_MACHINE.md, and ADR-011:
1. Packages final deliverables (SUMMARY.md, SUMMARY.json, reports, logs) into a sealed ZIP bundle.
2. Generates checksums.sha256 manifest within the package.
3. Applies Anti-Zip Slip sanitization on bundled archive paths.
4. Registers package in SQLite artifacts table (Domain 11) and results table (Domain 12).
5. Transitions run status to 'RESULT_PACKAGED'.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import io
import logging
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional, Tuple
import zipfile

from sacl.observability.audit import AuditEventEmitter
from sacl.observability.events import (
    ARTIFACT_REGISTERED,
    Severity,
    create_audit_event,
)
from sacl.observability.evidence import EvidenceRegistry, compute_file_sha256
from sacl.results.models import PackagedResult

logger = logging.getLogger("sacl.results.packager")

# Windows reserved device names
RESERVED_DEVICE_NAMES = frozenset({
    "con", "prn", "aux", "nul",
    "com1", "com2", "com3", "com4", "com5", "com6", "com7", "com8", "com9",
    "lpt1", "lpt2", "lpt3", "lpt4", "lpt5", "lpt6", "lpt7", "lpt8", "lpt9",
})


def sanitize_archive_entry_path(rel_path: str) -> str:
    """Sanitizes an archive path, rejecting Zip-Slip traversal or invalid device names."""
    clean = rel_path.strip().replace("\\", "/")
    # Reject path traversal
    parts = clean.split("/")
    if any(p == ".." for p in parts):
        raise ValueError(f"Anti-Zip Slip Violation: path '{rel_path}' contains directory traversal '..'")
    # Reject drive letters or absolute paths
    if clean.startswith("/") or (len(clean) >= 2 and clean[1] == ":"):
        raise ValueError(f"Anti-Zip Slip Violation: path '{rel_path}' is absolute")
    # Reject reserved Windows device names
    for part in parts:
        base = part.split(".", 1)[0].lower()
        if base in RESERVED_DEVICE_NAMES:
            raise ValueError(f"Reserved device name violation: '{base}' in '{rel_path}'")
    return clean


class ResultPackager:
    """Packages run deliverables into a sealed result archive and records metadata."""

    def __init__(
        self,
        evidence_registry: Optional[EvidenceRegistry] = None,
        audit_emitter: Optional[AuditEventEmitter] = None,
    ) -> None:
        self.evidence_registry = evidence_registry
        self.audit_emitter = audit_emitter

    def package_run_results(
        self,
        run_id: str,
        job_id: str,
        run_dir: Path,
        summary_md_path: Path,
        summary_json_path: Path,
        final_verdict: str,
        db_conn: Optional[sqlite3.Connection] = None,
        additional_files: Optional[List[Path]] = None,
        output_zip_name: Optional[str] = None,
    ) -> PackagedResult:
        """Packages run deliverables into response.zip or <run_id>-result.zip.

        Returns:
            PackagedResult containing zip path, file size, SHA-256 hash, and paths.
        """
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        zip_name = output_zip_name or f"{run_id}-result.zip"
        zip_path = run_dir / zip_name

        # Collect files to package
        files_to_pack: List[Tuple[Path, str]] = [
            (summary_md_path, "SUMMARY.md"),
            (summary_json_path, "SUMMARY.json"),
        ]

        # Include deliverable reports
        reports_dir = run_dir / "reports"
        if reports_dir.exists():
            for report in reports_dir.glob("*.md"):
                files_to_pack.append((report, f"reports/{report.name}"))

        # Include logs
        logs_dir = run_dir / "logs"
        if logs_dir.exists():
            for log_file in logs_dir.glob("*.log"):
                files_to_pack.append((log_file, f"logs/{log_file.name}"))

        # Include additional files
        if additional_files:
            for extra in additional_files:
                if extra.exists():
                    rel = extra.relative_to(run_dir) if run_dir in extra.parents else extra.name
                    files_to_pack.append((extra, str(rel).replace("\\", "/")))

        # Build checksums.sha256 manifest
        checksum_lines: List[str] = []
        for file_path, archive_name in files_to_pack:
            if file_path.exists():
                h = compute_file_sha256(file_path)
                clean_name = sanitize_archive_entry_path(archive_name)
                checksum_lines.append(f"{h}  {clean_name}")

        checksums_content = "\n".join(checksum_lines) + "\n"

        # Create ZIP archive
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for file_path, archive_name in files_to_pack:
                if file_path.exists():
                    clean_name = sanitize_archive_entry_path(archive_name)
                    zf.write(file_path, arcname=clean_name)
            # Add checksums manifest
            zf.writestr("checksums.sha256", checksums_content)

        # Compute archive metrics
        file_size_bytes = zip_path.stat().st_size
        sha256_hash = compute_file_sha256(zip_path)

        norm_zip_path = str(zip_path).replace("\\", "/")
        norm_md_path = str(summary_md_path).replace("\\", "/")
        norm_json_path = str(summary_json_path).replace("\\", "/")

        # Record in SQLite Operational Store
        if db_conn:
            cursor = db_conn.cursor()

            # Domain 11: artifacts table
            cursor.execute(
                """
                INSERT INTO artifacts (
                    run_id, job_id, artifact_type, storage_path, file_size_bytes, sha256_hash, created_at
                ) VALUES (?, ?, 'ZIP_RESULT', ?, ?, ?, ?)
                """,
                (run_id, job_id, norm_zip_path, file_size_bytes, sha256_hash, now_iso),
            )

            # Domain 12: results table
            cursor.execute(
                """
                INSERT INTO results (
                    job_id, run_id, status, final_verdict, summary_md_path, summary_json_path,
                    package_result_zip, created_at
                ) VALUES (?, ?, 'RESULT_PACKAGED', ?, ?, ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                    status = excluded.status,
                    final_verdict = excluded.final_verdict,
                    summary_md_path = excluded.summary_md_path,
                    summary_json_path = excluded.summary_json_path,
                    package_result_zip = excluded.package_result_zip;
                """,
                (
                    job_id,
                    run_id,
                    final_verdict,
                    norm_md_path,
                    norm_json_path,
                    norm_zip_path,
                    now_iso,
                ),
            )

            # Update runs table lifecycle status to RESULT_PACKAGED
            cursor.execute(
                "UPDATE runs SET status = 'RESULT_PACKAGED' WHERE run_id = ?",
                (run_id,),
            )

            # Update jobs table lifecycle status to RESULT_PACKAGED
            cursor.execute(
                "UPDATE jobs SET status = 'RESULT_PACKAGED', updated_at = ? WHERE job_id = ?",
                (now_iso, job_id),
            )

            db_conn.commit()

        # Emit audit event
        if self.audit_emitter:
            self.audit_emitter.emit(
                event_type="RESULT_PACKAGED",
                severity=Severity.INFO,
                job_id=job_id,
                run_id=run_id,
                payload={
                    "zip_path": norm_zip_path,
                    "file_size_bytes": file_size_bytes,
                    "sha256_hash": sha256_hash,
                    "final_verdict": final_verdict,
                },
            )

        logger.info(
            "Sealed result package for run %s at %s (%d bytes, sha256=%s...)",
            run_id,
            norm_zip_path,
            file_size_bytes,
            sha256_hash[:12],
        )

        return PackagedResult(
            run_id=run_id,
            job_id=job_id,
            zip_path=zip_path,
            file_size_bytes=file_size_bytes,
            sha256_hash=sha256_hash,
            summary_md_path=summary_md_path,
            summary_json_path=summary_json_path,
            created_at=now_iso,
        )


__all__ = ["ResultPackager", "sanitize_archive_entry_path"]

"""SACL V1 Package Staging Pipeline.

Coordinates:
1. Cryptographic archive SHA-256 computation.
2. At-least-once duplicate & replay detection.
3. Anti-Zip Slip, resource limits, and declarative manifest validation.
4. Safe extraction to isolated staging directory (packages/inbox/<package_id>_<timestamp>/).
5. Checksums cryptographic integrity verification.
6. Fail-closed quarantine isolation for security violations.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import json
import os
from pathlib import Path
import shutil
from typing import Any, Dict, Optional
import zipfile

from sacl.contracts.invariants import JobStatus, MailStatus
from sacl.contracts.models import Manifest
from sacl.package.exceptions import (
    PackageError,
    PackageIntegrityMismatchError,
    ZipResourceLimitExceeded,
)
from sacl.package.idempotency import (
    DuplicateCheckResult,
    DuplicateStatus,
    IDuplicateDetector,
)
from sacl.package.limits import PackageResourceLimits
from sacl.package.quarantine import IQuarantineManager, QuarantineManager, QuarantineOutcome
from sacl.package.validator import PackageValidator, compute_sha256


class StagingOutcome(str, Enum):
    """Lifecycle outcome of package staging process."""

    VALIDATED = "VALIDATED"
    DUPLICATE_IGNORED = "DUPLICATE_IGNORED"
    QUARANTINED = "QUARANTINED"
    REJECTED = "REJECTED"


@dataclass
class StagingResult:
    """Detailed result of package staging and validation pipeline."""

    outcome: StagingOutcome
    job_id: str
    archive_sha256: str
    package_id: Optional[str] = None
    staged_dir: Optional[Path] = None
    manifest: Optional[Manifest] = None
    quarantine_outcome: Optional[QuarantineOutcome] = None
    duplicate_info: Optional[DuplicateCheckResult] = None
    message: str = ""

    @property
    def is_success(self) -> bool:
        return self.outcome == StagingOutcome.VALIDATED


class PackageStagingPipeline:
    """Full-lifecycle package intake and staging pipeline."""

    def __init__(
        self,
        staging_base_dir: Path,
        validator: Optional[PackageValidator] = None,
        quarantine_manager: Optional[IQuarantineManager] = None,
        duplicate_detector: Optional[IDuplicateDetector] = None,
        limits: Optional[PackageResourceLimits] = None,
    ) -> None:
        self.staging_base_dir = Path(staging_base_dir)
        self.staging_base_dir.mkdir(parents=True, exist_ok=True)
        self.limits = limits or PackageResourceLimits()
        self.validator = validator or PackageValidator(limits=self.limits)
        self.quarantine_manager = quarantine_manager or QuarantineManager(
            self.staging_base_dir.parent / "quarantine"
        )
        self.duplicate_detector = duplicate_detector

    def process_intake(
        self,
        zip_path: Path,
        expected_job_id: Optional[str] = None,
        nonce: Optional[str] = None,
        message_id: Optional[str] = None,
    ) -> StagingResult:
        """Processes an incoming package archive through validation, deduplication, and staging."""
        zip_path = Path(zip_path)
        if not zip_path.exists():
            raise FileNotFoundError(f"Package ZIP archive does not exist: {zip_path}")

        archive_sha256 = compute_sha256(zip_path)

        # 1. Early resource limit check on raw archive size
        raw_size = zip_path.stat().st_size
        if raw_size > self.limits.max_archive_size_bytes:
            q_outcome = self.quarantine_manager.quarantine(
                source_path=zip_path,
                reason_code="ZIP_RESOURCE_LIMIT_EXCEEDED",
                message=f"Archive size {raw_size} exceeds quota of {self.limits.max_archive_size_bytes} bytes",
                job_id=expected_job_id,
                archive_sha256=archive_sha256,
            )
            return StagingResult(
                outcome=StagingOutcome.QUARANTINED,
                job_id=expected_job_id or "UNKNOWN",
                archive_sha256=archive_sha256,
                quarantine_outcome=q_outcome,
                message=q_outcome.message,
            )

        # 2. Check duplicate / replay if expected_job_id provided
        if expected_job_id and self.duplicate_detector:
            dup = self.duplicate_detector.check_duplicate(
                job_id=expected_job_id,
                archive_sha256=archive_sha256,
                nonce=nonce,
                message_id=message_id,
            )
            if dup.status == DuplicateStatus.DUPLICATE_IGNORED:
                return StagingResult(
                    outcome=StagingOutcome.DUPLICATE_IGNORED,
                    job_id=expected_job_id,
                    archive_sha256=archive_sha256,
                    package_id=dup.existing_package_id,
                    duplicate_info=dup,
                    message=dup.message,
                )
            elif dup.status in (DuplicateStatus.CONFLICT, DuplicateStatus.NONCE_REPLAY):
                q_outcome = self.quarantine_manager.quarantine(
                    source_path=zip_path,
                    reason_code="JOB_ID_HASH_MISMATCH",
                    message=dup.message,
                    job_id=expected_job_id,
                    archive_sha256=archive_sha256,
                    details={"existing_sha256": dup.existing_sha256, "duplicate_status": dup.status.value},
                )
                return StagingResult(
                    outcome=StagingOutcome.QUARANTINED,
                    job_id=expected_job_id,
                    archive_sha256=archive_sha256,
                    quarantine_outcome=q_outcome,
                    duplicate_info=dup,
                    message=dup.message,
                )

        # 3. Validate archive (traversal, device names, symlinks, binaries, quotas, manifest schema)
        try:
            manifest = self.validator.validate_archive(zip_path)
        except Exception as err:
            reason_code = getattr(err, "reason_code", "PACKAGE_VALIDATION_FAILURE")
            details = getattr(err, "details", {})
            pkg_id = getattr(err, "package_id", None)
            q_outcome = self.quarantine_manager.quarantine(
                source_path=zip_path,
                reason_code=reason_code,
                message=str(err),
                package_id=pkg_id,
                job_id=expected_job_id,
                archive_sha256=archive_sha256,
                details=details,
            )
            return StagingResult(
                outcome=StagingOutcome.QUARANTINED,
                job_id=expected_job_id or "UNKNOWN",
                package_id=pkg_id,
                archive_sha256=archive_sha256,
                quarantine_outcome=q_outcome,
                message=str(err),
            )

        # 4. Routing hint verification: manifest job_id must match expected_job_id if given
        if expected_job_id and manifest.job_id != expected_job_id:
            msg = (
                f"Routing hint mismatch: Transport indicated job_id '{expected_job_id}', "
                f"but manifest declared job_id '{manifest.job_id}'"
            )
            q_outcome = self.quarantine_manager.quarantine(
                source_path=zip_path,
                reason_code="MANIFEST_VALIDATION_ERROR",
                message=msg,
                package_id=manifest.package_id,
                job_id=expected_job_id,
                archive_sha256=archive_sha256,
            )
            return StagingResult(
                outcome=StagingOutcome.QUARANTINED,
                job_id=expected_job_id,
                package_id=manifest.package_id,
                archive_sha256=archive_sha256,
                quarantine_outcome=q_outcome,
                message=msg,
            )

        # 5. Check duplicate with manifest.job_id if not checked earlier
        if not expected_job_id and self.duplicate_detector:
            dup = self.duplicate_detector.check_duplicate(
                job_id=manifest.job_id,
                archive_sha256=archive_sha256,
                nonce=nonce,
                message_id=message_id,
            )
            if dup.status == DuplicateStatus.DUPLICATE_IGNORED:
                return StagingResult(
                    outcome=StagingOutcome.DUPLICATE_IGNORED,
                    job_id=manifest.job_id,
                    package_id=manifest.package_id,
                    archive_sha256=archive_sha256,
                    duplicate_info=dup,
                    message=dup.message,
                )
            elif dup.status in (DuplicateStatus.CONFLICT, DuplicateStatus.NONCE_REPLAY):
                q_outcome = self.quarantine_manager.quarantine(
                    source_path=zip_path,
                    reason_code="JOB_ID_HASH_MISMATCH",
                    message=dup.message,
                    package_id=manifest.package_id,
                    job_id=manifest.job_id,
                    archive_sha256=archive_sha256,
                    details={"existing_sha256": dup.existing_sha256, "duplicate_status": dup.status.value},
                )
                return StagingResult(
                    outcome=StagingOutcome.QUARANTINED,
                    job_id=manifest.job_id,
                    package_id=manifest.package_id,
                    archive_sha256=archive_sha256,
                    quarantine_outcome=q_outcome,
                    duplicate_info=dup,
                    message=dup.message,
                )

        # 6. Safe extraction into isolated staging directory
        timestamp_slug = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        staged_dir = self.staging_base_dir / f"{manifest.package_id}_{timestamp_slug}"
        staged_dir.mkdir(parents=True, exist_ok=True)

        try:
            self._safe_extract(zip_path, staged_dir)
        except Exception as err:
            shutil.rmtree(staged_dir, ignore_errors=True)
            reason_code = getattr(err, "reason_code", "ZIP_RESOURCE_LIMIT_EXCEEDED")
            q_outcome = self.quarantine_manager.quarantine(
                source_path=zip_path,
                reason_code=reason_code,
                message=f"Safe extraction failed: {err}",
                package_id=manifest.package_id,
                job_id=manifest.job_id,
                archive_sha256=archive_sha256,
            )
            return StagingResult(
                outcome=StagingOutcome.QUARANTINED,
                job_id=manifest.job_id,
                package_id=manifest.package_id,
                archive_sha256=archive_sha256,
                quarantine_outcome=q_outcome,
                message=f"Extraction failure: {err}",
            )

        # 7. Checksums cryptographic integrity verification
        try:
            self.validator.verify_checksums(staged_dir, manifest.checksums_file)
        except PackageIntegrityMismatchError as pime:
            q_outcome = self.quarantine_manager.quarantine(
                source_path=staged_dir,
                reason_code=pime.reason_code,
                message=pime.message,
                package_id=manifest.package_id,
                job_id=manifest.job_id,
                archive_sha256=archive_sha256,
                details=pime.details,
            )
            shutil.rmtree(staged_dir, ignore_errors=True)
            return StagingResult(
                outcome=StagingOutcome.QUARANTINED,
                job_id=manifest.job_id,
                package_id=manifest.package_id,
                archive_sha256=archive_sha256,
                quarantine_outcome=q_outcome,
                message=pime.message,
            )

        # 8. Record intake in duplicate detector
        if self.duplicate_detector:
            self.duplicate_detector.record_intake(
                job_id=manifest.job_id,
                archive_sha256=archive_sha256,
                status=JobStatus.VALIDATED.value,
                package_id=manifest.package_id,
                nonce=nonce,
                message_id=message_id,
                storage_path=str(staged_dir),
                manifest_json=json.dumps(manifest.to_dict()),
            )

        return StagingResult(
            outcome=StagingOutcome.VALIDATED,
            job_id=manifest.job_id,
            package_id=manifest.package_id,
            staged_dir=staged_dir,
            manifest=manifest,
            archive_sha256=archive_sha256,
            message="Package intake, security checks, and staging validated successfully.",
        )

    def _safe_extract(self, zip_path: Path, destination_dir: Path) -> None:
        """Extracts ZIP archive safely while enforcing quotas and canonical directory bounds."""
        dest_canonical = destination_dir.resolve()
        dest_str = str(dest_canonical)
        bytes_written = 0

        with zipfile.ZipFile(zip_path, "r") as zf:
            for entry in zf.infolist():
                name = entry.filename

                # Verify canonical destination path again
                norm_name = name.replace("\\", "/").lstrip("/")
                target_path = (dest_canonical / norm_name).resolve()
                target_str = str(target_path)
                if not (target_str == dest_str or target_str.startswith(dest_str + os.sep)):
                    raise PackageError(
                        f"Zip Slip prevented during extraction: '{name}'",
                        reason_code="ZIP_PATH_TRAVERSAL_DETECTED",
                    )

                if entry.is_dir():
                    target_path.mkdir(parents=True, exist_ok=True)
                    continue

                target_path.parent.mkdir(parents=True, exist_ok=True)

                # Stream and enforce uncompressed limit chunk by chunk
                with zf.open(entry, "r") as source, open(target_path, "wb") as target:
                    while chunk := source.read(65536):
                        bytes_written += len(chunk)
                        if bytes_written > self.limits.max_uncompressed_size_bytes:
                            raise ZipResourceLimitExceeded(
                                package_id="UNKNOWN",
                                reason=(
                                    f"Uncompressed stream exceeded limit of "
                                    f"{self.limits.max_uncompressed_size_bytes} bytes during extraction"
                                ),
                            )
                        target.write(chunk)

"""SACL V1 Archive Admission Controller.

Orchestrates complete archive admission and quarantine gating for incoming wave packages:
- Resource exhaustion & zip bomb quotas validation (25MB archive / 100MB uncompressed / 1000 files)
- Entry-by-entry Anti-Zip Slip, DOS device, ADS colon, and symlink defenses
- SHA-256 integrity calculation
- Manifest presence, schema validation, and declarative package authority enforcement
- At-least-once delivery idempotency and SHA-256 hash conflict detection
- Safe extraction to isolated staging directory
"""

from __future__ import annotations

import hashlib
import io
import json
import logging
import zipfile
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from sacl.contracts.exceptions import ContractValidationError
from sacl.contracts.schema_validator import SchemaValidator, get_default_validator
from sacl.security.exceptions import (
    ArchiveAdmissionError,
    InvalidFilenameSecurityError,
    PathTraversalSecurityError,
    ResourceLimitExceededError,
    SymlinkSecurityError,
)
from sacl.security.path_sanitizer import (
    validate_safe_path,
)
from sacl.security.redaction import assert_zero_secrets
from sacl.security.resource_limits import (
    ResourceLimitValidator,
    ResourceQuotas,
    StreamingExtractionBudgetTracker,
)

logger = logging.getLogger("sacl.security.admission")


class AdmissionStatus(str, Enum):
    """Authoritative outcome of the archive admission inspection."""

    ADMITTED = "ADMITTED"
    DUPLICATE_IGNORED = "DUPLICATE_IGNORED"
    REJECTED_RESOURCE_QUOTA = "REJECTED_RESOURCE_QUOTA"
    REJECTED_TRAVERSAL_FAIL = "REJECTED_TRAVERSAL_FAIL"
    REJECTED_INVALID_FILENAME = "REJECTED_INVALID_FILENAME"
    REJECTED_SYMLINK = "REJECTED_SYMLINK"
    REJECTED_HASH_CONFLICT = "REJECTED_HASH_CONFLICT"
    REJECTED_MANIFEST_INVALID = "REJECTED_MANIFEST_INVALID"
    REJECTED_CORRUPT_ARCHIVE = "REJECTED_CORRUPT_ARCHIVE"
    QUARANTINED = "QUARANTINED"


@dataclass
class AdmissionDecision:
    """Detailed decision and artifacts emitted by ArchiveAdmissionController."""

    admitted: bool
    status: AdmissionStatus
    package_id: str
    job_id: Optional[str] = None
    sha256: str = ""
    staging_path: Optional[Path] = None
    manifest_data: Optional[Dict[str, Any]] = None
    extracted_files: List[Path] = field(default_factory=list)
    rejection_reason: Optional[str] = None
    violation_code: Optional[str] = None


class ArchiveAdmissionController:
    """Security admission controller for incoming package ZIP archives."""

    def __init__(
        self,
        resource_quotas: Optional[ResourceQuotas] = None,
        schema_validator: Optional[SchemaValidator] = None,
        existing_package_lookup: Optional[Callable[[str], Optional[str]]] = None,
    ) -> None:
        """Args:

        resource_quotas: Configured quotas or canonical defaults.
        schema_validator: JSON schema validator for manifest.json.
        existing_package_lookup: Optional callable (job_id) -> existing_sha256 for idempotency checks.
        """
        self.quotas = resource_quotas or ResourceQuotas()
        self.resource_validator = ResourceLimitValidator(self.quotas)
        self.schema_validator = schema_validator
        self.existing_package_lookup = existing_package_lookup

    def compute_sha256(self, source: Union[bytes, Path, str]) -> str:
        """Computes SHA-256 hash of archive source."""
        h = hashlib.sha256()
        if isinstance(source, (bytes, bytearray)):
            h.update(source)
        else:
            with open(Path(source), "rb") as f:
                while chunk := f.read(65536):
                    h.update(chunk)
        return h.hexdigest().lower()

    def admit_and_stage(
        self,
        archive_source: Union[bytes, Path, str],
        staging_dir: Union[Path, str],
        package_id: str = "unknown",
        fail_closed: bool = True,
    ) -> AdmissionDecision:
        """Runs complete admission security pipeline and extracts admitted packages.

        If fail_closed is True, security violations raise typed SecurityError exceptions.
        If fail_closed is False, returns AdmissionDecision with admitted=False and status details.
        """
        staging_root = Path(staging_dir).resolve()

        # Step 0: Open archive and compute SHA-256
        try:
            sha256_hash = self.compute_sha256(archive_source)
        except Exception as e:
            msg = f"Cannot compute SHA-256 on archive: {e}"
            if fail_closed:
                raise ArchiveAdmissionError(
                    package_id, msg, violation_code=AdmissionStatus.REJECTED_CORRUPT_ARCHIVE.value
                ) from e
            return AdmissionDecision(
                admitted=False,
                status=AdmissionStatus.REJECTED_CORRUPT_ARCHIVE,
                package_id=package_id,
                rejection_reason=msg,
                violation_code=AdmissionStatus.REJECTED_CORRUPT_ARCHIVE.value,
            )

        if isinstance(archive_source, (bytes, bytearray)):
            compressed_size = len(archive_source)
            try:
                zf = zipfile.ZipFile(io.BytesIO(archive_source), "r")
            except Exception as e:
                msg = f"Failed to open zip archive from memory: {e}"
                if fail_closed:
                    raise ArchiveAdmissionError(
                        package_id,
                        msg,
                        violation_code=AdmissionStatus.REJECTED_CORRUPT_ARCHIVE.value,
                    ) from e
                return AdmissionDecision(
                    admitted=False,
                    status=AdmissionStatus.REJECTED_CORRUPT_ARCHIVE,
                    package_id=package_id,
                    sha256=sha256_hash,
                    rejection_reason=msg,
                    violation_code=AdmissionStatus.REJECTED_CORRUPT_ARCHIVE.value,
                )
        else:
            p = Path(archive_source)
            if not p.exists():
                msg = f"Archive file does not exist: {p}"
                if fail_closed:
                    raise ArchiveAdmissionError(package_id, msg, violation_code="ARCHIVE_NOT_FOUND")
                return AdmissionDecision(
                    admitted=False,
                    status=AdmissionStatus.REJECTED_CORRUPT_ARCHIVE,
                    package_id=package_id,
                    rejection_reason=msg,
                    violation_code="ARCHIVE_NOT_FOUND",
                )
            compressed_size = p.stat().st_size
            try:
                zf = zipfile.ZipFile(p, "r")
            except Exception as e:
                msg = f"Failed to open zip file at '{p}': {e}"
                if fail_closed:
                    raise ArchiveAdmissionError(
                        package_id,
                        msg,
                        violation_code=AdmissionStatus.REJECTED_CORRUPT_ARCHIVE.value,
                    ) from e
                return AdmissionDecision(
                    admitted=False,
                    status=AdmissionStatus.REJECTED_CORRUPT_ARCHIVE,
                    package_id=package_id,
                    sha256=sha256_hash,
                    rejection_reason=msg,
                    violation_code=AdmissionStatus.REJECTED_CORRUPT_ARCHIVE.value,
                )

        with zf:
            # Step 1: Resource Quotas (Decompression Bomb Defense)
            try:
                self.resource_validator.validate_archive_metadata(
                    zf=zf,
                    compressed_size=compressed_size,
                    package_id=package_id,
                )
            except ResourceLimitExceededError as e:
                if fail_closed:
                    raise
                return AdmissionDecision(
                    admitted=False,
                    status=AdmissionStatus.REJECTED_RESOURCE_QUOTA,
                    package_id=package_id,
                    sha256=sha256_hash,
                    rejection_reason=str(e),
                    violation_code="ZIP_RESOURCE_LIMIT_EXCEEDED",
                )

            # Step 2: Entry-by-entry structural inspection (Anti-Zip Slip, DOS devices, symlinks)
            for info in zf.infolist():
                try:
                    validate_safe_path(
                        entry_name=info.filename,
                        destination_root=staging_root,
                        package_id=package_id,
                        external_attr=info.external_attr,
                    )
                except PathTraversalSecurityError as e:
                    if fail_closed:
                        raise
                    return AdmissionDecision(
                        admitted=False,
                        status=AdmissionStatus.REJECTED_TRAVERSAL_FAIL,
                        package_id=package_id,
                        sha256=sha256_hash,
                        rejection_reason=str(e),
                        violation_code="ZIP_PATH_TRAVERSAL_DETECTED",
                    )
                except InvalidFilenameSecurityError as e:
                    if fail_closed:
                        raise
                    return AdmissionDecision(
                        admitted=False,
                        status=AdmissionStatus.REJECTED_INVALID_FILENAME,
                        package_id=package_id,
                        sha256=sha256_hash,
                        rejection_reason=str(e),
                        violation_code="INVALID_FILENAME_CHARACTER",
                    )
                except SymlinkSecurityError as e:
                    if fail_closed:
                        raise
                    return AdmissionDecision(
                        admitted=False,
                        status=AdmissionStatus.REJECTED_SYMLINK,
                        package_id=package_id,
                        sha256=sha256_hash,
                        rejection_reason=str(e),
                        violation_code="SYMLINK_NOT_PERMITTED",
                    )

            # Step 3: Manifest Validation & Declarative Authority Check
            manifest_info = None
            for info in zf.infolist():
                if info.filename.lower() in ("manifest.json", "./manifest.json"):
                    manifest_info = info
                    break

            if not manifest_info:
                msg = "Archive is missing required root manifest.json"
                if fail_closed:
                    raise ArchiveAdmissionError(package_id, msg, violation_code="MANIFEST_MISSING")
                return AdmissionDecision(
                    admitted=False,
                    status=AdmissionStatus.REJECTED_MANIFEST_INVALID,
                    package_id=package_id,
                    sha256=sha256_hash,
                    rejection_reason=msg,
                    violation_code="MANIFEST_MISSING",
                )

            try:
                manifest_raw = zf.read(manifest_info).decode("utf-8")
                manifest_data = json.loads(manifest_raw)
            except Exception as e:
                msg = f"Failed to parse manifest.json: {e}"
                if fail_closed:
                    raise ArchiveAdmissionError(
                        package_id, msg, violation_code="MANIFEST_PARSE_ERROR"
                    ) from e
                return AdmissionDecision(
                    admitted=False,
                    status=AdmissionStatus.REJECTED_MANIFEST_INVALID,
                    package_id=package_id,
                    sha256=sha256_hash,
                    rejection_reason=msg,
                    violation_code="MANIFEST_PARSE_ERROR",
                )

            # Check zero secrets in manifest
            try:
                assert_zero_secrets(manifest_data, context=f"manifest.json of {package_id}")
            except Exception as e:
                if fail_closed:
                    raise
                return AdmissionDecision(
                    admitted=False,
                    status=AdmissionStatus.QUARANTINED,
                    package_id=package_id,
                    sha256=sha256_hash,
                    rejection_reason=str(e),
                    violation_code="SECRET_IN_MANIFEST",
                )

            job_id = manifest_data.get("job_id")
            resolved_pkg_id = manifest_data.get("package_id", package_id)

            # Declarative Authority Rule (SB-FREEZE-P1-02): packages cannot self-authorize scripts
            if "authorized_scripts" in manifest_data:
                msg = "Package contains prohibited field 'authorized_scripts'. Packages are declarative only."
                if fail_closed:
                    raise ArchiveAdmissionError(
                        resolved_pkg_id,
                        msg,
                        violation_code="SELF_AUTHORIZING_SCRIPTS_PROHIBITED",
                    )
                return AdmissionDecision(
                    admitted=False,
                    status=AdmissionStatus.REJECTED_MANIFEST_INVALID,
                    package_id=resolved_pkg_id,
                    job_id=job_id,
                    sha256=sha256_hash,
                    manifest_data=manifest_data,
                    rejection_reason=msg,
                    violation_code="SELF_AUTHORIZING_SCRIPTS_PROHIBITED",
                )

            # Validate against manifest JSON schema if validator provided or available
            validator = self.schema_validator
            if validator is None:
                try:
                    validator = get_default_validator()
                except Exception:
                    validator = None

            if validator is not None:
                try:
                    validator.validate("manifest", manifest_data)
                except ContractValidationError as e:
                    msg = f"manifest.json schema validation failed: {e.validation_errors}"
                    if fail_closed:
                        raise ArchiveAdmissionError(
                            resolved_pkg_id,
                            msg,
                            violation_code="MANIFEST_SCHEMA_VIOLATION",
                            details={"validation_errors": e.validation_errors},
                        ) from e
                    return AdmissionDecision(
                        admitted=False,
                        status=AdmissionStatus.REJECTED_MANIFEST_INVALID,
                        package_id=resolved_pkg_id,
                        job_id=job_id,
                        sha256=sha256_hash,
                        manifest_data=manifest_data,
                        rejection_reason=msg,
                        violation_code="MANIFEST_SCHEMA_VIOLATION",
                    )

            # Step 4: Idempotency & SHA-256 Conflict Detection
            if job_id and self.existing_package_lookup is not None:
                existing_sha = self.existing_package_lookup(job_id)
                if existing_sha is not None:
                    if existing_sha.lower() == sha256_hash.lower():
                        # Idempotent re-delivery: same job_id and same hash
                        logger.info(
                            "Idempotent package re-delivery for job %s (hash %s)",
                            job_id,
                            sha256_hash,
                        )
                        return AdmissionDecision(
                            admitted=True,
                            status=AdmissionStatus.DUPLICATE_IGNORED,
                            package_id=resolved_pkg_id,
                            job_id=job_id,
                            sha256=sha256_hash,
                            manifest_data=manifest_data,
                            staging_path=None,
                        )
                    else:
                        # Conflicting delivery: same job_id but different hash
                        msg = (
                            f"Hash conflict for job '{job_id}': stored hash {existing_sha} "
                            f"differs from incoming hash {sha256_hash}"
                        )
                        if fail_closed:
                            raise ArchiveAdmissionError(
                                resolved_pkg_id,
                                msg,
                                violation_code=AdmissionStatus.REJECTED_HASH_CONFLICT.value,
                            )
                        return AdmissionDecision(
                            admitted=False,
                            status=AdmissionStatus.REJECTED_HASH_CONFLICT,
                            package_id=resolved_pkg_id,
                            job_id=job_id,
                            sha256=sha256_hash,
                            manifest_data=manifest_data,
                            rejection_reason=msg,
                            violation_code=AdmissionStatus.REJECTED_HASH_CONFLICT.value,
                        )

            # Step 5: Safe Extraction to Isolated Staging Directory
            staging_root.mkdir(parents=True, exist_ok=True)
            extracted_files: List[Path] = []
            budget_tracker = StreamingExtractionBudgetTracker(
                max_total_bytes=self.quotas.max_uncompressed_bytes,
                package_id=resolved_pkg_id,
            )

            for member in zf.infolist():
                target_path = (staging_root / member.filename).resolve()
                if member.is_dir():
                    target_path.mkdir(parents=True, exist_ok=True)
                else:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(member) as src, open(target_path, "wb") as dst:
                        while chunk := src.read(65536):
                            budget_tracker.add_bytes(len(chunk))
                            dst.write(chunk)
                    extracted_files.append(target_path)

            return AdmissionDecision(
                admitted=True,
                status=AdmissionStatus.ADMITTED,
                package_id=resolved_pkg_id,
                job_id=job_id,
                sha256=sha256_hash,
                staging_path=staging_root,
                manifest_data=manifest_data,
                extracted_files=extracted_files,
            )

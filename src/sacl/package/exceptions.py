"""SACL V1 Package Intake Typed Exceptions.

All package intake security violations trigger quarantine outcomes
and inherit from QuarantineError and SaclError.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from sacl.contracts.exceptions import QuarantineError


class PackageError(QuarantineError):
    """Base exception for all package intake, validation, and staging errors."""

    def __init__(
        self,
        reason: str,
        reason_code: str = "PACKAGE_ERROR",
        package_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        pkg_id = package_id or "UNKNOWN"
        super().__init__(package_id=pkg_id, reason=reason)
        self.reason_code = reason_code
        self.reason = reason
        if details:
            self.details.update(details)
        self.details["reason_code"] = reason_code


class ZipResourceLimitExceeded(PackageError):
    """Raised when archive violates resource quotas (size, uncompressed size, count, ratio)."""

    def __init__(
        self,
        package_id: str,
        reason: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            reason=reason,
            reason_code="ZIP_RESOURCE_LIMIT_EXCEEDED",
            package_id=package_id,
            details=details,
        )


class ZipPathTraversalError(PackageError):
    """Raised when archive member attempts Zip Slip or path traversal outside destination directory."""

    def __init__(
        self,
        package_id: str,
        reason: str,
        violations: Optional[List[str]] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        merged = {"violations": violations or []}
        if details:
            merged.update(details)
        super().__init__(
            reason=reason,
            reason_code="ZIP_PATH_TRAVERSAL_DETECTED",
            package_id=package_id,
            details=merged,
        )
        self.violations = violations or []


class InvalidFilenameError(PackageError):
    """Raised when member filename matches DOS reserved device names or contains ADS colons."""

    def __init__(
        self,
        package_id: str,
        reason: str,
        offending_name: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        merged = {"offending_name": offending_name}
        if details:
            merged.update(details)
        super().__init__(
            reason=reason,
            reason_code="INVALID_FILENAME_CHARACTER",
            package_id=package_id,
            details=merged,
        )
        self.offending_name = offending_name


class SymlinkNotPermittedError(PackageError):
    """Raised when archive contains Unix symlinks or Windows reparse points."""

    def __init__(
        self,
        package_id: str,
        entry_name: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        merged = {"entry_name": entry_name}
        if details:
            merged.update(details)
        super().__init__(
            reason=f"Symlink or reparse point not permitted: '{entry_name}'",
            reason_code="SYMLINK_NOT_PERMITTED",
            package_id=package_id,
            details=merged,
        )
        self.entry_name = entry_name


class ProhibitedBinaryError(PackageError):
    """Raised when archive contains uninspected binary executables (.exe, .dll, .cmd, .msi)."""

    def __init__(
        self,
        package_id: str,
        entry_name: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        merged = {"entry_name": entry_name}
        if details:
            merged.update(details)
        super().__init__(
            reason=f"Prohibited executable binary member: '{entry_name}'",
            reason_code="PROHIBITED_BINARY_ATTACHMENT",
            package_id=package_id,
            details=merged,
        )
        self.entry_name = entry_name


class PackageIntegrityMismatchError(PackageError):
    """Raised when checksums.sha256 verification fails or expected assets are missing/tampered."""

    def __init__(
        self,
        package_id: str,
        reason: str,
        mismatched_files: Optional[List[str]] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        merged = {"mismatched_files": mismatched_files or []}
        if details:
            merged.update(details)
        super().__init__(
            reason=reason,
            reason_code="PACKAGE_INTEGRITY_MISMATCH",
            package_id=package_id,
            details=merged,
        )
        self.mismatched_files = mismatched_files or []


class ManifestValidationError(PackageError):
    """Raised when manifest.json fails JSON schema validation or is malformed."""

    def __init__(
        self,
        package_id: str,
        reason: str,
        errors: Optional[List[str]] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        merged = {"validation_errors": errors or []}
        if details:
            merged.update(details)
        super().__init__(
            reason=reason,
            reason_code="MANIFEST_VALIDATION_ERROR",
            package_id=package_id,
            details=merged,
        )
        self.validation_errors = errors or []


class DeclarativeAuthorityViolationError(PackageError):
    """Raised when package attempts self-authorization (e.g. including authorized_scripts)."""

    def __init__(
        self,
        package_id: str,
        reason: str = "Package contains forbidden authority field 'authorized_scripts'. Package authority remains declarative.",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            reason=reason,
            reason_code="DECLARATIVE_AUTHORITY_VIOLATION",
            package_id=package_id,
            details=details,
        )


class ReplayConflictError(PackageError):
    """Raised when a package with an existing job_id is received with a different SHA-256 hash."""

    def __init__(
        self,
        job_id: str,
        new_sha256: str,
        existing_sha256: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        reason = f"Job ID '{job_id}' hash mismatch (existing: {existing_sha256[:12]}..., incoming: {new_sha256[:12]}...)"
        merged = {"existing_sha256": existing_sha256, "new_sha256": new_sha256}
        if details:
            merged.update(details)
        super().__init__(
            reason=reason,
            reason_code="JOB_ID_HASH_MISMATCH",
            package_id=job_id,
            details=merged,
        )
        self.job_id = job_id
        self.new_sha256 = new_sha256
        self.existing_sha256 = existing_sha256

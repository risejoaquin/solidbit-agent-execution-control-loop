"""SACL V1 Package Subsystem.

Provides package intake and staging validation:
- Canonical limits and decompression quotas
- Zip slip and anti-traversal inspection
- Windows DOS device name and ADS defenses
- Symlink, reparse point, and uninspected binary prohibitions
- Declarative package authority enforcement (no self-authorized code)
- Checksums cryptographic SHA-256 asset verification
- At-least-once duplicate and replay detection interfaces
- Fail-closed quarantine outcomes and manager
- End-to-end package staging pipeline
"""

from sacl.package.exceptions import (
    DeclarativeAuthorityViolationError,
    InvalidFilenameError,
    ManifestValidationError,
    PackageError,
    PackageIntegrityMismatchError,
    ProhibitedBinaryError,
    ReplayConflictError,
    SymlinkNotPermittedError,
    ZipPathTraversalError,
    ZipResourceLimitExceeded,
)
from sacl.package.idempotency import (
    DuplicateCheckResult,
    DuplicateStatus,
    IDuplicateDetector,
    InMemoryDuplicateDetector,
    SQLiteDuplicateDetector,
)
from sacl.package.limits import (
    MAX_ARCHIVE_SIZE_BYTES,
    MAX_COMPRESSION_RATIO,
    MAX_FILE_COUNT,
    MAX_UNCOMPRESSED_SIZE_BYTES,
    PROHIBITED_BINARY_EXTENSIONS,
    RESERVED_DEVICE_NAMES,
    PackageResourceLimits,
    has_alternate_data_stream,
    is_prohibited_binary,
    is_reserved_device_name,
    is_symlink_or_reparse,
)
from sacl.package.quarantine import (
    IQuarantineManager,
    QuarantineManager,
    QuarantineOutcome,
)
from sacl.package.staging import (
    PackageStagingPipeline,
    StagingOutcome,
    StagingResult,
)
from sacl.package.validator import (
    PackageValidator,
    compute_bytes_sha256,
    compute_sha256,
)

__all__ = [
    # Limits & Constants
    "MAX_ARCHIVE_SIZE_BYTES",
    "MAX_UNCOMPRESSED_SIZE_BYTES",
    "MAX_FILE_COUNT",
    "MAX_COMPRESSION_RATIO",
    "RESERVED_DEVICE_NAMES",
    "PROHIBITED_BINARY_EXTENSIONS",
    "PackageResourceLimits",
    "is_reserved_device_name",
    "has_alternate_data_stream",
    "is_prohibited_binary",
    "is_symlink_or_reparse",
    # Exceptions
    "PackageError",
    "ZipResourceLimitExceeded",
    "ZipPathTraversalError",
    "InvalidFilenameError",
    "SymlinkNotPermittedError",
    "ProhibitedBinaryError",
    "PackageIntegrityMismatchError",
    "ManifestValidationError",
    "DeclarativeAuthorityViolationError",
    "ReplayConflictError",
    # Validator
    "PackageValidator",
    "compute_sha256",
    "compute_bytes_sha256",
    # Idempotency
    "DuplicateStatus",
    "DuplicateCheckResult",
    "IDuplicateDetector",
    "InMemoryDuplicateDetector",
    "SQLiteDuplicateDetector",
    # Quarantine
    "QuarantineOutcome",
    "IQuarantineManager",
    "QuarantineManager",
    # Staging Pipeline
    "StagingOutcome",
    "StagingResult",
    "PackageStagingPipeline",
]

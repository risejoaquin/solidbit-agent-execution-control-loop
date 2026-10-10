"""SACL V1 Package Quarantine Outcomes and Manager.

Isolates untrusted or malicious archives/payloads violating security policies
into dedicated quarantine directories with forensic metadata.
"""

from __future__ import annotations

import abc
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
from typing import Any, Dict, List, Optional

from sacl.contracts.invariants import JobSideStatus, MailStatus


@dataclass
class QuarantineOutcome:
    """Structured result of a quarantine action."""

    quarantined: bool
    reason_code: str
    message: str
    package_id: Optional[str] = None
    job_id: Optional[str] = None
    archive_sha256: Optional[str] = None
    quarantine_dir: Optional[Path] = None
    metadata_file: Optional[Path] = None
    quarantined_file: Optional[Path] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    details: Dict[str, Any] = field(default_factory=dict)
    job_status: str = JobSideStatus.QUARANTINED.value
    mail_status: str = MailStatus.QUARANTINED.value

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.quarantine_dir:
            d["quarantine_dir"] = str(self.quarantine_dir)
        if self.metadata_file:
            d["metadata_file"] = str(self.metadata_file)
        if self.quarantined_file:
            d["quarantined_file"] = str(self.quarantined_file)
        return d


class IQuarantineManager(abc.ABC):
    """Abstract interface for managing quarantined package artifacts."""

    @abc.abstractmethod
    def quarantine(
        self,
        source_path: Path,
        reason_code: str,
        message: str,
        package_id: Optional[str] = None,
        job_id: Optional[str] = None,
        archive_sha256: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> QuarantineOutcome:
        """Isolates offending package and writes forensic metadata."""
        pass


class QuarantineManager(IQuarantineManager):
    """Manages file isolation and forensic metadata for quarantined packages."""

    def __init__(self, quarantine_base_dir: Path) -> None:
        self.quarantine_base_dir = Path(quarantine_base_dir)

    def quarantine(
        self,
        source_path: Path,
        reason_code: str,
        message: str,
        package_id: Optional[str] = None,
        job_id: Optional[str] = None,
        archive_sha256: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> QuarantineOutcome:
        """Copies or moves offending source to quarantine directory and records metadata."""
        timestamp_slug = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        safe_id = (package_id or job_id or "unidentified").replace("/", "_").replace("\\", "_")
        target_dir = self.quarantine_base_dir / f"{timestamp_slug}_{safe_id}"
        target_dir.mkdir(parents=True, exist_ok=True)

        quarantined_file_path: Optional[Path] = None

        if source_path.exists():
            if source_path.is_file():
                dest_file = target_dir / source_path.name
                shutil.copy2(source_path, dest_file)
                quarantined_file_path = dest_file
            elif source_path.is_dir():
                dest_subdir = target_dir / "extracted_contents"
                shutil.copytree(source_path, dest_subdir, dirs_exist_ok=True)
                quarantined_file_path = dest_subdir

        metadata_file = target_dir / "QUARANTINE_METADATA.json"
        outcome = QuarantineOutcome(
            quarantined=True,
            reason_code=reason_code,
            message=message,
            package_id=package_id,
            job_id=job_id,
            archive_sha256=archive_sha256,
            quarantine_dir=target_dir,
            metadata_file=metadata_file,
            quarantined_file=quarantined_file_path,
            details=details or {},
        )

        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(outcome.to_dict(), f, indent=2)

        return outcome

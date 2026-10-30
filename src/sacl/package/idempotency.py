"""SACL V1 Duplicate and Replay Detection Interfaces and Implementations.

Enforces at-least-once delivery idempotency per docs/SECURITY_MODEL.md §6:
1. (Same JOB_ID + Same SHA-256) or Same Message-ID -> DUPLICATE_IGNORED.
2. Same JOB_ID + Different SHA-256 -> CONFLICT (JOB_ID_HASH_MISMATCH).
3. New JOB_ID -> NEW.
4. Nonce replay with mismatched payload -> NONCE_REPLAY.
"""

from __future__ import annotations

import abc
import sqlite3
import threading
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Union


class DuplicateStatus(str, Enum):
    """Outcomes of duplicate and replay inspection."""

    NEW = "NEW"
    DUPLICATE_IGNORED = "DUPLICATE_IGNORED"
    CONFLICT = "CONFLICT"
    NONCE_REPLAY = "NONCE_REPLAY"


@dataclass(frozen=True)
class DuplicateCheckResult:
    """Detailed result of duplicate and replay verification."""

    status: DuplicateStatus
    job_id: str
    archive_sha256: str
    message: str
    existing_status: Optional[str] = None
    existing_sha256: Optional[str] = None
    existing_package_id: Optional[str] = None


class IDuplicateDetector(abc.ABC):
    """Abstract interface for duplicate and replay detection."""

    @abc.abstractmethod
    def check_duplicate(
        self,
        job_id: str,
        archive_sha256: str,
        nonce: Optional[str] = None,
        message_id: Optional[str] = None,
    ) -> DuplicateCheckResult:
        """Verifies whether incoming job/archive has been seen before."""
        pass

    @abc.abstractmethod
    def record_intake(
        self,
        job_id: str,
        archive_sha256: str,
        status: str,
        package_id: Optional[str] = None,
        nonce: Optional[str] = None,
        message_id: Optional[str] = None,
        storage_path: Optional[str] = None,
        manifest_json: Optional[str] = None,
    ) -> None:
        """Records intake event in tracking store."""
        pass


class InMemoryDuplicateDetector(IDuplicateDetector):
    """Thread-safe in-memory duplicate and replay detector for unit testing."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self._nonces: Dict[str, Dict[str, Any]] = {}
        self._messages: Dict[str, Dict[str, Any]] = {}

    def check_duplicate(
        self,
        job_id: str,
        archive_sha256: str,
        nonce: Optional[str] = None,
        message_id: Optional[str] = None,
    ) -> DuplicateCheckResult:
        with self._lock:
            # Check by message_id first if provided
            if message_id and message_id in self._messages:
                existing = self._messages[message_id]
                if existing["archive_sha256"] == archive_sha256:
                    return DuplicateCheckResult(
                        status=DuplicateStatus.DUPLICATE_IGNORED,
                        job_id=job_id,
                        archive_sha256=archive_sha256,
                        message=f"Message ID '{message_id}' already processed with identical hash. Ignored.",
                        existing_status=existing.get("status"),
                        existing_sha256=existing["archive_sha256"],
                        existing_package_id=existing.get("package_id"),
                    )

            # Check by nonce
            if nonce and nonce in self._nonces:
                existing_nonce = self._nonces[nonce]
                if (
                    existing_nonce["archive_sha256"] != archive_sha256
                    or existing_nonce["job_id"] != job_id
                ):
                    return DuplicateCheckResult(
                        status=DuplicateStatus.NONCE_REPLAY,
                        job_id=job_id,
                        archive_sha256=archive_sha256,
                        message=f"Anti-replay nonce '{nonce}' replayed with mismatched payload.",
                        existing_status=existing_nonce.get("status"),
                        existing_sha256=existing_nonce["archive_sha256"],
                        existing_package_id=existing_nonce.get("package_id"),
                    )

            # Check by job_id
            if job_id in self._jobs:
                existing_job = self._jobs[job_id]
                existing_hash = existing_job["archive_sha256"]
                if existing_hash == archive_sha256:
                    return DuplicateCheckResult(
                        status=DuplicateStatus.DUPLICATE_IGNORED,
                        job_id=job_id,
                        archive_sha256=archive_sha256,
                        message=f"Job '{job_id}' already ingested with identical SHA-256. Ignored.",
                        existing_status=existing_job.get("status"),
                        existing_sha256=existing_hash,
                        existing_package_id=existing_job.get("package_id"),
                    )
                else:
                    return DuplicateCheckResult(
                        status=DuplicateStatus.CONFLICT,
                        job_id=job_id,
                        archive_sha256=archive_sha256,
                        message=(
                            f"JOB_ID_HASH_MISMATCH: Job '{job_id}' previously ingested with "
                            f"hash {existing_hash[:12]}..., incoming has {archive_sha256[:12]}..."
                        ),
                        existing_status=existing_job.get("status"),
                        existing_sha256=existing_hash,
                        existing_package_id=existing_job.get("package_id"),
                    )

            return DuplicateCheckResult(
                status=DuplicateStatus.NEW,
                job_id=job_id,
                archive_sha256=archive_sha256,
                message=f"Job '{job_id}' is a new intake request.",
            )

    def record_intake(
        self,
        job_id: str,
        archive_sha256: str,
        status: str,
        package_id: Optional[str] = None,
        nonce: Optional[str] = None,
        message_id: Optional[str] = None,
        storage_path: Optional[str] = None,
        manifest_json: Optional[str] = None,
    ) -> None:
        with self._lock:
            record = {
                "job_id": job_id,
                "archive_sha256": archive_sha256,
                "status": status,
                "package_id": package_id,
                "storage_path": storage_path,
                "manifest_json": manifest_json,
            }
            self._jobs[job_id] = record
            if nonce:
                self._nonces[nonce] = record
            if message_id:
                self._messages[message_id] = record


class SQLiteDuplicateDetector(IDuplicateDetector):
    """SQLite-backed duplicate and replay detector inspecting packages and mail_messages."""

    def __init__(self, connection_or_path: Union[sqlite3.Connection, Path, str]) -> None:
        if isinstance(connection_or_path, sqlite3.Connection):
            self._conn = connection_or_path
            self._close_on_exit = False
        else:
            self._conn = sqlite3.connect(str(connection_or_path), check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._close_on_exit = True
        self._lock = threading.Lock()

    def check_duplicate(
        self,
        job_id: str,
        archive_sha256: str,
        nonce: Optional[str] = None,
        message_id: Optional[str] = None,
    ) -> DuplicateCheckResult:
        with self._lock:
            cursor = self._conn.cursor()

            # 1. Check message_id in mail_messages if table exists
            if message_id:
                try:
                    cursor.execute(
                        "SELECT message_id, attachment_sha, status, job_id FROM mail_messages WHERE message_id = ?",
                        (message_id,),
                    )
                    row = cursor.fetchone()
                    if row:
                        if row["attachment_sha"] == archive_sha256:
                            return DuplicateCheckResult(
                                status=DuplicateStatus.DUPLICATE_IGNORED,
                                job_id=job_id,
                                archive_sha256=archive_sha256,
                                message=f"Message ID '{message_id}' already processed with identical hash. Ignored.",
                                existing_status=row["status"],
                                existing_sha256=row["attachment_sha"],
                            )
                except sqlite3.OperationalError:
                    pass

            # 2. Check nonce in mail_messages
            if nonce:
                try:
                    cursor.execute(
                        "SELECT nonce, attachment_sha, status, job_id FROM mail_messages WHERE nonce = ?",
                        (nonce,),
                    )
                    row = cursor.fetchone()
                    if row:
                        if row["attachment_sha"] != archive_sha256 or (
                            row["job_id"] and row["job_id"] != job_id
                        ):
                            return DuplicateCheckResult(
                                status=DuplicateStatus.NONCE_REPLAY,
                                job_id=job_id,
                                archive_sha256=archive_sha256,
                                message=f"Anti-replay nonce '{nonce}' replayed with mismatched payload.",
                                existing_status=row["status"],
                                existing_sha256=row["attachment_sha"],
                            )
                except sqlite3.OperationalError:
                    pass

            # 3. Check job_id in packages table
            try:
                cursor.execute(
                    "SELECT package_id, job_id, archive_sha256, status FROM packages WHERE job_id = ?",
                    (job_id,),
                )
                row = cursor.fetchone()
                if row:
                    existing_hash = row["archive_sha256"]
                    if existing_hash == archive_sha256:
                        return DuplicateCheckResult(
                            status=DuplicateStatus.DUPLICATE_IGNORED,
                            job_id=job_id,
                            archive_sha256=archive_sha256,
                            message=f"Job '{job_id}' already recorded in packages with identical SHA-256. Ignored.",
                            existing_status=row["status"],
                            existing_sha256=existing_hash,
                            existing_package_id=row["package_id"],
                        )
                    else:
                        return DuplicateCheckResult(
                            status=DuplicateStatus.CONFLICT,
                            job_id=job_id,
                            archive_sha256=archive_sha256,
                            message=(
                                f"JOB_ID_HASH_MISMATCH: Job '{job_id}' previously recorded with "
                                f"hash {existing_hash[:12]}..., incoming has {archive_sha256[:12]}..."
                            ),
                            existing_status=row["status"],
                            existing_sha256=existing_hash,
                            existing_package_id=row["package_id"],
                        )
            except sqlite3.OperationalError:
                pass

            return DuplicateCheckResult(
                status=DuplicateStatus.NEW,
                job_id=job_id,
                archive_sha256=archive_sha256,
                message=f"Job '{job_id}' is a new intake request.",
            )

    def record_intake(
        self,
        job_id: str,
        archive_sha256: str,
        status: str,
        package_id: Optional[str] = None,
        nonce: Optional[str] = None,
        message_id: Optional[str] = None,
        storage_path: Optional[str] = None,
        manifest_json: Optional[str] = None,
    ) -> None:
        with self._lock:
            cursor = self._conn.cursor()
            pkg_id = package_id or job_id
            now_str = sqlite3.datetime.datetime.utcnow().isoformat() + "Z"

            # Insert or update packages table
            try:
                cursor.execute(
                    """
                    INSERT INTO packages (package_id, job_id, archive_sha256, manifest_json, storage_path, created_at, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(package_id) DO UPDATE SET
                        status = excluded.status,
                        storage_path = excluded.storage_path
                    """,
                    (
                        pkg_id,
                        job_id,
                        archive_sha256,
                        manifest_json or "{}",
                        storage_path or "",
                        now_str,
                        status,
                    ),
                )
            except sqlite3.OperationalError:
                pass

            # Insert or update jobs table (parent FK for mail_messages)
            try:
                cursor.execute(
                    """
                    INSERT INTO jobs (job_id, package_id, status, priority, created_at, updated_at)
                    VALUES (?, ?, ?, 0, ?, ?)
                    ON CONFLICT(job_id) DO UPDATE SET
                        status = excluded.status,
                        package_id = excluded.package_id,
                        updated_at = excluded.updated_at
                    """,
                    (job_id, pkg_id, status, now_str, now_str),
                )
            except (sqlite3.OperationalError, sqlite3.IntegrityError):
                pass

            # Insert into mail_messages if message_id and nonce are provided
            if message_id and nonce:
                try:
                    cursor.execute(
                        """
                        INSERT INTO mail_messages (
                            message_id, sender, recipient, subject, received_at,
                            nonce, attachment_sha, status, job_id
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(message_id) DO UPDATE SET status = excluded.status
                        """,
                        (
                            message_id,
                            "uniquedraken@gmail.com",
                            "uniquedraken@gmail.com",
                            f"[SACL][JOB][v1][{job_id}]",
                            now_str,
                            nonce,
                            archive_sha256,
                            status,
                            job_id,
                        ),
                    )
                except (sqlite3.OperationalError, sqlite3.IntegrityError):
                    pass

            self._conn.commit()

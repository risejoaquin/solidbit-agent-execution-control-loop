"""SACL V1 Idempotency & Deduplication Engine.

Implements ADR-010 at-least-once delivery semantics, multi-tiered inbound deduplication,
payload conflict defense, anti-replay nonce validation, and monotonic cursor guards.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Union

from sacl.state.repositories.base import BaseRepository
from sacl.state.repositories.jobs import JobRepository
from sacl.state.repositories.mail import MailRepository
from sacl.state.repositories.packages import PackageRepository
from sacl.state.repositories.runs import RunRepository
from sacl.state.utils import utc_now


class InboundAction(str, Enum):
    DUPLICATE_IGNORED = "DUPLICATE_IGNORED"
    PAYLOAD_CONFLICT_REJECTED = "PAYLOAD_CONFLICT_REJECTED"
    ATTEMPT_STAGED = "ATTEMPT_STAGED"
    ACCEPTED_QUEUED = "ACCEPTED_QUEUED"


@dataclass(frozen=True)
class InboundEvaluationResult:
    action: InboundAction
    job_id: str
    package_sha256: str
    message: str
    existing_package_id: Optional[str] = None
    attempt_number: int = 1


class IdempotencyHelper(BaseRepository):
    """Enforces idempotency and anti-replay invariants across transport and execution tiers."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        super().__init__(conn)
        self.mail_repo = MailRepository(conn)
        self.job_repo = JobRepository(conn)
        self.package_repo = PackageRepository(conn)
        self.run_repo = RunRepository(conn)

    def is_nonce_seen(self, nonce: str) -> bool:
        """Verifies if anti-replay cryptographic nonce has already been received."""
        msg = self.mail_repo.get_message_by_nonce(nonce)
        if msg is not None:
            return True
        sql_inbox = "SELECT message_id FROM mail_inbox WHERE nonce = ? LIMIT 1;"
        return bool(self.fetchone_dict(sql_inbox, (nonce,)))

    def evaluate_inbound_package(
        self,
        job_id: str,
        package_sha256: str,
        nonce: Optional[str] = None,
        is_explicit_retry: bool = False,
    ) -> InboundEvaluationResult:
        """Evaluates an incoming package against ADR-010 deduplication ladder.

        1. Duplicate Redelivery: Same JOB_ID AND identical SHA-256 hash -> DUPLICATE_IGNORED.
        2. Conflicting Resubmission: Same JOB_ID AND different SHA-256 hash -> PAYLOAD_CONFLICT_REJECTED.
        3. Legitimate Retry / Recovery: Same JOB_ID with explicit retry -> ATTEMPT_STAGED.
        4. Novel Job: Unseen JOB_ID AND unseen hash -> ACCEPTED_QUEUED.
        """
        existing_job = self.job_repo.get_job(job_id)

        if existing_job:
            existing_pkg_id = existing_job.get("package_id")
            existing_pkg = (
                self.package_repo.get_package(existing_pkg_id) if existing_pkg_id else None
            )

            if existing_pkg:
                existing_sha = existing_pkg.get("archive_sha256", "")
                if existing_sha == package_sha256:
                    if is_explicit_retry:
                        # Legitimate retry with identical verified package
                        existing_runs = self.run_repo.list_runs(job_id=job_id)
                        attempt_num = len(existing_runs) + 1
                        return InboundEvaluationResult(
                            action=InboundAction.ATTEMPT_STAGED,
                            job_id=job_id,
                            package_sha256=package_sha256,
                            message=f"Legitimate retry for job '{job_id}' (attempt {attempt_num}).",
                            existing_package_id=existing_pkg_id,
                            attempt_number=attempt_num,
                        )
                    # Benign redelivery
                    return InboundEvaluationResult(
                        action=InboundAction.DUPLICATE_IGNORED,
                        job_id=job_id,
                        package_sha256=package_sha256,
                        message=f"Duplicate redelivery for job '{job_id}' with identical package hash.",
                        existing_package_id=existing_pkg_id,
                    )
                else:
                    # Conflicting resubmission (same job_id, different payload hash)
                    return InboundEvaluationResult(
                        action=InboundAction.PAYLOAD_CONFLICT_REJECTED,
                        job_id=job_id,
                        package_sha256=package_sha256,
                        message=(
                            f"Conflicting payload for job '{job_id}': existing hash '{existing_sha}' "
                            f"conflicts with incoming hash '{package_sha256}'."
                        ),
                        existing_package_id=existing_pkg_id,
                    )

        # Job not seen yet: Novel Job
        return InboundEvaluationResult(
            action=InboundAction.ACCEPTED_QUEUED,
            job_id=job_id,
            package_sha256=package_sha256,
            message=f"Novel execution package accepted for job '{job_id}'.",
            attempt_number=1,
        )

    def advance_history_cursor_monotonic(
        self,
        cursor_name: str,
        new_history_id: str,
        expiration_at: Optional[str] = None,
        resource_id: Optional[str] = None,
    ) -> bool:
        """Advances Gmail historyId cursor guaranteeing monotonic progress."""
        existing = self.mail_repo.get_cursor(cursor_name)
        if existing:
            current_hid = existing.get("history_id", "0")
            try:
                # Monotonic numeric comparison
                if int(new_history_id) < int(current_hid):
                    return False  # Regressive cursor update rejected
            except ValueError:
                # Fallback to string comparison
                if new_history_id < current_hid:
                    return False

        self.mail_repo.advance_cursor(
            cursor_name=cursor_name,
            history_id=new_history_id,
            expiration_at=expiration_at,
            resource_id=resource_id,
        )
        return True

    def atomic_transition(
        self,
        table: str,
        id_column: str,
        id_value: Any,
        expected_status: Union[str, Sequence[str]],
        target_status: str,
        extra_updates: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Atomically transitions an entity's status iff current status matches expected_status."""
        now = utc_now()
        set_clauses = (
            ["status = ?", "updated_at = ?"]
            if "updated_at" in self._get_table_columns(table)
            else ["status = ?"]
        )
        params: List[Any] = [target_status]
        if "updated_at" in self._get_table_columns(table):
            params.append(now)

        if extra_updates:
            for col, val in extra_updates.items():
                set_clauses.append(f"{col} = ?")
                params.append(val)

        if isinstance(expected_status, str):
            where_status = "status = ?"
            status_params = [expected_status]
        else:
            placeholders = ", ".join("?" for _ in expected_status)
            where_status = f"status IN ({placeholders})"
            status_params = list(expected_status)

        params.append(id_value)
        params.extend(status_params)

        sql = f"""
            UPDATE {table}
            SET {", ".join(set_clauses)}
            WHERE {id_column} = ? AND {where_status};
        """
        cursor = self.execute(sql, params)
        self.commit()
        return cursor.rowcount > 0

    def _get_table_columns(self, table: str) -> List[str]:
        """Returns column names for a SQLite table."""
        cursor = self.execute(f"PRAGMA table_info({table});")
        return [row["name"] for row in cursor.fetchall()]

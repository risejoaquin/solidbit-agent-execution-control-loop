"""SACL V1 4-Dimensional Run Status Reconciler.

Implements IReconciler from sacl.contracts.interfaces adhering to:
- RESULT_PROTOCOL.md (4-point canonical reconciliation)
- Invariant: Run success NEVER depends on process exit code alone ($Process.ExitCode == 0).
- PID Recycling defense (3-way check, process image whitelist, max 300s drift).
- 6-Priority Verdict Extraction Ladder.
- Semantic rules: DONE_REVIEW_REQUIRED never means PASS; PASS (Report Present) legacy fallback.
- Validation against schemas/result.schema.json.
"""

from __future__ import annotations

from datetime import datetime, timezone
import logging
from pathlib import Path
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from sacl.contracts.exceptions import ContractValidationError
from sacl.contracts.interfaces import IReconciler
from sacl.contracts.invariants import (
    ALLOWED_PROCESS_IMAGES,
    HEADER_STATUS_REGEX,
    PID_DRIFT_TOLERANCE_SECONDS,
    VERDICT_REGEX,
    Verdict,
)
from sacl.contracts.models import (
    PersistedState,
    ProcessObservation,
    ReconciledResult,
    ReconciliationData,
    RequiredOutputs,
    VerdictExtraction,
    WorktreeState,
)
from sacl.contracts.reconciliation import (
    extract_verdict_from_content,
    verify_process_observation,
)
from sacl.contracts.schema_validator import SchemaValidator, get_default_validator

logger = logging.getLogger("sacl.results.reconciler")

# Pattern for review required marker
REVIEW_REQUIRED_REGEX = re.compile(
    r"(?:REVIEW_REQUIRED|DONE_REVIEW_REQUIRED|Review\s*Required|Needs\s*Review)",
    re.IGNORECASE,
)


class ResultReconciler(IReconciler):
    """Authoritative 4-dimensional run and agent status reconciliation engine."""

    def __init__(self, validator: Optional[SchemaValidator] = None) -> None:
        self.validator = validator or get_default_validator()

    def reconcile(
        self,
        run_id: str,
        agent_id: str,
        pid: Optional[int],
        process_name: str,
        is_active: bool,
        exit_code: Optional[int],
        persisted_start_time: Optional[Union[str, datetime]],
        actual_start_time: Optional[datetime],
        persisted_status: str,
        report_path: Path,
        stdout_path: Path,
        stderr_path: Path,
        worktree_path: Path,
        job_id: Optional[str] = None,
        node_id: Optional[str] = None,
        stage_id: Optional[Any] = None,
        persisted_verdict: Optional[str] = None,
        branch: Optional[str] = None,
        commit_sha: Optional[str] = None,
        modified_files: Optional[List[str]] = None,
        is_clean: bool = True,
        finished_at: Optional[str] = None,
    ) -> ReconciledResult:
        """Evaluates all 4 pillars and returns canonical reconciled verdict."""
        # ---------------------------------------------------------------------
        # PILLAR 1: Process Observation & PID Recycling Defense
        # ---------------------------------------------------------------------
        process_obs, is_valid_obs, obs_error = verify_process_observation(
            pid=pid,
            process_name=process_name,
            is_active=is_active,
            exit_code=exit_code,
            persisted_start_time=persisted_start_time,
            actual_start_time=actual_start_time,
            allowed_images=ALLOWED_PROCESS_IMAGES,
            drift_tolerance_seconds=PID_DRIFT_TOLERANCE_SECONDS,
        )

        # ---------------------------------------------------------------------
        # PILLAR 2: Persisted Agent State
        # ---------------------------------------------------------------------
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        start_iso = (
            persisted_start_time
            if isinstance(persisted_start_time, str)
            else (
                persisted_start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                if persisted_start_time
                else now_iso
            )
        )
        if start_iso and not start_iso.endswith("Z"):
            start_iso = f"{start_iso}Z"

        persisted_state = PersistedState(
            status=persisted_status,
            started_at=start_iso,
            updated_at=now_iso,
            finished_at=finished_at or (now_iso if not is_active else None),
        )

        # ---------------------------------------------------------------------
        # PILLAR 3: Required Outputs (Physical Filesystem Evidence)
        # ---------------------------------------------------------------------
        report_exists = report_path.exists()
        report_size_bytes = report_path.stat().st_size if report_exists else 0
        expected_files_verified = report_exists and report_size_bytes > 0

        required_outputs = RequiredOutputs(
            report_path=str(report_path).replace("\\", "/"),
            report_exists=report_exists,
            report_size_bytes=report_size_bytes,
            stdout_path=str(stdout_path).replace("\\", "/"),
            stderr_path=str(stderr_path).replace("\\", "/"),
            expected_files_verified=expected_files_verified,
        )

        # ---------------------------------------------------------------------
        # PILLAR 4: Final Verdict Extraction (Priority Ladder)
        # ---------------------------------------------------------------------
        report_content = None
        if report_exists:
            try:
                report_content = report_path.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                logger.warning("Failed to read report %s: %s", report_path, e)

        stdout_content = None
        if stdout_path.exists():
            try:
                stdout_content = stdout_path.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                logger.warning("Failed to read stdout %s: %s", stdout_path, e)

        stderr_content = None
        if stderr_path.exists():
            try:
                stderr_content = stderr_path.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                logger.warning("Failed to read stderr %s: %s", stderr_path, e)

        verdict_ext = self._extract_verdict_with_review_semantics(
            report_content=report_content,
            stdout_content=stdout_content,
            stderr_content=stderr_content,
            report_exists=report_exists,
            report_size_bytes=report_size_bytes,
            exit_code=exit_code,
            persisted_verdict=persisted_verdict,
            is_valid_obs=is_valid_obs,
            obs_error=obs_error,
        )

        # ---------------------------------------------------------------------
        # Lifecycle Status Derivation
        # ---------------------------------------------------------------------
        final_verdict = verdict_ext.verdict
        error_msg = obs_error

        if final_verdict in {Verdict.PASS.value, Verdict.PASS_REPORT_PRESENT.value}:
            status = "SUCCEEDED"
        elif final_verdict == Verdict.PARTIAL.value:
            status = "SUCCEEDED"
        elif final_verdict == Verdict.DONE_REVIEW_REQUIRED.value:
            status = "COMPLETE"
        elif final_verdict == Verdict.BLOCKED.value:
            status = "BLOCKED"
        elif final_verdict == Verdict.STOPPED_BY_USER.value:
            status = "STOPPED"
        elif is_active:
            status = "RUNNING"
        else:
            status = "FAILED"
            if not expected_files_verified and not error_msg:
                error_msg = f"Deliverable report missing or 0 bytes: {report_path}"

        # ---------------------------------------------------------------------
        # Worktree State Construction
        # ---------------------------------------------------------------------
        wt_state = WorktreeState(
            branch=branch or "HEAD",
            worktree_path=str(worktree_path).replace("\\", "/"),
            commit_sha=commit_sha,
            is_clean=is_clean,
            modified_files=list(modified_files or []),
        )

        # Ensure start_time_drift_seconds is int or None
        if process_obs.start_time_drift_seconds is not None:
            process_obs.start_time_drift_seconds = int(round(process_obs.start_time_drift_seconds))

        recon_data = ReconciliationData(
            process_observation=process_obs,
            persisted_state=persisted_state,
            required_outputs=required_outputs,
            verdict_extraction=verdict_ext,
        )

        result = ReconciledResult(
            run_id=run_id,
            agent_id=agent_id,
            job_id=job_id,
            node_id=node_id,
            stage_id=stage_id,
            status=status,
            result_verdict=final_verdict,
            reconciliation=recon_data,
            worktree=wt_state,
            error_message=error_msg,
        )

        # Validate against result.schema.json
        self.validate_schema(result)
        return result

    def _extract_verdict_with_review_semantics(
        self,
        report_content: Optional[str],
        stdout_content: Optional[str],
        stderr_content: Optional[str],
        report_exists: bool,
        report_size_bytes: int,
        exit_code: Optional[int],
        persisted_verdict: Optional[str],
        is_valid_obs: bool,
        obs_error: Optional[str],
    ) -> VerdictExtraction:
        """Executes the 6-priority ladder enforcing DONE_REVIEW_REQUIRED semantics."""
        # Check if process observation failed (e.g. PID recycled or unwhitelisted image)
        if not is_valid_obs:
            return VerdictExtraction(
                verdict=Verdict.FAILED.value,
                extraction_method="FAILED_NO_EVIDENCE",
                matched_marker=obs_error,
            )

        # Priority 1: Authoritative DB verdict if already terminal
        if persisted_verdict in {
            Verdict.PASS.value,
            Verdict.PARTIAL.value,
            Verdict.BLOCKED.value,
            Verdict.DONE_REVIEW_REQUIRED.value,
            Verdict.STOPPED_BY_USER.value,
        }:
            return VerdictExtraction(
                verdict=persisted_verdict,
                extraction_method="SQLITE_RECORD",
                matched_marker=f"DB_RECORD={persisted_verdict}",
            )

        # Check for DONE_REVIEW_REQUIRED in deliverable report
        if report_content:
            # Check bottom-up for primary structured regex
            lines = [line.strip() for line in report_content.splitlines() if line.strip()]
            for line in reversed(lines):
                match = re.search(VERDICT_REGEX, line, re.IGNORECASE)
                if match:
                    raw_verdict = match.group(1).upper()
                    return VerdictExtraction(
                        verdict=raw_verdict,
                        extraction_method="REGEX_PRIMARY",
                        matched_marker=line,
                    )
                # Check for explicit review required
                if REVIEW_REQUIRED_REGEX.search(line):
                    return VerdictExtraction(
                        verdict=Verdict.DONE_REVIEW_REQUIRED.value,
                        extraction_method="REGEX_PRIMARY",
                        matched_marker=line,
                    )

            # Check Wave Summary Marker
            wave_match = re.search(r"(?m)^WAVE\d+_RESULT\s*=\s*(PASS|PARTIAL|BLOCKED)\s*$", report_content)
            if wave_match:
                return VerdictExtraction(
                    verdict=wave_match.group(1).upper(),
                    extraction_method="REGEX_WAVE_SUMMARY",
                    matched_marker=wave_match.group(0).strip(),
                )

            # Priority 3: Scan top 25 lines of report for markdown header
            for line in lines[:25]:
                match = re.search(HEADER_STATUS_REGEX, line)
                if match:
                    raw_verdict = match.group(1).upper()
                    if "PASS" in raw_verdict or "COMPLETE" in raw_verdict or "VERIFIED" in raw_verdict:
                        norm = Verdict.PASS.value
                    elif "PARTIAL" in raw_verdict:
                        norm = Verdict.PARTIAL.value
                    elif "BLOCKED" in raw_verdict:
                        norm = Verdict.BLOCKED.value
                    else:
                        norm = Verdict.FAILED.value
                    return VerdictExtraction(
                        verdict=norm,
                        extraction_method="HEADER_MARKER",
                        matched_marker=line,
                    )

        # Priority 4: Scan tail 150 lines of logs
        log_lines: List[str] = []
        if stdout_content:
            log_lines.extend(stdout_content.splitlines()[-150:])
        if stderr_content:
            log_lines.extend(stderr_content.splitlines()[-150:])

        for line in reversed(log_lines):
            line_clean = line.strip()
            match = re.search(VERDICT_REGEX, line_clean, re.IGNORECASE)
            if match:
                return VerdictExtraction(
                    verdict=match.group(1).upper(),
                    extraction_method="REGEX_PRIMARY",
                    matched_marker=line_clean,
                )

        # Priority 5: Legacy Fallback: Report Present & Non-Empty & exit_code == 0
        if report_exists and report_size_bytes > 0 and exit_code == 0:
            return VerdictExtraction(
                verdict=Verdict.PASS_REPORT_PRESENT.value,
                extraction_method="FALLBACK_REPORT_PRESENT",
                matched_marker=f"FILE_EXISTS_SIZE_{report_size_bytes}_EXIT_0",
            )

        # Priority 6: Failure / Unknown
        return VerdictExtraction(
            verdict=Verdict.FAILED.value,
            extraction_method="FAILED_NO_EVIDENCE",
            matched_marker=None,
        )

    def validate_schema(self, result: ReconciledResult) -> None:
        """Validates ReconciledResult against schemas/result.schema.json."""
        d = result.to_dict()
        # Omit optional fields if None to satisfy result.schema.json type constraints
        for k in ["job_id", "node_id", "stage_id"]:
            if d.get(k) is None:
                del d[k]
        self.validator.validate_result(d)


__all__ = ["ResultReconciler", "REVIEW_REQUIRED_REGEX"]

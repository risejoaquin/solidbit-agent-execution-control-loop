"""SACL V1 4-Point Run Status Reconciliation Engine.

Implements the canonical 4-dimensional reconciliation invariant from RESULT_PROTOCOL.md:
1. Process Observation (PID check, image whitelist, 300s start-time drift guard)
2. Persisted State (SQLite agents table records)
3. Required Outputs (Physical deliverable markdown files, non-empty, log files)
4. Final Verdict Extraction (Priority ladder across report regexes, headers, and logs)

Invariant: Run success NEVER depends on process exit code alone.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

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
    ReconciliationData,
    ReconciledResult,
    RequiredOutputs,
    VerdictExtraction,
    WorktreeState,
)


def verify_process_observation(
    pid: Optional[int],
    process_name: str,
    is_active: bool,
    exit_code: Optional[int] = None,
    persisted_start_time: Optional[datetime | str] = None,
    actual_start_time: Optional[datetime] = None,
    allowed_images: Iterable[str] = ALLOWED_PROCESS_IMAGES,
    drift_tolerance_seconds: int = PID_DRIFT_TOLERANCE_SECONDS,
) -> Tuple[ProcessObservation, bool, Optional[str]]:
    """Evaluates Pillar 1: Process Observation & PID recycling defense.

    Returns:
        (ProcessObservation, is_valid_observation, failure_reason)
    """
    clean_name = process_name.lower().replace(".exe", "")
    allowed = {img.lower() for img in allowed_images}

    if clean_name not in allowed:
        reason = f"Process image '{process_name}' not in allowed whitelist: {sorted(allowed)}"
        obs = ProcessObservation(
            pid=pid,
            is_active=is_active,
            process_name=process_name,
            start_time_drift_seconds=None,
            exit_code=exit_code,
        )
        return obs, False, reason

    drift_sec: Optional[float] = None
    if persisted_start_time and actual_start_time:
        if isinstance(persisted_start_time, str):
            try:
                # Remove Z and parse ISO format
                ts = persisted_start_time.replace("Z", "+00:00")
                persisted_dt = datetime.fromisoformat(ts)
            except Exception:
                persisted_dt = None
        else:
            persisted_dt = persisted_start_time

        if persisted_dt:
            # Normalize naive datetimes
            if persisted_dt.tzinfo is not None and actual_start_time.tzinfo is None:
                actual_start_time = actual_start_time.astimezone()
            drift_sec = abs((actual_start_time - persisted_dt).total_seconds())
            if drift_sec > drift_tolerance_seconds:
                reason = (
                    f"PID recycling detected: process start time drift {drift_sec:.1f}s "
                    f"exceeds tolerance {drift_tolerance_seconds}s"
                )
                obs = ProcessObservation(
                    pid=pid,
                    is_active=is_active,
                    process_name=process_name,
                    start_time_drift_seconds=drift_sec,
                    exit_code=exit_code,
                )
                return obs, False, reason

    obs = ProcessObservation(
        pid=pid,
        is_active=is_active,
        process_name=process_name,
        start_time_drift_seconds=drift_sec,
        exit_code=exit_code,
    )
    return obs, True, None


def extract_verdict_from_content(
    report_content: Optional[str],
    stdout_content: Optional[str] = None,
    stderr_content: Optional[str] = None,
    report_exists: bool = False,
    report_size_bytes: int = 0,
    exit_code: Optional[int] = None,
    persisted_verdict: Optional[str] = None,
) -> VerdictExtraction:
    """Executes the 6-priority verdict extraction ladder from RESULT_PROTOCOL.md.

    Priority 1: Explicit persisted DB verdict if already terminal PASS/PARTIAL/BLOCKED
    Priority 2: Report bottom-up scan for Primary Structured Marker Regex
    Priority 3: Top 25 lines of Report for Markdown Status Header Regex
    Priority 4: Tail 150 lines of Stdout/Stderr logs for Structured Marker Regex
    Priority 5: Report present & non-empty & exit_code == 0 -> 'PASS (Report Present)'
    Priority 6: Return UNKNOWN (evaluates to FAILED)
    """
    # Priority 1: Authoritative DB verdict if already terminal
    if persisted_verdict in {Verdict.PASS.value, Verdict.PARTIAL.value, Verdict.BLOCKED.value}:
        return VerdictExtraction(
            verdict=persisted_verdict,
            extraction_method="PERSISTED_DATABASE_STATE",
            matched_marker=f"DB_STATUS={persisted_verdict}",
        )

    # Priority 2: Scan deliverable report bottom-up for primary structured regex
    if report_content:
        lines = [line.strip() for line in report_content.splitlines() if line.strip()]
        for line in reversed(lines):
            match = re.search(VERDICT_REGEX, line, re.IGNORECASE)
            if match:
                extracted = match.group(1).upper()
                return VerdictExtraction(
                    verdict=extracted,
                    extraction_method="REGEX_PRIMARY_BOTTOM_UP",
                    matched_marker=line,
                )

        # Priority 3: Scan top 25 lines of report for markdown status header
        top_lines = lines[:25]
        for line in top_lines:
            match = re.search(HEADER_STATUS_REGEX, line)
            if match:
                raw_verdict = match.group(1).upper()
                if "PASS" in raw_verdict or "COMPLETE" in raw_verdict or "VERIFIED" in raw_verdict:
                    normalized = Verdict.PASS.value
                elif "PARTIAL" in raw_verdict:
                    normalized = Verdict.PARTIAL.value
                elif "BLOCKED" in raw_verdict:
                    normalized = Verdict.BLOCKED.value
                else:
                    normalized = Verdict.FAILED.value
                return VerdictExtraction(
                    verdict=normalized,
                    extraction_method="HEADER_FALLBACK_TOP25",
                    matched_marker=line,
                )

    # Priority 4: Scan tail 150 lines of logs
    log_sources = []
    if stdout_content:
        log_sources.extend(stdout_content.splitlines()[-150:])
    if stderr_content:
        log_sources.extend(stderr_content.splitlines()[-150:])

    for line in reversed(log_sources):
        line_clean = line.strip()
        match = re.search(VERDICT_REGEX, line_clean, re.IGNORECASE)
        if match:
            extracted = match.group(1).upper()
            return VerdictExtraction(
                verdict=extracted,
                extraction_method="LOG_SCAN_TAIL150",
                matched_marker=line_clean,
            )

    # Priority 5: Report present on disk & non-empty & exit_code == 0
    if report_exists and report_size_bytes > 0 and exit_code == 0:
        return VerdictExtraction(
            verdict=Verdict.PASS_REPORT_PRESENT.value,
            extraction_method="LEGACY_REPORT_PRESENT_FALLBACK",
            matched_marker=f"FILE_EXISTS_SIZE_{report_size_bytes}_EXIT_0",
        )

    # Priority 6: Failure / Unknown
    return VerdictExtraction(
        verdict=Verdict.FAILED.value,
        extraction_method="NO_EVIDENCE_FOUND",
        matched_marker=None,
    )


def reconcile_agent(
    run_id: str,
    agent_id: str,
    process_obs: ProcessObservation,
    persisted_state: PersistedState,
    required_outputs: RequiredOutputs,
    worktree: WorktreeState,
    job_id: Optional[str] = None,
    node_id: Optional[str] = None,
    stage_id: Optional[Any] = None,
    report_content: Optional[str] = None,
    stdout_content: Optional[str] = None,
    stderr_content: Optional[str] = None,
    error_message: Optional[str] = None,
) -> ReconciledResult:
    """Executes full 4-point reconciliation across all four pillars."""
    verdict_ext = extract_verdict_from_content(
        report_content=report_content,
        stdout_content=stdout_content,
        stderr_content=stderr_content,
        report_exists=required_outputs.report_exists,
        report_size_bytes=required_outputs.report_size_bytes,
        exit_code=process_obs.exit_code,
        persisted_verdict=None,
    )

    final_verdict = verdict_ext.verdict
    # Determine lifecycle status from verdict and process
    if final_verdict in {Verdict.PASS.value, Verdict.PASS_REPORT_PRESENT.value}:
        status = "SUCCEEDED"
    elif final_verdict == Verdict.BLOCKED.value:
        status = "BLOCKED"
    elif final_verdict == Verdict.PARTIAL.value:
        status = "SUCCEEDED"
    elif final_verdict == Verdict.DONE_REVIEW_REQUIRED.value:
        status = "COMPLETE"
    else:
        status = "FAILED"

    recon_data = ReconciliationData(
        process_observation=process_obs,
        persisted_state=persisted_state,
        required_outputs=required_outputs,
        verdict_extraction=verdict_ext,
    )

    return ReconciledResult(
        run_id=run_id,
        agent_id=agent_id,
        job_id=job_id,
        node_id=node_id,
        stage_id=stage_id,
        status=status,
        result_verdict=final_verdict,
        reconciliation=recon_data,
        worktree=worktree,
        error_message=error_message,
    )

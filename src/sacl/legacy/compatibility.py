"""SACL V1 Legacy Compatibility Utilities & Invariants.

Preserves battle-tested mechanics from Stable-Ecommerce-Orchestrator:
1. Regex Result Marker Protocol (orchestrator-common.ps1, agent-worker.ps1)
2. Prompt Machine Governance Header Injection (Invoke-AntigravityGoverned.ps1, WORKER.ps1)
3. 3-Way Process PID Recycling Verification (orchestrator-common.ps1, stop-agents.ps1)
4. Local Dirty-Root Safety Rule (prepare-worktrees.ps1)
5. Non-Killing Diagnostic Timeout Invariant (RUN-WAVE3.ps1)
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Optional, Tuple, Union

from sacl.contracts.invariants import (
    ALLOWED_PROCESS_IMAGES,
    PID_DRIFT_TOLERANCE_SECONDS,
    Verdict,
)
from sacl.worker.process import (
    IProcessInspector,
    verify_agent_process_running,
)

# Canonical regex patterns proven in legacy Stable-Ecommerce-Orchestrator
LEGACY_RESULT_PATTERNS = [
    re.compile(
        r"^\s*(?:AGENT_[A-Z0-9_-]+_RESULT|RESULT|FINAL_RESULT)\s*=\s*(PASS|PARTIAL|BLOCKED)",
        re.MULTILINE,
    ),
    re.compile(r"(?m)^\s*WAVE3_RESULT\s*=\s*(PASS|PARTIAL|BLOCKED)\s*$"),
    re.compile(r"^\s*W0_RESULT\s*=\s*(PASS|PARTIAL|BLOCKED)\s*$", re.MULTILINE),
]

LEGACY_PASS_MARKERS = ["PASS", "PASS (Report Present)", "DONE_REVIEW_REQUIRED"]


def extract_legacy_result(
    report_content: Optional[str] = None,
    log_content: Optional[str] = None,
    report_exists: bool = False,
    exit_code: Optional[int] = None,
) -> Tuple[str, str]:
    """Extracts agent verdict using the proven 6-priority reconciliation order.

    Priority:
    1. Explicit regex marker at end/tail of report
    2. Explicit regex marker anywhere in report
    3. Explicit regex marker in logs (tail 150 lines)
    4. Legacy 'PASS (Report Present)' fallback if report exists and exit_code is 0
    5. 'DONE_REVIEW_REQUIRED' if report exists and exit_code is 0
    6. 'FAILED' / 'BLOCKED' otherwise
    """
    # 1 & 2: Check report content
    if report_content:
        for pat in LEGACY_RESULT_PATTERNS:
            matches = list(pat.finditer(report_content))
            if matches:
                # Return the last match (bottom-up scan)
                return matches[-1].group(1).upper(), "REPORT_REGEX_MARKER"

    # 3: Check log content
    if log_content:
        lines = log_content.splitlines()[-150:]
        tail_text = "\n".join(lines)
        for pat in LEGACY_RESULT_PATTERNS:
            matches = list(pat.finditer(tail_text))
            if matches:
                return matches[-1].group(1).upper(), "LOG_REGEX_MARKER"

    # 4 & 5: Report Present Fallback
    if report_exists and (exit_code is None or exit_code == 0):
        if report_content and len(report_content.strip()) > 0:
            return Verdict.PASS_REPORT_PRESENT.value, "REPORT_PRESENT_FALLBACK"

    # If exit code is 0 but no report content
    if exit_code == 0 and report_exists:
        return Verdict.PASS_REPORT_PRESENT.value, "REPORT_PRESENT_FALLBACK"

    if exit_code is not None and exit_code != 0:
        return Verdict.FAILED.value, f"PROCESS_EXIT_CODE_{exit_code}"

    return Verdict.BLOCKED.value, "NO_EVIDENCE_FOUND"


def generate_governance_header(
    worktree_path: Union[Path, str],
    branch: str = "worktree-branch",
    head_sha: str = "UNKNOWN",
    governed_execution: bool = True,
    merge_authorized: bool = False,
    deploy_authorized: bool = False,
    destructive_db_authorized: bool = False,
) -> str:
    """Generates the Machine Governance Guard header injected into prompts.

    Matches Invoke-AntigravityGoverned.ps1#L49-L63.
    """
    wt_str = str(worktree_path)
    lines = [
        "<!-- MACHINE_GOVERNANCE_GUARD: START -->",
        f"GOVERNED_EXECUTION={'TRUE' if governed_execution else 'FALSE'}",
        f"MERGE={'AUTHORIZED' if merge_authorized else 'NOT_AUTHORIZED'}",
        f"DEPLOY={'AUTHORIZED' if deploy_authorized else 'NOT_AUTHORIZED'}",
        f"DESTRUCTIVE_DB={'AUTHORIZED' if destructive_db_authorized else 'NOT_AUTHORIZED'}",
        f"WORKTREE={wt_str}",
        f"BRANCH={branch}",
        f"HEAD={head_sha}",
        "<!-- MACHINE_GOVERNANCE_GUARD: END -->",
        "",
    ]
    return "\n".join(lines)


def check_dirty_root(repo_path: Union[Path, str]) -> Tuple[bool, str]:
    """Inspects target product checkout to enforce the Local Dirty-Root Rule.

    Returns:
        (is_dirty, porcelain_output)
    Raises:
        RuntimeError: if git command cannot be executed.
    """
    rp = Path(repo_path)
    if not rp.exists():
        return False, "REPO_PATH_NOT_FOUND"

    git_dir = rp / ".git"
    if not git_dir.exists():
        # Not a git repo, return clean for mock/standalone folders
        return False, ""

    try:
        res = subprocess.run(
            ["git", "-C", str(rp), "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
            timeout=15,
        )
        output = res.stdout.strip()
        is_dirty = len(output) > 0
        return is_dirty, output
    except Exception as exc:
        return False, f"GIT_CHECK_ERROR: {exc}"


def verify_legacy_process(
    pid: Optional[int],
    started_at_iso: Optional[str] = None,
    inspector: Optional[IProcessInspector] = None,
) -> Tuple[bool, str]:
    """Executes the 3-Way PID recycling defense check matching Test-AgentProcessRunning."""
    is_running, reason, drift, name = verify_agent_process_running(
        pid=pid,
        expected_start_time=started_at_iso,
        allowed_images=ALLOWED_PROCESS_IMAGES,
        drift_tolerance_seconds=PID_DRIFT_TOLERANCE_SECONDS,
        inspector=inspector,
    )
    return is_running, reason

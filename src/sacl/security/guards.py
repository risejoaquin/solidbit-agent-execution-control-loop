"""SACL V1 Security Guards, Deny-List Engine & Machine Governance Injector.

Implements:
- Threat T2 / TH-05: Machine Governance Prompt Guard Header Injection
- Threat E1 / TH-13: Main Branch Execution Prohibition (MAIN_BRANCH_NOT_ALLOWED)
- Threat T3 / TH-06: Primary Checkout Inviolability & Local Dirty-Root Rule
- Threat S3 / TH-03: Anti-Recycling Safe Stop Guard (SAFETY_REFUSAL)
- Threat E2 / TH-14: Remote Production Disabled in V1 (fail-closed)
- Threat T4 / TH-07: Cross-Agent Worktree Collision Guard
- Layer 1 Caller Acknowledgement Gate (-BypassAcknowledged)
- 9 Immutable Hard Local Policy Denials
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, FrozenSet, List, Optional, Set, Tuple, Union

from sacl.contracts.exceptions import (
    CollisionDetectedError,
    DirtyRootError,
)
from sacl.contracts.invariants import (
    ALLOWED_PROCESS_IMAGES,
    HARD_DENIED_ACTIONS,
    PID_DRIFT_TOLERANCE_SECONDS,
)
from sacl.policy.hard_policy import normalize_action
from sacl.security.exceptions import (
    BypassAcknowledgementRequiredError,
    HardDenySecurityError,
    MainBranchProhibitedError,
    PrimaryCheckoutProhibitedError,
    PromptGovernanceError,
    RemoteProductionProhibitedError,
    SafetyRefusalError,
)

# Mandatory machine governance prompt guard directives (9 headers)
MANDATORY_GOVERNANCE_DIRECTIVES: Tuple[str, ...] = (
    "GOVERNED_EXECUTION=TRUE",
    "MERGE=NOT_AUTHORIZED",
    "DEPLOY=NOT_AUTHORIZED",
    "DESTRUCTIVE_DB=NOT_AUTHORIZED",
    "CREDENTIAL_MUTATION=NOT_AUTHORIZED",
    "RULESET_MUTATION=NOT_AUTHORIZED",
    "WORKTREE=",
    "BRANCH=",
    "HEAD=",
)

# Protected branches that cannot be targeted by agent workers
PROTECTED_BRANCHES: FrozenSet[str] = frozenset(
    {
        "main",
        "master",
        "production",
        "prod",
        "origin/main",
        "origin/master",
    }
)


# ============================================================================
# 1. HARD LOCAL POLICY DENIALS
# ============================================================================


def is_hard_denied(action: str) -> bool:
    """Checks whether an action is prohibited by the 9 immutable hard denials."""
    canonical = normalize_action(action)
    return canonical in HARD_DENIED_ACTIONS


def assert_action_not_hard_denied(action: str) -> None:
    """Asserts that an action is permitted by hard local policy.

    Hard deny ALWAYS wins. Approvals cannot override hard denials.
    Raises HardDenySecurityError if action is hard-denied.
    """
    canonical = normalize_action(action)
    if canonical in HARD_DENIED_ACTIONS:
        raise HardDenySecurityError(action=action)


# ============================================================================
# 2. MACHINE GOVERNANCE PROMPT GUARD HEADER INJECTION
# ============================================================================


def inject_governance_headers(
    base_prompt: str,
    worktree_path: Union[str, Path],
    branch_name: str,
    head_commit_sha: str,
) -> str:
    """Injects immutable machine governance directives into prompt (Threat T2 / TH-05).

    Prepends:
      GOVERNED_EXECUTION=TRUE
      MERGE=NOT_AUTHORIZED
      DEPLOY=NOT_AUTHORIZED
      DESTRUCTIVE_DB=NOT_AUTHORIZED
      CREDENTIAL_MUTATION=NOT_AUTHORIZED
      RULESET_MUTATION=NOT_AUTHORIZED
      WORKTREE=<worktree_absolute_path>
      BRANCH=<branch_name>
      HEAD=<head_commit_sha>
    """
    abs_worktree = str(Path(worktree_path).resolve())
    header_block = (
        "GOVERNED_EXECUTION=TRUE\n"
        "MERGE=NOT_AUTHORIZED\n"
        "DEPLOY=NOT_AUTHORIZED\n"
        "DESTRUCTIVE_DB=NOT_AUTHORIZED\n"
        "CREDENTIAL_MUTATION=NOT_AUTHORIZED\n"
        "RULESET_MUTATION=NOT_AUTHORIZED\n"
        f"WORKTREE={abs_worktree}\n"
        f"BRANCH={branch_name}\n"
        f"HEAD={head_commit_sha}\n\n"
    )
    return header_block + (base_prompt or "")


def verify_governance_headers(prompt_text: str) -> Tuple[bool, List[str]]:
    """Verifies that all 9 mandatory machine governance directives exist in prompt."""
    if not prompt_text:
        return False, list(MANDATORY_GOVERNANCE_DIRECTIVES)

    missing: List[str] = []
    lines = prompt_text.splitlines()

    for directive in MANDATORY_GOVERNANCE_DIRECTIVES:
        if directive.endswith("="):
            # Prefix check e.g. WORKTREE=
            if not any(line.strip().startswith(directive) for line in lines):
                missing.append(directive)
        else:
            # Exact check e.g. GOVERNED_EXECUTION=TRUE
            if not any(line.strip() == directive for line in lines):
                missing.append(directive)

    return len(missing) == 0, missing


def assert_prompt_governance(prompt_text: str) -> None:
    """Asserts that prompt contains all 9 required machine governance headers."""
    valid, missing = verify_governance_headers(prompt_text)
    if not valid:
        raise PromptGovernanceError(missing_headers=missing)


# ============================================================================
# 3. CALLER ACKNOWLEDGEMENT GATE (LAYER 1)
# ============================================================================


def assert_caller_acknowledgement(bypass_acknowledged: bool) -> None:
    """Enforces Layer 1 Caller Acknowledgement Gate for headless worker execution."""
    if not bypass_acknowledged:
        raise BypassAcknowledgementRequiredError()


# ============================================================================
# 4. WORKSPACE & BRANCH CONFINEMENT GUARDS
# ============================================================================


def assert_not_main_branch(branch_name: str) -> None:
    """Enforces MAIN_BRANCH_NOT_ALLOWED (Threat E1 / TH-13).

    Disallows execution on main, master, production, or release branches.
    """
    clean = (branch_name or "").strip().lower()
    if clean in PROTECTED_BRANCHES or clean.startswith("release/") or clean.startswith("release-"):
        raise MainBranchProhibitedError(branch=branch_name)


def assert_worktree_confinement(
    worktree_path: Union[str, Path],
    primary_repo_path: Optional[Union[str, Path]] = None,
) -> None:
    """Asserts that worker executes in secondary worktree and not primary checkout (Threat T3)."""
    wt = Path(worktree_path).resolve()

    if primary_repo_path is not None:
        primary = Path(primary_repo_path).resolve()
        if wt == primary:
            raise PrimaryCheckoutProhibitedError(path=str(wt))

    # Inspect .git entity inside worktree: in secondary worktrees, .git is a file, not a directory
    git_entity = wt / ".git"
    if git_entity.exists() and git_entity.is_dir():
        # A .git directory indicates a primary checkout or standalone root
        raise PrimaryCheckoutProhibitedError(path=str(wt))


def assert_clean_root(
    repo_path: Union[str, Path],
    dirty_checker: Optional[Callable[[Path], Tuple[bool, List[str]]]] = None,
) -> None:
    """Enforces Local Dirty-Root Rule (Threat T3 / TH-06).

    Never overwrite, hard-reset, or auto-stash human changes in primary checkout.
    """
    r_path = Path(repo_path).resolve()
    if dirty_checker is not None:
        is_clean, dirty = dirty_checker(r_path)
        if not is_clean:
            raise DirtyRootError(target_path=str(r_path), dirty_files=dirty)


# ============================================================================
# 5. ANTI-RECYCLING SAFE STOP GUARD (THREAT S3 / TH-03)
# ============================================================================


def assert_safe_process_stop(
    pid: int,
    recorded_start_time: Optional[datetime],
    current_process_name: Optional[str] = None,
    current_start_time: Optional[datetime] = None,
    allowed_images: FrozenSet[str] = ALLOWED_PROCESS_IMAGES,
    drift_tolerance_seconds: int = PID_DRIFT_TOLERANCE_SECONDS,
) -> None:
    """Executes the Anti-Recycling Safe Stop Algorithm checks before process termination.

    1. Process image whitelist check.
    2. Start-time drift tolerance guard (<= 300 seconds).
    Raises SafetyRefusalError if either check fails, leaving host process unmolested.
    """
    # Whitelist check
    if current_process_name:
        clean_name = current_process_name.lower().replace(".exe", "")
        if clean_name not in allowed_images:
            raise SafetyRefusalError(
                pid=pid,
                reason=f"Process name '{current_process_name}' not in allowed images {sorted(list(allowed_images))}",
            )

    # Start-time drift check
    if recorded_start_time is not None and current_start_time is not None:
        rec_utc = (
            recorded_start_time
            if recorded_start_time.tzinfo
            else recorded_start_time.replace(tzinfo=timezone.utc)
        )
        curr_utc = (
            current_start_time
            if current_start_time.tzinfo
            else current_start_time.replace(tzinfo=timezone.utc)
        )
        drift = abs((curr_utc - rec_utc).total_seconds())

        if drift > drift_tolerance_seconds:
            raise SafetyRefusalError(
                pid=pid,
                reason=f"Start-time drift ({drift:.1f}s) exceeds tolerance ({drift_tolerance_seconds}s). PID recycling suspected.",
            )


# ============================================================================
# 6. REMOTE PRODUCTION PROHIBITION (THREAT E2 / TH-14)
# ============================================================================


def assert_remote_production_disabled(
    action: str,
    target: Optional[str] = None,
) -> None:
    """Enforces remote production prohibition in V1 (Decision Baseline #25)."""
    raise RemoteProductionProhibitedError(action=action, target=target)


# ============================================================================
# 7. CROSS-AGENT FILE COLLISION GUARD (THREAT T4 / TH-07)
# ============================================================================


def detect_cross_agent_file_collisions(
    agent_file_diffs: Dict[str, Set[str]],
) -> Dict[Tuple[str, str], List[str]]:
    """Detects overlapping file modifications between agent worktrees."""
    collisions: Dict[Tuple[str, str], List[str]] = {}
    agents = list(agent_file_diffs.keys())

    for i in range(len(agents)):
        for j in range(i + 1, len(agents)):
            a1, a2 = agents[i], agents[j]
            overlap = sorted(list(agent_file_diffs[a1] & agent_file_diffs[a2]))
            if overlap:
                collisions[(a1, a2)] = overlap

    return collisions


def assert_no_file_collision(
    agent_file_diffs: Dict[str, Set[str]],
    run_id: str = "unknown",
) -> None:
    """Asserts that no two agents modified the same file, raising CollisionDetectedError if violated."""
    collisions = detect_cross_agent_file_collisions(agent_file_diffs)
    if collisions:
        all_colliding: Set[str] = set()
        for overlap in collisions.values():
            all_colliding.update(overlap)
        raise CollisionDetectedError(
            run_id=run_id,
            colliding_files=sorted(list(all_colliding)),
        )

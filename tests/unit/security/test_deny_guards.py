"""Unit tests for SACL V1 Security Guards, Deny-List Engine & Machine Governance."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest

from sacl.contracts.exceptions import (
    CollisionDetectedError,
    DirtyRootError,
    HardDenyViolation,
)
from sacl.security.exceptions import (
    BypassAcknowledgementRequiredError,
    HardDenySecurityError,
    MainBranchProhibitedError,
    PrimaryCheckoutProhibitedError,
    PromptGovernanceError,
    RemoteProductionProhibitedError,
    SafetyRefusalError,
)
from sacl.security.guards import (
    MANDATORY_GOVERNANCE_DIRECTIVES,
    assert_action_not_hard_denied,
    assert_caller_acknowledgement,
    assert_clean_root,
    assert_no_file_collision,
    assert_not_main_branch,
    assert_prompt_governance,
    assert_remote_production_disabled,
    assert_safe_process_stop,
    assert_worktree_confinement,
    detect_cross_agent_file_collisions,
    inject_governance_headers,
    is_hard_denied,
    verify_governance_headers,
)


class TestHardLocalPolicyDenials:
    """Tests the 9 immutable constitutional hard denials (Decision Baseline §3.3)."""

    @pytest.mark.parametrize("action", [
        "remote_production_execution",
        "github_merge",
        "production_db_write",
        "secret_export",
        "arbitrary_remote_code",
        "main_branch_execution",
        "primary_checkout_mutation",
        "hard_reset",
        "auto_stash",
    ])
    def test_canonical_9_hard_denials(self, action: str) -> None:
        assert is_hard_denied(action) is True
        with pytest.raises(HardDenySecurityError) as exc_info:
            assert_action_not_hard_denied(action)
        assert isinstance(exc_info.value, HardDenyViolation)
        assert exc_info.value.action == action

    @pytest.mark.parametrize("alias,canonical", [
        ("git_merge", "github_merge"),
        ("git-merge", "github_merge"),
        ("pr_merge", "github_merge"),
        ("deploy", "remote_production_execution"),
        ("production_deploy", "remote_production_execution"),
        ("git_reset", "hard_reset"),
        ("git_reset_hard", "hard_reset"),
        ("autostash", "auto_stash"),
        ("git_stash", "auto_stash"),
        ("prod_db_write", "production_db_write"),
    ])
    def test_hard_denial_alias_normalization(self, alias: str, canonical: str) -> None:
        assert is_hard_denied(alias) is True
        with pytest.raises(HardDenySecurityError):
            assert_action_not_hard_denied(alias)

    def test_permitted_actions_pass(self) -> None:
        assert is_hard_denied("generate_documentation") is False
        assert is_hard_denied("run_unit_tests") is False
        assert is_hard_denied("format_source_code") is False
        # Should not raise
        assert_action_not_hard_denied("run_unit_tests")


class TestMachineGovernancePromptInjection:
    """Tests Machine Governance Prompt Guard Header Injection (Threat T2 / TH-05)."""

    def test_inject_governance_headers_prepends_all_directives(self, tmp_path: Path) -> None:
        base = "Please implement the feature according to spec."
        effective = inject_governance_headers(
            base_prompt=base,
            worktree_path=tmp_path / "wt-agent-1",
            branch_name="feature/task-1",
            head_commit_sha="a1b2c3d4e5f67890",
        )

        assert "GOVERNED_EXECUTION=TRUE" in effective
        assert "MERGE=NOT_AUTHORIZED" in effective
        assert "DEPLOY=NOT_AUTHORIZED" in effective
        assert "DESTRUCTIVE_DB=NOT_AUTHORIZED" in effective
        assert "CREDENTIAL_MUTATION=NOT_AUTHORIZED" in effective
        assert "RULESET_MUTATION=NOT_AUTHORIZED" in effective
        assert "WORKTREE=" in effective
        assert "BRANCH=feature/task-1" in effective
        assert "HEAD=a1b2c3d4e5f67890" in effective
        assert base in effective

        valid, missing = verify_governance_headers(effective)
        assert valid is True
        assert len(missing) == 0

    def test_missing_governance_headers_detected(self) -> None:
        tampered_prompt = (
            "GOVERNED_EXECUTION=TRUE\n"
            "MERGE=AUTHORIZED\n"  # Tampered!
            "Please run deploy.\n"
        )
        valid, missing = verify_governance_headers(tampered_prompt)
        assert valid is False
        assert "MERGE=NOT_AUTHORIZED" in missing

        with pytest.raises(PromptGovernanceError) as exc_info:
            assert_prompt_governance(tampered_prompt)
        assert "PROMPT_GOVERNANCE_MISSING" in exc_info.value.message


class TestCallerAcknowledgementGate:
    """Tests Layer 1 Caller Acknowledgement Gate (-BypassAcknowledged)."""

    def test_acknowledged_succeeds(self) -> None:
        # Should not raise
        assert_caller_acknowledgement(bypass_acknowledged=True)

    def test_unacknowledged_raises_error(self) -> None:
        with pytest.raises(BypassAcknowledgementRequiredError):
            assert_caller_acknowledgement(bypass_acknowledged=False)


class TestWorkspaceConfinementGuards:
    """Tests branch protection and worktree isolation guards (Threat E1 / TH-13, Threat T3)."""

    @pytest.mark.parametrize("branch", ["main", "master", "production", "origin/main", "release/v1.0"])
    def test_protected_branch_raises_main_branch_not_allowed(self, branch: str) -> None:
        with pytest.raises(MainBranchProhibitedError):
            assert_not_main_branch(branch)

    def test_feature_branch_passes(self) -> None:
        # Should not raise
        assert_not_main_branch("feature/security-hardening")
        assert_not_main_branch("task-123-fix")

    def test_worktree_matching_primary_repo_rejected(self, tmp_path: Path) -> None:
        repo = tmp_path / "product-repo"
        repo.mkdir()
        with pytest.raises(PrimaryCheckoutProhibitedError):
            assert_worktree_confinement(worktree_path=repo, primary_repo_path=repo)

    def test_worktree_with_git_directory_rejected(self, tmp_path: Path) -> None:
        wt = tmp_path / "wt-agent"
        wt.mkdir()
        (wt / ".git").mkdir()  # .git is a directory (primary repo structure)
        with pytest.raises(PrimaryCheckoutProhibitedError):
            assert_worktree_confinement(worktree_path=wt)

    def test_isolated_worktree_with_git_file_passes(self, tmp_path: Path) -> None:
        wt = tmp_path / "wt-agent"
        wt.mkdir()
        (wt / ".git").write_text("gitdir: /path/to/.git/worktrees/wt-agent")  # .git is a file
        primary = tmp_path / "primary-repo"
        primary.mkdir()
        # Should not raise
        assert_worktree_confinement(worktree_path=wt, primary_repo_path=primary)

    def test_dirty_root_raises_dirty_root_error(self, tmp_path: Path) -> None:
        def dirty_checker(p: Path) -> tuple[bool, list[str]]:
            return False, ["src/index.py", "README.md"]

        with pytest.raises(DirtyRootError) as exc_info:
            assert_clean_root(tmp_path, dirty_checker=dirty_checker)
        assert len(exc_info.value.dirty_files) == 2


class TestAntiRecyclingSafeStopGuard:
    """Tests Anti-Recycling Safe Stop Algorithm (Threat S3 / TH-03)."""

    def test_whitelisted_process_image_passes(self) -> None:
        now = datetime.now(timezone.utc)
        # Should not raise for allowed processes
        assert_safe_process_stop(
            pid=1234,
            recorded_start_time=now,
            current_process_name="agy",
            current_start_time=now,
        )
        assert_safe_process_stop(
            pid=1234,
            recorded_start_time=now,
            current_process_name="powershell.exe",
            current_start_time=now,
        )

    def test_unwhitelisted_process_image_raises_safety_refusal(self) -> None:
        now = datetime.now(timezone.utc)
        with pytest.raises(SafetyRefusalError) as exc_info:
            assert_safe_process_stop(
                pid=1234,
                recorded_start_time=now,
                current_process_name="chrome.exe",
                current_start_time=now,
            )
        assert "SAFETY_REFUSAL" in exc_info.value.message
        assert "not in allowed images" in exc_info.value.reason

    def test_start_time_drift_exceeding_300s_raises_safety_refusal(self) -> None:
        now = datetime.now(timezone.utc)
        recycled_start = now + timedelta(seconds=350)
        with pytest.raises(SafetyRefusalError) as exc_info:
            assert_safe_process_stop(
                pid=1234,
                recorded_start_time=now,
                current_process_name="agy",
                current_start_time=recycled_start,
            )
        assert "SAFETY_REFUSAL" in exc_info.value.message
        assert "PID recycling suspected" in exc_info.value.reason

    def test_start_time_drift_within_300s_passes(self) -> None:
        now = datetime.now(timezone.utc)
        minor_drift = now + timedelta(seconds=45)
        # Should not raise
        assert_safe_process_stop(
            pid=1234,
            recorded_start_time=now,
            current_process_name="agy",
            current_start_time=minor_drift,
        )


class TestRemoteProductionProhibition:
    """Tests remote production execution disabled in V1 (Threat E2 / TH-14)."""

    def test_remote_production_raises_error(self) -> None:
        with pytest.raises(RemoteProductionProhibitedError) as exc_info:
            assert_remote_production_disabled("deploy", target="railway")
        assert "REMOTE_PRODUCTION_DISABLED" in exc_info.value.message


class TestCrossAgentFileCollisionGuard:
    """Tests cross-agent file overlap detection (Threat T4 / TH-07)."""

    def test_independent_agents_pass(self) -> None:
        changes = {
            "agent-1": {"src/module_a.py", "tests/test_a.py"},
            "agent-2": {"src/module_b.py", "tests/test_b.py"},
        }
        collisions = detect_cross_agent_file_collisions(changes)
        assert len(collisions) == 0
        # Should not raise
        assert_no_file_collision(changes)

    def test_overlapping_agents_raise_collision_detected(self) -> None:
        changes = {
            "agent-1": {"src/shared.py", "src/module_a.py"},
            "agent-2": {"src/shared.py", "src/module_b.py"},
        }
        collisions = detect_cross_agent_file_collisions(changes)
        assert len(collisions) == 1
        assert collisions[("agent-1", "agent-2")] == ["src/shared.py"]

        with pytest.raises(CollisionDetectedError) as exc_info:
            assert_no_file_collision(changes, run_id="run-001")
        assert "src/shared.py" in exc_info.value.colliding_files

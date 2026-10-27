"""Tests for Bounded Approval Validation Primitives (src/sacl/policy/approval.py).

Constitutional Invariant (ADR-007):
Approvals are strictly bound to (job_id, action, scope, request_id, expires_at).
Approvals RESUME the same logical run and CANNOT override hard local policy denies.
Approver channels are strictly CLI, GMAIL, MANUAL (no webhooks).
"""

from datetime import datetime, timedelta, timezone

import pytest

from sacl.contracts.exceptions import (
    ApprovalExpiredError,
    ContractValidationError,
    HardDenyViolation,
    PolicyDeniedError,
)
from sacl.contracts.models import ApprovalToken, Approver
from sacl.policy.approval import (
    ApprovalManager,
    ApprovalValidator,
    format_iso_datetime,
    is_scope_covered,
    matches_scope_pattern,
)


@pytest.fixture
def valid_approval_token():
    future_time = datetime.now(timezone.utc) + timedelta(hours=2)
    return ApprovalToken(
        request_id="REQ-20261007-001",
        job_id="job-20261007-123456",
        action="SPECIFICATION_MATERIALIZATION",
        scope=["docs/*", "schemas/*"],
        expires_at=format_iso_datetime(future_time),
        decision="APPROVED",
        approver=Approver(identity="Joaquín", channel="CLI"),
        schema="solidbit.approval.v1",
        resume_run=True,
        cannot_override_hard_deny=True,
    )


def test_valid_approval_token_passes(valid_approval_token):
    validator = ApprovalValidator()
    validator.validate_invariants(valid_approval_token)


def test_approval_expired_fails_closed(valid_approval_token):
    validator = ApprovalValidator()
    past_time = datetime.now(timezone.utc) - timedelta(minutes=5)
    valid_approval_token.expires_at = format_iso_datetime(past_time)

    with pytest.raises(ApprovalExpiredError) as excinfo:
        validator.validate_invariants(valid_approval_token)
    assert excinfo.value.request_id == "REQ-20261007-001"


def test_disallowed_approver_channel_fails():
    validator = ApprovalValidator()
    future_time = datetime.now(timezone.utc) + timedelta(hours=1)
    token = ApprovalToken(
        request_id="REQ-20261007-002",
        job_id="job-123",
        action="STAGE_CONTINUATION",
        scope=["*"],
        expires_at=format_iso_datetime(future_time),
        decision="APPROVED",
        approver=Approver(identity="Joaquín", channel="WEBHOOK"),  # Invalid! Webhooks disallowed
    )
    with pytest.raises(ContractValidationError):
        validator.validate_invariants(token)


@pytest.mark.parametrize(
    "hard_action",
    [
        "remote_production_execution",
        "github_merge",
        "production_db_write",
        "secret_export",
        "arbitrary_remote_code",
        "main_branch_execution",
        "primary_checkout_mutation",
        "hard_reset",
        "auto_stash",
        "GIT_MERGE",
        "REMOTE_DEPLOY",
        "PRODUCTION_DB_MUTATION",
    ],
)
def test_approval_cannot_override_hard_deny_unconditional_violation(
    valid_approval_token, hard_action
):
    validator = ApprovalValidator()
    valid_approval_token.action = hard_action

    # Attempting to authorize a hard denied action MUST raise HardDenyViolation
    with pytest.raises(HardDenyViolation) as excinfo:
        validator.validate_invariants(valid_approval_token)
    assert "Approval Override Prohibited Invariant Violation" in excinfo.value.message


def test_cannot_override_hard_deny_flag_violation(valid_approval_token):
    validator = ApprovalValidator()
    valid_approval_token.cannot_override_hard_deny = False

    with pytest.raises(HardDenyViolation):
        validator.validate_invariants(valid_approval_token)


def test_rejected_and_deferred_decisions_do_not_authorize(valid_approval_token):
    validator = ApprovalValidator()

    valid_approval_token.decision = "REJECTED"
    with pytest.raises(PolicyDeniedError):
        validator.validate_invariants(valid_approval_token)

    valid_approval_token.decision = "DEFERRED"
    with pytest.raises(PolicyDeniedError):
        validator.validate_invariants(valid_approval_token)


def test_scope_pattern_matching():
    assert matches_scope_pattern("docs/*", "docs/ARCHITECTURE.md") is True
    assert matches_scope_pattern("docs/*", "docs/adr/ADR-001.md") is True
    assert matches_scope_pattern("schemas/*", "schemas/approval.schema.json") is True
    assert matches_scope_pattern("docs/*", "src/main.py") is False
    assert matches_scope_pattern("*", "anything.txt") is True

    # Multi-scope containment
    assert is_scope_covered(["docs/*", "schemas/*"], ["docs/a.md", "schemas/b.json"]) is True
    assert is_scope_covered(["docs/*"], ["docs/a.md", "src/b.py"]) is False


def test_token_binding_validation(valid_approval_token):
    validator = ApprovalValidator()

    # Valid binding
    validator.validate_binding(
        token=valid_approval_token,
        job_id="job-20261007-123456",
        action="SPECIFICATION_MATERIALIZATION",
        requested_scope=["docs/AUTHORITY_MODEL.md"],
    )

    # Job ID mismatch
    with pytest.raises(PolicyDeniedError) as excinfo:
        validator.validate_binding(
            token=valid_approval_token,
            job_id="different-job-id",
            action="SPECIFICATION_MATERIALIZATION",
            requested_scope=["docs/AUTHORITY_MODEL.md"],
        )
    assert "Token binding mismatch" in excinfo.value.message

    # Action mismatch
    with pytest.raises(PolicyDeniedError) as excinfo:
        validator.validate_binding(
            token=valid_approval_token,
            job_id="job-20261007-123456",
            action="DIFFERENT_ACTION",
            requested_scope=["docs/AUTHORITY_MODEL.md"],
        )
    assert "Token binding mismatch" in excinfo.value.message

    # Scope mismatch
    with pytest.raises(PolicyDeniedError) as excinfo:
        validator.validate_binding(
            token=valid_approval_token,
            job_id="job-20261007-123456",
            action="SPECIFICATION_MATERIALIZATION",
            requested_scope=["src/sacl/engine.py"],  # outside docs/* and schemas/*
        )
    assert "Scope containment failure" in excinfo.value.message


def test_approval_manager_request_and_decision_lifecycle():
    manager = ApprovalManager()

    # Cannot create request for hard denied action
    with pytest.raises(HardDenyViolation):
        manager.create_approval_request(
            job_id="job-456",
            action="github_merge",
            scope=["main"],
        )

    # Create legitimate request
    req_id = manager.create_approval_request(
        job_id="job-456",
        action="BRANCH_INTEGRATION",
        scope=["feature/*"],
        run_id="run-789",
        ttl_seconds=3600,
    )
    assert req_id.startswith("REQ-")
    assert manager.get_request(req_id)["status"] == "PENDING"

    # Record approval decision
    token = manager.record_decision(
        request_id=req_id,
        decision="APPROVED",
        approver=Approver(identity="Joaquín", channel="CLI"),
        notes="Approved branch integration.",
    )
    assert token.request_id == req_id
    assert token.decision == "APPROVED"
    assert token.resume_run is True

    # Retrieve and validate token
    fetched = manager.get_approval(req_id)
    assert fetched is not None
    manager.validator.validate_binding(
        token=fetched,
        job_id="job-456",
        action="BRANCH_INTEGRATION",
        requested_scope=["feature/task-1"],
    )

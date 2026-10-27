"""Tests for Approval Decision Recording and Channel Handlers (CLI, GMAIL, MANUAL).

Constitutional Invariants (ADR-007, SB-FREEZE-P1-06):
- Approval channels in V1 are strictly CLI, GMAIL, MANUAL (no webhooks).
- Human approver identity is sovereign (e.g. Joaquín).
- Hard denials can NEVER be approved under any circumstance.
- Expiration is strictly fail-closed.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from sacl.approval.channels import (
    CLIChannelHandler,
    GmailChannelHandler,
    ManualChannelHandler,
)
from sacl.approval.manager import BoundedApprovalManager
from sacl.approval.models import Approver
from sacl.contracts.exceptions import (
    ApprovalExpiredError,
    ContractValidationError,
    PolicyDeniedError,
)
from sacl.contracts.invariants import ApprovalChannel


@pytest.fixture
def manager(sqlite_memory_db: sqlite3.Connection) -> BoundedApprovalManager:
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cursor = sqlite_memory_db.cursor()
    cursor.execute(
        """
        INSERT INTO jobs (job_id, status, priority, created_at, updated_at)
        VALUES ('job-dec-001', 'RUNNING', 0, ?, ?)
        """,
        (now_iso, now_iso),
    )
    cursor.execute(
        """
        INSERT INTO runs (
            run_id, job_id, package_id, project, repository, mode,
            source_orchestrator, target_repo_path, run_dir, status,
            ready_for_integration, started_at
        ) VALUES (
            'run-dec-001', 'job-dec-001', 'pkg-001', 'solidbit', 'org/repo', 'isolated_branch',
            '', '', '', 'RUNNING', 'NO', ?
        )
        """,
        (now_iso,),
    )
    sqlite_memory_db.commit()
    return BoundedApprovalManager(db_conn=sqlite_memory_db)


def test_record_approval_decision_approved(manager: BoundedApprovalManager) -> None:
    req_id = manager.create_approval_request(
        job_id="job-dec-001",
        action="STAGE_CONTINUATION",
        scope=["docs/*"],
        run_id="run-dec-001",
    )

    approver = Approver(identity="Joaquín", channel=ApprovalChannel.CLI.value)
    token = manager.record_decision(
        request_id=req_id,
        decision="APPROVED",
        approver=approver,
        notes="Authorized stage 2 execution.",
    )

    assert token.decision == "APPROVED"
    assert token.approver.identity == "Joaquín"
    assert token.approver.channel == "CLI"
    assert token.resume_run is True
    assert token.cannot_override_hard_deny is True
    assert token.notes == "Authorized stage 2 execution."


def test_record_approval_decision_rejected(manager: BoundedApprovalManager) -> None:
    req_id = manager.create_approval_request(
        job_id="job-dec-001",
        action="BRANCH_INTEGRATION",
        scope=["feature/unsafe"],
        run_id="run-dec-001",
    )

    approver = Approver(identity="Joaquín", channel=ApprovalChannel.CLI.value)
    token = manager.record_decision(
        request_id=req_id,
        decision="REJECTED",
        approver=approver,
        notes="Unsafe branch integration rejected.",
    )

    assert token.decision == "REJECTED"
    assert token.notes == "Unsafe branch integration rejected."


def test_record_decision_disallowed_channel_rejected(manager: BoundedApprovalManager) -> None:
    """Disallowed channel (e.g. WEBHOOK) fails schema/invariant validation."""
    req_id = manager.create_approval_request(
        job_id="job-dec-001",
        action="STAGE_CONTINUATION",
        scope=["*"],
    )

    approver = Approver(identity="Joaquín", channel="WEBHOOK")
    with pytest.raises(ContractValidationError):
        manager.record_decision(
            request_id=req_id,
            decision="APPROVED",
            approver=approver,
        )


def test_record_decision_past_expiration_fails_closed(manager: BoundedApprovalManager) -> None:
    """Attempting to approve an expired request fails closed."""
    req_id = manager.create_approval_request(
        job_id="job-dec-001",
        action="STAGE_CONTINUATION",
        scope=["*"],
        ttl_seconds=10,
    )

    future_time = datetime.now(timezone.utc) + timedelta(hours=2)
    approver = Approver(identity="Joaquín", channel=ApprovalChannel.CLI.value)

    with pytest.raises(ApprovalExpiredError) as excinfo:
        manager.record_decision(
            request_id=req_id,
            decision="APPROVED",
            approver=approver,
            reference_time=future_time,
        )
    assert excinfo.value.request_id == req_id


def test_cli_channel_handler(manager: BoundedApprovalManager) -> None:
    cli_handler = CLIChannelHandler(default_identity="Joaquín")
    req_id = manager.create_approval_request(
        job_id="job-dec-001",
        action="STAGE_CONTINUATION",
        scope=["docs/*"],
        reason="Verify documentation",
    )
    req = manager.get_request(req_id)
    assert req is not None

    display = cli_handler.format_request_display(req)
    assert "SACL BOUNDED APPROVAL ACTION GATE" in display
    assert req_id in display
    assert "STAGE_CONTINUATION" in display

    approver = cli_handler.create_cli_approver()
    assert approver.identity == "Joaquín"
    assert approver.channel == "CLI"


def test_gmail_channel_handler() -> None:
    gmail_handler = GmailChannelHandler(authorized_senders={"uniquedraken@gmail.com"})

    # Test subject formatting
    subject = gmail_handler.format_outbound_subject(
        job_id="job-100", request_id="REQ-20261007-001", action="STAGE_CONTINUATION"
    )
    assert subject == "[SACL][APPROVAL][v1][job-100] STAGE_CONTINUATION (REQ-20261007-001)"

    # Test valid inbound reply parsing
    inbound_body = "DECISION: APPROVED\nNOTES: Verified safe for execution.\nREQ-20261007-001"
    req_id, decision, approver, notes = gmail_handler.parse_inbound_decision(
        sender_email="uniquedraken@gmail.com",
        subject="Re: [SACL][APPROVAL][v1][job-100] STAGE_CONTINUATION",
        body_text=inbound_body,
    )

    assert req_id == "REQ-20261007-001"
    assert decision == "APPROVED"
    assert approver.identity == "Joaquín"
    assert approver.channel == "GMAIL"
    assert notes == "Verified safe for execution."

    # Test unauthorized sender rejection
    with pytest.raises(PolicyDeniedError):
        gmail_handler.parse_inbound_decision(
            sender_email="attacker@external.com",
            subject="Re: [SACL][APPROVAL][v1][job-100]",
            body_text=inbound_body,
        )


def test_manual_channel_handler(tmp_path: Path, manager: BoundedApprovalManager) -> None:
    manual_handler = ManualChannelHandler()

    req_id = manager.create_approval_request(
        job_id="job-dec-001",
        action="SPECIFICATION_MATERIALIZATION",
        scope=["docs/*"],
    )
    approver = Approver(identity="Joaquín", channel=ApprovalChannel.MANUAL.value)
    token = manager.record_decision(
        request_id=req_id,
        decision="APPROVED",
        approver=approver,
    )

    # Save to disk
    token_file = tmp_path / "approval.token.json"
    manual_handler.save_token_to_file(token, token_file)
    assert token_file.exists()

    # Load and validate
    loaded = manual_handler.load_token_from_file(token_file)
    assert loaded.request_id == req_id
    assert loaded.decision == "APPROVED"
    assert loaded.approver.channel == "MANUAL"

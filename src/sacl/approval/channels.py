"""SACL V1 Approval Channel Handlers.

Constitutional Invariants (ADR-007, docs/MAIL_PROTOCOL.md):
- Approval channels are strictly CLI, GMAIL, MANUAL (zero webhooks in V1).
- Outbound Gmail approval requests use routing hint: [SACL][APPROVAL][<JOB_ID>]
- Approver identities are verified against authorized human sovereigns.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional, Tuple

from sacl.approval.models import ApprovalRequest, ApprovalToken, Approver, utc_now_iso
from sacl.approval.validator import BoundedApprovalValidator, token_to_schema_dict
from sacl.contracts.exceptions import ContractValidationError, PolicyDeniedError
from sacl.contracts.invariants import ApprovalChannel, ApprovalDecision

DEFAULT_SOVEREIGN_IDENTITY = "Joaquín"
AUTHORIZED_EMAIL_SENDERS = {"uniquedraken@gmail.com"}


class CLIChannelHandler:
    """Handles bounded approvals attested via the Command Line Interface."""

    def __init__(self, default_identity: str = DEFAULT_SOVEREIGN_IDENTITY) -> None:
        self.default_identity = default_identity

    def format_request_display(self, req: ApprovalRequest) -> str:
        """Formats an approval request for terminal display."""
        lines = [
            "==================================================",
            "        SACL BOUNDED APPROVAL ACTION GATE         ",
            "==================================================",
            f"Request ID:  {req.request_id}",
            f"Job ID:      {req.job_id}",
            f"Run ID:      {req.run_id or 'N/A'}",
            f"Action:      {req.action}",
            f"Scope:       {', '.join(req.scope)}",
            f"Expires At:  {req.expires_at} (Fail-Closed)",
        ]
        if req.reason:
            lines.append(f"Reason:      {req.reason}")
        if req.prohibited_actions:
            lines.append(f"Prohibited:  {', '.join(req.prohibited_actions)}")
        lines.append("--------------------------------------------------")
        lines.append("To approve via CLI, run with APPROVED and identity.")
        lines.append("Hard local policy denies CANNOT be overridden.")
        lines.append("==================================================")
        return "\n".join(lines)

    def create_cli_approver(
        self,
        identity: Optional[str] = None,
        approved_at: Optional[str] = None,
    ) -> Approver:
        """Constructs a valid Approver record for CLI channel."""
        return Approver(
            identity=identity or self.default_identity,
            channel=ApprovalChannel.CLI.value,
            approved_at=approved_at or utc_now_iso(),
        )


class GmailChannelHandler:
    """Handles bounded approvals initiated or decided via Gmail transport."""

    def __init__(
        self,
        authorized_senders: Optional[set[str]] = None,
        default_identity: str = DEFAULT_SOVEREIGN_IDENTITY,
    ) -> None:
        self.authorized_senders = (
            set(authorized_senders)
            if authorized_senders is not None
            else set(AUTHORIZED_EMAIL_SENDERS)
        )
        self.default_identity = default_identity

    def format_outbound_subject(self, job_id: str, request_id: str, action: str) -> str:
        """Formats canonical Gmail subject intake routing hint for approval request."""
        return f"[SACL][APPROVAL][v1][{job_id}] {action} ({request_id})"

    def format_outbound_body(self, req: ApprovalRequest) -> str:
        """Constructs markdown body for outbound approval email."""
        return (
            f"# SACL Bounded Approval Request: {req.action}\n\n"
            f"A bounded human approval gate has been encountered.\n\n"
            f"- **Request ID:** `{req.request_id}`\n"
            f"- **Job ID:** `{req.job_id}`\n"
            f"- **Run ID:** `{req.run_id or 'N/A'}`\n"
            f"- **Action:** `{req.action}`\n"
            f"- **Scope:** `{', '.join(req.scope)}`\n"
            f"- **Expires At:** `{req.expires_at}` (Strict fail-closed expiration)\n"
            f"- **Reason:** {req.reason or 'Action requires sovereign human sign-off.'}\n\n"
            f"> [!IMPORTANT]\n"
            f"> Reply to this message with `DECISION: APPROVED` or `DECISION: REJECTED`.\n"
            f"> Approvals resume the same logical run and cannot override hard local policy.\n"
        )

    def parse_inbound_decision(
        self,
        sender_email: str,
        subject: str,
        body_text: str,
    ) -> Tuple[str, str, Approver, Optional[str]]:
        """Parses an inbound approval email reply.

        Returns:
            Tuple of (request_id, decision, approver, notes)
        Raises:
            PolicyDeniedError: If sender is not authorized.
            ContractValidationError: If email does not contain valid approval syntax.
        """
        clean_sender = sender_email.strip().lower()
        if clean_sender not in self.authorized_senders:
            raise PolicyDeniedError(
                action="GMAIL_APPROVAL",
                layer="SENDER_AUTHORIZATION",
                reason=f"Sender '{sender_email}' is not in authorized approver whitelist {self.authorized_senders}",
            )

        # Extract request ID from subject or body
        req_match = re.search(r"\b(REQ-[A-Za-z0-9_-]+)\b", f"{subject}\n{body_text}", re.IGNORECASE)
        if not req_match:
            raise ContractValidationError(
                schema_name="approval",
                message="Inbound approval email does not contain a valid request_id token.",
            )
        request_id = req_match.group(1).upper()

        # Extract decision
        dec_match = re.search(
            r"DECISION\s*:\s*(APPROVED|REJECTED|DEFERRED)", body_text, re.IGNORECASE
        )
        if not dec_match:
            # Fallback check simple keyword
            if re.search(r"\bAPPROVED\b", body_text, re.IGNORECASE):
                decision = ApprovalDecision.APPROVED.value
            elif re.search(r"\bREJECTED\b", body_text, re.IGNORECASE):
                decision = ApprovalDecision.REJECTED.value
            else:
                raise ContractValidationError(
                    schema_name="approval",
                    message="Could not parse explicit decision (APPROVED/REJECTED) from email body.",
                )
        else:
            decision = dec_match.group(1).upper()

        notes = None
        notes_match = re.search(r"NOTES\s*:\s*(.+)", body_text, re.IGNORECASE)
        if notes_match:
            notes = notes_match.group(1).strip()

        approver = Approver(
            identity=self.default_identity,
            channel=ApprovalChannel.GMAIL.value,
            approved_at=utc_now_iso(),
        )

        return request_id, decision, approver, notes


class ManualChannelHandler:
    """Handles manual file-based approval token imports and exports."""

    def __init__(self, validator: Optional[BoundedApprovalValidator] = None) -> None:
        self.validator = validator or BoundedApprovalValidator()

    def load_token_from_file(self, file_path: Path) -> ApprovalToken:
        """Loads and parses an approval token from a JSON file.

        Raises:
            FileNotFoundError: If token file does not exist.
            ContractValidationError: If token fails schema or invariants.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Approval file '{file_path}' does not exist.")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        token = ApprovalToken.from_dict(data)
        # Verify that channel is MANUAL or valid
        if token.approver.channel != ApprovalChannel.MANUAL.value:
            if token.approver.channel not in {
                ApprovalChannel.CLI.value,
                ApprovalChannel.GMAIL.value,
            }:
                raise ContractValidationError(
                    schema_name="approval",
                    message=f"Invalid channel '{token.approver.channel}' in manual token file.",
                )
        self.validator.validate_invariants(token)
        return token

    def save_token_to_file(self, token: ApprovalToken, target_path: Path) -> None:
        """Serializes an approval token to disk in canonical JSON format."""
        target_path.parent.mkdir(parents=True, exist_ok=True)
        schema_dict = token_to_schema_dict(token)
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(schema_dict, f, indent=2)


__all__ = [
    "CLIChannelHandler",
    "GmailChannelHandler",
    "ManualChannelHandler",
    "DEFAULT_SOVEREIGN_IDENTITY",
    "AUTHORIZED_EMAIL_SENDERS",
]

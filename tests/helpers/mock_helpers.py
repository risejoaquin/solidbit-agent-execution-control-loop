"""SACL V1 Test Mock Helpers.

Provides generators for mock reports, mock logs, mock envelopes, and mock processes.
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, Optional


def create_mock_report_content(
    agent_id: str = "AG-TEST",
    verdict: str = "PASS",
    marker_type: str = "PRIMARY",  # PRIMARY, HEADER, NONE
    num_body_lines: int = 10,
) -> str:
    """Generates synthetic deliverable report markdown text."""
    lines = [
        f"# Deliverable Report: {agent_id}",
        "",
        "## Summary",
        f"This is an automated report for agent {agent_id}.",
        "",
        "## Execution Evidence",
    ]
    for i in range(num_body_lines):
        lines.append(f"- Step {i + 1}: Completed operation successfully.")
    lines.append("")

    if marker_type == "PRIMARY":
        lines.append("## Canonical Outcome")
        lines.append(f"AGENT_{agent_id.replace('-', '_')}_RESULT = {verdict}")
    elif marker_type == "HEADER":
        # Put header in first 25 lines
        lines.insert(2, f"**Final Status:** {verdict}")
    elif marker_type == "NONE":
        lines.append("Execution concluded without marker.")

    return "\n".join(lines) + "\n"


def create_mock_log_content(
    agent_id: str = "AG-TEST",
    verdict: Optional[str] = None,
    num_lines: int = 200,
) -> str:
    """Generates synthetic stdout log text with an optional tail marker."""
    lines = [f"[INFO] Initializing agent worker {agent_id}"]
    for i in range(num_lines):
        lines.append(f"[INFO] Worker loop iteration {i}: healthy")
    if verdict:
        lines.append(f"AGENT_{agent_id.replace('-', '_')}_RESULT = {verdict}")
    lines.append("[INFO] Worker process shutting down gracefully.")
    return "\n".join(lines) + "\n"


def create_mock_mail_payload(
    job_id: str = "job-20261007-001",
    nonce: str = "abcdef0123456789",
    status: str = "RECEIVED",
) -> Dict[str, Any]:
    """Generates a valid MailEnvelope dictionary for testing."""
    return {
        "schema": "solidbit.mail-envelope.v1",
        "message_id": f"<{job_id}@mail.invalid>",
        "history_id": "100001",
        "thread_id": "thread-001",
        "direction": "INBOUND",
        "sender": "uniquedraken@gmail.com",
        "recipient": "uniquedraken@gmail.com",
        "routing_subject": {
            "raw_subject": f"[SACL][JOB][v1][{job_id}] Test Package",
            "routing_prefix": "[SACL][JOB][v1]",
            "job_id": job_id,
            "is_valid_routing_hint": True,
        },
        "delivery_semantics": "AT_LEAST_ONCE",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "nonce": nonce,
        "attachment": {
            "filename": "package.zip",
            "size_bytes": 1024,
            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "mime_type": "application/zip",
        },
        "status": status,
        "signature_hmac": None,
        "rejection_reason": None,
        "run_id": None,
    }

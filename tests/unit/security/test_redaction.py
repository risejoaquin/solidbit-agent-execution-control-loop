"""Unit tests for SACL V1 Secret Redaction and Zero Secrets Policy."""

from __future__ import annotations

import io

import pytest

from sacl.security.exceptions import SecretLeakError
from sacl.security.redaction import (
    REDACTION_MARKER,
    StreamingSecretRedactor,
    assert_zero_secrets,
    redact_secrets,
    scan_for_secrets,
)


class TestSecretPatternRedaction:
    """Tests redaction filter against specific token types (Threat I1 / TH-09)."""

    def test_github_classic_pat_redacted(self) -> None:
        raw = "Auth token is ghp_1234567890abcdefghijklmnopqrstuvwxyz for repo access."
        redacted = redact_secrets(raw)
        assert "ghp_" not in redacted
        assert REDACTION_MARKER in redacted
        assert redacted == f"Auth token is {REDACTION_MARKER} for repo access."

    def test_github_oauth_token_redacted(self) -> None:
        raw = "OAuth: gho_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        redacted = redact_secrets(raw)
        assert "gho_" not in redacted
        assert REDACTION_MARKER in redacted

    def test_github_fine_grained_pat_redacted(self) -> None:
        raw = "PAT: github_pat_11ABCDEFG0123456789012_abcdefghijklmnopqrstuvwxyz012345678901234567890123456789012345678"
        redacted = redact_secrets(raw)
        assert "github_pat_" not in redacted
        assert REDACTION_MARKER in redacted

    def test_google_api_key_redacted(self) -> None:
        raw = "Connecting to Maps with AIzaSyD-1234567890abcdefghijklmnopqrst"
        redacted = redact_secrets(raw)
        assert "AIza" not in redacted
        assert REDACTION_MARKER in redacted

    def test_google_oauth_token_redacted(self) -> None:
        raw = "Bearer ya29.a0AfH6SMC123456789abcdefghijklmnopqrstuvwxyz"
        redacted = redact_secrets(raw)
        assert "ya29." not in redacted
        assert REDACTION_MARKER in redacted

    def test_railway_token_redacted(self) -> None:
        raw = "Deploying with railway_1234567890abcdef12345678"
        redacted = redact_secrets(raw)
        assert "railway_" not in redacted
        assert REDACTION_MARKER in redacted

    def test_bearer_authorization_header_redacted(self) -> None:
        raw = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.sometokenpayload12345"
        redacted = redact_secrets(raw)
        assert "eyJhbGci" not in redacted
        assert f"Bearer {REDACTION_MARKER}" in redacted

    def test_pem_private_key_redacted(self) -> None:
        raw = (
            "-----BEGIN RSA PRIVATE KEY-----\n"
            "MIIEowIBAAKCAQEA0Y1234567890abcdef\n"
            "-----END RSA PRIVATE KEY-----"
        )
        redacted = redact_secrets(raw)
        assert "MIIEow" not in redacted
        assert REDACTION_MARKER in redacted

    def test_generic_secret_assignment_redacted(self) -> None:
        raw = 'api_key = "supersecretvalue123456"'
        redacted = redact_secrets(raw)
        assert "supersecretvalue123456" not in redacted
        assert f'api_key = "{REDACTION_MARKER}"' in redacted


class TestStreamingRedactor:
    """Tests streaming wrapper for stdout/stderr redaction."""

    def test_streaming_redactor_masks_writes(self) -> None:
        buf = io.StringIO()
        stream = StreamingSecretRedactor(buf)

        stream.write("Worker log: ghp_1234567890abcdefghijklmnopqrstuvwxyz initialized\n")
        stream.write("Calling service with AIzaSyD-1234567890abcdefghijklmnopqrst\n")
        stream.flush()

        output = buf.getvalue()
        assert "ghp_" not in output
        assert "AIza" not in output
        assert REDACTION_MARKER in output


class TestSecretScannerAndZeroSecretsAssertion:
    """Tests forensic secret detection and Zero Secrets Policy enforcement."""

    def test_scan_for_secrets_detects_findings(self) -> None:
        content = (
            "Line 1: clean\nLine 2: token ghp_1234567890abcdefghijklmnopqrstuvwxyz\nLine 3: clean\n"
        )
        findings = scan_for_secrets(content)
        assert len(findings) == 1
        assert findings[0].line_number == 2
        assert findings[0].secret_type == "GITHUB_TOKEN_GHP"
        assert "***" in findings[0].masked_preview

    def test_assert_zero_secrets_passes_on_clean_data(self) -> None:
        clean_data = {
            "task": "build_docs",
            "parameters": ["--verbose", "--output", "dist"],
        }
        # Should not raise
        assert_zero_secrets(clean_data)

    def test_assert_zero_secrets_raises_on_leaked_token(self) -> None:
        dirty_dict = {
            "task": "fetch_data",
            "auth": "AIzaSyD-1234567890abcdefghijklmnopqrst",
        }
        with pytest.raises(SecretLeakError) as exc_info:
            assert_zero_secrets(dirty_dict, context="manifest_config")
        assert "SECRET_LEAK_DETECTED" in exc_info.value.message
        assert exc_info.value.secret_type == "GOOGLE_API_KEY"

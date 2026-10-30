"""SACL V1 Secret Redaction and Zero-Secrets Invariant Engine.

Implements Threat I1 / TH-09 & Security Policy §3.1:
- Streaming regex log scrubbing on stdout/stderr
- Redaction replacement token: [REDACTED_SECRET]
- Scrubs GitHub tokens, Google API keys, Railway tokens, Bearer headers, Private Keys
- Zero secrets enforcement in state and manifests
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, List, Optional, Pattern, TextIO, Tuple

from sacl.security.exceptions import SecretLeakError

REDACTION_MARKER: str = "[REDACTED_SECRET]"

# Compiled secret patterns
SECRET_PATTERNS: List[Tuple[str, Pattern[str]]] = [
    # GitHub Classic and Fine-grained PATs & tokens
    ("GITHUB_FINE_GRAINED_PAT", re.compile(r"github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}")),
    ("GITHUB_TOKEN_GHP", re.compile(r"ghp_[a-zA-Z0-9]{36}")),
    ("GITHUB_TOKEN_GHO", re.compile(r"gho_[a-zA-Z0-9]{36}")),
    ("GITHUB_TOKEN_GHU", re.compile(r"ghu_[a-zA-Z0-9]{36}")),
    ("GITHUB_TOKEN_GHS", re.compile(r"ghs_[a-zA-Z0-9]{36}")),
    ("GITHUB_TOKEN_GHR", re.compile(r"ghr_[a-zA-Z0-9]{36}")),
    # Google API Keys
    ("GOOGLE_API_KEY", re.compile(r"AIza[0-9A-Za-z\-_]{30,40}")),
    # Google OAuth Tokens
    ("GOOGLE_OAUTH_TOKEN", re.compile(r"ya29\.[0-9A-Za-z\-_]+")),
    # Railway Tokens
    ("RAILWAY_TOKEN", re.compile(r"(?:railway_[a-zA-Z0-9]{24,}|ral_[a-zA-Z0-9]{32,})")),
    # PEM Private Keys
    (
        "PEM_PRIVATE_KEY",
        re.compile(
            r"-----BEGIN (?:[A-Z ]+)?PRIVATE KEY-----[\s\S]*?-----END (?:[A-Z ]+)?PRIVATE KEY-----"
        ),
    ),
    # Authorization / Bearer headers
    ("BEARER_TOKEN", re.compile(r"(?i)\bBearer\s+[a-zA-Z0-9_\-\.]{24,}")),
    ("BASIC_AUTH", re.compile(r"(?i)\bBasic\s+[a-zA-Z0-9+/=]{24,}")),
    # Generic secret assignments (e.g. api_key="secret", password='value')
    (
        "GENERIC_SECRET_ASSIGNMENT",
        re.compile(
            r"""(?i)(?:api[_-]?key|client[_-]?secret|auth[_-]?token|secret[_-]?key)\s*[:=]\s*['"]([a-zA-Z0-9_\-\.]{16,})['"]"""
        ),
    ),
]


@dataclass(frozen=True)
class SecretFinding:
    """Forensic record of a detected unmasked secret."""

    secret_type: str
    line_number: int
    masked_preview: str


class SecretRedactor:
    """Engine for redacting sensitive credentials and enforcing zero-secrets invariants."""

    def __init__(
        self,
        patterns: Optional[List[Tuple[str, Pattern[str]]]] = None,
        redaction_marker: str = REDACTION_MARKER,
    ) -> None:
        self.patterns = patterns or SECRET_PATTERNS
        self.redaction_marker = redaction_marker

    def redact(self, text: str) -> str:
        """Applies all credential scrubbing patterns, replacing sensitive tokens with REDACTION_MARKER."""
        if not text:
            return text

        result = text
        for stype, pattern in self.patterns:
            if stype == "GENERIC_SECRET_ASSIGNMENT":
                result = pattern.sub(self._mask_assignment, result)
            elif stype == "BEARER_TOKEN":
                result = pattern.sub(f"Bearer {self.redaction_marker}", result)
            elif stype == "BASIC_AUTH":
                result = pattern.sub(f"Basic {self.redaction_marker}", result)
            else:
                result = pattern.sub(self.redaction_marker, result)

        return result

    def _mask_assignment(self, match: re.Match[str]) -> str:
        full = match.group(0)
        val = match.group(1)
        return full.replace(val, self.redaction_marker, 1)

    def scan(self, text: str) -> List[SecretFinding]:
        """Scans text and returns list of detected secret matches without modifying text."""
        findings: List[SecretFinding] = []
        if not text:
            return findings

        lines = text.splitlines()
        for line_idx, line in enumerate(lines, start=1):
            for stype, pattern in self.patterns:
                for match in pattern.finditer(line):
                    matched_str = match.group(0)
                    preview = (
                        matched_str[:4] + "***" + matched_str[-4:]
                        if len(matched_str) >= 10
                        else "***"
                    )
                    findings.append(
                        SecretFinding(
                            secret_type=stype,
                            line_number=line_idx,
                            masked_preview=preview,
                        )
                    )
        return findings

    def assert_zero_secrets(self, data: Any, context: str = "payload") -> None:
        """Enforces the Zero Secrets Policy.

        Scans data (str, dict, list) and raises SecretLeakError if any secrets are present.
        """
        text_repr = ""
        if isinstance(data, str):
            text_repr = data
        elif isinstance(data, (dict, list)):
            text_repr = str(data)
        else:
            text_repr = repr(data)

        findings = self.scan(text_repr)
        if findings:
            first = findings[0]
            raise SecretLeakError(
                secret_type=first.secret_type,
                context=f"{context} (line {first.line_number})",
                sample_masked=first.masked_preview,
            )


class StreamingSecretRedactor:
    """Wraps an output stream (e.g. log file or stdout) to redact secrets in real time."""

    def __init__(
        self,
        underlying_stream: TextIO,
        redactor: Optional[SecretRedactor] = None,
    ) -> None:
        self.underlying_stream = underlying_stream
        self.redactor = redactor or SecretRedactor()

    def write(self, data: str) -> int:
        """Redacts data before forwarding to underlying stream."""
        sanitized = self.redactor.redact(data)
        return self.underlying_stream.write(sanitized)

    def flush(self) -> None:
        self.underlying_stream.flush()

    def close(self) -> None:
        self.underlying_stream.close()


# Module-level convenience functions
_DEFAULT_REDACTOR = SecretRedactor()


def redact_secrets(text: str) -> str:
    """Redacts secrets in text using default SACL V1 patterns."""
    return _DEFAULT_REDACTOR.redact(text)


def scan_for_secrets(text: str) -> List[SecretFinding]:
    """Scans text for secrets using default SACL V1 patterns."""
    return _DEFAULT_REDACTOR.scan(text)


def assert_zero_secrets(data: Any, context: str = "payload") -> None:
    """Asserts zero secrets in data; raises SecretLeakError if detected."""
    _DEFAULT_REDACTOR.assert_zero_secrets(data, context=context)

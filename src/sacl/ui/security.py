"""Security primitives for the SACL Decision Shell.

Provides a per-installation secret, HMAC-bound gate decision tokens,
inbound webhook tokens, and Svix (Resend webhook) signature verification.
All comparisons are constant-time.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import os
import secrets
import time
from pathlib import Path
from typing import Mapping, Optional

logger = logging.getLogger("sacl.ui.security")

SECRET_ENV = "SACL_UI_SECRET"
SECRET_FILENAME = ".sacl_ui_secret"
SVIX_TOLERANCE_SECONDS = 300


def load_or_create_secret(base_dir: Optional[Path] = None) -> bytes:
    """Returns the installation secret.

    Priority: ``SACL_UI_SECRET`` env var, then a persisted file next to the
    operational database, otherwise a freshly generated secret that is
    persisted so that links sent by email survive server restarts.
    """
    env_val = os.environ.get(SECRET_ENV)
    if env_val:
        return env_val.encode("utf-8")

    base = Path(base_dir) if base_dir else Path.cwd()
    secret_file = base / SECRET_FILENAME
    try:
        if secret_file.exists():
            content = secret_file.read_text(encoding="ascii").strip()
            if len(content) >= 32:
                return content.encode("ascii")
        value = secrets.token_urlsafe(48)
        secret_file.write_text(value, encoding="ascii")
        try:
            os.chmod(secret_file, 0o600)
        except OSError:
            pass
        return value.encode("ascii")
    except OSError as exc:
        logger.warning(f"Could not persist UI secret ({exc}); using ephemeral secret")
        return secrets.token_urlsafe(48).encode("ascii")


def _hmac_hex(secret: bytes, message: str, length: int = 32) -> str:
    return hmac.new(secret, message.encode("utf-8"), hashlib.sha256).hexdigest()[:length]


def sign_gate_token(secret: bytes, request_id: str) -> str:
    """Token binding a quick-decision link to one specific approval request."""
    return _hmac_hex(secret, f"gate-quick-decide:{request_id}")


def verify_gate_token(secret: bytes, request_id: str, token: Optional[str]) -> bool:
    if not request_id or not token:
        return False
    return hmac.compare_digest(sign_gate_token(secret, request_id), token)


def inbound_webhook_token(secret: bytes) -> str:
    """Static (per installation) token that must accompany inbound email webhooks."""
    return _hmac_hex(secret, "inbound-email-webhook", length=40)


def verify_inbound_token(secret: bytes, token: Optional[str]) -> bool:
    if not token:
        return False
    return hmac.compare_digest(inbound_webhook_token(secret), token)


def verify_svix_signature(
    webhook_secret: str,
    headers: Mapping[str, str],
    raw_body: bytes,
    now: Optional[float] = None,
    tolerance: int = SVIX_TOLERANCE_SECONDS,
) -> bool:
    """Verifies a Svix-signed webhook (the scheme used by Resend webhooks).

    Signed content is ``{svix-id}.{svix-timestamp}.{body}``, HMAC-SHA256 with the
    base64-decoded part of the ``whsec_...`` secret. The ``svix-signature`` header
    may carry several space-separated ``v1,<base64>`` signatures.
    """

    def _h(name: str) -> str:
        for key, value in headers.items():
            if key.lower() == name:
                return value or ""
        return ""

    msg_id = _h("svix-id")
    timestamp = _h("svix-timestamp")
    signature_header = _h("svix-signature")
    if not (msg_id and timestamp and signature_header and webhook_secret):
        return False

    try:
        ts = int(timestamp)
    except ValueError:
        return False
    current = time.time() if now is None else now
    if abs(current - ts) > tolerance:
        return False

    secret_part = (
        webhook_secret.split("_", 1)[1] if webhook_secret.startswith("whsec_") else webhook_secret
    )
    try:
        key = base64.b64decode(secret_part)
    except Exception:
        return False

    signed = msg_id.encode("utf-8") + b"." + timestamp.encode("utf-8") + b"." + raw_body
    expected = base64.b64encode(hmac.new(key, signed, hashlib.sha256).digest()).decode("ascii")

    for candidate in signature_header.split():
        version, _, sig = candidate.partition(",")
        if version == "v1" and hmac.compare_digest(sig, expected):
            return True
    return False

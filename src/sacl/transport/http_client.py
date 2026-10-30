"""Secure HTTP client and URL utilities enforcing scheme restrictions (CWE-22 / Bandit B310)."""

from __future__ import annotations

import urllib.parse
import urllib.request
from typing import Any


def safe_urlopen(url_or_req: Any, *args: Any, **kwargs: Any) -> Any:
    """Safe wrapper around urllib.request.urlopen verifying permitted schemes ('http', 'https').

    Prevents unexpected use of file://, gopher://, ftp:// or custom local schemes (LFI / SSRF).
    """
    if isinstance(url_or_req, str):
        url = url_or_req
    elif hasattr(url_or_req, "full_url"):
        url = url_or_req.full_url
    else:
        url = str(url_or_req)

    parsed = urllib.parse.urlparse(url)
    if parsed.scheme.lower() not in ("http", "https") or not parsed.netloc:
        raise ValueError(
            f"URL scheme not allowed or invalid destination: '{parsed.scheme}://{parsed.netloc}'"
        )

    return urllib.request.urlopen(url_or_req, *args, **kwargs)  # nosec B310

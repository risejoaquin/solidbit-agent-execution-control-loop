"""Detect ambiguous ZIP member destinations before archive extraction.

Windows worktrees are case-insensitive by default; separators and redundant
segments may resolve to the same extraction target. Reject collisions rather
than depending on zipfile's last-entry-wins behavior.
"""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Iterable, Optional, Tuple
import zipfile


def find_ambiguous_member(entries: Iterable[zipfile.ZipInfo]) -> Optional[Tuple[str, str]]:
    """Return first conflicting pair, or None if member destinations are unique.

    An empty/root-only member is rejected as an ambiguity with itself. The
    caller must also apply its existing traversal, device-name and ADS checks.
    """
    seen: dict[str, str] = {}
    for entry in entries:
        name = entry.filename
        normalized = PurePosixPath(name.replace("\\", "/")).as_posix().rstrip("/")
        if normalized in ("", "."):
            return (name, name)
        key = normalized.casefold()
        if key in seen:
            return (seen[key], name)
        seen[key] = name
    return None

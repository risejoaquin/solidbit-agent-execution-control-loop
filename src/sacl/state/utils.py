"""SACL V1 State Store Utilities.

Helper functions for UTC timestamps, SHA-256 calculation, path normalization,
and SQLite row serialization.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import sqlite3


def utc_now() -> str:
    """Returns current UTC timestamp in strict ISO-8601 UTC format (YYYY-MM-DDTHH:MM:SSZ)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def format_utc(dt: datetime) -> str:
    """Formats a datetime object to canonical ISO-8601 UTC string (YYYY-MM-DDTHH:MM:SSZ)."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_utc(dt_str: str) -> datetime:
    """Parses an ISO-8601 UTC string into a timezone-aware datetime object."""
    cleaned = dt_str.strip()
    if cleaned.endswith("Z"):
        cleaned = cleaned[:-1] + "+00:00"
    return datetime.fromisoformat(cleaned).astimezone(timezone.utc)


def normalize_repo_path(path: Union[str, Path]) -> str:
    """Normalizes filesystem path to use forward slashes (/) per storage boundary invariants."""
    return str(path).replace("\\", "/")


def calculate_sha256(content_or_path: Union[bytes, str, Path]) -> str:
    """Calculates SHA-256 hexadecimal digest for bytes, string, or a file on disk."""
    hasher = hashlib.sha256()
    if isinstance(content_or_path, (str, Path)) and Path(str(content_or_path)).is_file():
        with open(content_or_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
    elif isinstance(content_or_path, str):
        hasher.update(content_or_path.encode("utf-8"))
    elif isinstance(content_or_path, bytes):
        hasher.update(content_or_path)
    else:
        raise TypeError(f"Unsupported content type for SHA-256 hashing: {type(content_or_path)}")
    return hasher.hexdigest()


def row_to_dict(row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
    """Converts a sqlite3.Row instance to a standard Python dictionary."""
    if row is None:
        return None
    return dict(row)


def rows_to_dicts(rows: List[sqlite3.Row]) -> List[Dict[str, Any]]:
    """Converts a list of sqlite3.Row instances to a list of standard Python dictionaries."""
    return [dict(r) for r in rows]


def json_dumps_safe(data: Any) -> Optional[str]:
    """Safely serializes Python data structure to JSON string; returns None if input is None."""
    if data is None:
        return None
    return json.dumps(data)


def json_loads_safe(data_str: Optional[str]) -> Optional[Any]:
    """Safely deserializes JSON string; returns None if input is None or empty."""
    if not data_str:
        return None
    try:
        return json.loads(data_str)
    except Exception:
        return None

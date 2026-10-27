"""Evidence & Audit Center UI Module.

Lists and previews generated evidence reports, diffs, test logs,
and SHA-256 verification packages.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("sacl.ui.modules.evidence")


class EvidenceModule:
    """Manages discovery and inspection of campaign evidence packages."""

    def __init__(self, evidence_dirs: Optional[List[Path]] = None) -> None:
        if evidence_dirs:
            self.evidence_dirs = evidence_dirs
        else:
            self.evidence_dirs = [
                Path.home()
                / "Documents"
                / "Stable-Ecommerce-Orchestrator"
                / "SACL_ORCHESTRATOR_IMPLEMENTATION_CAMPAIGN_v1_PREPARED"
                / "evidence",
                Path.home()
                / "Documents"
                / "Stable-Ecommerce-Orchestrator"
                / "SACL_IMPLEMENTATION_CAMPAIGN_v1"
                / "runs"
                / "impl-20261007-203727-e69378"
                / "evidence",
                Path("evidence"),
            ]

    def list_evidence(self) -> List[Dict[str, Any]]:
        """Discovers evidence files across campaign directories."""
        files = []
        seen_names = set()
        for ed in self.evidence_dirs:
            if not ed.exists():
                continue
            for item in ed.glob("*.*"):
                if item.name in seen_names or item.name.startswith("."):
                    continue
                seen_names.add(item.name)
                stat = item.stat()
                files.append(
                    {
                        "name": item.name,
                        "path": str(item),
                        "size_bytes": stat.st_size,
                        "modified_at": stat.st_mtime,
                        "type": "markdown" if item.suffix == ".md" else "data",
                    }
                )
        return sorted(files, key=lambda x: x["name"])

    def read_report(self, filename: str) -> Dict[str, Any]:
        """Reads a specific evidence report."""
        clean_name = Path(filename).name  # Prevent directory traversal
        for ed in self.evidence_dirs:
            target = ed / clean_name
            if target.exists() and target.is_file():
                try:
                    content = target.read_text(encoding="utf-8", errors="replace")
                    sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
                    return {
                        "name": clean_name,
                        "found": True,
                        "sha256": sha,
                        "content": content,
                    }
                except Exception as exc:
                    return {"name": clean_name, "found": False, "error": str(exc)}

        return {"name": clean_name, "found": False, "error": "Report not found"}

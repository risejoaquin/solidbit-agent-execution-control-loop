"""Git Diff and Working Tree Inspector for SolidBit SACL UI.

Extracts real unstaged and staged git diffs, parses unified diff chunks,
and provides structured visual telemetry for the Diff Inspector modal
and HITL Decision Gate reviews.
"""

from __future__ import annotations

import logging
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("sacl.ui.modules.diff")


class GitDiffModule:
    """Extracts and parses git diffs from the workspace repository."""

    def __init__(self, workspace_root: Optional[Path] = None) -> None:
        self.workspace_root = workspace_root or Path.cwd()

    def get_status(self) -> Dict[str, Any]:
        """Runs git status --porcelain to list all dirty files."""
        try:
            res = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=str(self.workspace_root),
                capture_output=True,
                text=True,
                timeout=5,
                encoding="utf-8",
                errors="replace",
            )
            if res.returncode != 0:
                return {"success": False, "error": res.stderr.strip()}

            files: List[Dict[str, str]] = []
            for line in res.stdout.splitlines():
                if not line or len(line) < 3:
                    continue
                code = line[:2].strip()
                path = line[3:].strip()
                status = "modified"
                if "?" in code:
                    status = "untracked"
                elif "A" in code:
                    status = "added"
                elif "D" in code:
                    status = "deleted"
                elif "R" in code:
                    status = "renamed"

                files.append(
                    {
                        "path": path,
                        "status": status,
                        "code": code,
                    }
                )

            # Get current branch and commit
            branch_res = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=str(self.workspace_root),
                capture_output=True,
                text=True,
                timeout=3,
            )
            branch = branch_res.stdout.strip() if branch_res.returncode == 0 else "unknown"

            commit_res = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=str(self.workspace_root),
                capture_output=True,
                text=True,
                timeout=3,
            )
            commit = commit_res.stdout.strip() if commit_res.returncode == 0 else "unknown"

            return {
                "success": True,
                "branch": branch,
                "commit": commit,
                "clean": len(files) == 0,
                "total_changed": len(files),
                "files": files,
            }
        except Exception as exc:
            logger.warning(f"git status failed: {exc}")
            return {"success": False, "error": str(exc), "files": []}

    def get_unified_diff(self, target_file: Optional[str] = None) -> Dict[str, Any]:
        """Extracts and parses git diff into structured per-file hunks."""
        cmd = ["git", "diff", "HEAD"]
        if target_file:
            cmd.extend(["--", target_file])

        try:
            res = subprocess.run(
                cmd,
                cwd=str(self.workspace_root),
                capture_output=True,
                text=True,
                timeout=10,
                encoding="utf-8",
                errors="replace",
            )

            # If diff against HEAD is empty, also try unstaged diff
            diff_text = res.stdout
            if not diff_text.strip():
                unstaged_res = subprocess.run(
                    ["git", "diff"],
                    cwd=str(self.workspace_root),
                    capture_output=True,
                    text=True,
                    timeout=5,
                    encoding="utf-8",
                    errors="replace",
                )
                diff_text = unstaged_res.stdout

            parsed_files = self._parse_diff_output(diff_text)

            # Also check untracked files if any
            status_info = self.get_status()
            untracked_paths = [
                f["path"] for f in status_info.get("files", []) if f["status"] == "untracked"
            ]

            for u_path in untracked_paths:
                if target_file and u_path != target_file:
                    continue
                full_p = self.workspace_root / u_path
                if full_p.is_file():
                    try:
                        content = full_p.read_text(encoding="utf-8", errors="replace")
                        lines = content.splitlines()
                        chunks = [
                            {
                                "header": f"@@ -0,0 +1,{len(lines)} @@",
                                "lines": [
                                    {
                                        "type": "add",
                                        "text": line,
                                        "old_num": None,
                                        "new_num": idx + 1,
                                    }
                                    for idx, line in enumerate(lines[:300])
                                ],
                            }
                        ]
                        parsed_files.append(
                            {
                                "path": u_path,
                                "status": "untracked",
                                "additions": len(lines),
                                "deletions": 0,
                                "chunks": chunks,
                            }
                        )
                    except Exception:
                        pass

            total_additions = sum(f["additions"] for f in parsed_files)
            total_deletions = sum(f["deletions"] for f in parsed_files)

            return {
                "success": True,
                "total_files": len(parsed_files),
                "total_additions": total_additions,
                "total_deletions": total_deletions,
                "files": parsed_files,
                "raw_diff": diff_text[:100000] if len(diff_text) > 100000 else diff_text,
            }
        except Exception as exc:
            logger.warning(f"git diff failed: {exc}")
            return {"success": False, "error": str(exc), "files": []}

    def _parse_diff_output(self, diff_text: str) -> List[Dict[str, Any]]:
        """Parses git unified diff string into structured JSON objects."""
        files: List[Dict[str, Any]] = []
        if not diff_text.strip():
            return files

        raw_file_blocks = re.split(r"^diff --git ", diff_text, flags=re.MULTILINE)

        for block in raw_file_blocks:
            if not block.strip():
                continue

            lines = block.splitlines()
            header = lines[0]
            # e.g. "a/path/to/file b/path/to/file"
            paths = header.split(" ")
            b_path = paths[-1].lstrip("b/") if len(paths) >= 2 else "unknown"

            # Check status
            status = "modified"
            if "new file mode" in block:
                status = "added"
            elif "deleted file mode" in block:
                status = "deleted"
            elif "similarity index" in block:
                status = "renamed"

            chunks: List[Dict[str, Any]] = []
            current_chunk: Optional[Dict[str, Any]] = None
            old_line = 0
            new_line = 0
            additions = 0
            deletions = 0

            hunk_header_re = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")

            for line in lines[1:]:
                hunk_match = hunk_header_re.match(line)
                if hunk_match:
                    if current_chunk:
                        chunks.append(current_chunk)
                    old_start = int(hunk_match.group(1))
                    new_start = int(hunk_match.group(3))
                    old_line = old_start
                    new_line = new_start
                    current_chunk = {
                        "header": line,
                        "lines": [],
                    }
                    continue

                if current_chunk is not None:
                    if line.startswith("+") and not line.startswith("+++"):
                        additions += 1
                        current_chunk["lines"].append(
                            {
                                "type": "add",
                                "text": line[1:],
                                "old_num": None,
                                "new_num": new_line,
                            }
                        )
                        new_line += 1
                    elif line.startswith("-") and not line.startswith("---"):
                        deletions += 1
                        current_chunk["lines"].append(
                            {
                                "type": "del",
                                "text": line[1:],
                                "old_num": old_line,
                                "new_num": None,
                            }
                        )
                        old_line += 1
                    elif line.startswith(" "):
                        current_chunk["lines"].append(
                            {
                                "type": "ctx",
                                "text": line[1:],
                                "old_num": old_line,
                                "new_num": new_line,
                            }
                        )
                        old_line += 1
                        new_line += 1

            if current_chunk:
                chunks.append(current_chunk)

            files.append(
                {
                    "path": b_path,
                    "status": status,
                    "additions": additions,
                    "deletions": deletions,
                    "chunks": chunks,
                }
            )

        return files

    def revert_file(self, file_path: str) -> Dict[str, Any]:
        """Reverts uncommitted changes in a specific file."""
        if not file_path or ".." in file_path:
            return {"success": False, "error": "Ruta inválida o no permitida"}

        try:
            # Check if file is tracked
            checkout_res = subprocess.run(
                ["git", "checkout", "HEAD", "--", file_path],
                cwd=str(self.workspace_root),
                capture_output=True,
                text=True,
                timeout=5,
            )
            if checkout_res.returncode == 0:
                return {"success": True, "message": f"Archivo {file_path} restaurado a HEAD"}

            # If untracked, remove it safely
            full_path = self.workspace_root / file_path
            if full_path.exists() and full_path.is_file():
                full_path.unlink()
                return {"success": True, "message": f"Archivo no rastreado {file_path} eliminado"}

            return {"success": False, "error": checkout_res.stderr.strip()}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

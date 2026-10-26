"""
GitHub Integration Module for SACL UI (Zero-Smoke).
Direct integration with Git local CLI and GitHub CLI (gh) under identity risejoaquin.
"""

from __future__ import annotations

import json
import logging
import subprocess
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _run_cmd(cmd: List[str], cwd: Optional[str] = None) -> tuple[int, str, str]:
    """Execute a CLI command safely and return (returncode, stdout, stderr)."""
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except Exception as e:
        logger.error(f"Error running command {cmd}: {e}")
        return 1, "", str(e)


def get_github_status() -> Dict[str, Any]:
    """Return local Git and GitHub CLI connectivity and status."""
    # 1. Current Branch
    code, branch, _ = _run_cmd(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    current_branch = branch if code == 0 else "unknown"

    # 2. Remote URL
    code, remote_url, _ = _run_cmd(["git", "config", "--get", "remote.origin.url"])
    repo_name = "risejoaquin/solidbit-agent-execution-control-loop"
    if "github.com" in remote_url:
        parts = remote_url.split("github.com/")[-1].replace(".git", "")
        if parts:
            repo_name = parts

    # 3. Status Cleanliness
    code, status_out, _ = _run_cmd(["git", "status", "--porcelain"])
    is_clean = len(status_out) == 0

    # 4. Ahead / Behind
    code, count_out, _ = _run_cmd(
        ["git", "rev-list", "--left-right", "--count", f"origin/{current_branch}...HEAD"]
    )
    ahead, behind = 0, 0
    if code == 0 and "\t" in count_out:
        parts = count_out.split("\t")
        behind = int(parts[0]) if parts[0].isdigit() else 0
        ahead = int(parts[1]) if parts[1].isdigit() else 0

    # 5. GitHub CLI user
    code, gh_user, _ = _run_cmd(["gh", "api", "user", "--jq", ".login"])
    user = gh_user if code == 0 and gh_user else "risejoaquin"

    return {
        "connected": True,
        "repo": repo_name,
        "branch": current_branch,
        "remote_url": remote_url or f"https://github.com/{repo_name}",
        "user": user,
        "is_clean": is_clean,
        "ahead": ahead,
        "behind": behind,
        "status_label": "Sincronizado" if ahead == 0 and behind == 0 else f"{ahead} commits por subir",
    }


def get_pull_requests() -> List[Dict[str, Any]]:
    """Return active Pull Requests directly from GitHub via gh CLI."""
    code, stdout, _ = _run_cmd([
        "gh", "pr", "list",
        "--json", "number,title,state,isDraft,headRefName,url,updatedAt"
    ])
    if code == 0 and stdout:
        try:
            return json.loads(stdout)
        except json.JSONDecodeError:
            pass
    return []


def get_recent_commits(limit: int = 10) -> List[Dict[str, Any]]:
    """Return recent Git commits formatted for clean UI presentation."""
    code, stdout, _ = _run_cmd([
        "git", "log", f"-n{limit}", '--format=%h|%an|%ar|%s'
    ])
    commits = []
    if code == 0 and stdout:
        for line in stdout.splitlines():
            parts = line.split("|", 3)
            if len(parts) == 4:
                commits.append({
                    "sha": parts[0],
                    "author": parts[1],
                    "time": parts[2],
                    "message": parts[3],
                })
    return commits


def get_actions_runs(limit: int = 6) -> List[Dict[str, Any]]:
    """Return GitHub Actions CI/CD workflow runs."""
    code, stdout, _ = _run_cmd([
        "gh", "run", "list",
        f"--limit={limit}",
        "--json", "name,status,conclusion,headBranch,url,createdAt"
    ])
    if code == 0 and stdout:
        try:
            return json.loads(stdout)
        except json.JSONDecodeError:
            pass
    return []


def sync_origin() -> Dict[str, Any]:
    """Fetch from origin and update local tracking."""
    code, stdout, stderr = _run_cmd(["git", "fetch", "origin"])
    return {
        "success": code == 0,
        "output": stdout or stderr or "Fetch completed successfully",
    }


def create_pull_request(title: str, body: str, base: str = "main", draft: bool = True) -> Dict[str, Any]:
    """Create a new Pull Request on GitHub via gh CLI."""
    cmd = ["gh", "pr", "create", "--title", title, "--body", body, "--base", base]
    if draft:
        cmd.append("--draft")
    code, stdout, stderr = _run_cmd(cmd)
    return {
        "success": code == 0,
        "url": stdout if code == 0 else "",
        "error": stderr if code != 0 else "",
    }

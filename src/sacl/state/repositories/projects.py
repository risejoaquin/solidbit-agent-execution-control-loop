"""SACL V1 Project Repository.

Domain 2: Projects registry decoupling the core execution loop
from hardcoded repository paths (ADR-009).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from sacl.state.repositories.base import BaseRepository
from sacl.state.utils import json_dumps_safe, json_loads_safe, normalize_repo_path, utc_now


class ProjectRepository(BaseRepository):
    """Repository managing Domain 2 'projects' table."""

    def register_project(
        self,
        project_id: str,
        name: str,
        root_path: str,
        repo_url: Optional[str] = None,
        default_branch: str = "main",
        policy_override: Optional[Union[Dict[str, Any], str]] = None,
        created_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Registers or updates a target project repository in the registry."""
        now = created_at or utc_now()
        norm_root = normalize_repo_path(root_path)

        if isinstance(policy_override, dict):
            policy_json = json_dumps_safe(policy_override)
        else:
            policy_json = policy_override

        sql = """
            INSERT INTO projects (
                project_id, name, repo_url, root_path, default_branch,
                policy_override_json, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(project_id) DO UPDATE SET
                name = excluded.name,
                repo_url = excluded.repo_url,
                root_path = excluded.root_path,
                default_branch = excluded.default_branch,
                policy_override_json = excluded.policy_override_json,
                updated_at = excluded.updated_at;
        """
        self.execute(
            sql, (project_id, name, repo_url, norm_root, default_branch, policy_json, now, now)
        )
        self.commit()
        return self.get_project(project_id)  # type: ignore[return-value]

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves project record by project ID."""
        sql = "SELECT * FROM projects WHERE project_id = ?;"
        row = self.fetchone_dict(sql, (project_id,))
        if row:
            row["policy_override"] = json_loads_safe(row.get("policy_override_json"))
        return row

    def list_projects(self) -> List[Dict[str, Any]]:
        """Lists all registered projects."""
        sql = "SELECT * FROM projects ORDER BY project_id ASC;"
        rows = self.fetchall_dict(sql)
        for r in rows:
            r["policy_override"] = json_loads_safe(r.get("policy_override_json"))
        return rows

    def update_policy_override(
        self, project_id: str, policy_override: Union[Dict[str, Any], str]
    ) -> None:
        """Updates project-specific policy configuration override."""
        policy_json = (
            json_dumps_safe(policy_override)
            if isinstance(policy_override, dict)
            else policy_override
        )
        now = utc_now()
        sql = "UPDATE projects SET policy_override_json = ?, updated_at = ? WHERE project_id = ?;"
        self.execute(sql, (policy_json, now, project_id))
        self.commit()

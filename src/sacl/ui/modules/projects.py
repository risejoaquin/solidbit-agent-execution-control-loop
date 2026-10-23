"""Project Workspace Management Module for SACL UI.

Allows developers and operators to switch workspaces, inspect repository status,
and track multi-project boundaries across the SDLC.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("sacl.ui.modules.projects")


class ProjectsModule:
    """Manages active project workspaces and switching."""

    DEFAULT_PROJECTS = [
        {
            "id": "stable-ecommerce",
            "name": "Stable-Ecommerce",
            "description": "Production-grade multi-vendor platform with frozen contracts.",
            "path": r"C:\Users\Lucilfer\Documents\Stable-Ecommerce-Orchestrator",
            "tech_stack": ["Next.js", "FastAPI", "PostgreSQL", "Railway", "Supabase"],
            "status": "ACTIVE",
            "branch": "main",
            "readiness": 94,
        },
        {
            "id": "sacl-control-loop",
            "name": "SolidBit SACL Control Loop",
            "description": "Autonomous multi-agent execution loop and boundary supervisor.",
            "path": r"C:\Users\Lucilfer\Documents\solidbit-agent-execution-control-loop",
            "tech_stack": ["Python 3.11", "SQLite WAL", "Pytest", "GitHub Actions"],
            "status": "STANDBY",
            "branch": "sacl-implementation-v1",
            "readiness": 100,
        },
        {
            "id": "solidbit-blueprints",
            "name": "SolidBit Architectural Blueprints",
            "description": "Frozen data contracts, invariants specifications, and PRDs.",
            "path": r"C:\Users\Lucilfer\Desktop\SOLIDBIT",
            "tech_stack": ["Markdown", "Mermaid", "JSON Schema", "RFC"],
            "status": "STANDBY",
            "branch": "frozen",
            "readiness": 100,
        },
    ]

    def __init__(self, default_id: str = "stable-ecommerce") -> None:
        self.projects = list(self.DEFAULT_PROJECTS)
        self.active_project_id = default_id

    def list_projects(self) -> List[Dict[str, Any]]:
        """Returns all registered projects with active flag."""
        out = []
        for p in self.projects:
            item = dict(p)
            item["is_active"] = (p["id"] == self.active_project_id)
            p_path = Path(p["path"])
            item["exists_on_disk"] = p_path.exists()
            out.append(item)
        return out

    def get_active_project(self) -> Dict[str, Any]:
        """Returns current active project details."""
        for p in self.list_projects():
            if p.get("is_active"):
                return p
        return self.projects[0]

    def switch_project(self, project_id: str) -> Dict[str, Any]:
        """Switches the active project context."""
        matched = next((p for p in self.projects if p["id"] == project_id), None)
        if not matched:
            return {"success": False, "error": f"Proyecto '{project_id}' no encontrado"}
        self.active_project_id = project_id
        return {
            "success": True,
            "active_project": self.get_active_project(),
            "message": f"Espacio de trabajo cambiado a: {matched['name']}",
        }

    def add_custom_project(self, name: str, path_str: str, tech_stack: Optional[List[str]] = None) -> Dict[str, Any]:
        """Registers a new custom project workspace."""
        p_id = name.lower().replace(" ", "-")
        item = {
            "id": p_id,
            "name": name,
            "description": f"Custom project workspace at {path_str}",
            "path": path_str,
            "tech_stack": tech_stack or ["Custom"],
            "status": "STANDBY",
            "branch": "main",
            "readiness": 80,
        }
        self.projects.append(item)
        return {"success": True, "project": item}

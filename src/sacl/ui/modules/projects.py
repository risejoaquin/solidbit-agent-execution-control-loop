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

    def scan_local_projects(self, search_roots: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Scans local directories for git repositories and projects with documentation and SDLC scripts."""
        roots = [Path(r) for r in search_roots] if search_roots else [
            Path.home() / "Documents",
            Path.home() / "Desktop",
        ]
        scanned: List[Dict[str, Any]] = []

        for root in roots:
            if not root.exists():
                continue
            for item in root.iterdir():
                if not item.is_dir() or item.name.startswith(".") or "node_modules" in item.name:
                    continue
                has_git = (item / ".git").exists()
                has_pkg = (item / "package.json").exists()
                has_py = (item / "pyproject.toml").exists() or any(item.glob("*.py"))
                has_manifest = (item / "MANIFEST.json").exists()
                has_docs = (item / "docs").exists() or any(item.glob("*.md"))

                # Filter out system or non-code folders
                skip_names = {"Eden Emulador", "Obsidian Vault", "Fortinait", "POR TERMINAR", "Music", "Pictures", "Videos"}
                if item.name in skip_names:
                    continue

                if has_git or has_pkg or has_py or has_manifest or has_docs:
                    # Detect documentation files
                    docs_list = []
                    for doc_file in item.glob("*.md"):
                        docs_list.append({"name": doc_file.name, "path": str(doc_file), "type": "root_doc"})
                    if (item / "docs").exists():
                        for doc_file in (item / "docs").glob("*.md"):
                            docs_list.append({"name": f"docs/{doc_file.name}", "path": str(doc_file), "type": "arch_doc"})
                    if (item / "docs" / "architecture").exists():
                        for doc_file in (item / "docs" / "architecture").glob("*.md"):
                            docs_list.append({"name": f"architecture/{doc_file.name}", "path": str(doc_file), "type": "deep_spec"})

                    # Detect SDLC Automations (Scripts)
                    automations = []
                    for script in item.glob("*.ps1"):
                        automations.append({"name": script.name, "path": str(script), "type": "powershell_runner"})
                    for script in item.glob("*.sh"):
                        automations.append({"name": script.name, "path": str(script), "type": "bash_runner"})
                    if (item / "scripts").exists():
                        for script in (item / "scripts").glob("*.ps1"):
                            automations.append({"name": f"scripts/{script.name}", "path": str(script), "type": "powershell_runner"})
                        for script in (item / "scripts").glob("*.py"):
                            automations.append({"name": f"scripts/{script.name}", "path": str(script), "type": "python_runner"})

                    # Tech stack detection
                    tech = []
                    if (item / "package.json").exists(): tech.append("Node.js")
                    if (item / "tsconfig.json").exists(): tech.append("TypeScript")
                    if (item / "next.config.js").exists() or (item / "next.config.mjs").exists(): tech.append("Next.js")
                    if has_py: tech.append("Python")
                    if (item / "railway.json").exists() or (item / "railway.toml").exists(): tech.append("Railway")
                    if (item / "supabase").exists(): tech.append("Supabase")
                    if (item / "docker-compose.yml").exists() or (item / "Dockerfile").exists(): tech.append("Docker")
                    if not tech: tech = ["SDLC Sovereign Project"]

                    p_id = item.name.lower().replace(" ", "-")
                    scanned.append({
                        "id": p_id,
                        "name": item.name,
                        "description": f"Proyecto detectado en {item.parent.name} con {len(docs_list)} documentos y {len(automations)} scripts SDLC.",
                        "path": str(item),
                        "tech_stack": tech,
                        "status": "DETECTED",
                        "branch": "main",
                        "readiness": 90 if has_git and docs_list else 80,
                        "is_active": (p_id == self.active_project_id),
                        "exists_on_disk": True,
                        "documentation": docs_list[:8],
                        "docs_count": len(docs_list),
                        "automations": automations[:8],
                        "automations_count": len(automations),
                    })
        return scanned

    def list_projects(self) -> List[Dict[str, Any]]:
        """Returns all registered and locally scanned projects with documentation and automations."""
        scanned = self.scan_local_projects()
        scanned_ids = {p["id"] for p in scanned}
        
        # Include default blueprints if not already scanned
        out = list(scanned)
        for p in self.projects:
            if p["id"] not in scanned_ids:
                item = dict(p)
                item["is_active"] = (p["id"] == self.active_project_id)
                item["exists_on_disk"] = Path(p["path"]).exists()
                item["documentation"] = []
                item["automations"] = []
                out.append(item)

        # Ensure active project is marked
        for item in out:
            item["is_active"] = (item["id"] == self.active_project_id)

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

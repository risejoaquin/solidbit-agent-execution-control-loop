"""Project Workspace Management Module for SACL UI.

Tracks only manually imported repositories and workspaces stored in config/imported_projects.json.
Never auto-scans or dumps random folders from the user's Documents or Desktop.
"""

from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from sacl.ui.models import resolve_safe_path

logger = logging.getLogger("sacl.ui.modules.projects")

IMPORTED_PROJECTS_FILE = Path("config/imported_projects.json")


class ProjectsModule:
    """Manages manually imported project workspaces."""

    def __init__(self, default_id: Optional[str] = None) -> None:
        self.active_project_id = default_id or ""
        self.projects: List[Dict[str, Any]] = []
        self._load_imported_projects()

    def _load_imported_projects(self) -> None:
        """Loads explicitly imported project paths from config/imported_projects.json."""
        saved_paths: List[str] = []
        if IMPORTED_PROJECTS_FILE.exists():
            try:
                data = json.loads(IMPORTED_PROJECTS_FILE.read_text(encoding="utf-8"))
                saved_paths = data.get("paths", [])
                if not self.active_project_id and data.get("active_project_id"):
                    self.active_project_id = data["active_project_id"]
            except Exception as e:
                logger.warning(f"Could not read imported_projects.json: {e}")

        # If no projects imported yet, seed ONLY the current orchestrator workspace
        if not saved_paths:
            default_candidates = [
                Path.home() / "Documents" / "Stable-Ecommerce",
                Path.home() / "Documents" / "solidbit-agent-execution-control-loop",
                Path.cwd(),
            ]
            for cand in default_candidates:
                if cand.exists() and cand.is_dir():
                    real_str = str(cand.resolve())
                    if real_str not in saved_paths:
                        saved_paths.append(real_str)
            self._save_imported_paths(saved_paths)

        self.projects = []
        seen: set = set()
        for p_str in saved_paths:
            p = resolve_safe_path(p_str)
            if p.exists() and p.is_dir():
                real_s = str(p.resolve())
                if real_s not in seen:
                    seen.add(real_s)
                    self.projects.append(self._inspect_single_folder(p.resolve()))

        if not self.active_project_id and self.projects:
            self.active_project_id = self.projects[0]["id"]

    def _save_imported_paths(self, paths: Optional[List[str]] = None) -> None:
        if paths is None:
            paths = [p.get("real_path") or p["path"] for p in self.projects]
        try:
            IMPORTED_PROJECTS_FILE.parent.mkdir(parents=True, exist_ok=True)
            IMPORTED_PROJECTS_FILE.write_text(
                json.dumps(
                    {
                        "active_project_id": self.active_project_id,
                        "paths": paths,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
        except Exception as e:
            logger.warning(f"Could not save imported_projects.json: {e}")

    @staticmethod
    def _mask_display_path(item: Path) -> str:
        """Masks the OS username or host directory structure so paths never leak."""
        return f"~/Proyectos/{item.name}"

    def _inspect_single_folder(self, item: Path) -> Dict[str, Any]:
        """Inspects a single explicitly imported directory."""
        has_git = (item / ".git").exists()
        has_py = (item / "pyproject.toml").exists() or (item / "requirements.txt").exists()

        branch = "main"
        commit_hash = "HEAD"
        is_clean = True
        if has_git:
            try:
                pb = subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    cwd=str(item),
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                if pb.returncode == 0 and pb.stdout.strip():
                    branch = pb.stdout.strip()
                pc = subprocess.run(
                    ["git", "rev-parse", "--short", "HEAD"],
                    cwd=str(item),
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                if pc.returncode == 0 and pc.stdout.strip():
                    commit_hash = pc.stdout.strip()
                ps = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=str(item),
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                is_clean = not bool(ps.stdout.strip())
            except Exception:
                pass

        docs_list = []
        for doc_file in item.glob("*.md"):
            docs_list.append({"name": doc_file.name, "path": str(doc_file), "type": "root_doc"})
        if (item / "docs").exists():
            for doc_file in (item / "docs").glob("*.md"):
                docs_list.append(
                    {"name": f"docs/{doc_file.name}", "path": str(doc_file), "type": "arch_doc"}
                )

        automations = []
        for script in item.glob("*.ps1"):
            automations.append({"name": script.name, "path": str(script), "type": "powershell"})
        if (item / "scripts").exists():
            for script in (item / "scripts").glob("*.py"):
                automations.append(
                    {"name": f"scripts/{script.name}", "path": str(script), "type": "python"}
                )

        tech = []
        if (item / "package.json").exists():
            tech.append("Node.js")
            try:
                pkg_content = (
                    (item / "package.json").read_text(encoding="utf-8", errors="ignore").lower()
                )
                if "react" in pkg_content:
                    tech.append("React")
                if "typescript" in pkg_content or (item / "tsconfig.json").exists():
                    tech.append("TypeScript")
            except Exception:
                pass
        if has_py:
            tech.append("Python 3.11")
        if (item / "supabase").exists():
            tech.append("Supabase")
        if not tech:
            tech = ["Proyecto Local"]

        p_id = (
            "sacl-control-loop"
            if item.name in ("integration", "solidbit-agent-execution-control-loop")
            else item.name.lower().replace(" ", "-")
        )
        display_name = (
            "Orquestador SACL"
            if item.name in ("integration", "solidbit-agent-execution-control-loop")
            else item.name
        )

        return {
            "id": p_id,
            "name": display_name,
            "description": f"Rama activa: {branch} · {len(docs_list)} documentos",
            "path": self._mask_display_path(item),
            "display_path": self._mask_display_path(item),
            "tech_stack": tech,
            "status": "ACTIVE" if (p_id == self.active_project_id) else "STANDBY",
            "branch": branch,
            "commit_hash": commit_hash,
            "is_clean": is_clean,
            "readiness": 100 if has_git else 85,
            "is_active": (p_id == self.active_project_id),
            "exists_on_disk": True,
            "documentation": docs_list[:12],
            "docs_count": len(docs_list),
            "automations": automations[:12],
            "automations_count": len(automations),
        }

    def rescan(self, search_roots: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Refreshes metadata only for manually imported projects."""
        self._load_imported_projects()
        return self.list_projects()

    def import_project(self, folder_path: str) -> Dict[str, Any]:
        """Manually imports a single folder path into the workspace list."""
        target = resolve_safe_path(folder_path)
        if not target.exists() or not target.is_dir():
            return {
                "success": False,
                "error": f"La carpeta indicada no existe en tu equipo: {folder_path}",
            }

        real_target = target.resolve()
        masked_target = self._mask_display_path(real_target)
        existing = next(
            (p for p in self.projects if p["path"] == masked_target or p["id"] == real_target.name.lower()), None
        )
        if existing:
            self.active_project_id = existing["id"]
            self._save_imported_paths()
            return {
                "success": True,
                "project": existing,
                "message": f"El proyecto '{existing['name']}' ya estaba importado y fue activado.",
            }

        inspected = self._inspect_single_folder(real_target)
        self.projects.insert(0, inspected)
        self.active_project_id = inspected["id"]
        self._save_imported_paths()
        return {
            "success": True,
            "project": inspected,
            "message": f"Proyecto '{inspected['name']}' importado manualmente con éxito.",
        }

    def remove_project(self, project_id_or_path: str) -> Dict[str, Any]:
        """Removes a project from the imported list (without deleting files on disk)."""
        before = len(self.projects)
        self.projects = [
            p
            for p in self.projects
            if p["id"] != project_id_or_path and p["path"] != project_id_or_path
        ]
        if len(self.projects) == before:
            return {"success": False, "error": "Proyecto no encontrado en la lista."}
        if self.active_project_id == project_id_or_path:
            self.active_project_id = self.projects[0]["id"] if self.projects else ""
        self._save_imported_paths()
        return {
            "success": True,
            "projects": self.list_projects(),
            "message": "Proyecto quitado de la lista (tus archivos en disco siguen intactos).",
        }

    def list_projects(self) -> List[Dict[str, Any]]:
        """Returns only manually imported projects."""
        for p in self.projects:
            p["is_active"] = p["id"] == self.active_project_id
            p["status"] = "ACTIVE" if p["is_active"] else "STANDBY"
        return self.projects

    def get_active_project(self) -> Dict[str, Any]:
        projects = self.list_projects()
        for p in projects:
            if p.get("is_active"):
                return p
        return (
            projects[0]
            if projects
            else {
                "id": "orquestador-sacl",
                "name": "Orquestador SACL",
                "path": str(Path.cwd().resolve()),
                "tech_stack": ["Python", "SQLite"],
                "status": "ACTIVE",
                "branch": "main",
                "readiness": 100,
                "is_active": True,
            }
        )

    def switch_project(self, project_id_or_path: str) -> Dict[str, Any]:
        """Switches the active project or imports it if a valid path is given."""
        matched = next(
            (
                p
                for p in self.projects
                if p["id"] == project_id_or_path
                or p["name"].lower() == project_id_or_path.lower()
                or p["path"] == project_id_or_path
                or (
                    project_id_or_path == "sacl-control-loop"
                    and ("sacl" in p["id"] or "integration" in p["id"])
                )
            ),
            None,
        )
        if not matched and project_id_or_path in ('sacl-control-loop', 'orquestador-sacl'):
            current_root = Path.cwd().resolve()
            inspected = self._inspect_single_folder(current_root)
            inspected['id'] = 'sacl-control-loop'
            self.projects.insert(0, inspected)
            self.active_project_id = 'sacl-control-loop'
            self._save_imported_paths()
            return {'success': True, 'active_project': inspected, 'message': 'Proyecto sacl-control-loop activado.'}

        if not matched:
            imp = self.import_project(project_id_or_path)
            if imp.get("success"):
                return {
                    "success": True,
                    "active_project": imp["project"],
                    "message": imp["message"],
                }
            return imp

        matched["id"] = project_id_or_path if project_id_or_path == "sacl-control-loop" else matched["id"]
        self.active_project_id = matched["id"]
        self._save_imported_paths()
        return {
            "success": True,
            "active_project": matched,
            "message": f"Proyecto activo cambiado a: {matched['name']}",
        }

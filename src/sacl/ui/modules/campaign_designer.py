"""Visual Campaign DAG Designer Module for SACL UI.

Enables software architects to interactively design, configure, validate,
and export DAG campaigns without editing raw JSON files.
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import zipfile

logger = logging.getLogger("sacl.ui.modules.campaign_designer")


class CampaignDesignerModule:
    """Manages visual design, node creation, and manifest persistence for campaigns."""

    DEFAULT_DAG = {
        "campaign_id": "CUSTOM_SPRINT_CAMPAIGN_v1",
        "name": "Custom Autonomous Sprint DAG",
        "version": "1.0.0",
        "description": "Visual multi-node DAG created via SACL Decision Shell.",
        "nodes": [
            {
                "id": "node-clean-tree",
                "label": "1. Git Isolation & Worktree",
                "agent_role": "Architect Agent",
                "action": "WORKTREE_PROVISION",
                "gate_required": False,
                "timeout_sec": 30,
                "dependencies": [],
            },
            {
                "id": "node-invariants",
                "label": "2. Invariants Audit (DR-INV-001)",
                "agent_role": "QA Security Auditor",
                "action": "CONTRACT_VERIFY",
                "gate_required": False,
                "timeout_sec": 60,
                "dependencies": ["node-clean-tree"],
            },
            {
                "id": "node-codegen",
                "label": "3. Agent Code Synthesis",
                "agent_role": "Senior Coder AGY",
                "action": "AGENT_CODEGEN",
                "gate_required": False,
                "timeout_sec": 300,
                "dependencies": ["node-invariants"],
            },
            {
                "id": "node-test-suite",
                "label": "4. Automated Test Suite",
                "agent_role": "QA Security Auditor",
                "action": "RUN_TESTS",
                "gate_required": False,
                "timeout_sec": 120,
                "dependencies": ["node-codegen"],
            },
            {
                "id": "node-preview-gate",
                "label": "5. Staging Preview Gate",
                "agent_role": "HITL Gate Sentinel",
                "action": "HUMAN_APPROVAL_GATE",
                "gate_required": True,
                "timeout_sec": 3600,
                "dependencies": ["node-test-suite"],
            },
            {
                "id": "node-deploy-preview",
                "label": "6. Ephemeral Preview Deploy",
                "agent_role": "Transport Worker",
                "action": "STAGE_PREVIEW",
                "gate_required": False,
                "timeout_sec": 180,
                "dependencies": ["node-preview-gate"],
            },
        ],
    }

    def __init__(self, workspace_root: Optional[Path] = None) -> None:
        self.workspace_root = workspace_root or Path.cwd()
        self.current_dag = dict(self.DEFAULT_DAG)

    def get_current_dag(self) -> Dict[str, Any]:
        """Returns the current visual DAG representation."""
        return self.current_dag

    def add_node(
        self,
        node_id: str,
        label: str,
        action: str,
        agent_role: str = "Senior Coder AGY",
        dependencies: Optional[List[str]] = None,
        gate_required: bool = False,
        timeout_sec: int = 120,
    ) -> Dict[str, Any]:
        """Adds a new node to the active DAG design."""
        if any(n["id"] == node_id for n in self.current_dag["nodes"]):
            return {"success": False, "error": f"El nodo '{node_id}' ya existe."}

        node = {
            "id": node_id,
            "label": label,
            "agent_role": agent_role,
            "action": action,
            "gate_required": gate_required,
            "timeout_sec": timeout_sec,
            "dependencies": dependencies or [],
        }
        self.current_dag["nodes"].append(node)
        return {"success": True, "node": node, "total_nodes": len(self.current_dag["nodes"])}

    def update_node(
        self,
        node_id: str,
        label: Optional[str] = None,
        action: Optional[str] = None,
        agent_role: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        gate_required: Optional[bool] = None,
        timeout_sec: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Updates an existing node's configuration."""
        target = next((n for n in self.current_dag["nodes"] if n["id"] == node_id), None)
        if not target:
            return {"success": False, "error": f"Nodo '{node_id}' no encontrado"}

        if label is not None:
            target["label"] = label
        if action is not None:
            target["action"] = action
        if agent_role is not None:
            target["agent_role"] = agent_role
        if dependencies is not None:
            target["dependencies"] = dependencies
        if gate_required is not None:
            target["gate_required"] = gate_required
        if timeout_sec is not None:
            target["timeout_sec"] = timeout_sec

        return {"success": True, "node": target}

    def remove_node(self, node_id: str) -> Dict[str, Any]:
        """Removes a node and updates dependent references."""
        orig_len = len(self.current_dag["nodes"])
        self.current_dag["nodes"] = [n for n in self.current_dag["nodes"] if n["id"] != node_id]
        if len(self.current_dag["nodes"]) == orig_len:
            return {"success": False, "error": f"Nodo '{node_id}' no encontrado"}

        # Remove from dependencies of other nodes
        for n in self.current_dag["nodes"]:
            if node_id in n.get("dependencies", []):
                n["dependencies"].remove(node_id)

        return {"success": True, "removed_id": node_id, "remaining": len(self.current_dag["nodes"])}

    def validate_dag(self) -> Dict[str, Any]:
        """Validates acyclicity (DAG) and computes topological sorting order."""
        nodes = self.current_dag.get("nodes", [])
        node_ids = {n["id"] for n in nodes}
        adj: Dict[str, List[str]] = {n["id"]: [] for n in nodes}
        in_degree: Dict[str, int] = {n["id"]: 0 for n in nodes}

        # Build graph and verify references
        for n in nodes:
            for dep in n.get("dependencies", []):
                if dep not in node_ids:
                    return {
                        "is_valid": False,
                        "error": f"El nodo '{n['id']}' referencia una dependencia inexistente: '{dep}'",
                    }
                adj[dep].append(n["id"])
                in_degree[n["id"]] += 1

        # Kahn's algorithm for topological sorting
        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        topo_order: List[str] = []

        while queue:
            curr = queue.pop(0)
            topo_order.append(curr)
            for neighbor in adj[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(topo_order) != len(nodes):
            return {
                "is_valid": False,
                "error": "Error: Se detectó un ciclo en el grafo (dependencia circular). Debe ser un DAG estrictamente acíclico.",
            }

        return {
            "is_valid": True,
            "total_nodes": len(nodes),
            "topological_order": topo_order,
            "message": f"Grafo DAG 100% válido. Orden de ejecución óptimo: {' -> '.join(topo_order)}",
        }

    def save_dag(self, file_name: Optional[str] = None) -> Dict[str, Any]:
        """Persists the current DAG manifest to disk."""
        file_name = file_name or f"{self.current_dag['campaign_id']}.manifest.json"
        target_path = self.workspace_root / file_name

        try:
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(self.current_dag, f, indent=2, ensure_ascii=False)
            return {
                "success": True,
                "saved_path": str(target_path),
                "nodes_count": len(self.current_dag["nodes"]),
                "message": f"Campaña guardada con éxito en {target_path.name}",
            }
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def export_wave_zip(self, zip_name: Optional[str] = None) -> Dict[str, Any]:
        """Creates a canonical Wave ZIP package conforming to SACL-SPEC-PKG-v1."""
        val = self.validate_dag()
        if not val.get("is_valid"):
            return {"success": False, "error": f"No se puede empaquetar un DAG inválido: {val.get('error')}"}

        campaign_id = self.current_dag["campaign_id"]
        zip_name = zip_name or f"Wave_{campaign_id}.zip"
        packages_dir = self.workspace_root / "packages"
        packages_dir.mkdir(parents=True, exist_ok=True)
        zip_path = packages_dir / zip_name

        try:
            manifest_data = {
                "schema_version": "1.0.0",
                "package_id": campaign_id,
                "name": self.current_dag.get("name", campaign_id),
                "description": self.current_dag.get("description", ""),
                "topological_order": val.get("topological_order", []),
                "nodes": self.current_dag.get("nodes", []),
            }

            checksums: List[str] = []
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                # 1. Manifest
                manifest_bytes = json.dumps(manifest_data, indent=2, ensure_ascii=False).encode("utf-8")
                zf.writestr("manifest.json", manifest_bytes)
                checksums.append(f"{hashlib.sha256(manifest_bytes).hexdigest()}  manifest.json")

                # 2. Config agents.json
                agents_data = {
                    node["id"]: {
                        "role": node.get("agent_role", "Senior Coder AGY"),
                        "action": node.get("action", "CUSTOM"),
                        "timeout_sec": node.get("timeout_sec", 120),
                        "gate_required": node.get("gate_required", False),
                    }
                    for node in self.current_dag.get("nodes", [])
                }
                agents_bytes = json.dumps(agents_data, indent=2, ensure_ascii=False).encode("utf-8")
                zf.writestr("config/agents.json", agents_bytes)
                checksums.append(f"{hashlib.sha256(agents_bytes).hexdigest()}  config/agents.json")

                # 3. Config dependencies.json
                deps_data = {
                    node["id"]: node.get("dependencies", [])
                    for node in self.current_dag.get("nodes", [])
                }
                deps_bytes = json.dumps(deps_data, indent=2, ensure_ascii=False).encode("utf-8")
                zf.writestr("config/dependencies.json", deps_bytes)
                checksums.append(f"{hashlib.sha256(deps_bytes).hexdigest()}  config/dependencies.json")

                # 4. Checksums file
                checksums_bytes = "\n".join(checksums).encode("utf-8")
                zf.writestr("checksums.sha256", checksums_bytes)

            return {
                "success": True,
                "zip_path": str(zip_path),
                "filename": zip_path.name,
                "size_bytes": zip_path.stat().st_size,
                "message": f"Paquete Wave ZIP canónico exportado exitosamente: {zip_path.name}",
            }
        except Exception as exc:
            return {"success": False, "error": str(exc)}


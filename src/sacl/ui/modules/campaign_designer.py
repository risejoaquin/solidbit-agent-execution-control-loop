"""Visual Campaign DAG Designer Module for SACL UI.

Enables software architects to interactively design, configure, validate,
and export DAG campaigns without editing raw JSON files.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

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
                "action": "WORKTREE_PROVISION",
                "gate_required": False,
                "timeout_sec": 30,
                "dependencies": [],
            },
            {
                "id": "node-invariants",
                "label": "2. Invariants Audit (DR-INV-001)",
                "action": "CONTRACT_VERIFY",
                "gate_required": False,
                "timeout_sec": 60,
                "dependencies": ["node-clean-tree"],
            },
            {
                "id": "node-codegen",
                "label": "3. Agent Code Synthesis",
                "action": "AGENT_CODEGEN",
                "gate_required": False,
                "timeout_sec": 300,
                "dependencies": ["node-invariants"],
            },
            {
                "id": "node-test-suite",
                "label": "4. Automated Test Suite",
                "action": "RUN_TESTS",
                "gate_required": False,
                "timeout_sec": 120,
                "dependencies": ["node-codegen"],
            },
            {
                "id": "node-preview-gate",
                "label": "5. Staging Preview Gate",
                "action": "HUMAN_APPROVAL_GATE",
                "gate_required": True,
                "timeout_sec": 3600,
                "dependencies": ["node-test-suite"],
            },
            {
                "id": "node-deploy-preview",
                "label": "6. Ephemeral Preview Deploy",
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
            "action": action,
            "gate_required": gate_required,
            "timeout_sec": timeout_sec,
            "dependencies": dependencies or [],
        }
        self.current_dag["nodes"].append(node)
        return {"success": True, "node": node, "total_nodes": len(self.current_dag["nodes"])}

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

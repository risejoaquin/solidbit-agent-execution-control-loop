"""SACL V1 Legacy Package Compatibility Adapter.

Adapts proven wave packages (e.g. SOLIDBIT_CCP46_WAVE_B_LOCAL_GOVERNANCE_v1,
SACL_W0_ARCHITECTURE_FREEZE_RUNNABLE_v1) to the SACL V1 declarative contract
while preserving 100% backward compatibility for operator scripts and prompts.
"""

from __future__ import annotations

import json
import logging
import re
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from sacl.contracts.models import ExecutionGraph, GraphNode, GraphPhase, Manifest
from sacl.contracts.schema_validator import SchemaValidator, get_default_validator
from sacl.legacy.compatibility import generate_governance_header

logger = logging.getLogger("sacl.legacy.adapter")

DEFAULT_PROHIBITED_ACTIONS = [
    "merge",
    "production_deploy",
    "direct_main_push",
    "production_db_mutation",
    "secret_export",
    "arbitrary_script_execution",
]

DEFAULT_EXPECTED_OUTPUTS = [
    "SUMMARY.md",
    "SUMMARY.json",
    "reports/FINAL_REPORT.md",
    "reports/*.REPORT.md",
    "state/*.json",
    "logs/*",
]

DEFAULT_RUNTIME_FILES = [
    "RUN-WAVE.ps1",
    "WORKER.ps1",
    "MONITOR.ps1",
    "FINALIZE.ps1",
]

DEFAULT_REQUESTED_OPERATIONS = [
    "op:worker-governed-execution",
    "op:preflight-check",
]


class LegacyPackageAdapter:
    """Adapts legacy wave packages and manifests to canonical SACL V1 structures."""

    def __init__(self, validator: Optional[SchemaValidator] = None) -> None:
        self.validator = validator or get_default_validator()

    def load_manifest(self, package_dir: Union[Path, str]) -> Manifest:
        """Loads and normalizes manifest.json from a wave package directory.

        Validates against schemas/manifest.schema.json after adaptation.
        """
        pkg_path = Path(package_dir)
        if pkg_path.is_file() and pkg_path.suffix.lower() == ".json":
            manifest_file = pkg_path
            pkg_path = pkg_path.parent
        else:
            manifest_file = pkg_path / "manifest.json"

        if not manifest_file.exists():
            raise FileNotFoundError(f"Package manifest not found: {manifest_file}")

        with open(manifest_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        normalized_data = self.normalize_manifest_dict(raw_data, package_dir=pkg_path)
        # Validate against canonical manifest.schema.json
        self.validator.validate_manifest(normalized_data)
        return Manifest.from_dict(normalized_data)

    def normalize_manifest_dict(
        self,
        raw_data: Dict[str, Any],
        package_dir: Optional[Path] = None,
        job_id_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Normalizes a raw or legacy manifest dictionary to solidbit.execution-package.v1.

        Fills required fields from existing legacy directory contents or safe defaults.
        """
        data = dict(raw_data)

        # 1. Schema version
        data["schema"] = "solidbit.execution-package.v1"

        # 2. Package ID
        pkg_id = data.get("package_id") or (package_dir.name if package_dir else "LEGACY-WAVE-v1")
        # Sanitize package_id for schema regex ^[A-Za-z0-9_-]+$
        clean_pkg_id = re.sub(r"[^A-Za-z0-9_-]", "-", pkg_id)
        data["package_id"] = clean_pkg_id

        # 3. Job ID (Mandatory in V1 per SB-FREEZE-P2-01)
        if job_id_override:
            data["job_id"] = job_id_override
        elif "job_id" not in data or not data["job_id"]:
            # Synthesize deterministic/clean job ID from package_id
            rand_suffix = uuid.uuid4().hex[:6]
            data["job_id"] = f"job-{clean_pkg_id}-{rand_suffix}"

        # 4. Project and repository
        if "project" not in data or not data["project"]:
            data["project"] = "solidbit-agent-execution-control-loop"
        if "repository" not in data or not data["repository"]:
            data["repository"] = "risejoaquin/solidbit-agent-execution-control-loop"

        # 5. Execution mode
        valid_modes = {
            "architecture_freeze_and_repo_bootstrap",
            "governed_documentation_generation",
            "isolated_branch_development",
            "integration_and_audit",
            "certification_test",
        }
        mode = data.get("mode")
        if not mode or mode not in valid_modes:
            data["mode"] = "isolated_branch_development"

        # 6. Source orchestrator and target local repo
        if "source_orchestrator" not in data or not data["source_orchestrator"]:
            data["source_orchestrator"] = (
                r"C:\Users\Lucilfer\Documents\Stable-Ecommerce-Orchestrator"
            )
        if "target_local_repo" not in data or not data["target_local_repo"]:
            data["target_local_repo"] = (
                r"C:\Users\Lucilfer\Documents\solidbit-agent-execution-control-loop"
            )

        # 7. Agents list
        agents = data.get("agents", [])
        if not agents and package_dir:
            # Try to discover prompts
            prompts_dir = package_dir / "prompts"
            if prompts_dir.exists():
                agents = [p.stem for p in prompts_dir.glob("*.md")]
        if not agents:
            agents = ["AG-MAIN"]
        # Ensure all agents are strings matching regex ^[A-Za-z0-9_-]+$
        clean_agents = []
        for a in agents:
            if isinstance(a, dict):
                a_name = a.get("agent_id") or a.get("name") or "AG-WORKER"
            else:
                a_name = str(a)
            clean_agents.append(re.sub(r"[^A-Za-z0-9_-]", "-", a_name))
        data["agents"] = list(dict.fromkeys(clean_agents))  # unique preserving order

        # 8. Entrypoint, Execution Plan, Readme
        data["entrypoint"] = data.get("entrypoint") or "RUN-WAVE.ps1"
        exec_plan = data.get("execution_plan")
        if isinstance(exec_plan, dict) or not exec_plan:
            data["execution_plan"] = "EXECUTION_PLAN.md"
        else:
            data["execution_plan"] = str(exec_plan)
        data["readme"] = data.get("readme") or "README.md"

        # 9. Requested operations (Mandatory in V1, prevents self-authorizing scripts)
        req_ops = data.get("requested_operations")
        if not req_ops:
            req_ops = list(DEFAULT_REQUESTED_OPERATIONS)
        data["requested_operations"] = req_ops

        # 10. Prohibited actions
        proh = data.get("prohibited_actions")
        if not proh:
            proh = list(DEFAULT_PROHIBITED_ACTIONS)
        data["prohibited_actions"] = proh

        # 11. Expected outputs
        exp = data.get("expected_outputs")
        if not exp:
            exp = list(DEFAULT_EXPECTED_OUTPUTS)
        data["expected_outputs"] = exp

        # 12. Runtime files
        rt = data.get("runtime_files")
        if not rt:
            rt = list(DEFAULT_RUNTIME_FILES)
        data["runtime_files"] = rt

        return data

    def build_execution_graph(
        self,
        package_dir: Union[Path, str],
        manifest: Optional[Manifest] = None,
        max_parallel: int = 4,
    ) -> ExecutionGraph:
        """Constructs an ExecutionGraph from package config or sequential phases."""
        pkg_path = Path(package_dir)
        if manifest is None:
            manifest = self.load_manifest(pkg_path)

        dep_file = pkg_path / "config" / "dependencies.json"
        if dep_file.exists():
            try:
                with open(dep_file, "r", encoding="utf-8") as f:
                    dep_data = json.load(f)
                return self._parse_dependencies_json(dep_data, manifest, max_parallel)
            except Exception as exc:
                logger.warning(
                    "Failed to parse config/dependencies.json: %s. Falling back to phases.", exc
                )

        # Fallback: create phases from agents list
        phases: List[GraphPhase] = []
        nodes: List[GraphNode] = []
        edges: List[List[str]] = []
        prev_agent = None

        for idx, agent_id in enumerate(manifest.agents, start=1):
            node = GraphNode(
                node_id=agent_id,
                agent_id=agent_id,
                phase_number=idx,
                timeout_minutes=30,
            )
            nodes.append(node)
            phase = GraphPhase(
                phase_number=idx,
                stage_name=f"Phase {idx} ({agent_id})",
                agents=[agent_id],
            )
            phases.append(phase)
            if prev_agent:
                edges.append([prev_agent, agent_id])
            prev_agent = agent_id

        return ExecutionGraph(
            graph_id=f"graph-{manifest.package_id}",
            job_id=manifest.job_id,
            max_parallel=max_parallel,
            default_timeout_minutes=30,
            phases=phases,
            edges=edges,
            nodes=nodes,
            failure_policy="abort_immediately",
        )

    def _parse_dependencies_json(
        self,
        dep_data: Dict[str, Any],
        manifest: Manifest,
        max_parallel: int,
    ) -> ExecutionGraph:
        """Parses legacy dependencies.json into an ExecutionGraph."""
        phases_list: List[GraphPhase] = []
        nodes_list: List[GraphNode] = []
        edges_list: List[List[str]] = []
        raw_phases = dep_data.get("phases", [])

        if raw_phases:
            for idx, p_info in enumerate(raw_phases, start=1):
                p_name = p_info.get("name", f"Phase {idx}")
                phase_agents: List[str] = []
                for n_info in p_info.get("nodes", []):
                    node_id = n_info.get("node_id") or n_info.get("agent_id")
                    timeout = n_info.get("timeout_minutes", 30)
                    phase_agents.append(node_id)
                    nodes_list.append(
                        GraphNode(
                            node_id=node_id,
                            agent_id=node_id,
                            phase_number=idx,
                            timeout_minutes=timeout,
                        )
                    )
                    for dep in n_info.get("dependencies", []):
                        edges_list.append([dep, node_id])

                phases_list.append(
                    GraphPhase(
                        phase_number=idx,
                        stage_name=p_name,
                        agents=phase_agents,
                    )
                )
        else:
            # Fallback flat nodes with stage/phase
            phase_map: Dict[str, List[str]] = {}
            for agent_id, info in dep_data.get("agents", {}).items():
                p_id = info.get("phase", "Phase-1")
                phase_map.setdefault(p_id, []).append(agent_id)
                for dep in info.get("depends_on", []):
                    edges_list.append([dep, agent_id])

            for idx, (p_id, ag_list) in enumerate(phase_map.items(), start=1):
                phases_list.append(
                    GraphPhase(
                        phase_number=idx,
                        stage_name=p_id,
                        agents=ag_list,
                    )
                )
                for a_id in ag_list:
                    nodes_list.append(
                        GraphNode(
                            node_id=a_id,
                            agent_id=a_id,
                            phase_number=idx,
                            timeout_minutes=30,
                        )
                    )

        return ExecutionGraph(
            graph_id=f"graph-{manifest.package_id}",
            job_id=manifest.job_id,
            max_parallel=dep_data.get("max_parallel", max_parallel),
            default_timeout_minutes=30,
            phases=phases_list,
            edges=edges_list,
            nodes=nodes_list,
            failure_policy=dep_data.get("failure_policy", "abort_immediately"),
        )

    def render_prompt(
        self,
        prompt_template_path: Union[Path, str],
        package_root: Union[Path, str],
        run_dir: Union[Path, str],
        report_path: Union[Path, str],
        source_orchestrator: Union[Path, str],
        decision_baseline: Optional[Union[Path, str]] = None,
        worktree_path: Optional[Union[Path, str]] = None,
        branch: str = "worktree-branch",
        head_sha: str = "UNKNOWN",
        inject_governance_guard: bool = True,
        extra_replacements: Optional[Dict[str, str]] = None,
    ) -> str:
        """Renders an agent prompt with legacy variable substitution and governance headers."""
        p_path = Path(prompt_template_path)
        if not p_path.exists():
            raise FileNotFoundError(f"Prompt template not found: {p_path}")

        with open(p_path, "r", encoding="utf-8") as f:
            content = f.read()

        pkg_root_str = str(Path(package_root).resolve())
        run_dir_str = str(Path(run_dir).resolve())
        report_path_str = str(Path(report_path).resolve())
        src_orch_str = str(Path(source_orchestrator).resolve())
        decision_str = (
            str(Path(decision_baseline).resolve())
            if decision_baseline
            else str(Path(package_root) / "inputs" / "DECISION_BASELINE.md")
        )

        # Proven legacy placeholder replacements
        content = content.replace("{{PACKAGE_ROOT}}", pkg_root_str)
        content = content.replace("{{RUN_DIR}}", run_dir_str)
        content = content.replace("{{REPORT}}", report_path_str)
        content = content.replace("{{SOURCE_ORCHESTRATOR}}", src_orch_str)
        content = content.replace("{{DECISION_BASELINE}}", decision_str)

        if extra_replacements:
            for k, v in extra_replacements.items():
                content = content.replace(f"{{{{{k}}}}}", str(v))

        # Inject Machine Governance Guard header (Invoke-AntigravityGoverned.ps1)
        if inject_governance_guard:
            wt_path = worktree_path or pkg_root_str
            header = generate_governance_header(
                worktree_path=wt_path,
                branch=branch,
                head_sha=head_sha,
                governed_execution=True,
                merge_authorized=False,
                deploy_authorized=False,
                destructive_db_authorized=False,
            )
            content = header + content

        return content

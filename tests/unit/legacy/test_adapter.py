"""Unit tests for SACL V1 Legacy Package Adapter."""

from __future__ import annotations

import json

import pytest

from sacl.legacy.adapter import LegacyPackageAdapter


@pytest.fixture
def adapter():
    return LegacyPackageAdapter()


def test_normalize_manifest_legacy_fields(adapter, tmp_path):
    legacy_manifest = {
        "schema": "solidbit.execution-package.v1",
        "package_id": "SACL_W0_ARCHITECTURE_FREEZE_RUNNABLE_v1",
        "project": "solidbit-agent-execution-control-loop",
        "repository": "risejoaquin/solidbit-agent-execution-control-loop",
        "mode": "architecture_freeze_and_repo_bootstrap",
        "source_orchestrator": "C:\\Users\\Lucilfer\\Documents\\Stable-Ecommerce-Orchestrator",
        "target_local_repo": "C:\\Users\\Lucilfer\\Documents\\solidbit-agent-execution-control-loop",
        "agents": ["AG-COMPAT", "AG-ARCH"],
        "entrypoint": "RUN-WAVE.ps1",
        "prohibited_actions": ["merge", "production_deploy"],
        "expected_outputs": ["SUMMARY.md", "SUMMARY.json"],
        "runtime_files": ["RUN-WAVE.ps1", "WORKER.ps1"],
    }

    norm = adapter.normalize_manifest_dict(legacy_manifest, package_dir=tmp_path)
    # job_id should be synthesized
    assert "job_id" in norm
    assert norm["job_id"].startswith("job-SACL_W0_ARCHITECTURE_FREEZE_RUNNABLE_v1")
    # requested_operations should be populated
    assert "requested_operations" in norm
    assert len(norm["requested_operations"]) >= 1
    # execution_plan & readme should be present
    assert norm["execution_plan"] == "EXECUTION_PLAN.md"
    assert norm["readme"] == "README.md"


def test_load_manifest_validates_schema(adapter, tmp_path):
    manifest_data = {
        "schema": "solidbit.execution-package.v1",
        "package_id": "TEST-PACKAGE-v1",
        "job_id": "job-test-123",
        "project": "solidbit-agent-execution-control-loop",
        "repository": "risejoaquin/solidbit-agent-execution-control-loop",
        "mode": "isolated_branch_development",
        "source_orchestrator": "C:\\source",
        "target_local_repo": "C:\\target",
        "agents": ["AG-1"],
        "entrypoint": "RUN-WAVE.ps1",
        "execution_plan": "EXECUTION_PLAN.md",
        "readme": "README.md",
        "requested_operations": ["op:worker-governed-execution"],
        "prohibited_actions": ["merge"],
        "expected_outputs": ["SUMMARY.md", "SUMMARY.json"],
        "runtime_files": ["RUN-WAVE.ps1"],
    }

    mf_path = tmp_path / "manifest.json"
    with open(mf_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f)

    loaded = adapter.load_manifest(tmp_path)
    assert loaded.package_id == "TEST-PACKAGE-v1"
    assert loaded.job_id == "job-test-123"
    assert loaded.agents == ["AG-1"]


def test_build_execution_graph_fallback(adapter, tmp_path):
    manifest_data = {
        "schema": "solidbit.execution-package.v1",
        "package_id": "TEST-PACKAGE-v1",
        "job_id": "job-test-123",
        "project": "solidbit-agent-execution-control-loop",
        "repository": "risejoaquin/solidbit-agent-execution-control-loop",
        "mode": "isolated_branch_development",
        "source_orchestrator": "C:\\source",
        "target_local_repo": "C:\\target",
        "agents": ["AG-1", "AG-2"],
        "entrypoint": "RUN-WAVE.ps1",
        "execution_plan": "EXECUTION_PLAN.md",
        "readme": "README.md",
        "requested_operations": ["op:worker-governed-execution"],
        "prohibited_actions": ["merge"],
        "expected_outputs": ["SUMMARY.md", "SUMMARY.json"],
        "runtime_files": ["RUN-WAVE.ps1"],
    }
    with open(tmp_path / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest_data, f)

    graph = adapter.build_execution_graph(tmp_path)
    assert graph.graph_id == "graph-TEST-PACKAGE-v1"
    assert len(graph.phases) == 2
    assert graph.phases[0].agents == ["AG-1"]
    assert graph.phases[1].agents == ["AG-2"]
    assert graph.nodes[0].agent_id == "AG-1"
    assert graph.nodes[1].agent_id == "AG-2"


def test_build_execution_graph_from_dependencies_json(adapter, tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir(parents=True)
    dep_data = {
        "max_parallel": 3,
        "phases": [
            {
                "phase_id": "P1",
                "name": "Phase 1",
                "nodes": [{"node_id": "AG-A", "dependencies": [], "timeout_minutes": 20}],
            },
            {
                "phase_id": "P2",
                "name": "Phase 2",
                "nodes": [{"node_id": "AG-B", "dependencies": ["AG-A"]}],
            },
        ],
    }
    with open(config_dir / "dependencies.json", "w", encoding="utf-8") as f:
        json.dump(dep_data, f)

    manifest_data = {
        "schema": "solidbit.execution-package.v1",
        "package_id": "TEST-PKG",
        "job_id": "job-1",
        "project": "proj",
        "repository": "org/repo",
        "mode": "isolated_branch_development",
        "source_orchestrator": "C:\\src",
        "target_local_repo": "C:\\tgt",
        "agents": ["AG-A", "AG-B"],
        "entrypoint": "RUN-WAVE.ps1",
        "execution_plan": "EXECUTION_PLAN.md",
        "readme": "README.md",
        "requested_operations": ["op:test"],
        "prohibited_actions": ["merge"],
        "expected_outputs": ["SUMMARY.md", "SUMMARY.json"],
        "runtime_files": ["RUN-WAVE.ps1"],
    }
    with open(tmp_path / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest_data, f)

    graph = adapter.build_execution_graph(tmp_path)
    assert len(graph.phases) == 2
    assert graph.max_parallel == 3
    assert graph.nodes[0].node_id == "AG-A"
    assert graph.edges == [["AG-A", "AG-B"]]


def test_render_prompt(adapter, tmp_path):
    prompt_file = tmp_path / "test.md"
    prompt_file.write_text(
        "Hello {{PACKAGE_ROOT}} in {{RUN_DIR}} with {{REPORT}}", encoding="utf-8"
    )

    rendered = adapter.render_prompt(
        prompt_template_path=prompt_file,
        package_root="C:/pkg",
        run_dir="C:/run",
        report_path="C:/rep.md",
        source_orchestrator="C:/src",
        inject_governance_guard=True,
    )
    assert "GOVERNED_EXECUTION=TRUE" in rendered
    assert "C:\\pkg" in rendered or "C:/pkg" in rendered
    assert "C:\\run" in rendered or "C:/run" in rendered
    assert "C:\\rep.md" in rendered or "C:/rep.md" in rendered

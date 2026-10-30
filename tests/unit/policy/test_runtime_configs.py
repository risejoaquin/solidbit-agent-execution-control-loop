"""Tests for Runtime Configuration Files (config/runtime/*.json).

Validates that all local runtime configuration files strictly conform to
canonical schemas in schemas/*.schema.json and load cleanly with their managers.
"""

import json
from pathlib import Path

import pytest

from sacl.contracts.schema_validator import SchemaValidator
from sacl.policy.hard_policy import HardPolicyEngine
from sacl.policy.operation_registry import OperationRegistryManager
from sacl.policy.project_registry import ProjectRegistryManager


@pytest.fixture
def runtime_dir():
    current = Path(__file__).resolve()
    for parent in [
        current.parent,
        current.parents[1],
        current.parents[2],
        current.parents[3],
        Path.cwd(),
    ]:
        candidate = parent / "config" / "runtime"
        if candidate.exists() and (candidate / "hard-policy.json").exists():
            return candidate
    raise FileNotFoundError("Could not find config/runtime directory.")


def test_hard_policy_config_validates_and_loads(runtime_dir):
    config_file = runtime_dir / "hard-policy.json"
    assert config_file.exists()

    with open(config_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    validator = SchemaValidator()
    validator.validate_hard_policy(data)

    engine = HardPolicyEngine.from_file(config_file)
    assert engine.get_hard_local_policy().hard_deny_always_wins is True
    assert engine.get_hard_local_policy().approval_override_allowed is False


def test_project_registry_config_validates_and_loads(runtime_dir):
    config_file = runtime_dir / "projects.json"
    assert config_file.exists()

    with open(config_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    validator = SchemaValidator()
    validator.validate_project_registry(data)

    manager = ProjectRegistryManager.from_file(config_file)
    projects = manager.list_projects()
    assert len(projects) >= 2

    # Verify solidbit core project
    sb = manager.get_project("solidbit-agent-execution-control-loop")
    assert sb is not None
    assert sb.concurrency_policy.max_mutating_jobs == 1
    assert sb.enforce_dirty_root_check is True

    # Verify stable-ecommerce project
    se = manager.get_project("stable-ecommerce")
    assert se is not None
    assert se.risk_tier == "POST_GATE"


def test_operation_registry_config_validates_and_loads(runtime_dir):
    config_file = runtime_dir / "operations.json"
    assert config_file.exists()

    with open(config_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    validator = SchemaValidator()
    validator.validate_operation_registry(data)

    manager = OperationRegistryManager.from_file(config_file)
    ops = manager.list_operations()
    assert len(ops) >= 5

    preflight = manager.get_operation("op:preflight-check")
    assert preflight is not None
    assert preflight.enabled is True

    worker = manager.get_operation("op:worker-governed-execution")
    assert worker is not None
    assert worker.execution_profile.isolation == "worktree"


def test_default_policy_config_validates(runtime_dir):
    config_file = runtime_dir / "default-policy.json"
    assert config_file.exists()

    with open(config_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    validator = SchemaValidator()
    validator.validate_policy(data)

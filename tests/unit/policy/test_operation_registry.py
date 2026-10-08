"""Tests for Local Operation Registry Manager (src/sacl/policy/operation_registry.py).

Constitutional Invariants (ADR-006):
Packages cannot self-authorize attached code.
Autoexecution is restricted exclusively to trusted handlers in the Local Operation Registry.
Handler integrity is verified via cryptographic SHA-256 digests.
"""

import hashlib
from pathlib import Path
import pytest

from sacl.contracts.exceptions import PolicyDeniedError
from sacl.contracts.models import OperationRegistry
from sacl.policy.operation_registry import (
    OperationRegistryManager,
    normalize_image_name,
)


@pytest.fixture
def temp_operation_env(tmp_path):
    # Create handler scripts and calculate their SHA-256 digests
    handler1 = tmp_path / "handler1.ps1"
    handler1.write_text("Write-Output 'Hello from preflight'", encoding="utf-8")
    sha1 = hashlib.sha256(handler1.read_bytes()).hexdigest()

    handler2 = tmp_path / "handler2.ps1"
    handler2.write_text("Write-Output 'Hello from worker'", encoding="utf-8")
    sha2 = hashlib.sha256(handler2.read_bytes()).hexdigest()

    registry_dict = {
        "schema": "solidbit.operation-registry.v1",
        "registry_id": "test-operation-registry",
        "version": "1.0.0",
        "operations": [
            {
                "operation_id": "op:test-preflight",
                "name": "Test Preflight Check",
                "handler_path": str(handler1),
                "handler_type": "powershell",
                "handler_sha256": sha1,
                "execution_profile": {
                    "timeout_seconds": 60,
                    "max_memory_mb": 256,
                    "isolation": "readonly",
                    "allow_network": False,
                    "allowed_process_images": ["powershell", "pwsh"],
                },
                "required_permissions": ["source_orchestrator_read"],
                "enabled": True,
            },
            {
                "operation_id": "op:test-worker",
                "name": "Test Worker Execution",
                "handler_path": str(handler2),
                "handler_type": "powershell",
                "handler_sha256": sha2,
                "execution_profile": {
                    "timeout_seconds": 600,
                    "max_memory_mb": 1024,
                    "isolation": "worktree",
                    "allow_network": True,
                    "allowed_process_images": ["agy", "powershell", "node"],
                },
                "required_permissions": ["target_docs_write"],
                "enabled": True,
            },
            {
                "operation_id": "op:disabled-op",
                "name": "Disabled Operation",
                "handler_path": str(handler1),
                "handler_type": "powershell",
                "handler_sha256": sha1,
                "execution_profile": {
                    "timeout_seconds": 10,
                    "isolation": "readonly",
                    "allow_network": False,
                },
                "required_permissions": [],
                "enabled": False,
            },
        ],
    }

    return {
        "registry_dict": registry_dict,
        "handler1": handler1,
        "handler2": handler2,
        "sha1": sha1,
        "sha2": sha2,
        "base_dir": tmp_path,
    }


def test_resolve_registered_operation(temp_operation_env):
    manager = OperationRegistryManager.from_dict(
        temp_operation_env["registry_dict"],
        base_dir=temp_operation_env["base_dir"],
    )

    op = manager.resolve_operation("op:test-preflight")
    assert op.name == "Test Preflight Check"
    assert op.execution_profile.timeout_seconds == 60
    assert op.execution_profile.allow_network is False
    assert manager.get_required_permissions("op:test-preflight") == ["source_orchestrator_read"]


def test_unregistered_operation_rejected_fail_closed(temp_operation_env):
    manager = OperationRegistryManager.from_dict(
        temp_operation_env["registry_dict"],
        base_dir=temp_operation_env["base_dir"],
    )

    with pytest.raises(PolicyDeniedError) as excinfo:
        manager.resolve_operation("op:untrusted-package-script")
    assert "Unknown Operation Invariant Violation" in excinfo.value.message


def test_disabled_operation_rejected(temp_operation_env):
    manager = OperationRegistryManager.from_dict(
        temp_operation_env["registry_dict"],
        base_dir=temp_operation_env["base_dir"],
    )

    with pytest.raises(PolicyDeniedError) as excinfo:
        manager.resolve_operation("op:disabled-op")
    assert "disabled" in excinfo.value.message


def test_handler_cryptographic_integrity_success(temp_operation_env):
    manager = OperationRegistryManager.from_dict(
        temp_operation_env["registry_dict"],
        base_dir=temp_operation_env["base_dir"],
    )

    assert manager.verify_handler_integrity("op:test-preflight") is True
    assert manager.verify_handler_integrity("op:test-worker") is True


def test_handler_tamper_digest_mismatch_fails_closed(temp_operation_env):
    manager = OperationRegistryManager.from_dict(
        temp_operation_env["registry_dict"],
        base_dir=temp_operation_env["base_dir"],
    )

    # Tamper with handler file content
    temp_operation_env["handler1"].write_text("MALICIOUS INJECTED CODE", encoding="utf-8")

    with pytest.raises(PolicyDeniedError) as excinfo:
        manager.verify_handler_integrity("op:test-preflight")
    assert "Handler Cryptographic Tamper/Mismatch Violation" in excinfo.value.message


def test_missing_handler_file_fails_closed(temp_operation_env):
    manager = OperationRegistryManager.from_dict(
        temp_operation_env["registry_dict"],
        base_dir=temp_operation_env["base_dir"],
    )

    # Delete handler file
    temp_operation_env["handler2"].unlink()

    with pytest.raises(PolicyDeniedError) as excinfo:
        manager.verify_handler_integrity("op:test-worker")
    assert "does not physically exist" in excinfo.value.message


def test_process_image_validation(temp_operation_env):
    manager = OperationRegistryManager.from_dict(
        temp_operation_env["registry_dict"],
        base_dir=temp_operation_env["base_dir"],
    )

    # Valid process images for op:test-worker
    assert manager.validate_process_image("op:test-worker", "agy") is True
    assert manager.validate_process_image("op:test-worker", "agy.exe") is True
    assert manager.validate_process_image("op:test-worker", "powershell") is True
    assert manager.validate_process_image("op:test-worker", "pwsh") is False  # not in op profile whitelist
    assert manager.validate_process_image("op:test-worker", "node.exe") is True

    # Image not in global whitelist
    assert manager.validate_process_image("op:test-worker", "malware.exe") is False
    assert manager.validate_process_image("op:test-worker", "bash") is False

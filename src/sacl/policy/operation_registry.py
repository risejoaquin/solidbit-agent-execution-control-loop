"""SACL V1 Local Operation Registry Manager.

Authoritative local registry of trusted execution handlers and operation profiles
owned by the local SACL core installation.

Constitutional Invariant (ADR-006 & Authority Model §3):
Execution packages are declarative requests and possess zero execution authority.
Packages cannot self-authorize executable scripts.
Autoexecution in SACL core is restricted exclusively to locally installed handlers
registered in the Local Operation Registry with verified cryptographic SHA-256 digests.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from sacl.contracts.exceptions import PolicyDeniedError
from sacl.contracts.invariants import ALLOWED_PROCESS_IMAGES
from sacl.contracts.models import ExecutionProfile, OperationRegistry, OperationRegistryEntry
from sacl.contracts.schema_validator import SchemaValidator, get_default_validator


def normalize_image_name(image: str) -> str:
    """Normalizes an executable/process image name (e.g. agy.exe -> agy)."""
    clean = image.strip().lower()
    if clean.endswith(".exe"):
        clean = clean[:-4]
    return clean


class OperationRegistryManager:
    """Manages locally trusted operations, handler integrity, and profiles."""

    def __init__(
        self,
        registry: OperationRegistry,
        validator: Optional[SchemaValidator] = None,
        base_dir: Optional[Union[str, Path]] = None,
    ) -> None:
        self.validator = validator or get_default_validator()
        self._registry = registry
        self._base_dir = Path(base_dir).resolve() if base_dir else Path.cwd()
        self._validate_registry_invariants(self._registry)
        self._operations: Dict[str, OperationRegistryEntry] = {
            op.operation_id: op for op in self._registry.operations
        }

    def _validate_registry_invariants(self, registry: OperationRegistry) -> None:
        """Validates schema conformance and cryptographic digest formats."""
        self.validator.validate_operation_registry(registry.to_dict())

    @property
    def registry(self) -> OperationRegistry:
        """Returns the underlying OperationRegistry model."""
        return self._registry

    def list_operations(self) -> List[OperationRegistryEntry]:
        """Returns all registered operations."""
        return list(self._registry.operations)

    def get_operation(self, operation_id: str) -> Optional[OperationRegistryEntry]:
        """Finds operation by canonical operation_id."""
        return self._operations.get(operation_id)

    def resolve_operation(self, operation_id: str) -> OperationRegistryEntry:
        """Resolves an operation and asserts it is trusted and active.

        Raises:
            PolicyDeniedError: If operation is unregistered or disabled.
        """
        op = self.get_operation(operation_id)
        if not op:
            raise PolicyDeniedError(
                action=operation_id,
                layer="OPERATION_REGISTRY",
                reason=(
                    f"Unknown Operation Invariant Violation: Operation '{operation_id}' is not "
                    f"registered in the Local Operation Registry. Untrusted package scripts cannot self-authorize."
                ),
            )
        if not op.enabled:
            raise PolicyDeniedError(
                action=operation_id,
                layer="OPERATION_REGISTRY",
                reason=f"Operation '{operation_id}' is disabled in the Local Operation Registry.",
            )
        return op

    def resolve_handler_path(
        self, operation_id: str, custom_base_dir: Optional[Union[str, Path]] = None
    ) -> Path:
        """Resolves absolute path to handler file on disk."""
        op = self.resolve_operation(operation_id)
        base = Path(custom_base_dir).resolve() if custom_base_dir else self._base_dir
        path = Path(op.handler_path)
        if path.is_absolute():
            return path
        return base / path

    def verify_handler_integrity(
        self,
        operation_id: str,
        custom_base_dir: Optional[Union[str, Path]] = None,
    ) -> bool:
        """Verifies cryptographic SHA-256 digest of local handler on disk.

        Raises:
            PolicyDeniedError: If file is missing or SHA-256 digest does not match.
        """
        op = self.resolve_operation(operation_id)
        handler_path = self.resolve_handler_path(operation_id, custom_base_dir)

        if not handler_path.exists() or not handler_path.is_file():
            raise PolicyDeniedError(
                action=operation_id,
                layer="OPERATION_REGISTRY",
                reason=f"Handler script '{op.handler_path}' does not physically exist at '{handler_path}'.",
            )

        with open(handler_path, "rb") as f:
            content = f.read()

        actual_sha256 = hashlib.sha256(content).hexdigest().lower()
        expected_sha256 = op.handler_sha256.lower()

        if actual_sha256 != expected_sha256:
            raise PolicyDeniedError(
                action=operation_id,
                layer="OPERATION_REGISTRY",
                reason=(
                    f"Handler Cryptographic Tamper/Mismatch Violation: Operation '{operation_id}' "
                    f"handler '{handler_path}' failed digest verification. "
                    f"Expected: {expected_sha256}, Actual: {actual_sha256}"
                ),
            )

        return True

    def get_execution_profile(self, operation_id: str) -> ExecutionProfile:
        """Retrieves execution profile for operation."""
        op = self.resolve_operation(operation_id)
        return op.execution_profile

    def validate_process_image(self, operation_id: str, image_name: str) -> bool:
        """Validates that a process executable image is authorized for this operation."""
        profile = self.get_execution_profile(operation_id)
        clean_img = normalize_image_name(image_name)

        # 1. Check global image whitelist invariant
        if clean_img not in ALLOWED_PROCESS_IMAGES:
            return False

        # 2. Check operation-specific whitelist if declared
        if profile.allowed_process_images:
            allowed_norm = {normalize_image_name(img) for img in profile.allowed_process_images}
            return clean_img in allowed_norm

        return True

    def get_required_permissions(self, operation_id: str) -> List[str]:
        """Returns permissions required by operation."""
        op = self.resolve_operation(operation_id)
        return list(op.required_permissions)

    @classmethod
    def from_file(
        cls,
        path: Union[Path, str],
        validator: Optional[SchemaValidator] = None,
        base_dir: Optional[Union[str, Path]] = None,
    ) -> OperationRegistryManager:
        """Loads and validates OperationRegistryManager from a JSON file."""
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Operation registry configuration not found at: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        registry = OperationRegistry.from_dict(data)
        resolved_base = base_dir or file_path.parent
        return cls(registry=registry, validator=validator, base_dir=resolved_base)

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
        validator: Optional[SchemaValidator] = None,
        base_dir: Optional[Union[str, Path]] = None,
    ) -> OperationRegistryManager:
        """Loads and validates OperationRegistryManager from a dictionary."""
        registry = OperationRegistry.from_dict(data)
        return cls(registry=registry, validator=validator, base_dir=base_dir)

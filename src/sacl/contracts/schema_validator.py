"""SACL V1 Schema Validator Wrapper.

Provides strict jsonschema (Draft 2020-12) validation against canonical frozen schemas.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import jsonschema
from jsonschema.validators import Draft202012Validator

from sacl.contracts.exceptions import ContractValidationError


# Map schema identifiers and filenames
SCHEMA_FILES: Dict[str, str] = {
    "manifest": "manifest.schema.json",
    "solidbit.execution-package.v1": "manifest.schema.json",
    "approval": "approval.schema.json",
    "solidbit.approval.v1": "approval.schema.json",
    "graph": "graph.schema.json",
    "solidbit.execution-graph.v1": "graph.schema.json",
    "hard-policy": "hard-policy.schema.json",
    "solidbit.hard-policy.v1": "hard-policy.schema.json",
    "mail-envelope": "mail-envelope.schema.json",
    "solidbit.mail-envelope.v1": "mail-envelope.schema.json",
    "operation-registry": "operation-registry.schema.json",
    "solidbit.operation-registry.v1": "operation-registry.schema.json",
    "policy": "policy.schema.json",
    "solidbit.policy.v1": "policy.schema.json",
    "project-registry": "project-registry.schema.json",
    "solidbit.project-registry.v1": "project-registry.schema.json",
    "result": "result.schema.json",
    "solidbit.result.v1": "result.schema.json",
    "summary": "summary.schema.json",
    "solidbit.run-summary.v1": "summary.schema.json",
}


def find_schemas_dir(explicit_path: Optional[Path] = None) -> Path:
    """Discovers the directory containing canonical frozen JSON schemas."""
    if explicit_path and explicit_path.exists():
        return explicit_path

    # Search candidates from current file or cwd
    current = Path(__file__).resolve()
    for parent in [current.parent, current.parents[1], current.parents[2], current.parents[3], Path.cwd()]:
        candidate = parent / "schemas"
        if candidate.exists() and (candidate / "manifest.schema.json").exists():
            return candidate
        # Frozen architecture inputs
        candidate_frozen = parent / "inputs" / "frozen-architecture" / "schemas"
        if candidate_frozen.exists() and (candidate_frozen / "manifest.schema.json").exists():
            return candidate_frozen

    raise FileNotFoundError("Could not locate SACL canonical schemas directory ('schemas/').")


class SchemaValidator:
    """Validates payloads against SACL V1 JSON schemas using Draft202012Validator."""

    def __init__(self, schemas_dir: Optional[Path] = None) -> None:
        self.schemas_dir = find_schemas_dir(schemas_dir)
        self._schema_cache: Dict[str, Dict[str, Any]] = {}
        self._validator_cache: Dict[str, Draft202012Validator] = {}

    def get_schema(self, schema_key: str) -> Dict[str, Any]:
        """Loads and caches raw JSON schema by key or filename."""
        filename = SCHEMA_FILES.get(schema_key, schema_key)
        if not filename.endswith(".json"):
            filename = f"{filename}.schema.json"

        if filename in self._schema_cache:
            return self._schema_cache[filename]

        schema_file = self.schemas_dir / filename
        if not schema_file.exists():
            raise FileNotFoundError(f"Schema file '{filename}' does not exist in {self.schemas_dir}")

        with open(schema_file, "r", encoding="utf-8") as f:
            schema_data = json.load(f)

        self._schema_cache[filename] = schema_data
        return schema_data

    def get_validator(self, schema_key: str) -> Draft202012Validator:
        """Returns or creates a cached Draft202012Validator."""
        filename = SCHEMA_FILES.get(schema_key, schema_key)
        if not filename.endswith(".json"):
            filename = f"{filename}.schema.json"

        if filename in self._validator_cache:
            return self._validator_cache[filename]

        schema = self.get_schema(filename)
        validator = Draft202012Validator(schema)
        self._validator_cache[filename] = validator
        return validator

    def validate(self, schema_key: str, instance: Dict[str, Any]) -> None:
        """Validates an instance dictionary against the specified schema.

        Raises:
            ContractValidationError: If instance does not strictly conform.
        """
        validator = self.get_validator(schema_key)
        errors: List[str] = []
        for error in validator.iter_errors(instance):
            path_str = " -> ".join(str(p) for p in error.path) or "root"
            errors.append(f"[{path_str}]: {error.message}")

        if errors:
            raise ContractValidationError(
                schema_name=schema_key,
                message=f"Instance failed validation with {len(errors)} error(s)",
                errors=errors,
            )

    def is_valid(self, schema_key: str, instance: Dict[str, Any]) -> bool:
        """Returns True if the instance is valid, False otherwise."""
        try:
            self.validate(schema_key, instance)
            return True
        except ContractValidationError:
            return False

    # Convenience domain-specific methods
    def validate_manifest(self, instance: Dict[str, Any]) -> None:
        self.validate("manifest", instance)

    def validate_approval(self, instance: Dict[str, Any]) -> None:
        self.validate("approval", instance)

    def validate_graph(self, instance: Dict[str, Any]) -> None:
        self.validate("graph", instance)

    def validate_hard_policy(self, instance: Dict[str, Any]) -> None:
        self.validate("hard-policy", instance)

    def validate_mail_envelope(self, instance: Dict[str, Any]) -> None:
        self.validate("mail-envelope", instance)

    def validate_operation_registry(self, instance: Dict[str, Any]) -> None:
        self.validate("operation-registry", instance)

    def validate_policy(self, instance: Dict[str, Any]) -> None:
        self.validate("policy", instance)

    def validate_project_registry(self, instance: Dict[str, Any]) -> None:
        self.validate("project-registry", instance)

    def validate_result(self, instance: Dict[str, Any]) -> None:
        self.validate("result", instance)

    def validate_summary(self, instance: Dict[str, Any]) -> None:
        self.validate("summary", instance)


# Module-level singleton
_default_validator: Optional[SchemaValidator] = None


def get_default_validator() -> SchemaValidator:
    global _default_validator
    if _default_validator is None:
        _default_validator = SchemaValidator()
    return _default_validator


def validate_payload(schema_key: str, instance: Dict[str, Any], schemas_dir: Optional[Path] = None) -> None:
    """Convenience function to validate a payload against a schema."""
    if schemas_dir:
        SchemaValidator(schemas_dir).validate(schema_key, instance)
    else:
        get_default_validator().validate(schema_key, instance)

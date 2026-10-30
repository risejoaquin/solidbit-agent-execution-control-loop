"""SACL V1 Test Schema Helpers.

Utility functions for schema assertions and example payload validations in tests.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pytest

from sacl.contracts.exceptions import ContractValidationError
from sacl.contracts.schema_validator import SchemaValidator


def assert_validates_schema(
    validator: SchemaValidator, schema_key: str, instance: Dict[str, Any]
) -> None:
    """Asserts that an instance dictionary strictly validates against schema_key."""
    try:
        validator.validate(schema_key, instance)
    except ContractValidationError as exc:
        pytest.fail(
            f"Validation failed unexpectedly for '{schema_key}':\n"
            + "\n".join(exc.validation_errors)
        )


def assert_fails_schema(
    validator: SchemaValidator,
    schema_key: str,
    instance: Dict[str, Any],
    expected_error_substr: str | None = None,
) -> None:
    """Asserts that an instance dictionary fails schema validation."""
    with pytest.raises(ContractValidationError) as exc_info:
        validator.validate(schema_key, instance)
    if expected_error_substr:
        errors_text = " ".join(exc_info.value.validation_errors)
        assert expected_error_substr.lower() in errors_text.lower(), (
            f"Expected substring '{expected_error_substr}' not found in errors: {errors_text}"
        )


def load_json_file(path: Path) -> Dict[str, Any]:
    """Reads and parses a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

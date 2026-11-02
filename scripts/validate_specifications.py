#!/usr/bin/env python3
"""Validate SACL .sdd.json contracts and monotonic parent/child governance."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("specification root must be a JSON object")
    return value


def validate_inheritance(specs: list[dict[str, Any]]) -> list[str]:
    """Return deterministic errors for identity, parent, cycle, and monotonicity violations."""
    errors: list[str] = []
    by_id: dict[str, dict[str, Any]] = {}

    for spec in specs:
        spec_id = spec.get("spec_id")
        if not isinstance(spec_id, str):
            continue
        if spec_id in by_id:
            errors.append(f"duplicate spec_id: {spec_id}")
        else:
            by_id[spec_id] = spec

        for collection in (
            "functional_contracts",
            "invariants",
            "quality_attributes",
            "acceptance_scenarios",
        ):
            seen: set[str] = set()
            for item in spec.get(collection, []):
                item_id = item.get("id") if isinstance(item, dict) else None
                if not isinstance(item_id, str):
                    continue
                if item_id in seen:
                    errors.append(f"{spec_id}: duplicate {collection} id: {item_id}")
                seen.add(item_id)

        seen_roles: set[str] = set()
        for role in spec.get("agent_roles", []):
            role_id = role.get("role") if isinstance(role, dict) else None
            if not isinstance(role_id, str):
                continue
            if role_id in seen_roles:
                errors.append(f"{spec_id}: duplicate agent role: {role_id}")
            seen_roles.add(role_id)

    for spec_id, spec in by_id.items():
        parent_id = spec.get("parent_spec")
        if parent_id is None:
            continue
        parent = by_id.get(parent_id)
        if parent is None:
            errors.append(f"{spec_id}: missing parent_spec {parent_id}")
            continue
        if parent.get("status") == "superseded":
            errors.append(f"{spec_id}: cannot inherit from superseded parent {parent_id}")

        parent_invariants = {
            item.get("id"): item.get("statement")
            for item in parent.get("invariants", [])
            if isinstance(item, dict)
        }
        child_invariants = {
            item.get("id"): item.get("statement")
            for item in spec.get("invariants", [])
            if isinstance(item, dict)
        }
        for invariant_id, statement in parent_invariants.items():
            if child_invariants.get(invariant_id) != statement:
                errors.append(
                    f"{spec_id}: inherited invariant {invariant_id} is missing or modified"
                )

        parent_denials = set(parent.get("security", {}).get("must_not", []))
        child_denials = set(spec.get("security", {}).get("must_not", []))
        if not parent_denials.issubset(child_denials):
            errors.append(f"{spec_id}: child weakens inherited security.must_not restrictions")

        parent_forbidden = set(parent.get("architecture", {}).get("forbidden_dependencies", []))
        child_forbidden = set(spec.get("architecture", {}).get("forbidden_dependencies", []))
        if not parent_forbidden.issubset(child_forbidden):
            errors.append(
                f"{spec_id}: child removes inherited architecture.forbidden_dependencies"
            )

        parent_allowed = set(parent.get("architecture", {}).get("allowed_dependencies", []))
        child_allowed = set(spec.get("architecture", {}).get("allowed_dependencies", []))
        if not child_allowed.issubset(parent_allowed):
            errors.append(
                f"{spec_id}: child adds an allowed dependency not permitted by its parent"
            )

        if spec.get("status") == "frozen" and parent.get("status") != "frozen":
            errors.append(f"{spec_id}: cannot be frozen while parent {parent_id} is not frozen")

    # Detect cycles independently from missing-parent and schema diagnostics.
    for start_id in by_id:
        visited: set[str] = set()
        current_id: str | None = start_id
        while current_id is not None and current_id in by_id:
            if current_id in visited:
                errors.append(f"inheritance cycle detected from {start_id}")
                break
            visited.add(current_id)
            current_id = by_id[current_id].get("parent_spec")

    return sorted(set(errors))


def validate_repository(root: Path) -> list[str]:
    """Validate all specs under root/specs against root/schemas/specification.schema.json."""
    specs_dir = root / "specs"
    schema_path = root / "schemas" / "specification.schema.json"
    if not schema_path.is_file():
        return [f"missing specification schema: {schema_path}"]
    if not specs_dir.is_dir():
        return [f"missing specifications directory: {specs_dir}"]

    try:
        schema = _load_json(schema_path)
        Draft202012Validator.check_schema(schema)
    except Exception as exc:  # schema load errors are user-facing validation failures
        return [f"invalid specification schema: {exc}"]

    validator = Draft202012Validator(schema)
    paths = sorted(specs_dir.rglob("*.sdd.json"))
    if not paths:
        return ["no .sdd.json specification documents found"]

    documents: list[dict[str, Any]] = []
    errors: list[str] = []
    for path in paths:
        try:
            document = _load_json(path)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{path.relative_to(root)}: cannot parse JSON: {exc}")
            continue
        documents.append(document)
        for issue in validator.iter_errors(document):
            location = ".".join(str(part) for part in issue.absolute_path) or "$"
            errors.append(f"{path.relative_to(root)}:{location}: {issue.message}")

    if not errors:
        errors.extend(validate_inheritance(documents))
    return sorted(errors)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root (defaults to the parent of scripts/)",
    )
    args = parser.parse_args()
    errors = validate_repository(args.root.resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Specification governance: FAIL ({len(errors)} error(s))", file=sys.stderr)
        return 1
    print("Specification governance: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

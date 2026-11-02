"""Regression tests for closed SACL specification contracts."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from scripts.validate_specifications import validate_inheritance, validate_repository

ROOT = Path(__file__).resolve().parents[2]


def test_repository_specifications_are_valid() -> None:
    assert validate_repository(ROOT) == []


def test_child_cannot_remove_parent_invariant() -> None:
    parent = {
        "spec_id": "SACL-ROOT-001",
        "status": "frozen",
        "parent_spec": None,
        "invariants": [{"id": "SACL-I-001", "statement": "MUST preserve the canonical precedence hierarchy."}],
        "security": {"must_not": ["MUST NOT store secrets in Git."]},
        "architecture": {
            "allowed_dependencies": ["jsonschema"],
            "forbidden_dependencies": ["production database writes"],
        },
    }
    child = {
        "spec_id": "SACL-MOD-001",
        "status": "draft",
        "parent_spec": "SACL-ROOT-001",
        "invariants": [],
        "security": {"must_not": []},
        "architecture": {
            "allowed_dependencies": ["jsonschema", "requests"],
            "forbidden_dependencies": [],
        },
    }

    errors = validate_inheritance([parent, child])
    assert any("inherited invariant" in error for error in errors)
    assert any("weakens inherited security" in error for error in errors)
    assert any("removes inherited architecture" in error for error in errors)
    assert any("adds an allowed dependency" in error for error in errors)


def test_inheritance_cycle_is_rejected() -> None:
    base = {
        "status": "draft",
        "invariants": [],
        "security": {"must_not": []},
        "architecture": {"allowed_dependencies": [], "forbidden_dependencies": []},
    }
    first = {**base, "spec_id": "SACL-MOD-001", "parent_spec": "SACL-MOD-002"}
    second = {**base, "spec_id": "SACL-MOD-002", "parent_spec": "SACL-MOD-001"}
    assert any("cycle detected" in error for error in validate_inheritance([first, second]))


def test_duplicate_requirement_ids_are_rejected() -> None:
    spec = {
        "spec_id": "SACL-MOD-001",
        "status": "draft",
        "parent_spec": None,
        "functional_contracts": [
            {"id": "SACL-F-001"},
            {"id": "SACL-F-001"},
        ],
    }
    assert any(
        "duplicate functional_contracts id" in error
        for error in validate_inheritance([spec])
    )


def test_cli_returns_nonzero_for_invalid_specification(tmp_path: Path) -> None:
    (tmp_path / "schemas").mkdir()
    shutil.copy(
        ROOT / "schemas" / "specification.schema.json",
        tmp_path / "schemas" / "specification.schema.json",
    )
    (tmp_path / "specs").mkdir()
    (tmp_path / "specs" / "invalid.sdd.json").write_text(
        json.dumps({"schema": "wrong", "spec_id": "broken"}),
        encoding="utf-8",
    )
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_specifications.py"), "--root", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 1
    assert "Specification governance: FAIL" in completed.stderr

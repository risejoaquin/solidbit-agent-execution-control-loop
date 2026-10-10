"""Tests for Dual SUMMARY Deliverables Contracts (SUMMARY.md and SUMMARY.json).

Adheres to:
- RESULT_PROTOCOL.md §7
- schemas/summary.schema.json
- Decision Baseline #23 (Mandatory dual deliverables)
- Invariant: A boolean in summary is evidence of authorization, NOT execution authority.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from sacl.contracts.exceptions import ContractValidationError
from sacl.contracts.models import AgentResult, RunSummary
from sacl.contracts.schema_validator import SchemaValidator
from sacl.results.summary import DualSummaryGenerator


@pytest.fixture
def summary_gen(schema_validator: SchemaValidator) -> DualSummaryGenerator:
    return DualSummaryGenerator(validator=schema_validator)


@pytest.fixture
def sample_agent_results() -> list[AgentResult]:
    return [
        AgentResult(
            agent="AG-PROTOCOL",
            status="COMPLETE",
            exitCode=0,
            verdict="PASS",
            reportExists=True,
        ),
        AgentResult(
            agent="AG-ARCH",
            status="COMPLETE",
            exitCode=0,
            verdict="PASS",
            reportExists=True,
        ),
    ]


def test_build_summary_model_validates_against_schema(
    summary_gen: DualSummaryGenerator, sample_agent_results: list[AgentResult]
) -> None:
    summary = summary_gen.build_summary_model(
        run_id="w0-1-20261007-094653-54bb4c",
        package_id="SACL-W0-1-PACKAGE-v1",
        project="solidbit-agent-execution-control-loop",
        status="PASS",
        ready_for_integration="NO",
        agent_results=sample_agent_results,
        conflicting_files=[],
        documents_created=["docs/spec.md"],
        adrs_created=["ADR-001"],
        schemas_created=["schemas/summary.schema.json"],
        compatibility_findings=["P1-01 Subject syntax"],
        next_safe_action="HUMAN_CODE_REVIEW",
        architecture_freeze_ready=True,
        implementation_authorized=False,
    )

    assert summary.run_id == "w0-1-20261007-094653-54bb4c"
    assert summary.status == "PASS"
    assert summary.ready_for_integration == "NO"
    assert summary.implementation_authorized is False
    assert len(summary.agent_results) == 2


def test_format_markdown_summary_structure(
    summary_gen: DualSummaryGenerator, sample_agent_results: list[AgentResult]
) -> None:
    summary = summary_gen.build_summary_model(
        run_id="run-md-001",
        package_id="pkg-001",
        project="test-project",
        status="PASS",
        ready_for_integration="YES",
        agent_results=sample_agent_results,
        conflicting_files=[],
        documents_created=["docs/test.md"],
        next_safe_action="MERGE_PR",
    )

    md = summary_gen.format_markdown_summary(summary)

    # Check key sections
    assert "# SACL EXECUTION RUN SUMMARY: PASS" in md
    assert "`run-md-001`" in md
    assert "## 1. Run Metadata" in md
    assert "## 2. Agent Deliverables & Status" in md
    assert "| `AG-PROTOCOL` | `COMPLETE` | `0` | `YES` | **`PASS`** |" in md
    assert "## 3. Cross-Agent File Collisions & Modifications" in md
    assert "No cross-agent file conflicts detected" in md
    assert "## 4. Deliverables Created" in md
    assert "## 5. Immediate Next Safe Action" in md
    assert "**`MERGE_PR`**" in md


def test_write_dual_summaries_materializes_both_files(
    summary_gen: DualSummaryGenerator, sample_agent_results: list[AgentResult], tmp_path: Path
) -> None:
    summary = summary_gen.build_summary_model(
        run_id="run-dual-001",
        package_id="pkg-001",
        project="test-project",
        status="PASS",
        ready_for_integration="YES",
        agent_results=sample_agent_results,
        conflicting_files=[],
        next_safe_action="DEPLOY_STAGING",
    )

    run_dir = tmp_path / "run_out"
    md_path, json_path = summary_gen.write_dual_summaries(summary, run_dir)

    assert md_path.exists()
    assert json_path.exists()
    assert md_path.stat().st_size > 0
    assert json_path.stat().st_size > 0

    # Verify JSON content
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["schema"] == "solidbit.run-summary.v1"
    assert data["run_id"] == "run-dual-001"
    assert data["status"] == "PASS"

"""SACL V1 Comprehensive Contracts & Scaffold Test Suite.

Validates:
- All 10 frozen examples against canonical schemas
- Architecture invariants JSON conformance
- Strongly-typed models serialization & deserialization
- Hard deny policy enforcement
- PID recycling and whitelist defense
- 4-point reconciliation priority ladder
- SQLite 001_init.sql schema integrity across all 16 domains and compatibility tables
"""

from __future__ import annotations

import datetime
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict

import pytest

from sacl.contracts.exceptions import (
    ContractValidationError,
    HardDenyViolation,
)
from sacl.contracts.invariants import (
    ALL_JOB_STATES,
    ALLOWED_PROCESS_IMAGES,
    APPROVAL_BINDING_FIELDS,
    APPROVAL_CHANNELS_V1,
    DECISION_PRECEDENCE,
    GRAPH_NODE_STATES,
    HARD_DENIED_ACTIONS,
    OPERATIONAL_STATE_DOMAINS,
    PRIMARY_JOB_STATES,
    RECONCILIATION_PILLARS,
    SIDE_JOB_STATES,
    ApprovalChannel,
    ApprovalDecision,
    ApprovalStatus,
    GraphNodeStatus,
    JobSideStatus,
    JobStatus,
    Verdict,
)
from sacl.contracts.models import (
    ApprovalToken,
    ExecutionGraph,
    HardLocalPolicy,
    MailEnvelope,
    Manifest,
    OperationRegistry,
    PersistedState,
    ProcessObservation,
    ProjectPolicy,
    ProjectRegistry,
    ReconciledResult,
    RequiredOutputs,
    RunSummary,
    WorktreeState,
)
from sacl.contracts.reconciliation import (
    extract_verdict_from_content,
    reconcile_agent,
    verify_process_observation,
)
from sacl.contracts.schema_validator import SchemaValidator
from tests.helpers.db_helpers import (
    check_foreign_keys_enabled,
    check_wal_mode,
    get_all_table_names,
    verify_canonical_domains_exist,
)
from tests.helpers.mock_helpers import (
    create_mock_log_content,
    create_mock_report_content,
)
from tests.helpers.schema_helpers import (
    assert_fails_schema,
    assert_validates_schema,
)


# ============================================================================
# 1. ARCHITECTURAL INVARIANTS & CONSTITUTIONAL TESTS
# ============================================================================

def test_decision_precedence_invariants() -> None:
    """Verifies that decision precedence contains exactly the four inviolable tiers in order."""
    expected = (
        "explicit_joaquin_decisions",
        "proven_current_orchestrator_behavior",
        "existing_governance_and_contracts",
        "industry_standard_for_undefined_gaps_only",
    )
    assert DECISION_PRECEDENCE == expected


def test_job_lifecycle_12_primary_and_10_side_states() -> None:
    """Verifies the 12 canonical linear job states and 10 side states."""
    assert len(JobStatus) == 12
    assert len(JobSideStatus) == 10

    expected_primary = [
        "RECEIVED", "AUTHENTICATED", "VALIDATED", "PERSISTED",
        "QUEUED", "DISPATCHED", "RUNNING", "VERIFYING",
        "RESULT_PACKAGED", "RESULT_SENT", "COMPLETED", "ARCHIVED"
    ]
    assert [s.value for s in JobStatus] == expected_primary

    expected_side = [
        "WAITING_APPROVAL", "RETRY_WAIT", "BLOCKED", "FAILED",
        "CANCELLED", "INTERRUPTED", "TIMED_OUT", "POLICY_DENIED",
        "REJECTED", "QUARANTINED"
    ]
    assert [s.value for s in JobSideStatus] == expected_side


def test_graph_node_9_states() -> None:
    """Verifies the 9 Graph-H DAG node states."""
    expected = [
        "PENDING", "READY", "RUNNING", "SUCCEEDED",
        "RETRYABLE_FAILURE", "FAILED", "BLOCKED",
        "WAITING_APPROVAL", "CANCELLED"
    ]
    assert [s.value for s in GraphNodeStatus] == expected


def test_architecture_invariants_json_consistency(repo_root: Path) -> None:
    """Verifies physical contracts/architecture-invariants.json matches Python contract constants."""
    invariants_path = repo_root / "contracts" / "architecture-invariants.json"
    assert invariants_path.exists(), "contracts/architecture-invariants.json must exist"

    with open(invariants_path, "r", encoding="utf-8") as f:
        inv = json.load(f)

    assert inv["decision_precedence"] == list(DECISION_PRECEDENCE)
    assert inv["job_lifecycle"] == [s.value for s in JobStatus]
    assert inv["job_side_states"] == [s.value for s in JobSideStatus]
    assert inv["graph_node_states"] == [s.value for s in GraphNodeStatus]
    assert inv["approval_binding"] == list(APPROVAL_BINDING_FIELDS)
    assert inv["operational_state_domains"] == list(OPERATIONAL_STATE_DOMAINS)
    assert set(inv["approval_channels_v1"]) == APPROVAL_CHANNELS_V1
    assert inv["heavy_artifacts_on_filesystem"] is True
    assert inv["process_exit_code_alone_is_authoritative"] is False
    assert inv["run_status_reconciliation"] == list(RECONCILIATION_PILLARS)


def test_hard_denied_actions_envelope() -> None:
    """Verifies that all 9 immutable hard denials are present in HARD_DENIED_ACTIONS."""
    required_denials = {
        "remote_production_execution",
        "github_merge",
        "production_db_write",
        "secret_export",
        "arbitrary_remote_code",
        "main_branch_execution",
        "primary_checkout_mutation",
        "hard_reset",
        "auto_stash",
    }
    assert HARD_DENIED_ACTIONS == required_denials

    # Verify exception behavior
    with pytest.raises(HardDenyViolation) as exc_info:
        raise HardDenyViolation("github_merge")
    assert "github_merge" in exc_info.value.message


# ============================================================================
# 2. FROZEN EXAMPLES SCHEMA VALIDATION TESTS
# ============================================================================

def test_all_10_frozen_examples_validate_against_schemas(
    schema_validator: SchemaValidator,
    examples_dir: Path,
) -> None:
    """Validates each of the 10 canonical frozen example files against its schema."""
    mapping = {
        "approval.valid.json": "approval",
        "graph.valid.json": "graph",
        "hard-policy.valid.json": "hard-policy",
        "mail-envelope.valid.json": "mail-envelope",
        "manifest.valid.json": "manifest",
        "operation-registry.valid.json": "operation-registry",
        "policy.valid.json": "policy",
        "project-registry.valid.json": "project-registry",
        "result.valid.json": "result",
        "summary.valid.json": "summary",
    }

    validated_count = 0
    for filename, schema_key in mapping.items():
        filepath = examples_dir / filename
        assert filepath.exists(), f"Example file '{filename}' missing in {examples_dir}"
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert_validates_schema(schema_validator, schema_key, data)
        validated_count += 1

    assert validated_count == 10


# ============================================================================
# 3. STRONGLY-TYPED MODEL ROUND-TRIP TESTS
# ============================================================================

def test_models_roundtrip_from_and_to_dict(
    load_frozen_example: Any,
    schema_validator: SchemaValidator,
) -> None:
    """Verifies that models parse from frozen example dictionaries and serialize back cleanly."""
    # Manifest
    manifest_data = load_frozen_example("manifest.valid.json")
    manifest = Manifest.from_dict(manifest_data)
    assert manifest.package_id == manifest_data["package_id"]
    assert manifest.job_id == manifest_data["job_id"]
    schema_validator.validate_manifest(manifest.to_dict())

    # ApprovalToken
    approval_data = load_frozen_example("approval.valid.json")
    approval = ApprovalToken.from_dict(approval_data)
    assert approval.request_id == approval_data["request_id"]
    assert approval.approver.identity == "Joaquín"
    schema_validator.validate_approval(approval.to_dict())

    # HardLocalPolicy
    hard_policy_data = load_frozen_example("hard-policy.valid.json")
    hard_policy = HardLocalPolicy.from_dict(hard_policy_data)
    assert hard_policy.hard_denies.github_merge is True
    schema_validator.validate_hard_policy(hard_policy.to_dict())

    # ExecutionGraph
    graph_data = load_frozen_example("graph.valid.json")
    graph = ExecutionGraph.from_dict(graph_data)
    assert graph.max_parallel == 2
    assert len(graph.phases) == 2
    schema_validator.validate_graph(graph.to_dict())

    # MailEnvelope
    mail_data = load_frozen_example("mail-envelope.valid.json")
    mail = MailEnvelope.from_dict(mail_data)
    assert mail.direction == "INBOUND"
    assert mail.routing_subject.job_id == "job-20261007-094653"
    schema_validator.validate_mail_envelope(mail.to_dict())

    # OperationRegistry
    op_data = load_frozen_example("operation-registry.valid.json")
    op_reg = OperationRegistry.from_dict(op_data)
    assert len(op_reg.operations) == 5
    schema_validator.validate_operation_registry(op_reg.to_dict())

    # ProjectRegistry
    proj_data = load_frozen_example("project-registry.valid.json")
    proj_reg = ProjectRegistry.from_dict(proj_data)
    assert len(proj_reg.projects) == 2
    schema_validator.validate_project_registry(proj_reg.to_dict())

    # ProjectPolicy
    policy_data = load_frozen_example("policy.valid.json")
    policy = ProjectPolicy.from_dict(policy_data)
    assert policy.permissions["source_orchestrator_read"] is True
    schema_validator.validate_policy(policy.to_dict())

    # ReconciledResult
    res_data = load_frozen_example("result.valid.json")
    res = ReconciledResult.from_dict(res_data)
    assert res.result_verdict == "PASS"
    schema_validator.validate_result(res.to_dict())

    # RunSummary
    summary_data = load_frozen_example("summary.valid.json")
    summary = RunSummary.from_dict(summary_data)
    assert summary.status == "PASS"
    assert summary.ready_for_integration == "NO"
    schema_validator.validate_summary(summary.to_dict())


# ============================================================================
# 4. PID RECYCLING & PROCESS OBSERVATION DEFENSE TESTS
# ============================================================================

def test_process_observation_image_whitelist() -> None:
    """Verifies that non-whitelisted image binaries are rejected."""
    # Whitelisted images succeed
    for img in ["agy.exe", "powershell", "pwsh.exe", "cmd", "node", "python", "git"]:
        obs, valid, reason = verify_process_observation(pid=1234, process_name=img, is_active=True)
        assert valid is True
        assert reason is None

    # Unapproved image is rejected
    obs, valid, reason = verify_process_observation(pid=5678, process_name="calc.exe", is_active=True)
    assert valid is False
    assert "not in allowed whitelist" in str(reason)


def test_process_observation_start_time_drift_guard() -> None:
    """Verifies that process start time drift exceeding 300 seconds triggers PID recycling defense."""
    base_time = datetime.datetime(2026, 10, 7, 12, 0, 0, tzinfo=datetime.timezone.utc)

    # Within tolerance: 10 seconds drift -> valid
    actual_ok = base_time + datetime.timedelta(seconds=10)
    obs, valid, reason = verify_process_observation(
        pid=9999,
        process_name="agy",
        is_active=True,
        persisted_start_time=base_time.isoformat(),
        actual_start_time=actual_ok,
    )
    assert valid is True
    assert reason is None
    assert obs.start_time_drift_seconds == 10.0

    # Exceeding tolerance: 301 seconds drift -> PID recycled by unrelated process!
    actual_recycled = base_time + datetime.timedelta(seconds=301)
    obs, valid, reason = verify_process_observation(
        pid=9999,
        process_name="agy",
        is_active=True,
        persisted_start_time=base_time.isoformat(),
        actual_start_time=actual_recycled,
    )
    assert valid is False
    assert "PID recycling detected" in str(reason)
    assert obs.start_time_drift_seconds == 301.0


# ============================================================================
# 5. RECONCILIATION PRIORITY LADDER TESTS
# ============================================================================

def test_verdict_extraction_priority_2_report_bottom_up() -> None:
    """Priority 2: Report bottom-up primary structured marker."""
    content = create_mock_report_content(agent_id="AG-BOOTSTRAP", verdict="PASS", marker_type="PRIMARY")
    ve = extract_verdict_from_content(report_content=content, report_exists=True, report_size_bytes=len(content))
    assert ve.verdict == "PASS"
    assert ve.extraction_method == "REGEX_PRIMARY_BOTTOM_UP"
    assert "AGENT_AG_BOOTSTRAP_RESULT = PASS" in ve.matched_marker


def test_verdict_extraction_priority_3_header_fallback() -> None:
    """Priority 3: Top 25 lines header fallback."""
    content = create_mock_report_content(agent_id="AG-TEST", verdict="PARTIAL", marker_type="HEADER")
    ve = extract_verdict_from_content(report_content=content, report_exists=True, report_size_bytes=len(content))
    assert ve.verdict == "PARTIAL"
    assert ve.extraction_method == "HEADER_FALLBACK_TOP25"


def test_verdict_extraction_priority_4_log_scan() -> None:
    """Priority 4: Tail 150 lines of logs scan."""
    report_no_marker = create_mock_report_content(agent_id="AG-TEST", marker_type="NONE")
    logs = create_mock_log_content(agent_id="AG-TEST", verdict="BLOCKED")
    ve = extract_verdict_from_content(
        report_content=report_no_marker,
        stdout_content=logs,
        report_exists=True,
        report_size_bytes=len(report_no_marker),
    )
    assert ve.verdict == "BLOCKED"
    assert ve.extraction_method == "LOG_SCAN_TAIL150"


def test_verdict_extraction_priority_5_legacy_fallback() -> None:
    """Priority 5: Report present & non-empty & exit_code == 0 -> 'PASS (Report Present)'."""
    report_no_marker = create_mock_report_content(agent_id="AG-TEST", marker_type="NONE")
    ve = extract_verdict_from_content(
        report_content=report_no_marker,
        stdout_content=None,
        report_exists=True,
        report_size_bytes=len(report_no_marker),
        exit_code=0,
    )
    assert ve.verdict == Verdict.PASS_REPORT_PRESENT.value
    assert ve.extraction_method == "LEGACY_REPORT_PRESENT_FALLBACK"


def test_verdict_extraction_priority_6_failure() -> None:
    """Priority 6: Missing report and no markers evaluates to FAILED."""
    ve = extract_verdict_from_content(
        report_content=None,
        stdout_content=None,
        report_exists=False,
        report_size_bytes=0,
        exit_code=1,
    )
    assert ve.verdict == Verdict.FAILED.value
    assert ve.extraction_method == "NO_EVIDENCE_FOUND"


def test_done_review_required_never_equals_pass() -> None:
    """Constitutional Invariant: DONE_REVIEW_REQUIRED never equals PASS."""
    assert Verdict.DONE_REVIEW_REQUIRED.value != Verdict.PASS.value
    assert Verdict.DONE_REVIEW_REQUIRED.value != Verdict.PASS_REPORT_PRESENT.value


# ============================================================================
# 6. SQLITE RELATIONAL SCHEMA (001_INIT.SQL) TESTS
# ============================================================================

def test_sqlite_all_16_domains_created(sqlite_memory_db: sqlite3.Connection) -> None:
    """Verifies that 001_init.sql creates all 16 canonical operational state domains."""
    domain_checks = verify_canonical_domains_exist(sqlite_memory_db)
    missing = [domain for domain, exists in domain_checks.items() if not exists]
    assert not missing, f"Missing canonical SQLite domains: {missing}"


def test_sqlite_compatibility_tables_created(sqlite_memory_db: sqlite3.Connection) -> None:
    """Verifies that legacy compatibility tables exist in the database."""
    tables = set(get_all_table_names(sqlite_memory_db))
    expected_compat = {
        "supervisor_locks",
        "dag_stages",
        "agent_dependencies",
        "file_modifications",
        "file_conflicts",
        "mail_inbox",
        "mail_outbox",
        "audit_events",
    }
    missing = expected_compat - tables
    assert not missing, f"Missing compatibility tables: {missing}"


def test_sqlite_foreign_key_enforcement(sqlite_memory_db: sqlite3.Connection) -> None:
    """Verifies that foreign keys are strictly enforced (e.g. jobs -> packages)."""
    assert check_foreign_keys_enabled(sqlite_memory_db) is True
    cursor = sqlite_memory_db.cursor()

    # Attempting to insert a job pointing to a non-existent package should fail
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute(
            """
            INSERT INTO jobs (job_id, package_id, status, created_at, updated_at)
            VALUES ('job-bad-fk', 'non-existent-package', 'RECEIVED', '2026-10-07T00:00:00Z', '2026-10-07T00:00:00Z');
            """
        )


def test_sqlite_wal_mode_and_pragmas(sqlite_temp_db: sqlite3.Connection) -> None:
    """Verifies that a disk-backed SQLite connection successfully operates in WAL mode."""
    assert check_wal_mode(sqlite_temp_db) is True
    assert check_foreign_keys_enabled(sqlite_temp_db) is True


# ============================================================================
# 7. NEGATIVE SCHEMA VALIDATION TESTS
# ============================================================================

def test_negative_schema_manifest_missing_job_id(
    load_frozen_example: Any,
    schema_validator: SchemaValidator,
) -> None:
    """Manifest strictly requires job_id (SB-FREEZE-P2-01)."""
    manifest_data = load_frozen_example("manifest.valid.json")
    del manifest_data["job_id"]
    assert_fails_schema(schema_validator, "manifest", manifest_data, "job_id")


def test_negative_schema_approval_disallowed_channel(
    load_frozen_example: Any,
    schema_validator: SchemaValidator,
) -> None:
    """Approvals in V1 allow only CLI, GMAIL, MANUAL (no webhook)."""
    approval_data = load_frozen_example("approval.valid.json")
    approval_data["approver"]["channel"] = "WEBHOOK"
    assert_fails_schema(schema_validator, "approval", approval_data)


def test_negative_schema_mail_envelope_size_exceeded(
    load_frozen_example: Any,
    schema_validator: SchemaValidator,
) -> None:
    """Mail envelope rejects attachments larger than 25 MB (26,214,400 bytes)."""
    mail_data = load_frozen_example("mail-envelope.valid.json")
    mail_data["attachment"]["size_bytes"] = 30_000_000
    assert_fails_schema(schema_validator, "mail-envelope", mail_data)


# ============================================================================
# 8. FULL RECONCILIATION PIPELINE INTEGRATION TESTS
# ============================================================================

def test_reconcile_agent_full_pipeline_success() -> None:
    """Tests complete reconcile_agent returning a valid SUCCEEDED ReconciledResult."""
    obs = ProcessObservation(
        pid=1234,
        is_active=False,
        process_name="agy",
        start_time_drift_seconds=2.0,
        exit_code=0,
    )
    pstate = PersistedState(status="RUNNING")
    report_text = create_mock_report_content(agent_id="AG-BOOTSTRAP", verdict="PASS", marker_type="PRIMARY")
    outputs = RequiredOutputs(
        report_path="reports/AG-BOOTSTRAP.REPORT.md",
        report_exists=True,
        report_size_bytes=len(report_text),
        stdout_path="logs/AG-BOOTSTRAP.stdout.log",
        stderr_path="logs/AG-BOOTSTRAP.stderr.log",
        expected_files_verified=True,
    )
    wt = WorktreeState(
        branch="sacl-test-bootstrap",
        worktree_path="C:/tmp/wt",
        commit_sha=None,
        is_clean=True,
        modified_files=["pyproject.toml"],
    )

    reconciled = reconcile_agent(
        run_id="run-001",
        agent_id="AG-BOOTSTRAP",
        process_obs=obs,
        persisted_state=pstate,
        required_outputs=outputs,
        worktree=wt,
        report_content=report_text,
    )

    assert reconciled.status == "SUCCEEDED"
    assert reconciled.result_verdict == "PASS"
    assert reconciled.reconciliation.verdict_extraction.verdict == "PASS"


def test_reconcile_agent_full_pipeline_blocked() -> None:
    """Tests reconcile_agent returning a BLOCKED ReconciledResult when report contains BLOCKED."""
    obs = ProcessObservation(
        pid=1234,
        is_active=False,
        process_name="agy",
        start_time_drift_seconds=1.0,
        exit_code=0,
    )
    pstate = PersistedState(status="RUNNING")
    report_text = create_mock_report_content(agent_id="AG-TEST", verdict="BLOCKED", marker_type="PRIMARY")
    outputs = RequiredOutputs(
        report_path="reports/AG-TEST.REPORT.md",
        report_exists=True,
        report_size_bytes=len(report_text),
        stdout_path="logs/AG-TEST.stdout.log",
        stderr_path="logs/AG-TEST.stderr.log",
        expected_files_verified=True,
    )
    wt = WorktreeState(
        branch="sacl-test",
        worktree_path="C:/tmp/wt",
        commit_sha=None,
        is_clean=True,
    )

    reconciled = reconcile_agent(
        run_id="run-002",
        agent_id="AG-TEST",
        process_obs=obs,
        persisted_state=pstate,
        required_outputs=outputs,
        worktree=wt,
        report_content=report_text,
    )

    assert reconciled.status == "BLOCKED"
    assert reconciled.result_verdict == "BLOCKED"

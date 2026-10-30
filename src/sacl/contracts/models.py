"""SACL V1 Strongly-Typed Data Models.

Matches schemas under schemas/*.schema.json and operational tables in 001_init.sql.
Provides serialization and deserialization helpers.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

# ============================================================================
# HARD LOCAL POLICY MODELS
# ============================================================================


@dataclass
class HardDenies:
    """The 9 immutable prohibitions in Hard Local Policy."""

    remote_production_execution: bool = True
    github_merge: bool = True
    production_db_write: bool = True
    secret_export: bool = True
    arbitrary_remote_code: bool = True
    main_branch_execution: bool = True
    primary_checkout_mutation: bool = True
    hard_reset: bool = True
    auto_stash: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> HardDenies:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class HardLocalPolicy:
    """SolidBit Hard Local Policy Specification v1."""

    policy_id: str
    hard_denies: HardDenies
    schema: str = "solidbit.hard-policy.v1"
    lattice_level: str = "HARD_LOCAL_POLICY"
    hard_deny_always_wins: bool = True
    approval_override_allowed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["hard_denies"] = self.hard_denies.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> HardLocalPolicy:
        hd = HardDenies.from_dict(data.get("hard_denies", {}))
        return cls(
            policy_id=data["policy_id"],
            hard_denies=hd,
            schema=data.get("schema", "solidbit.hard-policy.v1"),
            lattice_level=data.get("lattice_level", "HARD_LOCAL_POLICY"),
            hard_deny_always_wins=data.get("hard_deny_always_wins", True),
            approval_override_allowed=data.get("approval_override_allowed", False),
        )


# ============================================================================
# BOUNDED APPROVAL MODELS
# ============================================================================


@dataclass
class Approver:
    identity: str
    channel: str  # CLI, GMAIL, MANUAL
    approved_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Approver:
        return cls(
            identity=data["identity"],
            channel=data["channel"],
            approved_at=data.get("approved_at"),
        )


@dataclass
class ApprovalToken:
    """Bounded human approval token bound to (job_id, action, scope, request_id, expires_at)."""

    request_id: str
    job_id: str
    action: str
    scope: List[str]
    expires_at: str
    decision: str  # APPROVED, REJECTED, DEFERRED
    approver: Approver
    schema: str = "solidbit.approval.v1"
    run_id: Optional[str] = None
    package_id: Optional[str] = None
    resume_run: bool = True
    cannot_override_hard_deny: bool = True
    created_at: Optional[str] = None
    prohibited_actions: List[str] = field(default_factory=list)
    remaining_blockers: List[str] = field(default_factory=list)
    next_safe_action: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["approver"] = self.approver.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ApprovalToken:
        approver = Approver.from_dict(data["approver"])
        return cls(
            request_id=data["request_id"],
            job_id=data["job_id"],
            action=data["action"],
            scope=list(data["scope"]),
            expires_at=data["expires_at"],
            decision=data["decision"],
            approver=approver,
            schema=data.get("schema", "solidbit.approval.v1"),
            run_id=data.get("run_id"),
            package_id=data.get("package_id"),
            resume_run=data.get("resume_run", True),
            cannot_override_hard_deny=data.get("cannot_override_hard_deny", True),
            created_at=data.get("created_at"),
            prohibited_actions=list(data.get("prohibited_actions", [])),
            remaining_blockers=list(data.get("remaining_blockers", [])),
            next_safe_action=data.get("next_safe_action"),
            notes=data.get("notes"),
        )


# ============================================================================
# EXECUTION PACKAGE MANIFEST MODELS
# ============================================================================


@dataclass
class Manifest:
    """Declarative execution package manifest."""

    package_id: str
    job_id: str
    project: str
    repository: str
    mode: str
    source_orchestrator: str
    target_local_repo: str
    agents: List[str]
    entrypoint: str
    execution_plan: str
    readme: str
    requested_operations: List[str]
    prohibited_actions: List[str]
    expected_outputs: List[str]
    runtime_files: List[str]
    schema: str = "solidbit.execution-package.v1"
    checksums_file: str = "checksums.sha256"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Manifest:
        return cls(
            package_id=data["package_id"],
            job_id=data["job_id"],
            project=data["project"],
            repository=data["repository"],
            mode=data["mode"],
            source_orchestrator=data["source_orchestrator"],
            target_local_repo=data["target_local_repo"],
            agents=list(data["agents"]),
            entrypoint=data["entrypoint"],
            execution_plan=data["execution_plan"],
            readme=data["readme"],
            requested_operations=list(data["requested_operations"]),
            prohibited_actions=list(data["prohibited_actions"]),
            expected_outputs=list(data["expected_outputs"]),
            runtime_files=list(data["runtime_files"]),
            schema=data.get("schema", "solidbit.execution-package.v1"),
            checksums_file=data.get("checksums_file", "checksums.sha256"),
            metadata=dict(data.get("metadata", {})),
        )


# ============================================================================
# OPERATION REGISTRY MODELS
# ============================================================================


@dataclass
class ExecutionProfile:
    timeout_seconds: int
    allow_network: bool
    isolation: str = "readonly"  # worktree, readonly, sandbox, none
    max_memory_mb: Optional[int] = None
    allowed_process_images: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.max_memory_mb is None:
            del d["max_memory_mb"]
        if not self.allowed_process_images:
            del d["allowed_process_images"]
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ExecutionProfile:
        return cls(
            timeout_seconds=data["timeout_seconds"],
            allow_network=data["allow_network"],
            isolation=data.get("isolation", "readonly"),
            max_memory_mb=data.get("max_memory_mb"),
            allowed_process_images=list(data.get("allowed_process_images", [])),
        )


@dataclass
class OperationRegistryEntry:
    operation_id: str
    name: str
    handler_path: str
    handler_type: str  # powershell, binary, builtin, node, python
    handler_sha256: str
    execution_profile: ExecutionProfile
    required_permissions: List[str]
    enabled: bool
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["execution_profile"] = self.execution_profile.to_dict()
        if self.description is None:
            del d["description"]
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> OperationRegistryEntry:
        ep = ExecutionProfile.from_dict(data["execution_profile"])
        return cls(
            operation_id=data["operation_id"],
            name=data["name"],
            handler_path=data["handler_path"],
            handler_type=data["handler_type"],
            handler_sha256=data["handler_sha256"],
            execution_profile=ep,
            required_permissions=list(data.get("required_permissions", [])),
            enabled=data["enabled"],
            description=data.get("description"),
        )


@dataclass
class OperationRegistry:
    registry_id: str
    version: str
    operations: List[OperationRegistryEntry]
    schema: str = "solidbit.operation-registry.v1"
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["operations"] = [op.to_dict() for op in self.operations]
        if self.description is None:
            del d["description"]
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> OperationRegistry:
        ops = [OperationRegistryEntry.from_dict(op) for op in data.get("operations", [])]
        return cls(
            registry_id=data["registry_id"],
            version=data["version"],
            operations=ops,
            schema=data.get("schema", "solidbit.operation-registry.v1"),
            description=data.get("description"),
        )


# ============================================================================
# PROJECT REGISTRY MODELS
# ============================================================================


@dataclass
class ConcurrencyPolicy:
    max_mutating_jobs: int = 1
    allow_concurrent_read_only: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ConcurrencyPolicy:
        return cls(
            max_mutating_jobs=data.get("max_mutating_jobs", 1),
            allow_concurrent_read_only=data.get("allow_concurrent_read_only", True),
        )


@dataclass
class ProjectRegistryEntry:
    project_id: str
    repository: str
    target_local_repo: str
    risk_tier: str
    default_branch: str = "main"
    allowed_worktree_base: Optional[str] = None
    allowed_target_roots: List[str] = field(default_factory=list)
    allow_target_override: bool = False
    concurrency_policy: Optional[ConcurrencyPolicy] = None
    enforce_dirty_root_check: bool = True
    active: bool = True
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.concurrency_policy:
            d["concurrency_policy"] = self.concurrency_policy.to_dict()
        else:
            del d["concurrency_policy"]
        if self.allowed_worktree_base is None:
            del d["allowed_worktree_base"]
        if not self.allowed_target_roots:
            del d["allowed_target_roots"]
        if self.description is None:
            del d["description"]
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ProjectRegistryEntry:
        cp = (
            ConcurrencyPolicy.from_dict(data["concurrency_policy"])
            if "concurrency_policy" in data
            else None
        )
        return cls(
            project_id=data["project_id"],
            repository=data["repository"],
            target_local_repo=data["target_local_repo"],
            risk_tier=data["risk_tier"],
            default_branch=data.get("default_branch", "main"),
            allowed_worktree_base=data.get("allowed_worktree_base"),
            allowed_target_roots=list(data.get("allowed_target_roots", [])),
            allow_target_override=data.get("allow_target_override", False),
            concurrency_policy=cp,
            enforce_dirty_root_check=data.get("enforce_dirty_root_check", True),
            active=data.get("active", True),
            description=data.get("description"),
        )


@dataclass
class ProjectRegistry:
    version: str
    projects: List[ProjectRegistryEntry]
    schema: str = "solidbit.project-registry.v1"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "version": self.version,
            "projects": [p.to_dict() for p in self.projects],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ProjectRegistry:
        projects = [ProjectRegistryEntry.from_dict(p) for p in data.get("projects", [])]
        return cls(
            version=data["version"],
            projects=projects,
            schema=data.get("schema", "solidbit.project-registry.v1"),
        )


# ============================================================================
# PROJECT POLICY MODELS
# ============================================================================


@dataclass
class WorkspaceSafety:
    enforce_clean_root: bool = True
    disallow_main_branch: bool = True
    allow_primary_checkout: bool = False
    allow_hard_reset: bool = False
    allow_auto_stash: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> WorkspaceSafety:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class RuntimeSafety:
    remote_execution_enabled: bool = False
    non_killing_timeout: bool = True
    pid_drift_tolerance_seconds: int = 300
    allowed_process_images: List[str] = field(
        default_factory=lambda: ["agy", "powershell", "pwsh", "cmd", "node", "conhost"]
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RuntimeSafety:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class ProjectPolicy:
    policy_id: str
    permissions: Dict[str, bool]
    workspace_safety: WorkspaceSafety
    runtime_safety: RuntimeSafety
    stop_conditions: Dict[str, List[str]]
    schema: str = "solidbit.policy.v1"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["workspace_safety"] = self.workspace_safety.to_dict()
        d["runtime_safety"] = self.runtime_safety.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ProjectPolicy:
        ws = WorkspaceSafety.from_dict(data["workspace_safety"])
        rs = RuntimeSafety.from_dict(data["runtime_safety"])
        return cls(
            policy_id=data["policy_id"],
            permissions=dict(data["permissions"]),
            workspace_safety=ws,
            runtime_safety=rs,
            stop_conditions=dict(data["stop_conditions"]),
            schema=data.get("schema", "solidbit.policy.v1"),
        )


# ============================================================================
# MAIL ENVELOPE MODELS
# ============================================================================


@dataclass
class RoutingSubject:
    raw_subject: str
    job_id: str
    is_valid_routing_hint: bool
    routing_prefix: str = "[SACL][JOB][v1]"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RoutingSubject:
        return cls(
            raw_subject=data["raw_subject"],
            job_id=data["job_id"],
            is_valid_routing_hint=data["is_valid_routing_hint"],
            routing_prefix=data.get("routing_prefix", "[SACL][JOB][v1]"),
        )


@dataclass
class AttachmentMetadata:
    filename: str
    size_bytes: int
    sha256: str
    mime_type: str = "application/zip"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AttachmentMetadata:
        return cls(
            filename=data["filename"],
            size_bytes=data["size_bytes"],
            sha256=data["sha256"],
            mime_type=data.get("mime_type", "application/zip"),
        )


@dataclass
class MailEnvelope:
    message_id: str
    direction: str  # INBOUND, OUTBOUND
    sender: str
    recipient: str
    routing_subject: RoutingSubject
    timestamp: str
    nonce: str
    attachment: AttachmentMetadata
    status: str
    schema: str = "solidbit.mail-envelope.v1"
    history_id: Optional[str] = None
    thread_id: Optional[str] = None
    delivery_semantics: str = "AT_LEAST_ONCE"
    signature_hmac: Optional[str] = None
    rejection_reason: Optional[str] = None
    run_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["routing_subject"] = self.routing_subject.to_dict()
        d["attachment"] = self.attachment.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MailEnvelope:
        rs = RoutingSubject.from_dict(data["routing_subject"])
        att = AttachmentMetadata.from_dict(data["attachment"])
        return cls(
            message_id=data["message_id"],
            direction=data["direction"],
            sender=data["sender"],
            recipient=data["recipient"],
            routing_subject=rs,
            timestamp=data["timestamp"],
            nonce=data["nonce"],
            attachment=att,
            status=data["status"],
            schema=data.get("schema", "solidbit.mail-envelope.v1"),
            history_id=data.get("history_id"),
            thread_id=data.get("thread_id"),
            delivery_semantics=data.get("delivery_semantics", "AT_LEAST_ONCE"),
            signature_hmac=data.get("signature_hmac"),
            rejection_reason=data.get("rejection_reason"),
            run_id=data.get("run_id"),
        )


# ============================================================================
# GRAPH-H DAG MODELS
# ============================================================================


@dataclass
class GraphPhase:
    phase_number: int
    stage_name: str
    agents: List[str]
    gate_required: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GraphPhase:
        return cls(
            phase_number=data["phase_number"],
            stage_name=data["stage_name"],
            agents=list(data["agents"]),
            gate_required=data.get("gate_required", False),
        )


@dataclass
class GraphNode:
    node_id: str
    agent_id: str
    phase_number: int
    timeout_minutes: Optional[int] = None
    max_attempts: int = 1
    gate_required: bool = False
    allowed_states: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.timeout_minutes is None:
            del d["timeout_minutes"]
        if not self.allowed_states:
            del d["allowed_states"]
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GraphNode:
        return cls(
            node_id=data["node_id"],
            agent_id=data["agent_id"],
            phase_number=data["phase_number"],
            timeout_minutes=data.get("timeout_minutes"),
            max_attempts=data.get("max_attempts", 1),
            gate_required=data.get("gate_required", False),
            allowed_states=list(data.get("allowed_states", [])),
        )


@dataclass
class ExecutionGraph:
    graph_id: str
    max_parallel: int
    default_timeout_minutes: int
    phases: List[GraphPhase]
    edges: List[List[str]]
    failure_policy: str  # abort_immediately, complete_stage_then_halt, continue_independent
    schema: str = "solidbit.execution-graph.v1"
    job_id: Optional[str] = None
    nodes: List[GraphNode] = field(default_factory=list)
    agent_timeouts: Dict[str, int] = field(default_factory=dict)
    collision_detection: Dict[str, Any] = field(
        default_factory=lambda: {"enabled": True, "scope": "stage"}
    )

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["phases"] = [p.to_dict() for p in self.phases]
        if self.nodes:
            d["nodes"] = [n.to_dict() for n in self.nodes]
        else:
            del d["nodes"]
        if self.job_id is None:
            del d["job_id"]
        if not self.agent_timeouts:
            del d["agent_timeouts"]
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ExecutionGraph:
        phases = [GraphPhase.from_dict(p) for p in data["phases"]]
        nodes = [GraphNode.from_dict(n) for n in data.get("nodes", [])]
        return cls(
            graph_id=data["graph_id"],
            max_parallel=data["max_parallel"],
            default_timeout_minutes=data["default_timeout_minutes"],
            phases=phases,
            edges=[list(e) for e in data["edges"]],
            failure_policy=data["failure_policy"],
            schema=data.get("schema", "solidbit.execution-graph.v1"),
            job_id=data.get("job_id"),
            nodes=nodes,
            agent_timeouts=dict(data.get("agent_timeouts", {})),
            collision_detection=dict(
                data.get("collision_detection", {"enabled": True, "scope": "stage"})
            ),
        )


# ============================================================================
# RECONCILIATION & RESULT MODELS
# ============================================================================


@dataclass
class ProcessObservation:
    is_active: bool
    process_name: str
    pid: Optional[int] = None
    start_time_drift_seconds: Optional[float] = None
    exit_code: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ProcessObservation:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class PersistedState:
    status: str
    started_at: Optional[str] = None
    updated_at: Optional[str] = None
    finished_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PersistedState:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class RequiredOutputs:
    report_path: str
    report_exists: bool
    report_size_bytes: int
    stdout_path: str
    stderr_path: str
    expected_files_verified: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RequiredOutputs:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class VerdictExtraction:
    verdict: str
    extraction_method: str
    matched_marker: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> VerdictExtraction:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class WorktreeState:
    branch: str
    worktree_path: str
    commit_sha: Optional[str] = None
    is_clean: bool = True
    modified_files: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> WorktreeState:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class ReconciliationData:
    process_observation: ProcessObservation
    persisted_state: PersistedState
    required_outputs: RequiredOutputs
    verdict_extraction: VerdictExtraction

    def to_dict(self) -> Dict[str, Any]:
        return {
            "process_observation": self.process_observation.to_dict(),
            "persisted_state": self.persisted_state.to_dict(),
            "required_outputs": self.required_outputs.to_dict(),
            "verdict_extraction": self.verdict_extraction.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ReconciliationData:
        return cls(
            process_observation=ProcessObservation.from_dict(data["process_observation"]),
            persisted_state=PersistedState.from_dict(data["persisted_state"]),
            required_outputs=RequiredOutputs.from_dict(data["required_outputs"]),
            verdict_extraction=VerdictExtraction.from_dict(data["verdict_extraction"]),
        )


@dataclass
class ReconciledResult:
    run_id: str
    agent_id: str
    status: str
    result_verdict: str
    reconciliation: ReconciliationData
    worktree: WorktreeState
    schema: str = "solidbit.result.v1"
    job_id: Optional[str] = None
    node_id: Optional[str] = None
    stage_id: Optional[Any] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["reconciliation"] = self.reconciliation.to_dict()
        d["worktree"] = self.worktree.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ReconciledResult:
        recon = ReconciliationData.from_dict(data["reconciliation"])
        wt = WorktreeState.from_dict(data["worktree"])
        return cls(
            run_id=data["run_id"],
            agent_id=data["agent_id"],
            status=data["status"],
            result_verdict=data["result_verdict"],
            reconciliation=recon,
            worktree=wt,
            schema=data.get("schema", "solidbit.result.v1"),
            job_id=data.get("job_id"),
            node_id=data.get("node_id"),
            stage_id=data.get("stage_id"),
            error_message=data.get("error_message"),
        )


# ============================================================================
# UNIVERSAL SUMMARY MODELS
# ============================================================================


@dataclass
class AgentResult:
    agent: str
    status: str
    verdict: str
    reportExists: bool
    exitCode: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AgentResult:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class RunSummary:
    """Universal summary schema for SACL V1 execution runs."""

    run_id: str
    package_id: str
    project: str
    status: str
    architecture_freeze_ready: bool
    implementation_authorized: bool
    open_contradictions: int
    security_critical_unknowns: int
    ready_for_integration: str  # YES, NO
    agent_results: List[AgentResult]
    conflicting_files: List[str]
    documents_created: List[str]
    adrs_created: List[str]
    schemas_created: List[str]
    compatibility_findings: List[str]
    next_safe_action: str
    schema: str = "solidbit.run-summary.v1"
    job_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["agent_results"] = [ar.to_dict() for ar in self.agent_results]
        if self.job_id is None:
            del d["job_id"]
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RunSummary:
        results = [AgentResult.from_dict(ar) for ar in data.get("agent_results", [])]
        return cls(
            run_id=data["run_id"],
            package_id=data["package_id"],
            project=data["project"],
            status=data["status"],
            architecture_freeze_ready=data["architecture_freeze_ready"],
            implementation_authorized=data["implementation_authorized"],
            open_contradictions=data["open_contradictions"],
            security_critical_unknowns=data["security_critical_unknowns"],
            ready_for_integration=data["ready_for_integration"],
            agent_results=results,
            conflicting_files=list(data.get("conflicting_files", [])),
            documents_created=list(data.get("documents_created", [])),
            adrs_created=list(data.get("adrs_created", [])),
            schemas_created=list(data.get("schemas_created", [])),
            compatibility_findings=list(data.get("compatibility_findings", [])),
            next_safe_action=data["next_safe_action"],
            schema=data.get("schema", "solidbit.run-summary.v1"),
            job_id=data.get("job_id"),
        )


# ============================================================================
# AUDIT, LEASE, HEARTBEAT, AND ERROR MODELS
# ============================================================================


@dataclass
class AuditEvent:
    event_type: str
    severity: str  # DEBUG, INFO, WARN, ERROR, FATAL
    payload: Dict[str, Any]
    created_at: str
    event_id: Optional[int] = None
    job_id: Optional[str] = None
    run_id: Optional[str] = None
    node_id: Optional[str] = None
    agent_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LeaseRecord:
    lease_name: str
    holder_id: str
    holder_pid: int
    acquired_at: str
    heartbeat_at: str
    expires_at: str
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HeartbeatRecord:
    component: str
    instance_id: str
    pid: int
    status: str
    last_seen_at: str
    heartbeat_id: Optional[int] = None
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ErrorRecord:
    error_code: str
    category: str
    severity: str
    message: str
    occurred_at: str
    error_id: Optional[int] = None
    job_id: Optional[str] = None
    run_id: Optional[str] = None
    node_id: Optional[str] = None
    agent_id: Optional[str] = None
    stack_trace: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

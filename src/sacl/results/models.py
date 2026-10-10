"""SACL V1 Results and Deliverables Data Models.

Defines structures for:
- 4-Point reconciliation outcomes
- Cross-agent file modification overlap and conflict reports
- Sealed result packages
- Outbox delivery handoff results
- Universal run summaries
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from sacl.contracts.invariants import Verdict
from sacl.contracts.models import (
    AgentResult,
    PersistedState,
    ProcessObservation,
    ReconciledResult,
    ReconciliationData,
    RequiredOutputs,
    RunSummary,
    VerdictExtraction,
    WorktreeState,
)


@dataclass
class CollisionRecord:
    """Record of a single conflicting file modified by multiple agents."""

    file_path: str
    agents: List[str]
    agent_count: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CollisionReport:
    """Evaluation report of cross-agent file modifications and collisions."""

    run_id: str
    conflicting_files: List[str]
    conflicts_by_file: Dict[str, List[str]]
    ready_for_integration: str  # 'YES' | 'NO'
    blockers: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PackagedResult:
    """Sealed result ZIP bundle metadata."""

    run_id: str
    job_id: str
    zip_path: Path
    file_size_bytes: int
    sha256_hash: str
    summary_md_path: Path
    summary_json_path: Path
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["zip_path"] = str(self.zip_path)
        d["summary_md_path"] = str(self.summary_md_path)
        d["summary_json_path"] = str(self.summary_json_path)
        return d


@dataclass
class OutboxHandoffResult:
    """Outcome of enqueuing/dispatching result to the transport outbox."""

    outbox_id: int
    run_id: str
    recipient: str
    subject: str
    status: str  # 'QUEUED', 'SENT', 'FAILED'
    dispatched: bool
    dispatched_at: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RunCollectionResult:
    """Aggregated outcome of reconciling all agents in a run attempt."""

    run_id: str
    job_id: str
    overall_verdict: str
    agent_results: List[ReconciledResult]
    collision_report: CollisionReport
    ready_for_integration: str
    artifacts_collected: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["agent_results"] = [ar.to_dict() for ar in self.agent_results]
        d["collision_report"] = self.collision_report.to_dict()
        return d


__all__ = [
    "CollisionRecord",
    "CollisionReport",
    "PackagedResult",
    "OutboxHandoffResult",
    "RunCollectionResult",
    "Verdict",
    "ReconciledResult",
    "ReconciliationData",
    "ProcessObservation",
    "PersistedState",
    "RequiredOutputs",
    "VerdictExtraction",
    "WorktreeState",
    "RunSummary",
    "AgentResult",
]

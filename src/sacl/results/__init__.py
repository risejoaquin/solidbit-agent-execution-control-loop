"""SACL V1 Results, Reconciliation, Packaging, and Outbox Subsystem.

Enforces:
- 4-Dimensional Canonical Run Status Reconciliation (RESULT_PROTOCOL.md)
- Cross-Agent File Overlap and Collision Gating
- Dual Deliverable Summary Contracts (SUMMARY.md and SUMMARY.json)
- Result Packaging into Sealed Response ZIP Bundles
- Result Outbox Queue Handoff and Asynchronous Transport Dispatch
"""

from sacl.results.collector import ResultCollector
from sacl.results.collision import CollisionDetector, normalize_file_path
from sacl.results.models import (
    AgentResult,
    CollisionRecord,
    CollisionReport,
    OutboxHandoffResult,
    PackagedResult,
    PersistedState,
    ProcessObservation,
    ReconciledResult,
    ReconciliationData,
    RequiredOutputs,
    RunCollectionResult,
    RunSummary,
    Verdict,
    VerdictExtraction,
    WorktreeState,
)
from sacl.results.outbox import (
    DEFAULT_RESULT_RECIPIENT,
    ResultOutboxHandoff,
    format_result_subject,
)
from sacl.results.packager import ResultPackager, sanitize_archive_entry_path
from sacl.results.reconciler import ResultReconciler, REVIEW_REQUIRED_REGEX
from sacl.results.summary import DualSummaryGenerator

__all__ = [
    # Models
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
    # Reconciler
    "ResultReconciler",
    "REVIEW_REQUIRED_REGEX",
    # Collision
    "CollisionDetector",
    "normalize_file_path",
    # Collector
    "ResultCollector",
    # Summary
    "DualSummaryGenerator",
    # Packager
    "ResultPackager",
    "sanitize_archive_entry_path",
    # Outbox
    "ResultOutboxHandoff",
    "format_result_subject",
    "DEFAULT_RESULT_RECIPIENT",
]

"""SolidBit Agent Execution Control Loop (SACL V1).

A sovereign, deterministic multi-agent execution control loop for Windows/host systems.
"""

from sacl.contracts.invariants import (
    ApprovalChannel,
    ApprovalDecision,
    ApprovalStatus,
    ArtifactType,
    ExecutionMode,
    GraphNodeStatus,
    JobSideStatus,
    JobStatus,
    OperationalStateDomain,
    Verdict,
)

__version__ = "0.1.0"
__author__ = "SolidBit Core Team"

__all__ = [
    "__version__",
    "__author__",
    "JobStatus",
    "JobSideStatus",
    "GraphNodeStatus",
    "Verdict",
    "ApprovalChannel",
    "ApprovalDecision",
    "ApprovalStatus",
    "OperationalStateDomain",
    "ArtifactType",
    "ExecutionMode",
]

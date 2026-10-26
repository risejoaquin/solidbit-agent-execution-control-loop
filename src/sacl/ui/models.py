"""SACL V1 UI Data Models.

Defines point-in-time consolidated view models for the Apple-grade
Decision Shell and Dashboard, adhering to docs/SCREEN_BY_SCREEN_SPEC.md
and docs/UI_UX_SPEC_DEEP.md.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def resolve_safe_path(p_str: Union[str, Path, None]) -> Path:
    """Safely resolves filesystem paths expanding ~ and normalizing cross-platform separators."""
    if not p_str:
        return Path.cwd().resolve()
    s = str(p_str).strip()
    s = s.replace('/', os.sep).replace('\\', os.sep)
    expanded = os.path.expanduser(s)
    if expanded.startswith('~'):
        expanded = str(Path.home() / expanded.lstrip('~\\/'))
    return Path(expanded).resolve()



class UIMode(str, Enum):
    """User experience mode for the SACL control shell."""

    SIMPLE = "simple"
    TECHNICAL = "technical"
    AUDIT = "audit"


class ConnectionState(str, Enum):
    """Health state of external CLI or service connection."""

    CONNECTED = "connected"
    DEGRADED = "degraded"
    DISCONNECTED = "disconnected"
    UNAUTHENTICATED = "unauthenticated"


@dataclass
class TechnologyConnection:
    """Readiness and health status for an external tool or CLI."""

    id: str
    name: str
    category: str  # e.g. "vcs", "infra", "database", "governance", "runtime"
    status: ConnectionState
    version: Optional[str] = None
    account_info: Optional[str] = None
    last_checked: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d


@dataclass
class HumanGateCard:
    """Micro-decision card for human-in-the-loop governance gates."""

    approval_id: str
    request_id: str
    job_id: str
    run_id: Optional[str]
    action: str
    scope: str
    risk_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    status: str      # "PENDING", "APPROVED", "REJECTED", "EXPIRED"
    reason: str
    evidence_summary: str
    created_at: str
    expires_at: str
    can_decide: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SafetyBoundaryStatus:
    """Constitutional safety boundary display model."""

    production_allowed: bool = False
    deploy_allowed: bool = False
    merge_allowed: bool = False
    destructive_git_allowed: bool = False
    ruleset_protected: bool = True
    dirty_root_prevented: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RecoverySummaryView:
    """Status of crash detection and safe resume capability."""

    interrupted_runs_count: int = 0
    latest_run_id: Optional[str] = None
    classification: str = "CLEAN"
    safe_to_resume: bool = True
    recommended_action: str = "Ready for execution"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FullDashboardView:
    """Root model backing the entire Decision Shell interface."""

    readiness_score: int
    active_project: str
    active_campaign: Optional[str]
    mode: str
    safety: SafetyBoundaryStatus
    connections: List[TechnologyConnection]
    pending_gates: List[HumanGateCard]
    agents: List[Dict[str, Any]]
    leases: List[Dict[str, Any]]
    recovery: RecoverySummaryView
    alerts: List[str]
    recent_events: List[Dict[str, Any]]
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "readiness_score": self.readiness_score,
            "active_project": self.active_project,
            "active_campaign": self.active_campaign,
            "mode": self.mode,
            "safety": self.safety.to_dict(),
            "connections": [c.to_dict() for c in self.connections],
            "pending_gates": [g.to_dict() for g in self.pending_gates],
            "agents": self.agents,
            "leases": self.leases,
            "recovery": self.recovery.to_dict(),
            "alerts": self.alerts,
            "recent_events": self.recent_events,
            "timestamp": self.timestamp,
        }

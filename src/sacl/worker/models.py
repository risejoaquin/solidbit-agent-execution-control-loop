"""SACL V1 Worker Data Models.

Defines typed configurations, attempt records, and lifecycle states for
individual agent worker processes executing inside isolated worktrees.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple


@dataclass
class ProcessIdentity:
    """Captured OS process metadata for 3-way PID recycling defense."""

    pid: Optional[int]
    process_name: str
    started_at: Optional[datetime] = None
    is_active: bool = False
    exit_code: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.started_at:
            d["started_at"] = self.started_at.isoformat()
        return d


@dataclass
class WorkerAttemptRecord:
    """Execution history for a single worker attempt on a graph node."""

    attempt_number: int
    started_at: str
    stdout_path: str
    stderr_path: str
    report_path: str
    pid: Optional[int] = None
    process_name: str = "agy"
    status: str = "RUNNING"
    exit_code: Optional[int] = None
    finished_at: Optional[str] = None
    verdict: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> WorkerAttemptRecord:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class WorkerConfig:
    """Configuration for an isolated agent worker execution."""

    agent_id: str
    run_id: str
    worktree_path: Path
    prompt_path: Path
    report_path: Path
    stdout_path: Path
    stderr_path: Path
    job_id: Optional[str] = None
    node_id: Optional[str] = None
    phase_number: int = 1
    stage_name: str = "PHASE_1"
    branch: Optional[str] = None
    timeout_seconds: int = 1800
    max_attempts: int = 1
    executable_command: Optional[List[str]] = None
    env_overrides: Dict[str, str] = field(default_factory=dict)
    run_dir: Optional[Path] = None
    # Optional execution hook or mock runner for deterministic testing
    mock_runner: Optional[Callable[[WorkerConfig, int], Tuple[int, Optional[str]]]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "job_id": self.job_id,
            "node_id": self.node_id,
            "phase_number": self.phase_number,
            "stage_name": self.stage_name,
            "branch": self.branch,
            "timeout_seconds": self.timeout_seconds,
            "max_attempts": self.max_attempts,
            "worktree_path": str(self.worktree_path),
            "prompt_path": str(self.prompt_path),
            "report_path": str(self.report_path),
            "stdout_path": str(self.stdout_path),
            "stderr_path": str(self.stderr_path),
            "executable_command": self.executable_command,
            "run_dir": str(self.run_dir) if self.run_dir else None,
        }

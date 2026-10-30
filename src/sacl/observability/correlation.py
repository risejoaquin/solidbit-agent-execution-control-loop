"""SACL V1 Correlation ID and Execution Context Management.

Provides thread-safe and asynchronous-safe propagation of correlation IDs,
trace IDs, and hierarchical execution context (job, run, node, agent).
"""

from __future__ import annotations

import contextvars
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Dict, Generator, Optional


def generate_trace_id() -> str:
    """Generates a standard 32-character hexadecimal trace ID."""
    return uuid.uuid4().hex


def generate_correlation_id(prefix: str = "corr-") -> str:
    """Generates a prefixed unique correlation token."""
    return f"{prefix}{uuid.uuid4().hex[:12]}"


@dataclass
class CorrelationContext:
    """Immutable or semi-mutable snapshot of active execution correlation.

    Propagates across system boundaries, mail messages, supervisor dispatches,
    worker tasks, and log records.
    """

    trace_id: str = field(default_factory=generate_trace_id)
    job_id: Optional[str] = None
    run_id: Optional[str] = None
    node_id: Optional[str] = None
    agent_id: Optional[str] = None
    parent_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes correlation context to a dictionary."""
        d: Dict[str, Any] = {
            "trace_id": self.trace_id,
        }
        if self.job_id is not None:
            d["job_id"] = self.job_id
        if self.run_id is not None:
            d["run_id"] = self.run_id
        if self.node_id is not None:
            d["node_id"] = self.node_id
        if self.agent_id is not None:
            d["agent_id"] = self.agent_id
        if self.parent_id is not None:
            d["parent_id"] = self.parent_id
        if self.metadata:
            d["metadata"] = dict(self.metadata)
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CorrelationContext:
        """Constructs a CorrelationContext from a dictionary."""
        return cls(
            trace_id=data.get("trace_id") or generate_trace_id(),
            job_id=data.get("job_id"),
            run_id=data.get("run_id"),
            node_id=data.get("node_id"),
            agent_id=data.get("agent_id"),
            parent_id=data.get("parent_id"),
            metadata=dict(data.get("metadata", {})),
        )

    def to_headers(self, prefix: str = "X-SACL-") -> Dict[str, str]:
        """Serializes correlation fields into transport headers."""
        headers: Dict[str, str] = {
            f"{prefix}Trace-Id": self.trace_id,
        }
        if self.job_id:
            headers[f"{prefix}Job-Id"] = self.job_id
        if self.run_id:
            headers[f"{prefix}Run-Id"] = self.run_id
        if self.node_id:
            headers[f"{prefix}Node-Id"] = self.node_id
        if self.agent_id:
            headers[f"{prefix}Agent-Id"] = self.agent_id
        if self.parent_id:
            headers[f"{prefix}Parent-Id"] = self.parent_id
        return headers

    @classmethod
    def from_headers(cls, headers: Dict[str, str], prefix: str = "X-SACL-") -> CorrelationContext:
        """Extracts correlation context from case-insensitive transport headers."""
        norm = {k.lower(): v for k, v in headers.items()}
        pref = prefix.lower()

        trace_id = (
            norm.get(f"{pref}trace-id") or norm.get("x-correlation-id") or generate_trace_id()
        )
        job_id = norm.get(f"{pref}job-id")
        run_id = norm.get(f"{pref}run-id")
        node_id = norm.get(f"{pref}node-id")
        agent_id = norm.get(f"{pref}agent-id")
        parent_id = norm.get(f"{pref}parent-id")

        return cls(
            trace_id=trace_id,
            job_id=job_id,
            run_id=run_id,
            node_id=node_id,
            agent_id=agent_id,
            parent_id=parent_id,
        )

    def derive_child(
        self,
        node_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CorrelationContext:
        """Derives a child correlation context preserving the root trace and run IDs."""
        child_meta = dict(self.metadata)
        if metadata:
            child_meta.update(metadata)

        return CorrelationContext(
            trace_id=self.trace_id,
            job_id=self.job_id,
            run_id=self.run_id,
            node_id=node_id if node_id is not None else self.node_id,
            agent_id=agent_id if agent_id is not None else self.agent_id,
            parent_id=self.node_id or self.agent_id or self.run_id,
            metadata=child_meta,
        )


_CORRELATION_VAR: contextvars.ContextVar[Optional[CorrelationContext]] = contextvars.ContextVar(
    "sacl_correlation_context", default=None
)


def get_current_correlation() -> CorrelationContext:
    """Returns the current active correlation context or creates a default one."""
    ctx = _CORRELATION_VAR.get()
    if ctx is None:
        ctx = CorrelationContext()
        _CORRELATION_VAR.set(ctx)
    return ctx


def set_current_correlation(ctx: CorrelationContext) -> contextvars.Token:
    """Sets the active correlation context, returning the reset token."""
    return _CORRELATION_VAR.set(ctx)


def reset_current_correlation(token: contextvars.Token) -> None:
    """Resets the correlation context using a previously returned token."""
    _CORRELATION_VAR.reset(token)


def clear_current_correlation() -> None:
    """Clears the active correlation context."""
    _CORRELATION_VAR.set(None)


@contextmanager
def correlation_scope(
    trace_id: Optional[str] = None,
    job_id: Optional[str] = None,
    run_id: Optional[str] = None,
    node_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    parent_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Generator[CorrelationContext, None, None]:
    """Scoped context manager for correlation context propagation.

    Inherits unset fields from the current context and restores the prior
    context upon exiting the block, even if an exception is raised.
    """
    parent = _CORRELATION_VAR.get()

    active_trace = trace_id or (parent.trace_id if parent else generate_trace_id())
    active_job = job_id if job_id is not None else (parent.job_id if parent else None)
    active_run = run_id if run_id is not None else (parent.run_id if parent else None)
    active_node = node_id if node_id is not None else (parent.node_id if parent else None)
    active_agent = agent_id if agent_id is not None else (parent.agent_id if parent else None)
    active_parent = parent_id if parent_id is not None else (parent.parent_id if parent else None)

    active_meta = dict(parent.metadata) if parent else {}
    if metadata:
        active_meta.update(metadata)

    new_ctx = CorrelationContext(
        trace_id=active_trace,
        job_id=active_job,
        run_id=active_run,
        node_id=active_node,
        agent_id=active_agent,
        parent_id=active_parent,
        metadata=active_meta,
    )

    token = _CORRELATION_VAR.set(new_ctx)
    try:
        yield new_ctx
    finally:
        _CORRELATION_VAR.reset(token)

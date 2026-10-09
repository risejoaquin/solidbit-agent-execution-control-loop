"""SACL V1 Dynamic Worker Concurrency Throttling.

Implements pool concurrency throttling from CONCURRENCY_AND_LOCKING.md §5.2:
Limits the number of simultaneously active worker processes to $MaxParallel
(default 3, range 1-16) to prevent host memory exhaustion and process starvation.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Set

from sacl.contracts.exceptions import ContractValidationError


class DynamicConcurrencyPool:
    """Manages dynamic concurrency slot allocation and throttling."""

    def __init__(self, max_parallel: int = 3) -> None:
        self._set_max_parallel_internal(max_parallel)
        self.active_slots: Set[str] = set()

    def _set_max_parallel_internal(self, limit: int) -> None:
        if limit < 1 or limit > 16:
            raise ContractValidationError(
                "solidbit.execution-graph.v1",
                f"max_parallel must be between 1 and 16, got {limit}",
            )
        self.max_parallel = limit

    def set_max_parallel(self, limit: int) -> None:
        """Dynamically adjusts max parallel capacity during execution."""
        self._set_max_parallel_internal(limit)

    @property
    def available_slots(self) -> int:
        """Returns the number of available concurrency slots."""
        return max(0, self.max_parallel - len(self.active_slots))

    @property
    def is_full(self) -> bool:
        """Returns True if the pool has reached maximum concurrency."""
        return len(self.active_slots) >= self.max_parallel

    def acquire_slot(self, node_id: str) -> bool:
        """Attempts to acquire an execution slot for a worker node."""
        if self.is_full:
            return False
        self.active_slots.add(node_id)
        return True

    def release_slot(self, node_id: str) -> None:
        """Releases an execution slot when a worker terminates."""
        self.active_slots.discard(node_id)

    def active_count(self) -> int:
        """Returns count of active workers holding concurrency slots."""
        return len(self.active_slots)

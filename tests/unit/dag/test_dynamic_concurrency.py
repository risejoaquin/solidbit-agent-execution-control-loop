"""Tests for Dynamic Worker Concurrency Throttling ($MaxParallel)."""

from __future__ import annotations

import pytest

from sacl.contracts.exceptions import ContractValidationError
from sacl.dag.concurrency import DynamicConcurrencyPool


def test_concurrency_pool_limits_and_slots():
    pool = DynamicConcurrencyPool(max_parallel=2)
    assert pool.max_parallel == 2
    assert pool.available_slots == 2
    assert pool.is_full is False

    # Acquire 1
    assert pool.acquire_slot("node-1") is True
    assert pool.available_slots == 1
    assert pool.is_full is False

    # Acquire 2
    assert pool.acquire_slot("node-2") is True
    assert pool.available_slots == 0
    assert pool.is_full is True

    # Acquire 3 (Exceeds capacity -> rejected)
    assert pool.acquire_slot("node-3") is False

    # Release 1
    pool.release_slot("node-1")
    assert pool.available_slots == 1
    assert pool.is_full is False

    # Now node-3 can acquire
    assert pool.acquire_slot("node-3") is True
    assert pool.is_full is True


def test_dynamic_capacity_adjustment():
    pool = DynamicConcurrencyPool(max_parallel=2)
    pool.acquire_slot("node-1")
    pool.acquire_slot("node-2")
    assert pool.is_full is True

    # Scale up dynamically to 4
    pool.set_max_parallel(4)
    assert pool.max_parallel == 4
    assert pool.available_slots == 2
    assert pool.is_full is False

    assert pool.acquire_slot("node-3") is True
    assert pool.acquire_slot("node-4") is True
    assert pool.is_full is True


def test_invalid_max_parallel_raises():
    with pytest.raises(ContractValidationError):
        DynamicConcurrencyPool(max_parallel=0)

    with pytest.raises(ContractValidationError):
        DynamicConcurrencyPool(max_parallel=17)

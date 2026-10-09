"""Tests for worker process lifecycle, 3-way PID recycling defense, and safe-stop protocol."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from sacl.contracts.invariants import AgentStatus, Verdict
from sacl.worker.process import (
    MockProcessInspector,
    safe_stop_agent_process,
    verify_agent_process_running,
)


def test_verify_process_running_valid():
    inspector = MockProcessInspector()
    now = datetime.now(timezone.utc)
    inspector.register_process(pid=4820, process_name="agy", start_time=now, is_running=True)

    is_running, reason, drift, name = verify_agent_process_running(
        pid=4820,
        expected_start_time=now,
        inspector=inspector,
    )
    assert is_running is True
    assert reason == "VERIFIED_RUNNING"
    assert name == "agy"
    assert drift is not None
    assert drift < 1.0


def test_verify_process_not_found():
    inspector = MockProcessInspector()
    is_running, reason, _, _ = verify_agent_process_running(
        pid=9999,
        expected_start_time=datetime.now(timezone.utc),
        inspector=inspector,
    )
    assert is_running is False
    assert reason == "PROCESS_NOT_FOUND"


def test_verify_process_image_whitelist_rejection():
    inspector = MockProcessInspector()
    now = datetime.now(timezone.utc)
    # Recycled PID assigned to unwhitelisted process (e.g. chrome or explorer)
    inspector.register_process(pid=4820, process_name="chrome", start_time=now, is_running=True)

    is_running, reason, _, name = verify_agent_process_running(
        pid=4820,
        expected_start_time=now,
        inspector=inspector,
    )
    assert is_running is False
    assert reason == "PROCESS_NAME_MISMATCH_RECYCLED"
    assert name == "chrome"


def test_verify_process_start_time_drift_rejection():
    inspector = MockProcessInspector()
    record_time = datetime.now(timezone.utc)
    # OS process started 400 seconds later (recycled PID)
    actual_time = record_time + timedelta(seconds=400)
    inspector.register_process(pid=4820, process_name="agy", start_time=actual_time, is_running=True)

    is_running, reason, drift, _ = verify_agent_process_running(
        pid=4820,
        expected_start_time=record_time,
        inspector=inspector,
    )
    assert is_running is False
    assert reason == "START_TIME_MISMATCH_RECYCLED"
    assert drift is not None
    assert drift >= 400.0


def test_safe_stop_verified_process_success():
    inspector = MockProcessInspector()
    now = datetime.now(timezone.utc)
    inspector.register_process(pid=4820, process_name="agy", start_time=now, is_running=True)

    success, code, details = safe_stop_agent_process(
        pid=4820,
        expected_start_time=now,
        inspector=inspector,
    )
    assert success is True
    assert code == "STOPPED_BY_USER"
    assert details["terminated"] is True
    assert inspector.is_process_running(4820) is False


def test_safe_stop_already_dead_process():
    inspector = MockProcessInspector()
    success, code, details = safe_stop_agent_process(
        pid=8888,
        expected_start_time=datetime.now(timezone.utc),
        inspector=inspector,
    )
    assert success is True
    assert code == "ALREADY_DEAD"


def test_safe_stop_safety_refusal_on_image_mismatch():
    inspector = MockProcessInspector()
    now = datetime.now(timezone.utc)
    inspector.register_process(pid=4820, process_name="explorer", start_time=now, is_running=True)

    success, code, details = safe_stop_agent_process(
        pid=4820,
        expected_start_time=now,
        inspector=inspector,
    )
    # SAFETY REFUSAL: Refuse to kill unrelated OS process!
    assert success is False
    assert code == "SAFETY_REFUSAL_NAME"
    assert details["safety_refusal"] is True
    # Host process must be unmolested!
    assert inspector.is_process_running(4820) is True


def test_safe_stop_safety_refusal_on_drift_mismatch():
    inspector = MockProcessInspector()
    record_time = datetime.now(timezone.utc)
    actual_time = record_time + timedelta(seconds=350)
    inspector.register_process(pid=4820, process_name="powershell", start_time=actual_time, is_running=True)

    success, code, details = safe_stop_agent_process(
        pid=4820,
        expected_start_time=record_time,
        inspector=inspector,
    )
    assert success is False
    assert code == "SAFETY_REFUSAL_DRIFT"
    assert details["safety_refusal"] is True
    assert inspector.is_process_running(4820) is True

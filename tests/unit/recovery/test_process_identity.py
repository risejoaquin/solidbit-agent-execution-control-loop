"""Unit tests for SACL V1 Process Identity and PID Recycling Protection."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from sacl.contracts.invariants import ALLOWED_PROCESS_IMAGES, PID_DRIFT_TOLERANCE_SECONDS
from sacl.recovery.process_identity import (
    MockProcessInspector,
    ProcessInspectionStatus,
    inspect_process,
    test_agent_process_running,
)


@pytest.fixture
def base_time() -> datetime:
    return datetime(2026, 10, 7, 12, 0, 0, tzinfo=timezone.utc)


def test_process_alive_and_valid_whitelisted(base_time: datetime) -> None:
    """Active process with matching start time and whitelisted image is ALIVE_VALID."""
    inspector = MockProcessInspector()
    inspector.register_process(
        pid=1234,
        process_name="pwsh.exe",
        is_active=True,
        start_time=base_time + timedelta(seconds=5),
    )

    res = inspect_process(
        pid=1234,
        persisted_start_time=base_time,
        inspector=inspector,
    )

    assert res.status == ProcessInspectionStatus.ALIVE_VALID
    assert res.is_valid is True
    assert res.is_alive is True
    assert res.is_recycled is False
    assert (
        test_agent_process_running(1234, persisted_start_time=base_time, inspector=inspector)
        is True
    )


def test_process_all_whitelisted_images_succeed(base_time: datetime) -> None:
    """All 9 whitelisted images succeed."""
    inspector = MockProcessInspector()
    for idx, img in enumerate(ALLOWED_PROCESS_IMAGES, start=2000):
        inspector.register_process(
            pid=idx,
            process_name=img,
            is_active=True,
            start_time=base_time,
        )
        res = inspect_process(pid=idx, persisted_start_time=base_time, inspector=inspector)
        assert res.status == ProcessInspectionStatus.ALIVE_VALID
        assert res.is_valid is True


def test_process_disallowed_image_rejected(base_time: datetime) -> None:
    """Non-whitelisted image binary is detected as DISALLOWED_IMAGE."""
    inspector = MockProcessInspector()
    inspector.register_process(
        pid=5555,
        process_name="calc.exe",
        is_active=True,
        start_time=base_time,
    )

    res = inspect_process(pid=5555, persisted_start_time=base_time, inspector=inspector)
    assert res.status == ProcessInspectionStatus.DISALLOWED_IMAGE
    assert res.is_valid is False
    assert res.is_alive is True
    assert "not in allowed whitelist" in str(res.failure_reason)
    assert (
        test_agent_process_running(5555, persisted_start_time=base_time, inspector=inspector)
        is False
    )


def test_pid_recycling_detected_excessive_start_drift(base_time: datetime) -> None:
    """Start time drift exceeding 300 seconds triggers PID recycling defense."""
    inspector = MockProcessInspector()
    # 301 seconds drift -> PID recycled by unrelated process!
    recycled_time = base_time + timedelta(seconds=PID_DRIFT_TOLERANCE_SECONDS + 1)
    inspector.register_process(
        pid=6666,
        process_name="agy",
        is_active=True,
        start_time=recycled_time,
    )

    res = inspect_process(pid=6666, persisted_start_time=base_time, inspector=inspector)
    assert res.status == ProcessInspectionStatus.PID_RECYCLED
    assert res.is_valid is False
    assert res.is_recycled is True
    assert "PID recycling detected" in str(res.failure_reason)
    assert (
        test_agent_process_running(6666, persisted_start_time=base_time, inspector=inspector)
        is False
    )


def test_pid_drift_within_tolerance_accepted(base_time: datetime) -> None:
    """Start time drift within 300 seconds is accepted."""
    inspector = MockProcessInspector()
    ok_time = base_time + timedelta(seconds=PID_DRIFT_TOLERANCE_SECONDS - 5)
    inspector.register_process(
        pid=7777,
        process_name="python.exe",
        is_active=True,
        start_time=ok_time,
    )

    res = inspect_process(pid=7777, persisted_start_time=base_time, inspector=inspector)
    assert res.status == ProcessInspectionStatus.ALIVE_VALID
    assert res.is_valid is True
    assert res.observation.start_time_drift_seconds == 295.0


def test_process_terminated_or_missing() -> None:
    """Process that exited or does not exist evaluates to TERMINATED."""
    inspector = MockProcessInspector()
    inspector.register_process(
        pid=8888,
        process_name="agy",
        is_active=False,
        exit_code=0,
    )

    res = inspect_process(pid=8888, inspector=inspector)
    assert res.status == ProcessInspectionStatus.TERMINATED
    assert res.is_alive is False
    assert res.observation.exit_code == 0
    assert test_agent_process_running(8888, inspector=inspector) is False

    # Unregistered PID
    res_missing = inspect_process(pid=9999, inspector=inspector)
    assert res_missing.status == ProcessInspectionStatus.TERMINATED
    assert res_missing.is_alive is False


def test_invalid_pid_handled_gracefully() -> None:
    """None or negative PID returns TERMINATED."""
    res_none = inspect_process(pid=None)
    assert res_none.status == ProcessInspectionStatus.TERMINATED
    assert res_none.is_alive is False

    res_neg = inspect_process(pid=-1)
    assert res_neg.status == ProcessInspectionStatus.TERMINATED
    assert res_neg.is_alive is False

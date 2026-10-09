"""SACL V1 Worker Process Lifecycle and PID Recycling Defense.

Implements the proven 3-Way Process Observation Check and Safe-Stop Protocol
from ADR-013, RETRY_AND_TIMEOUT_POLICY.md §3, and STATE_MACHINE.md §6.2:
1. OS active process check
2. Process executable image whitelist check
3. Start-time drift tolerance guard (<= 300 seconds)

Safety Refusal Invariant:
If an OS process fails the whitelist or start-time check, the orchestrator
MUST REFUSE to issue termination signals, leaving host processes unmolested.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

from sacl.contracts.exceptions import ProcessObservationError
from sacl.contracts.invariants import (
    ALLOWED_PROCESS_IMAGES,
    PID_DRIFT_TOLERANCE_SECONDS,
    AgentStatus,
    Verdict,
)
from sacl.worker.models import ProcessIdentity, WorkerConfig


class IProcessInspector:
    """Interface for inspecting host operating system processes."""

    def is_process_running(self, pid: int) -> bool:
        """Checks if process with given PID exists and is running."""
        raise NotImplementedError

    def get_process_name(self, pid: int) -> Optional[str]:
        """Returns the process executable name (e.g. 'agy', 'python')."""
        raise NotImplementedError

    def get_process_start_time(self, pid: int) -> Optional[datetime]:
        """Returns the process start timestamp in UTC."""
        raise NotImplementedError

    def terminate_process(self, pid: int, force: bool = False) -> bool:
        """Sends termination or kill signal to process."""
        raise NotImplementedError


class OSProcessInspector(IProcessInspector):
    """Default host OS process inspector using standard library and platform calls."""

    def is_process_running(self, pid: int) -> bool:
        if pid <= 0:
            return False
        if sys.platform == "win32":
            try:
                # OpenProcess with PROCESS_QUERY_LIMITED_INFORMATION (0x1000)
                import ctypes
                kernel32 = ctypes.windll.kernel32
                SYNCHRONIZE = 0x00100000
                PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
                handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION | SYNCHRONIZE, False, pid)
                if not handle:
                    return False
                exit_code = ctypes.c_ulong()
                kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))
                kernel32.CloseHandle(handle)
                STILL_ACTIVE = 259
                return exit_code.value == STILL_ACTIVE
            except Exception:
                # Fallback to powershell or tasklist
                cmd = ["powershell", "-NoProfile", "-Command", f"(Get-Process -Id {pid} -ErrorAction SilentlyContinue) -ne $null"]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                return "True" in res.stdout
        else:
            try:
                os.kill(pid, 0)
                return True
            except OSError:
                return False

    def get_process_name(self, pid: int) -> Optional[str]:
        if pid <= 0:
            return None
        if sys.platform == "win32":
            try:
                cmd = [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    f"(Get-Process -Id {pid} -ErrorAction SilentlyContinue).ProcessName",
                ]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                name = res.stdout.strip()
                return name if name else None
            except Exception:
                return None
        else:
            try:
                with open(f"/proc/{pid}/comm", "r", encoding="utf-8") as f:
                    return f.read().strip()
            except Exception:
                return None

    def get_process_start_time(self, pid: int) -> Optional[datetime]:
        if pid <= 0:
            return None
        if sys.platform == "win32":
            try:
                cmd = [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    f"(Get-Process -Id {pid} -ErrorAction SilentlyContinue).StartTime.ToUniversalTime().ToString('o')",
                ]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                out = res.stdout.strip()
                if out:
                    return datetime.fromisoformat(out.replace("Z", "+00:00"))
            except Exception:
                pass
            return None
        else:
            try:
                stat_mtime = os.stat(f"/proc/{pid}").st_mtime
                return datetime.fromtimestamp(stat_mtime, tz=timezone.utc)
            except Exception:
                return None

    def terminate_process(self, pid: int, force: bool = False) -> bool:
        if pid <= 0:
            return False
        if sys.platform == "win32":
            try:
                flag = "/F" if force else ""
                cmd = ["taskkill", "/PID", str(pid), "/T"]
                if force:
                    cmd.append("/F")
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                return res.returncode == 0
            except Exception:
                return False
        else:
            try:
                sig = signal.SIGKILL if force else signal.SIGTERM
                os.kill(pid, sig)
                return True
            except OSError:
                return False


class MockProcessInspector(IProcessInspector):
    """Deterministic mock process inspector for testing PID recycling and safe stop."""

    def __init__(self) -> None:
        self.running_processes: Dict[int, Dict[str, Any]] = {}

    def register_process(
        self,
        pid: int,
        process_name: str,
        start_time: datetime,
        is_running: bool = True,
    ) -> None:
        self.running_processes[pid] = {
            "name": process_name,
            "start_time": start_time,
            "is_running": is_running,
        }

    def is_process_running(self, pid: int) -> bool:
        info = self.running_processes.get(pid)
        return bool(info and info.get("is_running", False))

    def get_process_name(self, pid: int) -> Optional[str]:
        info = self.running_processes.get(pid)
        if info:
            return info.get("name")
        return None

    def get_process_start_time(self, pid: int) -> Optional[datetime]:
        info = self.running_processes.get(pid)
        if info:
            return info.get("start_time")
        return None

    def terminate_process(self, pid: int, force: bool = False) -> bool:
        if pid in self.running_processes:
            self.running_processes[pid]["is_running"] = False
            return True
        return False


def verify_agent_process_running(
    pid: Optional[int],
    expected_start_time: Optional[Union[datetime, str]] = None,
    allowed_images: Iterable[str] = ALLOWED_PROCESS_IMAGES,
    drift_tolerance_seconds: int = PID_DRIFT_TOLERANCE_SECONDS,
    inspector: Optional[IProcessInspector] = None,
) -> Tuple[bool, str, Optional[float], Optional[str]]:
    """Executes the 3-Way Process Observation Check (Test-AgentProcessRunning).

    Returns:
        (is_verified_running, reason, drift_seconds, actual_process_name)
    """
    if pid is None or pid <= 0:
        return False, "INVALID_PID", None, None

    ins = inspector or OSProcessInspector()

    # 1. OS Process Existence Check
    if not ins.is_process_running(pid):
        return False, "PROCESS_NOT_FOUND", None, None

    # 2. Executable Name Whitelist Check
    actual_name = ins.get_process_name(pid)
    if not actual_name:
        return False, "PROCESS_NAME_UNAVAILABLE", None, None

    clean_name = actual_name.lower().replace(".exe", "")
    allowed = {img.lower().replace(".exe", "") for img in allowed_images}

    matches = any(clean_name == allowed_img or allowed_img in clean_name for allowed_img in allowed)
    if not matches:
        return False, "PROCESS_NAME_MISMATCH_RECYCLED", None, actual_name

    # 3. Start-Time Drift Tolerance Check (Window <= 300 seconds)
    drift_sec: Optional[float] = None
    if expected_start_time is not None:
        expected_dt: Optional[datetime]
        if isinstance(expected_start_time, str):
            try:
                expected_dt = datetime.fromisoformat(expected_start_time.replace("Z", "+00:00"))
            except Exception:
                expected_dt = None
        else:
            expected_dt = expected_start_time

        actual_start_dt = ins.get_process_start_time(pid)
        if expected_dt and actual_start_dt:
            # Normalize timezones
            if expected_dt.tzinfo is not None and actual_start_dt.tzinfo is None:
                actual_start_dt = actual_start_dt.replace(tzinfo=timezone.utc)
            elif expected_dt.tzinfo is None and actual_start_dt.tzinfo is not None:
                expected_dt = expected_dt.replace(tzinfo=timezone.utc)

            drift_sec = abs((actual_start_dt - expected_dt).total_seconds())
            if drift_sec > drift_tolerance_seconds:
                return False, "START_TIME_MISMATCH_RECYCLED", drift_sec, actual_name

    return True, "VERIFIED_RUNNING", drift_sec, actual_name


def safe_stop_agent_process(
    pid: Optional[int],
    expected_start_time: Optional[Union[datetime, str]] = None,
    allowed_images: Iterable[str] = ALLOWED_PROCESS_IMAGES,
    drift_tolerance_seconds: int = PID_DRIFT_TOLERANCE_SECONDS,
    force: bool = True,
    inspector: Optional[IProcessInspector] = None,
) -> Tuple[bool, str, Dict[str, Any]]:
    """Executes the Safe-Stop Protocol & Local Kill Switch.

    Safety Refusal Invariant:
    If OS process matching PID has a non-whitelisted image or start-time drift > 300s:
    1. REFUSES to terminate the process.
    2. Leaves host process unmolested.
    3. Returns safety refusal metadata for marking UNKNOWN state.

    Returns:
        (success, outcome_code, details)
        where outcome_code is one of:
        - "STOPPED_BY_USER": Process verified and terminated.
        - "ALREADY_DEAD": Process was not running.
        - "SAFETY_REFUSAL_NAME": Whitelist mismatch; kill refused.
        - "SAFETY_REFUSAL_DRIFT": Start-time drift violation; kill refused.
    """
    if pid is None or pid <= 0:
        return True, "ALREADY_DEAD", {"pid": pid, "reason": "PID <= 0"}

    ins = inspector or OSProcessInspector()

    # Step 1: Check if already dead
    if not ins.is_process_running(pid):
        return True, "ALREADY_DEAD", {"pid": pid, "reason": "Process already dead"}

    # Step 2: 3-Way verification
    is_verified, reason, drift, proc_name = verify_agent_process_running(
        pid=pid,
        expected_start_time=expected_start_time,
        allowed_images=allowed_images,
        drift_tolerance_seconds=drift_tolerance_seconds,
        inspector=ins,
    )

    if not is_verified:
        if reason == "PROCESS_NAME_MISMATCH_RECYCLED":
            return False, "SAFETY_REFUSAL_NAME", {
                "pid": pid,
                "process_name": proc_name,
                "reason": "Process image not in whitelist; PID recycling suspected",
                "safety_refusal": True,
            }
        elif reason == "START_TIME_MISMATCH_RECYCLED":
            return False, "SAFETY_REFUSAL_DRIFT", {
                "pid": pid,
                "process_name": proc_name,
                "drift_seconds": drift,
                "reason": f"Start-time drift {drift:.1f}s exceeds {drift_tolerance_seconds}s; PID recycling suspected",
                "safety_refusal": True,
            }
        elif reason == "PROCESS_NOT_FOUND":
            return True, "ALREADY_DEAD", {"pid": pid, "reason": "Process already dead"}
        else:
            return False, "SAFETY_REFUSAL_UNVERIFIED", {
                "pid": pid,
                "reason": reason,
                "safety_refusal": True,
            }

    # Step 3: Verified process identity - safe to terminate
    terminated = ins.terminate_process(pid=pid, force=force)
    return terminated, "STOPPED_BY_USER", {
        "pid": pid,
        "process_name": proc_name,
        "drift_seconds": drift,
        "terminated": terminated,
    }

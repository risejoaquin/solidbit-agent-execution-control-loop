"""SACL V1 Process Identity & PID Recycling Protection Subsystem.

Implements the proven 3-way check and PID recycling defense:
1. Process existence in the operating system.
2. Whitelist validation against permitted execution images (ALLOWED_PROCESS_IMAGES).
3. 300-second start-time drift tolerance guard against Windows PID recycling.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, Iterable, Optional, Protocol, Union

from sacl.contracts.invariants import (
    ALLOWED_PROCESS_IMAGES,
    PID_DRIFT_TOLERANCE_SECONDS,
)
from sacl.contracts.models import ProcessObservation
from sacl.contracts.reconciliation import verify_process_observation


class ProcessInspectionStatus(str, Enum):
    """Classification of an inspected process's identity and liveness."""

    ALIVE_VALID = "ALIVE_VALID"
    TERMINATED = "TERMINATED"
    PID_RECYCLED = "PID_RECYCLED"
    DISALLOWED_IMAGE = "DISALLOWED_IMAGE"
    UNKNOWN = "UNKNOWN"


@dataclass
class ProcessIdentity:
    """Observed runtime characteristics of an OS process."""

    pid: int
    process_name: str
    is_active: bool
    start_time: Optional[datetime] = None
    exit_code: Optional[int] = None


@dataclass
class ProcessObservationResult:
    """Outcome of evaluating process identity and PID recycling invariants."""

    observation: ProcessObservation
    status: ProcessInspectionStatus
    is_valid: bool
    is_alive: bool
    is_recycled: bool
    failure_reason: Optional[str] = None


class ProcessInspector(Protocol):
    """Protocol for abstracting OS-level process querying."""

    def get_process_info(self, pid: int) -> Optional[ProcessIdentity]:
        """Queries the OS for process metadata by PID."""
        ...


class MockProcessInspector:
    """Deterministic in-memory process inspector for unit testing and simulation."""

    def __init__(self, processes: Optional[Dict[int, ProcessIdentity]] = None) -> None:
        self.processes: Dict[int, ProcessIdentity] = processes or {}

    def register_process(
        self,
        pid: int,
        process_name: str,
        is_active: bool = True,
        start_time: Optional[datetime] = None,
        exit_code: Optional[int] = None,
    ) -> ProcessIdentity:
        ident = ProcessIdentity(
            pid=pid,
            process_name=process_name,
            is_active=is_active,
            start_time=start_time,
            exit_code=exit_code,
        )
        self.processes[pid] = ident
        return ident

    def unregister_process(self, pid: int) -> None:
        self.processes.pop(pid, None)

    def set_active(self, pid: int, is_active: bool, exit_code: Optional[int] = None) -> None:
        if pid in self.processes:
            self.processes[pid].is_active = is_active
            self.processes[pid].exit_code = exit_code

    def get_process_info(self, pid: int) -> Optional[ProcessIdentity]:
        return self.processes.get(pid)


class SystemProcessInspector:
    """Production process inspector querying the host operating system."""

    def get_process_info(self, pid: int) -> Optional[ProcessIdentity]:
        if pid <= 0:
            return None

        if sys.platform == "win32":
            return self._get_windows_process_info(pid)
        else:
            return self._get_posix_process_info(pid)

    def _get_windows_process_info(self, pid: int) -> Optional[ProcessIdentity]:
        # Try Windows ctypes API first
        try:
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            STILL_ACTIVE = 259

            handle = ctypes.windll.kernel32.OpenProcess(
                PROCESS_QUERY_LIMITED_INFORMATION, False, pid
            )
            if not handle:
                return None

            try:
                # Check exit code
                exit_code_dword = ctypes.c_ulong()
                is_active = True
                exit_code = None
                if ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code_dword)):
                    if exit_code_dword.value != STILL_ACTIVE:
                        is_active = False
                        exit_code = int(exit_code_dword.value)

                # Query process image path / name
                buf = ctypes.create_unicode_buffer(1024)
                size = ctypes.c_ulong(1024)
                process_name = "unknown"
                if ctypes.windll.kernel32.QueryFullProcessImageNameW(
                    handle, 0, buf, ctypes.byref(size)
                ):
                    full_path = buf.value
                    process_name = Path(full_path).name

                # Query process creation time
                creation_time = ctypes.c_uint64()
                exit_time = ctypes.c_uint64()
                kernel_time = ctypes.c_uint64()
                user_time = ctypes.c_uint64()
                start_dt: Optional[datetime] = None

                if ctypes.windll.kernel32.GetProcessTimes(
                    handle,
                    ctypes.byref(creation_time),
                    ctypes.byref(exit_time),
                    ctypes.byref(kernel_time),
                    ctypes.byref(user_time),
                ):
                    # Windows FILETIME is 100-nanosecond intervals since Jan 1, 1601 UTC
                    epoch_diff = 116444736000000000
                    filetime_val = creation_time.value
                    if filetime_val > epoch_diff:
                        unix_time_sec = (filetime_val - epoch_diff) / 10_000_000.0
                        start_dt = datetime.fromtimestamp(unix_time_sec, tz=timezone.utc)

                return ProcessIdentity(
                    pid=pid,
                    process_name=process_name,
                    is_active=is_active,
                    start_time=start_dt,
                    exit_code=exit_code,
                )
            finally:
                ctypes.windll.kernel32.CloseHandle(handle)
        except Exception:
            # Fallback to powershell query if ctypes fails
            return self._query_powershell_process_info(pid)

    def _query_powershell_process_info(self, pid: int) -> Optional[ProcessIdentity]:
        try:
            cmd = [
                "powershell",
                "-NoProfile",
                "-Command",
                f"$p = Get-Process -Id {pid} -ErrorAction SilentlyContinue; "
                f"if ($p) {{ [string]::Format('{{0}}|{{1}}|{{2}}|{{3}}', $p.ProcessName, $p.HasExited, $p.StartTime.ToUniversalTime().ToString('o'), $p.ExitCode) }}",
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5, check=False)
            out = res.stdout.strip()
            if not out or "|" not in out:
                return None
            parts = out.split("|")
            pname = parts[0]
            has_exited = parts[1].strip().lower() == "true"
            start_str = parts[2].strip()
            start_dt: Optional[datetime] = None
            if start_str:
                try:
                    start_dt = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                except Exception:
                    pass
            exit_code = int(parts[3]) if parts[3].strip().isdigit() else None
            return ProcessIdentity(
                pid=pid,
                process_name=pname,
                is_active=not has_exited,
                start_time=start_dt,
                exit_code=exit_code,
            )
        except Exception:
            return None

    def _get_posix_process_info(self, pid: int) -> Optional[ProcessIdentity]:
        # POSIX liveness check
        try:
            os.kill(pid, 0)
            is_active = True
        except ProcessLookupError:
            return None
        except PermissionError:
            is_active = True

        process_name = "unknown"
        start_dt: Optional[datetime] = None

        proc_stat = Path(f"/proc/{pid}/stat")
        if proc_stat.exists():
            try:
                content = proc_stat.read_text()
                # Comm is in parentheses
                if "(" in content and ")" in content:
                    process_name = content[content.find("(") + 1 : content.rfind(")")]
            except Exception:
                pass

        return ProcessIdentity(
            pid=pid,
            process_name=process_name,
            is_active=is_active,
            start_time=start_dt,
            exit_code=None,
        )


_default_inspector: ProcessInspector = SystemProcessInspector()


def get_default_process_inspector() -> ProcessInspector:
    return _default_inspector


def set_default_process_inspector(inspector: ProcessInspector) -> None:
    global _default_inspector
    _default_inspector = inspector


def inspect_process(
    pid: Optional[int],
    persisted_start_time: Optional[Union[datetime, str]] = None,
    inspector: Optional[ProcessInspector] = None,
    allowed_images: Iterable[str] = ALLOWED_PROCESS_IMAGES,
    drift_tolerance_seconds: int = PID_DRIFT_TOLERANCE_SECONDS,
) -> ProcessObservationResult:
    """Performs the canonical 3-way check on an OS process ID.

    1. Checks if PID is running in OS.
    2. Validates process name against image whitelist.
    3. Checks start-time drift against 300s tolerance to defeat PID recycling.
    """
    if pid is None or pid <= 0:
        obs = ProcessObservation(
            pid=pid,
            is_active=False,
            process_name="none",
            start_time_drift_seconds=None,
            exit_code=None,
        )
        return ProcessObservationResult(
            observation=obs,
            status=ProcessInspectionStatus.TERMINATED,
            is_valid=False,
            is_alive=False,
            is_recycled=False,
            failure_reason="No valid PID specified",
        )

    insp = inspector or _default_inspector
    proc_info = insp.get_process_info(pid)

    if proc_info is None or not proc_info.is_active:
        exit_code = proc_info.exit_code if proc_info else None
        pname = proc_info.process_name if proc_info else "unknown"
        obs = ProcessObservation(
            pid=pid,
            is_active=False,
            process_name=pname,
            start_time_drift_seconds=None,
            exit_code=exit_code,
        )
        return ProcessObservationResult(
            observation=obs,
            status=ProcessInspectionStatus.TERMINATED,
            is_valid=True,
            is_alive=False,
            is_recycled=False,
            failure_reason=None,
        )

    # Process is active in OS -> verify observation contract
    obs, is_valid, reason = verify_process_observation(
        pid=pid,
        process_name=proc_info.process_name,
        is_active=True,
        exit_code=proc_info.exit_code,
        persisted_start_time=persisted_start_time,
        actual_start_time=proc_info.start_time,
        allowed_images=allowed_images,
        drift_tolerance_seconds=drift_tolerance_seconds,
    )

    if not is_valid:
        if reason and "PID recycling" in reason:
            return ProcessObservationResult(
                observation=obs,
                status=ProcessInspectionStatus.PID_RECYCLED,
                is_valid=False,
                is_alive=True,
                is_recycled=True,
                failure_reason=reason,
            )
        else:
            return ProcessObservationResult(
                observation=obs,
                status=ProcessInspectionStatus.DISALLOWED_IMAGE,
                is_valid=False,
                is_alive=True,
                is_recycled=False,
                failure_reason=reason,
            )

    return ProcessObservationResult(
        observation=obs,
        status=ProcessInspectionStatus.ALIVE_VALID,
        is_valid=True,
        is_alive=True,
        is_recycled=False,
        failure_reason=None,
    )


def test_agent_process_running(
    pid: Optional[int],
    persisted_start_time: Optional[Union[datetime, str]] = None,
    inspector: Optional[ProcessInspector] = None,
) -> bool:
    """Canonical Python implementation of Test-AgentProcessRunning.

    Returns True if and only if the process is active, whitelisted,
    and has not suffered start-time drift indicating PID recycling.
    """
    result = inspect_process(
        pid=pid,
        persisted_start_time=persisted_start_time,
        inspector=inspector,
    )
    return result.status == ProcessInspectionStatus.ALIVE_VALID


# Prevent pytest from collecting test_agent_process_running as a test
test_agent_process_running.__test__ = False

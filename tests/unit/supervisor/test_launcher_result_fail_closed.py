"""P0: invalid launcher return values must not produce phantom RUNNING jobs."""
import sqlite3

import pytest

from sacl.contracts.invariants import JobSideStatus, JobStatus
from sacl.supervisor.dispatcher import JobDispatcher
from sacl.supervisor.lease import LeaseCoordinator
from sacl.supervisor.lifecycle import JobLifecycleManager


class ProcessHandle:
    def __init__(self, pid, status=None):
        self.pid = pid
        self.status = status

    def poll(self):
        return self.status


@pytest.mark.parametrize("result", [
    None, 0, -1, False, True, "123", object(),
    ProcessHandle(0), ProcessHandle(-1), ProcessHandle(123, 0),
    ProcessHandle(True), ProcessHandle("12"),
])
def test_invalid_launcher_result_never_enters_running(sqlite_temp_db: sqlite3.Connection, result):
    conn = sqlite_temp_db
    conn.execute(
        "INSERT INTO projects (project_id, name, root_path, created_at, updated_at) "
        "VALUES ('proj-handle', 'Handle test', 'C:/repo', '2026-10-18', '2026-10-18')"
    )
    conn.commit()
    lease = LeaseCoordinator(conn)
    lifecycle = JobLifecycleManager(conn, lease_coordinator=lease)
    dispatcher = JobDispatcher(conn, lease, lifecycle, executor_launcher=lambda ctx: result)
    lifecycle.create_job("job-handle", project_id="proj-handle", status=JobStatus.QUEUED)

    assert dispatcher.dispatch_job("job-handle") is None
    job = lifecycle.get_job("job-handle")
    assert job["status"] == JobSideStatus.FAILED.value
    assert "EXECUTOR_UNAVAILABLE" in job["error_summary"]
    assert lease.get_project_lease("proj-handle") is None
    rows = conn.execute(
        "SELECT run_id, status FROM runs WHERE job_id = 'job-handle'"
    ).fetchall()
    assert len(rows) == 1
    assert rows[0]["status"] == JobSideStatus.FAILED.value
    assert dispatcher.get_run_context(rows[0]["run_id"]) is None
    assert dispatcher.get_launcher_result(rows[0]["run_id"]) is None


@pytest.mark.parametrize("result,pid", [
    (7654, 7654), (ProcessHandle(7655), 7655),
])
def test_valid_launcher_result_enters_running(sqlite_temp_db: sqlite3.Connection, result, pid):
    conn = sqlite_temp_db
    conn.execute(
        "INSERT INTO projects (project_id, name, root_path, created_at, updated_at) "
        "VALUES ('proj-live', 'Live test', 'C:/repo', '2026-10-18', '2026-10-18')"
    )
    conn.commit()
    lease = LeaseCoordinator(conn)
    lifecycle = JobLifecycleManager(conn, lease_coordinator=lease)
    dispatcher = JobDispatcher(conn, lease, lifecycle, executor_launcher=lambda ctx: result)
    lifecycle.create_job("job-live", project_id="proj-live", status=JobStatus.QUEUED)

    run_id = dispatcher.dispatch_job("job-live")
    assert run_id is not None
    assert lifecycle.get_job("job-live")["status"] == JobStatus.RUNNING.value
    assert dispatcher.get_run_context(run_id).pid == pid
    assert dispatcher.get_launcher_result(run_id) is result

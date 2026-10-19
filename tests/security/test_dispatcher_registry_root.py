"""T54 P0: trusted project registry root wins over untrusted job metadata.

Only mock executor callbacks are used. No worker processes are launched.
"""
import sqlite3
import pytest

from sacl.contracts.invariants import JobSideStatus, JobStatus
from sacl.supervisor.dispatcher import JobDispatcher
from sacl.supervisor.lease import LeaseCoordinator
from sacl.supervisor.lifecycle import JobLifecycleManager


def _setup(conn: sqlite3.Connection, resolver, metadata):
    conn.execute(
        "INSERT INTO projects (project_id, name, root_path, created_at, updated_at) "
        "VALUES ('proj-t54', 'T54 test', 'C:/repo', '2026-10-18', '2026-10-18')"
    )
    conn.commit()
    lease = LeaseCoordinator(conn)
    lifecycle = JobLifecycleManager(conn, lease_coordinator=lease)
    launches = []
    dispatcher = JobDispatcher(
        conn, lease, lifecycle,
        executor_launcher=lambda ctx: launches.append(ctx) or 7777,
        project_root_resolver=resolver,
    )
    lifecycle.create_job(
        "job-t54", project_id="proj-t54",
        status=JobStatus.QUEUED, metadata=metadata,
    )
    return lease, lifecycle, dispatcher, launches


def _assert_denied(conn, lease, lifecycle, dispatcher, launches):
    assert dispatcher.dispatch_job("job-t54") is None
    job = lifecycle.get_job("job-t54")
    assert job["status"] == JobSideStatus.POLICY_DENIED.value
    assert "TARGET_ROOT_DENIED" in job["error_summary"]
    assert job["current_run_id"] is None
    assert lease.get_project_lease("proj-t54") is None
    assert conn.execute(
        "SELECT COUNT(*) FROM runs WHERE job_id = 'job-t54'"
    ).fetchone()[0] == 0
    assert launches == []


@pytest.mark.parametrize("override", [
    "C:/other", "C:/repo-evil", "../outside", "D:/repo",
])
def test_metadata_cannot_redirect_trusted_root(sqlite_temp_db, override):
    conn = sqlite_temp_db
    args = _setup(conn, lambda project_id: "C:/repo", {"target_repo_path": override})
    _assert_denied(conn, *args)


@pytest.mark.parametrize("resolver", [
    lambda project_id: (_ for _ in ()).throw(RuntimeError("registry unavailable")),
    lambda project_id: "",
    lambda project_id: None,
])
def test_registry_resolver_failure_is_not_silently_ignored(sqlite_temp_db, resolver):
    conn = sqlite_temp_db
    args = _setup(conn, resolver, {"target_repo_path": "C:/repo"})
    _assert_denied(conn, *args)


@pytest.mark.parametrize("metadata", [
    {}, {"target_repo_path": "C:/repo"}, {"target_repo_path": "c:\\repo"},
])
def test_authorized_registered_root_launches_mock_only(sqlite_temp_db, metadata):
    conn = sqlite_temp_db
    lease, lifecycle, dispatcher, launches = _setup(
        conn, lambda project_id: "C:/repo", metadata,
    )
    run_id = dispatcher.dispatch_job("job-t54")
    assert run_id is not None
    assert lifecycle.get_job("job-t54")["status"] == JobStatus.RUNNING.value
    assert dispatcher.get_run_context(run_id).target_repo_path == "C:/repo"
    assert dispatcher.get_run_context(run_id).pid == 7777
    assert len(launches) == 1
    assert lease.get_project_lease("proj-t54") is not None

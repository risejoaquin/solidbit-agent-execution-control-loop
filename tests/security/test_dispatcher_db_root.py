"""T55 P0: SQLite registry root is authoritative when no resolver is injected.

All executor callbacks are mock functions. No worker is started.
"""
import sqlite3
import pytest

from sacl.contracts.invariants import JobSideStatus, JobStatus
from sacl.contracts.exceptions import PolicyDeniedError
from sacl.supervisor.dispatcher import JobDispatcher
from sacl.supervisor.lease import LeaseCoordinator
from sacl.supervisor.lifecycle import JobLifecycleManager


def _setup(conn: sqlite3.Connection, metadata):
    conn.execute(
        "INSERT INTO projects (project_id, name, root_path, created_at, updated_at) "
        "VALUES ('proj-t55', 'T55 test', 'C:/repo', '2026-10-18', '2026-10-18')"
    )
    conn.commit()
    lease = LeaseCoordinator(conn)
    lifecycle = JobLifecycleManager(conn, lease_coordinator=lease)
    launches = []
    dispatcher = JobDispatcher(
        conn, lease, lifecycle,
        executor_launcher=lambda ctx: launches.append(ctx) or 7777,
    )
    lifecycle.create_job(
        'job-t55', project_id='proj-t55',
        status=JobStatus.QUEUED, metadata=metadata,
    )
    return lease, lifecycle, dispatcher, launches


def _assert_denied(conn, lease, lifecycle, dispatcher, launches):
    assert dispatcher.dispatch_job('job-t55') is None
    job = lifecycle.get_job('job-t55')
    assert job['status'] == JobSideStatus.POLICY_DENIED.value
    assert 'TARGET_ROOT_DENIED' in job['error_summary']
    assert job['current_run_id'] is None
    assert lease.get_project_lease('proj-t55') is None
    assert conn.execute(
        "SELECT COUNT(*) FROM runs WHERE job_id = 'job-t55'"
    ).fetchone()[0] == 0
    assert launches == []


@pytest.mark.parametrize('override', [
    'C:/other', 'C:/repo-evil', '../outside', 'D:/repo',
    '', 42, True, [],
])
def test_metadata_cannot_redirect_sqlite_registered_root(sqlite_temp_db, override):
    conn = sqlite_temp_db
    args = _setup(conn, {'target_repo_path': override})
    _assert_denied(conn, *args)


@pytest.mark.parametrize('bad_root', ['', 'relative/path', 'C:relative'])
def test_invalid_sqlite_root_fails_closed(sqlite_temp_db, bad_root):
    conn = sqlite_temp_db
    args = _setup(conn, {})
    conn.execute('UPDATE projects SET root_path = ? WHERE project_id = ?', (bad_root, 'proj-t55'))
    conn.commit()
    _assert_denied(conn, *args)


@pytest.mark.parametrize('metadata', [
    {}, {'target_repo_path': 'C:/repo'},
    {'target_repo_path': 'c:\\repo'}, {'target_repo_path': None},
])
def test_sqlite_registered_root_is_used_with_mock_launcher(sqlite_temp_db, metadata):
    conn = sqlite_temp_db
    lease, lifecycle, dispatcher, launches = _setup(conn, metadata)
    run_id = dispatcher.dispatch_job('job-t55')
    assert run_id is not None
    assert lifecycle.get_job('job-t55')['status'] == JobStatus.RUNNING.value
    assert dispatcher.get_run_context(run_id).target_repo_path == 'C:/repo'
    assert dispatcher.get_run_context(run_id).pid == 7777
    assert len(launches) == 1
    assert lease.get_project_lease('proj-t55') is not None


def test_missing_registry_row_denied_before_lease_or_run(sqlite_temp_db):
    conn = sqlite_temp_db
    args = _setup(conn, {'target_repo_path': 'C:/repo'})
    # Verify the resolver directly: deleting a referenced project is forbidden by FK.
    with pytest.raises(PolicyDeniedError) as exc:
        args[2]._resolve_target_repo_path('unregistered-project', {'target_repo_path': 'C:/repo'})
    assert 'registry' in str(exc.value).lower()

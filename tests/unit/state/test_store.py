"""Unit tests for SACL V1 Authoritative SqliteStateStore Subsystem Facade."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path
from typing import Generator

# Ensure repo root is on sys.path
_repo_root = Path(__file__).resolve().parents[3]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

import pytest

from sacl.contracts.invariants import JobStatus, Verdict
from sacl.contracts.models import AuditEvent, HeartbeatRecord
from sacl.state.store import SqliteStateStore, StateStore
from tests.helpers.db_helpers import check_wal_mode, verify_canonical_domains_exist


def test_store_initialization_and_auto_migrate(migration_sql_path: Path) -> None:
    """Verifies SqliteStateStore initialization and automatic migration."""
    store = SqliteStateStore(":memory:")
    store.initialize_schema(migration_sql_path.parent)

    checks = verify_canonical_domains_exist(store.connection)
    for domain, exists in checks.items():
        assert exists is True, f"Domain table {domain} missing"

    store.close()


def test_store_context_manager_protocol(migration_sql_path: Path) -> None:
    """Verifies SqliteStateStore context manager (__enter__ / __exit__)."""
    with SqliteStateStore(":memory:") as store:
        store.initialize_schema(migration_sql_path.parent)
        assert store.connection is not None
        # Connection active inside context
        cursor = store.connection.cursor()
        cursor.execute("SELECT 1;")
        assert cursor.fetchone()[0] == 1


def test_store_disk_backed_wal_mode(tmp_path: Path, migration_sql_path: Path) -> None:
    """Verifies disk-backed SqliteStateStore enables WAL mode."""
    db_file = tmp_path / "sacl_ops.db"
    with SqliteStateStore(db_file) as store:
        store.initialize_schema(migration_sql_path.parent)
        assert check_wal_mode(store.connection) is True


def test_store_job_and_run_lifecycle_facade(migration_sql_path: Path) -> None:
    """Verifies job, run, and agent tracking via SqliteStateStore facade."""
    with SqliteStateStore(":memory:") as store:
        store.initialize_schema(migration_sql_path.parent)

        # Register project & package
        store.register_project("proj-alpha", "Alpha", "C:/repos/alpha")
        store.record_package(
            package_id="pkg-w1",
            archive_sha256="sha-pkg-w1",
            manifest={"job_id": "job-10"},
            storage_path="packages/pkg-w1.zip",
            project_id="proj-alpha",
        )

        # Create Job
        store.create_job(
            job_id="job-10",
            package_id="pkg-w1",
            project_id="proj-alpha",
            status=JobStatus.RECEIVED.value,
            priority=5,
        )
        job = store.get_job("job-10")
        assert job is not None
        assert job["status"] == JobStatus.RECEIVED.value

        # Update Job
        store.update_job_status("job-10", status=JobStatus.RUNNING.value)
        assert store.get_job("job-10")["status"] == JobStatus.RUNNING.value

        # Create Run
        store.create_run(
            run_id="run-10-1",
            job_id="job-10",
            package_id="pkg-w1",
            project="Alpha",
            repository="org/alpha",
            mode="isolated_branch",
            source_orchestrator="C:/orch",
            target_repo_path="C:/repos/alpha",
            run_dir="runs/run-10-1",
            status="RUNNING",
        )
        run = store.get_run("run-10-1")
        assert run is not None
        assert run["status"] == "RUNNING"

        # Update Run
        store.update_run_status(
            run_id="run-10-1",
            status="COMPLETED",
            ready_for_integration="YES",
            reconciled_verdict=Verdict.PASS.value,
        )
        updated_run = store.get_run("run-10-1")
        assert updated_run["status"] == "COMPLETED"
        assert updated_run["reconciled_verdict"] == "PASS"

        # Agent tracking
        store.record_agent(
            agent_id="AG-TEST",
            run_id="run-10-1",
            status="RUNNING",
            prompt_path="prompts/p.md",
            report_path="reports/r.md",
            stdout_path="logs/stdout.log",
            stderr_path="logs/stderr.log",
            pid=7777,
        )
        agent = store.get_agent("AG-TEST", "run-10-1")
        assert agent is not None
        assert agent["pid"] == 7777

        store.update_agent(
            agent_id="AG-TEST",
            run_id="run-10-1",
            status="COMPLETE",
            result_verdict="PASS",
            exit_code=0,
        )
        updated_agent = store.get_agent("AG-TEST", "run-10-1")
        assert updated_agent["status"] == "COMPLETE"
        assert updated_agent["result_verdict"] == "PASS"

        # Results & Deliverables
        store.record_result(
            job_id="job-10",
            run_id="run-10-1",
            status="COMPLETE",
            final_verdict=Verdict.PASS.value,
            summary_md_path="runs/run-10-1/SUMMARY.md",
            summary_json_path="runs/run-10-1/SUMMARY.json",
            delivered_to="uniquedraken@gmail.com",
        )
        res = store.get_result("run-10-1")
        assert res is not None
        assert res["final_verdict"] == "PASS"
        assert res["delivered_to"] == "uniquedraken@gmail.com"


def test_store_audit_event_and_heartbeat_facade(migration_sql_path: Path) -> None:
    """Verifies audit event logging and heartbeat management via store facade."""
    with SqliteStateStore(":memory:") as store:
        store.initialize_schema(migration_sql_path.parent)

        # Audit Event
        ev = AuditEvent(
            event_type="DISPATCH_ATTEMPT",
            severity="INFO",
            payload={"worker": "AG-COMPAT"},
            created_at="2026-10-07T12:00:00Z",
            run_id="run-ev-1",
        )
        ev_id = store.record_event(ev)
        assert ev_id > 0

        events = store.list_events(run_id="run-ev-1")
        assert len(events) == 1
        assert events[0]["event_type"] == "DISPATCH_ATTEMPT"

        # Heartbeat
        hb = HeartbeatRecord(
            component="SUPERVISOR",
            instance_id="sup-facade-1",
            pid=3333,
            status="IDLE",
            last_seen_at="2026-10-07T12:00:00Z",
        )
        hb_id = store.record_heartbeat(hb)
        assert hb_id > 0
        assert store.heartbeats.get_latest_heartbeat("SUPERVISOR", "sup-facade-1") is not None


def test_store_lease_facade(migration_sql_path: Path) -> None:
    """Verifies lease acquisition, renewal, and release via store facade."""
    with SqliteStateStore(":memory:") as store:
        store.initialize_schema(migration_sql_path.parent)

        acq = store.acquire_lease("SUPERVISOR_SINGLETON", holder_id="sup-1", holder_pid=1111, ttl_seconds=20)
        assert acq is True

        renewed = store.renew_lease("SUPERVISOR_SINGLETON", holder_id="sup-1", ttl_seconds=30)
        assert renewed is True

        released = store.release_lease("SUPERVISOR_SINGLETON", holder_id="sup-1")
        assert released is True


def test_store_conflict_detection_facade(migration_sql_path: Path) -> None:
    """Verifies cross-agent file modification conflict detection via store facade."""
    with SqliteStateStore(":memory:") as store:
        store.initialize_schema(migration_sql_path.parent)

        store.create_job("job-cf", None, None, status="RECEIVED")
        store.create_run(
            run_id="run-cf",
            job_id="job-cf",
            package_id="pkg-cf",
            project="Proj",
            repository="org/repo",
            mode="branch",
            source_orchestrator="C:/orch",
            target_repo_path="C:/target",
            run_dir="runs/cf",
            status="RUNNING",
        )
        store.record_agent(
            agent_id="AG-1", run_id="run-cf", status="RUNNING",
            prompt_path="p", report_path="r", stdout_path="o", stderr_path="e"
        )
        store.record_agent(
            agent_id="AG-2", run_id="run-cf", status="RUNNING",
            prompt_path="p", report_path="r", stdout_path="o", stderr_path="e"
        )

        store.record_file_modifications("run-cf", "AG-1", ["shared/file.py", "ag1/unique.py"])
        store.record_file_modifications("run-cf", "AG-2", ["shared/file.py", "ag2/unique.py"])

        conflicts = store.detect_file_conflicts("run-cf")
        assert len(conflicts) == 1
        assert conflicts[0]["file_path"] == "shared/file.py"
        assert store.get_run("run-cf")["ready_for_integration"] == "NO"


def test_store_transactions_and_savepoints(migration_sql_path: Path) -> None:
    """Verifies ACID transactions and nested savepoints via store facade."""
    with SqliteStateStore(":memory:") as store:
        store.initialize_schema(migration_sql_path.parent)

        # Successful transaction
        with store.transaction():
            store.create_job("job-tx-1", None, None, status="RECEIVED")

        assert store.get_job("job-tx-1") is not None

        # Rollback transaction on exception
        with pytest.raises(ValueError):
            with store.transaction():
                store.create_job("job-tx-fail", None, None, status="RECEIVED")
                raise ValueError("Forced error")

        assert store.get_job("job-tx-fail") is None

        # Nested savepoint rollback
        with store.transaction():
            store.create_job("job-tx-keep", None, None, status="RECEIVED")
            try:
                with store.savepoint("sp_sub"):
                    store.create_job("job-tx-discard", None, None, status="RECEIVED")
                    raise RuntimeError("Discard sub-transaction")
            except RuntimeError:
                pass

        assert store.get_job("job-tx-keep") is not None
        assert store.get_job("job-tx-discard") is None

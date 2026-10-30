"""Tests for inviolable non-killing diagnostic timeout (TIMEOUT_RUNNING)."""

from __future__ import annotations

import time
from pathlib import Path

from sacl.contracts.invariants import AgentStatus, Verdict
from sacl.observability.audit import AuditEventEmitter
from sacl.worker.agent_worker import AgentWorker
from sacl.worker.models import WorkerConfig
from sacl.worker.process import MockProcessInspector


def test_non_killing_timeout_transition(tmp_path: Path, sqlite_memory_db):
    """Verifies that an agent exceeding timeout transitions to TIMEOUT_RUNNING and is NOT killed."""
    audit_emitter = AuditEventEmitter(sqlite_memory_db)
    inspector = MockProcessInspector()

    # Create dummy files
    run_dir = tmp_path / "run_01"
    run_dir.mkdir(parents=True)
    report_p = run_dir / "reports" / "AG-TEST.md"
    stdout_p = run_dir / "logs" / "AG-TEST.stdout.log"
    stderr_p = run_dir / "logs" / "AG-TEST.stderr.log"
    prompt_p = run_dir / "prompts" / "AG-TEST.prompt.txt"
    worktree_p = run_dir / "worktrees" / "wt-AG-TEST"

    # Configure worker with very short timeout (0.1 seconds)
    config = WorkerConfig(
        agent_id="AG-TEST",
        run_id="run-timeout-001",
        worktree_path=worktree_p,
        prompt_path=prompt_p,
        report_path=report_p,
        stdout_path=stdout_p,
        stderr_path=stderr_p,
        timeout_seconds=0.1,  # 100ms
        max_attempts=1,
    )

    worker = AgentWorker(
        config=config,
        db_conn=sqlite_memory_db,
        audit_emitter=audit_emitter,
        process_inspector=inspector,
    )

    # Launch worker attempt
    worker.launch_attempt()
    worker.pid = 7777
    inspector.register_process(7777, "agy", worker.started_at, is_running=True)

    # Wait 150ms to exceed timeout
    time.sleep(0.15)

    is_running, status = worker.check_liveness_and_timeout()
    assert is_running is True
    assert status == AgentStatus.TIMEOUT_RUNNING.value
    assert worker.is_timed_out is True

    # INVIOLABLE INVARIANT: The process is NOT killed!
    assert inspector.is_process_running(7777) is True

    # Verify audit event in SQLite
    cur = sqlite_memory_db.cursor()
    cur.execute("SELECT event_type, severity FROM events WHERE event_type = 'TIMEOUT_DETECTED';")
    events = cur.fetchall()
    assert len(events) == 1
    assert events[0][0] == "TIMEOUT_DETECTED"
    assert events[0][1] == "WARN"

    # Now verify that when process later finishes with a report, it completes normally
    report_p.parent.mkdir(parents=True, exist_ok=True)
    report_p.write_text("# Deliverable\n\nAGENT_AG_TEST_RESULT = PASS\n", encoding="utf-8")
    stdout_p.parent.mkdir(parents=True, exist_ok=True)
    stdout_p.write_text("Execution logs...", encoding="utf-8")
    stderr_p.parent.mkdir(parents=True, exist_ok=True)
    stderr_p.write_text("", encoding="utf-8")

    inspector.terminate_process(7777)
    res = worker.handle_process_exit(exit_code=0)

    assert res.status == "SUCCEEDED"
    assert res.result_verdict == Verdict.PASS.value
    assert worker.status == AgentStatus.COMPLETE.value

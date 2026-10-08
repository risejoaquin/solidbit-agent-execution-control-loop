"""Unit tests for SACL V1 correlation ID and execution context management."""

import concurrent.futures
from sacl.observability.correlation import (
    CorrelationContext,
    clear_current_correlation,
    correlation_scope,
    generate_correlation_id,
    generate_trace_id,
    get_current_correlation,
    reset_current_correlation,
    set_current_correlation,
)


def test_generate_ids():
    """Verifies format and uniqueness of generated trace and correlation IDs."""
    trace1 = generate_trace_id()
    trace2 = generate_trace_id()
    assert len(trace1) == 32
    assert trace1 != trace2

    corr1 = generate_correlation_id()
    corr2 = generate_correlation_id(prefix="custom-")
    assert corr1.startswith("corr-")
    assert corr2.startswith("custom-")
    assert corr1 != corr2


def test_correlation_context_serialization():
    """Verifies dictionary and transport header roundtrip."""
    ctx = CorrelationContext(
        trace_id="1234567890abcdef1234567890abcdef",
        job_id="job-001",
        run_id="run-001",
        node_id="node-001",
        agent_id="AG-TEST",
        parent_id="parent-001",
        metadata={"custom": "val"},
    )
    d = ctx.to_dict()
    assert d["trace_id"] == "1234567890abcdef1234567890abcdef"
    assert d["job_id"] == "job-001"
    assert d["run_id"] == "run-001"
    assert d["agent_id"] == "AG-TEST"
    assert d["metadata"]["custom"] == "val"

    rebuilt = CorrelationContext.from_dict(d)
    assert rebuilt.trace_id == ctx.trace_id
    assert rebuilt.job_id == ctx.job_id
    assert rebuilt.run_id == ctx.run_id
    assert rebuilt.metadata == ctx.metadata

    # Headers roundtrip
    headers = ctx.to_headers()
    assert headers["X-SACL-Trace-Id"] == ctx.trace_id
    assert headers["X-SACL-Job-Id"] == "job-001"
    assert headers["X-SACL-Run-Id"] == "run-001"

    from_hdrs = CorrelationContext.from_headers(headers)
    assert from_hdrs.trace_id == ctx.trace_id
    assert from_hdrs.job_id == ctx.job_id
    assert from_hdrs.run_id == ctx.run_id
    assert from_hdrs.agent_id == ctx.agent_id


def test_correlation_context_derive_child():
    """Verifies that child context preserves root trace/job/run while updating agent/node."""
    root = CorrelationContext(
        trace_id="trace-root-123",
        job_id="job-100",
        run_id="run-200",
        metadata={"tier": "mutating"},
    )
    child = root.derive_child(node_id="NODE-1", agent_id="AG-1", metadata={"step": "1"})

    assert child.trace_id == "trace-root-123"
    assert child.job_id == "job-100"
    assert child.run_id == "run-200"
    assert child.node_id == "NODE-1"
    assert child.agent_id == "AG-1"
    assert child.parent_id == "run-200"
    assert child.metadata["tier"] == "mutating"
    assert child.metadata["step"] == "1"


def test_correlation_scope_nesting_and_restoration():
    """Verifies hierarchical nesting and reliable restoration of correlation scope."""
    clear_current_correlation()
    base = get_current_correlation()
    base_trace = base.trace_id

    with correlation_scope(job_id="job-outer", run_id="run-outer") as outer_ctx:
        assert outer_ctx.job_id == "job-outer"
        assert outer_ctx.run_id == "run-outer"
        assert outer_ctx.trace_id == base_trace
        assert get_current_correlation().job_id == "job-outer"

        with correlation_scope(agent_id="AG-INNER", node_id="node-inner") as inner_ctx:
            assert inner_ctx.job_id == "job-outer"
            assert inner_ctx.run_id == "run-outer"
            assert inner_ctx.agent_id == "AG-INNER"
            assert inner_ctx.node_id == "node-inner"
            assert get_current_correlation().agent_id == "AG-INNER"

        # After exiting inner block, inner values must be restored
        current = get_current_correlation()
        assert current.job_id == "job-outer"
        assert current.agent_id is None

    # After exiting outer block, base must be restored
    assert get_current_correlation().job_id is None


def test_correlation_scope_exception_safety():
    """Verifies context is safely restored even when an unhandled exception is raised."""
    clear_current_correlation()
    assert get_current_correlation().job_id is None

    try:
        with correlation_scope(job_id="failing-job", run_id="failing-run"):
            assert get_current_correlation().job_id == "failing-job"
            raise RuntimeError("Deliberate failure inside scope")
    except RuntimeError:
        pass

    assert get_current_correlation().job_id is None


def test_thread_isolation_of_correlation():
    """Verifies that separate threads maintain isolated correlation contexts."""
    clear_current_correlation()

    def thread_worker(job_name: str) -> str:
        with correlation_scope(job_id=job_name):
            return get_current_correlation().job_id or ""

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        f1 = executor.submit(thread_worker, "job-A")
        f2 = executor.submit(thread_worker, "job-B")
        f3 = executor.submit(thread_worker, "job-C")

        assert f1.result() == "job-A"
        assert f2.result() == "job-B"
        assert f3.result() == "job-C"


def test_imperative_set_and_clear_correlation():
    """Verifies imperative set and clear operations."""
    clear_current_correlation()
    ctx = CorrelationContext(trace_id="manual-trace", job_id="manual-job")
    token = set_current_correlation(ctx)

    assert get_current_correlation().trace_id == "manual-trace"
    assert get_current_correlation().job_id == "manual-job"

    reset_current_correlation(token)
    assert get_current_correlation().job_id is None

    # Test clear
    set_current_correlation(ctx)
    clear_current_correlation()
    assert get_current_correlation().job_id is None


def test_headers_case_insensitivity_and_defaults():
    """Verifies from_headers handles mixed case, missing keys, and default trace IDs."""
    headers = {
        "x-sacl-trace-id": "trace-lower",
        "X-SACL-JOB-ID": "job-upper",
        "X-sacl-RUN-id": "run-mixed",
    }
    parsed = CorrelationContext.from_headers(headers)
    assert parsed.trace_id == "trace-lower"
    assert parsed.job_id == "job-upper"
    assert parsed.run_id == "run-mixed"
    assert parsed.node_id is None

    # Completely empty headers generates valid trace_id
    empty_parsed = CorrelationContext.from_headers({})
    assert len(empty_parsed.trace_id) == 32
    assert empty_parsed.job_id is None


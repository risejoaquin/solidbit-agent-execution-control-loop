"""Unit tests for SACL V1 UI Data Models."""

import json

from sacl.ui.models import (
    ConnectionState,
    FullDashboardView,
    HumanGateCard,
    RecoverySummaryView,
    SafetyBoundaryStatus,
    TechnologyConnection,
    UIMode,
)


def test_ui_mode_enum():
    assert UIMode.SIMPLE.value == "simple"
    assert UIMode.TECHNICAL.value == "technical"
    assert UIMode.AUDIT.value == "audit"


def test_technology_connection_serialization():
    conn = TechnologyConnection(
        id="gh",
        name="GitHub CLI",
        category="vcs",
        status=ConnectionState.CONNECTED,
        version="gh version 2.40.0",
        account_info="Logged in as test_user",
        last_checked="2026-10-22T20:00:00Z",
    )
    d = conn.to_dict()
    assert d["id"] == "gh"
    assert d["status"] == "connected"
    assert d["category"] == "vcs"
    assert json.dumps(d)


def test_human_gate_card_serialization():
    card = HumanGateCard(
        approval_id="appr-001",
        request_id="req-001",
        job_id="job-railway-check",
        run_id="run-101",
        action="DEPLOY_STAGING",
        scope="railway/service-backend",
        risk_level="MEDIUM",
        status="PENDING",
        reason="Verification required for staging deployment",
        evidence_summary="Unit tests passed; staging deployment pending confirmation",
        created_at="2026-10-22T20:00:00Z",
        expires_at="2026-10-22T21:00:00Z",
        can_decide=True,
    )
    d = card.to_dict()
    assert d["approval_id"] == "appr-001"
    assert d["risk_level"] == "MEDIUM"
    assert d["can_decide"] is True


def test_full_dashboard_view_serialization():
    safety = SafetyBoundaryStatus(
        production_allowed=False,
        deploy_allowed=False,
        merge_allowed=False,
        ruleset_protected=True,
        dirty_root_prevented=True,
    )
    recovery = RecoverySummaryView(
        interrupted_runs_count=0,
        classification="CLEAN",
        safe_to_resume=True,
        recommended_action="Ready",
    )
    snap = FullDashboardView(
        readiness_score=95,
        active_project="Stable-Ecommerce",
        active_campaign="Productization Campaign",
        mode="simple",
        safety=safety,
        connections=[],
        pending_gates=[],
        agents=[],
        leases=[],
        recovery=recovery,
        alerts=["Notice: Production locked"],
        recent_events=[],
        timestamp="2026-10-22T20:00:00Z",
    )
    d = snap.to_dict()
    assert d["readiness_score"] == 95
    assert d["safety"]["production_allowed"] is False
    assert d["safety"]["ruleset_protected"] is True
    assert json.dumps(d)

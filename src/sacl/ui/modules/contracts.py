"""Contracts & Constitutional Policies UI Module.

Exposes frozen architectural contracts (DR-INV-001, DR-PAY-001),
the 6 mandatory Decision Gates, and hard deny boundaries.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from sacl.contracts.invariants import HARD_DENIED_ACTIONS

logger = logging.getLogger("sacl.ui.modules.contracts")


class ContractsModule:
    """Manages frozen contracts and SDLC gate specifications."""

    CONTRACTS = [
        {
            "id": "DR-INV-001",
            "title": "SellableUnit & Stock Allocation",
            "status": "FROZEN",
            "enforcement": "STRICT",
            "description": "Stock deduction and SellableUnit availability must maintain atomic inventory locks across web checkout and browser POS.",
        },
        {
            "id": "DR-PAY-001",
            "title": "Payment Ledger Transaction Atomicity",
            "status": "FROZEN",
            "enforcement": "STRICT",
            "description": "Payment records and status changes require double-entry ledger journals. No mutable balance updates without ledger trail.",
        },
        {
            "id": "DR-IDEM-001",
            "title": "Mutating Endpoint Idempotency",
            "status": "FROZEN",
            "enforcement": "STRICT",
            "description": "All mutating APIs (/api/pos/sales, checkout, webhooks) must accept and enforce Idempotency-Key headers.",
        },
        {
            "id": "DR-AUTH-001",
            "title": "RBAC & Multi-Tenant Isolation",
            "status": "FROZEN",
            "enforcement": "STRICT",
            "description": "Zero cross-tenant data leaks. Supabase RLS and token claims strictly verified on every data layer boundary.",
        },
        {
            "id": "DR-ERR-001",
            "title": "Canonical Error Envelopes",
            "status": "FROZEN",
            "enforcement": "STRICT",
            "description": "Standardized { error: { code, message, details } } format. Contracts must never be altered to make an accidental test pass.",
        },
        {
            "id": "DR-REC-001",
            "title": "Receipts & Offline Recovery",
            "status": "FROZEN",
            "enforcement": "STRICT",
            "description": "Deterministic receipt generation and crash-consistent synchronization between offline SQLite POS and cloud backend.",
        },
    ]

    GATES = [
        {
            "id": "GATE-0",
            "name": "Preflight & Worktrees",
            "rule": "Verify clean git roots, worktrees exist, CLIs authenticated. No auto-cleaning.",
        },
        {
            "id": "GATE-1",
            "name": "Railway Safety",
            "rule": "Production autoDeploy OFF verified in-session; staging untouched; zero prod deploy.",
        },
        {
            "id": "GATE-2",
            "name": "GitHub Governance",
            "rule": "JSON backup of rulesets; CODEOWNERS matrix preserved; author cannot approve own PR.",
        },
        {
            "id": "GATE-3",
            "name": "Jira Graph Integrity",
            "rule": "Pre-backup of all issue links; live DAG verification; no cycle creation.",
        },
        {
            "id": "GATE-4",
            "name": "QA Independent Read-Only",
            "rule": "Direct API verification; detect false green reports or collateral damage.",
        },
        {
            "id": "GATE-5",
            "name": "Release Authority",
            "rule": "Zero automated merges to production, zero cutovers without sovereign human consent.",
        },
    ]

    def get_policies_overview(self) -> Dict[str, Any]:
        """Returns consolidated contract rules and safety boundaries."""
        return {
            "contracts": self.CONTRACTS,
            "decision_gates": self.GATES,
            "hard_denied_actions": sorted(list(HARD_DENIED_ACTIONS)),
            "safety_summary": "6 Frozen Contracts · 6 Mandatory Decision Gates · Hard Denies Supremacy",
        }

"""SDLC Roadmap & Milestone Governance Module for SACL UI.

Presents the full Software Development Life Cycle (SDLC) timeline, linking Jira epics,
frozen architectural contracts, bounded gates, and release milestones.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger("sacl.ui.modules.roadmap")


class RoadmapModule:
    """Provides structured visibility into the full SDLC lifecycle and roadmap."""

    PHASES = [
        {
            "id": "phase-1",
            "name": "Fase 1: Arquitectura & Contratos Inmutables",
            "code": "SDLC-ARCH",
            "status": "COMPLETED",
            "progress": 100,
            "period": "Q1 2026",
            "deliverables": [
                "DR-INV-001: Ledger de Inventario Atómico SellableUnit",
                "DR-PAY-001: Capture & Balance Transaccional Cero-Overcharge",
                "DR-IDEM-001: Llaves de Idempotencia en SQLite WAL",
                "Especificación formal SCREEN_BY_SCREEN_SPEC.md",
            ],
            "jira_keys": ["SOLID-101", "SOLID-102"],
            "contracts_semaphore": "GREEN",
        },
        {
            "id": "phase-2",
            "name": "Fase 2: Motor de Control SACL & Recuperación ante Fallos",
            "code": "SDLC-ENGINE",
            "status": "COMPLETED",
            "progress": 100,
            "period": "Q2 2026",
            "deliverables": [
                "Bucle de control cerrado con supremacía de Hard Deny",
                "Scheduler DAG topológico con isolación de worktree",
                "Recuperación consistente post-crash sin mutación de historial",
                "683/683 pruebas unitarias e integración en verde",
            ],
            "jira_keys": ["SOLID-103", "SOLID-104"],
            "contracts_semaphore": "GREEN",
        },
        {
            "id": "phase-3",
            "name": "Fase 3: Capa UI & Decision Shell Modular",
            "code": "SDLC-UIX",
            "status": "COMPLETED",
            "progress": 100,
            "period": "Q3 2026",
            "deliverables": [
                "Diseño Apple HIG Dark OLED con tipografía SF Pro",
                "Cajón de Impacto Visual & Diff con semáforo de contratos",
                "Streaming de eventos en tiempo real (Server-Sent Events)",
                "Lanzador visual de campañas y workorders con 1 clic",
            ],
            "jira_keys": ["SOLID-105"],
            "contracts_semaphore": "GREEN",
        },
        {
            "id": "phase-4",
            "name": "Fase 4: E2E Auth, Notificaciones Móviles & Telemetría",
            "code": "SDLC-AUTH-OPS",
            "status": "IN_PROGRESS",
            "progress": 85,
            "period": "Q4 2026",
            "deliverables": [
                "Autenticación asistida con navegador (gh, railway, supabase, jira, gcloud)",
                "Gateway móvil de micro-decisiones por correo/webhook (Resend)",
                "Monitor de ejecución de tareas en tiempo real con fases y gráficas pastel",
                "Diseñador interactivo de campañas DAG",
            ],
            "jira_keys": ["SOLID-106", "SOLID-107"],
            "contracts_semaphore": "GREEN",
        },
        {
            "id": "phase-5",
            "name": "Fase 5: Despliegue Soberano & Canary en Producción",
            "code": "SDLC-PROD",
            "status": "PLANNED",
            "progress": 20,
            "period": "Q1 2027",
            "deliverables": [
                "Compuerta de Despliegue de Producción con firma multi-operador",
                "Verificación Canary con rollback automático en < 1.5s",
                "Monitoreo continuo de integridad de base de datos WAL",
            ],
            "jira_keys": ["SOLID-108"],
            "contracts_semaphore": "PENDING",
        },
    ]

    def get_roadmap(self) -> Dict[str, Any]:
        """Returns the complete SDLC roadmap state and aggregate metrics."""
        total_phases = len(self.PHASES)
        completed = sum(1 for p in self.PHASES if p["status"] == "COMPLETED")
        overall_progress = round(sum(p["progress"] for p in self.PHASES) / total_phases)

        return {
            "overall_progress": overall_progress,
            "total_phases": total_phases,
            "completed_phases": completed,
            "active_phase": "Fase 4: E2E Auth, Notificaciones Móviles & Telemetría",
            "phases": self.PHASES,
            "architecture_invariants_status": "LOCKED_AND_VERIFIED",
        }

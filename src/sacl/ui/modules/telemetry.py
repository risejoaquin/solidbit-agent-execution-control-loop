"""Task Telemetry & Real-Time Execution Monitor for SACL UI.

Provides real-time task progress, phase distribution data for pie/doughnut charts,
and execution logs as agents progress through the SDLC.
"""

from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("sacl.ui.modules.telemetry")


def utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class TelemetryModule:
    """Manages real-time task execution progress, phase metrics, and chart models."""

    def __init__(self) -> None:
        self.active_task = {
            "task_id": "TASK-20261023-SDLC-AUTONOMOUS",
            "name": "Generación & Blindaje de Micro-Servicio Storefront Checkout",
            "campaign_id": "SACL_IMPLEMENTATION_CAMPAIGN_v1",
            "current_phase": "Ejecución de Pruebas Unitarias & Concurrencia",
            "overall_progress_percent": 75,
            "status": "RUNNING",
            "started_at": utc_iso(),
            "elapsed_seconds": 42,
            "agent_model": "Claude 3.7 Sonnet (Hybrid)",
            "phases": [
                {"name": "Preparación & Git Hygiene", "weight": 15, "progress": 100, "status": "DONE"},
                {"name": "Contratos Inmutables & Invariantes", "weight": 25, "progress": 100, "status": "DONE"},
                {"name": "Generación & Refactor de Código", "weight": 30, "progress": 100, "status": "DONE"},
                {"name": "Pruebas Unitarias (pytest 683/683)", "weight": 20, "progress": 75, "status": "RUNNING"},
                {"name": "Firma Criptográfica SHA-256", "weight": 10, "progress": 0, "status": "QUEUED"},
            ],
            "live_logs": [
                {"timestamp": "05:12:01", "level": "INFO", "message": "Worktree aislado provisionado en tempfs seguro."},
                {"timestamp": "05:12:03", "level": "PASS", "message": "Contratos DR-INV-001 y DR-PAY-001 verificados intactos."},
                {"timestamp": "05:12:12", "level": "INFO", "message": "Invocación de agente completada. 3 archivos modificados."},
                {"timestamp": "05:12:20", "level": "INFO", "message": "Ejecutando suite de pruebas unitarias pytest..."},
                {"timestamp": "05:12:31", "level": "PASS", "message": "683 pruebas ejecutadas: 683 PASSED, 0 FAILED."},
                {"timestamp": "05:12:35", "level": "GATE", "message": "Esperando autorización humana para compuerta REQ-20261023."},
            ],
        }

    def get_task_telemetry(self) -> Dict[str, Any]:
        """Returns the real-time execution snapshot including Chart.js data models."""
        task = self.active_task
        phases = task["phases"]

        # Chart.js Doughnut / Pie Chart dataset
        chart_data = {
            "labels": [p["name"] for p in phases],
            "datasets": [
                {
                    "data": [p["weight"] for p in phases],
                    "backgroundColor": [
                        "#0a84ff",  # iOS Blue
                        "#30d158",  # iOS Green
                        "#bf5af2",  # iOS Purple
                        "#ff9f0a",  # iOS Orange
                        "#64d2ff",  # iOS Cyan
                    ],
                    "borderColor": "#161618",
                    "borderWidth": 2,
                    "hoverOffset": 4,
                }
            ],
        }

        # Progress distribution chart
        progress_chart_data = {
            "labels": [p["name"] for p in phases],
            "datasets": [
                {
                    "label": "Progreso %",
                    "data": [p["progress"] for p in phases],
                    "backgroundColor": "#30d158",
                    "borderRadius": 6,
                }
            ],
        }

        return {
            "task": task,
            "chart_data": chart_data,
            "progress_chart_data": progress_chart_data,
            "overall_progress": task["overall_progress_percent"],
            "status": task["status"],
            "timestamp": utc_iso(),
        }

    def update_task_progress(self, progress: int, current_phase: Optional[str] = None) -> Dict[str, Any]:
        """Updates task progress percent."""
        self.active_task["overall_progress_percent"] = max(0, min(100, progress))
        if current_phase:
            self.active_task["current_phase"] = current_phase
        return self.get_task_telemetry()

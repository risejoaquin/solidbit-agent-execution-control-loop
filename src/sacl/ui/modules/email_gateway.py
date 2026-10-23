"""Email Gateway & Bi-directional Agent Automation Module for SACL UI.

Handles dispatching completion & gate decision emails to the operator (lawlieeet@outlook.es)
from the system address (lucilfer@selfcaresinners.com), as well as ingesting inbound emails
to autonomously trigger agent DAGs and workorders.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import logging
import os
import re
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("sacl.ui.modules.email_gateway")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class EmailGatewayModule:
    """Manages email notification dispatch and inbound email command triggers."""

    def __init__(
        self,
        sender_email: str = "lucilfer@selfcaresinners.com",
        operator_email: str = "lawlieeet@outlook.es",
        launch_campaign_cb: Optional[Callable[[str], Dict[str, Any]]] = None,
        host: str = "127.0.0.1",
        port: int = 8765,
    ) -> None:
        self.sender_email = sender_email
        self.operator_email = operator_email
        self.launch_campaign_cb = launch_campaign_cb
        self.host = host
        self.port = port
        self.authorized_senders = [operator_email.lower(), "lucilfer@selfcaresinners.com"]
        self.inbound_webhook_token = hashlib.sha256(b"solidbit-inbound-secret-salt").hexdigest()[:24]

        # In-memory audit trail of sent and received emails
        self.email_log: List[Dict[str, Any]] = [
            {
                "id": "EML-INIT-001",
                "direction": "OUTBOUND",
                "from": self.sender_email,
                "to": self.operator_email,
                "subject": "[SACL Decision Shell] Sistema de Notificaciones Inicializado",
                "status": "DELIVERED",
                "timestamp": utc_now_iso(),
                "summary": "Canal seguro de notificaciones y decisiones establecido para lawlieeet@outlook.es",
            }
        ]

    def get_config(self) -> Dict[str, Any]:
        """Returns the active email gateway configuration."""
        api_key = os.environ.get("RESEND_API_KEY", "")
        masked_key = f"{api_key[:6]}...{api_key[-4:]}" if len(api_key) > 10 else ("Configurada" if api_key else "No configurada (Modo Sandbox)")

        return {
            "sender_email": self.sender_email,
            "operator_email": self.operator_email,
            "authorized_senders": self.authorized_senders,
            "resend_status": "ACTIVE" if api_key else "SANDBOX_SIMULATED",
            "masked_api_key": masked_key,
            "inbound_webhook_url": f"http://{self.host}:{self.port}/api/webhooks/inbound-email?token={self.inbound_webhook_token}",
            "logs_count": len(self.email_log),
            "recent_logs": list(reversed(self.email_log[-10:])),
        }

    def update_config(
        self,
        sender_email: Optional[str] = None,
        operator_email: Optional[str] = None,
        resend_api_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Updates email addresses or Resend credentials."""
        if sender_email:
            self.sender_email = sender_email.strip()
        if operator_email:
            self.operator_email = operator_email.strip()
            if self.operator_email.lower() not in self.authorized_senders:
                self.authorized_senders.append(self.operator_email.lower())
        if resend_api_key:
            os.environ["RESEND_API_KEY"] = resend_api_key.strip()

        return {
            "success": True,
            "config": self.get_config(),
            "message": "Configuración de Email Gateway guardada correctamente.",
        }

    def send_task_completion_report(
        self,
        task_id: str,
        task_name: str,
        results_summary: str,
        gate_request_id: Optional[str] = None,
        quick_decide_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Sends an HTML completion report to the operator for micro-decision taking."""
        subject = f"[SACL · Tarea Completada] {task_name} (ID: {task_id[:12]})"

        if not quick_decide_url and gate_request_id:
            token = hashlib.sha256(f"{gate_request_id}-mobile-secret".encode("utf-8")).hexdigest()[:16]
            quick_decide_url = f"http://{self.host}:{self.port}/api/gates/quick-decide?request_id={gate_request_id}&token={token}&decision=APPROVED"

        log_entry = {
            "id": f"EML-OUT-{int(datetime.now().timestamp())}",
            "direction": "OUTBOUND",
            "from": self.sender_email,
            "to": self.operator_email,
            "subject": subject,
            "status": "SENT",
            "timestamp": utc_now_iso(),
            "summary": results_summary[:160],
            "quick_decide_url": quick_decide_url,
        }
        self.email_log.append(log_entry)

        # Dispatch via Resend API if key available, else log simulated
        api_key = os.environ.get("RESEND_API_KEY")
        if api_key:
            try:
                import urllib.request
                payload = {
                    "from": f"SolidBit SACL <{self.sender_email}>",
                    "to": [self.operator_email],
                    "subject": subject,
                    "html": f"""
                    <div style="font-family: -apple-system, sans-serif; max-width: 600px; margin: 0 auto; background: #000; color: #fff; padding: 24px; border-radius: 16px;">
                        <h2 style="color: #30d158; margin-top: 0;">SACL: Proceso de Agentes Completado</h2>
                        <p><strong>Tarea:</strong> {task_name}</p>
                        <p><strong>Resultados:</strong> {results_summary}</p>
                        <div style="margin: 24px 0; text-align: center;">
                            <a href="{quick_decide_url}" style="background: #30d158; color: #000; font-weight: bold; padding: 12px 24px; border-radius: 8px; text-decoration: none; display: inline-block;">
                                Autorizar y Desplegar Preview
                            </a>
                        </div>
                        <p style="font-size: 11px; color: #86868b;">Enviado desde {self.sender_email} hacia {self.operator_email}. SolidBit SACL Control Loop.</p>
                    </div>
                    """,
                }
                req = urllib.request.Request(
                    "https://api.resend.com/emails",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=5.0) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))
                    log_entry["resend_id"] = resp_data.get("id")
            except Exception as exc:
                logger.warning(f"Resend dispatch error: {exc}")
                log_entry["resend_error"] = str(exc)

        return {
            "success": True,
            "message": f"Reporte de resultados despachado exitosamente a {self.operator_email}",
            "log": log_entry,
        }

    def process_inbound_email(
        self,
        sender: str,
        subject: str,
        body_text: str,
    ) -> Dict[str, Any]:
        """Ingests an inbound email from the operator and triggers agent execution."""
        sender_clean = sender.lower().strip()
        # Extract email address if format is "Name <email@domain>"
        match = re.search(r"[\w\.-]+@[\w\.-]+", sender_clean)
        sender_addr = match.group(0) if match else sender_clean

        # Security Check: Verify sender authorization
        if sender_addr not in self.authorized_senders:
            log_entry = {
                "id": f"EML-IN-{int(datetime.now().timestamp())}",
                "direction": "INBOUND",
                "from": sender,
                "to": self.sender_email,
                "subject": subject,
                "status": "REJECTED_UNAUTHORIZED",
                "timestamp": utc_now_iso(),
                "summary": f"Intento no autorizado de {sender_addr}. Remitente bloqueado.",
            }
            self.email_log.append(log_entry)
            return {
                "success": False,
                "error": f"Remitente '{sender_addr}' no autorizado. Solo se aceptan correos de {self.operator_email}",
            }

        # Parse command from subject or body
        # E.g. "RUN SPRINT", "EJECUTAR CAMPAÑA", "TEST", "DEPLOY PREVIEW"
        command = f"{subject} {body_text}".upper()
        triggered_campaign = "SACL_ORCHESTRATOR_IMPLEMENTATION_CAMPAIGN_v1_PREPARED"

        action_detected = "AUTONOMOUS_SPRINT_TRIGGER"
        if "TEST" in command:
            action_detected = "RUN_AUTOMATED_TESTS"
        elif "PREVIEW" in command or "DEPLOY" in command:
            action_detected = "STAGE_PREVIEW_EXECUTION"

        # Trigger execution callback if registered
        launch_result = None
        if self.launch_campaign_cb:
            try:
                launch_result = self.launch_campaign_cb(triggered_campaign)
            except Exception as exc:
                launch_result = {"error": str(exc)}

        log_entry = {
            "id": f"EML-IN-{int(datetime.now().timestamp())}",
            "direction": "INBOUND",
            "from": sender,
            "to": self.sender_email,
            "subject": subject,
            "status": "ACCEPTED_AND_TRIGGERED",
            "timestamp": utc_now_iso(),
            "summary": f"Comando '{action_detected}' reconocido. Agentes puestos a trabajar en {triggered_campaign}.",
            "launch_result": launch_result,
        }
        self.email_log.append(log_entry)

        # Notify operator back that work has started
        self.send_task_completion_report(
            task_id=f"INBOUND-{int(datetime.now().timestamp())}",
            task_name=f"Ejecución iniciada por correo: {subject}",
            results_summary=f"Comando recibido de {sender_addr}. Los agentes de SACL están ejecutando el DAG con isolación de worktree.",
        )

        return {
            "success": True,
            "action": action_detected,
            "campaign_id": triggered_campaign,
            "message": f"Correo autenticado de {sender_addr}. Los agentes se han puesto a trabajar en la campaña.",
            "log": log_entry,
        }

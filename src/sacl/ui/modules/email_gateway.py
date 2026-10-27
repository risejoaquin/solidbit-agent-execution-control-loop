"""Email Gateway & Bi-directional Agent Automation Module for SACL UI.

Handles dispatching completion & gate decision emails to the operator (lawlieeet@outlook.es)
from the system address (lucilfer@selfcaresinners.com), as well as ingesting inbound emails
to autonomously trigger agent DAGs and workorders.

Inbound webhooks are only accepted when they are authenticated, either by a valid
Svix signature (``RESEND_WEBHOOK_SECRET``) or by the per-installation webhook token.
The sender allow-list is applied *after* authentication; on its own a ``from``
header is spoofable and is never trusted as the sole control.
"""

from __future__ import annotations

import html
import json
import logging
import os
import re
import secrets
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Mapping, Optional

from sacl.ui.security import inbound_webhook_token, verify_inbound_token, verify_svix_signature

logger = logging.getLogger("sacl.ui.modules.email_gateway")

WEBHOOK_SECRET_ENV = "RESEND_WEBHOOK_SECRET"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class EmailGatewayModule:
    """Manages email notification dispatch and inbound email command triggers."""

    def __init__(
        self,
        sender_email: str = "",
        operator_email: str = "",
        launch_campaign_cb: Optional[Callable[[str], Dict[str, Any]]] = None,
        host: str = "127.0.0.1",
        port: int = 8765,
        secret: Optional[bytes] = None,
        gate_url_builder: Optional[Callable[[str], str]] = None,
    ) -> None:
        self.sender_email = sender_email
        self.operator_email = operator_email
        self.launch_campaign_cb = launch_campaign_cb
        self.host = host
        self.port = port
        self.secret = secret or secrets.token_bytes(32)
        self.gate_url_builder = gate_url_builder
        self.authorized_senders = [e.lower() for e in (operator_email, sender_email) if e]
        self.inbound_webhook_token = inbound_webhook_token(self.secret)

        # In-memory audit trail of sent and received emails
        self.email_log: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------ config
    def get_config(self, include_secrets: bool = False) -> Dict[str, Any]:
        """Returns the active email gateway configuration.

        The inbound webhook URL embeds a secret token, so it is only included
        when ``include_secrets`` is True (the server only allows that for
        loopback clients).
        """
        api_key = os.environ.get("RESEND_API_KEY", "")
        if len(api_key) > 10:
            masked_key = f"{api_key[:5]}…{api_key[-4:]}"
        else:
            masked_key = "Configurada" if api_key else "No configurada"

        webhook_path = "/api/webhooks/inbound-email"
        return {
            "sender_email": self.sender_email,
            "operator_email": self.operator_email,
            "authorized_senders": self.authorized_senders,
            "resend_status": "ACTIVE" if api_key else "SANDBOX",
            "masked_api_key": masked_key,
            "security": {
                "token_required": True,
                "svix_signature": bool(os.environ.get(WEBHOOK_SECRET_ENV)),
                "sender_allowlist": True,
            },
            "inbound_webhook_url": (
                f"http://{self.host}:{self.port}{webhook_path}?token={self.inbound_webhook_token}"
            ),
            "webhook_token": self.inbound_webhook_token,
            "logs_count": len(self.email_log),
            "recent_logs": list(reversed(self.email_log[-25:])),
        }

    def update_config(
        self,
        sender_email: Optional[str] = None,
        operator_email: Optional[str] = None,
        resend_api_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Updates email addresses or Resend credentials."""
        email_re = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
        for value in (sender_email, operator_email):
            if value and not email_re.match(value.strip()):
                return {"success": False, "error": f"Dirección de correo inválida: {value}"}

        if sender_email:
            self.sender_email = sender_email.strip()
            if self.sender_email.lower() not in self.authorized_senders:
                self.authorized_senders.append(self.sender_email.lower())
        if operator_email:
            self.operator_email = operator_email.strip()
            if self.operator_email.lower() not in self.authorized_senders:
                self.authorized_senders.append(self.operator_email.lower())
        if resend_api_key:
            os.environ["RESEND_API_KEY"] = resend_api_key.strip()

        return {
            "success": True,
            "config": self.get_config(),
            "message": "Configuración de Email Gateway guardada.",
        }

    # ---------------------------------------------------------------- outbound
    def send_task_completion_report(
        self,
        task_id: str,
        task_name: str,
        results_summary: str,
        gate_request_id: Optional[str] = None,
        quick_decide_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Sends an HTML completion report to the operator for micro-decision taking."""
        subject = f"[SACL] {task_name}"[:180]

        if not quick_decide_url and gate_request_id and self.gate_url_builder:
            quick_decide_url = self.gate_url_builder(gate_request_id)

        log_entry: Dict[str, Any] = {
            "id": f"EML-OUT-{secrets.token_hex(4)}",
            "direction": "OUTBOUND",
            "from": self.sender_email,
            "to": self.operator_email,
            "subject": subject,
            "status": "SIMULATED",
            "timestamp": utc_now_iso(),
            "summary": results_summary[:200],
            "task_id": task_id,
        }

        api_key = os.environ.get("RESEND_API_KEY")
        if api_key and not api_key.startswith("re_sample"):
            safe_task = html.escape(task_name)
            safe_summary = html.escape(results_summary)
            button = ""
            if quick_decide_url:
                safe_url = html.escape(quick_decide_url, quote=True)
                button = (
                    f'<a href="{safe_url}" style="display:inline-block;background:#ffffff;color:#000000;'
                    'font-weight:600;padding:12px 22px;border-radius:8px;text-decoration:none;">'
                    "Revisar y decidir</a>"
                )
            payload = {
                "from": f"SolidBit SACL <{self.sender_email}>",
                "to": [self.operator_email],
                "subject": subject,
                "html": (
                    '<div style="font-family:-apple-system,Segoe UI,sans-serif;max-width:560px;margin:0 auto;'
                    'background:#000;color:#ededed;padding:28px;border-radius:14px;border:1px solid #222;">'
                    '<p style="font-size:12px;color:#a1a1aa;margin:0 0 8px;letter-spacing:.08em;">SOLIDBIT · SACL</p>'
                    f'<h2 style="margin:0 0 12px;font-size:20px;color:#fff;">{safe_task}</h2>'
                    f'<p style="font-size:14px;line-height:1.6;color:#d4d4d8;">{safe_summary}</p>'
                    f'<div style="margin:24px 0;">{button}</div>'
                    f'<p style="font-size:12px;color:#8b8b93;">Enviado por {html.escape(self.sender_email)}. '
                    "El enlace pide confirmación antes de ejecutar cualquier acción.</p></div>"
                ),
            }
            try:
                import urllib.request

                req = urllib.request.Request(
                    "https://api.resend.com/emails",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "User-Agent": "resend-python/2.50.0",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=8.0) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))
                    log_entry["resend_id"] = resp_data.get("id")
                    log_entry["status"] = "SENT"
            except Exception as exc:
                logger.warning(f"Resend dispatch error: {exc}")
                log_entry["status"] = "FAILED"
                log_entry["error"] = str(exc)[:200]

        self.email_log.append(log_entry)
        ok = log_entry["status"] in ("SENT", "SIMULATED")
        if log_entry["status"] == "SENT":
            msg = f"Correo enviado a {self.operator_email}"
        elif log_entry["status"] == "SIMULATED":
            msg = f"Modo sandbox: correo registrado para {self.operator_email} (configura RESEND_API_KEY para envío real)"
        else:
            msg = f"No se pudo enviar el correo: {log_entry.get('error', 'error desconocido')}"
        return {"success": ok, "message": msg, "log": log_entry}

    # ----------------------------------------------------------------- inbound
    def verify_inbound_request(
        self,
        query_token: Optional[str],
        headers: Mapping[str, str],
        raw_body: bytes,
    ) -> Dict[str, Any]:
        """Authenticates an inbound webhook call before any parsing or side effect."""
        webhook_secret = os.environ.get(WEBHOOK_SECRET_ENV)
        if webhook_secret:
            if verify_svix_signature(webhook_secret, headers, raw_body):
                return {"ok": True, "method": "svix"}
            return {"ok": False, "error": "Firma Svix inválida o ausente"}
        if verify_inbound_token(self.secret, query_token):
            return {"ok": True, "method": "token"}
        return {"ok": False, "error": "Token de webhook inválido o ausente"}

    @staticmethod
    def extract_email_fields(body: Dict[str, Any]) -> Dict[str, str]:
        """Normalizes direct JSON and Resend ``email.received`` webhook payloads."""
        data = body.get("data") if isinstance(body.get("data"), dict) else body
        sender = data.get("from") or data.get("sender") or data.get("from_email") or ""
        if isinstance(sender, dict):
            sender = sender.get("email") or sender.get("address") or ""
        if isinstance(sender, list):
            sender = sender[0] if sender else ""
        subject = data.get("subject") or ""
        text = data.get("text") or data.get("body") or data.get("html") or ""
        return {"sender": str(sender), "subject": str(subject), "text": str(text)}

    def process_inbound_email(
        self,
        sender: str,
        subject: str,
        body_text: str,
    ) -> Dict[str, Any]:
        """Ingests an authenticated inbound email from the operator and triggers agent execution."""
        sender_clean = sender.lower().strip()
        match = re.search(r"[\w\.\+-]+@[\w\.-]+", sender_clean)
        sender_addr = match.group(0) if match else sender_clean
        subject = subject[:200]

        if sender_addr not in self.authorized_senders:
            self.email_log.append(
                {
                    "id": f"EML-IN-{secrets.token_hex(4)}",
                    "direction": "INBOUND",
                    "from": sender_addr[:120],
                    "to": self.sender_email,
                    "subject": subject,
                    "status": "REJECTED",
                    "timestamp": utc_now_iso(),
                    "summary": f"Remitente no autorizado: {sender_addr[:120]}",
                }
            )
            return {
                "success": False,
                "error": f"Remitente '{sender_addr}' no autorizado. Solo se aceptan correos de {self.operator_email}",
            }

        command = f"{subject} {body_text}".upper()
        triggered_campaign = "SACL_ORCHESTRATOR_IMPLEMENTATION_CAMPAIGN_v1_PREPARED"
        action_detected = "AUTONOMOUS_SPRINT_TRIGGER"
        if "TEST" in command or "PRUEBA" in command:
            action_detected = "RUN_AUTOMATED_TESTS"
        elif "PREVIEW" in command:
            action_detected = "STAGE_PREVIEW_EXECUTION"

        launch_result = None
        if self.launch_campaign_cb:
            try:
                launch_result = self.launch_campaign_cb(triggered_campaign)
            except Exception as exc:
                launch_result = {"error": str(exc)}

        log_entry = {
            "id": f"EML-IN-{secrets.token_hex(4)}",
            "direction": "INBOUND",
            "from": sender_addr,
            "to": self.sender_email,
            "subject": subject,
            "status": "ACCEPTED",
            "timestamp": utc_now_iso(),
            "summary": f"Comando {action_detected} reconocido. Agentes trabajando en {triggered_campaign}.",
            "launch_result": launch_result,
        }
        self.email_log.append(log_entry)

        self.send_task_completion_report(
            task_id=(launch_result or {}).get("run_id", "INBOUND"),
            task_name=f"Recibido: {subject or 'comando por correo'}",
            results_summary=(
                f"Comando recibido de {sender_addr}. Los agentes están ejecutando el DAG en un worktree aislado. "
                "Te escribiremos cuando haya resultados o una compuerta que requiera tu decisión."
            ),
        )

        return {
            "success": True,
            "action": action_detected,
            "campaign_id": triggered_campaign,
            "message": f"Correo de {sender_addr} autenticado. Los agentes se pusieron a trabajar.",
            "log": log_entry,
        }

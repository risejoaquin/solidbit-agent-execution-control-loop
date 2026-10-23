"""SACL V1 Local Decision Shell Web Server with SSE and Remote Gate Approval.

Lightweight, high-performance embedded HTTP server powering the Apple-grade
operator UI, micro-decision center, SSE live streams, and mobile gate authorizations.
"""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import logging
from pathlib import Path
import threading
import time
from typing import Any, Dict, List, Optional, Tuple, Union
import urllib.parse

from sacl.ui.service import UIService
from sacl.ui.templates import HTML_APPLICATION

logger = logging.getLogger("sacl.ui.server")

# Active SSE listeners
_sse_clients: List[BaseHTTPRequestHandler] = []
_sse_lock = threading.Lock()


def broadcast_sse(event_type: str, data: Any) -> None:
    """Broadcasts an instant real-time event to all connected UI clients."""
    payload = f"event: {event_type}\ndata: {json.dumps(data)}\n\n".encode("utf-8")
    with _sse_lock:
        dead_clients = []
        for client in _sse_clients:
            try:
                client.wfile.write(payload)
                client.wfile.flush()
            except Exception:
                dead_clients.append(client)
        for dead in dead_clients:
            if dead in _sse_clients:
                _sse_clients.remove(dead)


class DecisionShellRequestHandler(BaseHTTPRequestHandler):
    """Handles REST API, SSE streaming, and static UI delivery for the SACL Decision Shell."""

    service: UIService

    def _send_json(self, status_code: int, data: Any) -> None:
        payload = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def _send_html(self, status_code: int, html_str: str) -> None:
        payload = html_str.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self) -> None:
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        # 1. Root / UI Shell
        if path in ("/", "/index.html", "/ui"):
            self._send_html(200, HTML_APPLICATION)
            return

        # 2. Server-Sent Events (SSE) Live Stream: /api/events/stream
        if path == "/api/events/stream":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            with _sse_lock:
                _sse_clients.append(self)

            # Send initial snapshot immediately
            try:
                snap = self.service.get_dashboard_snapshot()
                init_msg = f"event: snapshot\ndata: {json.dumps(snap.to_dict())}\n\n".encode("utf-8")
                self.wfile.write(init_msg)
                self.wfile.flush()

                # Keep stream alive
                while True:
                    time.sleep(15)
                    self.wfile.write(b": heartbeat\n\n")
                    self.wfile.flush()
            except (ConnectionResetError, BrokenPipeError):
                pass
            finally:
                with _sse_lock:
                    if self in _sse_clients:
                        _sse_clients.remove(self)
            return

        # 3. REST API: Dashboard Snapshot
        if path == "/api/snapshot":
            mode = query.get("mode", ["simple"])[0]
            snap = self.service.get_dashboard_snapshot(mode=mode)
            self._send_json(200, snap.to_dict())
            return

        # 4. REST API: Human Decision Gates
        if path == "/api/gates":
            gates = [g.to_dict() for g in self.service.get_pending_gates()]
            self._send_json(200, {"gates": gates, "count": len(gates)})
            return

        if path == "/api/gates/impact":
            req_id = query.get("request_id", [""])[0]
            impact = self.service.gates.get_gate_impact_details(req_id)
            self._send_json(200, impact)
            return

        # 5. Remote / Mobile Quick Decision Gateway
        if path == "/api/gates/quick-decide":
            req_id = query.get("request_id", [""])[0]
            decision = query.get("decision", ["APPROVED"])[0]

            res = self.service.submit_gate_decision(
                request_id=req_id,
                decision_str=decision,
                approver_id="mobile_operator",
                justification="Autorizado vía Mobile Quick Decision Link",
            )
            broadcast_sse("gate_decided", res)

            # Mobile-friendly Apple landing page
            status_color = "#30d158" if decision == "APPROVED" else "#ff453a"
            status_text = "Acción Autorizada con Éxito" if decision == "APPROVED" else "Acción Rechazada de Forma Segura"
            html = f"""<!DOCTYPE html>
            <html lang="es">
            <head>
              <meta name="viewport" content="width=device-width, initial-scale=1.0">
              <title>SolidBit Mobile Gate</title>
              <style>
                body {{ background: #000; color: #fff; font-family: -apple-system, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; text-align: center; }}
                .card {{ background: rgba(30,30,38,0.9); border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; padding: 32px 24px; max-width: 360px; margin: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.8); }}
                .badge {{ background: {status_color}; color: #000; font-weight: 700; padding: 6px 16px; border-radius: 20px; font-size: 13px; display: inline-block; margin-bottom: 16px; }}
                h1 {{ font-size: 20px; margin-bottom: 8px; }}
                p {{ font-size: 13px; color: #86868b; line-height: 1.5; }}
              </style>
            </head>
            <body>
              <div class="card">
                <div class="badge">{decision}</div>
                <h1>{status_text}</h1>
                <p>La micro-decisión ha sido registrada en el control loop de tu servidor local. El DAG continúa ejecutándose según las reglas de seguridad.</p>
              </div>
            </body>
            </html>"""
            self._send_html(200, html)
            return

        # 6. REST API: Technology Connections
        if path == "/api/connections":
            conns = [c.to_dict() for c in self.service.check_technology_connections()]
            self._send_json(200, {"connections": conns, "count": len(conns)})
            return

        # 7. REST API: Campaigns & DAG
        if path == "/api/campaigns":
            overview = self.service.campaigns.get_campaigns_overview()
            self._send_json(200, overview)
            return

        # 8. REST API: Recovery Center
        if path == "/api/recovery":
            recovery = self.service.recovery.get_recovery_status()
            self._send_json(200, recovery)
            return

        # 9. REST API: Evidence Center
        if path == "/api/evidence":
            evidence_files = self.service.evidence.list_evidence()
            self._send_json(200, {"files": evidence_files, "count": len(evidence_files)})
            return

        if path == "/api/evidence/view":
            filename = query.get("file", [""])[0]
            report = self.service.evidence.read_report(filename)
            self._send_json(200, report)
            return

        # 10. REST API: Contracts & Policies
        if path == "/api/contracts":
            policies = self.service.contracts.get_policies_overview()
            self._send_json(200, policies)
            return

        # 11. REST API: Database Inspector
        if path == "/api/db/stats":
            stats = self.service.db_inspector.get_database_stats()
            self._send_json(200, stats)
            return

        # 404
        self._send_json(404, {"error": "Not Found", "path": path})

    def do_POST(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        content_len = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
        try:
            body = json.loads(post_data) if post_data else {}
        except Exception:
            body = {}

        # 1. Gate Micro-Decision
        if path == "/api/gates/decide":
            req_id = body.get("request_id")
            decision = body.get("decision", "REJECTED")
            justification = body.get("justification", "Decidido vía Decision Shell")

            if not req_id:
                self._send_json(400, {"error": "Missing 'request_id' parameter"})
                return

            result = self.service.submit_gate_decision(
                request_id=req_id,
                decision_str=decision,
                justification=justification,
            )
            broadcast_sse("gate_decided", result)
            self._send_json(200, result)
            return

        # 2. Gate Mobile Notification
        if path == "/api/gates/notify":
            req_id = body.get("request_id")
            channel = body.get("channel", "resend")
            res = self.service.gates.notify_mobile(req_id, channel=channel)
            self._send_json(200, res)
            return

        # 3. Connection Targeted Test
        if path == "/api/connections/test":
            tool_id = body.get("tool_id", "")
            res = self.service.connections.test_single(tool_id)
            self._send_json(200, res)
            return

        # 4. Connection E2E Authentication
        if path == "/api/connections/auth":
            tool_id = body.get("tool_id", "")
            credentials = body.get("credentials", {})
            res = self.service.connections.authenticate_e2e(tool_id, credentials)
            broadcast_sse("connection_updated", res)
            self._send_json(200, res)
            return

        # 5. Campaign 1-Click Launch
        if path == "/api/campaigns/launch":
            camp_id = body.get("campaign_id", "SACL_ORCHESTRATOR_IMPLEMENTATION_CAMPAIGN_v1_PREPARED")
            res = self.service.campaigns.launch_campaign(camp_id)
            broadcast_sse("campaign_launched", res)
            self._send_json(200, res)
            return

        self._send_json(404, {"error": "Not Found", "path": path})

    def log_message(self, format: str, *args: Any) -> None:
        pass


class DecisionShellServer:
    """Manages the lifecycle of the SACL Decision Shell web server."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8765,
        db_path: Optional[Union[Path, str]] = None,
        workspace_root: Optional[Union[Path, str]] = None,
    ) -> None:
        self.host = host
        self.port = port
        self.service = UIService(
            db_path=db_path,
            workspace_root=workspace_root,
            host=host,
            port=port,
        )
        self._server: Optional[ThreadingHTTPServer] = None
        self._thread: Optional[threading.Thread] = None

    def start(self, blocking: bool = False) -> Tuple[str, int]:
        """Starts the HTTP server."""
        class CustomHandler(DecisionShellRequestHandler):
            service = self.service

        self._server = ThreadingHTTPServer((self.host, self.port), CustomHandler)
        actual_port = self._server.server_address[1]
        self.port = actual_port
        self.service.port = actual_port
        self.service.gates.port = actual_port

        if blocking:
            print(f"[INFO] SACL Decision Shell running on http://{self.host}:{self.port}")
            try:
                self._server.serve_forever()
            except KeyboardInterrupt:
                self.stop()
        else:
            self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
            self._thread.start()

        return self.host, self.port

    def stop(self) -> None:
        """Shuts down the server."""
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None

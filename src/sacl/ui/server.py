"""SACL V1 Local Decision Shell Web Server.

Lightweight, high-performance embedded HTTP server powering the Apple-grade
operator UI and micro-decision center across all system modules.
"""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import logging
from pathlib import Path
import threading
from typing import Any, Dict, Optional, Tuple, Union
import urllib.parse

from sacl.ui.service import UIService
from sacl.ui.templates import HTML_APPLICATION

logger = logging.getLogger("sacl.ui.server")


class DecisionShellRequestHandler(BaseHTTPRequestHandler):
    """Handles REST API and static UI delivery for the SACL Decision Shell."""

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

        # 2. REST API: Dashboard Snapshot
        if path == "/api/snapshot":
            mode = query.get("mode", ["simple"])[0]
            snap = self.service.get_dashboard_snapshot(mode=mode)
            self._send_json(200, snap.to_dict())
            return

        # 3. REST API: Human Decision Gates
        if path == "/api/gates":
            gates = [g.to_dict() for g in self.service.get_pending_gates()]
            self._send_json(200, {"gates": gates, "count": len(gates)})
            return

        if path == "/api/gates/history":
            history = self.service.gates.get_gate_history()
            self._send_json(200, {"history": history, "count": len(history)})
            return

        # 4. REST API: Technology Connections
        if path == "/api/connections":
            conns = [c.to_dict() for c in self.service.check_technology_connections()]
            self._send_json(200, {"connections": conns, "count": len(conns)})
            return

        # 5. REST API: Campaigns & DAG
        if path == "/api/campaigns":
            overview = self.service.campaigns.get_campaigns_overview()
            self._send_json(200, overview)
            return

        # 6. REST API: Recovery Center
        if path == "/api/recovery":
            recovery = self.service.recovery.get_recovery_status()
            self._send_json(200, recovery)
            return

        # 7. REST API: Evidence Center
        if path == "/api/evidence":
            evidence_files = self.service.evidence.list_evidence()
            self._send_json(200, {"files": evidence_files, "count": len(evidence_files)})
            return

        if path == "/api/evidence/view":
            filename = query.get("file", [""])[0]
            report = self.service.evidence.read_report(filename)
            self._send_json(200, report)
            return

        # 8. REST API: Contracts & Policies
        if path == "/api/contracts":
            policies = self.service.contracts.get_policies_overview()
            self._send_json(200, policies)
            return

        # 9. REST API: Database Inspector
        if path == "/api/db/stats":
            stats = self.service.db_inspector.get_database_stats()
            self._send_json(200, stats)
            return

        if path == "/api/db/events":
            events = self.service.db_inspector.get_recent_audit_events()
            self._send_json(200, {"events": events, "count": len(events)})
            return

        # 404
        self._send_json(404, {"error": "Not Found", "path": path})

    def do_POST(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        # 1. Gate Micro-Decision
        if path == "/api/gates/decide":
            content_len = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_len).decode("utf-8")
            try:
                body = json.loads(post_data)
                req_id = body.get("request_id")
                decision = body.get("decision", "REJECTED")
                justification = body.get("justification", "Decided via Decision Shell")

                if not req_id:
                    self._send_json(400, {"error": "Missing 'request_id' parameter"})
                    return

                result = self.service.submit_gate_decision(
                    request_id=req_id,
                    decision_str=decision,
                    justification=justification,
                )
                self._send_json(200, result)
            except Exception as exc:
                self._send_json(500, {"error": str(exc)})
            return

        # 2. Connection targeted test
        if path == "/api/connections/test":
            content_len = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_len).decode("utf-8")
            try:
                body = json.loads(post_data)
                tool_id = body.get("tool_id", "")
                res = self.service.connections.test_single(tool_id)
                self._send_json(200, res)
            except Exception as exc:
                self._send_json(500, {"error": str(exc)})
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
        self.service = UIService(db_path=db_path, workspace_root=workspace_root)
        self._server: Optional[ThreadingHTTPServer] = None
        self._thread: Optional[threading.Thread] = None

    def start(self, blocking: bool = False) -> Tuple[str, int]:
        """Starts the HTTP server."""
        class CustomHandler(DecisionShellRequestHandler):
            service = self.service

        self._server = ThreadingHTTPServer((self.host, self.port), CustomHandler)
        actual_port = self._server.server_address[1]
        self.port = actual_port

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

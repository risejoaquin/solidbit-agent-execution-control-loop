"""Slash Command and Context Mention Registry for SolidBit SACL UI.

Provides the full Google Antigravity slash commands specification (/plan,
/goal, /schedule, /audit, /diff, /boost, /plugin, etc.) plus dynamic
discovery of installed skills (/<skill_id>) and @-mention context providers.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from sacl.engine.workflow_engine import WorkflowEngine

logger = logging.getLogger("sacl.ui.modules.slash_commands")


@dataclass
class SlashCommand:
    command: str
    label: str
    description: str
    category: str  # "workflow" | "core" | "governance" | "devtools"
    syntax: str
    example: str
    requires_arg: bool = False
    arg_placeholder: Optional[str] = None


class SlashCommandRegistry:
    """Manages the catalogue of slash commands and @mentions."""

    def __init__(self, workspace_root: Optional[Path] = None, workflow_engine: Optional[WorkflowEngine] = None) -> None:
        self.workspace_root = workspace_root or Path.cwd()
        self.workflow_engine = workflow_engine or WorkflowEngine(self.workspace_root)

    def get_builtin_commands(self) -> List[SlashCommand]:
        return [
            SlashCommand(
                command="/plan",
                label="Planificador DAG",
                description="Diseña un plan riguroso paso a paso con particionado de Kahn antes de ejecutar.",
                category="core",
                syntax="/plan <objetivo>",
                example="/plan Implementar endpoint de reservas atómicas",
                requires_arg=True,
                arg_placeholder="Objetivo de la planificación...",
            ),
            SlashCommand(
                command="/goal",
                label="Misión Autónoma Prolongada",
                description="Ejecución iterativa profunda sin detenerse hasta verificar la meta con tests e invariantes.",
                category="core",
                syntax="/goal <meta>",
                example="/goal Completar migración de schema y validar 100% tests",
                requires_arg=True,
                arg_placeholder="Meta técnica a alcanzar...",
            ),
            SlashCommand(
                command="/audit",
                label="Auditoría de Invariantes SolidBit",
                description="Verifica de forma estricta los contratos congelados DR-INV-001, DR-PAY-001 y Hard Deny.",
                category="governance",
                syntax="/audit [contrato]",
                example="/audit DR-INV-001",
                requires_arg=False,
                arg_placeholder="Contrato opcional...",
            ),
            SlashCommand(
                command="/diff",
                label="Inspector Visual de Diffs",
                description="Abre el visualizador de cambios pendientes y diffs en el worktree actual.",
                category="devtools",
                syntax="/diff [archivo]",
                example="/diff",
                requires_arg=False,
                arg_placeholder="Ruta opcional...",
            ),
            SlashCommand(
                command="/schedule",
                label="Automatización / Cron",
                description="Programa un temporizador de una sola vez o un cron recurrente en segundo plano.",
                category="core",
                syntax="/schedule <expresión cron o segundos>",
                example="/schedule 0 8 * * 1 Revisar estado de stock diario",
                requires_arg=True,
                arg_placeholder="*/15 * * * * o 300s...",
            ),
            SlashCommand(
                command="/boost",
                label="Razonamiento Profundo",
                description="Activa el modo de pensamiento analítico intensivo y verificación rigurosa.",
                category="core",
                syntax="/boost <pregunta>",
                example="/boost Analizar consistencia en caso de fallo de red en pagos",
                requires_arg=True,
                arg_placeholder="Problema o consulta compleja...",
            ),
            SlashCommand(
                command="/grill-me",
                label="Entrevista de Decisiones de Diseño",
                description="El asistente entrevista al operador para resolver decisiones arquitectónicas críticas.",
                category="governance",
                syntax="/grill-me [tema]",
                example="/grill-me Arquitectura de checkout",
                requires_arg=False,
            ),
            SlashCommand(
                command="/teamwork-preview",
                label="Enjambre Multi-Agente",
                description="Coordina un equipo de agentes autónomos especializados trabajando en paralelo.",
                category="core",
                syntax="/teamwork-preview <misión>",
                example="/teamwork-preview Refactorizar capa de persistencia",
                requires_arg=True,
            ),
            SlashCommand(
                command="/learn",
                label="Persistir Regla / Memoria",
                description="Registra una nueva convención o comportamiento persistente para futuras sesiones.",
                category="devtools",
                syntax="/learn <regla o solución>",
                example="/learn Siempre validar PRAGMA integrity_check antes de commit",
                requires_arg=True,
            ),
            SlashCommand(
                command="/browser",
                label="Navegador Web / Investigación",
                description="Delega búsqueda y navegación web documental a un subagente especializado.",
                category="devtools",
                syntax="/browser <búsqueda o url>",
                example="/browser Docs de Resend API rate limits",
                requires_arg=True,
            ),
            SlashCommand(
                command="/plugin",
                label="Gestión de Plugins y Skills",
                description="Inspecciona el catálogo de plugins y extensiones instaladas en Antigravity.",
                category="devtools",
                syntax="/plugin [listar | info <id>]",
                example="/plugin",
                requires_arg=False,
            ),
            SlashCommand(
                command="/reconcile",
                label="Reconciliación de Procesos SQLite",
                description="Revisa y normaliza estados zombis en el ledger sacl_ops.db hacia CLEAN_STEADY.",
                category="governance",
                syntax="/reconcile",
                example="/reconcile",
                requires_arg=False,
            ),
        ]

    def get_all_commands(self) -> List[Dict[str, Any]]:
        """Returns built-in commands plus dynamically discovered skills."""
        commands = [asdict(cmd) for cmd in self.get_builtin_commands()]

        # Discover dynamic skills
        skills = self.workflow_engine.discover_skills()
        for s in skills:
            # Avoid duplicate if command already in builtin
            cmd_name = s["slash_command"]
            if not any(c["command"] == cmd_name for c in commands):
                commands.append({
                    "command": cmd_name,
                    "label": f"Workflow: {s['name']}",
                    "description": s["description"],
                    "category": "workflow",
                    "syntax": f"{cmd_name} [parámetros]",
                    "example": f"{cmd_name} {s.get('parameters', [{}])[0].get('placeholder', '')}",
                    "requires_arg": False,
                    "skill_id": s["id"],
                    "scope": s["scope"],
                })

        return commands

    def get_mention_suggestions(self) -> Dict[str, List[Dict[str, Any]]]:
        """Returns contextual mention suggestions categorized by type."""
        contracts = [
            {"id": "DR-INV-001", "name": "SellableUnit & Double-Entry Ledger", "desc": "Invariante de no-sobreventa y ledger atómico", "category": "contract"},
            {"id": "DR-PAY-001", "name": "Payment Idempotency & Auth Expiry", "desc": "Idempotencia estricta en cobros y reservas", "category": "contract"},
            {"id": "DR-IDEM-001", "name": "Idempotent Transaction Enforcer", "desc": "Prevención de procesamiento duplicado", "category": "contract"},
            {"id": "DR-AUTH-001", "name": "HMAC-SHA256 Gate Authorization", "desc": "Firma criptográfica con TTL de 15 minutos", "category": "contract"},
        ]

        jira_tickets = [
            {"id": "SOLID-101", "name": "SOLID-101: Gobernanza e Invariantes", "desc": "Hard Deny Supremacy & Reglas Estáticas", "category": "jira"},
            {"id": "SOLID-102", "name": "SOLID-102: SellableUnit Stock Engine", "desc": "Inventario atómico sin condiciones de carrera", "category": "jira"},
            {"id": "SOLID-103", "name": "SOLID-103: Ledger de Pagos Idempotente", "desc": "Doble partida contable bancaria", "category": "jira"},
            {"id": "SOLID-104", "name": "SOLID-104: Aislamiento Git Worktree", "desc": "Ramas efímeras con Dirty-Root check", "category": "jira"},
            {"id": "SOLID-105", "name": "SOLID-105: SQLite WAL & Recuperación", "desc": "22 Dominios persistentes y crash-consistent", "category": "jira"},
            {"id": "SOLID-106", "name": "SOLID-106: Carrito, Checkout & Integración", "desc": "Flujo de compra E-commerce MVP", "category": "jira"},
        ]

        db_tables = [
            {"id": "jobs", "name": "jobs", "desc": "Trabajos globales de orquestación", "category": "table"},
            {"id": "runs", "name": "runs", "desc": "Ejecuciones individuales de agentes", "category": "table"},
            {"id": "events", "name": "events", "desc": "Log append-only de eventos del sistema", "category": "table"},
            {"id": "approvals", "name": "approvals", "desc": "Compuertas HITL soberanas y firmas HMAC", "category": "table"},
            {"id": "artifacts", "name": "artifacts", "desc": "Entregables físicos verificados en disco", "category": "table"},
            {"id": "connections", "name": "connections", "desc": "Estado de las herramientas conectadas", "category": "table"},
        ]

        # Scan top 15 key project files
        files: List[Dict[str, Any]] = []
        try:
            for p in self.workspace_root.rglob("*"):
                if p.is_file() and not any(part.startswith(".") or part in ("node_modules", "dist", "__pycache__") for part in p.parts):
                    rel = str(p.relative_to(self.workspace_root)).replace("\\", "/")
                    if rel.endswith((".py", ".tsx", ".ts", ".json", ".md", ".toml", ".sql")):
                        files.append({"id": rel, "name": rel, "desc": f"Archivo ({p.suffix})", "category": "file"})
                        if len(files) >= 25:
                            break
        except Exception:
            pass

        return {
            "contracts": contracts,
            "jira": jira_tickets,
            "tables": db_tables,
            "files": files,
        }

"""Tests for Google Antigravity equivalency modules in SolidBit SACL:
- WorkflowEngine & Skills Execution
- GitDiffModule & Working Tree telemetry
- SlashCommandRegistry & @-mentions
- SubagentsManager lifecycle
- HTTP endpoints
"""

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pytest

from sacl.engine.workflow_engine import WorkflowEngine
from sacl.state.connection import create_connection
from sacl.state.migrations import MigrationRunner
from sacl.ui.modules.diff import GitDiffModule
from sacl.ui.modules.slash_commands import SlashCommandRegistry
from sacl.ui.modules.subagents_manager import SubagentsManager
from sacl.ui.server import DecisionShellServer


@pytest.fixture
def running_server(tmp_path: Path, migration_sql_path: Path):
    db_file = tmp_path / "sacl_ops.db"
    conn = create_connection(db_file)
    runner = MigrationRunner(migration_sql_path.parent)
    runner.apply_all(conn)

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    conn.execute(
        """
        INSERT INTO jobs (job_id, status, priority, created_at, updated_at)
        VALUES ('job-antigravity', 'RUNNING', 0, ?, ?);
        """,
        (now_iso, now_iso),
    )
    conn.commit()
    conn.close()

    server = DecisionShellServer(
        host="127.0.0.1",
        port=0,
        db_path=db_file,
    )
    host, port = server.start(blocking=False)
    yield host, port, db_file, server
    server.stop()


def test_workflow_engine_discovery(tmp_path: Path):
    # Create sample skill in tmp workspace
    skills_dir = tmp_path / ".agents" / "skills" / "custom-deploy"
    skills_dir.mkdir(parents=True)
    skill_md = skills_dir / "SKILL.md"
    skill_md.write_text(
        """---
name: Custom Deploy
description: Despliegue continuo en Railway con invariantes verificados.
---
# Instrucciones de Despliegue
Ejecutar paso 1, paso 2 y paso 3.
""",
        encoding="utf-8",
    )

    engine = WorkflowEngine(workspace_root=tmp_path)
    skills = engine.discover_skills()
    assert len(skills) >= 1
    custom_skill = next((s for s in skills if s["id"] == "custom-deploy"), None)
    assert custom_skill is not None
    assert custom_skill["name"] == "Custom Deploy"
    assert "Railway" in custom_skill["description"]
    assert custom_skill["scope"] == "workspace"
    assert custom_skill["slash_command"] == "/custom-deploy"


def test_workflow_engine_execution(tmp_path: Path):
    engine = WorkflowEngine(workspace_root=tmp_path)
    # Execute built-in / general skill
    res = engine.execute_skill("solidbit-sdlc", {"goal": "Verificar contratos de release"})
    assert res["success"] is True
    assert res["status"] == "COMPLETED"
    assert len(res["steps"]) >= 3
    assert len(res["deliverables"]) >= 1


def test_git_diff_module(tmp_path: Path):
    diff_mod = GitDiffModule(workspace_root=Path.cwd())
    status = diff_mod.get_status()
    assert status["success"] is True
    assert "branch" in status
    assert "files" in status

    diff = diff_mod.get_unified_diff()
    assert diff["success"] is True
    assert "total_files" in diff
    assert "files" in diff


def test_slash_command_registry():
    registry = SlashCommandRegistry(workspace_root=Path.cwd())
    commands = registry.get_all_commands()
    cmd_names = [c["command"] for c in commands]

    # Verify standard Antigravity commands are present
    assert "/plan" in cmd_names
    assert "/goal" in cmd_names
    assert "/schedule" in cmd_names
    assert "/audit" in cmd_names
    assert "/diff" in cmd_names
    assert "/boost" in cmd_names
    assert "/learn" in cmd_names
    assert "/browser" in cmd_names

    mentions = registry.get_mention_suggestions()
    assert len(mentions["contracts"]) >= 4
    assert len(mentions["jira"]) >= 5
    assert len(mentions["tables"]) >= 4


def test_subagents_manager():
    mgr = SubagentsManager(workspace_root=Path.cwd())
    res = mgr.list_subagents_and_tasks()
    assert res["success"] is True
    assert len(res["tasks"]) >= 2

    logs = mgr.get_task_logs(res["tasks"][0]["id"])
    assert logs["success"] is True
    assert len(logs["lines"]) > 0

    kill_res = mgr.kill_task("test-task-1")
    assert kill_res["success"] is True


def test_antigravity_http_endpoints(running_server):
    host, port, *_ = running_server

    # 1. GET /api/skills
    req = urllib.request.Request(f"http://{host}:{port}/api/skills")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["success"] is True
        assert len(data["skills"]) >= 2

    # 2. GET /api/git/status
    req = urllib.request.Request(f"http://{host}:{port}/api/git/status")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["success"] is True

    # 3. GET /api/commands/registry
    req = urllib.request.Request(f"http://{host}:{port}/api/commands/registry")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["success"] is True
        assert any(c["command"] == "/plan" for c in data["commands"])

    # 4. GET /api/commands/mentions
    req = urllib.request.Request(f"http://{host}:{port}/api/commands/mentions")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["success"] is True
        assert "contracts" in data["mentions"]

    # 5. GET /api/subagents/list
    req = urllib.request.Request(f"http://{host}:{port}/api/subagents/list")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["success"] is True
        assert len(data["tasks"]) >= 1

    # 6. POST /api/chat/message with slash command /diff
    post_req = urllib.request.Request(
        f"http://{host}:{port}/api/chat/message",
        data=json.dumps({"prompt": "/diff"}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(post_req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["success"] is True
        assert "Inspector de Cambios Git" in data["assistant_message"]["content"]
        assert len(data["assistant_message"].get("tool_calls", [])) >= 1

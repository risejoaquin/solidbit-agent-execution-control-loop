"""LLM Model Selector & Parameter Configuration Module for SACL UI.

Allows operators and architects to configure the sovereign agent engine,
switch models, tune temperatures, and enforce bounded reasoning guardrails.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("sacl.ui.modules.models")


class ModelsModule:
    """Manages AI model selection, provider routing, and agent reasoning parameters."""

    AVAILABLE_MODELS = [
        {
            "id": "claude-3-7-sonnet",
            "name": "Claude 3.7 Sonnet",
            "provider": "Anthropic",
            "tier": "Flagship Hybrid",
            "badge": "Recommended",
            "description": "State-of-the-art hybrid reasoning for strict code generation and architecture invariants.",
            "context_window": "200k",
            "default_temp": 0.2,
        },
        {
            "id": "claude-3-5-sonnet",
            "name": "Claude 3.5 Sonnet",
            "provider": "Anthropic",
            "tier": "Code Specialist",
            "badge": "Proven",
            "description": "High-speed code synthesis, refactoring, and deterministic test writing.",
            "context_window": "200k",
            "default_temp": 0.1,
        },
        {
            "id": "gemini-2-flash",
            "name": "Gemini 2.0 Flash",
            "provider": "Google DeepMind",
            "tier": "Ultra-Low Latency",
            "badge": "Fast",
            "description": "Sub-second step transitions for fast DAG triage and real-time validations.",
            "context_window": "1M",
            "default_temp": 0.3,
        },
        {
            "id": "gemini-1-5-pro",
            "name": "Gemini 1.5 Pro",
            "provider": "Google DeepMind",
            "tier": "Massive Context",
            "badge": "Deep Context",
            "description": "Full-codebase multi-file analysis, cross-repository audits, and monolithic reviews.",
            "context_window": "2M",
            "default_temp": 0.2,
        },
        {
            "id": "gpt-4o",
            "name": "OpenAI GPT-4o",
            "provider": "OpenAI",
            "tier": "Omni Multi-modal",
            "badge": "General",
            "description": "Versatile documentation synthesis, diagram interpretations, and schema validations.",
            "context_window": "128k",
            "default_temp": 0.2,
        },
        {
            "id": "deepseek-r1",
            "name": "DeepSeek R1 (Local / Ollama)",
            "provider": "Local/Open",
            "tier": "Autonomous Reasoner",
            "badge": "Private",
            "description": "Air-gapped on-premise execution with step-by-step mathematical reasoning.",
            "context_window": "64k",
            "default_temp": 0.6,
        },
    ]

    def __init__(self, default_model: str = "claude-3-7-sonnet") -> None:
        self.active_model_id = default_model
        self.temperature = 0.2
        self.max_tokens = 8192
        self.guardrails_enforced = True
        self.system_prompt_mode = "ARCHITECT_STRICT"

    def get_config(self) -> Dict[str, Any]:
        """Returns the current model configuration and catalog."""
        models = []
        for m in self.AVAILABLE_MODELS:
            item = dict(m)
            item["is_active"] = (m["id"] == self.active_model_id)
            models.append(item)

        active = next((m for m in self.AVAILABLE_MODELS if m["id"] == self.active_model_id), self.AVAILABLE_MODELS[0])

        return {
            "active_model": active,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "guardrails_enforced": self.guardrails_enforced,
            "system_prompt_mode": self.system_prompt_mode,
            "available_models": models,
        }

    def update_config(
        self,
        model_id: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        guardrails_enforced: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Updates active model or parameters."""
        if model_id:
            matched = next((m for m in self.AVAILABLE_MODELS if m["id"] == model_id), None)
            if not matched:
                return {"success": False, "error": f"Modelo '{model_id}' no disponible"}
            self.active_model_id = model_id
        if temperature is not None:
            self.temperature = max(0.0, min(1.0, float(temperature)))
        if max_tokens is not None:
            self.max_tokens = int(max_tokens)
        if guardrails_enforced is not None:
            self.guardrails_enforced = bool(guardrails_enforced)

        return {
            "success": True,
            "config": self.get_config(),
            "message": f"Configuración de modelo actualizada: {self.active_model_id}",
        }

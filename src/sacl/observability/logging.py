"""SACL V1 Structured Logging Subsystem.

Provides JSON-formatted and human-readable logging with automatic correlation
ID enrichment, file sink setup for worker logs, and audit event forwarding.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from sacl.observability.correlation import get_current_correlation
from sacl.observability.events import Severity


class JsonLogFormatter(logging.Formatter):
    """Formats log records as structured, single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        corr = get_current_correlation()

        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "trace_id": corr.trace_id,
        }

        if corr.job_id:
            log_data["job_id"] = corr.job_id
        if corr.run_id:
            log_data["run_id"] = corr.run_id
        if corr.node_id:
            log_data["node_id"] = corr.node_id
        if corr.agent_id:
            log_data["agent_id"] = corr.agent_id

        # Merge extra attributes if passed in record.__dict__
        standard_attrs = {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "exc_info",
            "exc_text",
            "stack_info",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
            "message",
        }
        extras = {
            k: v
            for k, v in record.__dict__.items()
            if k not in standard_attrs and not k.startswith("_")
        }
        if extras:
            log_data["extra"] = extras

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class TextLogFormatter(logging.Formatter):
    """Formats log records as human-readable lines with correlation context."""

    def format(self, record: logging.LogRecord) -> str:
        corr = get_current_correlation()
        iso_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        context_parts = []
        if corr.run_id:
            context_parts.append(f"run={corr.run_id}")
        if corr.agent_id:
            context_parts.append(f"agent={corr.agent_id}")
        elif corr.node_id:
            context_parts.append(f"node={corr.node_id}")

        context_str = f" [{', '.join(context_parts)}]" if context_parts else ""
        msg = record.getMessage()

        base = f"[{iso_time}] [{record.levelname:<5}]{context_str} [{record.name}] {msg}"
        if record.exc_info:
            base += "\n" + self.formatException(record.exc_info)
        return base


class StructuredLogger:
    """Wrapper around standard Logger that automatically injects correlation context

    and provides optional automatic audit event forwarding on critical severities.
    """

    def __init__(self, logger: logging.Logger, audit_sink: Optional[Callable[..., Any]] = None):
        self._logger = logger
        self.audit_sink = audit_sink

    @property
    def name(self) -> str:
        return self._logger.name

    def set_level(self, level: int | str) -> None:
        if isinstance(level, str):
            level = getattr(logging, level.upper(), logging.INFO)
        self._logger.setLevel(level)

    def _log(
        self,
        level: int,
        msg: str,
        *args: Any,
        audit: bool = False,
        audit_event_type: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        exc_info = kwargs.pop("exc_info", None)
        stack_info = kwargs.pop("stack_info", False)
        extra = kwargs.pop("extra", {})
        if kwargs:
            extra.update(kwargs)

        self._logger.log(level, msg, *args, exc_info=exc_info, stack_info=stack_info, extra=extra)

        # Forward to audit sink if requested or on critical failures
        if (audit or level >= logging.WARN) and self.audit_sink is not None:
            sev_map = {
                logging.DEBUG: Severity.DEBUG.value,
                logging.INFO: Severity.INFO.value,
                logging.WARN: Severity.WARN.value,
                logging.ERROR: Severity.ERROR.value,
                logging.CRITICAL: Severity.FATAL.value,
            }
            sev = sev_map.get(level, Severity.INFO.value)
            ev_type = audit_event_type or ("LOG_WARNING" if level == logging.WARN else "LOG_ERROR")
            payload = {"message": msg, **extra}
            try:
                self.audit_sink(event_type=ev_type, severity=sev, payload=payload)
            except Exception:
                pass  # Sinks must not crash application logger

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._log(logging.DEBUG, msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._log(logging.INFO, msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._log(logging.WARNING, msg, *args, **kwargs)

    def warn(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._log(logging.ERROR, msg, *args, **kwargs)

    def fatal(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._log(logging.CRITICAL, msg, *args, **kwargs)

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._log(logging.CRITICAL, msg, *args, **kwargs)

    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:
        kwargs["exc_info"] = True
        self._log(logging.ERROR, msg, *args, **kwargs)


def get_logger(
    name: str = "sacl", audit_sink: Optional[Callable[..., Any]] = None
) -> StructuredLogger:
    """Returns a StructuredLogger instance with the specified name."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(TextLogFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return StructuredLogger(logger, audit_sink=audit_sink)


def create_file_logger(
    name: str,
    log_path: Path,
    json_format: bool = False,
    level: str = "INFO",
    audit_sink: Optional[Callable[..., Any]] = None,
) -> StructuredLogger:
    """Creates a dedicated StructuredLogger that writes to a specified file on disk."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(f"{name}.file.{log_path.name}")
    logger.propagate = False

    # Avoid duplicate file handlers
    handlers_to_remove = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
    for h in handlers_to_remove:
        logger.removeHandler(h)

    handler = logging.FileHandler(str(log_path), encoding="utf-8")
    formatter = JsonLogFormatter() if json_format else TextLogFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    return StructuredLogger(logger, audit_sink=audit_sink)

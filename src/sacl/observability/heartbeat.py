"""SACL V1 High-Frequency Heartbeat and Process Liveness Subsystem.

Provides heartbeat registration, staleness detection, and background liveness
telemetry for Graph-P supervisor daemons and worker processes.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from sacl.contracts.models import HeartbeatRecord


class HeartbeatService:
    """Manages high-frequency process liveness registry in SQLite heartbeats domain."""

    def __init__(
        self,
        db_source: Union[sqlite3.Connection, Path, str, Callable[[], sqlite3.Connection]],
    ):
        self._db_source = db_source
        self._db_file: Optional[str] = None
        if isinstance(db_source, sqlite3.Connection):
            try:
                for r in db_source.execute("PRAGMA database_list;").fetchall():
                    if r[1] == "main" and r[2] and r[2] != ":memory:":
                        self._db_file = r[2]
                        break
            except Exception:
                pass

    def _get_connection(self) -> tuple[sqlite3.Connection, bool]:
        if isinstance(self._db_source, sqlite3.Connection):
            try:
                self._db_source.execute("SELECT 1;")
                return self._db_source, False
            except sqlite3.ProgrammingError:
                if self._db_file:
                    conn = sqlite3.connect(self._db_file)
                    conn.row_factory = sqlite3.Row
                    conn.execute("PRAGMA foreign_keys = ON;")
                    conn.execute("PRAGMA busy_timeout = 5000;")
                    return conn, True
                raise
        elif callable(self._db_source):
            return self._db_source(), False
        else:
            conn = sqlite3.connect(str(self._db_source))
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("PRAGMA busy_timeout = 5000;")
            return conn, True

    def record_heartbeat(
        self,
        component: str,
        instance_id: str,
        pid: int,
        status: str = "HEALTHY",
        details: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Records a timestamped liveness signal for a daemon or worker process."""
        iso_timestamp = datetime.now(timezone.utc).isoformat()
        details_json = json.dumps(details or {})

        conn, should_close = self._get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO heartbeats (component, instance_id, pid, status, last_seen_at, details_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    component,
                    instance_id,
                    pid,
                    status,
                    iso_timestamp,
                    details_json,
                ),
            )
            heartbeat_id = cursor.lastrowid or 0
            conn.commit()
            return heartbeat_id
        finally:
            if should_close:
                conn.close()

    def get_latest_heartbeat(
        self,
        component: str,
        instance_id: str,
    ) -> Optional[HeartbeatRecord]:
        """Retrieves the most recent heartbeat record for a given component instance."""
        conn, should_close = self._get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT heartbeat_id, component, instance_id, pid, status, last_seen_at, details_json
                FROM heartbeats
                WHERE component = ? AND instance_id = ?
                ORDER BY heartbeat_id DESC LIMIT 1
                """,
                (component, instance_id),
            )
            row = cursor.fetchone()
            if not row:
                return None

            try:
                details = json.loads(row["details_json"] or "{}")
            except Exception:
                details = {}

            return HeartbeatRecord(
                heartbeat_id=row["heartbeat_id"],
                component=row["component"],
                instance_id=row["instance_id"],
                pid=row["pid"],
                status=row["status"],
                last_seen_at=row["last_seen_at"],
                details=details,
            )
        finally:
            if should_close:
                conn.close()

    def list_heartbeats(
        self,
        component: Optional[str] = None,
        limit: int = 50,
    ) -> List[HeartbeatRecord]:
        """Lists recent heartbeats optionally filtered by component."""
        conn, should_close = self._get_connection()

        try:
            query = "SELECT heartbeat_id, component, instance_id, pid, status, last_seen_at, details_json FROM heartbeats"
            params: List[Any] = []
            if component is not None:
                query += " WHERE component = ?"
                params.append(component)
            query += " ORDER BY heartbeat_id DESC LIMIT ?"
            params.append(limit)

            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

            records: List[HeartbeatRecord] = []
            for row in rows:
                try:
                    details = json.loads(row["details_json"] or "{}")
                except Exception:
                    details = {}
                records.append(
                    HeartbeatRecord(
                        heartbeat_id=row["heartbeat_id"],
                        component=row["component"],
                        instance_id=row["instance_id"],
                        pid=row["pid"],
                        status=row["status"],
                        last_seen_at=row["last_seen_at"],
                        details=details,
                    )
                )
            return records
        finally:
            if should_close:
                conn.close()

    def check_liveness(
        self,
        component: str,
        instance_id: str,
        ttl_seconds: int = 60,
    ) -> Tuple[bool, Optional[HeartbeatRecord]]:
        """Checks if a component instance is alive (has recorded a heartbeat within ttl_seconds)."""
        latest = self.get_latest_heartbeat(component, instance_id)
        if not latest:
            return False, None

        try:
            # Parse last_seen_at timestamp
            ts_str = latest.last_seen_at.replace("Z", "+00:00")
            last_dt = datetime.fromisoformat(ts_str)
            now_dt = datetime.now(timezone.utc)
            if last_dt.tzinfo is None:
                last_dt = last_dt.replace(tzinfo=timezone.utc)
            age_sec = (now_dt - last_dt).total_seconds()
            is_alive = age_sec <= ttl_seconds
            return is_alive, latest
        except Exception:
            return False, latest

    def detect_stale_processes(
        self,
        ttl_seconds: int = 60,
        component: Optional[str] = None,
    ) -> List[HeartbeatRecord]:
        """Detects active component instances whose last heartbeat exceeds ttl_seconds."""
        conn, should_close = self._get_connection()

        try:
            # Group by component, instance_id taking MAX(heartbeat_id)
            query = """
                SELECT h.heartbeat_id, h.component, h.instance_id, h.pid, h.status, h.last_seen_at, h.details_json
                FROM heartbeats h
                INNER JOIN (
                    SELECT component, instance_id, MAX(heartbeat_id) as max_id
                    FROM heartbeats
                    GROUP BY component, instance_id
                ) latest ON h.heartbeat_id = latest.max_id
            """
            params: List[Any] = []
            if component is not None:
                query += " WHERE h.component = ?"
                params.append(component)

            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

            now_dt = datetime.now(timezone.utc)
            stale: List[HeartbeatRecord] = []

            for row in rows:
                try:
                    ts_str = row["last_seen_at"].replace("Z", "+00:00")
                    last_dt = datetime.fromisoformat(ts_str)
                    if last_dt.tzinfo is None:
                        last_dt = last_dt.replace(tzinfo=timezone.utc)
                    age_sec = (now_dt - last_dt).total_seconds()
                except Exception:
                    age_sec = float("inf")

                if age_sec > ttl_seconds:
                    try:
                        details = json.loads(row["details_json"] or "{}")
                    except Exception:
                        details = {}

                    stale.append(
                        HeartbeatRecord(
                            heartbeat_id=row["heartbeat_id"],
                            component=row["component"],
                            instance_id=row["instance_id"],
                            pid=row["pid"],
                            status="STALE",
                            last_seen_at=row["last_seen_at"],
                            details=details,
                        )
                    )
            return stale
        finally:
            if should_close:
                conn.close()


class BackgroundHeartbeater:
    """Threaded background heartbeat emitter for persistent daemons or long tasks."""

    def __init__(
        self,
        service: HeartbeatService,
        component: str,
        instance_id: str,
        pid: int,
        interval_seconds: float = 10.0,
        status: str = "HEALTHY",
        details_fn: Optional[Callable[[], Dict[str, Any]]] = None,
    ):
        self.service = service
        self.component = component
        self.instance_id = instance_id
        self.pid = pid
        self.interval_seconds = interval_seconds
        self.status = status
        self.details_fn = details_fn
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Starts background heartbeat emission."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name=f"heartbeat-{self.component}")
        self._thread.start()

    def stop(self) -> None:
        """Stops background heartbeat emission."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None

    def _run(self) -> None:
        # Immediate first tick
        try:
            details = self.details_fn() if self.details_fn else {}
            self.service.record_heartbeat(
                component=self.component,
                instance_id=self.instance_id,
                pid=self.pid,
                status=self.status,
                details=details,
            )
        except Exception:
            pass

        while not self._stop_event.wait(self.interval_seconds):
            try:
                details = self.details_fn() if self.details_fn else {}
                self.service.record_heartbeat(
                    component=self.component,
                    instance_id=self.instance_id,
                    pid=self.pid,
                    status=self.status,
                    details=details,
                )
            except Exception:
                pass

    def __enter__(self) -> BackgroundHeartbeater:
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.stop()

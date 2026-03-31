from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .protocol import TelemetryMessage


class TelemetryStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL;")
        connection.execute("PRAGMA synchronous=NORMAL;")
        return connection

    def _init_db(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS telemetry_samples (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_mode TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    uptime_ms INTEGER NOT NULL,
                    temperature_c REAL NOT NULL,
                    humidity_pct REAL NOT NULL,
                    light_lux REAL NOT NULL,
                    voltage_v REAL NOT NULL,
                    mock_mode INTEGER NOT NULL,
                    queue_overflows INTEGER NOT NULL,
                    sensor_failures INTEGER NOT NULL,
                    serial_disconnects INTEGER NOT NULL,
                    watchdog_resets INTEGER NOT NULL,
                    fault_flags INTEGER NOT NULL,
                    sensor_heartbeat INTEGER NOT NULL,
                    telemetry_heartbeat INTEGER NOT NULL,
                    heartbeat_heartbeat INTEGER NOT NULL,
                    fault_heartbeat INTEGER NOT NULL,
                    ring_count INTEGER NOT NULL,
                    queue_depth INTEGER NOT NULL,
                    received_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS host_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    payload_json TEXT,
                    created_at TEXT NOT NULL
                );
                """
            )

    def insert_telemetry(self, message: TelemetryMessage, source_mode: str, received_at: str | None = None) -> None:
        received_at = received_at or datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO telemetry_samples (
                    source_mode, sequence, uptime_ms, temperature_c, humidity_pct, light_lux, voltage_v,
                    mock_mode, queue_overflows, sensor_failures, serial_disconnects, watchdog_resets,
                    fault_flags, sensor_heartbeat, telemetry_heartbeat, heartbeat_heartbeat, fault_heartbeat,
                    ring_count, queue_depth, received_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    source_mode,
                    message.seq,
                    message.uptime_ms,
                    message.sensor.temperature_c,
                    message.sensor.humidity_pct,
                    message.sensor.light_lux,
                    message.sensor.voltage_v,
                    int(message.status.mock_mode),
                    message.status.queue_overflows,
                    message.status.sensor_failures,
                    message.status.serial_disconnects,
                    message.status.watchdog_resets,
                    message.status.fault_flags,
                    message.status.heartbeats["sensor"],
                    message.status.heartbeats["telemetry"],
                    message.status.heartbeats["heartbeat"],
                    message.status.heartbeats["fault"],
                    message.buffer.ring_count,
                    message.buffer.queue_depth,
                    received_at,
                ),
            )

    def record_event(self, level: str, message: str, payload: dict[str, Any] | None = None) -> None:
        created_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO host_events (level, message, payload_json, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (level, message, json.dumps(payload) if payload else None, created_at),
            )

    def prune_samples(self, max_samples: int) -> None:
        if max_samples <= 0:
            return
        with self._connect() as connection:
            connection.execute(
                """
                DELETE FROM telemetry_samples
                WHERE id NOT IN (
                    SELECT id FROM telemetry_samples
                    ORDER BY id DESC
                    LIMIT ?
                )
                """,
                (max_samples,),
            )

    def latest_sample(self) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM telemetry_samples ORDER BY id DESC LIMIT 1"
            ).fetchone()
        return dict(row) if row else None

    def recent_samples(self, limit: int = 25) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM telemetry_samples ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def recent_events(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM host_events ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def summary(self) -> dict[str, Any]:
        latest = self.latest_sample()
        with self._connect() as connection:
            counts = connection.execute(
                """
                SELECT
                    COUNT(*) AS sample_count,
                    SUM(CASE WHEN fault_flags != 0 THEN 1 ELSE 0 END) AS faulted_samples,
                    MAX(temperature_c) AS max_temp_c
                FROM telemetry_samples
                """
            ).fetchone()
        return {
            "sample_count": int(counts["sample_count"] or 0),
            "faulted_samples": int(counts["faulted_samples"] or 0),
            "max_temp_c": float(counts["max_temp_c"] or 0.0),
            "latest": latest,
        }

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class SensorPayload:
    temperature_c: float
    humidity_pct: float
    light_lux: float
    voltage_v: float


@dataclass(frozen=True)
class StatusPayload:
    mock_mode: bool
    queue_overflows: int
    sensor_failures: int
    serial_disconnects: int
    watchdog_resets: int
    fault_flags: int
    heartbeats: dict[str, int]


@dataclass(frozen=True)
class BufferPayload:
    ring_count: int
    queue_depth: int


@dataclass(frozen=True)
class TelemetryMessage:
    seq: int
    uptime_ms: int
    sensor: SensorPayload
    status: StatusPayload
    buffer: BufferPayload


@dataclass(frozen=True)
class BootMessage:
    boot: str
    mock_mode: bool
    sample_rate_hz: int
    telemetry_interval_ms: int
    queue_length: int
    ring_capacity: int


ProtocolMessage = BootMessage | TelemetryMessage


def _require_keys(payload: dict[str, Any], keys: list[str]) -> None:
    missing = [key for key in keys if key not in payload]
    if missing:
        raise ValueError(f"missing keys: {', '.join(missing)}")


def parse_protocol_line(line: str) -> ProtocolMessage:
    try:
        payload = json.loads(line)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid json line: {exc}") from exc

    if "boot" in payload:
        _require_keys(
            payload,
            ["boot", "mock_mode", "sample_rate_hz", "telemetry_interval_ms", "queue_length", "ring_capacity"],
        )
        return BootMessage(
            boot=str(payload["boot"]),
            mock_mode=bool(payload["mock_mode"]),
            sample_rate_hz=int(payload["sample_rate_hz"]),
            telemetry_interval_ms=int(payload["telemetry_interval_ms"]),
            queue_length=int(payload["queue_length"]),
            ring_capacity=int(payload["ring_capacity"]),
        )

    _require_keys(payload, ["seq", "uptime_ms", "sensor", "status", "buffer"])
    sensor = payload["sensor"]
    status = payload["status"]
    buffer = payload["buffer"]
    _require_keys(sensor, ["temperature_c", "humidity_pct", "light_lux", "voltage_v"])
    _require_keys(
        status,
        ["mock_mode", "queue_overflows", "sensor_failures", "serial_disconnects", "watchdog_resets", "fault_flags", "heartbeats"],
    )
    _require_keys(status["heartbeats"], ["sensor", "telemetry", "heartbeat", "fault"])
    _require_keys(buffer, ["ring_count", "queue_depth"])

    return TelemetryMessage(
        seq=int(payload["seq"]),
        uptime_ms=int(payload["uptime_ms"]),
        sensor=SensorPayload(
            temperature_c=float(sensor["temperature_c"]),
            humidity_pct=float(sensor["humidity_pct"]),
            light_lux=float(sensor["light_lux"]),
            voltage_v=float(sensor["voltage_v"]),
        ),
        status=StatusPayload(
            mock_mode=bool(status["mock_mode"]),
            queue_overflows=int(status["queue_overflows"]),
            sensor_failures=int(status["sensor_failures"]),
            serial_disconnects=int(status["serial_disconnects"]),
            watchdog_resets=int(status["watchdog_resets"]),
            fault_flags=int(status["fault_flags"]),
            heartbeats={
                "sensor": int(status["heartbeats"]["sensor"]),
                "telemetry": int(status["heartbeats"]["telemetry"]),
                "heartbeat": int(status["heartbeats"]["heartbeat"]),
                "fault": int(status["heartbeats"]["fault"]),
            },
        ),
        buffer=BufferPayload(
            ring_count=int(buffer["ring_count"]),
            queue_depth=int(buffer["queue_depth"]),
        ),
    )


def serialize_protocol_message(message: ProtocolMessage) -> str:
    return json.dumps(asdict(message), separators=(",", ":"))

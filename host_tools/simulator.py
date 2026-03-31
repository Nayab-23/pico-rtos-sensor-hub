from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Iterator

from .protocol import (
    BootMessage,
    BufferPayload,
    SensorPayload,
    StatusPayload,
    TelemetryMessage,
    serialize_protocol_message,
)


@dataclass
class TelemetrySimulator:
    sample_rate_hz: int = 10
    telemetry_interval_ms: int = 500
    ring_capacity: int = 64
    queue_length: int = 16
    mock_mode: bool = True
    sequence: int = 0
    start_monotonic: float = field(default_factory=time.monotonic)

    def boot_message(self) -> BootMessage:
        return BootMessage(
            boot="pico-rtos-sensor-hub",
            mock_mode=self.mock_mode,
            sample_rate_hz=self.sample_rate_hz,
            telemetry_interval_ms=self.telemetry_interval_ms,
            queue_length=self.queue_length,
            ring_capacity=self.ring_capacity,
        )

    def next_message(self) -> TelemetryMessage:
        self.sequence += 1
        elapsed_s = time.monotonic() - self.start_monotonic
        fault_flags = 0
        if self.sequence % 45 == 0:
            fault_flags = 1

        return TelemetryMessage(
            seq=self.sequence,
            uptime_ms=int(elapsed_s * 1000),
            sensor=SensorPayload(
                temperature_c=24.0 + 2.5 * math.sin(elapsed_s / 5.0),
                humidity_pct=45.0 + 7.5 * math.cos(elapsed_s / 6.0),
                light_lux=160.0 + 70.0 * (math.sin(elapsed_s / 3.0) + 1.0),
                voltage_v=3.24 + 0.04 * math.sin(elapsed_s / 9.0),
            ),
            status=StatusPayload(
                mock_mode=self.mock_mode,
                queue_overflows=0,
                sensor_failures=0,
                serial_disconnects=0,
                watchdog_resets=0,
                fault_flags=fault_flags,
                heartbeats={
                    "sensor": self.sequence * max(1, self.sample_rate_hz // 2),
                    "telemetry": self.sequence,
                    "heartbeat": self.sequence * 2,
                    "fault": self.sequence,
                },
            ),
            buffer=BufferPayload(
                ring_count=min(self.sequence, self.ring_capacity),
                queue_depth=0,
            ),
        )

    def iter_lines(self, include_boot: bool = True, sleep_between_messages: bool = True) -> Iterator[str]:
        if include_boot:
            yield serialize_protocol_message(self.boot_message())

        while True:
            message = self.next_message()
            yield serialize_protocol_message(message)
            if sleep_between_messages:
                time.sleep(self.telemetry_interval_ms / 1000.0)

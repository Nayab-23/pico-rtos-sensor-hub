from host_tools.protocol import TelemetryMessage, parse_protocol_line
from host_tools.simulator import TelemetrySimulator


def test_simulator_generates_parseable_stream() -> None:
    simulator = TelemetrySimulator(telemetry_interval_ms=1)
    lines = simulator.iter_lines(include_boot=True, sleep_between_messages=False)

    boot = parse_protocol_line(next(lines))
    telemetry = parse_protocol_line(next(lines))

    assert getattr(boot, "boot", "") == "pico-rtos-sensor-hub"
    assert isinstance(telemetry, TelemetryMessage)
    assert telemetry.buffer.ring_count == 1

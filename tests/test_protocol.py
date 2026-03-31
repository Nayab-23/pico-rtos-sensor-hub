from host_tools.protocol import BootMessage, TelemetryMessage, parse_protocol_line
from host_tools.simulator import TelemetrySimulator


def test_parse_boot_message() -> None:
    simulator = TelemetrySimulator()
    message = parse_protocol_line(next(simulator.iter_lines(include_boot=True, sleep_between_messages=False)))
    assert isinstance(message, BootMessage)
    assert message.boot == "pico-rtos-sensor-hub"


def test_parse_telemetry_message() -> None:
    simulator = TelemetrySimulator()
    lines = simulator.iter_lines(include_boot=False, sleep_between_messages=False)
    message = parse_protocol_line(next(lines))
    assert isinstance(message, TelemetryMessage)
    assert message.seq == 1
    assert message.sensor.voltage_v > 3.0

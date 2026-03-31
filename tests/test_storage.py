from host_tools.protocol import TelemetryMessage, parse_protocol_line
from host_tools.simulator import TelemetrySimulator
from host_tools.storage import TelemetryStore


def test_storage_round_trip(tmp_path) -> None:
    store = TelemetryStore(tmp_path / "telemetry.db")
    simulator = TelemetrySimulator()
    message = parse_protocol_line(next(simulator.iter_lines(include_boot=False, sleep_between_messages=False)))

    assert isinstance(message, TelemetryMessage)

    store.insert_telemetry(message, source_mode="simulator")
    summary = store.summary()
    latest = store.latest_sample()

    assert summary["sample_count"] == 1
    assert latest is not None
    assert latest["source_mode"] == "simulator"
    assert latest["sequence"] == 1

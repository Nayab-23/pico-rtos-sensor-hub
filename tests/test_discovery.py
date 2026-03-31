from types import SimpleNamespace

from host_tools import discovery


def test_detect_pico_serial_devices(monkeypatch) -> None:
    fake_port = SimpleNamespace(
        device="/dev/ttyACM0",
        description="Raspberry Pi Pico",
        hwid="USB VID:PID=2E8A:0005",
        vid=0x2E8A,
        pid=0x0005,
    )

    monkeypatch.setattr(discovery.list_ports, "comports", lambda: [fake_port])
    devices = discovery.detect_pico_serial_devices()

    assert len(devices) == 1
    assert devices[0].device == "/dev/ttyACM0"

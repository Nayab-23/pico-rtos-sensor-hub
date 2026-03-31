from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from serial.tools import list_ports


PICO_USB_VID = 0x2E8A


@dataclass(frozen=True)
class SerialDevice:
    device: str
    description: str
    hwid: str
    vid: int | None
    pid: int | None


def list_serial_devices() -> list[SerialDevice]:
    devices: list[SerialDevice] = []
    for port in list_ports.comports():
        devices.append(
            SerialDevice(
                device=port.device,
                description=port.description or "",
                hwid=port.hwid or "",
                vid=port.vid,
                pid=port.pid,
            )
        )
    return devices


def detect_pico_serial_devices() -> list[SerialDevice]:
    matches: list[SerialDevice] = []
    for device in list_serial_devices():
        description = device.description.lower()
        hwid = device.hwid.lower()
        is_pico = device.vid == PICO_USB_VID or "rp2040" in description or "pico" in description or "2e8a" in hwid
        if is_pico:
            matches.append(device)
    return matches


def detect_bootsel_mounts(extra_roots: list[Path] | None = None) -> list[str]:
    search_roots = [
        Path("/media"),
        Path("/mnt"),
        Path("/run/media"),
    ]
    if extra_roots:
        search_roots.extend(extra_roots)

    mounts: list[str] = []
    for root in search_roots:
        if not root.exists():
            continue
        for candidate in root.rglob("RPI-RP2"):
            if candidate.is_dir():
                mounts.append(str(candidate))
    return sorted(set(mounts))


def detect_environment_summary() -> dict[str, object]:
    serial_devices = [asdict(device) for device in detect_pico_serial_devices()]
    bootsel_mounts = detect_bootsel_mounts()
    return {
        "pico_detected": bool(serial_devices),
        "serial_devices": serial_devices,
        "bootsel_mounts": bootsel_mounts,
    }


def detect_environment_json() -> str:
    return json.dumps(detect_environment_summary(), indent=2)

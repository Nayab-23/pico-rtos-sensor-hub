from __future__ import annotations

import argparse
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys
import time

import serial

from .config import ensure_runtime_dirs
from .discovery import detect_environment_summary, detect_pico_serial_devices
from .protocol import BootMessage, TelemetryMessage, parse_protocol_line
from .simulator import TelemetrySimulator
from .storage import TelemetryStore


LOGGER = logging.getLogger("pico_rtos_sensor_hub.monitor")


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Monitor Pico RTOS telemetry from serial or simulator mode.")
    parser.add_argument("--mode", choices=["auto", "serial", "simulator"], default="auto")
    parser.add_argument("--port", help="Serial port to use, for example /dev/ttyACM0.")
    parser.add_argument("--baudrate", type=int, default=115200)
    parser.add_argument("--db-path", type=Path, help="SQLite database path.")
    parser.add_argument("--jsonl-path", type=Path, help="Rotated JSONL telemetry log path.")
    parser.add_argument("--max-retained-samples", type=int, default=5000)
    parser.add_argument("--max-messages", type=int, default=0, help="Stop after N telemetry messages. Zero means run forever.")
    parser.add_argument("--telemetry-interval-ms", type=int, default=500)
    return parser


def configure_logging(jsonl_path: Path) -> logging.Logger:
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    telemetry_logger = logging.getLogger("pico_rtos_sensor_hub.telemetry_jsonl")
    telemetry_logger.setLevel(logging.INFO)
    telemetry_logger.handlers.clear()
    handler = RotatingFileHandler(jsonl_path, maxBytes=2_000_000, backupCount=3)
    handler.setFormatter(logging.Formatter("%(message)s"))
    telemetry_logger.addHandler(handler)

    if not LOGGER.handlers:
        stream_handler = logging.StreamHandler(sys.stderr)
        stream_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        LOGGER.addHandler(stream_handler)
    LOGGER.setLevel(logging.INFO)
    return telemetry_logger


def choose_source(mode: str, port: str | None) -> tuple[str, str | None]:
    if mode == "simulator":
        return "simulator", None
    if mode == "serial":
        if port:
            return "serial", port
        devices = detect_pico_serial_devices()
        if not devices:
            raise RuntimeError("serial mode requested but no Pico serial device was detected")
        return "serial", devices[0].device

    if port:
        return "serial", port
    devices = detect_pico_serial_devices()
    if devices:
        return "serial", devices[0].device
    return "simulator", None


def print_telemetry_line(source_mode: str, message: TelemetryMessage) -> None:
    print(
        (
            f"[{source_mode}] seq={message.seq:04d} uptime={message.uptime_ms:>6}ms "
            f"temp={message.sensor.temperature_c:>5.2f}C humidity={message.sensor.humidity_pct:>5.1f}% "
            f"light={message.sensor.light_lux:>6.1f}lx voltage={message.sensor.voltage_v:>4.2f}V "
            f"faults=0x{message.status.fault_flags:02x} ring={message.buffer.ring_count} "
            f"queue={message.buffer.queue_depth}"
        ),
        flush=True,
    )


def run_simulator_loop(store: TelemetryStore, telemetry_logger: logging.Logger, args: argparse.Namespace) -> int:
    simulator = TelemetrySimulator(telemetry_interval_ms=args.telemetry_interval_ms)
    count = 0
    for line in simulator.iter_lines(include_boot=True, sleep_between_messages=True):
        telemetry_logger.info(line)
        message = parse_protocol_line(line)
        if isinstance(message, BootMessage):
            print(
                f"[simulator] boot={message.boot} mock_mode={message.mock_mode} sample_rate={message.sample_rate_hz}Hz",
                flush=True,
            )
            store.record_event("info", "simulator_boot", {"boot": message.boot})
            continue

        store.insert_telemetry(message, source_mode="simulator")
        store.prune_samples(args.max_retained_samples)
        print_telemetry_line("simulator", message)
        count += 1
        if args.max_messages and count >= args.max_messages:
            return count
    return count


def run_serial_loop(
    store: TelemetryStore,
    telemetry_logger: logging.Logger,
    port: str,
    baudrate: int,
    max_retained_samples: int,
    max_messages: int,
) -> int:
    count = 0
    with serial.Serial(port, baudrate=baudrate, timeout=1) as connection:
        store.record_event("info", "serial_connected", {"port": port, "baudrate": baudrate})
        LOGGER.info("connected to Pico serial port %s", port)
        while True:
            raw = connection.readline()
            if not raw:
                continue
            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                continue
            telemetry_logger.info(line)
            try:
                message = parse_protocol_line(line)
            except ValueError as exc:
                store.record_event("warning", "invalid_protocol_line", {"line": line, "error": str(exc)})
                LOGGER.warning("invalid telemetry line: %s", exc)
                continue

            if isinstance(message, BootMessage):
                print(
                    f"[serial:{port}] boot={message.boot} mock_mode={message.mock_mode} sample_rate={message.sample_rate_hz}Hz",
                    flush=True,
                )
                continue

            store.insert_telemetry(message, source_mode="serial")
            store.prune_samples(max_retained_samples)
            print_telemetry_line(f"serial:{port}", message)
            count += 1
            if max_messages and count >= max_messages:
                return count


def main() -> int:
    args = build_argument_parser().parse_args()
    runtime_paths = ensure_runtime_dirs()
    db_path = args.db_path or runtime_paths.db_path
    jsonl_path = args.jsonl_path or runtime_paths.telemetry_log_path
    store = TelemetryStore(db_path)
    telemetry_logger = configure_logging(jsonl_path)

    environment = detect_environment_summary()
    store.record_event("info", "startup_environment", environment)
    source_mode, port = choose_source(args.mode, args.port)

    if source_mode == "simulator":
        LOGGER.info("running in simulator mode because no Pico serial device is attached")
        return run_simulator_loop(store, telemetry_logger, args)

    while True:
        try:
            return run_serial_loop(
                store=store,
                telemetry_logger=telemetry_logger,
                port=port or "",
                baudrate=args.baudrate,
                max_retained_samples=args.max_retained_samples,
                max_messages=args.max_messages,
            )
        except (serial.SerialException, OSError) as exc:
            LOGGER.warning("serial connection failed: %s", exc)
            store.record_event("warning", "serial_disconnected", {"port": port, "error": str(exc)})
            if args.mode == "serial":
                raise
            time.sleep(2.0)
            devices = detect_pico_serial_devices()
            if not devices:
                LOGGER.info("no Pico detected after disconnect, switching to simulator mode")
                return run_simulator_loop(store, telemetry_logger, args)
            port = devices[0].device


if __name__ == "__main__":
    raise SystemExit(main())

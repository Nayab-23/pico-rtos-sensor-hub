# Pico RTOS Sensor Hub

`pico-rtos-sensor-hub` is a firmware-oriented embedded project that uses the Raspberry Pi as the development host for a Raspberry Pi Pico or Pico W telemetry hub.

## Chosen Stack

- Firmware: Pico SDK + FreeRTOS
- Host tools: Python
- Communication: USB serial JSON lines

Zephyr was intentionally not chosen for this machine because the Pi did not already have the Zephyr tooling stack, while Pico SDK plus FreeRTOS is a more reliable path to a real build here today.

## Project Goals

- RTOS-based multitask firmware
- structured telemetry over USB serial
- bounded buffering and fault counters
- host-side flashing, detection, and monitoring tools
- simulator mode when no Pico is attached

## Repository Layout

- `firmware/`: Pico SDK + FreeRTOS firmware
- `host_tools/`: Python telemetry monitor, simulator, and dashboard
- `docs/`: architecture, RTOS design, hardware notes, and resume bullets
- `scripts/`: setup, detection, build, flash, and host-run helpers
- `tests/`: host-side tests

## Hardware Status Handling

If no Pico or Pico W is attached:

- the firmware workspace is still buildable
- the host monitor runs in simulator mode
- flashing instructions remain documented for later hardware bring-up

## Quick Start

```bash
./scripts/setup_host_tools.sh
./scripts/detect_pico.py
./scripts/run_monitor.sh --mode auto
```

On this Raspberry Pi host, no Pico was detected during initial setup on March 30, 2026, so the project is configured to be immediately useful in simulator mode while keeping the firmware build and flash path ready for real hardware.

## What Is Implemented

- Pico SDK + FreeRTOS firmware with four RTOS tasks:
  - sensor acquisition
  - telemetry output
  - heartbeat indicator
  - fault monitor with optional watchdog
- structured JSON-line telemetry over USB serial
- bounded FreeRTOS queue plus diagnostic ring buffer
- host-side Pico detection, serial ingest, simulator fallback, and SQLite persistence
- local FastAPI dashboard backed by the same telemetry database
- build, flash, and monitor helper scripts for Raspberry Pi bring-up
- pytest coverage for protocol parsing, storage, simulator, and device detection logic

## Repository Layout

- `firmware/`: Pico SDK + FreeRTOS application and CMake build files
- `host_tools/`: Python monitor, simulator, SQLite store, and dashboard
- `scripts/`: Pi helper scripts for setup, detection, build, flash, and runtime
- `tests/`: host-side test coverage
- `docs/`: architecture, RTOS notes, host integration, hardware matrix, and resume bullets

## Firmware Build

Install dependencies on the Raspberry Pi first:

```bash
./scripts/bootstrap_pi.sh
```

Build the UF2 artifact:

```bash
./scripts/build_firmware.sh
```

Useful build-time overrides:

```bash
PICO_BOARD=pico_w SENSOR_HUB_USE_MOCK_SENSORS=OFF ./scripts/build_firmware.sh
```

## Flashing

When a Pico is attached in BOOTSEL mode and mounted as `RPI-RP2`:

```bash
./scripts/flash_pico.sh
```

The flash script auto-detects the mount if possible, or you can pass it explicitly:

```bash
./scripts/flash_pico.sh /media/nayab/RPI-RP2
```

## Host Monitoring

Auto mode prefers a live Pico serial device and falls back to simulator mode when no board is attached:

```bash
./scripts/run_monitor.sh --mode auto
```

Force simulator mode for demos and tests:

```bash
./scripts/run_monitor.sh --mode simulator --max-messages 20
```

Launch the local dashboard:

```bash
./scripts/run_dashboard.sh --host 0.0.0.0 --port 8081
```

Open `http://<pi-ip>:8081/` to review the latest samples, fault history, and host-side events.

## Documentation

- `docs/architecture.md`
- `docs/rtos_design.md`
- `docs/host_integration.md`
- `docs/hardware_matrix.md`
- `docs/resume_bullets.md`

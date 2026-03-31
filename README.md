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
make host-install
make host-test
```

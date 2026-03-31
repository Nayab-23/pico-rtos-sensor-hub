# Architecture

## Overview

`pico-rtos-sensor-hub` is split into a firmware plane on the RP2040 and a host-integration plane on the Raspberry Pi.

The design goal is simple: the firmware should stay deterministic and RTOS-oriented, while the Raspberry Pi handles persistence, visualization, and device-management concerns that would be awkward to push onto the microcontroller.

## Firmware Plane

The firmware is built with Pico SDK and FreeRTOS.

Primary responsibilities:

- sample the active sensor source on a fixed cadence
- preserve recent readings in a bounded ring buffer
- publish structured telemetry over USB serial
- surface liveness and fault state using explicit heartbeats and counters
- optionally feed the watchdog when the runtime remains healthy

### RTOS Tasks

- `sensor_task`
  - samples either the onboard RP2040 temperature channel or the mock sensor source
  - writes each sample into a FreeRTOS queue and the diagnostic ring buffer
- `telemetry_task`
  - drains the freshest sample
  - formats a JSON-line payload
  - emits telemetry over USB serial
- `heartbeat_task`
  - toggles the board heartbeat indicator when a GPIO LED is available
  - increments a liveness counter for fault supervision
- `fault_task`
  - watches task heartbeats and counters
  - marks queue overflow, stale-task, and sensor-failure conditions
  - updates the optional watchdog

### Firmware Data Flow

1. `sensor_task` acquires a reading.
2. The reading is pushed into the queue and ring buffer.
3. `telemetry_task` serializes the newest sample and current status snapshot.
4. The host-side monitor parses the same JSON protocol in either live or simulated mode.

## Host Plane

The Raspberry Pi side is a Python toolchain that treats the Pico as a telemetry producer.

Primary responsibilities:

- detect Pico serial devices and BOOTSEL mounts
- monitor USB serial telemetry with reconnect-safe behavior
- fall back to a simulator when no hardware is attached
- store samples and host events in SQLite
- expose a dashboard for quick review

### Host Components

- `host_tools.discovery`
  - finds candidate Pico serial ports and BOOTSEL mount points
- `host_tools.monitor`
  - long-running ingest loop for live serial or simulated telemetry
- `host_tools.storage`
  - SQLite-backed telemetry and event persistence
- `host_tools.dashboard`
  - FastAPI dashboard over the stored samples
- `host_tools.simulator`
  - emits the exact same protocol as the firmware for development without hardware

## Protocol Strategy

The protocol is intentionally lightweight and debugging-friendly:

- one JSON object per line
- a startup boot banner with runtime configuration
- recurring telemetry frames with sensor values, buffer depth, and fault state

This makes it easy to inspect live output in a serial terminal, archive it as JSONL, and replay it into higher-level analytics later.

## Mode Strategy

- Preferred mode: live Pico over USB serial
- Secondary mode: Pico in BOOTSEL for UF2 flashing
- Fallback mode: host-side simulator that emits the same JSON protocol

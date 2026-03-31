# Architecture

## Overview

The project has two primary layers:

1. Firmware on the Pico or Pico W using FreeRTOS tasks and bounded buffers.
2. Host-side Raspberry Pi tooling for serial ingestion, telemetry persistence, terminal monitoring, and optional dashboard serving.

## Top-Level Components

### Firmware

- sensor acquisition task
- telemetry output task
- heartbeat/status task
- fault monitor and watchdog task
- ring buffer and error accounting

### Host Side

- device detection and bring-up scripts
- serial monitor with auto-detect and simulator fallback
- SQLite logging for telemetry history
- optional local dashboard over the stored telemetry stream

## Mode Strategy

- Preferred mode: live Pico over USB serial
- Fallback mode: host-side simulator that emits the same JSON line protocol

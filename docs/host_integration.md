# Host Integration

## Raspberry Pi Responsibilities

- detect Pico serial devices
- build firmware artifacts
- optionally copy UF2 output to a mounted boot device
- monitor live telemetry over USB serial
- run a simulator when no hardware is attached

## Host Tooling Plan

- terminal monitor for live metrics
- SQLite-backed telemetry log
- optional local dashboard for recent samples and fault state

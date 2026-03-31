# Hardware Matrix

| Hardware State | Firmware Workspace | Host Tools | Expected Mode |
| --- | --- | --- | --- |
| Pico attached as serial device | Build and monitor | Serial ingest | Live hardware |
| Pico in BOOTSEL mass-storage mode | Build and flash | Flash helper | Bring-up / flashing |
| No Pico attached | Build workspace only | Simulator and tests | Mock telemetry |

## Current Pi Observation

Observation date: March 30, 2026

- No `/dev/ttyACM*` or `/dev/ttyUSB*` Pico device was detected during setup.
- No Raspberry Pi USB vendor device with VID `0x2e8a` was visible in `lsusb`.
- The project therefore defaults to simulator mode on this Raspberry Pi today.

## Supported Bring-Up Cases

### No Hardware Attached

- build the firmware workspace
- run the host monitor in simulator mode
- validate parsing, persistence, and dashboard behavior

### Pico Attached as USB CDC Serial

- run `./scripts/run_monitor.sh --mode auto`
- the monitor will prefer serial mode automatically
- the dashboard reflects live device telemetry

### Pico Attached in BOOTSEL Mode

- run `./scripts/build_firmware.sh`
- run `./scripts/flash_pico.sh`
- reboot into the application and then start the monitor

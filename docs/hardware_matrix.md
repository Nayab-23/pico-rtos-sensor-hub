# Hardware Matrix

| Hardware State | Firmware Workspace | Host Tools | Expected Mode |
| --- | --- | --- | --- |
| Pico attached as serial device | Optional build and monitor | Serial ingest | Live hardware |
| Pico in BOOTSEL mass-storage mode | Optional build and flash | Flash helper | Bring-up / flashing |
| No Pico attached | Toolchain deferred | Simulator and tests | Mock telemetry |

## Current Pi Observation

Observation date: March 30, 2026

- No `/dev/ttyACM*` or `/dev/ttyUSB*` Pico device was detected during setup.
- No Raspberry Pi USB vendor device with VID `0x2e8a` was visible in `lsusb`.
- The project therefore defaults to simulator mode on this Raspberry Pi today.
- The simulator-first path is considered the canonical daily workflow until real hardware is attached.

## Supported Bring-Up Cases

### No Hardware Attached

- run the host monitor in simulator mode
- validate parsing, persistence, and dashboard behavior
- defer heavy toolchain installation unless it is explicitly needed

### Pico Attached as USB CDC Serial

- run `./scripts/run_monitor.sh --mode auto`
- the monitor will prefer serial mode automatically
- the dashboard reflects live device telemetry

### Pico Attached in BOOTSEL Mode

- run `./scripts/install_firmware_toolchain.sh` if the toolchain is not already installed
- run `./scripts/build_firmware.sh`
- run `./scripts/flash_pico.sh`
- reboot into the application and then start the monitor

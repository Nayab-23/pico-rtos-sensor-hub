# Hardware Matrix

| Hardware State | Firmware Workspace | Host Tools | Expected Mode |
| --- | --- | --- | --- |
| Pico attached as serial device | Build and monitor | Serial ingest | Live hardware |
| Pico in BOOTSEL mass-storage mode | Build and flash | Flash helper | Bring-up / flashing |
| No Pico attached | Build workspace only | Simulator and tests | Mock telemetry |

## Current Pi Observation

- No `/dev/ttyACM*` or `/dev/ttyUSB*` Pico device detected during setup
- No Raspberry Pi USB vendor device was visible in `lsusb`

# Host Integration

## Raspberry Pi Responsibilities

- detect Pico serial devices
- build firmware artifacts
- optionally copy UF2 output to a mounted boot device
- monitor live telemetry over USB serial
- run a simulator when no hardware is attached

## Runtime Modes

### Live Hardware Mode

- `host_tools.monitor` opens the first detected Pico serial port
- boot banners and telemetry frames are parsed line-by-line
- samples are stored in SQLite and mirrored to a rotated JSONL log
- disconnects are recorded as host events

### Simulator Mode

- activated automatically when no Pico serial device is detected in `--mode auto`
- can also be forced with `--mode simulator`
- emits the same JSON-line protocol as the firmware
- supports dashboard demos, parser tests, and storage validation on a Pi with no hardware attached

## Persistence

The host-side SQLite store keeps:

- telemetry samples
- fault flags and buffer metrics
- host events such as boot banners, invalid protocol lines, and disconnects

The monitor also prunes old samples after inserts, which keeps the on-device database bounded for long-running sessions.

## Dashboard

The local dashboard is served by FastAPI and reads directly from SQLite.

Exposed routes:

- `/`
  - HTML dashboard with latest sample, recent history, and host events
- `/api/latest`
  - summary payload with latest sample and aggregate counts
- `/api/history`
  - recent telemetry samples
- `/api/events`
  - recent host-side events

## Bring-Up Sequence

1. Run `./scripts/bootstrap_pi.sh` to install cross-build and Python dependencies.
2. Run `./scripts/detect_pico.py` to inspect current hardware state.
3. Build firmware with `./scripts/build_firmware.sh`.
4. Flash with `./scripts/flash_pico.sh` once a board is mounted in BOOTSEL mode.
5. Start ingestion with `./scripts/run_monitor.sh --mode auto`.
6. Start the dashboard with `./scripts/run_dashboard.sh`.

# RTOS Design

## Tasks

- `sensor_task`: samples the active sensor layer at a fixed rate
- `telemetry_task`: serializes structured telemetry and emits JSON lines over USB
- `heartbeat_task`: updates the visible status heartbeat and liveness counters
- `fault_task`: checks task health, queue pressure, and optional watchdog behavior

## Buffering Strategy

- a FreeRTOS queue carries fresh sensor samples
- a bounded ring buffer stores recent history for diagnostics
- overflow increments fault counters instead of crashing the system

## Fault Model

- queue overflow
- stale task heartbeat
- sensor read failure
- serial output backpressure or disconnect conditions

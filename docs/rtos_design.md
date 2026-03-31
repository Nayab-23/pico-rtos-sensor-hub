# RTOS Design

## Task Responsibilities

- `sensor_task`
  - periodic producer
  - sampling interval is controlled by `SENSOR_HUB_SAMPLE_RATE_HZ`
  - reports sensor-read failures through explicit counters instead of blocking
- `telemetry_task`
  - consumer and serializer
  - publishes the freshest available sample at `SENSOR_HUB_TELEMETRY_INTERVAL_MS`
- `heartbeat_task`
  - keeps a visible heartbeat and task-liveness counter
  - remains independent from telemetry so a dead serial path does not hide scheduler liveness
- `fault_task`
  - supervisory task
  - checks whether sensor and telemetry heartbeats are still advancing
  - updates the watchdog only after the runtime remains healthy enough to do so

## Scheduling Notes

- The sample task runs at a higher priority than the heartbeat task.
- Telemetry runs separately from acquisition so serial I/O jitter does not directly set the sensor cadence.
- Fault supervision runs on a one-second cadence, which is long enough to avoid false positives while still surfacing stalled tasks quickly.

## Buffering Strategy

- a bounded FreeRTOS queue carries fresh sensor samples between acquisition and telemetry
- a bounded ring buffer stores recent history for diagnostics and last-value recovery
- queue overflow increments counters and fault flags instead of crashing the system
- telemetry can continue using the most recent ring-buffer sample even if the queue is temporarily drained

## Fault Model

- queue overflow
- stale sensor task
- stale telemetry task
- sensor read failure
- watchdog-caused reboot on the next boot cycle

## Sensor Strategy

Two modes are supported:

- `SENSOR_HUB_USE_MOCK_SENSORS=ON`
  - generates realistic synthetic telemetry for development and demonstrations
- `SENSOR_HUB_USE_MOCK_SENSORS=OFF`
  - uses the RP2040 internal temperature sensor via the ADC path

This keeps the firmware runnable before any external sensor hardware is available, while still supporting a real measurement path.

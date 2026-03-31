#!/usr/bin/env bash
set -euo pipefail

# Build the Pico firmware with configurable board and mock-sensor options.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BUILD_DIR="${BUILD_DIR:-${REPO_ROOT}/build/firmware}"
BOARD="${PICO_BOARD:-pico}"
USE_MOCK="${SENSOR_HUB_USE_MOCK_SENSORS:-ON}"
ENABLE_WATCHDOG="${SENSOR_HUB_ENABLE_WATCHDOG:-OFF}"
SAMPLE_RATE="${SENSOR_HUB_SAMPLE_RATE_HZ:-10}"
TELEMETRY_INTERVAL="${SENSOR_HUB_TELEMETRY_INTERVAL_MS:-500}"
QUEUE_LENGTH="${SENSOR_HUB_QUEUE_LENGTH:-16}"
RING_CAPACITY="${SENSOR_HUB_RING_CAPACITY:-64}"

if ! command -v cmake >/dev/null 2>&1; then
  echo "cmake is not installed. Run ./scripts/bootstrap_pi.sh first." >&2
  exit 1
fi

if ! command -v arm-none-eabi-gcc >/dev/null 2>&1; then
  echo "arm-none-eabi-gcc is not installed. Run ./scripts/bootstrap_pi.sh first." >&2
  exit 1
fi

cmake -S "${REPO_ROOT}/firmware" -B "${BUILD_DIR}" -G Ninja \
  -DPICO_BOARD="${BOARD}" \
  -DSENSOR_HUB_USE_MOCK_SENSORS="${USE_MOCK}" \
  -DSENSOR_HUB_ENABLE_WATCHDOG="${ENABLE_WATCHDOG}" \
  -DSENSOR_HUB_SAMPLE_RATE_HZ="${SAMPLE_RATE}" \
  -DSENSOR_HUB_TELEMETRY_INTERVAL_MS="${TELEMETRY_INTERVAL}" \
  -DSENSOR_HUB_QUEUE_LENGTH="${QUEUE_LENGTH}" \
  -DSENSOR_HUB_RING_CAPACITY="${RING_CAPACITY}"

cmake --build "${BUILD_DIR}" --parallel

echo "Firmware build complete:"
echo "  ${BUILD_DIR}/pico_rtos_sensor_hub.uf2"

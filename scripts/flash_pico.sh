#!/usr/bin/env bash
set -euo pipefail

# Copy the built UF2 image to a Pico mounted in BOOTSEL mode.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
UF2_PATH="${UF2_PATH:-${REPO_ROOT}/build/firmware/pico_rtos_sensor_hub.uf2}"
TARGET_MOUNT="${1:-${PICO_MOUNT_POINT:-}}"

if [[ ! -f "${UF2_PATH}" ]]; then
  echo "UF2 not found at ${UF2_PATH}. Run ./scripts/build_firmware.sh first." >&2
  exit 1
fi

if [[ -z "${TARGET_MOUNT}" ]]; then
  while IFS= read -r candidate; do
    TARGET_MOUNT="${candidate}"
    break
  done < <(find /media /run/media /mnt -type d -name RPI-RP2 2>/dev/null | sort)
fi

if [[ -z "${TARGET_MOUNT}" || ! -d "${TARGET_MOUNT}" ]]; then
  echo "Could not find an RPI-RP2 mount. Put the Pico in BOOTSEL mode and retry." >&2
  exit 1
fi

cp "${UF2_PATH}" "${TARGET_MOUNT}/"
sync

echo "Flashed ${UF2_PATH} to ${TARGET_MOUNT}"

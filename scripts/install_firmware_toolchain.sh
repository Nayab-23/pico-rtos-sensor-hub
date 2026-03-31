#!/usr/bin/env bash
set -euo pipefail

# Install the optional ARM firmware build toolchain.
# This is intentionally separate from bootstrap_pi.sh so daily work can stay
# simulator-first and avoid long provisioning steps.
PACKAGES=(
  cmake
  gcc-arm-none-eabi
  libnewlib-arm-none-eabi
  ninja-build
)

sudo apt-get update
sudo apt-get install -y "${PACKAGES[@]}"

echo "Optional firmware toolchain installed."
echo "You can now run ./scripts/build_firmware.sh"

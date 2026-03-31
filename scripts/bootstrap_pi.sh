#!/usr/bin/env bash
set -euo pipefail

# Install the Raspberry Pi packages needed for cross-building and host tooling.
PACKAGES=(
  cmake
  gcc-arm-none-eabi
  libnewlib-arm-none-eabi
  ninja-build
  python3-pip
  python3-venv
)

sudo apt-get update
sudo apt-get install -y "${PACKAGES[@]}"

echo "Base Raspberry Pi dependencies installed."
echo "Next: ./scripts/setup_host_tools.sh"

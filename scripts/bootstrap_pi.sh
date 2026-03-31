#!/usr/bin/env bash
set -euo pipefail

# Install only the lightweight Raspberry Pi packages needed for host-side tooling.
# Heavy firmware toolchain packages are intentionally deferred to
# ./scripts/install_firmware_toolchain.sh so they do not block daily work.
PACKAGES=(
  python3-pip
  python3-venv
)

sudo apt-get update
sudo apt-get install -y "${PACKAGES[@]}"

echo "Lightweight host dependencies installed."
echo "Next: ./scripts/run_simulator_validation.sh"
echo "Optional later step for real firmware builds: ./scripts/install_firmware_toolchain.sh"

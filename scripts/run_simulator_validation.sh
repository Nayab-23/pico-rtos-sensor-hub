#!/usr/bin/env bash
set -euo pipefail

# Validate the host-side tooling without requiring a Pico or firmware toolchain.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"
./scripts/setup_host_tools.sh
. .venv/bin/activate
pytest tests
python -m host_tools.monitor --mode simulator --max-messages 5

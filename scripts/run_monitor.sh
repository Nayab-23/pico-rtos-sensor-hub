#!/usr/bin/env bash
set -euo pipefail

# Run the host telemetry monitor in serial or simulator mode.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENV_PYTHON="${REPO_ROOT}/.venv/bin/python"

if [[ ! -x "${VENV_PYTHON}" ]]; then
  echo "Host tools are not installed. Run ./scripts/setup_host_tools.sh first." >&2
  exit 1
fi

exec "${VENV_PYTHON}" -m host_tools.monitor "$@"

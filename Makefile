PYTHON ?= python3
VENV ?= .venv
PIP := $(VENV)/bin/pip
PYTHON_BIN := $(VENV)/bin/python
PYTEST := $(VENV)/bin/pytest

.PHONY: host-install host-test detect-pico host-monitor host-simulator host-dashboard build-firmware

host-install:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r host_tools/requirements.txt

host-test: host-install
	$(PYTEST) tests

detect-pico: host-install
	$(PYTHON_BIN) scripts/detect_pico.py

host-monitor: host-install
	$(PYTHON_BIN) -m host_tools.monitor --mode auto

host-simulator: host-install
	$(PYTHON_BIN) -m host_tools.monitor --mode simulator

host-dashboard: host-install
	$(PYTHON_BIN) -m host_tools.dashboard --host 0.0.0.0 --port 8081

build-firmware:
	./scripts/build_firmware.sh

# Resume Bullets

- Built a Raspberry Pi Pico sensor hub on Pico SDK + FreeRTOS with four coordinated tasks for acquisition, telemetry, heartbeat, and fault supervision, plus bounded queue and ring-buffer data handling.
- Implemented a USB serial JSON telemetry protocol and a Raspberry Pi host ingestion stack with auto-detection, reconnect-safe monitoring, SQLite persistence, rotated JSONL logs, and a FastAPI dashboard.
- Designed the project to remain development-ready without hardware by adding simulator-mode telemetry, scripted build and flash helpers, and documented bring-up paths for Pico and Pico W targets.

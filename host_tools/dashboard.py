from __future__ import annotations

import argparse
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn

from .config import ensure_runtime_dirs, repo_root
from .storage import TelemetryStore


def create_app(db_path: Path | None = None) -> FastAPI:
    runtime_paths = ensure_runtime_dirs()
    store = TelemetryStore(db_path or runtime_paths.db_path)
    templates = Jinja2Templates(directory=str(repo_root() / "host_tools" / "templates"))

    app = FastAPI(title="Pico RTOS Sensor Hub Dashboard")

    @app.get("/", response_class=HTMLResponse)
    def dashboard(request: Request) -> HTMLResponse:
        summary = store.summary()
        recent_samples = store.recent_samples(20)
        recent_events = store.recent_events(10)
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "summary": summary,
                "recent_samples": recent_samples,
                "recent_events": recent_events,
            },
        )

    @app.get("/api/latest")
    def latest_sample() -> dict[str, object]:
        return store.summary()

    @app.get("/api/history")
    def sample_history(limit: int = 50) -> list[dict[str, object]]:
        return store.recent_samples(limit)

    @app.get("/api/events")
    def event_history(limit: int = 20) -> list[dict[str, object]]:
        return store.recent_events(limit)

    return app


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve the Pico RTOS sensor hub dashboard.")
    parser.add_argument("--db-path", type=Path)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8081)
    args = parser.parse_args()

    app = create_app(args.db_path)
    uvicorn.run(app, host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

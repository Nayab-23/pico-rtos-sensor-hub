from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class RuntimePaths:
    root: Path
    data_dir: Path
    log_dir: Path
    db_path: Path
    telemetry_log_path: Path


def default_runtime_paths() -> RuntimePaths:
    root = repo_root()
    data_dir = root / "runtime" / "data"
    log_dir = root / "runtime" / "logs"
    return RuntimePaths(
        root=root,
        data_dir=data_dir,
        log_dir=log_dir,
        db_path=data_dir / "telemetry.db",
        telemetry_log_path=log_dir / "telemetry.jsonl",
    )


def ensure_runtime_dirs(paths: RuntimePaths | None = None) -> RuntimePaths:
    paths = paths or default_runtime_paths()
    paths.data_dir.mkdir(parents=True, exist_ok=True)
    paths.log_dir.mkdir(parents=True, exist_ok=True)
    return paths

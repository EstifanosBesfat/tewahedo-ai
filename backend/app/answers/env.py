"""Load a local backend environment file without printing its values."""

from __future__ import annotations

import os
from pathlib import Path


def backend_env_path() -> Path:
    return Path(__file__).resolve().parents[2] / ".env"


def load_backend_env(path: Path | None = None) -> None:
    """Set missing environment variables from backend/.env.

    Values already present in the process environment stay in place.
    Lines are never logged.
    """

    env_path = backend_env_path() if path is None else path
    if not env_path.is_file():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key or key in os.environ:
            continue
        os.environ[key] = value.strip().strip('"').strip("'")

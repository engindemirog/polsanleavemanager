"""Starts the application locally: ``uv run python -m app`` (README)."""

import os
from collections.abc import Mapping
from dataclasses import dataclass

import uvicorn

# Loopback only: by default the app is not reachable from the network (spec 0001, R-1).
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000


@dataclass(frozen=True)
class RunSettings:
    host: str
    port: int


def settings_from_env(env: Mapping[str, str]) -> RunSettings:
    return RunSettings(
        # An empty value falls back too: "" would bind every interface (review F-2).
        host=env.get("PLM_HOST") or DEFAULT_HOST,
        port=int(env.get("PLM_PORT", DEFAULT_PORT)),
    )


def main() -> None:
    settings = settings_from_env(os.environ)
    uvicorn.run("app.main:app", host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()

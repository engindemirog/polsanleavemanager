"""E2E: owns the app-under-test lifecycle (docs/testing.md, Resource hygiene rule 4)."""

import os
import socket
import subprocess
import sys
import time
from collections.abc import Iterator
from pathlib import Path

import httpx
import pytest

E2E_DIR = Path(__file__).parent
READY_TIMEOUT_S = 10.0
STOP_TIMEOUT_S = 5.0


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    # Every test under tests/e2e is e2e: a new one cannot slip into the fast profile.
    for item in items:
        if E2E_DIR in item.path.parents:
            item.add_marker(pytest.mark.e2e)


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port: int = sock.getsockname()[1]
        return port


def _wait_until_ready(process: subprocess.Popen[bytes], url: str) -> None:
    deadline = time.monotonic() + READY_TIMEOUT_S
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"app under test exited early with code {process.returncode}")
        try:
            if httpx.get(f"{url}/api/health", timeout=1.0).status_code == 200:
                return
        except httpx.TransportError:
            pass
        time.sleep(0.1)
    raise TimeoutError(f"app under test not ready within {READY_TIMEOUT_S} s")


def _stop(process: subprocess.Popen[bytes]) -> None:
    process.terminate()
    try:
        process.wait(timeout=STOP_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


@pytest.fixture(scope="session")
def base_url() -> Iterator[str]:
    """Starts the app with the README command (`python -m app`), default host, a free port."""
    port = _free_port()
    env = {**os.environ, "PLM_PORT": str(port)}
    env.pop("PLM_HOST", None)  # AC-1: the default host must be what we reach
    process = subprocess.Popen([sys.executable, "-m", "app"], env=env)
    try:
        url = f"http://127.0.0.1:{port}"
        _wait_until_ready(process, url)
        yield url
    finally:
        _stop(process)

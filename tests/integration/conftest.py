from collections.abc import Callable

import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.main import create_app


def add_route(app: FastAPI, path: str, endpoint: Callable[[], object]) -> None:
    """Registers a test-only route ahead of the catch-all static mount."""
    app.router.routes.insert(0, APIRoute(path, endpoint, methods=["GET"]))


@pytest.fixture
def app() -> FastAPI:
    return create_app()


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    # follow_redirects=False: a redirect is a response under test, never silently followed.
    return TestClient(app, raise_server_exceptions=False, follow_redirects=False)

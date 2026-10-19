import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tests.integration.conftest import add_route

EXPECTED_HEADERS = {
    "content-security-policy": "default-src 'self'",
    "x-content-type-options": "nosniff",
    "referrer-policy": "same-origin",
}


def _boom() -> None:
    raise RuntimeError("boom")


@pytest.mark.parametrize(
    ("path", "status"),
    [
        ("/", 200),
        ("/api/health", 200),
        ("/api/does-not-exist", 404),
        ("/api/test-boom", 500),
    ],
    ids=["landing-page", "health", "not-found", "server-error"],
)
def test_security_headers_present(app: FastAPI, client: TestClient, path: str, status: int) -> None:
    """AC-9"""
    add_route(app, "/api/test-boom", _boom)

    response = client.get(path)

    assert response.status_code == status
    for name, value in EXPECTED_HEADERS.items():
        assert response.headers.get(name) == value

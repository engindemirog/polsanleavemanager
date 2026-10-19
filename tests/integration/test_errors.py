import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.shared.errors import PROBLEM_MEDIA_TYPE, DomainError
from tests.integration.conftest import add_route

HIDDEN_MESSAGE = "gizli-istisna-mesaji"


def _boom() -> None:
    raise RuntimeError(HIDDEN_MESSAGE)


def _assert_problem(response_json: dict[str, object], status: int, code: str) -> None:
    assert response_json["status"] == status
    assert response_json["code"] == code
    assert isinstance(response_json["title"], str) and response_json["title"]
    assert isinstance(response_json["detail"], str) and response_json["detail"]


def test_unknown_api_path_returns_not_found_problem(client: TestClient) -> None:
    """AC-5"""
    response = client.get("/api/does-not-exist")

    assert response.status_code == 404
    assert response.headers["content-type"] == PROBLEM_MEDIA_TYPE
    _assert_problem(response.json(), 404, "not_found")
    assert response.json()["title"] == "Bulunamadı"


def test_unknown_non_api_path_returns_not_found_problem(client: TestClient) -> None:
    """AC-5"""
    response = client.get("/does-not-exist")

    assert response.status_code == 404
    assert response.headers["content-type"] == PROBLEM_MEDIA_TYPE
    _assert_problem(response.json(), 404, "not_found")


def test_unsupported_method_returns_method_not_allowed_problem(client: TestClient) -> None:
    """AC-6"""
    response = client.post("/api/health")

    assert response.status_code == 405
    assert response.headers["content-type"] == PROBLEM_MEDIA_TYPE
    _assert_problem(response.json(), 405, "method_not_allowed")
    assert response.json()["title"] == "Yöntem desteklenmiyor"


def test_unexpected_error_returns_generic_problem_with_correlation_id(
    app: FastAPI, client: TestClient
) -> None:
    """AC-7: generic Turkish message, correlation ID, no internals."""
    add_route(app, "/api/test-boom", _boom)

    response = client.get("/api/test-boom")

    assert response.status_code == 500
    assert response.headers["content-type"] == PROBLEM_MEDIA_TYPE
    body = response.json()
    _assert_problem(body, 500, "internal_error")
    assert body["title"] == "Beklenmeyen bir hata oluştu"
    assert isinstance(body["correlation_id"], str) and body["correlation_id"]
    for leak in (HIDDEN_MESSAGE, "RuntimeError", "Traceback", ".py"):
        assert leak not in response.text


def test_unexpected_error_log_has_correlation_id_and_no_request_data(
    app: FastAPI, client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    """AC-7: the same correlation ID is logged with the error; body, cookies, headers are not."""
    add_route(app, "/api/test-boom", _boom)
    client.cookies.set("session", "cerez-degeri")

    with caplog.at_level(logging.ERROR, logger="app.errors"):
        response = client.request(
            "GET",
            "/api/test-boom",
            content=b"govde-icerigi",
            headers={"X-Custom": "baslik-degeri"},
        )

    log_text = caplog.text
    assert response.json()["correlation_id"] in log_text
    assert "RuntimeError" in log_text
    assert "GET" in log_text and "/api/test-boom" in log_text
    for leak in (HIDDEN_MESSAGE, "cerez-degeri", "govde-icerigi", "baslik-degeri"):
        assert leak not in log_text


def test_two_unexpected_errors_get_different_correlation_ids(
    app: FastAPI, client: TestClient
) -> None:
    """AC-8"""
    add_route(app, "/api/test-boom", _boom)

    first = client.get("/api/test-boom").json()["correlation_id"]
    second = client.get("/api/test-boom").json()["correlation_id"]

    assert first != second


class _OverlapError(DomainError):
    status_code = 409
    code = "test_overlap"
    title = "Çakışma"
    detail = "Test amaçlı çakışma."


def _raise_domain_error() -> None:
    raise _OverlapError


def test_domain_error_returns_its_problem(app: FastAPI, client: TestClient) -> None:
    """R-5: business rule violations use the same standard shape."""
    add_route(app, "/api/test-domain", _raise_domain_error)

    response = client.get("/api/test-domain")

    assert response.status_code == 409
    assert response.headers["content-type"] == PROBLEM_MEDIA_TYPE
    _assert_problem(response.json(), 409, "test_overlap")

"""HTTP-level error handling and security headers shared by every route."""

import logging
import traceback
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.shared.errors import DomainError, problem_response

logger = logging.getLogger("app.errors")

SECURITY_HEADERS = (
    (b"content-security-policy", b"default-src 'self'"),
    (b"x-content-type-options", b"nosniff"),
    (b"referrer-policy", b"same-origin"),
)

_HTTP_PROBLEMS = {
    404: ("not_found", "Bulunamadı", "İstenen kaynak bulunamadı."),
    405: (
        "method_not_allowed",
        "Yöntem desteklenmiyor",
        "Bu adres bu istek yöntemini desteklemiyor.",
    ),
}
_GENERIC_HTTP_PROBLEM = ("http_error", "İstek işlenemedi", "İstek işlenemedi.")


async def _http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, HTTPException):  # registered for HTTPException only
        raise exc
    code, title, detail = _HTTP_PROBLEMS.get(exc.status_code, _GENERIC_HTTP_PROBLEM)
    return problem_response(exc.status_code, code, title, detail, headers=exc.headers)


async def _domain_error_handler(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, DomainError):  # registered for DomainError only
        raise exc
    return problem_response(exc.status_code, exc.code, exc.title, exc.detail)


class UnhandledErrorMiddleware:
    """Turns any unexpected exception into a generic 500 problem with a correlation ID.

    The log record carries only the correlation ID, method, path, exception type and stack
    frames — never the exception message, body, cookies or headers (docs/security.md, KVKK).
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        response_started = False

        async def send_tracking(message: Message) -> None:
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, receive, send_tracking)
        except Exception as exc:
            if response_started:
                raise
            correlation_id = uuid.uuid4().hex
            logger.error(
                "unhandled error correlation_id=%s method=%s path=%s exception=%s\n%s",
                correlation_id,
                scope["method"],
                scope["path"],
                type(exc).__name__,
                "".join(traceback.format_tb(exc.__traceback__)),
            )
            response = problem_response(
                500,
                "internal_error",
                "Beklenmeyen bir hata oluştu",
                "İsteğiniz işlenirken beklenmeyen bir hata oluştu. Destek ekibine korelasyon "
                "kimliğini iletin.",
                correlation_id=correlation_id,
            )
            await response(scope, receive, send)


class SecurityHeadersMiddleware:
    """Adds the docs/security.md response headers to every HTTP response, errors included."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                message["headers"] = [*message.get("headers", []), *SECURITY_HEADERS]
            await send(message)

        await self.app(scope, receive, send_with_headers)


def install_error_handling(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, _http_exception_handler)
    app.add_exception_handler(DomainError, _domain_error_handler)
    # Starlette renders 500s outside user middleware; catching them here keeps them inside
    # SecurityHeadersMiddleware (added last = outermost).
    app.add_middleware(UnhandledErrorMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)

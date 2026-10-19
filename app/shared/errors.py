"""The one error shape of the system: RFC 9457 problem+json (docs/conventions.md)."""

from collections.abc import Mapping
from typing import Any

from fastapi.responses import JSONResponse

PROBLEM_MEDIA_TYPE = "application/problem+json"


class DomainError(Exception):
    """A business rule violation. Subclasses set ``code``, ``title`` and ``detail`` (Turkish)."""

    status_code = 400
    code = "domain_error"
    title = "İşlem kurala aykırı"
    detail = "İstenen işlem bir iş kuralını ihlal ediyor."


def problem_response(
    status: int,
    code: str,
    title: str,
    detail: str,
    headers: Mapping[str, str] | None = None,
    **extra: Any,
) -> JSONResponse:
    body: dict[str, Any] = {
        "type": "about:blank",
        "title": title,
        "status": status,
        "detail": detail,
        "code": code,
        **extra,
    }
    return JSONResponse(body, status_code=status, headers=headers, media_type=PROBLEM_MEDIA_TYPE)

"""Response helpers for the read-only local service."""

from dataclasses import dataclass
from html import escape
import json
from typing import Any, Mapping


DEFAULT_LIMITATIONS = (
    "local reviewed index only",
    "read-only service",
    "no live source inspection",
)


@dataclass(frozen=True)
class LocalServiceResponse:
    status_code: int
    content_type: str
    body: str
    headers: Mapping[str, str]
    payload: Mapping[str, Any]


def json_response(
    status_code: int,
    payload: Mapping[str, Any],
    headers: Mapping[str, str] | None = None,
) -> LocalServiceResponse:
    body_payload = _normalize_payload(payload, status_code=status_code)
    return LocalServiceResponse(
        status_code=status_code,
        content_type="application/json; charset=utf-8",
        body=json.dumps(body_payload, indent=2, sort_keys=True),
        headers=_headers(headers),
        payload=body_payload,
    )


def error_response(
    status_code: int,
    code: str,
    message: str,
    details: Mapping[str, Any] | None = None,
) -> LocalServiceResponse:
    payload: dict[str, Any] = {
        "schema_version": "local_http_error_response.v0",
        "status": "fail",
        "error": {
            "code": code,
            "message": message,
            "details": dict(details or {}),
        },
        "warnings": [],
        "limitations": list(DEFAULT_LIMITATIONS),
    }
    return json_response(status_code, payload)


def text_response(
    status_code: int,
    text: str,
    headers: Mapping[str, str] | None = None,
) -> LocalServiceResponse:
    payload = _normalize_payload(
        {
            "schema_version": "local_http_text_response.v0",
            "status": "pass" if 200 <= status_code < 400 else "fail",
            "text": text,
            "warnings": [],
            "limitations": list(DEFAULT_LIMITATIONS),
        },
        status_code=status_code,
    )
    return LocalServiceResponse(
        status_code=status_code,
        content_type="text/plain; charset=utf-8",
        body=text,
        headers=_headers(headers),
        payload=payload,
    )


def html_response(
    status_code: int,
    html: str,
    payload: Mapping[str, Any] | None = None,
    headers: Mapping[str, str] | None = None,
) -> LocalServiceResponse:
    return LocalServiceResponse(
        status_code=status_code,
        content_type="text/html; charset=utf-8",
        body=html,
        headers=_headers(headers),
        payload=_normalize_payload(payload or {"schema_version": "local_http_html_response.v0"}, status_code=status_code),
    )


def redirect_response(location: str, status_code: int = 302) -> LocalServiceResponse:
    safe_location = str(location or "/")
    body = "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            "  <title>Continue - Eureka</title>",
            "</head>",
            "<body>",
            f'  <main><p>Continue to <a href="{escape(safe_location, quote=True)}">{escape(safe_location)}</a>.</p></main>',
            "</body>",
            "</html>",
        ]
    )
    payload = _normalize_payload(
        {
            "schema_version": "local_http_redirect_response.v0",
            "status": "redirect",
            "location": safe_location,
            "warnings": [],
            "limitations": list(DEFAULT_LIMITATIONS),
        },
        status_code=status_code,
    )
    return LocalServiceResponse(
        status_code=status_code,
        content_type="text/html; charset=utf-8",
        body=body,
        headers=_headers({"Location": safe_location}),
        payload=payload,
    )


def _normalize_payload(payload: Mapping[str, Any], *, status_code: int) -> dict[str, Any]:
    normalized = dict(payload)
    normalized.setdefault("schema_version", "local_http_response.v0")
    normalized.setdefault("status", "pass" if 200 <= status_code < 400 else "fail")
    normalized.setdefault("warnings", [])
    normalized.setdefault("limitations", list(DEFAULT_LIMITATIONS))
    return normalized


def _headers(headers: Mapping[str, str] | None) -> dict[str, str]:
    merged = {
        "Cache-Control": "no-store",
        "X-Eureka-Local-Service": "read-only",
    }
    if headers:
        merged.update({str(key): str(value) for key, value in headers.items()})
    return merged

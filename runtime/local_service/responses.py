"""Response helpers for the read-only local service."""

from dataclasses import dataclass
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

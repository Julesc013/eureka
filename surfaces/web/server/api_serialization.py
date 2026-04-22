from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping


_STATUS_LINES = {
    200: "200 OK",
    202: "202 Accepted",
    400: "400 Bad Request",
    404: "404 Not Found",
    405: "405 Method Not Allowed",
    422: "422 Unprocessable Entity",
    503: "503 Service Unavailable",
}


@dataclass(frozen=True)
class SerializedHttpResponse:
    status: str
    content_type: str
    payload: bytes
    headers: tuple[tuple[str, str], ...] = ()


def json_response(
    status_code: int,
    payload: Mapping[str, Any],
    *,
    headers: tuple[tuple[str, str], ...] = (),
) -> SerializedHttpResponse:
    body = json.dumps(dict(payload), indent=2, sort_keys=True)
    encoded = f"{body}\n".encode("utf-8")
    return SerializedHttpResponse(
        status=status_line(status_code),
        content_type="application/json; charset=utf-8",
        payload=encoded,
        headers=headers,
    )


def bytes_response(
    status_code: int,
    *,
    content_type: str,
    payload: bytes,
    filename: str | None = None,
) -> SerializedHttpResponse:
    headers: list[tuple[str, str]] = []
    if filename is not None:
        headers.append(("Content-Disposition", f"attachment; filename=\"{filename}\""))
    return SerializedHttpResponse(
        status=status_line(status_code),
        content_type=content_type,
        payload=payload,
        headers=tuple(headers),
    )


def error_response(
    status_code: int,
    *,
    code: str,
    message: str,
    extra_fields: Mapping[str, Any] | None = None,
    headers: tuple[tuple[str, str], ...] = (),
) -> SerializedHttpResponse:
    payload: dict[str, Any] = {
        "status": "blocked",
        "code": code,
        "message": message,
    }
    if extra_fields:
        payload.update(extra_fields)
    return json_response(status_code, payload, headers=headers)


def status_line(status_code: int) -> str:
    try:
        return _STATUS_LINES[status_code]
    except KeyError as error:
        raise ValueError(f"Unsupported bootstrap HTTP status code '{status_code}'.") from error

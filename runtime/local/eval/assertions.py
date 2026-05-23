"""Assertions for deterministic local evaluation."""

from __future__ import annotations

import json
from typing import Any, Mapping

from .errors import LocalEvalValidationError


def assert_status_ok(response: Mapping[str, Any], allowed: tuple[int, ...] = (200,)) -> None:
    status_code = int(response.get("status_code", 0) or 0)
    if status_code not in allowed:
        raise LocalEvalValidationError(f"unexpected status {status_code}; expected one of {allowed}")


def assert_json_shape(payload: Any, required: tuple[str, ...] = ()) -> None:
    if not isinstance(payload, Mapping):
        raise LocalEvalValidationError("JSON payload is required")
    for key in required:
        if key not in payload:
            raise LocalEvalValidationError(f"JSON payload is missing {key}")


def assert_html_contains(text: str, marker: str) -> None:
    if marker not in text:
        raise LocalEvalValidationError(f"HTML marker missing: {marker}")


def assert_html_not_contains(text: str, marker: str) -> None:
    if marker.lower() in text.lower():
        raise LocalEvalValidationError(f"HTML forbidden marker present: {marker}")


def assert_no_mutation_controls(html: str) -> None:
    lowered = html.lower()
    for marker in ("method=\"post\"", "formmethod=\"post\"", "enable lan", "execute worker", "run source probe"):
        if marker in lowered:
            raise LocalEvalValidationError(f"mutation control marker present: {marker}")


def assert_absence_non_global(value: Any) -> None:
    text = json.dumps(value, sort_keys=True).lower() if not isinstance(value, str) else value.lower()
    if "reviewed_public_index" not in text and "reviewed public index" not in text and "local reviewed index" not in text:
        raise LocalEvalValidationError("absence checked layer marker is missing")
    if "not global" not in text and "not proof" not in text and "does not prove" not in text:
        raise LocalEvalValidationError("absence non-global wording is missing")


def assert_route_rejected(response: Mapping[str, Any], allowed: tuple[int, ...] = (400, 401, 403, 404, 405)) -> None:
    assert_status_ok(response, allowed)

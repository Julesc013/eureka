from __future__ import annotations

from typing import Any, Mapping


def search_response_envelope_to_search_results_view_model(
    search_envelope: Mapping[str, Any],
) -> dict[str, Any]:
    view_model: dict[str, Any] = {
        "query": _require_string(search_envelope.get("query"), "search_envelope.query"),
        "result_count": _require_int(search_envelope.get("result_count"), "search_envelope.result_count"),
        "results": _coerce_results(search_envelope.get("results")),
    }

    absence = search_envelope.get("absence")
    if absence is not None:
        view_model["absence"] = _coerce_absence(absence)

    return view_model


def _coerce_results(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError("search_envelope.results must be a list.")

    results: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"search_envelope.results[{index}] must be an object.")
        result = {
            "target_ref": _require_string(item.get("target_ref"), f"search_envelope.results[{index}].target_ref"),
            "object": _coerce_object_summary(item.get("object"), f"search_envelope.results[{index}].object"),
        }
        results.append(result)
    return results


def _coerce_object_summary(value: Any, field_name: str) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")

    summary = {"id": _require_string(value.get("id"), f"{field_name}.id")}
    kind = _optional_string(value.get("kind"), f"{field_name}.kind")
    label = _optional_string(value.get("label"), f"{field_name}.label")
    if kind is not None:
        summary["kind"] = kind
    if label is not None:
        summary["label"] = label
    return summary


def _coerce_absence(value: Any) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise ValueError("search_envelope.absence must be an object.")
    return {
        "code": _require_string(value.get("code"), "search_envelope.absence.code"),
        "message": _require_string(value.get("message"), "search_envelope.absence.message"),
    }


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value


def _optional_string(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string when provided.")
    return value


def _require_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer.")
    return value

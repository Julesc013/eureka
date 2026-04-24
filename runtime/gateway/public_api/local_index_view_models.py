from __future__ import annotations

from typing import Any, Mapping


def local_index_envelope_to_view_model(envelope: Mapping[str, Any]) -> dict[str, Any]:
    view_model: dict[str, Any] = {
        "status": _require_string(envelope.get("status"), "envelope.status"),
        "index": _coerce_index(envelope.get("index"), "envelope.index"),
    }
    query = envelope.get("query")
    if query is not None:
        view_model["query"] = _require_string(query, "envelope.query")
    result_count = envelope.get("result_count")
    if result_count is not None:
        view_model["result_count"] = _require_non_negative_int(
            result_count,
            "envelope.result_count",
        )
    results = envelope.get("results")
    if results is not None:
        view_model["results"] = _coerce_results(results, "envelope.results")
    notices = envelope.get("notices")
    if notices is not None:
        view_model["notices"] = _coerce_notices(notices, "envelope.notices")
    return view_model


def _coerce_index(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    index_path = value.get("index_path")
    payload: dict[str, Any] = {
        "index_path_kind": _require_string(value.get("index_path_kind"), f"{field_name}.index_path_kind"),
        "fts_mode": _require_string(value.get("fts_mode"), f"{field_name}.fts_mode"),
        "record_count": _require_non_negative_int(value.get("record_count"), f"{field_name}.record_count"),
        "record_kind_counts": _coerce_record_kind_counts(
            value.get("record_kind_counts"),
            f"{field_name}.record_kind_counts",
        ),
    }
    if index_path is not None:
        payload["index_path"] = _require_string(index_path, f"{field_name}.index_path")
    return payload


def _coerce_record_kind_counts(value: Any, field_name: str) -> dict[str, int]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    counts: dict[str, int] = {}
    for key, raw_value in value.items():
        if not isinstance(key, str) or not key:
            raise ValueError(f"{field_name} keys must be non-empty strings.")
        counts[key] = _require_non_negative_int(raw_value, f"{field_name}.{key}")
    return counts


def _coerce_results(value: Any, field_name: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    results: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        result: dict[str, Any] = {
            "index_record_id": _require_string(item.get("index_record_id"), f"{field_name}[{index}].index_record_id"),
            "record_kind": _require_string(item.get("record_kind"), f"{field_name}[{index}].record_kind"),
            "label": _require_string(item.get("label"), f"{field_name}[{index}].label"),
            "evidence": _coerce_string_list(item.get("evidence"), f"{field_name}[{index}].evidence"),
            "route_hints": _coerce_json_mapping(item.get("route_hints"), f"{field_name}[{index}].route_hints"),
        }
        for optional_name in (
            "summary",
            "target_ref",
            "resolved_resource_id",
            "source_id",
            "source_family",
            "source_label",
            "subject_key",
            "version_or_state",
            "representation_id",
            "member_path",
        ):
            optional_value = item.get(optional_name)
            if optional_value is not None:
                result[optional_name] = _require_string(
                    optional_value,
                    f"{field_name}[{index}].{optional_name}",
                )
        results.append(result)
    return results


def _coerce_json_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    payload: dict[str, Any] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key:
            raise ValueError(f"{field_name} keys must be non-empty strings.")
        payload[key] = _clone_json_like(item, f"{field_name}.{key}")
    return payload


def _clone_json_like(value: Any, field_name: str) -> Any:
    if isinstance(value, Mapping):
        return _coerce_json_mapping(value, field_name)
    if isinstance(value, list):
        return [_clone_json_like(item, f"{field_name}[]") for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise ValueError(f"{field_name} must contain only JSON-compatible values.")


def _coerce_notices(value: Any, field_name: str) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    notices: list[dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        notice: dict[str, str] = {
            "code": _require_string(item.get("code"), f"{field_name}[{index}].code"),
            "severity": _require_string(item.get("severity"), f"{field_name}[{index}].severity"),
        }
        message = item.get("message")
        if message is not None:
            notice["message"] = _require_string(message, f"{field_name}[{index}].message")
        notices.append(notice)
    return notices


def _coerce_string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    return [_require_string(item, f"{field_name}[{index}]") for index, item in enumerate(value)]


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value


def _require_non_negative_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer.")
    return value

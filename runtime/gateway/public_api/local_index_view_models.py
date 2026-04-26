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
            "parent_target_ref",
            "parent_resolved_resource_id",
            "parent_representation_id",
            "parent_object_label",
            "member_kind",
            "media_type",
            "content_hash",
        ):
            optional_value = item.get(optional_name)
            if optional_value is not None:
                result[optional_name] = _require_string(
                    optional_value,
                    f"{field_name}[{index}].{optional_name}",
                )
        size_bytes = item.get("size_bytes")
        if size_bytes is not None:
            result["size_bytes"] = _require_non_negative_int(
                size_bytes,
                f"{field_name}[{index}].size_bytes",
            )
        action_hints = item.get("action_hints")
        if action_hints is not None:
            result["action_hints"] = _coerce_string_list(
                action_hints,
                f"{field_name}[{index}].action_hints",
            )
        compatibility_evidence = item.get("compatibility_evidence")
        if compatibility_evidence is not None:
            result["compatibility_evidence"] = _coerce_json_list(
                compatibility_evidence,
                f"{field_name}[{index}].compatibility_evidence",
            )
        compatibility_summary = item.get("compatibility_summary")
        if compatibility_summary is not None:
            result["compatibility_summary"] = _require_string(
                compatibility_summary,
                f"{field_name}[{index}].compatibility_summary",
            )
        _copy_usefulness_fields(item, result, f"{field_name}[{index}]")
        results.append(result)
    return results


def _copy_usefulness_fields(value: Mapping[str, Any], result: dict[str, Any], field_name: str) -> None:
    result_lanes = value.get("result_lanes")
    if result_lanes is not None:
        result["result_lanes"] = _coerce_string_list(result_lanes, f"{field_name}.result_lanes")
    primary_lane = value.get("primary_lane")
    if primary_lane is not None:
        result["primary_lane"] = _require_string(primary_lane, f"{field_name}.primary_lane")
    user_cost_score = value.get("user_cost_score")
    if user_cost_score is not None:
        result["user_cost_score"] = _require_non_negative_int(
            user_cost_score,
            f"{field_name}.user_cost_score",
        )
    user_cost_reasons = value.get("user_cost_reasons")
    if user_cost_reasons is not None:
        result["user_cost_reasons"] = _coerce_string_list(
            user_cost_reasons,
            f"{field_name}.user_cost_reasons",
        )
    usefulness_summary = value.get("usefulness_summary")
    if usefulness_summary is not None:
        result["usefulness_summary"] = _require_string(usefulness_summary, f"{field_name}.usefulness_summary")


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


def _coerce_json_list(value: Any, field_name: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    return [_clone_json_like(item, f"{field_name}[{index}]") for index, item in enumerate(value)]


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

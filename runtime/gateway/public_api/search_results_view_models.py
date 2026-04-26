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
        resolved_resource_id = _optional_string(
            item.get("resolved_resource_id"),
            f"search_envelope.results[{index}].resolved_resource_id",
        )
        if resolved_resource_id is not None:
            result["resolved_resource_id"] = resolved_resource_id
        source = _optional_source_summary(item.get("source"), f"search_envelope.results[{index}].source")
        if source is not None:
            result["source"] = source
        evidence = _optional_evidence_list(item.get("evidence"), f"search_envelope.results[{index}].evidence")
        if evidence:
            result["evidence"] = evidence
        _copy_usefulness_fields(item, result, f"search_envelope.results[{index}]")
        results.append(result)
    return results


def _coerce_object_summary(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")

    summary: dict[str, Any] = {"id": _require_string(value.get("id"), f"{field_name}.id")}
    kind = _optional_string(value.get("kind"), f"{field_name}.kind")
    label = _optional_string(value.get("label"), f"{field_name}.label")
    if kind is not None:
        summary["kind"] = kind
    if label is not None:
        summary["label"] = label
    for optional_name in (
        "record_kind",
        "parent_target_ref",
        "parent_resolved_resource_id",
        "parent_representation_id",
        "parent_object_label",
        "member_path",
        "member_label",
        "member_kind",
        "media_type",
        "content_hash",
    ):
        optional_value = _optional_string(value.get(optional_name), f"{field_name}.{optional_name}")
        if optional_value is not None:
            summary[optional_name] = optional_value
    size_bytes = _optional_non_negative_int(value.get("size_bytes"), f"{field_name}.size_bytes")
    if size_bytes is not None:
        summary["size_bytes"] = size_bytes
    action_hints = value.get("action_hints")
    if action_hints is not None:
        summary["action_hints"] = _coerce_string_list(action_hints, f"{field_name}.action_hints")
    _copy_usefulness_fields(value, summary, field_name)
    return summary


def _copy_usefulness_fields(value: Mapping[str, Any], result: dict[str, Any], field_name: str) -> None:
    result_lanes = value.get("result_lanes")
    if result_lanes is not None:
        result["result_lanes"] = _coerce_string_list(result_lanes, f"{field_name}.result_lanes")
    primary_lane = _optional_string(value.get("primary_lane"), f"{field_name}.primary_lane")
    if primary_lane is not None:
        result["primary_lane"] = primary_lane
    user_cost_score = _optional_non_negative_int(value.get("user_cost_score"), f"{field_name}.user_cost_score")
    if user_cost_score is not None:
        result["user_cost_score"] = user_cost_score
    user_cost_reasons = value.get("user_cost_reasons")
    if user_cost_reasons is not None:
        result["user_cost_reasons"] = _coerce_string_list(
            user_cost_reasons,
            f"{field_name}.user_cost_reasons",
        )
    usefulness_summary = _optional_string(value.get("usefulness_summary"), f"{field_name}.usefulness_summary")
    if usefulness_summary is not None:
        result["usefulness_summary"] = usefulness_summary


def _coerce_absence(value: Any) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise ValueError("search_envelope.absence must be an object.")
    return {
        "code": _require_string(value.get("code"), "search_envelope.absence.code"),
        "message": _require_string(value.get("message"), "search_envelope.absence.message"),
    }


def _optional_source_summary(value: Any, field_name: str) -> dict[str, str] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    source = {
        "family": _require_string(value.get("family"), f"{field_name}.family"),
    }
    source_id = _optional_string(value.get("source_id"), f"{field_name}.source_id")
    label = _optional_string(value.get("label"), f"{field_name}.label")
    locator = _optional_string(value.get("locator"), f"{field_name}.locator")
    if source_id is not None:
        source["source_id"] = source_id
    if label is not None:
        source["label"] = label
    if locator is not None:
        source["locator"] = locator
    return source


def _optional_evidence_list(value: Any, field_name: str) -> list[dict[str, str]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    return [_coerce_evidence_summary(item, f"{field_name}[{index}]") for index, item in enumerate(value)]


def _coerce_evidence_summary(value: Any, field_name: str) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    evidence = {
        "claim_kind": _require_string(value.get("claim_kind"), f"{field_name}.claim_kind"),
        "claim_value": _require_string(value.get("claim_value"), f"{field_name}.claim_value"),
        "asserted_by_family": _require_string(
            value.get("asserted_by_family"),
            f"{field_name}.asserted_by_family",
        ),
        "evidence_kind": _require_string(value.get("evidence_kind"), f"{field_name}.evidence_kind"),
        "evidence_locator": _require_string(
            value.get("evidence_locator"),
            f"{field_name}.evidence_locator",
        ),
    }
    asserted_by_label = _optional_string(value.get("asserted_by_label"), f"{field_name}.asserted_by_label")
    asserted_at = _optional_string(value.get("asserted_at"), f"{field_name}.asserted_at")
    if asserted_by_label is not None:
        evidence["asserted_by_label"] = asserted_by_label
    if asserted_at is not None:
        evidence["asserted_at"] = asserted_at
    return evidence


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


def _optional_non_negative_int(value: Any, field_name: str) -> int | None:
    if value is None:
        return None
    return _require_int(value, field_name)


def _coerce_string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    return [_require_string(item, f"{field_name}[{index}]") for index, item in enumerate(value)]

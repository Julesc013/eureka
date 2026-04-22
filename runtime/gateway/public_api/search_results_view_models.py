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


def _optional_source_summary(value: Any, field_name: str) -> dict[str, str] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    source = {
        "family": _require_string(value.get("family"), f"{field_name}.family"),
    }
    label = _optional_string(value.get("label"), f"{field_name}.label")
    locator = _optional_string(value.get("locator"), f"{field_name}.locator")
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

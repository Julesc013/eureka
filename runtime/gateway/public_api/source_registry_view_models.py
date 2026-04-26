from __future__ import annotations

from typing import Any, Mapping


def source_registry_envelope_to_view_model(envelope: Mapping[str, Any]) -> dict[str, Any]:
    view_model: dict[str, Any] = {
        "status": _require_string(envelope.get("status"), "envelope.status"),
        "source_count": _require_non_negative_int(envelope.get("source_count"), "envelope.source_count"),
        "sources": _coerce_sources(envelope.get("sources"), "envelope.sources"),
    }
    applied_filters = envelope.get("applied_filters")
    if applied_filters is not None:
        view_model["applied_filters"] = _coerce_applied_filters(applied_filters)
    selected_source_id = _optional_string(
        envelope.get("selected_source_id"),
        "envelope.selected_source_id",
    )
    if selected_source_id is not None:
        view_model["selected_source_id"] = selected_source_id
    notices = envelope.get("notices")
    if notices is not None:
        view_model["notices"] = _coerce_notices(notices, "envelope.notices")
    return view_model


def _coerce_sources(value: Any, field_name: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    sources: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        source = {
            "source_id": _require_string(item.get("source_id"), f"{field_name}[{index}].source_id"),
            "name": _require_string(item.get("name"), f"{field_name}[{index}].name"),
            "source_family": _require_string(
                item.get("source_family"),
                f"{field_name}[{index}].source_family",
            ),
            "status": _require_string(item.get("status"), f"{field_name}[{index}].status"),
            "status_summary": _require_string(
                item.get("status_summary"),
                f"{field_name}[{index}].status_summary",
            ),
            "roles": _coerce_string_list(item.get("roles"), f"{field_name}[{index}].roles"),
            "surfaces": _coerce_string_list(item.get("surfaces"), f"{field_name}[{index}].surfaces"),
            "trust_lane": _require_string(item.get("trust_lane"), f"{field_name}[{index}].trust_lane"),
            "authority_class": _require_string(
                item.get("authority_class"),
                f"{field_name}[{index}].authority_class",
            ),
            "object_types": _coerce_string_list(
                item.get("object_types"),
                f"{field_name}[{index}].object_types",
            ),
            "artifact_types": _coerce_string_list(
                item.get("artifact_types"),
                f"{field_name}[{index}].artifact_types",
            ),
            "identifier_types_emitted": _coerce_string_list(
                item.get("identifier_types_emitted"),
                f"{field_name}[{index}].identifier_types_emitted",
            ),
            "connector": _coerce_connector(
                item.get("connector"),
                f"{field_name}[{index}].connector",
            ),
            "capabilities": _coerce_bool_mapping(
                item.get("capabilities"),
                f"{field_name}[{index}].capabilities",
            ),
            "capabilities_summary": _coerce_string_list(
                item.get("capabilities_summary"),
                f"{field_name}[{index}].capabilities_summary",
            ),
            "coverage": _coerce_coverage(
                item.get("coverage"),
                f"{field_name}[{index}].coverage",
            ),
            "coverage_depth": _require_string(
                item.get("coverage_depth"),
                f"{field_name}[{index}].coverage_depth",
            ),
            "coverage_status": _require_string(
                item.get("coverage_status"),
                f"{field_name}[{index}].coverage_status",
            ),
            "connector_mode": _require_string(
                item.get("connector_mode"),
                f"{field_name}[{index}].connector_mode",
            ),
            "indexed_scopes": _coerce_string_list(
                item.get("indexed_scopes"),
                f"{field_name}[{index}].indexed_scopes",
            ),
            "current_limitations": _coerce_string_list(
                item.get("current_limitations"),
                f"{field_name}[{index}].current_limitations",
            ),
            "next_coverage_step": _require_string(
                item.get("next_coverage_step"),
                f"{field_name}[{index}].next_coverage_step",
            ),
            "placeholder_warning": _optional_text(
                item.get("placeholder_warning"),
                f"{field_name}[{index}].placeholder_warning",
            ),
            "live_access_mode": _require_string(
                item.get("live_access_mode"),
                f"{field_name}[{index}].live_access_mode",
            ),
            "extraction_mode": _require_string(
                item.get("extraction_mode"),
                f"{field_name}[{index}].extraction_mode",
            ),
            "legal_posture": _require_string(
                item.get("legal_posture"),
                f"{field_name}[{index}].legal_posture",
            ),
            "freshness_model": _require_string(
                item.get("freshness_model"),
                f"{field_name}[{index}].freshness_model",
            ),
            "rights_notes": _require_string(
                item.get("rights_notes"),
                f"{field_name}[{index}].rights_notes",
            ),
            "notes": _require_string(item.get("notes"), f"{field_name}[{index}].notes"),
        }
        sources.append(source)
    return sources


def _coerce_applied_filters(value: Any) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise ValueError("envelope.applied_filters must be an object.")
    filters: dict[str, str] = {}
    for key, raw_value in value.items():
        if not isinstance(key, str) or not key:
            raise ValueError("envelope.applied_filters keys must be non-empty strings.")
        if not isinstance(raw_value, str) or not raw_value:
            raise ValueError("envelope.applied_filters values must be non-empty strings.")
        filters[key] = raw_value
    return filters


def _coerce_notices(value: Any, field_name: str) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    notices: list[dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        notice = {
            "code": _require_string(item.get("code"), f"{field_name}[{index}].code"),
            "severity": _require_string(item.get("severity"), f"{field_name}[{index}].severity"),
        }
        message = _optional_string(item.get("message"), f"{field_name}[{index}].message")
        if message is not None:
            notice["message"] = message
        notices.append(notice)
    return notices


def _coerce_connector(value: Any, field_name: str) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    return {
        "label": _require_string(value.get("label"), f"{field_name}.label"),
        "status": _require_string(value.get("status"), f"{field_name}.status"),
    }


def _coerce_bool_mapping(value: Any, field_name: str) -> dict[str, bool]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    values: dict[str, bool] = {}
    for key, raw_value in value.items():
        if not isinstance(key, str) or not key:
            raise ValueError(f"{field_name} keys must be non-empty strings.")
        if not isinstance(raw_value, bool):
            raise ValueError(f"{field_name}.{key} must be a boolean.")
        values[key] = raw_value
    return values


def _coerce_coverage(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    return {
        "coverage_depth": _require_string(
            value.get("coverage_depth"),
            f"{field_name}.coverage_depth",
        ),
        "coverage_status": _require_string(
            value.get("coverage_status"),
            f"{field_name}.coverage_status",
        ),
        "indexed_scopes": _coerce_string_list(
            value.get("indexed_scopes"),
            f"{field_name}.indexed_scopes",
        ),
        "connector_mode": _require_string(
            value.get("connector_mode"),
            f"{field_name}.connector_mode",
        ),
        "last_fixture_update": _require_string(
            value.get("last_fixture_update"),
            f"{field_name}.last_fixture_update",
        ),
        "coverage_notes": _require_string(
            value.get("coverage_notes"),
            f"{field_name}.coverage_notes",
        ),
        "current_limitations": _coerce_string_list(
            value.get("current_limitations"),
            f"{field_name}.current_limitations",
        ),
        "next_coverage_step": _require_string(
            value.get("next_coverage_step"),
            f"{field_name}.next_coverage_step",
        ),
    }


def _coerce_string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    values: list[str] = []
    for index, item in enumerate(value):
        values.append(_require_string(item, f"{field_name}[{index}]"))
    return values


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value


def _optional_string(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    return _require_string(value, field_name)


def _optional_text(value: Any, field_name: str) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string.")
    return value


def _require_non_negative_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer.")
    return value

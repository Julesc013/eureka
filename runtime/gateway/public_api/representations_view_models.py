from __future__ import annotations

from typing import Any, Mapping


def representations_envelope_to_view_model(envelope: Mapping[str, Any]) -> dict[str, Any]:
    view_model: dict[str, Any] = {
        "status": _require_string(envelope.get("status"), "representations.status"),
        "target_ref": _require_string(envelope.get("target_ref"), "representations.target_ref"),
        "representations": _coerce_representations(
            envelope.get("representations"),
            "representations.representations",
        ),
        "notices": _coerce_notice_list(envelope.get("notices"), "representations.notices"),
    }
    resolved_resource_id = _optional_string(
        envelope.get("resolved_resource_id"),
        "representations.resolved_resource_id",
    )
    if resolved_resource_id is not None:
        view_model["resolved_resource_id"] = resolved_resource_id
    primary_object = envelope.get("primary_object")
    if primary_object is not None:
        view_model["primary_object"] = _coerce_object_summary(
            primary_object,
            "representations.primary_object",
        )
    source = envelope.get("source")
    if source is not None:
        view_model["source"] = _coerce_source_summary(source, "representations.source")
    return view_model


def _coerce_representations(value: Any, field_name: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    representations: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        representation: dict[str, Any] = {
            "representation_id": _require_string(
                item.get("representation_id"),
                f"{field_name}[{index}].representation_id",
            ),
            "representation_kind": _require_string(
                item.get("representation_kind"),
                f"{field_name}[{index}].representation_kind",
            ),
            "label": _require_string(item.get("label"), f"{field_name}[{index}].label"),
            "source_family": _require_string(
                item.get("source_family"),
                f"{field_name}[{index}].source_family",
            ),
            "access_kind": _require_string(
                item.get("access_kind"),
                f"{field_name}[{index}].access_kind",
            ),
            "is_direct": _require_bool(item.get("is_direct"), f"{field_name}[{index}].is_direct"),
            "is_fetchable": _require_bool(
                item.get("is_fetchable"),
                f"{field_name}[{index}].is_fetchable",
            ),
        }
        for key in (
            "content_type",
            "filename",
            "source_label",
            "source_locator",
            "access_path_id",
            "access_locator",
        ):
            optional = _optional_string(item.get(key), f"{field_name}[{index}].{key}")
            if optional is not None:
                representation[key] = optional
        byte_length = _optional_non_negative_int(
            item.get("byte_length"),
            f"{field_name}[{index}].byte_length",
        )
        if byte_length is not None:
            representation["byte_length"] = byte_length
        representations.append(representation)
    return representations


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


def _coerce_source_summary(value: Any, field_name: str) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    source = {"family": _require_string(value.get("family"), f"{field_name}.family")}
    label = _optional_string(value.get("label"), f"{field_name}.label")
    locator = _optional_string(value.get("locator"), f"{field_name}.locator")
    if label is not None:
        source["label"] = label
    if locator is not None:
        source["locator"] = locator
    return source


def _coerce_notice_list(value: Any, field_name: str) -> list[dict[str, str]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list when provided.")
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


def _require_bool(value: Any, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field_name} must be a boolean.")
    return value


def _optional_non_negative_int(value: Any, field_name: str) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer when provided.")
    return value

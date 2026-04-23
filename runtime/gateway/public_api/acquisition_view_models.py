from __future__ import annotations

from typing import Any, Mapping


def acquisition_envelope_to_view_model(envelope: Mapping[str, Any]) -> dict[str, Any]:
    view_model: dict[str, Any] = {
        "status": _require_string(envelope.get("status"), "acquisition.status"),
        "acquisition_status": _require_string(
            envelope.get("acquisition_status"),
            "acquisition.acquisition_status",
        ),
        "target_ref": _require_string(envelope.get("target_ref"), "acquisition.target_ref"),
        "representation_id": _require_string(
            envelope.get("representation_id"),
            "acquisition.representation_id",
        ),
        "reason_codes": _coerce_string_list(
            envelope.get("reason_codes"),
            "acquisition.reason_codes",
        ),
        "reason_messages": _coerce_string_list(
            envelope.get("reason_messages"),
            "acquisition.reason_messages",
        ),
        "notices": _coerce_notice_list(envelope.get("notices"), "acquisition.notices"),
    }
    for field_name in (
        "resolved_resource_id",
        "representation_kind",
        "label",
        "filename",
        "content_type",
        "source_family",
        "source_label",
        "source_locator",
        "access_kind",
        "access_locator",
    ):
        optional = _optional_string(envelope.get(field_name), f"acquisition.{field_name}")
        if optional is not None:
            view_model[field_name] = optional
    byte_length = envelope.get("byte_length")
    if byte_length is not None:
        view_model["byte_length"] = _require_int(byte_length, "acquisition.byte_length")
    return view_model


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


def _coerce_string_list(value: Any, field_name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    return [_require_string(item, f"{field_name}[{index}]") for index, item in enumerate(value)]


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

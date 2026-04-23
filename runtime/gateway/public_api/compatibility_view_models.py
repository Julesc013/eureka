from __future__ import annotations

from typing import Any, Mapping


def compatibility_envelope_to_view_model(envelope: Mapping[str, Any]) -> dict[str, Any]:
    view_model: dict[str, Any] = {
        "status": _require_string(envelope.get("status"), "compatibility.status"),
        "target_ref": _require_string(envelope.get("target_ref"), "compatibility.target_ref"),
        "host_profile": _coerce_host_profile(
            envelope.get("host_profile"),
            "compatibility.host_profile",
        ),
        "reasons": _coerce_reasons(envelope.get("reasons"), "compatibility.reasons"),
        "next_steps": _coerce_string_list(envelope.get("next_steps"), "compatibility.next_steps"),
        "notices": _coerce_notice_list(envelope.get("notices"), "compatibility.notices"),
    }
    compatibility_status = _optional_string(
        envelope.get("compatibility_status"),
        "compatibility.compatibility_status",
    )
    if compatibility_status is not None:
        view_model["compatibility_status"] = compatibility_status
    resolved_resource_id = _optional_string(
        envelope.get("resolved_resource_id"),
        "compatibility.resolved_resource_id",
    )
    if resolved_resource_id is not None:
        view_model["resolved_resource_id"] = resolved_resource_id
    primary_object = envelope.get("primary_object")
    if primary_object is not None:
        view_model["primary_object"] = _coerce_object_summary(
            primary_object,
            "compatibility.primary_object",
        )
    source = envelope.get("source")
    if source is not None:
        view_model["source"] = _coerce_source_summary(source, "compatibility.source")
    return view_model


def _coerce_host_profile(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    host_profile = {
        "host_profile_id": _require_string(value.get("host_profile_id"), f"{field_name}.host_profile_id"),
        "os_family": _require_string(value.get("os_family"), f"{field_name}.os_family"),
        "architecture": _require_string(value.get("architecture"), f"{field_name}.architecture"),
        "features": _coerce_string_list(value.get("features"), f"{field_name}.features"),
    }
    runtime_family = _optional_string(value.get("runtime_family"), f"{field_name}.runtime_family")
    if runtime_family is not None:
        host_profile["runtime_family"] = runtime_family
    return host_profile


def _coerce_reasons(value: Any, field_name: str) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    reasons: list[dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        reasons.append(
            {
                "code": _require_string(item.get("code"), f"{field_name}[{index}].code"),
                "message": _require_string(item.get("message"), f"{field_name}[{index}].message"),
            }
        )
    return reasons


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


def _coerce_string_list(value: Any, field_name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    strings: list[str] = []
    for index, item in enumerate(value):
        strings.append(_require_string(item, f"{field_name}[{index}]"))
    return strings


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

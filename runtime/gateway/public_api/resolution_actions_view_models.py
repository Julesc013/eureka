from __future__ import annotations

from typing import Any, Mapping


def resolution_actions_envelope_to_view_model(
    actions_envelope: Mapping[str, Any],
) -> dict[str, Any]:
    view_model: dict[str, Any] = {
        "target_ref": _require_string(actions_envelope.get("target_ref"), "actions_envelope.target_ref"),
        "actions": _coerce_actions(actions_envelope.get("actions")),
    }
    resolved_resource_id = _optional_string(
        actions_envelope.get("resolved_resource_id"),
        "actions_envelope.resolved_resource_id",
    )
    if resolved_resource_id is not None:
        view_model["resolved_resource_id"] = resolved_resource_id

    notices = _coerce_notice_list(actions_envelope.get("notices"), "actions_envelope.notices")
    if notices:
        view_model["notices"] = notices

    return view_model


def _coerce_actions(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise ValueError("actions_envelope.actions must be a list.")

    actions: list[dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"actions_envelope.actions[{index}] must be an object.")

        action = {
            "action_id": _require_string(item.get("action_id"), f"actions_envelope.actions[{index}].action_id"),
            "label": _require_string(item.get("label"), f"actions_envelope.actions[{index}].label"),
            "availability": _require_string(
                item.get("availability"),
                f"actions_envelope.actions[{index}].availability",
            ),
        }
        href = _optional_string(item.get("href"), f"actions_envelope.actions[{index}].href")
        if href is not None:
            action["href"] = href
        actions.append(action)
    return actions


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

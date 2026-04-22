from __future__ import annotations

from typing import Any, Mapping


def stored_exports_envelope_to_view_model(
    stored_exports_envelope: Mapping[str, Any],
) -> dict[str, Any]:
    view_model: dict[str, Any] = {
        "target_ref": _require_string(stored_exports_envelope.get("target_ref"), "stored_exports.target_ref"),
        "store_actions": _coerce_store_actions(stored_exports_envelope.get("store_actions")),
        "artifacts": _coerce_artifacts(stored_exports_envelope.get("artifacts")),
    }
    resolved_resource_id = _optional_string(
        stored_exports_envelope.get("resolved_resource_id"),
        "stored_exports.resolved_resource_id",
    )
    if resolved_resource_id is not None:
        view_model["resolved_resource_id"] = resolved_resource_id

    notices = _coerce_notice_list(stored_exports_envelope.get("notices"), "stored_exports.notices")
    if notices:
        view_model["notices"] = notices
    return view_model


def _coerce_store_actions(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise ValueError("stored_exports.store_actions must be a list.")
    actions: list[dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"stored_exports.store_actions[{index}] must be an object.")
        action = {
            "action_id": _require_string(item.get("action_id"), f"stored_exports.store_actions[{index}].action_id"),
            "label": _require_string(item.get("label"), f"stored_exports.store_actions[{index}].label"),
            "availability": _require_string(
                item.get("availability"),
                f"stored_exports.store_actions[{index}].availability",
            ),
        }
        href = _optional_string(item.get("href"), f"stored_exports.store_actions[{index}].href")
        if href is not None:
            action["href"] = href
        actions.append(action)
    return actions


def _coerce_artifacts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError("stored_exports.artifacts must be a list.")
    artifacts: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"stored_exports.artifacts[{index}] must be an object.")
        artifact: dict[str, Any] = {
            "artifact_id": _require_string(item.get("artifact_id"), f"stored_exports.artifacts[{index}].artifact_id"),
            "artifact_kind": _require_string(item.get("artifact_kind"), f"stored_exports.artifacts[{index}].artifact_kind"),
            "content_type": _require_string(item.get("content_type"), f"stored_exports.artifacts[{index}].content_type"),
            "byte_length": _require_int(item.get("byte_length"), f"stored_exports.artifacts[{index}].byte_length"),
            "availability": _require_string(
                item.get("availability"),
                f"stored_exports.artifacts[{index}].availability",
            ),
        }
        resolved_resource_id = _optional_string(
            item.get("resolved_resource_id"),
            f"stored_exports.artifacts[{index}].resolved_resource_id",
        )
        if resolved_resource_id is not None:
            artifact["resolved_resource_id"] = resolved_resource_id
        href = _optional_string(item.get("href"), f"stored_exports.artifacts[{index}].href")
        if href is not None:
            artifact["href"] = href
        filename = _optional_string(item.get("filename"), f"stored_exports.artifacts[{index}].filename")
        if filename is not None:
            artifact["filename"] = filename
        source = _optional_source_summary(item.get("source"), f"stored_exports.artifacts[{index}].source")
        if source is not None:
            artifact["source"] = source
        evidence = _optional_evidence_list(item.get("evidence"), f"stored_exports.artifacts[{index}].evidence")
        if evidence:
            artifact["evidence"] = evidence
        artifacts.append(artifact)
    return artifacts


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
    return _require_string(value, field_name)


def _require_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer.")
    return value


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

from __future__ import annotations

from typing import Any, Mapping


def comparison_envelope_to_view_model(envelope: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "status": _require_string(envelope.get("status"), "comparison.status"),
        "left": _coerce_side(envelope.get("left"), "comparison.left"),
        "right": _coerce_side(envelope.get("right"), "comparison.right"),
        "agreements": _coerce_agreements(envelope.get("agreements"), "comparison.agreements"),
        "disagreements": _coerce_disagreements(
            envelope.get("disagreements"),
            "comparison.disagreements",
        ),
        "notices": _coerce_notice_list(envelope.get("notices"), "comparison.notices"),
    }


def _coerce_side(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    side = {
        "target_ref": _require_string(value.get("target_ref"), f"{field_name}.target_ref"),
        "status": _require_string(value.get("status"), f"{field_name}.status"),
        "notices": _coerce_notice_list(value.get("notices"), f"{field_name}.notices"),
    }
    resolved_resource_id = _optional_string(
        value.get("resolved_resource_id"),
        f"{field_name}.resolved_resource_id",
    )
    if resolved_resource_id is not None:
        side["resolved_resource_id"] = resolved_resource_id
    object_summary = _optional_object_summary(value.get("object"), f"{field_name}.object")
    if object_summary is not None:
        side["object"] = object_summary
    source = _optional_source_summary(value.get("source"), f"{field_name}.source")
    if source is not None:
        side["source"] = source
    version_or_state = _optional_string(value.get("version_or_state"), f"{field_name}.version_or_state")
    if version_or_state is not None:
        side["version_or_state"] = version_or_state
    evidence = _optional_evidence_list(value.get("evidence"), f"{field_name}.evidence")
    if evidence:
        side["evidence"] = evidence
    return side


def _coerce_agreements(value: Any, field_name: str) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    agreements: list[dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        agreements.append(
            {
                "category": _require_string(item.get("category"), f"{field_name}[{index}].category"),
                "value": _require_string(item.get("value"), f"{field_name}[{index}].value"),
            }
        )
    return agreements


def _coerce_disagreements(value: Any, field_name: str) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    disagreements: list[dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        disagreements.append(
            {
                "category": _require_string(item.get("category"), f"{field_name}[{index}].category"),
                "left_value": _require_string(item.get("left_value"), f"{field_name}[{index}].left_value"),
                "right_value": _require_string(item.get("right_value"), f"{field_name}[{index}].right_value"),
            }
        )
    return disagreements


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


def _optional_object_summary(value: Any, field_name: str) -> dict[str, str] | None:
    if value is None:
        return None
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


def _optional_source_summary(value: Any, field_name: str) -> dict[str, str] | None:
    if value is None:
        return None
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


def _optional_evidence_list(value: Any, field_name: str) -> list[dict[str, str]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    evidence: list[dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        entry = {
            "claim_kind": _require_string(item.get("claim_kind"), f"{field_name}[{index}].claim_kind"),
            "claim_value": _require_string(item.get("claim_value"), f"{field_name}[{index}].claim_value"),
            "asserted_by_family": _require_string(
                item.get("asserted_by_family"),
                f"{field_name}[{index}].asserted_by_family",
            ),
            "evidence_kind": _require_string(item.get("evidence_kind"), f"{field_name}[{index}].evidence_kind"),
            "evidence_locator": _require_string(
                item.get("evidence_locator"),
                f"{field_name}[{index}].evidence_locator",
            ),
        }
        asserted_by_label = _optional_string(
            item.get("asserted_by_label"),
            f"{field_name}[{index}].asserted_by_label",
        )
        asserted_at = _optional_string(item.get("asserted_at"), f"{field_name}[{index}].asserted_at")
        if asserted_by_label is not None:
            entry["asserted_by_label"] = asserted_by_label
        if asserted_at is not None:
            entry["asserted_at"] = asserted_at
        evidence.append(entry)
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

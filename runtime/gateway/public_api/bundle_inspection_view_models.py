from __future__ import annotations

from typing import Any, Mapping


def bundle_inspection_envelope_to_view_model(
    inspection_envelope: Mapping[str, Any],
) -> dict[str, Any]:
    view_model: dict[str, Any] = {
        "status": _require_string(inspection_envelope.get("status"), "inspection_envelope.status"),
        "inspection_mode": _require_string(
            inspection_envelope.get("inspection_mode"),
            "inspection_envelope.inspection_mode",
        ),
        "source": _coerce_source(inspection_envelope.get("source")),
        "notices": _coerce_notices(inspection_envelope.get("notices")),
    }
    resolved_resource_id = _optional_string(
        inspection_envelope.get("resolved_resource_id"),
        "inspection_envelope.resolved_resource_id",
    )
    if resolved_resource_id is not None:
        view_model["resolved_resource_id"] = resolved_resource_id
    evidence = _coerce_evidence_list(inspection_envelope.get("evidence"), "inspection_envelope.evidence")
    if evidence:
        view_model["evidence"] = evidence

    bundle_summary = inspection_envelope.get("bundle")
    if bundle_summary is not None:
        view_model["bundle"] = _coerce_bundle_summary(bundle_summary)

    primary_object = inspection_envelope.get("primary_object")
    if primary_object is not None:
        view_model["primary_object"] = _coerce_object_summary(primary_object, "inspection_envelope.primary_object")

    normalized_record = inspection_envelope.get("normalized_record")
    if normalized_record is not None:
        view_model["normalized_record"] = _coerce_normalized_record(normalized_record)

    return view_model


def _coerce_source(value: Any) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise ValueError("inspection_envelope.source must be an object.")
    return {
        "kind": _require_string(value.get("kind"), "inspection_envelope.source.kind"),
        "locator": _require_string(value.get("locator"), "inspection_envelope.source.locator"),
    }


def _coerce_bundle_summary(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("inspection_envelope.bundle must be an object.")
    summary: dict[str, Any] = {
        "member_list": _coerce_member_list(value.get("member_list")),
    }
    bundle_kind = _optional_string(value.get("bundle_kind"), "inspection_envelope.bundle.bundle_kind")
    bundle_version = _optional_string(value.get("bundle_version"), "inspection_envelope.bundle.bundle_version")
    target_ref = _optional_string(value.get("target_ref"), "inspection_envelope.bundle.target_ref")
    if bundle_kind is not None:
        summary["bundle_kind"] = bundle_kind
    if bundle_version is not None:
        summary["bundle_version"] = bundle_version
    if target_ref is not None:
        summary["target_ref"] = target_ref
    return summary


def _coerce_object_summary(value: Any, field_name: str) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    summary = {
        "id": _require_string(value.get("id"), f"{field_name}.id"),
    }
    kind = _optional_string(value.get("kind"), f"{field_name}.kind")
    label = _optional_string(value.get("label"), f"{field_name}.label")
    if kind is not None:
        summary["kind"] = kind
    if label is not None:
        summary["label"] = label
    return summary


def _coerce_normalized_record(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("inspection_envelope.normalized_record must be an object.")
    result: dict[str, Any] = {
        "record_kind": _require_string(
            value.get("record_kind"),
            "inspection_envelope.normalized_record.record_kind",
        ),
        "target_ref": _require_string(
            value.get("target_ref"),
            "inspection_envelope.normalized_record.target_ref",
        ),
    }
    resolved_resource_id = _optional_string(
        value.get("resolved_resource_id"),
        "inspection_envelope.normalized_record.resolved_resource_id",
    )
    if resolved_resource_id is not None:
        result["resolved_resource_id"] = resolved_resource_id
    for field_name in ("source", "object", "state", "representation"):
        field_value = value.get(field_name)
        if field_value is not None:
            if not isinstance(field_value, Mapping):
                raise ValueError(f"inspection_envelope.normalized_record.{field_name} must be an object when provided.")
            result[field_name] = dict(field_value)
    evidence = _coerce_evidence_list(value.get("evidence"), "inspection_envelope.normalized_record.evidence")
    if evidence:
        result["evidence"] = evidence
    expected_member_order = value.get("expected_member_order")
    if expected_member_order is not None:
        result["expected_member_order"] = _coerce_member_list(expected_member_order)
    return result


def _coerce_member_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        raise ValueError("inspection member_list must be a list.")
    members: list[str] = []
    for index, item in enumerate(value):
        members.append(_require_string(item, f"inspection member_list[{index}]"))
    return members


def _coerce_notices(value: Any) -> list[dict[str, str]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("inspection_envelope.notices must be a list when provided.")
    notices: list[dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"inspection_envelope.notices[{index}] must be an object.")
        notice = {
            "code": _require_string(item.get("code"), f"inspection_envelope.notices[{index}].code"),
            "severity": _require_string(
                item.get("severity"),
                f"inspection_envelope.notices[{index}].severity",
            ),
        }
        message = _optional_string(item.get("message"), f"inspection_envelope.notices[{index}].message")
        if message is not None:
            notice["message"] = message
        notices.append(notice)
    return notices


def _coerce_evidence_list(value: Any, field_name: str) -> list[dict[str, str]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list when provided.")
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

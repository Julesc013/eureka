from __future__ import annotations

from typing import Any, Mapping


def absence_envelope_to_view_model(envelope: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "request_kind": _require_string(envelope.get("request_kind"), "absence.request_kind"),
        "requested_value": _require_string(envelope.get("requested_value"), "absence.requested_value"),
        "status": _require_string(envelope.get("status"), "absence.status"),
        "checked_source_families": _coerce_string_list(
            envelope.get("checked_source_families"),
            "absence.checked_source_families",
        ),
        "checked_record_count": _require_int(
            envelope.get("checked_record_count"),
            "absence.checked_record_count",
        ),
        "checked_subject_count": _require_int(
            envelope.get("checked_subject_count"),
            "absence.checked_subject_count",
        ),
        "likely_reason_code": _require_string(
            envelope.get("likely_reason_code"),
            "absence.likely_reason_code",
        ),
        "reason_message": _require_string(envelope.get("reason_message"), "absence.reason_message"),
        "near_matches": _coerce_near_matches(envelope.get("near_matches"), "absence.near_matches"),
        "next_steps": _coerce_string_list(envelope.get("next_steps"), "absence.next_steps"),
        "notices": _coerce_notice_list(envelope.get("notices"), "absence.notices"),
    }


def _coerce_near_matches(value: Any, field_name: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    near_matches: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        match = {
            "match_kind": _require_string(item.get("match_kind"), f"{field_name}[{index}].match_kind"),
            "target_ref": _require_string(item.get("target_ref"), f"{field_name}[{index}].target_ref"),
            "resolved_resource_id": _require_string(
                item.get("resolved_resource_id"),
                f"{field_name}[{index}].resolved_resource_id",
            ),
            "object": _coerce_object_summary(item.get("object"), f"{field_name}[{index}].object"),
        }
        source = _optional_source_summary(item.get("source"), f"{field_name}[{index}].source")
        if source is not None:
            match["source"] = source
        subject_key = _optional_string(item.get("subject_key"), f"{field_name}[{index}].subject_key")
        if subject_key is not None:
            match["subject_key"] = subject_key
        version_or_state = _optional_string(
            item.get("version_or_state"),
            f"{field_name}[{index}].version_or_state",
        )
        if version_or_state is not None:
            match["version_or_state"] = version_or_state
        normalized_version_or_state = _optional_string(
            item.get("normalized_version_or_state"),
            f"{field_name}[{index}].normalized_version_or_state",
        )
        if normalized_version_or_state is not None:
            match["normalized_version_or_state"] = normalized_version_or_state
        evidence = _optional_evidence_list(item.get("evidence"), f"{field_name}[{index}].evidence")
        if evidence:
            match["evidence"] = evidence
        near_matches.append(match)
    return near_matches


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


def _require_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer.")
    return value

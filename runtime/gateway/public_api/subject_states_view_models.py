from __future__ import annotations

from typing import Any, Mapping


def subject_states_envelope_to_view_model(envelope: Mapping[str, Any]) -> dict[str, Any]:
    view_model: dict[str, Any] = {
        "status": _require_string(envelope.get("status"), "subject_states.status"),
        "requested_subject_key": _require_string(
            envelope.get("requested_subject_key"),
            "subject_states.requested_subject_key",
        ),
        "states": _coerce_states(envelope.get("states"), "subject_states.states"),
        "notices": _coerce_notice_list(envelope.get("notices"), "subject_states.notices"),
    }
    subject = envelope.get("subject")
    if subject is not None:
        view_model["subject"] = _coerce_subject(subject, "subject_states.subject")
    return view_model


def _coerce_subject(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    subject = {
        "subject_key": _require_string(value.get("subject_key"), f"{field_name}.subject_key"),
        "subject_label": _require_string(value.get("subject_label"), f"{field_name}.subject_label"),
        "state_count": _require_int(value.get("state_count"), f"{field_name}.state_count"),
    }
    source_family_hint = _optional_string(
        value.get("source_family_hint"),
        f"{field_name}.source_family_hint",
    )
    if source_family_hint is not None:
        subject["source_family_hint"] = source_family_hint
    return subject


def _coerce_states(value: Any, field_name: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    states: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        state = {
            "target_ref": _require_string(item.get("target_ref"), f"{field_name}[{index}].target_ref"),
            "resolved_resource_id": _require_string(
                item.get("resolved_resource_id"),
                f"{field_name}[{index}].resolved_resource_id",
            ),
            "object": _coerce_object_summary(item.get("object"), f"{field_name}[{index}].object"),
        }
        version_or_state = _optional_string(
            item.get("version_or_state"),
            f"{field_name}[{index}].version_or_state",
        )
        normalized_version_or_state = _optional_string(
            item.get("normalized_version_or_state"),
            f"{field_name}[{index}].normalized_version_or_state",
        )
        source = _optional_source_summary(item.get("source"), f"{field_name}[{index}].source")
        evidence = _optional_evidence_list(item.get("evidence"), f"{field_name}[{index}].evidence")
        if version_or_state is not None:
            state["version_or_state"] = version_or_state
        if normalized_version_or_state is not None:
            state["normalized_version_or_state"] = normalized_version_or_state
        if source is not None:
            state["source"] = source
        if evidence:
            state["evidence"] = evidence
        states.append(state)
    return states


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

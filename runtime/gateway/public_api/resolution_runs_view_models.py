from __future__ import annotations

from typing import Any, Mapping


def resolution_runs_envelope_to_view_model(envelope: Mapping[str, Any]) -> dict[str, Any]:
    view_model: dict[str, Any] = {
        "status": _require_string(envelope.get("status"), "envelope.status"),
        "run_count": _require_non_negative_int(envelope.get("run_count"), "envelope.run_count"),
        "runs": _coerce_runs(envelope.get("runs"), "envelope.runs"),
    }
    selected_run_id = _optional_string(envelope.get("selected_run_id"), "envelope.selected_run_id")
    if selected_run_id is not None:
        view_model["selected_run_id"] = selected_run_id
    notices = envelope.get("notices")
    if notices is not None:
        view_model["notices"] = _coerce_notices(notices, "envelope.notices")
    return view_model


def _coerce_runs(value: Any, field_name: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    runs: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        run: dict[str, Any] = {
            "run_id": _require_string(item.get("run_id"), f"{field_name}[{index}].run_id"),
            "run_kind": _require_string(item.get("run_kind"), f"{field_name}[{index}].run_kind"),
            "requested_value": _require_string(
                item.get("requested_value"),
                f"{field_name}[{index}].requested_value",
            ),
            "status": _require_string(item.get("status"), f"{field_name}[{index}].status"),
            "started_at": _require_string(item.get("started_at"), f"{field_name}[{index}].started_at"),
            "completed_at": _require_string(
                item.get("completed_at"),
                f"{field_name}[{index}].completed_at",
            ),
            "checked_source_ids": _coerce_string_list(
                item.get("checked_source_ids"),
                f"{field_name}[{index}].checked_source_ids",
            ),
            "checked_source_families": _coerce_string_list(
                item.get("checked_source_families"),
                f"{field_name}[{index}].checked_source_families",
            ),
            "checked_sources": _coerce_checked_sources(
                item.get("checked_sources"),
                f"{field_name}[{index}].checked_sources",
            ),
            "notices": _coerce_notices(item.get("notices"), f"{field_name}[{index}].notices"),
            "created_by_slice": _require_string(
                item.get("created_by_slice"),
                f"{field_name}[{index}].created_by_slice",
            ),
        }
        resolution_task = item.get("resolution_task")
        if resolution_task is not None:
            run["resolution_task"] = _coerce_resolution_task(
                resolution_task,
                f"{field_name}[{index}].resolution_task",
            )
        result_summary = item.get("result_summary")
        if result_summary is not None:
            run["result_summary"] = _coerce_result_summary(
                result_summary,
                f"{field_name}[{index}].result_summary",
            )
        absence_report = item.get("absence_report")
        if absence_report is not None:
            run["absence_report"] = _coerce_absence_report(
                absence_report,
                f"{field_name}[{index}].absence_report",
            )
        runs.append(run)
    return runs


def _coerce_checked_sources(value: Any, field_name: str) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    sources: list[dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        sources.append(
            {
                "source_id": _require_string(item.get("source_id"), f"{field_name}[{index}].source_id"),
                "name": _require_string(item.get("name"), f"{field_name}[{index}].name"),
                "source_family": _require_string(
                    item.get("source_family"),
                    f"{field_name}[{index}].source_family",
                ),
                "status": _require_string(item.get("status"), f"{field_name}[{index}].status"),
                "trust_lane": _require_string(
                    item.get("trust_lane"),
                    f"{field_name}[{index}].trust_lane",
                ),
            }
        )
    return sources


def _coerce_resolution_task(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    return {
        "raw_query": _require_string(value.get("raw_query"), f"{field_name}.raw_query"),
        "task_kind": _require_string(value.get("task_kind"), f"{field_name}.task_kind"),
        "object_type": _require_string(value.get("object_type"), f"{field_name}.object_type"),
        "constraints": _coerce_json_object(value.get("constraints"), f"{field_name}.constraints"),
        "prefer": _coerce_string_list(value.get("prefer"), f"{field_name}.prefer"),
        "exclude": _coerce_string_list(value.get("exclude"), f"{field_name}.exclude"),
        "action_hints": _coerce_string_list(value.get("action_hints"), f"{field_name}.action_hints"),
        "source_hints": _coerce_string_list(value.get("source_hints"), f"{field_name}.source_hints"),
        "planner_confidence": _require_string(
            value.get("planner_confidence"),
            f"{field_name}.planner_confidence",
        ),
        "planner_notes": _coerce_string_list(
            value.get("planner_notes"),
            f"{field_name}.planner_notes",
        ),
    }


def _coerce_json_object(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    return _clone_json_like(value, field_name)


def _clone_json_like(value: Any, field_name: str) -> Any:
    if isinstance(value, Mapping):
        payload: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key:
                raise ValueError(f"{field_name} keys must be non-empty strings.")
            payload[key] = _clone_json_like(item, f"{field_name}.{key}")
        return payload
    if isinstance(value, list):
        return [_clone_json_like(item, f"{field_name}[]") for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise ValueError(f"{field_name} must contain only JSON-compatible values.")


def _coerce_result_summary(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    items = value.get("items")
    if not isinstance(items, list):
        raise ValueError(f"{field_name}.items must be a list.")
    coerced_items: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}.items[{index}] must be an object.")
        coerced_item: dict[str, Any] = {
            "target_ref": _require_string(item.get("target_ref"), f"{field_name}.items[{index}].target_ref"),
            "object": _coerce_object(item.get("object"), f"{field_name}.items[{index}].object"),
        }
        resolved_resource_id = _optional_string(
            item.get("resolved_resource_id"),
            f"{field_name}.items[{index}].resolved_resource_id",
        )
        if resolved_resource_id is not None:
            coerced_item["resolved_resource_id"] = resolved_resource_id
        source = item.get("source")
        if source is not None:
            coerced_item["source"] = _coerce_source(source, f"{field_name}.items[{index}].source")
        evidence = item.get("evidence")
        if evidence is not None:
            coerced_item["evidence"] = _coerce_evidence_list(
                evidence,
                f"{field_name}.items[{index}].evidence",
            )
        coerced_items.append(coerced_item)
    return {
        "result_kind": _require_string(value.get("result_kind"), f"{field_name}.result_kind"),
        "result_count": _require_non_negative_int(
            value.get("result_count"),
            f"{field_name}.result_count",
        ),
        "items": coerced_items,
    }


def _coerce_absence_report(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    near_matches = value.get("near_matches")
    if not isinstance(near_matches, list):
        raise ValueError(f"{field_name}.near_matches must be a list.")
    coerced_near_matches: list[dict[str, Any]] = []
    for index, item in enumerate(near_matches):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}.near_matches[{index}] must be an object.")
        near_match: dict[str, Any] = {
            "match_kind": _require_string(
                item.get("match_kind"),
                f"{field_name}.near_matches[{index}].match_kind",
            ),
            "target_ref": _require_string(
                item.get("target_ref"),
                f"{field_name}.near_matches[{index}].target_ref",
            ),
            "resolved_resource_id": _require_string(
                item.get("resolved_resource_id"),
                f"{field_name}.near_matches[{index}].resolved_resource_id",
            ),
            "object": _coerce_object(item.get("object"), f"{field_name}.near_matches[{index}].object"),
        }
        source = item.get("source")
        if source is not None:
            near_match["source"] = _coerce_source(
                source,
                f"{field_name}.near_matches[{index}].source",
            )
        subject_key = _optional_string(
            item.get("subject_key"),
            f"{field_name}.near_matches[{index}].subject_key",
        )
        if subject_key is not None:
            near_match["subject_key"] = subject_key
        version_or_state = _optional_string(
            item.get("version_or_state"),
            f"{field_name}.near_matches[{index}].version_or_state",
        )
        if version_or_state is not None:
            near_match["version_or_state"] = version_or_state
        normalized_version_or_state = _optional_string(
            item.get("normalized_version_or_state"),
            f"{field_name}.near_matches[{index}].normalized_version_or_state",
        )
        if normalized_version_or_state is not None:
            near_match["normalized_version_or_state"] = normalized_version_or_state
        evidence = item.get("evidence")
        if evidence is not None:
            near_match["evidence"] = _coerce_evidence_list(
                evidence,
                f"{field_name}.near_matches[{index}].evidence",
            )
        coerced_near_matches.append(near_match)
    return {
        "request_kind": _require_string(value.get("request_kind"), f"{field_name}.request_kind"),
        "requested_value": _require_string(
            value.get("requested_value"),
            f"{field_name}.requested_value",
        ),
        "status": _require_string(value.get("status"), f"{field_name}.status"),
        "checked_source_families": _coerce_string_list(
            value.get("checked_source_families"),
            f"{field_name}.checked_source_families",
        ),
        "checked_record_count": _require_non_negative_int(
            value.get("checked_record_count"),
            f"{field_name}.checked_record_count",
        ),
        "checked_subject_count": _require_non_negative_int(
            value.get("checked_subject_count"),
            f"{field_name}.checked_subject_count",
        ),
        "likely_reason_code": _require_string(
            value.get("likely_reason_code"),
            f"{field_name}.likely_reason_code",
        ),
        "reason_message": _require_string(
            value.get("reason_message"),
            f"{field_name}.reason_message",
        ),
        "near_matches": coerced_near_matches,
        "next_steps": _coerce_string_list(value.get("next_steps"), f"{field_name}.next_steps"),
        "notices": _coerce_notices(value.get("notices"), f"{field_name}.notices"),
    }


def _coerce_object(value: Any, field_name: str) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    object_view = {"id": _require_string(value.get("id"), f"{field_name}.id")}
    kind = _optional_string(value.get("kind"), f"{field_name}.kind")
    if kind is not None:
        object_view["kind"] = kind
    label = _optional_string(value.get("label"), f"{field_name}.label")
    if label is not None:
        object_view["label"] = label
    return object_view


def _coerce_source(value: Any, field_name: str) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    source_view = {"family": _require_string(value.get("family"), f"{field_name}.family")}
    source_id = _optional_string(value.get("source_id"), f"{field_name}.source_id")
    if source_id is not None:
        source_view["source_id"] = source_id
    label = _optional_string(value.get("label"), f"{field_name}.label")
    if label is not None:
        source_view["label"] = label
    locator = _optional_string(value.get("locator"), f"{field_name}.locator")
    if locator is not None:
        source_view["locator"] = locator
    return source_view


def _coerce_evidence_list(value: Any, field_name: str) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    evidence: list[dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        evidence.append(
            {
                "claim_kind": _require_string(item.get("claim_kind"), f"{field_name}[{index}].claim_kind"),
                "claim_value": _require_string(
                    item.get("claim_value"),
                    f"{field_name}[{index}].claim_value",
                ),
                "asserted_by_family": _require_string(
                    item.get("asserted_by_family"),
                    f"{field_name}[{index}].asserted_by_family",
                ),
                "evidence_kind": _require_string(
                    item.get("evidence_kind"),
                    f"{field_name}[{index}].evidence_kind",
                ),
                "evidence_locator": _require_string(
                    item.get("evidence_locator"),
                    f"{field_name}[{index}].evidence_locator",
                ),
            }
        )
        asserted_by_label = _optional_string(
            item.get("asserted_by_label"),
            f"{field_name}[{index}].asserted_by_label",
        )
        if asserted_by_label is not None:
            evidence[-1]["asserted_by_label"] = asserted_by_label
        asserted_at = _optional_string(item.get("asserted_at"), f"{field_name}[{index}].asserted_at")
        if asserted_at is not None:
            evidence[-1]["asserted_at"] = asserted_at
    return evidence


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


def _require_non_negative_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer.")
    return value

from __future__ import annotations

from typing import Any, Mapping


def resolution_memory_envelope_to_view_model(envelope: Mapping[str, Any]) -> dict[str, Any]:
    view_model: dict[str, Any] = {
        "status": _require_string(envelope.get("status"), "envelope.status"),
        "memory_count": _require_non_negative_int(
            envelope.get("memory_count"),
            "envelope.memory_count",
        ),
        "memories": _coerce_memories(envelope.get("memories"), "envelope.memories"),
    }
    selected_memory_id = envelope.get("selected_memory_id")
    if selected_memory_id is not None:
        view_model["selected_memory_id"] = _require_string(
            selected_memory_id,
            "envelope.selected_memory_id",
        )
    requested_run_id = envelope.get("requested_run_id")
    if requested_run_id is not None:
        view_model["requested_run_id"] = _require_string(
            requested_run_id,
            "envelope.requested_run_id",
        )
    notices = envelope.get("notices")
    if notices is not None:
        view_model["notices"] = _coerce_notices(notices, "envelope.notices")
    return view_model


def _coerce_memories(value: Any, field_name: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    memories: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        memory: dict[str, Any] = {
            "memory_id": _require_string(item.get("memory_id"), f"{field_name}[{index}].memory_id"),
            "memory_kind": _require_string(item.get("memory_kind"), f"{field_name}[{index}].memory_kind"),
            "source_run_id": _require_string(
                item.get("source_run_id"),
                f"{field_name}[{index}].source_run_id",
            ),
            "created_at": _require_string(item.get("created_at"), f"{field_name}[{index}].created_at"),
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
            "result_summaries": _coerce_result_summaries(
                item.get("result_summaries"),
                f"{field_name}[{index}].result_summaries",
            ),
            "useful_source_ids": _coerce_string_list(
                item.get("useful_source_ids"),
                f"{field_name}[{index}].useful_source_ids",
            ),
            "evidence_summary": _coerce_evidence_summary(
                item.get("evidence_summary"),
                f"{field_name}[{index}].evidence_summary",
            ),
            "notices": _coerce_notices(item.get("notices"), f"{field_name}[{index}].notices"),
            "created_by_slice": _require_string(
                item.get("created_by_slice"),
                f"{field_name}[{index}].created_by_slice",
            ),
        }
        for optional_name in ("raw_query", "task_kind", "requested_value", "primary_resolved_resource_id"):
            optional_value = item.get(optional_name)
            if optional_value is not None:
                memory[optional_name] = _require_string(
                    optional_value,
                    f"{field_name}[{index}].{optional_name}",
                )
        resolution_task = item.get("resolution_task")
        if resolution_task is not None:
            memory["resolution_task"] = _coerce_json_object(
                resolution_task,
                f"{field_name}[{index}].resolution_task",
            )
        absence_report = item.get("absence_report")
        if absence_report is not None:
            memory["absence_report"] = _coerce_json_object(
                absence_report,
                f"{field_name}[{index}].absence_report",
            )
        invalidation_hints = item.get("invalidation_hints")
        if invalidation_hints is not None:
            memory["invalidation_hints"] = _coerce_json_object(
                invalidation_hints,
                f"{field_name}[{index}].invalidation_hints",
            )
        memories.append(memory)
    return memories


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


def _coerce_result_summaries(value: Any, field_name: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    summaries: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        summary: dict[str, Any] = {
            "target_ref": _require_string(item.get("target_ref"), f"{field_name}[{index}].target_ref"),
            "object": _coerce_json_object(item.get("object"), f"{field_name}[{index}].object"),
        }
        resolved_resource_id = item.get("resolved_resource_id")
        if resolved_resource_id is not None:
            summary["resolved_resource_id"] = _require_string(
                resolved_resource_id,
                f"{field_name}[{index}].resolved_resource_id",
            )
        source = item.get("source")
        if source is not None:
            summary["source"] = _coerce_json_object(source, f"{field_name}[{index}].source")
        summaries.append(summary)
    return summaries


def _coerce_evidence_summary(value: Any, field_name: str) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    summaries: list[dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        summary = {
            "claim_kind": _require_string(item.get("claim_kind"), f"{field_name}[{index}].claim_kind"),
            "claim_value": _require_string(item.get("claim_value"), f"{field_name}[{index}].claim_value"),
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
        asserted_by_label = item.get("asserted_by_label")
        if asserted_by_label is not None:
            summary["asserted_by_label"] = _require_string(
                asserted_by_label,
                f"{field_name}[{index}].asserted_by_label",
            )
        asserted_at = item.get("asserted_at")
        if asserted_at is not None:
            summary["asserted_at"] = _require_string(
                asserted_at,
                f"{field_name}[{index}].asserted_at",
            )
        summaries.append(summary)
    return summaries


def _coerce_notices(value: Any, field_name: str) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    notices: list[dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        notice: dict[str, str] = {
            "code": _require_string(item.get("code"), f"{field_name}[{index}].code"),
            "severity": _require_string(item.get("severity"), f"{field_name}[{index}].severity"),
        }
        message = item.get("message")
        if message is not None:
            notice["message"] = _require_string(message, f"{field_name}[{index}].message")
        notices.append(notice)
    return notices


def _coerce_string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    entries: list[str] = []
    for index, item in enumerate(value):
        entries.append(_require_string(item, f"{field_name}[{index}]"))
    return entries


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


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value


def _require_non_negative_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer.")
    return value

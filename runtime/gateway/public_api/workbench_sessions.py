from __future__ import annotations

from typing import Any, Mapping


def resolution_job_envelope_to_workbench_session(
    job_envelope: Mapping[str, Any],
    *,
    session_id: str,
) -> dict[str, Any]:
    workbench_session: dict[str, Any] = {
        "session_id": _require_string(session_id, "session_id"),
        "active_job": {
            "job_id": _require_string(job_envelope.get("job_id"), "job_envelope.job_id"),
            "status": _require_string(job_envelope.get("status"), "job_envelope.status"),
            "target_ref": _require_string(job_envelope.get("target_ref"), "job_envelope.target_ref"),
        },
    }
    resolved_resource_id = _optional_string(
        job_envelope.get("resolved_resource_id"),
        "job_envelope.resolved_resource_id",
    )
    if resolved_resource_id is not None:
        workbench_session["resolved_resource_id"] = resolved_resource_id

    selected_object = _extract_primary_object(job_envelope)
    if selected_object is not None:
        workbench_session["selected_object"] = selected_object

    source = _extract_source_summary(job_envelope)
    if source is not None:
        workbench_session["source"] = source
    representations = _extract_representation_list(job_envelope)
    if representations:
        workbench_session["representations"] = representations
    evidence = _extract_evidence_list(job_envelope)
    if evidence:
        workbench_session["evidence"] = evidence

    notices = _collect_notices(job_envelope)
    if notices:
        workbench_session["notices"] = notices

    return workbench_session


def _extract_primary_object(job_envelope: Mapping[str, Any]) -> dict[str, Any] | None:
    result = job_envelope.get("result")
    if not isinstance(result, Mapping):
        return None

    primary_object = result.get("primary_object")
    if not isinstance(primary_object, Mapping):
        return None

    summary: dict[str, Any] = {"id": _require_string(primary_object.get("id"), "result.primary_object.id")}
    kind = _optional_string(primary_object.get("kind"), "result.primary_object.kind")
    label = _optional_string(primary_object.get("label"), "result.primary_object.label")
    if kind is not None:
        summary["kind"] = kind
    if label is not None:
        summary["label"] = label
    for optional_name in (
        "record_kind",
        "parent_target_ref",
        "parent_resolved_resource_id",
        "parent_representation_id",
        "parent_object_label",
        "member_path",
        "member_label",
        "member_kind",
        "media_type",
        "content_hash",
    ):
        optional_value = _optional_string(primary_object.get(optional_name), f"result.primary_object.{optional_name}")
        if optional_value is not None:
            summary[optional_name] = optional_value
    size_bytes = _optional_non_negative_int(primary_object.get("size_bytes"), "result.primary_object.size_bytes")
    if size_bytes is not None:
        summary["size_bytes"] = size_bytes
    action_hints = primary_object.get("action_hints")
    if action_hints is not None:
        summary["action_hints"] = _coerce_string_list(action_hints, "result.primary_object.action_hints")
    compatibility_evidence = primary_object.get("compatibility_evidence")
    if compatibility_evidence is not None:
        summary["compatibility_evidence"] = _coerce_json_list(
            compatibility_evidence,
            "result.primary_object.compatibility_evidence",
        )
    compatibility_summary = _optional_string(
        primary_object.get("compatibility_summary"),
        "result.primary_object.compatibility_summary",
    )
    if compatibility_summary is not None:
        summary["compatibility_summary"] = compatibility_summary
    _copy_usefulness_fields(primary_object, summary, "result.primary_object")
    return summary


def _copy_usefulness_fields(value: Mapping[str, Any], summary: dict[str, Any], field_name: str) -> None:
    result_lanes = value.get("result_lanes")
    if result_lanes is not None:
        summary["result_lanes"] = _coerce_string_list(result_lanes, f"{field_name}.result_lanes")
    primary_lane = _optional_string(value.get("primary_lane"), f"{field_name}.primary_lane")
    if primary_lane is not None:
        summary["primary_lane"] = primary_lane
    user_cost_score = _optional_non_negative_int(value.get("user_cost_score"), f"{field_name}.user_cost_score")
    if user_cost_score is not None:
        summary["user_cost_score"] = user_cost_score
    user_cost_reasons = value.get("user_cost_reasons")
    if user_cost_reasons is not None:
        summary["user_cost_reasons"] = _coerce_string_list(
            user_cost_reasons,
            f"{field_name}.user_cost_reasons",
        )
    usefulness_summary = _optional_string(value.get("usefulness_summary"), f"{field_name}.usefulness_summary")
    if usefulness_summary is not None:
        summary["usefulness_summary"] = usefulness_summary


def _collect_notices(job_envelope: Mapping[str, Any]) -> list[dict[str, str]]:
    notices: list[dict[str, str]] = []
    notices.extend(_coerce_notice_list(job_envelope.get("notices"), "job_envelope.notices"))

    result = job_envelope.get("result")
    if isinstance(result, Mapping):
        notices.extend(_coerce_notice_list(result.get("notices"), "result.notices"))

    return notices


def _extract_source_summary(job_envelope: Mapping[str, Any]) -> dict[str, str] | None:
    result = job_envelope.get("result")
    if not isinstance(result, Mapping):
        return None
    source = result.get("source")
    if not isinstance(source, Mapping):
        return None

    summary = {"family": _require_string(source.get("family"), "result.source.family")}
    source_id = _optional_string(source.get("source_id"), "result.source.source_id")
    label = _optional_string(source.get("label"), "result.source.label")
    locator = _optional_string(source.get("locator"), "result.source.locator")
    if source_id is not None:
        summary["source_id"] = source_id
    if label is not None:
        summary["label"] = label
    if locator is not None:
        summary["locator"] = locator
    return summary


def _extract_evidence_list(job_envelope: Mapping[str, Any]) -> list[dict[str, str]]:
    result = job_envelope.get("result")
    if not isinstance(result, Mapping):
        return []
    return _coerce_evidence_list(result.get("evidence"), "result.evidence")


def _extract_representation_list(job_envelope: Mapping[str, Any]) -> list[dict[str, Any]]:
    result = job_envelope.get("result")
    if not isinstance(result, Mapping):
        return []
    return _coerce_representation_list(result.get("representations"), "result.representations")


def _coerce_notice_list(value: Any, field_name: str) -> list[dict[str, str]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list when provided.")

    return [_coerce_notice(item, f"{field_name}[{index}]") for index, item in enumerate(value)]


def _coerce_notice(value: Any, field_name: str) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")

    notice = {
        "code": _require_string(value.get("code"), f"{field_name}.code"),
        "severity": _require_string(value.get("severity"), f"{field_name}.severity"),
    }
    message = _optional_string(value.get("message"), f"{field_name}.message")
    if message is not None:
        notice["message"] = message
    return notice


def _coerce_evidence_list(value: Any, field_name: str) -> list[dict[str, str]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list when provided.")
    return [_coerce_evidence(item, f"{field_name}[{index}]") for index, item in enumerate(value)]


def _coerce_evidence(value: Any, field_name: str) -> dict[str, str]:
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


def _coerce_representation_list(value: Any, field_name: str) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list when provided.")
    return [_coerce_representation(item, f"{field_name}[{index}]") for index, item in enumerate(value)]


def _coerce_representation(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    representation: dict[str, Any] = {
        "representation_id": _require_string(value.get("representation_id"), f"{field_name}.representation_id"),
        "representation_kind": _require_string(
            value.get("representation_kind"),
            f"{field_name}.representation_kind",
        ),
        "label": _require_string(value.get("label"), f"{field_name}.label"),
        "source_family": _require_string(value.get("source_family"), f"{field_name}.source_family"),
        "access_kind": _require_string(value.get("access_kind"), f"{field_name}.access_kind"),
        "is_direct": _require_bool(value.get("is_direct"), f"{field_name}.is_direct"),
        "is_fetchable": _require_bool(value.get("is_fetchable"), f"{field_name}.is_fetchable"),
    }
    for key in (
        "content_type",
        "filename",
        "source_label",
        "source_locator",
        "access_path_id",
        "access_locator",
    ):
        optional = _optional_string(value.get(key), f"{field_name}.{key}")
        if optional is not None:
            representation[key] = optional
    byte_length = _optional_non_negative_int(value.get("byte_length"), f"{field_name}.byte_length")
    if byte_length is not None:
        representation["byte_length"] = byte_length
    return representation


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


def _require_bool(value: Any, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field_name} must be a boolean.")
    return value


def _optional_non_negative_int(value: Any, field_name: str) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer when provided.")
    return value


def _coerce_string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    return [_require_string(item, f"{field_name}[{index}]") for index, item in enumerate(value)]


def _coerce_json_list(value: Any, field_name: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    return [_clone_json_like(item, f"{field_name}[{index}]") for index, item in enumerate(value)]


def _coerce_json_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    payload: dict[str, Any] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key:
            raise ValueError(f"{field_name} keys must be non-empty strings.")
        payload[key] = _clone_json_like(item, f"{field_name}.{key}")
    return payload


def _clone_json_like(value: Any, field_name: str) -> Any:
    if isinstance(value, Mapping):
        return _coerce_json_mapping(value, field_name)
    if isinstance(value, list):
        return [_clone_json_like(item, f"{field_name}[]") for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise ValueError(f"{field_name} must contain only JSON-compatible values.")

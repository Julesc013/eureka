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

    selected_object = _extract_primary_object(job_envelope)
    if selected_object is not None:
        workbench_session["selected_object"] = selected_object

    notices = _collect_notices(job_envelope)
    if notices:
        workbench_session["notices"] = notices

    return workbench_session


def _extract_primary_object(job_envelope: Mapping[str, Any]) -> dict[str, str] | None:
    result = job_envelope.get("result")
    if not isinstance(result, Mapping):
        return None

    primary_object = result.get("primary_object")
    if not isinstance(primary_object, Mapping):
        return None

    summary = {"id": _require_string(primary_object.get("id"), "result.primary_object.id")}
    kind = _optional_string(primary_object.get("kind"), "result.primary_object.kind")
    label = _optional_string(primary_object.get("label"), "result.primary_object.label")
    if kind is not None:
        summary["kind"] = kind
    if label is not None:
        summary["label"] = label
    return summary


def _collect_notices(job_envelope: Mapping[str, Any]) -> list[dict[str, str]]:
    notices: list[dict[str, str]] = []
    notices.extend(_coerce_notice_list(job_envelope.get("notices"), "job_envelope.notices"))

    result = job_envelope.get("result")
    if isinstance(result, Mapping):
        notices.extend(_coerce_notice_list(result.get("notices"), "result.notices"))

    return notices


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

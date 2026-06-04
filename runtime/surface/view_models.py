"""Canonical view-model adapters for SurfaceKernel."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from runtime.engine.interfaces.public import ResolutionRunRecord
from runtime.surface.fallback import canonical_status, missing_summary_note


SURFACE_VIEW_MODEL_VERSION = "surface_view_model.v0"


def adapt_surface_view_model(route_id: str, payload: Any) -> dict[str, Any]:
    route = str(route_id or "unknown")
    if route == "resolution_run":
        return resolution_run_view(payload)
    if route == "workbench_run_review":
        return workbench_run_review_view(_payload_mapping(payload))
    if route == "search":
        return public_search_view(_payload_mapping(payload))
    if route in {"candidate", "need"}:
        return fallback_item_view(route, _payload_mapping(payload))
    return generic_view(route, _payload_mapping(payload))


def resolution_run_view(payload: Any) -> dict[str, Any]:
    run = _record_payload(payload)
    entity_id = _text(run.get("run_id"), "resolution-run")
    fallback = _fallback_summary_view(run.get("fallback_summary"))
    result_summary = run.get("result_summary") if isinstance(run.get("result_summary"), Mapping) else None
    status, notes = canonical_status(_status_from_run(run, fallback))
    return {
        "schema_version": SURFACE_VIEW_MODEL_VERSION,
        "view_model_version": SURFACE_VIEW_MODEL_VERSION,
        "view_family": "resolution_run",
        "route_id": "resolution_run",
        "entity_id": entity_id,
        "canonical_status": status,
        "title": f"Resolution run {entity_id}",
        "summary": _resolution_run_summary(run, result_summary, fallback),
        "actions": _read_actions(),
        "policy_notes": notes + missing_summary_note(result_summary if fallback is None else {"fallback": fallback}),
        "payload": {
            "run": {
                "run_id": entity_id,
                "run_kind": _text(run.get("run_kind"), "unknown"),
                "requested_value": _text(run.get("requested_value"), ""),
                "status": _text(run.get("status"), "unknown"),
                "checked_source_ids": _strings(run.get("checked_source_ids")),
                "checked_source_families": _strings(run.get("checked_source_families")),
            },
            "result_summary": deepcopy(dict(result_summary)) if result_summary is not None else None,
            "absence_report": deepcopy(dict(run.get("absence_report"))) if isinstance(run.get("absence_report"), Mapping) else None,
            "fallback_summary": fallback,
        },
        **_no_mutation_flags(),
    }


def public_search_view(payload: Mapping[str, Any]) -> dict[str, Any]:
    entity_id = _text(payload.get("query", {}).get("normalized") if isinstance(payload.get("query"), Mapping) else payload.get("query"), "search")
    return {
        "schema_version": SURFACE_VIEW_MODEL_VERSION,
        "view_model_version": SURFACE_VIEW_MODEL_VERSION,
        "view_family": "public_search",
        "route_id": "search",
        "entity_id": entity_id,
        "canonical_status": "verified" if payload.get("results") else "unknown",
        "title": "Search",
        "summary": f"{len(payload.get('results') or [])} public search results",
        "actions": _read_actions(),
        "policy_notes": ["public search view is read-only"],
        "payload": deepcopy(dict(payload)),
        **_no_mutation_flags(),
    }


def workbench_run_review_view(payload: Mapping[str, Any]) -> dict[str, Any]:
    run = payload.get("run") if isinstance(payload.get("run"), Mapping) else {}
    entity_id = _text(run.get("run_id"), _text(payload.get("run_id"), "workbench-run-review"))
    actions = payload.get("operator_actions") if isinstance(payload.get("operator_actions"), list) else []
    status, notes = canonical_status(
        _text(payload.get("fallback_summary", {}).get("status") if isinstance(payload.get("fallback_summary"), Mapping) else "", "unknown")
    )
    return {
        "schema_version": SURFACE_VIEW_MODEL_VERSION,
        "view_model_version": SURFACE_VIEW_MODEL_VERSION,
        "view_family": "workbench_run_review",
        "route_id": "workbench_run_review",
        "entity_id": entity_id,
        "canonical_status": status,
        "title": f"Workbench run {entity_id}",
        "summary": "Private Workbench run/review projection",
        "actions": deepcopy(actions),
        "policy_notes": notes + ["private operator projection"],
        "payload": deepcopy(dict(payload)),
        **_no_mutation_flags(),
    }


def fallback_item_view(route_id: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    status, notes = canonical_status(payload.get("status") or route_id)
    item_id = _text(payload.get("candidate_id") or payload.get("need_id") or payload.get("item_id"), route_id)
    return {
        "schema_version": SURFACE_VIEW_MODEL_VERSION,
        "view_model_version": SURFACE_VIEW_MODEL_VERSION,
        "view_family": route_id,
        "route_id": route_id,
        "entity_id": item_id,
        "canonical_status": status,
        "title": _text(payload.get("title"), item_id),
        "summary": _text(payload.get("summary"), "Summary unavailable"),
        "actions": _read_actions(),
        "policy_notes": notes,
        "payload": deepcopy(dict(payload)),
        **_no_mutation_flags(),
    }


def generic_view(route_id: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    status, notes = canonical_status(payload.get("status"))
    entity_id = _text(payload.get("id") or payload.get("entity_id") or payload.get("source_id"), route_id)
    return {
        "schema_version": SURFACE_VIEW_MODEL_VERSION,
        "view_model_version": SURFACE_VIEW_MODEL_VERSION,
        "view_family": route_id,
        "route_id": route_id,
        "entity_id": entity_id,
        "canonical_status": status,
        "title": _text(payload.get("title") or payload.get("label"), entity_id),
        "summary": _text(payload.get("summary"), "Summary unavailable"),
        "actions": _read_actions(),
        "policy_notes": notes,
        "payload": deepcopy(dict(payload)),
        **_no_mutation_flags(),
    }


def _fallback_summary_view(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, Mapping):
        return None
    summary = deepcopy(dict(value))
    status, notes = canonical_status(summary.get("status"))
    summary["canonical_status"] = status
    summary["policy_notes"] = list(summary.get("policy_notes") or []) + notes
    summary["verified"] = False
    summary["accepted_truth"] = False
    summary["reviewed_record_created"] = False
    summary["reviewed_index_mutated"] = False
    summary["public_index_mutated"] = False
    for item in summary.get("candidates") or []:
        if isinstance(item, dict):
            item["canonical_status"] = "candidate"
            item["verified"] = False
            item["accepted_truth"] = False
    for item in summary.get("needs") or []:
        if isinstance(item, dict):
            item["canonical_status"] = "need"
            item["verified"] = False
            item["accepted_truth"] = False
    return summary


def _record_payload(payload: Any) -> dict[str, Any]:
    if isinstance(payload, ResolutionRunRecord):
        return payload.to_dict()
    return _payload_mapping(payload)


def _payload_mapping(payload: Any) -> dict[str, Any]:
    return deepcopy(dict(payload)) if isinstance(payload, Mapping) else {}


def _status_from_run(run: Mapping[str, Any], fallback: Mapping[str, Any] | None) -> str:
    if fallback is not None:
        return _text(fallback.get("status"), "unknown")
    if isinstance(run.get("result_summary"), Mapping):
        return "verified"
    if isinstance(run.get("absence_report"), Mapping):
        return "unknown"
    return _text(run.get("status"), "unknown")


def _resolution_run_summary(
    run: Mapping[str, Any],
    result_summary: Mapping[str, Any] | None,
    fallback: Mapping[str, Any] | None,
) -> str:
    if result_summary is not None:
        return f"{result_summary.get('result_count', 0)} reviewed local results"
    if fallback is not None:
        return f"Fallback returned {fallback.get('canonical_status', 'unknown')}"
    return f"Run status {_text(run.get('status'), 'unknown')}"


def _read_actions() -> list[dict[str, str]]:
    return [
        {"action_id": "view", "classification": "read_only"},
        {"action_id": "inspect_evidence", "classification": "read_only"},
        {"action_id": "cite", "classification": "read_only"},
    ]


def _no_mutation_flags() -> dict[str, bool]:
    return {
        "verified": False,
        "reviewed_record_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def _strings(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return []
    return [item for item in (_text(item, "") for item in value) if item]


def _text(value: Any, default: str) -> str:
    if isinstance(value, str) and value:
        return value
    if isinstance(value, (int, float)):
        return str(value)
    return default

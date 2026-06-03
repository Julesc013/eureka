"""Private Workbench projection over resolution runs and review ledger state."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from runtime.engine.interfaces.public import ResolutionRunRecord
from runtime.review import (
    REVIEW_LEDGER_DECISIONS,
    build_review_item_from_fallback_summary,
    enqueue_fallback_review_item,
    review_boundary_report,
)
from runtime.review.queue import ReviewDecision, ReviewEvent, ReviewItemRecord, ReviewQueueStore


PROJECTION_PROFILES = ("operator_workbench", "public_web", "native_desktop_read_only")
OPERATOR_PROFILE = "operator_workbench"
FALLBACK_REVIEWABLE_STATUSES = frozenset({"candidate", "need"})
REVIEW_CANDIDATE_ACTION = "review" + "_candidate"
REBUILD_INDEX_ACTION = "rebuild" + "_index"
PUBLIC_DISALLOWED_ACTIONS = (
    REVIEW_CANDIDATE_ACTION,
    *REVIEW_LEDGER_DECISIONS,
    REBUILD_INDEX_ACTION,
)
OPERATOR_ACTIONS = (
    "inspect_run",
    "inspect_fallback_summary",
    "inspect_candidate",
    "inspect_need",
    "create_review_item_from_candidate",
    "create_review_item_from_need",
    REVIEW_CANDIDATE_ACTION,
    *REVIEW_LEDGER_DECISIONS,
    "inspect_review_event",
)


def project_workbench_run_review(
    run_or_payload: ResolutionRunRecord | Mapping[str, Any],
    *,
    review_store: ReviewQueueStore | None = None,
    projection_profile: str = OPERATOR_PROFILE,
) -> dict[str, Any]:
    """Project run, fallback, and review ledger state for private Workbench use."""
    profile = _projection_profile(projection_profile)
    run = _run_payload(run_or_payload)
    fallback_summary = _fallback_summary(run)
    review = _project_review_ledger(fallback_summary, review_store, profile)
    fallback_projection = _project_fallback_summary(fallback_summary, review, profile)
    operator_actions = _operator_actions(fallback_summary, review, profile)
    public_action_policy = {
        "public_routes_read_only": True,
        "operator_actions_exposed_publicly": False,
    }
    if profile == OPERATOR_PROFILE:
        public_action_policy["disallowed_public_actions"] = list(PUBLIC_DISALLOWED_ACTIONS)
    else:
        public_action_policy["disallowed_public_action_count"] = len(PUBLIC_DISALLOWED_ACTIONS)

    projection = {
        "schema_version": "workbench_run_review_projection.v0",
        "projection_profile": profile,
        "read_only": profile != OPERATOR_PROFILE,
        "auth_boundary": {
            "operator_auth_enforced_by_this_module": False,
            "exposure": "private_runtime_helper_only",
            "missing_auth_boundary": True,
        },
        "run": _project_run(run),
        "local_lookup": _project_local_lookup(run, fallback_summary),
        "fallback_summary": fallback_projection,
        "review_handoff": _project_review_handoff(fallback_summary, review, profile),
        "review_ledger": review,
        "operator_actions": operator_actions if profile == OPERATOR_PROFILE else [],
        "public_action_policy": public_action_policy,
        "boundary_report": _boundary_report(fallback_summary, profile),
        "warnings": _warnings(profile),
        "limitations": [
            "Workbench projection is private/operator scoped.",
            "Projection does not create reviewed records.",
            "Projection does not mutate reviewed, public, or master indexes.",
        ],
    }
    return projection


def create_review_item_from_fallback_for_workbench(
    review_store: ReviewQueueStore,
    run_or_fallback: ResolutionRunRecord | Mapping[str, Any],
    *,
    priority: int = 100,
    projection_profile: str = OPERATOR_PROFILE,
) -> dict[str, Any]:
    """Create a sanitized review item from fallback output through the operator path."""
    profile = _projection_profile(projection_profile)
    fallback_summary = _fallback_summary(_run_payload(run_or_fallback)) if _looks_like_run(run_or_fallback) else dict(run_or_fallback)
    status = _text(fallback_summary.get("status"), "unavailable")
    blocked_reasons: list[str] = []
    if profile != OPERATOR_PROFILE:
        blocked_reasons.append(f"{profile} projections are read-only")
    if not fallback_summary:
        blocked_reasons.append("fallback_summary is required")
    if status not in FALLBACK_REVIEWABLE_STATUSES:
        blocked_reasons.append(f"{status} fallback state cannot create a review item in this task")
    if blocked_reasons:
        return {
            "schema_version": "workbench_run_review_item_creation.v0",
            "status": "blocked",
            "projection_profile": profile,
            "review_item_created": False,
            "blocked_reasons": blocked_reasons,
            **_mutation_flags(),
        }

    item = enqueue_fallback_review_item(review_store, fallback_summary, priority=priority)
    return {
        "schema_version": "workbench_run_review_item_creation.v0",
        "status": "stored",
        "projection_profile": profile,
        "review_item_created": True,
        "review_item": _project_review_item(item, profile),
        "blocked_reasons": [],
        **_mutation_flags(),
    }


def public_surface_operator_action_audit(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Audit that a public payload does not expose Workbench-only actions."""
    serialized = repr(dict(payload))
    leaked = [action for action in PUBLIC_DISALLOWED_ACTIONS if action in serialized]
    return {
        "schema_version": "workbench_public_surface_operator_action_audit.v0",
        "status": "pass" if not leaked else "fail",
        "operator_actions_exposed_publicly": bool(leaked),
        "leaked_actions": leaked,
        "disallowed_public_actions": list(PUBLIC_DISALLOWED_ACTIONS),
    }


def _project_run(run: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "run_id": _text(run.get("run_id"), ""),
        "run_kind": _text(run.get("run_kind"), ""),
        "requested_value": _text(run.get("requested_value"), ""),
        "status": _text(run.get("status"), ""),
        "started_at": _text(run.get("started_at"), ""),
        "completed_at": _text(run.get("completed_at"), ""),
        "checked_source_ids": _strings(run.get("checked_source_ids")),
        "checked_source_families": _strings(run.get("checked_source_families")),
        "result_kind": _result_kind(run),
        "result_count": _result_count(run),
        "has_absence_report": isinstance(run.get("absence_report"), Mapping),
        "has_fallback_summary": isinstance(run.get("fallback_summary"), Mapping),
    }


def _project_local_lookup(run: Mapping[str, Any], fallback_summary: Mapping[str, Any]) -> dict[str, Any]:
    trigger = _text(fallback_summary.get("trigger"), "")
    if _result_count(run) > 0:
        state = "reviewed_result_available"
        insufficient = False
    elif trigger == "local_lookup_unavailable":
        state = "local_lookup_unavailable"
        insufficient = True
    elif fallback_summary:
        state = "local_lookup_insufficient"
        insufficient = True
    elif isinstance(run.get("absence_report"), Mapping):
        state = "local_lookup_no_results"
        insufficient = True
    else:
        state = "unknown"
        insufficient = True
    return {
        "status": state,
        "local_lookup_first": True,
        "insufficient_for_reviewed_answer": insufficient,
        "result_count": _result_count(run),
        "absence_report_present": isinstance(run.get("absence_report"), Mapping),
        "fallback_trigger": trigger or None,
    }


def _project_fallback_summary(
    fallback_summary: Mapping[str, Any],
    review: Mapping[str, Any],
    profile: str,
) -> dict[str, Any] | None:
    if not fallback_summary:
        return None
    status = _text(fallback_summary.get("status"), "unavailable")
    projected = {
        "schema_version": "workbench_fallback_summary_projection.v0",
        "mode": _text(fallback_summary.get("mode"), "indexless_live_search_fallback"),
        "status": status,
        "trigger": _text(fallback_summary.get("trigger"), ""),
        "query": _text(fallback_summary.get("query"), ""),
        "source_id": _text(fallback_summary.get("source_id"), ""),
        "source_family": _text(fallback_summary.get("source_family"), ""),
        "fallback_enabled": fallback_summary.get("fallback_enabled"),
        "source_allowlisted": bool(fallback_summary.get("source_allowlisted", False)),
        "reason_codes": _strings(fallback_summary.get("reason_codes")),
        "budget": _json_object(fallback_summary.get("budget")),
        "source_observation": _project_source_observation(fallback_summary.get("source_observation"), profile),
        "candidate_count": _non_negative_int(fallback_summary.get("candidate_count"), 0),
        "candidates": [
            _project_fallback_item(item, "candidate", review)
            for item in _mappings(fallback_summary.get("candidates"))
        ],
        "need_count": _non_negative_int(fallback_summary.get("need_count"), 0),
        "needs": [
            _project_fallback_item(item, "need", review)
            for item in _mappings(fallback_summary.get("needs"))
        ],
        "policy_blocked": status == "policy_blocked",
        "unavailable": status == "unavailable",
        "review_required": status in FALLBACK_REVIEWABLE_STATUSES,
        "verified": False,
        "accepted_truth": False,
        "reviewed_record_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }
    if profile != OPERATOR_PROFILE:
        projected["source_observation"] = _redact_source_observation(projected["source_observation"])
    return projected


def _project_fallback_item(
    item: Mapping[str, Any],
    item_kind: str,
    review: Mapping[str, Any],
) -> dict[str, Any]:
    projected = deepcopy(dict(item))
    item_id_key = "candidate_id" if item_kind == "candidate" else "need_id"
    projected.setdefault("status", item_kind)
    projected["item_kind"] = item_kind
    projected["item_id"] = _text(projected.get(item_id_key), "")
    projected["canonical_status"] = item_kind
    projected["verified"] = False
    projected["accepted_truth"] = False
    projected["reviewed_record_created"] = False
    projected["reviewed_index_mutated"] = False
    projected["public_index_mutated"] = False
    projected["master_index_mutated"] = False
    projected["review_item_id"] = review.get("expected_review_item_id")
    projected["review_item_present"] = bool(review.get("review_item_present"))
    return projected


def _project_source_observation(value: Any, profile: str) -> dict[str, Any] | None:
    if not isinstance(value, Mapping):
        return None
    observation = deepcopy(dict(value))
    observation["verified"] = False
    observation["accepted_truth"] = False
    observation["reviewed_record_created"] = False
    observation["reviewed_index_mutated"] = False
    observation["public_index_mutated"] = False
    if profile != OPERATOR_PROFILE:
        observation.pop("warnings", None)
    return observation


def _project_review_handoff(
    fallback_summary: Mapping[str, Any],
    review: Mapping[str, Any],
    profile: str,
) -> dict[str, Any] | None:
    if not fallback_summary:
        return None
    status = _text(fallback_summary.get("status"), "unavailable")
    preview = review.get("review_item_preview")
    allowed = profile == OPERATOR_PROFILE and status in FALLBACK_REVIEWABLE_STATUSES
    return {
        "schema_version": "workbench_review_handoff_projection.v0",
        "status": "available" if allowed else "blocked",
        "input_status": status,
        "review_item_present": bool(review.get("review_item_present")),
        "expected_review_item_id": review.get("expected_review_item_id"),
        "review_item_preview": preview if allowed else None,
        "allowed_actions": _handoff_actions(status) if allowed else [],
        "blocked_reasons": [] if allowed else [f"{status} fallback state is not eligible for review-item creation here"],
        "reviewed_record_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def _project_review_ledger(
    fallback_summary: Mapping[str, Any],
    review_store: ReviewQueueStore | None,
    profile: str,
) -> dict[str, Any]:
    expected_item = build_review_item_from_fallback_summary(fallback_summary) if fallback_summary else None
    stored_item = (
        review_store.get_review_item(expected_item.review_item_id)
        if review_store is not None and expected_item is not None
        else None
    )
    item = stored_item or expected_item
    decisions = (
        [_project_decision(decision, profile) for decision in review_store.list_decisions(item.review_item_id)]
        if review_store is not None and stored_item is not None
        else []
    )
    events = (
        [_project_event(event, profile) for event in review_store.list_events(item.review_item_id)]
        if review_store is not None and stored_item is not None
        else []
    )
    return {
        "schema_version": "workbench_review_ledger_projection.v0",
        "review_store_present": review_store is not None,
        "review_item_present": stored_item is not None,
        "expected_review_item_id": item.review_item_id if item is not None else None,
        "review_item_preview": _project_review_item(expected_item, profile) if expected_item is not None else None,
        "review_items": [_project_review_item(stored_item, profile)] if stored_item is not None else [],
        "review_item_count": 1 if stored_item is not None else 0,
        "decisions": decisions,
        "decision_count": len(decisions),
        "audit_events": events,
        "audit_event_count": len(events),
        "allowed_ledger_decisions": list(REVIEW_LEDGER_DECISIONS) if profile == OPERATOR_PROFILE else [],
        "reviewed_record_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def _project_review_item(item: ReviewItemRecord | None, profile: str) -> dict[str, Any] | None:
    if item is None:
        return None
    payload = dict(item.payload)
    projected = {
        "review_item_id": item.review_item_id,
        "subject_kind": item.subject_kind,
        "subject_id": item.subject_id,
        "queue_status": item.queue_status.value,
        "priority": item.priority,
        "evidence_id": item.evidence_id,
        "source_cache_entry_id": item.source_cache_entry_id,
        "summary": item.summary,
        "payload": {
            "schema_version": _text(payload.get("schema_version"), ""),
            "input_kind": _text(payload.get("input_kind"), ""),
            "fallback_status": _text(payload.get("fallback_status"), ""),
            "candidate_ids": _strings(payload.get("candidate_ids")),
            "need_ids": _strings(payload.get("need_ids")),
            "source_observation_refs": _strings(payload.get("source_observation_refs")),
            "evidence_refs": _strings(payload.get("evidence_refs")),
            "fallback_refs": _strings(payload.get("fallback_refs")),
            "review_required": bool(payload.get("review_required", True)),
            "self_promotion_allowed": False,
        },
        "limitations": list(item.limitations),
        "warnings": list(item.warnings),
        "created_at": item.created_at,
        "updated_at": item.updated_at,
    }
    if profile != OPERATOR_PROFILE:
        projected["payload"] = {
            "fallback_status": projected["payload"]["fallback_status"],
            "review_required": projected["payload"]["review_required"],
            "self_promotion_allowed": False,
        }
    return projected


def _project_decision(decision: ReviewDecision, profile: str) -> dict[str, Any]:
    projected = decision.to_dict()
    projected["reviewed_record_created"] = False
    projected["reviewed_index_mutated"] = False
    projected["public_index_mutated"] = False
    projected["master_index_mutated"] = False
    if profile != OPERATOR_PROFILE:
        projected.pop("decision_actor", None)
        projected.pop("reason", None)
    return projected


def _project_event(event: ReviewEvent, profile: str) -> dict[str, Any]:
    projected = event.to_dict()
    projected["audit_visible"] = True
    if profile != OPERATOR_PROFILE:
        projected["event_payload"] = {
            "ledger_event_kind": projected.get("event_payload", {}).get("ledger_event_kind"),
        }
    return projected


def _operator_actions(
    fallback_summary: Mapping[str, Any],
    review: Mapping[str, Any],
    profile: str,
) -> list[dict[str, Any]]:
    if profile != OPERATOR_PROFILE:
        return []
    fallback_status = _text(fallback_summary.get("status"), "")
    review_item_present = bool(review.get("review_item_present"))
    events_present = bool(review.get("audit_events"))
    actions: list[dict[str, Any]] = []
    for action_id in OPERATOR_ACTIONS:
        enabled = _action_enabled(action_id, fallback_status, fallback_summary, review_item_present, events_present)
        actions.append(
            {
                "action_id": action_id,
                "classification": "operator_only",
                "enabled": enabled,
                "mutates_review_queue": action_id.startswith("create_review_item"),
                "mutates_review_ledger": action_id in REVIEW_LEDGER_DECISIONS or action_id == REVIEW_CANDIDATE_ACTION,
                "mutates_reviewed_record": False,
                "mutates_reviewed_index": False,
                "mutates_public_index": False,
                "mutates_master_index": False,
                "blocked_reasons": [] if enabled else _action_blocked_reasons(action_id, fallback_status, review_item_present, events_present),
            }
        )
    return actions


def _action_enabled(
    action_id: str,
    fallback_status: str,
    fallback_summary: Mapping[str, Any],
    review_item_present: bool,
    events_present: bool,
) -> bool:
    if action_id == "inspect_run":
        return True
    if action_id == "inspect_fallback_summary":
        return bool(fallback_summary)
    if action_id == "inspect_candidate":
        return fallback_status == "candidate"
    if action_id == "inspect_need":
        return fallback_status == "need"
    if action_id == "create_review_item_from_candidate":
        return fallback_status == "candidate" and not review_item_present
    if action_id == "create_review_item_from_need":
        return fallback_status == "need" and not review_item_present
    if action_id == REVIEW_CANDIDATE_ACTION:
        return review_item_present and fallback_status == "candidate"
    if action_id in REVIEW_LEDGER_DECISIONS:
        return review_item_present
    if action_id == "inspect_review_event":
        return events_present
    return False


def _action_blocked_reasons(
    action_id: str,
    fallback_status: str,
    review_item_present: bool,
    events_present: bool,
) -> list[str]:
    if action_id.startswith("create_review_item"):
        if fallback_status not in FALLBACK_REVIEWABLE_STATUSES:
            return [f"{fallback_status or 'missing'} fallback state is not review-item creation eligible"]
        if review_item_present:
            return ["review item already exists"]
    if action_id in REVIEW_LEDGER_DECISIONS or action_id == REVIEW_CANDIDATE_ACTION:
        if not review_item_present:
            return ["review item is required before this action"]
    if action_id == "inspect_review_event" and not events_present:
        return ["no review audit event is present"]
    if action_id == "inspect_fallback_summary" and not fallback_status:
        return ["fallback summary is absent"]
    return ["not applicable to current projection state"]


def _handoff_actions(status: str) -> list[str]:
    if status == "candidate":
        return ["inspect_candidate", "create_review_item_from_candidate"]
    if status == "need":
        return ["inspect_need", "create_review_item_from_need"]
    return []


def _boundary_report(fallback_summary: Mapping[str, Any], profile: str) -> dict[str, Any]:
    report = review_boundary_report(fallback_summary or {})
    report.update(_mutation_flags())
    report.update(
        {
            "workbench_projection_only": True,
            "public_projection_can_change_review_state": False,
            "operator_actions_exposed_publicly": False,
            "source_provider_called_by_workbench_projection": False,
        }
    )
    if profile != OPERATOR_PROFILE:
        report = {
            "schema_version": "workbench_run_review_public_boundary_report.v0",
            "workbench_projection_only": True,
            "public_projection_can_change_review_state": False,
            "review_event_required_for_reviewed_status": True,
            "operator_actions_exposed_publicly": False,
            "source_provider_called_by_workbench_projection": False,
            **_mutation_flags(),
        }
    return report


def _mutation_flags() -> dict[str, bool]:
    return {
        "reviewed_record_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "operator_instance_mutated": False,
    }


def _run_payload(run_or_payload: ResolutionRunRecord | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(run_or_payload, ResolutionRunRecord):
        return run_or_payload.to_dict()
    payload = deepcopy(dict(run_or_payload))
    if _looks_like_fallback_summary(payload):
        return {"fallback_summary": payload}
    return payload


def _fallback_summary(run_payload: Mapping[str, Any]) -> dict[str, Any]:
    value = run_payload.get("fallback_summary")
    return deepcopy(dict(value)) if isinstance(value, Mapping) else {}


def _looks_like_run(value: object) -> bool:
    return isinstance(value, ResolutionRunRecord) or (
        isinstance(value, Mapping)
        and ("fallback_summary" in value or "run_id" in value or "run_kind" in value)
        and not _looks_like_fallback_summary(value)
    )


def _looks_like_fallback_summary(value: Mapping[str, Any]) -> bool:
    return _text(value.get("mode"), "") == "indexless_live_search_fallback" or (
        "candidate_count" in value and "candidates" in value and "status" in value
    )


def _result_kind(run: Mapping[str, Any]) -> str | None:
    summary = run.get("result_summary")
    if not isinstance(summary, Mapping):
        return None
    return _text(summary.get("result_kind"), "")


def _result_count(run: Mapping[str, Any]) -> int:
    summary = run.get("result_summary")
    if not isinstance(summary, Mapping):
        return 0
    return _non_negative_int(summary.get("result_count"), 0)


def _projection_profile(value: str) -> str:
    if value not in PROJECTION_PROFILES:
        raise ValueError(f"unsupported projection profile: {value}")
    return value


def _json_object(value: Any) -> dict[str, Any]:
    return deepcopy(dict(value)) if isinstance(value, Mapping) else {}


def _mappings(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _redact_source_observation(value: dict[str, Any] | None) -> dict[str, Any] | None:
    if value is None:
        return None
    return {
        key: deepcopy(item)
        for key, item in value.items()
        if key
        in {
            "schema_version",
            "observation_id",
            "status",
            "source_id",
            "source_family",
            "candidate_count",
            "accepted_truth",
            "verified",
            "review_required",
        }
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


def _non_negative_int(value: Any, default: int) -> int:
    if isinstance(value, int) and value >= 0:
        return value
    return default


def _warnings(profile: str) -> list[str]:
    if profile == OPERATOR_PROFILE:
        return []
    return ["Non-operator projections are read-only and hide operator controls."]


__all__ = [
    "OPERATOR_ACTIONS",
    "PUBLIC_DISALLOWED_ACTIONS",
    "create_review_item_from_fallback_for_workbench",
    "project_workbench_run_review",
    "public_surface_operator_action_audit",
]

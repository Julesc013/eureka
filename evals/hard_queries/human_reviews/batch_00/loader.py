"""Loader and projection helpers for human review batch zero."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Mapping

from evals.hard_queries.manual_observations.batch_00 import (
    BASELINE_PROFILES,
    load_observations,
    load_reviewable_items,
    observation_records,
)
from runtime.surface import SurfaceKernel, SurfaceRequest


REVIEW_DECISIONS = (
    "promote",
    "reject",
    "supersede",
    "mark_near_miss",
    "mark_need",
    "mark_policy_blocked",
    "request_more_evidence",
)
DECISION_RESULTING_STATUS = {
    "promote": "verified",
    "reject": "rejected",
    "supersede": "superseded",
    "mark_near_miss": "near_miss",
    "mark_need": "need",
    "mark_policy_blocked": "policy_blocked",
    "request_more_evidence": "need",
}
PUBLIC_ALLOWED_ACTIONS = frozenset({"view", "inspect_evidence", "compare", "cite", "export_manifest"})
OPERATOR_ACTIONS = frozenset({"review_candidate", "promote", "reject", "request_more_evidence", "mark_near_miss", "mark_need"})
REQUIRED_DECISION_FIELDS = (
    "review_decision_id",
    "review_event_id",
    "review_item_id",
    "manual_observation_id",
    "hard_query_id",
    "decision",
    "resulting_status",
    "actor_id",
    "actor_type",
    "review_mode",
    "reviewed_at",
    "rationale",
    "source_references_used",
    "citation_reference_ids",
    "confidence",
    "known_limitations",
    "public_visibility",
    "index_impact",
    "next_required_action",
    "local_only_confirmed",
    "reviewed_record_created",
    "reviewed_record_id",
    "reviewed_index_mutated",
    "public_index_mutated",
    "master_index_mutated",
    "synthetic_eval_fixture_used_as_evidence",
    "ai_model_output_counted_as_truth",
    "source_observation_self_promoted",
    "candidate_self_promoted",
    "fallback_summary_self_promoted",
)


def batch_root() -> Path:
    return Path(__file__).resolve().parent


def load_review_decisions(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "review_decisions.json")


def load_review_events(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "review_events.json")


def load_reviewed_seed_records(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "reviewed_seed_records.json")


def load_corpus_gate_update(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "corpus_gate_update.json")


def load_record_materialization_backlog(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "record_materialization_backlog.json")


def review_decision_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("review_decisions") or [] if isinstance(item, Mapping))


def reviewed_seed_record_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("reviewed_seed_records") or [] if isinstance(item, Mapping))


def review_decision_counts(payload: Mapping[str, Any]) -> dict[str, int]:
    counts = {decision: 0 for decision in REVIEW_DECISIONS}
    counts.update(
        {
            "reviewed": 0,
            "review_decision_backed": 0,
            "candidate": 0,
            "need": 0,
            "near_miss": 0,
            "policy_blocked": 0,
            "unavailable": 0,
            "blocked_for_user_details": 0,
            "request_more_evidence": 0,
        }
    )
    for item in review_decision_records(payload):
        decision = str(item.get("decision") or "")
        resulting = str(item.get("resulting_status") or "unknown")
        if decision in REVIEW_DECISIONS:
            counts[decision] += 1
            counts["review_decision_backed"] += 1
        if decision == "promote" and resulting == "verified" and item.get("reviewed_record_created") is True:
            counts["reviewed"] += 1
        elif resulting in {"candidate", "need", "near_miss", "policy_blocked", "unavailable"}:
            counts[resulting] += 1
        if str(item.get("next_required_action") or "") == "collect_user_hardware_details":
            counts["blocked_for_user_details"] += 1
    return counts


def validate_review_decisions(
    payload: Mapping[str, Any],
    *,
    observations: Mapping[str, Any] | None = None,
    reviewable_items: Mapping[str, Any] | None = None,
) -> tuple[str, ...]:
    errors: list[str] = []
    decisions = payload.get("review_decisions")
    if not isinstance(decisions, list):
        return ("review_decisions must be a list",)
    records = review_decision_records(payload)
    ids = [str(item.get("review_decision_id") or "") for item in records]
    if len(ids) != len(set(ids)):
        errors.append("review_decision_id values must be unique")
    observation_ids = {item["observation_id"] for item in observation_records(observations or load_observations())}
    reviewable_ids = {
        str(item.get("reviewable_item_id") or "")
        for item in (reviewable_items or load_reviewable_items()).get("reviewable_items", [])
        if isinstance(item, Mapping)
    }
    for item in records:
        errors.extend(_validate_decision(item, observation_ids, reviewable_ids))
    return tuple(errors)


def validate_review_events(events: Mapping[str, Any], decisions: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    event_items = events.get("review_events")
    if not isinstance(event_items, list):
        return ("review_events must be a list",)
    decision_by_event = {
        str(item.get("review_event_id") or ""): item for item in review_decision_records(decisions or load_review_decisions())
    }
    for event in event_items:
        if not isinstance(event, Mapping):
            errors.append("review event must be an object")
            continue
        event_id = str(event.get("review_event_id") or "")
        if event_id not in decision_by_event:
            errors.append(f"{event_id or '<missing>'} has no matching decision")
        if event.get("event_kind") != "decision_recorded":
            errors.append(f"{event_id or '<missing>'} must be decision_recorded")
        for flag in ("reviewed_index_mutated", "public_index_mutated", "master_index_mutated"):
            if event.get(flag) is not False:
                errors.append(f"{event_id or '<missing>'} must keep {flag}=false")
    return tuple(errors)


def validate_reviewed_seed_records(records: Mapping[str, Any], decisions: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    seed_records = records.get("reviewed_seed_records")
    if not isinstance(seed_records, list):
        return ("reviewed_seed_records must be a list",)
    promote_decisions = {
        str(item.get("review_decision_id") or ""): item
        for item in review_decision_records(decisions or load_review_decisions())
        if item.get("decision") == "promote"
    }
    for record in reviewed_seed_record_records(records):
        record_id = str(record.get("reviewed_seed_record_id") or "<missing>")
        decision_id = str(record.get("review_decision_id") or "")
        if decision_id not in promote_decisions:
            errors.append(f"{record_id} must reference a promote decision")
        if record.get("canonical_status") != "verified":
            errors.append(f"{record_id} must be verified")
        if not record.get("review_event_id"):
            errors.append(f"{record_id} must include review_event_id")
        if not record.get("evidence_refs"):
            errors.append(f"{record_id} must include evidence refs")
        if not record.get("source_observation_refs"):
            errors.append(f"{record_id} must include source observation refs")
        if record.get("reviewed_record_created") is not True:
            errors.append(f"{record_id} must mark reviewed_record_created=true")
        for flag in ("reviewed_index_mutated", "public_index_mutated", "master_index_mutated"):
            if record.get(flag) is not False:
                errors.append(f"{record_id} must keep {flag}=false")
    return tuple(errors)


def validate_corpus_gate_update(payload: Mapping[str, Any], decisions: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    if payload.get("public_alpha_corpus_gate") != "FAIL_INSUFFICIENT_REVIEWED_CORPUS":
        errors.append("corpus gate must remain failed for this batch")
    counts = payload.get("counts")
    if not isinstance(counts, Mapping):
        return tuple(errors + ["counts must be present"])
    if decisions is not None:
        computed = review_decision_counts(decisions)
        for key in ("reviewed", "review_decision_backed", "candidate", "need", "near_miss", "policy_blocked", "unavailable", "request_more_evidence", "blocked_for_user_details"):
            count_key = f"{key}_count"
            if int(counts.get(count_key, -1)) != computed[key]:
                errors.append(f"{count_key} does not match decisions")
    truth = payload.get("truth_boundary")
    if not isinstance(truth, Mapping):
        errors.append("truth_boundary must be present")
    else:
        for key, value in truth.items():
            if value is not False:
                errors.append(f"truth boundary flag must be false: {key}")
    return tuple(errors)


def validate_record_materialization_backlog(payload: Mapping[str, Any], decisions: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    backlog = payload.get("record_materialization_backlog")
    if not isinstance(backlog, list):
        return ("record_materialization_backlog must be a list",)
    decision_ids = {str(item.get("review_decision_id") or "") for item in review_decision_records(decisions or load_review_decisions())}
    for item in backlog:
        if not isinstance(item, Mapping):
            errors.append("backlog item must be an object")
            continue
        if str(item.get("review_decision_id") or "") not in decision_ids:
            errors.append(f"{item.get('backlog_item_id', '<missing>')} references unknown decision")
        if item.get("reviewed_seed_record_created") is not False:
            errors.append(f"{item.get('backlog_item_id', '<missing>')} must not create reviewed seed record")
    return tuple(errors)


def project_review_decision(decision: Mapping[str, Any], profile: str, *, visibility_posture: str = "public") -> dict[str, Any]:
    public = visibility_posture != "operator_private"
    return SurfaceKernel().project(
        SurfaceRequest(
            route_id="object",
            entity_id=_public_decision_ref(decision) if public else str(decision.get("review_decision_id") or "review-decision"),
            payload=_decision_view_payload(decision, public=public),
            requested_profile=profile,
            visibility_posture=visibility_posture,
            data_version="human-review-batch-00",
        )
    )


def project_reviewed_seed_record(record: Mapping[str, Any], profile: str, *, visibility_posture: str = "public") -> dict[str, Any]:
    public = visibility_posture != "operator_private"
    return SurfaceKernel().project(
        SurfaceRequest(
            route_id="object",
            entity_id=str(record.get("reviewed_seed_record_id") or "reviewed-seed-record"),
            payload=_record_view_payload(record, public=public),
            requested_profile=profile,
            visibility_posture=visibility_posture,
            data_version="human-review-batch-00",
        )
    )


def _validate_decision(item: Mapping[str, Any], observation_ids: set[str], reviewable_ids: set[str]) -> tuple[str, ...]:
    errors: list[str] = []
    decision_id = str(item.get("review_decision_id") or "<missing>")
    for field in REQUIRED_DECISION_FIELDS:
        if field not in item:
            errors.append(f"{decision_id} missing {field}")
    decision = str(item.get("decision") or "")
    if decision not in REVIEW_DECISIONS:
        errors.append(f"{decision_id} has unsupported decision")
    if str(item.get("resulting_status") or "") != DECISION_RESULTING_STATUS.get(decision):
        errors.append(f"{decision_id} has inconsistent resulting_status")
    if str(item.get("manual_observation_id") or "") not in observation_ids:
        errors.append(f"{decision_id} references unknown observation")
    review_item_id = str(item.get("review_item_id") or "")
    if review_item_id and review_item_id.startswith("reviewable_") and review_item_id not in reviewable_ids:
        errors.append(f"{decision_id} references unknown reviewable item")
    if decision == "promote":
        if item.get("local_only_confirmed") is not True:
            errors.append(f"{decision_id} promote requires local_only_confirmed=true")
        if not item.get("source_references_used"):
            errors.append(f"{decision_id} promote requires source references")
        if not item.get("citation_reference_ids"):
            errors.append(f"{decision_id} promote requires citation references")
        if item.get("reviewed_record_created") is not True:
            errors.append(f"{decision_id} promote should create reviewed seed record in this batch")
    else:
        if item.get("reviewed_record_created") is not False:
            errors.append(f"{decision_id} non-promote must not create reviewed record")
    if not item.get("rationale"):
        errors.append(f"{decision_id} must include rationale")
    for flag in (
        "reviewed_index_mutated",
        "public_index_mutated",
        "master_index_mutated",
        "synthetic_eval_fixture_used_as_evidence",
        "ai_model_output_counted_as_truth",
        "source_observation_self_promoted",
        "candidate_self_promoted",
        "fallback_summary_self_promoted",
    ):
        if item.get(flag) is not False:
            errors.append(f"{decision_id} must keep {flag}=false")
    return tuple(errors)


def _decision_view_payload(decision: Mapping[str, Any], *, public: bool) -> dict[str, Any]:
    payload = {
        "schema_version": "human_review_decision_view.v0",
        "id": _public_decision_ref(decision) if public else str(decision.get("review_decision_id") or "review-decision"),
        "title": str(decision.get("title") or decision.get("review_item_id") or "Review decision"),
        "summary": str(decision.get("rationale") or ""),
        "status": str(decision.get("resulting_status") or "unknown"),
        "reviewed_record_created": bool(decision.get("reviewed_record_created")),
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }
    if public:
        payload["public_review_ref"] = _public_decision_ref(decision)
        payload["actions"] = [
            {"action_id": "view", "classification": "read_only"},
            {"action_id": "inspect_evidence", "classification": "read_only"},
            {"action_id": "cite", "classification": "read_only"},
        ]
    else:
        operator_actions = list(decision.get("operator_actions") or ["review_candidate", str(decision.get("decision") or "")])
        payload["review_decision_id"] = str(decision.get("review_decision_id") or "")
        payload["review_event_id"] = str(decision.get("review_event_id") or "")
        payload["decision"] = str(decision.get("decision") or "")
        payload["operator_actions"] = operator_actions
        payload["actions"] = [{"action_id": action, "classification": "operator"} for action in operator_actions]
    return payload


def _record_view_payload(record: Mapping[str, Any], *, public: bool) -> dict[str, Any]:
    payload = {
        "schema_version": "human_review_seed_record_view.v0",
        "id": str(record.get("reviewed_seed_record_id") or "reviewed-seed-record"),
        "title": str(record.get("title") or "Reviewed seed record"),
        "summary": str(record.get("summary") or ""),
        "status": str(record.get("canonical_status") or "unknown"),
        "actions": [{"action_id": "view", "classification": "read_only"}, {"action_id": "inspect_evidence", "classification": "read_only"}, {"action_id": "cite", "classification": "read_only"}],
        "reviewed_record_created": True,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }
    if public:
        payload["public_review_ref"] = f"reviewed_seed_public_{record.get('hard_query_id', 'unknown')}"
    else:
        payload["review_event_id"] = str(record.get("review_event_id") or "")
        payload["review_decision_id"] = str(record.get("review_decision_id") or "")
        payload["operator_actions"] = ["review_candidate", "rebuild_index"]
    return payload


def _public_decision_ref(decision: Mapping[str, Any]) -> str:
    return f"review_decision_public_{decision.get('hard_query_id', 'unknown')}"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

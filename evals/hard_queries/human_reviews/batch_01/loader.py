"""Loader and projection helpers for human review batch one."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Mapping

from evals.hard_queries.manual_observations.batch_01 import (
    BASELINE_PROFILES,
    load_non_reviewable_items,
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
OPERATOR_ACTIONS = frozenset(
    {"review_candidate", "promote", "reject", "supersede", "request_more_evidence", "mark_near_miss", "mark_need"}
)
TRUTH_BOUNDARY_FLAGS = (
    "synthetic_eval_fixture_used_as_evidence",
    "ai_model_output_counted_as_truth",
    "source_observation_self_promoted",
    "candidate_self_promoted",
    "fallback_summary_self_promoted",
    "reviewable_item_self_promoted",
    "reviewed_index_mutated",
    "public_index_mutated",
    "master_index_mutated",
    "product_runtime_live_source_calls_performed",
    "downloads_performed",
    "file_fetches_performed",
    "wayback_replay_performed",
)
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


def load_query_coverage_update(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "query_coverage_update.json")


def load_surface_projection_fixtures(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "surface_projection_fixtures.json")


def load_renderer_expected_outputs(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "renderer_expected_outputs.json")


def load_record_materialization_backlog(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "record_materialization_backlog.json")


def review_decision_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("review_decisions") or [] if isinstance(item, Mapping))


def reviewed_seed_record_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("reviewed_seed_records") or [] if isinstance(item, Mapping))


def query_coverage_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("query_coverage") or [] if isinstance(item, Mapping))


def review_decision_counts(payload: Mapping[str, Any]) -> dict[str, int]:
    counts = {decision: 0 for decision in REVIEW_DECISIONS}
    counts.update(
        {
            "reviewed": 0,
            "review_decision_backed": 0,
            "candidate": 0,
            "need": 0,
            "near_miss": 0,
            "superseded": 0,
            "policy_blocked": 0,
            "unavailable": 0,
            "unknown": 0,
            "request_more_evidence": 0,
            "blocked_for_user_details": 0,
        }
    )
    for item in review_decision_records(payload):
        decision = str(item.get("decision") or "")
        resulting = str(item.get("resulting_status") or "unknown")
        if decision in REVIEW_DECISIONS:
            counts[decision] += 1
            counts["review_decision_backed"] += 1
        if str(item.get("next_required_action") or "") == "collect_user_hardware_details":
            counts["blocked_for_user_details"] += 1
        if decision == "promote" and resulting == "verified" and item.get("reviewed_record_created") is True:
            counts["reviewed"] += 1
        elif resulting in {"candidate", "need", "near_miss", "superseded", "policy_blocked", "unavailable"}:
            counts[resulting] += 1
        elif resulting != "verified":
            counts["unknown"] += 1
    return counts


def validate_review_decisions(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    decisions = payload.get("review_decisions")
    if not isinstance(decisions, list):
        return ("review_decisions must be a list",)
    records = review_decision_records(payload)
    ids = [str(item.get("review_decision_id") or "") for item in records]
    if len(ids) != len(set(ids)):
        errors.append("review_decision_id values must be unique")
    observation_ids = {item["observation_id"] for item in observation_records(load_observations())}
    valid_review_item_ids = _valid_review_item_ids()
    for item in records:
        errors.extend(_validate_decision(item, observation_ids, valid_review_item_ids))
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
    if len(seed_records) != len(promote_decisions):
        errors.append("reviewed seed records must match promote decisions")
    for record in reviewed_seed_record_records(records):
        record_id = str(record.get("reviewed_seed_record_id") or "<missing>")
        decision_id = str(record.get("review_decision_id") or "")
        if decision_id not in promote_decisions:
            errors.append(f"{record_id} must reference a promote decision")
        if record.get("canonical_status") != "verified":
            errors.append(f"{record_id} must be verified")
        if record.get("accepted_truth") is not True:
            errors.append(f"{record_id} must mark accepted_truth=true")
        if not record.get("review_event_id") or not record.get("evidence_refs") or not record.get("source_observation_refs"):
            errors.append(f"{record_id} must include review event and evidence refs")
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
    batch_counts = payload.get("batch_counts")
    if not isinstance(batch_counts, Mapping):
        return tuple(errors + ["batch_counts must be present"])
    if decisions is not None:
        computed = review_decision_counts(decisions)
        for key in (
            "reviewed",
            "review_decision_backed",
            "candidate",
            "need",
            "near_miss",
            "superseded",
            "policy_blocked",
            "unavailable",
            "request_more_evidence",
            "blocked_for_user_details",
        ):
            if int(batch_counts.get(f"{key}_count", -1)) != computed[key]:
                errors.append(f"batch {key}_count does not match decisions")
    cumulative = payload.get("cumulative_counts_after_batch")
    if not isinstance(cumulative, Mapping):
        errors.append("cumulative_counts_after_batch must be present")
    elif int(cumulative.get("reviewed_count", 0)) < int(batch_counts.get("reviewed_count", 0)):
        errors.append("cumulative reviewed count must include batch reviewed count")
    for flag in TRUTH_BOUNDARY_FLAGS:
        if payload.get("truth_boundary", {}).get(flag) is not False:
            errors.append(f"truth boundary flag must be false: {flag}")
    return tuple(errors)


def validate_query_coverage_update(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    items = query_coverage_records(payload)
    if len(items) != 6:
        errors.append("query coverage must include six hard queries")
    query_ids = {str(item.get("hard_query_id") or "") for item in items}
    for required in {
        "hq_windows_7_apps",
        "hq_driver_win98",
        "hq_blue_ftp_client_xp",
        "hq_sound_blaster_ct1740_manual",
        "hq_firefox_last_xp",
        "hq_ray_tracing_1994_magazine",
    }:
        if required not in query_ids:
            errors.append(f"missing query coverage for {required}")
    for item in items:
        if item.get("public_alpha_readiness") != "not_ready":
            errors.append(f"{item.get('hard_query_id', '<missing>')} must remain not_ready")
        if not item.get("next_required_action"):
            errors.append(f"{item.get('hard_query_id', '<missing>')} must include next_required_action")
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
        item_id = str(item.get("backlog_item_id") or "<missing>")
        if str(item.get("review_decision_id") or "") not in decision_ids:
            errors.append(f"{item_id} references unknown decision")
        if item.get("reviewed_seed_record_created") is not False:
            errors.append(f"{item_id} must not create reviewed seed record")
    return tuple(errors)


def validate_surface_projection_fixtures(payload: Mapping[str, Any], decisions: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    fixtures = payload.get("fixtures")
    if not isinstance(fixtures, list):
        return ("surface projection fixtures must be a list",)
    decision_by_id = {
        str(item.get("review_decision_id") or ""): item for item in review_decision_records(decisions or load_review_decisions())
    }
    for fixture in fixtures:
        if not isinstance(fixture, Mapping):
            errors.append("fixture must be an object")
            continue
        fixture_id = str(fixture.get("review_decision_id") or "")
        decision = decision_by_id.get(fixture_id)
        if decision is None:
            errors.append(f"{fixture_id or '<missing>'} references unknown decision")
            continue
        if fixture.get("expected_status") != decision.get("resulting_status"):
            errors.append(f"{fixture_id} expected status does not match decision")
        if tuple(fixture.get("renderer_profiles_expected") or ()) != BASELINE_PROFILES:
            errors.append(f"{fixture_id} must cover all baseline profiles")
        public_actions = set(_strings(fixture.get("public_actions")))
        if not public_actions.issubset(PUBLIC_ALLOWED_ACTIONS):
            errors.append(f"{fixture_id} has unsafe public action")
    return tuple(errors)


def validate_renderer_expected_outputs(payload: Mapping[str, Any], decisions: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    if tuple(payload.get("renderer_profiles") or ()) != BASELINE_PROFILES:
        errors.append("renderer expected outputs must cover all baseline profiles")
    expected = payload.get("expected_status_by_decision")
    if not isinstance(expected, Mapping):
        return tuple(errors + ["expected_status_by_decision must be present"])
    for decision in review_decision_records(decisions or load_review_decisions()):
        decision_id = str(decision.get("review_decision_id") or "")
        if expected.get(decision_id) != decision.get("resulting_status"):
            errors.append(f"{decision_id} expected status does not match decision")
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
            data_version="human-review-batch-01",
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
            data_version="human-review-batch-01",
        )
    )


def _validate_decision(item: Mapping[str, Any], observation_ids: set[str], valid_review_item_ids: set[str]) -> tuple[str, ...]:
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
    if str(item.get("review_item_id") or "") not in valid_review_item_ids:
        errors.append(f"{decision_id} references unknown review item")
    if decision == "promote":
        if item.get("local_only_confirmed") is not True:
            errors.append(f"{decision_id} promote requires local_only_confirmed=true")
        if not item.get("source_references_used") or not item.get("citation_reference_ids"):
            errors.append(f"{decision_id} promote requires source and citation references")
        if item.get("reviewed_record_created") is not True or not item.get("reviewed_record_id"):
            errors.append(f"{decision_id} promote must create a reviewed seed record")
    else:
        if item.get("reviewed_record_created") is not False or item.get("reviewed_record_id") is not None:
            errors.append(f"{decision_id} non-promote must not create reviewed record")
    if decision == "supersede" and not item.get("superseded_by_reviewed_record_id"):
        errors.append(f"{decision_id} supersede requires superseded_by_reviewed_record_id")
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
        "summary": str(decision.get("public_summary") or decision.get("rationale") or ""),
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
        operator_actions = [action for action in _strings(decision.get("operator_actions")) if action in OPERATOR_ACTIONS]
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
        "actions": [
            {"action_id": "view", "classification": "read_only"},
            {"action_id": "inspect_evidence", "classification": "read_only"},
            {"action_id": "cite", "classification": "read_only"},
        ],
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


def _valid_review_item_ids() -> set[str]:
    reviewable_ids = {
        str(item.get("review_item_id") or "")
        for item in load_reviewable_items().get("reviewable_items", [])
        if isinstance(item, Mapping)
    }
    non_reviewable_ids = {
        str(item.get("non_reviewable_item_id") or "")
        for item in load_non_reviewable_items().get("non_reviewable_items", [])
        if isinstance(item, Mapping)
    }
    return {item_id for item_id in reviewable_ids | non_reviewable_ids if item_id}


def _public_decision_ref(decision: Mapping[str, Any]) -> str:
    return f"review_decision_public_{decision.get('hard_query_id', 'unknown')}_{decision.get('manual_observation_id', 'unknown')}"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _strings(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    if isinstance(value, tuple):
        return [str(item) for item in value if str(item)]
    if isinstance(value, str) and value:
        return [value]
    return []

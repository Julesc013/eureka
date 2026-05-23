"""Workbench review, promotion-preview, and temp refresh helpers."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

from runtime.evidence.ledger import EvidenceCandidateRecord, EvidenceReviewStatus
from runtime.local.review import rebuild_reviewed_index, record_review_decision as record_local_review_decision
from runtime.index.public.absence import build_absence_report
from runtime.review.queue import ReviewItemRecord, ReviewQueueStatus
from runtime.resolution_run.run_store import FIXED_CREATED_AT, stable_id
from runtime.source.cache import SourceCacheEntry, SourceCacheStatus


PROJECTION_PROFILES = ("operator_workbench", "public_web", "native_desktop_read_only")
REVIEW_DECISIONS = (
    "accept_local_reviewed",
    "reject_wrong_object",
    "reject_wrong_version",
    "reject_wrong_platform",
    "needs_more_evidence",
    "duplicate",
    "unsafe",
    "rights_risk",
    "defer",
)
READ_ONLY_PROJECTIONS = {"public_web", "native_desktop_read_only"}
BLOCKED_ACTIONS = (
    "automatic_candidate_acceptance",
    "operator_instance_apply",
    "master_index_mutation",
    "public_index_mutation",
    "download",
    "extraction",
    "model_provider_call",
    "deployment",
)

SAMPLE_CANDIDATE = {
    "schema_version": "workbench_review_candidate.v0",
    "candidate_id": "candidate.workbench_review.sampleproject.v0",
    "candidate_source": "local_candidate_results",
    "title": "SampleProject candidate",
    "summary": "Fixture candidate for Workbench review/promotion preview.",
    "source_id": "source.fixture.workbench_review",
    "source_family": "fixture",
    "source_locator": "fixture:workbench-review-promote:sampleproject",
    "evidence_id": "evidence.workbench_review.sampleproject.v0",
    "source_cache_entry_id": "source_cache.workbench_review.sampleproject.v0",
    "claim_subject": "sampleproject",
    "domain_id": "legacy_software",
    "review_required": True,
    "accepted_truth": False,
    "limitations": [
        "Fixture candidate only.",
        "Promotion preview is not promotion.",
    ],
}

_REVIEW_ITEMS: dict[str, dict[str, Any]] = {}
_DECISIONS: dict[str, dict[str, Any]] = {}
_PREVIEWS: dict[str, dict[str, Any]] = {}


def default_policy() -> dict[str, Any]:
    return {
        "review_requires_operator_token": True,
        "public_review_enabled": False,
        "native_review_enabled": False,
        "review_decision_mutates_temp_instance_only_by_default": True,
        "promotion_preview_is_not_promotion": True,
        "promotion_preview_requires_review_decision": True,
        "reviewed_index_refresh_allowed_only_temp_or_explicit_instance": True,
        "operator_instance_mutation_default": False,
        "master_index_mutation_enabled": False,
        "committed_data_public_index_mutation_enabled": False,
        "automatic_candidate_acceptance_enabled": False,
        "fake_evidence_forbidden": True,
        "fake_verified_records_forbidden": True,
        "downloads_enabled": False,
        "extraction_enabled": False,
        "model_provider_enabled": False,
        "deployment_enabled": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def load_policy(path: str | Path | None = None) -> dict[str, Any]:
    if not path:
        return default_policy()
    import json

    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    policy = default_policy()
    policy.update({key: value for key, value in payload.items() if key != "schema_version"})
    return policy


def create_review_item_from_candidate(candidate_ref: Mapping[str, Any] | str | None = None, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    candidate = normalize_candidate(candidate_ref)
    review_item_id = stable_id("review_item", {"candidate_id": candidate["candidate_id"], "source_cache_entry_id": candidate["source_cache_entry_id"]})
    review_item = {
        "schema_version": "workbench_review_item.v0",
        "review_item_id": review_item_id,
        "candidate_id": candidate["candidate_id"],
        "candidate_source": candidate["candidate_source"],
        "queue_status": "review_pending",
        "subject_kind": "candidate_record",
        "subject_id": candidate["candidate_id"],
        "evidence_id": candidate["evidence_id"],
        "source_cache_entry_id": candidate["source_cache_entry_id"],
        "summary": "Review required before local reviewed projection.",
        "candidate": candidate,
        "created_at": FIXED_CREATED_AT,
        "review_required": True,
        "accepted_truth": False,
        "allowed_decisions": list(REVIEW_DECISIONS),
        "blocked_actions": list(BLOCKED_ACTIONS),
        "limitations": [
            "Review item is local/operator scoped.",
            "Review item does not create evidence or reviewed truth.",
        ],
    }
    _REVIEW_ITEMS[review_item_id] = deepcopy(review_item)
    return review_item


def list_review_items(projection_profile: str = "operator_workbench") -> dict[str, Any]:
    profile = projection_profile_or_default(projection_profile)
    items = [project_review_flow_for_workbench(item, profile) for item in _REVIEW_ITEMS.values()]
    return {
        "schema_version": "workbench_review_item_list.v0",
        "projection_profile": profile,
        "status": "pass",
        "review_item_count": len(items),
        "review_items": items,
        "public_projection_read_only": profile != "operator_workbench",
        "warnings": [],
        "limitations": ["Process-local Workbench review preview state only."],
    }


def get_review_item(review_item_id: str, projection_profile: str = "operator_workbench") -> dict[str, Any]:
    profile = projection_profile_or_default(projection_profile)
    item = _REVIEW_ITEMS.get(review_item_id)
    return {
        "schema_version": "workbench_review_item_detail.v0",
        "projection_profile": profile,
        "status": "pass" if item else "fail",
        "found": item is not None,
        "review_item_id": review_item_id,
        "review_item": project_review_flow_for_workbench(item, profile) if item else None,
        "warnings": [] if item else ["review item not found in process-local preview state"],
        "limitations": ["Process-local Workbench review preview state only."],
    }


def record_review_decision(
    review_item_id: str,
    decision: str,
    operator_context: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    policy_record = dict(default_policy(), **dict(policy or {}))
    context = dict(operator_context or {})
    profile = projection_profile_or_default(str(context.get("projection_profile", "operator_workbench")))
    token = str(context.get("operator_token", "") or "")
    dry_run = bool(context.get("dry_run", False))
    decision = normalize_decision(decision)
    review_item = _REVIEW_ITEMS.get(review_item_id) or create_review_item_from_candidate(None, policy_record)
    allowed = profile == "operator_workbench" and (bool(token) or dry_run)
    blocked_reasons: list[str] = []
    if profile in READ_ONLY_PROJECTIONS:
        blocked_reasons.append(f"{profile} projections are read-only")
    if not token and not dry_run:
        blocked_reasons.append("operator token is required to record a review decision")
    decision_id = stable_id("review_decision", {"review_item_id": review_item_id, "decision": decision, "token": token or "dry-run"})
    record = {
        "schema_version": "workbench_review_decision.v0",
        "decision_id": decision_id,
        "review_item_id": review_item["review_item_id"],
        "candidate_id": review_item["candidate_id"],
        "decision": decision,
        "mapped_local_review_decision": map_to_local_review_decision(decision),
        "decision_status": "dry_run_review_plan" if allowed and not token else ("recorded_temp_scope" if allowed else "blocked_by_policy"),
        "allowed": allowed,
        "dry_run": dry_run,
        "operator_token_required": True,
        "operator_token_present": bool(token),
        "review_decision_recorded": bool(allowed and token),
        "automatic_candidate_acceptance_enabled": False,
        "blocked_reasons": blocked_reasons,
        "created_at": FIXED_CREATED_AT,
        "accepted_truth": False,
        "review_required": True,
        "limitations": [
            "Decision is local review state only.",
            "Promotion preview is separate and does not mutate a master or public index.",
        ],
    }
    if allowed:
        _DECISIONS[decision_id] = deepcopy(record)
    return record


def build_promotion_preview(review_decision: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    decision = normalize_decision(str(review_decision.get("decision", "")))
    review_item = _REVIEW_ITEMS.get(str(review_decision.get("review_item_id", ""))) or create_review_item_from_candidate(None, policy)
    preview_id = stable_id("promotion_preview", {"review_item_id": review_item["review_item_id"], "decision": decision})
    allowed = decision == "accept_local_reviewed" and bool(review_decision.get("allowed", False))
    preview = {
        "schema_version": "workbench_promotion_preview.v0",
        "preview_id": preview_id,
        "review_item_id": review_item["review_item_id"],
        "decision_id": review_decision.get("decision_id", ""),
        "candidate_id": review_item["candidate_id"],
        "created_at": FIXED_CREATED_AT,
        "status": "preview_available" if allowed else "blocked",
        "promotion_preview_created": allowed,
        "promotion_preview_is_not_promotion": True,
        "reviewed_local_record_preview": build_reviewed_local_record_preview(review_item),
        "evidence_summary": {
            "evidence_id": review_item["evidence_id"],
            "claim_subject": review_item["candidate"].get("claim_subject", "sampleproject"),
            "review_required": True,
        },
        "source_summary": {
            "source_id": review_item["candidate"].get("source_id", ""),
            "source_cache_entry_id": review_item["source_cache_entry_id"],
            "source_family": review_item["candidate"].get("source_family", "fixture"),
        },
        "limitations": [
            "Preview is not promotion.",
            "Reviewed local index refresh is temp/explicit-instance only.",
        ],
        "action_posture": "operator_gated_temp_refresh_only",
        "blocked_actions": list(BLOCKED_ACTIONS),
        "index_delta_preview": {
            "add_record_count": 1 if allowed else 0,
            "update_record_count": 0,
            "delete_record_count": 0,
            "master_index_mutated": False,
            "committed_data_public_index_mutated": False,
        },
        "automatic_candidate_acceptance_enabled": False,
        "accepted_truth": False,
    }
    if allowed:
        _PREVIEWS[preview_id] = deepcopy(preview)
    return preview


def build_reviewed_index_refresh_preview(promotion_preview: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    preview_allowed = bool(promotion_preview.get("promotion_preview_created"))
    record = dict(promotion_preview.get("reviewed_local_record_preview") or {})
    return {
        "schema_version": "workbench_reviewed_index_refresh_preview.v0",
        "refresh_preview_id": stable_id("reviewed_index_refresh_preview", str(promotion_preview.get("preview_id", ""))),
        "promotion_preview_id": promotion_preview.get("preview_id", ""),
        "status": "preview_available" if preview_allowed else "blocked",
        "temp_reviewed_index_delta": {"add": [record] if preview_allowed else [], "update": [], "delete": []},
        "search_result_after_refresh": build_search_result_after_refresh(record) if preview_allowed else None,
        "object_packet_after_refresh": build_object_packet_after_refresh(record) if preview_allowed else None,
        "absence_packet_after_refresh": build_absence_packet_after_refresh(record) if preview_allowed else None,
        "rollback_hint": "discard temp instance or restore pre-apply snapshot",
        "refresh_allowed_only_temp_or_explicit_instance": True,
        "operator_instance_mutated": False,
        "master_index_mutated": False,
        "committed_data_public_index_mutated": False,
        "limitations": ["Refresh preview does not write a reviewed index."],
    }


def refresh_reviewed_index_temp(
    promotion_preview: Mapping[str, Any],
    temp_instance: Any,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if not promotion_preview.get("promotion_preview_created"):
        return {
            "schema_version": "workbench_reviewed_index_refresh_temp_result.v0",
            "status": "blocked",
            "temp_reviewed_index_refresh_passed": False,
            "blocked_reasons": ["promotion preview is not available"],
            **boundary_flags(),
        }
    runtime = temp_instance
    candidate = candidate_from_promotion_preview(promotion_preview)
    seed = seed_temp_review_records(runtime, candidate)
    decision = record_local_review_decision(runtime, seed["review_item_id"], "accept", None, "workbench_review_promote", True)
    refresh = rebuild_reviewed_index(runtime, operator_label="workbench_review_promote", dry_run=False)
    query = candidate.get("claim_subject", "sampleproject")
    search_results = [item.to_dict() for item in runtime.public_index.search(query, limit=10)]
    return {
        "schema_version": "workbench_reviewed_index_refresh_temp_result.v0",
        "status": "pass",
        "review_decision": decision,
        "reviewed_index_refresh": refresh,
        "review_item_id": seed["review_item_id"],
        "temp_reviewed_index_refresh_passed": bool(refresh.get("included_count", 0) >= 1),
        "temp_search_after_refresh_passed": bool(search_results),
        "search_results": search_results,
        "temp_instance_scope": "explicit_test_temp_instance",
        "operator_instance_mutated": False,
        "master_index_mutated": False,
        "committed_data_public_index_mutated": False,
        "rollback_hint": "discard temp instance",
        **boundary_flags(),
    }


def project_review_flow_for_workbench(record: Mapping[str, Any] | None, projection_profile: str = "operator_workbench") -> dict[str, Any] | None:
    if record is None:
        return None
    profile = projection_profile_or_default(projection_profile)
    projected = deepcopy(dict(record))
    projected["projection_profile"] = profile
    projected["read_only"] = profile in READ_ONLY_PROJECTIONS
    if profile in READ_ONLY_PROJECTIONS:
        projected["allowed_decisions"] = []
        projected["operator_controls_visible"] = False
        projected["blocked_reasons"] = [f"{profile} projection is read-only"]
    else:
        projected["operator_controls_visible"] = True
    return projected


def build_review_promote_boundary_report(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "workbench_review_promote_boundary_report.v0",
        "review_flow_is_operator_gated": True,
        "promotion_preview_is_not_promotion": True,
        "reviewed_local_index_is_not_master_truth": True,
        "temp_instance_refresh_allowed": True,
        "automatic_candidate_acceptance_enabled": False,
        "fake_evidence_created": False,
        "fake_verified_records_created": False,
        "operator_instance_mutated": False,
        "master_index_mutated": False,
        "committed_data_public_index_mutated": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "result_status": result.get("status", "unknown"),
    }


def run_review_promote_flow(
    *,
    candidate: Mapping[str, Any] | str | None = None,
    decision: str = "accept_local_reviewed",
    projection_profile: str = "operator_workbench",
    operator_token: str = "",
    dry_run: bool = True,
    runtime: Any | None = None,
    apply_to_temp: bool = False,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    profile = projection_profile_or_default(projection_profile)
    review_item = create_review_item_from_candidate(candidate, policy)
    decision_record = record_review_decision(
        review_item["review_item_id"],
        decision,
        {
            "projection_profile": profile,
            "operator_token": operator_token,
            "dry_run": bool(dry_run),
        },
        policy,
    )
    preview = build_promotion_preview(decision_record, policy)
    refresh_preview = build_reviewed_index_refresh_preview(preview, policy)
    temp_result: dict[str, Any] | None = None
    if apply_to_temp:
        if profile != "operator_workbench":
            temp_result = {
                "schema_version": "workbench_reviewed_index_refresh_temp_result.v0",
                "status": "blocked",
                "blocked_reasons": [f"{profile} projection cannot refresh reviewed index"],
                "temp_reviewed_index_refresh_passed": False,
                "temp_search_after_refresh_passed": False,
                **boundary_flags(),
            }
        elif not operator_token:
            temp_result = {
                "schema_version": "workbench_reviewed_index_refresh_temp_result.v0",
                "status": "blocked",
                "blocked_reasons": ["operator token is required for temp refresh"],
                "temp_reviewed_index_refresh_passed": False,
                "temp_search_after_refresh_passed": False,
                **boundary_flags(),
            }
        elif runtime is None:
            temp_result = {
                "schema_version": "workbench_reviewed_index_refresh_temp_result.v0",
                "status": "blocked",
                "blocked_reasons": ["explicit temp runtime is required for apply-to-temp"],
                "temp_reviewed_index_refresh_passed": False,
                "temp_search_after_refresh_passed": False,
                **boundary_flags(),
            }
        else:
            temp_result = refresh_reviewed_index_temp(preview, runtime, policy)
    result = {
        "schema_version": "workbench_review_promote_flow.v0",
        "status": "pass",
        "projection_profile": profile,
        "review_item": project_review_flow_for_workbench(review_item, profile),
        "review_decision": project_review_flow_for_workbench(decision_record, profile),
        "promotion_preview": project_review_flow_for_workbench(preview, profile),
        "reviewed_index_refresh_preview": project_review_flow_for_workbench(refresh_preview, profile),
        "reviewed_index_refresh_temp_result": temp_result,
        "events": build_review_promote_events(review_item, decision_record, preview, temp_result),
        "review_item_created": True,
        "operator_token_required": True,
        "public_projection_blocked": profile == "public_web",
        "native_read_only_projection_blocked": profile == "native_desktop_read_only",
        "promotion_preview_created": bool(preview.get("promotion_preview_created")),
        "temp_reviewed_index_refresh_passed": bool(temp_result and temp_result.get("temp_reviewed_index_refresh_passed")),
        "temp_search_after_refresh_passed": bool(temp_result and temp_result.get("temp_search_after_refresh_passed")),
        "warnings": [],
        "limitations": [
            "Promotion preview is not promotion.",
            "Reviewed local index refresh is temp/explicit-instance only.",
        ],
    }
    result["boundary_report"] = build_review_promote_boundary_report(result)
    result.update(boundary_flags())
    return result


def seed_temp_review_records(runtime: Any, candidate_ref: Mapping[str, Any] | None = None) -> dict[str, str]:
    candidate = normalize_candidate(candidate_ref)
    cache = SourceCacheEntry(
        entry_id=candidate["source_cache_entry_id"],
        source_id=candidate["source_id"],
        source_family=candidate.get("source_family", "fixture"),
        trust_lane="workbench_review_promote",
        request_id=stable_id("request", candidate["candidate_id"]),
        response_id=stable_id("response", candidate["candidate_id"]),
        observation_id=stable_id("observation", candidate["candidate_id"]),
        normalized_observation_id=stable_id("normalized", candidate["candidate_id"]),
        response_fingerprint="sha256:" + stable_id("response", candidate["candidate_id"]),
        status=SourceCacheStatus.CACHED,
        payload={
            "normalized_observation": {
                "normalized_fields": {
                    "title": candidate["title"],
                    "description": candidate["summary"],
                    "domain_id": candidate.get("domain_id", "legacy_software"),
                }
            }
        },
        limitations=("workbench review/promote temp fixture",),
    )
    evidence = EvidenceCandidateRecord(
        evidence_id=candidate["evidence_id"],
        source_id=cache.source_id,
        source_cache_entry_id=cache.entry_id,
        observation_id=cache.observation_id,
        normalized_observation_id=cache.normalized_observation_id,
        claim_kind="metadata_claim",
        claim_subject=candidate.get("claim_subject", "sampleproject"),
        claim_payload={
            "normalized_fields": {
                "title": candidate["title"],
                "description": candidate["summary"],
                "domain_id": candidate.get("domain_id", "legacy_software"),
            }
        },
        status=EvidenceReviewStatus.NEEDS_REVIEW,
        limitations=("workbench review/promote temp fixture",),
    )
    review = ReviewItemRecord(
        review_item_id=stable_id("review_item_temp", candidate["candidate_id"]),
        subject_kind="evidence_candidate",
        subject_id=evidence.evidence_id,
        queue_status=ReviewQueueStatus.NEEDS_REVIEW,
        evidence_id=evidence.evidence_id,
        source_cache_entry_id=cache.entry_id,
        summary="Review temp candidate for Workbench promotion preview.",
    )
    runtime.source_cache.write_cache_entry(cache)
    runtime.evidence_ledger.write_evidence_candidate(evidence)
    runtime.review_queue.enqueue_review_item(review)
    return {
        "source_cache_entry_id": cache.entry_id,
        "evidence_id": evidence.evidence_id,
        "review_item_id": review.review_item_id,
    }


def build_reviewed_local_record_preview(review_item: Mapping[str, Any]) -> dict[str, Any]:
    candidate = dict(review_item.get("candidate") or {})
    return {
        "record_id": stable_id("reviewed_local", review_item["review_item_id"]),
        "title": candidate.get("title", "SampleProject candidate"),
        "summary": candidate.get("summary", ""),
        "source_id": candidate.get("source_id", ""),
        "source_cache_entry_id": review_item.get("source_cache_entry_id", ""),
        "evidence_id": review_item.get("evidence_id", ""),
        "review_item_id": review_item.get("review_item_id", ""),
        "truth_level": "reviewed_local_not_master_public_truth",
        "accepted_truth": False,
        "review_required": False,
        "created_at": FIXED_CREATED_AT,
    }


def build_search_result_after_refresh(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "workbench_reviewed_search_result_preview.v0",
        "query": str(record.get("title", "sampleproject")).lower(),
        "result_count": 1,
        "results": [
            {
                "record_id": record.get("record_id", ""),
                "title": record.get("title", ""),
                "summary": record.get("summary", ""),
                "truth_level": record.get("truth_level", "reviewed_local_not_master_public_truth"),
            }
        ],
    }


def build_object_packet_after_refresh(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "workbench_reviewed_object_packet_preview.v0",
        "object_id": record.get("record_id", ""),
        "title": record.get("title", ""),
        "source_refs": [record.get("source_cache_entry_id", "")],
        "evidence_refs": [record.get("evidence_id", "")],
        "review_refs": [record.get("review_item_id", "")],
        "accepted_truth": False,
    }


def build_absence_packet_after_refresh(record: Mapping[str, Any]) -> dict[str, Any]:
    packet = build_absence_report(
        str(record.get("title", "sampleproject")),
        result_count=1,
        checked_sources=("temp_reviewed_index",),
    ).to_dict()
    packet["created_at"] = FIXED_CREATED_AT
    return packet


def build_review_promote_events(
    review_item: Mapping[str, Any],
    decision: Mapping[str, Any],
    preview: Mapping[str, Any],
    temp_result: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    events = [
        event("review.item_created", review_item["review_item_id"], {"candidate_id": review_item["candidate_id"]}),
        event("review.decision_proposed", review_item["review_item_id"], {"decision": decision.get("decision")}),
    ]
    if decision.get("review_decision_recorded"):
        events.append(event("review.decision_recorded", review_item["review_item_id"], {"decision_id": decision.get("decision_id")}))
    if preview.get("promotion_preview_created"):
        events.append(event("promotion.preview_created", review_item["review_item_id"], {"preview_id": preview.get("preview_id")}))
        events.append(event("reviewed_index.refresh_preview_created", review_item["review_item_id"], {"preview_id": preview.get("preview_id")}))
    else:
        events.append(event("promotion.preview_blocked", review_item["review_item_id"], {"status": preview.get("status")}))
    if temp_result and temp_result.get("temp_reviewed_index_refresh_passed"):
        events.append(event("reviewed_index.refresh_completed_temp", review_item["review_item_id"], {"status": "pass"}))
    if decision.get("blocked_reasons"):
        events.append(event("action.blocked", review_item["review_item_id"], {"blocked_reasons": decision.get("blocked_reasons")}))
    return events


def event(event_type: str, subject_id: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "workbench_review_promote_event.v0",
        "event_id": stable_id("event", {"event_type": event_type, "subject_id": subject_id, "payload": dict(payload)}),
        "event_type": event_type,
        "subject_id": subject_id,
        "created_at": FIXED_CREATED_AT,
        "payload": dict(payload),
    }


def normalize_candidate(candidate_ref: Mapping[str, Any] | str | None) -> dict[str, Any]:
    if isinstance(candidate_ref, Mapping):
        candidate = dict(SAMPLE_CANDIDATE)
        candidate.update(dict(candidate_ref))
    elif candidate_ref:
        candidate = dict(SAMPLE_CANDIDATE)
        candidate["candidate_id"] = str(candidate_ref)
    else:
        candidate = dict(SAMPLE_CANDIDATE)
    candidate.setdefault("source_cache_entry_id", stable_id("source_cache", candidate["candidate_id"]))
    candidate.setdefault("evidence_id", stable_id("evidence", candidate["candidate_id"]))
    candidate.setdefault("source_id", "source.fixture.workbench_review")
    candidate.setdefault("title", "SampleProject candidate")
    candidate.setdefault("summary", "Fixture candidate for Workbench review/promotion preview.")
    candidate.setdefault("candidate_source", "local_candidate_results")
    candidate.setdefault("claim_subject", "sampleproject")
    candidate["accepted_truth"] = False
    candidate["review_required"] = True
    return candidate


def candidate_from_promotion_preview(promotion_preview: Mapping[str, Any]) -> dict[str, Any]:
    record = dict(promotion_preview.get("reviewed_local_record_preview") or {})
    candidate = dict(SAMPLE_CANDIDATE)
    candidate.update(
        {
            "candidate_id": str(promotion_preview.get("candidate_id") or candidate["candidate_id"]),
            "title": str(record.get("title") or candidate["title"]),
            "summary": str(record.get("summary") or candidate["summary"]),
            "source_cache_entry_id": str(record.get("source_cache_entry_id") or candidate["source_cache_entry_id"]),
            "evidence_id": str(record.get("evidence_id") or candidate["evidence_id"]),
            "claim_subject": "sampleproject",
        }
    )
    return candidate


def normalize_decision(decision: str) -> str:
    if decision == "accept":
        decision = "accept_local_reviewed"
    if decision not in REVIEW_DECISIONS:
        return "defer"
    return decision


def map_to_local_review_decision(decision: str) -> str:
    return {
        "accept_local_reviewed": "accept",
        "reject_wrong_object": "reject",
        "reject_wrong_version": "reject",
        "reject_wrong_platform": "reject",
        "needs_more_evidence": "request_more_evidence",
        "duplicate": "note_only",
        "unsafe": "block",
        "rights_risk": "block",
        "defer": "note_only",
    }[normalize_decision(decision)]


def projection_profile_or_default(profile: str) -> str:
    return profile if profile in PROJECTION_PROFILES else "operator_workbench"


def boundary_flags() -> dict[str, bool]:
    return {
        "automatic_candidate_acceptance_enabled": False,
        "fake_evidence_created": False,
        "fake_verified_records_created": False,
        "operator_instance_mutated": False,
        "master_index_mutated": False,
        "committed_data_public_index_mutated": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }

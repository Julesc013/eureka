"""Deterministic candidate index runtime.

Candidates are review-only memory. This module intentionally does not mutate
reviewed indexes, public indexes, operator instances, or accepted truth.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping, Sequence


SCHEMA_VERSION = "candidate_index_runtime.v0"
DEFAULT_TIMESTAMP = "2026-05-30T00:00:00Z"
DEFAULT_POLICY: dict[str, Any] = {
    "candidates_are_not_truth": True,
    "candidate_index_is_not_reviewed_index": True,
    "candidate_persistence_operator_or_temp_only": True,
    "public_candidate_mutation_enabled": False,
    "automatic_candidate_acceptance_enabled": False,
    "reviewed_index_mutation_enabled": False,
    "master_index_mutation_enabled": False,
    "accepted_truth_created": False,
    "review_required_for_promotion": True,
    "downloads_enabled": False,
    "extraction_enabled": False,
    "model_provider_enabled": False,
    "deployment_enabled": False,
}

CANDIDATE_STATES = (
    "new",
    "seen",
    "useful_lead",
    "needs_review",
    "review_item_created",
    "rejected_wrong_object",
    "rejected_wrong_version",
    "rejected_wrong_platform",
    "rejected_low_quality",
    "duplicate",
    "blocked",
    "accepted_local_reviewed",
)

AUTOMATIC_TRANSITIONS = {
    ("new", "seen"),
    ("seen", "duplicate"),
    ("seen", "needs_review"),
    ("needs_review", "review_item_created"),
}

OPERATOR_TRANSITIONS = {
    ("needs_review", "useful_lead"),
    ("needs_review", "rejected_wrong_object"),
    ("needs_review", "rejected_wrong_version"),
    ("needs_review", "rejected_wrong_platform"),
    ("needs_review", "rejected_low_quality"),
    ("needs_review", "blocked"),
    ("review_item_created", "accepted_local_reviewed"),
}

CANDIDATE_KINDS = (
    "source_metadata_candidate",
    "artifact_candidate",
    "source_lead",
    "provenance_lead",
    "near_miss",
    "collection_candidate",
    "file_manifest_candidate",
    "review_seed",
)


def normalize_candidate(
    raw_candidate: Mapping[str, Any],
    query_plan: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Normalize any bounded source candidate into a CandidateRecord."""

    merged_policy = _policy(policy)
    _assert_non_claim_policy(merged_policy)
    plan = query_plan if isinstance(query_plan, Mapping) else {}
    source_locator = _source_locator(raw_candidate)
    title = _first_text(
        raw_candidate.get("title"),
        raw_candidate.get("candidate_title"),
        raw_candidate.get("name"),
        _locator_text(source_locator),
        "Untitled candidate",
    )
    candidate_id = _first_text(raw_candidate.get("candidate_id"), "")
    if not candidate_id:
        candidate_id = _stable_id("candidate", title, source_locator, plan.get("plan_id"))
    review_state = _first_text(
        raw_candidate.get("review_state"),
        raw_candidate.get("candidate_status"),
        "needs_review",
    )
    if review_state not in CANDIDATE_STATES:
        review_state = "needs_review"
    candidate_kind = _candidate_kind(raw_candidate)
    source_family = _first_text(
        raw_candidate.get("source_family"),
        raw_candidate.get("source_id"),
        "unknown_source_family",
    )
    matched_query = _first_text(
        raw_candidate.get("matched_query"),
        raw_candidate.get("query"),
        plan.get("normalized_query"),
        plan.get("raw_query"),
        "",
    )
    domain_id = _first_text(
        raw_candidate.get("domain_id"),
        raw_candidate.get("domain_pack"),
        plan.get("domain_pack"),
        "general_archive_metadata",
    )
    candidate = {
        "schema_version": "candidate_record.v0",
        "candidate_id": candidate_id,
        "candidate_kind": candidate_kind,
        "source_family": source_family,
        "source_locator": source_locator,
        "title": title,
        "description": _first_text(
            raw_candidate.get("description"),
            raw_candidate.get("candidate_summary"),
            raw_candidate.get("summary"),
            "Review-only source candidate.",
        ),
        "matched_query": matched_query,
        "query_plan_ref": _first_text(raw_candidate.get("query_plan_ref"), plan.get("plan_id"), ""),
        "source_action_ref": _source_action_ref(raw_candidate, plan),
        "source_observation_ref": _first_text(
            raw_candidate.get("source_observation_ref"),
            raw_candidate.get("observation_id"),
            "",
        ),
        "evidence_candidate_refs": _text_list(raw_candidate.get("evidence_candidate_refs")),
        "domain_id": domain_id,
        "confidence_label": _first_text(raw_candidate.get("confidence_label"), "medium"),
        "match_reasons": _match_reasons(raw_candidate, plan),
        "suppressions": _suppressions(raw_candidate, plan),
        "limitations": _limitations(raw_candidate),
        "action_posture": _action_posture(raw_candidate),
        "review_state": review_state,
        "accepted_truth": False,
        "reviewed_record_ref": None,
        "created_at": _first_text(raw_candidate.get("created_at"), DEFAULT_TIMESTAMP),
        "updated_at": _first_text(raw_candidate.get("updated_at"), DEFAULT_TIMESTAMP),
    }
    fingerprint = build_candidate_fingerprint(candidate, merged_policy)
    candidate["fingerprint"] = fingerprint
    candidate["dedupe_key"] = fingerprint["dedupe_key"]
    return candidate


def archive_org_candidate_to_record(
    raw_candidate: Mapping[str, Any],
    query_plan: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Map an Archive.org metadata candidate into a CandidateRecord."""

    shaped = dict(raw_candidate)
    shaped.setdefault("candidate_kind", "source_metadata_candidate")
    shaped.setdefault("source_family", "internet_archive")
    shaped.setdefault("confidence_label", "medium")
    shaped.setdefault("match_reasons", ["archive_org_metadata_match"])
    shaped.setdefault("limitations", [])
    shaped.setdefault("action_posture", {})
    return normalize_candidate(shaped, query_plan, policy)


def build_candidate_fingerprint(
    candidate: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_non_claim_policy(merged_policy)
    locator = _source_locator(candidate)
    normalized_title = _normalize_text(_first_text(candidate.get("title"), candidate.get("candidate_title"), ""))
    source_family = _first_text(candidate.get("source_family"), "unknown_source_family")
    source_locator = _locator_text(locator)
    domain_id = _first_text(candidate.get("domain_id"), candidate.get("domain_pack"), "")
    object_hint = _object_hint(candidate)
    version_hint = _version_hint(candidate)
    platform_hint = _platform_hint(candidate)
    checksum_hint = _checksum_hint(candidate)
    dedupe_parts = {
        "normalized_title": normalized_title,
        "source_family": source_family,
        "source_locator": source_locator,
        "domain_id": domain_id,
        "object_hint": object_hint,
        "version_hint": version_hint,
        "platform_hint": platform_hint,
        "checksum_hint": checksum_hint,
    }
    dedupe_key = hashlib.sha256(
        json.dumps(dedupe_parts, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:24]
    candidate_id = _first_text(candidate.get("candidate_id"), "")
    return {
        "schema_version": "candidate_fingerprint.v0",
        "fingerprint_id": f"candidate-fingerprint:{dedupe_key}",
        "candidate_id": candidate_id,
        "normalized_title": normalized_title,
        "source_family": source_family,
        "source_locator": source_locator,
        "domain_id": domain_id,
        "object_hint": object_hint,
        "version_hint": version_hint,
        "platform_hint": platform_hint,
        "checksum_hint": checksum_hint,
        "dedupe_key": dedupe_key,
        "collision_notes": [],
    }


def dedupe_candidates(
    candidates: Sequence[Mapping[str, Any]],
    existing_candidates: Sequence[Mapping[str, Any]] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_non_claim_policy(merged_policy)
    existing = [dict(item) for item in existing_candidates or []]
    normalized = [
        dict(item) if item.get("schema_version") == "candidate_record.v0" else normalize_candidate(item, {}, merged_policy)
        for item in candidates
    ]
    seen: dict[str, str] = {}
    for item in existing:
        key = _dedupe_key(item, merged_policy)
        if key:
            seen[key] = _first_text(item.get("candidate_id"), "")
    unique: list[dict[str, Any]] = []
    duplicates: list[dict[str, Any]] = []
    for candidate in normalized:
        key = _dedupe_key(candidate, merged_policy)
        if key in seen:
            duplicate = _clone(candidate)
            duplicate["dedupe_status"] = "duplicate"
            duplicate["duplicate_of_candidate_id"] = seen[key]
            duplicate["review_state"] = "duplicate"
            duplicates.append(duplicate)
        else:
            candidate["dedupe_status"] = "unique"
            seen[key] = candidate["candidate_id"]
            unique.append(candidate)
    return {
        "schema_version": "candidate_deduplication_result.v0",
        "unique_candidates": unique,
        "duplicate_candidates": duplicates,
        "unique_count": len(unique),
        "duplicate_count": len(duplicates),
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
    }


def build_candidate_index_write_plan(
    candidate: Mapping[str, Any],
    target: str,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_non_claim_policy(merged_policy)
    normalized = (
        dict(candidate)
        if candidate.get("schema_version") == "candidate_record.v0"
        else normalize_candidate(candidate, {}, merged_policy)
    )
    target_name = _first_text(target, "temp_store")
    write_allowed = target_name in {"temp_store", "operator_local_candidate_index"}
    return {
        "schema_version": "candidate_index_write_plan.v0",
        "plan_id": _stable_id("candidate_write_plan", normalized["candidate_id"], target_name),
        "candidate_id": normalized["candidate_id"],
        "target": target_name,
        "write_allowed": write_allowed,
        "write_applied": False,
        "requires_explicit_apply": True,
        "candidate_record": normalized,
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "operator_instance_mutated": False,
        "public_mutation_enabled": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
    }


def apply_candidate_index_write_plan_temp(
    write_plan: Mapping[str, Any],
    temp_store: MutableMapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_non_claim_policy(merged_policy)
    if write_plan.get("target") != "temp_store":
        raise ValueError("candidate temp apply only accepts target=temp_store")
    if not bool(write_plan.get("write_allowed")):
        raise ValueError("candidate write plan is not allowed")
    candidate = dict(write_plan.get("candidate_record") or {})
    if candidate.get("schema_version") != "candidate_record.v0":
        candidate = normalize_candidate(candidate, {}, merged_policy)
    candidates = [dict(item) for item in temp_store.get("candidates", []) if isinstance(item, Mapping)]
    existing_by_id = {_first_text(item.get("candidate_id"), ""): item for item in candidates}
    existing_by_id[candidate["candidate_id"]] = candidate
    stored = sorted(existing_by_id.values(), key=lambda item: _first_text(item.get("candidate_id"), ""))
    temp_store.clear()
    temp_store.update(
        {
            "schema_version": "candidate_index_snapshot.v0",
            "store_mode": "temp_store",
            "candidates": stored,
            "candidate_count": len(stored),
            "accepted_truth_created": False,
            "reviewed_index_mutated": False,
            "master_index_mutated": False,
            "public_index_mutated": False,
            "operator_instance_mutated": False,
        }
    )
    return {
        "schema_version": "candidate_index_write_result.v0",
        "write_applied": True,
        "candidate_id": candidate["candidate_id"],
        "candidate_count": len(stored),
        "store": _clone(temp_store),
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "operator_instance_mutated": False,
    }


def search_candidates(
    query: str,
    candidate_index: Mapping[str, Any] | Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_non_claim_policy(merged_policy)
    normalized_query = " ".join(str(query or "").split())
    query_terms = _tokens(normalized_query)
    candidates = _candidate_list(candidate_index)
    scored: list[tuple[int, dict[str, Any]]] = []
    for candidate in candidates:
        haystack = " ".join(
            [
                _first_text(candidate.get("title"), ""),
                _first_text(candidate.get("description"), ""),
                _locator_text(_source_locator(candidate)),
                _first_text(candidate.get("domain_id"), ""),
                " ".join(_text_list(candidate.get("match_reasons"))),
            ]
        ).casefold()
        if not query_terms:
            score = 1
        else:
            score = sum(1 for term in query_terms if term in haystack)
        if score > 0:
            result = _public_candidate_summary(candidate)
            result["match_score"] = score
            result["matched_terms"] = [term for term in query_terms if term in haystack]
            scored.append((score, result))
    scored.sort(key=lambda item: (-item[0], item[1]["candidate_id"]))
    results = [item for _, item in scored]
    return {
        "schema_version": "candidate_search_result.v0",
        "query": normalized_query,
        "result_count": len(results),
        "results": results,
        "accepted_truth": False,
        "review_required": True,
        "public_mutation_enabled": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
    }


def build_candidate_lane_packet(
    search_results: Mapping[str, Any],
    projection_profile: str,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_non_claim_policy(merged_policy)
    profile = _first_text(projection_profile, "public_web")
    public_profile = profile == "public_web"
    allowed_actions = ["inspect", "view_source", "view_provenance", "read"]
    future_gated_actions = ["create_review_handoff", "update_candidate_state"]
    if not public_profile:
        allowed_actions.append("create_review_handoff")
    return {
        "schema_version": "candidate_lane_packet.v0",
        "lane_id": "candidate_results",
        "projection_profile": profile,
        "truth_status": "candidate_only",
        "review_required": True,
        "accepted_truth": False,
        "candidate_count": int(search_results.get("result_count") or 0),
        "candidates": [dict(item) for item in search_results.get("results", []) if isinstance(item, Mapping)],
        "allowed_actions": allowed_actions,
        "blocked_actions": ["accept", "reject", "promote", "download", "extract", "execute", "install_handoff", "upload"],
        "future_gated_actions": future_gated_actions,
        "public_mutation_enabled": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "limitations": [
            "candidate_not_reviewed_truth",
            "review_required_for_promotion",
            "public_read_only_projection",
            "no_download",
            "no_extraction",
            "no_auto_promotion",
        ],
    }


def update_candidate_state(
    candidate_id: str,
    new_state: str,
    actor_context: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_non_claim_policy(merged_policy)
    if new_state not in CANDIDATE_STATES:
        raise ValueError(f"unknown candidate state: {new_state}")
    actor_type = _first_text(actor_context.get("actor_type"), "public")
    if actor_type == "public":
        raise PermissionError("public candidate mutation is disabled")
    old_state = _first_text(actor_context.get("current_state"), "needs_review")
    transition = (old_state, new_state)
    operator_approved = bool(actor_context.get("operator_approved"))
    automatic_actor = actor_type in {"system", "runtime"}
    if automatic_actor and transition not in AUTOMATIC_TRANSITIONS:
        raise PermissionError(f"automatic transition blocked: {old_state}->{new_state}")
    if actor_type == "operator" and (not operator_approved or transition not in OPERATOR_TRANSITIONS):
        raise PermissionError(f"operator transition blocked: {old_state}->{new_state}")
    return {
        "schema_version": "candidate_state_transition_result.v0",
        "candidate_id": str(candidate_id),
        "old_state": old_state,
        "new_state": new_state,
        "actor_type": actor_type,
        "transition_allowed": True,
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_mutation_enabled": False,
    }


def build_candidate_review_handoff(
    candidate: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_non_claim_policy(merged_policy)
    normalized = (
        dict(candidate)
        if candidate.get("schema_version") == "candidate_record.v0"
        else normalize_candidate(candidate, {}, merged_policy)
    )
    return {
        "schema_version": "candidate_review_handoff.v0",
        "handoff_id": _stable_id("candidate_review_handoff", normalized["candidate_id"]),
        "candidate_id": normalized["candidate_id"],
        "review_state": normalized.get("review_state", "needs_review"),
        "recommended_review_action": "create_review_item",
        "review_required": True,
        "accepted_truth": False,
        "reviewed_record_ref": None,
        "candidate_summary": _public_candidate_summary(normalized),
        "allowed_operator_actions": [
            "mark_useful_lead",
            "reject_wrong_object",
            "reject_wrong_version",
            "reject_wrong_platform",
            "reject_low_quality",
            "block",
            "create_review_item",
        ],
        "blocked_public_actions": ["accept", "reject", "promote", "update_state"],
        "promotion_requires_review": True,
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_mutation_enabled": False,
    }


def build_candidate_boundary_report(
    operation: str,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    return {
        "schema_version": "candidate_boundary_report.v0",
        "operation": str(operation or "candidate_index_runtime"),
        "candidates_are_not_truth": bool(merged_policy.get("candidates_are_not_truth", True)),
        "candidate_index_is_not_reviewed_index": bool(
            merged_policy.get("candidate_index_is_not_reviewed_index", True)
        ),
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "public_mutation_enabled": False,
        "operator_instance_mutated": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def sample_archive_org_candidate(query: str = "New York 1993 D-Theater HD demo tape original source") -> dict[str, Any]:
    return {
        "schema_version": "archive_org_metadata_candidate.v0",
        "candidate_id": "archive_org_dtheater_candidate",
        "candidate_status": "needs_review",
        "candidate_type": "archive_org_item_metadata_candidate",
        "candidate_title": "New York 1993 D-Theater HD demo tape source lead",
        "candidate_summary": "Archive.org metadata candidate for a frontier-resolution D-Theater source lead.",
        "identifier": "new_york_1993_dtheater_demo_fixture",
        "source_locator": {
            "locator_kind": "archive_org_details_page",
            "url": "https://archive.org/details/new_york_1993_dtheater_demo_fixture",
        },
        "source_family": "internet_archive",
        "matched_query": query,
        "accepted_truth": False,
        "review_required": True,
        "download_performed": False,
        "extraction_executed": False,
    }


def sample_candidate_index() -> dict[str, Any]:
    examples = load_candidates_from_examples()
    if examples:
        candidates = examples
    else:
        candidates = [normalize_candidate(sample_archive_org_candidate(), {}, DEFAULT_POLICY)]
    return {
        "schema_version": "candidate_index_snapshot.v0",
        "store_mode": "example_fixture",
        "candidate_count": len(candidates),
        "candidates": candidates,
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
    }


def load_candidates_from_examples(root: Path | None = None) -> list[dict[str, Any]]:
    base = root or Path(__file__).resolve().parents[2] / "examples" / "candidates"
    if not base.exists():
        return []
    candidates: list[dict[str, Any]] = []
    for path in sorted(base.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, Mapping):
            if payload.get("schema_version") == "candidate_record.v0":
                candidates.append(dict(payload))
            else:
                candidates.append(normalize_candidate(payload, {}, DEFAULT_POLICY))
    return candidates


def _candidate_list(candidate_index: Mapping[str, Any] | Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(candidate_index, Mapping):
        values = candidate_index.get("candidates", [])
    else:
        values = candidate_index
    return [dict(item) for item in values if isinstance(item, Mapping)]


def _public_candidate_summary(candidate: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "candidate_summary.v0",
        "candidate_id": _first_text(candidate.get("candidate_id"), ""),
        "candidate_kind": _first_text(candidate.get("candidate_kind"), ""),
        "source_family": _first_text(candidate.get("source_family"), ""),
        "source_locator": _source_locator(candidate),
        "title": _first_text(candidate.get("title"), ""),
        "description": _first_text(candidate.get("description"), ""),
        "domain_id": _first_text(candidate.get("domain_id"), ""),
        "confidence_label": _first_text(candidate.get("confidence_label"), ""),
        "match_reasons": _text_list(candidate.get("match_reasons")),
        "suppressions": _text_list(candidate.get("suppressions")),
        "limitations": _text_list(candidate.get("limitations")),
        "action_posture": dict(candidate.get("action_posture") or {}),
        "review_state": _first_text(candidate.get("review_state"), "needs_review"),
        "accepted_truth": False,
        "review_required": True,
        "reviewed_record_ref": None,
    }


def _source_locator(value: Mapping[str, Any]) -> dict[str, Any]:
    locator = value.get("source_locator")
    if isinstance(locator, Mapping):
        return {str(key): _clone_scalar(item) for key, item in locator.items()}
    identifier = _first_text(value.get("identifier"), value.get("source_identifier"), "")
    if identifier:
        return {
            "locator_kind": "archive_org_details_page",
            "identifier": identifier,
            "url": f"https://archive.org/details/{identifier}",
        }
    return {"locator_kind": "unknown", "value": ""}


def _source_action_ref(raw_candidate: Mapping[str, Any], query_plan: Mapping[str, Any]) -> str:
    direct = _first_text(raw_candidate.get("source_action_ref"), "")
    if direct:
        return direct
    source_family = _first_text(raw_candidate.get("source_family"), raw_candidate.get("source_id"), "")
    for index, action in enumerate(query_plan.get("source_actions", []) or []):
        if isinstance(action, Mapping) and _first_text(action.get("source_family"), "") == source_family:
            return _stable_id("source_action", query_plan.get("plan_id"), source_family, index)
    if source_family:
        return _stable_id("source_action", query_plan.get("plan_id"), source_family)
    return ""


def _candidate_kind(raw_candidate: Mapping[str, Any]) -> str:
    value = _first_text(raw_candidate.get("candidate_kind"), raw_candidate.get("candidate_type"), "")
    if value in CANDIDATE_KINDS:
        return value
    if value == "archive_org_item_metadata_candidate":
        return "source_metadata_candidate"
    return "source_metadata_candidate"


def _match_reasons(raw_candidate: Mapping[str, Any], query_plan: Mapping[str, Any]) -> list[str]:
    direct = _text_list(raw_candidate.get("match_reasons"))
    if direct:
        return direct
    reasons = _text_list(query_plan.get("intent_reasons"))
    source_family = _first_text(raw_candidate.get("source_family"), raw_candidate.get("source_id"), "")
    if source_family:
        reasons.append(f"{source_family}_candidate")
    return reasons or ["candidate_source_match"]


def _suppressions(raw_candidate: Mapping[str, Any], query_plan: Mapping[str, Any]) -> list[str]:
    direct = _text_list(raw_candidate.get("suppressions"))
    if direct:
        return direct
    suppressions: list[str] = []
    for item in query_plan.get("candidate_suppressions", []) or []:
        if isinstance(item, Mapping):
            suppressions.append(_first_text(item.get("suppression_id"), "candidate_suppression"))
    return suppressions


def _limitations(raw_candidate: Mapping[str, Any]) -> list[str]:
    values = _text_list(raw_candidate.get("limitations"))
    for item in (
        "candidate_not_reviewed_truth",
        "review_required_for_promotion",
        "no_download",
        "no_extraction",
        "no_auto_promotion",
    ):
        if item not in values:
            values.append(item)
    return values


def _action_posture(raw_candidate: Mapping[str, Any]) -> dict[str, Any]:
    posture = raw_candidate.get("action_posture")
    if isinstance(posture, Mapping):
        result = dict(posture)
    else:
        result = {}
    result.update(
        {
            "allowed_actions": ["inspect", "view_source", "view_provenance", "read"],
            "blocked_actions": ["download", "install_handoff", "execute", "upload", "extract", "promote"],
            "future_gated_actions": ["create_review_handoff", "update_candidate_state"],
            "public_mutation_enabled": False,
            "accepted_truth": False,
        }
    )
    return result


def _dedupe_key(candidate: Mapping[str, Any], policy: Mapping[str, Any]) -> str:
    direct = _first_text(candidate.get("dedupe_key"), "")
    if direct:
        return direct
    fingerprint = candidate.get("fingerprint")
    if isinstance(fingerprint, Mapping):
        direct = _first_text(fingerprint.get("dedupe_key"), "")
        if direct:
            return direct
    return build_candidate_fingerprint(candidate, policy)["dedupe_key"]


def _object_hint(candidate: Mapping[str, Any]) -> str:
    return _normalize_text(
        _first_text(candidate.get("object_hint"), candidate.get("title"), candidate.get("candidate_title"), "")
    )


def _version_hint(candidate: Mapping[str, Any]) -> str:
    text = " ".join(
        [
            _first_text(candidate.get("version_hint"), ""),
            _first_text(candidate.get("title"), ""),
            _first_text(candidate.get("description"), ""),
        ]
    )
    match = re.search(r"\b(?:v)?\d+(?:\.\d+){1,4}\b|\b(?:19|20)\d{2}\b", text)
    return match.group(0).casefold() if match else ""


def _platform_hint(candidate: Mapping[str, Any]) -> str:
    text = " ".join(
        [
            _first_text(candidate.get("platform_hint"), ""),
            _first_text(candidate.get("title"), ""),
            _first_text(candidate.get("description"), ""),
            _first_text(candidate.get("domain_id"), ""),
        ]
    ).casefold()
    for term in ("windows 7", "windows xp", "mac os 8", "directx", "d-theater", "d-vhs"):
        if term in text:
            return term
    return ""


def _checksum_hint(candidate: Mapping[str, Any]) -> str:
    text = _first_text(candidate.get("checksum_hint"), candidate.get("sha256"), candidate.get("checksum"), "")
    return text.casefold()


def _locator_text(locator: Mapping[str, Any]) -> str:
    for key in ("url", "identifier", "value", "path"):
        value = _first_text(locator.get(key), "")
        if value:
            return value
    return json.dumps(locator, sort_keys=True, separators=(",", ":"))


def _tokens(query: str) -> list[str]:
    return [item for item in re.findall(r"[a-z0-9][a-z0-9._-]*", query.casefold()) if len(item) > 1]


def _normalize_text(value: str) -> str:
    return " ".join(_tokens(value))[:240]


def _first_text(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return " ".join(value.split())[:1000]
        if isinstance(value, (int, float)):
            return str(value)
    return ""


def _text_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [_first_text(item) for item in value if _first_text(item)]
    text = _first_text(value)
    return [text] if text else []


def _clone(value: Mapping[str, Any]) -> dict[str, Any]:
    return copy.deepcopy(dict(value))


def _clone_scalar(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, list):
        return [_clone_scalar(item) for item in value]
    if isinstance(value, Mapping):
        return {str(key): _clone_scalar(item) for key, item in value.items()}
    return str(value)


def _stable_id(prefix: str, *parts: Any) -> str:
    digest = hashlib.sha256(
        json.dumps(parts, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]
    return f"{prefix}:{digest}"


def _policy(policy: Mapping[str, Any] | None) -> dict[str, Any]:
    merged = dict(DEFAULT_POLICY)
    if isinstance(policy, Mapping):
        merged.update(policy)
    return merged


def _assert_non_claim_policy(policy: Mapping[str, Any]) -> None:
    forbidden_true = {
        "automatic_candidate_acceptance_enabled",
        "reviewed_index_mutation_enabled",
        "master_index_mutation_enabled",
        "accepted_truth_created",
        "downloads_enabled",
        "extraction_enabled",
        "model_provider_enabled",
        "deployment_enabled",
    }
    enabled = sorted(key for key in forbidden_true if bool(policy.get(key)))
    if enabled:
        raise PermissionError(f"candidate policy enables forbidden behavior: {', '.join(enabled)}")

"""Deterministic batch review workflow over candidate clusters.

Batch review improves operator throughput, but it never creates accepted truth
or mutates reviewed, master, public, or operator instance indexes.
"""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Mapping, Sequence

from runtime.candidate_store import sample_candidate_index
from runtime.scout import build_scout_run


DEFAULT_TIMESTAMP = "2026-05-31T00:00:00Z"

CANDIDATE_CLUSTER_KINDS = (
    "duplicate_cluster",
    "near_miss_cluster",
    "same_source_family_cluster",
    "same_collection_cluster",
    "same_domain_cluster",
    "same_platform_cluster",
    "same_format_family_cluster",
    "provenance_chain_cluster",
    "review_priority_cluster",
)

BATCH_DECISIONS = (
    "accept_local_reviewed_preview",
    "reject_wrong_object",
    "reject_wrong_version",
    "reject_wrong_platform",
    "reject_low_quality",
    "mark_duplicate",
    "mark_useful_lead",
    "needs_more_evidence",
    "block_candidate",
    "defer_candidate",
)

STATE_TRANSITIONS = (
    ("new", "seen"),
    ("seen", "needs_review"),
    ("needs_review", "useful_lead"),
    ("needs_review", "rejected_wrong_object"),
    ("needs_review", "rejected_wrong_version"),
    ("needs_review", "duplicate"),
    ("needs_review", "blocked"),
    ("needs_review", "review_item_created"),
    ("review_item_created", "promotion_preview_created"),
)

DECISION_TO_STATE = {
    "accept_local_reviewed_preview": "promotion_preview_created",
    "reject_wrong_object": "rejected_wrong_object",
    "reject_wrong_version": "rejected_wrong_version",
    "reject_wrong_platform": "rejected_wrong_platform",
    "reject_low_quality": "rejected_low_quality",
    "mark_duplicate": "duplicate",
    "mark_useful_lead": "useful_lead",
    "needs_more_evidence": "needs_review",
    "block_candidate": "blocked",
    "defer_candidate": "seen",
}

RELATION_TO_CLUSTER = {
    "duplicate_candidate": "duplicate_cluster",
    "near_miss_cluster": "near_miss_cluster",
    "same_source_family": "same_source_family_cluster",
    "same_collection": "same_collection_cluster",
    "same_domain": "same_domain_cluster",
    "same_platform": "same_platform_cluster",
    "same_format_family": "same_format_family_cluster",
    "provenance_chain": "provenance_chain_cluster",
}

DEFAULT_POLICY: dict[str, Any] = {
    "batch_review_requires_operator_context": True,
    "public_batch_review_enabled": False,
    "public_candidate_mutation_enabled": False,
    "automatic_candidate_acceptance_enabled": False,
    "promotion_preview_is_not_promotion": True,
    "local_apply_handoff_only": True,
    "snapshot_refresh_handoff_only": True,
    "reviewed_index_mutation_enabled": False,
    "master_index_mutation_enabled": False,
    "public_index_mutation_enabled": False,
    "accepted_truth_created": False,
    "downloads_enabled": False,
    "extraction_enabled": False,
    "model_provider_enabled": False,
    "deployment_enabled": False,
    "live_source_calls_enabled": False,
}


def build_candidate_clusters(
    candidates: Mapping[str, Any] | Sequence[Mapping[str, Any]],
    scout_relations: Mapping[str, Any] | Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Build deterministic candidate clusters from local candidates and SCOUT relations."""

    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    candidate_list = _candidate_list(candidates)
    candidates_by_id = {_candidate_id(candidate): candidate for candidate in candidate_list if _candidate_id(candidate)}
    relations = _relation_list(scout_relations)
    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    for relation in relations:
        relation_type = _text(relation.get("relation_type"))
        cluster_kind = RELATION_TO_CLUSTER.get(relation_type)
        if not cluster_kind:
            continue
        refs = _candidate_refs(relation)
        if not refs:
            continue
        key = (cluster_kind, relation_type)
        entry = grouped.setdefault(
            key,
            {
                "cluster_kind": cluster_kind,
                "relation_type": relation_type,
                "candidate_refs": set(),
                "scout_relation_refs": [],
                "reasons": set(),
            },
        )
        entry["candidate_refs"].update(refs)
        relation_id = _text(relation.get("relation_id"))
        if relation_id:
            entry["scout_relation_refs"].append(relation_id)
        explanation = _text(relation.get("explanation"))
        if explanation:
            entry["reasons"].add(explanation)

    needs_review_refs = sorted(
        candidate_id
        for candidate_id, candidate in candidates_by_id.items()
        if _text(candidate.get("review_state")) in {"", "new", "seen", "needs_review", "review_item_created"}
    )
    if needs_review_refs:
        grouped[("review_priority_cluster", "needs_review")] = {
            "cluster_kind": "review_priority_cluster",
            "relation_type": "needs_review",
            "candidate_refs": set(needs_review_refs),
            "scout_relation_refs": [],
            "reasons": {"candidates require operator review before any promotion preview"},
        }

    clusters: list[dict[str, Any]] = []
    for entry in grouped.values():
        refs = sorted(ref for ref in entry["candidate_refs"] if ref)
        if not refs:
            continue
        cluster_kind = str(entry["cluster_kind"])
        relation_type = str(entry["relation_type"])
        cluster_id = _stable_id("candidate_cluster", cluster_kind, relation_type, refs)
        clusters.append(
            {
                "schema_version": "candidate_cluster.v0",
                "record_type": "candidate_cluster",
                "cluster_id": cluster_id,
                "cluster_kind": cluster_kind,
                "relation_type": relation_type,
                "candidate_refs": refs,
                "candidates": [_candidate_summary(candidates_by_id[ref]) for ref in refs if ref in candidates_by_id],
                "scout_relation_refs": sorted(set(entry["scout_relation_refs"])),
                "scout_related_path_refs": [],
                "reason": "; ".join(sorted(entry["reasons"])) or f"{relation_type} cluster",
                "priority": _cluster_priority(cluster_kind),
                "operator_context_required": True,
                "review_required": True,
                "accepted_truth": False,
                "created_at": DEFAULT_TIMESTAMP,
                **_false_boundaries(),
            }
        )
    clusters.sort(key=lambda item: (item["priority"], item["cluster_kind"], item["cluster_id"]))
    return clusters


def build_review_batch_packet(
    candidate_clusters: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    clusters = [dict(cluster) for cluster in candidate_clusters if isinstance(cluster, Mapping)]
    candidate_refs = sorted({ref for cluster in clusters for ref in _list_text(cluster.get("candidate_refs"))})
    cluster_refs = [str(cluster.get("cluster_id") or "") for cluster in clusters if cluster.get("cluster_id")]
    review_batch_id = _stable_id("review_batch", candidate_refs, cluster_refs)
    return {
        "schema_version": "review_batch_packet.v0",
        "record_type": "review_batch_packet",
        "review_batch_id": review_batch_id,
        "candidate_refs": candidate_refs,
        "cluster_refs": cluster_refs,
        "clusters": clusters,
        "operator_context_required": True,
        "allowed_batch_decisions": list(BATCH_DECISIONS),
        "decisions": [],
        "promotion_previews": [],
        "local_apply_handoff": None,
        "snapshot_refresh_handoff": None,
        "limitations": _limitations(),
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def validate_batch_decision(
    batch_packet: Mapping[str, Any],
    decision: Mapping[str, Any] | str,
    operator_context: Mapping[str, Any] | None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    decision_name = _decision_name(decision)
    context = dict(operator_context or {})
    projection_profile = _text(context.get("projection_profile")) or "operator_workbench"
    dry_run = bool(context.get("dry_run", False))
    operator_token_present = bool(_text(context.get("operator_token")))
    selected_refs = _selected_candidate_refs(batch_packet, decision)
    blocked_reasons: list[str] = []
    if decision_name not in BATCH_DECISIONS:
        blocked_reasons.append(f"unknown batch decision: {decision_name}")
    if projection_profile in {"public_web", "native_desktop_read_only"}:
        blocked_reasons.append(f"{projection_profile} projection is read-only")
    if not (operator_token_present or dry_run):
        blocked_reasons.append("operator token or dry-run context is required")
    if bool(merged_policy.get("public_batch_review_enabled")):
        blocked_reasons.append("policy unexpectedly enables public batch review")
    allowed = not blocked_reasons
    decision_id = _stable_id(
        "review_batch_decision",
        batch_packet.get("review_batch_id"),
        decision_name,
        selected_refs,
        "token" if operator_token_present else "dry_run" if dry_run else "blocked",
    )
    record = {
        "schema_version": "review_batch_decision.v0",
        "record_type": "review_batch_decision",
        "decision_id": decision_id,
        "review_batch_id": _text(batch_packet.get("review_batch_id")),
        "candidate_refs": selected_refs,
        "cluster_refs": _selected_cluster_refs(batch_packet, decision),
        "decision": decision_name,
        "operator_context_required": True,
        "operator_context_present": bool(operator_token_present or dry_run),
        "operator_token_present": operator_token_present,
        "dry_run": dry_run,
        "allowed": allowed,
        "decision_status": "validated_preview" if allowed else "blocked_by_policy",
        "blocked_reasons": blocked_reasons,
        "candidate_summaries": _candidate_summaries_for_refs(batch_packet, selected_refs),
        "creates_accepted_truth": False,
        "promotion_preview_requested": decision_name == "accept_local_reviewed_preview",
        "limitations": _limitations(),
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }
    return record


def apply_batch_decision_preview(
    batch_packet: Mapping[str, Any],
    decision: Mapping[str, Any] | str,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    decision_record = dict(decision) if isinstance(decision, Mapping) else validate_batch_decision(
        batch_packet,
        decision,
        {"projection_profile": "operator_workbench", "dry_run": True},
        merged_policy,
    )
    state_updates = build_candidate_state_updates(decision_record, merged_policy)
    promotion_previews = build_batch_promotion_previews(decision_record, merged_policy)
    local_apply_handoff = build_batch_local_apply_handoff(promotion_previews, merged_policy)
    snapshot_refresh_handoff = build_batch_snapshot_refresh_handoff(promotion_previews, merged_policy)
    result = {
        "schema_version": "review_batch_decision_preview.v0",
        "record_type": "review_batch_decision_preview",
        "review_batch_id": _text(batch_packet.get("review_batch_id")),
        "decision": decision_record,
        "state_updates": state_updates,
        "promotion_previews": promotion_previews,
        "local_apply_handoff": local_apply_handoff,
        "snapshot_refresh_handoff": snapshot_refresh_handoff,
        "status": "preview_available" if decision_record.get("allowed") else "blocked",
        "batch_decision_applied": False,
        "local_apply_executed": False,
        "snapshot_refresh_executed": False,
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }
    result["boundary_report"] = build_review_batch_boundary_report(result, merged_policy)
    return result


def build_candidate_state_updates(
    batch_decision: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    if not bool(batch_decision.get("allowed")):
        return []
    decision_name = _text(batch_decision.get("decision"))
    new_state = DECISION_TO_STATE.get(decision_name, "needs_review")
    updates = []
    for candidate_id in _list_text(batch_decision.get("candidate_refs")):
        updates.append(
            {
                "schema_version": "review_batch_state_update.v0",
                "record_type": "review_batch_state_update",
                "state_update_id": _stable_id("review_batch_state_update", batch_decision.get("decision_id"), candidate_id),
                "review_batch_id": _text(batch_decision.get("review_batch_id")),
                "decision_id": _text(batch_decision.get("decision_id")),
                "candidate_id": candidate_id,
                "decision": decision_name,
                "old_state": "needs_review",
                "new_state": new_state,
                "transition_preview": True,
                "transition_applied": False,
                "operator_context_required": True,
                "review_required": True,
                "accepted_truth": False,
                "created_at": DEFAULT_TIMESTAMP,
                **_false_boundaries(),
            }
        )
    return updates


def build_batch_promotion_previews(
    batch_decision: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    if not bool(batch_decision.get("allowed")) or batch_decision.get("decision") != "accept_local_reviewed_preview":
        return []
    summaries = {
        _text(summary.get("candidate_id")): dict(summary)
        for summary in batch_decision.get("candidate_summaries", [])
        if isinstance(summary, Mapping) and _text(summary.get("candidate_id"))
    }
    previews = []
    for candidate_id in _list_text(batch_decision.get("candidate_refs")):
        summary = summaries.get(candidate_id, {"candidate_id": candidate_id, "title": candidate_id})
        preview_id = _stable_id("batch_promotion_preview", batch_decision.get("decision_id"), candidate_id)
        previews.append(
            {
                "schema_version": "batch_promotion_preview.v0",
                "record_type": "batch_promotion_preview",
                "preview_id": preview_id,
                "review_batch_id": _text(batch_decision.get("review_batch_id")),
                "decision_id": _text(batch_decision.get("decision_id")),
                "candidate_id": candidate_id,
                "candidate_refs": [candidate_id],
                "status": "preview_available",
                "promotion_preview_created": True,
                "promotion_preview_is_not_promotion": True,
                "reviewed_local_record_preview": {
                    "schema_version": "reviewed_local_record_preview.v0",
                    "record_id": _stable_id("reviewed_local_preview", candidate_id),
                    "candidate_id": candidate_id,
                    "title": _text(summary.get("title")) or candidate_id,
                    "source_family": _text(summary.get("source_family")),
                    "source_locator": summary.get("source_locator") if isinstance(summary.get("source_locator"), Mapping) else {},
                    "truth_level": "promotion_preview_only_not_reviewed_truth",
                    "accepted_truth": False,
                    "review_required": True,
                    "created_at": DEFAULT_TIMESTAMP,
                },
                "local_apply_required": True,
                "snapshot_refresh_required": True,
                "limitations": _limitations(),
                "review_required": True,
                "accepted_truth": False,
                "created_at": DEFAULT_TIMESTAMP,
                **_false_boundaries(),
            }
        )
    return previews


def build_batch_local_apply_handoff(
    promotion_previews: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    preview_refs = [_text(item.get("preview_id")) for item in promotion_previews if isinstance(item, Mapping)]
    preview_refs = sorted(ref for ref in preview_refs if ref)
    return {
        "schema_version": "batch_local_apply_handoff.v0",
        "record_type": "batch_local_apply_handoff",
        "handoff_id": _stable_id("batch_local_apply_handoff", preview_refs),
        "promotion_preview_refs": preview_refs,
        "handoff_status": "handoff_ready" if preview_refs else "blocked_no_promotion_previews",
        "local_apply_handoff_only": True,
        "local_apply_command_hint": "python scripts/eureka_local_apply.py --dry-run --json",
        "operator_context_required": True,
        "local_apply_executed": False,
        "requires_separate_local_apply_gate": True,
        "limitations": _limitations(),
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_batch_snapshot_refresh_handoff(
    promotion_previews: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    preview_refs = [_text(item.get("preview_id")) for item in promotion_previews if isinstance(item, Mapping)]
    preview_refs = sorted(ref for ref in preview_refs if ref)
    return {
        "schema_version": "batch_snapshot_refresh_handoff.v0",
        "record_type": "batch_snapshot_refresh_handoff",
        "handoff_id": _stable_id("batch_snapshot_refresh_handoff", preview_refs),
        "promotion_preview_refs": preview_refs,
        "handoff_status": "handoff_ready" if preview_refs else "blocked_no_promotion_previews",
        "snapshot_refresh_handoff_only": True,
        "snapshot_refresh_command_hint": "python scripts/eureka_snapshot_build.py --preview-only --json",
        "operator_context_required": True,
        "snapshot_refresh_executed": False,
        "requires_separate_snapshot_refresh_gate": True,
        "limitations": _limitations(),
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def project_review_batch(
    batch_packet: Mapping[str, Any],
    projection_profile: str,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    profile = _text(projection_profile) or "public_web"
    public_profile = profile in {"public_web", "native_desktop_read_only"}
    clusters = [dict(item) for item in batch_packet.get("clusters", []) if isinstance(item, Mapping)]
    return {
        "schema_version": "review_batch_projection.v0",
        "record_type": "review_batch_projection",
        "projection_profile": profile,
        "review_batch_id": _text(batch_packet.get("review_batch_id")),
        "cluster_count": len(clusters),
        "candidate_count": len(_list_text(batch_packet.get("candidate_refs"))),
        "clusters": [_public_cluster(cluster) for cluster in clusters],
        "read_only": public_profile,
        "allowed_actions": ["inspect", "read", "view_cluster"]
        + ([] if public_profile else ["validate_batch_decision", "preview_promotion", "build_handoff"]),
        "blocked_actions": [
            "public_batch_review",
            "public_candidate_mutation",
            "automatic_candidate_acceptance",
            "reviewed_index_mutation",
            "master_index_mutation",
            "public_index_mutation",
            "download",
            "extraction",
            "model_provider_call",
            "deployment",
        ],
        "decision_actions_visible": not public_profile,
        "operator_context_required": True,
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_review_batch_boundary_report(
    batch_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    return {
        "schema_version": "review_batch_boundary_report.v0",
        "record_type": "review_batch_boundary_report",
        "review_batch_id": _text(batch_result.get("review_batch_id")),
        "batch_review_requires_operator_context": bool(merged_policy.get("batch_review_requires_operator_context", True)),
        "promotion_preview_is_not_promotion": bool(merged_policy.get("promotion_preview_is_not_promotion", True)),
        "local_apply_handoff_only": bool(merged_policy.get("local_apply_handoff_only", True)),
        "snapshot_refresh_handoff_only": bool(merged_policy.get("snapshot_refresh_handoff_only", True)),
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def load_review_batch_inputs_from_examples() -> dict[str, Any]:
    candidate_index = sample_candidate_index()
    candidates = _candidate_list(candidate_index)
    scout_runs = []
    relation_by_id: dict[str, dict[str, Any]] = {}
    related_paths_by_id: dict[str, dict[str, Any]] = {}
    for candidate in candidates:
        candidate_id = _candidate_id(candidate)
        if not candidate_id:
            continue
        run = build_scout_run(candidate_id, candidate_index)
        scout_runs.append(run)
        for relation in run.get("relations", []):
            if isinstance(relation, Mapping) and _text(relation.get("relation_id")):
                relation_by_id[_text(relation.get("relation_id"))] = dict(relation)
        for path in run.get("related_paths", []):
            if isinstance(path, Mapping) and _text(path.get("related_path_id")):
                related_paths_by_id[_text(path.get("related_path_id"))] = dict(path)
    return {
        "schema_version": "review_batch_example_inputs.v0",
        "candidate_index": candidate_index,
        "candidates": candidates,
        "scout_runs": scout_runs,
        "scout_relations": [relation_by_id[key] for key in sorted(relation_by_id)],
        "related_paths": [related_paths_by_id[key] for key in sorted(related_paths_by_id)],
        "accepted_truth": False,
        **_false_boundaries(),
    }


def run_review_batch_from_examples(
    decision: str | None = None,
    operator_context: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    inputs = load_review_batch_inputs_from_examples()
    clusters = build_candidate_clusters(inputs["candidates"], inputs["scout_relations"], merged_policy)
    packet = build_review_batch_packet(clusters, merged_policy)
    projection = project_review_batch(packet, "public_web", merged_policy)
    result = {
        "schema_version": "review_batch_runtime_result.v0",
        "record_type": "review_batch_runtime_result",
        "status": "pass",
        "review_batch_packet": packet,
        "public_projection": projection,
        "cluster_count": len(clusters),
        "candidate_count": len(packet["candidate_refs"]),
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }
    if decision:
        decision_record = validate_batch_decision(
            packet,
            decision,
            operator_context or {"projection_profile": "operator_workbench", "dry_run": True},
            merged_policy,
        )
        result["decision_preview"] = apply_batch_decision_preview(packet, decision_record, merged_policy)
    result["boundary_report"] = build_review_batch_boundary_report(result, merged_policy)
    return result


def _candidate_list(candidates: Mapping[str, Any] | Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(candidates, Mapping):
        values = candidates.get("candidates", [])
    else:
        values = candidates
    return [dict(item) for item in values if isinstance(item, Mapping)]


def _relation_list(relations: Mapping[str, Any] | Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(relations, Mapping):
        values = relations.get("relations", [])
    else:
        values = relations
    return [dict(item) for item in values if isinstance(item, Mapping)]


def _candidate_id(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("candidate_id") or candidate.get("result_id"))


def _candidate_refs(relation: Mapping[str, Any]) -> list[str]:
    refs = _list_text(relation.get("candidate_refs"))
    if refs:
        return sorted(set(refs))
    return sorted({_text(relation.get("from_ref")), _text(relation.get("to_ref"))} - {""})


def _candidate_summary(candidate: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "review_batch_candidate_summary.v0",
        "candidate_id": _candidate_id(candidate),
        "title": _text(candidate.get("title")),
        "source_family": _text(candidate.get("source_family")),
        "source_locator": copy.deepcopy(candidate.get("source_locator") if isinstance(candidate.get("source_locator"), Mapping) else {}),
        "domain_id": _text(candidate.get("domain_id")),
        "review_state": _text(candidate.get("review_state")) or "needs_review",
        "confidence_label": _text(candidate.get("confidence_label")) or "unknown",
        "review_required": True,
        "accepted_truth": False,
    }


def _candidate_summaries_for_refs(batch_packet: Mapping[str, Any], refs: Sequence[str]) -> list[dict[str, Any]]:
    wanted = set(refs)
    summaries: dict[str, dict[str, Any]] = {}
    for cluster in batch_packet.get("clusters", []):
        if not isinstance(cluster, Mapping):
            continue
        for summary in cluster.get("candidates", []):
            if isinstance(summary, Mapping):
                candidate_id = _text(summary.get("candidate_id"))
                if candidate_id in wanted:
                    summaries[candidate_id] = dict(summary)
    return [summaries[key] for key in sorted(summaries)]


def _selected_candidate_refs(batch_packet: Mapping[str, Any], decision: Mapping[str, Any] | str) -> list[str]:
    if isinstance(decision, Mapping):
        refs = _list_text(decision.get("candidate_refs"))
        if refs:
            return sorted(set(refs))
        cluster_refs = set(_list_text(decision.get("cluster_refs")))
        if cluster_refs:
            selected: set[str] = set()
            for cluster in batch_packet.get("clusters", []):
                if isinstance(cluster, Mapping) and _text(cluster.get("cluster_id")) in cluster_refs:
                    selected.update(_list_text(cluster.get("candidate_refs")))
            if selected:
                return sorted(selected)
    return _list_text(batch_packet.get("candidate_refs"))


def _selected_cluster_refs(batch_packet: Mapping[str, Any], decision: Mapping[str, Any] | str) -> list[str]:
    if isinstance(decision, Mapping):
        refs = _list_text(decision.get("cluster_refs"))
        if refs:
            return sorted(set(refs))
    return _list_text(batch_packet.get("cluster_refs"))


def _decision_name(decision: Mapping[str, Any] | str) -> str:
    if isinstance(decision, Mapping):
        return _text(decision.get("decision") or decision.get("decision_kind"))
    return _text(decision)


def _public_cluster(cluster: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "cluster_id": _text(cluster.get("cluster_id")),
        "cluster_kind": _text(cluster.get("cluster_kind")),
        "candidate_refs": _list_text(cluster.get("candidate_refs")),
        "candidate_count": len(_list_text(cluster.get("candidate_refs"))),
        "reason": _text(cluster.get("reason")),
        "review_required": True,
        "accepted_truth": False,
    }


def _cluster_priority(cluster_kind: str) -> int:
    return {
        "duplicate_cluster": 10,
        "near_miss_cluster": 20,
        "review_priority_cluster": 30,
        "provenance_chain_cluster": 40,
    }.get(cluster_kind, 50)


def _limitations() -> list[str]:
    return [
        "batch_review_is_operator_gated",
        "promotion_preview_is_not_promotion",
        "local_apply_is_separate_gate",
        "snapshot_refresh_is_separate_gate",
        "no_automatic_truth_creation",
        "no_public_mutation",
    ]


def _false_boundaries() -> dict[str, bool]:
    return {
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "public_mutation_enabled": False,
        "operator_instance_mutated": False,
        "live_source_call_performed": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def _list_text(value: Any) -> list[str]:
    if isinstance(value, list):
        return [_text(item) for item in value if _text(item)]
    text = _text(value)
    return [text] if text else []


def _text(value: Any) -> str:
    if isinstance(value, str):
        return " ".join(value.split())
    if isinstance(value, (int, float)):
        return str(value)
    return ""


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


def _assert_policy(policy: Mapping[str, Any]) -> None:
    forbidden_true = {
        "public_batch_review_enabled",
        "public_candidate_mutation_enabled",
        "automatic_candidate_acceptance_enabled",
        "reviewed_index_mutation_enabled",
        "master_index_mutation_enabled",
        "public_index_mutation_enabled",
        "accepted_truth_created",
        "downloads_enabled",
        "extraction_enabled",
        "model_provider_enabled",
        "deployment_enabled",
        "live_source_calls_enabled",
    }
    enabled = sorted(key for key in forbidden_true if bool(policy.get(key)))
    if enabled:
        raise PermissionError(f"review batch policy enables forbidden behavior: {', '.join(enabled)}")

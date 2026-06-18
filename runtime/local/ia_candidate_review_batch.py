"""Prepare IA candidate review batches and gate explicit review decisions."""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.local.evidence_ledger_summary import (
    load_candidate_index_delta_manifest,
    load_candidates,
    load_delta_manifest as load_evidence_delta_manifest,
    load_source_observation_delta_manifest,
    load_source_observations,
)
from runtime.review.ledger import (
    REVIEW_LEDGER_DECISIONS,
    ReviewLedgerDecisionRequest,
    ReviewLedgerError,
    record_review_ledger_decision,
)
from runtime.review.queue import ReviewItemRecord, ReviewQueueStatus, ReviewQueueStore


SCHEMA_VERSION = "eureka.ia_candidate_review_batch.v0"
REVIEW_ITEM_SCHEMA_VERSION = "eureka.ia_candidate_review_item.v0"
DECISION_SCHEMA_VERSION = "eureka.ia_candidate_review_decisions.v0"
DECISION_VALIDATION_SCHEMA_VERSION = "eureka.ia_candidate_review_decision_validation.v0"
RECORD_DECISIONS_SCHEMA_VERSION = "eureka.ia_candidate_review_record_decisions.v0"
SOURCE_FAMILY = "ia_metadata"
DEFAULT_LICENSE_POSTURE = "restricted_source_available"
DEFAULT_RECOMMENDED_NEXT_ACTION = "operator_review_required"

REVIEW_ITEMS_FILE_NAME = "review_items.jsonl"
MANIFEST_FILE_NAME = "review_batch_manifest.json"
REPORT_FILE_NAME = "REVIEW_BATCH_REPORT.md"
OPERATOR_PACKET_FILE_NAME = "OPERATOR_REVIEW_PACKET.md"
DECISION_TEMPLATE_FILE_NAME = "operator_decision_template.json"
DECISION_GUIDE_FILE_NAME = "OPERATOR_DECISION_GUIDE.md"
TRANCHE_REVIEW_ITEMS_FILE_NAME = "tranche_review_items.jsonl"
TRANCHE_MANIFEST_FILE_NAME = "tranche_manifest.json"
TRANCHE_OPERATOR_PACKET_FILE_NAME = "OPERATOR_REVIEW_TRANCHE.md"
TRANCHE_DECISION_TEMPLATE_FILE_NAME = "operator_decision_template.json"
TRANCHE_DECISION_GUIDE_FILE_NAME = "OPERATOR_DECISION_GUIDE.md"
TRANCHE_DECISION_SCHEMA_VERSION = "eureka.ia_candidate_review_decisions.v0"
SUPPORTED_TRANCHE_SELECTION_POLICIES = {"balanced_evidence_rich_v0"}
TRANCHE_ALLOWED_DECISIONS = (
    "reject",
    "supersede",
    "mark_near_miss",
    "mark_need",
    "mark_policy_blocked",
    "request_more_evidence",
)
TRANCHE_PROMOTION_BLOCKERS = ("fixture_only_provenance", "independent_external_evidence_missing")

ALLOWED_REVIEW_GROUPS = {
    "evidence_rich_pending_review",
    "insufficient_support",
    "absence_or_near_miss",
    "metadata_only",
    "conflict_attention",
    "source_unavailable",
    "mixed_or_ambiguous",
}

REQUIRED_REVIEW_ITEM_FIELDS = {
    "review_item_id",
    "batch_id",
    "candidate_id",
    "candidate_status",
    "review_status",
    "source_family",
    "query_seed_refs",
    "source_observation_refs",
    "evidence_summary_refs",
    "evidence_type_counts",
    "support_posture_counts",
    "candidate_support_count",
    "metadata_mention_count",
    "insufficient_support_count",
    "absence_count",
    "near_miss_count",
    "contradiction_count",
    "provider_modes",
    "title_name_hints",
    "object_type_hints",
    "platform_hints",
    "date_version_hints",
    "representation_member_hints",
    "source_locator_hints",
    "missing_field_flags",
    "ambiguity_flags",
    "source_unavailable_flags",
    "review_attention_score",
    "review_attention_band",
    "review_group",
    "decision",
    "decision_actor",
    "decision_reason",
    "review_required",
    "self_promotion_allowed",
    "reviewed_record_created",
    "reviewed_index_mutated",
    "public_index_mutated",
    "master_index_mutated",
}

REQUIRED_MANIFEST_FIELDS = {
    "batch_id",
    "source_family",
    "generated_at",
    "input_source_observation_delta",
    "input_source_observation_delta_hash",
    "input_candidate_index_delta",
    "input_candidate_index_delta_hash",
    "input_evidence_summary_delta",
    "input_evidence_summary_delta_hash",
    "source_observation_count",
    "candidate_count",
    "evidence_summary_count",
    "review_item_count",
    "pending_review_count",
    "decisions_supplied",
    "decisions_recorded",
    "review_ledger_events_written",
    "promoted_count",
    "rejected_count",
    "superseded_count",
    "near_miss_count",
    "need_count",
    "policy_blocked_count",
    "more_evidence_count",
    "undecided_count",
    "review_group_counts",
    "attention_band_counts",
    "missing_field_counts",
    "contradiction_count",
    "insufficient_support_item_count",
    "absence_near_miss_item_count",
    "orphan_candidate_ref_count",
    "orphan_observation_ref_count",
    "orphan_evidence_ref_count",
    "unsafe_record_count",
    "automatic_decisions",
    "automatic_promotion",
    "reviewed_record_creation",
    "reviewed_master_mutation",
    "public_index_mutation",
    "candidate_index_store_mutation",
    "evidence_ledger_store_mutation",
    "reviewed_index_rebuild",
    "snapshot_refresh",
    "public_fanout",
    "network_during_prepare",
    "license_posture",
    "review_items_file",
    "review_items_file_hash",
    "decision_template_file",
    "decision_template_file_hash",
    "previous_batch_id",
    "previous_batch_path",
    "diff_status",
    "validation_status",
    "blockers",
    "recommended_next_action",
}

FORBIDDEN_TRUE_FLAGS = {
    "automatic_decisions",
    "automatic_promotion",
    "reviewed_record_creation",
    "reviewed_record_created",
    "reviewed_master_mutation",
    "reviewed_index_mutated",
    "public_index_mutation",
    "public_index_mutated",
    "master_index_mutated",
    "candidate_index_store_mutation",
    "evidence_ledger_store_mutation",
    "reviewed_index_rebuild",
    "snapshot_refresh",
    "public_fanout",
    "network_during_prepare",
    "accepted_truth_created",
}

FORBIDDEN_FALSE_FLAGS = {
    "no_downloads",
    "no_file_fetch",
    "no_wayback_replay",
    "no_public_fanout",
}

FORBIDDEN_KEYS = {
    "downloaded_files",
    "payload_bytes",
    "private_credentials",
    "secret_tokens",
    "binary_payload",
    "raw_provider_response",
    "file_bytes",
}

AI_ACTOR_MARKERS = ("ai", "llm", "model", "codex", "agent", "generated")
REASON_REQUIRED_DECISIONS = {"reject", "supersede", "mark_policy_blocked", "request_more_evidence"}


class IACandidateReviewBatchError(ValueError):
    """Raised when IA candidate review batch preparation violates policy."""


def prepare_tranche(
    *,
    batch_manifest_path: str | Path,
    group: str,
    limit: int,
    selection_policy: str,
    tranche_id: str,
    out_dir: str | Path,
) -> dict[str, Any]:
    if selection_policy not in SUPPORTED_TRANCHE_SELECTION_POLICIES:
        raise IACandidateReviewBatchError(f"unsupported tranche selection policy: {selection_policy}")
    if group not in ALLOWED_REVIEW_GROUPS:
        raise IACandidateReviewBatchError(f"unsupported review group: {group}")
    if limit <= 0:
        raise IACandidateReviewBatchError("limit must be positive")
    batch_path = Path(batch_manifest_path)
    batch_manifest = load_review_batch_manifest(batch_path)
    batch_errors = validate_batch_path(batch_path, strict=True)
    if batch_errors["status"] != "PASS":
        raise IACandidateReviewBatchError("; ".join(str(error) for error in batch_errors.get("errors", [])))
    parent_items = load_review_items(batch_path, batch_manifest)
    selected = select_tranche_review_items(
        parent_items,
        group=group,
        limit=limit,
        selection_policy=selection_policy,
    )
    if len(selected) != limit:
        raise IACandidateReviewBatchError(f"selected {len(selected)} tranche items, expected {limit}")
    tranche_items = [_tranche_item(item) for item in selected]
    errors = _tranche_item_errors(tranche_items)
    if errors:
        raise IACandidateReviewBatchError("; ".join(errors))

    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    items_path = output / TRANCHE_REVIEW_ITEMS_FILE_NAME
    manifest_path = output / TRANCHE_MANIFEST_FILE_NAME
    packet_path = output / TRANCHE_OPERATOR_PACKET_FILE_NAME
    template_path = output / TRANCHE_DECISION_TEMPLATE_FILE_NAME
    guide_path = output / TRANCHE_DECISION_GUIDE_FILE_NAME

    decision_template = build_tranche_decision_template(
        batch_manifest=batch_manifest,
        tranche_id=tranche_id,
        tranche_items=tranche_items,
    )
    _write_jsonl(items_path, tranche_items)
    _write_json(template_path, decision_template)
    items_hash = _file_hash(items_path)
    template_hash = _file_hash(template_path)
    manifest = build_tranche_manifest(
        batch_manifest=batch_manifest,
        batch_manifest_path=batch_path,
        tranche_id=tranche_id,
        selection_policy=selection_policy,
        requested_count=limit,
        tranche_items=tranche_items,
        items_hash=items_hash,
        template_hash=template_hash,
    )
    manifest_errors = validate_tranche_manifest(manifest, tranche_items=tranche_items, strict=False)
    if manifest_errors:
        raise IACandidateReviewBatchError("; ".join(manifest_errors))
    _write_json(manifest_path, manifest)
    packet_path.write_text(render_operator_tranche_packet(manifest, tranche_items=tranche_items), encoding="utf-8", newline="\n")
    guide_path.write_text(render_tranche_decision_guide(manifest), encoding="utf-8", newline="\n")
    return {
        "schema_version": "eureka.ia_candidate_review_tranche_prepare_result.v0",
        "status": "PASS_WITH_WARNINGS",
        "tranche_id": tranche_id,
        "source_batch_id": manifest.get("source_batch_id"),
        "manifest": manifest,
        "manifest_path": _safe_path_label(manifest_path),
        "tranche_items_path": _safe_path_label(items_path),
        "operator_packet_path": _safe_path_label(packet_path),
        "decision_template_path": _safe_path_label(template_path),
        "decision_guide_path": _safe_path_label(guide_path),
        "selected_count": len(tranche_items),
        "pending_review_count": len(tranche_items),
        "decisions_recorded": 0,
        "review_ledger_events_written": 0,
        "network_used": False,
        "provider_calls": False,
        "automatic_decisions": False,
        "automatic_promotion": False,
        "reviewed_records_created": False,
        "reviewed_master_mutation": False,
        "public_index_mutation": False,
    }


def select_tranche_review_items(
    review_items: Sequence[Mapping[str, Any]],
    *,
    group: str,
    limit: int,
    selection_policy: str,
) -> list[dict[str, Any]]:
    if selection_policy != "balanced_evidence_rich_v0":
        raise IACandidateReviewBatchError(f"unsupported tranche selection policy: {selection_policy}")
    candidates = [
        dict(item)
        for item in review_items
        if str(item.get("review_group") or "") == group
        and int(item.get("contradiction_count") or 0) == 0
        and not _text_list(item.get("source_unavailable_flags"))
        and _text_list(item.get("candidate_id"))
        and _text_list(item.get("source_observation_refs"))
        and _text_list(item.get("evidence_summary_refs"))
        and _scan_unsafe_content(item, "$") == []
    ]
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in candidates:
        buckets[_primary_query(item)].append(item)
    for query in buckets:
        buckets[query].sort(key=lambda item: (-_tranche_preference_score(item), str(item.get("review_item_id") or "")))
    selected: list[dict[str, Any]] = []
    per_query = Counter()
    max_per_query = 2
    query_order = sorted(buckets)
    while len(selected) < limit and any(buckets.values()):
        made_progress = False
        for query in query_order:
            if len(selected) >= limit:
                break
            if not buckets[query]:
                continue
            if per_query[query] >= max_per_query:
                continue
            selected.append(buckets[query].pop(0))
            per_query[query] += 1
            made_progress = True
        if not made_progress:
            max_per_query += 1
    return selected


def build_tranche_manifest(
    *,
    batch_manifest: Mapping[str, Any],
    batch_manifest_path: Path,
    tranche_id: str,
    selection_policy: str,
    requested_count: int,
    tranche_items: Sequence[Mapping[str, Any]],
    items_hash: str,
    template_hash: str,
) -> dict[str, Any]:
    query_seed_counts = Counter(_primary_query(item) for item in tranche_items)
    review_group_counts = Counter(str(item.get("review_group") or "unknown") for item in tranche_items)
    attention_band_counts = Counter(str(item.get("review_attention_band") or "unknown") for item in tranche_items)
    evidence_type_counts: Counter[str] = Counter()
    support_posture_counts: Counter[str] = Counter()
    missing_field_counts: Counter[str] = Counter()
    for item in tranche_items:
        evidence_type_counts.update(dict(item.get("evidence_type_counts", {}) or {}))
        support_posture_counts.update(dict(item.get("support_posture_counts", {}) or {}))
        missing_field_counts.update(_text_list(item.get("missing_field_flags")))
    selected_ids = [str(item.get("review_item_id") or "") for item in tranche_items]
    return {
        "schema_version": "eureka.ia_candidate_review_tranche.v0",
        "tranche_id": tranche_id,
        "source_batch_id": str(batch_manifest.get("batch_id") or ""),
        "source_batch_manifest": _safe_path_label(batch_manifest_path),
        "source_batch_manifest_hash": f"sha256:{_file_hash(batch_manifest_path)}",
        "selection_policy": selection_policy,
        "generated_at": str(batch_manifest.get("generated_at") or ""),
        "requested_count": requested_count,
        "selected_count": len(tranche_items),
        "selected_review_item_ids": selected_ids,
        "query_seed_counts": dict(sorted(query_seed_counts.items())),
        "review_group_counts": dict(sorted(review_group_counts.items())),
        "attention_band_counts": dict(sorted(attention_band_counts.items())),
        "evidence_type_counts": dict(sorted(evidence_type_counts.items())),
        "support_posture_counts": dict(sorted(support_posture_counts.items())),
        "missing_field_counts": dict(sorted(missing_field_counts.items())),
        "fixture_derived_count": sum(1 for item in tranche_items if "fixture" in _text_list(item.get("provider_modes"))),
        "live_derived_count": sum(1 for item in tranche_items if "live" in _text_list(item.get("provider_modes"))),
        "promotion_eligible_count": sum(1 for item in tranche_items if item.get("promotion_eligible") is True),
        "promotion_blocked_count": sum(1 for item in tranche_items if item.get("promotion_eligible") is False),
        "decisions_supplied": False,
        "decisions_recorded": 0,
        "review_ledger_events_written": 0,
        "reviewed_records_created": False,
        "reviewed_master_mutation": False,
        "public_index_mutation": False,
        "candidate_index_store_mutation": False,
        "evidence_ledger_store_mutation": False,
        "reviewed_index_rebuild": False,
        "snapshot_refresh": False,
        "network_provider_calls": False,
        "automatic_decisions": False,
        "automatic_promotion": False,
        "tranche_items_file": TRANCHE_REVIEW_ITEMS_FILE_NAME,
        "tranche_items_file_hash": f"sha256:{items_hash}",
        "decision_template_file": TRANCHE_DECISION_TEMPLATE_FILE_NAME,
        "decision_template_file_hash": f"sha256:{template_hash}",
        "validation_status": "PASS_WITH_WARNINGS",
        "blockers": [
            "WAITING_FOR_OPERATOR_REVIEW_DECISIONS",
            "PROMOTION_BLOCKED_FIXTURE_ONLY_PROVENANCE",
        ],
        "recommended_next_action": "operator_decisions_required",
    }


def build_tranche_decision_template(
    *,
    batch_manifest: Mapping[str, Any],
    tranche_id: str,
    tranche_items: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": TRANCHE_DECISION_SCHEMA_VERSION,
        "batch_id": batch_manifest.get("batch_id"),
        "tranche_id": tranche_id,
        "actor": "OPERATOR_REQUIRED",
        "generated_at": str(batch_manifest.get("generated_at") or ""),
        "decisions": [
            {
                "review_item_id": item.get("review_item_id"),
                "candidate_id": item.get("candidate_id"),
                "decision": None,
                "reason": None,
                "evidence_refs": _text_list(item.get("evidence_summary_refs")),
                "source_observation_refs": _text_list(item.get("source_observation_refs")),
                "absence_refs": [],
                "fallback_refs": [],
                "supersedes_review_item_id": None,
                "local_only_confirmed": False,
                "promotion_eligible": False,
                "promotion_blockers": list(TRANCHE_PROMOTION_BLOCKERS),
            }
            for item in sorted(tranche_items, key=lambda value: str(value.get("review_item_id") or ""))
        ],
    }


def load_tranche_manifest(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    if not source.is_file():
        raise IACandidateReviewBatchError(f"tranche manifest not found: {source}")
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise IACandidateReviewBatchError(f"invalid tranche manifest JSON: {exc.msg}") from exc
    if not isinstance(payload, Mapping):
        raise IACandidateReviewBatchError("tranche manifest must be a JSON object")
    return dict(payload)


def load_tranche_items(tranche_manifest_path: str | Path, manifest: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    manifest_path = Path(tranche_manifest_path)
    active_manifest = dict(manifest or load_tranche_manifest(manifest_path))
    items_path = _resolve_manifest_ref(manifest_path.parent, str(active_manifest.get("tranche_items_file") or TRANCHE_REVIEW_ITEMS_FILE_NAME))
    rows = _read_jsonl(items_path, "tranche review items")
    errors = _tranche_item_errors(rows)
    if errors:
        raise IACandidateReviewBatchError("; ".join(errors))
    return rows


def validate_tranche_path(path: str | Path, *, strict: bool = False) -> dict[str, Any]:
    manifest_path = Path(path)
    try:
        manifest = load_tranche_manifest(manifest_path)
        items = load_tranche_items(manifest_path, manifest)
        errors = validate_tranche_manifest(manifest, tranche_items=items, strict=strict)
        if strict:
            items_hash = f"sha256:{_file_hash(_resolve_manifest_ref(manifest_path.parent, str(manifest.get('tranche_items_file') or TRANCHE_REVIEW_ITEMS_FILE_NAME)))}"
            if manifest.get("tranche_items_file_hash") != items_hash:
                errors.append("tranche_items_file_hash does not match tranche items file")
            template_path = _resolve_manifest_ref(manifest_path.parent, str(manifest.get("decision_template_file") or TRANCHE_DECISION_TEMPLATE_FILE_NAME))
            template_hash = f"sha256:{_file_hash(template_path)}"
            if manifest.get("decision_template_file_hash") != template_hash:
                errors.append("decision_template_file_hash does not match decision template file")
            template = _load_json_object(template_path, "tranche decision template")
            errors.extend(_tranche_template_errors(template, manifest=manifest, items=items))
        return {
            "schema_version": "eureka.ia_candidate_review_tranche_validation.v0",
            "status": "PASS" if not errors else "FAIL",
            "errors": sorted(dict.fromkeys(errors)),
            "tranche_id": manifest.get("tranche_id"),
            "source_batch_id": manifest.get("source_batch_id"),
            "selected_count": manifest.get("selected_count"),
            "promotion_eligible_count": manifest.get("promotion_eligible_count"),
            "promotion_blocked_count": manifest.get("promotion_blocked_count"),
            "decisions_supplied": manifest.get("decisions_supplied"),
            "decisions_recorded": manifest.get("decisions_recorded"),
            "network_provider_calls": manifest.get("network_provider_calls"),
        }
    except IACandidateReviewBatchError as exc:
        return {
            "schema_version": "eureka.ia_candidate_review_tranche_validation.v0",
            "status": "FAIL",
            "errors": [str(exc)],
        }


def validate_tranche_manifest(
    manifest: Mapping[str, Any],
    *,
    tranche_items: Sequence[Mapping[str, Any]] | None = None,
    strict: bool = False,
) -> list[str]:
    required = {
        "tranche_id",
        "source_batch_id",
        "selection_policy",
        "generated_at",
        "requested_count",
        "selected_count",
        "selected_review_item_ids",
        "query_seed_counts",
        "review_group_counts",
        "attention_band_counts",
        "evidence_type_counts",
        "support_posture_counts",
        "missing_field_counts",
        "fixture_derived_count",
        "live_derived_count",
        "promotion_eligible_count",
        "promotion_blocked_count",
        "decisions_supplied",
        "decisions_recorded",
        "review_ledger_events_written",
        "reviewed_records_created",
        "reviewed_master_mutation",
        "public_index_mutation",
        "network_provider_calls",
        "validation_status",
        "blockers",
        "recommended_next_action",
    }
    errors: list[str] = []
    missing = sorted(required - set(manifest))
    if missing:
        errors.append(f"tranche manifest missing required fields: {', '.join(missing)}")
    if manifest.get("selection_policy") not in SUPPORTED_TRANCHE_SELECTION_POLICIES:
        errors.append("selection_policy is not supported")
    if not isinstance(manifest.get("requested_count"), int) or int(manifest.get("requested_count") or 0) <= 0:
        errors.append("requested_count must be positive")
    if manifest.get("selected_count") != manifest.get("requested_count"):
        errors.append("selected_count must equal requested_count")
    if manifest.get("fixture_derived_count") != manifest.get("selected_count"):
        errors.append("fixture_derived_count must equal selected_count for Tranche 01")
    if manifest.get("live_derived_count") != 0:
        errors.append("live_derived_count must be 0 for Tranche 01")
    if manifest.get("promotion_eligible_count") != 0:
        errors.append("promotion_eligible_count must be 0")
    if manifest.get("promotion_blocked_count") != manifest.get("selected_count"):
        errors.append("promotion_blocked_count must equal selected_count")
    for key in (
        "decisions_supplied",
        "reviewed_records_created",
        "reviewed_master_mutation",
        "public_index_mutation",
        "candidate_index_store_mutation",
        "evidence_ledger_store_mutation",
        "reviewed_index_rebuild",
        "snapshot_refresh",
        "network_provider_calls",
        "automatic_decisions",
        "automatic_promotion",
    ):
        if manifest.get(key) is not False:
            errors.append(f"{key} must be false")
    for key in ("decisions_recorded", "review_ledger_events_written"):
        if manifest.get(key) != 0:
            errors.append(f"{key} must be 0")
    if manifest.get("recommended_next_action") != "operator_decisions_required":
        errors.append("recommended_next_action must be operator_decisions_required")
    if "WAITING_FOR_OPERATOR_REVIEW_DECISIONS" not in _text_list(manifest.get("blockers")):
        errors.append("tranche manifest must include WAITING_FOR_OPERATOR_REVIEW_DECISIONS")
    if tranche_items is not None:
        errors.extend(_tranche_item_errors(tranche_items))
        if manifest.get("selected_count") != len(tranche_items):
            errors.append("selected_count does not match tranche items")
        selected_ids = [str(item.get("review_item_id") or "") for item in tranche_items]
        if manifest.get("selected_review_item_ids") != selected_ids:
            errors.append("selected_review_item_ids do not match tranche item order")
        if strict and len(selected_ids) != len(set(selected_ids)):
            errors.append("selected review item ids must be unique")
    return sorted(dict.fromkeys(errors))


def status_for_tranche(path: str | Path) -> dict[str, Any]:
    manifest = load_tranche_manifest(path)
    return {
        "schema_version": "eureka.ia_candidate_review_tranche_status.v0",
        "status": manifest.get("validation_status"),
        "tranche_id": manifest.get("tranche_id"),
        "source_batch_id": manifest.get("source_batch_id"),
        "selection_policy": manifest.get("selection_policy"),
        "requested_count": manifest.get("requested_count"),
        "selected_count": manifest.get("selected_count"),
        "query_seed_counts": manifest.get("query_seed_counts", {}),
        "review_group_counts": manifest.get("review_group_counts", {}),
        "attention_band_counts": manifest.get("attention_band_counts", {}),
        "fixture_derived_count": manifest.get("fixture_derived_count"),
        "live_derived_count": manifest.get("live_derived_count"),
        "promotion_eligible_count": manifest.get("promotion_eligible_count"),
        "promotion_blocked_count": manifest.get("promotion_blocked_count"),
        "decisions_supplied": manifest.get("decisions_supplied"),
        "decisions_recorded": manifest.get("decisions_recorded"),
        "network_provider_calls": manifest.get("network_provider_calls"),
        "blockers": manifest.get("blockers", []),
        "recommended_next_action": manifest.get("recommended_next_action"),
    }


def build_review_batch(
    *,
    source: str,
    source_observation_delta_path: str | Path,
    candidate_index_delta_path: str | Path,
    evidence_summary_delta_path: str | Path,
    out_dir: str | Path,
) -> dict[str, Any]:
    normalized_source = _normalize_source(source)
    if normalized_source != SOURCE_FAMILY:
        raise IACandidateReviewBatchError(f"unsupported source: {source}")

    source_delta_path = Path(source_observation_delta_path)
    candidate_delta_path = Path(candidate_index_delta_path)
    evidence_delta_path = Path(evidence_summary_delta_path)
    source_manifest = load_source_observation_delta_manifest(source_delta_path)
    candidate_manifest = load_candidate_index_delta_manifest(candidate_delta_path)
    evidence_manifest = load_evidence_delta_manifest(evidence_delta_path)
    source_observations = load_source_observations(source_delta_path, source_manifest)
    candidates = load_candidates(candidate_delta_path, candidate_manifest)
    evidence_summaries = _load_evidence_summaries(evidence_delta_path, evidence_manifest)

    source_delta_hash = _file_hash(source_delta_path)
    candidate_delta_hash = _file_hash(candidate_delta_path)
    evidence_delta_hash = _file_hash(evidence_delta_path)
    input_errors = _input_errors(
        source_manifest=source_manifest,
        candidate_manifest=candidate_manifest,
        evidence_manifest=evidence_manifest,
        source_delta_hash=source_delta_hash,
        candidate_delta_hash=candidate_delta_hash,
        source_observations=source_observations,
        candidates=candidates,
        evidence_summaries=evidence_summaries,
    )
    if input_errors:
        raise IACandidateReviewBatchError("; ".join(input_errors))

    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    review_items_path = output / REVIEW_ITEMS_FILE_NAME
    manifest_path = output / MANIFEST_FILE_NAME
    report_path = output / REPORT_FILE_NAME
    operator_packet_path = output / OPERATOR_PACKET_FILE_NAME
    decision_template_path = output / DECISION_TEMPLATE_FILE_NAME
    decision_guide_path = output / DECISION_GUIDE_FILE_NAME

    batch_seed = {
        "source_family": SOURCE_FAMILY,
        "source_delta": f"sha256:{source_delta_hash}",
        "candidate_delta": f"sha256:{candidate_delta_hash}",
        "evidence_delta": f"sha256:{evidence_delta_hash}",
        "candidate_ids": sorted(str(item.get("candidate_id") or "") for item in candidates),
    }
    batch_id = f"review-batch:{SOURCE_FAMILY}:{_stable_digest(batch_seed, 20)}"
    review_items = normalize_review_items(
        batch_id=batch_id,
        source_manifest=source_manifest,
        candidate_manifest=candidate_manifest,
        evidence_manifest=evidence_manifest,
        source_observations=source_observations,
        candidates=candidates,
        evidence_summaries=evidence_summaries,
    )
    item_errors = _review_item_errors(
        review_items,
        candidate_ids={str(item.get("candidate_id") or "") for item in candidates},
        source_observation_ids={str(item.get("observation_id") or "") for item in source_observations},
        evidence_summary_ids={str(item.get("evidence_summary_id") or "") for item in evidence_summaries},
    )
    if item_errors:
        raise IACandidateReviewBatchError("; ".join(item_errors))

    previous = _load_previous_manifest(manifest_path)
    decision_template = build_decision_template(batch_id=batch_id, review_items=review_items, generated_at=_generated_at(evidence_manifest, candidate_manifest, source_manifest))

    _write_jsonl(review_items_path, review_items)
    _write_json(decision_template_path, decision_template)
    review_items_hash = _file_hash(review_items_path)
    decision_template_hash = _file_hash(decision_template_path)
    manifest = build_review_batch_manifest(
        batch_id=batch_id,
        source_manifest=source_manifest,
        candidate_manifest=candidate_manifest,
        evidence_manifest=evidence_manifest,
        source_delta_path=source_delta_path,
        candidate_delta_path=candidate_delta_path,
        evidence_delta_path=evidence_delta_path,
        source_delta_hash=source_delta_hash,
        candidate_delta_hash=candidate_delta_hash,
        evidence_delta_hash=evidence_delta_hash,
        source_observations=source_observations,
        candidates=candidates,
        evidence_summaries=evidence_summaries,
        review_items=review_items,
        review_items_hash=review_items_hash,
        decision_template_hash=decision_template_hash,
        previous=previous,
    )
    manifest_errors = validate_review_batch_manifest(manifest, review_items=review_items)
    if manifest_errors:
        raise IACandidateReviewBatchError("; ".join(manifest_errors))
    _write_json(manifest_path, manifest)
    report_path.write_text(render_markdown_summary(manifest, review_items=review_items), encoding="utf-8", newline="\n")
    operator_packet_path.write_text(render_operator_review_packet(manifest, review_items=review_items), encoding="utf-8", newline="\n")
    decision_guide_path.write_text(render_decision_guide(manifest), encoding="utf-8", newline="\n")

    return {
        "schema_version": "eureka.ia_candidate_review_batch_prepare_result.v0",
        "status": "PASS" if manifest["validation_status"] == "PASS" else "PASS_WITH_WARNINGS",
        "manifest": manifest,
        "manifest_path": _safe_path_label(manifest_path),
        "review_items_path": _safe_path_label(review_items_path),
        "operator_packet_path": _safe_path_label(operator_packet_path),
        "decision_template_path": _safe_path_label(decision_template_path),
        "decision_guide_path": _safe_path_label(decision_guide_path),
        "report_path": _safe_path_label(report_path),
        "review_item_count": len(review_items),
        "pending_review_count": len(review_items),
        "decisions_recorded": 0,
        "review_ledger_events_written": 0,
        "network_used": False,
        "provider_calls": False,
        "downloads": False,
        "file_fetch": False,
        "wayback_replay": False,
        "automatic_decisions": False,
        "automatic_promotion": False,
        "reviewed_record_creation": False,
        "reviewed_master_mutation": False,
        "public_index_mutation": False,
        "candidate_index_store_mutation": False,
        "evidence_ledger_store_mutation": False,
        "reviewed_index_rebuild": False,
        "snapshot_refresh": False,
    }


def normalize_review_items(
    *,
    batch_id: str,
    source_manifest: Mapping[str, Any],
    candidate_manifest: Mapping[str, Any],
    evidence_manifest: Mapping[str, Any],
    source_observations: Sequence[Mapping[str, Any]],
    candidates: Sequence[Mapping[str, Any]],
    evidence_summaries: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    evidence_by_candidate: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for summary in evidence_summaries:
        for candidate_id in _text_list(summary.get("candidate_refs")):
            evidence_by_candidate[candidate_id].append(summary)

    observations_by_id = {str(item.get("observation_id") or ""): dict(item) for item in source_observations}
    generated_at = _generated_at(evidence_manifest, candidate_manifest, source_manifest)
    source_delta_id = str(source_manifest.get("delta_id") or "")
    candidate_delta_id = str(candidate_manifest.get("delta_id") or "")
    evidence_delta_id = str(evidence_manifest.get("delta_id") or "")

    review_items: list[dict[str, Any]] = []
    for candidate in sorted(candidates, key=lambda item: str(item.get("candidate_id") or "")):
        candidate_id = str(candidate.get("candidate_id") or "")
        summaries = sorted(
            evidence_by_candidate.get(candidate_id, []),
            key=lambda item: str(item.get("evidence_summary_id") or ""),
        )
        evidence_refs = [str(item.get("evidence_summary_id") or "") for item in summaries if item.get("evidence_summary_id")]
        source_observation_refs = _text_list(candidate.get("source_observation_refs"))
        if not source_observation_refs:
            source_observation_refs = sorted(
                {
                    ref
                    for item in summaries
                    for ref in _text_list(item.get("source_observation_refs"))
                    if ref
                }
            )
        observation_records = [observations_by_id[ref] for ref in source_observation_refs if ref in observations_by_id]
        query_seed_refs = sorted(
            set(_text_list(candidate.get("query_seed_refs")))
            | {ref for item in summaries for ref in _text_list(item.get("query_seed_refs"))}
            | {str(item.get("query_seed") or "") for item in observation_records if item.get("query_seed")}
        )
        provider_modes = sorted(
            set(_text_list(candidate.get("provider_mode_refs")))
            | {ref for item in summaries for ref in _text_list(item.get("provider_mode_refs"))}
            | {str(item.get("provider_mode") or "") for item in observation_records if item.get("provider_mode")}
        )
        evidence_type_counts = Counter(str(item.get("evidence_type") or "unknown") for item in summaries)
        support_posture_counts = Counter(str(item.get("support_posture") or "unknown") for item in summaries)
        contradiction_flags = sorted({flag for item in summaries for flag in _text_list(item.get("contradiction_flags"))})
        absence_flags = sorted(
            {
                flag
                for item in summaries
                if str(item.get("evidence_type") or "") == "absence clue"
                for flag in (_text_list(item.get("absence_or_near_miss_flags")) or ["absence clue"])
            }
        )
        near_miss_flags = sorted(
            {
                flag
                for item in summaries
                if str(item.get("evidence_type") or "") == "near-miss clue"
                for flag in (_text_list(item.get("absence_or_near_miss_flags")) or ["near-miss clue"])
            }
        )
        source_unavailable_flags = sorted(
            {
                str(item.get("evidence_summary_id") or "")
                for item in summaries
                if str(item.get("support_posture") or "") == "source_unavailable"
            }
        )
        title_name_hints = _single_text_list(candidate.get("normalized_title"))
        object_type_hints = _text_list(candidate.get("normalized_type_hints"))
        platform_time_hints = _text_list(candidate.get("platform_time_version_hints"))
        representation_hints = _text_list(candidate.get("representation_member_hints"))
        locator_hints = [dict(item) for item in candidate.get("source_locator_refs", []) if isinstance(item, Mapping)]
        missing_flags = _missing_field_flags(
            title_name_hints=title_name_hints,
            object_type_hints=object_type_hints,
            platform_hints=platform_time_hints,
            representation_hints=representation_hints,
            source_locator_hints=locator_hints,
            source_observation_refs=source_observation_refs,
            evidence_refs=evidence_refs,
        )
        item_seed = {
            "batch_id": batch_id,
            "candidate_id": candidate_id,
            "source_delta_id": source_delta_id,
            "candidate_delta_id": candidate_delta_id,
            "evidence_delta_id": evidence_delta_id,
            "source_observation_refs": source_observation_refs,
            "evidence_refs": evidence_refs,
        }
        review_item_id = f"review-item:{SOURCE_FAMILY}:{_stable_digest(item_seed, 20)}"
        attention_score = _attention_score(
            evidence_count=len(summaries),
            insufficient_count=int(support_posture_counts.get("insufficient", 0)),
            absence_count=len(absence_flags),
            near_miss_count=len(near_miss_flags),
            contradiction_count=len(contradiction_flags),
            source_unavailable_count=len(source_unavailable_flags),
            missing_field_count=len(missing_flags),
            provider_modes=provider_modes,
        )
        review_group = _review_group(
            support_posture_counts=support_posture_counts,
            absence_count=len(absence_flags),
            near_miss_count=len(near_miss_flags),
            contradiction_count=len(contradiction_flags),
            source_unavailable_count=len(source_unavailable_flags),
            ambiguity_flags=_text_list(candidate.get("ambiguity_flags")),
        )
        review_items.append(
            {
                "schema_version": REVIEW_ITEM_SCHEMA_VERSION,
                "review_item_id": review_item_id,
                "batch_id": batch_id,
                "candidate_id": candidate_id,
                "candidate_status": "provisional",
                "review_status": "pending",
                "source_family": SOURCE_FAMILY,
                "query_seed_refs": query_seed_refs,
                "source_observation_refs": source_observation_refs,
                "evidence_summary_refs": evidence_refs,
                "evidence_type_counts": dict(sorted(evidence_type_counts.items())),
                "support_posture_counts": dict(sorted(support_posture_counts.items())),
                "candidate_support_count": int(support_posture_counts.get("candidate_support", 0)),
                "metadata_mention_count": int(support_posture_counts.get("metadata_mention", 0)),
                "insufficient_support_count": int(support_posture_counts.get("insufficient", 0)),
                "absence_count": len(absence_flags),
                "near_miss_count": len(near_miss_flags),
                "contradiction_count": len(contradiction_flags),
                "provider_modes": provider_modes,
                "title_name_hints": title_name_hints,
                "object_type_hints": object_type_hints,
                "platform_hints": _platform_hints(platform_time_hints),
                "date_version_hints": _date_version_hints(platform_time_hints),
                "representation_member_hints": representation_hints,
                "source_locator_hints": locator_hints,
                "missing_field_flags": missing_flags,
                "ambiguity_flags": _text_list(candidate.get("ambiguity_flags")),
                "source_unavailable_flags": source_unavailable_flags,
                "review_attention_score": attention_score,
                "review_attention_band": _attention_band(attention_score),
                "review_group": review_group,
                "decision": None,
                "decision_actor": None,
                "decision_reason": None,
                "review_required": True,
                "self_promotion_allowed": False,
                "reviewed_record_created": False,
                "reviewed_index_mutated": False,
                "public_index_mutated": False,
                "master_index_mutated": False,
                "generated_at": generated_at,
                "input_source_observation_delta_id": source_delta_id,
                "input_candidate_index_delta_id": candidate_delta_id,
                "input_evidence_summary_delta_id": evidence_delta_id,
                "decision_template_status": "blank_operator_required",
                "operator_statement": "Decision pending - no outcome inferred",
            }
        )
    return review_items


def build_review_batch_manifest(
    *,
    batch_id: str,
    source_manifest: Mapping[str, Any],
    candidate_manifest: Mapping[str, Any],
    evidence_manifest: Mapping[str, Any],
    source_delta_path: Path,
    candidate_delta_path: Path,
    evidence_delta_path: Path,
    source_delta_hash: str,
    candidate_delta_hash: str,
    evidence_delta_hash: str,
    source_observations: Sequence[Mapping[str, Any]],
    candidates: Sequence[Mapping[str, Any]],
    evidence_summaries: Sequence[Mapping[str, Any]],
    review_items: Sequence[Mapping[str, Any]],
    review_items_hash: str,
    decision_template_hash: str,
    previous: Mapping[str, Any] | None,
) -> dict[str, Any]:
    review_group_counts = Counter(str(item.get("review_group") or "unknown") for item in review_items)
    attention_band_counts = Counter(str(item.get("review_attention_band") or "unknown") for item in review_items)
    missing_field_counts: Counter[str] = Counter()
    for item in review_items:
        missing_field_counts.update(_text_list(item.get("missing_field_flags")))
    contradiction_count = sum(1 for item in review_items if int(item.get("contradiction_count") or 0) > 0)
    insufficient_items = sum(1 for item in review_items if int(item.get("insufficient_support_count") or 0) > 0)
    absence_near_miss_items = sum(
        1
        for item in review_items
        if int(item.get("absence_count") or 0) > 0 or int(item.get("near_miss_count") or 0) > 0
    )
    source_ids = {str(item.get("observation_id") or "") for item in source_observations}
    candidate_ids = {str(item.get("candidate_id") or "") for item in candidates}
    evidence_ids = {str(item.get("evidence_summary_id") or "") for item in evidence_summaries}
    previous_batch_id: str | None = None
    previous_batch_path: str | None = None
    diff_status = "first_run_no_previous_batch"
    if previous:
        previous_id = str(previous.get("batch_id") or "") or None
        if previous_id and previous_id != batch_id:
            previous_batch_id = previous_id
            previous_batch_path = str(previous.get("previous_batch_path") or _safe_path_label(Path(MANIFEST_FILE_NAME))) or None
            diff_status = "changed_from_previous_batch"
        elif previous_id == batch_id and previous.get("diff_status") != "first_run_no_previous_batch":
            previous_batch_id = previous_id
            previous_batch_path = str(previous.get("previous_batch_path") or _safe_path_label(Path(MANIFEST_FILE_NAME))) or None
            diff_status = "unchanged_from_previous_batch"
    validation_status = "PASS" if previous_batch_id else "PASS_WITH_WARNINGS"
    blockers = ["WAITING_FOR_OPERATOR_REVIEW_DECISIONS"]
    return {
        "schema_version": SCHEMA_VERSION,
        "batch_id": batch_id,
        "source_family": SOURCE_FAMILY,
        "generated_at": _generated_at(evidence_manifest, candidate_manifest, source_manifest),
        "input_source_observation_delta": _safe_path_label(source_delta_path),
        "input_source_observation_delta_hash": f"sha256:{source_delta_hash}",
        "input_source_observation_delta_id": source_manifest.get("delta_id"),
        "input_candidate_index_delta": _safe_path_label(candidate_delta_path),
        "input_candidate_index_delta_hash": f"sha256:{candidate_delta_hash}",
        "input_candidate_index_delta_id": candidate_manifest.get("delta_id"),
        "input_evidence_summary_delta": _safe_path_label(evidence_delta_path),
        "input_evidence_summary_delta_hash": f"sha256:{evidence_delta_hash}",
        "input_evidence_summary_delta_id": evidence_manifest.get("delta_id"),
        "source_observation_count": len(source_observations),
        "candidate_count": len(candidates),
        "evidence_summary_count": len(evidence_summaries),
        "review_item_count": len(review_items),
        "pending_review_count": len(review_items),
        "decisions_supplied": False,
        "decisions_recorded": 0,
        "review_ledger_events_written": 0,
        "promoted_count": 0,
        "rejected_count": 0,
        "superseded_count": 0,
        "near_miss_count": 0,
        "need_count": 0,
        "policy_blocked_count": 0,
        "more_evidence_count": 0,
        "undecided_count": len(review_items),
        "review_group_counts": dict(sorted(review_group_counts.items())),
        "attention_band_counts": dict(sorted(attention_band_counts.items())),
        "missing_field_counts": dict(sorted(missing_field_counts.items())),
        "provider_modes": sorted(
            set(_text_list(source_manifest.get("provider_modes_represented")))
            | set(_text_list(candidate_manifest.get("provider_modes")))
            | set(_text_list(evidence_manifest.get("provider_modes")))
        ),
        "item_provider_modes": sorted({mode for item in review_items for mode in _text_list(item.get("provider_modes"))}),
        "contradiction_count": contradiction_count,
        "insufficient_support_item_count": insufficient_items,
        "absence_near_miss_item_count": absence_near_miss_items,
        "live_derived_item_count": sum(1 for item in review_items if "live" in _text_list(item.get("provider_modes"))),
        "fixture_derived_item_count": sum(1 for item in review_items if "fixture" in _text_list(item.get("provider_modes"))),
        "orphan_candidate_ref_count": _orphan_ref_count(review_items, "candidate_id", candidate_ids),
        "orphan_observation_ref_count": _orphan_ref_count(review_items, "source_observation_refs", source_ids),
        "orphan_evidence_ref_count": _orphan_ref_count(review_items, "evidence_summary_refs", evidence_ids),
        "unsafe_record_count": 0,
        "redacted_error_count": int(source_manifest.get("redacted_error_count") or 0)
        + int(candidate_manifest.get("redacted_error_count") or 0)
        + int(evidence_manifest.get("redacted_error_count") or 0),
        "no_downloads": True,
        "no_file_fetch": True,
        "no_wayback_replay": True,
        "no_public_fanout": True,
        "automatic_decisions": False,
        "automatic_promotion": False,
        "reviewed_record_creation": False,
        "reviewed_master_mutation": False,
        "public_index_mutation": False,
        "candidate_index_store_mutation": False,
        "evidence_ledger_store_mutation": False,
        "reviewed_index_rebuild": False,
        "snapshot_refresh": False,
        "public_fanout": False,
        "network_during_prepare": False,
        "license_posture": DEFAULT_LICENSE_POSTURE,
        "review_items_file": REVIEW_ITEMS_FILE_NAME,
        "review_items_file_hash": f"sha256:{review_items_hash}",
        "decision_template_file": DECISION_TEMPLATE_FILE_NAME,
        "decision_template_file_hash": f"sha256:{decision_template_hash}",
        "previous_batch_id": previous_batch_id,
        "previous_batch_path": previous_batch_path,
        "diff_status": diff_status,
        "validation_status": validation_status,
        "blockers": blockers,
        "recommended_next_action": DEFAULT_RECOMMENDED_NEXT_ACTION,
        "review_item_id_pattern": f"review-item:{SOURCE_FAMILY}:<short_hash>",
        "operator_review_packet": OPERATOR_PACKET_FILE_NAME,
        "decision_guide": DECISION_GUIDE_FILE_NAME,
        "live_probe_statuses_preserved": evidence_manifest.get("live_probe_statuses_preserved", []),
        "source_index_path": [
            "IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00",
            "IA-SOURCE-OBSERVATION-CACHE-DELTA-00",
            "IA-CANDIDATE-INDEX-REFRESH-00",
            "IA-EVIDENCE-LEDGER-SUMMARY-00",
            "REVIEW-IA-CANDIDATES-BATCH-00",
            "REVIEWED-INDEX-REFRESH-FROM-IA-00",
        ],
    }


def build_decision_template(
    *,
    batch_id: str,
    review_items: Sequence[Mapping[str, Any]],
    generated_at: str,
) -> dict[str, Any]:
    decisions: list[dict[str, Any]] = []
    for item in sorted(review_items, key=lambda value: str(value.get("review_item_id") or "")):
        evidence_refs = _text_list(item.get("evidence_summary_refs"))
        absence_refs = [
            ref
            for ref in evidence_refs
            if int(item.get("absence_count") or 0) > 0 or int(item.get("near_miss_count") or 0) > 0
        ]
        decisions.append(
            {
                "review_item_id": item.get("review_item_id"),
                "candidate_id": item.get("candidate_id"),
                "decision": None,
                "reason": None,
                "evidence_refs": evidence_refs,
                "source_observation_refs": _text_list(item.get("source_observation_refs")),
                "absence_refs": absence_refs,
                "fallback_refs": [],
                "supersedes_review_item_id": None,
                "local_only_confirmed": False,
            }
        )
    return {
        "schema_version": DECISION_SCHEMA_VERSION,
        "batch_id": batch_id,
        "actor": "OPERATOR_REQUIRED",
        "generated_at": generated_at,
        "decisions": decisions,
    }


def validate_review_batch_manifest(
    manifest: Mapping[str, Any],
    *,
    review_items: Sequence[Mapping[str, Any]] | None = None,
) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_MANIFEST_FIELDS - set(manifest))
    if missing:
        errors.append(f"manifest missing required fields: {', '.join(missing)}")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if manifest.get("source_family") != SOURCE_FAMILY:
        errors.append(f"source_family must be {SOURCE_FAMILY}")
    if manifest.get("license_posture") != DEFAULT_LICENSE_POSTURE:
        errors.append(f"license_posture must be {DEFAULT_LICENSE_POSTURE}")
    if manifest.get("recommended_next_action") != DEFAULT_RECOMMENDED_NEXT_ACTION:
        errors.append(f"recommended_next_action must be {DEFAULT_RECOMMENDED_NEXT_ACTION}")
    for key in FORBIDDEN_FALSE_FLAGS:
        if key in manifest and manifest.get(key) is not True:
            errors.append(f"{key} must be true")
    for key in (
        "automatic_decisions",
        "automatic_promotion",
        "reviewed_record_creation",
        "reviewed_master_mutation",
        "public_index_mutation",
        "candidate_index_store_mutation",
        "evidence_ledger_store_mutation",
        "reviewed_index_rebuild",
        "snapshot_refresh",
        "public_fanout",
        "network_during_prepare",
    ):
        if manifest.get(key) is not False:
            errors.append(f"{key} must be false")
    for key in (
        "source_observation_count",
        "candidate_count",
        "evidence_summary_count",
        "review_item_count",
        "pending_review_count",
        "decisions_recorded",
        "review_ledger_events_written",
        "unsafe_record_count",
    ):
        if not isinstance(manifest.get(key), int) or int(manifest.get(key)) < 0:
            errors.append(f"{key} must be a non-negative integer")
    if manifest.get("decisions_supplied") is not False:
        errors.append("prepare manifest must have decisions_supplied false")
    if manifest.get("decisions_recorded") != 0:
        errors.append("prepare manifest must record zero decisions")
    if manifest.get("pending_review_count") != manifest.get("review_item_count"):
        errors.append("prepare manifest pending_review_count must equal review_item_count")
    if manifest.get("undecided_count") != manifest.get("review_item_count"):
        errors.append("prepare manifest undecided_count must equal review_item_count")
    if manifest.get("unsafe_record_count") != 0:
        errors.append("unsafe_record_count must be 0")
    if "WAITING_FOR_OPERATOR_REVIEW_DECISIONS" not in _text_list(manifest.get("blockers")):
        errors.append("prepare manifest must include WAITING_FOR_OPERATOR_REVIEW_DECISIONS blocker")
    if review_items is not None:
        errors.extend(_review_item_errors(review_items))
        if manifest.get("review_item_count") != len(review_items):
            errors.append("review_item_count does not match review item rows")
        if manifest.get("pending_review_count") != len(review_items):
            errors.append("pending_review_count does not match review item rows")
    for path, value in _walk_items(manifest):
        key = path.rsplit(".", 1)[-1]
        if key in FORBIDDEN_TRUE_FLAGS and value is True:
            errors.append(f"{path} must be false")
    errors.extend(_scan_unsafe_content(manifest, "$"))
    return sorted(dict.fromkeys(errors))


def load_review_batch_manifest(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    if not source.is_file():
        raise IACandidateReviewBatchError(f"review batch manifest not found: {source}")
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise IACandidateReviewBatchError(f"invalid review batch manifest JSON: {exc.msg}") from exc
    if not isinstance(payload, Mapping):
        raise IACandidateReviewBatchError("review batch manifest must be a JSON object")
    return dict(payload)


def load_review_items(batch_manifest_path: str | Path, manifest: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    manifest_path = Path(batch_manifest_path)
    active_manifest = dict(manifest or load_review_batch_manifest(manifest_path))
    items_path = _resolve_manifest_ref(manifest_path.parent, str(active_manifest.get("review_items_file") or REVIEW_ITEMS_FILE_NAME))
    rows = _read_jsonl(items_path, "review items")
    errors = _review_item_errors(rows)
    if errors:
        raise IACandidateReviewBatchError("; ".join(errors))
    return rows


def validate_batch_path(path: str | Path, *, strict: bool = False) -> dict[str, Any]:
    manifest_path = Path(path)
    try:
        manifest = load_review_batch_manifest(manifest_path)
        review_items = load_review_items(manifest_path, manifest)
        errors = validate_review_batch_manifest(manifest, review_items=review_items)
        if strict:
            expected_hash = manifest.get("review_items_file_hash")
            actual_hash = f"sha256:{_file_hash(_resolve_manifest_ref(manifest_path.parent, str(manifest.get('review_items_file') or REVIEW_ITEMS_FILE_NAME)))}"
            if expected_hash != actual_hash:
                errors.append("review_items_file_hash does not match review items file")
            template_hash = manifest.get("decision_template_file_hash")
            template_file = str(manifest.get("decision_template_file") or DECISION_TEMPLATE_FILE_NAME)
            actual_template_hash = f"sha256:{_file_hash(_resolve_manifest_ref(manifest_path.parent, template_file))}"
            if template_hash != actual_template_hash:
                errors.append("decision_template_file_hash does not match decision template file")
        status = "PASS" if not errors else "FAIL"
        return {
            "schema_version": "eureka.ia_candidate_review_batch_validation.v0",
            "status": status,
            "errors": sorted(dict.fromkeys(errors)),
            "batch_id": manifest.get("batch_id"),
            "review_item_count": manifest.get("review_item_count"),
            "pending_review_count": manifest.get("pending_review_count"),
            "decisions_supplied": manifest.get("decisions_supplied"),
            "decisions_recorded": manifest.get("decisions_recorded"),
            "automatic_decisions": manifest.get("automatic_decisions"),
            "reviewed_record_creation": manifest.get("reviewed_record_creation"),
            "public_index_mutation": manifest.get("public_index_mutation"),
            "unsafe_record_count": manifest.get("unsafe_record_count"),
        }
    except IACandidateReviewBatchError as exc:
        return {
            "schema_version": "eureka.ia_candidate_review_batch_validation.v0",
            "status": "FAIL",
            "errors": [str(exc)],
        }


def status_for_batch(path: str | Path) -> dict[str, Any]:
    manifest = load_review_batch_manifest(path)
    return {
        "schema_version": "eureka.ia_candidate_review_batch_status.v0",
        "status": manifest.get("validation_status"),
        "batch_id": manifest.get("batch_id"),
        "source_family": manifest.get("source_family"),
        "source_observations": manifest.get("source_observation_count"),
        "candidates": manifest.get("candidate_count"),
        "evidence_summaries": manifest.get("evidence_summary_count"),
        "review_items": manifest.get("review_item_count"),
        "pending_review_items": manifest.get("pending_review_count"),
        "review_group_counts": manifest.get("review_group_counts", {}),
        "attention_band_counts": manifest.get("attention_band_counts", {}),
        "missing_field_counts": manifest.get("missing_field_counts", {}),
        "insufficient_support_items": manifest.get("insufficient_support_item_count"),
        "absence_near_miss_items": manifest.get("absence_near_miss_item_count"),
        "live_derived_items": manifest.get("live_derived_item_count"),
        "fixture_derived_items": manifest.get("fixture_derived_item_count"),
        "decisions_supplied": manifest.get("decisions_supplied"),
        "decisions_recorded": manifest.get("decisions_recorded"),
        "automatic_decisions": manifest.get("automatic_decisions"),
        "automatic_promotion": manifest.get("automatic_promotion"),
        "reviewed_record_creation": manifest.get("reviewed_record_creation"),
        "reviewed_master_mutation": manifest.get("reviewed_master_mutation"),
        "public_index_mutation": manifest.get("public_index_mutation"),
        "recommended_next_action": manifest.get("recommended_next_action"),
        "blockers": manifest.get("blockers", []),
    }


def validate_decision_file(
    *,
    batch_manifest_path: str | Path,
    decision_file_path: str | Path,
    strict: bool = False,
) -> dict[str, Any]:
    errors: list[str] = []
    manifest = load_review_batch_manifest(batch_manifest_path)
    review_items = load_review_items(batch_manifest_path, manifest)
    items_by_id = {str(item.get("review_item_id") or ""): item for item in review_items}
    batch_id = str(manifest.get("batch_id") or "")
    decision_path = Path(decision_file_path)
    decisions_payload = _load_json_object(decision_path, "operator decision file")

    if decisions_payload.get("schema_version") != DECISION_SCHEMA_VERSION:
        errors.append(f"schema_version must be {DECISION_SCHEMA_VERSION}")
    if str(decisions_payload.get("batch_id") or "") != batch_id:
        errors.append("decision file batch_id does not match review batch")
    actor = str(decisions_payload.get("actor") or "").strip()
    if not actor or actor == "OPERATOR_REQUIRED":
        errors.append("actor is required")
    if _looks_like_generated_actor(actor):
        errors.append("actor must be an explicit human/operator, not AI/model/generated output")
    if any(key in decisions_payload for key in ("bulk_decision", "decision_for_all", "auto_decision", "inferred_decisions")):
        errors.append("bulk or inferred decision fields are not allowed")
    decisions = decisions_payload.get("decisions")
    if not isinstance(decisions, list):
        errors.append("decisions must be a list")
        decisions = []

    seen: set[str] = set()
    accepted_count = 0
    for index, entry in enumerate(decisions):
        if not isinstance(entry, Mapping):
            errors.append(f"decisions[{index}] must be an object")
            continue
        review_item_id = str(entry.get("review_item_id") or "").strip()
        candidate_id = str(entry.get("candidate_id") or "").strip()
        decision = str(entry.get("decision") or "").strip()
        if not review_item_id:
            errors.append(f"decisions[{index}].review_item_id is required")
            continue
        if review_item_id in seen:
            errors.append(f"duplicate review item decision: {review_item_id}")
        seen.add(review_item_id)
        item = items_by_id.get(review_item_id)
        if item is None:
            errors.append(f"unknown review item id: {review_item_id}")
            continue
        if candidate_id != str(item.get("candidate_id") or ""):
            errors.append(f"candidate_id does not match review item: {review_item_id}")
        if decision not in REVIEW_LEDGER_DECISIONS:
            errors.append(f"unsupported decision for {review_item_id}: {decision or '<missing>'}")
            continue
        if decision in REASON_REQUIRED_DECISIONS and not str(entry.get("reason") or "").strip():
            errors.append(f"reason is required for {decision}: {review_item_id}")
        if decision == "supersede":
            supersedes = str(entry.get("supersedes_review_item_id") or "").strip()
            if not supersedes:
                errors.append(f"supersede requires supersedes_review_item_id: {review_item_id}")
            elif supersedes not in items_by_id:
                errors.append(f"supersedes_review_item_id is unknown: {supersedes}")
            elif supersedes == review_item_id:
                errors.append(f"supersede target must differ from review item: {review_item_id}")
        if decision == "promote" and entry.get("local_only_confirmed") is not True:
            errors.append(f"promote requires local_only_confirmed true: {review_item_id}")
        if not _has_reference_or_rationale(entry):
            errors.append(f"decision requires refs or rationale: {review_item_id}")
        accepted_count += 1

    status = "PASS" if not errors else "FAIL"
    omitted_count = max(0, len(review_items) - len(seen))
    return {
        "schema_version": DECISION_VALIDATION_SCHEMA_VERSION,
        "status": status,
        "errors": sorted(dict.fromkeys(errors)),
        "batch_id": batch_id,
        "decision_file": _safe_path_label(decision_path),
        "decision_file_hash": f"sha256:{_file_hash(decision_path)}" if decision_path.is_file() else None,
        "actor": actor if actor and actor != "OPERATOR_REQUIRED" else None,
        "decisions_supplied": bool(decisions),
        "decisions_validated": accepted_count if status == "PASS" else 0,
        "decision_count": len(decisions),
        "omitted_pending_count": omitted_count,
        "subset_decision_file": omitted_count > 0,
        "missing_decision_posture": "pending_not_inferred",
        "strict": bool(strict),
    }


def validate_tranche_decision_file(
    *,
    tranche_manifest_path: str | Path,
    decision_file_path: str | Path,
    strict: bool = False,
) -> dict[str, Any]:
    errors: list[str] = []
    manifest = load_tranche_manifest(tranche_manifest_path)
    tranche_items = load_tranche_items(tranche_manifest_path, manifest)
    items_by_id = {str(item.get("review_item_id") or ""): item for item in tranche_items}
    decision_path = Path(decision_file_path)
    decisions_payload = _load_json_object(decision_path, "operator tranche decision file")

    if decisions_payload.get("schema_version") != TRANCHE_DECISION_SCHEMA_VERSION:
        errors.append(f"schema_version must be {TRANCHE_DECISION_SCHEMA_VERSION}")
    if str(decisions_payload.get("batch_id") or "") != str(manifest.get("source_batch_id") or ""):
        errors.append("decision file batch_id does not match tranche source batch")
    if str(decisions_payload.get("tranche_id") or "") != str(manifest.get("tranche_id") or ""):
        errors.append("decision file tranche_id does not match tranche manifest")
    actor = str(decisions_payload.get("actor") or "").strip()
    if not actor or actor == "OPERATOR_REQUIRED":
        errors.append("actor is required")
    if _looks_like_generated_actor(actor):
        errors.append("actor must be an explicit human/operator, not AI/model/generated output")
    if any(key in decisions_payload for key in ("bulk_decision", "decision_for_all", "auto_decision", "inferred_decisions")):
        errors.append("bulk or inferred decision fields are not allowed")

    decisions = decisions_payload.get("decisions")
    if not isinstance(decisions, list):
        errors.append("decisions must be a list")
        decisions = []
    seen: set[str] = set()
    accepted_count = 0
    for index, entry in enumerate(decisions):
        if not isinstance(entry, Mapping):
            errors.append(f"decisions[{index}] must be an object")
            continue
        review_item_id = str(entry.get("review_item_id") or "").strip()
        candidate_id = str(entry.get("candidate_id") or "").strip()
        decision = str(entry.get("decision") or "").strip()
        if not review_item_id:
            errors.append(f"decisions[{index}].review_item_id is required")
            continue
        if review_item_id in seen:
            errors.append(f"duplicate review item decision: {review_item_id}")
        seen.add(review_item_id)
        item = items_by_id.get(review_item_id)
        if item is None:
            errors.append(f"unknown review item id for tranche: {review_item_id}")
            continue
        if candidate_id != str(item.get("candidate_id") or ""):
            errors.append(f"candidate_id does not match tranche review item: {review_item_id}")
        if decision == "promote":
            errors.append(f"promote is not allowed for this tranche: {review_item_id}")
            continue
        if decision not in TRANCHE_ALLOWED_DECISIONS:
            errors.append(f"unsupported tranche decision for {review_item_id}: {decision or '<missing>'}")
            continue
        if decision in REASON_REQUIRED_DECISIONS and not str(entry.get("reason") or "").strip():
            errors.append(f"reason is required for {decision}: {review_item_id}")
        if decision == "supersede":
            supersedes = str(entry.get("supersedes_review_item_id") or "").strip()
            if not supersedes:
                errors.append(f"supersede requires supersedes_review_item_id: {review_item_id}")
            elif supersedes not in items_by_id:
                errors.append(f"supersedes_review_item_id is outside this tranche: {supersedes}")
            elif supersedes == review_item_id:
                errors.append(f"supersede target must differ from review item: {review_item_id}")
        if entry.get("promotion_eligible") is not False:
            errors.append(f"promotion_eligible must be false for this tranche: {review_item_id}")
        blockers = _text_list(entry.get("promotion_blockers"))
        for blocker in TRANCHE_PROMOTION_BLOCKERS:
            if blocker not in blockers:
                errors.append(f"promotion_blockers must include {blocker}: {review_item_id}")
        if not _has_reference_or_rationale(entry):
            errors.append(f"decision requires refs or rationale: {review_item_id}")
        accepted_count += 1

    status = "PASS" if not errors else "FAIL"
    return {
        "schema_version": "eureka.ia_candidate_review_tranche_decision_validation.v0",
        "status": status,
        "errors": sorted(dict.fromkeys(errors)),
        "tranche_id": manifest.get("tranche_id"),
        "source_batch_id": manifest.get("source_batch_id"),
        "decision_file": _safe_path_label(decision_path),
        "decision_file_hash": f"sha256:{_file_hash(decision_path)}" if decision_path.is_file() else None,
        "actor": actor if actor and actor != "OPERATOR_REQUIRED" else None,
        "decisions_supplied": bool(decisions),
        "decisions_validated": accepted_count if status == "PASS" else 0,
        "decision_count": len(decisions),
        "omitted_pending_count": max(0, len(tranche_items) - len(seen)),
        "subset_decision_file": len(seen) < len(tranche_items),
        "promotion_allowed": False,
        "strict": bool(strict),
    }


def record_decisions(
    *,
    batch_manifest_path: str | Path,
    decision_file_path: str | Path,
    review_store_path: str | Path,
    strict: bool = False,
) -> dict[str, Any]:
    validation = validate_decision_file(
        batch_manifest_path=batch_manifest_path,
        decision_file_path=decision_file_path,
        strict=strict,
    )
    if validation["status"] != "PASS":
        raise IACandidateReviewBatchError("; ".join(str(error) for error in validation.get("errors", [])))

    manifest = load_review_batch_manifest(batch_manifest_path)
    review_items = load_review_items(batch_manifest_path, manifest)
    items_by_id = {str(item.get("review_item_id") or ""): item for item in review_items}
    decisions_payload = _load_json_object(Path(decision_file_path), "operator decision file")
    actor = str(decisions_payload.get("actor") or "").strip()
    records = list(decisions_payload.get("decisions") or [])
    results: list[dict[str, Any]] = []
    decision_counts: Counter[str] = Counter()

    with ReviewQueueStore.open(review_store_path) as store:
        store.init()
        for entry in records:
            review_item_id = str(entry.get("review_item_id") or "").strip()
            item = items_by_id[review_item_id]
            if store.list_decisions(review_item_id, limit=1000):
                raise IACandidateReviewBatchError(f"decision already recorded for review item: {review_item_id}")
            if store.get_review_item(review_item_id) is None:
                store.enqueue_review_item(_review_queue_item(item))
            request = ReviewLedgerDecisionRequest(
                review_item_id=review_item_id,
                decision=str(entry.get("decision") or ""),
                actor=actor,
                reason=str(entry.get("reason") or "").strip() or None,
                evidence_refs=tuple(_text_list(entry.get("evidence_refs"))),
                source_observation_refs=tuple(_text_list(entry.get("source_observation_refs"))),
                absence_refs=tuple(_text_list(entry.get("absence_refs"))),
                fallback_refs=tuple(_text_list(entry.get("fallback_refs"))),
                supersedes_review_item_id=str(entry.get("supersedes_review_item_id") or "").strip() or None,
                local_only_confirmed=bool(entry.get("local_only_confirmed")),
            )
            try:
                result = record_review_ledger_decision(store, request).to_dict()
            except ReviewLedgerError as exc:
                raise IACandidateReviewBatchError(str(exc)) from exc
            results.append(result)
            decision_counts[str(entry.get("decision") or "")] += 1
        summary = store.summarize().to_dict()

    return {
        "schema_version": RECORD_DECISIONS_SCHEMA_VERSION,
        "status": "PASS",
        "batch_id": manifest.get("batch_id"),
        "batch_manifest": _safe_path_label(Path(batch_manifest_path)),
        "batch_manifest_hash": f"sha256:{_file_hash(Path(batch_manifest_path))}",
        "decision_file": _safe_path_label(Path(decision_file_path)),
        "decision_file_hash": validation.get("decision_file_hash"),
        "review_store": str(review_store_path),
        "actor": actor,
        "decisions_recorded": len(results),
        "review_ledger_events_written": len(results),
        "decision_counts": dict(sorted(decision_counts.items())),
        "omitted_pending_count": validation.get("omitted_pending_count"),
        "results": results,
        "review_store_summary": summary,
        "reviewed_record_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "reviewed_index_rebuild": False,
        "snapshot_refresh": False,
        "public_projection": False,
    }


def render_markdown_summary(
    manifest: Mapping[str, Any],
    *,
    review_items: Sequence[Mapping[str, Any]] | None = None,
) -> str:
    group_counts = json.dumps(manifest.get("review_group_counts", {}), sort_keys=True)
    band_counts = json.dumps(manifest.get("attention_band_counts", {}), sort_keys=True)
    missing_counts = json.dumps(manifest.get("missing_field_counts", {}), sort_keys=True)
    lines = [
        "# IA Candidate Review Batch",
        "",
        f"Status: `{manifest.get('validation_status')}`",
        "",
        "## Summary",
        "",
        f"- batch id: `{manifest.get('batch_id')}`",
        f"- source observations consumed: {manifest.get('source_observation_count')}",
        f"- candidates consumed: {manifest.get('candidate_count')}",
        f"- evidence summaries consumed: {manifest.get('evidence_summary_count')}",
        f"- review items prepared: {manifest.get('review_item_count')}",
        f"- pending review items: {manifest.get('pending_review_count')}",
        f"- decisions supplied: {str(manifest.get('decisions_supplied')).lower()}",
        f"- decisions recorded: {manifest.get('decisions_recorded')}",
        f"- blockers: {', '.join(_text_list(manifest.get('blockers'))) or 'none'}",
        "",
        "## Review Organization",
        "",
        f"- review group counts: `{group_counts}`",
        f"- attention band counts: `{band_counts}`",
        f"- missing field counts: `{missing_counts}`",
        f"- insufficient-support items: {manifest.get('insufficient_support_item_count')}",
        f"- absence/near-miss items: {manifest.get('absence_near_miss_item_count')}",
        "",
        "## Boundary",
        "",
        "- automatic decisions: false",
        "- automatic promotion: false",
        "- reviewed records created: false",
        "- reviewed/master mutation: false",
        "- public-index mutation: false",
        "- candidate-index store mutation: false",
        "- evidence-ledger store mutation: false",
        "- snapshot refresh: false",
        "- network/provider calls: false",
        "",
        "Recommended next action: operator review required.",
    ]
    if review_items:
        lines.extend(["", "## First Items", ""])
        for item in sorted(review_items, key=lambda value: (-int(value.get("review_attention_score") or 0), str(value.get("review_item_id") or "")))[:10]:
            lines.append(
                f"- `{item.get('review_item_id')}` `{item.get('review_group')}` "
                f"score={item.get('review_attention_score')} candidate=`{item.get('candidate_id')}` - Decision pending - no outcome inferred"
            )
    return "\n".join(lines) + "\n"


def render_operator_review_packet(
    manifest: Mapping[str, Any],
    *,
    review_items: Sequence[Mapping[str, Any]],
) -> str:
    lines = [
        "# Operator Review Packet - IA Candidates",
        "",
        "Decision pending - no outcome inferred.",
        "",
        "## Batch Overview",
        "",
        f"- batch id: `{manifest.get('batch_id')}`",
        f"- total candidates: {manifest.get('candidate_count')}",
        f"- review items: {manifest.get('review_item_count')}",
        f"- group counts: `{json.dumps(manifest.get('review_group_counts', {}), sort_keys=True)}`",
        f"- attention bands: `{json.dumps(manifest.get('attention_band_counts', {}), sort_keys=True)}`",
        f"- evidence summaries: {manifest.get('evidence_summary_count')}",
        f"- insufficient-support items: {manifest.get('insufficient_support_item_count')}",
        f"- absence/near-miss items: {manifest.get('absence_near_miss_item_count')}",
        f"- live-derived items: {manifest.get('live_derived_item_count')}",
        f"- fixture-derived items: {manifest.get('fixture_derived_item_count')}",
        "- automatic decisions: false",
        "",
    ]
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for item in review_items:
        grouped[str(item.get("review_group") or "mixed_or_ambiguous")].append(item)
    for group in sorted(grouped):
        lines.extend([f"## {group}", ""])
        ordered = sorted(
            grouped[group],
            key=lambda value: (-int(value.get("review_attention_score") or 0), str(value.get("review_item_id") or "")),
        )
        for item in ordered:
            title = _display(_text_list(item.get("title_name_hints")))
            locator_labels = _display([str(ref.get("label") or ref.get("value_hash") or "") for ref in item.get("source_locator_hints", []) if isinstance(ref, Mapping)])
            lines.extend(
                [
                    f"### {item.get('review_item_id')}",
                    "",
                    f"- candidate id: `{item.get('candidate_id')}`",
                    f"- originating query: {_display(_text_list(item.get('query_seed_refs')))}",
                    f"- title/name hints: {title}",
                    f"- object/platform/date/version hints: {_display(_text_list(item.get('object_type_hints')) + _text_list(item.get('platform_hints')) + _text_list(item.get('date_version_hints')))}",
                    f"- provider modes: {_display(_text_list(item.get('provider_modes')))}",
                    f"- source locator summary: {locator_labels}",
                    f"- evidence type counts: `{json.dumps(item.get('evidence_type_counts', {}), sort_keys=True)}`",
                    f"- support counts: `{json.dumps(item.get('support_posture_counts', {}), sort_keys=True)}`",
                    f"- absence/near-miss: absence={item.get('absence_count')} near_miss={item.get('near_miss_count')}",
                    f"- missing fields: {_display(_text_list(item.get('missing_field_flags')))}",
                    f"- ambiguity/conflict flags: {_display(_text_list(item.get('ambiguity_flags')) + ['contradiction'] * int(item.get('contradiction_count') or 0))}",
                    f"- source-observation refs: {_display(_text_list(item.get('source_observation_refs')))}",
                    f"- evidence-summary refs: {_display(_text_list(item.get('evidence_summary_refs')))}",
                    f"- review attention band: `{item.get('review_attention_band')}`",
                    "- Decision pending - no outcome inferred",
                    "",
                ]
            )
    return "\n".join(lines)


def render_operator_tranche_packet(
    manifest: Mapping[str, Any],
    *,
    tranche_items: Sequence[Mapping[str, Any]],
) -> str:
    lines = [
        "# Operator Review Tranche 01 - IA Candidates",
        "",
        "Decision pending - no outcome inferred.",
        "",
        "## Overview",
        "",
        f"- tranche id: `{manifest.get('tranche_id')}`",
        f"- source batch id: `{manifest.get('source_batch_id')}`",
        f"- selection policy: `{manifest.get('selection_policy')}`",
        f"- selected items: {manifest.get('selected_count')}",
        f"- query seed counts: `{json.dumps(manifest.get('query_seed_counts', {}), sort_keys=True)}`",
        f"- attention bands: `{json.dumps(manifest.get('attention_band_counts', {}), sort_keys=True)}`",
        f"- fixture-derived items: {manifest.get('fixture_derived_count')}",
        f"- live-derived items: {manifest.get('live_derived_count')}",
        f"- promotion eligible: {manifest.get('promotion_eligible_count')}",
        f"- promotion blocked: {manifest.get('promotion_blocked_count')}",
        "- automatic decisions: false",
        "- automatic promotion: false",
        "",
    ]
    for index, item in enumerate(tranche_items, start=1):
        lines.extend(
            [
                f"## {index}. {item.get('review_item_id')}",
                "",
                f"- candidate id: `{item.get('candidate_id')}`",
                f"- originating query: {_display(_text_list(item.get('query_seed_refs')))}",
                f"- title/name hints: {_display(_text_list(item.get('title_name_hints')))}",
                f"- object-type hints: {_display(_text_list(item.get('object_type_hints')))}",
                f"- platform/date/version hints: {_display(_text_list(item.get('platform_hints')) + _text_list(item.get('date_version_hints')))}",
                f"- representation/member hints: {_display(_text_list(item.get('representation_member_hints')))}",
                f"- source locator summary: {_locator_summary(item)}",
                f"- provider modes: {_display(_text_list(item.get('provider_modes')))}",
                f"- evidence type counts: `{json.dumps(item.get('evidence_type_counts', {}), sort_keys=True)}`",
                f"- support-posture counts: `{json.dumps(item.get('support_posture_counts', {}), sort_keys=True)}`",
                f"- missing fields: {_display(_text_list(item.get('missing_field_flags')))}",
                f"- ambiguity flags: {_display(_text_list(item.get('ambiguity_flags')))}",
                f"- attention band: `{item.get('review_attention_band')}`",
                f"- source-observation refs: {_display(_text_list(item.get('source_observation_refs')))}",
                f"- evidence-summary refs: {_display(_text_list(item.get('evidence_summary_refs')))}",
                f"- promotion eligible: {str(item.get('promotion_eligible')).lower()}",
                f"- promotion blockers: {_display(_text_list(item.get('promotion_blockers')))}",
                "- Decision pending - no outcome inferred.",
                "",
            ]
        )
    return "\n".join(lines)


def render_decision_guide(manifest: Mapping[str, Any]) -> str:
    decisions = ", ".join(REVIEW_LEDGER_DECISIONS)
    return (
        "# Operator Decision Guide\n\n"
        "Use `operator_decision_template.json` as a starting point, then fill only the items you have inspected.\n\n"
        "Supported decisions: "
        f"{decisions}.\n\n"
        "Rules:\n\n"
        "- actor is required and must identify the operator\n"
        "- each included item must have an explicit decision\n"
        "- omitted items remain pending\n"
        "- reject, supersede, policy-blocked, and request-more-evidence require a reason\n"
        "- supersede requires `supersedes_review_item_id`\n"
        "- promote requires `local_only_confirmed: true`\n"
        "- each decision needs evidence refs, source-observation refs, absence refs, fallback refs, or rationale\n"
        "- review-ledger decisions do not create reviewed records or rebuild indexes\n\n"
        f"Batch id: `{manifest.get('batch_id')}`\n"
    )


def render_tranche_decision_guide(manifest: Mapping[str, Any]) -> str:
    return (
        "# Operator Decision Guide - Tranche 01\n\n"
        "Fill only explicitly reviewed items. Omitted items remain pending.\n\n"
        "Allowed Tranche 01 decisions:\n\n"
        "- reject\n"
        "- supersede\n"
        "- mark_near_miss\n"
        "- mark_need\n"
        "- mark_policy_blocked\n"
        "- request_more_evidence\n\n"
        "Promotion is blocked for this tranche because all selected items are fixture-derived and independent external evidence is missing.\n\n"
        "Rules:\n\n"
        "- actor is required and must identify the local operator\n"
        "- no decision may be preselected by automation\n"
        "- promote is not allowed for Tranche 01\n"
        "- each included item needs evidence refs, source-observation refs, absence refs, fallback refs, or rationale\n"
        "- review-ledger decisions do not create reviewed records or rebuild indexes\n\n"
        f"Tranche id: `{manifest.get('tranche_id')}`\n"
    )


def validate_decision_payload_for_template(payload: Mapping[str, Any]) -> list[str]:
    """Public helper for tests that need template-level validation semantics."""

    errors: list[str] = []
    if payload.get("actor") == "OPERATOR_REQUIRED":
        errors.append("actor is required")
    for index, entry in enumerate(payload.get("decisions", []) or []):
        if isinstance(entry, Mapping) and entry.get("decision") is None:
            errors.append(f"decisions[{index}].decision is required")
    return errors


def _tranche_item(item: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(item)
    payload["tranche_status"] = "pending_operator_decision"
    payload["promotion_eligible"] = False
    payload["promotion_blockers"] = list(TRANCHE_PROMOTION_BLOCKERS)
    payload["allowed_decisions"] = list(TRANCHE_ALLOWED_DECISIONS)
    payload["operator_statement"] = "Decision pending - no outcome inferred"
    return payload


def _review_queue_item(item: Mapping[str, Any]) -> ReviewItemRecord:
    now = str(item.get("generated_at") or "")
    score = int(item.get("review_attention_score") or 0)
    priority = max(1, 100 - min(score, 90))
    payload = {
        "schema_version": "eureka.ia_candidate_review_queue_item.v0",
        "batch_id": item.get("batch_id"),
        "candidate_id": item.get("candidate_id"),
        "source_family": item.get("source_family"),
        "query_seed_refs": _text_list(item.get("query_seed_refs")),
        "source_observation_refs": _text_list(item.get("source_observation_refs")),
        "evidence_refs": _text_list(item.get("evidence_summary_refs")),
        "review_required": True,
        "self_promotion_allowed": False,
        "decision_posture": "operator_required",
    }
    return ReviewItemRecord(
        review_item_id=str(item.get("review_item_id") or ""),
        subject_kind="ia_metadata_candidate",
        subject_id=str(item.get("candidate_id") or ""),
        queue_status=ReviewQueueStatus.NEEDS_REVIEW,
        priority=priority,
        evidence_id=_text_list(item.get("evidence_summary_refs"))[0] if _text_list(item.get("evidence_summary_refs")) else None,
        source_cache_entry_id=None,
        summary=f"IA metadata candidate review item {item.get('candidate_id')}",
        payload=payload,
        limitations=(
            "review batch item is not accepted truth",
            "review ledger decision required before reviewed projection",
        ),
        warnings=tuple(_text_list(item.get("missing_field_flags"))),
        created_at=now,
        updated_at=now,
    )


def _tranche_item_errors(items: Sequence[Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    ids: list[str] = []
    for index, item in enumerate(items):
        ids.append(str(item.get("review_item_id") or ""))
        if item.get("review_group") != "evidence_rich_pending_review":
            errors.append(f"tranche_items[{index}].review_group must be evidence_rich_pending_review")
        if item.get("decision") is not None:
            errors.append(f"tranche_items[{index}].decision must be null")
        if item.get("decision_actor") is not None:
            errors.append(f"tranche_items[{index}].decision_actor must be null")
        if item.get("review_status") != "pending":
            errors.append(f"tranche_items[{index}].review_status must be pending")
        if not _text_list(item.get("candidate_id")):
            errors.append(f"tranche_items[{index}].candidate_id is required")
        if not _text_list(item.get("source_observation_refs")):
            errors.append(f"tranche_items[{index}].source_observation_refs are required")
        if not _text_list(item.get("evidence_summary_refs")):
            errors.append(f"tranche_items[{index}].evidence_summary_refs are required")
        if item.get("promotion_eligible") is not False:
            errors.append(f"tranche_items[{index}].promotion_eligible must be false")
        blockers = _text_list(item.get("promotion_blockers"))
        for blocker in TRANCHE_PROMOTION_BLOCKERS:
            if blocker not in blockers:
                errors.append(f"tranche_items[{index}].promotion_blockers must include {blocker}")
        if tuple(_text_list(item.get("allowed_decisions"))) != TRANCHE_ALLOWED_DECISIONS:
            errors.append(f"tranche_items[{index}].allowed_decisions must match Tranche 01 allowed decisions")
        if "fixture" not in _text_list(item.get("provider_modes")):
            errors.append(f"tranche_items[{index}] must be fixture-derived")
        if "live" in _text_list(item.get("provider_modes")):
            errors.append(f"tranche_items[{index}] must not be live-derived")
        if int(item.get("contradiction_count") or 0) != 0:
            errors.append(f"tranche_items[{index}].contradiction_count must be 0")
        if _text_list(item.get("source_unavailable_flags")):
            errors.append(f"tranche_items[{index}].source_unavailable_flags must be empty")
        errors.extend(f"tranche_items[{index}].{error}" for error in _scan_unsafe_content(item, "$"))
    if len(ids) != len(set(ids)):
        errors.append("tranche review item ids must be unique")
    return sorted(dict.fromkeys(errors))


def _tranche_template_errors(
    template: Mapping[str, Any],
    *,
    manifest: Mapping[str, Any],
    items: Sequence[Mapping[str, Any]],
) -> list[str]:
    errors: list[str] = []
    if template.get("schema_version") != TRANCHE_DECISION_SCHEMA_VERSION:
        errors.append(f"tranche decision template schema_version must be {TRANCHE_DECISION_SCHEMA_VERSION}")
    if template.get("batch_id") != manifest.get("source_batch_id"):
        errors.append("tranche decision template batch_id does not match source batch")
    if template.get("tranche_id") != manifest.get("tranche_id"):
        errors.append("tranche decision template tranche_id does not match tranche manifest")
    if template.get("actor") != "OPERATOR_REQUIRED":
        errors.append("tranche decision template actor must be OPERATOR_REQUIRED")
    decisions = template.get("decisions")
    if not isinstance(decisions, list):
        errors.append("tranche decision template decisions must be a list")
        return errors
    item_ids = {str(item.get("review_item_id") or "") for item in items}
    candidate_by_item = {str(item.get("review_item_id") or ""): str(item.get("candidate_id") or "") for item in items}
    if len(decisions) != len(items):
        errors.append("tranche decision template decision count must match selected items")
    for index, decision in enumerate(decisions):
        if not isinstance(decision, Mapping):
            errors.append(f"tranche decision template decisions[{index}] must be an object")
            continue
        review_item_id = str(decision.get("review_item_id") or "")
        if review_item_id not in item_ids:
            errors.append(f"tranche decision template has unknown review item: {review_item_id}")
        if str(decision.get("candidate_id") or "") != candidate_by_item.get(review_item_id):
            errors.append(f"tranche decision template candidate mismatch: {review_item_id}")
        if decision.get("decision") is not None:
            errors.append(f"tranche decision template decision must be null: {review_item_id}")
        if decision.get("reason") is not None:
            errors.append(f"tranche decision template reason must be null: {review_item_id}")
        if decision.get("local_only_confirmed") is not False:
            errors.append(f"tranche decision template local_only_confirmed must be false: {review_item_id}")
        if decision.get("promotion_eligible") is not False:
            errors.append(f"tranche decision template promotion_eligible must be false: {review_item_id}")
        blockers = _text_list(decision.get("promotion_blockers"))
        for blocker in TRANCHE_PROMOTION_BLOCKERS:
            if blocker not in blockers:
                errors.append(f"tranche decision template promotion blockers missing {blocker}: {review_item_id}")
    return sorted(dict.fromkeys(errors))


def _input_errors(
    *,
    source_manifest: Mapping[str, Any],
    candidate_manifest: Mapping[str, Any],
    evidence_manifest: Mapping[str, Any],
    source_delta_hash: str,
    candidate_delta_hash: str,
    source_observations: Sequence[Mapping[str, Any]],
    candidates: Sequence[Mapping[str, Any]],
    evidence_summaries: Sequence[Mapping[str, Any]],
) -> list[str]:
    errors: list[str] = []
    source_hash = f"sha256:{source_delta_hash}"
    candidate_hash = f"sha256:{candidate_delta_hash}"
    if candidate_manifest.get("input_source_observation_delta_hash") != source_hash:
        errors.append("candidate delta source-observation input hash does not match source delta manifest")
    if evidence_manifest.get("input_source_observation_delta_hash") != source_hash:
        errors.append("evidence delta source-observation input hash does not match source delta manifest")
    if evidence_manifest.get("input_candidate_index_delta_hash") != candidate_hash:
        errors.append("evidence delta candidate-index input hash does not match candidate delta manifest")
    if int(source_manifest.get("observation_count") or source_manifest.get("source_observation_count") or 0) != len(source_observations):
        errors.append("source observation manifest count does not match source observations")
    if int(candidate_manifest.get("candidate_count") or 0) != len(candidates):
        errors.append("candidate manifest count does not match candidates")
    if int(evidence_manifest.get("evidence_summary_count") or 0) != len(evidence_summaries):
        errors.append("evidence manifest count does not match evidence summaries")
    for manifest_name, manifest in (
        ("source observation", source_manifest),
        ("candidate", candidate_manifest),
        ("evidence", evidence_manifest),
    ):
        if manifest.get("license_posture") != DEFAULT_LICENSE_POSTURE:
            errors.append(f"{manifest_name} license_posture must be {DEFAULT_LICENSE_POSTURE}")
        for key in ("no_downloads", "no_file_fetch", "no_wayback_replay", "no_public_fanout"):
            if manifest.get(key) is not True:
                errors.append(f"{manifest_name} {key} must be true")
        for key in (
            "reviewed_master_mutation",
            "public_index_mutation",
            "candidate_index_store_mutation",
            "evidence_ledger_store_mutation",
            "review_promotion_mutation",
            "accepted_truth_created",
        ):
            if key in manifest and manifest.get(key) is True:
                errors.append(f"{manifest_name} {key} must be false")
    source_ids = {str(item.get("observation_id") or "") for item in source_observations}
    candidate_ids = {str(item.get("candidate_id") or "") for item in candidates}
    for candidate in candidates:
        for ref in _text_list(candidate.get("source_observation_refs")):
            if ref not in source_ids:
                errors.append(f"candidate has orphan source observation ref: {ref}")
    for summary in evidence_summaries:
        for ref in _text_list(summary.get("source_observation_refs")):
            if ref not in source_ids:
                errors.append(f"evidence summary has orphan source observation ref: {ref}")
        for ref in _text_list(summary.get("candidate_refs")):
            if ref not in candidate_ids:
                errors.append(f"evidence summary has orphan candidate ref: {ref}")
    return sorted(dict.fromkeys(errors))


def _review_item_errors(
    review_items: Sequence[Mapping[str, Any]],
    *,
    candidate_ids: set[str] | None = None,
    source_observation_ids: set[str] | None = None,
    evidence_summary_ids: set[str] | None = None,
) -> list[str]:
    errors: list[str] = []
    ids: list[str] = []
    for index, item in enumerate(review_items):
        missing = sorted(REQUIRED_REVIEW_ITEM_FIELDS - set(item))
        if missing:
            errors.append(f"review_items[{index}] missing required fields: {', '.join(missing)}")
        if item.get("schema_version") != REVIEW_ITEM_SCHEMA_VERSION:
            errors.append(f"review_items[{index}].schema_version must be {REVIEW_ITEM_SCHEMA_VERSION}")
        item_id = str(item.get("review_item_id") or "")
        ids.append(item_id)
        if not item_id.startswith(f"review-item:{SOURCE_FAMILY}:"):
            errors.append(f"review_items[{index}].review_item_id has invalid pattern")
        if item.get("candidate_status") != "provisional":
            errors.append(f"review_items[{index}].candidate_status must be provisional")
        if item.get("review_status") != "pending":
            errors.append(f"review_items[{index}].review_status must be pending")
        if item.get("source_family") != SOURCE_FAMILY:
            errors.append(f"review_items[{index}].source_family must be {SOURCE_FAMILY}")
        if item.get("decision") is not None:
            errors.append(f"review_items[{index}].decision must be null in prepare mode")
        if item.get("decision_actor") is not None:
            errors.append(f"review_items[{index}].decision_actor must be null in prepare mode")
        if item.get("decision_reason") is not None:
            errors.append(f"review_items[{index}].decision_reason must be null in prepare mode")
        for key in (
            "review_required",
            "self_promotion_allowed",
            "reviewed_record_created",
            "reviewed_index_mutated",
            "public_index_mutated",
            "master_index_mutated",
        ):
            expected = True if key == "review_required" else False
            if item.get(key) is not expected:
                errors.append(f"review_items[{index}].{key} must be {str(expected).lower()}")
        if item.get("review_group") not in ALLOWED_REVIEW_GROUPS:
            errors.append(f"review_items[{index}].review_group is not allowed")
        if not isinstance(item.get("review_attention_score"), int) or int(item.get("review_attention_score") or 0) < 0:
            errors.append(f"review_items[{index}].review_attention_score must be a non-negative integer")
        if item.get("review_attention_band") not in {"standard_attention", "medium_attention", "high_attention"}:
            errors.append(f"review_items[{index}].review_attention_band is not allowed")
        if candidate_ids is not None and str(item.get("candidate_id") or "") not in candidate_ids:
            errors.append(f"review_items[{index}] has orphan candidate_id")
        if source_observation_ids is not None:
            for ref in _text_list(item.get("source_observation_refs")):
                if ref not in source_observation_ids:
                    errors.append(f"review_items[{index}] has orphan source observation ref: {ref}")
        if evidence_summary_ids is not None:
            for ref in _text_list(item.get("evidence_summary_refs")):
                if ref not in evidence_summary_ids:
                    errors.append(f"review_items[{index}] has orphan evidence summary ref: {ref}")
        for path, value in _walk_items(item):
            key = path.rsplit(".", 1)[-1]
            if key in FORBIDDEN_TRUE_FLAGS and value is True:
                errors.append(f"review_items[{index}].{path} must be false")
        errors.extend(f"review_items[{index}].{error}" for error in _scan_unsafe_content(item, "$"))
    if len(ids) != len(set(ids)):
        errors.append("review item ids must be unique")
    return sorted(dict.fromkeys(errors))


def _load_evidence_summaries(manifest_path: Path, manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    evidence_file = str(manifest.get("evidence_summary_file") or "evidence_summaries.jsonl")
    evidence_path = _resolve_manifest_ref(manifest_path.parent, evidence_file)
    return _read_jsonl(evidence_path, "evidence summaries")


def _load_previous_manifest(path: Path) -> Mapping[str, Any] | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _read_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    if not path.is_file():
        raise IACandidateReviewBatchError(f"{label} file not found: {path}")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise IACandidateReviewBatchError(f"{path}:{line_number}: invalid JSONL row: {exc.msg}") from exc
        if not isinstance(payload, Mapping):
            raise IACandidateReviewBatchError(f"{path}:{line_number}: JSONL row must be an object")
        rows.append(dict(payload))
    return rows


def _load_json_object(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise IACandidateReviewBatchError(f"{label} not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise IACandidateReviewBatchError(f"invalid {label} JSON: {exc.msg}") from exc
    if not isinstance(payload, Mapping):
        raise IACandidateReviewBatchError(f"{label} must be a JSON object")
    return dict(payload)


def _write_jsonl(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def _file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stable_digest(value: Any, length: int = 16) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")).hexdigest()[:length]


def _safe_path_label(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _resolve_manifest_ref(base_dir: Path, label: str) -> Path:
    candidate = Path(label)
    if candidate.is_absolute():
        return candidate
    by_base = base_dir / candidate
    if by_base.exists():
        return by_base
    by_cwd = Path.cwd() / candidate
    if by_cwd.exists():
        return by_cwd
    return by_base


def _generated_at(*manifests: Mapping[str, Any]) -> str:
    for manifest in manifests:
        value = str(manifest.get("generated_at") or "")
        if value:
            return value
    return ""


def _normalize_source(source: str) -> str:
    return str(source or "").strip().lower().replace("-", "_")


def _text_list(value: Any) -> list[str]:
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, Sequence) or isinstance(value, (bytes, bytearray)):
        return []
    seen: list[str] = []
    for item in value:
        text = str(item or "").strip()
        if text and text not in seen:
            seen.append(text)
    return seen


def _single_text_list(value: Any) -> list[str]:
    text = str(value or "").strip()
    return [text] if text else []


def _display(values: Sequence[str]) -> str:
    cleaned = [str(value) for value in values if str(value)]
    if not cleaned:
        return "none"
    return ", ".join(cleaned[:8]) + (" ..." if len(cleaned) > 8 else "")


def _missing_field_flags(
    *,
    title_name_hints: Sequence[str],
    object_type_hints: Sequence[str],
    platform_hints: Sequence[str],
    representation_hints: Sequence[str],
    source_locator_hints: Sequence[Mapping[str, Any]],
    source_observation_refs: Sequence[str],
    evidence_refs: Sequence[str],
) -> list[str]:
    missing: list[str] = []
    if not title_name_hints:
        missing.append("missing_title_name_hint")
    if not object_type_hints:
        missing.append("missing_object_type_hint")
    if not platform_hints:
        missing.append("missing_platform_or_date_hint")
    if not representation_hints:
        missing.append("missing_representation_member_hint")
    if not source_locator_hints:
        missing.append("missing_source_locator_hint")
    if not source_observation_refs:
        missing.append("missing_source_observation_ref")
    if not evidence_refs:
        missing.append("missing_evidence_summary_ref")
    return missing


def _platform_hints(values: Sequence[str]) -> list[str]:
    keywords = ("mac", "windows", "dos", "directx", "driver", "sdk", "os")
    return [value for value in values if any(keyword in value.lower() for keyword in keywords)]


def _date_version_hints(values: Sequence[str]) -> list[str]:
    return [value for value in values if any(ch.isdigit() for ch in value)]


def _attention_score(
    *,
    evidence_count: int,
    insufficient_count: int,
    absence_count: int,
    near_miss_count: int,
    contradiction_count: int,
    source_unavailable_count: int,
    missing_field_count: int,
    provider_modes: Sequence[str],
) -> int:
    return (
        min(max(evidence_count, 0) // 4, 4)
        + insufficient_count * 3
        + (absence_count + near_miss_count) * 2
        + contradiction_count * 4
        + source_unavailable_count * 3
        + missing_field_count * 2
        + (1 if "live" in provider_modes else 0)
    )


def _attention_band(score: int) -> str:
    if score >= 10:
        return "high_attention"
    if score >= 5:
        return "medium_attention"
    return "standard_attention"


def _review_group(
    *,
    support_posture_counts: Counter[str],
    absence_count: int,
    near_miss_count: int,
    contradiction_count: int,
    source_unavailable_count: int,
    ambiguity_flags: Sequence[str],
) -> str:
    if contradiction_count:
        return "conflict_attention"
    if source_unavailable_count:
        return "source_unavailable"
    if absence_count or near_miss_count:
        return "absence_or_near_miss"
    if support_posture_counts.get("insufficient", 0):
        return "insufficient_support"
    if ambiguity_flags:
        return "mixed_or_ambiguous"
    if set(support_posture_counts) <= {"metadata_mention"}:
        return "metadata_only"
    return "evidence_rich_pending_review"


def _primary_query(item: Mapping[str, Any]) -> str:
    refs = _text_list(item.get("query_seed_refs"))
    return refs[0] if refs else "unknown_query"


def _tranche_preference_score(item: Mapping[str, Any]) -> int:
    score = 0
    if _text_list(item.get("title_name_hints")):
        score += 3
    if _text_list(item.get("object_type_hints")):
        score += 3
    if _text_list(item.get("platform_hints")) or _text_list(item.get("date_version_hints")):
        score += 2
    if _text_list(item.get("representation_member_hints")):
        score += 2
    if item.get("source_locator_hints"):
        score += 2
    score += int(item.get("candidate_support_count") or 0) * 2
    score -= int(item.get("insufficient_support_count") or 0) * 2
    score -= len(_text_list(item.get("missing_field_flags")))
    return score


def _locator_summary(item: Mapping[str, Any]) -> str:
    labels = []
    for locator in item.get("source_locator_hints", []) or []:
        if not isinstance(locator, Mapping):
            continue
        labels.append(str(locator.get("label") or locator.get("value_hash") or locator.get("kind") or ""))
    return _display(labels)


def _orphan_ref_count(rows: Sequence[Mapping[str, Any]], key: str, allowed: set[str]) -> int:
    count = 0
    for row in rows:
        if key == "candidate_id":
            refs = [str(row.get("candidate_id") or "")]
        else:
            refs = _text_list(row.get(key))
        count += sum(1 for ref in refs if ref and ref not in allowed)
    return count


def _has_reference_or_rationale(entry: Mapping[str, Any]) -> bool:
    return bool(
        str(entry.get("reason") or "").strip()
        or _text_list(entry.get("evidence_refs"))
        or _text_list(entry.get("source_observation_refs"))
        or _text_list(entry.get("absence_refs"))
        or _text_list(entry.get("fallback_refs"))
    )


def _looks_like_generated_actor(actor: str) -> bool:
    lowered = actor.strip().lower()
    if not lowered:
        return False
    return any(marker in lowered for marker in AI_ACTOR_MARKERS)


def _scan_unsafe_content(value: Any, path: str) -> list[str]:
    errors: list[str] = []
    for item_path, item in _walk_items(value, path):
        key = item_path.rsplit(".", 1)[-1]
        if key in FORBIDDEN_KEYS:
            errors.append(f"{item_path} is forbidden")
        if isinstance(item, str):
            lowered = item.lower()
            if "rights cleared" in lowered or "malware safe" in lowered or "verified artifact truth" in lowered:
                errors.append(f"{item_path} contains a forbidden rights/safety/truth claim")
    return errors


def _walk_items(value: Any, path: str = "$") -> list[tuple[str, Any]]:
    items: list[tuple[str, Any]] = [(path, value)]
    if isinstance(value, Mapping):
        for key, child in value.items():
            items.extend(_walk_items(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            items.extend(_walk_items(child, f"{path}[{index}]"))
    return items

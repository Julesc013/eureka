"""Offline H14 Source OS quality delta helpers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

from control.prototypes.legacy_runtime.connectors.h14_source_discovery.normalizer_common import H14_SOURCE_IDS
from control.prototypes.legacy_runtime.connectors.h14_source_discovery.review_integration import (
    REVIEW_SEED_KEYS,
    detect_h14_review_product_boundary_violations,
    detect_h14_review_truth_boundary_violations,
)

FORBIDDEN_TRUE_KEYS = set([
    "production_search_quality", "production_source_discovery_quality",
    "source_coverage_completeness", "exhaustive_global_coverage",
    "connector_reliability_verified", "freshness_verified", "source_approval",
    "connector_approval", "legal_approval", "rights_clearance", "safe_source_status",
    "registry_mutation_completed", "pack_export_completed", "pack_import_completed",
    "source_cache_write_completed", "public_index_write_completed",
    "production_readiness", "launch_readiness", "future_connector_auto_approval",
    "source_need_seed_accepts_source_approval", "source_candidate_seed_accepts_source_truth",
    "source_discovery_seed_mutates_registry", "source_pack_manifest_seed_exports_pack",
    "connector_pack_manifest_seed_approves_connector",
    "coverage_manifest_seed_accepts_coverage_truth",
    "connector_scorecard_seed_approves_connector",
    "reliability_freshness_seed_accepts_truth",
    "dispute_revocation_seed_accepts_truth",
    "lineage_provenance_seed_accepts_lineage_truth",
    "pack_boundary_seed_grants_import_export_permission",
    "source_cache_review_seed_accepts_source",
    "evidence_review_seed_accepts_evidence",
    "candidate_promotion_preview_promotes_candidate",
    "source_pack_preview_is_imported_or_submitted",
])


def build_h14_quality_delta(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    review = dict(inputs.get("review_integration_result") or inputs)
    sources = list(review.get("sources") or [])
    blocked_sources = list(review.get("blocked_sources") or [])
    fixture_outputs = list(review.get("used_fixture_outputs") or [])
    rollup_outputs = list(review.get("used_rollup_dry_run_outputs") or [])
    known_gaps = _known_gaps(review)
    metrics = {
        "source_count": len(sources) or len(H14_SOURCE_IDS),
        "fixture_sources_count": len({item.get("source_id") for item in fixture_outputs if item.get("source_id")}) or len(sources),
        "rollup_dry_run_sources_count": len({item.get("source_id") for item in rollup_outputs if item.get("result_status") == "rollup_dry_run_completed"}),
        "blocked_sources_count": len(blocked_sources),
        "normalized_record_count": len(review.get("source_cache_review_seeds", [])),
        "source_need_candidate_count": len(review.get("source_need_review_seeds", [])),
        "source_candidate_candidate_count": len(review.get("source_candidate_review_seeds", [])),
        "source_discovery_candidate_count": len(review.get("source_discovery_candidate_review_seeds", [])),
        "source_pack_manifest_candidate_count": len(review.get("source_pack_manifest_review_seeds", [])),
        "connector_pack_manifest_candidate_count": len(review.get("connector_pack_manifest_review_seeds", [])),
        "coverage_manifest_candidate_count": len(review.get("coverage_manifest_review_seeds", [])),
        "connector_scorecard_candidate_count": len(review.get("connector_scorecard_review_seeds", [])),
        "reliability_freshness_candidate_count": len(review.get("reliability_freshness_review_seeds", [])),
        "dispute_revocation_candidate_count": len(review.get("dispute_revocation_review_seeds", [])),
        "lineage_provenance_candidate_count": len(review.get("lineage_provenance_review_seeds", [])),
        "pack_import_export_boundary_candidate_count": len(review.get("pack_import_export_boundary_review_seeds", [])),
        "source_cache_candidate_count": len(review.get("source_cache_review_seeds", [])),
        "evidence_candidate_preview_count": len(review.get("evidence_candidate_review_seeds", [])),
        "review_seed_count": sum(len(review.get(key, [])) for key in REVIEW_SEED_KEYS),
        "coverage_preview_count": len(review.get("coverage_update_previews", [])),
        "scorecard_update_count": len(review.get("scorecard_updates", [])),
        "known_gap_count": len(known_gaps),
        "blocker_count": 0,
        "warning_count": len(review.get("warnings", [])) + (1 if blocked_sources else 0),
    }
    delta = {
        "schema_version": "h14_source_discovery_quality_delta_report.v0",
        "quality_delta_id": f"h14.quality_delta.{_digest(review)[:12]}.v0",
        "wave_id": "H14",
        "comparison_scope": "fixture_replay_rollup_dry_run_and_blocked_review_evidence",
        **metrics,
        "per_source_deltas": [_per_source_delta(source_id, review, fixture_outputs, rollup_outputs, blocked_sources) for source_id in sorted(set(sources) or set(H14_SOURCE_IDS))],
        "limitations": [
            "Quality delta measures H14 review readiness only.",
            "Blocked or completed rollup dry-runs do not prove source discovery behavior, coverage completeness, reliability, freshness, rights clearance, safe source status, production readiness, or launch readiness.",
        ],
        "forbidden_claims": sorted(FORBIDDEN_TRUE_KEYS),
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H14 quality delta is operational review evidence only."],
    }
    errors = detect_h14_quality_overclaim(delta, policy)
    if errors:
        raise ValueError("; ".join(errors))
    return delta


def summarize_h14_quality_delta(delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    errors = detect_h14_quality_overclaim(delta, policy)
    return {
        "schema_version": "h14_quality_delta_summary.v0",
        "status": "pass" if not errors else "invalid",
        "quality_delta_id": delta.get("quality_delta_id"),
        "source_count": delta.get("source_count", 0),
        "fixture_sources_count": delta.get("fixture_sources_count", 0),
        "rollup_dry_run_sources_count": delta.get("rollup_dry_run_sources_count", 0),
        "blocked_sources_count": delta.get("blocked_sources_count", 0),
        "source_need_candidate_count": delta.get("source_need_candidate_count", 0),
        "source_candidate_candidate_count": delta.get("source_candidate_candidate_count", 0),
        "source_discovery_candidate_count": delta.get("source_discovery_candidate_count", 0),
        "coverage_manifest_candidate_count": delta.get("coverage_manifest_candidate_count", 0),
        "connector_scorecard_candidate_count": delta.get("connector_scorecard_candidate_count", 0),
        "review_seed_count": delta.get("review_seed_count", 0),
        "known_gap_count": delta.get("known_gap_count", 0),
        "blocker_count": delta.get("blocker_count", 0),
        "claims_production_source_discovery_quality": False,
        "claims_source_coverage_completeness": False,
        "claims_connector_reliability_verified": False,
        "claims_freshness_verified": False,
        "claims_source_approval": False,
        "claims_connector_approval": False,
        "claims_legal_approval": False,
        "claims_rights_clearance": False,
        "claims_safe_source_status": False,
        "claims_production_readiness": False,
        "overclaim_errors": errors,
    }


def detect_h14_quality_overclaim(delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors = [f"quality overclaim: {path}=true" for path, key, value in _iter_key_values(delta) if key in FORBIDDEN_TRUE_KEYS and value is True]
    errors.extend(detect_h14_review_truth_boundary_violations(delta, policy))
    errors.extend(detect_h14_review_product_boundary_violations(delta, policy))
    return sorted(dict.fromkeys(errors))


def _per_source_delta(source_id: str, review: Mapping[str, Any], fixture_outputs: list[Mapping[str, Any]], rollup_outputs: list[Mapping[str, Any]], blocked_sources: list[str]) -> dict[str, Any]:
    represented = source_id in review.get("sources", [])
    return {
        "source_id": source_id,
        "fixture_output_integrated": any(item.get("source_id") == source_id for item in fixture_outputs) or represented,
        "rollup_dry_run_completed": any(item.get("source_id") == source_id and item.get("result_status") == "rollup_dry_run_completed" for item in rollup_outputs),
        "rollup_dry_run_blocked": source_id in blocked_sources,
        "source_need_review_seed_created": represented,
        "source_candidate_review_seed_created": represented,
        "source_discovery_review_seed_created": represented,
        "source_pack_manifest_review_seed_created": represented,
        "connector_pack_manifest_review_seed_created": represented,
        "coverage_manifest_review_seed_created": represented,
        "connector_scorecard_review_seed_created": represented,
        "reliability_freshness_review_seed_created": represented,
        "dispute_revocation_review_seed_created": represented,
        "lineage_provenance_review_seed_created": represented,
        "pack_import_export_boundary_review_seed_created": represented,
        "limitations": ["Review only; not accepted source, evidence, candidate, coverage, scorecard, reliability, freshness, dispute, revocation, lineage, pack, public, or production proof."],
    }


def _known_gaps(review: Mapping[str, Any]) -> list[str]:
    gaps: list[str] = []
    if review.get("blocked_sources"):
        gaps.append("some_rollup_dry_run_outputs_blocked_by_policy")
    if len(review.get("source_cache_review_seeds", [])) < len(H14_SOURCE_IDS):
        gaps.append("not_all_sources_have_review_seeds")
    return sorted(dict.fromkeys(gaps))


def _truth_boundary() -> dict[str, bool]:
    return {key: False for key in FORBIDDEN_TRUE_KEYS}


def _product_boundary() -> dict[str, bool]:
    return {key: False for key in ["enabled_source_discovery", "enabled_live_access", "enabled_network_access", "enabled_model_provider", "enabled_source_sync", "enabled_pack_export_import", "enabled_registry_mutation", "enabled_source_cache_writes", "enabled_evidence_writes", "mutated_public_index", "mutated_master_index", "changed_public_search_behavior"]}


def _iter_key_values(value: Any, prefix: str = ""):
    if isinstance(value, Mapping):
        for key, inner in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            yield path, str(key), inner
            yield from _iter_key_values(inner, path)
    elif isinstance(value, list):
        for index, inner in enumerate(value):
            yield from _iter_key_values(inner, f"{prefix}[{index}]")


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode("utf-8")).hexdigest()

"""Offline H1 metadata-wave quality delta helpers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

from control.prototypes.legacy_runtime.connectors.h1_metadata_wave.normalizer_common import H1_SOURCE_IDS
from control.prototypes.legacy_runtime.connectors.h1_metadata_wave.review_integration import (
    detect_h1_review_product_boundary_violations,
    detect_h1_review_truth_boundary_violations,
)


FORBIDDEN_TRUE_KEYS = {
    "automatic_future_connector_approval",
    "beats_google",
    "beats_internet_archive",
    "claims_external_superiority",
    "claims_production_readiness",
    "exhaustive_global_coverage",
    "external_superiority_claimed",
    "future_connector_auto_approval",
    "malware_safety",
    "malware_safety_claimed",
    "production_search_quality",
    "production_readiness_claimed",
    "public_index_mutated",
    "rights_clearance",
    "rights_clearance_claimed",
    "verified_installability",
    "verified_installability_claimed",
}


def build_h1_quality_delta(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build a bounded H1 quality delta from review integration outputs."""

    review = dict(inputs.get("review_integration_result") or inputs)
    sources = list(review.get("sources") or [])
    blocked_sources = list(review.get("blocked_sources") or [])
    fixture_outputs = list(review.get("used_fixture_outputs") or [])
    live_outputs = list(review.get("used_live_probe_outputs") or [])
    known_gaps = _known_gaps(review)
    metrics = {
        "source_count": len(sources) or len(H1_SOURCE_IDS),
        "fixture_sources_count": len(fixture_outputs) or len(sources),
        "live_probe_sources_count": sum(1 for item in live_outputs if item.get("status") == "live_probe_completed"),
        "blocked_sources_count": len(blocked_sources),
        "normalized_record_count": len(review.get("source_cache_review_seeds", [])),
        "source_cache_candidate_count": len(review.get("source_cache_review_seeds", [])),
        "evidence_candidate_preview_count": len(review.get("evidence_candidate_review_seeds", [])),
        "review_seed_count": len(review.get("source_cache_review_seeds", [])) + len(review.get("evidence_candidate_review_seeds", [])),
        "coverage_preview_count": len(review.get("coverage_update_previews", [])),
        "scorecard_update_count": len(review.get("scorecard_updates", [])),
        "known_gap_count": len(known_gaps),
        "blocker_count": len(blocked_sources),
        "warning_count": len(review.get("warnings", [])),
    }
    per_source = [
        {
            "source_id": source_id,
            "fixture_output_integrated": any(item.get("source_id") == source_id for item in fixture_outputs) or source_id in sources,
            "live_probe_completed": any(item.get("source_id") == source_id and item.get("status") == "live_probe_completed" for item in live_outputs),
            "live_probe_blocked": source_id in blocked_sources,
            "review_seed_preview_created": source_id in sources,
            "limitations": ["Fixture/local review only; not accepted truth."],
        }
        for source_id in sorted(set(sources) or set(H1_SOURCE_IDS))
    ]
    delta = {
        "schema_version": "h1_quality_delta_report.v0",
        "quality_delta_id": f"h1.quality_delta.{_digest(review)[:12]}.v0",
        "wave_id": "H1",
        "comparison_scope": "fixture_review_and_blocked_live_probe_evidence",
        **metrics,
        "per_source_deltas": per_source,
        "limitations": [
            "Quality delta measures H1 review readiness only.",
            "Blocked live probes do not prove endpoint behavior.",
            "No production search quality or external superiority claim is made.",
        ],
        "forbidden_claims": [
            "beats_google",
            "beats_internet_archive",
            "exhaustive_global_coverage",
            "production_search_quality",
            "rights_clearance",
            "malware_safety",
            "verified_installability",
            "automatic_future_connector_approval",
        ],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H1 quality delta is operational evidence only."],
    }
    errors = detect_h1_quality_overclaim(delta, policy)
    if errors:
        raise ValueError("; ".join(errors))
    return delta


def summarize_h1_quality_delta(delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    errors = detect_h1_quality_overclaim(delta, policy)
    return {
        "schema_version": "h1_quality_delta_summary.v0",
        "status": "pass" if not errors else "invalid",
        "quality_delta_id": delta.get("quality_delta_id"),
        "source_count": delta.get("source_count", 0),
        "fixture_sources_count": delta.get("fixture_sources_count", 0),
        "live_probe_sources_count": delta.get("live_probe_sources_count", 0),
        "blocked_sources_count": delta.get("blocked_sources_count", 0),
        "review_seed_count": delta.get("review_seed_count", 0),
        "known_gap_count": delta.get("known_gap_count", 0),
        "blocker_count": delta.get("blocker_count", 0),
        "claims_external_superiority": False,
        "claims_production_readiness": False,
        "overclaim_errors": errors,
    }


def detect_h1_quality_overclaim(delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors = [f"quality overclaim: {path}=true" for path, key, value in _iter_key_values(delta) if key in FORBIDDEN_TRUE_KEYS and value is True]
    errors.extend(detect_h1_review_truth_boundary_violations(delta, policy))
    errors.extend(detect_h1_review_product_boundary_violations(delta, policy))
    return sorted(dict.fromkeys(errors))


def _known_gaps(review: Mapping[str, Any]) -> list[str]:
    gaps = []
    if review.get("blocked_sources"):
        gaps.append("operator_approval_missing_for_live_metadata_probes")
    if len(review.get("source_cache_review_seeds", [])) < len(H1_SOURCE_IDS):
        gaps.append("not_all_sources_have_review_seeds")
    if not review.get("used_live_probe_outputs"):
        gaps.append("approved_live_probe_outputs_not_available")
    return sorted(dict.fromkeys(gaps))


def _truth_boundary() -> dict[str, bool]:
    return {
        "quality_delta_is_public_truth": False,
        "claims_external_superiority": False,
        "claims_production_readiness": False,
        "external_superiority_claimed": False,
        "production_readiness_claimed": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
        "automatic_future_connector_approval": False,
    }


def _product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_hosting": False,
        "enabled_source_sync": False,
        "enabled_downloads": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def _iter_key_values(value: Any, prefix: str = ""):
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            yield path, key_text, child
            yield from _iter_key_values(child, path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _iter_key_values(child, f"{prefix}[{index}]")


def _digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

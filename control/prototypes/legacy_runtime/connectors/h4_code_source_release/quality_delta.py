"""Offline H4 code/source/release quality delta helpers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

from control.prototypes.legacy_runtime.connectors.h4_code_source_release.normalizer_common import H4_SOURCE_IDS
from control.prototypes.legacy_runtime.connectors.h4_code_source_release.review_integration import (
    detect_h4_review_product_boundary_violations,
    detect_h4_review_truth_boundary_violations,
)


FORBIDDEN_TRUE_KEYS = {
    "automatic_future_connector_approval",
    "build_reproducibility_verified",
    "exhaustive_global_coverage",
    "future_connector_auto_approval",
    "malware_safety",
    "malware_safety_claimed",
    "production_readiness_claimed",
    "production_search_quality",
    "production_source_coverage",
    "public_index_mutated",
    "release_authenticity_verified",
    "rights_clearance",
    "rights_clearance_claimed",
    "source_authenticity_verified",
    "source_to_binary_provenance_verified",
    "verified_installability",
    "verified_installability_claimed",
}


def build_h4_quality_delta(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    review = dict(inputs.get("review_integration_result") or inputs)
    sources = list(review.get("sources") or [])
    blocked_sources = list(review.get("blocked_sources") or [])
    fixture_outputs = list(review.get("used_fixture_outputs") or [])
    live_outputs = list(review.get("used_live_probe_outputs") or [])
    known_gaps = _known_gaps(review)
    metrics = {
        "source_count": len(sources) or len(H4_SOURCE_IDS),
        "fixture_sources_count": len({item.get("source_id") for item in fixture_outputs if item.get("source_id")}) or len(sources),
        "live_probe_sources_count": len({item.get("source_id") for item in live_outputs if item.get("status") == "live_probe_completed"}),
        "blocked_sources_count": len(blocked_sources),
        "normalized_record_count": len(review.get("source_cache_review_seeds", [])),
        "source_identity_candidate_count": len(review.get("source_identity_review_seeds", [])),
        "release_identity_candidate_count": len(review.get("release_identity_review_seeds", [])),
        "source_to_binary_relation_candidate_count": len(review.get("source_to_binary_relation_review_seeds", [])),
        "release_asset_candidate_count": len(review.get("release_asset_candidate_review_seeds", [])),
        "source_cache_candidate_count": len(review.get("source_cache_review_seeds", [])),
        "evidence_candidate_preview_count": len(review.get("evidence_candidate_review_seeds", [])),
        "review_seed_count": sum(
            len(review.get(key, []))
            for key in (
                "source_identity_review_seeds",
                "release_identity_review_seeds",
                "source_to_binary_relation_review_seeds",
                "release_asset_candidate_review_seeds",
                "source_cache_review_seeds",
                "evidence_candidate_review_seeds",
            )
        ),
        "coverage_preview_count": len(review.get("coverage_update_previews", [])),
        "scorecard_update_count": len(review.get("scorecard_updates", [])),
        "known_gap_count": len(known_gaps),
        "blocker_count": 0,
        "warning_count": len(review.get("warnings", [])) + (1 if blocked_sources else 0),
    }
    per_source = [
        {
            "source_id": source_id,
            "fixture_output_integrated": any(item.get("source_id") == source_id for item in fixture_outputs) or source_id in sources,
            "live_probe_completed": any(item.get("source_id") == source_id and item.get("status") == "live_probe_completed" for item in live_outputs),
            "live_probe_blocked": source_id in blocked_sources,
            "source_identity_review_seed_created": source_id in sources,
            "release_identity_review_seed_created": source_id in sources,
            "source_to_binary_relation_review_seed_created": source_id in sources,
            "release_asset_review_seed_created": any(seed.get("source_id") == source_id for seed in review.get("release_asset_candidate_review_seeds", [])),
            "source_cache_review_seed_created": source_id in sources,
            "evidence_review_seed_created": source_id in sources,
            "limitations": ["Fixture/local review only; not accepted truth, authenticity, provenance, safety, rights, or build proof."],
        }
        for source_id in sorted(set(sources) or set(H4_SOURCE_IDS))
    ]
    delta = {
        "schema_version": "h4_code_source_quality_delta_report.v0",
        "quality_delta_id": f"h4.quality_delta.{_digest(review)[:12]}.v0",
        "wave_id": "H4",
        "comparison_scope": "fixture_review_and_blocked_live_probe_evidence",
        **metrics,
        "per_source_deltas": per_source,
        "limitations": [
            "Quality delta measures H4 review readiness only.",
            "Blocked live probes do not prove endpoint behavior.",
            "Repository and release metadata is not authenticity, provenance, build reproducibility, rights, safety, installability, or production coverage proof.",
        ],
        "forbidden_claims": [
            "production_search_quality",
            "production_source_coverage",
            "exhaustive_global_coverage",
            "source_authenticity_verified",
            "release_authenticity_verified",
            "source_to_binary_provenance_verified",
            "build_reproducibility_verified",
            "rights_clearance",
            "malware_safety",
            "verified_installability",
            "automatic_future_connector_approval",
        ],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H4 quality delta is operational evidence only."],
    }
    errors = detect_h4_quality_overclaim(delta, policy)
    if errors:
        raise ValueError("; ".join(errors))
    return delta


def summarize_h4_quality_delta(delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    errors = detect_h4_quality_overclaim(delta, policy)
    return {
        "schema_version": "h4_quality_delta_summary.v0",
        "status": "pass" if not errors else "invalid",
        "quality_delta_id": delta.get("quality_delta_id"),
        "source_count": delta.get("source_count", 0),
        "fixture_sources_count": delta.get("fixture_sources_count", 0),
        "live_probe_sources_count": delta.get("live_probe_sources_count", 0),
        "blocked_sources_count": delta.get("blocked_sources_count", 0),
        "source_identity_candidate_count": delta.get("source_identity_candidate_count", 0),
        "release_identity_candidate_count": delta.get("release_identity_candidate_count", 0),
        "source_to_binary_relation_candidate_count": delta.get("source_to_binary_relation_candidate_count", 0),
        "release_asset_candidate_count": delta.get("release_asset_candidate_count", 0),
        "review_seed_count": delta.get("review_seed_count", 0),
        "known_gap_count": delta.get("known_gap_count", 0),
        "blocker_count": delta.get("blocker_count", 0),
        "claims_source_authenticity_verified": False,
        "claims_release_authenticity_verified": False,
        "claims_source_to_binary_provenance_verified": False,
        "claims_build_reproducibility_verified": False,
        "claims_rights_clearance": False,
        "claims_malware_safety": False,
        "claims_production_readiness": False,
        "overclaim_errors": errors,
    }


def detect_h4_quality_overclaim(delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors = [f"quality overclaim: {path}=true" for path, key, value in _iter_key_values(delta) if key in FORBIDDEN_TRUE_KEYS and value is True]
    errors.extend(detect_h4_review_truth_boundary_violations(delta, policy))
    errors.extend(detect_h4_review_product_boundary_violations(delta, policy))
    return sorted(dict.fromkeys(errors))


def _known_gaps(review: Mapping[str, Any]) -> list[str]:
    gaps = []
    if review.get("blocked_sources"):
        gaps.append("operator_approval_missing_for_live_metadata_probes")
    if len(review.get("source_cache_review_seeds", [])) < len(H4_SOURCE_IDS):
        gaps.append("not_all_sources_have_review_seeds")
    if not any(item.get("status") == "live_probe_completed" for item in review.get("used_live_probe_outputs", [])):
        gaps.append("approved_live_probe_outputs_not_available")
    return sorted(dict.fromkeys(gaps))


def _truth_boundary() -> dict[str, bool]:
    return {
        "quality_delta_is_public_truth": False,
        "production_search_quality": False,
        "production_source_coverage": False,
        "exhaustive_global_coverage": False,
        "source_authenticity_verified": False,
        "release_authenticity_verified": False,
        "source_to_binary_provenance_verified": False,
        "build_reproducibility_verified": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
        "verified_authenticity_claimed": False,
        "verified_build_reproducibility_claimed": False,
        "production_readiness_claimed": False,
        "automatic_future_connector_approval": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def _product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_hosting": False,
        "enabled_source_sync": False,
        "enabled_repository_clone": False,
        "enabled_downloads": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "enabled_installers": False,
        "enabled_execution": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
        "repository_clone_enabled": False,
        "source_archive_download_enabled": False,
        "release_asset_download_enabled": False,
        "git_command_invocation_enabled": False,
        "build_tool_invocation_enabled": False,
        "install_execute_enabled": False,
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

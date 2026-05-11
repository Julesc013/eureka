"""Offline H11 storefront quality delta helpers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

from runtime.connectors.h11_storefront.normalizer_common import H11_SOURCE_IDS
from runtime.connectors.h11_storefront.review_integration import (
    REVIEW_SEED_KEYS,
    detect_h11_review_product_boundary_violations,
    detect_h11_review_truth_boundary_violations,
)

FORBIDDEN_TRUE_KEYS = {
    "production_search_quality", "production_storefront_coverage",
    "exhaustive_global_coverage", "storefront_availability_verified",
    "current_price_verified", "current_availability_verified",
    "license_entitlement_verified", "legal_acquisition_verified",
    "download_permission_verified", "installability_verified",
    "review_correctness_verified", "rating_correctness_verified",
    "rights_clearance", "rights_clearance_claimed", "malware_safety",
    "malware_safety_claimed", "content_safety", "content_safety_claimed",
    "privacy_safety", "privacy_safety_claimed", "verified_authenticity",
    "verified_authenticity_claimed", "production_readiness_claimed",
    "automatic_future_connector_approval", "future_connector_auto_approval",
}


def build_h11_quality_delta(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    review = dict(inputs.get("review_integration_result") or inputs)
    sources = list(review.get("sources") or [])
    blocked_sources = list(review.get("blocked_sources") or [])
    fixture_outputs = list(review.get("used_fixture_outputs") or [])
    live_outputs = list(review.get("used_live_probe_outputs") or [])
    known_gaps = _known_gaps(review)
    metrics = {
        "source_count": len(sources) or len(H11_SOURCE_IDS),
        "fixture_sources_count": len({item.get("source_id") for item in fixture_outputs if item.get("source_id")}) or len(sources),
        "live_probe_sources_count": len({item.get("source_id") for item in live_outputs if item.get("status") == "live_probe_completed"}),
        "blocked_sources_count": len(blocked_sources),
        "normalized_record_count": len(review.get("source_cache_review_seeds", [])),
        "storefront_listing_identity_candidate_count": len(review.get("storefront_listing_identity_review_seeds", [])),
        "app_product_identity_candidate_count": len(review.get("app_product_identity_review_seeds", [])),
        "version_release_channel_candidate_count": len(review.get("version_release_channel_review_seeds", [])),
        "price_availability_region_candidate_count": len(review.get("price_availability_region_review_seeds", [])),
        "acquisition_path_candidate_count": len(review.get("acquisition_path_review_seeds", [])),
        "review_rating_metadata_candidate_count": len(review.get("review_rating_metadata_review_seeds", [])),
        "account_entitlement_boundary_candidate_count": len(review.get("account_entitlement_boundary_review_seeds", [])),
        "storefront_rights_safety_candidate_count": len(review.get("storefront_rights_safety_review_seeds", [])),
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
        "schema_version": "h11_storefront_quality_delta_report.v0",
        "quality_delta_id": f"h11.quality_delta.{_digest(review)[:12]}.v0",
        "wave_id": "H11",
        "comparison_scope": "fixture_review_and_blocked_live_probe_evidence",
        **metrics,
        "per_source_deltas": [_per_source_delta(source_id, review, fixture_outputs, live_outputs, blocked_sources) for source_id in sorted(set(sources) or set(H11_SOURCE_IDS))],
        "limitations": [
            "Quality delta measures H11 review readiness only.",
            "Blocked live probes do not prove endpoint behavior.",
            "Storefront metadata is not listing truth, app/product truth, version truth, storefront availability proof, current price proof, current availability proof, license entitlement proof, legal acquisition proof, download permission, installability, review correctness, rating correctness, rights clearance, malware safety, privacy safety, content safety, production coverage, or production quality proof.",
        ],
        "forbidden_claims": [
            "production_search_quality", "production_storefront_coverage",
            "exhaustive_global_coverage", "storefront_availability_verified",
            "current_price_verified", "current_availability_verified",
            "license_entitlement_verified", "legal_acquisition_verified",
            "download_permission_verified", "installability_verified",
            "review_correctness_verified", "rating_correctness_verified",
            "rights_clearance", "malware_safety", "content_safety",
            "privacy_safety", "verified_authenticity",
            "automatic_future_connector_approval",
        ],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H11 quality delta is operational review evidence only."],
    }
    errors = detect_h11_quality_overclaim(delta, policy)
    if errors:
        raise ValueError("; ".join(errors))
    return delta


def summarize_h11_quality_delta(delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    errors = detect_h11_quality_overclaim(delta, policy)
    return {
        "schema_version": "h11_quality_delta_summary.v0",
        "status": "pass" if not errors else "invalid",
        "quality_delta_id": delta.get("quality_delta_id"),
        "source_count": delta.get("source_count", 0),
        "fixture_sources_count": delta.get("fixture_sources_count", 0),
        "live_probe_sources_count": delta.get("live_probe_sources_count", 0),
        "blocked_sources_count": delta.get("blocked_sources_count", 0),
        "storefront_listing_identity_candidate_count": delta.get("storefront_listing_identity_candidate_count", 0),
        "app_product_identity_candidate_count": delta.get("app_product_identity_candidate_count", 0),
        "version_release_channel_candidate_count": delta.get("version_release_channel_candidate_count", 0),
        "price_availability_region_candidate_count": delta.get("price_availability_region_candidate_count", 0),
        "acquisition_path_candidate_count": delta.get("acquisition_path_candidate_count", 0),
        "review_rating_metadata_candidate_count": delta.get("review_rating_metadata_candidate_count", 0),
        "account_entitlement_boundary_candidate_count": delta.get("account_entitlement_boundary_candidate_count", 0),
        "storefront_rights_safety_candidate_count": delta.get("storefront_rights_safety_candidate_count", 0),
        "review_seed_count": delta.get("review_seed_count", 0),
        "known_gap_count": delta.get("known_gap_count", 0),
        "blocker_count": delta.get("blocker_count", 0),
        "claims_storefront_availability_verified": False,
        "claims_current_price_verified": False,
        "claims_current_availability_verified": False,
        "claims_license_entitlement_verified": False,
        "claims_legal_acquisition": False,
        "claims_download_permission": False,
        "claims_installability": False,
        "claims_review_correctness": False,
        "claims_rating_correctness": False,
        "claims_rights_clearance": False,
        "claims_malware_safety": False,
        "claims_content_safety": False,
        "claims_privacy_safety": False,
        "claims_verified_authenticity": False,
        "claims_production_readiness": False,
        "overclaim_errors": errors,
    }


def detect_h11_quality_overclaim(delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors = [f"quality overclaim: {path}=true" for path, key, value in _iter_key_values(delta) if key in FORBIDDEN_TRUE_KEYS and value is True]
    errors.extend(detect_h11_review_truth_boundary_violations(delta, policy))
    errors.extend(detect_h11_review_product_boundary_violations(delta, policy))
    return sorted(dict.fromkeys(errors))


def _per_source_delta(source_id: str, review: Mapping[str, Any], fixture_outputs: list[Mapping[str, Any]], live_outputs: list[Mapping[str, Any]], blocked_sources: list[str]) -> dict[str, Any]:
    represented = source_id in review.get("sources", [])
    return {
        "source_id": source_id,
        "fixture_output_integrated": any(item.get("source_id") == source_id for item in fixture_outputs) or represented,
        "live_probe_completed": any(item.get("source_id") == source_id and item.get("status") == "live_probe_completed" for item in live_outputs),
        "live_probe_blocked": source_id in blocked_sources,
        "storefront_listing_identity_review_seed_created": represented,
        "app_product_identity_review_seed_created": represented,
        "version_release_channel_review_seed_created": represented,
        "price_availability_region_review_seed_created": represented,
        "acquisition_path_review_seed_created": represented,
        "review_rating_metadata_review_seed_created": represented,
        "account_entitlement_boundary_review_seed_created": represented,
        "storefront_rights_safety_review_seed_created": represented,
        "source_cache_review_seed_created": represented,
        "evidence_review_seed_created": represented,
        "limitations": ["Fixture/local review only; not accepted source, evidence, candidate, listing, app/product, version, price/availability, acquisition, review/rating, account/entitlement, rights/safety, or production proof."],
    }


def _known_gaps(review: Mapping[str, Any]) -> list[str]:
    gaps: list[str] = []
    if review.get("blocked_sources"):
        gaps.append("operator_approval_missing_for_live_metadata_probes")
    if len(review.get("source_cache_review_seeds", [])) < len(H11_SOURCE_IDS):
        gaps.append("not_all_sources_have_review_seeds")
    if not any(item.get("status") == "live_probe_completed" for item in review.get("used_live_probe_outputs", [])):
        gaps.append("approved_live_probe_outputs_not_available")
    return sorted(dict.fromkeys(gaps))


def _truth_boundary() -> dict[str, bool]:
    return {
        "quality_delta_is_public_truth": False,
        "production_search_quality": False,
        "production_storefront_coverage": False,
        "exhaustive_global_coverage": False,
        "storefront_availability_verified": False,
        "current_price_verified": False,
        "current_availability_verified": False,
        "license_entitlement_verified": False,
        "legal_acquisition_verified": False,
        "download_permission_verified": False,
        "installability_verified": False,
        "review_correctness_verified": False,
        "rating_correctness_verified": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "content_safety_claimed": False,
        "privacy_safety_claimed": False,
        "verified_authenticity_claimed": False,
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
        "enabled_downloads": False,
        "enabled_accounts": False,
        "enabled_purchase_actions": False,
        "enabled_entitlement_checks": False,
        "enabled_install_launch": False,
        "enabled_crawling": False,
        "enabled_uploads": False,
        "enabled_telemetry": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


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

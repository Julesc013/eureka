"""Offline H5 vendor/update/driver quality delta helpers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

from runtime.connectors.h5_vendor_update_driver.normalizer_common import H5_SOURCE_IDS
from runtime.connectors.h5_vendor_update_driver.review_integration import (
    detect_h5_review_product_boundary_violations,
    detect_h5_review_truth_boundary_violations,
)


FORBIDDEN_TRUE_KEYS = {
    "authenticity_verified",
    "automatic_future_connector_approval",
    "compatibility_verified",
    "driver_identity_verified",
    "exhaustive_global_coverage",
    "firmware_identity_verified",
    "future_connector_auto_approval",
    "installability_verified",
    "malware_safety",
    "malware_safety_claimed",
    "official_status_verified",
    "production_readiness_claimed",
    "production_search_quality",
    "production_vendor_coverage",
    "rights_clearance",
    "rights_clearance_claimed",
    "runtime_identity_verified",
    "safety_verified",
    "verified_authenticity_claimed",
    "verified_compatibility_claimed",
    "verified_installability_claimed",
}


def build_h5_quality_delta(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    review = dict(inputs.get("review_integration_result") or inputs)
    sources = list(review.get("sources") or [])
    blocked_sources = list(review.get("blocked_sources") or [])
    fixture_outputs = list(review.get("used_fixture_outputs") or [])
    live_outputs = list(review.get("used_live_probe_outputs") or [])
    known_gaps = _known_gaps(review)
    metrics = {
        "source_count": len(sources) or len(H5_SOURCE_IDS),
        "fixture_sources_count": len({item.get("source_id") for item in fixture_outputs if item.get("source_id")}) or len(sources),
        "live_probe_sources_count": len({item.get("source_id") for item in live_outputs if item.get("status") == "live_probe_completed"}),
        "blocked_sources_count": len(blocked_sources),
        "normalized_record_count": len(review.get("source_cache_review_seeds", [])),
        "vendor_identity_candidate_count": len(review.get("vendor_identity_review_seeds", [])),
        "driver_device_compatibility_candidate_count": len(review.get("driver_device_compatibility_review_seeds", [])),
        "firmware_update_candidate_count": len(review.get("firmware_update_review_seeds", [])),
        "runtime_redistributable_candidate_count": len(review.get("runtime_redistributable_review_seeds", [])),
        "payload_metadata_candidate_count": len(review.get("payload_metadata_review_seeds", [])),
        "source_cache_candidate_count": len(review.get("source_cache_review_seeds", [])),
        "evidence_candidate_preview_count": len(review.get("evidence_candidate_review_seeds", [])),
        "review_seed_count": sum(
            len(review.get(key, []))
            for key in (
                "vendor_identity_review_seeds",
                "driver_device_compatibility_review_seeds",
                "firmware_update_review_seeds",
                "runtime_redistributable_review_seeds",
                "payload_metadata_review_seeds",
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
            "vendor_identity_review_seed_created": source_id in sources,
            "driver_device_compatibility_review_seed_created": source_id in sources,
            "firmware_update_review_seed_created": source_id in sources,
            "runtime_redistributable_review_seed_created": source_id in sources,
            "payload_metadata_review_seed_created": source_id in sources,
            "source_cache_review_seed_created": source_id in sources,
            "evidence_review_seed_created": source_id in sources,
            "limitations": ["Fixture/local review only; not accepted vendor, driver, firmware, runtime, compatibility, authenticity, safety, rights, or installability proof."],
        }
        for source_id in sorted(set(sources) or set(H5_SOURCE_IDS))
    ]
    delta = {
        "schema_version": "h5_vendor_update_quality_delta_report.v0",
        "quality_delta_id": f"h5.quality_delta.{_digest(review)[:12]}.v0",
        "wave_id": "H5",
        "comparison_scope": "fixture_review_and_blocked_live_probe_evidence",
        **metrics,
        "per_source_deltas": per_source,
        "limitations": [
            "Quality delta measures H5 review readiness only.",
            "Blocked live probes do not prove endpoint behavior.",
            "Vendor metadata is not official-status, compatibility, authenticity, safety, installability, rights, malware, or production coverage proof.",
        ],
        "forbidden_claims": [
            "production_search_quality",
            "production_vendor_coverage",
            "exhaustive_global_coverage",
            "official_status_verified",
            "driver_identity_verified",
            "firmware_identity_verified",
            "runtime_identity_verified",
            "compatibility_verified",
            "authenticity_verified",
            "safety_verified",
            "installability_verified",
            "rights_clearance",
            "malware_safety",
            "automatic_future_connector_approval",
        ],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H5 quality delta is operational review evidence only."],
    }
    errors = detect_h5_quality_overclaim(delta, policy)
    if errors:
        raise ValueError("; ".join(errors))
    return delta


def summarize_h5_quality_delta(delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    errors = detect_h5_quality_overclaim(delta, policy)
    return {
        "schema_version": "h5_quality_delta_summary.v0",
        "status": "pass" if not errors else "invalid",
        "quality_delta_id": delta.get("quality_delta_id"),
        "source_count": delta.get("source_count", 0),
        "fixture_sources_count": delta.get("fixture_sources_count", 0),
        "live_probe_sources_count": delta.get("live_probe_sources_count", 0),
        "blocked_sources_count": delta.get("blocked_sources_count", 0),
        "vendor_identity_candidate_count": delta.get("vendor_identity_candidate_count", 0),
        "driver_device_compatibility_candidate_count": delta.get("driver_device_compatibility_candidate_count", 0),
        "firmware_update_candidate_count": delta.get("firmware_update_candidate_count", 0),
        "runtime_redistributable_candidate_count": delta.get("runtime_redistributable_candidate_count", 0),
        "payload_metadata_candidate_count": delta.get("payload_metadata_candidate_count", 0),
        "review_seed_count": delta.get("review_seed_count", 0),
        "known_gap_count": delta.get("known_gap_count", 0),
        "blocker_count": delta.get("blocker_count", 0),
        "claims_official_status_verified": False,
        "claims_compatibility_verified": False,
        "claims_authenticity_verified": False,
        "claims_safety_verified": False,
        "claims_installability_verified": False,
        "claims_rights_clearance": False,
        "claims_malware_safety": False,
        "claims_production_readiness": False,
        "overclaim_errors": errors,
    }


def detect_h5_quality_overclaim(delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors = [f"quality overclaim: {path}=true" for path, key, value in _iter_key_values(delta) if key in FORBIDDEN_TRUE_KEYS and value is True]
    errors.extend(detect_h5_review_truth_boundary_violations(delta, policy))
    errors.extend(detect_h5_review_product_boundary_violations(delta, policy))
    return sorted(dict.fromkeys(errors))


def _known_gaps(review: Mapping[str, Any]) -> list[str]:
    gaps: list[str] = []
    if review.get("blocked_sources"):
        gaps.append("operator_approval_missing_for_live_metadata_probes")
    if len(review.get("source_cache_review_seeds", [])) < len(H5_SOURCE_IDS):
        gaps.append("not_all_sources_have_review_seeds")
    if not any(item.get("status") == "live_probe_completed" for item in review.get("used_live_probe_outputs", [])):
        gaps.append("approved_live_probe_outputs_not_available")
    return sorted(dict.fromkeys(gaps))


def _truth_boundary() -> dict[str, bool]:
    return {
        "quality_delta_is_public_truth": False,
        "production_search_quality": False,
        "production_vendor_coverage": False,
        "exhaustive_global_coverage": False,
        "official_status_verified": False,
        "driver_identity_verified": False,
        "firmware_identity_verified": False,
        "runtime_identity_verified": False,
        "compatibility_verified": False,
        "authenticity_verified": False,
        "safety_verified": False,
        "installability_verified": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
        "verified_compatibility_claimed": False,
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
        "enabled_catalog_sync": False,
        "enabled_downloads": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "enabled_installers": False,
        "enabled_execution": False,
        "enabled_firmware_flashing": False,
        "enabled_vendor_tool_invocation": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
        "catalog_fetch_enabled": False,
        "driver_download_enabled": False,
        "firmware_download_enabled": False,
        "runtime_download_enabled": False,
        "installer_download_enabled": False,
        "vendor_tool_invocation_enabled": False,
        "firmware_flash_enabled": False,
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
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode("utf-8")).hexdigest()

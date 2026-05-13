"""Offline H8 manuals/docs/standards quality delta helpers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

from control.prototypes.legacy_runtime.connectors.h8_manuals_docs_standards.normalizer_common import H8_SOURCE_IDS
from control.prototypes.legacy_runtime.connectors.h8_manuals_docs_standards.review_integration import (
    detect_h8_review_product_boundary_violations,
    detect_h8_review_truth_boundary_violations,
)


FORBIDDEN_TRUE_KEYS = {
    "access_rights_verified",
    "automatic_future_connector_approval",
    "compatibility_correctness_verified",
    "documentation_completeness_verified",
    "electrical_safety_verified",
    "exhaustive_global_coverage",
    "future_connector_auto_approval",
    "installability_verified",
    "malware_safety",
    "malware_safety_claimed",
    "open_access_truth",
    "open_access_truth_claimed",
    "open_access_truth_verified",
    "production_documentation_coverage",
    "production_readiness_claimed",
    "production_search_quality",
    "repair_safety_verified",
    "rights_clearance",
    "rights_clearance_claimed",
    "standards_compliance_verified",
    "verified_authenticity",
    "verified_authenticity_claimed",
}


def build_h8_quality_delta(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    review = dict(inputs.get("review_integration_result") or inputs)
    sources = list(review.get("sources") or [])
    blocked_sources = list(review.get("blocked_sources") or [])
    fixture_outputs = list(review.get("used_fixture_outputs") or [])
    live_outputs = list(review.get("used_live_probe_outputs") or [])
    known_gaps = _known_gaps(review)
    metrics = {
        "source_count": len(sources) or len(H8_SOURCE_IDS),
        "fixture_sources_count": len({item.get("source_id") for item in fixture_outputs if item.get("source_id")}) or len(sources),
        "live_probe_sources_count": len({item.get("source_id") for item in live_outputs if item.get("status") == "live_probe_completed"}),
        "blocked_sources_count": len(blocked_sources),
        "normalized_record_count": len(review.get("source_cache_review_seeds", [])),
        "technical_document_identity_candidate_count": len(review.get("technical_document_identity_review_seeds", [])),
        "manual_artifact_relation_candidate_count": len(review.get("manual_artifact_relation_review_seeds", [])),
        "datasheet_device_identity_candidate_count": len(review.get("datasheet_device_identity_review_seeds", [])),
        "standards_specification_identity_candidate_count": len(review.get("standards_specification_identity_review_seeds", [])),
        "install_requirement_claim_candidate_count": len(review.get("install_requirement_claim_review_seeds", [])),
        "repair_service_safety_candidate_count": len(review.get("repair_service_safety_review_seeds", [])),
        "access_rights_candidate_count": len(review.get("access_rights_review_seeds", [])),
        "source_cache_candidate_count": len(review.get("source_cache_review_seeds", [])),
        "evidence_candidate_preview_count": len(review.get("evidence_candidate_review_seeds", [])),
        "review_seed_count": sum(len(review.get(key, [])) for key in (
            "technical_document_identity_review_seeds",
            "manual_artifact_relation_review_seeds",
            "datasheet_device_identity_review_seeds",
            "standards_specification_identity_review_seeds",
            "install_requirement_claim_review_seeds",
            "repair_service_safety_review_seeds",
            "access_rights_review_seeds",
            "source_cache_review_seeds",
            "evidence_candidate_review_seeds",
        )),
        "coverage_preview_count": len(review.get("coverage_update_previews", [])),
        "scorecard_update_count": len(review.get("scorecard_updates", [])),
        "known_gap_count": len(known_gaps),
        "blocker_count": 0,
        "warning_count": len(review.get("warnings", [])) + (1 if blocked_sources else 0),
    }
    delta = {
        "schema_version": "h8_manuals_docs_quality_delta_report.v0",
        "quality_delta_id": f"h8.quality_delta.{_digest(review)[:12]}.v0",
        "wave_id": "H8",
        "comparison_scope": "fixture_review_and_blocked_live_probe_evidence",
        **metrics,
        "per_source_deltas": [_per_source_delta(source_id, review, fixture_outputs, live_outputs, blocked_sources) for source_id in sorted(set(sources) or set(H8_SOURCE_IDS))],
        "limitations": [
            "Quality delta measures H8 review readiness only.",
            "Blocked live probes do not prove endpoint behavior.",
            "Technical-document metadata is not documentation completeness, standards compliance, compatibility correctness, installability, repair safety, electrical safety, rights clearance, open-access truth, malware safety, verified authenticity, or production coverage proof.",
        ],
        "forbidden_claims": [
            "production_search_quality",
            "production_documentation_coverage",
            "exhaustive_global_coverage",
            "documentation_completeness_verified",
            "standards_compliance_verified",
            "compatibility_correctness_verified",
            "installability_verified",
            "repair_safety_verified",
            "electrical_safety_verified",
            "access_rights_verified",
            "open_access_truth_verified",
            "rights_clearance",
            "malware_safety",
            "verified_authenticity",
            "automatic_future_connector_approval",
        ],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H8 quality delta is operational review evidence only."],
    }
    errors = detect_h8_quality_overclaim(delta, policy)
    if errors:
        raise ValueError("; ".join(errors))
    return delta


def summarize_h8_quality_delta(delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    errors = detect_h8_quality_overclaim(delta, policy)
    return {
        "schema_version": "h8_quality_delta_summary.v0",
        "status": "pass" if not errors else "invalid",
        "quality_delta_id": delta.get("quality_delta_id"),
        "source_count": delta.get("source_count", 0),
        "fixture_sources_count": delta.get("fixture_sources_count", 0),
        "live_probe_sources_count": delta.get("live_probe_sources_count", 0),
        "blocked_sources_count": delta.get("blocked_sources_count", 0),
        "technical_document_identity_candidate_count": delta.get("technical_document_identity_candidate_count", 0),
        "manual_artifact_relation_candidate_count": delta.get("manual_artifact_relation_candidate_count", 0),
        "datasheet_device_identity_candidate_count": delta.get("datasheet_device_identity_candidate_count", 0),
        "standards_specification_identity_candidate_count": delta.get("standards_specification_identity_candidate_count", 0),
        "install_requirement_claim_candidate_count": delta.get("install_requirement_claim_candidate_count", 0),
        "repair_service_safety_candidate_count": delta.get("repair_service_safety_candidate_count", 0),
        "access_rights_candidate_count": delta.get("access_rights_candidate_count", 0),
        "review_seed_count": delta.get("review_seed_count", 0),
        "known_gap_count": delta.get("known_gap_count", 0),
        "blocker_count": delta.get("blocker_count", 0),
        "claims_documentation_completeness_verified": False,
        "claims_standards_compliance_verified": False,
        "claims_compatibility_correctness_verified": False,
        "claims_installability_verified": False,
        "claims_repair_safety_verified": False,
        "claims_electrical_safety_verified": False,
        "claims_rights_clearance": False,
        "claims_open_access_truth": False,
        "claims_malware_safety": False,
        "claims_verified_authenticity": False,
        "claims_production_readiness": False,
        "overclaim_errors": errors,
    }


def detect_h8_quality_overclaim(delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors = [f"quality overclaim: {path}=true" for path, key, value in _iter_key_values(delta) if key in FORBIDDEN_TRUE_KEYS and value is True]
    errors.extend(detect_h8_review_truth_boundary_violations(delta, policy))
    errors.extend(detect_h8_review_product_boundary_violations(delta, policy))
    return sorted(dict.fromkeys(errors))


def _per_source_delta(source_id: str, review: Mapping[str, Any], fixture_outputs: list[Mapping[str, Any]], live_outputs: list[Mapping[str, Any]], blocked_sources: list[str]) -> dict[str, Any]:
    represented = source_id in review.get("sources", [])
    return {
        "source_id": source_id,
        "fixture_output_integrated": any(item.get("source_id") == source_id for item in fixture_outputs) or represented,
        "live_probe_completed": any(item.get("source_id") == source_id and item.get("status") == "live_probe_completed" for item in live_outputs),
        "live_probe_blocked": source_id in blocked_sources,
        "technical_document_identity_review_seed_created": represented,
        "manual_artifact_relation_review_seed_created": represented,
        "datasheet_device_identity_review_seed_created": represented,
        "standards_specification_identity_review_seed_created": represented,
        "install_requirement_claim_review_seed_created": represented,
        "repair_service_safety_review_seed_created": represented,
        "access_rights_review_seed_created": represented,
        "source_cache_review_seed_created": represented,
        "evidence_review_seed_created": represented,
        "limitations": ["Fixture/local review only; not accepted source, evidence, document, relation, datasheet/device, standards, install, repair/safety, access-rights, rights, action, or production proof."],
    }


def _known_gaps(review: Mapping[str, Any]) -> list[str]:
    gaps: list[str] = []
    if review.get("blocked_sources"):
        gaps.append("operator_approval_missing_for_live_metadata_probes")
    if len(review.get("source_cache_review_seeds", [])) < len(H8_SOURCE_IDS):
        gaps.append("not_all_sources_have_review_seeds")
    if not any(item.get("status") == "live_probe_completed" for item in review.get("used_live_probe_outputs", [])):
        gaps.append("approved_live_probe_outputs_not_available")
    return sorted(dict.fromkeys(gaps))


def _truth_boundary() -> dict[str, bool]:
    return {
        "quality_delta_is_public_truth": False,
        "production_search_quality": False,
        "production_documentation_coverage": False,
        "exhaustive_global_coverage": False,
        "documentation_completeness_verified": False,
        "standards_compliance_verified": False,
        "compatibility_correctness_verified": False,
        "installability_verified": False,
        "repair_safety_verified": False,
        "electrical_safety_verified": False,
        "access_rights_verified": False,
        "rights_clearance_claimed": False,
        "open_access_truth_claimed": False,
        "malware_safety_claimed": False,
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
        "enabled_extraction": False,
        "enabled_crawling": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
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

"""Offline H11 storefront review integration helpers.

These helpers consume explicit fixture replay outputs plus blocked or approved
metadata-only live-probe outputs. They produce review seeds and planning
previews only; they do not call networks, query storefronts, fetch product
pages, download, upload, access accounts, purchase, check entitlements,
install, launch, write reviews, scrape, crawl, access restricted sources,
accept truth, or mutate runtime state or indexes.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import hashlib
import json
from pathlib import Path
from typing import Any

from runtime.connectors.h11_storefront.normalizer_common import (
    H11_SOURCE_CONFIGS,
    H11_SOURCE_IDS,
    PRODUCT_FORBIDDEN_TRUE_KEYS as H11_PRODUCT_FORBIDDEN_TRUE_KEYS,
    TRUTH_FORBIDDEN_TRUE_KEYS as H11_TRUTH_FORBIDDEN_TRUE_KEYS,
)

FORBIDDEN_TRUTH_TRUE_KEYS = set(H11_TRUTH_FORBIDDEN_TRUE_KEYS) | {
    "accepts_listing_identity_truth", "accepts_app_product_truth",
    "accepts_version_release_truth", "accepts_price_availability_truth",
    "accepts_acquisition_permission", "accepts_review_rating_truth",
    "accepts_account_entitlement_truth", "accepts_rights_safety_truth",
    "accepts_source_truth", "accepts_evidence_truth", "accepts_candidate_truth",
    "accepted_listing_identity_truth", "accepted_app_product_truth",
    "accepted_version_release_truth", "accepted_price_availability_truth",
    "accepted_acquisition_permission", "accepted_review_rating_truth",
    "accepted_account_entitlement_truth", "accepted_rights_safety_truth",
    "accepted_source_truth", "accepted_evidence_truth", "accepted_candidate_truth",
    "accepted_public_record", "listing_identity_seed_accepts_listing_truth",
    "app_product_seed_accepts_product_truth", "version_release_seed_accepts_version_truth",
    "price_availability_seed_accepts_price_availability_truth",
    "acquisition_path_seed_accepts_action_permission",
    "review_rating_seed_accepts_review_rating_truth",
    "account_entitlement_seed_accepts_license_truth",
    "rights_safety_seed_accepts_rights_safety_truth",
    "source_cache_review_seed_accepts_source", "evidence_review_seed_accepts_evidence",
    "candidate_promotion_preview_promotes_candidate",
    "source_pack_preview_is_imported_or_submitted", "review_seed_is_review_decision",
    "storefront_availability_verified", "current_price_verified",
    "current_availability_verified", "license_entitlement_verified",
    "legal_acquisition_verified", "download_permission_verified",
    "installability_verified", "review_correctness_verified",
    "rating_correctness_verified", "rights_clearance", "rights_clearance_claimed",
    "malware_safety", "malware_safety_claimed", "content_safety",
    "content_safety_claimed", "privacy_safety", "privacy_safety_claimed",
    "verified_authenticity", "verified_authenticity_claimed",
    "production_storefront_coverage", "production_search_quality",
    "production_readiness_claim", "production_readiness_claimed",
    "automatic_future_connector_approval", "future_connector_auto_approval",
    "public_index_mutated", "master_index_mutated",
}

FORBIDDEN_PRODUCT_TRUE_KEYS = set(H11_PRODUCT_FORBIDDEN_TRUE_KEYS) | {
    "api_catalog_sync_permission", "product_page_fetch_permission",
    "download_permission", "account_access_permission", "purchase_permission",
    "checkout_permission", "entitlement_verification_permission",
    "install_launch_permission", "review_rating_write_permission",
    "scraping_crawling_permission", "restricted_source_access_permission",
    "source_sync_enablement", "query_fetch_download_account_purchase_entitlement_install_launch",
    "restricted_source_access", "acquisition_permission", "network_calls_made",
    "api_calls_made", "catalog_fetch_used", "storefront_search_used",
    "product_page_fetch_used", "screenshot_media_fetch_used", "download_used",
    "account_access_used", "purchase_action_used", "entitlement_check_used",
    "install_launch_used", "review_rating_write_used", "scraping_used",
    "crawling_used", "bypass_or_automation_used", "restricted_source_access_used",
    "enabled_source_sync", "enabled_downloads", "enabled_accounts",
    "enabled_purchase_actions", "enabled_entitlement_checks", "enabled_install_launch",
    "enabled_crawling", "enabled_uploads", "enabled_telemetry",
    "changed_public_search_behavior", "mutated_public_index", "mutated_master_index",
}

REVIEW_SEED_KEYS = (
    "storefront_listing_identity_review_seeds",
    "app_product_identity_review_seeds",
    "version_release_channel_review_seeds",
    "price_availability_region_review_seeds",
    "acquisition_path_review_seeds",
    "review_rating_metadata_review_seeds",
    "account_entitlement_boundary_review_seeds",
    "storefront_rights_safety_review_seeds",
    "source_cache_review_seeds",
    "evidence_candidate_review_seeds",
)


def load_h11_storefront_outputs(paths: Sequence[str | Path]) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    for path_text in paths:
        path = Path(path_text)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            raise ValueError(f"{path} must contain a JSON object")
        outputs.append(dict(payload))
    return outputs


def build_h11_storefront_listing_identity_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("storefront_listing_identity", _source_id(inputs), _first_ref(inputs, "storefront_listing_identity_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h11_storefront_listing_identity_review_seed.v0",
        "review_subject_type": "storefront_listing_identity_candidate",
        "accepted_listing_identity_truth": False,
        "listing_identity_seed_accepts_listing_truth": False,
        "storefront_availability_verified": False,
        "limitations": _limitations(inputs) + ["Storefront listing identity review seed is not accepted listing truth, availability proof, acquisition permission, or current metadata truth."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h11_app_product_identity_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("app_product_identity", _source_id(inputs), _first_ref(inputs, "app_product_identity_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h11_app_product_identity_review_seed.v0",
        "review_subject_type": "app_product_identity_candidate",
        "accepted_app_product_truth": False,
        "app_product_seed_accepts_product_truth": False,
        "installability_verified": False,
        "license_entitlement_verified": False,
        "limitations": _limitations(inputs) + ["App/product identity review seed is not accepted product truth, entitlement proof, installability proof, or safety proof."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h11_version_release_channel_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("version_release_channel", _source_id(inputs), _first_ref(inputs, "version_release_channel_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h11_version_release_channel_review_seed.v0",
        "review_subject_type": "version_release_channel_candidate",
        "accepted_version_release_truth": False,
        "version_release_seed_accepts_version_truth": False,
        "limitations": _limitations(inputs) + ["Version/release/channel review seed is not version truth and does not prove current availability, compatibility, installability, or release correctness."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h11_price_availability_region_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("price_availability_region", _source_id(inputs), _first_ref(inputs, "price_availability_region_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h11_price_availability_region_review_seed.v0",
        "review_subject_type": "price_availability_region_candidate",
        "accepted_price_availability_truth": False,
        "price_availability_seed_accepts_price_availability_truth": False,
        "current_price_verified": False,
        "current_availability_verified": False,
        "storefront_availability_verified": False,
        "limitations": _limitations(inputs) + ["Price/availability/region review seed is not current price, current availability, region availability, legal acquisition, or purchase eligibility truth."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h11_acquisition_path_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("acquisition_path", _source_id(inputs), _first_ref(inputs, "acquisition_path_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h11_acquisition_path_review_seed.v0",
        "review_subject_type": "acquisition_path_candidate",
        "accepted_acquisition_permission": False,
        "acquisition_path_seed_accepts_action_permission": False,
        "download_permission_verified": False,
        "legal_acquisition_verified": False,
        "download_permission_current": False,
        "account_access_permission_current": False,
        "purchase_permission_current": False,
        "checkout_permission_current": False,
        "entitlement_verification_permission_current": False,
        "install_launch_permission_current": False,
        "limitations": _limitations(inputs) + ["Acquisition path review seed is not action permission and authorizes no download, purchase, checkout, account, entitlement, install, launch, or acquisition behavior."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h11_review_rating_metadata_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("review_rating_metadata", _source_id(inputs), _first_ref(inputs, "review_rating_metadata_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h11_review_rating_metadata_review_seed.v0",
        "review_subject_type": "review_rating_metadata_candidate",
        "accepted_review_rating_truth": False,
        "review_rating_seed_accepts_review_rating_truth": False,
        "review_correctness_verified": False,
        "rating_correctness_verified": False,
        "review_rating_write_permission_current": False,
        "limitations": _limitations(inputs) + ["Review/rating metadata review seed is not review correctness, rating correctness, quality truth, or write permission."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h11_account_entitlement_boundary_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("account_entitlement_boundary", _source_id(inputs), _first_ref(inputs, "account_entitlement_boundary_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h11_account_entitlement_boundary_review_seed.v0",
        "review_subject_type": "account_entitlement_boundary_candidate",
        "accepted_account_entitlement_truth": False,
        "account_entitlement_seed_accepts_license_truth": False,
        "license_entitlement_verified": False,
        "account_access_permission_current": False,
        "credential_or_token_handling_current": False,
        "receipt_license_entitlement_handling_current": False,
        "limitations": _limitations(inputs) + ["Account/entitlement boundary review seed is not license entitlement truth and does not authorize account, credential, token, receipt, license, entitlement, payment, or user-library access."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h11_storefront_rights_safety_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("storefront_rights_safety", _source_id(inputs), _first_ref(inputs, "storefront_rights_safety_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h11_storefront_rights_safety_review_seed.v0",
        "review_subject_type": "storefront_rights_safety_candidate",
        "accepted_rights_safety_truth": False,
        "rights_safety_seed_accepts_rights_safety_truth": False,
        "rights_clearance_claimed": False,
        "legal_acquisition_verified": False,
        "malware_safety_claimed": False,
        "content_safety_claimed": False,
        "privacy_safety_claimed": False,
        "limitations": _limitations(inputs) + ["Storefront rights/safety review seed is not rights clearance, legal acquisition truth, malware safety, content safety, privacy safety, or production readiness."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h11_source_cache_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("source_cache", _source_id(inputs), _first_ref(inputs, "source_cache_candidate_preview", "preview_id"), inputs)
    seed.update({
        "schema_version": "h11_source_cache_review_seed.v0",
        "review_subject_type": "source_cache_candidate_preview",
        "accepted_source_truth": False,
        "source_cache_review_seed_accepts_source": False,
        "source_cache_write_allowed_current": False,
        "limitations": _limitations(inputs) + ["Source-cache review seed is not accepted source truth and does not write the source cache."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h11_evidence_candidate_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("evidence_candidate", _source_id(inputs), _first_ref(inputs, "evidence_candidate_preview", "preview_id"), inputs)
    seed.update({
        "schema_version": "h11_evidence_candidate_review_seed.v0",
        "review_subject_type": "evidence_candidate_preview",
        "accepted_evidence_truth": False,
        "evidence_review_seed_accepts_evidence": False,
        "evidence_ledger_write_allowed_current": False,
        "limitations": _limitations(inputs) + ["Evidence candidate review seed is not accepted evidence and does not write the evidence ledger."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h11_candidate_promotion_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = {
        "schema_version": "h11_candidate_promotion_preview.v0",
        "candidate_promotion_preview_id": f"h11.candidate_promotion.{source_id}.{_digest(inputs)[:12]}.v0",
        "source_id": source_id,
        "preview_only": True,
        "promotes_candidate": False,
        "candidate_promotion_preview_promotes_candidate": False,
        "accepted_candidate_truth": False,
        "review_required_before_promotion": True,
        "limitations": _limitations(inputs) + ["Candidate promotion preview does not promote, accept, publish, persist, download, purchase, install, launch, or acquire any storefront candidate."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h11_coverage_update_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = {
        "schema_version": "h11_source_coverage_update_preview.v0",
        "coverage_update_preview_id": f"h11.coverage_update.{source_id}.{_digest(inputs)[:12]}.v0",
        "source_id": source_id,
        "coverage_basis": "fixture_review_and_blocked_live_probe_evidence",
        "coverage_preview_only": True,
        "coverage_manifest_is_exhaustive_global_coverage": False,
        "production_storefront_coverage": False,
        "limitations": ["Coverage update preview is not exhaustive global coverage, production storefront coverage, availability proof, price truth, entitlement proof, acquisition proof, or safety proof."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h11_connector_scorecard_update(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    update = {
        "schema_version": "h11_connector_scorecard_update.v0",
        "connector_scorecard_update_id": f"h11.scorecard_update.{source_id}.{_digest(inputs)[:12]}.v0",
        "source_id": source_id,
        "fixture_replay_status": "integrated",
        "live_probe_status": "blocked_or_dry_preflight_without_approval",
        "review_integration_status": "preview_created",
        "production_ready": False,
        "auto_approves_future_connectors": False,
        "limitations": ["Connector scorecard update is not production readiness, acquisition permission, or future connector approval."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_boundaries_fail(update, policy)
    return update


def build_h11_source_pack_update_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = {
        "schema_version": "h11_source_pack_update_preview.v0",
        "source_pack_update_preview_id": f"h11.source_pack_update.{source_id}.{_digest(inputs)[:12]}.v0",
        "source_id": source_id,
        "preview_only": True,
        "source_pack_imported": False,
        "source_pack_submitted": False,
        "source_pack_accepted": False,
        "source_pack_preview_is_imported_or_submitted": False,
        "limitations": ["Source pack update preview is not import, submission, acceptance, public truth, source sync, download, account, purchase, entitlement, install, launch, or acquisition permission."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h11_review_integration_result(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    outputs = list(inputs.get("outputs") or [])
    input_refs = list(inputs.get("input_refs") or [])
    by_source = _best_inputs_by_source(outputs)
    sources = [source for source in H11_SOURCE_IDS if source in by_source] or list(H11_SOURCE_IDS)
    fixture_outputs = [_output_summary(item) for item in outputs if item.get("schema_version") == "h11_storefront_fixture_replay_result.v0"]
    live_outputs = [_output_summary(item) for item in outputs if item.get("schema_version") == "h11_storefront_live_probe_result.v0"]
    blocked_sources = sorted({str(item.get("source_id")) for item in outputs if str(item.get("result_status", "")).startswith("blocked") and item.get("source_id")})
    seed_inputs = [by_source.get(source_id, {"source_id": source_id}) for source_id in sources]
    result = {
        "schema_version": "h11_storefront_review_integration_result.v0",
        "review_integration_result_id": f"h11.review_integration.{_digest({'sources': sources, 'inputs': input_refs})[:12]}.v0",
        "wave_id": "H11",
        "sources": sources,
        "source_count": len(sources),
        "input_refs": input_refs,
        "used_fixture_outputs": fixture_outputs,
        "used_live_probe_outputs": live_outputs,
        "storefront_listing_identity_review_seeds": [build_h11_storefront_listing_identity_review_seed(item, policy) for item in seed_inputs],
        "app_product_identity_review_seeds": [build_h11_app_product_identity_review_seed(item, policy) for item in seed_inputs],
        "version_release_channel_review_seeds": [build_h11_version_release_channel_review_seed(item, policy) for item in seed_inputs],
        "price_availability_region_review_seeds": [build_h11_price_availability_region_review_seed(item, policy) for item in seed_inputs],
        "acquisition_path_review_seeds": [build_h11_acquisition_path_review_seed(item, policy) for item in seed_inputs],
        "review_rating_metadata_review_seeds": [build_h11_review_rating_metadata_review_seed(item, policy) for item in seed_inputs],
        "account_entitlement_boundary_review_seeds": [build_h11_account_entitlement_boundary_review_seed(item, policy) for item in seed_inputs],
        "storefront_rights_safety_review_seeds": [build_h11_storefront_rights_safety_review_seed(item, policy) for item in seed_inputs],
        "source_cache_review_seeds": [build_h11_source_cache_review_seed(item, policy) for item in seed_inputs],
        "evidence_candidate_review_seeds": [build_h11_evidence_candidate_review_seed(item, policy) for item in seed_inputs],
        "candidate_promotion_previews": [build_h11_candidate_promotion_preview(item, policy) for item in seed_inputs],
        "coverage_update_previews": [build_h11_coverage_update_preview(item, policy) for item in seed_inputs],
        "scorecard_updates": [build_h11_connector_scorecard_update(item, policy) for item in seed_inputs],
        "source_pack_update_previews": [build_h11_source_pack_update_preview(item, policy) for item in seed_inputs],
        "blocked_sources": blocked_sources,
        "warnings": ["H11 live probes remain blocked pending operator approval."] if blocked_sources else [],
        "limitations": [
            "H11 review integration is a wave-level audit and rehearsal, not promotion.",
            "Fixture replay and blocked/preflight live-probe reports do not prove listing identity, app/product identity, version truth, current price, current availability, region availability, account entitlement, legal acquisition, download permission, installability, review correctness, rating correctness, rights clearance, malware safety, privacy safety, content safety, production coverage, or live endpoint behavior.",
        ],
        "accepts_listing_identity_truth": False,
        "accepts_app_product_truth": False,
        "accepts_version_release_truth": False,
        "accepts_price_availability_truth": False,
        "accepts_acquisition_permission": False,
        "accepts_review_rating_truth": False,
        "accepts_account_entitlement_truth": False,
        "accepts_rights_safety_truth": False,
        "accepts_source_truth": False,
        "accepts_evidence_truth": False,
        "accepts_candidate_truth": False,
        "mutates_public_index": False,
        "mutates_master_index": False,
        "enables_api_catalog_sync": False,
        "enables_product_page_fetch": False,
        "enables_downloads": False,
        "enables_account_access": False,
        "enables_purchase_automation": False,
        "enables_entitlement_verification": False,
        "enables_install_launch": False,
        "enables_review_rating_write": False,
        "enables_scraping_crawling": False,
        "enables_restricted_source_access": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Review seeds and previews require explicit human review before any downstream persistence."],
    }
    _raise_if_boundaries_fail(result, policy)
    return result


def summarize_h11_review_integration(result: Mapping[str, Any]) -> dict[str, Any]:
    errors = detect_h11_review_truth_boundary_violations(result) + detect_h11_review_product_boundary_violations(result)
    return {
        "schema_version": "h11_review_integration_summary.v0",
        "status": "pass" if not errors else "invalid",
        "review_integration_result_id": result.get("review_integration_result_id"),
        "source_count": len(result.get("sources", [])),
        "storefront_listing_identity_review_seed_count": len(result.get("storefront_listing_identity_review_seeds", [])),
        "app_product_identity_review_seed_count": len(result.get("app_product_identity_review_seeds", [])),
        "version_release_channel_review_seed_count": len(result.get("version_release_channel_review_seeds", [])),
        "price_availability_region_review_seed_count": len(result.get("price_availability_region_review_seeds", [])),
        "acquisition_path_review_seed_count": len(result.get("acquisition_path_review_seeds", [])),
        "review_rating_metadata_review_seed_count": len(result.get("review_rating_metadata_review_seeds", [])),
        "account_entitlement_boundary_review_seed_count": len(result.get("account_entitlement_boundary_review_seeds", [])),
        "storefront_rights_safety_review_seed_count": len(result.get("storefront_rights_safety_review_seeds", [])),
        "source_cache_review_seed_count": len(result.get("source_cache_review_seeds", [])),
        "evidence_candidate_review_seed_count": len(result.get("evidence_candidate_review_seeds", [])),
        "blocked_sources": list(result.get("blocked_sources", [])),
        "truth_boundary_errors": detect_h11_review_truth_boundary_violations(result),
        "product_boundary_errors": detect_h11_review_product_boundary_violations(result),
    }


def detect_h11_review_truth_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return sorted(dict.fromkeys(f"truth boundary violation: {path}=true" for path, key, value in _iter_key_values(result) if key in FORBIDDEN_TRUTH_TRUE_KEYS and value is True))


def detect_h11_review_product_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return sorted(dict.fromkeys(f"product boundary violation: {path}=true" for path, key, value in _iter_key_values(result) if key in FORBIDDEN_PRODUCT_TRUE_KEYS and value is True))


def _best_inputs_by_source(outputs: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    by_source: dict[str, dict[str, Any]] = {}
    for item in outputs:
        source_id = item.get("source_id")
        if source_id in H11_SOURCE_IDS:
            normalized = item.get("normalized_record")
            if isinstance(normalized, Mapping):
                by_source[str(source_id)] = dict(normalized)
            elif str(source_id) not in by_source:
                by_source[str(source_id)] = dict(item)
    return by_source


def _output_summary(item: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": item.get("schema_version"),
        "source_id": item.get("source_id"),
        "status": item.get("result_status") or item.get("replay_status"),
        "ref": item.get("live_probe_result_id") or item.get("fixture_replay_result_id") or item.get("replay_result_id") or item.get("fixture_id"),
        "request_count": item.get("request_count", 0),
        "network_used": bool(item.get("network_used", False)),
    }


def _source_id(inputs: Mapping[str, Any]) -> str:
    source_id = str(inputs.get("source_id") or "")
    if source_id not in H11_SOURCE_IDS:
        raise ValueError(f"unknown or missing H11 source_id: {source_id}")
    return source_id


def _first_ref(inputs: Mapping[str, Any], *keys: str) -> str:
    for key in keys:
        value = inputs.get(key)
        if isinstance(value, list) and value:
            first = value[0]
            if isinstance(first, Mapping):
                for id_key in ("candidate_id", "preview_id", "source_cache_candidate_preview_id", "evidence_candidate_preview_id"):
                    if first.get(id_key):
                        return str(first[id_key])
            return str(first)
        if isinstance(value, Mapping):
            for id_key in ("candidate_id", "preview_id", "source_cache_candidate_preview_id", "evidence_candidate_preview_id"):
                if value.get(id_key):
                    return str(value[id_key])
        if value:
            return str(value)
    return str(inputs.get("normalized_record_id") or inputs.get("live_probe_result_id") or inputs.get("fixture_replay_result_id") or inputs.get("source_id") or "unknown")


def _limitations(inputs: Mapping[str, Any]) -> list[str]:
    values = inputs.get("limitations") or inputs.get("source_limitations") or []
    if isinstance(values, str):
        values = [values]
    return [str(item) for item in values if item]


def _seed_base(kind: str, source_id: str, subject_ref: str, inputs: Mapping[str, Any]) -> dict[str, Any]:
    config = H11_SOURCE_CONFIGS.get(source_id, {})
    return {
        "review_seed_id": f"h11.{kind}.review_seed.{source_id}.{_digest({'ref': subject_ref, 'kind': kind})[:12]}.v0",
        "wave_id": "H11",
        "source_id": source_id,
        "connector_family": inputs.get("connector_family") or config.get("connector_family", "unknown"),
        "review_subject_ref": subject_ref,
        "input_schema_version": inputs.get("schema_version", "unknown"),
        "review_required": True,
        "review_decision": "not_made",
        "preview_only": True,
        "source_cache_write_allowed_current": False,
        "evidence_acceptance_allowed_current": False,
        "candidate_acceptance_allowed_current": False,
        "public_index_mutation_allowed_current": False,
        "master_index_mutation_allowed_current": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Review seed is a preview only and is not a review decision."],
    }


def _truth_boundary() -> dict[str, bool]:
    return {
        "listing_identity_seed_accepts_listing_truth": False,
        "app_product_seed_accepts_product_truth": False,
        "version_release_seed_accepts_version_truth": False,
        "price_availability_seed_accepts_price_availability_truth": False,
        "acquisition_path_seed_accepts_action_permission": False,
        "review_rating_seed_accepts_review_rating_truth": False,
        "account_entitlement_seed_accepts_license_truth": False,
        "rights_safety_seed_accepts_rights_safety_truth": False,
        "source_cache_review_seed_accepts_source": False,
        "evidence_review_seed_accepts_evidence": False,
        "candidate_promotion_preview_promotes_candidate": False,
        "source_pack_preview_is_imported_or_submitted": False,
        "review_seed_is_review_decision": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
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
        "accepted_listing_identity_truth": False,
        "accepted_app_product_truth": False,
        "accepted_version_release_truth": False,
        "accepted_price_availability_truth": False,
        "accepted_acquisition_permission": False,
        "accepted_review_rating_truth": False,
        "accepted_account_entitlement_truth": False,
        "accepted_rights_safety_truth": False,
        "accepted_source_truth": False,
        "accepted_evidence_truth": False,
        "accepted_candidate_truth": False,
    }


def _product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_hosting": False,
        "enabled_live_probes": False,
        "enabled_source_sync": False,
        "enabled_downloads": False,
        "enabled_accounts": False,
        "enabled_purchase_actions": False,
        "enabled_entitlement_checks": False,
        "enabled_install_launch": False,
        "enabled_crawling": False,
        "enabled_scraping": False,
        "enabled_uploads": False,
        "enabled_telemetry": False,
        "network_calls_made": False,
        "api_calls_made": False,
        "catalog_fetch_used": False,
        "storefront_search_used": False,
        "product_page_fetch_used": False,
        "screenshot_media_fetch_used": False,
        "download_used": False,
        "account_access_used": False,
        "purchase_action_used": False,
        "entitlement_check_used": False,
        "install_launch_used": False,
        "review_rating_write_used": False,
        "scraping_used": False,
        "crawling_used": False,
        "restricted_source_access_used": False,
        "bypass_or_automation_used": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def _raise_if_boundaries_fail(payload: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> None:
    errors = detect_h11_review_truth_boundary_violations(payload, policy)
    errors.extend(detect_h11_review_product_boundary_violations(payload, policy))
    if errors:
        raise ValueError("; ".join(errors))


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

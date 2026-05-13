"""Offline H9 media metadata review integration helpers.

These helpers consume explicit H9 fixture replay outputs and blocked or
approved metadata-only live-probe outputs. They produce review seeds and
planning previews only; they do not call networks, query catalogs, fetch
media, download payloads, upload media, submit or generate fingerprints,
scrape, crawl, access restricted sources, accept truth, or mutate runtime
state or indexes.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import hashlib
import json
from pathlib import Path
from typing import Any

from control.prototypes.legacy_runtime.connectors.h9_media_metadata.normalizer_common import H9_SOURCE_CONFIGS, H9_SOURCE_IDS

FORBIDDEN_TRUTH_TRUE_KEYS = {
    "accepted_candidate_truth", "accepted_creator_collection_relation_truth",
    "accepted_evidence_truth", "accepted_fingerprint_identity_truth",
    "accepted_image_video_map_truth", "accepted_media_identity_truth",
    "accepted_music_identity_truth", "accepted_public_record",
    "accepted_rights_license_truth", "accepted_safety_privacy_truth",
    "accepted_source_truth", "automatic_future_connector_approval",
    "candidate_promotion_preview_promotes_candidate", "content_safety_claimed",
    "content_safety_verified", "creative_commons_metadata_is_license_truth",
    "creative_commons_truth_claimed", "creative_commons_truth_verified",
    "creator_collection_relation_candidate_is_truth",
    "creator_collection_seed_accepts_relation_truth",
    "evidence_review_seed_accepts_evidence",
    "fingerprint_identity_verified", "fingerprint_match_candidate_is_truth",
    "fingerprint_seed_accepts_identity_truth",
    "future_connector_auto_approval", "image_identity_verified",
    "image_video_map_identity_candidate_is_truth",
    "image_video_map_seed_accepts_object_truth",
    "license_correctness_verified", "license_metadata_is_rights_clearance",
    "malware_safety", "malware_safety_claimed", "master_index_mutated",
    "media_authenticity_verified", "media_object_identity_candidate_is_truth",
    "media_object_seed_accepts_media_truth", "music_identity_candidate_is_truth",
    "music_identity_seed_accepts_music_truth", "privacy_safety_claimed",
    "privacy_safety_verified", "production_media_coverage",
    "production_readiness_claimed", "production_search_quality",
    "public_domain_metadata_is_public_domain_truth", "public_domain_truth_claimed",
    "public_domain_truth_verified", "public_index_mutated", "review_seed_is_review_decision",
    "rights_clearance", "rights_clearance_claimed", "rights_license_candidate_is_rights_truth",
    "rights_license_seed_accepts_rights_truth", "safety_privacy_candidate_is_safety_truth",
    "safety_privacy_seed_accepts_safety_truth", "source_cache_candidate_is_accepted_source",
    "source_cache_review_seed_accepts_source", "source_pack_preview_is_imported_or_submitted",
    "verified_authenticity", "verified_authenticity_claimed",
}

FORBIDDEN_PRODUCT_TRUE_KEYS = {
    "acquisition_permission", "api_calls_made", "api_catalog_sync_permission",
    "api_query_used", "audio_download_used", "browser_automation_used",
    "bypass_or_automation_used", "catalog_fetch_used", "changed_public_search_behavior",
    "crawling_used", "enabled_accounts", "enabled_crawling", "enabled_downloads",
    "enabled_fingerprinting", "enabled_hosting", "enabled_live_probes",
    "enabled_source_sync", "enabled_telemetry", "enabled_uploads",
    "enables_api_catalog_sync", "enables_fingerprinting", "enables_media_downloads",
    "enables_media_uploads", "enables_restricted_source_access",
    "enables_scraping_crawling", "fingerprint_generation_used", "fingerprint_lookup_used",
    "fingerprint_submission_used", "image_download_used", "map_download_used",
    "media_download_used", "media_upload_used", "mutated_master_index",
    "mutated_public_index", "network_calls_made", "restricted_source_access_used",
    "score_download_used", "scraping_used", "thumbnail_fetch_used", "video_download_used",
}

REVIEW_SEED_KEYS = (
    "media_object_identity_review_seeds",
    "music_work_recording_release_review_seeds",
    "image_video_map_identity_review_seeds",
    "media_creator_collection_relation_review_seeds",
    "media_fingerprint_review_seeds",
    "media_rights_license_review_seeds",
    "media_safety_privacy_review_seeds",
    "source_cache_review_seeds",
    "evidence_candidate_review_seeds",
)


def load_h9_media_metadata_outputs(paths: Sequence[str | Path]) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    for path_text in paths:
        path = Path(path_text)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            raise ValueError(f"{path} must contain a JSON object")
        outputs.append(dict(payload))
    return outputs


def build_h9_media_object_identity_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("media_object_identity", _source_id(inputs), _first_ref(inputs, "media_object_identity_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h9_media_object_identity_review_seed.v0",
        "review_subject_type": "media_object_identity_candidate",
        "accepted_media_identity_truth": False,
        "media_object_seed_accepts_media_truth": False,
        "media_authenticity_verified": False,
        "media_download_permission": False,
        "limitations": _limitations(inputs) + ["Media object review seed is not media truth, availability proof, rights clearance, authenticity proof, malware safety proof, or download permission."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h9_music_work_recording_release_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("music_work_recording_release", _source_id(inputs), _first_ref(inputs, "music_work_recording_release_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h9_music_work_recording_release_review_seed.v0",
        "review_subject_type": "music_work_recording_release_candidate",
        "accepted_music_identity_truth": False,
        "music_identity_seed_accepts_music_truth": False,
        "audio_identity_verified": False,
        "media_download_permission": False,
        "limitations": _limitations(inputs) + ["Music work/recording/release review seed is not music identity truth, audio identity proof, streaming permission, download permission, or redistribution permission."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h9_image_video_map_identity_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("image_video_map_identity", _source_id(inputs), _first_ref(inputs, "image_video_map_identity_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h9_image_video_map_identity_review_seed.v0",
        "review_subject_type": "image_video_map_identity_candidate",
        "accepted_image_video_map_truth": False,
        "image_video_map_seed_accepts_object_truth": False,
        "image_identity_verified": False,
        "geospatial_correctness_verified": False,
        "media_download_permission": False,
        "limitations": _limitations(inputs) + ["Image/video/map review seed is not object truth, geospatial correctness proof, rights clearance, authenticity proof, or download permission."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h9_media_creator_collection_relation_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("media_creator_collection_relation", _source_id(inputs), _first_ref(inputs, "media_creator_collection_relation_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h9_media_creator_collection_relation_review_seed.v0",
        "review_subject_type": "media_creator_collection_relation_candidate",
        "accepted_creator_collection_relation_truth": False,
        "creator_collection_seed_accepts_relation_truth": False,
        "attribution_correctness_verified": False,
        "limitations": _limitations(inputs) + ["Creator/collection relation review seed is not relation truth, duplicate truth, attribution correctness, or rights clearance."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h9_media_fingerprint_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("media_fingerprint", _source_id(inputs), _first_ref(inputs, "media_fingerprint_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h9_media_fingerprint_review_seed.v0",
        "review_subject_type": "media_fingerprint_candidate",
        "accepted_fingerprint_identity_truth": False,
        "fingerprint_seed_accepts_identity_truth": False,
        "fingerprint_identity_verified": False,
        "fingerprint_lookup_permission_current": False,
        "fingerprint_submission_permission_current": False,
        "fingerprint_generation_permission_current": False,
        "limitations": _limitations(inputs) + ["Fingerprint review seed is not identity truth and grants no lookup, upload, submission, generation, safety, or rights permission."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h9_media_rights_license_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("media_rights_license", _source_id(inputs), _first_ref(inputs, "media_rights_license_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h9_media_rights_license_review_seed.v0",
        "review_subject_type": "media_rights_license_candidate",
        "accepted_rights_license_truth": False,
        "rights_license_seed_accepts_rights_truth": False,
        "rights_clearance_claimed": False,
        "public_domain_truth_claimed": False,
        "creative_commons_truth_claimed": False,
        "media_download_permission": False,
        "redistribution_permission_current": False,
        "limitations": _limitations(inputs) + ["Rights/license review seed is not rights clearance, public-domain truth, Creative Commons truth, attribution correctness, download permission, or redistribution permission."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h9_media_safety_privacy_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("media_safety_privacy", _source_id(inputs), _first_ref(inputs, "media_safety_privacy_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h9_media_safety_privacy_review_seed.v0",
        "review_subject_type": "media_safety_privacy_candidate",
        "accepted_safety_privacy_truth": False,
        "safety_privacy_seed_accepts_safety_truth": False,
        "content_safety_claimed": False,
        "privacy_safety_claimed": False,
        "malware_safety_claimed": False,
        "limitations": _limitations(inputs) + ["Safety/privacy review seed is not content safety truth, privacy safety truth, malware safety proof, takedown resolution, or release approval."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h9_source_cache_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("source_cache", _source_id(inputs), _first_ref(inputs, "source_cache_candidate_preview", "source_cache_candidate_preview_id"), inputs)
    seed.update({
        "schema_version": "h9_source_cache_review_seed.v0",
        "review_subject_type": "source_cache_candidate_preview",
        "accepted_source_truth": False,
        "source_cache_review_seed_accepts_source": False,
        "source_cache_write_allowed_current": False,
        "limitations": _limitations(inputs) + ["Source-cache review seed is not accepted source truth and does not write the source cache."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h9_evidence_candidate_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("evidence_candidate", _source_id(inputs), _first_ref(inputs, "evidence_candidate_preview", "evidence_candidate_preview_id"), inputs)
    seed.update({
        "schema_version": "h9_evidence_candidate_review_seed.v0",
        "review_subject_type": "evidence_candidate_preview",
        "accepted_evidence_truth": False,
        "evidence_review_seed_accepts_evidence": False,
        "evidence_ledger_write_allowed_current": False,
        "limitations": _limitations(inputs) + ["Evidence candidate review seed is not accepted evidence and does not write the evidence ledger."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h9_candidate_promotion_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = {
        "schema_version": "h9_candidate_promotion_preview.v0",
        "candidate_promotion_preview_id": f"h9.candidate_promotion.{source_id}.{_digest(inputs)[:12]}.v0",
        "source_id": source_id,
        "preview_only": True,
        "promotes_candidate": False,
        "candidate_promotion_preview_promotes_candidate": False,
        "accepted_candidate_truth": False,
        "review_required_before_promotion": True,
        "limitations": _limitations(inputs) + ["Candidate promotion preview does not promote, accept, publish, or persist any media metadata candidate."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h9_coverage_update_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = {
        "schema_version": "h9_source_coverage_update_preview.v0",
        "coverage_update_preview_id": f"h9.coverage_update.{source_id}.{_digest(inputs)[:12]}.v0",
        "source_id": source_id,
        "coverage_basis": "fixture_review_and_blocked_live_probe_evidence",
        "coverage_preview_only": True,
        "coverage_manifest_is_exhaustive_global_coverage": False,
        "production_media_coverage": False,
        "limitations": ["Coverage update preview is not exhaustive global coverage or production media coverage."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h9_connector_scorecard_update(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    update = {
        "schema_version": "h9_connector_scorecard_update.v0",
        "connector_scorecard_update_id": f"h9.scorecard_update.{source_id}.{_digest(inputs)[:12]}.v0",
        "source_id": source_id,
        "fixture_replay_status": "integrated",
        "live_probe_status": "blocked_or_dry_preflight_without_approval",
        "review_integration_status": "preview_created",
        "production_ready": False,
        "auto_approves_future_connectors": False,
        "limitations": ["Connector scorecard update is not production readiness or future connector approval."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_boundaries_fail(update, policy)
    return update


def build_h9_source_pack_update_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = {
        "schema_version": "h9_source_pack_update_preview.v0",
        "source_pack_update_preview_id": f"h9.source_pack_update.{source_id}.{_digest(inputs)[:12]}.v0",
        "source_id": source_id,
        "preview_only": True,
        "source_pack_imported": False,
        "source_pack_submitted": False,
        "source_pack_accepted": False,
        "source_pack_preview_is_imported_or_submitted": False,
        "limitations": ["Source pack update preview is not import, submission, acceptance, or public truth."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h9_review_integration_result(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    outputs = list(inputs.get("outputs") or [])
    input_refs = list(inputs.get("input_refs") or [])
    by_source = _best_inputs_by_source(outputs)
    sources = sorted(by_source) or list(H9_SOURCE_IDS)
    fixture_outputs = [_output_summary(item) for item in outputs if item.get("schema_version") == "h9_media_metadata_fixture_replay_result.v0"]
    live_outputs = [_output_summary(item) for item in outputs if item.get("schema_version") == "h9_media_metadata_live_probe_result.v0"]
    blocked_sources = sorted({str(item.get("source_id")) for item in outputs if str(item.get("result_status", "")).startswith("blocked") and item.get("source_id")})
    seed_inputs = [by_source.get(source_id, {"source_id": source_id}) for source_id in sources]
    result = {
        "schema_version": "h9_media_metadata_review_integration_result.v0",
        "review_integration_result_id": f"h9.review_integration.{_digest({'sources': sources, 'inputs': input_refs})[:12]}.v0",
        "wave_id": "H9",
        "sources": sources,
        "source_count": len(sources),
        "input_refs": input_refs,
        "used_fixture_outputs": fixture_outputs,
        "used_live_probe_outputs": live_outputs,
        "media_object_identity_review_seeds": [build_h9_media_object_identity_review_seed(item, policy) for item in seed_inputs],
        "music_work_recording_release_review_seeds": [build_h9_music_work_recording_release_review_seed(item, policy) for item in seed_inputs],
        "image_video_map_identity_review_seeds": [build_h9_image_video_map_identity_review_seed(item, policy) for item in seed_inputs],
        "media_creator_collection_relation_review_seeds": [build_h9_media_creator_collection_relation_review_seed(item, policy) for item in seed_inputs],
        "media_fingerprint_review_seeds": [build_h9_media_fingerprint_review_seed(item, policy) for item in seed_inputs],
        "media_rights_license_review_seeds": [build_h9_media_rights_license_review_seed(item, policy) for item in seed_inputs],
        "media_safety_privacy_review_seeds": [build_h9_media_safety_privacy_review_seed(item, policy) for item in seed_inputs],
        "source_cache_review_seeds": [build_h9_source_cache_review_seed(item, policy) for item in seed_inputs],
        "evidence_candidate_review_seeds": [build_h9_evidence_candidate_review_seed(item, policy) for item in seed_inputs],
        "candidate_promotion_previews": [build_h9_candidate_promotion_preview(item, policy) for item in seed_inputs],
        "coverage_update_previews": [build_h9_coverage_update_preview(item, policy) for item in seed_inputs],
        "scorecard_updates": [build_h9_connector_scorecard_update(item, policy) for item in seed_inputs],
        "source_pack_update_previews": [build_h9_source_pack_update_preview(item, policy) for item in seed_inputs],
        "blocked_sources": blocked_sources,
        "warnings": ["H9 live probes remain blocked pending operator approval."] if blocked_sources else [],
        "limitations": [
            "H9 review integration is a wave-level audit and rehearsal, not promotion.",
            "Fixture replay and blocked/preflight live-probe reports do not prove media authenticity, audio identity, image identity, map correctness, rights clearance, public-domain status, Creative Commons validity, attribution correctness, malware safety, privacy safety, content safety, production coverage, or live endpoint behavior.",
        ],
        "accepts_media_identity_truth": False,
        "accepts_music_identity_truth": False,
        "accepts_image_video_map_truth": False,
        "accepts_creator_collection_relation_truth": False,
        "accepts_fingerprint_identity_truth": False,
        "accepts_rights_license_truth": False,
        "accepts_safety_privacy_truth": False,
        "accepts_source_truth": False,
        "accepts_evidence_truth": False,
        "accepts_candidate_truth": False,
        "mutates_public_index": False,
        "mutates_master_index": False,
        "enables_api_catalog_sync": False,
        "enables_media_downloads": False,
        "enables_media_uploads": False,
        "enables_fingerprinting": False,
        "enables_scraping_crawling": False,
        "enables_restricted_source_access": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Review seeds and previews require explicit human review before any downstream persistence."],
    }
    _raise_if_boundaries_fail(result, policy)
    return result


def summarize_h9_review_integration(result: Mapping[str, Any]) -> dict[str, Any]:
    errors = detect_h9_review_truth_boundary_violations(result) + detect_h9_review_product_boundary_violations(result)
    return {
        "schema_version": "h9_review_integration_summary.v0",
        "status": "pass" if not errors else "invalid",
        "review_integration_result_id": result.get("review_integration_result_id"),
        "source_count": len(result.get("sources", [])),
        "media_object_identity_review_seed_count": len(result.get("media_object_identity_review_seeds", [])),
        "music_work_recording_release_review_seed_count": len(result.get("music_work_recording_release_review_seeds", [])),
        "image_video_map_identity_review_seed_count": len(result.get("image_video_map_identity_review_seeds", [])),
        "media_creator_collection_relation_review_seed_count": len(result.get("media_creator_collection_relation_review_seeds", [])),
        "media_fingerprint_review_seed_count": len(result.get("media_fingerprint_review_seeds", [])),
        "media_rights_license_review_seed_count": len(result.get("media_rights_license_review_seeds", [])),
        "media_safety_privacy_review_seed_count": len(result.get("media_safety_privacy_review_seeds", [])),
        "source_cache_review_seed_count": len(result.get("source_cache_review_seeds", [])),
        "evidence_candidate_review_seed_count": len(result.get("evidence_candidate_review_seeds", [])),
        "blocked_sources": list(result.get("blocked_sources", [])),
        "truth_boundary_errors": detect_h9_review_truth_boundary_violations(result),
        "product_boundary_errors": detect_h9_review_product_boundary_violations(result),
    }


def detect_h9_review_truth_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return sorted(dict.fromkeys(f"truth boundary violation: {path}=true" for path, key, value in _iter_key_values(result) if key in FORBIDDEN_TRUTH_TRUE_KEYS and value is True))


def detect_h9_review_product_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return sorted(dict.fromkeys(f"product boundary violation: {path}=true" for path, key, value in _iter_key_values(result) if key in FORBIDDEN_PRODUCT_TRUE_KEYS and value is True))


def _best_inputs_by_source(outputs: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    by_source: dict[str, dict[str, Any]] = {}
    for item in outputs:
        source_id = item.get("source_id")
        if source_id in H9_SOURCE_IDS:
            normalized = item.get("normalized_record")
            if item.get("schema_version") == "h9_media_metadata_fixture_replay_result.v0" and isinstance(normalized, Mapping):
                by_source[str(source_id)] = dict(normalized)
            elif str(source_id) not in by_source:
                by_source[str(source_id)] = dict(normalized) if isinstance(normalized, Mapping) else dict(item)
    return by_source


def _output_summary(item: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": item.get("schema_version"),
        "source_id": item.get("source_id"),
        "status": item.get("replay_status") or item.get("result_status"),
        "ref": item.get("live_probe_result_id") or item.get("fixture_replay_result_id") or item.get("fixture_id"),
        "request_count": item.get("request_count", 0),
        "network_used": bool(item.get("network_used", False)),
    }


def _source_id(inputs: Mapping[str, Any]) -> str:
    source_id = str(inputs.get("source_id") or "")
    if source_id not in H9_SOURCE_IDS:
        raise ValueError(f"unknown or missing H9 source_id: {source_id}")
    return source_id


def _first_ref(inputs: Mapping[str, Any], *keys: str) -> str:
    for key in keys:
        value = inputs.get(key)
        if isinstance(value, list) and value:
            first = value[0]
            if isinstance(first, Mapping):
                for id_key in ("candidate_id", "source_cache_candidate_preview_id", "evidence_candidate_preview_id"):
                    if first.get(id_key):
                        return str(first[id_key])
            return str(first)
        if isinstance(value, Mapping):
            for id_key in ("candidate_id", "source_cache_candidate_preview_id", "evidence_candidate_preview_id"):
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
    config = H9_SOURCE_CONFIGS.get(source_id, {})
    return {
        "review_seed_id": f"h9.{kind}.review_seed.{source_id}.{_digest({'ref': subject_ref, 'kind': kind})[:12]}.v0",
        "wave_id": "H9",
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
        "media_object_seed_accepts_media_truth": False,
        "music_identity_seed_accepts_music_truth": False,
        "image_video_map_seed_accepts_object_truth": False,
        "creator_collection_seed_accepts_relation_truth": False,
        "fingerprint_seed_accepts_identity_truth": False,
        "rights_license_seed_accepts_rights_truth": False,
        "safety_privacy_seed_accepts_safety_truth": False,
        "source_cache_review_seed_accepts_source": False,
        "evidence_review_seed_accepts_evidence": False,
        "candidate_promotion_preview_promotes_candidate": False,
        "source_pack_preview_is_imported_or_submitted": False,
        "review_seed_is_review_decision": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "public_domain_truth_claimed": False,
        "creative_commons_truth_claimed": False,
        "content_safety_claimed": False,
        "privacy_safety_claimed": False,
        "malware_safety_claimed": False,
        "verified_authenticity_claimed": False,
        "production_readiness_claimed": False,
        "automatic_future_connector_approval": False,
        "accepted_media_identity_truth": False,
        "accepted_music_identity_truth": False,
        "accepted_image_video_map_truth": False,
        "accepted_creator_collection_relation_truth": False,
        "accepted_fingerprint_identity_truth": False,
        "accepted_rights_license_truth": False,
        "accepted_safety_privacy_truth": False,
        "accepted_source_truth": False,
        "accepted_evidence_truth": False,
        "accepted_candidate_truth": False,
        "accepted_public_record": False,
        "media_object_identity_candidate_is_truth": False,
        "music_identity_candidate_is_truth": False,
        "image_video_map_identity_candidate_is_truth": False,
        "creator_collection_relation_candidate_is_truth": False,
        "fingerprint_match_candidate_is_truth": False,
        "rights_license_candidate_is_rights_truth": False,
        "safety_privacy_candidate_is_safety_truth": False,
        "license_metadata_is_rights_clearance": False,
        "public_domain_metadata_is_public_domain_truth": False,
        "creative_commons_metadata_is_license_truth": False,
    }


def _product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_hosting": False,
        "enabled_live_probes": False,
        "enabled_source_sync": False,
        "enabled_downloads": False,
        "enabled_uploads": False,
        "enabled_fingerprinting": False,
        "enabled_crawling": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "network_calls_made": False,
        "api_calls_made": False,
        "catalog_fetch_used": False,
        "media_download_used": False,
        "image_download_used": False,
        "video_download_used": False,
        "audio_download_used": False,
        "map_download_used": False,
        "score_download_used": False,
        "thumbnail_fetch_used": False,
        "media_upload_used": False,
        "fingerprint_lookup_used": False,
        "fingerprint_submission_used": False,
        "fingerprint_generation_used": False,
        "scraping_used": False,
        "crawling_used": False,
        "browser_automation_used": False,
        "bypass_or_automation_used": False,
        "restricted_source_access_used": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def _raise_if_boundaries_fail(payload: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> None:
    errors = detect_h9_review_truth_boundary_violations(payload, policy)
    errors.extend(detect_h9_review_product_boundary_violations(payload, policy))
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

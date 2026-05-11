"""Fail-closed H9 media metadata live-probe helpers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from pathlib import Path
from typing import Any

from runtime.connectors.h9_media_metadata.normalizer_common import (
    build_h9_evidence_candidate_preview as _fixture_evidence_preview,
    build_h9_image_video_map_identity_candidate as _fixture_visual_candidate,
    build_h9_media_creator_collection_relation_candidates as _fixture_relation_candidates,
    build_h9_media_fingerprint_candidate as _fixture_fingerprint_candidate,
    build_h9_media_object_identity_candidate as _fixture_media_candidate,
    build_h9_media_rights_license_candidate as _fixture_rights_candidate,
    build_h9_media_safety_privacy_candidate as _fixture_safety_candidate,
    build_h9_music_work_recording_release_candidate as _fixture_music_candidate,
    build_h9_source_cache_candidate_preview as _fixture_source_cache_preview,
    detect_h9_product_boundary_violations as _fixture_product_violations,
    detect_h9_truth_boundary_violations as _fixture_truth_violations,
    normalize_h9_media_metadata_fixture,
)

POLICY_PATHS = {
    "live_probe_policy": "control/inventory/connectors/h9_media_metadata_live_probe_policy.json",
    "allowed_requests": "control/inventory/connectors/h9_media_metadata_live_probe_allowed_requests.json",
    "endpoint_policy": "control/inventory/connectors/h9_media_metadata_live_probe_endpoint_policy.json",
    "rate_limit_policy": "control/inventory/connectors/h9_media_metadata_live_probe_rate_limit_policy.json",
    "cache_policy": "control/inventory/connectors/h9_media_metadata_live_probe_cache_policy.json",
    "kill_switch_policy": "control/inventory/connectors/h9_media_metadata_live_probe_kill_switch_policy.json",
    "output_policy": "control/inventory/connectors/h9_media_metadata_live_probe_output_policy.json",
    "path_policy": "control/inventory/connectors/h9_media_metadata_live_probe_path_policy.json",
    "review_policy": "control/inventory/connectors/h9_media_metadata_live_probe_review_policy.json",
    "truth_policy": "control/inventory/connectors/h9_media_metadata_live_probe_truth_policy.json",
    "no_download_upload_policy": "control/inventory/connectors/h9_media_metadata_live_probe_no_download_upload_policy.json",
    "restricted_source_policy": "control/inventory/connectors/h9_media_metadata_live_probe_restricted_source_policy.json",
}
SOURCE_CONFIGS = {'wikimedia_commons': {'label': 'Wikimedia Commons metadata', 'connector_family': 'open_media_catalog', 'source_record_kind': 'media_metadata', 'endpoint': 'media_metadata_lookup_future', 'request_key': 'example_media_metadata'}, 'openverse': {'label': 'Openverse metadata', 'connector_family': 'open_media_catalog', 'source_record_kind': 'media_metadata', 'endpoint': 'open_media_metadata_lookup_future', 'request_key': 'example_open_media_metadata'}, 'flickr_commons': {'label': 'Flickr Commons metadata', 'connector_family': 'image_collection_metadata', 'source_record_kind': 'image_collection_metadata', 'endpoint': 'image_collection_metadata_lookup_future', 'request_key': 'example_image_metadata'}, 'david_rumsey_maps': {'label': 'David Rumsey Map Collection metadata', 'connector_family': 'map_collection_metadata', 'source_record_kind': 'map_metadata', 'endpoint': 'map_metadata_lookup_future', 'request_key': 'example_map_metadata'}, 'nasa_image_video': {'label': 'NASA Image and Video Library metadata', 'connector_family': 'image_collection_metadata', 'source_record_kind': 'image_video_metadata', 'endpoint': 'media_metadata_lookup_future', 'request_key': 'example_media_metadata'}, 'met_museum_collection': {'label': 'Metropolitan Museum of Art collection metadata', 'connector_family': 'museum_collection_api', 'source_record_kind': 'museum_collection_metadata', 'endpoint': 'collection_object_metadata_lookup_future', 'request_key': 'example_collection_object_metadata'}, 'art_institute_chicago': {'label': 'Art Institute of Chicago collection metadata', 'connector_family': 'museum_collection_api', 'source_record_kind': 'museum_collection_metadata', 'endpoint': 'collection_object_metadata_lookup_future', 'request_key': 'example_collection_object_metadata'}, 'musicbrainz': {'label': 'MusicBrainz metadata', 'connector_family': 'music_metadata_api', 'source_record_kind': 'music_metadata', 'endpoint': 'artist_recording_release_metadata_lookup_future', 'request_key': 'example_recording_metadata'}, 'discogs': {'label': 'Discogs metadata', 'connector_family': 'music_metadata_api', 'source_record_kind': 'music_metadata', 'endpoint': 'release_artist_label_metadata_lookup_future', 'request_key': 'example_release_metadata'}, 'rate_your_music_policy_limited': {'label': 'Rate Your Music metadata, policy-limited', 'connector_family': 'html_catalog_policy_limited', 'source_record_kind': 'policy_limited_music_metadata', 'endpoint': 'metadata_manifest_only_future', 'request_key': 'example_manifest_metadata'}, 'acoustid_policy_limited': {'label': 'AcoustID fingerprint metadata, policy-limited', 'connector_family': 'fingerprint_metadata', 'source_record_kind': 'fingerprint_metadata', 'endpoint': 'fingerprint_metadata_lookup_future', 'request_key': 'example_fingerprint_metadata'}, 'imslp': {'label': 'IMSLP score metadata', 'connector_family': 'open_media_catalog', 'source_record_kind': 'score_metadata', 'endpoint': 'score_metadata_lookup_future', 'request_key': 'example_score_metadata'}, 'librivox': {'label': 'LibriVox audiobook metadata', 'connector_family': 'audio_archive_metadata', 'source_record_kind': 'audio_metadata', 'endpoint': 'audiobook_metadata_lookup_future', 'request_key': 'example_audio_metadata'}, 'freesound': {'label': 'Freesound metadata', 'connector_family': 'audio_archive_metadata', 'source_record_kind': 'sound_metadata', 'endpoint': 'sound_metadata_lookup_future', 'request_key': 'example_sound_metadata'}, 'great_78_project': {'label': 'Great 78 Project metadata', 'connector_family': 'audio_archive_metadata', 'source_record_kind': 'audio_archive_metadata', 'endpoint': 'audio_archive_metadata_lookup_future', 'request_key': 'example_audio_metadata'}, 'live_music_archive': {'label': 'Live Music Archive metadata', 'connector_family': 'audio_archive_metadata', 'source_record_kind': 'live_music_archive_metadata', 'endpoint': 'live_music_metadata_lookup_future', 'request_key': 'example_live_music_metadata'}, 'smithsonian_folkways': {'label': 'Smithsonian Folkways metadata', 'connector_family': 'audio_archive_metadata', 'source_record_kind': 'audio_collection_metadata', 'endpoint': 'audio_collection_metadata_lookup_future', 'request_key': 'example_audio_metadata'}, 'prelinger_archives': {'label': 'Prelinger Archives metadata', 'connector_family': 'video_archive_metadata', 'source_record_kind': 'video_archive_metadata', 'endpoint': 'video_archive_metadata_lookup_future', 'request_key': 'example_video_metadata'}, 'ubuweb_policy_limited': {'label': 'UbuWeb metadata, policy-limited', 'connector_family': 'html_catalog_policy_limited', 'source_record_kind': 'policy_limited_media_metadata', 'endpoint': 'metadata_manifest_only_future', 'request_key': 'example_manifest_metadata'}, 'vimeo_creative_commons_policy_limited': {'label': 'Vimeo Creative Commons metadata, policy-limited', 'connector_family': 'video_archive_metadata', 'source_record_kind': 'video_metadata', 'endpoint': 'cc_metadata_lookup_future', 'request_key': 'example_cc_video_metadata'}}
H9_SOURCE_IDS = tuple(SOURCE_CONFIGS)

REQUEST_FORBIDDEN_TRUE_KEYS = {
    "media_download_requested",
    "image_download_requested",
    "video_download_requested",
    "audio_download_requested",
    "map_download_requested",
    "score_download_requested",
    "thumbnail_fetch_requested",
    "media_upload_requested",
    "fingerprint_submission_requested",
    "fingerprint_generation_requested",
    "scraping_or_crawling_requested",
    "restricted_source_requested",
    "bypass_or_automation_requested",
}
FORBIDDEN_TRUTH_TRUE_KEYS = set(['accepted_candidate_truth', 'accepted_creator_collection_relation_truth', 'accepted_evidence_truth', 'accepted_fingerprint_identity_truth', 'accepted_image_video_map_truth', 'accepted_media_identity_truth', 'accepted_music_identity_truth', 'accepted_public_record', 'accepted_rights_license_truth', 'accepted_safety_privacy_truth', 'accepted_source_truth', 'content_safety_claimed', 'creative_commons_metadata_is_license_truth', 'creative_commons_truth_claimed', 'creator_collection_relation_candidate_is_truth', 'evidence_candidate_preview_is_accepted_evidence', 'evidence_preview_is_accepted_evidence', 'fingerprint_match_candidate_is_truth', 'image_video_map_identity_candidate_is_truth', 'license_metadata_is_rights_clearance', 'live_probe_result_is_public_truth', 'malware_safety_claimed', 'master_index_mutated', 'media_object_identity_candidate_is_truth', 'music_identity_candidate_is_truth', 'normalized_record_is_public_truth', 'privacy_safety_claimed', 'production_readiness_claimed', 'public_domain_metadata_is_public_domain_truth', 'public_domain_truth_claimed', 'public_index_mutated', 'review_seed_is_review_decision', 'rights_clearance_claimed', 'rights_license_candidate_is_rights_truth', 'safety_privacy_candidate_is_safety_truth', 'source_cache_candidate_is_accepted_source', 'source_cache_preview_is_accepted_source', 'verified_authenticity_claimed'])
FORBIDDEN_PRODUCT_TRUE_KEYS = set(['api_calls_made', 'audio_download_used', 'browser_automation_used', 'bypass_or_automation_used', 'catalog_fetch_used', 'changed_public_search_behavior', 'crawling_used', 'enabled_accounts', 'enabled_crawling', 'enabled_downloads', 'enabled_fingerprinting', 'enabled_hosting', 'enabled_source_sync', 'enabled_telemetry', 'enabled_uploads', 'fingerprint_generation_used', 'fingerprint_lookup_used', 'fingerprint_submission_used', 'image_download_used', 'map_download_used', 'media_download_used', 'media_upload_used', 'mutated_master_index', 'mutated_public_index', 'network_calls_made', 'restricted_source_access_used', 'score_download_used', 'scraping_used', 'thumbnail_fetch_used', 'video_download_used'])


def load_h9_media_metadata_live_probe_policy_bundle(root: str | Path | None = None) -> dict[str, Any]:
    base = Path(root) if root is not None else Path(__file__).resolve().parents[3]
    return {key: json.loads((base / rel).read_text(encoding="utf-8")) for key, rel in POLICY_PATHS.items()}


def build_h9_media_metadata_live_probe_request(source_id: str, request_key: str, policy_bundle: Mapping[str, Any], live_requested: bool = False) -> dict[str, Any]:
    if source_id not in SOURCE_CONFIGS:
        raise ValueError(f"unknown H9 source_id: {source_id}")
    cfg = SOURCE_CONFIGS[source_id]
    request = {
        "schema_version": "h9_media_metadata_live_probe_request.v0",
        "live_probe_request_id": f"h9.live_probe_request.{source_id}.{_slug(request_key)}.v0",
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "source_record_kind": cfg["source_record_kind"],
        "operation_scope": "metadata_only",
        "endpoint_or_metadata_class": cfg["endpoint"],
        "request_shape": {"request_key": request_key, "identifier_shape": "single_committed_metadata_identifier_future", "arbitrary_url_allowed": False},
        "approved_request_key": request_key,
        "media_or_catalog_identifier": f"metadata-only-candidate:{source_id}:{request_key}",
        "music_or_recording_context": "candidate_metadata_context_only",
        "image_video_map_context": "candidate_metadata_context_only",
        "collection_or_creator_context": cfg["label"],
        "fingerprint_context": "candidate_metadata_context_only_no_upload_no_generation",
        "approval_refs": [POLICY_PATHS["allowed_requests"]],
        "policy_refs": list(POLICY_PATHS.values()),
        "live_requested": bool(live_requested),
        "dry_run_only": not bool(live_requested),
        "api_query_requested": False,
        "catalog_fetch_requested": False,
        "media_download_requested": False,
        "image_download_requested": False,
        "video_download_requested": False,
        "audio_download_requested": False,
        "map_download_requested": False,
        "score_download_requested": False,
        "thumbnail_fetch_requested": False,
        "media_upload_requested": False,
        "fingerprint_lookup_requested": False,
        "fingerprint_submission_requested": False,
        "fingerprint_generation_requested": False,
        "scraping_or_crawling_requested": False,
        "restricted_source_requested": False,
        "bypass_or_automation_requested": False,
        "output_policy_ref": POLICY_PATHS["output_policy"],
        "review_policy_ref": POLICY_PATHS["review_policy"],
        "truth_policy_ref": POLICY_PATHS["truth_policy"],
        "limitations": ["Request envelope is fail-closed unless committed source policy approves the exact metadata-only request."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H9-BUNDLE-03 examples are dry preflight by default and do not call networks."],
    }
    _raise_on_boundary_errors(request, policy_bundle)
    return request


def validate_h9_media_metadata_live_probe_request(request: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    source_id = str(request.get("source_id") or "")
    request_key = str(request.get("approved_request_key") or "")
    if source_id not in SOURCE_CONFIGS:
        reasons.append(f"{source_id or 'missing_source'} is not a known H9 media metadata source")
    else:
        cfg = SOURCE_CONFIGS[source_id]
        if request.get("operation_scope") != "metadata_only":
            reasons.append("approved_operation_scope must be metadata_only")
        endpoint = str(request.get("endpoint_or_metadata_class") or "")
        if endpoint != cfg["endpoint"]:
            reasons.append("endpoint_or_metadata_class download/fetch class is forbidden or does not match source policy plan")
    if request.get("api_query_requested") is True:
        reasons.append("api_query_requested is not approved without exact committed bounded metadata policy")
    if request.get("catalog_fetch_requested") is True:
        reasons.append("catalog_fetch_requested is not approved without exact committed bounded metadata policy")
    if request.get("fingerprint_lookup_requested") is True:
        reasons.append("fingerprint_lookup_requested is not approved without exact committed bounded metadata policy")
    for key in sorted(REQUEST_FORBIDDEN_TRUE_KEYS):
        if request.get(key) is True:
            reasons.append(f"{key} is forbidden for H9-BUNDLE-03 live probes")
    if source_id in SOURCE_CONFIGS:
        reasons.extend(validate_h9_source_approval(source_id, request_key, policy_bundle)["blocked_reasons"])
    reasons = _dedupe(reasons)
    return {"approved": not reasons, "result_status": _status_for_reasons(reasons), "blocked_reasons": reasons}


def validate_h9_source_approval(source_id: str, request_key: str, policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    if source_id not in SOURCE_CONFIGS:
        return {"approved": False, "result_status": "blocked_by_policy", "blocked_reasons": [f"{source_id} is not a known H9 source"]}
    cfg = SOURCE_CONFIGS[source_id]
    allowed = _source_policy(source_id, policy_bundle, "allowed_requests")
    if not allowed:
        reasons.append("source is not listed in H9 allowed request policy")
    else:
        if allowed.get("approval_status") != "approved_for_bounded_metadata_probe":
            reasons.append("source approval_status is not approved_for_bounded_metadata_probe")
        if allowed.get("live_access_approved") is not True:
            reasons.append("live_access_approved is missing or false")
        if allowed.get("metadata_probe_approved") is not True:
            reasons.append("metadata_probe_approved is missing or false")
        if allowed.get("approved_operation_scope") != "metadata_only":
            reasons.append("approved_operation_scope is not metadata_only")
        if allowed.get("approved_source_id") != source_id:
            reasons.append("approved_source_id does not match requested source")
        if request_key not in (allowed.get("allowed_request_keys") or []):
            reasons.append("request key is not approved for this source")
        for key in ("source_sync_approved", "media_download_approved", "image_download_approved", "video_download_approved", "audio_download_approved", "map_download_approved", "score_download_approved", "thumbnail_fetch_approved", "media_upload_approved", "fingerprint_submission_approved", "fingerprint_generation_approved", "user_media_upload_approved", "scraping_approved", "crawling_approved", "browser_automation_approved", "restricted_rights_sensitive_source_approved", "bypass_or_access_control_automation_approved", "public_query_fanout_approved"):
            if allowed.get(key) is not False:
                reasons.append(f"{key} must remain false")
    endpoint = _source_policy(source_id, policy_bundle, "endpoint_policy")
    if cfg["endpoint"] not in (endpoint.get("allowlisted_endpoint_or_metadata_classes_current") or []):
        reasons.append("endpoint/metadata class is not allowlisted for current live access")
    rate = _source_policy(source_id, policy_bundle, "rate_limit_policy")
    if rate.get("decision_status") != "approved_for_bounded_metadata_probe":
        reasons.append("rate limit policy is not approved")
    if int(rate.get("max_requests_per_run") or 0) < 1:
        reasons.append("request budget is zero or missing")
    if int(rate.get("timeout_seconds") or 0) <= 0:
        reasons.append("timeout_seconds is missing")
    if not isinstance(rate.get("retry_policy"), Mapping):
        reasons.append("retry policy is missing")
    if not str(rate.get("user_agent_contact_posture") or "").startswith("approved"):
        reasons.append("User-Agent/contact posture is not approved")
    if not str(rate.get("auth_posture") or "").startswith("approved"):
        reasons.append("auth/no-auth posture is not approved")
    cache = _source_policy(source_id, policy_bundle, "cache_policy")
    if cache.get("decision_status") != "approved_for_bounded_metadata_probe" and cache.get("no_cache_decision") != "approved":
        reasons.append("cache TTL/no-cache decision is not approved")
    kill = _source_policy(source_id, policy_bundle, "kill_switch_policy")
    if kill.get("default_enabled") is not True or kill.get("live_probe_kill_switch_engaged") is not False:
        reasons.append("kill switch defaults fail-closed or is engaged")
    reasons = _dedupe(reasons)
    return {"approved": not reasons, "result_status": _status_for_reasons(reasons), "blocked_reasons": reasons}


def build_h9_media_metadata_live_probe_blocked_result(request: Mapping[str, Any], reason: str | list[str], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    source_id = str(request.get("source_id") or "unknown")
    cfg = SOURCE_CONFIGS.get(source_id, {"connector_family": request.get("connector_family", "unknown"), "source_record_kind": request.get("source_record_kind", "unknown"), "endpoint": request.get("endpoint_or_metadata_class", "unknown")})
    reasons = reason if isinstance(reason, list) else [str(reason)]
    status = _status_for_reasons(reasons)
    result: dict[str, Any] = {
        "schema_version": "h9_media_metadata_live_probe_result.v0",
        "live_probe_result_id": f"h9.live_probe_result.{source_id}.blocked.{_short_fingerprint(request)}.v0",
        "live_probe_request_ref": request.get("live_probe_request_id"),
        "source_id": source_id,
        "connector_family": cfg.get("connector_family"),
        "source_record_kind": cfg.get("source_record_kind"),
        "result_status": status,
        "request_count": 0,
        "network_used": False,
        "endpoint_or_metadata_used": request.get("endpoint_or_metadata_class") or cfg.get("endpoint"),
        "response_status_code": None,
        "response_fingerprint": None,
        "response_summary": "blocked before network; no source call performed",
        "normalized_record": _blocked_candidate(),
        "media_object_identity_candidate": _blocked_candidate(),
        "music_work_recording_release_candidate": _blocked_candidate(),
        "image_video_map_identity_candidate": _blocked_candidate(),
        "media_creator_collection_relation_candidate": _blocked_candidate(),
        "media_fingerprint_candidate": _blocked_candidate(),
        "media_rights_license_candidate": _blocked_candidate(),
        "media_safety_privacy_candidate": _blocked_candidate(),
        "source_cache_candidate_preview": _blocked_candidate(),
        "evidence_candidate_preview": _blocked_candidate(),
        "review_queue_seed_preview": _blocked_review_seed(source_id, status, reasons),
        "blocked_reason": reasons[0] if reasons else None,
        "blocked_reasons": reasons,
        "warnings": [],
        "limitations": ["Blocked result: no network call, no media download/upload, no fingerprint submission/generation, no scrape/crawl, no restricted-source access, and no truth acceptance."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H9 live probe failed closed."],
    }
    result["connector_health_summary"] = build_h9_connector_health_summary(result, policy_bundle)
    _raise_on_boundary_errors(result, policy_bundle)
    return result


def build_h9_media_metadata_live_probe_result(source_id: str, response_payload: Mapping[str, Any], response_metadata: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    if source_id not in SOURCE_CONFIGS:
        raise ValueError(f"unknown H9 source_id: {source_id}")
    cfg = SOURCE_CONFIGS[source_id]
    payload = _metadata_payload_defaults(source_id, response_payload)
    fixture = _fixture_from_payload(source_id, payload)
    normalized = normalize_h9_media_metadata_fixture(fixture, source_id)
    network_used = bool(response_metadata.get("network_used"))
    result: dict[str, Any] = {
        "schema_version": "h9_media_metadata_live_probe_result.v0",
        "live_probe_result_id": f"h9.live_probe_result.{source_id}.{_short_fingerprint(payload)}.v0",
        "live_probe_request_ref": response_metadata.get("live_probe_request_ref"),
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "source_record_kind": cfg["source_record_kind"],
        "result_status": "live_probe_completed" if network_used else "dry_run_preflight_pass",
        "request_count": int(response_metadata.get("request_count") or (1 if network_used else 0)),
        "network_used": network_used,
        "endpoint_or_metadata_used": cfg["endpoint"],
        "response_status_code": response_metadata.get("response_status_code") if network_used else "not_called_dry_run",
        "response_fingerprint": _fingerprint(payload),
        "response_summary": "bounded metadata response normalized as candidate-only preview" if network_used else "fixture-equivalent metadata preview normalized without network",
        "normalized_record": normalized,
        "media_object_identity_candidate": _fixture_media_candidate(normalized),
        "music_work_recording_release_candidate": _fixture_music_candidate(normalized),
        "image_video_map_identity_candidate": _fixture_visual_candidate(normalized),
        "media_creator_collection_relation_candidate": _fixture_relation_candidates(normalized),
        "media_fingerprint_candidate": _fixture_fingerprint_candidate(normalized),
        "media_rights_license_candidate": _fixture_rights_candidate(normalized),
        "media_safety_privacy_candidate": _fixture_safety_candidate(normalized),
        "source_cache_candidate_preview": _fixture_source_cache_preview(normalized),
        "evidence_candidate_preview": _fixture_evidence_preview(normalized),
        "blocked_reason": None,
        "blocked_reasons": [],
        "warnings": list(response_metadata.get("warnings") or []),
        "limitations": ["Live-probe result is candidate-only metadata; it does not accept truth or authorize downloads/uploads/fingerprinting/actions."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Output bundle remains preview-only until separate review accepts it."],
    }
    result["review_queue_seed_preview"] = build_h9_review_queue_seed_preview_from_probe(result, result["source_cache_candidate_preview"], result["evidence_candidate_preview"], policy_bundle)
    result["connector_health_summary"] = build_h9_connector_health_summary(result, policy_bundle)
    _raise_on_boundary_errors(result, policy_bundle)
    return result


def normalize_h9_media_metadata_live_probe_result(result: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    normalized = result.get("normalized_record")
    if not isinstance(normalized, Mapping):
        raise ValueError("live probe result does not contain a normalized record")
    return dict(normalized)


def build_h9_media_object_identity_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_media_candidate(normalized_record)


def build_h9_music_work_recording_release_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_music_candidate(normalized_record)


def build_h9_image_video_map_identity_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_visual_candidate(normalized_record)


def build_h9_media_creator_collection_relation_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    return _fixture_relation_candidates(normalized_record)


def build_h9_media_fingerprint_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_fingerprint_candidate(normalized_record)


def build_h9_media_rights_license_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_rights_candidate(normalized_record)


def build_h9_media_safety_privacy_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_safety_candidate(normalized_record)


def build_h9_source_cache_candidate_preview_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_source_cache_preview(normalized_record)


def build_h9_evidence_candidate_preview_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_evidence_preview(normalized_record)


def build_h9_review_queue_seed_preview_from_probe(result: Mapping[str, Any], source_cache_preview: Mapping[str, Any], evidence_preview: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    source_id = str(result.get("source_id") or "unknown")
    seed = {
        "schema_version": "h9_media_metadata_live_probe_review_seed.v0",
        "review_queue_seed_preview_id": f"h9.review_seed_preview.{source_id}.{_short_fingerprint(result)}.v0",
        "source_id": source_id,
        "live_probe_result_ref": result.get("live_probe_result_id"),
        "source_cache_candidate_preview_ref": source_cache_preview.get("source_cache_candidate_preview_id") if isinstance(source_cache_preview, Mapping) else None,
        "evidence_candidate_preview_ref": evidence_preview.get("evidence_candidate_preview_id") if isinstance(evidence_preview, Mapping) else None,
        "preview_only": True,
        "review_seed_is_review_decision": False,
        "review_queue_write_allowed_current": False,
        "required_review": "human_or_future_policy_review_required_before_any_acceptance",
        "limitations": ["Review queue seed preview only; no review queue mutation or review decision."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(seed, policy_bundle)
    return seed


def build_h9_connector_health_summary(result: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    source_id = str(result.get("source_id") or "unknown")
    cfg = SOURCE_CONFIGS.get(source_id, {})
    health = {
        "schema_version": "h9_media_metadata_connector_health_summary.v0",
        "health_summary_id": f"h9.connector_health.{source_id}.{_short_fingerprint(result)}.v0",
        "source_id": source_id,
        "connector_family": str(cfg.get("connector_family") or result.get("connector_family") or "unknown"),
        "live_probe_status": str(result.get("result_status") or "not_evaluable"),
        "request_count": int(result.get("request_count") or 0),
        "response_status_summary": "blocked_before_network" if result.get("network_used") is not True else str(result.get("response_status_code") or "metadata_response_observed"),
        "policy_blockers": list(result.get("blocked_reasons") or []),
        "warnings": list(result.get("warnings") or []),
        "source_limitations": list(result.get("limitations") or []),
        "restricted_source_status": "blocked_current",
        "next_recommended_action": "review_fixture_equivalent_outputs_or_commit_operator_approval_before_live_probe",
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(health, policy_bundle)
    return health


def build_h9_media_metadata_live_probe_output_bundle(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "h9_media_metadata_live_probe_output_bundle.v0",
        "live_probe_result": dict(result),
        "normalized_record": result.get("normalized_record", {}),
        "media_object_identity_candidate": result.get("media_object_identity_candidate", {}),
        "music_work_recording_release_candidate": result.get("music_work_recording_release_candidate", {}),
        "image_video_map_identity_candidate": result.get("image_video_map_identity_candidate", {}),
        "media_creator_collection_relation_candidate": result.get("media_creator_collection_relation_candidate", []),
        "media_fingerprint_candidate": result.get("media_fingerprint_candidate", {}),
        "media_rights_license_candidate": result.get("media_rights_license_candidate", {}),
        "media_safety_privacy_candidate": result.get("media_safety_privacy_candidate", {}),
        "source_cache_candidate_preview": result.get("source_cache_candidate_preview", {}),
        "evidence_candidate_preview": result.get("evidence_candidate_preview", {}),
        "review_queue_seed_preview": result.get("review_queue_seed_preview", {}),
        "connector_health_summary": result.get("connector_health_summary", {}),
        "validation_summary": {
            "truth_boundary_violations": detect_h9_media_metadata_live_probe_truth_boundary_violations(result, {}),
            "product_boundary_violations": detect_h9_media_metadata_live_probe_product_boundary_violations(result, {}),
        },
    }


def summarize_h9_media_metadata_live_probe_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "h9_media_metadata_live_probe_summary.v0",
        "source_id": result.get("source_id"),
        "result_status": result.get("result_status"),
        "request_count": int(result.get("request_count") or 0),
        "network_used": bool(result.get("network_used")),
        "blocked_reasons": list(result.get("blocked_reasons") or []),
        "media_object_candidate_present": _present(result.get("media_object_identity_candidate")),
        "music_work_recording_release_candidate_present": _present(result.get("music_work_recording_release_candidate")),
        "image_video_map_candidate_present": _present(result.get("image_video_map_identity_candidate")),
        "creator_collection_relation_candidate_present": bool(result.get("media_creator_collection_relation_candidate")) and not _blocked(result.get("media_creator_collection_relation_candidate")),
        "fingerprint_candidate_present": _present(result.get("media_fingerprint_candidate")),
        "rights_license_candidate_present": _present(result.get("media_rights_license_candidate")),
        "safety_privacy_candidate_present": _present(result.get("media_safety_privacy_candidate")),
        "source_cache_preview_present": _present(result.get("source_cache_candidate_preview")),
        "evidence_preview_present": _present(result.get("evidence_candidate_preview")),
        "review_seed_present": _present(result.get("review_queue_seed_preview")),
        "connector_health_present": _present(result.get("connector_health_summary")),
    }


def detect_h9_media_metadata_live_probe_truth_boundary_violations(result: Mapping[str, Any], policy_bundle: Mapping[str, Any] | None = None) -> list[str]:
    return _fixture_truth_violations(result) + _detect_true_keys(result, FORBIDDEN_TRUTH_TRUE_KEYS, "truth")


def detect_h9_media_metadata_live_probe_product_boundary_violations(result: Mapping[str, Any], policy_bundle: Mapping[str, Any] | None = None) -> list[str]:
    return _fixture_product_violations(result) + _detect_true_keys(result, FORBIDDEN_PRODUCT_TRUE_KEYS, "product")


def _metadata_payload_defaults(source_id: str, response_payload: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(response_payload)
    cfg = SOURCE_CONFIGS[source_id]
    payload.setdefault("source_record_kind", cfg["source_record_kind"])
    payload.setdefault("source_native_id", f"{source_id}-metadata-candidate")
    payload.setdefault("media_title", f"Synthetic {cfg['label']} record")
    payload.setdefault("alternate_title", [f"{cfg['label']} metadata preview"])
    payload.setdefault("media_type", "metadata_record")
    payload.setdefault("media_format", "metadata_only")
    payload.setdefault("collection_id", f"collection:{source_id}")
    payload.setdefault("catalog_record_id", f"catalog:{source_id}:probe")
    payload.setdefault("creator_or_contributor", [cfg["label"]])
    payload.setdefault("publisher_or_collection", cfg["label"])
    payload.setdefault("creation_date_candidate", "2026-05-11")
    payload.setdefault("publication_date_candidate", "2026-05-11")
    payload.setdefault("language_or_locale", "en")
    payload.setdefault("subject_or_tag", ["metadata-only", "candidate"])
    payload.setdefault("duration_or_dimensions_candidate", "unknown")
    payload.setdefault("file_metadata_candidate", {"file_payload_present": False, "metadata_only": True})
    payload.setdefault("checksum_metadata_candidate", "unknown-not-authenticity-proof")
    payload.setdefault("source_locator_candidate", f"metadata-only-candidate:{source_id}")
    payload.setdefault("thumbnail_or_preview_ref", "not_fetched")
    payload.setdefault("metadata_license_candidate", "candidate_only_not_rights_clearance")
    payload.setdefault("artist_or_creator", [cfg["label"]])
    payload.setdefault("work_title", f"{cfg['label']} work metadata candidate")
    payload.setdefault("recording_title", f"{cfg['label']} recording metadata candidate")
    payload.setdefault("release_title", f"{cfg['label']} release metadata candidate")
    payload.setdefault("release_group_candidate", "candidate")
    payload.setdefault("label_or_publisher", cfg["label"])
    payload.setdefault("catalog_number", f"H9-{source_id.upper().replace('_', '-')}-META")
    payload.setdefault("isrc_candidate", "unknown")
    payload.setdefault("iswc_candidate", "unknown")
    payload.setdefault("musicbrainz_id_candidate", f"mbid-candidate-{source_id}" if cfg["connector_family"] == "music_metadata_api" else "unknown")
    payload.setdefault("discogs_id_candidate", f"discogs-candidate-{source_id}" if source_id == "discogs" else "unknown")
    payload.setdefault("acoustid_candidate", f"acoustid-candidate-{source_id}" if source_id == "acoustid_policy_limited" else "unknown")
    payload.setdefault("track_number_candidate", "unknown")
    payload.setdefault("medium_format_candidate", "metadata_only")
    payload.setdefault("country_or_region_candidate", "unknown")
    payload.setdefault("visual_title", f"{cfg['label']} visual metadata candidate")
    payload.setdefault("object_record_id", f"object:{source_id}:candidate")
    payload.setdefault("image_or_video_id", f"visual:{source_id}:candidate")
    payload.setdefault("map_id", f"map:{source_id}:candidate" if source_id == "david_rumsey_maps" else "unknown")
    payload.setdefault("place_or_geospatial_ref", "candidate_only_not_geospatial_truth")
    payload.setdefault("medium_or_material", "metadata_only")
    payload.setdefault("rights_or_license_metadata", {"rights_statement_candidate": "candidate only", "rights_clearance_claimed": False})
    payload.setdefault("fingerprint_metadata", {"fingerprint_id_candidate": "candidate only", "upload_allowed_current": False, "fingerprint_generation_allowed_current": False})
    payload.setdefault("safety_privacy_metadata", {"content_safety_metadata_candidate": "candidate only", "safety_truth_claimed": False})
    payload.setdefault("source_metadata", {"source_label": cfg["label"], "metadata_only_probe_preview": True})
    payload.setdefault("metadata_summary", f"Metadata-only observation candidate for {cfg['label']}.")
    return payload


def _fixture_from_payload(source_id: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    cfg = SOURCE_CONFIGS[source_id]
    return {
        "schema_version": "h9_media_metadata_fixture.v0",
        "fixture_id": f"h9.live_probe_fixture_equivalent.{source_id}.{_slug(str(payload.get('source_native_id') or 'metadata'))}.v0",
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "fixture_kind": "live_probe_metadata_response_preview",
        "fixture_status": "ready",
        "fixture_public_safe": True,
        "live_call_used": False,
        "network_used": False,
        "external_api_used": False,
        "catalog_payload_included": False,
        "media_payload_included": False,
        "image_payload_included": False,
        "video_payload_included": False,
        "audio_payload_included": False,
        "map_payload_included": False,
        "score_payload_included": False,
        "thumbnail_payload_included": False,
        "waveform_payload_included": False,
        "fingerprint_payload_included": False,
        "user_media_payload_included": False,
        "media_upload_performed": False,
        "fingerprint_submission_performed": False,
        "fingerprint_generation_performed": False,
        "scraping_output_included": False,
        "crawling_output_included": False,
        "restricted_source_accessed": False,
        "bypass_or_automation_used": False,
        "fixture_payload": dict(payload),
        "expected_normalized_ref": f"h9.normalized.{source_id}.candidate.v0",
        "limitations": ["Fixture-equivalent live-probe preview; no network or media payload included."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Built from mocked or dry-run metadata response only."],
    }


def _source_policy(source_id: str, policy_bundle: Mapping[str, Any], bundle_key: str) -> dict[str, Any]:
    for item in policy_bundle.get(bundle_key, {}).get("sources", []):
        if isinstance(item, Mapping) and item.get("source_id") == source_id:
            return dict(item)
    return {}


def _status_for_reasons(reasons: list[str]) -> str:
    joined = " ".join(reasons).lower()
    if not reasons:
        return "dry_run_preflight_pass"
    if "kill switch" in joined:
        return "blocked_by_kill_switch"
    if "download" in joined or "thumbnail" in joined:
        return "blocked_by_download_policy"
    if "upload" in joined:
        return "blocked_by_upload_policy"
    if "fingerprint" in joined:
        return "blocked_by_fingerprint_policy"
    if "endpoint" in joined:
        return "blocked_by_endpoint_policy"
    if "restricted" in joined:
        return "blocked_by_restricted_source_policy"
    if "bypass" in joined or "automation" in joined:
        return "blocked_by_bypass_policy"
    if "approval" in joined or "approved" in joined or "request key" in joined:
        return "blocked_by_missing_approval"
    return "blocked_by_policy"


def _blocked_candidate() -> dict[str, Any]:
    return {
        "schema_version": "h9_media_metadata_blocked_candidate.v0",
        "status": "not_created_blocked_by_policy",
        "preview_only": True,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }


def _blocked_review_seed(source_id: str, status: str, reasons: list[str]) -> dict[str, Any]:
    return {
        "schema_version": "h9_media_metadata_live_probe_review_seed.v0",
        "review_queue_seed_preview_id": f"h9.review_seed_preview.{source_id}.blocked.{_short_fingerprint(reasons)}.v0",
        "source_id": source_id,
        "preview_only": True,
        "review_seed_is_review_decision": False,
        "review_queue_write_allowed_current": False,
        "blocked_status": status,
        "blocked_reasons": reasons,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }


def _present(value: object) -> bool:
    return isinstance(value, Mapping) and value.get("status") != "not_created_blocked_by_policy"


def _blocked(value: object) -> bool:
    return isinstance(value, Mapping) and value.get("status") == "not_created_blocked_by_policy"


def _truth_boundary() -> dict[str, bool]:
    return {'live_probe_result_is_public_truth': False, 'normalized_record_is_public_truth': False, 'media_object_identity_candidate_is_truth': False, 'music_identity_candidate_is_truth': False, 'image_video_map_identity_candidate_is_truth': False, 'creator_collection_relation_candidate_is_truth': False, 'fingerprint_match_candidate_is_truth': False, 'rights_license_candidate_is_rights_truth': False, 'safety_privacy_candidate_is_safety_truth': False, 'license_metadata_is_rights_clearance': False, 'public_domain_metadata_is_public_domain_truth': False, 'creative_commons_metadata_is_license_truth': False, 'source_cache_candidate_is_accepted_source': False, 'source_cache_preview_is_accepted_source': False, 'evidence_candidate_preview_is_accepted_evidence': False, 'evidence_preview_is_accepted_evidence': False, 'review_seed_is_review_decision': False, 'accepted_source_truth': False, 'accepted_evidence_truth': False, 'accepted_candidate_truth': False, 'accepted_media_identity_truth': False, 'accepted_music_identity_truth': False, 'accepted_image_video_map_truth': False, 'accepted_creator_collection_relation_truth': False, 'accepted_fingerprint_identity_truth': False, 'accepted_rights_license_truth': False, 'accepted_safety_privacy_truth': False, 'accepted_public_record': False, 'public_index_mutated': False, 'master_index_mutated': False, 'rights_clearance_claimed': False, 'public_domain_truth_claimed': False, 'creative_commons_truth_claimed': False, 'content_safety_claimed': False, 'privacy_safety_claimed': False, 'malware_safety_claimed': False, 'verified_authenticity_claimed': False, 'production_readiness_claimed': False}.copy()


def _product_boundary() -> dict[str, bool]:
    return {'changed_public_search_behavior': False, 'enabled_hosting': False, 'enabled_source_sync': False, 'enabled_downloads': False, 'enabled_uploads': False, 'enabled_fingerprinting': False, 'enabled_crawling': False, 'enabled_accounts': False, 'enabled_telemetry': False, 'mutated_public_index': False, 'mutated_master_index': False, 'network_calls_made': False, 'api_calls_made': False, 'catalog_fetch_used': False, 'media_download_used': False, 'image_download_used': False, 'video_download_used': False, 'audio_download_used': False, 'map_download_used': False, 'score_download_used': False, 'thumbnail_fetch_used': False, 'media_upload_used': False, 'fingerprint_lookup_used': False, 'fingerprint_submission_used': False, 'fingerprint_generation_used': False, 'scraping_used': False, 'crawling_used': False, 'browser_automation_used': False, 'restricted_source_access_used': False, 'bypass_or_automation_used': False}.copy()


def _detect_true_keys(value: Any, forbidden: set[str], prefix: str = "") -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{prefix}.{key}" if prefix else str(key)
            if key in forbidden and child is True:
                errors.append(f"forbidden true boundary key: {child_path}")
            errors.extend(_detect_true_keys(child, forbidden, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_detect_true_keys(child, forbidden, f"{prefix}[{index}]"))
    return errors


def _raise_on_boundary_errors(record: Mapping[str, Any], policy_bundle: Mapping[str, Any] | None = None) -> None:
    errors = detect_h9_media_metadata_live_probe_truth_boundary_violations(record, policy_bundle) + detect_h9_media_metadata_live_probe_product_boundary_violations(record, policy_bundle)
    if errors:
        raise ValueError("; ".join(errors))


def _fingerprint(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def _short_fingerprint(payload: object) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:16]


def _slug(value: object) -> str:
    text = str(value or "unknown")
    safe = "".join(ch.lower() if ch.isalnum() else "-" for ch in text).strip("-")
    return safe[:64].strip("-") or "unknown"


def _dedupe(values: list[object]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value).strip()
        if text and text not in seen:
            result.append(text)
            seen.add(text)
    return result

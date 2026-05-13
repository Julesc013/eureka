"""Fixture-only H9 media metadata normalization helpers."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from typing import Any

H9_SOURCE_CONFIGS: dict[str, dict[str, str]] = {'wikimedia_commons': {'label': 'Wikimedia Commons metadata', 'connector_family': 'open_media_catalog'}, 'openverse': {'label': 'Openverse metadata', 'connector_family': 'open_media_catalog'}, 'flickr_commons': {'label': 'Flickr Commons metadata', 'connector_family': 'image_collection_metadata'}, 'david_rumsey_maps': {'label': 'David Rumsey Map Collection metadata', 'connector_family': 'map_collection_metadata'}, 'nasa_image_video': {'label': 'NASA Image and Video Library metadata', 'connector_family': 'image_collection_metadata'}, 'met_museum_collection': {'label': 'Metropolitan Museum of Art collection metadata', 'connector_family': 'museum_collection_api'}, 'art_institute_chicago': {'label': 'Art Institute of Chicago collection metadata', 'connector_family': 'museum_collection_api'}, 'musicbrainz': {'label': 'MusicBrainz metadata', 'connector_family': 'music_metadata_api'}, 'discogs': {'label': 'Discogs metadata', 'connector_family': 'music_metadata_api'}, 'rate_your_music_policy_limited': {'label': 'Rate Your Music metadata, policy-limited', 'connector_family': 'html_catalog_policy_limited'}, 'acoustid_policy_limited': {'label': 'AcoustID fingerprint metadata, policy-limited', 'connector_family': 'fingerprint_metadata'}, 'imslp': {'label': 'IMSLP score metadata', 'connector_family': 'open_media_catalog'}, 'librivox': {'label': 'LibriVox audiobook metadata', 'connector_family': 'audio_archive_metadata'}, 'freesound': {'label': 'Freesound metadata', 'connector_family': 'audio_archive_metadata'}, 'great_78_project': {'label': 'Great 78 Project metadata', 'connector_family': 'audio_archive_metadata'}, 'live_music_archive': {'label': 'Live Music Archive metadata', 'connector_family': 'audio_archive_metadata'}, 'smithsonian_folkways': {'label': 'Smithsonian Folkways metadata', 'connector_family': 'audio_archive_metadata'}, 'prelinger_archives': {'label': 'Prelinger Archives metadata', 'connector_family': 'video_archive_metadata'}, 'ubuweb_policy_limited': {'label': 'UbuWeb metadata, policy-limited', 'connector_family': 'html_catalog_policy_limited'}, 'vimeo_creative_commons_policy_limited': {'label': 'Vimeo Creative Commons metadata, policy-limited', 'connector_family': 'video_archive_metadata'}}
H9_SOURCE_IDS = tuple(H9_SOURCE_CONFIGS)
H9_FIXTURE_KINDS = ('minimal', 'media_identity', 'music_identity', 'image_video_map', 'creator_collection_relation', 'fingerprint_metadata', 'rights_license', 'safety_privacy', 'policy_blocked')

FIXTURE_FORBIDDEN_TRUE_KEYS = {
    "live_call_used",
    "network_used",
    "external_api_used",
    "catalog_payload_included",
    "media_payload_included",
    "image_payload_included",
    "video_payload_included",
    "audio_payload_included",
    "map_payload_included",
    "score_payload_included",
    "thumbnail_payload_included",
    "waveform_payload_included",
    "fingerprint_payload_included",
    "user_media_payload_included",
    "media_upload_performed",
    "fingerprint_submission_performed",
    "fingerprint_generation_performed",
    "scraping_output_included",
    "crawling_output_included",
    "restricted_source_accessed",
    "bypass_or_automation_used",
}

FORBIDDEN_TRUTH_TRUE_KEYS = set(('normalized_record_is_public_truth', 'media_object_identity_candidate_is_truth', 'music_identity_candidate_is_truth', 'image_video_map_identity_candidate_is_truth', 'creator_collection_relation_candidate_is_truth', 'fingerprint_match_candidate_is_truth', 'rights_license_candidate_is_rights_truth', 'safety_privacy_candidate_is_safety_truth', 'license_metadata_is_rights_clearance', 'public_domain_metadata_is_public_domain_truth', 'creative_commons_metadata_is_license_truth', 'media_metadata_grants_download_permission', 'fingerprint_candidate_grants_upload_or_submission_permission', 'source_cache_preview_is_accepted_source', 'evidence_preview_is_accepted_evidence', 'accepted_source_truth', 'accepted_evidence_truth', 'accepted_candidate_truth', 'accepted_media_identity_truth', 'accepted_music_identity_truth', 'accepted_image_video_map_truth', 'accepted_creator_collection_relation_truth', 'accepted_fingerprint_identity_truth', 'accepted_rights_license_truth', 'accepted_safety_privacy_truth', 'accepted_public_record', 'public_index_mutated', 'master_index_mutated', 'rights_clearance_claimed', 'public_domain_truth_claimed', 'creative_commons_truth_claimed', 'content_safety_claimed', 'privacy_safety_claimed', 'malware_safety_claimed', 'verified_authenticity_claimed', 'production_readiness_claimed'))
FORBIDDEN_PRODUCT_TRUE_KEYS = set(('changed_public_search_behavior', 'enabled_hosting', 'enabled_live_probes', 'enabled_source_sync', 'enabled_downloads', 'enabled_uploads', 'enabled_fingerprinting', 'enabled_crawling', 'enabled_accounts', 'enabled_telemetry', 'mutated_public_index', 'mutated_master_index', 'network_calls_made', 'api_calls_made', 'catalog_fetch_used', 'media_download_used', 'image_download_used', 'video_download_used', 'audio_download_used', 'map_download_used', 'score_download_used', 'thumbnail_fetch_used', 'media_upload_used', 'fingerprint_submission_used', 'fingerprint_generation_used', 'scraping_used', 'crawling_used', 'restricted_source_access_used', 'bypass_or_automation_used'))


def normalize_h9_media_metadata_fixture(raw_fixture: Mapping[str, Any], source_id: str, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if source_id not in H9_SOURCE_CONFIGS:
        raise ValueError(f"unknown H9 source_id: {source_id}")
    if raw_fixture.get("source_id") != source_id:
        raise ValueError(f"fixture source_id does not match requested source_id: {source_id}")
    _require_fixture_boundaries(raw_fixture)
    payload = _mapping(raw_fixture.get("fixture_payload"), "fixture_payload")
    config = H9_SOURCE_CONFIGS[source_id]
    native_id = _text(payload.get("source_native_id")) or _text(payload.get("catalog_record_id")) or _text(raw_fixture.get("fixture_id")) or f"fixture-{source_id}"
    limitations = list(raw_fixture.get("limitations") or [])
    limitations.extend(_missing_optional_limitations(payload))
    if raw_fixture.get("fixture_status") == "policy_blocked":
        limitations.append("fixture is policy-blocked and remains candidate-only")
    record: dict[str, Any] = {
        "schema_version": "h9_media_metadata_normalized_record.v0",
        "normalized_record_id": f"h9.normalized.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "connector_family": str(raw_fixture.get("connector_family") or config["connector_family"]),
        "source_record_kind": _text(payload.get("source_record_kind")) or _text(raw_fixture.get("fixture_kind")) or "unknown",
        "media_title": _text(payload.get("media_title")) or "unknown",
        "alternate_title": _list(payload.get("alternate_title")),
        "media_type": _text(payload.get("media_type")) or "unknown",
        "media_format": _text(payload.get("media_format")) or "unknown",
        "source_native_id": native_id,
        "collection_id": _text(payload.get("collection_id")) or "unknown",
        "catalog_record_id": _text(payload.get("catalog_record_id")) or "unknown",
        "creator_or_contributor": _list(payload.get("creator_or_contributor")),
        "publisher_or_collection": _text(payload.get("publisher_or_collection")) or "unknown",
        "creation_date_candidate": _text(payload.get("creation_date_candidate")) or "unknown",
        "publication_date_candidate": _text(payload.get("publication_date_candidate")) or "unknown",
        "language_or_locale": _text(payload.get("language_or_locale")) or "unknown",
        "subject_or_tag": _list(payload.get("subject_or_tag")),
        "duration_or_dimensions_candidate": _text(payload.get("duration_or_dimensions_candidate")) or "unknown",
        "file_metadata_candidate": _mapping(payload.get("file_metadata_candidate"), "file_metadata_candidate", default={}),
        "checksum_metadata_candidate": _text(payload.get("checksum_metadata_candidate")) or "unknown",
        "source_locator_candidate": _text(payload.get("source_locator_candidate")) or "unknown",
        "thumbnail_or_preview_ref": _text(payload.get("thumbnail_or_preview_ref")) or "not_provided",
        "metadata_license_candidate": _text(payload.get("metadata_license_candidate")) or "unknown",
        "artist_or_creator": _list(payload.get("artist_or_creator")),
        "work_title": _text(payload.get("work_title")) or "unknown",
        "recording_title": _text(payload.get("recording_title")) or "unknown",
        "release_title": _text(payload.get("release_title")) or "unknown",
        "release_group_candidate": _text(payload.get("release_group_candidate")) or "unknown",
        "label_or_publisher": _text(payload.get("label_or_publisher")) or "unknown",
        "catalog_number": _text(payload.get("catalog_number")) or "unknown",
        "isrc_candidate": _text(payload.get("isrc_candidate")) or "unknown",
        "iswc_candidate": _text(payload.get("iswc_candidate")) or "unknown",
        "musicbrainz_id_candidate": _text(payload.get("musicbrainz_id_candidate")) or "unknown",
        "discogs_id_candidate": _text(payload.get("discogs_id_candidate")) or "unknown",
        "acoustid_candidate": _text(payload.get("acoustid_candidate")) or "unknown",
        "track_number_candidate": _text(payload.get("track_number_candidate")) or "unknown",
        "medium_format_candidate": _text(payload.get("medium_format_candidate")) or "unknown",
        "country_or_region_candidate": _text(payload.get("country_or_region_candidate")) or "unknown",
        "visual_title": _text(payload.get("visual_title")) or "unknown",
        "object_record_id": _text(payload.get("object_record_id")) or "unknown",
        "image_or_video_id": _text(payload.get("image_or_video_id")) or "unknown",
        "map_id": _text(payload.get("map_id")) or "unknown",
        "place_or_geospatial_ref": _text(payload.get("place_or_geospatial_ref")) or "unknown",
        "medium_or_material": _text(payload.get("medium_or_material")) or "unknown",
        "rights_or_license_metadata": _mapping(payload.get("rights_or_license_metadata"), "rights_or_license_metadata", default={}),
        "fingerprint_metadata": _mapping(payload.get("fingerprint_metadata"), "fingerprint_metadata", default={}),
        "safety_privacy_metadata": _mapping(payload.get("safety_privacy_metadata"), "safety_privacy_metadata", default={}),
        "source_metadata": _mapping(payload.get("source_metadata"), "source_metadata", default={}),
        "metadata_summary": _text(payload.get("metadata_summary")) or "fixture-only media metadata summary",
        "source_limitations": _dedupe(limitations),
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Fixture-only H9 normalized record; review is required before any downstream use."],
    }
    record["media_object_identity_candidate"] = build_h9_media_object_identity_candidate(record, policy)
    record["music_work_recording_release_candidate"] = build_h9_music_work_recording_release_candidate(record, policy)
    record["image_video_map_identity_candidate"] = build_h9_image_video_map_identity_candidate(record, policy)
    record["media_creator_collection_relation_candidate"] = build_h9_media_creator_collection_relation_candidates(record, policy)
    record["media_fingerprint_candidate"] = build_h9_media_fingerprint_candidate(record, policy)
    record["media_rights_license_candidate"] = build_h9_media_rights_license_candidate(record, policy)
    record["media_safety_privacy_candidate"] = build_h9_media_safety_privacy_candidate(record, policy)
    record["source_cache_candidate_preview"] = build_h9_source_cache_candidate_preview(record, policy)
    record["evidence_candidate_preview"] = build_h9_evidence_candidate_preview(record, policy)
    _raise_on_boundary_errors(record)
    return record


def build_h9_media_object_identity_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("media_title", "alternate_title", "media_type", "media_format", "source_native_id", "collection_id", "catalog_record_id", "creator_or_contributor", "publisher_or_collection", "creation_date_candidate", "publication_date_candidate", "language_or_locale", "subject_or_tag", "file_metadata_candidate", "checksum_metadata_candidate", "duration_or_dimensions_candidate", "source_locator_candidate", "thumbnail_or_preview_ref", "metadata_license_candidate")
    return _candidate(normalized_record, "h9_media_object_identity_candidate.v0", "media_object_identity", fields, "Media object identity candidate is not accepted media truth, availability proof, rights clearance, authenticity proof, malware safety proof, or download permission.")


def build_h9_music_work_recording_release_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("artist_or_creator", "work_title", "recording_title", "release_title", "release_group_candidate", "label_or_publisher", "catalog_number", "isrc_candidate", "iswc_candidate", "musicbrainz_id_candidate", "discogs_id_candidate", "acoustid_candidate", "track_number_candidate", "medium_format_candidate", "publication_date_candidate", "country_or_region_candidate")
    return _candidate(normalized_record, "h9_music_work_recording_release_candidate.v0", "music_work_recording_release", fields, "Music work/recording/release candidate is not accepted music truth, audio identity truth, streaming permission, download permission, or redistribution permission.")


def build_h9_image_video_map_identity_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("visual_title", "creator_or_contributor", "collection_id", "object_record_id", "image_or_video_id", "map_id", "creation_date_candidate", "place_or_geospatial_ref", "duration_or_dimensions_candidate", "medium_or_material", "rights_or_license_metadata", "file_metadata_candidate", "source_locator_candidate")
    return _candidate(normalized_record, "h9_image_video_map_identity_candidate.v0", "image_video_map_identity", fields, "Image/video/map identity candidate is not accepted object truth, geospatial correctness proof, rights clearance, authenticity proof, or download permission.")


def build_h9_media_creator_collection_relation_candidates(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    fields = ("source_native_id", "media_title", "creator_or_contributor", "publisher_or_collection", "collection_id", "work_title", "recording_title", "release_title", "place_or_geospatial_ref")
    return [_candidate(normalized_record, "h9_media_creator_collection_relation_candidate.v0", "media_creator_collection_relation", fields, "Creator/collection relation candidate is not relation truth, duplicate truth, attribution correctness, or rights clearance.")]


def build_h9_media_fingerprint_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("fingerprint_metadata", "acoustid_candidate", "recording_title", "source_native_id", "checksum_metadata_candidate")
    return _candidate(normalized_record, "h9_media_fingerprint_candidate.v0", "media_fingerprint", fields, "Fingerprint candidate is synthetic fixture metadata only; it is not identity truth, upload permission, submission permission, fingerprint generation permission, safety proof, or rights proof.")


def build_h9_media_rights_license_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("rights_or_license_metadata", "metadata_license_candidate", "source_locator_candidate", "publisher_or_collection", "thumbnail_or_preview_ref")
    return _candidate(normalized_record, "h9_media_rights_license_candidate.v0", "media_rights_license", fields, "Rights/license candidate is not rights clearance, public-domain truth, Creative Commons validity, download permission, redistribution permission, or attribution correctness.")


def build_h9_media_safety_privacy_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("safety_privacy_metadata", "subject_or_tag", "place_or_geospatial_ref", "rights_or_license_metadata")
    return _candidate(normalized_record, "h9_media_safety_privacy_candidate.v0", "media_safety_privacy", fields, "Safety/privacy candidate is not content safety truth, privacy safety truth, malware safety proof, takedown resolution, or release approval.")


def build_h9_source_cache_candidate_preview(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    preview = {
        "schema_version": "h9_media_metadata_source_cache_candidate_preview.v0",
        "source_cache_candidate_preview_id": f"h9.source_cache_preview.{normalized_record.get('source_id')}.{_slug(normalized_record.get('source_native_id'))}.v0",
        "source_id": normalized_record.get("source_id"),
        "source_record_ref": normalized_record.get("normalized_record_id"),
        "preview_only": True,
        "accepted_source": False,
        "persistence_allowed_current": False,
        "supporting_fields": [field for field in ("media_title", "source_native_id", "connector_family", "source_record_kind") if _is_present(normalized_record.get(field))],
        "limitations": ["Source-cache candidate preview only; no source cache mutation or accepted source truth."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(preview)
    return preview


def build_h9_evidence_candidate_preview(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    preview = {
        "schema_version": "h9_media_metadata_evidence_candidate_preview.v0",
        "evidence_candidate_preview_id": f"h9.evidence_preview.{normalized_record.get('source_id')}.{_slug(normalized_record.get('source_native_id'))}.v0",
        "source_id": normalized_record.get("source_id"),
        "source_record_ref": normalized_record.get("normalized_record_id"),
        "preview_only": True,
        "accepted_evidence": False,
        "evidence_ledger_write_allowed_current": False,
        "supporting_fields": [field for field in ("media_title", "catalog_record_id", "metadata_summary") if _is_present(normalized_record.get(field))],
        "limitations": ["Evidence candidate preview only; no evidence ledger mutation or accepted evidence truth."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(preview)
    return preview


def build_h9_fixture_replay_result(fixture: Mapping[str, Any], normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    status = "blocked_by_policy_fixture" if fixture.get("fixture_status") == "policy_blocked" else "fixture_replayed"
    result = {
        "schema_version": "h9_media_metadata_fixture_replay_result.v0",
        "fixture_replay_result_id": f"h9.replay.{fixture.get('source_id')}.{_slug(fixture.get('fixture_id'))}.v0",
        "fixture_ref": fixture.get("fixture_id"),
        "source_id": fixture.get("source_id"),
        "connector_family": fixture.get("connector_family"),
        "fixture_kind": fixture.get("fixture_kind"),
        "replay_status": status,
        "normalized_record": dict(normalized_record),
        "media_object_identity_candidate": normalized_record.get("media_object_identity_candidate", {}),
        "music_work_recording_release_candidate": normalized_record.get("music_work_recording_release_candidate", {}),
        "image_video_map_identity_candidate": normalized_record.get("image_video_map_identity_candidate", {}),
        "media_creator_collection_relation_candidate": normalized_record.get("media_creator_collection_relation_candidate", []),
        "media_fingerprint_candidate": normalized_record.get("media_fingerprint_candidate", {}),
        "media_rights_license_candidate": normalized_record.get("media_rights_license_candidate", {}),
        "media_safety_privacy_candidate": normalized_record.get("media_safety_privacy_candidate", {}),
        "source_cache_candidate_preview": normalized_record.get("source_cache_candidate_preview", {}),
        "evidence_candidate_preview": normalized_record.get("evidence_candidate_preview", {}),
        "no_network_used": True,
        "no_live_source_used": True,
        "no_api_catalog_query_used": True,
        "no_download_upload_fingerprint_used": True,
        "no_media_payload_used": True,
        "no_scraping_crawling_used": True,
        "no_restricted_source_access_used": True,
        "no_public_master_index_mutation": True,
        "no_truth_acceptance": True,
        "warnings": [],
        "limitations": ["Fixture replay result is an offline parser proof, not accepted truth or permission."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(result)
    return result


def summarize_h9_normalized_record(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "h9_media_metadata_normalized_record_summary.v0",
        "source_id": record.get("source_id"),
        "normalized_record_id": record.get("normalized_record_id"),
        "media_title": record.get("media_title"),
        "media_object_candidates": 1 if record.get("media_object_identity_candidate") else 0,
        "music_recording_release_candidates": 1 if record.get("music_work_recording_release_candidate") else 0,
        "image_video_map_candidates": 1 if record.get("image_video_map_identity_candidate") else 0,
        "creator_collection_relation_candidates": len(record.get("media_creator_collection_relation_candidate", []) or []),
        "fingerprint_candidates": 1 if record.get("media_fingerprint_candidate") else 0,
        "rights_license_candidates": 1 if record.get("media_rights_license_candidate") else 0,
        "safety_privacy_candidates": 1 if record.get("media_safety_privacy_candidate") else 0,
        "network_calls_made": False,
        "download_upload_fingerprint_used": False,
    }


def detect_h9_truth_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return _detect_true_keys(record, FORBIDDEN_TRUTH_TRUE_KEYS)


def detect_h9_product_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return _detect_true_keys(record, FORBIDDEN_PRODUCT_TRUE_KEYS)


def _candidate(normalized_record: Mapping[str, Any], schema_version: str, candidate_type: str, fields: tuple[str, ...], limitation: str) -> dict[str, Any]:
    source_id = str(normalized_record.get("source_id"))
    native_id = str(normalized_record.get("source_native_id") or normalized_record.get("normalized_record_id") or "unknown")
    supporting = [field for field in fields if _is_present(normalized_record.get(field))]
    candidate = {
        "schema_version": schema_version,
        "candidate_id": f"h9.{candidate_type}.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "source_record_ref": str(normalized_record.get("normalized_record_id") or "unknown"),
        "candidate_type": candidate_type,
        "candidate_fields": {field: normalized_record.get(field, "unknown") for field in fields},
        "supporting_fields": supporting,
        "missing_fields": [field for field in fields if field not in supporting],
        "confidence_or_uncertainty": {
            "confidence": "low",
            "uncertainty": "fixture-only metadata candidate requiring review",
        },
        "limitations": [limitation, "Candidate-only output; no source, evidence, candidate, media, rights, safety, public, public-index, or master-index truth is accepted."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(candidate)
    return candidate


def _require_fixture_boundaries(fixture: Mapping[str, Any]) -> None:
    for key in FIXTURE_FORBIDDEN_TRUE_KEYS:
        if fixture.get(key) is True:
            raise ValueError(f"fixture boundary violation: {key} must be false")
    if not isinstance(fixture.get("fixture_payload"), Mapping):
        raise ValueError("fixture_payload must be an object")


def _missing_optional_limitations(payload: Mapping[str, Any]) -> list[str]:
    optional_fields = ("media_title", "source_native_id", "rights_or_license_metadata", "fingerprint_metadata", "safety_privacy_metadata")
    return [f"optional field {field} is absent or unknown in committed fixture" for field in optional_fields if not _is_present(payload.get(field))]


def _truth_boundary() -> dict[str, bool]:
    return {'normalized_record_is_public_truth': False, 'media_object_identity_candidate_is_truth': False, 'music_identity_candidate_is_truth': False, 'image_video_map_identity_candidate_is_truth': False, 'creator_collection_relation_candidate_is_truth': False, 'fingerprint_match_candidate_is_truth': False, 'rights_license_candidate_is_rights_truth': False, 'safety_privacy_candidate_is_safety_truth': False, 'license_metadata_is_rights_clearance': False, 'public_domain_metadata_is_public_domain_truth': False, 'creative_commons_metadata_is_license_truth': False, 'media_metadata_grants_download_permission': False, 'fingerprint_candidate_grants_upload_or_submission_permission': False, 'source_cache_preview_is_accepted_source': False, 'evidence_preview_is_accepted_evidence': False, 'accepted_source_truth': False, 'accepted_evidence_truth': False, 'accepted_candidate_truth': False, 'accepted_media_identity_truth': False, 'accepted_music_identity_truth': False, 'accepted_image_video_map_truth': False, 'accepted_creator_collection_relation_truth': False, 'accepted_fingerprint_identity_truth': False, 'accepted_rights_license_truth': False, 'accepted_safety_privacy_truth': False, 'accepted_public_record': False, 'public_index_mutated': False, 'master_index_mutated': False, 'rights_clearance_claimed': False, 'public_domain_truth_claimed': False, 'creative_commons_truth_claimed': False, 'content_safety_claimed': False, 'privacy_safety_claimed': False, 'malware_safety_claimed': False, 'verified_authenticity_claimed': False, 'production_readiness_claimed': False}.copy()


def _product_boundary() -> dict[str, bool]:
    return {'changed_public_search_behavior': False, 'enabled_hosting': False, 'enabled_live_probes': False, 'enabled_source_sync': False, 'enabled_downloads': False, 'enabled_uploads': False, 'enabled_fingerprinting': False, 'enabled_crawling': False, 'enabled_accounts': False, 'enabled_telemetry': False, 'mutated_public_index': False, 'mutated_master_index': False, 'network_calls_made': False, 'api_calls_made': False, 'catalog_fetch_used': False, 'media_download_used': False, 'image_download_used': False, 'video_download_used': False, 'audio_download_used': False, 'map_download_used': False, 'score_download_used': False, 'thumbnail_fetch_used': False, 'media_upload_used': False, 'fingerprint_submission_used': False, 'fingerprint_generation_used': False, 'scraping_used': False, 'crawling_used': False, 'restricted_source_access_used': False, 'bypass_or_automation_used': False}.copy()


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


def _raise_on_boundary_errors(record: Mapping[str, Any]) -> None:
    errors = detect_h9_truth_boundary_violations(record) + detect_h9_product_boundary_violations(record)
    if errors:
        raise ValueError("; ".join(errors))


def _mapping(value: Any, name: str, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if value is None:
        return dict(default or {})
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be an object when present")
    return dict(value)


def _list(value: Any) -> list[Any]:
    if value is None or value == "unknown":
        return []
    if isinstance(value, list):
        return value
    return [value]


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value)


def _is_present(value: Any) -> bool:
    return value not in (None, "", "unknown", [], {})


def _dedupe(values: list[Any]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = _text(value)
        if text and text not in seen:
            result.append(text)
            seen.add(text)
    return result


def _slug(value: Any) -> str:
    text = _text(value) or "unknown"
    safe = "".join(ch.lower() if ch.isalnum() else "-" for ch in text).strip("-")
    if len(safe) > 64:
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
        safe = f"{safe[:48].strip('-')}-{digest}"
    return safe or "unknown"

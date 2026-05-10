"""Fixture-only H6 web archive/news/event normalization helpers."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from typing import Any


H6_SOURCE_CONFIGS: dict[str, dict[str, Any]] = {'wayback_cdx_memento': {'label': 'Internet Archive Wayback / CDX / Memento metadata', 'connector_family': 'warc_cdx', 'has_capture': True, 'has_time_state': True, 'has_event': False, 'has_dead_link': True, 'has_public_document': False, 'has_media': False}, 'common_crawl_cdxj': {'label': 'Common Crawl CDXJ / WARC index metadata', 'connector_family': 'warc_cdx', 'has_capture': True, 'has_time_state': True, 'has_event': False, 'has_dead_link': True, 'has_public_document': False, 'has_media': False}, 'public_warc_wacz_collection': {'label': 'Public WARC/WACZ collection metadata', 'connector_family': 'warc_wacz_manifest', 'has_capture': True, 'has_time_state': True, 'has_event': False, 'has_dead_link': True, 'has_public_document': False, 'has_media': True}, 'gdelt_news_event': {'label': 'GDELT news/event metadata', 'connector_family': 'api_json', 'has_capture': False, 'has_time_state': False, 'has_event': True, 'has_dead_link': False, 'has_public_document': False, 'has_media': False}, 'chronicling_america': {'label': 'Chronicling America newspaper metadata', 'connector_family': 'api_json', 'has_capture': False, 'has_time_state': False, 'has_event': True, 'has_dead_link': True, 'has_public_document': False, 'has_media': True}, 'trove_newspapers': {'label': 'Trove newspaper metadata', 'connector_family': 'newspaper_archive_metadata', 'has_capture': False, 'has_time_state': False, 'has_event': True, 'has_dead_link': True, 'has_public_document': False, 'has_media': True}, 'cspan_video_library': {'label': 'C-SPAN video/event metadata', 'connector_family': 'media_archive_metadata', 'has_capture': False, 'has_time_state': False, 'has_event': True, 'has_dead_link': False, 'has_public_document': False, 'has_media': True}, 'aapb_broadcast_archive': {'label': 'American Archive of Public Broadcasting metadata', 'connector_family': 'media_archive_metadata', 'has_capture': False, 'has_time_state': False, 'has_event': True, 'has_dead_link': False, 'has_public_document': False, 'has_media': True}, 'archive_today_snapshot': {'label': 'Archive.today / archive.ph snapshot metadata policy only', 'connector_family': 'html_catalog_policy_blocked', 'has_capture': True, 'has_time_state': True, 'has_event': False, 'has_dead_link': True, 'has_public_document': False, 'has_media': False}, 'generic_newspaper_archive': {'label': 'Generic newspaper archive metadata', 'connector_family': 'newspaper_archive_metadata', 'has_capture': False, 'has_time_state': False, 'has_event': True, 'has_dead_link': True, 'has_public_document': False, 'has_media': True}, 'generic_web_archive': {'label': 'Generic web archive metadata', 'connector_family': 'warc_cdx', 'has_capture': True, 'has_time_state': True, 'has_event': False, 'has_dead_link': True, 'has_public_document': False, 'has_media': False}, 'generic_public_event_trace': {'label': 'Generic public event/source-trace metadata', 'connector_family': 'api_json', 'has_capture': False, 'has_time_state': False, 'has_event': True, 'has_dead_link': True, 'has_public_document': False, 'has_media': False}, 'restricted_public_document_manifest': {'label': 'Restricted/sensitive public-document source manifests', 'connector_family': 'restricted_manifest_only', 'has_capture': False, 'has_time_state': False, 'has_event': False, 'has_dead_link': False, 'has_public_document': True, 'has_media': False}}
H6_SOURCE_IDS = tuple(H6_SOURCE_CONFIGS)
H6_FIXTURE_KINDS = ('minimal', 'capture', 'time_state', 'event_mention', 'dead_link_trace', 'public_document_trace', 'policy_blocked')

FORBIDDEN_TRUTH_TRUE_KEYS = {'archived_content_proves_rights_clearance', 'media_metadata_proves_event_truth', 'archived_download_page_grants_download_permission', 'accepted_candidate_truth', 'article_metadata_is_claim_truth', 'evidence_preview_is_accepted_evidence', 'master_index_mutated', 'privacy_safety_claimed', 'capture_presence_proves_completeness', 'mirror_candidate_proves_authenticity', 'accepted_public_record', 'accepted_web_capture_truth', 'nearest_capture_proves_exact_state', 'sensitive_source_access_approved', 'dead_link_trace_grants_acquisition_permission', 'verified_authenticity_claimed', 'public_index_mutated', 'normalized_record_is_public_truth', 'public_document_trace_is_public_truth', 'archived_time_state_candidate_is_historical_truth', 'checksum_candidate_proves_malware_safety', 'web_capture_candidate_is_truth', 'time_state_candidate_is_historical_truth', 'accepted_article_truth', 'missing_capture_proves_absence', 'old_download_page_proves_current_availability', 'accepted_public_document_truth', 'production_readiness_claimed', 'news_event_mention_candidate_is_event_truth', 'source_cache_preview_is_accepted_source', 'web_capture_identity_candidate_is_accepted_capture_truth', 'article_metadata_proves_claim_accuracy', 'accepted_event_truth', 'malware_safety_claimed', 'accepted_time_state_truth', 'accepted_source_truth', 'transcript_metadata_proves_full_context', 'capture_digest_proves_authenticity', 'accepted_evidence_truth', 'rights_clearance_claimed'}
FORBIDDEN_PRODUCT_TRUE_KEYS = {'network_calls_made', 'enabled_source_connectors', 'enabled_fetching', 'enabled_hosting', 'enabled_telemetry', 'archived_page_fetch_used', 'scraping_used', 'enabled_live_probes', 'mutated_master_index', 'enabled_downloads', 'api_calls_made', 'live_page_fetch_used', 'enabled_source_sync', 'warc_wacz_fetch_used', 'crawling_used', 'bypass_or_automation_used', 'enabled_browser_automation', 'public_document_fetch_used', 'enabled_uploads', 'mutated_public_index', 'media_download_used', 'transcript_download_used', 'restricted_sensitive_source_access_used', 'memento_lookup_used', 'enabled_accounts', 'enabled_scraping', 'cdx_query_used', 'changed_public_search_behavior', 'enabled_crawling'}
FIXTURE_FORBIDDEN_TRUE_KEYS = {
    "live_call_used", "network_used", "external_api_used", "cdx_payload_included",
    "memento_payload_included", "warc_wacz_payload_included", "archived_page_payload_included",
    "live_page_payload_included", "media_payload_included", "transcript_payload_included",
    "newspaper_page_payload_included", "public_document_payload_included",
    "scraping_output_included", "crawling_output_included",
    "restricted_sensitive_source_accessed", "bypass_or_automation_used",
}


def normalize_h6_web_archive_fixture(raw_fixture: Mapping[str, Any], source_id: str, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if source_id not in H6_SOURCE_CONFIGS:
        raise ValueError(f"unknown H6 source_id: {source_id}")
    if raw_fixture.get("source_id") != source_id:
        raise ValueError(f"fixture source_id does not match requested source_id: {source_id}")
    _require_fixture_boundaries(raw_fixture)
    payload = _mapping(raw_fixture.get("fixture_payload"), "fixture_payload")
    config = H6_SOURCE_CONFIGS[source_id]
    native_id = _text(payload.get("source_native_id")) or _text(payload.get("article_or_record_id")) or _text(payload.get("original_url")) or f"fixture-{source_id}"
    limitations = list(raw_fixture.get("limitations") or [])
    limitations.extend(_missing_optional_limitations(payload))
    if raw_fixture.get("fixture_status") == "policy_blocked":
        limitations.append("fixture is policy-blocked and remains candidate-only")
    record: dict[str, Any] = {
        "schema_version": "h6_web_archive_normalized_record.v0",
        "normalized_record_id": f"h6.normalized.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "connector_family": str(raw_fixture.get("connector_family") or config["connector_family"]),
        "source_record_kind": _text(payload.get("source_record_kind")) or _text(raw_fixture.get("fixture_kind")) or "unknown",
        "original_url": _text(payload.get("original_url")) or "unknown",
        "normalized_url_candidate": _text(payload.get("normalized_url_candidate")) or "unknown",
        "capture_url": _text(payload.get("capture_url")) or "unknown",
        "capture_timestamp": _text(payload.get("capture_timestamp")) or "unknown",
        "memento_datetime": _text(payload.get("memento_datetime")) or "unknown",
        "capture_status_code": _text(payload.get("capture_status_code")) or "unknown",
        "capture_mime_type": _text(payload.get("capture_mime_type")) or "unknown",
        "capture_digest": _text(payload.get("capture_digest")) or "unknown",
        "capture_length": _text(payload.get("capture_length")) or "unknown",
        "warc_record_id_candidate": _text(payload.get("warc_record_id_candidate")) or "unknown",
        "warc_filename_candidate": _text(payload.get("warc_filename_candidate")) or "unknown",
        "cdx_key_candidate": _text(payload.get("cdx_key_candidate")) or "unknown",
        "collection_id": _text(payload.get("collection_id")) or "unknown",
        "source_archive_ref": _text(payload.get("source_archive_ref")) or str(config["label"]),
        "requested_time": _text(payload.get("requested_time")) or "unknown",
        "nearest_capture": _text(payload.get("nearest_capture")) or "unknown",
        "first_seen_candidate": _text(payload.get("first_seen_candidate")) or "unknown",
        "last_seen_candidate": _text(payload.get("last_seen_candidate")) or "unknown",
        "status_at_time_candidate": _text(payload.get("status_at_time_candidate")) or "unknown",
        "redirect_state_candidate": _text(payload.get("redirect_state_candidate")) or "unknown",
        "missing_capture_candidate": _text(payload.get("missing_capture_candidate")) or "unknown",
        "gap_period_candidate": _text(payload.get("gap_period_candidate")) or "unknown",
        "source_disappearance_candidate": _text(payload.get("source_disappearance_candidate")) or "unknown",
        "resurrected_source_candidate": _text(payload.get("resurrected_source_candidate")) or "unknown",
        "archived_download_page_candidate": _text(payload.get("archived_download_page_candidate")) or "unknown",
        "article_or_record_id": _text(payload.get("article_or_record_id")) or "unknown",
        "headline_or_title": _text(payload.get("headline_or_title")) or "unknown",
        "publication_or_program": _text(payload.get("publication_or_program")) or "unknown",
        "publication_date": _text(payload.get("publication_date")) or "unknown",
        "byline_or_actor": _text(payload.get("byline_or_actor")) or "unknown",
        "event_date_candidate": _text(payload.get("event_date_candidate")) or "unknown",
        "event_location_candidate": _text(payload.get("event_location_candidate")) or "unknown",
        "mentioned_entity": _text(payload.get("mentioned_entity")) or "unknown",
        "mentioned_url": _text(payload.get("mentioned_url")) or "unknown",
        "mentioned_software_or_artifact": _text(payload.get("mentioned_software_or_artifact")) or "unknown",
        "topic_or_theme": _text(payload.get("topic_or_theme")) or "unknown",
        "snippet_or_summary": _text(payload.get("snippet_or_summary")) or "unknown",
        "transcript_or_caption_ref": _text(payload.get("transcript_or_caption_ref")) or "unknown",
        "media_ref": _text(payload.get("media_ref")) or "unknown",
        "dead_url_candidate": _text(payload.get("dead_url_candidate")) or "unknown",
        "last_live_candidate": _text(payload.get("last_live_candidate")) or "unknown",
        "first_dead_candidate": _text(payload.get("first_dead_candidate")) or "unknown",
        "archived_snapshot_candidate": _text(payload.get("archived_snapshot_candidate")) or "unknown",
        "referring_page_candidate": _text(payload.get("referring_page_candidate")) or "unknown",
        "old_download_page_candidate": _text(payload.get("old_download_page_candidate")) or "unknown",
        "mirror_candidate": _text(payload.get("mirror_candidate")) or "unknown",
        "checksum_candidate": _text(payload.get("checksum_candidate")) or "unknown",
        "product_or_artifact_ref": _text(payload.get("product_or_artifact_ref")) or "unknown",
        "vendor_or_source_ref": _text(payload.get("vendor_or_source_ref")) or "unknown",
        "disappearance_reason_candidate": _text(payload.get("disappearance_reason_candidate")) or "unknown",
        "followup_workunit_candidate": _text(payload.get("followup_workunit_candidate")) or "unknown",
        "public_document_ref": _text(payload.get("public_document_ref")) or "unknown",
        "document_collection_ref": _text(payload.get("document_collection_ref")) or "unknown",
        "document_record_id": _text(payload.get("document_record_id")) or "unknown",
        "document_title": _text(payload.get("document_title")) or "unknown",
        "publication_or_disclosure_date": _text(payload.get("publication_or_disclosure_date")) or "unknown",
        "source_locator": _text(payload.get("source_locator")) or "unknown",
        "source_risk_class": _text(payload.get("source_risk_class")) or "unknown",
        "sensitivity_class": _text(payload.get("sensitivity_class")) or "unknown",
        "rights_or_access_uncertainty": _text(payload.get("rights_or_access_uncertainty")) or "unknown",
        "restricted_source_policy": _text(payload.get("restricted_source_policy")) or "unknown",
        "media_or_transcript_ref": _text(payload.get("media_or_transcript_ref")) or "unknown",
        "media_or_program_id": _text(payload.get("media_or_program_id")) or "unknown",
        "media_title": _text(payload.get("media_title")) or "unknown",
        "media_date": _text(payload.get("media_date")) or "unknown",
        "speaker_or_actor_candidate": _text(payload.get("speaker_or_actor_candidate")) or "unknown",
        "topic_or_subject_candidate": _text(payload.get("topic_or_subject_candidate")) or "unknown",
        "metadata_summary": _text(payload.get("metadata_summary")) or "fixture-only metadata summary",
        "source_metadata": _mapping(payload.get("source_metadata"), "source_metadata", default={}),
        "source_limitations": _dedupe(limitations),
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Fixture-only H6 normalized record; review is required before any downstream use."],
    }
    capture = build_h6_web_capture_identity_candidate(record, policy)
    time_state = build_h6_archived_url_time_state_candidate(record, policy)
    event_candidates = build_h6_news_event_mention_candidates(record, policy)
    dead_link_candidates = build_h6_dead_link_trace_candidates(record, policy)
    public_document_candidates = build_h6_public_document_trace_candidates(record, policy)
    media_candidates = build_h6_media_transcript_metadata_candidates(record, policy)
    record["web_capture_identity_candidate"] = capture
    record["archived_url_time_state_candidate"] = time_state
    record["news_event_mention_candidate"] = event_candidates[0] if event_candidates else {}
    record["dead_link_trace_candidate"] = dead_link_candidates[0] if dead_link_candidates else {}
    record["public_document_trace_candidate"] = public_document_candidates[0] if public_document_candidates else {}
    record["media_transcript_metadata_candidate"] = media_candidates[0] if media_candidates else {}
    record["news_event_mention_candidate_preview"] = event_candidates
    record["dead_link_trace_candidate_preview"] = dead_link_candidates
    record["public_document_trace_candidate_preview"] = public_document_candidates
    record["media_transcript_metadata_candidate_preview"] = media_candidates
    record["source_cache_candidate_preview"] = build_h6_source_cache_candidate_preview(record, policy)
    record["evidence_candidate_preview"] = build_h6_evidence_candidate_preview(record, policy)
    _raise_on_boundary_errors(record)
    return record


def build_h6_web_capture_identity_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = str(normalized_record.get("source_id"))
    native_id = str(normalized_record.get("original_url") or normalized_record.get("normalized_record_id") or "unknown")
    fields = ("original_url", "normalized_url_candidate", "capture_url", "capture_timestamp", "memento_datetime", "capture_status_code", "capture_mime_type", "capture_digest", "capture_length", "warc_record_id_candidate", "warc_filename_candidate", "cdx_key_candidate", "collection_id", "source_archive_ref")
    candidate = {
        "schema_version": "h6_web_capture_identity_candidate.v0",
        "web_capture_identity_candidate_id": f"h6.web_capture.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "original_url": normalized_record.get("original_url", "unknown"),
        "normalized_url_candidate": normalized_record.get("normalized_url_candidate", "unknown"),
        "capture_url": normalized_record.get("capture_url", "unknown"),
        "capture_timestamp": normalized_record.get("capture_timestamp", "unknown"),
        "memento_datetime": normalized_record.get("memento_datetime", "unknown"),
        "capture_status_code": normalized_record.get("capture_status_code", "unknown"),
        "capture_mime_type": normalized_record.get("capture_mime_type", "unknown"),
        "capture_digest": normalized_record.get("capture_digest", "unknown"),
        "capture_length": normalized_record.get("capture_length", "unknown"),
        "warc_record_id_candidate": normalized_record.get("warc_record_id_candidate", "unknown"),
        "warc_filename_candidate": normalized_record.get("warc_filename_candidate", "unknown"),
        "cdx_key_candidate": normalized_record.get("cdx_key_candidate", "unknown"),
        "collection_id": normalized_record.get("collection_id", "unknown"),
        "source_archive_ref": normalized_record.get("source_archive_ref", "unknown"),
        "capture_locator_candidate": normalized_record.get("capture_url", "unknown"),
        "redirect_chain_candidate": normalized_record.get("redirect_state_candidate", "unknown"),
        "canonical_url_candidate": normalized_record.get("normalized_url_candidate", "unknown"),
        "confidence_or_uncertainty": "candidate_from_fixture_no_capture_truth",
        "supporting_fields": [field for field in fields if normalized_record.get(field) not in (None, "", "unknown", [], {})],
        "missing_fields": [field for field in fields if normalized_record.get(field) in (None, "", "unknown", [], {})],
        "limitations": ["Web capture identity candidate is not accepted capture truth, completeness, authenticity, or rights clearance."],
        "truth_boundary": {
            "web_capture_identity_candidate_is_accepted_capture_truth": False,
            "web_capture_candidate_is_truth": False,
            "capture_presence_proves_completeness": False,
            "capture_digest_proves_authenticity": False,
            "archived_content_proves_rights_clearance": False,
        },
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(candidate)
    return candidate


def build_h6_archived_url_time_state_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = str(normalized_record.get("source_id"))
    native_id = str(normalized_record.get("original_url") or normalized_record.get("normalized_record_id") or "unknown")
    candidate = {
        "schema_version": "h6_archived_url_time_state_candidate.v0",
        "time_state_candidate_id": f"h6.time_state.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "original_url": normalized_record.get("original_url", "unknown"),
        "requested_time": normalized_record.get("requested_time", "unknown"),
        "nearest_capture": normalized_record.get("nearest_capture", "unknown"),
        "first_seen_candidate": normalized_record.get("first_seen_candidate", "unknown"),
        "last_seen_candidate": normalized_record.get("last_seen_candidate", "unknown"),
        "status_at_time_candidate": normalized_record.get("status_at_time_candidate", "unknown"),
        "redirect_state_candidate": normalized_record.get("redirect_state_candidate", "unknown"),
        "missing_capture_candidate": normalized_record.get("missing_capture_candidate", "unknown"),
        "gap_period_candidate": normalized_record.get("gap_period_candidate", "unknown"),
        "source_disappearance_candidate": normalized_record.get("source_disappearance_candidate", "unknown"),
        "resurrected_source_candidate": normalized_record.get("resurrected_source_candidate", "unknown"),
        "archived_download_page_candidate": normalized_record.get("archived_download_page_candidate", "unknown"),
        "limitations": ["Archived URL time-state candidate is not historical truth or download permission."],
        "truth_boundary": {
            "archived_time_state_candidate_is_historical_truth": False,
            "time_state_candidate_is_historical_truth": False,
            "nearest_capture_proves_exact_state": False,
            "missing_capture_proves_absence": False,
            "archived_download_page_grants_download_permission": False,
        },
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(candidate)
    return candidate


def build_h6_news_event_mention_candidates(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    if not _has_any(normalized_record, ("article_or_record_id", "headline_or_title", "publication_or_program", "event_date_candidate", "mentioned_entity", "mentioned_url")):
        return []
    source_id = str(normalized_record.get("source_id"))
    native_id = str(normalized_record.get("article_or_record_id") or normalized_record.get("normalized_record_id") or "unknown")
    candidate = {
        "schema_version": "h6_news_event_mention_candidate.v0",
        "news_event_mention_candidate_id": f"h6.news_event.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "article_or_record_id": normalized_record.get("article_or_record_id", "unknown"),
        "headline_or_title": normalized_record.get("headline_or_title", "unknown"),
        "publication_or_program": normalized_record.get("publication_or_program", "unknown"),
        "publication_date": normalized_record.get("publication_date", "unknown"),
        "byline_or_actor": normalized_record.get("byline_or_actor", "unknown"),
        "event_date_candidate": normalized_record.get("event_date_candidate", "unknown"),
        "event_location_candidate": normalized_record.get("event_location_candidate", "unknown"),
        "mentioned_entity": normalized_record.get("mentioned_entity", "unknown"),
        "mentioned_url": normalized_record.get("mentioned_url", "unknown"),
        "mentioned_software_or_artifact": normalized_record.get("mentioned_software_or_artifact", "unknown"),
        "topic_or_theme": normalized_record.get("topic_or_theme", "unknown"),
        "snippet_or_summary": normalized_record.get("snippet_or_summary", "unknown"),
        "transcript_or_caption_ref": normalized_record.get("transcript_or_caption_ref", "unknown"),
        "media_ref": normalized_record.get("media_ref", "unknown"),
        "source_locator": normalized_record.get("source_locator", "unknown"),
        "confidence_or_uncertainty": "candidate_from_fixture_no_event_truth",
        "limitations": ["News/event mention candidate is not event truth, article truth, or full transcript context."],
        "truth_boundary": {
            "news_event_mention_candidate_is_event_truth": False,
            "article_metadata_proves_claim_accuracy": False,
            "article_metadata_is_claim_truth": False,
            "transcript_metadata_proves_full_context": False,
        },
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(candidate)
    return [candidate]


def build_h6_dead_link_trace_candidates(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    if not _has_any(normalized_record, ("dead_url_candidate", "archived_snapshot_candidate", "referring_page_candidate", "old_download_page_candidate")):
        return []
    source_id = str(normalized_record.get("source_id"))
    native_id = str(normalized_record.get("dead_url_candidate") or normalized_record.get("normalized_record_id") or "unknown")
    candidate = {
        "schema_version": "h6_dead_link_trace_candidate.v0",
        "dead_link_trace_candidate_id": f"h6.dead_link.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "dead_url_candidate": normalized_record.get("dead_url_candidate", "unknown"),
        "last_live_candidate": normalized_record.get("last_live_candidate", "unknown"),
        "first_dead_candidate": normalized_record.get("first_dead_candidate", "unknown"),
        "archived_snapshot_candidate": normalized_record.get("archived_snapshot_candidate", "unknown"),
        "referring_page_candidate": normalized_record.get("referring_page_candidate", "unknown"),
        "old_download_page_candidate": normalized_record.get("old_download_page_candidate", "unknown"),
        "mirror_candidate": normalized_record.get("mirror_candidate", "unknown"),
        "checksum_candidate": normalized_record.get("checksum_candidate", "unknown"),
        "product_or_artifact_ref": normalized_record.get("product_or_artifact_ref", "unknown"),
        "vendor_or_source_ref": normalized_record.get("vendor_or_source_ref", "unknown"),
        "disappearance_reason_candidate": normalized_record.get("disappearance_reason_candidate", "unknown"),
        "followup_workunit_candidate": normalized_record.get("followup_workunit_candidate", "unknown"),
        "limitations": ["Dead-link trace candidate grants no acquisition, authenticity, availability, or safety permission."],
        "truth_boundary": {
            "dead_link_trace_grants_acquisition_permission": False,
            "mirror_candidate_proves_authenticity": False,
            "checksum_candidate_proves_malware_safety": False,
            "old_download_page_proves_current_availability": False,
            "malware_safety_claimed": False,
        },
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(candidate)
    return [candidate]


def build_h6_public_document_trace_candidates(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    if not _has_any(normalized_record, ("document_collection_ref", "document_record_id", "document_title", "public_document_ref", "sensitivity_class")):
        return []
    source_id = str(normalized_record.get("source_id"))
    native_id = str(normalized_record.get("document_record_id") or normalized_record.get("public_document_ref") or "unknown")
    candidate = {
        "schema_version": "h6_public_document_trace_candidate.v0",
        "public_document_trace_candidate_id": f"h6.public_document.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "document_collection_ref": normalized_record.get("document_collection_ref", "unknown"),
        "document_record_id": normalized_record.get("document_record_id", "unknown"),
        "document_title": normalized_record.get("document_title", "unknown"),
        "publication_or_disclosure_date": normalized_record.get("publication_or_disclosure_date", "unknown"),
        "source_locator": normalized_record.get("source_locator", "unknown"),
        "source_risk_class": normalized_record.get("source_risk_class", "unknown"),
        "sensitivity_class": normalized_record.get("sensitivity_class", "unknown"),
        "rights_or_access_uncertainty": normalized_record.get("rights_or_access_uncertainty", "unknown"),
        "restricted_source_policy": normalized_record.get("restricted_source_policy", "manifest_only_policy_blocked"),
        "manifest_only_allowed": True,
        "direct_fetch_allowed_current": False,
        "review_required": True,
        "limitations": ["Public-document trace candidate is manifest-only and does not approve direct fetch or public truth."],
        "truth_boundary": {
            "public_document_trace_is_public_truth": False,
            "sensitive_source_access_approved": False,
            "rights_clearance_claimed": False,
            "privacy_safety_claimed": False,
        },
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(candidate)
    return [candidate]


def build_h6_media_transcript_metadata_candidates(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    if not _has_any(normalized_record, ("media_or_program_id", "media_title", "transcript_or_caption_ref", "media_or_transcript_ref", "media_ref")):
        return []
    source_id = str(normalized_record.get("source_id"))
    native_id = str(normalized_record.get("media_or_program_id") or normalized_record.get("media_ref") or "unknown")
    candidate = {
        "schema_version": "h6_media_transcript_metadata_candidate.v0",
        "media_transcript_metadata_candidate_id": f"h6.media_transcript.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "media_or_program_id": normalized_record.get("media_or_program_id", "unknown"),
        "media_title": normalized_record.get("media_title", "unknown"),
        "media_date": normalized_record.get("media_date", "unknown"),
        "transcript_or_caption_ref": normalized_record.get("transcript_or_caption_ref", "unknown"),
        "speaker_or_actor_candidate": normalized_record.get("speaker_or_actor_candidate", "unknown"),
        "topic_or_subject_candidate": normalized_record.get("topic_or_subject_candidate", "unknown"),
        "mentioned_entity": normalized_record.get("mentioned_entity", "unknown"),
        "mentioned_url": normalized_record.get("mentioned_url", "unknown"),
        "source_locator": normalized_record.get("source_locator", "unknown"),
        "payload_available_current": False,
        "download_allowed_current": False,
        "limitations": ["Media/transcript metadata candidate grants no payload access and proves no event truth or full context."],
        "truth_boundary": {
            "transcript_metadata_proves_full_context": False,
            "media_metadata_proves_event_truth": False,
            "news_event_mention_candidate_is_event_truth": False,
        },
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(candidate)
    return [candidate]


def build_h6_source_cache_candidate_preview(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = str(normalized_record.get("source_id"))
    preview = {
        "schema_version": "h6_web_archive_source_cache_candidate.v0",
        "source_cache_candidate_id": f"h6.source_cache.{source_id}.{_slug(str(normalized_record.get('normalized_record_id') or 'unknown'))}.v0",
        "source_id": source_id,
        "record_ref": normalized_record.get("normalized_record_id"),
        "candidate_status": "preview_only",
        "accepted_as_source": False,
        "review_required": True,
        "truth_boundary": {"source_cache_preview_is_accepted_source": False, "accepted_source_truth": False, "public_index_mutated": False, "master_index_mutated": False},
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(preview)
    return preview


def build_h6_evidence_candidate_preview(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = str(normalized_record.get("source_id"))
    preview = {
        "schema_version": "h6_web_archive_evidence_candidate_preview.v0",
        "evidence_candidate_preview_id": f"h6.evidence_preview.{source_id}.{_slug(str(normalized_record.get('normalized_record_id') or 'unknown'))}.v0",
        "source_id": source_id,
        "record_ref": normalized_record.get("normalized_record_id"),
        "candidate_status": "preview_only",
        "accepted_as_evidence": False,
        "review_required": True,
        "truth_boundary": {"evidence_preview_is_accepted_evidence": False, "accepted_evidence_truth": False, "public_index_mutated": False, "master_index_mutated": False},
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(preview)
    return preview


def build_h6_fixture_replay_result(fixture: Mapping[str, Any], normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = str(fixture.get("source_id"))
    result = {
        "schema_version": "h6_web_archive_fixture_replay_result.v0",
        "replay_result_id": f"h6.replay.{source_id}.{_slug(str(fixture.get('fixture_id') or 'fixture'))}.v0",
        "fixture_id": fixture.get("fixture_id"),
        "source_id": source_id,
        "connector_family": fixture.get("connector_family"),
        "replay_status": "pass_fixture_only" if fixture.get("fixture_status") != "policy_blocked" else "blocked_by_policy_fixture",
        "normalized_record_ref": normalized_record.get("normalized_record_id"),
        "web_capture_identity_candidate_ref": normalized_record.get("web_capture_identity_candidate", {}).get("web_capture_identity_candidate_id"),
        "archived_url_time_state_candidate_ref": normalized_record.get("archived_url_time_state_candidate", {}).get("time_state_candidate_id"),
        "news_event_mention_candidate_refs": [item.get("news_event_mention_candidate_id") for item in normalized_record.get("news_event_mention_candidate_preview", [])],
        "dead_link_trace_candidate_refs": [item.get("dead_link_trace_candidate_id") for item in normalized_record.get("dead_link_trace_candidate_preview", [])],
        "public_document_trace_candidate_refs": [item.get("public_document_trace_candidate_id") for item in normalized_record.get("public_document_trace_candidate_preview", [])],
        "media_transcript_metadata_candidate_refs": [item.get("media_transcript_metadata_candidate_id") for item in normalized_record.get("media_transcript_metadata_candidate_preview", [])],
        "source_cache_candidate_ref": normalized_record.get("source_cache_candidate_preview", {}).get("source_cache_candidate_id"),
        "evidence_candidate_preview_ref": normalized_record.get("evidence_candidate_preview", {}).get("evidence_candidate_preview_id"),
        "validation_summary": {
            "normalized": True,
            "fixture_only": True,
            "truth_boundary_violations": detect_h6_truth_boundary_violations(normalized_record),
            "product_boundary_violations": detect_h6_product_boundary_violations(normalized_record),
        },
        "warnings": [],
        "limitations": list(normalized_record.get("source_limitations") or []),
        "no_network_used": True,
        "no_live_source_used": True,
        "no_cdx_query_used": True,
        "no_memento_lookup_used": True,
        "no_warc_wacz_fetch_used": True,
        "no_archived_page_fetch_used": True,
        "no_media_download_used": True,
        "no_scraping_crawling_used": True,
        "no_sensitive_source_access_used": True,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Fixture replay result is not evidence acceptance or public truth."],
    }
    _raise_on_boundary_errors(result)
    return result


def summarize_h6_normalized_record(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": record.get("source_id"),
        "source_record_kind": record.get("source_record_kind"),
        "has_capture_candidate": bool(record.get("web_capture_identity_candidate")),
        "has_time_state_candidate": bool(record.get("archived_url_time_state_candidate")),
        "event_candidate_count": len(record.get("news_event_mention_candidate_preview", []) or []),
        "dead_link_candidate_count": len(record.get("dead_link_trace_candidate_preview", []) or []),
        "public_document_candidate_count": len(record.get("public_document_trace_candidate_preview", []) or []),
        "media_transcript_candidate_count": len(record.get("media_transcript_metadata_candidate_preview", []) or []),
        "truth_boundary_violations": detect_h6_truth_boundary_violations(record),
        "product_boundary_violations": detect_h6_product_boundary_violations(record),
    }


def detect_h6_truth_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return _detect_true_keys(record, FORBIDDEN_TRUTH_TRUE_KEYS, "truth")


def detect_h6_product_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return _detect_true_keys(record, FORBIDDEN_PRODUCT_TRUE_KEYS, "product")


def _require_fixture_boundaries(fixture: Mapping[str, Any]) -> None:
    for key in FIXTURE_FORBIDDEN_TRUE_KEYS:
        if fixture.get(key) is True:
            raise ValueError(f"fixture forbidden behavior flag is true: {key}")
    if fixture.get("fixture_public_safe") is not True:
        raise ValueError("fixture_public_safe must be true")
    for item in detect_h6_truth_boundary_violations(fixture) + detect_h6_product_boundary_violations(fixture):
        raise ValueError(item)


def _truth_boundary() -> dict[str, bool]:
    return {'normalized_record_is_public_truth': False, 'web_capture_identity_candidate_is_accepted_capture_truth': False, 'web_capture_candidate_is_truth': False, 'capture_presence_proves_completeness': False, 'capture_digest_proves_authenticity': False, 'archived_content_proves_rights_clearance': False, 'archived_time_state_candidate_is_historical_truth': False, 'time_state_candidate_is_historical_truth': False, 'nearest_capture_proves_exact_state': False, 'missing_capture_proves_absence': False, 'archived_download_page_grants_download_permission': False, 'news_event_mention_candidate_is_event_truth': False, 'article_metadata_proves_claim_accuracy': False, 'article_metadata_is_claim_truth': False, 'transcript_metadata_proves_full_context': False, 'dead_link_trace_grants_acquisition_permission': False, 'mirror_candidate_proves_authenticity': False, 'checksum_candidate_proves_malware_safety': False, 'old_download_page_proves_current_availability': False, 'public_document_trace_is_public_truth': False, 'sensitive_source_access_approved': False, 'media_metadata_proves_event_truth': False, 'source_cache_preview_is_accepted_source': False, 'evidence_preview_is_accepted_evidence': False, 'accepted_source_truth': False, 'accepted_evidence_truth': False, 'accepted_candidate_truth': False, 'accepted_web_capture_truth': False, 'accepted_time_state_truth': False, 'accepted_event_truth': False, 'accepted_article_truth': False, 'accepted_public_document_truth': False, 'accepted_public_record': False, 'public_index_mutated': False, 'master_index_mutated': False, 'rights_clearance_claimed': False, 'privacy_safety_claimed': False, 'malware_safety_claimed': False, 'verified_authenticity_claimed': False, 'production_readiness_claimed': False}.copy()


def _product_boundary() -> dict[str, bool]:
    return {'changed_public_search_behavior': False, 'enabled_hosting': False, 'enabled_live_probes': False, 'enabled_source_sync': False, 'enabled_source_connectors': False, 'enabled_fetching': False, 'enabled_crawling': False, 'enabled_scraping': False, 'enabled_downloads': False, 'enabled_uploads': False, 'enabled_accounts': False, 'enabled_telemetry': False, 'enabled_browser_automation': False, 'mutated_public_index': False, 'mutated_master_index': False, 'network_calls_made': False, 'api_calls_made': False, 'cdx_query_used': False, 'memento_lookup_used': False, 'warc_wacz_fetch_used': False, 'archived_page_fetch_used': False, 'live_page_fetch_used': False, 'media_download_used': False, 'transcript_download_used': False, 'public_document_fetch_used': False, 'scraping_used': False, 'crawling_used': False, 'restricted_sensitive_source_access_used': False, 'bypass_or_automation_used': False}.copy()


def _mapping(value: Any, name: str, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if value is None:
        return dict(default or {})
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be an object")
    return dict(value)


def _text(value: Any) -> str:
    if value in (None, ""):
        return ""
    return str(value)


def _slug(value: str) -> str:
    safe = "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")
    safe = "-".join(part for part in safe.split("-") if part)
    if safe:
        return safe[:64]
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def _missing_optional_limitations(payload: Mapping[str, Any]) -> list[str]:
    expected = ("original_url", "capture_timestamp", "memento_datetime", "article_or_record_id", "event_date_candidate", "dead_url_candidate", "document_record_id", "media_or_program_id")
    return [f"optional field absent or unknown: {key}" for key in expected if payload.get(key) in (None, "", "unknown", [], {})]


def _has_any(record: Mapping[str, Any], fields: tuple[str, ...]) -> bool:
    return any(record.get(field) not in (None, "", "unknown", [], {}) for field in fields)


def _dedupe(items: list[Any]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        text = str(item)
        if text not in seen:
            out.append(text)
            seen.add(text)
    return out


def _detect_true_keys(value: Any, forbidden: set[str], category: str, path: str = "") -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            current = f"{path}.{key}" if path else str(key)
            if key in forbidden and item is True:
                errors.append(f"{category} boundary forbidden true value: {current}")
            errors.extend(_detect_true_keys(item, forbidden, category, current))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            errors.extend(_detect_true_keys(item, forbidden, category, f"{path}[{index}]"))
    return errors


def _raise_on_boundary_errors(record: Mapping[str, Any]) -> None:
    errors = detect_h6_truth_boundary_violations(record) + detect_h6_product_boundary_violations(record)
    if errors:
        raise ValueError("; ".join(errors))

"""Fail-closed H6 web archive/news/event metadata live-probe helpers."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from typing import Any
import urllib.error
import urllib.request

from control.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.normalizer_common import (
    H6_SOURCE_IDS as FIXTURE_H6_SOURCE_IDS,
    build_h6_archived_url_time_state_candidate as _fixture_time_state_candidate,
    build_h6_dead_link_trace_candidates as _fixture_dead_link_candidates,
    build_h6_evidence_candidate_preview as _fixture_evidence_preview,
    build_h6_media_transcript_metadata_candidates as _fixture_media_candidates,
    build_h6_news_event_mention_candidates as _fixture_event_candidates,
    build_h6_public_document_trace_candidates as _fixture_public_document_candidates,
    build_h6_source_cache_candidate_preview as _fixture_source_cache_preview,
    build_h6_web_capture_identity_candidate as _fixture_capture_candidate,
    detect_h6_product_boundary_violations as _fixture_product_violations,
    detect_h6_truth_boundary_violations as _fixture_truth_violations,
    normalize_h6_web_archive_fixture,
)

POLICY_PATHS = {'allowed_requests': 'control/inventory/connectors/h6_web_archive_live_probe_allowed_requests.json',
 'cache_policy': 'control/inventory/connectors/h6_web_archive_live_probe_cache_policy.json',
 'endpoint_policy': 'control/inventory/connectors/h6_web_archive_live_probe_endpoint_policy.json',
 'kill_switch_policy': 'control/inventory/connectors/h6_web_archive_live_probe_kill_switch_policy.json',
 'live_probe_policy': 'control/inventory/connectors/h6_web_archive_live_probe_policy.json',
 'no_fetch_crawl_policy': 'control/inventory/connectors/h6_web_archive_live_probe_no_fetch_crawl_policy.json',
 'output_policy': 'control/inventory/connectors/h6_web_archive_live_probe_output_policy.json',
 'path_policy': 'control/inventory/connectors/h6_web_archive_live_probe_path_policy.json',
 'rate_limit_policy': 'control/inventory/connectors/h6_web_archive_live_probe_rate_limit_policy.json',
 'review_policy': 'control/inventory/connectors/h6_web_archive_live_probe_review_policy.json',
 'sensitive_source_policy': 'control/inventory/connectors/h6_web_archive_live_probe_sensitive_source_policy.json',
 'truth_policy': 'control/inventory/connectors/h6_web_archive_live_probe_truth_policy.json'}

SOURCE_CONFIGS = {'aapb_broadcast_archive': {'connector_family': 'media_archive_metadata',
                            'endpoint_or_metadata_class': 'broadcast_metadata_lookup_future',
                            'has_capture': False,
                            'has_dead_link': False,
                            'has_event': True,
                            'has_media': True,
                            'has_public_document': False,
                            'has_time_state': False,
                            'label': 'American Archive of Public Broadcasting metadata',
                            'request_key': 'example_broadcast_metadata',
                            'source_record_kind': 'broadcast_metadata'},
 'archive_today_snapshot': {'connector_family': 'html_catalog_policy_blocked',
                            'endpoint_or_metadata_class': 'snapshot_metadata_policy_blocked_current',
                            'has_capture': True,
                            'has_dead_link': True,
                            'has_event': False,
                            'has_media': False,
                            'has_public_document': False,
                            'has_time_state': True,
                            'label': 'Archive.today / archive.ph snapshot metadata policy only',
                            'request_key': 'example_snapshot_metadata',
                            'source_record_kind': 'policy_blocked_snapshot_metadata'},
 'chronicling_america': {'connector_family': 'api_json',
                         'endpoint_or_metadata_class': 'newspaper_metadata_lookup_future',
                         'has_capture': False,
                         'has_dead_link': True,
                         'has_event': True,
                         'has_media': True,
                         'has_public_document': False,
                         'has_time_state': False,
                         'label': 'Chronicling America newspaper metadata',
                         'request_key': 'example_newspaper_metadata',
                         'source_record_kind': 'newspaper_metadata'},
 'common_crawl_cdxj': {'connector_family': 'warc_cdx',
                       'endpoint_or_metadata_class': 'cdxj_metadata_lookup_future',
                       'has_capture': True,
                       'has_dead_link': True,
                       'has_event': False,
                       'has_media': False,
                       'has_public_document': False,
                       'has_time_state': True,
                       'label': 'Common Crawl CDXJ / WARC index metadata',
                       'request_key': 'example_cdxj_metadata',
                       'source_record_kind': 'web_capture_metadata'},
 'cspan_video_library': {'connector_family': 'media_archive_metadata',
                         'endpoint_or_metadata_class': 'video_event_metadata_lookup_future',
                         'has_capture': False,
                         'has_dead_link': False,
                         'has_event': True,
                         'has_media': True,
                         'has_public_document': False,
                         'has_time_state': False,
                         'label': 'C-SPAN video/event metadata',
                         'request_key': 'example_video_event_metadata',
                         'source_record_kind': 'video_event_metadata'},
 'gdelt_news_event': {'connector_family': 'api_json',
                      'endpoint_or_metadata_class': 'news_event_metadata_lookup_future',
                      'has_capture': False,
                      'has_dead_link': False,
                      'has_event': True,
                      'has_media': False,
                      'has_public_document': False,
                      'has_time_state': False,
                      'label': 'GDELT news/event metadata',
                      'request_key': 'example_news_event_metadata',
                      'source_record_kind': 'news_event_metadata'},
 'generic_newspaper_archive': {'connector_family': 'newspaper_archive_metadata',
                               'endpoint_or_metadata_class': 'newspaper_metadata_fixture_future',
                               'has_capture': False,
                               'has_dead_link': True,
                               'has_event': True,
                               'has_media': True,
                               'has_public_document': False,
                               'has_time_state': False,
                               'label': 'Generic newspaper archive metadata',
                               'request_key': 'example_newspaper_metadata',
                               'source_record_kind': 'newspaper_metadata'},
 'generic_public_event_trace': {'connector_family': 'api_json',
                                'endpoint_or_metadata_class': 'event_trace_metadata_fixture_future',
                                'has_capture': False,
                                'has_dead_link': True,
                                'has_event': True,
                                'has_media': False,
                                'has_public_document': False,
                                'has_time_state': False,
                                'label': 'Generic public event/source-trace metadata',
                                'request_key': 'example_event_trace_metadata',
                                'source_record_kind': 'event_trace_metadata'},
 'generic_web_archive': {'connector_family': 'warc_cdx',
                         'endpoint_or_metadata_class': 'web_archive_metadata_fixture_future',
                         'has_capture': True,
                         'has_dead_link': True,
                         'has_event': False,
                         'has_media': False,
                         'has_public_document': False,
                         'has_time_state': True,
                         'label': 'Generic web archive metadata',
                         'request_key': 'example_web_archive_metadata',
                         'source_record_kind': 'web_capture_metadata'},
 'public_warc_wacz_collection': {'connector_family': 'warc_wacz_manifest',
                                 'endpoint_or_metadata_class': 'manifest_metadata_lookup_future',
                                 'has_capture': True,
                                 'has_dead_link': True,
                                 'has_event': False,
                                 'has_media': True,
                                 'has_public_document': False,
                                 'has_time_state': True,
                                 'label': 'Public WARC/WACZ collection metadata',
                                 'request_key': 'example_manifest_metadata',
                                 'source_record_kind': 'warc_wacz_manifest_metadata'},
 'restricted_public_document_manifest': {'connector_family': 'restricted_manifest_only',
                                         'endpoint_or_metadata_class': 'manifest_only_policy_blocked_current',
                                         'has_capture': False,
                                         'has_dead_link': False,
                                         'has_event': False,
                                         'has_media': False,
                                         'has_public_document': True,
                                         'has_time_state': False,
                                         'label': 'Restricted/sensitive public-document source manifests',
                                         'request_key': 'example_manifest_metadata',
                                         'source_record_kind': 'public_document_manifest_metadata'},
 'trove_newspapers': {'connector_family': 'newspaper_archive_metadata',
                      'endpoint_or_metadata_class': 'newspaper_metadata_lookup_future',
                      'has_capture': False,
                      'has_dead_link': True,
                      'has_event': True,
                      'has_media': True,
                      'has_public_document': False,
                      'has_time_state': False,
                      'label': 'Trove newspaper metadata',
                      'request_key': 'example_newspaper_metadata',
                      'source_record_kind': 'newspaper_metadata'},
 'wayback_cdx_memento': {'connector_family': 'warc_cdx',
                         'endpoint_or_metadata_class': 'cdx_metadata_lookup_future',
                         'has_capture': True,
                         'has_dead_link': True,
                         'has_event': False,
                         'has_media': False,
                         'has_public_document': False,
                         'has_time_state': True,
                         'label': 'Internet Archive Wayback / CDX / Memento metadata',
                         'request_key': 'example_capture_metadata',
                         'source_record_kind': 'web_capture_metadata'}}
H6_SOURCE_IDS = tuple(SOURCE_CONFIGS)
ENDPOINT_URL_TEMPLATES = {
    source_id: "https://example.invalid/eureka/h6/{source_id}/{request_key}?metadata_class={metadata_class}"
    for source_id in H6_SOURCE_IDS
}

FORBIDDEN_TRUTH_TRUE_KEYS = set(['accepted_article_truth', 'accepted_candidate_truth', 'accepted_event_truth', 'accepted_evidence_truth', 'accepted_public_document_truth', 'accepted_public_record', 'accepted_source_truth', 'accepted_time_state_truth', 'accepted_web_capture_truth', 'archived_content_proves_rights_clearance', 'archived_time_state_candidate_is_truth', 'capture_digest_proves_authenticity', 'dead_link_trace_grants_acquisition_permission', 'evidence_candidate_preview_is_accepted_evidence', 'live_probe_result_is_public_truth', 'malware_safety_claimed', 'master_index_mutated', 'media_transcript_metadata_is_full_context', 'news_event_mention_candidate_is_event_truth', 'normalized_record_is_public_truth', 'privacy_safety_claimed', 'production_readiness_claimed', 'public_document_trace_is_public_truth', 'public_index_mutated', 'review_seed_is_review_decision', 'rights_clearance_claimed', 'source_cache_candidate_is_accepted_source', 'source_cache_preview_is_accepted_source', 'time_state_candidate_is_historical_truth', 'verified_authenticity_claimed', 'web_capture_candidate_is_truth'])
FORBIDDEN_PRODUCT_TRUE_KEYS = set(['changed_public_search_behavior', 'enabled_accounts', 'enabled_browser_automation', 'enabled_crawling', 'enabled_downloads', 'enabled_fetching', 'enabled_hosting', 'enabled_live_probes', 'enabled_scraping', 'enabled_source_sync', 'enabled_telemetry', 'enabled_uploads', 'mutated_master_index', 'mutated_public_index', 'restricted_sensitive_source_access_used']) | {
    "cdx_query_used",
    "memento_lookup_used",
    "warc_wacz_fetch_used",
    "archived_page_fetch_used",
    "live_page_fetch_used",
    "media_download_used",
    "transcript_download_used",
    "public_document_fetch_used",
    "scraping_used",
    "crawling_used",
    "bypass_or_automation_used",
}


class H6WebArchiveLiveProbeBlocked(RuntimeError):
    """Raised when H6 live-probe policy blocks before network use."""

    def __init__(self, result: Mapping[str, Any]):
        super().__init__("H6 web archive/news/event metadata live probe blocked by committed policy")
        self.result = dict(result)


def load_h6_web_archive_live_probe_policy_bundle(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[5]
    bundle: dict[str, Any] = {}
    for key, rel_path in POLICY_PATHS.items():
        with (root / rel_path).open("r", encoding="utf-8") as handle:
            bundle[key] = json.load(handle)
    return bundle


def build_h6_web_archive_live_probe_request(source_id: str, request_key: str, policy_bundle: Mapping[str, Any], live_requested: bool = False) -> dict[str, Any]:
    if source_id not in SOURCE_CONFIGS:
        raise ValueError(f"unknown H6 source_id: {source_id}")
    source_policy = _source_policy(source_id, policy_bundle)
    request_detail = _request_detail(source_policy, request_key)
    cfg = SOURCE_CONFIGS[source_id]
    request_shape = _mapping(request_detail.get("request_shape")) or {
        "kind": "bounded_trace_metadata_lookup",
        "identifier": {
            "original_url_or_identifier": f"fixture:h6:{source_id}:metadata-only",
            "timestamp_or_date_context": "2026-05-10T00:00:00Z",
            "collection_or_source_context": cfg["label"],
            "event_or_mention_context": "candidate-only metadata context",
        },
    }
    identifier = _mapping(request_shape.get("identifier"))
    endpoint_class = str(request_detail.get("endpoint_or_metadata_class") or cfg["endpoint_or_metadata_class"])
    request = {
        "schema_version": "h6_web_archive_live_probe_request.v0",
        "live_probe_request_id": f"h6.web_archive_live_probe_request.{source_id}.{_slug(request_key)}.v0",
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "source_record_kind": cfg["source_record_kind"],
        "operation_scope": "metadata_only",
        "endpoint_or_metadata_class": endpoint_class,
        "request_shape": request_shape,
        "approved_request_key": request_key,
        "original_url_or_identifier": str(identifier.get("original_url_or_identifier") or f"fixture:h6:{source_id}:metadata-only"),
        "timestamp_or_date_context": str(identifier.get("timestamp_or_date_context") or "2026-05-10T00:00:00Z"),
        "collection_or_source_context": str(identifier.get("collection_or_source_context") or cfg["label"]),
        "event_or_mention_context": str(identifier.get("event_or_mention_context") or "candidate-only metadata context"),
        "approval_refs": [POLICY_PATHS["allowed_requests"]],
        "policy_refs": list(POLICY_PATHS.values()),
        "live_requested": bool(live_requested),
        "dry_run_only": not bool(live_requested),
        "cdx_query_requested": False,
        "memento_lookup_requested": False,
        "warc_wacz_fetch_requested": False,
        "archived_page_fetch_requested": False,
        "live_page_fetch_requested": False,
        "media_download_requested": False,
        "transcript_download_requested": False,
        "public_document_fetch_requested": False,
        "scraping_or_crawling_requested": False,
        "restricted_sensitive_source_requested": False,
        "bypass_or_automation_requested": False,
        "output_policy_ref": POLICY_PATHS["output_policy"],
        "review_policy_ref": POLICY_PATHS["review_policy"],
        "truth_policy_ref": POLICY_PATHS["truth_policy"],
        "product_boundary": _product_boundary(),
        "truth_boundary": _truth_boundary(),
        "limitations": ["Request envelope does not grant live access, fetching, crawling, or truth acceptance."],
        "notes": ["H6 live probes fail closed unless committed source policy approves this exact metadata-only request."],
    }
    _raise_on_boundary_errors(request)
    return request


def validate_h6_web_archive_live_probe_request(request: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    source_id = str(request.get("source_id") or "")
    request_key = str(request.get("approved_request_key") or "")
    endpoint_class = str(request.get("endpoint_or_metadata_class") or "")
    if source_id not in H6_SOURCE_IDS:
        reasons.append(f"source is not in H6 allowlist: {source_id}")
        return {"approved": False, "blocked_reasons": reasons, "result_status": "blocked_by_policy"}
    if request.get("operation_scope") != "metadata_only":
        reasons.append("approved_operation_scope must be metadata_only")
    for key in (
        "warc_wacz_fetch_requested",
        "archived_page_fetch_requested",
        "live_page_fetch_requested",
        "media_download_requested",
        "transcript_download_requested",
        "public_document_fetch_requested",
    ):
        if request.get(key) is True:
            reasons.append(f"{key} must be false")
    if request.get("scraping_or_crawling_requested") is True:
        reasons.append("scraping_or_crawling_requested must be false")
    if request.get("restricted_sensitive_source_requested") is True:
        reasons.append("restricted_sensitive_source_requested must be false")
    if request.get("bypass_or_automation_requested") is True:
        reasons.append("bypass_or_automation_requested must be false")
    source = _source_policy(source_id, policy_bundle)
    endpoint = _source_policy(source_id, policy_bundle, "endpoint_policy")
    rate = _source_policy(source_id, policy_bundle, "rate_limit_policy")
    cache = _source_policy(source_id, policy_bundle, "cache_policy")
    kill = _source_policy(source_id, policy_bundle, "kill_switch_policy")
    for key in ("live_access_approved", "metadata_probe_approved"):
        if source.get(key) is not True:
            reasons.append(f"allowed_requests.{source_id}.{key} must be true")
    for key in (
        "source_sync_approved",
        "warc_wacz_fetch_approved",
        "archived_page_fetch_approved",
        "live_page_fetch_approved",
        "media_download_approved",
        "transcript_download_approved",
        "newspaper_page_download_approved",
        "public_document_fetch_approved",
        "restricted_sensitive_source_approved",
        "scraping_approved",
        "crawling_approved",
        "browser_automation_approved",
        "bypass_or_access_control_automation_approved",
        "public_query_fanout_approved",
    ):
        if source.get(key) is not False:
            reasons.append(f"allowed_requests.{source_id}.{key} must be false")
    if request.get("cdx_query_requested") is True and source.get("cdx_query_approved") is not True:
        reasons.append("cdx_query_requested must be false unless exact bounded metadata policy approves it")
    if request.get("memento_lookup_requested") is True and source.get("memento_lookup_approved") is not True:
        reasons.append("memento_lookup_requested must be false unless exact bounded metadata policy approves it")
    if source.get("cdx_query_approved") is not False and request.get("cdx_query_requested") is not True:
        reasons.append("cdx_query_approved must stay false unless exact bounded request is used")
    if source.get("memento_lookup_approved") is not False and request.get("memento_lookup_requested") is not True:
        reasons.append("memento_lookup_approved must stay false unless exact bounded request is used")
    if source.get("approved_operation_scope") != "metadata_only":
        reasons.append("approved_operation_scope must be metadata_only")
    if source.get("approved_source_id") != source_id:
        reasons.append("approved_source_id must match requested source")
    if request_key not in list(source.get("allowed_request_keys") or []):
        reasons.append(f"request key is not approved for live use: {request_key}")
    if request_key not in _mapping(source.get("requests")):
        reasons.append(f"request key is not present in request manifest: {request_key}")
    allowlisted = list(endpoint.get("allowlisted_endpoint_or_metadata_classes_current") or [])
    if endpoint_class not in allowlisted:
        reasons.append(f"endpoint/metadata class is not currently allowlisted: {endpoint_class}")
    forbidden_classes = list(endpoint.get("forbidden_endpoint_or_metadata_classes_current") or [])
    forbidden_terms = ("fetch", "download", "payload", "scrap", "crawl", "browser", "bypass", "direct_fetch")
    if endpoint_class in forbidden_classes or any(term in endpoint_class.casefold() and "metadata" not in endpoint_class.casefold() for term in forbidden_terms):
        reasons.append(f"endpoint/metadata class is forbidden: {endpoint_class}")
    for key in (
        "warc_wacz_fetch_allowed",
        "archived_page_fetch_allowed",
        "live_page_fetch_allowed",
        "media_download_allowed",
        "public_document_fetch_allowed",
        "scraping_allowed",
        "crawling_allowed",
        "browser_automation_allowed",
        "sensitive_source_access_allowed",
    ):
        if endpoint.get(key) is not False:
            reasons.append(f"endpoint policy {key} must be false")
    if rate.get("decision_status") != "approved_for_bounded_metadata_probe":
        reasons.append("rate limit policy is not approved for bounded metadata probe")
    if int(rate.get("max_requests_per_run") or 0) < 1:
        reasons.append("request budget must allow at least one request")
    if not rate.get("timeout_seconds"):
        reasons.append("timeout_seconds must be set")
    if not isinstance(rate.get("retry_policy"), Mapping):
        reasons.append("retry_policy must be set")
    if "approved" not in str(rate.get("user_agent_contact_posture") or "not_approved"):
        reasons.append("User-Agent/contact posture must be approved or documented")
    if "approved" not in str(rate.get("auth_posture") or "not_approved"):
        reasons.append("auth/no-auth posture must be approved")
    if cache.get("decision_status") != "approved_for_bounded_metadata_probe":
        reasons.append("cache/no-cache decision is not approved")
    if kill.get("decision_status") != "approved_for_bounded_metadata_probe":
        reasons.append("kill switch policy is not approved")
    if kill.get("default_enabled") is not True or kill.get("live_probe_kill_switch_engaged") is True:
        reasons.append("kill switch blocks live probe")
    return {"approved": not reasons, "blocked_reasons": reasons, "result_status": _status_for_reasons(reasons)}


def validate_h6_source_approval(source_id: str, request_key: str, policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    request = build_h6_web_archive_live_probe_request(source_id, request_key, policy_bundle, live_requested=True)
    return validate_h6_web_archive_live_probe_request(request, policy_bundle)


def build_h6_web_archive_live_probe_blocked_result(request: Mapping[str, Any], reason: str | list[str], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    reasons = [reason] if isinstance(reason, str) else list(reason)
    source_id = str(request.get("source_id") or "unknown")
    cfg = SOURCE_CONFIGS.get(source_id, {})
    status = _status_for_reasons(reasons)
    result_stub = {
        "schema_version": "h6_web_archive_live_probe_result.v0",
        "source_id": source_id,
        "connector_family": str(cfg.get("connector_family") or request.get("connector_family") or "unknown"),
        "result_status": status,
        "request_count": 0,
        "network_used": False,
        "blocked_reasons": reasons,
        "warnings": [],
        "source_limitations": ["Live probe blocked before network use."],
    }
    health = build_h6_connector_health_summary(result_stub, policy_bundle)
    result = {
        "schema_version": "h6_web_archive_live_probe_result.v0",
        "live_probe_result_id": f"h6.web_archive_live_probe_result.{source_id}.blocked.v0",
        "live_probe_request_ref": request.get("live_probe_request_id"),
        "source_id": source_id,
        "connector_family": result_stub["connector_family"],
        "source_record_kind": str(cfg.get("source_record_kind") or request.get("source_record_kind") or "unknown"),
        "result_status": status,
        "request_count": 0,
        "network_used": False,
        "endpoint_or_metadata_used": request.get("endpoint_or_metadata_class"),
        "response_status_code": None,
        "response_fingerprint": None,
        "response_summary": "No external request was made.",
        "normalized_record": {},
        "web_capture_identity_candidate": _blocked_candidate(),
        "archived_url_time_state_candidate": _blocked_candidate(),
        "news_event_mention_candidate": _blocked_candidate(),
        "dead_link_trace_candidate": _blocked_candidate(),
        "public_document_trace_candidate": _blocked_candidate(),
        "media_transcript_metadata_candidate": _blocked_candidate(),
        "source_cache_candidate_preview": _blocked_candidate(),
        "evidence_candidate_preview": _blocked_candidate(),
        "review_queue_seed_preview": {"status": "not_created_blocked_by_policy", "review_seed_is_review_decision": False, "truth_boundary": _truth_boundary(), "product_boundary": _product_boundary()},
        "connector_health_summary": health,
        "blocked_reason": reasons[0] if reasons else "blocked by policy",
        "blocked_reasons": reasons,
        "warnings": [],
        "limitations": ["Blocked preflight output only; no WARC/WACZ fetch, page fetch, media download, scraping, crawling, bypass, sensitive-source access, or truth acceptance occurred."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Blocked result is candidate/preflight output only."],
    }
    _raise_on_boundary_errors(result)
    return result


def build_h6_web_archive_live_probe_result(source_id: str, response_payload: Mapping[str, Any], response_metadata: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    cfg = SOURCE_CONFIGS[source_id]
    normalized = normalize_h6_web_archive_live_probe_result({"source_id": source_id, "response_payload": dict(response_payload), "response_metadata": dict(response_metadata)}, policy_bundle)
    capture = build_h6_web_capture_identity_candidate_from_probe(normalized, policy_bundle)
    time_state = build_h6_archived_url_time_state_candidate_from_probe(normalized, policy_bundle)
    event = build_h6_news_event_mention_candidate_from_probe(normalized, policy_bundle)
    dead_link = build_h6_dead_link_trace_candidate_from_probe(normalized, policy_bundle)
    public_document = build_h6_public_document_trace_candidate_from_probe(normalized, policy_bundle)
    media = build_h6_media_transcript_metadata_candidate_from_probe(normalized, policy_bundle)
    source_cache = build_h6_source_cache_candidate_preview_from_probe(normalized, policy_bundle)
    evidence = build_h6_evidence_candidate_preview_from_probe(normalized, policy_bundle)
    result_stub = {
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "result_status": "live_probe_completed",
        "request_count": int(response_metadata.get("request_count") or 1),
        "network_used": bool(response_metadata.get("network_used", True)),
        "blocked_reasons": [],
        "warnings": [],
    }
    review_seed = build_h6_review_queue_seed_preview_from_probe(result_stub, source_cache, evidence, policy_bundle)
    result = {
        "schema_version": "h6_web_archive_live_probe_result.v0",
        "live_probe_result_id": f"h6.web_archive_live_probe_result.{source_id}.{_slug(str(response_metadata.get('request_key') or cfg['request_key']))}.v0",
        "live_probe_request_ref": response_metadata.get("live_probe_request_ref"),
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "source_record_kind": cfg["source_record_kind"],
        "result_status": "live_probe_completed",
        "request_count": int(response_metadata.get("request_count") or 1),
        "network_used": bool(response_metadata.get("network_used", True)),
        "endpoint_or_metadata_used": response_metadata.get("endpoint_or_metadata_used") or cfg["endpoint_or_metadata_class"],
        "response_status_code": response_metadata.get("response_status_code"),
        "response_fingerprint": _fingerprint(response_payload),
        "response_summary": "Bounded metadata response normalized from approved live-probe payload.",
        "normalized_record": normalized,
        "web_capture_identity_candidate": capture,
        "archived_url_time_state_candidate": time_state,
        "news_event_mention_candidate": event,
        "dead_link_trace_candidate": dead_link,
        "public_document_trace_candidate": public_document,
        "media_transcript_metadata_candidate": media,
        "source_cache_candidate_preview": source_cache,
        "evidence_candidate_preview": evidence,
        "review_queue_seed_preview": review_seed,
        "connector_health_summary": build_h6_connector_health_summary(result_stub, policy_bundle),
        "blocked_reason": None,
        "blocked_reasons": [],
        "warnings": [],
        "limitations": ["Live metadata result is not capture completeness, historical truth, event truth, article truth, public-document truth, authenticity, rights, privacy, safety, or production coverage proof."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Network metadata observation remains candidate-only pending review."],
    }
    _raise_on_boundary_errors(result)
    return result


def normalize_h6_web_archive_live_probe_result(result: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    source_id = str(result.get("source_id") or "")
    payload = _mapping(result.get("response_payload"))
    cfg = SOURCE_CONFIGS[source_id]
    fixture_payload = _metadata_payload_defaults(source_id, payload)
    fixture = {
        "schema_version": "h6_web_archive_fixture.v0",
        "fixture_id": f"h6.live_probe_synthetic_fixture.{source_id}.v0",
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "fixture_kind": "live_probe_metadata_response",
        "fixture_status": "synthetic_probe_response",
        "fixture_public_safe": True,
        "live_call_used": False,
        "network_used": False,
        "external_api_used": False,
        "cdx_payload_included": False,
        "memento_payload_included": False,
        "warc_wacz_payload_included": False,
        "archived_page_payload_included": False,
        "live_page_payload_included": False,
        "media_payload_included": False,
        "transcript_payload_included": False,
        "newspaper_page_payload_included": False,
        "public_document_payload_included": False,
        "scraping_output_included": False,
        "crawling_output_included": False,
        "restricted_sensitive_source_accessed": False,
        "bypass_or_automation_used": False,
        "fixture_payload": fixture_payload,
        "expected_normalized_ref": None,
        "limitations": ["Constructed from bounded live-probe metadata response; not accepted truth."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Synthetic fixture envelope exists only to reuse fixture normalizer boundaries."],
    }
    return normalize_h6_web_archive_fixture(fixture, source_id, policy_bundle)


def build_h6_web_capture_identity_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_capture_candidate(normalized_record, policy_bundle)


def build_h6_archived_url_time_state_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_time_state_candidate(normalized_record, policy_bundle)


def build_h6_news_event_mention_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _first(_fixture_event_candidates(normalized_record, policy_bundle))


def build_h6_dead_link_trace_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _first(_fixture_dead_link_candidates(normalized_record, policy_bundle))


def build_h6_public_document_trace_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _first(_fixture_public_document_candidates(normalized_record, policy_bundle))


def build_h6_media_transcript_metadata_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _first(_fixture_media_candidates(normalized_record, policy_bundle))


def build_h6_source_cache_candidate_preview_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_source_cache_preview(normalized_record, policy_bundle)


def build_h6_evidence_candidate_preview_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_evidence_preview(normalized_record, policy_bundle)


def build_h6_review_queue_seed_preview_from_probe(result: Mapping[str, Any], source_cache_preview: Mapping[str, Any], evidence_preview: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    seed = {
        "schema_version": "h6_web_archive_live_probe_review_seed.v0",
        "review_seed_id": f"h6.review_seed.{result.get('source_id')}.{_slug(str(result.get('result_status') or 'probe'))}.v0",
        "source_id": result.get("source_id"),
        "seed_status": "preview_only",
        "source_cache_candidate_ref": source_cache_preview.get("source_cache_candidate_id"),
        "evidence_candidate_preview_ref": evidence_preview.get("evidence_candidate_preview_id"),
        "review_required": True,
        "review_seed_is_review_decision": False,
        "accepted_candidate_truth": False,
        "accepted_evidence_truth": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(seed)
    return seed


def build_h6_connector_health_summary(result: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    source_id = str(result.get("source_id") or "unknown")
    cfg = SOURCE_CONFIGS.get(source_id, {})
    health = {
        "schema_version": "h6_web_archive_connector_health_summary.v0",
        "health_summary_id": f"h6.web_archive_connector_health.{source_id}.{_slug(str(result.get('result_status') or 'unknown'))}.v0",
        "source_id": source_id,
        "connector_family": str(result.get("connector_family") or cfg.get("connector_family") or "unknown"),
        "live_probe_status": str(result.get("result_status") or "not_evaluable"),
        "request_count": int(result.get("request_count") or 0),
        "response_status_summary": "metadata_observed" if result.get("network_used") is True else "no_network_call",
        "policy_blockers": list(result.get("blocked_reasons") or ([] if not result.get("blocked_reason") else [result.get("blocked_reason")])),
        "warnings": list(result.get("warnings") or []),
        "source_limitations": list(result.get("source_limitations") or result.get("limitations") or []),
        "sensitive_source_status": "blocked_by_default" if source_id == "restricted_public_document_manifest" else "not_sensitive_or_public_safe_metadata_only",
        "next_recommended_action": "review_fixture_or_probe_output_before_any_promotion",
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(health)
    return health


def build_h6_web_archive_live_probe_output_bundle(result: Mapping[str, Any]) -> dict[str, Any]:
    bundle = {
        "schema_version": "h6_web_archive_live_probe_output_bundle.v0",
        "bundle_id": f"h6.live_probe_output_bundle.{result.get('source_id')}.{_slug(str(result.get('result_status') or 'unknown'))}.v0",
        "live_probe_result": dict(result),
        "normalized_record": result.get("normalized_record", {}),
        "web_capture_identity_candidate": result.get("web_capture_identity_candidate", {}),
        "archived_url_time_state_candidate": result.get("archived_url_time_state_candidate", {}),
        "news_event_mention_candidate": result.get("news_event_mention_candidate", {}),
        "dead_link_trace_candidate": result.get("dead_link_trace_candidate", {}),
        "public_document_trace_candidate": result.get("public_document_trace_candidate", {}),
        "media_transcript_metadata_candidate": result.get("media_transcript_metadata_candidate", {}),
        "source_cache_candidate_preview": result.get("source_cache_candidate_preview", {}),
        "evidence_candidate_preview": result.get("evidence_candidate_preview", {}),
        "review_queue_seed_preview": result.get("review_queue_seed_preview", {}),
        "connector_health_summary": result.get("connector_health_summary", {}),
        "validation_summary": {
            "truth_boundary_violations": detect_h6_web_archive_live_probe_truth_boundary_violations(result, {}),
            "product_boundary_violations": detect_h6_web_archive_live_probe_product_boundary_violations(result, {}),
        },
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(bundle)
    return bundle


def fetch_h6_web_archive_metadata_once(request: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    validation = validate_h6_web_archive_live_probe_request(request, policy_bundle)
    if not validation["approved"]:
        raise H6WebArchiveLiveProbeBlocked(build_h6_web_archive_live_probe_blocked_result(request, validation["blocked_reasons"], policy_bundle))
    source_id = str(request["source_id"])
    cfg = SOURCE_CONFIGS[source_id]
    url = ENDPOINT_URL_TEMPLATES[source_id].format(source_id=source_id, request_key=request["approved_request_key"], metadata_class=request["endpoint_or_metadata_class"])
    timeout = int(_source_policy(source_id, policy_bundle, "rate_limit_policy").get("timeout_seconds") or 10)
    started = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": "Eureka-H6-Metadata-Probe/0 blocked-by-default"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read(16384)
            status = getattr(response, "status", None)
    except urllib.error.URLError as exc:
        payload = _metadata_payload_defaults(source_id, {"source_metadata": {"url_error": str(exc)}})
        metadata = {"network_used": True, "request_count": 1, "response_status_code": None, "elapsed_seconds": round(time.time() - started, 3), "request_key": request["approved_request_key"], "endpoint_or_metadata_used": request["endpoint_or_metadata_class"]}
        return payload, metadata
    try:
        payload = json.loads(body.decode("utf-8"))
        if not isinstance(payload, Mapping):
            payload = {"response_summary": str(payload)}
    except Exception:
        payload = {"response_summary": body[:512].decode("utf-8", errors="replace")}
    metadata = {"network_used": True, "request_count": 1, "response_status_code": status, "elapsed_seconds": round(time.time() - started, 3), "request_key": request["approved_request_key"], "endpoint_or_metadata_used": request["endpoint_or_metadata_class"]}
    return dict(payload), metadata


def summarize_h6_web_archive_live_probe_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": result.get("source_id"),
        "result_status": result.get("result_status"),
        "request_count": int(result.get("request_count") or 0),
        "network_used": bool(result.get("network_used")),
        "blocked_reasons": list(result.get("blocked_reasons") or ([] if not result.get("blocked_reason") else [result.get("blocked_reason")])),
        "web_capture_candidate_present": _present(result.get("web_capture_identity_candidate")),
        "time_state_candidate_present": _present(result.get("archived_url_time_state_candidate")),
        "news_event_candidate_present": _present(result.get("news_event_mention_candidate")),
        "dead_link_candidate_present": _present(result.get("dead_link_trace_candidate")),
        "public_document_candidate_present": _present(result.get("public_document_trace_candidate")),
        "media_candidate_present": _present(result.get("media_transcript_metadata_candidate")),
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def detect_h6_web_archive_live_probe_truth_boundary_violations(result: Mapping[str, Any], policy_bundle: Mapping[str, Any] | None = None) -> list[str]:
    return _dedupe(_detect_true_keys(result, FORBIDDEN_TRUTH_TRUE_KEYS, "truth") + _fixture_truth_violations(result))


def detect_h6_web_archive_live_probe_product_boundary_violations(result: Mapping[str, Any], policy_bundle: Mapping[str, Any] | None = None) -> list[str]:
    return _dedupe(_detect_true_keys(result, FORBIDDEN_PRODUCT_TRUE_KEYS, "product") + _fixture_product_violations(result))


def build_metadata_request(source_id: str, request: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    cfg = SOURCE_CONFIGS[source_id]
    return {
        "source_id": source_id,
        "request_key": request.get("approved_request_key"),
        "endpoint_or_metadata_class": request.get("endpoint_or_metadata_class") or cfg["endpoint_or_metadata_class"],
        "request_shape": request.get("request_shape", {}),
        "url_template": ENDPOINT_URL_TEMPLATES[source_id],
        "metadata_only": True,
        "warc_wacz_fetch_allowed": False,
        "archived_page_fetch_allowed": False,
        "media_download_allowed": False,
        "scraping_crawling_allowed": False,
    }


def parse_metadata_response(source_id: str, response_payload: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _metadata_payload_defaults(source_id, response_payload)


def _metadata_payload_defaults(source_id: str, response_payload: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(response_payload)
    cfg = SOURCE_CONFIGS[source_id]
    payload.setdefault("source_record_kind", cfg["source_record_kind"])
    payload.setdefault("source_native_id", f"{source_id}-metadata-candidate")
    payload.setdefault("metadata_summary", f"Metadata-only observation candidate for {cfg['label']}.")
    payload.setdefault("source_archive_ref", cfg["label"])
    if cfg.get("has_capture"):
        payload.setdefault("original_url", f"https://example.invalid/h6/{source_id}/resource")
        payload.setdefault("normalized_url_candidate", f"https://example.invalid/h6/{source_id}/resource")
        payload.setdefault("capture_url", f"fixture:h6:{source_id}:capture-metadata")
        payload.setdefault("capture_timestamp", "20260510000000")
        payload.setdefault("memento_datetime", "Sun, 10 May 2026 00:00:00 GMT")
        payload.setdefault("capture_status_code", "200")
        payload.setdefault("capture_mime_type", "text/html")
        payload.setdefault("capture_digest", "sha256:candidate-only-not-authenticity-proof")
        payload.setdefault("capture_length", "0")
        payload.setdefault("warc_record_id_candidate", f"fixture-h6-{source_id}-record")
        payload.setdefault("warc_filename_candidate", "not-fetched-current")
        payload.setdefault("cdx_key_candidate", f"example.invalid/h6/{source_id}/resource")
    if cfg.get("has_time_state"):
        payload.setdefault("requested_time", "2026-05-10T00:00:00Z")
        payload.setdefault("nearest_capture", "candidate-only-nearest-capture")
        payload.setdefault("first_seen_candidate", "unknown")
        payload.setdefault("last_seen_candidate", "unknown")
        payload.setdefault("status_at_time_candidate", "candidate_only")
        payload.setdefault("redirect_state_candidate", "unknown")
        payload.setdefault("missing_capture_candidate", "not_evaluated")
        payload.setdefault("gap_period_candidate", "not_evaluated")
        payload.setdefault("source_disappearance_candidate", "not_evaluated")
        payload.setdefault("resurrected_source_candidate", "not_evaluated")
        payload.setdefault("archived_download_page_candidate", "download_permission_not_granted")
    if cfg.get("has_event"):
        payload.setdefault("article_or_record_id", f"{source_id}-record-candidate")
        payload.setdefault("headline_or_title", f"{cfg['label']} metadata candidate")
        payload.setdefault("publication_or_program", cfg["label"])
        payload.setdefault("publication_date", "2026-05-10")
        payload.setdefault("byline_or_actor", "unknown")
        payload.setdefault("event_date_candidate", "2026-05-10")
        payload.setdefault("event_location_candidate", "unknown")
        payload.setdefault("mentioned_entity", "Eureka fixture entity")
        payload.setdefault("mentioned_url", f"fixture:h6:{source_id}:mentioned-url")
        payload.setdefault("mentioned_software_or_artifact", "candidate-only artifact mention")
        payload.setdefault("topic_or_theme", "trace metadata")
        payload.setdefault("snippet_or_summary", "Metadata-only mention candidate; not event truth.")
        payload.setdefault("source_locator", f"fixture:h6:{source_id}:record")
    if cfg.get("has_dead_link"):
        payload.setdefault("dead_url_candidate", f"https://example.invalid/h6/{source_id}/dead")
        payload.setdefault("last_live_candidate", "unknown")
        payload.setdefault("first_dead_candidate", "unknown")
        payload.setdefault("archived_snapshot_candidate", f"fixture:h6:{source_id}:snapshot")
        payload.setdefault("referring_page_candidate", f"fixture:h6:{source_id}:referrer")
        payload.setdefault("old_download_page_candidate", "download_permission_not_granted")
        payload.setdefault("mirror_candidate", "not_authenticity_proof")
        payload.setdefault("checksum_candidate", "not_malware_safety")
        payload.setdefault("product_or_artifact_ref", "candidate-only trace")
        payload.setdefault("vendor_or_source_ref", cfg["label"])
        payload.setdefault("disappearance_reason_candidate", "unknown")
        payload.setdefault("followup_workunit_candidate", "review_required")
    if cfg.get("has_public_document"):
        payload.setdefault("public_document_ref", f"fixture:h6:{source_id}:manifest-only")
        payload.setdefault("document_collection_ref", "restricted_public_document_manifest")
        payload.setdefault("document_record_id", f"{source_id}-manifest-record")
        payload.setdefault("document_title", "Policy-blocked manifest-only public document trace")
        payload.setdefault("publication_or_disclosure_date", "unknown")
        payload.setdefault("source_locator", f"fixture:h6:{source_id}:manifest")
        payload.setdefault("source_risk_class", "restricted_sensitive_review_required")
        payload.setdefault("sensitivity_class", "policy_blocked")
        payload.setdefault("rights_or_access_uncertainty", "review_required")
        payload.setdefault("restricted_source_policy", "manifest_only_no_direct_fetch")
    if cfg.get("has_media"):
        payload.setdefault("media_or_transcript_ref", f"fixture:h6:{source_id}:media-metadata")
        payload.setdefault("media_or_program_id", f"{source_id}-media-candidate")
        payload.setdefault("media_title", f"{cfg['label']} media metadata candidate")
        payload.setdefault("media_date", "2026-05-10")
        payload.setdefault("transcript_or_caption_ref", "transcript_payload_not_available_current")
        payload.setdefault("media_ref", "media_payload_not_available_current")
        payload.setdefault("speaker_or_actor_candidate", "unknown")
        payload.setdefault("topic_or_subject_candidate", "trace metadata")
    metadata = _mapping(payload.get("source_metadata"))
    metadata.setdefault("live_probe_metadata_only", True)
    metadata.setdefault("response_fingerprint", _fingerprint(payload))
    payload["source_metadata"] = metadata
    return payload


def _source_policy(source_id: str, policy_bundle: Mapping[str, Any], bundle_key: str = "allowed_requests") -> dict[str, Any]:
    sources = _mapping(policy_bundle.get(bundle_key)).get("sources", [])
    for item in sources:
        if isinstance(item, Mapping) and item.get("source_id") == source_id:
            return dict(item)
    return {}


def _request_detail(source_policy: Mapping[str, Any], request_key: str) -> dict[str, Any]:
    request_map = _mapping(source_policy.get("requests"))
    detail = request_map.get(request_key)
    return dict(detail) if isinstance(detail, Mapping) else {}


def _status_for_reasons(reasons: list[str]) -> str:
    joined = " ".join(reasons).casefold()
    if not reasons:
        return "dry_run_preflight_pass"
    if "approved" in joined or "approval" in joined:
        return "blocked_by_missing_approval"
    if "kill switch" in joined:
        return "blocked_by_kill_switch"
    if "endpoint" in joined:
        return "blocked_by_fetch_policy" if any(word in joined for word in ("fetch", "download", "payload")) else "blocked_by_endpoint_policy"
    if any(word in joined for word in ("warc", "wacz", "fetch", "download", "page", "media", "transcript", "document")):
        return "blocked_by_fetch_policy"
    if any(word in joined for word in ("scraping", "crawl", "browser")):
        return "blocked_by_crawl_policy"
    if "sensitive" in joined or "restricted" in joined:
        return "blocked_by_sensitive_source_policy"
    if "bypass" in joined or "automation" in joined or "access control" in joined:
        return "blocked_by_bypass_policy"
    return "blocked_by_policy"


def _blocked_candidate() -> dict[str, Any]:
    return {"status": "not_created_blocked_by_policy", "truth_boundary": _truth_boundary(), "product_boundary": _product_boundary()}


def _first(items: list[dict[str, Any]]) -> dict[str, Any]:
    return dict(items[0]) if items else {}


def _present(value: Any) -> bool:
    return isinstance(value, Mapping) and value.get("status") != "not_created_blocked_by_policy" and bool(value)


def _fingerprint(payload: Mapping[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(body).hexdigest()


def _truth_boundary() -> dict[str, bool]:
    return {'live_probe_result_is_public_truth': False, 'normalized_record_is_public_truth': False, 'accepted_web_capture_truth': False, 'accepted_time_state_truth': False, 'accepted_event_truth': False, 'accepted_article_truth': False, 'accepted_public_document_truth': False, 'accepted_source_truth': False, 'accepted_evidence_truth': False, 'accepted_candidate_truth': False, 'accepted_public_record': False, 'web_capture_candidate_is_truth': False, 'archived_time_state_candidate_is_truth': False, 'time_state_candidate_is_historical_truth': False, 'news_event_mention_candidate_is_event_truth': False, 'dead_link_trace_grants_acquisition_permission': False, 'public_document_trace_is_public_truth': False, 'media_transcript_metadata_is_full_context': False, 'capture_digest_proves_authenticity': False, 'archived_content_proves_rights_clearance': False, 'source_cache_candidate_is_accepted_source': False, 'source_cache_preview_is_accepted_source': False, 'evidence_candidate_preview_is_accepted_evidence': False, 'review_seed_is_review_decision': False, 'public_index_mutated': False, 'master_index_mutated': False, 'rights_clearance_claimed': False, 'privacy_safety_claimed': False, 'malware_safety_claimed': False, 'verified_authenticity_claimed': False, 'production_readiness_claimed': False}


def _product_boundary() -> dict[str, bool]:
    return {'changed_public_search_behavior': False, 'enabled_hosting': False, 'enabled_live_probes': False, 'enabled_source_sync': False, 'enabled_fetching': False, 'enabled_crawling': False, 'enabled_downloads': False, 'enabled_uploads': False, 'enabled_accounts': False, 'enabled_telemetry': False, 'enabled_scraping': False, 'enabled_browser_automation': False, 'restricted_sensitive_source_access_used': False, 'mutated_public_index': False, 'mutated_master_index': False}


def _mapping(value: Any) -> dict[str, Any]:
    if value is None or not isinstance(value, Mapping):
        return {}
    return dict(value)


def _slug(value: str) -> str:
    safe = "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")
    safe = "-".join(part for part in safe.split("-") if part)
    return safe[:64] if safe else hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


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


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            out.append(item)
            seen.add(item)
    return out


def _raise_on_boundary_errors(record: Mapping[str, Any]) -> None:
    errors = detect_h6_web_archive_live_probe_truth_boundary_violations(record) + detect_h6_web_archive_live_probe_product_boundary_violations(record)
    if errors:
        raise ValueError("; ".join(errors))

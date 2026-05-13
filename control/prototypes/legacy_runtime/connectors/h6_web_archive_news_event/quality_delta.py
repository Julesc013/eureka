"""Offline H6 web archive/news/event quality delta helpers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

from control.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.normalizer_common import H6_SOURCE_IDS
from control.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.review_integration import (
    detect_h6_review_product_boundary_violations,
    detect_h6_review_truth_boundary_violations,
)


FORBIDDEN_TRUE_KEYS = {
    "archived_time_state_verified",
    "article_truth_verified",
    "automatic_future_connector_approval",
    "capture_completeness_verified",
    "event_truth_verified",
    "exhaustive_global_coverage",
    "future_connector_auto_approval",
    "malware_safety",
    "malware_safety_claimed",
    "privacy_safety",
    "privacy_safety_claimed",
    "production_readiness_claimed",
    "production_search_quality",
    "production_web_archive_coverage",
    "public_document_truth_verified",
    "rights_clearance",
    "rights_clearance_claimed",
    "source_authenticity_verified",
    "verified_authenticity_claimed",
}


def build_h6_quality_delta(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    review = dict(inputs.get("review_integration_result") or inputs)
    sources = list(review.get("sources") or [])
    blocked_sources = list(review.get("blocked_sources") or [])
    fixture_outputs = list(review.get("used_fixture_outputs") or [])
    live_outputs = list(review.get("used_live_probe_outputs") or [])
    known_gaps = _known_gaps(review)
    metrics = {
        "source_count": len(sources) or len(H6_SOURCE_IDS),
        "fixture_sources_count": len({item.get("source_id") for item in fixture_outputs if item.get("source_id")}) or len(sources),
        "live_probe_sources_count": len({item.get("source_id") for item in live_outputs if item.get("status") == "live_probe_completed"}),
        "blocked_sources_count": len(blocked_sources),
        "normalized_record_count": len(review.get("source_cache_review_seeds", [])),
        "web_capture_identity_candidate_count": len(review.get("web_capture_identity_review_seeds", [])),
        "archived_url_time_state_candidate_count": len(review.get("archived_url_time_state_review_seeds", [])),
        "news_event_mention_candidate_count": len(review.get("news_event_mention_review_seeds", [])),
        "dead_link_trace_candidate_count": len(review.get("dead_link_trace_review_seeds", [])),
        "public_document_trace_candidate_count": len(review.get("public_document_trace_review_seeds", [])),
        "media_transcript_metadata_candidate_count": len(review.get("media_transcript_metadata_review_seeds", [])),
        "source_cache_candidate_count": len(review.get("source_cache_review_seeds", [])),
        "evidence_candidate_preview_count": len(review.get("evidence_candidate_review_seeds", [])),
        "review_seed_count": sum(len(review.get(key, [])) for key in (
            "web_capture_identity_review_seeds",
            "archived_url_time_state_review_seeds",
            "news_event_mention_review_seeds",
            "dead_link_trace_review_seeds",
            "public_document_trace_review_seeds",
            "media_transcript_metadata_review_seeds",
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
        "schema_version": "h6_web_archive_quality_delta_report.v0",
        "quality_delta_id": f"h6.quality_delta.{_digest(review)[:12]}.v0",
        "wave_id": "H6",
        "comparison_scope": "fixture_review_and_blocked_live_probe_evidence",
        **metrics,
        "per_source_deltas": [_per_source_delta(source_id, review, fixture_outputs, live_outputs, blocked_sources) for source_id in sorted(set(sources) or set(H6_SOURCE_IDS))],
        "limitations": [
            "Quality delta measures H6 review readiness only.",
            "Blocked live probes do not prove endpoint behavior.",
            "Web archive/news/event metadata is not capture completeness, event truth, article truth, public-document truth, source authenticity, rights, privacy, malware, or production coverage proof.",
        ],
        "forbidden_claims": [
            "production_search_quality",
            "production_web_archive_coverage",
            "exhaustive_global_coverage",
            "capture_completeness_verified",
            "archived_time_state_verified",
            "event_truth_verified",
            "article_truth_verified",
            "public_document_truth_verified",
            "rights_clearance",
            "privacy_safety",
            "malware_safety",
            "source_authenticity_verified",
            "automatic_future_connector_approval",
        ],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H6 quality delta is operational review evidence only."],
    }
    errors = detect_h6_quality_overclaim(delta, policy)
    if errors:
        raise ValueError("; ".join(errors))
    return delta


def summarize_h6_quality_delta(delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    errors = detect_h6_quality_overclaim(delta, policy)
    return {
        "schema_version": "h6_quality_delta_summary.v0",
        "status": "pass" if not errors else "invalid",
        "quality_delta_id": delta.get("quality_delta_id"),
        "source_count": delta.get("source_count", 0),
        "fixture_sources_count": delta.get("fixture_sources_count", 0),
        "live_probe_sources_count": delta.get("live_probe_sources_count", 0),
        "blocked_sources_count": delta.get("blocked_sources_count", 0),
        "web_capture_identity_candidate_count": delta.get("web_capture_identity_candidate_count", 0),
        "archived_url_time_state_candidate_count": delta.get("archived_url_time_state_candidate_count", 0),
        "news_event_mention_candidate_count": delta.get("news_event_mention_candidate_count", 0),
        "dead_link_trace_candidate_count": delta.get("dead_link_trace_candidate_count", 0),
        "public_document_trace_candidate_count": delta.get("public_document_trace_candidate_count", 0),
        "media_transcript_metadata_candidate_count": delta.get("media_transcript_metadata_candidate_count", 0),
        "review_seed_count": delta.get("review_seed_count", 0),
        "known_gap_count": delta.get("known_gap_count", 0),
        "blocker_count": delta.get("blocker_count", 0),
        "claims_capture_completeness_verified": False,
        "claims_archived_time_state_verified": False,
        "claims_event_truth_verified": False,
        "claims_article_truth_verified": False,
        "claims_public_document_truth_verified": False,
        "claims_rights_clearance": False,
        "claims_privacy_safety": False,
        "claims_malware_safety": False,
        "claims_source_authenticity": False,
        "claims_production_readiness": False,
        "overclaim_errors": errors,
    }


def detect_h6_quality_overclaim(delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors = [f"quality overclaim: {path}=true" for path, key, value in _iter_key_values(delta) if key in FORBIDDEN_TRUE_KEYS and value is True]
    errors.extend(detect_h6_review_truth_boundary_violations(delta, policy))
    errors.extend(detect_h6_review_product_boundary_violations(delta, policy))
    return sorted(dict.fromkeys(errors))


def _per_source_delta(source_id: str, review: Mapping[str, Any], fixture_outputs: list[Mapping[str, Any]], live_outputs: list[Mapping[str, Any]], blocked_sources: list[str]) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "fixture_output_integrated": any(item.get("source_id") == source_id for item in fixture_outputs) or source_id in review.get("sources", []),
        "live_probe_completed": any(item.get("source_id") == source_id and item.get("status") == "live_probe_completed" for item in live_outputs),
        "live_probe_blocked": source_id in blocked_sources,
        "web_capture_identity_review_seed_created": source_id in review.get("sources", []),
        "archived_url_time_state_review_seed_created": source_id in review.get("sources", []),
        "news_event_mention_review_seed_created": source_id in review.get("sources", []),
        "dead_link_trace_review_seed_created": source_id in review.get("sources", []),
        "public_document_trace_review_seed_created": source_id in review.get("sources", []),
        "media_transcript_metadata_review_seed_created": source_id in review.get("sources", []),
        "source_cache_review_seed_created": source_id in review.get("sources", []),
        "evidence_review_seed_created": source_id in review.get("sources", []),
        "limitations": ["Fixture/local review only; not accepted source, evidence, web capture, time-state, event, article, public-document, privacy, safety, authenticity, rights, or production proof."],
    }


def _known_gaps(review: Mapping[str, Any]) -> list[str]:
    gaps: list[str] = []
    if review.get("blocked_sources"):
        gaps.append("operator_approval_missing_for_live_metadata_probes")
    if len(review.get("source_cache_review_seeds", [])) < len(H6_SOURCE_IDS):
        gaps.append("not_all_sources_have_review_seeds")
    if not any(item.get("status") == "live_probe_completed" for item in review.get("used_live_probe_outputs", [])):
        gaps.append("approved_live_probe_outputs_not_available")
    return sorted(dict.fromkeys(gaps))


def _truth_boundary() -> dict[str, bool]:
    return {
        "quality_delta_is_public_truth": False,
        "production_search_quality": False,
        "production_web_archive_coverage": False,
        "exhaustive_global_coverage": False,
        "capture_completeness_verified": False,
        "archived_time_state_verified": False,
        "event_truth_verified": False,
        "article_truth_verified": False,
        "public_document_truth_verified": False,
        "rights_clearance_claimed": False,
        "privacy_safety_claimed": False,
        "malware_safety_claimed": False,
        "source_authenticity_verified": False,
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
        "enabled_fetching": False,
        "enabled_crawling": False,
        "enabled_downloads": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "enabled_cdx_query": False,
        "enabled_memento_lookup": False,
        "enabled_warc_wacz_fetch": False,
        "enabled_archived_page_fetch": False,
        "enabled_media_downloads": False,
        "enabled_scraping_crawling": False,
        "enabled_sensitive_source_access": False,
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

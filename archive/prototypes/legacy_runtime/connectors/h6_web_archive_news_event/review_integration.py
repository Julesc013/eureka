"""Offline H6 web archive/news/event review integration helpers.

These helpers consume explicit H6 fixture replay outputs and blocked or
approved metadata-only live-probe outputs. They create review seeds and
planning previews only; they do not call networks, query CDX/Memento, fetch
WARC/WACZ files or pages, download media or documents, scrape, crawl, access
sensitive sources, accept truth, or mutate runtime state or indexes.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import hashlib
import json
from pathlib import Path
from typing import Any

from archive.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.normalizer_common import H6_SOURCE_CONFIGS, H6_SOURCE_IDS


FORBIDDEN_TRUTH_TRUE_KEYS = {
    "accepted_archived_time_state_truth",
    "accepted_article_truth",
    "accepted_candidate_truth",
    "accepted_event_truth",
    "accepted_evidence_truth",
    "accepted_privacy_safety_truth",
    "accepted_public_document_truth",
    "accepted_public_record",
    "accepted_source_truth",
    "accepted_web_capture_truth",
    "accepts_archived_time_state_truth",
    "accepts_article_truth",
    "accepts_candidate_truth",
    "accepts_event_truth",
    "accepts_evidence_truth",
    "accepts_privacy_safety_truth",
    "accepts_public_document_truth",
    "accepts_source_truth",
    "accepts_web_capture_truth",
    "archived_time_state_seed_accepts_historical_truth",
    "archived_time_state_verified",
    "article_truth_accepted",
    "article_truth_verified",
    "automatic_future_connector_approval",
    "candidate_promotion_preview_promotes_candidate",
    "capture_completeness_verified",
    "dead_link_seed_grants_acquisition_permission",
    "event_truth_verified",
    "evidence_review_seed_accepts_evidence",
    "future_connector_auto_approval",
    "h6_postmortem_enables_future_connectors_automatically",
    "malware_safety_claimed",
    "master_index_mutated",
    "media_transcript_seed_accepts_full_context_truth",
    "mutates_master_index",
    "mutates_public_index",
    "news_event_seed_accepts_event_truth",
    "privacy_safety_claimed",
    "production_readiness_claimed",
    "public_document_seed_accepts_public_document_truth",
    "public_document_truth_verified",
    "public_index_mutated",
    "rights_clearance_claimed",
    "source_authenticity_verified",
    "source_cache_review_seed_accepts_source",
    "source_pack_preview_is_imported_or_submitted",
    "verified_authenticity_claimed",
    "web_capture_seed_accepts_capture_truth",
}

FORBIDDEN_PRODUCT_TRUE_KEYS = {
    "changed_public_search_behavior",
    "enabled_accounts",
    "enabled_archived_page_fetch",
    "enabled_browser_automation",
    "enabled_cdx_query",
    "enabled_crawling",
    "enabled_downloads",
    "enabled_fetching",
    "enabled_hosting",
    "enabled_live_page_fetch",
    "enabled_media_downloads",
    "enabled_memento_lookup",
    "enabled_scraping_crawling",
    "enabled_sensitive_source_access",
    "enabled_source_sync",
    "enabled_telemetry",
    "enabled_uploads",
    "enabled_warc_wacz_fetch",
    "enables_archived_page_fetch",
    "enables_cdx_query",
    "enables_media_downloads",
    "enables_memento_lookup",
    "enables_scraping_crawling",
    "enables_sensitive_source_access",
    "enables_warc_wacz_fetch",
    "mutated_master_index",
    "mutated_public_index",
    "source_cache_runtime_mutated",
}

SEED_KIND_TO_RESULT_KEY = {
    "web_capture_identity": "web_capture_identity_review_seeds",
    "archived_url_time_state": "archived_url_time_state_review_seeds",
    "news_event_mention": "news_event_mention_review_seeds",
    "dead_link_trace": "dead_link_trace_review_seeds",
    "public_document_trace": "public_document_trace_review_seeds",
    "media_transcript_metadata": "media_transcript_metadata_review_seeds",
    "source_cache": "source_cache_review_seeds",
    "evidence_candidate": "evidence_candidate_review_seeds",
}


def load_h6_web_archive_outputs(paths: Sequence[str | Path]) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    for path_text in paths:
        path = Path(path_text)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            raise ValueError(f"{path} must contain a JSON object")
        outputs.append(dict(payload))
    return outputs


def build_h6_web_capture_identity_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("web_capture_identity", _source_id(inputs), _first_ref(inputs, "web_capture_identity_candidate_ref", "web_capture_identity_candidate", "web_capture_identity_candidate_id"), inputs)
    seed.update({
        "schema_version": "h6_web_capture_identity_review_seed.v0",
        "review_subject_type": "web_capture_identity_candidate",
        "accepted_web_capture_truth": False,
        "web_capture_seed_accepts_capture_truth": False,
        "capture_completeness_verified": False,
        "capture_digest_proves_authenticity": False,
        "archived_content_proves_rights_clearance": False,
        "limitations": _limitations(inputs) + ["Web capture identity review seed is not accepted capture truth, completeness, authenticity, or rights clearance."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h6_archived_url_time_state_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("archived_url_time_state", _source_id(inputs), _first_ref(inputs, "archived_url_time_state_candidate_ref", "archived_url_time_state_candidate", "time_state_candidate_id"), inputs)
    seed.update({
        "schema_version": "h6_archived_url_time_state_review_seed.v0",
        "review_subject_type": "archived_url_time_state_candidate",
        "accepted_archived_time_state_truth": False,
        "archived_time_state_seed_accepts_historical_truth": False,
        "archived_time_state_verified": False,
        "archived_page_fetch_permission": False,
        "limitations": _limitations(inputs) + ["Archived URL time-state seed is not historical truth or archived-page fetch permission."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h6_news_event_mention_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("news_event_mention", _source_id(inputs), _first_ref(inputs, "news_event_mention_candidate_refs", "news_event_mention_candidate", "news_event_mention_candidate_id"), inputs)
    seed.update({
        "schema_version": "h6_news_event_mention_review_seed.v0",
        "review_subject_type": "news_event_mention_candidate",
        "accepted_event_truth": False,
        "accepted_article_truth": False,
        "news_event_seed_accepts_event_truth": False,
        "article_truth_verified": False,
        "event_truth_verified": False,
        "limitations": _limitations(inputs) + ["News/event mention seed is not event truth, article truth, or full context."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h6_dead_link_trace_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("dead_link_trace", _source_id(inputs), _first_ref(inputs, "dead_link_trace_candidate_refs", "dead_link_trace_candidate", "dead_link_trace_candidate_id"), inputs)
    seed.update({
        "schema_version": "h6_dead_link_trace_review_seed.v0",
        "review_subject_type": "dead_link_trace_candidate",
        "dead_link_seed_grants_acquisition_permission": False,
        "warc_wacz_fetch_permission": False,
        "archived_page_fetch_permission": False,
        "media_download_permission": False,
        "limitations": _limitations(inputs) + ["Dead-link trace seed grants no acquisition, fetch, crawl, download, authenticity, or rights permission."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h6_public_document_trace_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("public_document_trace", _source_id(inputs), _first_ref(inputs, "public_document_trace_candidate_refs", "public_document_trace_candidate", "public_document_trace_candidate_id"), inputs)
    seed.update({
        "schema_version": "h6_public_document_trace_review_seed.v0",
        "review_subject_type": "public_document_trace_candidate",
        "accepted_public_document_truth": False,
        "accepted_privacy_safety_truth": False,
        "public_document_seed_accepts_public_document_truth": False,
        "public_document_fetch_permission": False,
        "sensitive_source_access_permission": False,
        "limitations": _limitations(inputs) + ["Public-document trace seed is not public-document truth, privacy/safety truth, or fetch permission."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h6_media_transcript_metadata_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("media_transcript_metadata", _source_id(inputs), _first_ref(inputs, "media_transcript_metadata_candidate_refs", "media_transcript_metadata_candidate", "media_transcript_metadata_candidate_id"), inputs)
    seed.update({
        "schema_version": "h6_media_transcript_metadata_review_seed.v0",
        "review_subject_type": "media_transcript_metadata_candidate",
        "media_transcript_seed_accepts_full_context_truth": False,
        "media_download_permission": False,
        "transcript_download_permission": False,
        "event_truth_verified": False,
        "limitations": _limitations(inputs) + ["Media/transcript metadata seed is not full-context, event truth, or download permission."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h6_source_cache_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("source_cache", _source_id(inputs), _first_ref(inputs, "source_cache_candidate_ref", "source_cache_candidate_preview", "source_cache_candidate_id"), inputs)
    seed.update({
        "schema_version": "h6_source_cache_review_seed.v0",
        "review_subject_type": "source_cache_candidate_preview",
        "accepted_source_truth": False,
        "source_cache_review_seed_accepts_source": False,
        "source_cache_runtime_mutated": False,
        "limitations": _limitations(inputs) + ["Source-cache review seed is not accepted source state and is not persisted."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h6_evidence_candidate_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("evidence_candidate", _source_id(inputs), _first_ref(inputs, "evidence_candidate_preview_ref", "evidence_candidate_preview", "evidence_candidate_preview_id"), inputs)
    seed.update({
        "schema_version": "h6_evidence_candidate_review_seed.v0",
        "review_subject_type": "evidence_candidate_preview",
        "accepted_evidence_truth": False,
        "accepted_candidate_truth": False,
        "evidence_review_seed_accepts_evidence": False,
        "review_decision_made": False,
        "limitations": _limitations(inputs) + ["Evidence candidate review seed is not accepted evidence or candidate truth."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h6_candidate_promotion_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = {
        "schema_version": "h6_candidate_promotion_preview.v0",
        "candidate_promotion_preview_id": f"h6.candidate_promotion.{source_id}.{_digest(inputs)[:10]}.v0",
        "source_id": source_id,
        "candidate_status": "preview_only",
        "candidate_promotion_preview_promotes_candidate": False,
        "accepted_candidate_truth": False,
        "accepted_evidence_truth": False,
        "review_required": True,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": _limitations(inputs) + ["Candidate promotion preview does not promote or accept a candidate."],
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h6_coverage_update_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = {
        "schema_version": "h6_source_coverage_update_preview.v0",
        "coverage_update_preview_id": f"h6.coverage_update.{source_id}.{_digest(inputs)[:10]}.v0",
        "source_id": source_id,
        "coverage_basis": "fixture_review_and_blocked_live_probe_evidence",
        "coverage_preview_is_exhaustive_global_coverage": False,
        "production_web_archive_coverage": False,
        "public_index_mutated": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": _limitations(inputs) + ["Coverage update is a preview and is not exhaustive or public-index state."],
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h6_connector_scorecard_update(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = {
        "schema_version": "h6_connector_scorecard_update.v0",
        "scorecard_update_id": f"h6.scorecard_update.{source_id}.{_digest(inputs)[:10]}.v0",
        "source_id": source_id,
        "fixture_replay_status": "integrated",
        "live_probe_status": str(inputs.get("result_status") or inputs.get("replay_status") or "fixture_integrated"),
        "production_ready": False,
        "auto_approves_future_connectors": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": _limitations(inputs) + ["Scorecard update is not production readiness or future connector approval."],
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h6_source_pack_update_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = {
        "schema_version": "h6_source_pack_update_preview.v0",
        "source_pack_update_preview_id": f"h6.source_pack_update.{source_id}.{_digest(inputs)[:10]}.v0",
        "source_id": source_id,
        "source_pack_preview_is_imported_or_submitted": False,
        "source_pack_import_enabled": False,
        "source_pack_submission_enabled": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": _limitations(inputs) + ["Source-pack update preview is not import, submission, acceptance, or public truth."],
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h6_review_integration_result(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    outputs = list(inputs.get("outputs") or [])
    input_refs = list(inputs.get("input_refs") or [])
    by_source = _best_inputs_by_source(outputs)
    sources = sorted(by_source) or list(H6_SOURCE_IDS)
    fixture_outputs = [_output_summary(item) for item in outputs if item.get("schema_version") == "h6_web_archive_fixture_replay_result.v0"]
    live_outputs = [_output_summary(item) for item in outputs if item.get("schema_version") == "h6_web_archive_live_probe_result.v0"]
    blocked_sources = sorted({item.get("source_id") for item in outputs if str(item.get("result_status", "")).startswith("blocked") and item.get("source_id")})
    seed_inputs = [by_source.get(source_id, {"source_id": source_id}) for source_id in sources]
    result = {
        "schema_version": "h6_web_archive_review_integration_result.v0",
        "review_integration_result_id": f"h6.review_integration.{_digest({'sources': sources, 'inputs': input_refs})[:12]}.v0",
        "wave_id": "H6",
        "sources": sources,
        "input_refs": input_refs,
        "used_fixture_outputs": fixture_outputs,
        "used_live_probe_outputs": live_outputs,
        "web_capture_identity_review_seeds": [build_h6_web_capture_identity_review_seed(item, policy) for item in seed_inputs],
        "archived_url_time_state_review_seeds": [build_h6_archived_url_time_state_review_seed(item, policy) for item in seed_inputs],
        "news_event_mention_review_seeds": [build_h6_news_event_mention_review_seed(item, policy) for item in seed_inputs],
        "dead_link_trace_review_seeds": [build_h6_dead_link_trace_review_seed(item, policy) for item in seed_inputs],
        "public_document_trace_review_seeds": [build_h6_public_document_trace_review_seed(item, policy) for item in seed_inputs],
        "media_transcript_metadata_review_seeds": [build_h6_media_transcript_metadata_review_seed(item, policy) for item in seed_inputs],
        "source_cache_review_seeds": [build_h6_source_cache_review_seed(item, policy) for item in seed_inputs],
        "evidence_candidate_review_seeds": [build_h6_evidence_candidate_review_seed(item, policy) for item in seed_inputs],
        "candidate_promotion_previews": [build_h6_candidate_promotion_preview(item, policy) for item in seed_inputs],
        "coverage_update_previews": [build_h6_coverage_update_preview(item, policy) for item in seed_inputs],
        "scorecard_updates": [build_h6_connector_scorecard_update(item, policy) for item in seed_inputs],
        "source_pack_update_previews": [build_h6_source_pack_update_preview(item, policy) for item in seed_inputs],
        "blocked_sources": blocked_sources,
        "warnings": ["H6 live probes remain blocked pending operator approval."] if blocked_sources else [],
        "limitations": [
            "H6 review integration is a wave-level rehearsal, not promotion.",
            "Fixture replay and blocked live-probe reports do not prove capture completeness, event truth, public-document truth, rights, privacy, safety, authenticity, or production coverage.",
        ],
        "accepts_web_capture_truth": False,
        "accepts_archived_time_state_truth": False,
        "accepts_event_truth": False,
        "accepts_article_truth": False,
        "accepts_public_document_truth": False,
        "accepts_privacy_safety_truth": False,
        "accepts_source_truth": False,
        "accepts_evidence_truth": False,
        "accepts_candidate_truth": False,
        "mutates_public_index": False,
        "mutates_master_index": False,
        "enables_cdx_query": False,
        "enables_memento_lookup": False,
        "enables_warc_wacz_fetch": False,
        "enables_archived_page_fetch": False,
        "enables_media_downloads": False,
        "enables_scraping_crawling": False,
        "enables_sensitive_source_access": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Review seeds and previews require explicit human review before any downstream persistence."],
    }
    _raise_if_boundaries_fail(result, policy)
    return result


def summarize_h6_review_integration(result: Mapping[str, Any]) -> dict[str, Any]:
    errors = detect_h6_review_truth_boundary_violations(result) + detect_h6_review_product_boundary_violations(result)
    return {
        "schema_version": "h6_review_integration_summary.v0",
        "status": "pass" if not errors else "invalid",
        "review_integration_result_id": result.get("review_integration_result_id"),
        "source_count": len(result.get("sources", [])),
        "web_capture_identity_review_seed_count": len(result.get("web_capture_identity_review_seeds", [])),
        "archived_url_time_state_review_seed_count": len(result.get("archived_url_time_state_review_seeds", [])),
        "news_event_mention_review_seed_count": len(result.get("news_event_mention_review_seeds", [])),
        "dead_link_trace_review_seed_count": len(result.get("dead_link_trace_review_seeds", [])),
        "public_document_trace_review_seed_count": len(result.get("public_document_trace_review_seeds", [])),
        "media_transcript_metadata_review_seed_count": len(result.get("media_transcript_metadata_review_seeds", [])),
        "source_cache_review_seed_count": len(result.get("source_cache_review_seeds", [])),
        "evidence_candidate_review_seed_count": len(result.get("evidence_candidate_review_seeds", [])),
        "blocked_sources": list(result.get("blocked_sources", [])),
        "truth_boundary_errors": detect_h6_review_truth_boundary_violations(result),
        "product_boundary_errors": detect_h6_review_product_boundary_violations(result),
    }


def detect_h6_review_truth_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return sorted({f"truth boundary violation: {path}=true" for path, key, value in _iter_key_values(result) if key in FORBIDDEN_TRUTH_TRUE_KEYS and value is True})


def detect_h6_review_product_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return sorted({f"product boundary violation: {path}=true" for path, key, value in _iter_key_values(result) if key in FORBIDDEN_PRODUCT_TRUE_KEYS and value is True})


def _seed_base(kind: str, source_id: str, ref: str, inputs: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "review_seed_id": f"h6.review_seed.{kind}.{source_id}.{_digest({'ref': ref, 'source_id': source_id})[:10]}.v0",
        "wave_id": "H6",
        "source_id": source_id,
        "source_label": str(H6_SOURCE_CONFIGS.get(source_id, {}).get("label", source_id)),
        "review_subject_ref": ref,
        "review_status": "seed_preview_only",
        "review_decision_made": False,
        "review_required": True,
        "source_cache_runtime_mutated": False,
        "evidence_ledger_runtime_mutated": False,
        "review_queue_runtime_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H6 review seed is not a review decision."],
    }


def _best_inputs_by_source(outputs: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    best: dict[str, dict[str, Any]] = {}
    for item in outputs:
        source_id = item.get("source_id")
        if source_id not in H6_SOURCE_IDS:
            continue
        current = best.get(str(source_id), {"source_id": source_id})
        merged = {**current, **dict(item)}
        if item.get("schema_version") == "h6_web_archive_fixture_replay_result.v0":
            best[str(source_id)] = merged
        else:
            best.setdefault(str(source_id), merged)
    return best


def _output_summary(item: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": item.get("source_id"),
        "schema_version": item.get("schema_version"),
        "status": item.get("result_status") or item.get("replay_status"),
        "ref": item.get("live_probe_result_id") or item.get("replay_result_id") or item.get("fixture_id"),
        "request_count": item.get("request_count", 0),
        "network_used": bool(item.get("network_used", False)),
    }


def _source_id(inputs: Mapping[str, Any]) -> str:
    source_id = str(inputs.get("source_id") or "")
    if source_id not in H6_SOURCE_IDS:
        raise ValueError(f"unknown or missing H6 source_id: {source_id}")
    return source_id


def _first_ref(inputs: Mapping[str, Any], *keys: str) -> str:
    for key in keys:
        value = inputs.get(key)
        if isinstance(value, list) and value:
            return str(value[0])
        if isinstance(value, Mapping):
            for id_key in ("web_capture_identity_candidate_id", "time_state_candidate_id", "news_event_mention_candidate_id", "dead_link_trace_candidate_id", "public_document_trace_candidate_id", "media_transcript_metadata_candidate_id", "source_cache_candidate_id", "evidence_candidate_preview_id"):
                if value.get(id_key):
                    return str(value[id_key])
        if value:
            return str(value)
    return f"h6.{_source_id(inputs)}.review_subject.preview"


def _limitations(inputs: Mapping[str, Any]) -> list[str]:
    values = inputs.get("limitations") or []
    return list(values) if isinstance(values, list) else [str(values)]


def _truth_boundary() -> dict[str, bool]:
    return {
        "web_capture_seed_accepts_capture_truth": False,
        "archived_time_state_seed_accepts_historical_truth": False,
        "news_event_seed_accepts_event_truth": False,
        "article_truth_accepted": False,
        "dead_link_seed_grants_acquisition_permission": False,
        "public_document_seed_accepts_public_document_truth": False,
        "media_transcript_seed_accepts_full_context_truth": False,
        "source_cache_review_seed_accepts_source": False,
        "evidence_review_seed_accepts_evidence": False,
        "candidate_promotion_preview_promotes_candidate": False,
        "source_pack_preview_is_imported_or_submitted": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "privacy_safety_claimed": False,
        "malware_safety_claimed": False,
        "verified_authenticity_claimed": False,
        "production_readiness_claimed": False,
        "automatic_future_connector_approval": False,
        "accepted_web_capture_truth": False,
        "accepted_archived_time_state_truth": False,
        "accepted_event_truth": False,
        "accepted_article_truth": False,
        "accepted_public_document_truth": False,
        "accepted_privacy_safety_truth": False,
        "accepted_source_truth": False,
        "accepted_evidence_truth": False,
        "accepted_candidate_truth": False,
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
        "enabled_live_page_fetch": False,
        "enabled_media_downloads": False,
        "enabled_scraping_crawling": False,
        "enabled_sensitive_source_access": False,
        "enabled_browser_automation": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def _raise_if_boundaries_fail(payload: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> None:
    errors = detect_h6_review_truth_boundary_violations(payload, policy)
    errors.extend(detect_h6_review_product_boundary_violations(payload, policy))
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

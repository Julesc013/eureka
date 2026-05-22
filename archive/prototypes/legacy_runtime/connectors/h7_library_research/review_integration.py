"""Offline H7 library/cultural/research review integration helpers.

These helpers consume explicit H7 fixture replay outputs and blocked or
approved metadata-only live-probe outputs. They create review seeds and
planning previews only; they do not call networks, harvest repositories,
query APIs, fetch full text or documents, download payloads, scrape, crawl,
access restricted sources, accept truth, or mutate runtime state or indexes.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import hashlib
import json
from pathlib import Path
from typing import Any

from archive.prototypes.legacy_runtime.connectors.h7_library_research.normalizer_common import H7_SOURCE_CONFIGS, H7_SOURCE_IDS


FORBIDDEN_TRUTH_TRUE_KEYS = {
    "accepted_access_rights_truth",
    "accepted_bibliographic_truth",
    "accepted_candidate_truth",
    "accepted_citation_truth",
    "accepted_cultural_object_truth",
    "accepted_dataset_truth",
    "accepted_evidence_truth",
    "accepted_patent_truth",
    "accepted_public_record",
    "accepted_research_work_truth",
    "accepted_source_truth",
    "access_metadata_is_rights_truth",
    "access_rights_seed_accepts_rights_truth",
    "automatic_future_connector_approval",
    "bibliographic_completeness_claimed",
    "bibliographic_completeness_verified",
    "bibliographic_identity_candidate_is_truth",
    "bibliographic_seed_accepts_bibliographic_truth",
    "candidate_promotion_preview_promotes_candidate",
    "citation_correctness_verified",
    "citation_relation_candidate_is_truth",
    "citation_seed_accepts_citation_truth",
    "cultural_object_candidate_is_truth",
    "cultural_object_seed_accepts_object_truth",
    "cultural_object_truth_verified",
    "dataset_identity_candidate_is_truth",
    "dataset_seed_accepts_dataset_truth",
    "dataset_validity_verified",
    "evidence_review_seed_accepts_evidence",
    "future_connector_auto_approval",
    "full_text_availability_verified",
    "landing_page_grants_download_permission",
    "malware_safety",
    "malware_safety_claimed",
    "master_index_mutated",
    "mutates_master_index",
    "mutates_public_index",
    "normalized_record_is_public_truth",
    "open_access_metadata_is_rights_clearance",
    "open_access_truth",
    "open_access_truth_claimed",
    "open_access_truth_verified",
    "patent_identity_candidate_is_truth",
    "patent_seed_accepts_patent_truth",
    "patent_validity_verified",
    "privacy_safety",
    "privacy_safety_claimed",
    "production_library_research_coverage",
    "production_readiness_claimed",
    "production_search_quality",
    "public_index_mutated",
    "research_work_candidate_is_truth",
    "research_work_identity_verified",
    "research_work_seed_accepts_work_truth",
    "review_seed_is_review_decision",
    "rights_clearance",
    "rights_clearance_claimed",
    "source_cache_review_seed_accepts_source",
    "source_pack_preview_is_imported_or_submitted",
    "verified_availability",
    "verified_availability_claimed",
}

FORBIDDEN_PRODUCT_TRUE_KEYS = {
    "api_calls_made",
    "article_download_used",
    "book_scan_download_used",
    "browser_automation_used",
    "bypass_or_automation_used",
    "changed_public_search_behavior",
    "crawling_used",
    "dataset_download_used",
    "doi_isbn_patent_query_used",
    "enabled_accounts",
    "enabled_browser_automation",
    "enabled_crawling",
    "enabled_downloads",
    "enabled_harvesting",
    "enabled_hosting",
    "enabled_live_probes",
    "enabled_restricted_source_access",
    "enabled_scraping",
    "enabled_source_sync",
    "enabled_telemetry",
    "enabled_uploads",
    "enables_api_sync",
    "enables_downloads",
    "enables_full_text_fetch",
    "enables_harvest_query_fetch_download",
    "enables_oai_pmh_harvest",
    "enables_restricted_source_access",
    "enables_scraping_crawling",
    "full_text_fetch_used",
    "iiif_fetch_used",
    "media_download_used",
    "mutated_master_index",
    "mutated_public_index",
    "network_calls_made",
    "oai_pmh_harvest_used",
    "patent_document_download_used",
    "pdf_download_used",
    "restricted_source_access_used",
    "scraping_used",
}

SEED_KIND_TO_RESULT_KEY = {
    "bibliographic_identity": "bibliographic_identity_review_seeds",
    "research_work_identity": "research_work_identity_review_seeds",
    "dataset_identity": "dataset_identity_review_seeds",
    "cultural_object_identity": "cultural_object_identity_review_seeds",
    "patent_identity": "patent_identity_review_seeds",
    "citation_relation": "citation_relation_review_seeds",
    "access_rights_availability": "access_rights_availability_review_seeds",
    "source_cache": "source_cache_review_seeds",
    "evidence_candidate": "evidence_candidate_review_seeds",
}


def load_h7_library_research_outputs(paths: Sequence[str | Path]) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    for path_text in paths:
        path = Path(path_text)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            raise ValueError(f"{path} must contain a JSON object")
        outputs.append(dict(payload))
    return outputs


def build_h7_bibliographic_identity_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("bibliographic_identity", _source_id(inputs), _first_ref(inputs, "bibliographic_identity_candidate", "bibliographic_identity_candidate_ref", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h7_bibliographic_identity_review_seed.v0",
        "review_subject_type": "bibliographic_identity_candidate",
        "accepted_bibliographic_truth": False,
        "bibliographic_seed_accepts_bibliographic_truth": False,
        "bibliographic_completeness_verified": False,
        "isbn_issn_oclc_lccn_truth_verified": False,
        "holdings_or_availability_verified": False,
        "rights_clearance_claimed": False,
        "limitations": _limitations(inputs) + ["Bibliographic identity review seed is not accepted bibliographic truth, completeness, holdings truth, identifier ownership truth, or rights clearance."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h7_research_work_identity_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("research_work_identity", _source_id(inputs), _first_ref(inputs, "research_work_identity_candidate", "research_work_identity_candidate_ref", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h7_research_work_identity_review_seed.v0",
        "review_subject_type": "research_work_identity_candidate",
        "accepted_research_work_truth": False,
        "research_work_seed_accepts_work_truth": False,
        "research_work_identity_verified": False,
        "article_truth_verified": False,
        "citation_correctness_verified": False,
        "open_access_truth_claimed": False,
        "limitations": _limitations(inputs) + ["Research work review seed is not accepted work truth, article truth, citation correctness, peer-review state, DOI truth, or open-access truth."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h7_dataset_identity_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("dataset_identity", _source_id(inputs), _first_ref(inputs, "dataset_identity_candidate", "dataset_identity_candidate_ref", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h7_dataset_identity_review_seed.v0",
        "review_subject_type": "dataset_identity_candidate",
        "accepted_dataset_truth": False,
        "dataset_seed_accepts_dataset_truth": False,
        "dataset_validity_verified": False,
        "dataset_download_permission": False,
        "malware_safety_claimed": False,
        "limitations": _limitations(inputs) + ["Dataset identity review seed is not dataset validity, download permission, rights clearance, or malware safety."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h7_cultural_object_identity_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("cultural_object_identity", _source_id(inputs), _first_ref(inputs, "cultural_object_identity_candidate", "cultural_object_identity_candidate_ref", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h7_cultural_object_identity_review_seed.v0",
        "review_subject_type": "cultural_object_identity_candidate",
        "accepted_cultural_object_truth": False,
        "cultural_object_seed_accepts_object_truth": False,
        "cultural_object_truth_verified": False,
        "iiif_or_media_fetch_permission": False,
        "rights_clearance_claimed": False,
        "limitations": _limitations(inputs) + ["Cultural object review seed is not object truth, collection completeness, media fetch permission, or rights clearance."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h7_patent_identity_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("patent_identity", _source_id(inputs), _first_ref(inputs, "patent_identity_candidate", "patent_identity_candidate_ref", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h7_patent_identity_review_seed.v0",
        "review_subject_type": "patent_identity_candidate",
        "accepted_patent_truth": False,
        "patent_seed_accepts_patent_truth": False,
        "patent_validity_verified": False,
        "patent_document_download_permission": False,
        "legal_status_verified": False,
        "limitations": _limitations(inputs) + ["Patent identity review seed is not patent validity, grant/expiry/enforceability, legal status, or document download permission."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h7_citation_relation_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("citation_relation", _source_id(inputs), _first_ref(inputs, "citation_relation_candidate", "citation_relation_candidate_ref", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h7_citation_relation_review_seed.v0",
        "review_subject_type": "citation_relation_candidate",
        "accepted_citation_truth": False,
        "citation_seed_accepts_citation_truth": False,
        "citation_correctness_verified": False,
        "same_work_cluster_verified": False,
        "impact_verified": False,
        "limitations": _limitations(inputs) + ["Citation relation review seed is not citation correctness, impact proof, or same-work clustering truth."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h7_access_rights_availability_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("access_rights_availability", _source_id(inputs), _first_ref(inputs, "access_rights_availability_candidate", "access_rights_availability_candidate_ref", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h7_access_rights_availability_review_seed.v0",
        "review_subject_type": "access_rights_availability_candidate",
        "accepted_access_rights_truth": False,
        "access_rights_seed_accepts_rights_truth": False,
        "rights_clearance_claimed": False,
        "open_access_truth_claimed": False,
        "verified_availability_claimed": False,
        "download_permission_current": False,
        "limitations": _limitations(inputs) + ["Access/rights/availability review seed is not rights clearance, open-access truth, verified availability, or download permission."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h7_source_cache_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("source_cache", _source_id(inputs), _first_ref(inputs, "source_cache_candidate_preview", "source_cache_candidate_preview_ref", "source_cache_candidate_preview_id"), inputs)
    seed.update({
        "schema_version": "h7_source_cache_review_seed.v0",
        "review_subject_type": "source_cache_candidate_preview",
        "accepted_source_truth": False,
        "source_cache_review_seed_accepts_source": False,
        "source_cache_runtime_mutated": False,
        "limitations": _limitations(inputs) + ["Source-cache review seed is not accepted source state and is not persisted."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h7_evidence_candidate_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("evidence_candidate", _source_id(inputs), _first_ref(inputs, "evidence_candidate_preview", "evidence_candidate_preview_ref", "evidence_candidate_preview_id"), inputs)
    seed.update({
        "schema_version": "h7_evidence_candidate_review_seed.v0",
        "review_subject_type": "evidence_candidate_preview",
        "accepted_evidence_truth": False,
        "accepted_candidate_truth": False,
        "evidence_review_seed_accepts_evidence": False,
        "review_decision_made": False,
        "limitations": _limitations(inputs) + ["Evidence candidate review seed is not accepted evidence or candidate truth."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h7_candidate_promotion_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = {
        "schema_version": "h7_candidate_promotion_preview.v0",
        "candidate_promotion_preview_id": f"h7.candidate_promotion.{source_id}.{_digest(inputs)[:10]}.v0",
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


def build_h7_coverage_update_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = {
        "schema_version": "h7_source_coverage_update_preview.v0",
        "coverage_update_preview_id": f"h7.coverage_update.{source_id}.{_digest(inputs)[:10]}.v0",
        "source_id": source_id,
        "coverage_basis": "fixture_review_and_blocked_live_probe_evidence",
        "coverage_preview_is_exhaustive_global_coverage": False,
        "production_library_research_coverage": False,
        "public_index_mutated": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": _limitations(inputs) + ["Coverage update is a preview and is not exhaustive or public-index state."],
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h7_connector_scorecard_update(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = {
        "schema_version": "h7_connector_scorecard_update.v0",
        "scorecard_update_id": f"h7.scorecard_update.{source_id}.{_digest(inputs)[:10]}.v0",
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


def build_h7_source_pack_update_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = {
        "schema_version": "h7_source_pack_update_preview.v0",
        "source_pack_update_preview_id": f"h7.source_pack_update.{source_id}.{_digest(inputs)[:10]}.v0",
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


def build_h7_review_integration_result(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    outputs = list(inputs.get("outputs") or [])
    input_refs = list(inputs.get("input_refs") or [])
    by_source = _best_inputs_by_source(outputs)
    sources = sorted(by_source) or list(H7_SOURCE_IDS)
    fixture_outputs = [_output_summary(item) for item in outputs if item.get("schema_version") == "h7_library_research_fixture_replay_result.v0"]
    live_outputs = [_output_summary(item) for item in outputs if item.get("schema_version") == "h7_library_research_live_probe_result.v0"]
    blocked_sources = sorted({item.get("source_id") for item in outputs if str(item.get("result_status", "")).startswith("blocked") and item.get("source_id")})
    seed_inputs = [by_source.get(source_id, {"source_id": source_id}) for source_id in sources]
    result = {
        "schema_version": "h7_library_research_review_integration_result.v0",
        "review_integration_result_id": f"h7.review_integration.{_digest({'sources': sources, 'inputs': input_refs})[:12]}.v0",
        "wave_id": "H7",
        "sources": sources,
        "source_count": len(sources),
        "input_refs": input_refs,
        "used_fixture_outputs": fixture_outputs,
        "used_live_probe_outputs": live_outputs,
        "bibliographic_identity_review_seeds": [build_h7_bibliographic_identity_review_seed(item, policy) for item in seed_inputs],
        "research_work_identity_review_seeds": [build_h7_research_work_identity_review_seed(item, policy) for item in seed_inputs],
        "dataset_identity_review_seeds": [build_h7_dataset_identity_review_seed(item, policy) for item in seed_inputs],
        "cultural_object_identity_review_seeds": [build_h7_cultural_object_identity_review_seed(item, policy) for item in seed_inputs],
        "patent_identity_review_seeds": [build_h7_patent_identity_review_seed(item, policy) for item in seed_inputs],
        "citation_relation_review_seeds": [build_h7_citation_relation_review_seed(item, policy) for item in seed_inputs],
        "access_rights_availability_review_seeds": [build_h7_access_rights_availability_review_seed(item, policy) for item in seed_inputs],
        "source_cache_review_seeds": [build_h7_source_cache_review_seed(item, policy) for item in seed_inputs],
        "evidence_candidate_review_seeds": [build_h7_evidence_candidate_review_seed(item, policy) for item in seed_inputs],
        "candidate_promotion_previews": [build_h7_candidate_promotion_preview(item, policy) for item in seed_inputs],
        "coverage_update_previews": [build_h7_coverage_update_preview(item, policy) for item in seed_inputs],
        "scorecard_updates": [build_h7_connector_scorecard_update(item, policy) for item in seed_inputs],
        "source_pack_update_previews": [build_h7_source_pack_update_preview(item, policy) for item in seed_inputs],
        "blocked_sources": blocked_sources,
        "warnings": ["H7 live probes remain blocked pending operator approval."] if blocked_sources else [],
        "limitations": [
            "H7 review integration is a wave-level rehearsal, not promotion.",
            "Fixture replay and blocked live-probe reports do not prove bibliographic completeness, citation correctness, DOI/ISBN/DataCite identity truth, article truth, dataset validity, rights clearance, open-access truth, patent validity, full-text availability, malware safety, privacy safety, verified availability, or production coverage.",
        ],
        "accepts_bibliographic_truth": False,
        "accepts_research_work_truth": False,
        "accepts_dataset_truth": False,
        "accepts_cultural_object_truth": False,
        "accepts_patent_truth": False,
        "accepts_citation_truth": False,
        "accepts_access_rights_truth": False,
        "accepts_source_truth": False,
        "accepts_evidence_truth": False,
        "accepts_candidate_truth": False,
        "mutates_public_index": False,
        "mutates_master_index": False,
        "enables_oai_pmh_harvest": False,
        "enables_api_sync": False,
        "enables_full_text_fetch": False,
        "enables_downloads": False,
        "enables_scraping_crawling": False,
        "enables_restricted_source_access": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Review seeds and previews require explicit human review before any downstream persistence."],
    }
    _raise_if_boundaries_fail(result, policy)
    return result


def summarize_h7_review_integration(result: Mapping[str, Any]) -> dict[str, Any]:
    errors = detect_h7_review_truth_boundary_violations(result) + detect_h7_review_product_boundary_violations(result)
    return {
        "schema_version": "h7_review_integration_summary.v0",
        "status": "pass" if not errors else "invalid",
        "review_integration_result_id": result.get("review_integration_result_id"),
        "source_count": len(result.get("sources", [])),
        "bibliographic_identity_review_seed_count": len(result.get("bibliographic_identity_review_seeds", [])),
        "research_work_identity_review_seed_count": len(result.get("research_work_identity_review_seeds", [])),
        "dataset_identity_review_seed_count": len(result.get("dataset_identity_review_seeds", [])),
        "cultural_object_identity_review_seed_count": len(result.get("cultural_object_identity_review_seeds", [])),
        "patent_identity_review_seed_count": len(result.get("patent_identity_review_seeds", [])),
        "citation_relation_review_seed_count": len(result.get("citation_relation_review_seeds", [])),
        "access_rights_availability_review_seed_count": len(result.get("access_rights_availability_review_seeds", [])),
        "source_cache_review_seed_count": len(result.get("source_cache_review_seeds", [])),
        "evidence_candidate_review_seed_count": len(result.get("evidence_candidate_review_seeds", [])),
        "blocked_sources": list(result.get("blocked_sources", [])),
        "truth_boundary_errors": detect_h7_review_truth_boundary_violations(result),
        "product_boundary_errors": detect_h7_review_product_boundary_violations(result),
    }


def detect_h7_review_truth_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return sorted({f"truth boundary violation: {path}=true" for path, key, value in _iter_key_values(result) if key in FORBIDDEN_TRUTH_TRUE_KEYS and value is True})


def detect_h7_review_product_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return sorted({f"product boundary violation: {path}=true" for path, key, value in _iter_key_values(result) if key in FORBIDDEN_PRODUCT_TRUE_KEYS and value is True})


def _seed_base(kind: str, source_id: str, ref: str, inputs: Mapping[str, Any]) -> dict[str, Any]:
    config = H7_SOURCE_CONFIGS.get(source_id, {})
    support_key = {
        "bibliographic_identity": "has_bibliographic",
        "research_work_identity": "has_research_work",
        "dataset_identity": "has_dataset",
        "cultural_object_identity": "has_cultural_object",
        "patent_identity": "has_patent",
        "citation_relation": "has_citation",
        "access_rights_availability": "has_access_rights",
    }.get(kind)
    return {
        "review_seed_id": f"h7.review_seed.{kind}.{source_id}.{_digest({'ref': ref, 'source_id': source_id})[:10]}.v0",
        "wave_id": "H7",
        "source_id": source_id,
        "source_label": str(config.get("label", source_id)),
        "connector_family": str(config.get("connector_family", inputs.get("connector_family", "unknown"))),
        "review_subject_ref": ref,
        "review_status": "seed_preview_only",
        "source_supports_candidate_family": bool(config.get(support_key, True)) if support_key else True,
        "review_decision_made": False,
        "review_required": True,
        "source_cache_runtime_mutated": False,
        "evidence_ledger_runtime_mutated": False,
        "review_queue_runtime_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H7 review seed is not a review decision."],
    }


def _best_inputs_by_source(outputs: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    best: dict[str, dict[str, Any]] = {}
    for item in outputs:
        source_id = item.get("source_id")
        if source_id not in H7_SOURCE_IDS:
            continue
        current = best.get(str(source_id), {"source_id": source_id})
        merged = {**current, **dict(item)}
        if item.get("schema_version") == "h7_library_research_fixture_replay_result.v0":
            best[str(source_id)] = merged
        else:
            best.setdefault(str(source_id), merged)
    return best


def _output_summary(item: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": item.get("source_id"),
        "schema_version": item.get("schema_version"),
        "status": item.get("result_status") or item.get("replay_status"),
        "ref": item.get("live_probe_result_id") or item.get("fixture_replay_result_id") or item.get("fixture_id"),
        "request_count": item.get("request_count", 0),
        "network_used": bool(item.get("network_used", False)),
    }


def _source_id(inputs: Mapping[str, Any]) -> str:
    source_id = str(inputs.get("source_id") or "")
    if source_id not in H7_SOURCE_IDS:
        raise ValueError(f"unknown or missing H7 source_id: {source_id}")
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
    return f"h7.{_source_id(inputs)}.review_subject.preview"


def _limitations(inputs: Mapping[str, Any]) -> list[str]:
    values = inputs.get("limitations") or []
    return list(values) if isinstance(values, list) else [str(values)]


def _truth_boundary() -> dict[str, bool]:
    return {
        "bibliographic_seed_accepts_bibliographic_truth": False,
        "research_work_seed_accepts_work_truth": False,
        "dataset_seed_accepts_dataset_truth": False,
        "cultural_object_seed_accepts_object_truth": False,
        "patent_seed_accepts_patent_truth": False,
        "citation_seed_accepts_citation_truth": False,
        "access_rights_seed_accepts_rights_truth": False,
        "source_cache_review_seed_accepts_source": False,
        "evidence_review_seed_accepts_evidence": False,
        "candidate_promotion_preview_promotes_candidate": False,
        "source_pack_preview_is_imported_or_submitted": False,
        "review_seed_is_review_decision": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "open_access_truth_claimed": False,
        "privacy_safety_claimed": False,
        "malware_safety_claimed": False,
        "verified_availability_claimed": False,
        "production_readiness_claimed": False,
        "automatic_future_connector_approval": False,
        "accepted_bibliographic_truth": False,
        "accepted_research_work_truth": False,
        "accepted_dataset_truth": False,
        "accepted_cultural_object_truth": False,
        "accepted_patent_truth": False,
        "accepted_citation_truth": False,
        "accepted_access_rights_truth": False,
        "accepted_source_truth": False,
        "accepted_evidence_truth": False,
        "accepted_candidate_truth": False,
        "accepted_public_record": False,
        "bibliographic_identity_candidate_is_truth": False,
        "research_work_candidate_is_truth": False,
        "dataset_identity_candidate_is_truth": False,
        "cultural_object_candidate_is_truth": False,
        "patent_identity_candidate_is_truth": False,
        "citation_relation_candidate_is_truth": False,
        "access_metadata_is_rights_truth": False,
        "open_access_metadata_is_rights_clearance": False,
        "landing_page_grants_download_permission": False,
        "bibliographic_completeness_verified": False,
        "citation_correctness_verified": False,
        "dataset_validity_verified": False,
        "cultural_object_truth_verified": False,
        "patent_validity_verified": False,
        "full_text_availability_verified": False,
    }


def _product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_hosting": False,
        "enabled_live_probes": False,
        "enabled_source_sync": False,
        "enabled_harvesting": False,
        "enabled_downloads": False,
        "enabled_crawling": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "enabled_scraping": False,
        "enabled_browser_automation": False,
        "network_calls_made": False,
        "api_calls_made": False,
        "oai_pmh_harvest_used": False,
        "doi_isbn_patent_query_used": False,
        "full_text_fetch_used": False,
        "pdf_download_used": False,
        "book_scan_download_used": False,
        "article_download_used": False,
        "dataset_download_used": False,
        "patent_document_download_used": False,
        "iiif_fetch_used": False,
        "media_download_used": False,
        "scraping_used": False,
        "crawling_used": False,
        "browser_automation_used": False,
        "bypass_or_automation_used": False,
        "restricted_source_access_used": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def _raise_if_boundaries_fail(payload: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> None:
    errors = detect_h7_review_truth_boundary_violations(payload, policy)
    errors.extend(detect_h7_review_product_boundary_violations(payload, policy))
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

"""Offline H8 manuals/docs/standards review integration helpers.

These helpers consume explicit H8 fixture replay outputs and blocked or
approved metadata-only live-probe outputs. They create review seeds and
planning previews only; they do not call networks, query catalogs, fetch
documents, download payloads, extract OCR/full text, scrape, crawl, access
restricted sources, accept truth, authorize repair/install actions, or mutate
runtime state or indexes.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import hashlib
import json
from pathlib import Path
from typing import Any

from runtime.connectors.h8_manuals_docs_standards.normalizer_common import H8_SOURCE_CONFIGS, H8_SOURCE_IDS


FORBIDDEN_TRUTH_TRUE_KEYS = {
    "accepted_access_rights_truth",
    "accepted_candidate_truth",
    "accepted_datasheet_device_truth",
    "accepted_document_truth",
    "accepted_evidence_truth",
    "accepted_install_requirement_truth",
    "accepted_manual_artifact_relation_truth",
    "accepted_public_record",
    "accepted_repair_service_safety_truth",
    "accepted_source_truth",
    "accepted_standards_truth",
    "access_metadata_is_rights_truth",
    "access_rights_seed_accepts_rights_truth",
    "access_rights_verified",
    "automatic_future_connector_approval",
    "candidate_promotion_preview_promotes_candidate",
    "compatibility_correctness_claimed",
    "compatibility_correctness_verified",
    "datasheet_device_identity_candidate_is_truth",
    "datasheet_device_seed_accepts_device_truth",
    "documentation_completeness_claimed",
    "documentation_completeness_verified",
    "electrical_safety_claimed",
    "electrical_safety_verified",
    "evidence_review_seed_accepts_evidence",
    "future_connector_auto_approval",
    "install_requirement_candidate_is_installability_truth",
    "install_requirement_seed_accepts_installability_truth",
    "installability_claimed",
    "installability_verified",
    "malware_safety",
    "malware_safety_claimed",
    "manual_artifact_relation_candidate_is_truth",
    "manual_artifact_seed_accepts_relation_truth",
    "master_index_mutated",
    "mutates_master_index",
    "mutates_public_index",
    "open_access_metadata_is_rights_clearance",
    "open_access_truth",
    "open_access_truth_claimed",
    "open_access_truth_verified",
    "production_documentation_coverage",
    "production_readiness_claimed",
    "production_search_quality",
    "public_index_mutated",
    "repair_safety_claimed",
    "repair_safety_verified",
    "repair_service_candidate_authorizes_action",
    "repair_service_safety_candidate_is_safety_truth",
    "repair_service_safety_seed_accepts_safety_truth",
    "review_seed_is_review_decision",
    "rights_clearance",
    "rights_clearance_claimed",
    "source_cache_review_seed_accepts_source",
    "source_pack_preview_is_imported_or_submitted",
    "standards_compliance_verified",
    "standards_conformance_verified",
    "standards_specification_candidate_is_truth",
    "standards_specification_seed_accepts_standards_truth",
    "technical_document_identity_candidate_is_truth",
    "technical_document_seed_accepts_document_truth",
    "verified_authenticity",
    "verified_authenticity_claimed",
}

FORBIDDEN_PRODUCT_TRUE_KEYS = {
    "api_calls_made",
    "api_query_used",
    "api_catalog_sync_permission",
    "browser_automation_used",
    "bypass_or_automation_used",
    "catalog_fetch_used",
    "changed_public_search_behavior",
    "crawling_used",
    "datasheet_download_used",
    "document_download_used",
    "document_fetch_used",
    "download_permission",
    "enabled_accounts",
    "enabled_browser_automation",
    "enabled_crawling",
    "enabled_downloads",
    "enabled_extraction",
    "enabled_hosting",
    "enabled_live_probes",
    "enabled_scraping",
    "enabled_source_sync",
    "enabled_telemetry",
    "enabled_uploads",
    "enables_api_catalog_sync",
    "enables_document_fetch",
    "enables_downloads",
    "enables_full_text_ocr",
    "enables_query_fetch_download_extract",
    "enables_restricted_source_access",
    "enables_scraping_crawling",
    "full_text_fetch_used",
    "manual_download_used",
    "media_download_used",
    "mutated_master_index",
    "mutated_public_index",
    "network_calls_made",
    "ocr_extraction_used",
    "pdf_download_used",
    "repair_or_install_action_authorized",
    "restricted_source_access_used",
    "scan_download_used",
    "schematic_download_used",
    "scraping_used",
    "service_manual_download_used",
    "standards_document_download_used",
}

REVIEW_SEED_BUILDERS: dict[str, str] = {
    "technical_document_identity": "technical_document_identity_review_seeds",
    "manual_artifact_relation": "manual_artifact_relation_review_seeds",
    "datasheet_device_identity": "datasheet_device_identity_review_seeds",
    "standards_specification_identity": "standards_specification_identity_review_seeds",
    "install_requirement_claim": "install_requirement_claim_review_seeds",
    "repair_service_safety": "repair_service_safety_review_seeds",
    "access_rights": "access_rights_review_seeds",
}


def load_h8_manuals_docs_outputs(paths: Sequence[str | Path]) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    for path_text in paths:
        path = Path(path_text)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            raise ValueError(f"{path} must contain a JSON object")
        outputs.append(dict(payload))
    return outputs


def build_h8_technical_document_identity_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("technical_document_identity", _source_id(inputs), _first_ref(inputs, "technical_document_identity_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h8_technical_document_identity_review_seed.v0",
        "review_subject_type": "technical_document_identity_candidate",
        "accepted_document_truth": False,
        "technical_document_seed_accepts_document_truth": False,
        "documentation_completeness_verified": False,
        "document_download_permission": False,
        "verified_authenticity_claimed": False,
        "limitations": _limitations(inputs) + ["Technical-document identity review seed is not accepted document truth, completeness proof, authenticity proof, extraction permission, or download permission."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h8_manual_artifact_relation_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("manual_artifact_relation", _source_id(inputs), _first_ref(inputs, "manual_artifact_relation_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h8_manual_artifact_relation_review_seed.v0",
        "review_subject_type": "manual_artifact_relation_candidate",
        "accepted_manual_artifact_relation_truth": False,
        "manual_artifact_seed_accepts_relation_truth": False,
        "compatibility_correctness_verified": False,
        "installability_verified": False,
        "repair_safety_verified": False,
        "limitations": _limitations(inputs) + ["Manual-artifact relation review seed is not relation truth, compatibility correctness, installability, repair safety, or rights clearance."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h8_datasheet_device_identity_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("datasheet_device_identity", _source_id(inputs), _first_ref(inputs, "datasheet_device_identity_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h8_datasheet_device_identity_review_seed.v0",
        "review_subject_type": "datasheet_device_identity_candidate",
        "accepted_datasheet_device_truth": False,
        "datasheet_device_seed_accepts_device_truth": False,
        "electrical_safety_verified": False,
        "datasheet_download_permission": False,
        "verified_authenticity_claimed": False,
        "limitations": _limitations(inputs) + ["Datasheet/device review seed is not device truth, electrical safety, lifecycle/availability truth, engineering guidance, or datasheet download permission."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h8_standards_specification_identity_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("standards_specification_identity", _source_id(inputs), _first_ref(inputs, "standards_specification_identity_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h8_standards_specification_identity_review_seed.v0",
        "review_subject_type": "standards_specification_identity_candidate",
        "accepted_standards_truth": False,
        "standards_specification_seed_accepts_standards_truth": False,
        "standards_compliance_verified": False,
        "standards_conformance_verified": False,
        "standards_document_download_permission": False,
        "limitations": _limitations(inputs) + ["Standards/specification review seed is not standards truth, conformance proof, document access permission, or rights clearance."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h8_install_requirement_claim_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("install_requirement_claim", _source_id(inputs), _first_ref(inputs, "install_requirement_claim_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h8_install_requirement_claim_review_seed.v0",
        "review_subject_type": "install_requirement_claim_candidate",
        "accepted_install_requirement_truth": False,
        "install_requirement_seed_accepts_installability_truth": False,
        "installability_verified": False,
        "repair_or_install_action_authorized": False,
        "limitations": _limitations(inputs) + ["Install requirement review seed is not installability truth, compatibility correctness, safe execution guidance, or action permission."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h8_repair_service_safety_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("repair_service_safety", _source_id(inputs), _first_ref(inputs, "repair_service_safety_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h8_repair_service_safety_review_seed.v0",
        "review_subject_type": "repair_service_safety_candidate",
        "accepted_repair_service_safety_truth": False,
        "repair_service_safety_seed_accepts_safety_truth": False,
        "repair_safety_verified": False,
        "electrical_safety_verified": False,
        "repair_or_install_action_authorized": False,
        "limitations": _limitations(inputs) + ["Repair/service/safety review seed is not safety truth, electrical safety proof, repair authorization, calibration permission, or action permission."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h8_access_rights_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("access_rights", _source_id(inputs), _first_ref(inputs, "access_rights_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h8_access_rights_review_seed.v0",
        "review_subject_type": "access_rights_candidate",
        "accepted_access_rights_truth": False,
        "access_rights_seed_accepts_rights_truth": False,
        "rights_clearance_claimed": False,
        "open_access_truth_claimed": False,
        "download_permission_current": False,
        "limitations": _limitations(inputs) + ["Access/rights review seed is not rights clearance, open-access truth, redistribution permission, or download permission."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h8_source_cache_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("source_cache", _source_id(inputs), _first_ref(inputs, "source_cache_candidate_preview", "source_cache_candidate_preview_id"), inputs)
    seed.update({
        "schema_version": "h8_source_cache_review_seed.v0",
        "review_subject_type": "source_cache_candidate_preview",
        "accepted_source_truth": False,
        "source_cache_review_seed_accepts_source": False,
        "source_cache_write_allowed_current": False,
        "limitations": _limitations(inputs) + ["Source-cache review seed is not accepted source truth and does not write the source cache."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h8_evidence_candidate_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("evidence_candidate", _source_id(inputs), _first_ref(inputs, "evidence_candidate_preview", "evidence_candidate_preview_id"), inputs)
    seed.update({
        "schema_version": "h8_evidence_candidate_review_seed.v0",
        "review_subject_type": "evidence_candidate_preview",
        "accepted_evidence_truth": False,
        "evidence_review_seed_accepts_evidence": False,
        "evidence_ledger_write_allowed_current": False,
        "limitations": _limitations(inputs) + ["Evidence candidate review seed is not accepted evidence and does not write the evidence ledger."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h8_candidate_promotion_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = {
        "schema_version": "h8_candidate_promotion_preview.v0",
        "candidate_promotion_preview_id": f"h8.candidate_promotion.{source_id}.{_digest(inputs)[:12]}.v0",
        "source_id": source_id,
        "preview_only": True,
        "promotes_candidate": False,
        "candidate_promotion_preview_promotes_candidate": False,
        "accepted_candidate_truth": False,
        "review_required_before_promotion": True,
        "limitations": _limitations(inputs) + ["Candidate promotion preview does not promote, accept, or publish any candidate."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h8_coverage_update_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = {
        "schema_version": "h8_source_coverage_update_preview.v0",
        "coverage_update_preview_id": f"h8.coverage_update.{source_id}.{_digest(inputs)[:12]}.v0",
        "source_id": source_id,
        "coverage_basis": "fixture_review_and_blocked_live_probe_evidence",
        "coverage_preview_only": True,
        "coverage_manifest_is_exhaustive_global_coverage": False,
        "production_documentation_coverage": False,
        "limitations": ["Coverage update preview is not exhaustive global coverage or production documentation coverage."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h8_connector_scorecard_update(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    update = {
        "schema_version": "h8_connector_scorecard_update.v0",
        "connector_scorecard_update_id": f"h8.scorecard_update.{source_id}.{_digest(inputs)[:12]}.v0",
        "source_id": source_id,
        "fixture_replay_status": "integrated",
        "live_probe_status": "blocked_or_not_run_without_approval",
        "review_integration_status": "preview_created",
        "production_ready": False,
        "auto_approves_future_connectors": False,
        "limitations": ["Connector scorecard update is not production readiness or future connector approval."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_boundaries_fail(update, policy)
    return update


def build_h8_source_pack_update_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = {
        "schema_version": "h8_source_pack_update_preview.v0",
        "source_pack_update_preview_id": f"h8.source_pack_update.{source_id}.{_digest(inputs)[:12]}.v0",
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


def build_h8_review_integration_result(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    outputs = list(inputs.get("outputs") or [])
    input_refs = list(inputs.get("input_refs") or [])
    by_source = _best_inputs_by_source(outputs)
    sources = sorted(by_source) or list(H8_SOURCE_IDS)
    fixture_outputs = [_output_summary(item) for item in outputs if item.get("schema_version") == "h8_manuals_docs_fixture_replay_result.v0"]
    live_outputs = [_output_summary(item) for item in outputs if item.get("schema_version") == "h8_manuals_docs_live_probe_result.v0"]
    blocked_sources = sorted({str(item.get("source_id")) for item in outputs if str(item.get("result_status", "")).startswith("blocked") and item.get("source_id")})
    seed_inputs = [by_source.get(source_id, {"source_id": source_id}) for source_id in sources]
    result = {
        "schema_version": "h8_manuals_docs_review_integration_result.v0",
        "review_integration_result_id": f"h8.review_integration.{_digest({'sources': sources, 'inputs': input_refs})[:12]}.v0",
        "wave_id": "H8",
        "sources": sources,
        "source_count": len(sources),
        "input_refs": input_refs,
        "used_fixture_outputs": fixture_outputs,
        "used_live_probe_outputs": live_outputs,
        "technical_document_identity_review_seeds": [build_h8_technical_document_identity_review_seed(item, policy) for item in seed_inputs],
        "manual_artifact_relation_review_seeds": [build_h8_manual_artifact_relation_review_seed(item, policy) for item in seed_inputs],
        "datasheet_device_identity_review_seeds": [build_h8_datasheet_device_identity_review_seed(item, policy) for item in seed_inputs],
        "standards_specification_identity_review_seeds": [build_h8_standards_specification_identity_review_seed(item, policy) for item in seed_inputs],
        "install_requirement_claim_review_seeds": [build_h8_install_requirement_claim_review_seed(item, policy) for item in seed_inputs],
        "repair_service_safety_review_seeds": [build_h8_repair_service_safety_review_seed(item, policy) for item in seed_inputs],
        "access_rights_review_seeds": [build_h8_access_rights_review_seed(item, policy) for item in seed_inputs],
        "source_cache_review_seeds": [build_h8_source_cache_review_seed(item, policy) for item in seed_inputs],
        "evidence_candidate_review_seeds": [build_h8_evidence_candidate_review_seed(item, policy) for item in seed_inputs],
        "candidate_promotion_previews": [build_h8_candidate_promotion_preview(item, policy) for item in seed_inputs],
        "coverage_update_previews": [build_h8_coverage_update_preview(item, policy) for item in seed_inputs],
        "scorecard_updates": [build_h8_connector_scorecard_update(item, policy) for item in seed_inputs],
        "source_pack_update_previews": [build_h8_source_pack_update_preview(item, policy) for item in seed_inputs],
        "blocked_sources": blocked_sources,
        "warnings": ["H8 live probes remain blocked pending operator approval."] if blocked_sources else [],
        "limitations": [
            "H8 review integration is a wave-level audit and rehearsal, not promotion.",
            "Fixture replay and blocked live-probe reports do not prove documentation completeness, standards compliance, compatibility correctness, installability, repair safety, electrical safety, rights clearance, open-access truth, malware safety, verified authenticity, or production coverage.",
        ],
        "accepts_document_truth": False,
        "accepts_manual_artifact_relation_truth": False,
        "accepts_datasheet_device_truth": False,
        "accepts_standards_truth": False,
        "accepts_install_requirement_truth": False,
        "accepts_repair_service_safety_truth": False,
        "accepts_access_rights_truth": False,
        "accepts_source_truth": False,
        "accepts_evidence_truth": False,
        "accepts_candidate_truth": False,
        "mutates_public_index": False,
        "mutates_master_index": False,
        "enables_api_catalog_sync": False,
        "enables_document_fetch": False,
        "enables_downloads": False,
        "enables_full_text_ocr": False,
        "enables_scraping_crawling": False,
        "enables_restricted_source_access": False,
        "grants_repair_or_install_action_permission": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Review seeds and previews require explicit human review before any downstream persistence."],
    }
    _raise_if_boundaries_fail(result, policy)
    return result


def summarize_h8_review_integration(result: Mapping[str, Any]) -> dict[str, Any]:
    errors = detect_h8_review_truth_boundary_violations(result) + detect_h8_review_product_boundary_violations(result)
    return {
        "schema_version": "h8_review_integration_summary.v0",
        "status": "pass" if not errors else "invalid",
        "review_integration_result_id": result.get("review_integration_result_id"),
        "source_count": len(result.get("sources", [])),
        "technical_document_identity_review_seed_count": len(result.get("technical_document_identity_review_seeds", [])),
        "manual_artifact_relation_review_seed_count": len(result.get("manual_artifact_relation_review_seeds", [])),
        "datasheet_device_identity_review_seed_count": len(result.get("datasheet_device_identity_review_seeds", [])),
        "standards_specification_identity_review_seed_count": len(result.get("standards_specification_identity_review_seeds", [])),
        "install_requirement_claim_review_seed_count": len(result.get("install_requirement_claim_review_seeds", [])),
        "repair_service_safety_review_seed_count": len(result.get("repair_service_safety_review_seeds", [])),
        "access_rights_review_seed_count": len(result.get("access_rights_review_seeds", [])),
        "source_cache_review_seed_count": len(result.get("source_cache_review_seeds", [])),
        "evidence_candidate_review_seed_count": len(result.get("evidence_candidate_review_seeds", [])),
        "blocked_sources": list(result.get("blocked_sources", [])),
        "truth_boundary_errors": detect_h8_review_truth_boundary_violations(result),
        "product_boundary_errors": detect_h8_review_product_boundary_violations(result),
    }


def detect_h8_review_truth_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return sorted(dict.fromkeys(f"truth boundary violation: {path}=true" for path, key, value in _iter_key_values(result) if key in FORBIDDEN_TRUTH_TRUE_KEYS and value is True))


def detect_h8_review_product_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return sorted(dict.fromkeys(f"product boundary violation: {path}=true" for path, key, value in _iter_key_values(result) if key in FORBIDDEN_PRODUCT_TRUE_KEYS and value is True))


def _best_inputs_by_source(outputs: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    by_source: dict[str, dict[str, Any]] = {}
    for item in outputs:
        source_id = item.get("source_id")
        if source_id in H8_SOURCE_IDS:
            if item.get("schema_version") == "h8_manuals_docs_fixture_replay_result.v0":
                by_source[str(source_id)] = dict(item.get("normalized_record") or item)
            elif str(source_id) not in by_source:
                by_source[str(source_id)] = dict(item.get("normalized_record") or item)
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
    if source_id not in H8_SOURCE_IDS:
        raise ValueError(f"unknown or missing H8 source_id: {source_id}")
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
    config = H8_SOURCE_CONFIGS.get(source_id, {})
    return {
        "review_seed_id": f"h8.{kind}.review_seed.{source_id}.{_digest({'ref': subject_ref, 'kind': kind})[:12]}.v0",
        "wave_id": "H8",
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
        "technical_document_seed_accepts_document_truth": False,
        "manual_artifact_seed_accepts_relation_truth": False,
        "datasheet_device_seed_accepts_device_truth": False,
        "standards_specification_seed_accepts_standards_truth": False,
        "install_requirement_seed_accepts_installability_truth": False,
        "repair_service_safety_seed_accepts_safety_truth": False,
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
        "compatibility_correctness_claimed": False,
        "installability_claimed": False,
        "repair_safety_claimed": False,
        "electrical_safety_claimed": False,
        "malware_safety_claimed": False,
        "verified_authenticity_claimed": False,
        "production_readiness_claimed": False,
        "automatic_future_connector_approval": False,
        "accepted_document_truth": False,
        "accepted_manual_artifact_relation_truth": False,
        "accepted_datasheet_device_truth": False,
        "accepted_standards_truth": False,
        "accepted_install_requirement_truth": False,
        "accepted_repair_service_safety_truth": False,
        "accepted_access_rights_truth": False,
        "accepted_source_truth": False,
        "accepted_evidence_truth": False,
        "accepted_candidate_truth": False,
        "accepted_public_record": False,
        "technical_document_identity_candidate_is_truth": False,
        "manual_artifact_relation_candidate_is_truth": False,
        "datasheet_device_identity_candidate_is_truth": False,
        "standards_specification_candidate_is_truth": False,
        "install_requirement_candidate_is_installability_truth": False,
        "repair_service_safety_candidate_is_safety_truth": False,
        "repair_service_candidate_authorizes_action": False,
        "access_metadata_is_rights_truth": False,
        "open_access_metadata_is_rights_clearance": False,
        "documentation_completeness_verified": False,
        "standards_compliance_verified": False,
        "standards_conformance_verified": False,
        "access_rights_verified": False,
    }


def _product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_hosting": False,
        "enabled_live_probes": False,
        "enabled_source_sync": False,
        "enabled_downloads": False,
        "enabled_extraction": False,
        "enabled_crawling": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "enabled_scraping": False,
        "enabled_browser_automation": False,
        "network_calls_made": False,
        "api_calls_made": False,
        "api_query_used": False,
        "catalog_fetch_used": False,
        "document_fetch_used": False,
        "document_download_used": False,
        "manual_download_used": False,
        "pdf_download_used": False,
        "scan_download_used": False,
        "datasheet_download_used": False,
        "standards_document_download_used": False,
        "schematic_download_used": False,
        "service_manual_download_used": False,
        "full_text_fetch_used": False,
        "ocr_extraction_used": False,
        "iiif_fetch_used": False,
        "media_download_used": False,
        "scraping_used": False,
        "crawling_used": False,
        "browser_automation_used": False,
        "bypass_or_automation_used": False,
        "restricted_source_access_used": False,
        "repair_or_install_action_authorized": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def _raise_if_boundaries_fail(payload: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> None:
    errors = detect_h8_review_truth_boundary_violations(payload, policy)
    errors.extend(detect_h8_review_product_boundary_violations(payload, policy))
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

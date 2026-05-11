"""Offline H12 retro/community review integration helpers.

These helpers consume explicit fixture replay outputs plus blocked or approved
metadata-only live-probe outputs. They produce review seeds and planning
previews only; they do not call networks, query community archives, fetch
catalogs/forums/gated sources/web archives, download, extract, execute,
acquire, upload, submit hashes, scrape, crawl, access restricted sources,
accept truth, or mutate runtime state or indexes.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import hashlib
import json
from pathlib import Path
from typing import Any

from runtime.connectors.h12_retro_community.normalizer_common import (
    H12_SOURCE_CONFIGS,
    H12_SOURCE_IDS,
    PRODUCT_FORBIDDEN_TRUE_KEYS as H12_PRODUCT_FORBIDDEN_TRUE_KEYS,
    TRUTH_FORBIDDEN_TRUE_KEYS as H12_TRUTH_FORBIDDEN_TRUE_KEYS,
)

EXTRA_TRUTH_FORBIDDEN_TRUE_KEYS = set(['abandonware_label_is_legal_permission', 'accepted_archive_item_member_truth', 'accepted_candidate_truth', 'accepted_community_review_truth', 'accepted_compatibility_install_truth', 'accepted_evidence_truth', 'accepted_gated_source_access_truth', 'accepted_hash_checksum_truth', 'accepted_ia_wayback_corroboration_truth', 'accepted_platform_version_truth', 'accepted_public_record', 'accepted_retro_software_identity_truth', 'accepted_rights_safety_truth', 'accepted_source_truth', 'accepts_archive_item_member_truth', 'accepts_candidate_truth', 'accepts_community_review_truth', 'accepts_compatibility_install_truth', 'accepts_evidence_truth', 'accepts_gated_source_access_truth', 'accepts_hash_checksum_truth', 'accepts_ia_wayback_corroboration_truth', 'accepts_platform_version_truth', 'accepts_retro_software_identity_truth', 'accepts_rights_safety_truth', 'accepts_source_truth', 'archive_item_member_seed_accepts_file_truth', 'archive_item_member_verified', 'archive_item_metadata_grants_download_or_extraction_permission', 'automatic_future_connector_approval', 'candidate_promotion_preview_promotes_candidate', 'checksum_correctness_verified', 'community_download_metadata_grants_acquisition_permission', 'community_reputation_claimed', 'community_reputation_verified', 'community_review_comment_seed_accepts_truth', 'compatibility_correctness_verified', 'compatibility_install_note_seed_accepts_compatibility_truth', 'content_safety', 'content_safety_claimed', 'evidence_review_seed_accepts_evidence', 'exhaustive_global_coverage', 'file_authenticity_verified', 'future_connector_auto_approval', 'gated_source_boundary_seed_grants_access_permission', 'hash_checksum_seed_accepts_hash_truth', 'ia_wayback_seed_accepts_corroboration_truth', 'installability_verified', 'legal_acquisition_verified', 'malware_safety', 'malware_safety_claimed', 'master_index_mutated', 'mutated_master_index', 'mutated_public_index', 'platform_version_seed_accepts_version_truth', 'platform_version_verified', 'playability_verified', 'privacy_safety', 'privacy_safety_claimed', 'production_readiness_claim', 'production_readiness_claimed', 'production_retro_archive_coverage', 'production_search_quality', 'public_index_mutated', 'retro_software_identity_seed_accepts_software_truth', 'retro_software_identity_verified', 'review_seed_is_review_decision', 'rights_clearance', 'rights_clearance_claimed', 'rights_safety_seed_accepts_rights_safety_truth', 'source_cache_review_seed_accepts_source', 'source_pack_accepted', 'source_pack_imported', 'source_pack_preview_is_imported_or_submitted', 'source_pack_submitted', 'verified_authenticity', 'verified_authenticity_claimed'])
EXTRA_PRODUCT_FORBIDDEN_TRUE_KEYS = set(['acquisition_action_used', 'acquisition_permission', 'api_calls_made', 'bypass_or_automation_used', 'catalog_fetch_used', 'changed_public_search_behavior', 'crawling_used', 'download_used', 'enabled_accounts', 'enabled_acquisition_actions', 'enabled_crawling', 'enabled_downloads', 'enabled_execution', 'enabled_extraction', 'enabled_hosting', 'enabled_live_probes', 'enabled_source_sync', 'enabled_telemetry', 'enabled_uploads', 'enables_acquisition_actions', 'enables_api_catalog_sync', 'enables_downloads', 'enables_execution', 'enables_extraction', 'enables_forum_or_gated_fetch', 'enables_hash_submission', 'enables_restricted_source_access', 'enables_scraping_crawling', 'enables_uploads', 'execution_used', 'extraction_used', 'forum_comment_fetch_used', 'gated_source_access_used', 'hash_submission_used', 'mutated_master_index', 'mutated_public_index', 'mutates_master_index', 'mutates_public_index', 'network_calls_made', 'query_fetch_download_extract_execute_acquire_upload', 'restricted_source_access', 'restricted_source_access_used', 'scraping_used', 'upload_used'])
FORBIDDEN_TRUTH_TRUE_KEYS = set(H12_TRUTH_FORBIDDEN_TRUE_KEYS) | EXTRA_TRUTH_FORBIDDEN_TRUE_KEYS
FORBIDDEN_PRODUCT_TRUE_KEYS = set(H12_PRODUCT_FORBIDDEN_TRUE_KEYS) | EXTRA_PRODUCT_FORBIDDEN_TRUE_KEYS
REVIEW_SEED_KEYS = tuple(['retro_software_identity_review_seeds', 'platform_version_edition_review_seeds', 'archive_item_member_review_seeds', 'compatibility_install_note_review_seeds', 'community_review_comment_review_seeds', 'hash_checksum_review_seeds', 'ia_wayback_corroboration_review_seeds', 'gated_source_boundary_review_seeds', 'retro_rights_safety_review_seeds', 'source_cache_review_seeds', 'evidence_candidate_review_seeds'])


def load_h12_retro_community_outputs(paths: Sequence[str | Path]) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    for path_text in paths:
        path = Path(path_text)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            raise ValueError(f"{path} must contain a JSON object")
        outputs.append(dict(payload))
    return outputs


def build_h12_retro_software_identity_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("retro_software_identity", _source_id(inputs), _first_ref(inputs, "retro_software_identity_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h12_retro_software_identity_review_seed.v0",
        "review_subject_type": "retro_software_identity_candidate",
        "accepted_retro_software_identity_truth": False,
        "retro_software_identity_seed_accepts_software_truth": False,
        "limitations": _limitations(inputs) + ["Retro software identity review seed is not accepted software identity truth, file authenticity proof, rights proof, installability proof, playability proof, or safety proof."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed

def build_h12_platform_version_edition_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("platform_version_edition", _source_id(inputs), _first_ref(inputs, "platform_version_edition_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h12_platform_version_edition_review_seed.v0",
        "review_subject_type": "platform_version_edition_candidate",
        "accepted_platform_version_truth": False,
        "platform_version_seed_accepts_version_truth": False,
        "limitations": _limitations(inputs) + ["Platform/version/edition review seed is not platform, version, edition, compatibility, installability, or acquisition truth."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed

def build_h12_archive_item_member_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("archive_item_member", _source_id(inputs), _first_ref(inputs, "archive_item_member_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h12_archive_item_member_review_seed.v0",
        "review_subject_type": "archive_item_member_candidate",
        "accepted_archive_item_member_truth": False,
        "archive_item_member_seed_accepts_file_truth": False,
        "limitations": _limitations(inputs) + ["Archive item/member review seed is not file/member truth and grants no download, extraction, mirror, execution, or acquisition permission."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed

def build_h12_compatibility_install_note_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("compatibility_install_note", _source_id(inputs), _first_ref(inputs, "compatibility_install_note_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h12_compatibility_install_note_review_seed.v0",
        "review_subject_type": "compatibility_install_note_candidate",
        "accepted_compatibility_install_truth": False,
        "compatibility_install_note_seed_accepts_compatibility_truth": False,
        "limitations": _limitations(inputs) + ["Compatibility/install-note review seed is not compatibility correctness, installability, playability, execution permission, or action permission."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed

def build_h12_community_review_comment_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("community_review_comment", _source_id(inputs), _first_ref(inputs, "community_review_comment_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h12_community_review_comment_review_seed.v0",
        "review_subject_type": "community_review_comment_candidate",
        "accepted_community_review_truth": False,
        "community_review_comment_seed_accepts_truth": False,
        "limitations": _limitations(inputs) + ["Community review/comment review seed is not accepted claim truth, community reputation truth, quality proof, or write permission."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed

def build_h12_hash_checksum_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("hash_checksum", _source_id(inputs), _first_ref(inputs, "hash_checksum_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h12_hash_checksum_review_seed.v0",
        "review_subject_type": "hash_checksum_candidate",
        "accepted_hash_checksum_truth": False,
        "hash_checksum_seed_accepts_hash_truth": False,
        "limitations": _limitations(inputs) + ["Hash/checksum review seed is not identity truth, file authenticity proof, checksum correctness, legal acquisition, or malware safety."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed

def build_h12_ia_wayback_corroboration_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("ia_wayback_corroboration", _source_id(inputs), _first_ref(inputs, "ia_wayback_corroboration_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h12_ia_wayback_corroboration_review_seed.v0",
        "review_subject_type": "ia_wayback_corroboration_candidate",
        "accepted_ia_wayback_corroboration_truth": False,
        "ia_wayback_seed_accepts_corroboration_truth": False,
        "limitations": _limitations(inputs) + ["IA/Wayback corroboration review seed is not accepted corroboration truth, acquisition permission, rights proof, or authenticity proof."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed

def build_h12_gated_source_boundary_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("gated_source_boundary", _source_id(inputs), _first_ref(inputs, "gated_source_boundary_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h12_gated_source_boundary_review_seed.v0",
        "review_subject_type": "gated_source_boundary_candidate",
        "accepted_gated_source_access_truth": False,
        "gated_source_boundary_seed_grants_access_permission": False,
        "limitations": _limitations(inputs) + ["Gated-source boundary review seed does not grant account, gated-source, private, invitation-only, or restricted-source access permission."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed

def build_h12_retro_rights_safety_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("retro_rights_safety", _source_id(inputs), _first_ref(inputs, "retro_rights_safety_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h12_retro_rights_safety_review_seed.v0",
        "review_subject_type": "retro_rights_safety_candidate",
        "accepted_rights_safety_truth": False,
        "rights_safety_seed_accepts_rights_safety_truth": False,
        "limitations": _limitations(inputs) + ["Retro rights/safety review seed is not rights clearance, legal acquisition truth, malware safety, content safety, privacy safety, or production readiness."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h12_source_cache_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("source_cache", _source_id(inputs), _first_ref(inputs, "source_cache_candidate_preview", "preview_id"), inputs)
    seed.update({
        "schema_version": "h12_source_cache_review_seed.v0",
        "review_subject_type": "source_cache_candidate_preview",
        "accepted_source_truth": False,
        "source_cache_review_seed_accepts_source": False,
        "source_cache_write_allowed_current": False,
        "limitations": _limitations(inputs) + ["Source-cache review seed is not accepted source truth and does not write the source cache."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h12_evidence_candidate_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("evidence_candidate", _source_id(inputs), _first_ref(inputs, "evidence_candidate_preview", "preview_id"), inputs)
    seed.update({
        "schema_version": "h12_evidence_candidate_review_seed.v0",
        "review_subject_type": "evidence_candidate_preview",
        "accepted_evidence_truth": False,
        "evidence_review_seed_accepts_evidence": False,
        "evidence_ledger_write_allowed_current": False,
        "limitations": _limitations(inputs) + ["Evidence candidate review seed is not accepted evidence and does not write the evidence ledger."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h12_candidate_promotion_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = {
        "schema_version": "h12_candidate_promotion_preview.v0",
        "candidate_promotion_preview_id": f"h12.candidate_promotion.{source_id}.{_digest(inputs)[:12]}.v0",
        "source_id": source_id,
        "preview_only": True,
        "promotes_candidate": False,
        "candidate_promotion_preview_promotes_candidate": False,
        "accepted_candidate_truth": False,
        "review_required_before_promotion": True,
        "limitations": _limitations(inputs) + ["Candidate promotion preview does not promote, accept, publish, persist, download, extract, execute, acquire, upload, or submit hashes for any retro/community candidate."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h12_coverage_update_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = {
        "schema_version": "h12_source_coverage_update_preview.v0",
        "coverage_update_preview_id": f"h12.coverage_update.{source_id}.{_digest(inputs)[:12]}.v0",
        "source_id": source_id,
        "coverage_basis": "fixture_review_and_blocked_live_probe_evidence",
        "coverage_preview_only": True,
        "coverage_manifest_is_exhaustive_global_coverage": False,
        "production_retro_archive_coverage": False,
        "limitations": ["Coverage update preview is not exhaustive global coverage, production retro/community archive coverage, identity proof, rights proof, safety proof, or acquisition proof."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h12_connector_scorecard_update(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    update = {
        "schema_version": "h12_connector_scorecard_update.v0",
        "connector_scorecard_update_id": f"h12.scorecard_update.{source_id}.{_digest(inputs)[:12]}.v0",
        "source_id": source_id,
        "fixture_replay_status": "integrated",
        "live_probe_status": "blocked_or_dry_preflight_without_approval",
        "review_integration_status": "preview_created",
        "production_ready": False,
        "auto_approves_future_connectors": False,
        "automatic_future_connector_approval": False,
        "limitations": ["Connector scorecard update is not production readiness, acquisition permission, rights clearance, safety proof, or future connector approval."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_boundaries_fail(update, policy)
    return update


def build_h12_source_pack_update_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = {
        "schema_version": "h12_source_pack_update_preview.v0",
        "source_pack_update_preview_id": f"h12.source_pack_update.{source_id}.{_digest(inputs)[:12]}.v0",
        "source_id": source_id,
        "preview_only": True,
        "source_pack_imported": False,
        "source_pack_submitted": False,
        "source_pack_accepted": False,
        "source_pack_preview_is_imported_or_submitted": False,
        "limitations": ["Source pack update preview is not import, submission, acceptance, public truth, source sync, download, extraction, execution, acquisition, upload, hash submission, gated-source access, or restricted-source access permission."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h12_review_integration_result(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    outputs = list(inputs.get("outputs") or [])
    input_refs = list(inputs.get("input_refs") or [])
    by_source = _best_inputs_by_source(outputs)
    sources = [source for source in H12_SOURCE_IDS if source in by_source] or list(H12_SOURCE_IDS)
    fixture_outputs = [_output_summary(item) for item in outputs if item.get("schema_version") == "h12_retro_community_fixture_replay_result.v0"]
    live_outputs = [_output_summary(item) for item in outputs if item.get("schema_version") == "h12_retro_community_live_probe_result.v0"]
    blocked_sources = sorted({str(item.get("source_id")) for item in outputs if str(item.get("result_status", "")).startswith("blocked") and item.get("source_id") in H12_SOURCE_IDS})
    seed_inputs = [by_source.get(source_id, {"source_id": source_id}) for source_id in sources]
    result = {
        "schema_version": "h12_retro_community_review_integration_result.v0",
        "review_integration_result_id": f"h12.review_integration.{_digest({'sources': sources, 'inputs': input_refs})[:12]}.v0",
        "wave_id": "H12",
        "sources": sources,
        "source_count": len(sources),
        "input_refs": input_refs,
        "used_fixture_outputs": fixture_outputs,
        "used_live_probe_outputs": live_outputs,
        "retro_software_identity_review_seeds": [build_h12_retro_software_identity_review_seed(item, policy) for item in seed_inputs],
        "platform_version_edition_review_seeds": [build_h12_platform_version_edition_review_seed(item, policy) for item in seed_inputs],
        "archive_item_member_review_seeds": [build_h12_archive_item_member_review_seed(item, policy) for item in seed_inputs],
        "compatibility_install_note_review_seeds": [build_h12_compatibility_install_note_review_seed(item, policy) for item in seed_inputs],
        "community_review_comment_review_seeds": [build_h12_community_review_comment_review_seed(item, policy) for item in seed_inputs],
        "hash_checksum_review_seeds": [build_h12_hash_checksum_review_seed(item, policy) for item in seed_inputs],
        "ia_wayback_corroboration_review_seeds": [build_h12_ia_wayback_corroboration_review_seed(item, policy) for item in seed_inputs],
        "gated_source_boundary_review_seeds": [build_h12_gated_source_boundary_review_seed(item, policy) for item in seed_inputs],
        "retro_rights_safety_review_seeds": [build_h12_retro_rights_safety_review_seed(item, policy) for item in seed_inputs],
        "source_cache_review_seeds": [build_h12_source_cache_review_seed(item, policy) for item in seed_inputs],
        "evidence_candidate_review_seeds": [build_h12_evidence_candidate_review_seed(item, policy) for item in seed_inputs],
        "candidate_promotion_previews": [build_h12_candidate_promotion_preview(item, policy) for item in seed_inputs],
        "coverage_update_previews": [build_h12_coverage_update_preview(item, policy) for item in seed_inputs],
        "scorecard_updates": [build_h12_connector_scorecard_update(item, policy) for item in seed_inputs],
        "source_pack_update_previews": [build_h12_source_pack_update_preview(item, policy) for item in seed_inputs],
        "blocked_sources": blocked_sources,
        "warnings": ["H12 live probes remain blocked pending operator approval."] if blocked_sources else [],
        "limitations": [
            "H12 review integration is a wave-level audit and rehearsal, not promotion.",
            "Fixture replay and blocked/preflight live-probe reports do not prove retro software identity, platform/version/edition truth, archive item/member truth, file authenticity, checksum correctness, compatibility correctness, installability, playability, legal acquisition, rights clearance, malware safety, content safety, privacy safety, community reputation, production coverage, or live endpoint behavior.",
        ],
        "accepts_retro_software_identity_truth": False,
        "accepts_platform_version_truth": False,
        "accepts_archive_item_member_truth": False,
        "accepts_compatibility_install_truth": False,
        "accepts_community_review_truth": False,
        "accepts_hash_checksum_truth": False,
        "accepts_ia_wayback_corroboration_truth": False,
        "accepts_gated_source_access_truth": False,
        "accepts_rights_safety_truth": False,
        "accepts_source_truth": False,
        "accepts_evidence_truth": False,
        "accepts_candidate_truth": False,
        "mutates_public_index": False,
        "mutates_master_index": False,
        "enables_api_catalog_sync": False,
        "enables_forum_or_gated_fetch": False,
        "enables_downloads": False,
        "enables_extraction": False,
        "enables_execution": False,
        "enables_acquisition_actions": False,
        "enables_uploads": False,
        "enables_hash_submission": False,
        "enables_scraping_crawling": False,
        "enables_restricted_source_access": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Review seeds and previews require explicit human review before any downstream persistence."],
    }
    _raise_if_boundaries_fail(result, policy)
    return result


def summarize_h12_review_integration(result: Mapping[str, Any]) -> dict[str, Any]:
    truth_errors = detect_h12_review_truth_boundary_violations(result)
    product_errors = detect_h12_review_product_boundary_violations(result)
    return {
        "schema_version": "h12_review_integration_summary.v0",
        "status": "pass" if not truth_errors and not product_errors else "invalid",
        "review_integration_result_id": result.get("review_integration_result_id"),
        "source_count": len(result.get("sources", [])),
        "retro_software_identity_review_seed_count": len(result.get("retro_software_identity_review_seeds", [])),
        "platform_version_edition_review_seed_count": len(result.get("platform_version_edition_review_seeds", [])),
        "archive_item_member_review_seed_count": len(result.get("archive_item_member_review_seeds", [])),
        "compatibility_install_note_review_seed_count": len(result.get("compatibility_install_note_review_seeds", [])),
        "community_review_comment_review_seed_count": len(result.get("community_review_comment_review_seeds", [])),
        "hash_checksum_review_seed_count": len(result.get("hash_checksum_review_seeds", [])),
        "ia_wayback_corroboration_review_seed_count": len(result.get("ia_wayback_corroboration_review_seeds", [])),
        "gated_source_boundary_review_seed_count": len(result.get("gated_source_boundary_review_seeds", [])),
        "retro_rights_safety_review_seed_count": len(result.get("retro_rights_safety_review_seeds", [])),
        "source_cache_review_seed_count": len(result.get("source_cache_review_seeds", [])),
        "evidence_candidate_review_seed_count": len(result.get("evidence_candidate_review_seeds", [])),
        "blocked_sources": list(result.get("blocked_sources", [])),
        "truth_boundary_errors": truth_errors,
        "product_boundary_errors": product_errors,
    }


def detect_h12_review_truth_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return sorted(dict.fromkeys(f"truth boundary violation: {path}=true" for path, key, value in _iter_key_values(result) if key in FORBIDDEN_TRUTH_TRUE_KEYS and value is True))


def detect_h12_review_product_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return sorted(dict.fromkeys(f"product boundary violation: {path}=true" for path, key, value in _iter_key_values(result) if key in FORBIDDEN_PRODUCT_TRUE_KEYS and value is True))


def _best_inputs_by_source(outputs: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    by_source: dict[str, dict[str, Any]] = {}
    for item in outputs:
        source_id = item.get("source_id")
        if source_id in H12_SOURCE_IDS:
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
    if source_id not in H12_SOURCE_IDS:
        raise ValueError(f"unknown or missing H12 source_id: {source_id}")
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
    config = H12_SOURCE_CONFIGS.get(source_id, {})
    return {
        "review_seed_id": f"h12.{kind}.review_seed.{source_id}.{_digest({'ref': subject_ref, 'kind': kind})[:12]}.v0",
        "wave_id": "H12",
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
    return {key: False for key in FORBIDDEN_TRUTH_TRUE_KEYS}


def _product_boundary() -> dict[str, bool]:
    return {key: False for key in FORBIDDEN_PRODUCT_TRUE_KEYS}


def _raise_if_boundaries_fail(payload: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> None:
    errors = detect_h12_review_truth_boundary_violations(payload, policy)
    errors.extend(detect_h12_review_product_boundary_violations(payload, policy))
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

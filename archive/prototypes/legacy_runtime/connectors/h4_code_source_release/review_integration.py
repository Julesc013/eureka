"""Offline H4 code/source/release review integration helpers.

These helpers consume explicit H4 fixture replay outputs and blocked or
approved metadata-only live-probe outputs. They create review seeds and
planning previews only; they do not call networks, clone repositories,
run git/build tools, download artifacts, accept truth, or mutate runtime
state or indexes.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from archive.prototypes.legacy_runtime.connectors.h4_code_source_release.normalizer_common import H4_SOURCE_IDS


FORBIDDEN_TRUTH_TRUE_KEYS = {
    "accepted_candidate_truth",
    "accepted_evidence",
    "accepted_evidence_truth",
    "accepted_public_record",
    "accepted_public_truth",
    "accepted_release_identity_truth",
    "accepted_source_identity_truth",
    "accepted_source_to_binary_provenance",
    "accepted_source_to_binary_relation_truth",
    "accepted_source_truth",
    "accepts_authenticity_truth",
    "accepts_build_reproducibility_truth",
    "accepts_candidate_truth",
    "accepts_evidence_truth",
    "accepts_release_identity_truth",
    "accepts_source_identity_truth",
    "accepts_source_to_binary_provenance",
    "accepts_source_truth",
    "asset_hash_proves_malware_safety",
    "asset_presence_proves_source_relationship",
    "automatic_future_connector_approval",
    "build_reproducibility_verified",
    "candidate_promotion_preview_promotes_candidate",
    "evidence_review_seed_accepts_evidence",
    "future_connector_auto_approval",
    "git_object_candidate_is_accepted_provenance",
    "git_object_candidate_is_provenance_truth",
    "license_metadata_is_rights_clearance",
    "malware_safety_claimed",
    "master_index_mutated",
    "mutates_master_index",
    "mutates_public_index",
    "normalized_record_is_public_truth",
    "production_readiness_claimed",
    "public_index_mutated",
    "relation_candidate_is_accepted_provenance",
    "release_asset_hash_candidate_is_malware_safety",
    "release_asset_metadata_grants_download_permission",
    "release_asset_seed_grants_download_or_safety",
    "release_authenticity_verified",
    "release_identity_candidate_is_accepted_release_truth",
    "release_identity_candidate_is_truth",
    "release_identity_seed_accepts_release_truth",
    "release_notes_prove_installability",
    "repository_url_proves_official_status",
    "rights_clearance_claimed",
    "sbom_metadata_is_provenance",
    "sbom_signature_metadata_proves_trust",
    "signature_metadata_is_authenticity",
    "signature_metadata_proves_authenticity",
    "source_authenticity_verified",
    "source_cache_review_seed_accepts_source",
    "source_identity_candidate_is_accepted_identity",
    "source_identity_candidate_is_truth",
    "source_identity_seed_accepts_identity",
    "source_pack_preview_is_imported_or_submitted",
    "source_to_binary_provenance_verified",
    "source_to_binary_relation_candidate_is_provenance_truth",
    "source_to_binary_seed_accepts_provenance",
    "swhid_candidate_is_accepted_object_truth",
    "swhid_candidate_is_object_truth",
    "tag_release_match_proves_build_relation",
    "verified_authenticity_claimed",
    "verified_build_reproducibility_claimed",
    "verified_installability_claimed",
}

FORBIDDEN_PRODUCT_TRUE_KEYS = {
    "api_calls_made",
    "build_tool_invoked",
    "build_tool_invocation_enabled",
    "changed_public_search_behavior",
    "downloads_made",
    "enabled_accounts",
    "enabled_downloads",
    "enabled_execution",
    "enabled_hosting",
    "enabled_installers",
    "enabled_live_probes",
    "enabled_model_provider_calls",
    "enabled_public_query_fanout",
    "enabled_repository_clone",
    "enabled_scraping",
    "enabled_source_connectors",
    "enabled_source_sync",
    "enabled_telemetry",
    "enabled_uploads",
    "enables_build_tools",
    "enables_git_commands",
    "enables_install_execute",
    "enables_release_asset_downloads",
    "enables_repository_clone",
    "enables_source_archive_downloads",
    "evidence_ledger_runtime_mutated",
    "git_command_invoked",
    "git_command_invocation_enabled",
    "install_execute_enabled",
    "install_execute_used",
    "model_provider_calls_made",
    "mutated_master_index",
    "mutated_public_index",
    "network_calls_made",
    "network_used",
    "release_asset_download_enabled",
    "release_asset_download_used",
    "repository_clone_enabled",
    "repository_clone_used",
    "review_queue_runtime_mutated",
    "source_archive_download_enabled",
    "source_archive_download_used",
    "source_cache_runtime_mutated",
    "source_sync_enabled",
}


def load_h4_code_source_outputs(paths: Sequence[str | Path]) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    for path_text in paths:
        path = Path(path_text)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            raise ValueError(f"{path} must contain a JSON object")
        outputs.append(dict(payload))
    return outputs


def build_h4_source_identity_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    record = _record_from_inputs(inputs)
    identity = _source_identity_from_inputs(inputs, record)
    source_id = _source_id(identity or record or inputs)
    native_id = str((identity or record).get("source_native_id") or (identity or record).get("source_identity_candidate_id") or "unknown")
    seed = {
        "schema_version": "h4_source_identity_review_seed.v0",
        "review_seed_id": f"h4.source_identity_review_seed.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "review_subject_type": "source_identity_candidate",
        "review_subject_ref": identity.get("source_identity_candidate_id"),
        "source_host": identity.get("source_host") or record.get("source_host"),
        "owner_or_namespace": identity.get("owner_or_namespace") or record.get("owner_or_namespace"),
        "repository_name": identity.get("repository_name") or record.get("repository_name"),
        "project_name": identity.get("project_name") or record.get("project_name"),
        "repository_url_candidate": identity.get("repository_url_candidate") or record.get("repository_url_candidate"),
        "git_commit_id_candidate": identity.get("git_commit_id_candidate") or record.get("git_commit_id_candidate"),
        "swhid_candidate": identity.get("swhid_candidate") or record.get("swhid_candidate"),
        "input_basis": _input_basis(inputs),
        "review_seed_status": "needs_review",
        "review_required": True,
        "accepted_source_identity_truth": False,
        "source_identity_seed_accepts_identity": False,
        "git_object_candidate_is_provenance_truth": False,
        "swhid_candidate_is_object_truth": False,
        "repository_url_proves_official_status": False,
        "limitations": _limitations(inputs) + ["Source identity review seed is not accepted source identity truth or provenance."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H4 source identity review seed is a local review preview only."],
    }
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h4_release_identity_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    record = _record_from_inputs(inputs)
    release = _release_identity_from_inputs(inputs, record)
    source_id = _source_id(release or record or inputs)
    release_id = str((release or record).get("release_id") or (release or record).get("release_identity_candidate_id") or "unknown")
    seed = {
        "schema_version": "h4_release_identity_review_seed.v0",
        "review_seed_id": f"h4.release_identity_review_seed.{source_id}.{_slug(release_id)}.v0",
        "source_id": source_id,
        "review_subject_type": "release_identity_candidate",
        "review_subject_ref": release.get("release_identity_candidate_id"),
        "release_id": release_id,
        "release_tag": release.get("release_tag") or record.get("release_tag"),
        "release_name": release.get("release_name") or record.get("release_name"),
        "release_version": release.get("release_version") or record.get("release_version"),
        "release_timestamp": release.get("release_timestamp") or record.get("release_timestamp"),
        "input_basis": _input_basis(inputs),
        "review_seed_status": "needs_review",
        "review_required": True,
        "accepted_release_identity_truth": False,
        "release_identity_seed_accepts_release_truth": False,
        "release_authenticity_verified": False,
        "release_notes_prove_installability": False,
        "limitations": _limitations(inputs) + ["Release identity review seed is not accepted release truth, authenticity, availability, compatibility, or installability."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H4 release identity review seed is candidate-only."],
    }
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h4_source_to_binary_relation_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    record = _record_from_inputs(inputs)
    relations = _relation_candidates_from_inputs(inputs, record)
    relation = relations[0] if relations else {"source_id": _source_id(record or inputs), "relation_kind": "not_evaluable"}
    source_id = _source_id(relation or record or inputs)
    relation_kind = str(relation.get("relation_kind") or "not_evaluable")
    seed = {
        "schema_version": "h4_source_to_binary_relation_review_seed.v0",
        "review_seed_id": f"h4.source_to_binary_review_seed.{source_id}.{_slug(relation_kind)}.{_digest(relation)[:8]}.v0",
        "source_id": source_id,
        "review_subject_type": "source_to_binary_relation_candidate",
        "review_subject_ref": relation.get("relation_candidate_id"),
        "relation_kind": relation_kind,
        "source_commit_ref": relation.get("source_commit_ref", "unknown"),
        "source_tag_ref": relation.get("source_tag_ref", "unknown"),
        "binary_asset_ref": relation.get("binary_asset_ref", "unknown"),
        "input_basis": _input_basis(inputs),
        "review_seed_status": "needs_review",
        "review_required": True,
        "accepted_source_to_binary_provenance": False,
        "source_to_binary_seed_accepts_provenance": False,
        "tag_release_match_proves_build_relation": False,
        "asset_presence_proves_source_relationship": False,
        "limitations": _limitations(inputs) + ["Source-to-binary relation review seed is not accepted provenance or build reproducibility."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H4 relation review seed remains a candidate-only preview."],
    }
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h4_release_asset_candidate_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    record = _record_from_inputs(inputs)
    assets = _asset_candidates_from_inputs(inputs, record)
    asset = assets[0] if assets else {"source_id": _source_id(record or inputs), "asset_name": "no_release_asset_candidate_observed"}
    source_id = _source_id(asset or record or inputs)
    asset_name = str(asset.get("asset_name") or "unknown")
    seed = {
        "schema_version": "h4_release_asset_candidate_review_seed.v0",
        "review_seed_id": f"h4.release_asset_review_seed.{source_id}.{_slug(asset_name)}.v0",
        "source_id": source_id,
        "review_subject_type": "release_asset_candidate",
        "review_subject_ref": asset.get("release_asset_candidate_id"),
        "asset_name": asset_name,
        "asset_kind": asset.get("asset_kind", "unknown"),
        "asset_size": asset.get("asset_size", "unknown"),
        "download_allowed_current": False,
        "payload_available_current": False,
        "input_basis": _input_basis(inputs),
        "review_seed_status": "needs_review",
        "review_required": True,
        "release_asset_seed_grants_download_or_safety": False,
        "release_asset_hash_candidate_is_malware_safety": False,
        "signature_metadata_proves_authenticity": False,
        "sbom_metadata_is_provenance": False,
        "limitations": _limitations(inputs) + ["Release asset review seed grants no download permission and proves no malware safety, authenticity, or provenance."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H4 release asset review seed is metadata-only."],
    }
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h4_source_cache_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    record = _record_from_inputs(inputs)
    source_cache = _source_cache_from_inputs(inputs, record)
    source_id = _source_id(source_cache or record or inputs)
    native_id = str(record.get("source_native_id") or source_cache.get("candidate_id") or "unknown")
    seed = {
        "schema_version": "h4_source_cache_review_seed.v0",
        "review_seed_id": f"h4.source_cache_review_seed.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "review_subject_type": "source_cache_candidate_preview",
        "review_subject_ref": source_cache.get("candidate_id"),
        "input_basis": _input_basis(inputs),
        "review_seed_status": "needs_review",
        "review_required": True,
        "source_cache_runtime_mutated": False,
        "accepted_source_truth": False,
        "source_cache_review_seed_accepts_source": False,
        "limitations": _limitations(inputs) + ["Source-cache review seed is not source cache persistence or source truth."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H4 source-cache review seed is a preview only."],
    }
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h4_evidence_candidate_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    record = _record_from_inputs(inputs)
    evidence = _evidence_from_inputs(inputs, record)
    source_id = _source_id(evidence or record or inputs)
    native_id = str(record.get("source_native_id") or evidence.get("evidence_preview_id") or "unknown")
    seed = {
        "schema_version": "h4_evidence_candidate_review_seed.v0",
        "review_seed_id": f"h4.evidence_review_seed.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "review_subject_type": "evidence_candidate_preview",
        "review_subject_ref": evidence.get("evidence_preview_id"),
        "input_basis": _input_basis(inputs),
        "review_seed_status": "needs_review",
        "review_required": True,
        "evidence_ledger_runtime_mutated": False,
        "accepted_evidence": False,
        "evidence_review_seed_accepts_evidence": False,
        "limitations": _limitations(inputs) + ["Evidence candidate review seed is not evidence acceptance."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H4 evidence review seed is a candidate-only preview."],
    }
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h4_candidate_promotion_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    preview = {
        "schema_version": "h4_candidate_promotion_preview.v0",
        "candidate_promotion_preview_id": f"h4.candidate_promotion_preview.{_digest(inputs)[:12]}.v0",
        "wave_id": "H4",
        "preview_status": "not_ready_review_required",
        "source_identity_review_seed_count": len(_list(inputs.get("source_identity_review_seeds"))),
        "release_identity_review_seed_count": len(_list(inputs.get("release_identity_review_seeds"))),
        "source_to_binary_relation_review_seed_count": len(_list(inputs.get("source_to_binary_relation_review_seeds"))),
        "release_asset_candidate_review_seed_count": len(_list(inputs.get("release_asset_candidate_review_seeds"))),
        "source_cache_review_seed_count": len(_list(inputs.get("source_cache_review_seeds"))),
        "evidence_candidate_review_seed_count": len(_list(inputs.get("evidence_candidate_review_seeds"))),
        "review_required": True,
        "candidate_promotion_preview_promotes_candidate": False,
        "accepted_candidate_truth": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "allowed_next_actions": ["human_review", "h5_policy_pack_planning"],
        "forbidden_next_actions": ["accept_candidate", "mutate_public_index", "mutate_master_index", "clone_repository", "download_source_archive", "download_release_asset", "run_git_or_build"],
        "limitations": ["Promotion preview does not promote or accept any candidate."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H4 promotion preview is rehearsal evidence only."],
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h4_coverage_update_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = str(inputs.get("source_id") or "h4_code_source_release")
    normalized_count = int(inputs.get("records_normalized", 1 if inputs.get("normalized_record_ref") else 0))
    preview = {
        "schema_version": "h4_source_coverage_update_preview.v0",
        "coverage_update_preview_id": f"h4.coverage_update.{source_id}.{_digest(inputs)[:10]}.v0",
        "source_id": source_id,
        "coverage_basis": str(inputs.get("coverage_basis", "fixture_only")),
        "coverage_depth_current": str(inputs.get("coverage_depth_current", "D2_metadata_indexed" if normalized_count else "D0_source_known")),
        "records_seen": int(inputs.get("records_seen", normalized_count)),
        "records_normalized": normalized_count,
        "repositories_cloned": 0,
        "source_archives_downloaded": 0,
        "release_assets_downloaded": 0,
        "git_commands_invoked": 0,
        "build_tools_invoked": 0,
        "coverage_manifest_is_exhaustive_global_coverage": False,
        "review_required": True,
        "limitations": _limitations(inputs) + ["Coverage update preview is bounded and not production or exhaustive coverage."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Coverage preview does not mutate coverage ledgers or indexes."],
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h4_connector_scorecard_update(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = str(inputs.get("source_id") or "h4_code_source_release")
    blocked = bool(_blocked_reasons(inputs))
    update = {
        "schema_version": "h4_connector_scorecard_update.v0",
        "connector_scorecard_update_id": f"h4.scorecard_update.{source_id}.{_digest(inputs)[:10]}.v0",
        "source_id": source_id,
        "scorecard_update_status": "blocked_live_probe_reviewed" if blocked else "fixture_review_integrated",
        "fixture_replay_status": "passed" if inputs.get("fixture_replay_used", True) else "not_used",
        "live_probe_status": str(inputs.get("live_probe_status", "blocked_or_not_used")),
        "review_integration_status": "preview_created",
        "quality_delta_status": "created",
        "repository_clone_status": "forbidden_current",
        "source_archive_download_status": "forbidden_current",
        "release_asset_download_status": "forbidden_current",
        "git_command_invocation_status": "forbidden_current",
        "build_tool_invocation_status": "forbidden_current",
        "production_ready": False,
        "auto_approves_future_connectors": False,
        "metrics": {
            "source_identity_review_seed_count": int(inputs.get("source_identity_review_seed_count", 1)),
            "release_identity_review_seed_count": int(inputs.get("release_identity_review_seed_count", 1)),
            "source_to_binary_relation_review_seed_count": int(inputs.get("source_to_binary_relation_review_seed_count", 1)),
            "release_asset_review_seed_count": int(inputs.get("release_asset_review_seed_count", 0)),
            "source_cache_candidate_count": int(inputs.get("source_cache_candidate_count", 1)),
            "evidence_candidate_count": int(inputs.get("evidence_candidate_count", 1)),
            "policy_block_count": len(_blocked_reasons(inputs)),
            "warning_count": int(inputs.get("warning_count", 0)),
        },
        "limitations": _limitations(inputs) + ["Scorecard update is not production readiness."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Scorecard update summarizes review previews only."],
    }
    _raise_if_boundaries_fail(update, policy)
    return update


def build_h4_source_pack_update_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_ids = sorted({str(item) for item in _list(inputs.get("sources")) if item})
    preview = {
        "schema_version": "h4_source_pack_update_preview.v0",
        "source_pack_update_preview_id": f"h4.source_pack_update.{_digest(inputs)[:12]}.v0",
        "wave_id": "H4",
        "sources": source_ids,
        "pack_update_status": "draft_update_preview",
        "source_pack_imported": False,
        "source_pack_submitted": False,
        "source_pack_accepted": False,
        "source_pack_preview_is_imported_or_submitted": False,
        "review_required": True,
        "limitations": ["Source pack update remains a preview and is not imported, submitted, or accepted."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Source pack update preview is planning evidence only."],
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h4_review_integration_result(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    raw_outputs = [deepcopy(dict(item)) for item in _list(inputs.get("outputs")) if isinstance(item, Mapping)]
    records = [_record_from_inputs(item) for item in raw_outputs if _record_from_inputs(item)]
    sources = sorted({source for source in (_source_id(item) for item in records) if source != "unknown_source"} or set(H4_SOURCE_IDS))
    fixture_outputs = [item for item in raw_outputs if item.get("schema_version") == "h4_code_source_fixture_replay_result.v0"]
    live_outputs = [item for item in raw_outputs if item.get("schema_version") == "h4_code_source_live_probe_result.v0"]
    blocked_sources = sorted({str(item.get("source_id")) for item in live_outputs if str(item.get("result_status", "")).startswith("blocked") and item.get("source_id")})
    source_identity_seeds = [build_h4_source_identity_review_seed(record, policy) for record in records]
    release_identity_seeds = [build_h4_release_identity_review_seed(record, policy) for record in records]
    relation_seeds = [build_h4_source_to_binary_relation_review_seed(candidate, policy) for record in records for candidate in _relation_candidates_from_inputs(record, record)]
    asset_seeds = [build_h4_release_asset_candidate_review_seed(candidate, policy) for record in records for candidate in _asset_candidates_from_inputs(record, record)]
    if not asset_seeds and records:
        asset_seeds = [build_h4_release_asset_candidate_review_seed({"source_id": _source_id(records[0]), "asset_name": "no_release_asset_candidate_observed", "limitations": ["No release asset candidate was observed in the fixture replay output."]}, policy)]
    source_cache_seeds = [build_h4_source_cache_review_seed(record, policy) for record in records]
    evidence_seeds = [build_h4_evidence_candidate_review_seed(record, policy) for record in records]
    coverage_updates = [
        build_h4_coverage_update_preview(
            {
                "source_id": _source_id(record),
                "normalized_record_ref": record.get("normalized_record_id"),
                "records_seen": 1,
                "records_normalized": 1,
                "coverage_basis": "fixture_only",
                "limitations": _limitations(record),
            },
            policy,
        )
        for record in records
    ]
    scorecard_updates = [
        build_h4_connector_scorecard_update(
            {
                "source_id": _source_id(record),
                "fixture_replay_used": True,
                "live_probe_status": "blocked_or_not_used" if _source_id(record) in blocked_sources else "not_used",
                "source_identity_review_seed_count": 1,
                "release_identity_review_seed_count": 1,
                "source_to_binary_relation_review_seed_count": len(_relation_candidates_from_inputs(record, record)),
                "release_asset_review_seed_count": len(_asset_candidates_from_inputs(record, record)),
                "source_cache_candidate_count": 1,
                "evidence_candidate_count": 1,
                "blocked_reasons": blocked_sources if _source_id(record) in blocked_sources else [],
            },
            policy,
        )
        for record in records
    ]
    promotion = build_h4_candidate_promotion_preview(
        {
            "source_identity_review_seeds": source_identity_seeds,
            "release_identity_review_seeds": release_identity_seeds,
            "source_to_binary_relation_review_seeds": relation_seeds,
            "release_asset_candidate_review_seeds": asset_seeds,
            "source_cache_review_seeds": source_cache_seeds,
            "evidence_candidate_review_seeds": evidence_seeds,
            "blocked_reasons": _blocked_reasons(raw_outputs),
        },
        policy,
    )
    pack_preview = build_h4_source_pack_update_preview({"sources": sources}, policy)
    result = {
        "schema_version": "h4_code_source_review_integration_result.v0",
        "review_integration_result_id": f"h4.review_integration.{_digest(raw_outputs)[:12]}.v0",
        "wave_id": "H4",
        "sources": sources,
        "input_refs": _list(inputs.get("input_refs")),
        "used_fixture_outputs": [{"source_id": item.get("source_id"), "ref": item.get("replay_result_id")} for item in fixture_outputs],
        "used_live_probe_outputs": [{"source_id": item.get("source_id"), "ref": item.get("live_probe_result_id"), "status": item.get("result_status")} for item in live_outputs],
        "source_identity_review_seeds": source_identity_seeds,
        "release_identity_review_seeds": release_identity_seeds,
        "source_to_binary_relation_review_seeds": relation_seeds,
        "release_asset_candidate_review_seeds": asset_seeds,
        "source_cache_review_seeds": source_cache_seeds,
        "evidence_candidate_review_seeds": evidence_seeds,
        "candidate_promotion_previews": [promotion],
        "coverage_update_previews": coverage_updates,
        "scorecard_updates": scorecard_updates,
        "source_pack_update_previews": [pack_preview],
        "blocked_sources": blocked_sources,
        "warnings": list(inputs.get("warnings", [])),
        "limitations": [
            "Review integration uses explicit committed H4 outputs only.",
            "Review seeds are not review decisions.",
            "Fixture-equivalent H4 outputs support H5 planning, not public truth.",
            "Blocked live probes record missing operator approval only.",
        ],
        "accepts_source_identity_truth": False,
        "accepts_release_identity_truth": False,
        "accepts_source_to_binary_provenance": False,
        "accepts_source_truth": False,
        "accepts_evidence_truth": False,
        "accepts_candidate_truth": False,
        "accepts_authenticity_truth": False,
        "accepts_build_reproducibility_truth": False,
        "mutates_public_index": False,
        "mutates_master_index": False,
        "enables_repository_clone": False,
        "enables_source_archive_downloads": False,
        "enables_release_asset_downloads": False,
        "enables_git_commands": False,
        "enables_build_tools": False,
        "enables_install_execute": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H4 review integration mutates no source cache, evidence ledger, review queue, public index, or master index."],
    }
    _raise_if_boundaries_fail(result, policy)
    return result


def summarize_h4_review_integration(result: Mapping[str, Any]) -> dict[str, Any]:
    violations = detect_h4_review_truth_boundary_violations(result, None) + detect_h4_review_product_boundary_violations(result, None)
    return {
        "schema_version": "h4_review_integration_summary.v0",
        "status": "pass" if not violations else "invalid",
        "wave_id": result.get("wave_id", "H4"),
        "source_count": len(result.get("sources", [])),
        "source_identity_review_seed_count": len(result.get("source_identity_review_seeds", [])),
        "release_identity_review_seed_count": len(result.get("release_identity_review_seeds", [])),
        "source_to_binary_relation_review_seed_count": len(result.get("source_to_binary_relation_review_seeds", [])),
        "release_asset_candidate_review_seed_count": len(result.get("release_asset_candidate_review_seeds", [])),
        "source_cache_review_seed_count": len(result.get("source_cache_review_seeds", [])),
        "evidence_candidate_review_seed_count": len(result.get("evidence_candidate_review_seeds", [])),
        "candidate_promotion_preview_count": len(result.get("candidate_promotion_previews", [])),
        "coverage_update_preview_count": len(result.get("coverage_update_previews", [])),
        "scorecard_update_count": len(result.get("scorecard_updates", [])),
        "source_pack_update_preview_count": len(result.get("source_pack_update_previews", [])),
        "blocked_sources": list(result.get("blocked_sources", [])),
        "truth_boundary_violations": violations,
    }


def detect_h4_review_truth_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return [f"{path}=true is forbidden for H4 review artifacts" for path, key, value in _iter_key_values(result) if key in FORBIDDEN_TRUTH_TRUE_KEYS and value is True]


def detect_h4_review_product_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return [f"{path}=true is forbidden for H4 review product boundaries" for path, key, value in _iter_key_values(result) if key in FORBIDDEN_PRODUCT_TRUE_KEYS and value is True]


def _record_from_inputs(inputs: Mapping[str, Any]) -> dict[str, Any]:
    if not inputs:
        return {}
    payload = deepcopy(dict(inputs))
    if payload.get("schema_version") == "h4_code_source_normalized_record.v0":
        return payload
    if isinstance(payload.get("normalized_record"), Mapping):
        return deepcopy(dict(payload["normalized_record"]))
    envelope = payload.get("connector_output_envelope")
    if isinstance(envelope, Mapping) and isinstance(envelope.get("normalized_record"), Mapping):
        return deepcopy(dict(envelope["normalized_record"]))
    return {}


def _source_identity_from_inputs(inputs: Mapping[str, Any], record: Mapping[str, Any]) -> dict[str, Any]:
    if inputs.get("schema_version") == "h4_source_identity_candidate.v0":
        return dict(inputs)
    if isinstance(record.get("source_identity_candidate"), Mapping):
        return dict(record["source_identity_candidate"])
    if isinstance(inputs.get("source_identity_candidate"), Mapping):
        return dict(inputs["source_identity_candidate"])
    return {}


def _release_identity_from_inputs(inputs: Mapping[str, Any], record: Mapping[str, Any]) -> dict[str, Any]:
    if inputs.get("schema_version") == "h4_release_identity_candidate.v0":
        return dict(inputs)
    if isinstance(record.get("release_identity_candidate"), Mapping):
        return dict(record["release_identity_candidate"])
    if isinstance(inputs.get("release_identity_candidate"), Mapping):
        return dict(inputs["release_identity_candidate"])
    return {}


def _relation_candidates_from_inputs(inputs: Mapping[str, Any], record: Mapping[str, Any]) -> list[dict[str, Any]]:
    if inputs.get("schema_version") == "h4_source_to_binary_relation_candidate.v0":
        return [dict(inputs)]
    value = record.get("source_to_binary_relation_candidate_preview") if record else inputs.get("source_to_binary_relation_candidate_preview")
    if isinstance(value, Mapping):
        return [dict(value)]
    return [dict(item) for item in value] if isinstance(value, list) else []


def _asset_candidates_from_inputs(inputs: Mapping[str, Any], record: Mapping[str, Any]) -> list[dict[str, Any]]:
    if inputs.get("schema_version") == "h4_release_asset_candidate.v0":
        return [dict(inputs)]
    value = record.get("release_asset_candidate_preview") if record else inputs.get("release_asset_candidate_preview")
    if isinstance(value, Mapping):
        return [dict(value)]
    return [dict(item) for item in value] if isinstance(value, list) else []


def _source_cache_from_inputs(inputs: Mapping[str, Any], record: Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(record.get("source_cache_candidate_preview"), Mapping):
        return dict(record["source_cache_candidate_preview"])
    if isinstance(inputs.get("source_cache_candidate_preview"), Mapping):
        return dict(inputs["source_cache_candidate_preview"])
    return {}


def _evidence_from_inputs(inputs: Mapping[str, Any], record: Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(record.get("evidence_candidate_preview"), Mapping):
        return dict(record["evidence_candidate_preview"])
    if isinstance(inputs.get("evidence_candidate_preview"), Mapping):
        return dict(inputs["evidence_candidate_preview"])
    return {}


def _source_id(value: Mapping[str, Any]) -> str:
    return str(value.get("source_id") or "unknown_source")


def _input_basis(value: Mapping[str, Any]) -> str:
    schema = str(value.get("schema_version", ""))
    if schema == "h4_code_source_live_probe_result.v0":
        return "live_probe_output"
    if schema == "h4_code_source_normalized_record.v0":
        return "normalized_record"
    if schema.startswith("h4_") and schema.endswith("candidate.v0"):
        return "candidate_output"
    return "fixture_replay_output"


def _limitations(value: Any) -> list[str]:
    limitations: list[str] = []
    for _path, key, child in _iter_key_values(value):
        if key == "limitations" and isinstance(child, list):
            limitations.extend(str(item) for item in child if item)
    return sorted(dict.fromkeys(limitations))


def _blocked_reasons(value: Any) -> list[str]:
    reasons: list[str] = []
    for _path, key, child in _iter_key_values(value):
        if key in {"blocked_reasons", "blocked_sources"} and isinstance(child, list):
            reasons.extend(str(item) for item in child if item)
        elif key == "blocked_reason" and child:
            reasons.append(str(child))
    return sorted(dict.fromkeys(reasons))


def _truth_boundary() -> dict[str, bool]:
    return {
        "source_identity_seed_accepts_identity": False,
        "release_identity_seed_accepts_release_truth": False,
        "source_to_binary_seed_accepts_provenance": False,
        "release_asset_seed_grants_download_or_safety": False,
        "source_cache_review_seed_accepts_source": False,
        "evidence_review_seed_accepts_evidence": False,
        "candidate_promotion_preview_promotes_candidate": False,
        "source_pack_preview_is_imported_or_submitted": False,
        "accepts_source_identity_truth": False,
        "accepts_release_identity_truth": False,
        "accepts_source_to_binary_provenance": False,
        "accepts_source_truth": False,
        "accepts_evidence_truth": False,
        "accepts_candidate_truth": False,
        "accepts_authenticity_truth": False,
        "accepts_build_reproducibility_truth": False,
        "source_identity_candidate_is_truth": False,
        "release_identity_candidate_is_truth": False,
        "source_to_binary_relation_candidate_is_provenance_truth": False,
        "git_object_candidate_is_provenance_truth": False,
        "swhid_candidate_is_object_truth": False,
        "release_asset_hash_candidate_is_malware_safety": False,
        "signature_metadata_is_authenticity": False,
        "signature_metadata_proves_authenticity": False,
        "sbom_metadata_is_provenance": False,
        "license_metadata_is_rights_clearance": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
        "verified_authenticity_claimed": False,
        "verified_build_reproducibility_claimed": False,
        "production_readiness_claimed": False,
    }


def _product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_hosting": False,
        "enabled_source_sync": False,
        "enabled_repository_clone": False,
        "enabled_downloads": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "enabled_installers": False,
        "enabled_execution": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
        "repository_clone_enabled": False,
        "source_archive_download_enabled": False,
        "release_asset_download_enabled": False,
        "git_command_invocation_enabled": False,
        "build_tool_invocation_enabled": False,
        "install_execute_enabled": False,
        "source_sync_enabled": False,
        "network_calls_made": False,
        "api_calls_made": False,
        "downloads_made": False,
        "git_command_invoked": False,
        "build_tool_invoked": False,
    }


def _raise_if_boundaries_fail(payload: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> None:
    violations = detect_h4_review_truth_boundary_violations(payload, policy) + detect_h4_review_product_boundary_violations(payload, policy)
    if violations:
        raise ValueError("; ".join(violations))


def _iter_key_values(value: Any, prefix: str = ""):
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            yield path, key_text, child
            yield from _iter_key_values(child, path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _iter_key_values(child, f"{prefix}[{index}]")


def _digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _slug(value: str) -> str:
    text = "".join(char.lower() if char.isalnum() else "_" for char in str(value))
    return "_".join(part for part in text.split("_") if part)[:80] or "unknown"


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def h4_source_ids() -> tuple[str, ...]:
    return tuple(H4_SOURCE_IDS)

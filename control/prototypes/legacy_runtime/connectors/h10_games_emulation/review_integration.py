"""Offline H10 games/emulation review integration helpers.

These helpers consume explicit fixture replay outputs plus blocked or approved
metadata-only live-probe outputs. They produce review seeds and planning
previews only; they do not call networks, query catalogs, fetch software lists
or hash sets, download, upload, execute, acquire, scrape, crawl, access
restricted sources, accept truth, or mutate runtime state or indexes.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import hashlib
import json
from pathlib import Path
from typing import Any

from control.prototypes.legacy_runtime.connectors.h10_games_emulation.normalizer_common import H10_SOURCE_CONFIGS, H10_SOURCE_IDS

FORBIDDEN_TRUTH_TRUE_KEYS = {
    "accepted_action_permission", "accepted_candidate_truth", "accepted_emulator_compatibility_truth",
    "accepted_evidence_truth", "accepted_game_identity_truth", "accepted_game_relation_truth",
    "accepted_hashset_truth", "accepted_platform_truth", "accepted_public_record",
    "accepted_release_truth", "accepted_rights_safety_truth", "accepted_rom_disc_media_truth",
    "accepted_source_truth", "action_permission_accepted", "automatic_future_connector_approval",
    "candidate_promotion_preview_promotes_candidate", "compatibility_correctness",
    "compatibility_correctness_claimed", "content_safety", "content_safety_claimed",
    "disc_authenticity_claimed", "disc_authenticity_verified", "emulator_action_candidate_is_action_permission",
    "emulator_action_seed_accepts_action_permission", "emulator_compatibility_candidate_is_truth",
    "emulator_compatibility_seed_accepts_compatibility_truth", "emulator_compatibility_verified",
    "evidence_review_seed_accepts_evidence", "exhaustive_global_coverage",
    "future_connector_auto_approval", "game_identity_seed_accepts_game_truth",
    "game_identity_verified", "game_relation_candidate_is_truth", "game_relation_seed_accepts_relation_truth",
    "game_software_identity_candidate_is_truth", "hash_metadata_proves_authenticity",
    "hashset_correctness_verified", "installability_claimed", "installability_verified",
    "legal_acquisition_claimed", "legal_acquisition_verified", "malware_safety",
    "malware_safety_claimed", "master_index_mutated", "media_identity_grants_download_permission",
    "platform_release_edition_candidate_is_truth", "platform_release_seed_accepts_platform_truth",
    "platform_release_seed_accepts_release_truth", "playability_claimed", "playability_verified",
    "preservation_hashset_candidate_is_truth", "preservation_hashset_seed_accepts_hashset_truth",
    "privacy_safety", "privacy_safety_claimed", "production_games_emulation_coverage",
    "production_readiness_claim", "production_readiness_claimed", "production_search_quality",
    "public_index_mutated", "release_identity_verified", "review_seed_is_review_decision",
    "rights_clearance", "rights_clearance_claimed", "rights_safety_candidate_is_rights_or_safety_truth",
    "rights_safety_seed_accepts_rights_safety_truth", "rom_authenticity_claimed",
    "rom_authenticity_verified", "rom_disc_media_candidate_is_truth",
    "rom_disc_media_identity_candidate_is_truth", "rom_disc_media_seed_accepts_media_truth",
    "source_cache_review_seed_accepts_source", "source_pack_preview_is_imported_or_submitted",
    "verified_authenticity", "verified_authenticity_claimed",
}

FORBIDDEN_PRODUCT_TRUE_KEYS = {
    "acquisition_action_used", "api_calls_made", "api_catalog_sync_permission",
    "api_query_used", "asset_download_used", "bios_firmware_download_used",
    "browser_automation_used", "bypass_or_automation_used", "catalog_fetch_used",
    "changed_public_search_behavior", "chd_download_used", "crawling_used",
    "disc_image_download_used", "emulator_download_used", "emulator_execution_used",
    "enabled_accounts", "enabled_acquisition_actions", "enabled_crawling",
    "enabled_downloads", "enabled_execution", "enabled_hosting", "enabled_live_probes",
    "enabled_scraping", "enabled_source_sync", "enabled_telemetry", "enabled_uploads",
    "enables_acquisition_actions", "enables_api_catalog_sync", "enables_downloads",
    "enables_execution", "enables_hashset_fetch", "enables_restricted_source_access",
    "enables_scraping_crawling", "enables_software_list_fetch", "enables_uploads",
    "file_upload_used", "game_binary_download_used", "game_execution_used",
    "hash_submission_used", "hashset_fetch_used", "install_execute_used",
    "installer_download_used", "iso_download_used", "mutated_master_index",
    "mutated_public_index", "network_calls_made", "patch_download_used",
    "query_fetch_download_upload_execute_acquire", "restricted_source_access",
    "restricted_source_access_used", "rom_download_used", "scraping_used",
    "software_list_fetch_used",
}

REVIEW_SEED_KEYS = (
    "game_software_identity_review_seeds",
    "platform_release_edition_review_seeds",
    "emulator_compatibility_review_seeds",
    "preservation_hashset_review_seeds",
    "rom_disc_media_identity_review_seeds",
    "game_relation_review_seeds",
    "emulator_action_candidate_review_seeds",
    "games_rights_safety_review_seeds",
    "source_cache_review_seeds",
    "evidence_candidate_review_seeds",
)


def load_h10_games_emulation_outputs(paths: Sequence[str | Path]) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    for path_text in paths:
        path = Path(path_text)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            raise ValueError(f"{path} must contain a JSON object")
        outputs.append(dict(payload))
    return outputs


def build_h10_game_software_identity_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("game_software_identity", _source_id(inputs), _first_ref(inputs, "game_software_identity_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h10_game_software_identity_review_seed.v0",
        "review_subject_type": "game_software_identity_candidate",
        "accepted_game_identity_truth": False,
        "game_identity_seed_accepts_game_truth": False,
        "game_identity_verified": False,
        "legal_acquisition_claimed": False,
        "playability_claimed": False,
        "limitations": _limitations(inputs) + ["Game/software identity review seed is not accepted game truth, availability proof, legal acquisition proof, playability, or installability."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h10_platform_release_edition_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("platform_release_edition", _source_id(inputs), _first_ref(inputs, "platform_release_edition_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h10_platform_release_edition_review_seed.v0",
        "review_subject_type": "platform_release_edition_candidate",
        "accepted_release_truth": False,
        "accepted_platform_truth": False,
        "platform_release_seed_accepts_release_truth": False,
        "platform_release_seed_accepts_platform_truth": False,
        "release_identity_verified": False,
        "limitations": _limitations(inputs) + ["Platform/release/edition review seed is not release truth, platform truth, compatibility proof, or acquisition permission."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h10_emulator_compatibility_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("emulator_compatibility", _source_id(inputs), _first_ref(inputs, "emulator_compatibility_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h10_emulator_compatibility_review_seed.v0",
        "review_subject_type": "emulator_compatibility_candidate",
        "accepted_emulator_compatibility_truth": False,
        "emulator_compatibility_seed_accepts_compatibility_truth": False,
        "emulator_compatibility_verified": False,
        "compatibility_correctness_claimed": False,
        "playability_claimed": False,
        "emulator_execution_permission_current": False,
        "limitations": _limitations(inputs) + ["Emulator compatibility review seed is not verified compatibility, playability, configuration approval, or execution permission."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h10_preservation_hashset_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("preservation_hashset", _source_id(inputs), _first_ref(inputs, "preservation_hashset_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h10_preservation_hashset_review_seed.v0",
        "review_subject_type": "preservation_hashset_candidate",
        "accepted_hashset_truth": False,
        "preservation_hashset_seed_accepts_hashset_truth": False,
        "hashset_correctness_verified": False,
        "hash_metadata_proves_authenticity": False,
        "hash_submission_permission_current": False,
        "limitations": _limitations(inputs) + ["Preservation hash-set review seed is not hash-set truth, authenticity proof, safety proof, legal acquisition proof, download permission, or hash-submission permission."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h10_rom_disc_media_identity_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("rom_disc_media_identity", _source_id(inputs), _first_ref(inputs, "rom_disc_media_identity_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h10_rom_disc_media_identity_review_seed.v0",
        "review_subject_type": "rom_disc_media_identity_candidate",
        "accepted_rom_disc_media_truth": False,
        "rom_disc_media_seed_accepts_media_truth": False,
        "rom_authenticity_claimed": False,
        "disc_authenticity_claimed": False,
        "legal_acquisition_claimed": False,
        "media_identity_grants_download_permission": False,
        "limitations": _limitations(inputs) + ["ROM/disc/media identity review seed is not media truth, authenticity proof, legal acquisition truth, safety proof, playability, or download permission."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h10_game_relation_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("game_relation", _source_id(inputs), _first_ref(inputs, "game_relation_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h10_game_relation_review_seed.v0",
        "review_subject_type": "game_relation_candidate",
        "accepted_game_relation_truth": False,
        "game_relation_seed_accepts_relation_truth": False,
        "limitations": _limitations(inputs) + ["Game relation review seed is not relation truth, duplicate truth, storefront acquisition proof, emulator playability proof, or source-code/binary relation truth."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h10_emulator_action_candidate_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("emulator_action_candidate", _source_id(inputs), _first_ref(inputs, "emulator_action_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h10_emulator_action_candidate_review_seed.v0",
        "review_subject_type": "emulator_action_candidate",
        "accepted_action_permission": False,
        "emulator_action_seed_accepts_action_permission": False,
        "emulator_execution_permission_current": False,
        "game_execution_permission_current": False,
        "install_execute_permission_current": False,
        "acquisition_action_permission_current": False,
        "limitations": _limitations(inputs) + ["Emulator/action review seed is not action permission and does not authorize emulate, install, execute, acquire, download, mirror, upload, or launch behavior."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h10_games_rights_safety_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("games_rights_safety", _source_id(inputs), _first_ref(inputs, "games_rights_safety_candidate", "candidate_id"), inputs)
    seed.update({
        "schema_version": "h10_games_rights_safety_review_seed.v0",
        "review_subject_type": "games_rights_safety_candidate",
        "accepted_rights_safety_truth": False,
        "rights_safety_seed_accepts_rights_safety_truth": False,
        "rights_clearance_claimed": False,
        "legal_acquisition_claimed": False,
        "malware_safety_claimed": False,
        "content_safety_claimed": False,
        "privacy_safety_claimed": False,
        "limitations": _limitations(inputs) + ["Rights/safety review seed is not rights clearance, legal acquisition truth, content safety, privacy safety, malware safety, or production readiness."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h10_source_cache_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("source_cache", _source_id(inputs), _first_ref(inputs, "source_cache_candidate_preview", "preview_id"), inputs)
    seed.update({
        "schema_version": "h10_source_cache_review_seed.v0",
        "review_subject_type": "source_cache_candidate_preview",
        "accepted_source_truth": False,
        "source_cache_review_seed_accepts_source": False,
        "source_cache_write_allowed_current": False,
        "limitations": _limitations(inputs) + ["Source-cache review seed is not accepted source truth and does not write the source cache."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h10_evidence_candidate_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    seed = _seed_base("evidence_candidate", _source_id(inputs), _first_ref(inputs, "evidence_candidate_preview", "preview_id"), inputs)
    seed.update({
        "schema_version": "h10_evidence_candidate_review_seed.v0",
        "review_subject_type": "evidence_candidate_preview",
        "accepted_evidence_truth": False,
        "evidence_review_seed_accepts_evidence": False,
        "evidence_ledger_write_allowed_current": False,
        "limitations": _limitations(inputs) + ["Evidence candidate review seed is not accepted evidence and does not write the evidence ledger."],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h10_candidate_promotion_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = {
        "schema_version": "h10_candidate_promotion_preview.v0",
        "candidate_promotion_preview_id": f"h10.candidate_promotion.{source_id}.{_digest(inputs)[:12]}.v0",
        "source_id": source_id,
        "preview_only": True,
        "promotes_candidate": False,
        "candidate_promotion_preview_promotes_candidate": False,
        "accepted_candidate_truth": False,
        "review_required_before_promotion": True,
        "limitations": _limitations(inputs) + ["Candidate promotion preview does not promote, accept, publish, persist, launch, download, or acquire any games/emulation candidate."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h10_coverage_update_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = {
        "schema_version": "h10_source_coverage_update_preview.v0",
        "coverage_update_preview_id": f"h10.coverage_update.{source_id}.{_digest(inputs)[:12]}.v0",
        "source_id": source_id,
        "coverage_basis": "fixture_review_and_blocked_live_probe_evidence",
        "coverage_preview_only": True,
        "coverage_manifest_is_exhaustive_global_coverage": False,
        "production_games_emulation_coverage": False,
        "limitations": ["Coverage update preview is not exhaustive global coverage, production coverage, game identity truth, compatibility proof, or legal acquisition proof."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h10_connector_scorecard_update(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    update = {
        "schema_version": "h10_connector_scorecard_update.v0",
        "connector_scorecard_update_id": f"h10.scorecard_update.{source_id}.{_digest(inputs)[:12]}.v0",
        "source_id": source_id,
        "fixture_replay_status": "integrated",
        "live_probe_status": "blocked_or_dry_preflight_without_approval",
        "review_integration_status": "preview_created",
        "production_ready": False,
        "auto_approves_future_connectors": False,
        "limitations": ["Connector scorecard update is not production readiness, action permission, or future connector approval."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_boundaries_fail(update, policy)
    return update


def build_h10_source_pack_update_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = {
        "schema_version": "h10_source_pack_update_preview.v0",
        "source_pack_update_preview_id": f"h10.source_pack_update.{source_id}.{_digest(inputs)[:12]}.v0",
        "source_id": source_id,
        "preview_only": True,
        "source_pack_imported": False,
        "source_pack_submitted": False,
        "source_pack_accepted": False,
        "source_pack_preview_is_imported_or_submitted": False,
        "limitations": ["Source pack update preview is not import, submission, acceptance, public truth, source sync, download, execution, or acquisition permission."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h10_review_integration_result(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    outputs = list(inputs.get("outputs") or [])
    input_refs = list(inputs.get("input_refs") or [])
    by_source = _best_inputs_by_source(outputs)
    sources = [source for source in H10_SOURCE_IDS if source in by_source] or list(H10_SOURCE_IDS)
    fixture_outputs = [_output_summary(item) for item in outputs if item.get("schema_version") == "h10_games_emulation_fixture_replay_result.v0"]
    live_outputs = [_output_summary(item) for item in outputs if item.get("schema_version") == "h10_games_emulation_live_probe_result.v0"]
    blocked_sources = sorted({str(item.get("source_id")) for item in outputs if str(item.get("result_status", "")).startswith("blocked") and item.get("source_id")})
    seed_inputs = [by_source.get(source_id, {"source_id": source_id}) for source_id in sources]
    result = {
        "schema_version": "h10_games_emulation_review_integration_result.v0",
        "review_integration_result_id": f"h10.review_integration.{_digest({'sources': sources, 'inputs': input_refs})[:12]}.v0",
        "wave_id": "H10",
        "sources": sources,
        "source_count": len(sources),
        "input_refs": input_refs,
        "used_fixture_outputs": fixture_outputs,
        "used_live_probe_outputs": live_outputs,
        "game_software_identity_review_seeds": [build_h10_game_software_identity_review_seed(item, policy) for item in seed_inputs],
        "platform_release_edition_review_seeds": [build_h10_platform_release_edition_review_seed(item, policy) for item in seed_inputs],
        "emulator_compatibility_review_seeds": [build_h10_emulator_compatibility_review_seed(item, policy) for item in seed_inputs],
        "preservation_hashset_review_seeds": [build_h10_preservation_hashset_review_seed(item, policy) for item in seed_inputs],
        "rom_disc_media_identity_review_seeds": [build_h10_rom_disc_media_identity_review_seed(item, policy) for item in seed_inputs],
        "game_relation_review_seeds": [build_h10_game_relation_review_seed(item, policy) for item in seed_inputs],
        "emulator_action_candidate_review_seeds": [build_h10_emulator_action_candidate_review_seed(item, policy) for item in seed_inputs],
        "games_rights_safety_review_seeds": [build_h10_games_rights_safety_review_seed(item, policy) for item in seed_inputs],
        "source_cache_review_seeds": [build_h10_source_cache_review_seed(item, policy) for item in seed_inputs],
        "evidence_candidate_review_seeds": [build_h10_evidence_candidate_review_seed(item, policy) for item in seed_inputs],
        "candidate_promotion_previews": [build_h10_candidate_promotion_preview(item, policy) for item in seed_inputs],
        "coverage_update_previews": [build_h10_coverage_update_preview(item, policy) for item in seed_inputs],
        "scorecard_updates": [build_h10_connector_scorecard_update(item, policy) for item in seed_inputs],
        "source_pack_update_previews": [build_h10_source_pack_update_preview(item, policy) for item in seed_inputs],
        "blocked_sources": blocked_sources,
        "warnings": ["H10 live probes remain blocked pending operator approval."] if blocked_sources else [],
        "limitations": [
            "H10 review integration is a wave-level audit and rehearsal, not promotion.",
            "Fixture replay and blocked/preflight live-probe reports do not prove game identity, ROM or disc authenticity, hash-set correctness, emulator compatibility, playability, installability, legal acquisition, rights clearance, malware safety, privacy safety, content safety, production coverage, or live endpoint behavior.",
        ],
        "accepts_game_identity_truth": False,
        "accepts_release_truth": False,
        "accepts_platform_truth": False,
        "accepts_emulator_compatibility_truth": False,
        "accepts_hashset_truth": False,
        "accepts_rom_disc_media_truth": False,
        "accepts_game_relation_truth": False,
        "accepts_action_permission": False,
        "accepts_rights_safety_truth": False,
        "accepts_source_truth": False,
        "accepts_evidence_truth": False,
        "accepts_candidate_truth": False,
        "mutates_public_index": False,
        "mutates_master_index": False,
        "enables_api_catalog_sync": False,
        "enables_software_list_fetch": False,
        "enables_hashset_fetch": False,
        "enables_downloads": False,
        "enables_uploads": False,
        "enables_execution": False,
        "enables_acquisition_actions": False,
        "enables_scraping_crawling": False,
        "enables_restricted_source_access": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Review seeds and previews require explicit human review before any downstream persistence."],
    }
    _raise_if_boundaries_fail(result, policy)
    return result


def summarize_h10_review_integration(result: Mapping[str, Any]) -> dict[str, Any]:
    errors = detect_h10_review_truth_boundary_violations(result) + detect_h10_review_product_boundary_violations(result)
    return {
        "schema_version": "h10_review_integration_summary.v0",
        "status": "pass" if not errors else "invalid",
        "review_integration_result_id": result.get("review_integration_result_id"),
        "source_count": len(result.get("sources", [])),
        "game_software_identity_review_seed_count": len(result.get("game_software_identity_review_seeds", [])),
        "platform_release_edition_review_seed_count": len(result.get("platform_release_edition_review_seeds", [])),
        "emulator_compatibility_review_seed_count": len(result.get("emulator_compatibility_review_seeds", [])),
        "preservation_hashset_review_seed_count": len(result.get("preservation_hashset_review_seeds", [])),
        "rom_disc_media_identity_review_seed_count": len(result.get("rom_disc_media_identity_review_seeds", [])),
        "game_relation_review_seed_count": len(result.get("game_relation_review_seeds", [])),
        "emulator_action_candidate_review_seed_count": len(result.get("emulator_action_candidate_review_seeds", [])),
        "games_rights_safety_review_seed_count": len(result.get("games_rights_safety_review_seeds", [])),
        "source_cache_review_seed_count": len(result.get("source_cache_review_seeds", [])),
        "evidence_candidate_review_seed_count": len(result.get("evidence_candidate_review_seeds", [])),
        "blocked_sources": list(result.get("blocked_sources", [])),
        "truth_boundary_errors": detect_h10_review_truth_boundary_violations(result),
        "product_boundary_errors": detect_h10_review_product_boundary_violations(result),
    }


def detect_h10_review_truth_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return sorted(dict.fromkeys(f"truth boundary violation: {path}=true" for path, key, value in _iter_key_values(result) if key in FORBIDDEN_TRUTH_TRUE_KEYS and value is True))


def detect_h10_review_product_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return sorted(dict.fromkeys(f"product boundary violation: {path}=true" for path, key, value in _iter_key_values(result) if key in FORBIDDEN_PRODUCT_TRUE_KEYS and value is True))


def _best_inputs_by_source(outputs: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    by_source: dict[str, dict[str, Any]] = {}
    for item in outputs:
        source_id = item.get("source_id")
        if source_id in H10_SOURCE_IDS:
            normalized = item.get("normalized_record")
            if item.get("schema_version") == "h10_games_emulation_fixture_replay_result.v0" and isinstance(normalized, Mapping):
                by_source[str(source_id)] = dict(normalized)
            elif str(source_id) not in by_source:
                by_source[str(source_id)] = dict(normalized) if isinstance(normalized, Mapping) else dict(item)
    return by_source


def _output_summary(item: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": item.get("schema_version"),
        "source_id": item.get("source_id"),
        "status": item.get("replay_status") or item.get("result_status"),
        "ref": item.get("live_probe_result_id") or item.get("replay_result_id") or item.get("fixture_id"),
        "request_count": item.get("request_count", 0),
        "network_used": bool(item.get("network_used", False)),
    }


def _source_id(inputs: Mapping[str, Any]) -> str:
    source_id = str(inputs.get("source_id") or "")
    if source_id not in H10_SOURCE_IDS:
        raise ValueError(f"unknown or missing H10 source_id: {source_id}")
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
    return str(inputs.get("normalized_record_id") or inputs.get("live_probe_result_id") or inputs.get("replay_result_id") or inputs.get("source_id") or "unknown")


def _limitations(inputs: Mapping[str, Any]) -> list[str]:
    values = inputs.get("limitations") or inputs.get("source_limitations") or []
    if isinstance(values, str):
        values = [values]
    return [str(item) for item in values if item]


def _seed_base(kind: str, source_id: str, subject_ref: str, inputs: Mapping[str, Any]) -> dict[str, Any]:
    config = H10_SOURCE_CONFIGS.get(source_id, {})
    return {
        "review_seed_id": f"h10.{kind}.review_seed.{source_id}.{_digest({'ref': subject_ref, 'kind': kind})[:12]}.v0",
        "wave_id": "H10",
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
        "game_identity_seed_accepts_game_truth": False,
        "platform_release_seed_accepts_release_truth": False,
        "platform_release_seed_accepts_platform_truth": False,
        "emulator_compatibility_seed_accepts_compatibility_truth": False,
        "preservation_hashset_seed_accepts_hashset_truth": False,
        "rom_disc_media_seed_accepts_media_truth": False,
        "game_relation_seed_accepts_relation_truth": False,
        "emulator_action_seed_accepts_action_permission": False,
        "rights_safety_seed_accepts_rights_safety_truth": False,
        "source_cache_review_seed_accepts_source": False,
        "evidence_review_seed_accepts_evidence": False,
        "candidate_promotion_preview_promotes_candidate": False,
        "source_pack_preview_is_imported_or_submitted": False,
        "review_seed_is_review_decision": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "legal_acquisition_claimed": False,
        "rom_authenticity_claimed": False,
        "disc_authenticity_claimed": False,
        "compatibility_correctness_claimed": False,
        "playability_claimed": False,
        "installability_claimed": False,
        "malware_safety_claimed": False,
        "content_safety_claimed": False,
        "privacy_safety_claimed": False,
        "verified_authenticity_claimed": False,
        "production_readiness_claimed": False,
        "automatic_future_connector_approval": False,
        "accepted_game_identity_truth": False,
        "accepted_release_truth": False,
        "accepted_platform_truth": False,
        "accepted_emulator_compatibility_truth": False,
        "accepted_hashset_truth": False,
        "accepted_rom_disc_media_truth": False,
        "accepted_game_relation_truth": False,
        "accepted_action_permission": False,
        "accepted_rights_safety_truth": False,
        "accepted_source_truth": False,
        "accepted_evidence_truth": False,
        "accepted_candidate_truth": False,
    }


def _product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_hosting": False,
        "enabled_live_probes": False,
        "enabled_source_sync": False,
        "enabled_downloads": False,
        "enabled_uploads": False,
        "enabled_execution": False,
        "enabled_acquisition_actions": False,
        "enabled_crawling": False,
        "enabled_scraping": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "network_calls_made": False,
        "api_calls_made": False,
        "catalog_fetch_used": False,
        "software_list_fetch_used": False,
        "hashset_fetch_used": False,
        "rom_download_used": False,
        "iso_download_used": False,
        "disc_image_download_used": False,
        "chd_download_used": False,
        "bios_firmware_download_used": False,
        "game_binary_download_used": False,
        "emulator_download_used": False,
        "installer_download_used": False,
        "patch_download_used": False,
        "asset_download_used": False,
        "file_upload_used": False,
        "hash_submission_used": False,
        "emulator_execution_used": False,
        "game_execution_used": False,
        "install_execute_used": False,
        "acquisition_action_used": False,
        "scraping_used": False,
        "crawling_used": False,
        "restricted_source_access_used": False,
        "bypass_or_automation_used": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def _raise_if_boundaries_fail(payload: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> None:
    errors = detect_h10_review_truth_boundary_violations(payload, policy)
    errors.extend(detect_h10_review_product_boundary_violations(payload, policy))
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

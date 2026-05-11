"""Offline H10 games/emulation fixture normalization helpers."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from typing import Any


H10_SOURCE_CONFIGS = {'flashpoint_metadata': {'connector_family': 'web_game_archive_metadata',
                         'source_family': 'games_emulation_software_identity',
                         'source_id': 'flashpoint_metadata',
                         'source_label': 'Flashpoint metadata',
                         'trust_lane': 'preservation'},
 'games_emulation_policy_blocked': {'connector_family': 'restricted_manifest_only',
                                    'source_family': 'games_emulation_software_identity',
                                    'source_id': 'games_emulation_policy_blocked',
                                    'source_label': 'Generic game/software identity policy-blocked source',
                                    'trust_lane': 'restricted_manifest_only'},
 'generic_emulator_compatibility': {'connector_family': 'emulator_compatibility_metadata',
                                    'source_family': 'games_emulation_software_identity',
                                    'source_id': 'generic_emulator_compatibility',
                                    'source_label': 'Generic emulator compatibility metadata',
                                    'trust_lane': 'unknown'},
 'generic_game_database': {'connector_family': 'game_database_api',
                           'source_family': 'games_emulation_software_identity',
                           'source_id': 'generic_game_database',
                           'source_label': 'Generic game database metadata',
                           'trust_lane': 'unknown'},
 'generic_preservation_hashset': {'connector_family': 'preservation_hashset_metadata',
                                  'source_family': 'games_emulation_software_identity',
                                  'source_id': 'generic_preservation_hashset',
                                  'source_label': 'Generic preservation hash-set metadata',
                                  'trust_lane': 'unknown'},
 'gog_game_metadata_policy_limited': {'connector_family': 'game_storefront_metadata',
                                      'source_family': 'games_emulation_software_identity',
                                      'source_id': 'gog_game_metadata_policy_limited',
                                      'source_label': 'GOG game metadata, policy-limited',
                                      'trust_lane': 'official'},
 'itchio_game_metadata_policy_limited': {'connector_family': 'game_storefront_metadata',
                                         'source_family': 'games_emulation_software_identity',
                                         'source_id': 'itchio_game_metadata_policy_limited',
                                         'source_label': 'itch.io game metadata, policy-limited',
                                         'trust_lane': 'community'},
 'mame_software_lists': {'connector_family': 'software_list_metadata',
                         'source_family': 'games_emulation_software_identity',
                         'source_id': 'mame_software_lists',
                         'source_label': 'MAME software lists metadata',
                         'trust_lane': 'preservation'},
 'mobygames': {'connector_family': 'game_database_api',
               'source_family': 'games_emulation_software_identity',
               'source_id': 'mobygames',
               'source_label': 'MobyGames metadata',
               'trust_lane': 'community'},
 'no_intro_hash_sets': {'connector_family': 'preservation_hashset_metadata',
                        'source_family': 'games_emulation_software_identity',
                        'source_id': 'no_intro_hash_sets',
                        'source_label': 'No-Intro hash-set metadata',
                        'trust_lane': 'preservation'},
 'redump_hash_sets': {'connector_family': 'preservation_hashset_metadata',
                      'source_family': 'games_emulation_software_identity',
                      'source_id': 'redump_hash_sets',
                      'source_label': 'Redump hash-set metadata',
                      'trust_lane': 'preservation'},
 'scummvm_compatibility': {'connector_family': 'emulator_compatibility_metadata',
                           'source_family': 'games_emulation_software_identity',
                           'source_id': 'scummvm_compatibility',
                           'source_label': 'ScummVM compatibility metadata',
                           'trust_lane': 'community'},
 'steam_game_metadata_policy_limited': {'connector_family': 'game_storefront_metadata',
                                        'source_family': 'games_emulation_software_identity',
                                        'source_id': 'steam_game_metadata_policy_limited',
                                        'source_label': 'Steam game metadata, policy-limited',
                                        'trust_lane': 'official'},
 'tosec_hash_sets': {'connector_family': 'preservation_hashset_metadata',
                     'source_family': 'games_emulation_software_identity',
                     'source_id': 'tosec_hash_sets',
                     'source_label': 'TOSEC hash-set metadata',
                     'trust_lane': 'preservation'}}
H10_SOURCE_IDS = tuple(H10_SOURCE_CONFIGS)
H10_FIXTURE_KINDS = ('minimal', 'game_identity', 'platform_release_edition', 'emulator_compatibility', 'preservation_hashset', 'rom_disc_media_identity', 'game_relation', 'emulator_action_blocked', 'rights_safety', 'policy_blocked')
FIXTURE_FORBIDDEN_TRUE_KEYS = {'game_execution_performed', 'asset_payload_included', 'install_execute_performed', 'external_api_used', 'restricted_source_accessed', 'game_binary_payload_included', 'bios_firmware_payload_included', 'network_used', 'live_call_used', 'hashset_payload_included', 'installer_payload_included', 'hash_submission_performed', 'scraping_output_included', 'catalog_payload_included', 'disc_image_payload_included', 'crack_key_serial_payload_included', 'acquisition_action_performed', 'bypass_or_automation_used', 'iso_payload_included', 'crawling_output_included', 'rom_payload_included', 'software_list_payload_included', 'emulator_execution_performed', 'file_upload_performed', 'emulator_payload_included', 'patch_payload_included', 'chd_payload_included'}
TRUTH_FORBIDDEN_TRUE_KEYS = {'malware_safety_claimed', 'accepted_public_record', 'download_permission_granted', 'accepted_release_truth', 'disc_authenticity_claimed', 'execution_permission_granted', 'privacy_safety_claimed', 'accepted_game_identity_truth', 'game_relation_candidate_is_truth', 'public_index_mutated', 'hash_metadata_proves_authenticity', 'rom_authenticity_claimed', 'preservation_hashset_candidate_is_truth', 'rights_clearance_claimed', 'accepted_source_truth', 'compatibility_metadata_proves_playability', 'accepted_action_permission', 'production_readiness_claimed', 'acquisition_permission_granted', 'evidence_preview_is_accepted_evidence', 'upload_permission_granted', 'rom_disc_media_identity_candidate_is_truth', 'verified_authenticity_claimed', 'platform_release_edition_candidate_is_truth', 'rom_disc_media_candidate_is_truth', 'accepted_rights_safety_truth', 'master_index_mutated', 'rights_safety_candidate_is_rights_or_safety_truth', 'accepted_hashset_truth', 'storefront_metadata_grants_acquisition_permission', 'game_software_identity_candidate_is_truth', 'emulator_compatibility_candidate_is_truth', 'normalized_record_is_public_truth', 'accepted_game_relation_truth', 'playability_claimed', 'emulator_action_candidate_is_action_permission', 'accepted_platform_truth', 'accepted_emulator_compatibility_truth', 'compatibility_correctness_claimed', 'legal_acquisition_claimed', 'media_identity_grants_download_permission', 'accepted_evidence_truth', 'accepted_candidate_truth', 'accepted_rom_disc_media_truth', 'content_safety_claimed', 'installability_claimed', 'source_cache_preview_is_accepted_source', 'hash_submission_permission_granted'}
PRODUCT_FORBIDDEN_TRUE_KEYS = {'changed_public_search_behavior', 'enabled_hosting', 'catalog_fetch_used', 'crawling_used', 'network_calls_made', 'chd_download_used', 'enabled_crawling', 'software_list_fetch_used', 'file_upload_used', 'enabled_acquisition_actions', 'game_binary_download_used', 'mutated_public_index', 'enabled_execution', 'enabled_source_sync', 'restricted_source_access_used', 'enabled_telemetry', 'mutated_master_index', 'bios_firmware_download_used', 'bypass_or_automation_used', 'iso_download_used', 'enabled_uploads', 'hash_submission_used', 'api_calls_made', 'patch_download_used', 'installer_download_used', 'install_execute_used', 'emulator_download_used', 'emulator_execution_used', 'game_execution_used', 'rom_download_used', 'enabled_downloads', 'disc_image_download_used', 'enabled_live_probes', 'enabled_accounts', 'asset_download_used', 'acquisition_action_used', 'enabled_scraping', 'scraping_used', 'hashset_fetch_used'}


NORMALIZED_SCALAR_FIELDS = (
    "source_native_id",
    "game_title",
    "series_or_franchise",
    "developer",
    "publisher",
    "platform",
    "release_date_candidate",
    "region_candidate",
    "language_candidate",
    "genre_or_category",
    "game_database_id_candidate",
    "mobygames_id_candidate",
    "steam_app_id_candidate",
    "gog_id_candidate",
    "itch_id_candidate",
    "software_list_id_candidate",
    "platform_family",
    "platform_name",
    "hardware_or_os_version",
    "release_title",
    "release_region",
    "release_language",
    "edition_name",
    "version_or_revision",
    "media_type",
    "emulator_or_runtime",
    "emulator_version_candidate",
    "compatibility_status_candidate",
    "known_issue_candidate",
    "required_bios_or_firmware_candidate",
    "required_patch_candidate",
    "configuration_hint_candidate",
    "hashset_name",
    "hash_algorithm",
    "hash_value_candidate",
    "file_name_candidate",
    "file_size_candidate",
    "dump_status_candidate",
    "disc_id_candidate",
    "serial_candidate",
    "product_code_candidate",
    "storefront_availability_candidate",
)


def normalize_h10_games_emulation_fixture(raw_fixture: Mapping[str, Any], source_id: str, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Normalize a committed H10 fixture without live access or side effects."""
    _require_fixture_boundaries(raw_fixture)
    if source_id not in H10_SOURCE_CONFIGS:
        raise ValueError(f"unknown H10 source_id: {source_id}")
    if raw_fixture.get("source_id") != source_id:
        raise ValueError("fixture source_id does not match requested source")
    config = H10_SOURCE_CONFIGS[source_id]
    payload = _mapping(raw_fixture.get("fixture_payload"), "fixture_payload")
    native_id = _text(payload.get("source_native_id")) or _text(raw_fixture.get("fixture_id")) or "unknown"
    fixture_kind = _text(raw_fixture.get("fixture_kind")) or "unknown"
    source_kind = _text(payload.get("source_record_kind")) or fixture_kind
    limitations = _dedupe(_list(raw_fixture.get("limitations")) + _missing_optional_limitations(payload))
    record: dict[str, Any] = {
        "schema_version": "h10_games_emulation_normalized_record.v0",
        "normalized_record_id": f"h10.normalized.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "connector_family": config["connector_family"],
        "source_record_kind": source_kind,
        "alternate_title": _list(payload.get("alternate_title")),
        "supported_features_candidate": _list(payload.get("supported_features_candidate")),
        "unsupported_features_candidate": _list(payload.get("unsupported_features_candidate")),
        "rights_safety_metadata": _mapping(payload.get("rights_safety_metadata"), "rights_safety_metadata"),
        "source_metadata": {
            "fixture_id": raw_fixture.get("fixture_id", "unknown"),
            "fixture_kind": fixture_kind,
            "fixture_status": raw_fixture.get("fixture_status", "unknown"),
            "source_label": config["source_label"],
            "trust_lane": config["trust_lane"],
            "metadata_summary": payload.get("metadata_summary", "synthetic fixture metadata only"),
        },
        "source_limitations": limitations,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": [
            "Offline fixture normalization only.",
            "Candidate and preview outputs require review and do not grant live access, downloads, uploads, execution, acquisition, evidence acceptance, or public truth.",
        ],
    }
    for field in NORMALIZED_SCALAR_FIELDS:
        record[field] = _text(payload.get(field)) or "unknown"
    record["game_software_identity_candidate"] = build_h10_game_software_identity_candidate(record, policy)
    record["platform_release_edition_candidate"] = build_h10_platform_release_edition_candidate(record, policy)
    record["emulator_compatibility_candidate"] = build_h10_emulator_compatibility_candidate(record, policy)
    record["preservation_hashset_candidate"] = build_h10_preservation_hashset_candidate(record, policy)
    record["rom_disc_media_identity_candidate"] = build_h10_rom_disc_media_identity_candidate(record, policy)
    record["game_relation_candidate"] = build_h10_game_relation_candidates(record, policy)
    record["emulator_action_candidate"] = build_h10_emulator_action_candidate(record, policy)
    record["games_rights_safety_candidate"] = build_h10_games_rights_safety_candidate(record, policy)
    record["source_cache_candidate_preview"] = build_h10_source_cache_candidate_preview(record, policy)
    record["evidence_candidate_preview"] = build_h10_evidence_candidate_preview(record, policy)
    _raise_on_boundary_errors(record)
    return record


def build_h10_game_software_identity_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("game_title", "alternate_title", "series_or_franchise", "developer", "publisher", "platform", "game_database_id_candidate", "mobygames_id_candidate", "steam_app_id_candidate", "gog_id_candidate", "itch_id_candidate", "software_list_id_candidate", "source_native_id")
    return _candidate(normalized_record, "game_software_identity", "h10_game_software_identity_candidate.v0", fields, "Game/software identity candidate only; title, platform, storefront, and database identifiers require review.")


def build_h10_platform_release_edition_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("platform_family", "platform_name", "hardware_or_os_version", "release_title", "release_region", "release_language", "edition_name", "version_or_revision", "media_type", "release_date_candidate", "publisher")
    return _candidate(normalized_record, "platform_release_edition", "h10_platform_release_edition_candidate.v0", fields, "Platform/release/edition candidate only; platform matches do not prove compatibility or acquisition permission.")


def build_h10_emulator_compatibility_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("emulator_or_runtime", "emulator_version_candidate", "game_title", "platform", "compatibility_status_candidate", "supported_features_candidate", "unsupported_features_candidate", "known_issue_candidate", "required_bios_or_firmware_candidate", "configuration_hint_candidate")
    return _candidate(normalized_record, "emulator_compatibility", "h10_emulator_compatibility_candidate.v0", fields, "Compatibility metadata is an observation candidate, not verified compatibility, playability, or execution permission.")


def build_h10_preservation_hashset_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("hashset_name", "hash_algorithm", "hash_value_candidate", "file_name_candidate", "file_size_candidate", "media_type", "platform", "game_title", "region_candidate", "dump_status_candidate")
    return _candidate(normalized_record, "preservation_hashset", "h10_preservation_hashset_candidate.v0", fields, "Hash-set metadata is a candidate and does not prove authenticity, safety, legality, or download permission.")


def build_h10_rom_disc_media_identity_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("media_type", "file_name_candidate", "file_size_candidate", "hash_algorithm", "hash_value_candidate", "disc_id_candidate", "serial_candidate", "product_code_candidate", "region_candidate", "language_candidate", "platform", "game_title", "release_title", "dump_status_candidate")
    return _candidate(normalized_record, "rom_disc_media_identity", "h10_rom_disc_media_identity_candidate.v0", fields, "ROM/disc/media identity candidate only; it does not prove authenticity, legality, safety, playability, or acquisition permission.")


def build_h10_game_relation_candidates(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    fields = ("game_title", "release_title", "platform", "media_type", "emulator_or_runtime", "storefront_availability_candidate", "source_native_id")
    candidate = _candidate(normalized_record, "game_relation", "h10_game_relation_candidate.v0", fields, "Game relation candidate only; release, port, storefront, hash, emulator, and manual/source-code relations require review.")
    candidate["relation_kind"] = "not_evaluable" if normalized_record.get("source_record_kind") == "policy_blocked" else "release_of_game"
    candidate["review_required"] = True
    _raise_on_boundary_errors(candidate)
    return [candidate]


def build_h10_emulator_action_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("game_title", "media_type", "emulator_or_runtime", "platform", "required_bios_or_firmware_candidate", "configuration_hint_candidate")
    candidate = _candidate(normalized_record, "emulator_action", "h10_emulator_action_candidate.v0", fields, "Action candidate is blocked by H10 fixture policy and is not action permission.")
    candidate["action_kind"] = "view_metadata" if normalized_record.get("source_record_kind") != "emulator_action_blocked" else "emulate"
    candidate["action_status_current"] = "blocked_current"
    candidate["blocked_reason"] = "H10-BUNDLE-02 fixture runtime does not authorize acquisition, download, install, launch, emulator execution, game execution, mirroring, or file/hash submission."
    candidate["j_track_required"] = True
    _raise_on_boundary_errors(candidate)
    return candidate


def build_h10_games_rights_safety_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("rights_safety_metadata", "storefront_availability_candidate", "game_title", "platform", "source_native_id")
    return _candidate(normalized_record, "games_rights_safety", "h10_games_rights_safety_candidate.v0", fields, "Rights, storefront, rating, and safety metadata is a candidate and is not rights clearance, legal acquisition truth, content safety, privacy safety, malware safety, or production readiness.")


def build_h10_source_cache_candidate_preview(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    preview = {
        "schema_version": "h10_games_emulation_source_cache_candidate_preview.v0",
        "preview_id": f"h10.source_cache.preview.{normalized_record.get('source_id')}.{_slug(normalized_record.get('source_native_id'))}.v0",
        "source_id": normalized_record.get("source_id"),
        "source_record_ref": normalized_record.get("normalized_record_id"),
        "preview_only": True,
        "accepted_source": False,
        "mutates_source_cache": False,
        "supporting_fields": {
            "source_native_id": normalized_record.get("source_native_id"),
            "source_record_kind": normalized_record.get("source_record_kind"),
            "game_title": normalized_record.get("game_title"),
        },
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": ["Source-cache preview only; no source cache write or source truth acceptance occurs."],
    }
    _raise_on_boundary_errors(preview)
    return preview


def build_h10_evidence_candidate_preview(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    preview = {
        "schema_version": "h10_games_emulation_evidence_candidate_preview.v0",
        "preview_id": f"h10.evidence.preview.{normalized_record.get('source_id')}.{_slug(normalized_record.get('source_native_id'))}.v0",
        "source_id": normalized_record.get("source_id"),
        "source_record_ref": normalized_record.get("normalized_record_id"),
        "preview_only": True,
        "accepted_evidence": False,
        "mutates_evidence_ledger": False,
        "supporting_fields": {
            "source_native_id": normalized_record.get("source_native_id"),
            "game_title": normalized_record.get("game_title"),
            "platform": normalized_record.get("platform"),
        },
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": ["Evidence preview only; no evidence ledger write or evidence truth acceptance occurs."],
    }
    _raise_on_boundary_errors(preview)
    return preview


def build_h10_fixture_replay_result(fixture: Mapping[str, Any], normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    relation_candidates = normalized_record.get("game_relation_candidate") or []
    result = {
        "schema_version": "h10_games_emulation_fixture_replay_result.v0",
        "replay_result_id": f"h10.replay.{normalized_record.get('source_id')}.{_slug(fixture.get('fixture_id'))}.v0",
        "source_id": normalized_record.get("source_id"),
        "connector_family": normalized_record.get("connector_family"),
        "fixture_ref": fixture.get("fixture_id"),
        "fixture_kind": fixture.get("fixture_kind"),
        "replay_status": "blocked_by_policy_fixture" if fixture.get("fixture_kind") == "policy_blocked" else "fixture_replay_completed",
        "normalized_record": dict(normalized_record),
        "candidate_counts": {
            "game_software_identity_candidates": 1,
            "platform_release_edition_candidates": 1,
            "emulator_compatibility_candidates": 1,
            "preservation_hashset_candidates": 1,
            "rom_disc_media_identity_candidates": 1,
            "game_relation_candidates": len(relation_candidates),
            "emulator_action_candidates": 1,
            "rights_safety_candidates": 1,
            "source_cache_candidate_previews": 1,
            "evidence_candidate_previews": 1,
        },
        "no_network_used": True,
        "no_live_source_used": True,
        "no_api_catalog_query_used": True,
        "no_software_list_hashset_fetch_used": True,
        "no_download_upload_execute_acquire_used": True,
        "no_scraping_crawling_used": True,
        "no_restricted_source_access_used": True,
        "no_public_master_index_mutation": True,
        "no_truth_acceptance": True,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": _list(fixture.get("limitations")) + ["Fixture replay result only; no public truth or production readiness is claimed."],
        "notes": ["Offline committed fixture replay; no live connector runtime was used."],
    }
    _raise_on_boundary_errors(result)
    return result


def summarize_h10_normalized_record(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "h10_games_emulation_normalized_record_summary.v0",
        "source_id": record.get("source_id"),
        "source_record_kind": record.get("source_record_kind"),
        "game_title": record.get("game_title"),
        "platform": record.get("platform"),
        "fixture_only": True,
        "candidate_counts": {
            "game_software_identity_candidates": 1 if record.get("game_software_identity_candidate") else 0,
            "platform_release_edition_candidates": 1 if record.get("platform_release_edition_candidate") else 0,
            "emulator_compatibility_candidates": 1 if record.get("emulator_compatibility_candidate") else 0,
            "preservation_hashset_candidates": 1 if record.get("preservation_hashset_candidate") else 0,
            "rom_disc_media_identity_candidates": 1 if record.get("rom_disc_media_identity_candidate") else 0,
            "game_relation_candidates": len(record.get("game_relation_candidate") or []),
            "emulator_action_candidates": 1 if record.get("emulator_action_candidate") else 0,
            "rights_safety_candidates": 1 if record.get("games_rights_safety_candidate") else 0,
        },
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }


def detect_h10_truth_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return _detect_true_keys(record, TRUTH_FORBIDDEN_TRUE_KEYS)


def detect_h10_product_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return _detect_true_keys(record, PRODUCT_FORBIDDEN_TRUE_KEYS)


def _candidate(normalized_record: Mapping[str, Any], candidate_type: str, schema_version: str, fields: tuple[str, ...], limitation: str) -> dict[str, Any]:
    source_id = _text(normalized_record.get("source_id")) or "unknown"
    native_id = _text(normalized_record.get("source_native_id")) or "unknown"
    supporting = [field for field in fields if _is_present(normalized_record.get(field))]
    candidate = {
        "schema_version": schema_version,
        "candidate_id": f"h10.{candidate_type}.{source_id}.{_slug(native_id)}.v0",
        "candidate_type": candidate_type,
        "source_id": source_id,
        "source_record_ref": str(normalized_record.get("normalized_record_id") or "unknown"),
        "supporting_fields": {field: normalized_record.get(field, "unknown") for field in fields},
        "missing_fields": [field for field in fields if field not in supporting],
        "confidence_or_uncertainty": {
            "confidence": "low",
            "uncertainty": "fixture-only metadata candidate requiring review",
        },
        "limitations": [limitation, "Candidate-only output; no source, evidence, candidate, identity, relation, action, rights, safety, public, public-index, or master-index truth is accepted."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(candidate)
    return candidate


def _require_fixture_boundaries(fixture: Mapping[str, Any]) -> None:
    if fixture.get("schema_version") != "h10_games_emulation_fixture.v0":
        raise ValueError("fixture schema_version must be h10_games_emulation_fixture.v0")
    if fixture.get("fixture_kind") not in H10_FIXTURE_KINDS:
        raise ValueError("unknown fixture_kind")
    for key in FIXTURE_FORBIDDEN_TRUE_KEYS:
        if fixture.get(key) is True:
            raise ValueError(f"fixture boundary violation: {key} must be false")
    if not isinstance(fixture.get("fixture_payload"), Mapping):
        raise ValueError("fixture_payload must be an object")


def _missing_optional_limitations(payload: Mapping[str, Any]) -> list[str]:
    optional_fields = (
        "game_title",
        "platform",
        "release_title",
        "emulator_or_runtime",
        "hashset_name",
        "hash_value_candidate",
        "file_name_candidate",
        "rights_safety_metadata",
    )
    return [f"optional field {field} is absent or unknown in committed fixture" for field in optional_fields if not _is_present(payload.get(field))]


def _truth_boundary() -> dict[str, bool]:
    return {'normalized_record_is_public_truth': False, 'game_software_identity_candidate_is_truth': False, 'platform_release_edition_candidate_is_truth': False, 'emulator_compatibility_candidate_is_truth': False, 'preservation_hashset_candidate_is_truth': False, 'rom_disc_media_identity_candidate_is_truth': False, 'rom_disc_media_candidate_is_truth': False, 'game_relation_candidate_is_truth': False, 'emulator_action_candidate_is_action_permission': False, 'rights_safety_candidate_is_rights_or_safety_truth': False, 'hash_metadata_proves_authenticity': False, 'storefront_metadata_grants_acquisition_permission': False, 'compatibility_metadata_proves_playability': False, 'media_identity_grants_download_permission': False, 'source_cache_preview_is_accepted_source': False, 'evidence_preview_is_accepted_evidence': False, 'accepted_source_truth': False, 'accepted_evidence_truth': False, 'accepted_candidate_truth': False, 'accepted_game_identity_truth': False, 'accepted_release_truth': False, 'accepted_platform_truth': False, 'accepted_emulator_compatibility_truth': False, 'accepted_hashset_truth': False, 'accepted_rom_disc_media_truth': False, 'accepted_game_relation_truth': False, 'accepted_action_permission': False, 'accepted_rights_safety_truth': False, 'accepted_public_record': False, 'public_index_mutated': False, 'master_index_mutated': False, 'rights_clearance_claimed': False, 'legal_acquisition_claimed': False, 'rom_authenticity_claimed': False, 'disc_authenticity_claimed': False, 'compatibility_correctness_claimed': False, 'playability_claimed': False, 'installability_claimed': False, 'malware_safety_claimed': False, 'content_safety_claimed': False, 'privacy_safety_claimed': False, 'verified_authenticity_claimed': False, 'production_readiness_claimed': False, 'download_permission_granted': False, 'upload_permission_granted': False, 'hash_submission_permission_granted': False, 'execution_permission_granted': False, 'acquisition_permission_granted': False}.copy()


def _product_boundary() -> dict[str, bool]:
    return {'changed_public_search_behavior': False, 'enabled_hosting': False, 'enabled_live_probes': False, 'enabled_source_sync': False, 'enabled_downloads': False, 'enabled_uploads': False, 'enabled_execution': False, 'enabled_acquisition_actions': False, 'enabled_crawling': False, 'enabled_scraping': False, 'enabled_accounts': False, 'enabled_telemetry': False, 'mutated_public_index': False, 'mutated_master_index': False, 'network_calls_made': False, 'api_calls_made': False, 'catalog_fetch_used': False, 'software_list_fetch_used': False, 'hashset_fetch_used': False, 'rom_download_used': False, 'iso_download_used': False, 'disc_image_download_used': False, 'chd_download_used': False, 'bios_firmware_download_used': False, 'game_binary_download_used': False, 'emulator_download_used': False, 'installer_download_used': False, 'patch_download_used': False, 'asset_download_used': False, 'file_upload_used': False, 'hash_submission_used': False, 'emulator_execution_used': False, 'game_execution_used': False, 'install_execute_used': False, 'acquisition_action_used': False, 'scraping_used': False, 'crawling_used': False, 'restricted_source_access_used': False, 'bypass_or_automation_used': False}.copy()


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
    errors = detect_h10_truth_boundary_violations(record) + detect_h10_product_boundary_violations(record)
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

"""Offline H12 retro/community fixture normalization helpers."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any


H12_SOURCE_CONFIGS = {'winworld_metadata': {'source_id': 'winworld_metadata', 'source_label': 'WinWorld metadata', 'connector_family': 'retro_software_catalog', 'source_family': 'retro_community_archive', 'trust_lane': 'community'}, 'macintosh_garden_metadata': {'source_id': 'macintosh_garden_metadata', 'source_label': 'Macintosh Garden metadata', 'connector_family': 'community_archive_catalog', 'source_family': 'retro_community_archive', 'trust_lane': 'community'}, 'macintosh_repository_metadata': {'source_id': 'macintosh_repository_metadata', 'source_label': 'Macintosh Repository metadata', 'connector_family': 'community_archive_catalog', 'source_family': 'retro_community_archive', 'trust_lane': 'community'}, 'vetusware_metadata': {'source_id': 'vetusware_metadata', 'source_label': 'VetusWare metadata', 'connector_family': 'old_version_catalog', 'source_family': 'retro_community_archive', 'trust_lane': 'community'}, 'oldversion_metadata': {'source_id': 'oldversion_metadata', 'source_label': 'OldVersion metadata', 'connector_family': 'old_version_catalog', 'source_family': 'retro_community_archive', 'trust_lane': 'community'}, 'my_abandonware_metadata': {'source_id': 'my_abandonware_metadata', 'source_label': 'My Abandonware metadata', 'connector_family': 'abandonware_metadata_policy_limited', 'source_family': 'retro_community_archive', 'trust_lane': 'community'}, 'dos_games_archive_metadata': {'source_id': 'dos_games_archive_metadata', 'source_label': 'DOS Games Archive metadata', 'connector_family': 'retro_software_catalog', 'source_family': 'retro_community_archive', 'trust_lane': 'community'}, 'hobbes_os2_archive_metadata': {'source_id': 'hobbes_os2_archive_metadata', 'source_label': 'Hobbes OS/2 Archive metadata', 'connector_family': 'platform_archive_metadata', 'source_family': 'retro_community_archive', 'trust_lane': 'preservation'}, 'aminet_metadata': {'source_id': 'aminet_metadata', 'source_label': 'Aminet metadata', 'connector_family': 'platform_archive_metadata', 'source_family': 'retro_community_archive', 'trust_lane': 'preservation'}, 'atarimania_metadata': {'source_id': 'atarimania_metadata', 'source_label': 'Atarimania metadata', 'connector_family': 'retro_software_catalog', 'source_family': 'retro_community_archive', 'trust_lane': 'community'}, 'tucows_ia_legacy_metadata': {'source_id': 'tucows_ia_legacy_metadata', 'source_label': 'Tucows legacy library / Internet Archive mirror metadata', 'connector_family': 'ia_mirror_bridge', 'source_family': 'retro_community_archive', 'trust_lane': 'preservation'}, 'betaarchive_public_metadata_policy_limited': {'source_id': 'betaarchive_public_metadata_policy_limited', 'source_label': 'BetaArchive public metadata / gated-community boundary, policy-limited', 'connector_family': 'gated_community_boundary', 'source_family': 'retro_community_archive', 'trust_lane': 'community'}, 'generic_retro_community_archive': {'source_id': 'generic_retro_community_archive', 'source_label': 'Generic retro/community archive metadata', 'connector_family': 'community_archive_catalog', 'source_family': 'retro_community_archive', 'trust_lane': 'community'}}
H12_SOURCE_IDS = tuple(H12_SOURCE_CONFIGS)
H12_FIXTURE_KINDS = ('minimal', 'retro_software_identity', 'platform_version_edition', 'archive_item_member', 'compatibility_install_note', 'community_review_comment', 'hash_checksum', 'ia_wayback_corroboration', 'gated_source_boundary', 'rights_safety', 'policy_blocked')
FIXTURE_FORBIDDEN_TRUE_KEYS = {'software_binary_payload_included', 'crack_key_serial_payload_included', 'extraction_output_included', 'installer_payload_included', 'forum_or_comment_payload_included', 'bypass_or_automation_used', 'execution_output_included', 'live_call_used', 'acquisition_action_performed', 'rom_payload_included', 'hash_submission_performed', 'iso_payload_included', 'network_used', 'driver_payload_included', 'crawling_output_included', 'scraping_output_included', 'restricted_source_accessed', 'patch_payload_included', 'gated_source_payload_included', 'bios_firmware_payload_included', 'catalog_payload_included', 'account_payload_included', 'external_api_used', 'chd_payload_included', 'file_upload_performed', 'disc_image_payload_included', 'archive_payload_included'}
TRUTH_FORBIDDEN_TRUE_KEYS = {'accepted_public_record', 'public_index_mutated', 'mutated_public_index', 'malware_safety_claimed', 'production_readiness_claimed', 'playability_claimed', 'content_safety_claimed', 'accepted_community_review_truth', 'normalized_record_is_public_truth', 'master_index_mutated', 'accepted_ia_wayback_corroboration_truth', 'checksum_correctness_claimed', 'accepted_archive_item_member_truth', 'evidence_preview_is_accepted_evidence', 'compatibility_correctness_claimed', 'accepted_gated_source_access_truth', 'community_download_metadata_grants_acquisition_permission', 'retro_software_identity_candidate_is_truth', 'accepted_platform_version_truth', 'accepted_source_truth', 'abandonware_label_is_legal_permission', 'accepted_retro_software_identity_truth', 'archive_item_member_candidate_is_truth', 'accepted_rights_safety_truth', 'accepted_compatibility_install_truth', 'accepted_evidence_truth', 'privacy_safety_claimed', 'policy_pack_grants_live_access', 'source_pack_is_truth', 'platform_version_edition_candidate_is_truth', 'source_pack_is_imported_state', 'source_cache_preview_is_accepted_source', 'verified_authenticity_claimed', 'community_review_comment_candidate_is_truth', 'ia_wayback_corroboration_candidate_is_truth', 'mutated_master_index', 'archive_item_metadata_grants_download_or_extraction_permission', 'file_authenticity_claimed', 'retro_rights_safety_candidate_is_rights_or_safety_truth', 'accepted_hash_checksum_truth', 'rights_clearance_claimed', 'legal_acquisition_claimed', 'capability_grants_permission', 'source_pack_is_accepted_evidence', 'compatibility_install_note_candidate_is_truth', 'community_reputation_claimed', 'installability_claimed', 'hash_checksum_candidate_is_truth', 'accepted_candidate_truth', 'gated_source_boundary_candidate_grants_access_permission'}
PRODUCT_FORBIDDEN_TRUE_KEYS = {'enabled_telemetry', 'account_access_used', 'hash_submission_used', 'download_used', 'enabled_hosting', 'enabled_acquisition_actions', 'forum_comment_fetch_used', 'mutated_public_index', 'gated_source_access_used', 'enabled_source_sync', 'enabled_live_probes', 'bypass_or_automation_used', 'html_catalog_fetch_used', 'network_calls_made', 'crawling_used', 'upload_used', 'enabled_uploads', 'extraction_used', 'acquisition_action_used', 'mutated_master_index', 'enabled_extraction', 'enabled_crawling', 'enabled_execution', 'changed_public_search_behavior', 'enabled_accounts', 'restricted_source_access_used', 'scraping_used', 'api_calls_made', 'execution_used', 'enabled_downloads', 'catalog_fetch_used'}
NORMALIZED_SCALAR_FIELDS = ('software_title', 'alternate_title', 'product_family', 'developer', 'publisher', 'platform', 'operating_system', 'version_candidate', 'edition_candidate', 'release_date_candidate', 'language_candidate', 'region_candidate', 'category_or_genre', 'source_native_id', 'community_item_id_candidate', 'vendor_identifier_candidate', 'related_game_or_app_candidate', 'source_locator_candidate', 'platform_family', 'platform_name', 'operating_system_version_candidate', 'hardware_or_architecture_candidate', 'software_version_candidate', 'edition_name', 'release_variant', 'region_or_language', 'media_type', 'build_or_revision_candidate', 'compatibility_platform_candidate', 'version_group_candidate', 'variant_candidate', 'archive_item_id', 'archive_title', 'item_locator_candidate', 'file_name_candidate', 'file_path_candidate', 'file_size_candidate', 'file_type_candidate', 'member_count_candidate', 'package_or_archive_format_candidate', 'checksum_candidate', 'uploader_or_curator_candidate', 'uploaded_or_observed_date_candidate', 'mirror_or_archive_ref_candidate', 'source_collection_ref', 'missing_evidence', 'target_software_ref', 'target_platform_ref', 'compatibility_status_candidate', 'install_note_candidate', 'required_runtime_candidate', 'required_driver_candidate', 'required_patch_candidate', 'emulator_or_vm_hint_candidate', 'known_issue_candidate', 'workaround_candidate', 'source_snippet_or_ref', 'comment_or_review_ref', 'subject_software_ref', 'author_or_handle_hash_candidate', 'comment_date_candidate', 'claim_type', 'claim_value', 'sentiment_or_quality_candidate', 'authenticity_opinion_candidate', 'compatibility_opinion_candidate', 'missing_file_report_candidate', 'takedown_or_dispute_candidate', 'evidence_snippet_or_ref', 'confidence_or_uncertainty', 'hash_algorithm', 'hash_value_candidate', 'checksum_source', 'checksum_context', 'related_archive_item_candidate', 'related_software_candidate', 'hash_observed_at_candidate', 'source_ref', 'verification_status_candidate', 'community_source_ref', 'archive_or_wayback_ref_candidate', 'internet_archive_item_candidate', 'wayback_capture_candidate', 'cdx_or_memento_trace_candidate', 'mirrored_item_candidate', 'dead_link_trace_candidate', 'source_page_trace_candidate', 'corroboration_kind', 'gated_source_ref', 'public_metadata_allowed_candidate', 'login_required_candidate', 'invitation_required_candidate', 'account_required_candidate', 'forum_rule_or_tos_candidate', 'credential_or_token_candidate', 'private_content_risk_candidate', 'user_owned_access_required', 'allowed_current_mode', 'blocked_action_candidate', 'rights_statement_candidate', 'abandonware_label_candidate', 'freeware_shareware_public_domain_label_candidate', 'license_or_distribution_metadata_candidate', 'malware_or_security_risk_candidate', 'content_warning_candidate', 'privacy_sensitive_content_candidate', 'restricted_access_candidate', 'crack_key_serial_risk_candidate', 'leaked_or_proprietary_risk_candidate', 'acquisition_permission_current')
CANDIDATE_FIELD_MAP = {'retro_software_identity': ['software_title', 'alternate_title', 'product_family', 'developer', 'publisher', 'platform', 'operating_system', 'version_candidate', 'edition_candidate', 'release_date_candidate', 'language_candidate', 'region_candidate', 'category_or_genre', 'source_native_id', 'community_item_id_candidate', 'vendor_identifier_candidate', 'related_game_or_app_candidate', 'source_locator_candidate'], 'platform_version_edition': ['platform_family', 'platform_name', 'operating_system_version_candidate', 'hardware_or_architecture_candidate', 'software_version_candidate', 'edition_name', 'release_variant', 'region_or_language', 'media_type', 'build_or_revision_candidate', 'compatibility_platform_candidate', 'version_group_candidate', 'variant_candidate'], 'archive_item_member': ['archive_item_id', 'archive_title', 'item_locator_candidate', 'file_name_candidate', 'file_path_candidate', 'file_size_candidate', 'file_type_candidate', 'member_count_candidate', 'media_type', 'package_or_archive_format_candidate', 'checksum_candidate', 'uploader_or_curator_candidate', 'uploaded_or_observed_date_candidate', 'mirror_or_archive_ref_candidate', 'source_collection_ref', 'missing_evidence'], 'compatibility_install_note': ['target_software_ref', 'target_platform_ref', 'compatibility_status_candidate', 'install_note_candidate', 'required_runtime_candidate', 'required_driver_candidate', 'required_patch_candidate', 'emulator_or_vm_hint_candidate', 'known_issue_candidate', 'workaround_candidate', 'source_snippet_or_ref', 'confidence_or_uncertainty'], 'community_review_comment': ['comment_or_review_ref', 'subject_software_ref', 'author_or_handle_hash_candidate', 'comment_date_candidate', 'claim_type', 'claim_value', 'sentiment_or_quality_candidate', 'authenticity_opinion_candidate', 'compatibility_opinion_candidate', 'missing_file_report_candidate', 'takedown_or_dispute_candidate', 'evidence_snippet_or_ref', 'confidence_or_uncertainty'], 'hash_checksum': ['hash_algorithm', 'hash_value_candidate', 'checksum_source', 'checksum_context', 'file_name_candidate', 'file_size_candidate', 'related_archive_item_candidate', 'related_software_candidate', 'hash_observed_at_candidate', 'source_ref', 'verification_status_candidate', 'missing_evidence'], 'ia_wayback_corroboration': ['community_source_ref', 'archive_or_wayback_ref_candidate', 'internet_archive_item_candidate', 'wayback_capture_candidate', 'cdx_or_memento_trace_candidate', 'mirrored_item_candidate', 'dead_link_trace_candidate', 'source_page_trace_candidate', 'corroboration_kind', 'confidence_or_uncertainty', 'missing_evidence'], 'gated_source_boundary': ['gated_source_ref', 'public_metadata_allowed_candidate', 'login_required_candidate', 'invitation_required_candidate', 'account_required_candidate', 'forum_rule_or_tos_candidate', 'credential_or_token_candidate', 'private_content_risk_candidate', 'user_owned_access_required', 'allowed_current_mode', 'blocked_action_candidate'], 'retro_rights_safety': ['rights_statement_candidate', 'abandonware_label_candidate', 'freeware_shareware_public_domain_label_candidate', 'license_or_distribution_metadata_candidate', 'takedown_or_dispute_candidate', 'malware_or_security_risk_candidate', 'content_warning_candidate', 'privacy_sensitive_content_candidate', 'restricted_access_candidate', 'crack_key_serial_risk_candidate', 'leaked_or_proprietary_risk_candidate', 'blocked_action_candidate', 'acquisition_permission_current']}


def load_h12_retro_community_fixture(path: str | Path) -> dict[str, Any]:
    fixture_path = Path(path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    _require_fixture_boundaries(payload)
    return payload


def normalize_h12_retro_community_fixture(raw_fixture: Mapping[str, Any], source_id: str, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Normalize a committed H12 fixture without live access or side effects."""
    _require_fixture_boundaries(raw_fixture)
    if source_id not in H12_SOURCE_CONFIGS:
        raise ValueError(f"unknown H12 source_id: {source_id}")
    if raw_fixture.get("source_id") != source_id:
        raise ValueError("fixture source_id does not match requested source")
    config = H12_SOURCE_CONFIGS[source_id]
    payload = _mapping(raw_fixture.get("fixture_payload"), "fixture_payload")
    native_id = _text(payload.get("source_native_id")) or _text(raw_fixture.get("fixture_id")) or "unknown"
    fixture_kind = _text(raw_fixture.get("fixture_kind")) or "unknown"
    record: dict[str, Any] = {
        "schema_version": "h12_retro_community_normalized_record.v0",
        "normalized_record_id": f"h12.normalized.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "connector_family": config["connector_family"],
        "source_record_kind": _text(payload.get("source_record_kind")) or fixture_kind,
        "source_metadata": {
            "fixture_id": raw_fixture.get("fixture_id", "unknown"),
            "fixture_kind": fixture_kind,
            "fixture_status": raw_fixture.get("fixture_status", "unknown"),
            "source_label": config["source_label"],
            "trust_lane": config["trust_lane"],
            "metadata_summary": payload.get("metadata_summary", "synthetic fixture metadata only"),
        },
        "source_limitations": _dedupe(_list(raw_fixture.get("limitations")) + _missing_optional_limitations(payload)),
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": [
            "Offline H12 fixture normalization only.",
            "Candidate and preview outputs require review and do not grant live access, downloads, extraction, execution, acquisition, upload, hash submission, gated-source access, evidence acceptance, or public truth.",
        ],
    }
    for field in NORMALIZED_SCALAR_FIELDS:
        record[field] = _value(payload.get(field))
    record["ia_wayback_corroboration_metadata"] = _mapping(payload.get("ia_wayback_corroboration_metadata"), "ia_wayback_corroboration_metadata") if isinstance(payload.get("ia_wayback_corroboration_metadata"), Mapping) else {}
    record["gated_source_boundary_metadata"] = _mapping(payload.get("gated_source_boundary_metadata"), "gated_source_boundary_metadata") if isinstance(payload.get("gated_source_boundary_metadata"), Mapping) else {}
    record["rights_safety_metadata"] = _mapping(payload.get("rights_safety_metadata"), "rights_safety_metadata") if isinstance(payload.get("rights_safety_metadata"), Mapping) else {}
    record["retro_software_identity_candidate"] = build_h12_retro_software_identity_candidate(record, policy)
    record["platform_version_edition_candidate"] = build_h12_platform_version_edition_candidate(record, policy)
    record["archive_item_member_candidate"] = build_h12_archive_item_member_candidate(record, policy)
    record["compatibility_install_note_candidate"] = build_h12_compatibility_install_note_candidates(record, policy)
    record["community_review_comment_candidate"] = build_h12_community_review_comment_candidates(record, policy)
    record["hash_checksum_candidate"] = build_h12_hash_checksum_candidate(record, policy)
    record["ia_wayback_corroboration_candidate"] = build_h12_ia_wayback_corroboration_candidate(record, policy)
    record["gated_source_boundary_candidate"] = build_h12_gated_source_boundary_candidate(record, policy)
    record["retro_rights_safety_candidate"] = build_h12_retro_rights_safety_candidate(record, policy)
    record["source_cache_candidate_preview"] = build_h12_source_cache_candidate_preview(record, policy)
    record["evidence_candidate_preview"] = build_h12_evidence_candidate_preview(record, policy)
    _raise_on_boundary_errors(record)
    return record


def build_h12_retro_software_identity_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _candidate(normalized_record, "retro_software_identity", "h12_retro_software_identity_candidate.v0", CANDIDATE_FIELD_MAP["retro_software_identity"], "Retro software identity candidate only; title/platform/version matches do not prove same object, availability, rights, installability, playability, or safety.")


def build_h12_platform_version_edition_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _candidate(normalized_record, "platform_version_edition", "h12_platform_version_edition_candidate.v0", CANDIDATE_FIELD_MAP["platform_version_edition"], "Platform/version/edition candidate only; platform match does not prove compatibility, installability, or legal acquisition.")


def build_h12_archive_item_member_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    candidate = _candidate(normalized_record, "archive_item_member", "h12_archive_item_member_candidate.v0", CANDIDATE_FIELD_MAP["archive_item_member"], "Archive item/member candidate only; file/member metadata does not prove authenticity or grant download, extraction, mirror, or execution permission.")
    candidate["download_permission_current"] = "blocked_current"
    candidate["extraction_permission_current"] = "blocked_current"
    _raise_on_boundary_errors(candidate)
    return candidate


def build_h12_compatibility_install_note_candidates(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    candidate = _candidate(normalized_record, "compatibility_install_note", "h12_compatibility_install_note_candidate.v0", CANDIDATE_FIELD_MAP["compatibility_install_note"], "Compatibility/install-note candidate only; community notes are source observations and do not authorize execution.")
    candidate["execution_permission_current"] = "blocked_current"
    candidate["track_j_required_before_action"] = True
    _raise_on_boundary_errors(candidate)
    return candidate


def build_h12_community_review_comment_candidates(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _candidate(normalized_record, "community_review_comment", "h12_community_review_comment_candidate.v0", CANDIDATE_FIELD_MAP["community_review_comment"], "Community review/comment candidate only; claims may be wrong, stale, malicious, subjective, or source-specific.")


def build_h12_hash_checksum_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    candidate = _candidate(normalized_record, "hash_checksum", "h12_hash_checksum_candidate.v0", CANDIDATE_FIELD_MAP["hash_checksum"], "Hash/checksum candidate only; hash metadata does not prove lawful acquisition, file authenticity, checksum correctness, or malware safety.")
    candidate["hash_submission_current"] = "blocked_current"
    _raise_on_boundary_errors(candidate)
    return candidate


def build_h12_ia_wayback_corroboration_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _candidate(normalized_record, "ia_wayback_corroboration", "h12_ia_wayback_corroboration_candidate.v0", CANDIDATE_FIELD_MAP["ia_wayback_corroboration"], "IA/Wayback corroboration candidate only; archived traces do not prove file authenticity, rights, acquisition, download, or redistribution permission.")


def build_h12_gated_source_boundary_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    candidate = _candidate(normalized_record, "gated_source_boundary", "h12_gated_source_boundary_candidate.v0", CANDIDATE_FIELD_MAP["gated_source_boundary"], "Gated/community-restricted source boundary candidate only; accounts, cookies, tokens, private forums, invitation-only pages, and gated downloads are blocked.")
    candidate["access_permission_current"] = "blocked_current"
    candidate["credentials_handled"] = False
    _raise_on_boundary_errors(candidate)
    return candidate


def build_h12_retro_rights_safety_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    candidate = _candidate(normalized_record, "retro_rights_safety", "h12_retro_rights_safety_candidate.v0", CANDIDATE_FIELD_MAP["retro_rights_safety"], "Retro rights/safety candidate only; rights labels, abandonware labels, and safety notes are not rights clearance, legal acquisition, malware safety, content safety, or privacy safety.")
    candidate["acquisition_permission_current"] = False
    _raise_on_boundary_errors(candidate)
    return candidate


def build_h12_source_cache_candidate_preview(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    preview = {
        "schema_version": "h12_retro_community_source_cache_candidate_preview.v0",
        "preview_id": f"h12.source_cache.preview.{normalized_record.get('source_id')}.{_slug(normalized_record.get('source_native_id'))}.v0",
        "source_id": normalized_record.get("source_id"),
        "source_record_ref": normalized_record.get("normalized_record_id"),
        "preview_only": True,
        "accepted_source": False,
        "mutates_source_cache": False,
        "supporting_fields": {
            "source_native_id": normalized_record.get("source_native_id"),
            "source_record_kind": normalized_record.get("source_record_kind"),
            "software_title": normalized_record.get("software_title"),
        },
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": ["Source-cache preview only; no source cache write or source truth acceptance occurs."],
    }
    _raise_on_boundary_errors(preview)
    return preview


def build_h12_evidence_candidate_preview(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    preview = {
        "schema_version": "h12_retro_community_evidence_candidate_preview.v0",
        "preview_id": f"h12.evidence.preview.{normalized_record.get('source_id')}.{_slug(normalized_record.get('source_native_id'))}.v0",
        "source_id": normalized_record.get("source_id"),
        "source_record_ref": normalized_record.get("normalized_record_id"),
        "preview_only": True,
        "accepted_evidence": False,
        "mutates_evidence_ledger": False,
        "claim_summary": "Retro/community fixture metadata candidate only.",
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": ["Evidence preview only; no evidence acceptance occurs."],
    }
    _raise_on_boundary_errors(preview)
    return preview


def build_h12_fixture_replay_result(fixture: Mapping[str, Any], normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    result = {
        "schema_version": "h12_retro_community_fixture_replay_result.v0",
        "fixture_replay_result_id": f"h12.replay.{fixture.get('source_id')}.{fixture.get('fixture_kind')}.v0",
        "source_id": fixture.get("source_id"),
        "connector_family": normalized_record.get("connector_family"),
        "fixture_ref": fixture.get("fixture_id"),
        "normalized_record_ref": normalized_record.get("normalized_record_id"),
        "result_status": "normalized_fixture",
        "network_used": False,
        "download_extract_execute_acquire_used": False,
        "candidate_counts": {
            "retro_software_identity_candidate": 1,
            "platform_version_edition_candidate": 1,
            "archive_item_member_candidate": 1,
            "compatibility_install_note_candidate": 1,
            "community_review_comment_candidate": 1,
            "hash_checksum_candidate": 1,
            "ia_wayback_corroboration_candidate": 1,
            "gated_source_boundary_candidate": 1,
            "retro_rights_safety_candidate": 1,
        },
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": ["Fixture replay output is not source, evidence, candidate, public, or master truth."],
    }
    _raise_on_boundary_errors(result)
    return result


def summarize_h12_normalized_record(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": record.get("source_id"),
        "source_record_kind": record.get("source_record_kind"),
        "software_title": record.get("software_title"),
        "platform_name": record.get("platform_name"),
        "candidate_count": 9,
        "truth_boundary_violations": detect_h12_truth_boundary_violations(record),
        "product_boundary_violations": detect_h12_product_boundary_violations(record),
    }


def detect_h12_truth_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    violations: list[str] = []
    _collect_true_keys(record, TRUTH_FORBIDDEN_TRUE_KEYS, "truth", violations)
    return violations


def detect_h12_product_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    violations: list[str] = []
    _collect_true_keys(record, PRODUCT_FORBIDDEN_TRUE_KEYS, "product", violations)
    return violations


def _candidate(normalized_record: Mapping[str, Any], kind: str, schema_version: str, fields: list[str], limitation: str) -> dict[str, Any]:
    supporting = {field: normalized_record.get(field) for field in fields if normalized_record.get(field) not in (None, "", [], {}, "unknown")}
    missing = [field for field in fields if field not in supporting]
    candidate = {
        "schema_version": schema_version,
        "candidate_id": f"h12.{kind}.{normalized_record.get('source_id')}.{_slug(normalized_record.get('source_native_id'))}.v0",
        "source_id": normalized_record.get("source_id"),
        "source_record_ref": normalized_record.get("normalized_record_id"),
        "candidate_kind": kind,
        "supporting_fields": supporting,
        "missing_fields": missing,
        "confidence_or_uncertainty": "low_confidence_fixture_candidate",
        "limitations": [limitation, "Review required before downstream use."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(candidate)
    return candidate


def _require_fixture_boundaries(raw_fixture: Mapping[str, Any]) -> None:
    if not isinstance(raw_fixture, Mapping):
        raise ValueError("fixture must be a mapping")
    errors: list[str] = []
    _collect_true_keys(raw_fixture, FIXTURE_FORBIDDEN_TRUE_KEYS, "fixture", errors)
    _collect_true_keys(raw_fixture, TRUTH_FORBIDDEN_TRUE_KEYS, "truth", errors)
    _collect_true_keys(raw_fixture, PRODUCT_FORBIDDEN_TRUE_KEYS, "product", errors)
    if errors:
        raise ValueError("; ".join(errors))


def _raise_on_boundary_errors(record: Mapping[str, Any]) -> None:
    errors = detect_h12_truth_boundary_violations(record) + detect_h12_product_boundary_violations(record)
    if errors:
        raise ValueError("; ".join(errors))


def _collect_true_keys(value: Any, forbidden: set[str], prefix: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key) in forbidden and item is True:
                errors.append(f"{prefix} boundary true claim: {key}")
            _collect_true_keys(item, forbidden, prefix, errors)
    elif isinstance(value, list):
        for item in value:
            _collect_true_keys(item, forbidden, prefix, errors)


def _truth_boundary() -> dict[str, bool]:
    return {key: False for key in TRUTH_FORBIDDEN_TRUE_KEYS}


def _product_boundary() -> dict[str, bool]:
    return {key: False for key in PRODUCT_FORBIDDEN_TRUE_KEYS}


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be a mapping")
    return value


def _value(value: Any) -> Any:
    if value is None:
        return "unknown"
    if isinstance(value, str):
        return value.strip() or "unknown"
    return value


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _missing_optional_limitations(payload: Mapping[str, Any]) -> list[str]:
    missing = [field for field in NORMALIZED_SCALAR_FIELDS if field not in payload]
    if not missing:
        return []
    return [f"Missing optional H12 fixture fields are unknown, not fabricated: {', '.join(missing[:10])}"]


def _dedupe(values: list[str]) -> list[str]:
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
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]

"""Fixture-only H4 code/source/release host normalization helpers."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from typing import Any

from runtime.connectors.core.output_envelope import build_connector_output_envelope


H4_SOURCE_CONFIGS: dict[str, dict[str, Any]] = {'software_heritage_identity': {'label': 'Software Heritage identity and archival metadata', 'connector_family': 'source_archive_identity', 'source_host': 'Software Heritage', 'owner': 'example-org', 'repository': 'example-preserved-project', 'project': 'example-preserved-project', 'trust_lane': 'preservation', 'has_release': True, 'has_asset': False, 'has_swhid': True, 'has_git_object': True, 'relation_kind': 'source_release_claim'}, 'github_repository': {'label': 'GitHub repository metadata', 'connector_family': 'api_json', 'source_host': 'GitHub', 'owner': 'example-org', 'repository': 'example-repository', 'project': 'example-repository', 'trust_lane': 'official', 'has_release': False, 'has_asset': False, 'has_swhid': False, 'has_git_object': True, 'relation_kind': 'tag_to_release_candidate'}, 'github_releases': {'label': 'GitHub Releases metadata', 'connector_family': 'api_json', 'source_host': 'GitHub', 'owner': 'example-org', 'repository': 'example-release-repository', 'project': 'example-release-repository', 'trust_lane': 'official', 'has_release': True, 'has_asset': True, 'has_swhid': False, 'has_git_object': True, 'relation_kind': 'tag_to_release_candidate'}, 'gitlab_repository': {'label': 'GitLab repository metadata', 'connector_family': 'api_json', 'source_host': 'GitLab', 'owner': 'example-group', 'repository': 'example-repository', 'project': 'example-repository', 'trust_lane': 'official', 'has_release': False, 'has_asset': False, 'has_swhid': False, 'has_git_object': True, 'relation_kind': 'tag_to_release_candidate'}, 'gitlab_releases': {'label': 'GitLab Releases metadata', 'connector_family': 'api_json', 'source_host': 'GitLab', 'owner': 'example-group', 'repository': 'example-release-repository', 'project': 'example-release-repository', 'trust_lane': 'official', 'has_release': True, 'has_asset': True, 'has_swhid': False, 'has_git_object': True, 'relation_kind': 'tag_to_release_candidate'}, 'sourceforge': {'label': 'SourceForge project and release/file metadata', 'connector_family': 'html_catalog', 'source_host': 'SourceForge', 'owner': 'example-projects', 'repository': 'example-sourceforge-project', 'project': 'example-sourceforge-project', 'trust_lane': 'community', 'has_release': True, 'has_asset': True, 'has_swhid': False, 'has_git_object': False, 'relation_kind': 'release_asset_claim'}, 'fosshub': {'label': 'FossHub project and release metadata', 'connector_family': 'html_catalog', 'source_host': 'FossHub', 'owner': 'example-publisher', 'repository': 'example-fosshub-project', 'project': 'example-fosshub-project', 'trust_lane': 'community', 'has_release': True, 'has_asset': True, 'has_swhid': False, 'has_git_object': False, 'relation_kind': 'release_asset_claim'}, 'github_archive_program': {'label': 'GitHub Archive Program archive-presence metadata', 'connector_family': 'archival_metadata', 'source_host': 'GitHub Archive Program', 'owner': 'example-org', 'repository': 'example-archived-repository', 'project': 'example-archived-repository', 'trust_lane': 'preservation', 'has_release': False, 'has_asset': False, 'has_swhid': True, 'has_git_object': True, 'relation_kind': 'not_evaluable'}, 'generic_git_repository': {'label': 'Generic Git repository metadata', 'connector_family': 'git_metadata_future', 'source_host': 'generic_git_host_candidate', 'owner': 'example-namespace', 'repository': 'example-git-repository', 'project': 'example-git-repository', 'trust_lane': 'unknown', 'has_release': False, 'has_asset': False, 'has_swhid': False, 'has_git_object': True, 'relation_kind': 'tag_to_release_candidate'}, 'generic_release_host': {'label': 'Generic release-host metadata', 'connector_family': 'release_host_metadata', 'source_host': 'generic_release_host_candidate', 'owner': 'example-publisher', 'repository': 'example-release-project', 'project': 'example-release-project', 'trust_lane': 'unknown', 'has_release': True, 'has_asset': True, 'has_swhid': False, 'has_git_object': False, 'relation_kind': 'release_asset_claim'}}
H4_SOURCE_IDS = tuple(H4_SOURCE_CONFIGS)
H4_FIXTURE_KINDS = ("minimal", "typical", "source_identity", "release", "source_to_binary", "policy_blocked")

FORBIDDEN_TRUTH_TRUE_KEYS = {
    "normalized_record_is_public_truth",
    "source_identity_candidate_is_truth",
    "source_identity_candidate_is_accepted_identity",
    "release_identity_candidate_is_truth",
    "release_identity_candidate_is_accepted_release_truth",
    "source_to_binary_relation_candidate_is_provenance_truth",
    "relation_candidate_is_accepted_provenance",
    "git_object_candidate_is_accepted_provenance",
    "git_object_candidate_is_provenance_truth",
    "swhid_candidate_is_accepted_object_truth",
    "swhid_candidate_is_object_truth",
    "repository_url_proves_official_status",
    "release_asset_metadata_grants_download_permission",
    "release_notes_prove_installability",
    "tag_release_match_proves_build_relation",
    "asset_presence_proves_source_relationship",
    "sbom_signature_metadata_proves_trust",
    "asset_hash_proves_malware_safety",
    "release_asset_hash_candidate_is_malware_safety",
    "signature_metadata_proves_authenticity",
    "signature_metadata_is_authenticity",
    "sbom_metadata_is_provenance",
    "license_metadata_is_rights_clearance",
    "source_cache_preview_is_accepted_source",
    "evidence_preview_is_accepted_evidence",
    "accepted_source_truth",
    "accepted_evidence_truth",
    "accepted_candidate_truth",
    "accepted_source_identity_truth",
    "accepted_release_identity_truth",
    "accepted_source_to_binary_relation_truth",
    "accepted_public_record",
    "public_index_mutated",
    "master_index_mutated",
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "verified_installability_claimed",
    "verified_authenticity_claimed",
    "verified_build_reproducibility_claimed",
    "production_readiness_claimed",
    "download_allowed_current",
    "payload_available_current",
}

FORBIDDEN_PRODUCT_TRUE_KEYS = {
    "changed_public_search_behavior",
    "enabled_hosting",
    "enabled_live_probes",
    "enabled_source_sync",
    "enabled_source_connectors",
    "enabled_repository_clone",
    "enabled_downloads",
    "enabled_installers",
    "enabled_execution",
    "enabled_uploads",
    "enabled_accounts",
    "enabled_telemetry",
    "mutated_public_index",
    "mutated_master_index",
    "network_calls_made",
    "api_calls_made",
    "repository_clone_used",
    "source_archive_download_used",
    "release_asset_download_used",
    "git_command_invoked",
    "build_tool_invoked",
    "install_execute_used",
    "repository_payload_included",
    "source_archive_payload_included",
    "release_asset_payload_included",
}


def normalize_h4_code_source_fixture(raw_fixture: Mapping[str, Any], source_id: str, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Normalize a committed H4 fixture into candidate-only records."""

    if source_id not in H4_SOURCE_CONFIGS:
        raise ValueError(f"unknown H4 source_id: {source_id}")
    if raw_fixture.get("source_id") != source_id:
        raise ValueError(f"fixture source_id does not match requested source_id: {source_id}")
    _require_fixture_boundaries(raw_fixture)
    payload = _mapping(raw_fixture.get("fixture_payload"), "fixture_payload")
    config = H4_SOURCE_CONFIGS[source_id]
    limitations = list(raw_fixture.get("limitations") or [])
    limitations.extend(_missing_optional_limitations(payload))
    if raw_fixture.get("fixture_status") == "policy_blocked":
        limitations.append("fixture is policy-blocked and remains candidate-only")
    native_id = _text(payload.get("source_native_id")) or f"fixture-{source_id}"
    release_assets = _list_of_mappings(payload.get("release_assets"))
    relation_payload = _mapping(payload.get("source_to_binary_relation"), "source_to_binary_relation", default={})
    source_host = _text(payload.get("source_host")) or str(config["source_host"])
    repository_name = _text(payload.get("repository_name")) or "unknown"
    project_name = _text(payload.get("project_name")) or repository_name
    record: dict[str, Any] = {
        "schema_version": "h4_code_source_normalized_record.v0",
        "normalized_record_id": f"h4.normalized.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "connector_family": str(raw_fixture.get("connector_family") or config["connector_family"]),
        "source_host": source_host,
        "owner_or_namespace": _text(payload.get("owner_or_namespace")) or "unknown",
        "repository_name": repository_name,
        "project_name": project_name,
        "origin_url_candidate": _text(payload.get("origin_url_candidate")) or "unknown",
        "repository_url_candidate": _text(payload.get("repository_url_candidate")) or "unknown",
        "source_native_id": native_id,
        "git_commit_id_candidate": _text(payload.get("git_commit_id_candidate")) or "unknown",
        "git_tree_id_candidate": _text(payload.get("git_tree_id_candidate")) or "unknown",
        "git_tag_candidate": _text(payload.get("git_tag_candidate")) or "unknown",
        "branch_name_candidate": _text(payload.get("branch_name_candidate")) or "unknown",
        "release_id": _text(payload.get("release_id")) or "unknown",
        "release_tag": _text(payload.get("release_tag")) or "unknown",
        "release_name": _text(payload.get("release_name")) or "unknown",
        "release_version": _text(payload.get("release_version")) or "unknown",
        "release_timestamp": _text(payload.get("release_timestamp")) or "unknown",
        "release_actor_or_author": _text(payload.get("release_actor_or_author")) or "unknown",
        "release_notes_ref": _text(payload.get("release_notes_ref")) or "unknown",
        "release_notes_summary": _text(payload.get("release_notes_summary")) or "unknown",
        "release_asset_summary": _mapping(payload.get("release_asset_summary"), "release_asset_summary", default={"asset_count": len(release_assets), "download_allowed_current": False, "payload_available_current": False}),
        "swhid_candidate": _text(payload.get("swhid_candidate")) or "unknown",
        "archived_origin_candidate": _text(payload.get("archived_origin_candidate")) or "unknown",
        "license_metadata": _mapping(payload.get("license_metadata"), "license_metadata", default={"declared_license": "unknown", "rights_clearance_claimed": False}),
        "readme_ref": _text(payload.get("readme_ref")) or "unknown",
        "changelog_ref": _text(payload.get("changelog_ref")) or "unknown",
        "source_archive_locator_candidate": _text(payload.get("source_archive_locator_candidate")) or "unknown",
        "project_urls": _strings(payload.get("project_urls")),
        "source_metadata": _mapping(payload.get("source_metadata"), "source_metadata", default={}),
        "source_limitations": _dedupe(limitations),
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Fixture-only H4 normalized record; review is required before any downstream use."],
    }
    record["source_identity_candidate"] = build_h4_source_identity_candidate(record, policy)
    record["release_identity_candidate"] = build_h4_release_identity_candidate(record, policy)
    record["source_to_binary_relation_candidate"] = relation_payload
    record["source_to_binary_relation_candidate_preview"] = build_h4_source_to_binary_relation_candidates(record, policy)
    record["release_asset_candidate_preview"] = build_h4_release_asset_candidates({"normalized_record": record, "release_assets": release_assets}, policy)
    record["source_cache_candidate_preview"] = build_h4_source_cache_candidate_preview(record, policy)
    record["evidence_candidate_preview"] = build_h4_evidence_candidate_preview(record, policy)
    _raise_on_boundary_errors(record)
    return record


def build_h4_source_identity_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = str(normalized_record.get("source_id"))
    native_id = str(normalized_record.get("source_native_id") or "unknown")
    supporting = [
        key for key in (
            "source_host",
            "owner_or_namespace",
            "repository_name",
            "project_name",
            "origin_url_candidate",
            "repository_url_candidate",
            "source_native_id",
            "git_commit_id_candidate",
            "git_tree_id_candidate",
            "git_tag_candidate",
            "branch_name_candidate",
            "swhid_candidate",
            "archived_origin_candidate",
        ) if normalized_record.get(key) not in (None, "", "unknown", [], {})
    ]
    missing = [
        key for key in (
            "origin_url_candidate",
            "repository_url_candidate",
            "git_commit_id_candidate",
            "swhid_candidate",
            "archived_origin_candidate",
        ) if normalized_record.get(key) in (None, "", "unknown", [], {})
    ]
    candidate = {
        "schema_version": "h4_source_identity_candidate.v0",
        "source_identity_candidate_id": f"h4.source_identity.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "source_host": normalized_record.get("source_host", "unknown"),
        "owner_or_namespace": normalized_record.get("owner_or_namespace", "unknown"),
        "repository_name": normalized_record.get("repository_name", "unknown"),
        "project_name": normalized_record.get("project_name", "unknown"),
        "origin_url_candidate": normalized_record.get("origin_url_candidate", "unknown"),
        "repository_url_candidate": normalized_record.get("repository_url_candidate", "unknown"),
        "source_native_id": native_id,
        "git_commit_id_candidate": normalized_record.get("git_commit_id_candidate", "unknown"),
        "git_tree_id_candidate": normalized_record.get("git_tree_id_candidate", "unknown"),
        "git_tag_candidate": normalized_record.get("git_tag_candidate", "unknown"),
        "branch_name_candidate": normalized_record.get("branch_name_candidate", "unknown"),
        "swhid_candidate": normalized_record.get("swhid_candidate", "unknown"),
        "archived_origin_candidate": normalized_record.get("archived_origin_candidate", "unknown"),
        "confidence_or_uncertainty": "candidate_from_fixture_no_truth_acceptance",
        "supporting_fields": supporting,
        "missing_fields": missing,
        "limitations": ["Source identity candidate requires review and does not prove official status or provenance."],
        "truth_boundary": {
            "source_identity_candidate_is_accepted_identity": False,
            "source_identity_candidate_is_truth": False,
            "git_object_candidate_is_accepted_provenance": False,
            "git_object_candidate_is_provenance_truth": False,
            "swhid_candidate_is_accepted_object_truth": False,
            "swhid_candidate_is_object_truth": False,
            "repository_url_proves_official_status": False,
            "license_metadata_is_rights_clearance": False,
        },
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(candidate)
    return candidate


def build_h4_release_identity_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = str(normalized_record.get("source_id"))
    release_id = str(normalized_record.get("release_id") or "unknown")
    supporting = [
        key for key in ("release_id", "release_tag", "release_name", "release_version", "release_timestamp", "release_notes_summary")
        if normalized_record.get(key) not in (None, "", "unknown", [], {})
    ]
    missing = [
        key for key in ("release_id", "release_tag", "release_version", "release_timestamp")
        if normalized_record.get(key) in (None, "", "unknown", [], {})
    ]
    candidate = {
        "schema_version": "h4_release_identity_candidate.v0",
        "release_identity_candidate_id": f"h4.release_identity.{source_id}.{_slug(release_id)}.v0",
        "source_id": source_id,
        "source_identity_candidate_ref": normalized_record.get("source_identity_candidate", {}).get("source_identity_candidate_id"),
        "release_id": release_id,
        "release_tag": normalized_record.get("release_tag", "unknown"),
        "release_name": normalized_record.get("release_name", "unknown"),
        "release_version": normalized_record.get("release_version", "unknown"),
        "release_timestamp": normalized_record.get("release_timestamp", "unknown"),
        "release_actor_or_author": normalized_record.get("release_actor_or_author", "unknown"),
        "release_notes_ref": normalized_record.get("release_notes_ref", "unknown"),
        "release_asset_refs": [item.get("release_asset_candidate_id") for item in normalized_record.get("release_asset_candidate_preview", [])],
        "confidence_or_uncertainty": "candidate_from_fixture_no_release_truth",
        "supporting_fields": supporting,
        "missing_fields": missing,
        "limitations": ["Release identity candidate does not prove release authenticity, availability, compatibility, or installability."],
        "truth_boundary": {
            "release_identity_candidate_is_accepted_release_truth": False,
            "release_identity_candidate_is_truth": False,
            "release_asset_metadata_grants_download_permission": False,
            "release_notes_prove_installability": False,
            "signature_metadata_proves_authenticity": False,
        },
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(candidate)
    return candidate


def build_h4_source_to_binary_relation_candidates(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    source_id = str(normalized_record.get("source_id"))
    relation = _mapping(normalized_record.get("source_to_binary_relation_candidate"), "source_to_binary_relation_candidate", default={})
    relation_kind = str(relation.get("relation_kind") or "not_evaluable")
    candidate = {
        "schema_version": "h4_source_to_binary_relation_candidate.v0",
        "relation_candidate_id": f"h4.source_to_binary.{source_id}.{_slug(normalized_record.get('source_native_id'))}.v0",
        "source_id": source_id,
        "source_identity_candidate_ref": normalized_record.get("source_identity_candidate", {}).get("source_identity_candidate_id"),
        "release_identity_candidate_ref": normalized_record.get("release_identity_candidate", {}).get("release_identity_candidate_id"),
        "source_commit_ref": relation.get("source_commit_ref", normalized_record.get("git_commit_id_candidate", "unknown")),
        "source_tag_ref": relation.get("source_tag_ref", normalized_record.get("git_tag_candidate", "unknown")),
        "source_archive_ref": relation.get("source_archive_ref", normalized_record.get("source_archive_locator_candidate", "unknown")),
        "binary_asset_ref": relation.get("binary_asset_ref", "unknown"),
        "package_asset_ref": relation.get("package_asset_ref", "unknown"),
        "checksum_ref": relation.get("checksum_ref", "unknown"),
        "signature_ref": relation.get("signature_ref", "unknown"),
        "sbom_ref": relation.get("sbom_ref", "unknown"),
        "relation_kind": relation_kind,
        "relation_confidence_or_uncertainty": relation.get("relation_confidence_or_uncertainty", "candidate_from_fixture_no_provenance"),
        "missing_evidence": list(relation.get("missing_evidence") or ["No build verification, signature verification, SBOM verification, package download, or artifact execution occurred."]),
        "review_required": True,
        "limitations": ["Relation candidate is not accepted provenance and does not prove source-to-binary linkage."],
        "truth_boundary": {
            "relation_candidate_is_accepted_provenance": False,
            "source_to_binary_relation_candidate_is_provenance_truth": False,
            "tag_release_match_proves_build_relation": False,
            "asset_presence_proves_source_relationship": False,
            "sbom_signature_metadata_proves_trust": False,
            "verified_build_reproducibility_claimed": False,
        },
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(candidate)
    return [candidate]


def build_h4_release_asset_candidates(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    record = _mapping(inputs.get("normalized_record"), "normalized_record")
    source_id = str(record.get("source_id"))
    assets = _list_of_mappings(inputs.get("release_assets"))
    candidates: list[dict[str, Any]] = []
    for index, asset in enumerate(assets):
        candidate = {
            "schema_version": "h4_release_asset_candidate.v0",
            "release_asset_candidate_id": f"h4.release_asset.{source_id}.{_slug(asset.get('asset_name', index))}.v0",
            "source_id": source_id,
            "release_identity_candidate_ref": record.get("release_identity_candidate", {}).get("release_identity_candidate_id"),
            "asset_name": asset.get("asset_name", "unknown"),
            "asset_kind": asset.get("asset_kind", "metadata_only"),
            "asset_size": asset.get("asset_size", "unknown"),
            "asset_hashes": _mapping(asset.get("asset_hashes"), "asset_hashes", default={}),
            "asset_locator": asset.get("asset_locator", "unknown"),
            "signature_metadata": _mapping(asset.get("signature_metadata"), "signature_metadata", default={"present": False, "verified_current": False}),
            "sbom_metadata": _mapping(asset.get("sbom_metadata"), "sbom_metadata", default={"present": False, "verified_current": False}),
            "download_allowed_current": False,
            "payload_available_current": False,
            "limitations": ["Release asset candidate is metadata-only and grants no download, authenticity, rights, or malware-safety claim."],
            "truth_boundary": {
                "asset_hash_proves_malware_safety": False,
                "release_asset_hash_candidate_is_malware_safety": False,
                "signature_metadata_proves_authenticity": False,
                "sbom_metadata_is_provenance": False,
                "release_asset_metadata_grants_download_permission": False,
            },
            "product_boundary": _product_boundary(),
        }
        _raise_on_boundary_errors(candidate)
        candidates.append(candidate)
    return candidates


def build_h4_source_cache_candidate_preview(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    preview = {
        "schema_version": "h4_code_source_source_cache_candidate.v0",
        "candidate_id": f"h4.source_cache.{normalized_record.get('source_id')}.{_slug(normalized_record.get('source_native_id'))}.v0",
        "source_id": normalized_record.get("source_id"),
        "source_native_id": normalized_record.get("source_native_id"),
        "cache_entry_kind": "code_source_release_metadata_preview",
        "payload_ref": normalized_record.get("normalized_record_id"),
        "accepted_as_source": False,
        "source_cache_write_enabled": False,
        "limitations": ["Preview only; it is not persisted to source cache by H4-BUNDLE-02."],
        "truth_boundary": {"source_cache_preview_is_accepted_source": False, "accepted_source_truth": False},
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(preview)
    return preview


def build_h4_evidence_candidate_preview(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    preview = {
        "schema_version": "h4_code_source_evidence_candidate_preview.v0",
        "evidence_preview_id": f"h4.evidence.{normalized_record.get('source_id')}.{_slug(normalized_record.get('source_native_id'))}.v0",
        "source_id": normalized_record.get("source_id"),
        "evidence_kind": "fixture_normalization_preview",
        "normalized_record_ref": normalized_record.get("normalized_record_id"),
        "accepted_as_evidence": False,
        "evidence_ledger_write_enabled": False,
        "limitations": ["Evidence preview requires review before evidence ledger use."],
        "truth_boundary": {"evidence_preview_is_accepted_evidence": False, "accepted_evidence_truth": False},
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(preview)
    return preview


def build_h4_fixture_replay_result(fixture: Mapping[str, Any], normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = str(normalized_record.get("source_id"))
    native_id = normalized_record.get("source_native_id")
    replay_status = "policy_blocked_fixture" if fixture.get("fixture_status") == "policy_blocked" else "replayed"
    envelope = build_connector_output_envelope(
        {
            "connector_id": f"h4_code_source_release_fixture.{source_id}",
            "source_id": source_id,
            "source_native_id": native_id,
            "output_type": "normalized_source_record",
            "output_status": "candidate_preview",
            "normalized_record": dict(normalized_record),
            "source_cache_candidate": normalized_record.get("source_cache_candidate_preview"),
            "evidence_candidate_preview": normalized_record.get("evidence_candidate_preview"),
            "limitations": list(normalized_record.get("source_limitations") or []),
        },
        policy,
    )
    relation_refs = [item.get("relation_candidate_id") for item in normalized_record.get("source_to_binary_relation_candidate_preview", [])]
    asset_refs = [item.get("release_asset_candidate_id") for item in normalized_record.get("release_asset_candidate_preview", [])]
    result = {
        "schema_version": "h4_code_source_fixture_replay_result.v0",
        "replay_result_id": f"h4.fixture_replay.{source_id}.{_slug(native_id)}.v0",
        "fixture_id": fixture.get("fixture_id"),
        "source_id": source_id,
        "connector_family": normalized_record.get("connector_family"),
        "replay_status": replay_status,
        "normalized_record_ref": f"examples/connectors/h4_code_source_release/normalized/{source_id}_normalized.json",
        "source_identity_candidate_ref": normalized_record.get("source_identity_candidate", {}).get("source_identity_candidate_id"),
        "release_identity_candidate_ref": normalized_record.get("release_identity_candidate", {}).get("release_identity_candidate_id"),
        "source_to_binary_relation_candidate_refs": relation_refs,
        "release_asset_candidate_refs": asset_refs,
        "source_cache_candidate_ref": normalized_record.get("source_cache_candidate_preview", {}).get("candidate_id"),
        "evidence_candidate_preview_ref": normalized_record.get("evidence_candidate_preview", {}).get("evidence_preview_id"),
        "connector_output_envelope": envelope,
        "validation_summary": {
            "status": replay_status,
            "fixture_only": True,
            "normalization_succeeded": True,
            "source_identity_candidate_count": 1 if normalized_record.get("source_identity_candidate") else 0,
            "release_identity_candidate_count": 1 if normalized_record.get("release_identity_candidate") else 0,
            "source_to_binary_relation_candidate_count": len(relation_refs),
            "release_asset_candidate_count": len(asset_refs),
            "no_network_used": True,
            "no_live_source_used": True,
            "no_repository_clone_used": True,
            "no_source_archive_download_used": True,
            "no_release_asset_download_used": True,
            "no_git_command_invoked": True,
            "no_build_tool_invoked": True,
        },
        "warnings": [],
        "limitations": list(normalized_record.get("source_limitations") or []),
        "no_network_used": True,
        "no_live_source_used": True,
        "no_repository_clone_used": True,
        "no_source_archive_download_used": True,
        "no_release_asset_download_used": True,
        "no_git_command_invoked": True,
        "no_build_tool_invoked": True,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Fixture replay proves parsing only; it grants no live access, clone, download, git/build invocation, install, execution, provenance, or truth acceptance."],
    }
    _raise_on_boundary_errors(result)
    return result


def summarize_h4_normalized_record(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": record.get("source_id"),
        "connector_family": record.get("connector_family"),
        "source_host": record.get("source_host"),
        "project_name": record.get("project_name"),
        "repository_name": record.get("repository_name"),
        "release_id": record.get("release_id"),
        "source_identity_candidate_count": 1 if record.get("source_identity_candidate") else 0,
        "release_identity_candidate_count": 1 if record.get("release_identity_candidate") else 0,
        "source_to_binary_relation_candidate_count": len(record.get("source_to_binary_relation_candidate_preview", []) or []),
        "release_asset_candidate_count": len(record.get("release_asset_candidate_preview", []) or []),
        "source_cache_preview_is_accepted_source": False,
        "evidence_preview_is_accepted_evidence": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def detect_h4_truth_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return [
        f"truth boundary violation: {path}=true"
        for path, key, value in _iter_key_values(record)
        if key in FORBIDDEN_TRUTH_TRUE_KEYS and value is True
    ]


def detect_h4_product_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return [
        f"product boundary violation: {path}=true"
        for path, key, value in _iter_key_values(record)
        if key in FORBIDDEN_PRODUCT_TRUE_KEYS and value is True
    ]


def _require_fixture_boundaries(fixture: Mapping[str, Any]) -> None:
    for key in ("live_call_used", "network_used", "external_api_used", "repository_payload_included", "source_archive_payload_included", "release_asset_payload_included", "git_command_invoked", "build_tool_invoked"):
        if fixture.get(key) is not False:
            raise ValueError(f"{key} must be false")
    _raise_on_boundary_errors(fixture)


def _truth_boundary() -> dict[str, bool]:
    return {'normalized_record_is_public_truth': False, 'source_identity_candidate_is_truth': False, 'source_identity_candidate_is_accepted_identity': False, 'release_identity_candidate_is_truth': False, 'release_identity_candidate_is_accepted_release_truth': False, 'source_to_binary_relation_candidate_is_provenance_truth': False, 'relation_candidate_is_accepted_provenance': False, 'git_object_candidate_is_accepted_provenance': False, 'git_object_candidate_is_provenance_truth': False, 'swhid_candidate_is_accepted_object_truth': False, 'swhid_candidate_is_object_truth': False, 'repository_url_proves_official_status': False, 'release_asset_metadata_grants_download_permission': False, 'release_notes_prove_installability': False, 'tag_release_match_proves_build_relation': False, 'asset_presence_proves_source_relationship': False, 'sbom_signature_metadata_proves_trust': False, 'asset_hash_proves_malware_safety': False, 'signature_metadata_proves_authenticity': False, 'sbom_metadata_is_provenance': False, 'license_metadata_is_rights_clearance': False, 'source_cache_preview_is_accepted_source': False, 'evidence_preview_is_accepted_evidence': False, 'accepted_source_truth': False, 'accepted_evidence_truth': False, 'accepted_candidate_truth': False, 'accepted_source_identity_truth': False, 'accepted_release_identity_truth': False, 'accepted_source_to_binary_relation_truth': False, 'public_index_mutated': False, 'master_index_mutated': False, 'rights_clearance_claimed': False, 'malware_safety_claimed': False, 'verified_installability_claimed': False, 'verified_authenticity_claimed': False, 'verified_build_reproducibility_claimed': False, 'production_readiness_claimed': False}


def _product_boundary() -> dict[str, bool]:
    return {'changed_public_search_behavior': False, 'enabled_hosting': False, 'enabled_live_probes': False, 'enabled_source_sync': False, 'enabled_source_connectors': False, 'enabled_repository_clone': False, 'enabled_downloads': False, 'enabled_installers': False, 'enabled_execution': False, 'enabled_uploads': False, 'enabled_accounts': False, 'enabled_telemetry': False, 'mutated_public_index': False, 'mutated_master_index': False, 'network_calls_made': False, 'api_calls_made': False, 'repository_clone_used': False, 'source_archive_download_used': False, 'release_asset_download_used': False, 'git_command_invoked': False, 'build_tool_invoked': False, 'install_execute_used': False}


def _raise_on_boundary_errors(record: Mapping[str, Any]) -> None:
    errors = detect_h4_truth_boundary_violations(record) + detect_h4_product_boundary_violations(record)
    if errors:
        raise ValueError("; ".join(errors))


def _missing_optional_limitations(payload: Mapping[str, Any]) -> list[str]:
    optional_fields = (
        "origin_url_candidate",
        "repository_url_candidate",
        "git_commit_id_candidate",
        "git_tree_id_candidate",
        "git_tag_candidate",
        "branch_name_candidate",
        "release_id",
        "release_tag",
        "release_version",
        "release_timestamp",
        "release_assets",
        "swhid_candidate",
        "archived_origin_candidate",
        "license_metadata",
        "source_to_binary_relation",
    )
    return [f"optional field absent or unknown: {field}" for field in optional_fields if payload.get(field) in (None, "", [], {})]


def _mapping(value: Any, label: str, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if value in (None, ""):
        if default is not None:
            return dict(default)
        return {}
    if isinstance(value, Mapping):
        return dict(value)
    raise ValueError(f"{label} must be a JSON object")


def _list_of_mappings(value: Any) -> list[dict[str, Any]]:
    if value in (None, ""):
        return []
    if not isinstance(value, list):
        raise ValueError("expected a JSON array")
    result: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, Mapping):
            raise ValueError("expected JSON objects in array")
        result.append(dict(item))
    return result


def _strings(value: Any) -> list[str]:
    if value in (None, ""):
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item not in (None, "")]
    return [str(value)]


def _text(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value)


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value)
        if text not in seen:
            seen.add(text)
            result.append(text)
    return result


def _slug(value: Any) -> str:
    text = "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value)).strip("_")
    return text[:80] or _hash_id(value)


def _hash_id(value: Any) -> str:
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:12]


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

"""Common fixture-only H2 package-registry normalization helpers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
from typing import Any

from runtime.connectors.core.output_envelope import build_connector_output_envelope


H2_SOURCE_CONFIGS: dict[str, dict[str, Any]] = {
    "maven_central": {"connector_family": "package_registry", "ecosystem": "maven"},
    "nuget": {"connector_family": "package_registry", "ecosystem": "nuget"},
    "crates_io": {"connector_family": "package_registry", "ecosystem": "cargo"},
    "rubygems": {"connector_family": "package_registry", "ecosystem": "gem"},
    "cpan": {"connector_family": "package_registry", "ecosystem": "cpan"},
    "cran": {"connector_family": "package_registry", "ecosystem": "cran"},
    "conda_forge": {"connector_family": "package_registry", "ecosystem": "conda"},
    "oci_registry_metadata": {"connector_family": "package_registry", "ecosystem": "oci"},
}
H2_SOURCE_IDS = tuple(H2_SOURCE_CONFIGS)

FORBIDDEN_TRUTH_TRUE_KEYS = {
    "accepted_candidate_truth",
    "accepted_evidence",
    "accepted_evidence_truth",
    "accepted_public_record",
    "accepted_public_truth",
    "accepted_source_truth",
    "dependency_candidate_proves_correctness",
    "dependency_candidate_is_correctness_proof",
    "dependency_correctness_claimed",
    "download_allowed_current",
    "evidence_preview_is_accepted_evidence",
    "file_hash_candidate_is_malware_safety",
    "fixture_replay_can_claim_malware_safety",
    "fixture_replay_can_claim_rights_clearance",
    "fixture_replay_can_claim_verified_installability",
    "fixture_replay_can_mutate_master_index",
    "fixture_replay_can_mutate_public_index",
    "fixture_replay_result_is_source_truth",
    "identity_candidate_is_accepted_identity",
    "license_field_proves_rights_clearance",
    "license_metadata_is_rights_clearance",
    "malware_safety_claimed",
    "master_index_mutated",
    "mutated_master_index",
    "mutated_public_index",
    "normalized_record_is_public_truth",
    "package_hash_proves_malware_safety",
    "package_identity_candidate_is_truth",
    "package_metadata_is_identity_truth",
    "package_metadata_is_installability_verification",
    "package_metadata_proves_installability",
    "payload_available_current",
    "purl_candidate_is_accepted_identity",
    "purl_candidate_is_truth",
    "public_index_mutated",
    "registry_metadata_is_installability_verification",
    "rights_clearance_claimed",
    "source_cache_preview_is_accepted_source",
    "verified_installability_claimed",
}

FORBIDDEN_PRODUCT_TRUE_KEYS = {
    "api_calls_made",
    "changed_public_search_behavior",
    "connector_runtime_enabled",
    "downloads_made",
    "enabled_accounts",
    "enabled_downloads",
    "enabled_execution",
    "enabled_hosting",
    "enabled_installers",
    "enabled_live_probes",
    "enabled_source_connectors",
    "enabled_source_sync",
    "enabled_telemetry",
    "enabled_uploads",
    "external_api_used",
    "live_access_enabled",
    "live_call_used",
    "live_connector_runtime_enabled",
    "mutated_master_index",
    "mutated_public_index",
    "network_calls_made",
    "network_used",
    "package_download_enabled",
    "package_manager_invoked",
    "package_manager_invocation_enabled",
    "package_payload_included",
    "public_index_mutated",
    "scraping_made",
    "source_sync_enabled",
}


def normalize_h2_package_fixture(raw_fixture: Mapping[str, Any], source_id: str, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Normalize one committed H2 fixture into candidate-only package metadata."""

    if source_id not in H2_SOURCE_CONFIGS:
        raise ValueError(f"unknown H2 source_id: {source_id}")
    if raw_fixture.get("source_id") != source_id:
        raise ValueError(f"fixture source_id does not match requested source_id: {source_id}")
    boundary_errors = detect_h2_package_truth_boundary_violations(raw_fixture) + detect_h2_package_product_boundary_violations(raw_fixture)
    if boundary_errors:
        raise ValueError("; ".join(boundary_errors))
    for key in ("live_call_used", "network_used", "external_api_used", "package_payload_included", "package_manager_invoked"):
        if raw_fixture.get(key) is not False:
            raise ValueError(f"fixture {key} must be false")

    payload = _mapping(raw_fixture.get("fixture_payload"), "fixture_payload")
    config = H2_SOURCE_CONFIGS[source_id]
    ecosystem = _text(payload.get("ecosystem")) or str(config["ecosystem"])
    package_name = _text(payload.get("package_name")) or _hash_id(raw_fixture.get("fixture_id") or source_id)
    namespace_or_scope = _text(payload.get("namespace_or_scope"))
    version = _text(payload.get("version"))
    release_id = _text(payload.get("release_id"))
    native_id = _text(payload.get("source_native_id")) or release_id or _hash_id(raw_fixture.get("fixture_id") or source_id)
    limitations = _strings(raw_fixture.get("limitations")) + _strings(payload.get("limitations"))
    limitations.extend(_missing_optional_limitations(payload))
    if raw_fixture.get("fixture_kind") == "policy_blocked" or raw_fixture.get("fixture_status") == "policy_blocked":
        limitations.append("policy-blocked fixture; no live operation is approved")

    dependencies = _list_of_mappings(payload.get("dependencies"))
    files = _list_of_mappings(payload.get("distribution_files"))
    base_record: dict[str, Any] = {
        "schema_version": "h2_package_normalized_record.v0",
        "normalized_record_id": f"h2.normalized.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "connector_family": config["connector_family"],
        "ecosystem": ecosystem,
        "package_name": package_name,
        "namespace_or_scope": namespace_or_scope,
        "version": version or "unknown",
        "release_id": release_id or "unknown",
        "source_native_id": native_id,
        "source_locator": _text(payload.get("source_locator")) or f"fixture:h2:{source_id}:{_slug(native_id)}",
        "title": _text(payload.get("title")) or f"{package_name} {version or 'unknown'}",
        "description_summary": _text(payload.get("description_summary")) or "unknown",
        "project_urls": _strings(payload.get("project_urls")),
        "repository_urls": _strings(payload.get("repository_urls")),
        "license_metadata": _mapping(payload.get("license_metadata"), "license_metadata", default={}),
        "maintainer_or_owner_metadata": _list_of_mappings(payload.get("maintainer_or_owner_metadata")),
        "dependency_summary": {"dependency_count": len(dependencies), "dependencies": dependencies},
        "distribution_file_summary": {"file_count": len(files), "files": files},
        "hash_metadata": _mapping(payload.get("hash_metadata"), "hash_metadata", default={}),
        "advisory_or_vulnerability_refs": _list_of_mappings(payload.get("advisory_or_vulnerability_refs")),
        "platform_or_environment_markers": _strings(payload.get("platform_or_environment_markers")),
        "purl_candidate": _text(payload.get("purl_candidate")) or _purl_candidate(ecosystem, package_name, namespace_or_scope, version),
        "source_metadata": _mapping(payload.get("source_metadata"), "source_metadata", default={}),
        "source_limitations": limitations or ["fixture-only normalization", "missing optional fields are represented as unknown"],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": [
            "Normalized from a committed H2 public-safe fixture.",
            "Fixture runtime proves parsing only and grants no live access, download, install, or execution permission.",
        ],
    }
    identity = build_h2_package_identity_candidate(base_record, policy)
    dependency_candidates = build_h2_dependency_candidates(base_record, policy)
    file_candidates = build_h2_package_file_candidates(base_record, policy)
    record = dict(base_record)
    record["package_identity_candidate"] = identity
    record["dependency_candidate_preview"] = dependency_candidates
    record["file_candidate_preview"] = file_candidates
    record["source_cache_candidate_preview"] = build_h2_source_cache_candidate_preview(record, policy)
    record["evidence_candidate_preview"] = build_h2_evidence_candidate_preview(record, policy)
    _raise_on_boundary_errors(record)
    return record


def build_h2_package_identity_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = str(normalized_record.get("source_id") or "unknown_source")
    native_id = str(normalized_record.get("source_native_id") or "unknown")
    missing = [field for field in ("ecosystem", "package_name", "version") if normalized_record.get(field) in (None, "", "unknown")]
    candidate = {
        "schema_version": "h2_package_identity_candidate.v0",
        "identity_candidate_id": f"h2.identity_candidate.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "ecosystem": normalized_record.get("ecosystem"),
        "package_name": normalized_record.get("package_name"),
        "namespace_or_scope": normalized_record.get("namespace_or_scope"),
        "version": normalized_record.get("version"),
        "purl_candidate": normalized_record.get("purl_candidate"),
        "source_native_id": native_id,
        "confidence_or_uncertainty": "candidate_from_committed_fixture_with_review_required",
        "supporting_fields": ["ecosystem", "package_name", "namespace_or_scope", "version", "source_native_id", "purl_candidate"],
        "missing_fields": missing,
        "limitations": [
            "Package identity candidate is not accepted identity truth.",
            "PURL candidate is not accepted identity truth.",
            "Registry metadata does not prove installability or endorsement.",
        ],
        "truth_boundary": {
            "identity_candidate_is_accepted_identity": False,
            "purl_candidate_is_accepted_identity": False,
            "package_identity_candidate_is_truth": False,
            "purl_candidate_is_truth": False,
            "package_metadata_is_identity_truth": False,
            "registry_metadata_is_installability_verification": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
        },
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(candidate)
    return candidate


def build_h2_dependency_candidates(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    source_id = str(normalized_record.get("source_id") or "unknown_source")
    identity_ref = f"h2.identity_candidate.{source_id}.{_slug(normalized_record.get('source_native_id') or 'unknown')}.v0"
    deps = _mapping(normalized_record.get("dependency_summary"), "dependency_summary", default={}).get("dependencies", [])
    candidates: list[dict[str, Any]] = []
    for index, dep in enumerate(_list_of_mappings(deps)):
        name = _text(dep.get("dependency_name")) or _text(dep.get("name")) or "unknown"
        candidate = {
            "schema_version": "h2_package_dependency_candidate.v0",
            "dependency_candidate_id": f"h2.dependency_candidate.{source_id}.{_slug(name)}.{index}.v0",
            "source_id": source_id,
            "package_identity_candidate_ref": identity_ref,
            "dependency_name": name,
            "dependency_version_range": _text(dep.get("dependency_version_range")) or _text(dep.get("version_range")) or "unknown",
            "dependency_group_or_scope": _text(dep.get("dependency_group_or_scope")) or _text(dep.get("group_or_scope")),
            "dependency_kind": _text(dep.get("dependency_kind")) or "unknown",
            "optional": bool(dep.get("optional", False)),
            "source_metadata_ref": normalized_record.get("source_native_id"),
            "limitations": ["Dependency candidate is a source observation and does not prove dependency correctness."],
            "truth_boundary": {
                "dependency_candidate_proves_correctness": False,
                "dependency_candidate_is_correctness_proof": False,
                "dependency_correctness_claimed": False,
                "accepted_candidate_truth": False,
                "public_index_mutated": False,
                "master_index_mutated": False,
            },
            "product_boundary": _product_boundary(),
        }
        _raise_on_boundary_errors(candidate)
        candidates.append(candidate)
    return candidates


def build_h2_package_file_candidates(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    source_id = str(normalized_record.get("source_id") or "unknown_source")
    identity_ref = f"h2.identity_candidate.{source_id}.{_slug(normalized_record.get('source_native_id') or 'unknown')}.v0"
    files = _mapping(normalized_record.get("distribution_file_summary"), "distribution_file_summary", default={}).get("files", [])
    candidates: list[dict[str, Any]] = []
    for index, file_item in enumerate(_list_of_mappings(files)):
        file_name = _text(file_item.get("file_name")) or _text(file_item.get("name")) or "unknown"
        candidate = {
            "schema_version": "h2_package_file_candidate.v0",
            "file_candidate_id": f"h2.file_candidate.{source_id}.{_slug(file_name)}.{index}.v0",
            "source_id": source_id,
            "package_identity_candidate_ref": identity_ref,
            "file_name": file_name,
            "file_kind": _text(file_item.get("file_kind")) or "unknown",
            "file_size": file_item.get("file_size"),
            "file_hashes": _mapping(file_item.get("file_hashes"), "file_hashes", default={}),
            "source_locator": _text(file_item.get("source_locator")) or normalized_record.get("source_locator"),
            "download_allowed_current": False,
            "payload_available_current": False,
            "limitations": [
                "File metadata candidate is not package download permission.",
                "Hash metadata candidate is not malware safety.",
            ],
            "truth_boundary": {
                "file_hash_candidate_is_malware_safety": False,
                "download_allowed_current": False,
                "payload_available_current": False,
                "malware_safety_claimed": False,
                "verified_installability_claimed": False,
                "public_index_mutated": False,
                "master_index_mutated": False,
            },
            "product_boundary": _product_boundary(),
        }
        _raise_on_boundary_errors(candidate)
        candidates.append(candidate)
    return candidates


def build_h2_source_cache_candidate_preview(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = str(normalized_record.get("source_id") or "unknown_source")
    native_id = str(normalized_record.get("source_native_id") or "unknown")
    preview = {
        "schema_version": "h2_package_source_cache_candidate_preview.v0",
        "candidate_id": f"h2.source_cache_candidate.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "connector_family": normalized_record.get("connector_family"),
        "source_native_id": native_id,
        "source_locator": normalized_record.get("source_locator"),
        "source_metadata_summary": {
            "ecosystem": normalized_record.get("ecosystem"),
            "package_name": normalized_record.get("package_name"),
            "namespace_or_scope": normalized_record.get("namespace_or_scope"),
            "version": normalized_record.get("version"),
            "release_id": normalized_record.get("release_id"),
            "purl_candidate": normalized_record.get("purl_candidate"),
        },
        "source_limitations": list(normalized_record.get("source_limitations") or []),
        "mapping_status": "preview_only_fixture",
        "source_cache_write_enabled": False,
        "source_cache_runtime_mutated": False,
        "accepted_source_truth": False,
        "truth_boundary": {
            "source_cache_preview_is_accepted_source": False,
            "normalized_record_is_public_truth": False,
            "package_identity_candidate_is_truth": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
        },
        "product_boundary": _product_boundary(),
        "notes": ["Source-cache preview only; no source-cache runtime write occurred."],
    }
    _raise_on_boundary_errors(preview)
    return preview


def build_h2_evidence_candidate_preview(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = str(normalized_record.get("source_id") or "unknown_source")
    native_id = str(normalized_record.get("source_native_id") or "unknown")
    candidates = [
        _claim("package_name_candidate", normalized_record.get("package_name"), "Package name is a source observation, not accepted identity truth."),
        _claim("version_candidate", normalized_record.get("version"), "Version is a source observation, not accepted release truth."),
        _claim("purl_candidate", normalized_record.get("purl_candidate"), "PURL is a candidate mapping, not accepted identity truth."),
        _claim("dependency_count_candidate", normalized_record.get("dependency_summary", {}).get("dependency_count"), "Dependency metadata does not prove dependency correctness."),
        _claim("file_metadata_count_candidate", normalized_record.get("distribution_file_summary", {}).get("file_count"), "File metadata does not grant download permission."),
    ]
    preview = {
        "schema_version": "h2_package_evidence_candidate_preview.v0",
        "evidence_preview_id": f"h2.evidence_candidate_preview.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "connector_family": normalized_record.get("connector_family"),
        "source_native_id": native_id,
        "source_locator": normalized_record.get("source_locator"),
        "candidate_count": len(candidates),
        "candidates": candidates,
        "evidence_ledger_write_enabled": False,
        "evidence_ledger_runtime_mutated": False,
        "accepted_evidence": False,
        "truth_boundary": {
            "evidence_preview_is_accepted_evidence": False,
            "normalized_record_is_public_truth": False,
            "package_identity_candidate_is_truth": False,
            "dependency_candidate_is_correctness_proof": False,
            "file_hash_candidate_is_malware_safety": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "rights_clearance_claimed": False,
            "malware_safety_claimed": False,
            "verified_installability_claimed": False,
        },
        "product_boundary": _product_boundary(),
        "notes": ["Evidence preview only; no evidence ledger runtime write occurred."],
    }
    _raise_on_boundary_errors(preview)
    return preview


def build_h2_fixture_replay_result(fixture: Mapping[str, Any], normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = str(fixture.get("source_id") or normalized_record.get("source_id"))
    native_id = str(normalized_record.get("source_native_id") or fixture.get("fixture_id") or "unknown")
    replay_status = "policy_blocked_fixture" if fixture.get("fixture_kind") == "policy_blocked" else "pass"
    envelope = build_connector_output_envelope(
        {
            "output_envelope_id": f"h2.output_envelope.{source_id}.{_slug(native_id)}.v0",
            "connector_id": f"{source_id}_package_fixture_normalizer",
            "source_id": source_id,
            "source_native_id": native_id,
            "output_type": "normalized_source_record",
            "normalized_record": dict(normalized_record),
            "source_cache_candidate": normalized_record.get("source_cache_candidate_preview"),
            "evidence_candidate_preview": normalized_record.get("evidence_candidate_preview"),
            "limitations": list(normalized_record.get("source_limitations") or []),
        },
        policy,
    )
    identity = normalized_record.get("package_identity_candidate", {})
    dependency_refs = [item.get("dependency_candidate_id") for item in normalized_record.get("dependency_candidate_preview", [])]
    file_refs = [item.get("file_candidate_id") for item in normalized_record.get("file_candidate_preview", [])]
    result = {
        "schema_version": "h2_package_fixture_replay_result.v0",
        "replay_result_id": f"h2.fixture_replay.{source_id}.{_slug(native_id)}.v0",
        "fixture_id": fixture.get("fixture_id"),
        "source_id": source_id,
        "connector_family": normalized_record.get("connector_family"),
        "replay_status": replay_status,
        "normalized_record_ref": f"examples/connectors/h2_package_registries/normalized/{source_id}_normalized.json",
        "package_identity_candidate_ref": identity.get("identity_candidate_id"),
        "dependency_candidate_refs": dependency_refs,
        "file_candidate_refs": file_refs,
        "source_cache_candidate_ref": normalized_record.get("source_cache_candidate_preview", {}).get("candidate_id"),
        "evidence_candidate_preview_ref": normalized_record.get("evidence_candidate_preview", {}).get("evidence_preview_id"),
        "connector_output_envelope": envelope,
        "validation_summary": {
            "status": replay_status,
            "fixture_only": True,
            "normalization_succeeded": True,
            "identity_candidate_count": 1 if identity else 0,
            "dependency_candidate_count": len(dependency_refs),
            "file_candidate_count": len(file_refs),
            "no_network_used": True,
            "no_live_source_used": True,
            "no_package_download_used": True,
            "no_package_manager_invoked": True,
            "source_cache_write_enabled": False,
            "evidence_ledger_write_enabled": False,
        },
        "warnings": [],
        "limitations": list(normalized_record.get("source_limitations") or []),
        "no_network_used": True,
        "no_live_source_used": True,
        "no_package_download_used": True,
        "no_package_manager_invoked": True,
        "truth_boundary": {
            "fixture_replay_result_is_source_truth": False,
            "normalized_record_is_public_truth": False,
            "package_identity_candidate_is_truth": False,
            "dependency_candidate_is_correctness_proof": False,
            "file_hash_candidate_is_malware_safety": False,
            "source_cache_preview_is_accepted_source": False,
            "evidence_preview_is_accepted_evidence": False,
            "fixture_replay_can_mutate_public_index": False,
            "fixture_replay_can_mutate_master_index": False,
            "fixture_replay_can_claim_rights_clearance": False,
            "fixture_replay_can_claim_malware_safety": False,
            "fixture_replay_can_claim_verified_installability": False,
        },
        "product_boundary": _product_boundary(),
        "notes": ["Fixture replay proves parsing only; it grants no source access, download, install, or execution permission."],
    }
    _raise_on_boundary_errors(result)
    return result


def summarize_h2_normalized_record(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": record.get("source_id"),
        "connector_family": record.get("connector_family"),
        "ecosystem": record.get("ecosystem"),
        "package_name": record.get("package_name"),
        "namespace_or_scope": record.get("namespace_or_scope"),
        "version": record.get("version"),
        "purl_candidate": record.get("purl_candidate"),
        "dependency_candidate_count": len(record.get("dependency_candidate_preview", []) or []),
        "file_candidate_count": len(record.get("file_candidate_preview", []) or []),
        "source_cache_preview_is_accepted_source": False,
        "evidence_preview_is_accepted_evidence": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def detect_h2_package_truth_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return [
        f"truth boundary violation: {path}=true"
        for path, key, value in _iter_key_values(record)
        if key in FORBIDDEN_TRUTH_TRUE_KEYS and value is True
    ]


def detect_h2_package_product_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return [
        f"product boundary violation: {path}=true"
        for path, key, value in _iter_key_values(record)
        if key in FORBIDDEN_PRODUCT_TRUE_KEYS and value is True
    ]


def _claim(claim_type: str, value: Any, limitation: str) -> dict[str, Any]:
    return {
        "claim_type": claim_type,
        "claim_value": value if value not in (None, "") else "unknown",
        "claim_status": "candidate_preview",
        "accepted_as_evidence": False,
        "accepted_as_public_truth": False,
        "limitations": [limitation, "Requires human review before downstream use."],
    }


def _truth_boundary() -> dict[str, bool]:
    return {
        "normalized_record_is_public_truth": False,
        "package_identity_candidate_is_truth": False,
        "purl_candidate_is_truth": False,
        "dependency_candidate_is_correctness_proof": False,
        "file_hash_candidate_is_malware_safety": False,
        "license_metadata_is_rights_clearance": False,
        "registry_metadata_is_installability_verification": False,
        "source_cache_preview_is_accepted_source": False,
        "evidence_preview_is_accepted_evidence": False,
        "accepted_source_truth": False,
        "accepted_evidence_truth": False,
        "accepted_candidate_truth": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
        "dependency_correctness_claimed": False,
    }


def _product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_hosting": False,
        "enabled_live_probes": False,
        "enabled_source_sync": False,
        "enabled_source_connectors": False,
        "enabled_downloads": False,
        "enabled_installers": False,
        "enabled_execution": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
        "network_calls_made": False,
        "api_calls_made": False,
        "downloads_made": False,
        "package_manager_invoked": False,
        "scraping_made": False,
    }


def _raise_on_boundary_errors(record: Mapping[str, Any]) -> None:
    errors = detect_h2_package_truth_boundary_violations(record) + detect_h2_package_product_boundary_violations(record)
    if errors:
        raise ValueError("; ".join(errors))


def _missing_optional_limitations(payload: Mapping[str, Any]) -> list[str]:
    optional_fields = (
        "version",
        "release_id",
        "description_summary",
        "project_urls",
        "repository_urls",
        "license_metadata",
        "dependencies",
        "distribution_files",
        "hash_metadata",
        "platform_or_environment_markers",
    )
    return [f"optional field absent or unknown: {field}" for field in optional_fields if payload.get(field) in (None, "", [], {})]


def _mapping(value: Any, label: str, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if value in (None, "") and default is not None:
        return dict(default)
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


def _purl_candidate(ecosystem: str, package_name: str, namespace: str | None, version: str | None) -> str:
    base = f"pkg:{ecosystem}/{package_name}" if not namespace else f"pkg:{ecosystem}/{namespace}/{package_name}"
    return f"{base}@{version}" if version else base


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


"""Common fixture-only H3 OS package archive normalization helpers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
from typing import Any

from runtime.connectors.core.output_envelope import build_connector_output_envelope


H3_SOURCE_CONFIGS: dict[str, dict[str, Any]] = {
    "debian_snapshot": {
        "connector_family": "directory_listing",
        "ecosystem": "debian",
        "distribution": "Debian",
        "distribution_release": "bookworm-fixture",
        "repository_component": "main",
        "repository_channel": "main",
        "architecture": "amd64",
        "operating_system_family": "Debian",
        "package_manager_context": "apt",
    },
    "ubuntu_old_releases": {
        "connector_family": "directory_listing",
        "ecosystem": "ubuntu",
        "distribution": "Ubuntu",
        "distribution_release": "jammy-fixture",
        "repository_component": "universe",
        "repository_channel": "universe",
        "architecture": "amd64",
        "operating_system_family": "Ubuntu",
        "package_manager_context": "apt",
    },
    "arch_linux_archive": {
        "connector_family": "directory_listing",
        "ecosystem": "arch",
        "distribution": "Arch Linux",
        "distribution_release": "rolling-fixture",
        "repository_component": "core",
        "repository_channel": "core",
        "architecture": "x86_64",
        "operating_system_family": "Arch Linux",
        "package_manager_context": "pacman",
    },
    "fedora_rpm_metadata": {
        "connector_family": "os_package_archive",
        "ecosystem": "rpm",
        "distribution": "Fedora",
        "distribution_release": "fedora-fixture",
        "repository_component": "updates",
        "repository_channel": "updates",
        "architecture": "x86_64",
        "operating_system_family": "Fedora",
        "package_manager_context": "dnf/rpm",
    },
    "freebsd_packages_ports": {
        "connector_family": "directory_listing",
        "ecosystem": "freebsd",
        "distribution": "FreeBSD",
        "distribution_release": "freebsd-fixture",
        "repository_component": "quarterly",
        "repository_channel": "quarterly",
        "architecture": "amd64",
        "operating_system_family": "FreeBSD",
        "package_manager_context": "pkg/ports",
    },
    "pkgsrc": {
        "connector_family": "os_package_archive",
        "ecosystem": "pkgsrc",
        "distribution": "pkgsrc",
        "distribution_release": "pkgsrc-current-fixture",
        "repository_component": "pkgsrc",
        "repository_channel": "pkgsrc",
        "architecture": "x86_64",
        "operating_system_family": "pkgsrc",
        "package_manager_context": "pkgsrc/pkgin",
    },
    "homebrew": {
        "connector_family": "package_registry",
        "ecosystem": "homebrew",
        "distribution": "Homebrew",
        "distribution_release": "macos-fixture",
        "repository_component": "core",
        "repository_channel": "core",
        "architecture": "arm64",
        "operating_system_family": "macOS",
        "package_manager_context": "brew",
    },
    "macports": {
        "connector_family": "package_registry",
        "ecosystem": "macports",
        "distribution": "MacPorts",
        "distribution_release": "macos-fixture",
        "repository_component": "ports",
        "repository_channel": "ports",
        "architecture": "x86_64",
        "operating_system_family": "macOS",
        "package_manager_context": "port",
    },
    "nixpkgs": {
        "connector_family": "package_registry",
        "ecosystem": "nix",
        "distribution": "NixOS",
        "distribution_release": "nixos-fixture",
        "repository_component": "nixpkgs",
        "repository_channel": "nixpkgs",
        "architecture": "x86_64-linux",
        "operating_system_family": "NixOS",
        "package_manager_context": "nix",
    },
    "winget": {
        "connector_family": "package_registry",
        "ecosystem": "winget",
        "distribution": "Windows",
        "distribution_release": "windows-fixture",
        "repository_component": "community",
        "repository_channel": "community",
        "architecture": "x64",
        "operating_system_family": "Windows",
        "package_manager_context": "winget",
    },
    "chocolatey": {
        "connector_family": "package_registry",
        "ecosystem": "chocolatey",
        "distribution": "Windows",
        "distribution_release": "windows-fixture",
        "repository_component": "community",
        "repository_channel": "community",
        "architecture": "x64",
        "operating_system_family": "Windows",
        "package_manager_context": "choco",
    },
    "flathub": {
        "connector_family": "storefront",
        "ecosystem": "flatpak",
        "distribution": "Flathub",
        "distribution_release": "linux-desktop-fixture",
        "repository_component": "stable",
        "repository_channel": "stable",
        "architecture": "x86_64",
        "operating_system_family": "Linux",
        "package_manager_context": "flatpak",
    },
    "snapcraft": {
        "connector_family": "storefront",
        "ecosystem": "snap",
        "distribution": "Snapcraft",
        "distribution_release": "linux-fixture",
        "repository_component": "stable",
        "repository_channel": "stable",
        "architecture": "amd64",
        "operating_system_family": "Linux",
        "package_manager_context": "snap",
    },
}
H3_SOURCE_IDS = tuple(H3_SOURCE_CONFIGS)

FORBIDDEN_TRUTH_TRUE_KEYS = {
    "accepted_candidate_truth",
    "accepted_compatibility_truth",
    "accepted_evidence",
    "accepted_evidence_truth",
    "accepted_os_compatibility_fact",
    "accepted_os_package_identity",
    "accepted_package_identity_truth",
    "accepted_public_record",
    "accepted_public_truth",
    "accepted_source_truth",
    "architecture_match_proves_runtime_compatibility",
    "compatibility_candidate_is_verified_compatibility",
    "compatibility_correctness_claimed",
    "compatibility_metadata_proves_compatibility_correctness",
    "dependency_candidate_is_correctness_proof",
    "dependency_candidate_proves_correctness",
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
    "os_compatibility_candidate_is_truth",
    "os_package_hash_proves_malware_safety",
    "os_package_identity_candidate_is_truth",
    "os_package_metadata_is_identity_truth",
    "os_package_metadata_proves_installability",
    "payload_available_current",
    "public_index_mutated",
    "purl_candidate_is_accepted_identity",
    "purl_candidate_is_truth",
    "repository_metadata_is_installability_verification",
    "repository_presence_proves_installability",
    "repository_presence_proves_installability_on_every_system",
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
    "repository_index_fetch_enabled",
    "repository_index_fetch_used",
    "repository_index_mirror_enabled",
    "scraping_made",
    "source_sync_enabled",
}


def normalize_h3_os_package_fixture(raw_fixture: Mapping[str, Any], source_id: str, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Normalize one committed H3 fixture into candidate-only OS package metadata."""

    if source_id not in H3_SOURCE_CONFIGS:
        raise ValueError(f"unknown H3 source_id: {source_id}")
    if raw_fixture.get("source_id") != source_id:
        raise ValueError(f"fixture source_id does not match requested source_id: {source_id}")
    boundary_errors = detect_h3_truth_boundary_violations(raw_fixture) + detect_h3_product_boundary_violations(raw_fixture)
    if boundary_errors:
        raise ValueError("; ".join(boundary_errors))
    for key in ("live_call_used", "network_used", "external_api_used", "repository_index_payload_included", "package_payload_included", "package_manager_invoked"):
        if raw_fixture.get(key) is not False:
            raise ValueError(f"fixture {key} must be false")

    payload = _mapping(raw_fixture.get("fixture_payload"), "fixture_payload")
    config = H3_SOURCE_CONFIGS[source_id]
    ecosystem = _text(payload.get("ecosystem")) or str(config["ecosystem"])
    distribution = _text(payload.get("distribution")) or str(config["distribution"])
    distribution_release = _text(payload.get("distribution_release")) or "unknown"
    repository_component = _text(payload.get("repository_component")) or "unknown"
    repository_channel = _text(payload.get("repository_channel")) or "unknown"
    package_name = _text(payload.get("package_name")) or _hash_id(raw_fixture.get("fixture_id") or source_id)
    source_package_name = _text(payload.get("source_package_name")) or package_name
    binary_package_name = _text(payload.get("binary_package_name")) or package_name
    architecture = _text(payload.get("architecture")) or "unknown"
    version = _text(payload.get("version")) or "unknown"
    epoch = _text(payload.get("epoch")) or "unknown"
    release_revision = _text(payload.get("release_revision")) or "unknown"
    build_id = _text(payload.get("build_id")) or "unknown"
    native_id = _text(payload.get("source_native_id")) or _hash_id(raw_fixture.get("fixture_id") or source_id)
    limitations = _strings(raw_fixture.get("limitations")) + _strings(payload.get("limitations"))
    limitations.extend(_missing_optional_limitations(payload))
    if raw_fixture.get("fixture_kind") == "policy_blocked" or raw_fixture.get("fixture_status") == "policy_blocked":
        limitations.append("policy-blocked fixture; no live operation is approved")

    relations = _list_of_mappings(payload.get("relations"))
    files = _list_of_mappings(payload.get("files"))
    base_record: dict[str, Any] = {
        "schema_version": "h3_os_package_normalized_record.v0",
        "normalized_record_id": f"h3.normalized.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "connector_family": config["connector_family"],
        "ecosystem": ecosystem,
        "distribution": distribution,
        "distribution_release": distribution_release,
        "repository_component": repository_component,
        "repository_channel": repository_channel,
        "package_name": package_name,
        "source_package_name": source_package_name,
        "binary_package_name": binary_package_name,
        "architecture": architecture,
        "version": version,
        "epoch": epoch,
        "release_revision": release_revision,
        "build_id": build_id,
        "source_native_id": native_id,
        "package_locator": _text(payload.get("package_locator")) or f"fixture:h3:{source_id}:{_slug(native_id)}",
        "title": _text(payload.get("title")) or f"{package_name} {version}",
        "description_summary": _text(payload.get("description_summary")) or "unknown",
        "project_urls": _strings(payload.get("project_urls")),
        "upstream_urls": _strings(payload.get("upstream_urls")),
        "repository_urls": _strings(payload.get("repository_urls")),
        "license_metadata": _mapping(payload.get("license_metadata"), "license_metadata", default={}),
        "maintainer_or_packager_metadata": _list_of_mappings(payload.get("maintainer_or_packager_metadata")),
        "dependency_summary": {
            "dependency_count": len([r for r in relations if r.get("relation_kind") in ("depends", "recommends", "suggests", "build_depends", "runtime_requirement")]),
            "relations": relations,
        },
        "conflict_summary": {
            "conflict_count": len([r for r in relations if r.get("relation_kind") in ("conflicts", "breaks", "replaces")]),
            "relations": [r for r in relations if r.get("relation_kind") in ("conflicts", "breaks", "replaces")],
        },
        "provides_summary": {
            "provides_count": len([r for r in relations if r.get("relation_kind") == "provides"]),
            "relations": [r for r in relations if r.get("relation_kind") == "provides"],
        },
        "file_or_artifact_summary": {"file_count": len(files), "files": files},
        "hash_metadata": _mapping(payload.get("hash_metadata"), "hash_metadata", default={}),
        "changelog_or_news_refs": _strings(payload.get("changelog_or_news_refs")),
        "platform_or_environment_markers": _strings(payload.get("platform_or_environment_markers")),
        "purl_candidate": _text(payload.get("purl_candidate")) or _purl_candidate(ecosystem, package_name, distribution, distribution_release, architecture, version),
        "source_metadata": _mapping(payload.get("source_metadata"), "source_metadata", default={}),
        "source_limitations": limitations or ["fixture-only normalization", "missing optional fields are represented as unknown"],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": [
            "Normalized from a committed H3 public-safe fixture.",
            "Fixture runtime proves parsing only and grants no live access, repository index fetch, download, package-manager invocation, install, or execution permission.",
        ],
    }
    identity = build_h3_os_package_identity_candidate(base_record, policy)
    compatibility = build_h3_os_platform_compatibility_candidate(base_record, policy)
    dependency_candidates = build_h3_dependency_candidates(base_record, policy)
    file_candidates = build_h3_package_file_candidates(base_record, policy)
    record = dict(base_record)
    record["os_package_identity_candidate"] = identity
    record["os_platform_compatibility_candidate"] = compatibility
    record["dependency_candidate_preview"] = dependency_candidates
    record["file_candidate_preview"] = file_candidates
    record["source_cache_candidate_preview"] = build_h3_source_cache_candidate_preview(record, policy)
    record["evidence_candidate_preview"] = build_h3_evidence_candidate_preview(record, policy)
    _raise_on_boundary_errors(record)
    return record


def build_h3_os_package_identity_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = str(normalized_record.get("source_id") or "unknown_source")
    native_id = str(normalized_record.get("source_native_id") or "unknown")
    missing = [field for field in ("ecosystem", "distribution", "package_name", "version", "architecture") if normalized_record.get(field) in (None, "", "unknown")]
    candidate = {
        "schema_version": "h3_os_package_identity_candidate.v0",
        "identity_candidate_id": f"h3.identity_candidate.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "ecosystem": normalized_record.get("ecosystem"),
        "distribution": normalized_record.get("distribution"),
        "distribution_release": normalized_record.get("distribution_release"),
        "repository_component": normalized_record.get("repository_component"),
        "package_name": normalized_record.get("package_name"),
        "source_package_name": normalized_record.get("source_package_name"),
        "binary_package_name": normalized_record.get("binary_package_name"),
        "architecture": normalized_record.get("architecture"),
        "version": normalized_record.get("version"),
        "epoch": normalized_record.get("epoch"),
        "release_revision": normalized_record.get("release_revision"),
        "purl_candidate": normalized_record.get("purl_candidate"),
        "source_native_id": native_id,
        "confidence_or_uncertainty": "candidate_from_committed_fixture_with_review_required",
        "supporting_fields": ["ecosystem", "distribution", "distribution_release", "repository_component", "package_name", "architecture", "version", "source_native_id", "purl_candidate"],
        "missing_fields": missing,
        "limitations": [
            "OS package identity candidate is not accepted identity truth.",
            "PURL candidate is not accepted identity truth.",
            "Repository metadata does not prove installability, compatibility, endorsement, rights, or safety.",
        ],
        "truth_boundary": {
            "identity_candidate_is_accepted_identity": False,
            "purl_candidate_is_accepted_identity": False,
            "os_package_identity_candidate_is_truth": False,
            "purl_candidate_is_truth": False,
            "os_package_metadata_is_identity_truth": False,
            "os_package_metadata_proves_installability": False,
            "repository_metadata_is_installability_verification": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
        },
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(candidate)
    return candidate


def build_h3_os_platform_compatibility_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = str(normalized_record.get("source_id") or "unknown_source")
    native_id = str(normalized_record.get("source_native_id") or "unknown")
    config = H3_SOURCE_CONFIGS.get(source_id, {})
    candidate = {
        "schema_version": "h3_os_platform_compatibility_candidate.v0",
        "compatibility_candidate_id": f"h3.compatibility_candidate.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "package_identity_candidate_ref": f"h3.identity_candidate.{source_id}.{_slug(native_id)}.v0",
        "operating_system_family": config.get("operating_system_family") or normalized_record.get("distribution"),
        "distribution": normalized_record.get("distribution"),
        "distribution_release": normalized_record.get("distribution_release"),
        "architecture": normalized_record.get("architecture"),
        "repository_component": normalized_record.get("repository_component"),
        "repository_channel": normalized_record.get("repository_channel"),
        "package_manager_context": config.get("package_manager_context", "unknown"),
        "dependency_environment_summary": normalized_record.get("dependency_summary"),
        "compatibility_status_candidate": "metadata_candidate_review_required",
        "unsupported_or_removed_candidate": False,
        "limitations": [
            "Compatibility candidate is not verified compatibility.",
            "Repository presence does not prove installability on every system.",
            "Architecture match does not prove runtime compatibility.",
        ],
        "truth_boundary": {
            "compatibility_candidate_is_verified_compatibility": False,
            "os_platform_compatibility_candidate_is_truth": False,
            "os_compatibility_candidate_is_truth": False,
            "repository_presence_proves_installability": False,
            "architecture_match_proves_runtime_compatibility": False,
            "compatibility_correctness_claimed": False,
            "dependency_correctness_claimed": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
        },
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(candidate)
    return candidate


def build_h3_dependency_candidates(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    source_id = str(normalized_record.get("source_id") or "unknown_source")
    identity_ref = f"h3.identity_candidate.{source_id}.{_slug(normalized_record.get('source_native_id') or 'unknown')}.v0"
    relations = _mapping(normalized_record.get("dependency_summary"), "dependency_summary", default={}).get("relations", [])
    candidates: list[dict[str, Any]] = []
    for index, relation in enumerate(_list_of_mappings(relations)):
        name = _text(relation.get("related_package_name")) or _text(relation.get("name")) or "unknown"
        relation_kind = _text(relation.get("relation_kind")) or "not_evaluable"
        candidate = {
            "schema_version": "h3_os_package_dependency_candidate.v0",
            "dependency_candidate_id": f"h3.dependency_candidate.{source_id}.{_slug(relation_kind)}.{_slug(name)}.{index}.v0",
            "source_id": source_id,
            "package_identity_candidate_ref": identity_ref,
            "relation_kind": relation_kind,
            "related_package_name": name,
            "version_range_or_constraint": _text(relation.get("version_range_or_constraint")) or _text(relation.get("version_range")) or "unknown",
            "architecture_or_context": _text(relation.get("architecture_or_context")) or normalized_record.get("architecture"),
            "optional": bool(relation.get("optional", False)),
            "source_metadata_ref": normalized_record.get("source_native_id"),
            "limitations": ["Dependency/conflict/provides candidate is a source observation and does not prove dependency correctness or environment solvability."],
            "truth_boundary": {
                "dependency_candidate_proves_correctness": False,
                "dependency_candidate_is_correctness_proof": False,
                "dependency_correctness_claimed": False,
                "compatibility_correctness_claimed": False,
                "accepted_candidate_truth": False,
                "public_index_mutated": False,
                "master_index_mutated": False,
            },
            "product_boundary": _product_boundary(),
        }
        _raise_on_boundary_errors(candidate)
        candidates.append(candidate)
    return candidates


def build_h3_package_file_candidates(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    source_id = str(normalized_record.get("source_id") or "unknown_source")
    identity_ref = f"h3.identity_candidate.{source_id}.{_slug(normalized_record.get('source_native_id') or 'unknown')}.v0"
    files = _mapping(normalized_record.get("file_or_artifact_summary"), "file_or_artifact_summary", default={}).get("files", [])
    candidates: list[dict[str, Any]] = []
    for index, file_item in enumerate(_list_of_mappings(files)):
        file_name = _text(file_item.get("file_name")) or _text(file_item.get("name")) or "unknown"
        candidate = {
            "schema_version": "h3_os_package_file_candidate.v0",
            "file_candidate_id": f"h3.file_candidate.{source_id}.{_slug(file_name)}.{index}.v0",
            "source_id": source_id,
            "package_identity_candidate_ref": identity_ref,
            "file_name": file_name,
            "file_kind": _text(file_item.get("file_kind")) or "unknown",
            "file_size": file_item.get("file_size"),
            "file_hashes": _mapping(file_item.get("file_hashes"), "file_hashes", default={}),
            "source_locator": _text(file_item.get("source_locator")) or normalized_record.get("package_locator"),
            "repository_locator": _text(file_item.get("repository_locator")) or normalized_record.get("repository_component"),
            "download_allowed_current": False,
            "payload_available_current": False,
            "limitations": [
                "File metadata candidate is not package download permission.",
                "Hash metadata candidate is not malware safety or authenticity proof without review.",
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


def build_h3_source_cache_candidate_preview(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = str(normalized_record.get("source_id") or "unknown_source")
    native_id = str(normalized_record.get("source_native_id") or "unknown")
    preview = {
        "schema_version": "h3_os_package_source_cache_candidate_preview.v0",
        "candidate_id": f"h3.source_cache_candidate.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "connector_family": normalized_record.get("connector_family"),
        "source_native_id": native_id,
        "package_locator": normalized_record.get("package_locator"),
        "source_metadata_summary": {
            "ecosystem": normalized_record.get("ecosystem"),
            "distribution": normalized_record.get("distribution"),
            "distribution_release": normalized_record.get("distribution_release"),
            "package_name": normalized_record.get("package_name"),
            "architecture": normalized_record.get("architecture"),
            "version": normalized_record.get("version"),
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
            "os_package_identity_candidate_is_truth": False,
            "os_compatibility_candidate_is_truth": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
        },
        "product_boundary": _product_boundary(),
        "notes": ["Source-cache preview only; no source-cache runtime write occurred."],
    }
    _raise_on_boundary_errors(preview)
    return preview


def build_h3_evidence_candidate_preview(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = str(normalized_record.get("source_id") or "unknown_source")
    native_id = str(normalized_record.get("source_native_id") or "unknown")
    candidates = [
        _claim("package_name_candidate", normalized_record.get("package_name"), "Package name is a source observation, not accepted identity truth."),
        _claim("version_candidate", normalized_record.get("version"), "Version is a source observation, not accepted release truth."),
        _claim("architecture_candidate", normalized_record.get("architecture"), "Architecture metadata does not prove runtime compatibility."),
        _claim("purl_candidate", normalized_record.get("purl_candidate"), "PURL is a candidate mapping, not accepted identity truth."),
        _claim("dependency_relation_count_candidate", len(normalized_record.get("dependency_candidate_preview", []) or []), "Dependency/conflict/provides metadata does not prove correctness."),
        _claim("file_metadata_count_candidate", len(normalized_record.get("file_candidate_preview", []) or []), "File metadata does not grant download permission."),
    ]
    preview = {
        "schema_version": "h3_os_package_evidence_candidate_preview.v0",
        "evidence_preview_id": f"h3.evidence_candidate_preview.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "connector_family": normalized_record.get("connector_family"),
        "source_native_id": native_id,
        "package_locator": normalized_record.get("package_locator"),
        "candidate_count": len(candidates),
        "candidates": candidates,
        "evidence_ledger_write_enabled": False,
        "evidence_ledger_runtime_mutated": False,
        "accepted_evidence": False,
        "truth_boundary": {
            "evidence_preview_is_accepted_evidence": False,
            "normalized_record_is_public_truth": False,
            "os_package_identity_candidate_is_truth": False,
            "os_compatibility_candidate_is_truth": False,
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


def build_h3_fixture_replay_result(fixture: Mapping[str, Any], normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = str(fixture.get("source_id") or normalized_record.get("source_id"))
    native_id = str(normalized_record.get("source_native_id") or fixture.get("fixture_id") or "unknown")
    replay_status = "policy_blocked_fixture" if fixture.get("fixture_kind") == "policy_blocked" else "pass"
    envelope = build_connector_output_envelope(
        {
            "output_envelope_id": f"h3.output_envelope.{source_id}.{_slug(native_id)}.v0",
            "connector_id": f"{source_id}_os_package_fixture_normalizer",
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
    identity = normalized_record.get("os_package_identity_candidate", {})
    compatibility = normalized_record.get("os_platform_compatibility_candidate", {})
    dependency_refs = [item.get("dependency_candidate_id") for item in normalized_record.get("dependency_candidate_preview", [])]
    file_refs = [item.get("file_candidate_id") for item in normalized_record.get("file_candidate_preview", [])]
    result = {
        "schema_version": "h3_os_package_fixture_replay_result.v0",
        "replay_result_id": f"h3.fixture_replay.{source_id}.{_slug(native_id)}.v0",
        "fixture_id": fixture.get("fixture_id"),
        "source_id": source_id,
        "connector_family": normalized_record.get("connector_family"),
        "replay_status": replay_status,
        "normalized_record_ref": f"examples/connectors/h3_os_package_archives/normalized/{source_id}_normalized.json",
        "os_package_identity_candidate_ref": identity.get("identity_candidate_id"),
        "os_platform_compatibility_candidate_ref": compatibility.get("compatibility_candidate_id"),
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
            "compatibility_candidate_count": 1 if compatibility else 0,
            "dependency_candidate_count": len(dependency_refs),
            "file_candidate_count": len(file_refs),
            "no_network_used": True,
            "no_live_source_used": True,
            "no_repository_index_fetch_used": True,
            "no_package_download_used": True,
            "no_package_manager_invoked": True,
            "source_cache_write_enabled": False,
            "evidence_ledger_write_enabled": False,
        },
        "warnings": [],
        "limitations": list(normalized_record.get("source_limitations") or []),
        "no_network_used": True,
        "no_live_source_used": True,
        "no_repository_index_fetch_used": True,
        "no_package_download_used": True,
        "no_package_manager_invoked": True,
        "truth_boundary": {
            "fixture_replay_result_is_source_truth": False,
            "normalized_record_is_public_truth": False,
            "os_package_identity_candidate_is_truth": False,
            "os_compatibility_candidate_is_truth": False,
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
        "notes": ["Fixture replay proves parsing only; it grants no source access, repository index fetch, download, package-manager invocation, install, or execution permission."],
    }
    _raise_on_boundary_errors(result)
    return result


def summarize_h3_normalized_record(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": record.get("source_id"),
        "connector_family": record.get("connector_family"),
        "ecosystem": record.get("ecosystem"),
        "distribution": record.get("distribution"),
        "package_name": record.get("package_name"),
        "architecture": record.get("architecture"),
        "version": record.get("version"),
        "purl_candidate": record.get("purl_candidate"),
        "dependency_candidate_count": len(record.get("dependency_candidate_preview", []) or []),
        "file_candidate_count": len(record.get("file_candidate_preview", []) or []),
        "source_cache_preview_is_accepted_source": False,
        "evidence_preview_is_accepted_evidence": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def detect_h3_truth_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return [
        f"truth boundary violation: {path}=true"
        for path, key, value in _iter_key_values(record)
        if key in FORBIDDEN_TRUTH_TRUE_KEYS and value is True
    ]


def detect_h3_product_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
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
        "os_package_identity_candidate_is_truth": False,
        "purl_candidate_is_truth": False,
        "os_compatibility_candidate_is_truth": False,
        "compatibility_candidate_is_verified_compatibility": False,
        "dependency_candidate_is_correctness_proof": False,
        "file_hash_candidate_is_malware_safety": False,
        "license_metadata_is_rights_clearance": False,
        "repository_metadata_is_installability_verification": False,
        "source_cache_preview_is_accepted_source": False,
        "evidence_preview_is_accepted_evidence": False,
        "accepted_source_truth": False,
        "accepted_evidence_truth": False,
        "accepted_candidate_truth": False,
        "accepted_os_package_identity": False,
        "accepted_os_compatibility_fact": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
        "dependency_correctness_claimed": False,
        "compatibility_correctness_claimed": False,
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
        "repository_index_fetch_used": False,
        "package_manager_invoked": False,
        "scraping_made": False,
    }


def _raise_on_boundary_errors(record: Mapping[str, Any]) -> None:
    errors = detect_h3_truth_boundary_violations(record) + detect_h3_product_boundary_violations(record)
    if errors:
        raise ValueError("; ".join(errors))


def _missing_optional_limitations(payload: Mapping[str, Any]) -> list[str]:
    optional_fields = (
        "version",
        "distribution_release",
        "repository_component",
        "repository_channel",
        "architecture",
        "description_summary",
        "project_urls",
        "upstream_urls",
        "repository_urls",
        "license_metadata",
        "relations",
        "files",
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


def _purl_candidate(ecosystem: str, package_name: str, distribution: str, release: str, architecture: str, version: str | None) -> str:
    qualifiers = []
    for key, value in (("distro", distribution), ("release", release), ("arch", architecture)):
        if value and value != "unknown":
            qualifiers.append(f"{key}={value}")
    base = f"pkg:{ecosystem}/{package_name}"
    suffix = f"@{version}" if version and version != "unknown" else ""
    query = "?" + "&".join(qualifiers) if qualifiers else ""
    return f"{base}{suffix}{query}"


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

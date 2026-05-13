"""Common fixture-only H1 metadata-wave normalization helpers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
from typing import Any

from runtime.connectors.core.output_envelope import build_connector_output_envelope


H1_SOURCE_CONFIGS: dict[str, dict[str, Any]] = {
    "wayback_cdx_memento": {
        "connector_family": "warc_cdx",
        "artifact_type": "web_archive_capture_metadata",
        "object_family": "web_archive_trace",
        "platform_or_context": "web archive capture context",
    },
    "github_releases": {
        "connector_family": "api_json",
        "artifact_type": "release_metadata",
        "object_family": "software_release",
        "platform_or_context": "code source release host",
    },
    "pypi": {
        "connector_family": "package_registry",
        "artifact_type": "package_metadata",
        "object_family": "python_package",
        "platform_or_context": "python package registry",
    },
    "npm_registry": {
        "connector_family": "package_registry",
        "artifact_type": "package_metadata",
        "object_family": "javascript_package",
        "platform_or_context": "npm package registry",
    },
    "software_heritage": {
        "connector_family": "api_json",
        "artifact_type": "software_preservation_metadata",
        "object_family": "source_snapshot",
        "platform_or_context": "software preservation archive",
    },
    "repology": {
        "connector_family": "api_json",
        "artifact_type": "cross_repository_package_metadata",
        "object_family": "package_project",
        "platform_or_context": "package repository crosswalk",
    },
    "osv": {
        "connector_family": "api_json",
        "artifact_type": "advisory_metadata",
        "object_family": "vulnerability_advisory",
        "platform_or_context": "security advisory metadata",
    },
}
H1_SOURCE_IDS = tuple(H1_SOURCE_CONFIGS)

FORBIDDEN_TRUTH_TRUE_KEYS = {
    "accepted_candidate_truth",
    "accepted_evidence",
    "accepted_evidence_truth",
    "accepted_public_record",
    "accepted_public_truth",
    "accepted_source_truth",
    "coverage_preview_claims_exhaustive_coverage",
    "download_permission_granted",
    "evidence_preview_is_accepted_evidence",
    "fixture_replay_can_claim_malware_safety",
    "fixture_replay_can_claim_rights_clearance",
    "fixture_replay_can_claim_verified_installability",
    "fixture_replay_can_mutate_master_index",
    "fixture_replay_can_mutate_public_index",
    "fixture_replay_result_is_source_truth",
    "local_availability_proven",
    "malware_safety_claimed",
    "master_index_mutated",
    "mutated_master_index",
    "mutated_public_index",
    "normalized_record_is_public_truth",
    "package_metadata_is_installability_verification",
    "package_download_permission",
    "public_index_mutated",
    "release_asset_entry_is_download_permission",
    "release_asset_download_permission",
    "rights_clearance_claimed",
    "security_conclusion_without_review",
    "source_locator_is_rights_clearance",
    "source_archive_download_permission",
    "source_cache_preview_is_accepted_source",
    "title_match_is_verified_identity",
    "verified_installability_claimed",
    "version_field_is_accepted_release_truth",
    "vulnerability_record_is_security_conclusion",
    "file_listing_is_local_availability_proof",
}

FORBIDDEN_PRODUCT_TRUE_KEYS = {
    "api_calls_made",
    "changed_public_search_behavior",
    "connector_runtime_enabled",
    "downloads_made",
    "enabled_accounts",
    "enabled_downloads",
    "enabled_hosting",
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
    "public_index_mutated",
    "scraping_made",
    "source_sync_enabled",
}


def normalize_h1_fixture(raw_fixture: Mapping[str, Any], source_id: str, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Normalize one committed H1 fixture into a preview-only metadata record."""

    if source_id not in H1_SOURCE_CONFIGS:
        raise ValueError(f"unknown H1 source_id: {source_id}")
    if raw_fixture.get("source_id") != source_id:
        raise ValueError(f"fixture source_id does not match requested source_id: {source_id}")
    boundary_errors = detect_h1_truth_boundary_violations(raw_fixture) + detect_h1_product_boundary_violations(raw_fixture)
    if boundary_errors:
        raise ValueError("; ".join(boundary_errors))
    for key in ("live_call_used", "network_used", "external_api_used"):
        if raw_fixture.get(key) is not False:
            raise ValueError(f"fixture {key} must be false")

    payload = _mapping(raw_fixture.get("fixture_payload"), "fixture_payload")
    config = H1_SOURCE_CONFIGS[source_id]
    native_id = _text(payload.get("native_id")) or _hash_id(raw_fixture.get("fixture_id") or source_id)
    fixture_limitations = _strings(raw_fixture.get("limitations"))
    payload_limitations = _strings(payload.get("limitations"))
    limitations = fixture_limitations + payload_limitations
    missing_optional = _missing_optional_limitations(payload)
    limitations.extend(missing_optional)
    if raw_fixture.get("fixture_kind") == "policy_blocked":
        limitations.append("policy-blocked fixture; no live operation is approved")

    base_record = {
        "schema_version": "h1_metadata_normalized_record.v0",
        "normalized_record_id": f"h1.normalized.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "connector_family": config["connector_family"],
        "source_native_id": native_id,
        "source_locator": _text(payload.get("source_locator")) or f"fixture:h1:{source_id}:{_slug(native_id)}",
        "title": _text(payload.get("title")) or _text(payload.get("package_or_project_name")) or native_id,
        "description_summary": _text(payload.get("description_summary")) or "unknown",
        "version_or_state": _text(payload.get("version_or_state")) or "unknown",
        "artifact_type": _text(payload.get("artifact_type")) or str(config["artifact_type"]),
        "object_family": _text(payload.get("object_family")) or str(config["object_family"]),
        "platform_or_context": _text(payload.get("platform_or_context")) or str(config["platform_or_context"]),
        "package_or_project_name": _text(payload.get("package_or_project_name")),
        "release_or_snapshot_id": _text(payload.get("release_or_snapshot_id")),
        "date_or_timestamp": _text(payload.get("date_or_timestamp")),
        "file_or_asset_summary": _mapping(payload.get("file_or_asset_summary"), "file_or_asset_summary", default={}),
        "dependency_or_relationship_summary": _mapping(payload.get("dependency_or_relationship_summary"), "dependency_or_relationship_summary", default={}),
        "vulnerability_or_advisory_summary": _mapping(payload.get("vulnerability_or_advisory_summary"), "vulnerability_or_advisory_summary", default={}),
        "identity_refs": _strings(payload.get("identity_refs")),
        "source_metadata": _mapping(payload.get("source_metadata"), "source_metadata", default={}),
        "source_limitations": limitations or ["fixture-only normalization", "missing optional fields are represented as unknown"],
        "access_path_candidates": [
            {
                "access_path_kind": "fixture_metadata_reference",
                "access_path_ref": f"fixture:h1:{source_id}:{_slug(native_id)}",
                "metadata_only": True,
                "live_access_approved": False,
                "download_approved": False,
                "file_fetch_approved": False,
                "package_download_approved": False,
                "release_asset_download_approved": False,
                "source_archive_download_approved": False,
            }
        ],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": [
            "Normalized from a committed H1 public-safe fixture.",
            "Fixture runtime proves parsing only and grants no live access.",
        ],
    }
    source_cache_preview = build_h1_source_cache_candidate_preview(base_record, policy)
    evidence_preview = build_h1_evidence_candidate_preview(base_record, policy)
    record = dict(base_record)
    record["source_cache_candidate_preview"] = source_cache_preview
    record["evidence_candidate_preview"] = evidence_preview
    _raise_on_boundary_errors(record)
    return record


def build_h1_source_cache_candidate_preview(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Map a normalized record into a source-cache candidate preview only."""

    source_id = str(normalized_record.get("source_id") or "unknown_source")
    native_id = str(normalized_record.get("source_native_id") or "unknown")
    preview = {
        "schema_version": "h1_metadata_source_cache_candidate_preview.v0",
        "candidate_id": f"h1.source_cache_candidate.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "connector_family": normalized_record.get("connector_family"),
        "source_native_id": native_id,
        "source_locator": normalized_record.get("source_locator"),
        "source_metadata_summary": {
            "title": normalized_record.get("title"),
            "version_or_state": normalized_record.get("version_or_state"),
            "artifact_type": normalized_record.get("artifact_type"),
            "object_family": normalized_record.get("object_family"),
            "package_or_project_name": normalized_record.get("package_or_project_name"),
            "release_or_snapshot_id": normalized_record.get("release_or_snapshot_id"),
            "date_or_timestamp": normalized_record.get("date_or_timestamp"),
        },
        "source_limitations": list(normalized_record.get("source_limitations") or []),
        "mapping_status": "preview_only_fixture",
        "source_cache_write_enabled": False,
        "source_cache_runtime_mutated": False,
        "accepted_source_truth": False,
        "truth_boundary": {
            "source_cache_preview_is_accepted_source": False,
            "normalized_record_is_public_truth": False,
            "title_match_is_verified_identity": False,
            "version_field_is_accepted_release_truth": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "rights_clearance_claimed": False,
            "malware_safety_claimed": False,
            "verified_installability_claimed": False,
        },
        "product_boundary": _product_boundary(),
        "notes": ["Source-cache preview only; no source-cache runtime write occurred."],
    }
    _raise_on_boundary_errors(preview)
    return preview


def build_h1_evidence_candidate_preview(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Map a normalized record into evidence candidate previews only."""

    source_id = str(normalized_record.get("source_id") or "unknown_source")
    native_id = str(normalized_record.get("source_native_id") or "unknown")
    candidates = [
        _claim("title_candidate", normalized_record.get("title"), "Title is a source observation, not verified identity."),
        _claim("version_or_state_candidate", normalized_record.get("version_or_state"), "Version/state is not accepted release truth."),
        _claim("source_locator_candidate", normalized_record.get("source_locator"), "Source locator is not rights clearance."),
        _claim("artifact_type_candidate", normalized_record.get("artifact_type"), "Artifact type is descriptive only."),
    ]
    if normalized_record.get("vulnerability_or_advisory_summary"):
        candidates.append(_claim("advisory_metadata_candidate", normalized_record.get("vulnerability_or_advisory_summary"), "Advisory metadata is not a security conclusion without review."))
    preview = {
        "schema_version": "h1_metadata_evidence_candidate_preview.v0",
        "evidence_preview_id": f"h1.evidence_candidate_preview.{source_id}.{_slug(native_id)}.v0",
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
            "title_match_is_verified_identity": False,
            "version_field_is_accepted_release_truth": False,
            "security_conclusion_without_review": False,
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


def build_h1_fixture_replay_result(
    fixture: Mapping[str, Any],
    normalized_record: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a replay result for one committed fixture."""

    source_id = str(fixture.get("source_id") or normalized_record.get("source_id"))
    native_id = str(normalized_record.get("source_native_id") or fixture.get("fixture_id") or "unknown")
    replay_status = "policy_blocked_fixture" if fixture.get("fixture_kind") == "policy_blocked" else "pass"
    envelope = build_connector_output_envelope(
        {
            "output_envelope_id": f"h1.output_envelope.{source_id}.{_slug(native_id)}.v0",
            "connector_id": f"{source_id}_fixture_normalizer",
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
    result = {
        "schema_version": "h1_metadata_fixture_replay_result.v0",
        "replay_result_id": f"h1.fixture_replay.{source_id}.{_slug(native_id)}.v0",
        "fixture_id": fixture.get("fixture_id"),
        "source_id": source_id,
        "connector_family": normalized_record.get("connector_family"),
        "replay_status": replay_status,
        "normalized_record_ref": f"examples/connectors/h1_metadata_wave/normalized/{source_id}_normalized.json",
        "source_cache_candidate_ref": normalized_record.get("source_cache_candidate_preview", {}).get("candidate_id"),
        "evidence_candidate_preview_ref": normalized_record.get("evidence_candidate_preview", {}).get("evidence_preview_id"),
        "connector_output_envelope": envelope,
        "validation_summary": {
            "status": replay_status,
            "fixture_only": True,
            "normalization_succeeded": True,
            "no_network_used": True,
            "no_live_source_used": True,
            "source_cache_write_enabled": False,
            "evidence_ledger_write_enabled": False,
        },
        "warnings": [],
        "limitations": list(normalized_record.get("source_limitations") or []),
        "no_network_used": True,
        "no_live_source_used": True,
        "truth_boundary": {
            "fixture_replay_result_is_source_truth": False,
            "normalized_record_is_public_truth": False,
            "source_cache_preview_is_accepted_source": False,
            "evidence_preview_is_accepted_evidence": False,
            "fixture_replay_can_mutate_public_index": False,
            "fixture_replay_can_mutate_master_index": False,
            "fixture_replay_can_claim_rights_clearance": False,
            "fixture_replay_can_claim_malware_safety": False,
            "fixture_replay_can_claim_verified_installability": False,
        },
        "product_boundary": _product_boundary(),
        "notes": ["Fixture replay proves parsing only; it grants no source access."],
    }
    _raise_on_boundary_errors(result)
    return result


def summarize_h1_normalized_record(record: Mapping[str, Any]) -> dict[str, Any]:
    """Return a compact normalized-record summary."""

    return {
        "source_id": record.get("source_id"),
        "connector_family": record.get("connector_family"),
        "source_native_id": record.get("source_native_id"),
        "title": record.get("title"),
        "version_or_state": record.get("version_or_state"),
        "artifact_type": record.get("artifact_type"),
        "source_cache_preview_is_accepted_source": False,
        "evidence_preview_is_accepted_evidence": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def detect_h1_truth_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return [
        f"truth boundary violation: {path}=true"
        for path, key, value in _iter_key_values(record)
        if key in FORBIDDEN_TRUTH_TRUE_KEYS and value is True
    ]


def detect_h1_product_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
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
        "source_cache_preview_is_accepted_source": False,
        "evidence_preview_is_accepted_evidence": False,
        "title_match_is_verified_identity": False,
        "version_field_is_accepted_release_truth": False,
        "package_metadata_is_installability_verification": False,
        "vulnerability_record_is_security_conclusion": False,
        "source_locator_is_rights_clearance": False,
        "release_asset_entry_is_download_permission": False,
        "file_listing_is_local_availability_proof": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
    }


def _product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_hosting": False,
        "enabled_live_probes": False,
        "enabled_source_sync": False,
        "enabled_source_connectors": False,
        "enabled_downloads": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
        "network_calls_made": False,
        "api_calls_made": False,
        "downloads_made": False,
        "scraping_made": False,
    }


def _raise_on_boundary_errors(record: Mapping[str, Any]) -> None:
    errors = detect_h1_truth_boundary_violations(record) + detect_h1_product_boundary_violations(record)
    if errors:
        raise ValueError("; ".join(errors))


def _missing_optional_limitations(payload: Mapping[str, Any]) -> list[str]:
    optional_fields = (
        "description_summary",
        "version_or_state",
        "date_or_timestamp",
        "file_or_asset_summary",
        "dependency_or_relationship_summary",
        "vulnerability_or_advisory_summary",
    )
    return [f"optional field absent or unknown: {field}" for field in optional_fields if payload.get(field) in (None, "", [], {})]


def _mapping(value: Any, label: str, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if value in (None, "") and default is not None:
        return dict(default)
    if isinstance(value, Mapping):
        return dict(value)
    raise ValueError(f"{label} must be a JSON object")


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


def _slug(value: str) -> str:
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

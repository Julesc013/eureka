"""Normalize committed Internet Archive-shaped metadata fixtures.

This module is fixture-only. It performs no live calls, opens no URLs, and
does not mutate source cache, evidence ledger, public index, or master index
state.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


SOURCE_ID = "internet_archive"
CONNECTOR_ID = "internet_archive_metadata_connector"

FORBIDDEN_TRUTH_TRUE_KEYS = {
    "accepted_as_evidence",
    "accepted_as_public_truth",
    "accepted_candidate_truth",
    "accepted_evidence",
    "accepted_evidence_truth",
    "accepted_public_truth",
    "candidate_truth_accepted",
    "claimed_exhaustive_search",
    "claimed_malware_safety",
    "claimed_production_readiness",
    "claimed_rights_clearance",
    "claimed_verified_installability",
    "evidence_preview_is_accepted_evidence",
    "file_download_availability_proven",
    "ia_metadata_is_public_truth",
    "is_public_truth",
    "malware_safety_claimed",
    "master_index_mutated",
    "metadata_is_canonical_truth",
    "public_index_mutated",
    "rights_clearance_claimed",
    "source_cache_preview_is_accepted_source",
    "title_match_is_identity_proof",
    "verified_installability_claimed",
}

FORBIDDEN_PRODUCT_TRUE_KEYS = {
    "api_calls_made",
    "archive_org_called",
    "changed_product_behavior",
    "changed_public_search_behavior",
    "connector_runtime_enabled",
    "downloads_enabled",
    "downloads_made",
    "enabled_accounts",
    "enabled_downloads",
    "enabled_hosting",
    "enabled_live_probes",
    "enabled_source_connectors",
    "enabled_source_sync",
    "enabled_telemetry",
    "enabled_uploads",
    "evidence_ledger_runtime_mutated",
    "external_api_used",
    "file_download_approved",
    "file_fetch_approved",
    "item_file_fetch_approved",
    "live_call_used",
    "live_connector_enabled",
    "master_index_mutated",
    "metadata_probe_approved",
    "mutated_master_index",
    "mutated_public_index",
    "network_calls_made",
    "network_used",
    "public_index_mutated",
    "public_query_fanout_approved",
    "scraping_approved",
    "source_cache_runtime_mutated",
}


def normalize_ia_metadata(raw_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Return a normalized source-observation record from a committed fixture."""

    boundary_errors = (
        validate_no_live_call_boundary(raw_record)
        + detect_truth_boundary_violations(raw_record)
        + detect_product_boundary_violations(raw_record)
    )
    if boundary_errors:
        raise ValueError("; ".join(boundary_errors))

    payload = _coerce_mapping(raw_record.get("raw_metadata") or raw_record.get("item") or raw_record, "raw metadata")
    metadata = _coerce_mapping(payload.get("metadata") or payload, "metadata")
    files = _coerce_list(payload.get("files"), "files")
    identifier = _required_string(metadata, "identifier")
    title = _string_value(metadata.get("title")) or identifier
    description = _description_summary(metadata.get("description"))
    mediatype = _string_value(metadata.get("mediatype")) or "unknown"
    collection = _string_list(metadata.get("collection"))
    creator = _string_list(metadata.get("creator"))
    date = _string_value(metadata.get("date"))
    publicdate = _string_value(metadata.get("publicdate"))
    file_candidates = [_normalize_file(item, index) for index, item in enumerate(files)]
    policy_state = _coerce_mapping(raw_record.get("policy") or {}, "policy")
    blocked_reasons = _string_list(policy_state.get("blocked_reasons"))
    fixture_limitations = _string_list(raw_record.get("limitations"))
    if policy_state.get("blocked_current") is True and "blocked by fixture policy" not in fixture_limitations:
        fixture_limitations.append("blocked by fixture policy")

    record = {
        "schema_version": "internet_archive_metadata_normalized_record.v0",
        "source_id": SOURCE_ID,
        "connector_id": CONNECTOR_ID,
        "source_native_id": identifier,
        "item_identifier": identifier,
        "title": title,
        "description_summary": description,
        "mediatype": mediatype,
        "collection": collection,
        "creator": creator,
        "date": date,
        "publicdate": publicdate,
        "metadata_fields": _public_safe_metadata(metadata),
        "file_summary": _file_summary(file_candidates),
        "file_count": len(file_candidates),
        "file_candidates": file_candidates,
        "source_locator": f"ia:item:{identifier}",
        "access_path_candidates": [
            {
                "access_path_kind": "internet_archive_item_metadata_future",
                "access_path_ref": f"ia:item:{identifier}",
                "metadata_only": True,
                "live_access_approved": False,
                "download_approved": False,
                "file_fetch_approved": False,
            }
        ],
        "policy": {
            "blocked_current": policy_state.get("blocked_current") is True,
            "blocked_reasons": blocked_reasons,
            "live_access_approved": False,
            "metadata_probe_approved": False,
            "download_approved": False,
            "file_fetch_approved": False,
            "scraping_approved": False,
            "public_query_fanout_approved": False,
        },
        "rights_risk_posture": _rights_risk_posture(),
        "limitations": fixture_limitations
        or [
            "fixture-only normalization",
            "Internet Archive metadata is a source observation, not truth",
        ],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": [
            "Normalized from a committed public-safe fixture.",
            "No Internet Archive source access, API call, file fetch, download, or scraping occurred.",
        ],
    }
    post_errors = detect_truth_boundary_violations(record) + detect_product_boundary_violations(record)
    if post_errors:
        raise ValueError("; ".join(post_errors))
    return record


def summarize_ia_normalized_record(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": record.get("source_id"),
        "item_identifier": record.get("item_identifier"),
        "title": record.get("title"),
        "mediatype": record.get("mediatype"),
        "file_count": record.get("file_count"),
        "blocked_current": _coerce_mapping(record.get("policy") or {}, "policy").get("blocked_current") is True,
        "accepted_public_truth": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def map_normalized_to_source_cache_candidate(
    record: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    identifier = _required_string(record, "item_identifier")
    candidate = {
        "schema_version": "internet_archive_source_cache_candidate_preview.v0",
        "candidate_id": f"source_cache_candidate.internet_archive.{identifier}.v0",
        "source_id": SOURCE_ID,
        "source_native_id": record.get("source_native_id"),
        "source_locator": record.get("source_locator"),
        "source_metadata_summary": {
            "title": record.get("title"),
            "description_summary": record.get("description_summary"),
            "mediatype": record.get("mediatype"),
            "creator": record.get("creator", []),
            "date": record.get("date"),
            "publicdate": record.get("publicdate"),
            "collection": record.get("collection", []),
        },
        "source_coverage_summary": {
            "file_count": record.get("file_count", 0),
            "file_names": [item.get("name") for item in record.get("file_candidates", []) if isinstance(item, Mapping)],
            "formats": record.get("file_summary", {}).get("formats", []) if isinstance(record.get("file_summary"), Mapping) else [],
        },
        "source_limitations": record.get("limitations", []),
        "mapping_status": "preview_only_fixture",
        "source_cache_write_enabled": False,
        "source_cache_runtime_mutated": False,
        "accepted_source_truth": False,
        "truth_boundary": {
            "source_cache_preview_is_accepted_source": False,
            "ia_metadata_is_public_truth": False,
            "accepted_evidence_truth": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "rights_clearance_claimed": False,
            "malware_safety_claimed": False,
            "verified_installability_claimed": False,
        },
        "product_boundary": _product_boundary(),
        "notes": [
            "Preview shape only; no source cache runtime write occurred.",
            "No direct truth conversion is allowed.",
        ],
    }
    _raise_on_boundary_errors(candidate)
    return candidate


def preview_evidence_candidates(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    identifier = _required_string(record, "item_identifier")
    candidates = [
        _evidence_candidate(identifier, "title_claim_candidate", record.get("title")),
        _evidence_candidate(identifier, "mediatype_claim_candidate", record.get("mediatype")),
        _evidence_candidate(identifier, "file_list_member_claim_candidate", record.get("file_summary")),
        _evidence_candidate(identifier, "creator_date_claim_candidate", {"creator": record.get("creator", []), "date": record.get("date")}),
        _evidence_candidate(identifier, "source_locator_claim_candidate", record.get("source_locator")),
        _evidence_candidate(identifier, "collection_membership_claim_candidate", record.get("collection", [])),
    ]
    preview = {
        "schema_version": "internet_archive_evidence_candidate_preview.v0",
        "evidence_preview_id": f"evidence_candidate_preview.internet_archive.{identifier}.v0",
        "source_id": SOURCE_ID,
        "source_native_id": record.get("source_native_id"),
        "source_locator": record.get("source_locator"),
        "candidate_count": len(candidates),
        "candidates": candidates,
        "evidence_ledger_runtime_mutated": False,
        "accepted_evidence": False,
        "truth_boundary": {
            "evidence_preview_is_accepted_evidence": False,
            "ia_metadata_is_public_truth": False,
            "title_match_is_identity_proof": False,
            "file_download_availability_proven": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "rights_clearance_claimed": False,
            "malware_safety_claimed": False,
            "verified_installability_claimed": False,
        },
        "product_boundary": _product_boundary(),
        "notes": [
            "Evidence candidates require later review before downstream use.",
            "No evidence ledger runtime write or evidence acceptance occurred.",
        ],
    }
    _raise_on_boundary_errors(preview)
    return preview


def validate_no_live_call_boundary(record: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for path, key, value in _iter_key_values(record):
        if key in {
            "live_call_used",
            "network_used",
            "external_api_used",
            "archive_org_called",
            "api_calls_made",
            "network_calls_made",
        } and value is True:
            errors.append(f"{path} must be false for IA-BUNDLE-01 fixture-only records")
    return errors


def detect_truth_boundary_violations(record: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for path, key, value in _iter_key_values(record):
        if key in FORBIDDEN_TRUTH_TRUE_KEYS and value is True:
            errors.append(f"truth boundary violation: {path}=true")
    return errors


def detect_product_boundary_violations(record: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for path, key, value in _iter_key_values(record):
        if key in FORBIDDEN_PRODUCT_TRUE_KEYS and value is True:
            errors.append(f"product boundary violation: {path}=true")
    return errors


def _raise_on_boundary_errors(record: Mapping[str, Any]) -> None:
    errors = detect_truth_boundary_violations(record) + detect_product_boundary_violations(record)
    if errors:
        raise ValueError("; ".join(errors))


def _normalize_file(item: Any, index: int) -> dict[str, Any]:
    if not isinstance(item, Mapping):
        raise ValueError(f"files[{index}] must be an object.")
    name = _string_value(item.get("name")) or f"unnamed_file_{index}"
    size = _integer_or_none(item.get("size"))
    return {
        "name": name,
        "format": _string_value(item.get("format")) or "unknown",
        "size": size,
        "source_member_ref": f"ia:file:{name}",
        "metadata_only": True,
        "downloadable_now": False,
        "file_fetch_approved": False,
        "download_approved": False,
        "truth_boundary": {
            "file_download_availability_proven": False,
            "accepted_evidence_truth": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "rights_clearance_claimed": False,
            "malware_safety_claimed": False,
            "verified_installability_claimed": False,
        },
    }


def _file_summary(file_candidates: list[Mapping[str, Any]]) -> dict[str, Any]:
    formats = sorted({str(item.get("format")) for item in file_candidates if item.get("format")})
    total_size = sum(item.get("size") or 0 for item in file_candidates)
    return {
        "file_count": len(file_candidates),
        "formats": formats,
        "total_size_bytes": total_size,
        "member_names": [str(item.get("name")) for item in file_candidates],
        "metadata_only": True,
        "download_approved": False,
    }


def _evidence_candidate(identifier: str, claim_kind: str, value: Any) -> dict[str, Any]:
    return {
        "candidate_id": f"evidence_candidate.internet_archive.{identifier}.{claim_kind}.v0",
        "claim_kind": claim_kind,
        "claim_value": value,
        "source_ref": f"ia:item:{identifier}",
        "review_required": True,
        "accepted_evidence": False,
        "accepted_public_truth": False,
        "master_index_mutation_allowed": False,
        "public_index_mutation_allowed": False,
        "limitations": [
            "candidate preview only",
            "Internet Archive metadata does not become canonical truth without review",
        ],
    }


def _truth_boundary() -> dict[str, bool]:
    return {
        "source_observation_only": True,
        "ia_metadata_is_public_truth": False,
        "accepted_evidence_truth": False,
        "accepted_candidate_truth": False,
        "accepted_public_truth": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
        "claimed_exhaustive_search": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def _product_boundary() -> dict[str, bool]:
    return {
        "changed_product_behavior": False,
        "changed_public_search_behavior": False,
        "live_connector_enabled": False,
        "enabled_live_probes": False,
        "enabled_source_sync": False,
        "enabled_source_connectors": False,
        "enabled_downloads": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "enabled_hosting": False,
        "network_calls_made": False,
        "api_calls_made": False,
        "downloads_made": False,
        "source_cache_runtime_mutated": False,
        "evidence_ledger_runtime_mutated": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def _rights_risk_posture() -> dict[str, bool]:
    return {
        "metadata_only": True,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
        "download_or_file_fetch_approved": False,
        "review_required": True,
    }


def _public_safe_metadata(metadata: Mapping[str, Any]) -> dict[str, Any]:
    allowed: dict[str, Any] = {}
    for key, value in sorted(metadata.items()):
        if key in {"identifier", "title", "description", "mediatype", "collection", "creator", "date", "publicdate"}:
            continue
        if isinstance(value, str):
            allowed[str(key)] = value
        elif isinstance(value, list) and all(isinstance(item, str) for item in value):
            allowed[str(key)] = list(value)
        elif isinstance(value, (int, float, bool)) or value is None:
            allowed[str(key)] = value
    return allowed


def _description_summary(value: Any) -> str:
    text = _string_value(value)
    if not text:
        return ""
    text = " ".join(text.split())
    return text[:240]


def _required_string(mapping: Mapping[str, Any], key: str) -> str:
    value = _string_value(mapping.get(key))
    if not value:
        raise ValueError(f"{key} must be a non-empty string.")
    return value


def _string_value(value: Any) -> str | None:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    if isinstance(value, list):
        strings = [item.strip() for item in value if isinstance(item, str) and item.strip()]
        return "; ".join(strings) if strings else None
    return None


def _string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, list):
        return [item.strip() for item in value if isinstance(item, str) and item.strip()]
    return []


def _integer_or_none(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _coerce_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object.")
    return value


def _coerce_list(value: Any, label: str) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list.")
    return value


def _iter_key_values(value: Any, prefix: str = "") -> Iterable[tuple[str, str, Any]]:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            yield path, key_text, nested
            yield from _iter_key_values(nested, path)
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            yield from _iter_key_values(nested, f"{prefix}[{index}]")

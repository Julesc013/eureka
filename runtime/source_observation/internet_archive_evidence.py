"""Internet Archive metadata source-cache to evidence-ledger candidate helpers."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.evidence_ledger import EvidenceCandidateRecord, EvidenceReviewStatus
from runtime.evidence_ledger.validation import validate_evidence_candidate_record
from runtime.source_observation.ids import stable_digest
from runtime.source_observation.internet_archive_metadata import SOURCE_ID
from runtime.source_observation.internet_archive_source_cache import (
    DEFAULT_LIVE_PREVIEW_PATHS,
    build_ia_source_cache_records,
    load_fixture_normalized_records,
    load_ia_source_cache_policy,
    load_live_preview_records,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY_PATH = REPO_ROOT / "control" / "policies" / "ia_evidence_ledger_policy.json"
DEFAULT_CREATED_AT = "2026-05-18T00:00:00Z"
CLAIM_KINDS = (
    "title_claim_candidate",
    "mediatype_claim_candidate",
    "collection_claim_candidate",
    "creator_claim_candidate",
    "date_claim_candidate",
    "description_claim_candidate",
    "file_metadata_claim_candidate",
    "checksum_metadata_claim_candidate",
    "source_locator_claim_candidate",
    "relation_claim_candidate",
)


def load_ia_evidence_policy(path: str | Path = DEFAULT_POLICY_PATH) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_default_ia_source_cache_records(
    *,
    include_fixtures: bool = True,
    include_live_preview: bool = True,
    live_preview_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    source_cache_policy = load_ia_source_cache_policy()
    normalized_records: list[dict[str, Any]] = []
    if include_fixtures:
        normalized_records.extend(load_fixture_normalized_records())
    if include_live_preview:
        path = live_preview_path or DEFAULT_LIVE_PREVIEW_PATHS[0]
        normalized_records.extend(load_live_preview_records(path))
    return build_ia_source_cache_records(
        normalized_records,
        source_cache_policy,
        live_probe_id="ia02_tls_continue_verified_probe",
    )


def load_ia_source_cache_record_file(path: str | Path) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return [dict(item) for item in payload if isinstance(item, Mapping)]
    if not isinstance(payload, Mapping):
        return []
    for key in ("records", "source_cache_records", "ia_source_cache_records"):
        value = payload.get(key)
        if isinstance(value, list):
            return [dict(item) for item in value if isinstance(item, Mapping)]
    if payload.get("schema_version") == "ia_source_cache_record.v0":
        return [dict(payload)]
    return []


def build_ia_evidence_candidates(source_cache_record: Mapping[str, Any], policy: Mapping[str, Any]) -> list[dict[str, Any]]:
    _ensure_policy(policy)
    record = dict(source_cache_record)
    candidates: list[dict[str, Any]] = []

    title = _candidate_or_redacted(record, "title_candidate", "title_candidate_present", "title metadata present")
    if title:
        candidates.append(_candidate(record, "title_claim_candidate", title, "metadata_field:title"))

    mediatype = str(record.get("mediatype_candidate", ""))
    if mediatype:
        candidates.append(_candidate(record, "mediatype_claim_candidate", mediatype, "metadata_field:mediatype"))

    collections = [str(item) for item in record.get("collection_candidates", []) or [] if str(item)]
    if collections:
        for collection in collections:
            candidates.append(_candidate(record, "collection_claim_candidate", collection, "metadata_field:collection"))
            candidates.append(
                _candidate(
                    record,
                    "relation_claim_candidate",
                    {"relation": "item_in_collection", "collection": collection},
                    "metadata_relation:collection",
                )
            )
    elif int(record.get("collection_candidate_count", 0) or 0):
        candidates.append(
            _candidate(
                record,
                "collection_claim_candidate",
                {"collection_metadata_count": int(record.get("collection_candidate_count", 0) or 0)},
                "metadata_field:collection",
            )
        )

    creator = _candidate_or_redacted(record, "creator_candidate", "creator_candidate_present", "creator metadata present")
    if creator:
        candidates.append(_candidate(record, "creator_claim_candidate", creator, "metadata_field:creator"))

    date = _candidate_or_redacted(record, "date_candidate", "date_candidate_present", "date metadata present")
    if date:
        candidates.append(_candidate(record, "date_claim_candidate", date, "metadata_field:date"))

    description = _candidate_or_redacted(
        record,
        "description_candidate",
        "description_candidate_present",
        "description metadata present",
    )
    if description:
        candidates.append(
            _candidate(record, "description_claim_candidate", _bounded_description(description), "metadata_field:description")
        )

    file_summary = dict(record.get("file_metadata_summary", {}) or {})
    if int(file_summary.get("count", 0) or 0):
        candidates.append(_candidate(record, "file_metadata_claim_candidate", _file_claim_value(file_summary), "metadata_field:files"))
        candidates.append(
            _candidate(
                record,
                "relation_claim_candidate",
                {"relation": "item_has_file_metadata_entries", "file_metadata_count": int(file_summary.get("count", 0) or 0)},
                "metadata_relation:file_list",
            )
        )

    checksum_summary = dict(record.get("checksum_summary", {}) or {})
    if int(checksum_summary.get("count", 0) or 0):
        candidates.append(
            _candidate(
                record,
                "checksum_metadata_claim_candidate",
                {
                    "checksum_metadata_count": int(checksum_summary.get("count", 0) or 0),
                    "algorithms": list(checksum_summary.get("algorithms", []) or []),
                    "source_provided_metadata_only": True,
                },
                "metadata_field:checksums",
            )
        )

    source_locator = dict(record.get("source_locator", {}) or {})
    if source_locator:
        candidates.append(_candidate(record, "source_locator_claim_candidate", _locator_claim_value(source_locator), "source_locator"))

    for candidate in candidates:
        errors = validate_ia_evidence_candidate(candidate, policy)
        if errors:
            raise ValueError("; ".join(errors))
    return candidates


def build_ia_evidence_candidate_records(
    source_cache_records: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any],
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for record in source_cache_records:
        candidates.extend(build_ia_evidence_candidates(record, policy))
    return candidates


def validate_ia_evidence_candidate(candidate: Mapping[str, Any], policy: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    if candidate.get("schema_version") != "ia_evidence_candidate.v0":
        errors.append("evidence candidate schema mismatch")
    if candidate.get("source_id") != SOURCE_ID:
        errors.append("source_id must be internet_archive_metadata")
    for key in (
        "evidence_id",
        "source_cache_record_id",
        "observation_id",
        "claim_id",
        "claim_kind",
        "claim_value",
        "claim_value_normalized",
        "claim_subject",
        "claim_scope",
        "source_locator",
        "provenance",
        "support_level",
        "confidence",
        "uncertainty",
        "limitations",
        "created_at",
    ):
        if key not in candidate or candidate.get(key) in ("", None):
            errors.append(f"{key} is required")
    if candidate.get("claim_kind") not in CLAIM_KINDS:
        errors.append("claim kind is not allowed for IA-04")
    if candidate.get("review_required") is not True:
        errors.append("review_required must be true")
    if candidate.get("reviewer_decision") not in ("pending", None):
        errors.append("reviewer decision must be pending")
    for key in (
        "accepted_truth",
        "candidate_index_mutation_performed",
        "reviewed_index_mutation_performed",
        "master_index_mutation_performed",
        "raw_response_committed",
        "download_performed",
        "upload_performed",
        "extraction_executed",
        "model_provider_used",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if candidate.get(key) is not False:
            errors.append(f"{key} must be false")
    if policy.get("evidence_ledger_writes_enabled_for_IA_04") is not True:
        errors.append("IA-04 evidence writes must be explicitly enabled by policy")
    if policy.get("accepted_truth_enabled") is not False:
        errors.append("accepted truth must be disabled")
    if policy.get("candidate_index_mutation_enabled") is not False:
        errors.append("candidate index mutation must be disabled")
    if policy.get("reviewed_index_mutation_enabled") is not False:
        errors.append("reviewed index mutation must be disabled")
    if policy.get("master_index_mutation_enabled") is not False:
        errors.append("master index mutation must be disabled")
    return tuple(errors)


def to_evidence_candidate_record(candidate: Mapping[str, Any]) -> EvidenceCandidateRecord:
    payload = _ledger_payload(candidate)
    record = EvidenceCandidateRecord(
        evidence_id=str(candidate["evidence_id"]),
        source_id=str(candidate["source_id"]),
        source_cache_entry_id=str(candidate["source_cache_record_id"]),
        observation_id=str(candidate["observation_id"]),
        normalized_observation_id="iaevnorm_" + stable_digest(payload),
        claim_kind=str(candidate["claim_kind"]),
        claim_subject=str(candidate["claim_subject"]),
        claim_payload=payload,
        status=EvidenceReviewStatus.NEEDS_REVIEW,
        limitations=tuple(str(item) for item in candidate.get("limitations", []) or []),
        warnings=tuple(str(item) for item in candidate.get("risk_flags", []) or []),
        created_at=str(candidate.get("created_at", DEFAULT_CREATED_AT)),
        updated_at=str(candidate.get("created_at", DEFAULT_CREATED_AT)),
    )
    errors = validate_evidence_candidate_record(record)
    if errors:
        raise ValueError("; ".join(errors))
    return record


def write_ia_evidence_candidates(store: Any, candidates: Sequence[Mapping[str, Any]], dry_run: bool = True) -> dict[str, Any]:
    candidate_list = [dict(candidate) for candidate in candidates]
    policy = {
        "evidence_ledger_writes_enabled_for_IA_04": True,
        "accepted_truth_enabled": False,
        "candidate_index_mutation_enabled": False,
        "reviewed_index_mutation_enabled": False,
        "master_index_mutation_enabled": False,
    }
    errors = [error for candidate in candidate_list for error in validate_ia_evidence_candidate(candidate, policy)]
    if errors:
        raise ValueError("; ".join(errors))
    result: dict[str, Any] = {
        "schema_version": "ia_evidence_store_write_result.v0",
        "dry_run": dry_run,
        "candidate_count": len(candidate_list),
        "write_applied": False,
        "writes": [],
        "summary": {},
        "integrity": {},
    }
    if dry_run:
        return result
    store.init()
    writes: list[dict[str, Any]] = []
    for candidate in candidate_list:
        writes.append(store.write_evidence_candidate(to_evidence_candidate_record(candidate)))
    result.update(
        {
            "write_applied": bool(candidate_list),
            "writes": writes,
            "summary": store.summarize().to_dict(),
            "integrity": store.check_integrity(),
        }
    )
    return result


def build_ia_evidence_write_report(
    candidates: Sequence[Mapping[str, Any]],
    dry_run: bool,
    store_result: Mapping[str, Any],
    write_scope: str,
) -> dict[str, Any]:
    candidate_list = [dict(item) for item in candidates]
    source_kinds = [str((item.get("provenance", {}) or {}).get("source_kind", "")) for item in candidate_list]
    claim_counts = Counter(str(item.get("claim_kind", "")) for item in candidate_list)
    write_applied = bool(store_result.get("write_applied", False))
    return {
        "schema_version": "ia_evidence_write_report.v0",
        "task": "IA-04",
        "status": "pass",
        "dry_run": dry_run,
        "write_scope": write_scope,
        "candidate_count": len(candidate_list),
        "fixture_candidate_count": source_kinds.count("ia_fixture_replay"),
        "live_preview_candidate_count": source_kinds.count("ia_live_probe_preview"),
        "claim_kind_counts": dict(sorted(claim_counts.items())),
        "evidence_ids": [str(item.get("evidence_id", "")) for item in candidate_list],
        "store_result": dict(store_result),
        "evidence_ledger_write_performed": write_applied,
        "fixture_evidence_written_to_temp": bool(write_applied and "ia_fixture_replay" in source_kinds),
        "live_preview_evidence_written_to_temp": bool(write_applied and "ia_live_probe_preview" in source_kinds),
        "all_evidence_requires_review": all(item.get("review_required") is True for item in candidate_list),
        "accepted_truth_created": any(item.get("accepted_truth") is True for item in candidate_list),
        "raw_response_committed": False,
        "candidate_index_mutated": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def build_ia_evidence_boundary_report(report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "ia_evidence_boundary_report.v0",
        "task": "IA-04",
        "passed": bool(report.get("all_evidence_requires_review", True)) and not bool(report.get("accepted_truth_created", False)),
        "violations": [],
        "dry_run": bool(report.get("dry_run", True)),
        "write_scope": str(report.get("write_scope", "")),
        "operator_instance_mutated": False,
        "instance_state_committed": False,
        "raw_response_committed": False,
        "evidence_ledger_write_performed": bool(report.get("evidence_ledger_write_performed", False)),
        "evidence_ledger_write_scope": str(report.get("write_scope", "")),
        "accepted_truth_created": bool(report.get("accepted_truth_created", False)),
        "candidate_index_mutated": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def _ensure_policy(policy: Mapping[str, Any]) -> None:
    if policy.get("schema_version") != "ia_evidence_ledger_policy.v0":
        raise ValueError("IA evidence policy schema mismatch")
    if policy.get("evidence_ledger_writes_enabled_for_IA_04") is not True:
        raise ValueError("IA evidence writes are not enabled for IA-04")
    if policy.get("accepted_truth_enabled") is not False:
        raise ValueError("accepted truth must remain disabled")


def _candidate(record: Mapping[str, Any], claim_kind: str, claim_value: Any, claim_scope: str) -> dict[str, Any]:
    source_cache_record_id = str(record.get("record_id", ""))
    source_locator = dict(record.get("source_locator", {}) or {})
    subject = _claim_subject(record, source_locator)
    claim_id = "iaclaim_" + stable_digest(
        {
            "source_cache_record_id": source_cache_record_id,
            "claim_kind": claim_kind,
            "claim_scope": claim_scope,
            "claim_value": claim_value,
        }
    )
    return {
        "schema_version": "ia_evidence_candidate.v0",
        "evidence_id": "iaev_" + stable_digest({"claim_id": claim_id, "observation_id": record.get("observation_id", "")}),
        "source_id": SOURCE_ID,
        "source_cache_record_id": source_cache_record_id,
        "observation_id": str(record.get("observation_id", "")),
        "claim_id": claim_id,
        "claim_kind": claim_kind,
        "claim_value": claim_value,
        "claim_value_normalized": _normalized_claim_value(claim_value),
        "claim_subject": subject,
        "claim_scope": claim_scope,
        "source_locator": _locator_claim_value(source_locator),
        "provenance": _provenance(record),
        "support_level": "source_metadata_observation_candidate",
        "confidence": float(record.get("confidence", 0.0) or 0.0),
        "uncertainty": [
            "source metadata requires human review",
            "source-provided metadata may be incomplete or stale",
            "rights, safety, compatibility, and final identity are not inferred",
        ],
        "limitations": _limitations(record),
        "risk_flags": list(record.get("risk_flags", []) or []),
        "rights_flags": list(record.get("rights_flags", []) or []),
        "review_required": True,
        "accepted_truth": False,
        "reviewer_decision": "pending",
        "candidate_index_mutation_performed": False,
        "reviewed_index_mutation_performed": False,
        "master_index_mutation_performed": False,
        "raw_response_committed": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "created_at": str(record.get("captured_at", DEFAULT_CREATED_AT) or DEFAULT_CREATED_AT),
    }


def _ledger_payload(candidate: Mapping[str, Any]) -> dict[str, Any]:
    provenance = dict(candidate.get("provenance", {}) or {})
    locator = dict(candidate.get("source_locator", {}) or {})
    return {
        "schema_version": "ia_evidence_ledger_payload.v0",
        "claim_id": str(candidate.get("claim_id", "")),
        "claim_value": candidate.get("claim_value"),
        "claim_value_normalized": candidate.get("claim_value_normalized"),
        "claim_scope": str(candidate.get("claim_scope", "")),
        "source_cache_record_id": str(candidate.get("source_cache_record_id", "")),
        "source_locator": {
            "kind": str(locator.get("kind", "")),
            "label": str(locator.get("label", "")),
            "value_hash": str(locator.get("value_hash", "")),
        },
        "provenance": {
            "source_kind": str(provenance.get("source_kind", "")),
            "observation_kind": str(provenance.get("observation_kind", "")),
            "endpoint_class": str(provenance.get("endpoint_class", "")),
            "fixture_id": str(provenance.get("fixture_id", "")),
            "live_probe_id": str(provenance.get("live_probe_id", "")),
            "request_policy_id": str(provenance.get("request_policy_id", "")),
            "metadata_only": True,
        },
        "support_level": str(candidate.get("support_level", "")),
        "confidence": float(candidate.get("confidence", 0.0) or 0.0),
        "uncertainty": list(candidate.get("uncertainty", []) or []),
        "limitations": list(candidate.get("limitations", []) or []),
        "risk_flags": list(candidate.get("risk_flags", []) or []),
        "rights_flags": list(candidate.get("rights_flags", []) or []),
        "requires_human_review": True,
        "candidate_only": True,
        "downstream_effects": {
            "candidate_index": "not_written",
            "reviewed_index": "not_written",
            "file_transfer": "not_performed",
        },
    }


def _provenance(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_cache_record_id": str(record.get("record_id", "")),
        "source_kind": str(record.get("source_kind", "")),
        "observation_kind": str(record.get("observation_kind", "")),
        "endpoint_class": str(record.get("endpoint_class", "")),
        "fixture_id": str(record.get("fixture_id", "")),
        "live_probe_id": str(record.get("live_probe_id", "")),
        "request_policy_id": str(record.get("request_policy_id", "")),
        "metadata_only": True,
        "raw_response_committed": False,
    }


def _candidate_or_redacted(record: Mapping[str, Any], value_key: str, present_key: str, redacted_label: str) -> str:
    value = str(record.get(value_key, ""))
    if value:
        return value
    if record.get(present_key) is True:
        return redacted_label
    return ""


def _bounded_description(value: str, limit: int = 240) -> str:
    text = value.strip()
    return text if len(text) <= limit else text[: limit - 3].rstrip() + "..."


def _file_claim_value(file_summary: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "file_metadata_count": int(file_summary.get("count", 0) or 0),
        "sample_names": list(file_summary.get("sample_names", []) or []),
        "metadata_only": True,
    }


def _locator_claim_value(source_locator: Mapping[str, Any]) -> dict[str, Any]:
    value = str(source_locator.get("value", ""))
    metadata = dict(source_locator.get("metadata", {}) or {})
    return {
        "kind": str(source_locator.get("kind", "")),
        "label": str(source_locator.get("label", "")),
        "value_hash": stable_digest(value, length=16) if value else "",
        "metadata_only": bool(metadata.get("metadata_only", True)),
    }


def _claim_subject(record: Mapping[str, Any], source_locator: Mapping[str, Any]) -> str:
    locator_value = str(source_locator.get("value", ""))
    if locator_value:
        return f"ia:{stable_digest(locator_value, length=16)}"
    return str(record.get("observation_id", ""))


def _normalized_claim_value(value: Any) -> Any:
    if isinstance(value, str):
        return " ".join(value.lower().split())
    if isinstance(value, list):
        return [_normalized_claim_value(item) for item in value]
    if isinstance(value, tuple):
        return [_normalized_claim_value(item) for item in value]
    if isinstance(value, Mapping):
        return stable_digest(dict(value), length=16)
    return str(value)


def _limitations(record: Mapping[str, Any]) -> list[str]:
    values = [str(item) for item in record.get("limitation_flags", []) or []]
    values.extend(
        [
            "evidence candidate requires review",
            "metadata does not establish rights clearance, compatibility, safety, installability, or final identity",
        ]
    )
    return values

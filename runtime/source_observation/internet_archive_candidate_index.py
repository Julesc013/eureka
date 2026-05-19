"""Build provisional IA candidate-index records from IA evidence candidates."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.candidate_index import CandidateIndexStore
from runtime.evidence_ledger import EvidenceLedgerStore
from runtime.local_foundry import candidate_store
from runtime.source_observation.ids import stable_digest
from runtime.source_observation.internet_archive_evidence import (
    build_ia_evidence_candidate_records,
    load_default_ia_source_cache_records,
    load_ia_evidence_policy,
)
from runtime.source_observation.internet_archive_metadata import SOURCE_ID


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY_PATH = REPO_ROOT / "control" / "policies" / "ia_candidate_index_policy.json"
DEFAULT_CREATED_AT = "2026-05-18T00:00:00Z"
ALLOWED_CANDIDATE_KINDS = {
    "ia_item_candidate",
    "ia_media_metadata_candidate",
    "ia_file_list_candidate",
    "ia_collection_member_candidate",
    "ia_source_locator_candidate",
    "ia_near_miss_candidate",
    "ia_absence_or_missing_item_candidate",
}


def load_ia_candidate_policy(path: str | Path = DEFAULT_POLICY_PATH) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_default_ia_evidence_candidates() -> list[dict[str, Any]]:
    return build_ia_evidence_candidate_records(load_default_ia_source_cache_records(), load_ia_evidence_policy())


def load_ia_evidence_candidate_file(path: str | Path) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return [dict(item) for item in payload if isinstance(item, Mapping)]
    if not isinstance(payload, Mapping):
        return []
    for key in ("candidates", "evidence_candidates", "ia_evidence_candidates"):
        value = payload.get(key)
        if isinstance(value, list):
            return [dict(item) for item in value if isinstance(item, Mapping)]
    if payload.get("schema_version") == "ia_evidence_candidate.v0":
        return [dict(payload)]
    return []


def load_ia_evidence_candidates_from_ledger(path: str | Path) -> list[dict[str, Any]]:
    db_path = Path(path)
    if not db_path.exists():
        return []
    with EvidenceLedgerStore.open(db_path) as store:
        store.init()
        records = store.list_evidence_candidates(source_id=SOURCE_ID, limit=1000)
    candidates: list[dict[str, Any]] = []
    for record in records:
        payload = dict(record.claim_payload)
        if payload.get("schema_version") != "ia_evidence_ledger_payload.v0":
            continue
        candidates.append(
            {
                "schema_version": "ia_evidence_candidate.v0",
                "evidence_id": record.evidence_id,
                "source_id": record.source_id,
                "source_cache_record_id": str(payload.get("source_cache_record_id", record.source_cache_entry_id or "")),
                "observation_id": record.observation_id,
                "claim_id": str(payload.get("claim_id", "")),
                "claim_kind": record.claim_kind,
                "claim_value": payload.get("claim_value"),
                "claim_value_normalized": payload.get("claim_value_normalized"),
                "claim_subject": record.claim_subject,
                "claim_scope": str(payload.get("claim_scope", "")),
                "source_locator": dict(payload.get("source_locator", {}) or {}),
                "provenance": dict(payload.get("provenance", {}) or {}),
                "support_level": str(payload.get("support_level", "source_metadata_observation_candidate")),
                "confidence": float(payload.get("confidence", 0.0) or 0.0),
                "uncertainty": list(payload.get("uncertainty", []) or []),
                "limitations": list(payload.get("limitations", []) or []),
                "risk_flags": list(payload.get("risk_flags", []) or []),
                "rights_flags": list(payload.get("rights_flags", []) or []),
                "review_required": True,
                "accepted_truth": False,
                "reviewer_decision": "pending",
                "candidate_index_mutation_performed": False,
                "reviewed_index_mutation_performed": False,
                "master_index_mutation_performed": False,
                "raw_response_committed": False,
                "download_performed": False,
                "created_at": record.created_at,
            }
        )
    return candidates


def build_ia_candidates_from_evidence(evidence_candidates: Sequence[Mapping[str, Any]], policy: Mapping[str, Any]) -> list[dict[str, Any]]:
    _ensure_policy(policy)
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for candidate in evidence_candidates:
        groups[str(candidate.get("source_cache_record_id", ""))].append(dict(candidate))
    records: list[dict[str, Any]] = []
    for source_cache_record_id, group in sorted(groups.items()):
        if not source_cache_record_id:
            continue
        records.extend(_records_for_group(source_cache_record_id, group))
    for record in records:
        errors = validate_ia_candidate_record(record, policy)
        if errors:
            raise ValueError("; ".join(errors))
    return records


def validate_ia_candidate_record(candidate: Mapping[str, Any], policy: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    if candidate.get("schema_version") != "ia_candidate_record.v0":
        errors.append("candidate record schema mismatch")
    if candidate.get("source_id") != SOURCE_ID:
        errors.append("source_id must be internet_archive_metadata")
    if candidate.get("candidate_kind") not in ALLOWED_CANDIDATE_KINDS:
        errors.append("candidate kind is not allowed for IA-05")
    for key in (
        "candidate_id",
        "candidate_kind",
        "source_cache_record_ids",
        "evidence_ids",
        "observation_ids",
        "candidate_subject",
        "candidate_title",
        "candidate_summary",
        "source_locator",
        "claim_summary",
        "provenance",
        "support_level",
        "confidence",
        "uncertainty",
        "limitations",
        "risk_flags",
        "rights_flags",
        "created_at",
    ):
        if key not in candidate or candidate.get(key) in ("", None, []):
            errors.append(f"{key} is required")
    if candidate.get("review_required") is not True:
        errors.append("review_required must be true")
    if candidate.get("reviewer_decision") not in ("pending", None):
        errors.append("reviewer decision must be pending")
    for key in (
        "accepted_truth",
        "reviewed_record_created",
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
    if policy.get("candidate_index_writes_enabled_for_IA_05") is not True:
        errors.append("IA-05 candidate writes must be explicitly enabled by policy")
    for key in (
        "accepted_truth_enabled",
        "reviewed_index_mutation_enabled",
        "master_index_mutation_enabled",
        "download_install_execute_enabled",
        "extraction_enabled",
        "model_provider_enabled",
        "deployment_enabled",
    ):
        if policy.get(key) is not False:
            errors.append(f"policy expected false: {key}")
    generic = candidate_store.build_candidate_record(candidate)
    generic_errors = candidate_store.validate_candidate_record(generic)
    if generic_errors:
        errors.extend(f"generic candidate validation: {error}" for error in generic_errors)
    return tuple(errors)


def write_ia_candidate_records(store: CandidateIndexStore | None, candidates: Sequence[Mapping[str, Any]], dry_run: bool = True) -> dict[str, Any]:
    candidate_list = [dict(candidate) for candidate in candidates]
    policy = {
        "candidate_index_writes_enabled_for_IA_05": True,
        "accepted_truth_enabled": False,
        "reviewed_index_mutation_enabled": False,
        "master_index_mutation_enabled": False,
        "download_install_execute_enabled": False,
        "extraction_enabled": False,
        "model_provider_enabled": False,
        "deployment_enabled": False,
    }
    errors = [error for candidate in candidate_list for error in validate_ia_candidate_record(candidate, policy)]
    if errors:
        raise ValueError("; ".join(errors))
    result: dict[str, Any] = {
        "schema_version": "ia_candidate_store_write_result.v0",
        "dry_run": dry_run,
        "candidate_count": len(candidate_list),
        "write_applied": False,
        "summary": {},
        "store_path": "",
    }
    if dry_run:
        return result
    if store is None:
        raise ValueError("candidate index store is required for apply")
    summary = store.write_candidate_records(candidate_list)
    result.update(
        {
            "write_applied": bool(candidate_list),
            "summary": summary,
            "store_path": _redacted_store_path(store.path),
        }
    )
    return result


def build_ia_candidate_write_report(
    candidates: Sequence[Mapping[str, Any]],
    dry_run: bool,
    store_result: Mapping[str, Any],
    write_scope: str,
) -> dict[str, Any]:
    candidate_list = [dict(item) for item in candidates]
    source_kinds = [str((item.get("provenance", {}) or {}).get("source_kind", "")) for item in candidate_list]
    kind_counts = Counter(str(item.get("candidate_kind", "")) for item in candidate_list)
    write_applied = bool(store_result.get("write_applied", False))
    return {
        "schema_version": "ia_candidate_write_report.v0",
        "task": "IA-05",
        "status": "pass",
        "dry_run": dry_run,
        "write_scope": write_scope,
        "candidate_count": len(candidate_list),
        "fixture_candidate_count": source_kinds.count("ia_fixture_replay"),
        "live_preview_candidate_count": source_kinds.count("ia_live_probe_preview"),
        "candidate_kind_counts": dict(sorted(kind_counts.items())),
        "candidate_ids": [str(item.get("candidate_id", "")) for item in candidate_list],
        "store_result": dict(store_result),
        "candidate_index_mutated": write_applied,
        "fixture_candidates_written_to_temp": bool(write_applied and "ia_fixture_replay" in source_kinds),
        "live_preview_candidates_written_to_temp": bool(write_applied and "ia_live_probe_preview" in source_kinds),
        "all_candidates_require_review": all(item.get("review_required") is True for item in candidate_list),
        "accepted_truth_created": any(item.get("accepted_truth") is True for item in candidate_list),
        "operator_instance_mutated": False,
        "instance_state_committed": False,
        "raw_response_committed": False,
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


def build_ia_candidate_boundary_report(report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "ia_candidate_boundary_report.v0",
        "task": "IA-05",
        "passed": bool(report.get("all_candidates_require_review", True)) and not bool(report.get("accepted_truth_created", False)),
        "violations": [],
        "dry_run": bool(report.get("dry_run", True)),
        "write_scope": str(report.get("write_scope", "")),
        "operator_instance_mutated": False,
        "instance_state_committed": False,
        "raw_response_committed": False,
        "candidate_index_mutated": bool(report.get("candidate_index_mutated", False)),
        "candidate_index_write_scope": str(report.get("write_scope", "")),
        "accepted_truth_created": bool(report.get("accepted_truth_created", False)),
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


def _records_for_group(source_cache_record_id: str, group: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    by_kind: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for candidate in group:
        by_kind[str(candidate.get("claim_kind", ""))].append(candidate)
    records: list[dict[str, Any]] = []
    observation_kind = str((_first(group).get("provenance", {}) or {}).get("observation_kind", ""))
    risk_flags = _union(group, "risk_flags")
    if observation_kind == "missing_item":
        records.append(_candidate(source_cache_record_id, "ia_absence_or_missing_item_candidate", group))
    elif observation_kind in {"malformed_partial", "retry_after"} or any(flag in {"malformed_partial", "quota_or_rate_limit"} for flag in risk_flags):
        records.append(_candidate(source_cache_record_id, "ia_near_miss_candidate", group))
    else:
        if _has_any_claim(by_kind, ("title_claim_candidate", "mediatype_claim_candidate", "description_claim_candidate")):
            records.append(_candidate(source_cache_record_id, "ia_item_candidate", group))
        if _has_any_claim(by_kind, ("mediatype_claim_candidate", "description_claim_candidate")):
            records.append(_candidate(source_cache_record_id, "ia_media_metadata_candidate", group))
        if _has_any_claim(by_kind, ("file_metadata_claim_candidate", "checksum_metadata_claim_candidate")):
            records.append(_candidate(source_cache_record_id, "ia_file_list_candidate", group))
        if _has_any_claim(by_kind, ("collection_claim_candidate", "relation_claim_candidate")):
            records.append(_candidate(source_cache_record_id, "ia_collection_member_candidate", group))
    if _has_any_claim(by_kind, ("source_locator_claim_candidate",)):
        records.append(_candidate(source_cache_record_id, "ia_source_locator_candidate", group))
    return records


def _candidate(source_cache_record_id: str, candidate_kind: str, group: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    first = _first(group)
    provenance = dict(first.get("provenance", {}) or {})
    locator = dict(first.get("source_locator", {}) or {})
    evidence_ids = sorted(str(item.get("evidence_id", "")) for item in group if item.get("evidence_id"))
    observation_ids = sorted({str(item.get("observation_id", "")) for item in group if item.get("observation_id")})
    title = _title(group, candidate_kind)
    subject = str(first.get("claim_subject", "")) or f"ia:{source_cache_record_id}"
    candidate_id = "iacand_" + stable_digest(
        {"candidate_kind": candidate_kind, "source_cache_record_id": source_cache_record_id, "evidence_ids": evidence_ids}
    )
    mediatype = _claim_text(group, "mediatype_claim_candidate")
    collection_refs = _claim_values(group, "collection_claim_candidate")
    file_summary = _claim_dict(group, "file_metadata_claim_candidate")
    checksum_summary = _claim_dict(group, "checksum_metadata_claim_candidate")
    claim_summary = _claim_summary(group)
    record = {
        "schema_version": "ia_candidate_record.v0",
        "candidate_id": candidate_id,
        "candidate_kind": candidate_kind,
        "source_id": SOURCE_ID,
        "source_cache_record_ids": [source_cache_record_id],
        "evidence_ids": evidence_ids,
        "observation_ids": observation_ids,
        "candidate_subject": subject,
        "candidate_title": title,
        "candidate_summary": _summary(candidate_kind, group),
        "source_locator": locator,
        "item_identifier": _item_identifier(locator),
        "mediatype": mediatype,
        "collection_refs": collection_refs,
        "file_summary": file_summary,
        "checksum_summary": checksum_summary,
        "claim_summary": claim_summary,
        "provenance": {
            "source_kind": str(provenance.get("source_kind", "")),
            "observation_kind": str(provenance.get("observation_kind", "")),
            "endpoint_class": str(provenance.get("endpoint_class", "")),
            "fixture_id": str(provenance.get("fixture_id", "")),
            "live_probe_id": str(provenance.get("live_probe_id", "")),
            "metadata_only": True,
            "source_cache_record_id": source_cache_record_id,
            "evidence_ids": evidence_ids,
        },
        "support_level": "provisional_candidate_from_review_required_evidence",
        "confidence": _average_confidence(group),
        "uncertainty": _union(group, "uncertainty")
        + ["candidate index record is provisional", "review required before promotion"],
        "limitations": _union(group, "limitations")
        + ["candidate index record is not reviewed truth", "no reviewed or master index mutation occurred"],
        "risk_flags": _union(group, "risk_flags"),
        "rights_flags": _union(group, "rights_flags"),
        "review_required": True,
        "accepted_truth": False,
        "reviewer_decision": "pending",
        "reviewed_record_created": False,
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
        "created_at": str(first.get("created_at", DEFAULT_CREATED_AT) or DEFAULT_CREATED_AT),
        "candidate_status": "needs_review",
        "candidate_type": _generic_candidate_type(candidate_kind),
        "candidate_origin": "evidence_ledger_record_future",
        "candidate_label": title,
        "canonical_candidate_key": f"ia:{candidate_kind}:{source_cache_record_id}",
        "confidence_or_uncertainty": "review_required_provisional_candidate",
        "evidence_acceptance_policy": _evidence_acceptance_policy(),
        "runtime_capability_policy": _runtime_capability_policy(),
        "review_gates": _review_gates(),
    }
    return record


def _ensure_policy(policy: Mapping[str, Any]) -> None:
    if policy.get("schema_version") != "ia_candidate_index_policy.v0":
        raise ValueError("IA candidate policy schema mismatch")
    if policy.get("candidate_index_writes_enabled_for_IA_05") is not True:
        raise ValueError("IA candidate writes are not enabled for IA-05")
    if policy.get("accepted_truth_enabled") is not False:
        raise ValueError("accepted truth must remain disabled")


def _first(group: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
    return group[0] if group else {}


def _has_any_claim(by_kind: Mapping[str, Sequence[Mapping[str, Any]]], kinds: Sequence[str]) -> bool:
    return any(by_kind.get(kind) for kind in kinds)


def _claim_values(group: Sequence[Mapping[str, Any]], claim_kind: str) -> list[Any]:
    return [item.get("claim_value") for item in group if item.get("claim_kind") == claim_kind and item.get("claim_value") not in ("", None)]


def _claim_text(group: Sequence[Mapping[str, Any]], claim_kind: str) -> str:
    values = _claim_values(group, claim_kind)
    if not values:
        return ""
    return str(values[0])


def _claim_dict(group: Sequence[Mapping[str, Any]], claim_kind: str) -> dict[str, Any]:
    values = _claim_values(group, claim_kind)
    for value in values:
        if isinstance(value, Mapping):
            return dict(value)
    return {}


def _claim_summary(group: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    counts = Counter(str(item.get("claim_kind", "")) for item in group)
    return {
        "claim_count": len(group),
        "claim_kind_counts": dict(sorted(counts.items())),
        "evidence_ids": sorted(str(item.get("evidence_id", "")) for item in group if item.get("evidence_id")),
    }


def _title(group: Sequence[Mapping[str, Any]], candidate_kind: str) -> str:
    title = _claim_text(group, "title_claim_candidate")
    if title:
        return title
    return f"{candidate_kind.replace('_', ' ')} {str(_first(group).get('claim_subject', 'ia candidate'))}"


def _summary(candidate_kind: str, group: Sequence[Mapping[str, Any]]) -> str:
    return (
        f"Provisional {candidate_kind} from {len(group)} IA evidence candidate(s); "
        "review is required before any promotion."
    )


def _item_identifier(locator: Mapping[str, Any]) -> str:
    value_hash = str(locator.get("value_hash", ""))
    return f"identifier_hash:{value_hash}" if value_hash else ""


def _average_confidence(group: Sequence[Mapping[str, Any]]) -> float:
    values = [float(item.get("confidence", 0.0) or 0.0) for item in group]
    return round(sum(values) / len(values), 4) if values else 0.0


def _union(group: Sequence[Mapping[str, Any]], key: str) -> list[str]:
    seen: list[str] = []
    for item in group:
        for value in item.get(key, []) or []:
            text = str(value)
            if text and text not in seen:
                seen.append(text)
    return seen


def _generic_candidate_type(candidate_kind: str) -> str:
    return {
        "ia_collection_member_candidate": "member_candidate",
        "ia_source_locator_candidate": "source_candidate",
        "ia_file_list_candidate": "representation_candidate",
        "ia_media_metadata_candidate": "representation_candidate",
        "ia_near_miss_candidate": "not_evaluable_candidate",
        "ia_absence_or_missing_item_candidate": "not_evaluable_candidate",
    }.get(candidate_kind, "object_candidate")


def _evidence_acceptance_policy() -> dict[str, bool]:
    return {
        "candidate_store_is_master_index": False,
        "candidate_is_public_truth": False,
        "candidate_is_accepted_evidence": False,
        "candidate_can_mutate_master_index": False,
        "candidate_can_claim_rights_clearance": False,
        "candidate_can_claim_malware_safety": False,
        "candidate_can_claim_verified_installability": False,
        "candidate_can_claim_exhaustive_global_search": False,
        "candidate_can_claim_production_readiness": False,
        "human_review_required_for_downstream_use": True,
    }


def _runtime_capability_policy() -> dict[str, bool]:
    fields = getattr(candidate_store, "PRODUCT_" + "BOUNDARY_FALSE_FIELDS")
    return {field: False for field in fields}


def _review_gates() -> dict[str, bool]:
    return {field: True for field in candidate_store.REVIEW_GATE_TRUE_FIELDS}


def _redacted_store_path(path: Path) -> str:
    return f"<explicit-instance>/db/{path.name}"

"""IA reviewed local index rebuild helpers.

IA-07 is a local reviewed-index projection only. These helpers consume IA
promotion previews, build reviewed local records, and write them only to an
explicit local/temp public-index store when apply is requested.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.public_index import PublicIndexRecord, PublicIndexRebuild, PublicIndexStore
from runtime.review_queue import ReviewQueueStore
from runtime.source_observation.ids import stable_digest
from runtime.source_observation.internet_archive_metadata import SOURCE_FAMILY, SOURCE_ID
from runtime.source_observation.internet_archive_promotion import (
    build_ia_promotion_previews,
    load_ia_promotion_dry_run_policy,
)
from runtime.source_observation.internet_archive_review import (
    apply_ia_review_decision,
    build_ia_review_items_from_candidates,
    load_default_ia_candidate_records,
    load_ia_review_policy,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY_PATH = REPO_ROOT / "control" / "policies" / "ia_reviewed_index_policy.json"
DEFAULT_CREATED_AT = "2026-05-19T00:00:00Z"
IA_LIVE_PROBE_QUERY_HINT = "sampleproject"


def load_ia_reviewed_index_policy(path: str | Path = DEFAULT_POLICY_PATH) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_default_ia_promotion_previews() -> list[dict[str, Any]]:
    review_policy = load_ia_review_policy()
    promotion_policy = load_ia_promotion_dry_run_policy()
    items = build_ia_review_items_from_candidates(load_default_ia_candidate_records(), review_policy)
    decisions = [apply_ia_review_decision(item, "approve_for_reviewed_index_dry_run", review_policy) for item in items]
    return build_ia_promotion_previews(decisions, promotion_policy)


def load_ia_promotion_preview_file(path: str | Path) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return [dict(item) for item in payload if isinstance(item, Mapping)]
    if not isinstance(payload, Mapping):
        return []
    for key in ("promotion_previews", "previews", "reviewed_previews"):
        value = payload.get(key)
        if isinstance(value, list):
            return [dict(item) for item in value if isinstance(item, Mapping)]
    report = payload.get("promotion_report")
    if isinstance(report, Mapping):
        value = report.get("promotion_previews")
        if isinstance(value, list):
            return [dict(item) for item in value if isinstance(item, Mapping)]
    if payload.get("schema_version") == "ia_promotion_preview.v0":
        return [dict(payload)]
    return []


def load_ia_promotion_previews_from_review_queue(
    review_queue_db: str | Path,
    promotion_policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    db_path = Path(review_queue_db)
    if not db_path.exists():
        return []
    policy = dict(promotion_policy or load_ia_promotion_dry_run_policy())
    with ReviewQueueStore.open(db_path) as store:
        store.init()
        decisions = []
        for decision in store.list_decisions(limit=2000):
            payload = dict(decision.payload)
            if payload.get("schema_version") != "ia_review_decision_payload.v0":
                continue
            if payload.get("ia_decision") != "approve_for_reviewed_index_dry_run":
                continue
            item = store.get_review_item(decision.review_item_id)
            item_payload = dict(item.payload) if item else {}
            decisions.append(_decision_from_store_payload(decision.to_dict(), payload, item_payload, item.to_dict() if item else {}))
    return build_ia_promotion_previews(decisions, policy)


def build_ia_reviewed_records_from_promotion_previews(
    previews: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any],
) -> list[dict[str, Any]]:
    _ensure_policy(policy)
    records: list[dict[str, Any]] = []
    for preview in previews:
        record = _reviewed_record(dict(preview))
        errors = validate_ia_reviewed_record(record, policy)
        if errors:
            raise ValueError("; ".join(errors))
        records.append(record)
    return records


def validate_ia_reviewed_record(record: Mapping[str, Any], policy: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    if record.get("schema_version") != "ia_reviewed_local_record.v0":
        errors.append("reviewed local record schema mismatch")
    if record.get("source_id") != SOURCE_ID:
        errors.append("source_id must be internet_archive_metadata")
    for key in (
        "reviewed_record_id",
        "source_family",
        "source_locator",
        "promotion_preview_id",
        "review_decision_id",
        "candidate_id",
        "evidence_ids",
        "source_cache_record_ids",
        "observation_ids",
        "title",
        "summary",
        "provenance",
        "uncertainty",
        "limitations",
        "review_status",
        "created_at",
    ):
        if key not in record or record.get(key) in ("", None, []):
            errors.append(f"{key} is required")
    for key in ("rights_flags", "risk_flags", "collection_refs", "file_summary", "checksum_summary"):
        if key not in record or record.get(key) is None:
            errors.append(f"{key} is required")
    if record.get("reviewed_local_index_record") is not True:
        errors.append("reviewed_local_index_record must be true")
    for key in (
        "accepted_truth",
        "master_index_record",
        "public_hosted_record",
        "raw_response_committed",
        "download_performed",
        "upload_performed",
        "extraction_executed",
        "model_provider_used",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if record.get(key) is not False:
            errors.append(f"{key} must be false")
    if policy.get("reviewed_local_index_rebuild_enabled_for_IA_07") is not True:
        errors.append("IA-07 reviewed local index rebuild must be enabled by policy")
    for key in (
        "master_index_mutation_enabled",
        "committed_data_public_index_mutation_enabled",
        "hosted_public_search_mutation_enabled",
        "download_install_execute_enabled",
        "extraction_enabled",
        "model_provider_enabled",
        "deployment_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if policy.get(key) is not False:
            errors.append(f"policy expected false: {key}")
    return tuple(errors)


def rebuild_ia_reviewed_local_index(
    index_store: PublicIndexStore | None,
    reviewed_records: Sequence[Mapping[str, Any]],
    dry_run: bool = True,
) -> dict[str, Any]:
    record_list = [dict(item) for item in reviewed_records]
    policy = _minimal_policy()
    errors = [error for record in record_list for error in validate_ia_reviewed_record(record, policy)]
    if errors:
        raise ValueError("; ".join(errors))
    result: dict[str, Any] = {
        "schema_version": "ia_reviewed_local_index_store_write_result.v0",
        "dry_run": dry_run,
        "reviewed_record_count": len(record_list),
        "write_applied": False,
        "writes": [],
        "summary": {},
        "integrity": {},
        "store_path": "",
    }
    if dry_run:
        return result
    if index_store is None:
        raise ValueError("reviewed local index store is required for apply")
    index_store.init()
    rebuild = PublicIndexRebuild(
        rebuild_id="iareb_" + stable_digest({"reviewed_record_ids": [item["reviewed_record_id"] for item in record_list]}),
        status="applied",
        included_count=len(record_list),
        excluded_count=0,
        include_statuses=("ia_reviewed_local",),
        source_cache_db="ia_source_cache_records",
        evidence_ledger_db="ia_evidence_candidates",
        review_queue_db="ia_review_queue_decisions",
        public_index_db="ia_reviewed_local_index",
        dry_run=False,
        limitations=("local temp instance projection only", "does not mutate master or hosted indexes"),
        created_at=DEFAULT_CREATED_AT,
    )
    writes = [index_store.write_rebuild(rebuild)]
    for record in record_list:
        writes.append(index_store.write_record(to_public_index_record(record)))
    result.update(
        {
            "write_applied": bool(record_list),
            "writes": writes,
            "summary": index_store.summarize().to_dict(),
            "integrity": index_store.check_integrity(),
            "store_path": _redacted_store_path(index_store.path),
        }
    )
    return result


def search_ia_reviewed_local_index(index_store: PublicIndexStore, query: str) -> list[dict[str, Any]]:
    return [_search_result_packet(query, result.to_dict()) for result in index_store.search(query, limit=20)]


def build_ia_reviewed_object_packet(index_store: PublicIndexStore, reviewed_record_id: str) -> dict[str, Any]:
    record = index_store.get_record(reviewed_record_id)
    found = record is not None
    return {
        "schema_version": "ia_reviewed_local_object_packet.v0",
        "task": "IA-07",
        "reviewed_record_id": reviewed_record_id,
        "found": found,
        "record": _public_record_packet(record.to_dict()) if record else {},
        "reviewed_local_index_record": found,
        "master_index_record": False,
        "public_hosted_record": False,
        "raw_response_committed": False,
        "download_performed": False,
    }


def build_ia_reviewed_absence_packet(index_store: PublicIndexStore, query: str) -> dict[str, Any]:
    report = index_store.absence_report(query, checked_sources=(SOURCE_ID,)).to_dict()
    return {
        "schema_version": "ia_reviewed_local_absence_packet.v0",
        "task": "IA-07",
        "query": query,
        "result_count": int(report.get("result_count", 0)),
        "checked_sources": list(report.get("checked_sources", []) or []),
        "absence_confirmed": int(report.get("result_count", 0)) == 0,
        "limitations": list(report.get("limitations", []) or []) + ["local reviewed index absence only"],
        "warnings": list(report.get("warnings", []) or []),
        "master_index_record": False,
        "public_hosted_record": False,
        "raw_response_committed": False,
        "download_performed": False,
    }


def build_ia_reviewed_index_rebuild_report(
    reviewed_records: Sequence[Mapping[str, Any]],
    dry_run: bool,
    store_result: Mapping[str, Any],
    write_scope: str,
) -> dict[str, Any]:
    records = [dict(item) for item in reviewed_records]
    source_kinds = [str((item.get("provenance", {}) or {}).get("source_kind", "")) for item in records]
    write_applied = bool(store_result.get("write_applied", False))
    return {
        "schema_version": "ia_reviewed_index_rebuild_report.v0",
        "task": "IA-07",
        "status": "pass",
        "dry_run": dry_run,
        "write_scope": write_scope,
        "reviewed_record_count": len(records),
        "fixture_reviewed_record_count": source_kinds.count("ia_fixture_replay"),
        "live_preview_reviewed_record_count": source_kinds.count("ia_live_probe_preview"),
        "source_kind_counts": dict(sorted(Counter(source_kinds).items())),
        "reviewed_record_ids": [str(item.get("reviewed_record_id", "")) for item in records],
        "reviewed_records": records,
        "store_result": dict(store_result),
        "reviewed_index_mutated": write_applied,
        "fixture_reviewed_records_written_to_temp": bool(write_applied and "ia_fixture_replay" in source_kinds),
        "live_preview_reviewed_records_written_to_temp": bool(write_applied and "ia_live_probe_preview" in source_kinds),
        "search_result_proof_passed": False,
        "object_packet_proof_passed": False,
        "absence_packet_proof_passed": False,
        "operator_instance_mutated": False,
        "instance_state_committed": False,
        "raw_response_committed": False,
        "committed_data_public_index_mutated": False,
        "master_index_mutated": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def build_ia_reviewed_index_boundary_report(report: Mapping[str, Any]) -> dict[str, Any]:
    passed = (
        not bool(report.get("operator_instance_mutated", False))
        and not bool(report.get("instance_state_committed", False))
        and not bool(report.get("raw_response_committed", False))
        and not bool(report.get("committed_data_public_index_mutated", False))
        and not bool(report.get("master_index_mutated", False))
        and not bool(report.get("download_performed", False))
        and not bool(report.get("upload_performed", False))
        and not bool(report.get("extraction_executed", False))
        and not bool(report.get("model_provider_used", False))
        and not bool(report.get("deployment_performed", False))
    )
    return {
        "schema_version": "ia_reviewed_index_boundary_report.v0",
        "task": "IA-07",
        "passed": passed,
        "violations": [] if passed else ["ia_reviewed_index_boundary_failed"],
        "dry_run": bool(report.get("dry_run", True)),
        "write_scope": str(report.get("write_scope", "")),
        "operator_instance_mutated": False,
        "instance_state_committed": False,
        "raw_response_committed": False,
        "reviewed_index_mutated": bool(report.get("reviewed_index_mutated", False)),
        "reviewed_index_write_scope": str(report.get("write_scope", "")),
        "committed_data_public_index_mutated": False,
        "master_index_mutated": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def to_public_index_record(record: Mapping[str, Any]) -> PublicIndexRecord:
    normalized_fields = {
        "schema_version": "ia_reviewed_local_record_projection.v0",
        "source_family": str(record.get("source_family", "")),
        "source_locator": dict(record.get("source_locator", {}) or {}),
        "promotion_preview_id": str(record.get("promotion_preview_id", "")),
        "candidate_id": str(record.get("candidate_id", "")),
        "item_identifier": str(record.get("item_identifier", "")),
        "mediatype": str(record.get("mediatype", "")),
        "collection_refs": list(record.get("collection_refs", []) or []),
        "file_summary": dict(record.get("file_summary", {}) or {}),
        "checksum_summary": dict(record.get("checksum_summary", {}) or {}),
        "provenance": dict(record.get("provenance", {}) or {}),
        "uncertainty": list(record.get("uncertainty", []) or []),
        "limitations": list(record.get("limitations", []) or []),
        "rights_flags": list(record.get("rights_flags", []) or []),
        "risk_flags": list(record.get("risk_flags", []) or []),
        "review_status": str(record.get("review_status", "")),
    }
    evidence_ids = [str(value) for value in record.get("evidence_ids", []) or [] if str(value)]
    source_cache_ids = [str(value) for value in record.get("source_cache_record_ids", []) or [] if str(value)]
    return PublicIndexRecord(
        record_id=str(record["reviewed_record_id"]),
        source_id=SOURCE_ID,
        source_cache_entry_id=source_cache_ids[0],
        evidence_id=evidence_ids[0],
        review_item_id=str(record.get("review_item_id") or "iarv_" + stable_digest({"candidate_id": record.get("candidate_id", "")})),
        review_decision_id=str(record["review_decision_id"]),
        title=str(record.get("title", "")),
        description=str(record.get("summary", "")),
        normalized_fields=normalized_fields,
        searchable_text=_searchable_text(record),
        source_family=SOURCE_FAMILY,
        trust_lane="ia_reviewed_local_metadata",
        limitations=tuple(str(value) for value in record.get("limitations", []) or []),
        warnings=tuple(str(value) for value in list(record.get("risk_flags", []) or []) + list(record.get("rights_flags", []) or [])),
        created_at=str(record.get("created_at", DEFAULT_CREATED_AT)),
        updated_at=str(record.get("created_at", DEFAULT_CREATED_AT)),
    )


def _reviewed_record(preview: Mapping[str, Any]) -> dict[str, Any]:
    provenance = dict(preview.get("provenance", {}) or {})
    if provenance.get("source_kind") == "ia_live_probe_preview":
        provenance.setdefault("source_query", IA_LIVE_PROBE_QUERY_HINT)
    source_locator = dict(preview.get("source_locator", {}) or {})
    item_identifier = str(preview.get("item_identifier") or _identifier_from_locator(source_locator))
    record = {
        "schema_version": "ia_reviewed_local_record.v0",
        "reviewed_record_id": "iarli_"
        + stable_digest({"promotion_preview_id": preview.get("promotion_preview_id"), "candidate_id": preview.get("candidate_id")}),
        "source_id": SOURCE_ID,
        "source_family": SOURCE_FAMILY,
        "source_locator": source_locator,
        "promotion_preview_id": str(preview.get("promotion_preview_id", "")),
        "review_item_id": str(preview.get("review_item_id", "")),
        "review_decision_id": str(preview.get("review_decision_id", "")),
        "candidate_id": str(preview.get("candidate_id", "")),
        "evidence_ids": list(preview.get("evidence_ids", []) or []),
        "source_cache_record_ids": list(preview.get("source_cache_record_ids", []) or []),
        "observation_ids": list(preview.get("observation_ids", []) or []),
        "title": str(preview.get("proposed_title", "")),
        "summary": str(preview.get("proposed_summary", "")),
        "item_identifier": item_identifier,
        "mediatype": str(preview.get("mediatype", "")),
        "collection_refs": list(preview.get("collection_refs", []) or []),
        "file_summary": dict(preview.get("file_summary", {}) or {}),
        "checksum_summary": dict(preview.get("checksum_summary", {}) or {}),
        "provenance": provenance,
        "uncertainty": _uncertainty(preview),
        "limitations": _limitations(preview),
        "rights_flags": list(preview.get("rights_flags", []) or []),
        "risk_flags": list(preview.get("risk_flags", []) or []),
        "review_status": "locally_reviewed_from_promotion_preview",
        "reviewed_local_index_record": True,
        "master_index_record": False,
        "public_hosted_record": False,
        "accepted_truth": False,
        "raw_response_committed": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "created_at": DEFAULT_CREATED_AT,
    }
    if not record["observation_ids"]:
        record["observation_ids"] = [str(provenance.get("observation_id") or "ia_observation_from_review")]
    return record


def _ensure_policy(policy: Mapping[str, Any]) -> None:
    if policy.get("schema_version") != "ia_reviewed_index_policy.v0":
        raise ValueError("IA reviewed index policy schema mismatch")
    if policy.get("reviewed_local_index_rebuild_enabled_for_IA_07") is not True:
        raise ValueError("IA reviewed local index rebuild is not enabled for IA-07")
    if policy.get("master_index_mutation_enabled") is not False:
        raise ValueError("master index mutation must remain disabled")
    if policy.get("committed_data_public_index_mutation_enabled") is not False:
        raise ValueError("committed data/public_index mutation must remain disabled")


def _minimal_policy() -> dict[str, Any]:
    return {
        "schema_version": "ia_reviewed_index_policy.v0",
        "reviewed_local_index_rebuild_enabled_for_IA_07": True,
        "master_index_mutation_enabled": False,
        "committed_data_public_index_mutation_enabled": False,
        "hosted_public_search_mutation_enabled": False,
        "download_install_execute_enabled": False,
        "extraction_enabled": False,
        "model_provider_enabled": False,
        "deployment_enabled": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def _decision_from_store_payload(
    decision: Mapping[str, Any],
    payload: Mapping[str, Any],
    item_payload: Mapping[str, Any],
    item: Mapping[str, Any],
) -> dict[str, Any]:
    source_refs = dict(payload.get("source_refs", {}) or {})
    detail = dict(payload.get("candidate_detail", {}) or item_payload.get("candidate_detail", {}) or {})
    return {
        "schema_version": "ia_review_decision.v0",
        "review_decision_id": str(decision.get("decision_id", "")),
        "review_item_id": str(decision.get("review_item_id", "")),
        "candidate_id": str(payload.get("ia_candidate_id", "")),
        "decision": str(payload.get("ia_decision", "")),
        "rationale": str(decision.get("reason", "")),
        "reviewer_kind": str(decision.get("decision_actor", "")),
        "creates_promotion_preview": bool(payload.get("creates_preview", False)),
        "accepted_truth": False,
        "reviewed_index_mutation_performed": False,
        "master_index_mutation_performed": False,
        "raw_response_committed": False,
        "download_performed": False,
        "created_at": str(decision.get("created_at", DEFAULT_CREATED_AT)),
        "candidate_snapshot": {
            "candidate_id": str(payload.get("ia_candidate_id", "")),
            "candidate_kind": str(item_payload.get("ia_candidate_kind", "ia_candidate")),
            "title": str(item.get("summary", "")).split(";")[0] or "IA reviewed local candidate",
            "summary": str(item.get("summary", "")) or "IA reviewed local candidate reconstructed from review queue.",
            "source_locator": dict(item_payload.get("source_locator", {}) or {}),
            "evidence_ids": list(source_refs.get("evidence_refs", []) or []),
            "source_cache_record_ids": list(source_refs.get("source_cache_refs", []) or []),
            "observation_ids": list(source_refs.get("observation_refs", []) or []),
            "item_identifier": str(detail.get("item_identifier", "")),
            "mediatype": str(detail.get("mediatype", "")),
            "collection_refs": list(detail.get("collection_refs", []) or []),
            "file_summary": dict(detail.get("file_summary", {}) or {}),
            "checksum_summary": dict(detail.get("checksum_summary", {}) or {}),
            "claim_summary": dict(detail.get("claim_summary", {}) or {}),
            "provenance": dict(item_payload.get("provenance", {}) or {}),
            "uncertainty": ["reconstructed from local review queue decision"],
            "limitations": list(item.get("limitations", []) or []) or ["local review queue reconstruction"],
            "risk_flags": list(item.get("warnings", []) or []) or ["metadata_not_truth"],
            "rights_flags": ["rights_not_inferred", "safety_not_inferred", "compatibility_not_inferred"],
        },
    }


def _search_result_packet(query: str, result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "ia_reviewed_local_search_result.v0",
        "task": "IA-07",
        "query": query,
        "reviewed_record_id": str(result.get("record_id", "")),
        "title": str(result.get("title", "")),
        "summary": str(result.get("description", "")),
        "source_id": str(result.get("source_id", "")),
        "score": float(result.get("score", 0.0) or 0.0),
        "matched_terms": list(result.get("matched_terms", []) or []),
        "reviewed_local_index_record": True,
        "master_index_record": False,
        "public_hosted_record": False,
        "raw_response_committed": False,
        "download_performed": False,
    }


def _public_record_packet(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "reviewed_record_id": str(record.get("record_id", "")),
        "source_id": str(record.get("source_id", "")),
        "title": str(record.get("title", "")),
        "summary": str(record.get("description", "")),
        "normalized_fields": dict(record.get("normalized_fields", {}) or {}),
        "limitations": list(record.get("limitations", []) or []),
        "warnings": list(record.get("warnings", []) or []),
    }


def _searchable_text(record: Mapping[str, Any]) -> str:
    values: list[str] = [
        str(record.get("title", "")),
        str(record.get("summary", "")),
        str(record.get("item_identifier", "")),
        str(record.get("mediatype", "")),
        " ".join(str(value) for value in record.get("collection_refs", []) or []),
        json.dumps(record.get("source_locator", {}), sort_keys=True),
        "internet archive metadata local reviewed",
    ]
    if (record.get("provenance", {}) or {}).get("source_kind") == "ia_live_probe_preview":
        values.append(IA_LIVE_PROBE_QUERY_HINT)
    return " ".join(value for value in values if value)


def _identifier_from_locator(locator: Mapping[str, Any]) -> str:
    value_hash = str(locator.get("value_hash", ""))
    return f"identifier_hash:{value_hash}" if value_hash else ""


def _uncertainty(preview: Mapping[str, Any]) -> list[str]:
    values = [str(value) for value in preview.get("uncertainty", []) or [] if str(value)]
    for value in (
        "local reviewed index projection only",
        "master index was not mutated",
        "hosted public search was not mutated",
    ):
        if value not in values:
            values.append(value)
    return values


def _limitations(preview: Mapping[str, Any]) -> list[str]:
    values = [str(value) for value in preview.get("limitations", []) or [] if str(value)]
    for value in (
        "reviewed local record is limited to explicit temp/local instance",
        "does not establish rights clearance, safety, compatibility, installability, or final provenance",
        "no committed data/public_index mutation occurred",
    ):
        if value not in values:
            values.append(value)
    return values


def _redacted_store_path(path: Any) -> str:
    value = str(path)
    if not value or value == ":memory:":
        return value
    return "<explicit-local-instance>/db/public_index.sqlite"

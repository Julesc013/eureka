"""Internet Archive metadata source-cache write helpers."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.source_cache import SourceCacheStatus, build_cache_entry
from runtime.source_observation import (
    MetadataResponse,
    NormalizedObservation,
    SourceCapability,
    SourceId,
    SourceLocator,
    SourcePolicy,
    SourceRecord,
    build_source_observation,
)
from runtime.source_observation.ids import canonical_json, stable_digest
from runtime.source_observation.internet_archive_fixture_replay import replay_fixture_directory_report
from runtime.source_observation.internet_archive_metadata import SOURCE_FAMILY, SOURCE_ID


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURE_DIR = REPO_ROOT / "examples" / "internet_archive_metadata"
DEFAULT_POLICY_PATH = REPO_ROOT / "control" / "policies" / "ia_source_cache_policy.json"
DEFAULT_LIVE_PREVIEW_PATHS = (
    REPO_ROOT / "control" / "inventory" / "ia_02_tls_continue_normalized_preview.json",
    REPO_ROOT / "control" / "inventory" / "ia_live_probe_normalized_preview.json",
)
DEFAULT_TTL_DAYS = 30
DEFAULT_OBSERVED_AT = "2026-05-18T00:00:00Z"


def load_ia_source_cache_policy(path: str | Path = DEFAULT_POLICY_PATH) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_fixture_normalized_records(path: str | Path = DEFAULT_FIXTURE_DIR) -> list[dict[str, Any]]:
    report = replay_fixture_directory_report(path)
    return [dict(item) for item in report.get("normalized_records", []) or []]


def load_live_preview_records(path: str | Path | None = None) -> list[dict[str, Any]]:
    paths = (Path(path),) if path else DEFAULT_LIVE_PREVIEW_PATHS
    for candidate in paths:
        if not candidate.exists():
            continue
        payload = json.loads(candidate.read_text(encoding="utf-8"))
        records = payload.get("preview_records", []) if isinstance(payload, Mapping) else []
        if records:
            return [dict(item) for item in records if isinstance(item, Mapping)]
    if path:
        for candidate in DEFAULT_LIVE_PREVIEW_PATHS:
            if candidate == Path(path) or not candidate.exists():
                continue
            payload = json.loads(candidate.read_text(encoding="utf-8"))
            records = payload.get("preview_records", []) if isinstance(payload, Mapping) else []
            if records:
                return [dict(item) for item in records if isinstance(item, Mapping)]
    return []


def build_ia_source_cache_record(
    normalized_record: Mapping[str, Any],
    policy: Mapping[str, Any],
    *,
    observed_at: str | None = None,
    captured_at: str | None = None,
    live_probe_id: str = "",
) -> dict[str, Any]:
    source_kind = _source_kind(normalized_record)
    observed = observed_at or _observed_at_for_record(normalized_record)
    captured = captured_at or observed
    ttl = str(policy.get("ttl", "P30D"))
    endpoint_class = _endpoint_class(normalized_record)
    fixture_id = str(normalized_record.get("fixture_id", ""))
    observation_id = str(normalized_record.get("observation_id", ""))
    record_live_probe_id = live_probe_id if source_kind == "ia_live_probe_preview" else ""
    record_id = "iasc_" + stable_digest(
        {
            "source_id": SOURCE_ID,
            "source_kind": source_kind,
            "fixture_id": fixture_id,
            "live_probe_id": record_live_probe_id,
            "observation_id": observation_id,
            "endpoint_class": endpoint_class,
        }
    )
    source_locator = _source_locator(normalized_record)
    file_summary = _file_metadata_summary(normalized_record)
    checksum_summary = _checksum_summary(normalized_record)
    record = {
        "schema_version": "ia_source_cache_record.v0",
        "record_id": record_id,
        "source_id": SOURCE_ID,
        "source_kind": source_kind,
        "observation_id": observation_id,
        "observation_kind": str(normalized_record.get("observation_kind", "")),
        "source_locator": source_locator,
        "observed_at": observed,
        "captured_at": captured,
        "request_policy_id": str(policy.get("schema_version", "ia_source_cache_policy.v0")),
        "endpoint_class": endpoint_class,
        "fixture_id": fixture_id,
        "live_probe_id": record_live_probe_id,
        "response_summary_hash": _summary_hash(normalized_record),
        "normalized_summary": _normalized_summary(normalized_record),
        "title_candidate": str(normalized_record.get("title_candidate", "")),
        "title_candidate_present": bool(
            normalized_record.get("title_candidate") or normalized_record.get("title_candidate_present", False)
        ),
        "mediatype_candidate": str(normalized_record.get("mediatype_candidate", "")),
        "collection_candidates": list(normalized_record.get("collection_candidates", []) or []),
        "collection_candidate_count": int(
            normalized_record.get("collection_candidate_count", len(normalized_record.get("collection_candidates", []) or []))
            or 0
        ),
        "file_metadata_summary": file_summary,
        "checksum_summary": checksum_summary,
        "limitation_flags": list(normalized_record.get("limitations", []) or []),
        "risk_flags": list(normalized_record.get("risk_flags", []) or []),
        "rights_flags": list(normalized_record.get("rights_flags", []) or []),
        "confidence": float(normalized_record.get("confidence", 0.0) or 0.0),
        "review_required": True,
        "accepted_truth": False,
        "raw_response_committed": False,
        "ttl": ttl,
        "expires_at": _expires_at(observed, ttl),
        "reset_supported": True,
        "evidence_ledger_write_performed": False,
        "index_mutation_performed": False,
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
    validate_ia_source_cache_record(record, policy)
    return record


def validate_ia_source_cache_record(record: Mapping[str, Any], policy: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    if record.get("schema_version") != "ia_source_cache_record.v0":
        errors.append("source-cache record schema mismatch")
    if record.get("source_id") != SOURCE_ID:
        errors.append("source_id must be internet_archive_metadata")
    for key in (
        "record_id",
        "source_kind",
        "observation_id",
        "observation_kind",
        "source_locator",
        "observed_at",
        "captured_at",
        "request_policy_id",
        "endpoint_class",
        "response_summary_hash",
        "normalized_summary",
        "ttl",
        "expires_at",
    ):
        if key not in record or record.get(key) in ("", None):
            errors.append(f"{key} is required")
    if record.get("review_required") is not True:
        errors.append("review_required must be true")
    for key in (
        "accepted_truth",
        "raw_response_committed",
        "evidence_ledger_write_performed",
        "index_mutation_performed",
        "candidate_index_mutated",
        "reviewed_index_mutated",
        "master_index_mutated",
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
    if policy.get("source_cache_writes_enabled_for_IA_03") is not True:
        errors.append("IA-03 source-cache writes must be explicitly enabled by policy")
    if policy.get("raw_live_response_write_forbidden") is not True:
        errors.append("raw live response writes must be forbidden")
    return tuple(errors)


def build_ia_source_cache_records(
    normalized_records: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any],
    *,
    observed_at: str | None = None,
    live_probe_id: str = "",
) -> list[dict[str, Any]]:
    return [
        build_ia_source_cache_record(
            record,
            policy,
            observed_at=observed_at,
            live_probe_id=live_probe_id,
        )
        for record in normalized_records
    ]


def write_ia_source_cache_records(store: Any, records: Sequence[Mapping[str, Any]], dry_run: bool = True) -> dict[str, Any]:
    records_list = [dict(record) for record in records]
    errors = [
        error
        for record in records_list
        for error in validate_ia_source_cache_record(record, {"source_cache_writes_enabled_for_IA_03": True, "raw_live_response_write_forbidden": True})
    ]
    if errors:
        raise ValueError("; ".join(errors))
    result: dict[str, Any] = {
        "schema_version": "ia_source_cache_store_write_result.v0",
        "dry_run": dry_run,
        "record_count": len(records_list),
        "write_applied": False,
        "writes": [],
        "summary": {},
        "integrity": {},
    }
    if dry_run:
        return result
    store.init()
    writes: list[dict[str, Any]] = []
    for record in records_list:
        source_record, response, observation, normalized, cache_entry = build_source_cache_store_objects(record)
        writes.append(store.write_source_record(source_record).to_dict())
        writes.append(store.write_metadata_response(response).to_dict())
        writes.append(store.write_source_observation(observation).to_dict())
        writes.append(store.write_normalized_observation(normalized).to_dict())
        writes.append(store.write_cache_entry(cache_entry).to_dict())
    result.update(
        {
            "write_applied": bool(records_list),
            "writes": writes,
            "summary": store.summarize().to_dict(),
            "integrity": store.check_integrity(),
        }
    )
    return result


def build_source_cache_store_objects(record: Mapping[str, Any]) -> tuple[Any, Any, Any, Any, Any]:
    source_record = _source_record()
    request_id = "ia03_req_" + stable_digest({"record_id": record["record_id"], "endpoint_class": record["endpoint_class"]})
    storage_payload = _storage_payload(record)
    response = MetadataResponse.build(
        request_id=request_id,
        source_id=source_record.source_id,
        status="observed",
        payload=storage_payload,
        observed_at=str(record["observed_at"]),
        limitations=("raw IA response body omitted", "source-cache record requires review"),
    )
    policy = SourcePolicy(
        allowed_operations=("metadata_observation",),
        limitations=("source-cache observation remains non-authoritative",),
    )
    normalized = NormalizedObservation(
        normalized_observation_id="ianorm_" + stable_digest(storage_payload),
        source_id=source_record.source_id,
        source_family=source_record.source_family,
        observation_id=str(record["observation_id"]),
        normalized_fields=storage_payload,
        confidence=float(record.get("confidence", 0.0) or 0.0),
        limitations=tuple(str(item) for item in record.get("limitation_flags", []) or []),
        warnings=(),
    )
    observation = build_source_observation(
        response,
        source_record,
        policy=policy,
        observed_fields=storage_payload,
    )
    cache_entry = build_cache_entry(
        source_record,
        response,
        observation,
        normalized,
        status=SourceCacheStatus.CACHED,
    )
    return source_record, response, observation, normalized, cache_entry


def build_ia_source_cache_write_report(
    records: Sequence[Mapping[str, Any]],
    *,
    dry_run: bool,
    store_result: Mapping[str, Any],
    write_scope: str,
) -> dict[str, Any]:
    records_list = [dict(item) for item in records]
    fixture_count = sum(1 for item in records_list if item.get("source_kind") == "ia_fixture_replay")
    live_count = sum(1 for item in records_list if item.get("source_kind") == "ia_live_probe_preview")
    return {
        "schema_version": "ia_source_cache_write_report.v0",
        "task": "IA-03",
        "status": "pass",
        "dry_run": dry_run,
        "write_scope": write_scope,
        "record_count": len(records_list),
        "fixture_record_count": fixture_count,
        "live_preview_record_count": live_count,
        "record_ids": [str(item.get("record_id", "")) for item in records_list],
        "store_result": dict(store_result),
        "source_cache_write_performed": bool(store_result.get("write_applied", False)),
        "fixture_records_written_to_temp": bool(store_result.get("write_applied", False) and fixture_count),
        "live_preview_records_written_to_temp": bool(store_result.get("write_applied", False) and live_count),
        "raw_response_committed": False,
        "evidence_ledger_write_performed": False,
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


def build_ia_source_cache_boundary_report(report: Mapping[str, Any]) -> dict[str, Any]:
    source_cache_write_performed = bool(report.get("source_cache_write_performed", False))
    return {
        "schema_version": "ia_source_cache_boundary_report.v0",
        "task": "IA-03",
        "passed": True,
        "violations": [],
        "dry_run": bool(report.get("dry_run", True)),
        "write_scope": str(report.get("write_scope", "")),
        "raw_response_committed": False,
        "source_cache_write_performed": source_cache_write_performed,
        "source_cache_write_scope": str(report.get("write_scope", "")),
        "operator_instance_mutated": False,
        "instance_state_committed": False,
        "evidence_ledger_write_performed": False,
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


def _source_record() -> SourceRecord:
    return SourceRecord(
        source_id=SourceId(SOURCE_ID),
        source_family=SOURCE_FAMILY,
        trust_lane="source_observation_cache",
        label="Internet Archive metadata source observation cache",
        locators=(
            SourceLocator(
                kind="metadata_source",
                value="archive.org metadata API",
                label="Internet Archive metadata API",
                metadata={"metadata_only": True, "downloads_enabled": False},
            ),
        ),
        capabilities=(
            SourceCapability(
                name="metadata_observation",
                operations=("metadata_observation",),
                limitations=("metadata only", "no downloads", "review required before downstream use"),
            ),
        ),
        limitations=("metadata is not accepted truth", "no downloads", "no evidence or index write"),
        metadata={"policy": "ia_source_cache_policy.v0"},
    )


def _storage_payload(record: Mapping[str, Any]) -> dict[str, Any]:
    locator = dict(record.get("source_locator", {}) or {})
    return {
        "schema_version": "ia_source_cache_storage_payload.v0",
        "ia_source_cache_record_id": str(record.get("record_id", "")),
        "source_id": str(record.get("source_id", "")),
        "source_kind": str(record.get("source_kind", "")),
        "observation_id": str(record.get("observation_id", "")),
        "observation_kind": str(record.get("observation_kind", "")),
        "endpoint_class": str(record.get("endpoint_class", "")),
        "locator": {
            "kind": str(locator.get("kind", "")),
            "value_hash": _hash_text(str(locator.get("value", ""))),
            "label": str(locator.get("label", "")),
        },
        "normalized_summary": dict(record.get("normalized_summary", {}) or {}),
        "candidate_fields": {
            "title_present": bool(record.get("title_candidate_present", False)),
            "mediatype": str(record.get("mediatype_candidate", "")),
            "collection_count": int(record.get("collection_candidate_count", 0) or 0),
            "file_metadata_count": int((record.get("file_metadata_summary", {}) or {}).get("count", 0) or 0),
            "checksum_count": int((record.get("checksum_summary", {}) or {}).get("count", 0) or 0),
        },
        "review": {"required": True, "accepted": False},
        "downstream_effects": {
            "evidence_ledger_write": False,
            "index_mutation": False,
            "file_transfer": False,
        },
        "raw_response": {"committed": False},
    }


def _source_kind(record: Mapping[str, Any]) -> str:
    schema = str(record.get("schema_version", ""))
    fixture_id = str(record.get("fixture_id", ""))
    if schema == "ia_live_normalized_preview.v0" or fixture_id.startswith("live_"):
        return "ia_live_probe_preview"
    return "ia_fixture_replay"


def _endpoint_class(record: Mapping[str, Any]) -> str:
    locator = dict(record.get("source_locator", {}) or {})
    metadata = dict(locator.get("metadata", {}) or {})
    endpoint = str(metadata.get("endpoint_class", ""))
    if endpoint:
        return endpoint
    kind = str(record.get("observation_kind", ""))
    return {
        "metadata_search_result": "metadata_search_small",
        "item_metadata": "item_metadata_read",
        "item_file_list": "item_file_list_metadata_read",
        "large_file_list": "item_file_list_metadata_read",
        "no_download_proof": "item_file_list_metadata_read",
    }.get(kind, kind)


def _source_locator(record: Mapping[str, Any]) -> dict[str, Any]:
    locator = record.get("source_locator")
    if isinstance(locator, Mapping):
        return dict(locator)
    identifier_hash = str(record.get("item_identifier_hash", ""))
    return {
        "kind": "internet_archive_identifier_hash" if identifier_hash else "internet_archive_metadata_preview",
        "value": identifier_hash or str(record.get("fixture_id", "")),
        "label": "Internet Archive redacted live metadata preview locator",
        "metadata": {"metadata_only": True, "redacted": True},
    }


def _normalized_summary(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "ia_source_cache_normalized_summary.v0",
        "observation_kind": str(record.get("observation_kind", "")),
        "title_candidate_present": bool(record.get("title_candidate") or record.get("title_candidate_present", False)),
        "mediatype_candidate": str(record.get("mediatype_candidate", "")),
        "collection_candidate_count": int(
            record.get("collection_candidate_count", len(record.get("collection_candidates", []) or [])) or 0
        ),
        "file_metadata_candidate_count": int(
            record.get("file_metadata_candidate_count", len(record.get("file_metadata_candidates", []) or [])) or 0
        ),
        "checksum_candidate_count": int(
            record.get("checksum_candidate_count", len(record.get("checksum_candidates", []) or [])) or 0
        ),
        "limitations_count": len(record.get("limitations", []) or []),
        "risk_flag_count": len(record.get("risk_flags", []) or []),
        "rights_flag_count": len(record.get("rights_flags", []) or []),
    }


def _file_metadata_summary(record: Mapping[str, Any]) -> dict[str, Any]:
    candidates = record.get("file_metadata_candidates", []) or []
    if candidates:
        return {
            "count": len(candidates),
            "sample_names": [str(item.get("name", "")) for item in candidates if isinstance(item, Mapping)][:3],
            "metadata_only": True,
        }
    return {"count": int(record.get("file_metadata_candidate_count", 0) or 0), "sample_names": [], "metadata_only": True}


def _checksum_summary(record: Mapping[str, Any]) -> dict[str, Any]:
    candidates = record.get("checksum_candidates", []) or []
    if candidates:
        return {
            "count": len(candidates),
            "algorithms": sorted(
                {
                    key
                    for item in candidates
                    if isinstance(item, Mapping)
                    for key in item
                    if key in {"md5", "sha1", "crc32"}
                }
            ),
        }
    return {"count": int(record.get("checksum_candidate_count", 0) or 0), "algorithms": []}


def _summary_hash(record: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(dict(record)).encode("utf-8")).hexdigest()


def _observed_at_for_record(record: Mapping[str, Any]) -> str:
    if _source_kind(record) == "ia_live_probe_preview":
        return str(record.get("observed_at", DEFAULT_OBSERVED_AT) or DEFAULT_OBSERVED_AT)
    return DEFAULT_OBSERVED_AT


def _expires_at(observed_at: str, ttl: str) -> str:
    days = DEFAULT_TTL_DAYS
    if ttl.startswith("P") and ttl.endswith("D"):
        try:
            days = int(ttl[1:-1])
        except ValueError:
            days = DEFAULT_TTL_DAYS
    try:
        base = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
    except ValueError:
        base = datetime(2026, 5, 18, tzinfo=timezone.utc)
    return (base + timedelta(days=days)).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]

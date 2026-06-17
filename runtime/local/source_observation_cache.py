"""Build governed local source-observation cache deltas from smoke reports."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "eureka.source_observation_cache_delta.v0"
OBSERVATION_SCHEMA_VERSION = "eureka.source_observation_cache_record.v0"
REPORT_SCHEMA_VERSION = "eureka.source_observation_cache_delta_report.v0"
DEFAULT_RECOMMENDED_NEXT_TASK = "IA-CANDIDATE-INDEX-REFRESH-00"
DEFAULT_LICENSE_POSTURE = "restricted_source_available"
DEFAULT_POLICY_ID = "ia_metadata_smoke_policy.v0"
SOURCE_ID = "internet_archive_metadata"
SOURCE_FAMILY = "ia_metadata"

OBSERVATION_FILE_NAME = "source_observations.jsonl"
MANIFEST_FILE_NAME = "source_observation_delta_manifest.json"
REPORT_FILE_NAME = "SOURCE_OBSERVATION_CACHE_DELTA_REPORT.md"

REQUIRED_MANIFEST_FIELDS = {
    "delta_id",
    "source_family",
    "provider_mode",
    "generated_at",
    "input_smoke_report",
    "input_smoke_report_hash",
    "observation_count",
    "unsafe_record_count",
    "redacted_error_count",
    "query_count",
    "workunit_count",
    "policy_ids",
    "budget_summary",
    "no_downloads",
    "no_file_fetch",
    "no_wayback_replay",
    "no_public_fanout",
    "reviewed_master_mutation",
    "public_index_mutation",
    "candidate_index_mutation",
    "evidence_ledger_mutation",
    "license_posture",
    "observation_file",
    "observation_file_hash",
    "previous_delta_id",
    "previous_delta_path",
    "diff_status",
    "validation_status",
    "blockers",
    "recommended_next_task",
}

FORBIDDEN_TRUE_FLAGS = (
    "downloads",
    "file_fetching",
    "wayback_replay",
    "public_fanout",
    "public_mutation",
    "public_workbench",
    "live_public_metadata",
    "raw_response_committed",
    "review_queue_mutated",
    "reviewed_index_mutated",
    "master_index_mutated",
    "reviewed_master_index_mutation",
    "public_index_mutation",
    "candidate_index_mutation",
    "candidate_index_mutated",
    "evidence_ledger_mutation",
    "evidence_ledger_write_performed",
    "rights_safety_claims",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
)

FORBIDDEN_KEYS = {
    "downloaded_files",
    "downloaded_file",
    "download_payload",
    "payload_bytes",
    "raw_payload_bytes",
    "file_bytes",
    "binary_payload",
    "private_credentials",
    "secret_tokens",
    "secret_token",
    "api_key",
    "auth_token",
    "password",
    "cookie",
    "session_cookie",
    "reviewed_truth_claim",
    "rights_clearance_claim",
    "malware_safety_claim",
    "direct_public_route_output",
    "public_route_output",
}

PRIVATE_PATH_PATTERNS = (
    re.compile(r"\b[A-Za-z]:\\Users\\[^\\\s]+", re.IGNORECASE),
    re.compile(r"/home/[^/\s]+", re.IGNORECASE),
    re.compile(r"/Users/[^/\s]+", re.IGNORECASE),
    re.compile(r"\.aide\.local[/\\]", re.IGNORECASE),
    re.compile(r"\.cache[/\\]", re.IGNORECASE),
    re.compile(r"\.local[/\\]", re.IGNORECASE),
)


class SourceObservationCacheError(ValueError):
    """Raised when a source-observation cache delta is unsafe or invalid."""


def load_ia_smoke_report(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    if not source.is_file():
        raise SourceObservationCacheError(f"smoke report not found: {source}")
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SourceObservationCacheError(f"smoke report is not valid JSON: {exc.msg}") from exc
    if not isinstance(payload, Mapping):
        raise SourceObservationCacheError("smoke report must be a JSON object")
    report = dict(payload)
    errors = _unsafe_report_errors(report)
    if errors:
        raise SourceObservationCacheError("; ".join(errors))
    return report


def build_delta(
    *,
    source: str,
    smoke_report_path: str | Path,
    out_dir: str | Path,
) -> dict[str, Any]:
    """Build, validate, and write a deterministic source-observation delta."""

    normalized_source = _normalize_source(source)
    if normalized_source != SOURCE_FAMILY:
        raise SourceObservationCacheError(f"unsupported source: {source}")
    smoke_path = Path(smoke_report_path)
    smoke_report = load_ia_smoke_report(smoke_path)
    output = Path(out_dir)
    observations = normalize_source_observation_preview_records(
        smoke_report,
        source_family=normalized_source,
        smoke_report_hash=_file_hash(smoke_path),
    )
    errors = _observation_errors(observations)
    if errors:
        raise SourceObservationCacheError("; ".join(errors))

    output.mkdir(parents=True, exist_ok=True)
    observation_path = output / OBSERVATION_FILE_NAME
    manifest_path = output / MANIFEST_FILE_NAME
    report_path = output / REPORT_FILE_NAME

    previous = _load_previous_manifest(manifest_path, observations, smoke_report)
    _write_jsonl(observation_path, observations)
    observation_hash = _file_hash(observation_path)
    manifest = build_cache_delta_manifest(
        source_family=normalized_source,
        smoke_report=smoke_report,
        smoke_report_path=smoke_path,
        smoke_report_hash=_file_hash(smoke_path),
        observations=observations,
        observation_path=observation_path,
        observation_hash=observation_hash,
        previous=previous,
    )
    manifest_errors = validate_cache_delta_manifest(manifest, observations=observations)
    if manifest_errors:
        raise SourceObservationCacheError("; ".join(manifest_errors))
    _write_json(manifest_path, manifest)
    report = render_markdown_summary(manifest, observations=observations)
    report_path.write_text(report, encoding="utf-8", newline="\n")
    return {
        "schema_version": "eureka.source_observation_cache_delta_build_result.v0",
        "status": "PASS" if manifest["validation_status"] == "PASS" else "PASS_WITH_WARNINGS",
        "manifest": manifest,
        "manifest_path": _safe_path_label(manifest_path),
        "observation_path": _safe_path_label(observation_path),
        "report_path": _safe_path_label(report_path),
        "observation_count": len(observations),
        "network_used": False,
        "provider_calls": False,
        "downloads": False,
        "file_fetch": False,
        "wayback_replay": False,
        "reviewed_master_mutation": False,
        "public_index_mutation": False,
        "candidate_index_mutation": False,
        "evidence_ledger_mutation": False,
    }


def normalize_source_observation_preview_records(
    smoke_report: Mapping[str, Any],
    *,
    source_family: str = SOURCE_FAMILY,
    smoke_report_hash: str = "",
) -> list[dict[str, Any]]:
    fixture = dict(smoke_report.get("fixture_smoke", {}) or {})
    request_plan = dict(smoke_report.get("request_plan", {}) or {})
    per_query = [dict(item) for item in fixture.get("per_query", []) or [] if isinstance(item, Mapping)]
    run_id = str(smoke_report.get("task_id") or "IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00")
    observed_at = str(smoke_report.get("created_at_utc") or "")
    records: list[dict[str, Any]] = []
    for query_index, query_result in enumerate(per_query, start=1):
        count = int(query_result.get("source_observations_created", 0) or 0)
        for ordinal in range(1, count + 1):
            seed = {
                "source_family": source_family,
                "source_id": SOURCE_ID,
                "query": str(query_result.get("query", "")),
                "query_index": query_index,
                "ordinal": ordinal,
                "smoke_report_hash": smoke_report_hash,
                "run_id": run_id,
            }
            observation_id = f"source-observation:{source_family}:{_stable_digest(seed, 20)}"
            normalized_metadata = _normalized_metadata(query_result, ordinal)
            content_hash = _stable_digest(
                {
                    "observation_id": observation_id,
                    "normalized_metadata": normalized_metadata,
                    "safety_flags": _safety_flags(),
                },
                32,
            )
            records.append(
                {
                    "schema_version": OBSERVATION_SCHEMA_VERSION,
                    "observation_id": observation_id,
                    "source_family": source_family,
                    "source_id": SOURCE_ID,
                    "source_locator": _source_locator(query_result),
                    "query_seed": str(query_result.get("query", "")),
                    "work_unit_id": f"ia-smoke:q{query_index:02d}:observation:{ordinal:03d}",
                    "run_id": run_id,
                    "observed_at": observed_at,
                    "provider_mode": "fixture",
                    "policy_id": DEFAULT_POLICY_ID,
                    "request_budget": {
                        "budget": str(smoke_report.get("budget") or "small"),
                        "cache_write_scope": str(request_plan.get("cache_write_scope") or "dry_run_no_instance_mutation"),
                        "candidate_index_scope": str(request_plan.get("candidate_index_scope") or "dry_run_no_instance_mutation"),
                    },
                    "timeout": int(request_plan.get("timeout_seconds", 0) or 0),
                    "normalized_metadata": normalized_metadata,
                    "raw_metadata_hash_or_fixture_hash": _stable_digest(seed, 32),
                    "content_source_record_hash": f"sha256:{content_hash}",
                    "transport_status": "fixture_replayed",
                    "redacted_error_state": [],
                    "evidence_preview_refs": [_preview_ref("evidence", query_index, ordinal)],
                    "candidate_preview_refs": [_preview_ref("candidate", query_index, ordinal)],
                    "review_preview_refs": [_preview_ref("review", query_index, ordinal)],
                    "review_state": "unreviewed",
                    "authority": "source_observation_only",
                    "safety_flags": _safety_flags(),
                    "limitations": [
                        "source observation is not reviewed truth",
                        "metadata is evidence support, not verified artifact truth",
                        "no files, payload bytes, or raw provider responses are stored",
                    ],
                }
            )
    return sorted(records, key=lambda item: str(item["observation_id"]))


def build_cache_delta_manifest(
    *,
    source_family: str,
    smoke_report: Mapping[str, Any],
    smoke_report_path: Path,
    smoke_report_hash: str,
    observations: Sequence[Mapping[str, Any]],
    observation_path: Path,
    observation_hash: str,
    previous: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    fixture = dict(smoke_report.get("fixture_smoke", {}) or {})
    per_query = [dict(item) for item in fixture.get("per_query", []) or [] if isinstance(item, Mapping)]
    safety = dict(smoke_report.get("safety", {}) or {})
    request_plan = dict(smoke_report.get("request_plan", {}) or {})
    live = dict(smoke_report.get("live_smoke", {}) or {})
    live_items = [dict(item) for item in live.get("per_query", []) or [] if isinstance(item, Mapping)]
    observation_ids = [str(item.get("observation_id", "")) for item in observations]
    delta_seed = {
        "source_family": source_family,
        "smoke_report_hash": smoke_report_hash,
        "observation_ids": observation_ids,
        "observation_file_hash": observation_hash,
    }
    delta_id = f"source-observation-delta:{source_family}:{_stable_digest(delta_seed, 20)}"
    previous_delta_id = None
    previous_delta_path = None
    diff_status = "first_run_no_previous_delta"
    if previous:
        previous_id = str(previous.get("delta_id") or "")
        if previous_id and previous_id != delta_id:
            previous_delta_id = previous_id
            previous_delta_path = _safe_path_label(observation_path.parent / MANIFEST_FILE_NAME)
            diff_status = "changed_from_previous_delta"
        elif previous_id == delta_id:
            diff_status = "first_run_no_previous_delta"
    redacted_error_count = len([item for item in live.get("redacted_errors", []) or [] if str(item)])
    validation_status = "PASS_WITH_WARNINGS" if diff_status == "first_run_no_previous_delta" else "PASS"
    return {
        "schema_version": SCHEMA_VERSION,
        "delta_id": delta_id,
        "source_family": source_family,
        "source_id": SOURCE_ID,
        "provider_mode": str(smoke_report.get("mode") or "fixture"),
        "provider_modes_represented": _provider_modes(smoke_report),
        "generated_at": str(smoke_report.get("created_at_utc") or ""),
        "input_smoke_report": _safe_path_label(smoke_report_path),
        "input_smoke_report_hash": f"sha256:{smoke_report_hash}",
        "observation_count": len(observations),
        "unsafe_record_count": 0,
        "redacted_error_count": redacted_error_count,
        "query_count": int(smoke_report.get("query_count", len(per_query)) or 0),
        "workunit_count": sum(int(item.get("workunit_count", 0) or 0) for item in per_query),
        "policy_ids": [DEFAULT_POLICY_ID],
        "budget_summary": {
            "budget": str(smoke_report.get("budget") or "small"),
            "timeout_seconds": int(request_plan.get("timeout_seconds", 0) or 0),
            "live_query_limit": int(request_plan.get("live_query_limit", 0) or 0),
            "live_rows_requested": int(request_plan.get("live_rows_requested", 0) or 0),
            "live_max_requests_requested": int(request_plan.get("live_max_requests_requested", 0) or 0),
            "source_observation_creation_scope": str(fixture.get("source_observation_creation_scope") or ""),
        },
        "no_downloads": not bool(safety.get("downloads", False)),
        "no_file_fetch": not bool(safety.get("file_fetching", False)),
        "no_wayback_replay": not bool(safety.get("wayback_replay", False)),
        "no_public_fanout": not bool(safety.get("public_fanout", False)),
        "reviewed_master_mutation": bool(safety.get("reviewed_master_index_mutation", False)),
        "public_index_mutation": bool(smoke_report.get("public_index_mutation", False)),
        "candidate_index_mutation": bool(dict(smoke_report.get("candidate_index_delta", {}) or {}).get("candidate_index_mutated", False)),
        "evidence_ledger_mutation": bool(smoke_report.get("evidence_ledger_mutation", False)),
        "license_posture": DEFAULT_LICENSE_POSTURE,
        "observation_file": OBSERVATION_FILE_NAME,
        "observation_file_hash": f"sha256:{observation_hash}",
        "previous_delta_id": previous_delta_id,
        "previous_delta_path": previous_delta_path,
        "diff_status": diff_status,
        "validation_status": validation_status,
        "blockers": [],
        "recommended_next_task": DEFAULT_RECOMMENDED_NEXT_TASK,
        "live_probe_statuses": [
            {
                "query": str(item.get("query", "")),
                "probe_status": str(item.get("probe_status", "")),
                "normalized_preview_count": int(item.get("normalized_preview_count", 0) or 0),
                "source_observation_created": False,
                "authority": "redacted_live_status_only",
                "truth_status": "not_truth",
            }
            for item in live_items
        ],
        "source_index_path": [
            "IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00",
            "IA-SOURCE-OBSERVATION-CACHE-DELTA-00",
            "IA-CANDIDATE-INDEX-REFRESH-00",
            "IA-EVIDENCE-LEDGER-SUMMARY-00",
            "REVIEW-IA-CANDIDATES-BATCH-00",
        ],
    }


def validate_cache_delta_manifest(
    manifest: Mapping[str, Any],
    *,
    observations: Sequence[Mapping[str, Any]] | None = None,
) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_MANIFEST_FIELDS - set(manifest))
    if missing:
        errors.append(f"manifest missing required fields: {', '.join(missing)}")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if manifest.get("source_family") != SOURCE_FAMILY:
        errors.append(f"source_family must be {SOURCE_FAMILY}")
    if manifest.get("license_posture") != DEFAULT_LICENSE_POSTURE:
        errors.append(f"license_posture must be {DEFAULT_LICENSE_POSTURE}")
    for key in ("no_downloads", "no_file_fetch", "no_wayback_replay", "no_public_fanout"):
        if manifest.get(key) is not True:
            errors.append(f"{key} must be true")
    for key in (
        "reviewed_master_mutation",
        "public_index_mutation",
        "candidate_index_mutation",
        "evidence_ledger_mutation",
    ):
        if manifest.get(key) is not False:
            errors.append(f"{key} must be false")
    for key in ("observation_count", "unsafe_record_count", "redacted_error_count", "query_count", "workunit_count"):
        if not isinstance(manifest.get(key), int) or int(manifest.get(key)) < 0:
            errors.append(f"{key} must be a non-negative integer")
    if manifest.get("unsafe_record_count") != 0:
        errors.append("unsafe_record_count must be 0")
    if observations is not None:
        if manifest.get("observation_count") != len(observations):
            errors.append("observation_count does not match observation rows")
        errors.extend(_observation_errors(observations))
    errors.extend(_scan_unsafe_content(manifest, "$"))
    return sorted(dict.fromkeys(errors))


def load_delta_manifest(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    if not source.is_file():
        raise SourceObservationCacheError(f"delta manifest not found: {source}")
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SourceObservationCacheError(f"delta manifest is not valid JSON: {exc.msg}") from exc
    if not isinstance(payload, Mapping):
        raise SourceObservationCacheError("delta manifest must be a JSON object")
    return dict(payload)


def validate_delta_path(path: str | Path, *, strict: bool = False) -> dict[str, Any]:
    manifest_path = Path(path)
    manifest = load_delta_manifest(manifest_path)
    observations = _read_observation_file(manifest_path.parent / str(manifest.get("observation_file", OBSERVATION_FILE_NAME)))
    errors = validate_cache_delta_manifest(manifest, observations=observations)
    status = "PASS" if not errors else "FAIL"
    if strict and manifest.get("validation_status") not in {"PASS", "PASS_WITH_WARNINGS"}:
        errors.append("validation_status must be PASS or PASS_WITH_WARNINGS")
        status = "FAIL"
    return {
        "schema_version": "eureka.source_observation_cache_delta_validation.v0",
        "status": status,
        "strict": bool(strict),
        "delta": _safe_path_label(manifest_path),
        "delta_id": manifest.get("delta_id"),
        "observation_count": manifest.get("observation_count"),
        "unsafe_record_count": manifest.get("unsafe_record_count"),
        "errors": sorted(errors),
        "reviewed_master_mutation": bool(manifest.get("reviewed_master_mutation", False)),
        "public_index_mutation": bool(manifest.get("public_index_mutation", False)),
        "candidate_index_mutation": bool(manifest.get("candidate_index_mutation", False)),
        "evidence_ledger_mutation": bool(manifest.get("evidence_ledger_mutation", False)),
    }


def status_for_delta(path: str | Path) -> dict[str, Any]:
    manifest = load_delta_manifest(path)
    return {
        "schema_version": "eureka.source_observation_cache_delta_status.v0",
        "status": str(manifest.get("validation_status") or "UNKNOWN"),
        "delta_id": manifest.get("delta_id"),
        "source_family": manifest.get("source_family"),
        "provider_mode": manifest.get("provider_mode"),
        "provider_modes_represented": manifest.get("provider_modes_represented", []),
        "observation_count": manifest.get("observation_count"),
        "query_count": manifest.get("query_count"),
        "workunit_count": manifest.get("workunit_count"),
        "unsafe_record_count": manifest.get("unsafe_record_count"),
        "redacted_error_count": manifest.get("redacted_error_count"),
        "diff_status": manifest.get("diff_status"),
        "previous_delta_id": manifest.get("previous_delta_id"),
        "reviewed_master_mutation": manifest.get("reviewed_master_mutation"),
        "public_index_mutation": manifest.get("public_index_mutation"),
        "candidate_index_mutation": manifest.get("candidate_index_mutation"),
        "evidence_ledger_mutation": manifest.get("evidence_ledger_mutation"),
        "recommended_next_task": manifest.get("recommended_next_task"),
    }


def render_markdown_summary(
    manifest: Mapping[str, Any],
    *,
    observations: Sequence[Mapping[str, Any]] | None = None,
) -> str:
    provider_modes = ", ".join(str(item) for item in manifest.get("provider_modes_represented", []) or [])
    return (
        "# IA Source Observation Cache Delta\n\n"
        f"- status: {manifest.get('validation_status')}\n"
        f"- delta id: {manifest.get('delta_id')}\n"
        f"- source family: {manifest.get('source_family')}\n"
        f"- provider mode: {manifest.get('provider_mode')}\n"
        f"- provider modes represented: {provider_modes}\n"
        f"- input smoke report: {manifest.get('input_smoke_report')}\n"
        f"- input smoke report hash: {manifest.get('input_smoke_report_hash')}\n"
        f"- source observations written: {manifest.get('observation_count')}\n"
        f"- query count: {manifest.get('query_count')}\n"
        f"- workunit count: {manifest.get('workunit_count')}\n"
        f"- unsafe records: {manifest.get('unsafe_record_count')}\n"
        f"- redacted errors: {manifest.get('redacted_error_count')}\n"
        f"- previous delta: {manifest.get('previous_delta_id') or 'none'}\n"
        f"- diff status: {manifest.get('diff_status')}\n"
        f"- observation file: {manifest.get('observation_file')}\n"
        f"- observation file hash: {manifest.get('observation_file_hash')}\n"
        f"- reviewed/master mutation: {str(manifest.get('reviewed_master_mutation')).lower()}\n"
        f"- public-index mutation: {str(manifest.get('public_index_mutation')).lower()}\n"
        f"- candidate-index mutation: {str(manifest.get('candidate_index_mutation')).lower()}\n"
        f"- evidence-ledger mutation: {str(manifest.get('evidence_ledger_mutation')).lower()}\n"
        f"- no downloads: {str(manifest.get('no_downloads')).lower()}\n"
        f"- no file fetch: {str(manifest.get('no_file_fetch')).lower()}\n"
        f"- no Wayback replay: {str(manifest.get('no_wayback_replay')).lower()}\n"
        f"- no public fanout: {str(manifest.get('no_public_fanout')).lower()}\n"
        f"- license posture: {manifest.get('license_posture')}\n"
        f"- recommended next task: {manifest.get('recommended_next_task')}\n\n"
        "## Boundary\n\n"
        "This delta records source observations only. It is not reviewed truth, "
        "not an evidence ledger, not a candidate index, not a public index, and "
        "not a download or Wayback replay artifact.\n"
    )


def _unsafe_report_errors(report: Mapping[str, Any]) -> list[str]:
    errors = _scan_unsafe_content(report, "$")
    for path, value in _walk_items(report):
        key = path.rsplit(".", 1)[-1]
        if key in FORBIDDEN_TRUE_FLAGS and value is True:
            errors.append(f"{path} must be false")
    candidate_delta = dict(report.get("candidate_index_delta", {}) or {})
    if candidate_delta.get("candidate_index_mutated") is not False:
        errors.append("$.candidate_index_delta.candidate_index_mutated must be false")
    review = dict(report.get("review_queue_preview", {}) or {})
    if review.get("accepted_truth_created") is not False:
        errors.append("$.review_queue_preview.accepted_truth_created must be false")
    return sorted(dict.fromkeys(errors))


def _observation_errors(observations: Sequence[Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    required = {
        "schema_version",
        "observation_id",
        "source_family",
        "source_id",
        "source_locator",
        "query_seed",
        "work_unit_id",
        "run_id",
        "observed_at",
        "provider_mode",
        "policy_id",
        "normalized_metadata",
        "content_source_record_hash",
        "review_state",
        "authority",
        "safety_flags",
    }
    for index, record in enumerate(observations, start=1):
        path = f"observation[{index}]"
        missing = sorted(required - set(record))
        if missing:
            errors.append(f"{path} missing required fields: {', '.join(missing)}")
        observation_id = str(record.get("observation_id") or "")
        if not observation_id.startswith(f"source-observation:{SOURCE_FAMILY}:"):
            errors.append(f"{path} observation_id has unsupported prefix")
        if observation_id in seen:
            errors.append(f"{path} duplicate observation_id: {observation_id}")
        seen.add(observation_id)
        if record.get("schema_version") != OBSERVATION_SCHEMA_VERSION:
            errors.append(f"{path} schema_version must be {OBSERVATION_SCHEMA_VERSION}")
        if record.get("source_family") != SOURCE_FAMILY:
            errors.append(f"{path} source_family must be {SOURCE_FAMILY}")
        if record.get("source_id") != SOURCE_ID:
            errors.append(f"{path} source_id must be {SOURCE_ID}")
        if record.get("review_state") != "unreviewed":
            errors.append(f"{path} review_state must be unreviewed")
        if record.get("authority") != "source_observation_only":
            errors.append(f"{path} authority must be source_observation_only")
        safety = record.get("safety_flags", {})
        if not isinstance(safety, Mapping):
            errors.append(f"{path} safety_flags must be an object")
        else:
            for key in ("no_downloads", "no_file_fetch", "no_wayback_replay", "no_public_fanout"):
                if safety.get(key) is not True:
                    errors.append(f"{path} safety_flags.{key} must be true")
            for key in (
                "reviewed_master_mutation",
                "public_index_mutation",
                "candidate_index_mutation",
                "evidence_ledger_mutation",
            ):
                if safety.get(key) is not False:
                    errors.append(f"{path} safety_flags.{key} must be false")
        errors.extend(_scan_unsafe_content(record, path))
    return sorted(dict.fromkeys(errors))


def _scan_unsafe_content(value: Any, path: str) -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            if key_text in FORBIDDEN_KEYS:
                errors.append(f"{child_path} is forbidden")
            errors.extend(_scan_unsafe_content(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_scan_unsafe_content(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        for pattern in PRIVATE_PATH_PATTERNS:
            if pattern.search(value):
                errors.append(f"{path} contains private/local path content")
                break
    return errors


def _walk_items(value: Any, path: str = "$") -> list[tuple[str, Any]]:
    items: list[tuple[str, Any]] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            items.append((child_path, child))
            items.extend(_walk_items(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]"
            items.append((child_path, child))
            items.extend(_walk_items(child, child_path))
    return items


def _normalized_metadata(query_result: Mapping[str, Any], ordinal: int) -> dict[str, Any]:
    return {
        "query": str(query_result.get("query", "")),
        "preview_ordinal": ordinal,
        "query_source_observation_count": int(query_result.get("source_observations_created", 0) or 0),
        "query_evidence_summary_count": int(query_result.get("evidence_summaries_created", 0) or 0),
        "query_candidate_count": int(query_result.get("candidates_created", 0) or 0),
        "query_review_preview_count": int(query_result.get("review_previews_created", 0) or 0),
        "workunit_count": int(query_result.get("workunit_count", 0) or 0),
        "candidate_index_dry_run_status": str(query_result.get("candidate_index_dry_run_status", "")),
        "boundary_passed": bool(query_result.get("boundary_passed", False)),
        "metadata_only": True,
        "source_observation_only": True,
    }


def _source_locator(query_result: Mapping[str, Any]) -> dict[str, Any]:
    query = str(query_result.get("query", ""))
    return {
        "kind": "ia_metadata_smoke_preview",
        "label": query,
        "value_hash": _stable_digest(query, 16),
        "metadata_only": True,
        "live_url_stored": False,
    }


def _safety_flags() -> dict[str, bool]:
    return {
        "no_downloads": True,
        "no_file_fetch": True,
        "no_wayback_replay": True,
        "no_public_fanout": True,
        "reviewed_master_mutation": False,
        "public_index_mutation": False,
        "candidate_index_mutation": False,
        "evidence_ledger_mutation": False,
        "rights_safety_claims": False,
        "production_readiness_claimed": False,
    }


def _provider_modes(smoke_report: Mapping[str, Any]) -> list[str]:
    modes: list[str] = []
    fixture = dict(smoke_report.get("fixture_smoke", {}) or {})
    live = dict(smoke_report.get("live_smoke", {}) or {})
    if fixture.get("status") not in {"", None, "not_requested"}:
        modes.append("fixture")
    if live.get("status") not in {"", None, "not_requested", "operator_blocked"} or live.get("query_count"):
        modes.append("live")
    return modes or [str(smoke_report.get("mode") or "fixture")]


def _load_previous_manifest(
    manifest_path: Path,
    observations: Sequence[Mapping[str, Any]],
    smoke_report: Mapping[str, Any],
) -> Mapping[str, Any] | None:
    if not manifest_path.is_file():
        return None
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, Mapping):
        return None
    return dict(payload)


def _read_observation_file(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise SourceObservationCacheError(f"observation file not found: {path}")
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SourceObservationCacheError(f"{path}:{line_number}: invalid JSONL row: {exc.msg}") from exc
        if not isinstance(payload, Mapping):
            raise SourceObservationCacheError(f"{path}:{line_number}: JSONL row must be an object")
        records.append(dict(payload))
    return records


def _write_jsonl(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(dict(row), sort_keys=True, separators=(",", ":"), ensure_ascii=True))
            handle.write("\n")


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(dict(payload), indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stable_digest(value: Any, length: int = 16) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:length]


def _preview_ref(kind: str, query_index: int, ordinal: int) -> str:
    return f"ia-{kind}-preview:q{query_index:02d}:{ordinal:03d}"


def _safe_path_label(path: Path) -> str:
    resolved = path
    try:
        repo_root = Path(__file__).resolve().parents[2]
        return resolved.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        return f"<external:{path.name}>"


def _normalize_source(source: str) -> str:
    return str(source or "").strip().replace("-", "_").lower()

"""Build governed local candidate-index refresh deltas from source observations."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "eureka.candidate_index_refresh_delta.v0"
CANDIDATE_SCHEMA_VERSION = "eureka.candidate_index_delta_record.v0"
REPORT_SCHEMA_VERSION = "eureka.candidate_index_refresh_report.v0"
SOURCE_OBSERVATION_SCHEMA_VERSION = "eureka.source_observation_cache_delta.v0"
SOURCE_FAMILY = "ia_metadata"
SOURCE_ID = "internet_archive_metadata"
DEFAULT_LICENSE_POSTURE = "restricted_source_available"
DEFAULT_RECOMMENDED_NEXT_TASK = "IA-EVIDENCE-LEDGER-SUMMARY-00"

CANDIDATE_FILE_NAME = "candidate_index_delta.jsonl"
MANIFEST_FILE_NAME = "candidate_index_delta_manifest.json"
REPORT_FILE_NAME = "CANDIDATE_INDEX_REFRESH_REPORT.md"
SOURCE_OBSERVATION_FILE_FALLBACK = "source_observations.jsonl"

REQUIRED_MANIFEST_FIELDS = {
    "delta_id",
    "source_family",
    "generated_at",
    "input_source_observation_delta",
    "input_source_observation_delta_hash",
    "candidate_count",
    "deduplicated_candidate_count",
    "source_observation_count",
    "query_count",
    "provider_modes",
    "unsafe_record_count",
    "redacted_error_count",
    "policy_ids",
    "no_downloads",
    "no_file_fetch",
    "no_wayback_replay",
    "no_public_fanout",
    "reviewed_master_mutation",
    "public_index_mutation",
    "candidate_index_delta_written",
    "candidate_index_store_mutation",
    "evidence_ledger_mutation",
    "review_promotion_mutation",
    "license_posture",
    "candidate_file",
    "candidate_file_hash",
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
    "reviewed_master_mutation",
    "reviewed_master_index_mutation",
    "reviewed_index_mutated",
    "master_index_mutated",
    "public_index_mutation",
    "candidate_index_store_mutation",
    "candidate_index_mutation",
    "candidate_index_mutated",
    "evidence_ledger_mutation",
    "evidence_ledger_materialized",
    "review_promotion_mutation",
    "review_queue_mutated",
    "accepted_truth_created",
    "accepted_truth",
    "reviewed_record_created",
    "public_snapshot_record_created",
    "rights_clearance_claimed",
    "rights_safety_claims",
    "malware_safety_claimed",
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
    "accepted_artifact_record",
    "public_snapshot_record",
    "rights_clearance",
    "rights_clearance_claim",
    "malware_safety_claim",
    "binary_safety_claim",
    "install_safety_claim",
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


class CandidateIndexRefreshError(ValueError):
    """Raised when a candidate-index refresh delta is unsafe or invalid."""


def load_source_observation_delta_manifest(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    if not source.is_file():
        raise CandidateIndexRefreshError(f"source-observation delta manifest not found: {source}")
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CandidateIndexRefreshError(f"source-observation delta manifest is not valid JSON: {exc.msg}") from exc
    if not isinstance(payload, Mapping):
        raise CandidateIndexRefreshError("source-observation delta manifest must be a JSON object")
    manifest = dict(payload)
    errors = _source_observation_manifest_errors(manifest)
    if errors:
        raise CandidateIndexRefreshError("; ".join(errors))
    return manifest


def load_source_observations(manifest_path: str | Path, manifest: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    path = Path(manifest_path)
    active_manifest = dict(manifest or load_source_observation_delta_manifest(path))
    observation_file = str(active_manifest.get("observation_file") or SOURCE_OBSERVATION_FILE_FALLBACK)
    observation_path = path.parent / observation_file
    if not observation_path.is_file():
        raise CandidateIndexRefreshError(f"source observations file not found: {observation_path}")
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(observation_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CandidateIndexRefreshError(f"{observation_path}:{line_number}: invalid JSONL row: {exc.msg}") from exc
        if not isinstance(payload, Mapping):
            raise CandidateIndexRefreshError(f"{observation_path}:{line_number}: JSONL row must be an object")
        records.append(dict(payload))
    errors = _source_observation_record_errors(records)
    if errors:
        raise CandidateIndexRefreshError("; ".join(errors))
    return records


def build_delta(
    *,
    source: str,
    source_observation_delta_path: str | Path,
    out_dir: str | Path,
) -> dict[str, Any]:
    normalized_source = _normalize_source(source)
    if normalized_source != SOURCE_FAMILY:
        raise CandidateIndexRefreshError(f"unsupported source: {source}")
    source_delta_path = Path(source_observation_delta_path)
    source_manifest = load_source_observation_delta_manifest(source_delta_path)
    observations = load_source_observations(source_delta_path, source_manifest)
    source_delta_hash = _file_hash(source_delta_path)
    candidates = normalize_provisional_candidates(
        observations,
        source_manifest=source_manifest,
        source_delta_hash=source_delta_hash,
    )
    candidate_errors = _candidate_record_errors(candidates)
    if candidate_errors:
        raise CandidateIndexRefreshError("; ".join(candidate_errors))

    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    candidate_path = output / CANDIDATE_FILE_NAME
    manifest_path = output / MANIFEST_FILE_NAME
    report_path = output / REPORT_FILE_NAME

    previous = _load_previous_manifest(manifest_path)
    _write_jsonl(candidate_path, candidates)
    candidate_hash = _file_hash(candidate_path)
    manifest = build_candidate_index_delta_manifest(
        source_manifest=source_manifest,
        source_delta_path=source_delta_path,
        source_delta_hash=source_delta_hash,
        observations=observations,
        candidates=candidates,
        candidate_path=candidate_path,
        candidate_hash=candidate_hash,
        previous=previous,
    )
    manifest_errors = validate_candidate_index_delta_manifest(manifest, candidates=candidates)
    if manifest_errors:
        raise CandidateIndexRefreshError("; ".join(manifest_errors))
    _write_json(manifest_path, manifest)
    report_path.write_text(render_markdown_summary(manifest, candidates=candidates), encoding="utf-8", newline="\n")
    return {
        "schema_version": "eureka.candidate_index_refresh_delta_build_result.v0",
        "status": "PASS" if manifest["validation_status"] == "PASS" else "PASS_WITH_WARNINGS",
        "manifest": manifest,
        "manifest_path": _safe_path_label(manifest_path),
        "candidate_path": _safe_path_label(candidate_path),
        "report_path": _safe_path_label(report_path),
        "candidate_count": len(candidates),
        "deduplicated_candidate_count": len({str(item.get("candidate_id", "")) for item in candidates}),
        "network_used": False,
        "provider_calls": False,
        "downloads": False,
        "file_fetch": False,
        "wayback_replay": False,
        "reviewed_master_mutation": False,
        "public_index_mutation": False,
        "candidate_index_store_mutation": False,
        "evidence_ledger_mutation": False,
        "review_promotion_mutation": False,
    }


def normalize_provisional_candidates(
    observations: Sequence[Mapping[str, Any]],
    *,
    source_manifest: Mapping[str, Any],
    source_delta_hash: str,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    generated_at = str(source_manifest.get("generated_at") or "")
    source_delta_id = str(source_manifest.get("delta_id") or "")
    input_delta_hash = f"sha256:{source_delta_hash}"
    for observation in observations:
        observation_id = str(observation.get("observation_id") or "")
        query_seed = str(observation.get("query_seed") or "")
        metadata = dict(observation.get("normalized_metadata", {}) or {})
        ordinal = int(metadata.get("preview_ordinal", 0) or 0)
        candidate_seed = {
            "source_family": SOURCE_FAMILY,
            "query_seed": query_seed,
            "source_observation_refs": [observation_id],
            "preview_ordinal": ordinal,
            "input_source_observation_delta_id": source_delta_id,
        }
        candidate_id = f"candidate:{SOURCE_FAMILY}:{_stable_digest(candidate_seed, 20)}"
        normalized_title = _candidate_title(query_seed, ordinal)
        candidate_without_hash = {
            "schema_version": CANDIDATE_SCHEMA_VERSION,
            "candidate_id": candidate_id,
            "candidate_status": "provisional",
            "candidate_authority": "candidate_only",
            "source_family": SOURCE_FAMILY,
            "source_id": str(observation.get("source_id") or SOURCE_ID),
            "source_observation_refs": [observation_id],
            "source_locator_refs": [dict(observation.get("source_locator", {}) or {})],
            "query_seed_refs": [query_seed],
            "provider_mode_refs": [str(observation.get("provider_mode") or "")],
            "normalized_title": normalized_title,
            "normalized_type_hints": _type_hints(query_seed),
            "platform_time_version_hints": _platform_time_version_hints(query_seed),
            "representation_member_hints": _representation_member_hints(query_seed),
            "source_confidence_hints": {
                "level": "low",
                "basis": "metadata_smoke_source_observation_preview",
                "source_observation_only": True,
                "review_required": True,
            },
            "matching_ranking_hints": {
                "query_seed": query_seed,
                "preview_ordinal": ordinal,
                "query_candidate_count_hint": int(metadata.get("query_candidate_count", 0) or 0),
                "boundary_passed": bool(metadata.get("boundary_passed", False)),
            },
            "ambiguity_flags": _ambiguity_flags(query_seed),
            "absence_near_miss_clues": _absence_near_miss_clues(query_seed, metadata),
            "risk_safety_placeholders": {
                "malware_safety": "unknown_not_claimed",
                "binary_install_execution_safety": "unknown_not_claimed",
            },
            "rights_posture": "unknown_not_cleared",
            "review_state": "unreviewed",
            "generated_at": generated_at,
            "input_source_observation_delta_id": source_delta_id,
            "input_source_observation_delta_hash": input_delta_hash,
            "evidence_preview_refs": list(observation.get("evidence_preview_refs", []) or []),
            "candidate_preview_refs": list(observation.get("candidate_preview_refs", []) or []),
            "review_preview_refs": list(observation.get("review_preview_refs", []) or []),
            "recommended_review_lane": "ia_metadata_candidate_review",
            "recommended_next_action": "queue_for_evidence_ledger_summary",
            "limitations": [
                "candidate is provisional and unreviewed",
                "source observation is not reviewed truth",
                "metadata is evidence support, not verified artifact truth",
                "no evidence ledger, reviewed index, public index, download, or Wayback replay mutation occurred",
            ],
            "safety_flags": _safety_flags(),
        }
        candidate_hash = _stable_digest(candidate_without_hash, 64)
        candidates.append({**candidate_without_hash, "deterministic_candidate_hash": f"sha256:{candidate_hash}"})
    return sorted(candidates, key=lambda item: str(item["candidate_id"]))


def build_candidate_index_delta_manifest(
    *,
    source_manifest: Mapping[str, Any],
    source_delta_path: Path,
    source_delta_hash: str,
    observations: Sequence[Mapping[str, Any]],
    candidates: Sequence[Mapping[str, Any]],
    candidate_path: Path,
    candidate_hash: str,
    previous: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    candidate_ids = [str(item.get("candidate_id", "")) for item in candidates]
    delta_seed = {
        "source_family": SOURCE_FAMILY,
        "source_delta_hash": source_delta_hash,
        "candidate_ids": candidate_ids,
        "candidate_file_hash": candidate_hash,
    }
    delta_id = f"candidate-index-delta:{SOURCE_FAMILY}:{_stable_digest(delta_seed, 20)}"
    previous_delta_id = None
    previous_delta_path = None
    diff_status = "first_run_no_previous_delta"
    if previous:
        previous_id = str(previous.get("delta_id") or "")
        if previous_id and previous_id != delta_id:
            previous_delta_id = previous_id
            previous_delta_path = _safe_path_label(candidate_path.parent / MANIFEST_FILE_NAME)
            diff_status = "changed_from_previous_delta"
        elif previous_id == delta_id:
            diff_status = "first_run_no_previous_delta"
    validation_status = "PASS_WITH_WARNINGS" if diff_status == "first_run_no_previous_delta" else "PASS"
    query_seeds = sorted({str(item.get("query_seed") or item.get("query_seed_refs", [""])[0]) for item in observations})
    return {
        "schema_version": SCHEMA_VERSION,
        "delta_id": delta_id,
        "source_family": SOURCE_FAMILY,
        "generated_at": str(source_manifest.get("generated_at") or ""),
        "input_source_observation_delta": _safe_path_label(source_delta_path),
        "input_source_observation_delta_id": str(source_manifest.get("delta_id") or ""),
        "input_source_observation_delta_hash": f"sha256:{source_delta_hash}",
        "candidate_count": len(candidates),
        "deduplicated_candidate_count": len(set(candidate_ids)),
        "source_observation_count": len(observations),
        "query_count": int(source_manifest.get("query_count", len(query_seeds)) or 0),
        "query_seeds": query_seeds,
        "provider_modes": list(source_manifest.get("provider_modes_represented", []) or []),
        "unsafe_record_count": 0,
        "redacted_error_count": int(source_manifest.get("redacted_error_count", 0) or 0),
        "policy_ids": list(source_manifest.get("policy_ids", []) or []),
        "no_downloads": bool(source_manifest.get("no_downloads", False)),
        "no_file_fetch": bool(source_manifest.get("no_file_fetch", False)),
        "no_wayback_replay": bool(source_manifest.get("no_wayback_replay", False)),
        "no_public_fanout": bool(source_manifest.get("no_public_fanout", False)),
        "reviewed_master_mutation": False,
        "public_index_mutation": False,
        "candidate_index_delta_written": True,
        "candidate_index_store_mutation": False,
        "evidence_ledger_mutation": False,
        "review_promotion_mutation": False,
        "license_posture": DEFAULT_LICENSE_POSTURE,
        "candidate_file": CANDIDATE_FILE_NAME,
        "candidate_file_hash": f"sha256:{candidate_hash}",
        "previous_delta_id": previous_delta_id,
        "previous_delta_path": previous_delta_path,
        "diff_status": diff_status,
        "validation_status": validation_status,
        "blockers": [],
        "recommended_next_task": DEFAULT_RECOMMENDED_NEXT_TASK,
        "candidate_id_pattern": f"candidate:{SOURCE_FAMILY}:<short_hash>",
        "review_state": "unreviewed",
        "candidate_status": "provisional",
        "candidate_authority": "candidate_only",
        "source_index_path": [
            "IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00",
            "IA-SOURCE-OBSERVATION-CACHE-DELTA-00",
            "IA-CANDIDATE-INDEX-REFRESH-00",
            "IA-EVIDENCE-LEDGER-SUMMARY-00",
            "REVIEW-IA-CANDIDATES-BATCH-00",
        ],
    }


def validate_candidate_index_delta_manifest(
    manifest: Mapping[str, Any],
    *,
    candidates: Sequence[Mapping[str, Any]] | None = None,
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
    if manifest.get("candidate_index_delta_written") is not True:
        errors.append("candidate_index_delta_written must be true")
    for key in (
        "reviewed_master_mutation",
        "public_index_mutation",
        "candidate_index_store_mutation",
        "evidence_ledger_mutation",
        "review_promotion_mutation",
    ):
        if manifest.get(key) is not False:
            errors.append(f"{key} must be false")
    for key in (
        "candidate_count",
        "deduplicated_candidate_count",
        "source_observation_count",
        "query_count",
        "unsafe_record_count",
        "redacted_error_count",
    ):
        if not isinstance(manifest.get(key), int) or int(manifest.get(key)) < 0:
            errors.append(f"{key} must be a non-negative integer")
    if manifest.get("unsafe_record_count") != 0:
        errors.append("unsafe_record_count must be 0")
    if manifest.get("recommended_next_task") != DEFAULT_RECOMMENDED_NEXT_TASK:
        errors.append(f"recommended_next_task must be {DEFAULT_RECOMMENDED_NEXT_TASK}")
    if candidates is not None:
        candidate_ids = [str(item.get("candidate_id", "")) for item in candidates]
        if manifest.get("candidate_count") != len(candidates):
            errors.append("candidate_count does not match candidate rows")
        if manifest.get("deduplicated_candidate_count") != len(set(candidate_ids)):
            errors.append("deduplicated_candidate_count does not match unique candidate IDs")
        errors.extend(_candidate_record_errors(candidates))
    for path, value in _walk_items(manifest):
        key = path.rsplit(".", 1)[-1]
        if key in FORBIDDEN_TRUE_FLAGS and value is True:
            errors.append(f"{path} must be false")
    errors.extend(_scan_unsafe_content(manifest, "$"))
    return sorted(dict.fromkeys(errors))


def load_delta_manifest(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    if not source.is_file():
        raise CandidateIndexRefreshError(f"candidate-index delta manifest not found: {source}")
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CandidateIndexRefreshError(f"candidate-index delta manifest is not valid JSON: {exc.msg}") from exc
    if not isinstance(payload, Mapping):
        raise CandidateIndexRefreshError("candidate-index delta manifest must be a JSON object")
    return dict(payload)


def validate_delta_path(path: str | Path, *, strict: bool = False) -> dict[str, Any]:
    manifest_path = Path(path)
    manifest = load_delta_manifest(manifest_path)
    candidate_path = manifest_path.parent / str(manifest.get("candidate_file", CANDIDATE_FILE_NAME))
    candidates = _read_candidate_file(candidate_path)
    errors = validate_candidate_index_delta_manifest(manifest, candidates=candidates)
    actual_candidate_hash = f"sha256:{_file_hash(candidate_path)}"
    if manifest.get("candidate_file_hash") != actual_candidate_hash:
        errors.append("candidate_file_hash does not match candidate file")
    if strict and manifest.get("validation_status") not in {"PASS", "PASS_WITH_WARNINGS"}:
        errors.append("validation_status must be PASS or PASS_WITH_WARNINGS")
    status = "PASS" if not errors else "FAIL"
    return {
        "schema_version": "eureka.candidate_index_refresh_delta_validation.v0",
        "status": status,
        "strict": bool(strict),
        "delta": _safe_path_label(manifest_path),
        "delta_id": manifest.get("delta_id"),
        "candidate_count": manifest.get("candidate_count"),
        "deduplicated_candidate_count": manifest.get("deduplicated_candidate_count"),
        "unsafe_record_count": manifest.get("unsafe_record_count"),
        "errors": sorted(errors),
        "reviewed_master_mutation": bool(manifest.get("reviewed_master_mutation", False)),
        "public_index_mutation": bool(manifest.get("public_index_mutation", False)),
        "candidate_index_store_mutation": bool(manifest.get("candidate_index_store_mutation", False)),
        "evidence_ledger_mutation": bool(manifest.get("evidence_ledger_mutation", False)),
        "review_promotion_mutation": bool(manifest.get("review_promotion_mutation", False)),
    }


def status_for_delta(path: str | Path) -> dict[str, Any]:
    manifest = load_delta_manifest(path)
    return {
        "schema_version": "eureka.candidate_index_refresh_delta_status.v0",
        "status": str(manifest.get("validation_status") or "UNKNOWN"),
        "delta_id": manifest.get("delta_id"),
        "source_family": manifest.get("source_family"),
        "candidate_count": manifest.get("candidate_count"),
        "deduplicated_candidate_count": manifest.get("deduplicated_candidate_count"),
        "source_observation_count": manifest.get("source_observation_count"),
        "query_count": manifest.get("query_count"),
        "provider_modes": manifest.get("provider_modes", []),
        "unsafe_record_count": manifest.get("unsafe_record_count"),
        "redacted_error_count": manifest.get("redacted_error_count"),
        "diff_status": manifest.get("diff_status"),
        "previous_delta_id": manifest.get("previous_delta_id"),
        "reviewed_master_mutation": manifest.get("reviewed_master_mutation"),
        "public_index_mutation": manifest.get("public_index_mutation"),
        "candidate_index_store_mutation": manifest.get("candidate_index_store_mutation"),
        "evidence_ledger_mutation": manifest.get("evidence_ledger_mutation"),
        "review_promotion_mutation": manifest.get("review_promotion_mutation"),
        "recommended_next_task": manifest.get("recommended_next_task"),
    }


def render_markdown_summary(
    manifest: Mapping[str, Any],
    *,
    candidates: Sequence[Mapping[str, Any]] | None = None,
) -> str:
    del candidates
    provider_modes = ", ".join(str(item) for item in manifest.get("provider_modes", []) or [])
    return (
        "# IA Candidate Index Refresh Delta\n\n"
        f"- status: {manifest.get('validation_status')}\n"
        f"- delta id: {manifest.get('delta_id')}\n"
        f"- source family: {manifest.get('source_family')}\n"
        f"- input source-observation delta: {manifest.get('input_source_observation_delta')}\n"
        f"- input source-observation delta hash: {manifest.get('input_source_observation_delta_hash')}\n"
        f"- source observations consumed: {manifest.get('source_observation_count')}\n"
        f"- candidates written: {manifest.get('candidate_count')}\n"
        f"- deduplicated candidates: {manifest.get('deduplicated_candidate_count')}\n"
        f"- query count: {manifest.get('query_count')}\n"
        f"- provider modes: {provider_modes}\n"
        f"- unsafe records: {manifest.get('unsafe_record_count')}\n"
        f"- redacted errors: {manifest.get('redacted_error_count')}\n"
        f"- previous delta: {manifest.get('previous_delta_id') or 'none'}\n"
        f"- diff status: {manifest.get('diff_status')}\n"
        f"- candidate file: {manifest.get('candidate_file')}\n"
        f"- candidate file hash: {manifest.get('candidate_file_hash')}\n"
        f"- reviewed/master mutation: {str(manifest.get('reviewed_master_mutation')).lower()}\n"
        f"- public-index mutation: {str(manifest.get('public_index_mutation')).lower()}\n"
        f"- candidate-index store mutation: {str(manifest.get('candidate_index_store_mutation')).lower()}\n"
        f"- evidence-ledger mutation: {str(manifest.get('evidence_ledger_mutation')).lower()}\n"
        f"- review/promotion mutation: {str(manifest.get('review_promotion_mutation')).lower()}\n"
        f"- no downloads: {str(manifest.get('no_downloads')).lower()}\n"
        f"- no file fetch: {str(manifest.get('no_file_fetch')).lower()}\n"
        f"- no Wayback replay: {str(manifest.get('no_wayback_replay')).lower()}\n"
        f"- no public fanout: {str(manifest.get('no_public_fanout')).lower()}\n"
        f"- license posture: {manifest.get('license_posture')}\n"
        f"- recommended next task: {manifest.get('recommended_next_task')}\n\n"
        "## Boundary\n\n"
        "This delta records provisional, unreviewed candidates derived from "
        "source observations. It is not reviewed truth, not an evidence ledger, "
        "not a public snapshot index, and not a candidate store mutation.\n"
    )


def _source_observation_manifest_errors(manifest: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema_version") != SOURCE_OBSERVATION_SCHEMA_VERSION:
        errors.append(f"source-observation manifest schema_version must be {SOURCE_OBSERVATION_SCHEMA_VERSION}")
    if manifest.get("source_family") != SOURCE_FAMILY:
        errors.append(f"source_family must be {SOURCE_FAMILY}")
    if manifest.get("license_posture") != DEFAULT_LICENSE_POSTURE:
        errors.append(f"license_posture must be {DEFAULT_LICENSE_POSTURE}")
    for key in ("no_downloads", "no_file_fetch", "no_wayback_replay", "no_public_fanout"):
        if manifest.get(key) is not True:
            errors.append(f"{key} must be true")
    for key in ("reviewed_master_mutation", "public_index_mutation", "candidate_index_mutation", "evidence_ledger_mutation"):
        if manifest.get(key) is not False:
            errors.append(f"{key} must be false")
    for path, value in _walk_items(manifest):
        key = path.rsplit(".", 1)[-1]
        if key in FORBIDDEN_TRUE_FLAGS and value is True:
            errors.append(f"{path} must be false")
    errors.extend(_scan_unsafe_content(manifest, "$"))
    return sorted(dict.fromkeys(errors))


def _source_observation_record_errors(observations: Sequence[Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for index, record in enumerate(observations, start=1):
        path = f"source_observation[{index}]"
        observation_id = str(record.get("observation_id") or "")
        if not observation_id.startswith(f"source-observation:{SOURCE_FAMILY}:"):
            errors.append(f"{path} observation_id has unsupported prefix")
        if observation_id in seen:
            errors.append(f"{path} duplicate observation_id: {observation_id}")
        seen.add(observation_id)
        if record.get("source_family") != SOURCE_FAMILY:
            errors.append(f"{path} source_family must be {SOURCE_FAMILY}")
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
            for key in ("reviewed_master_mutation", "public_index_mutation", "candidate_index_mutation", "evidence_ledger_mutation"):
                if safety.get(key) is not False:
                    errors.append(f"{path} safety_flags.{key} must be false")
        errors.extend(_scan_unsafe_content(record, path))
    return sorted(dict.fromkeys(errors))


def _candidate_record_errors(candidates: Sequence[Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    required = {
        "schema_version",
        "candidate_id",
        "candidate_status",
        "candidate_authority",
        "source_family",
        "source_observation_refs",
        "query_seed_refs",
        "provider_mode_refs",
        "normalized_title",
        "review_state",
        "input_source_observation_delta_id",
        "input_source_observation_delta_hash",
        "deterministic_candidate_hash",
        "safety_flags",
    }
    for index, record in enumerate(candidates, start=1):
        path = f"candidate[{index}]"
        missing = sorted(required - set(record))
        if missing:
            errors.append(f"{path} missing required fields: {', '.join(missing)}")
        candidate_id = str(record.get("candidate_id") or "")
        if not candidate_id.startswith(f"candidate:{SOURCE_FAMILY}:"):
            errors.append(f"{path} candidate_id has unsupported prefix")
        if candidate_id in seen:
            errors.append(f"{path} duplicate candidate_id: {candidate_id}")
        seen.add(candidate_id)
        if record.get("schema_version") != CANDIDATE_SCHEMA_VERSION:
            errors.append(f"{path} schema_version must be {CANDIDATE_SCHEMA_VERSION}")
        if record.get("candidate_status") != "provisional":
            errors.append(f"{path} candidate_status must be provisional")
        if record.get("candidate_authority") != "candidate_only":
            errors.append(f"{path} candidate_authority must be candidate_only")
        if record.get("source_family") != SOURCE_FAMILY:
            errors.append(f"{path} source_family must be {SOURCE_FAMILY}")
        if record.get("review_state") != "unreviewed":
            errors.append(f"{path} review_state must be unreviewed")
        if not list(record.get("source_observation_refs", []) or []):
            errors.append(f"{path} source_observation_refs must not be empty")
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
                "candidate_index_store_mutation",
                "evidence_ledger_mutation",
                "review_promotion_mutation",
                "accepted_truth_created",
            ):
                if safety.get(key) is not False:
                    errors.append(f"{path} safety_flags.{key} must be false")
        for walk_path, value in _walk_items(record, path):
            key = walk_path.rsplit(".", 1)[-1]
            if key in FORBIDDEN_TRUE_FLAGS and value is True:
                errors.append(f"{walk_path} must be false")
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


def _read_candidate_file(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise CandidateIndexRefreshError(f"candidate file not found: {path}")
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CandidateIndexRefreshError(f"{path}:{line_number}: invalid JSONL row: {exc.msg}") from exc
        if not isinstance(payload, Mapping):
            raise CandidateIndexRefreshError(f"{path}:{line_number}: JSONL row must be an object")
        records.append(dict(payload))
    return records


def _write_jsonl(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(dict(row), sort_keys=True, separators=(",", ":"), ensure_ascii=True))
            handle.write("\n")


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(dict(payload), indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def _load_previous_manifest(manifest_path: Path) -> Mapping[str, Any] | None:
    if not manifest_path.is_file():
        return None
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, Mapping):
        return None
    return dict(payload)


def _candidate_title(query: str, ordinal: int) -> str:
    suffix = f" metadata candidate {ordinal:03d}" if ordinal else " metadata candidate"
    return f"{query}{suffix}".strip()


def _type_hints(query: str) -> list[str]:
    lower = query.lower()
    hints: list[str] = []
    if "driver" in lower:
        hints.append("driver_or_support_software")
    if "manual" in lower:
        hints.append("manual_or_documentation")
    if "article" in lower or "magazine" in lower:
        hints.append("article_or_periodical_member")
    if "firefox" in lower or "directx" in lower or "ftp" in lower or "apps" in lower:
        hints.append("software_release_or_installer")
    return hints or ["metadata_candidate"]


def _platform_time_version_hints(query: str) -> list[str]:
    lower = query.lower()
    hints: list[str] = []
    for token in ("windows 2000", "win98", "windows 7", "xp", "mac os 8", "june 2010", "1994"):
        if token in lower:
            hints.append(token)
    return hints


def _representation_member_hints(query: str) -> list[str]:
    lower = query.lower()
    hints: list[str] = []
    if "article" in lower or "magazine" in lower:
        hints.append("member_inside_scan_or_issue")
    if "offline installer" in lower:
        hints.append("installer_representation")
    if "driver" in lower:
        hints.append("support_download_representation_unknown")
    return hints


def _ambiguity_flags(query: str) -> list[str]:
    lower = query.lower()
    flags: list[str] = []
    if "latest" in lower:
        flags.append("temporal_boundary_requires_review")
    if "driver" in lower:
        flags.append("hardware_platform_match_requires_review")
    if "article" in lower:
        flags.append("member_identity_requires_review")
    return flags


def _absence_near_miss_clues(query: str, metadata: Mapping[str, Any]) -> list[str]:
    clues: list[str] = []
    if int(metadata.get("query_candidate_count", 0) or 0) == 0:
        clues.append("zero_candidate_preview")
    if str(metadata.get("candidate_index_dry_run_status") or "") != "pass":
        clues.append("candidate_dry_run_not_passed")
    if "manual for Sound Blaster CT1740" in query:
        clues.append("live_zero_result_status_preserved_in_manifest_only")
    return clues


def _safety_flags() -> dict[str, bool]:
    return {
        "no_downloads": True,
        "no_file_fetch": True,
        "no_wayback_replay": True,
        "no_public_fanout": True,
        "reviewed_master_mutation": False,
        "public_index_mutation": False,
        "candidate_index_store_mutation": False,
        "evidence_ledger_mutation": False,
        "review_promotion_mutation": False,
        "accepted_truth_created": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "production_readiness_claimed": False,
    }


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stable_digest(value: Any, length: int = 16) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:length]


def _safe_path_label(path: Path) -> str:
    try:
        repo_root = Path(__file__).resolve().parents[2]
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        return f"<external:{path.name}>"


def _normalize_source(source: str) -> str:
    return str(source or "").strip().replace("-", "_").lower()

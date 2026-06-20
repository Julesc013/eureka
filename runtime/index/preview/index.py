"""Deterministic derived E2E Preview Index.

The Preview Index is a rebuildable projection over local reviewed and
provisional material. It is not an authority store and it does not promote
records across the review boundary.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json
import os
import re
import tempfile
from typing import Any, Iterable, Mapping, Sequence

from runtime.resolution_run import validate_run_bundle
from runtime.resolution_run.run_store import FIXED_CREATED_AT


PREVIEW_INDEX_SCHEMA_VERSION = "eureka.e2e_preview_index.v0"
PREVIEW_RECORD_SCHEMA_VERSION = "eureka.e2e_preview_record.v0"
DEFAULT_PREVIEW_INDEX_ROOT = Path(".eureka/e2e-reference/preview-index")
PREVIEW_GENERATED_AT = FIXED_CREATED_AT

CORE_STATUSES = {
    "reviewed",
    "candidate",
    "near_miss",
    "need",
    "absence",
    "policy_blocked",
    "unavailable",
    "unknown",
    "mention_only",
    "superseded",
    "rejected",
    "private_local",
}
CORE_AUTHORITIES = {
    "reviewed_record",
    "candidate_only",
    "source_observation_only",
    "evidence_summary_only",
    "absence_finding",
    "run_projection",
    "synthetic_test",
    "unknown",
}
DEFAULT_FORBIDDEN_ACTIONS = (
    "download",
    "install",
    "execute",
    "upload",
    "call_provider",
    "call_model",
    "promote_without_review",
    "write_review_decision",
    "create_reviewed_record",
    "mutate_reviewed_master_index",
    "mutate_public_index",
    "publish_snapshot",
    "expose_public_service",
)
DEFAULT_PERMITTED_ACTIONS = (
    "view",
    "inspect_provenance",
    "export_local_packet",
)
STATUS_TO_LANE = {
    "reviewed": "reviewed",
    "candidate": "candidates",
    "near_miss": "near_misses",
    "need": "needs",
    "absence": "absence_or_next_steps",
    "policy_blocked": "blocked_or_unavailable",
    "unavailable": "blocked_or_unavailable",
}
PRIVATE_PATH_PATTERNS = (
    re.compile(r"\b[A-Za-z]:\\Users\\[^\\\s]+", re.IGNORECASE),
    re.compile(r"/home/[^/\s]+", re.IGNORECASE),
    re.compile(r"/Users/[^/\s]+", re.IGNORECASE),
    re.compile(r"\.aide\.local[/\\]", re.IGNORECASE),
    re.compile(r"\.cache[/\\]", re.IGNORECASE),
    re.compile(r"\.local[/\\]", re.IGNORECASE),
)
STOPWORDS = {
    "a",
    "an",
    "and",
    "app",
    "apps",
    "for",
    "in",
    "index",
    "local",
    "of",
    "query",
    "the",
    "to",
    "with",
}


class PreviewIndexError(ValueError):
    """Raised when a Preview Index generation is invalid or unsafe."""


def build_preview_index(
    *,
    out_root: str | Path = DEFAULT_PREVIEW_INDEX_ROOT,
    runs_root: str | Path | None = None,
    candidate_delta: str | Path | None = None,
    evidence_delta: str | Path | None = None,
    source_observation_delta: str | Path | None = None,
    reviewed_records: str | Path | None = None,
    activate: bool = True,
) -> dict[str, Any]:
    """Build, validate, and optionally activate one immutable generation."""

    root = Path(out_root)
    records: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    if reviewed_records:
        path = Path(reviewed_records)
        reviewed = _records_from_reviewed_records(path)
        records.extend(reviewed)
        sources.append(_source_entry("reviewed_records", path))

    source_records: dict[str, Mapping[str, Any]] = {}
    if source_observation_delta:
        path = Path(source_observation_delta)
        source_records = _load_source_observation_records(path)
        records.extend(_records_from_source_observations(path, source_records.values()))
        sources.append(_source_entry("source_observation_delta", path))

    evidence_by_candidate: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    evidence_records: list[Mapping[str, Any]] = []
    if evidence_delta:
        path = Path(evidence_delta)
        evidence_records = _load_evidence_summary_records(path)
        for item in evidence_records:
            for candidate_id in _string_list(item.get("candidate_refs")):
                evidence_by_candidate[candidate_id].append(item)
        records.extend(_records_from_evidence(path, evidence_records))
        sources.append(_source_entry("evidence_delta", path))

    if candidate_delta:
        path = Path(candidate_delta)
        candidate_records = _load_candidate_records(path)
        records.extend(_records_from_candidates(path, candidate_records, evidence_by_candidate, source_records))
        sources.append(_source_entry("candidate_delta", path))

    if runs_root:
        run_records, run_sources, run_skipped = _records_from_runs_root(Path(runs_root))
        records.extend(run_records)
        sources.extend(run_sources)
        skipped.extend(run_skipped)

    records = _deduplicate_records(records)
    _assert_no_duplicate_ids(records)
    records = sorted(records, key=lambda item: str(item["preview_record_id"]))
    index_id = _preview_index_id(records, sources)
    generation_dir = _safe_child(root / "generations", index_id)
    if generation_dir.exists():
        # The generation is immutable; deterministic rebuilds may rewrite only
        # byte-identical content. Validation will catch any drift.
        pass
    generation_dir.mkdir(parents=True, exist_ok=True)

    record_path = generation_dir / "preview_records.jsonl"
    source_manifest_path = generation_dir / "source_manifest.json"
    stats_path = generation_dir / "stats.json"
    validation_path = generation_dir / "validation_report.json"
    manifest_path = generation_dir / "manifest.json"

    _write_jsonl(record_path, records)
    source_manifest = {"schema_version": "eureka.e2e_preview_index_sources.v0", "sources": sorted(sources, key=lambda item: item["path"])}
    _write_json(source_manifest_path, source_manifest)
    stats = _stats(records)
    _write_json(stats_path, stats)

    previous_current = _load_current_generation(root)
    manifest = {
        "schema_version": PREVIEW_INDEX_SCHEMA_VERSION,
        "preview_index_id": index_id,
        "generation_id": index_id,
        "generated_at": PREVIEW_GENERATED_AT,
        "generation_path": f"generations/{index_id}",
        "record_file": "preview_records.jsonl",
        "record_file_hash": f"sha256:{_file_hash(record_path)}",
        "source_manifest_file": "source_manifest.json",
        "source_manifest_hash": f"sha256:{_file_hash(source_manifest_path)}",
        "stats_file": "stats.json",
        "stats_hash": f"sha256:{_file_hash(stats_path)}",
        "input_manifests": sorted(sources, key=lambda item: item["path"]),
        "record_count": len(records),
        "status_counts": stats["status_counts"],
        "authority_counts": stats["authority_counts"],
        "source_family_counts": stats["source_family_counts"],
        "synthetic_count": stats["synthetic_count"],
        "reviewed_count": stats["status_counts"].get("reviewed", 0),
        "candidate_count": stats["status_counts"].get("candidate", 0),
        "absence_near_miss_count": stats["status_counts"].get("absence", 0) + stats["status_counts"].get("near_miss", 0),
        "malformed_skipped_count": len(skipped),
        "orphan_ref_count": _orphan_ref_count(records),
        "privacy_redaction_count": 0,
        "deterministic_build": True,
        "search_profile": "lexical_status_aware_v0",
        "previous_generation": previous_current,
        "rollback_eligible": True,
        "reviewed_store_mutation": False,
        "reviewed_master_mutation": False,
        "public_index_mutation": False,
        "source_provider_calls": False,
        "snapshot_publication": False,
        "accepted_truth_creation": False,
        "validation_status": "pending",
        "warnings": [],
        "blockers": [],
        "skipped_inputs": skipped,
    }
    _write_json(manifest_path, manifest)
    validation = validate_preview_index(manifest_path, strict=True, write_report=False)
    manifest["validation_status"] = "PASS" if validation["status"] == "pass" else "FAIL"
    manifest["blockers"] = list(validation.get("errors", []))
    _write_json(manifest_path, manifest)
    _write_json(validation_path, validation)
    if manifest["validation_status"] != "PASS":
        raise PreviewIndexError("; ".join(manifest["blockers"]) or "preview index validation failed")
    if activate:
        activate_preview_generation(root, index_id)
    return {
        "schema_version": "eureka.e2e_preview_index_build_result.v0",
        "status": "PASS",
        "preview_index_id": index_id,
        "generation_id": index_id,
        "manifest_path": str(manifest_path),
        "current_path": str(root / "current.json"),
        "record_file": str(record_path),
        "record_count": len(records),
        "status_counts": manifest["status_counts"],
        "authority_counts": manifest["authority_counts"],
        "synthetic_count": manifest["synthetic_count"],
        "reviewed_store_mutation": False,
        "reviewed_master_mutation": False,
        "public_index_mutation": False,
        "source_provider_calls": False,
        "accepted_truth_creation": False,
    }


def activate_preview_generation(root: str | Path, generation_id: str) -> dict[str, Any]:
    index_root = Path(root)
    manifest_path = _safe_child(index_root / "generations", generation_id) / "manifest.json"
    validation = validate_preview_index(manifest_path, strict=True)
    if validation["status"] != "pass":
        raise PreviewIndexError("cannot activate invalid preview generation")
    manifest = load_preview_manifest(manifest_path)
    current_path = index_root / "current.json"
    _atomic_write_text(current_path, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return {
        "schema_version": "eureka.e2e_preview_index_activation.v0",
        "status": "activated",
        "generation_id": generation_id,
        "current_path": str(current_path),
        "reviewed_master_mutation": False,
        "public_index_mutation": False,
    }


def rollback_preview_index(root: str | Path, generation_id: str) -> dict[str, Any]:
    index_root = Path(root)
    previous = _load_current_generation(index_root)
    activation = activate_preview_generation(index_root, generation_id)
    report = {
        "schema_version": "eureka.e2e_preview_index_rollback.v0",
        "status": "rolled_back",
        "from_generation": previous,
        "to_generation": generation_id,
        "current_path": activation["current_path"],
        "reviewed_master_mutation": False,
        "public_index_mutation": False,
        "authoritative_store_mutation": False,
    }
    _write_json(index_root / "rollback_report.json", report)
    return report


def list_preview_generations(root: str | Path) -> dict[str, Any]:
    index_root = Path(root)
    generations = []
    for manifest_path in sorted((index_root / "generations").glob("*/manifest.json")):
        manifest = load_preview_manifest(manifest_path)
        generations.append(
            {
                "generation_id": str(manifest.get("generation_id", "")),
                "record_count": int(manifest.get("record_count", 0) or 0),
                "status_counts": dict(manifest.get("status_counts") or {}),
                "validation_status": str(manifest.get("validation_status", "")),
            }
        )
    return {
        "schema_version": "eureka.e2e_preview_index_generation_list.v0",
        "current_generation": _load_current_generation(index_root),
        "generation_count": len(generations),
        "generations": generations,
    }


def compare_preview_generations(root: str | Path, left: str, right: str) -> dict[str, Any]:
    index_root = Path(root)
    left_manifest = load_preview_manifest(_safe_child(index_root / "generations", left) / "manifest.json")
    right_manifest = load_preview_manifest(_safe_child(index_root / "generations", right) / "manifest.json")
    left_records = _load_records_for_manifest(left_manifest, index_root=index_root)
    right_records = _load_records_for_manifest(right_manifest, index_root=index_root)
    left_ids = {str(item["preview_record_id"]) for item in left_records}
    right_ids = {str(item["preview_record_id"]) for item in right_records}
    return {
        "schema_version": "eureka.e2e_preview_index_generation_comparison.v0",
        "left_generation": left,
        "right_generation": right,
        "added": sorted(right_ids - left_ids),
        "removed": sorted(left_ids - right_ids),
        "unchanged_count": len(left_ids & right_ids),
        "status_count_delta": _count_delta(left_manifest.get("status_counts"), right_manifest.get("status_counts")),
        "authority_count_delta": _count_delta(left_manifest.get("authority_counts"), right_manifest.get("authority_counts")),
    }


def validate_preview_index(index: str | Path, *, strict: bool = True, write_report: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    path = Path(index)
    try:
        manifest = load_preview_manifest(path)
    except PreviewIndexError as exc:
        errors.append(str(exc))
        manifest = {}
    index_root = _index_root_from_manifest_path(path, manifest)
    records = _load_records_for_manifest(manifest, index_root=index_root, errors=errors) if manifest else []
    if manifest:
        if manifest.get("schema_version") != PREVIEW_INDEX_SCHEMA_VERSION:
            errors.append("schema_version must be eureka.e2e_preview_index.v0")
        if manifest.get("record_count") != len(records):
            errors.append("record_count must match preview records")
        if dict(manifest.get("status_counts") or {}) != _counts(item.get("status") for item in records):
            errors.append("status_counts must match preview records")
        if dict(manifest.get("authority_counts") or {}) != _counts(item.get("authority") for item in records):
            errors.append("authority_counts must match preview records")
        record_file = _record_file_for_manifest(manifest, index_root=index_root)
        if record_file.is_file() and f"sha256:{_file_hash(record_file)}" != manifest.get("record_file_hash"):
            errors.append("record_file_hash mismatch")
        if manifest.get("reviewed_master_mutation") is not False:
            errors.append("reviewed_master_mutation must be false")
        if manifest.get("public_index_mutation") is not False:
            errors.append("public_index_mutation must be false")
        if manifest.get("source_provider_calls") is not False:
            errors.append("source_provider_calls must be false")
        if manifest.get("accepted_truth_creation") is not False:
            errors.append("accepted_truth_creation must be false")
    errors.extend(_record_validation_errors(records, strict=strict))
    report = {
        "schema_version": "eureka.e2e_preview_index_validation.v0",
        "status": "pass" if not errors else "fail",
        "index": _safe_label(path),
        "record_count": len(records),
        "errors": errors,
        "strict": strict,
        "reviewed_master_mutation": False,
        "public_index_mutation": False,
        "provider_network_calls": False,
    }
    if write_report:
        target = path.parent / "validation_report.json" if path.name == "manifest.json" else path.with_name("validation_report.json")
        _write_json(target, report)
    return report


def preview_stats_payload(index: str | Path) -> dict[str, Any]:
    manifest = load_preview_manifest(index)
    return {
        "schema_version": "eureka.e2e_preview_index_stats.v0",
        "preview_index_id": str(manifest.get("preview_index_id") or ""),
        "generation_id": str(manifest.get("generation_id") or ""),
        "record_count": int(manifest.get("record_count") or 0),
        "status_counts": dict(manifest.get("status_counts") or {}),
        "authority_counts": dict(manifest.get("authority_counts") or {}),
        "source_family_counts": dict(manifest.get("source_family_counts") or {}),
        "synthetic_count": int(manifest.get("synthetic_count") or 0),
        "reviewed_count": int(manifest.get("reviewed_count") or 0),
        "candidate_count": int(manifest.get("candidate_count") or 0),
        "validation_status": str(manifest.get("validation_status") or ""),
    }


def search_preview_index(
    index: str | Path,
    query: str,
    *,
    limit: int = 10,
    include_synthetic: bool = False,
    include_rejected: bool = False,
    include_superseded: bool = False,
    status: str | None = None,
    authority: str | None = None,
    source_family: str | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    manifest = load_preview_manifest(index)
    index_root = _index_root_from_manifest_path(Path(index), manifest)
    records = _load_records_for_manifest(manifest, index_root=index_root)
    filtered = []
    for record in records:
        if record.get("synthetic") and not include_synthetic:
            continue
        if record.get("status") == "rejected" and not include_rejected:
            continue
        if record.get("status") == "superseded" and not include_superseded:
            continue
        if status and record.get("status") != status:
            continue
        if authority and record.get("authority") != authority:
            continue
        if source_family and record.get("source_family") != source_family:
            continue
        if run_id and run_id not in _string_list(record.get("run_refs")):
            continue
        score, why_matched, why_ranked = _score_record(record, query)
        if score <= 0:
            continue
        enriched = dict(record)
        enriched["rank_score"] = score
        enriched["why_matched"] = why_matched
        enriched["why_ranked"] = why_ranked
        filtered.append(enriched)
    filtered.sort(key=lambda item: (-int(item["rank_score"]), str(item.get("status")), str(item["preview_record_id"])))
    limited = filtered[: max(1, min(int(limit), 50))]
    lanes = _lanes(limited)
    return {
        "schema_version": "eureka.e2e_preview_index_search.v0",
        "preview_index_id": str(manifest.get("preview_index_id") or ""),
        "generation_id": str(manifest.get("generation_id") or ""),
        "query": str(query or ""),
        "normalized_query": _normalize_text(query),
        "result_count": len(limited),
        "results": limited,
        "lanes": lanes,
        "lane_counts": {lane: len(items) for lane, items in lanes.items()},
        "filters": {
            "include_synthetic": include_synthetic,
            "include_rejected": include_rejected,
            "include_superseded": include_superseded,
            "status": status or "",
            "authority": authority or "",
            "source_family": source_family or "",
            "run_id": run_id or "",
        },
        "reviewed_master_mutation": False,
        "public_index_mutation": False,
        "provider_network_calls": False,
    }


def preview_record_to_result_card(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "result_id": str(record.get("preview_record_id") or ""),
        "status": str(record.get("status") or "unknown"),
        "authority": str(record.get("authority") or "unknown"),
        "title": str(record.get("title") or "Preview result"),
        "summary": str(record.get("summary") or ""),
        "source_hints": _string_list(record.get("source_refs")) or _string_list(record.get("source_hints")),
        "evidence_hints": _string_list(record.get("evidence_refs")) or _string_list(record.get("evidence_hints")),
        "missing": _string_list(record.get("missing_information")),
        "safe_next_action": _safe_next_action(str(record.get("status") or "unknown")),
        "non_verified_reason": "; ".join(_string_list(record.get("uncertainty"))) or "preview record is not accepted truth",
        "verified": bool(record.get("accepted_truth") is True and record.get("authority") == "reviewed_record"),
        "accepted_truth": bool(record.get("accepted_truth") is True),
        "review_required": bool(record.get("review_required", record.get("status") != "reviewed")),
        "reviewed_record_id": (_string_list(record.get("reviewed_record_refs")) or [""])[0],
        "review_state": str(record.get("review_state") or ""),
        "artifact_verified": bool(record.get("artifact_verified") is True),
        "provenance": dict(record.get("provenance") or {}),
        "index_document_id": str(record.get("preview_record_id") or ""),
        "why_matched": _string_list(record.get("why_matched")),
        "why_ranked": _string_list(record.get("why_ranked")),
        "permitted_actions": _string_list(record.get("permitted_actions")),
        "forbidden_actions": _string_list(record.get("forbidden_actions")),
        "synthetic": bool(record.get("synthetic") is True),
        "source_family": str(record.get("source_family") or ""),
    }


def load_preview_manifest(index: str | Path) -> dict[str, Any]:
    path = Path(index)
    if not path.is_file():
        raise PreviewIndexError(f"preview index manifest not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PreviewIndexError(f"preview index manifest is not valid JSON: {exc.msg}") from exc
    if not isinstance(payload, Mapping):
        raise PreviewIndexError("preview index manifest must be an object")
    return dict(payload)


def _records_from_reviewed_records(path: Path) -> list[dict[str, Any]]:
    records = []
    for row in _load_jsonl(path):
        record_id = str(row.get("reviewed_record_id") or row.get("id") or "")
        review_refs = _string_list(row.get("review_refs")) or _string_list(row.get("review_event_refs"))
        if not record_id or not review_refs or row.get("accepted_truth") is not True:
            raise PreviewIndexError("reviewed records require reviewed_record_id, review refs, and accepted_truth true")
        records.append(
            _preview_record(
                semantic_type="reviewed_record",
                status="reviewed",
                authority="reviewed_record",
                title=str(row.get("title") or record_id),
                summary=str(row.get("summary") or "Reviewed local record."),
                normalized_search_text=_join_text(row.get("title"), row.get("summary"), row.get("query_hints")),
                matched_query_terms=[],
                why_matched=["reviewed record title and summary are indexed"],
                why_ranked=["reviewed authority is explicit"],
                uncertainty=_string_list(row.get("uncertainty")),
                missing_information=_string_list(row.get("missing_information")),
                source_refs=_string_list(row.get("source_refs")) or _string_list(row.get("source_hints")),
                evidence_refs=_string_list(row.get("evidence_refs")) or _string_list(row.get("evidence_hints")),
                reviewed_record_refs=[record_id],
                review_refs=review_refs,
                source_family=str(row.get("source_family") or "local_review"),
                accepted_truth=True,
                artifact_verified=bool(row.get("artifact_verified") is True),
                review_required=False,
                synthetic=False,
                provenance={"adapter": "reviewed_record", "input_path": _safe_label(path)},
            )
        )
    return records


def _records_from_candidates(
    manifest_path: Path,
    candidates: Sequence[Mapping[str, Any]],
    evidence_by_candidate: Mapping[str, Sequence[Mapping[str, Any]]],
    source_records: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    records = []
    for candidate in candidates:
        candidate_id = str(candidate.get("candidate_id") or "")
        source_refs = _string_list(candidate.get("source_observation_refs"))
        evidence_refs = _string_list(candidate.get("evidence_preview_refs"))
        related_evidence = list(evidence_by_candidate.get(candidate_id, []))
        evidence_refs.extend(str(item.get("evidence_summary_id")) for item in related_evidence if item.get("evidence_summary_id"))
        missing = ["human review before promotion"]
        if not related_evidence:
            missing.append("evidence summary")
        if not source_refs:
            missing.append("source observation reference")
        query_terms = _string_list(candidate.get("query_seed_refs"))
        title = str(candidate.get("normalized_title") or candidate_id)
        summary = _candidate_summary(candidate, related_evidence)
        provider_modes = _string_list(candidate.get("provider_mode_refs"))
        synthetic = "synthetic" in provider_modes
        records.append(
            _preview_record(
                semantic_type="candidate",
                status="candidate",
                authority="candidate_only",
                title=title,
                summary=summary,
                normalized_search_text=_join_text(title, summary, query_terms, candidate.get("normalized_type_hints")),
                matched_query_terms=query_terms,
                why_matched=["candidate title, query seed, and evidence summary text are indexed"],
                why_ranked=["candidate authority is provisional", "evidence count may help ranking but cannot promote authority"],
                uncertainty=_candidate_uncertainty(candidate, related_evidence),
                missing_information=missing,
                source_refs=source_refs,
                evidence_refs=sorted(set(evidence_refs)),
                candidate_refs=[candidate_id],
                run_refs=[],
                workunit_refs=[],
                source_family=str(candidate.get("source_family") or "unknown"),
                review_state=str(candidate.get("review_state") or "unreviewed"),
                synthetic=synthetic,
                provenance={
                    "adapter": "candidate_delta",
                    "input_path": _safe_label(manifest_path),
                    "source_records_available": sum(1 for ref in source_refs if ref in source_records),
                },
            )
        )
    return records


def _records_from_evidence(manifest_path: Path, evidence_records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for evidence in evidence_records:
        evidence_id = str(evidence.get("evidence_summary_id") or "")
        evidence_type = str(evidence.get("evidence_type") or "other")
        support = str(evidence.get("support_posture") or "unknown")
        status = "mention_only"
        authority = "evidence_summary_only"
        if "near-miss" in evidence_type:
            status = "near_miss"
        elif "absence" in evidence_type:
            status = "absence"
            authority = "absence_finding"
        elif support == "insufficient":
            status = "need"
        elif support == "source_unavailable":
            status = "unavailable"
        title = str(evidence.get("proposition") or evidence_id or evidence_type)
        summary = str(evidence.get("normalized_support_summary") or evidence.get("proposition") or evidence_type)
        missing = _string_list(evidence.get("uncertainty"))
        if status == "absence" and not _string_list(evidence.get("absence_or_near_miss_flags")):
            missing.append("absence scope or reason")
        if not missing:
            missing.append("evidence summary is not accepted truth")
        records.append(
            _preview_record(
                semantic_type="evidence_summary",
                status=status,
                authority=authority,
                title=title,
                summary=summary,
                normalized_search_text=_join_text(title, summary, evidence.get("query_seed_refs"), evidence_type, support),
                matched_query_terms=_string_list(evidence.get("query_seed_refs")),
                why_matched=["evidence proposition and support summary are indexed"],
                why_ranked=["evidence summary authority remains provisional"],
                uncertainty=missing,
                missing_information=missing if status in {"need", "absence", "unavailable"} else [],
                source_refs=_string_list(evidence.get("source_observation_refs")),
                evidence_refs=[evidence_id] if evidence_id else [],
                candidate_refs=_string_list(evidence.get("candidate_refs")),
                source_family=str(evidence.get("source_family") or "unknown"),
                review_state=str(evidence.get("review_state") or "unreviewed"),
                synthetic=False,
                provenance={"adapter": "evidence_delta", "input_path": _safe_label(manifest_path), "evidence_type": evidence_type},
            )
        )
    return records


def _records_from_source_observations(path: Path, observations: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for observation in observations:
        observation_id = str(observation.get("observation_id") or "")
        query = str(observation.get("query_seed") or "")
        metadata = observation.get("normalized_metadata") if isinstance(observation.get("normalized_metadata"), Mapping) else {}
        transport = str(observation.get("transport_status") or "")
        status = "unavailable" if transport in {"zero_results", "unavailable", "failed"} else "mention_only"
        records.append(
            _preview_record(
                semantic_type="source_observation",
                status=status,
                authority="source_observation_only",
                title=query or observation_id,
                summary=f"Source observation from {observation.get('source_id') or observation.get('source_family') or 'source'}.",
                normalized_search_text=_join_text(query, observation_id, metadata),
                matched_query_terms=[query] if query else [],
                why_matched=["source observation query and metadata fields are indexed"],
                why_ranked=["source observation is evidence support, not accepted truth"],
                uncertainty=_string_list(observation.get("limitations")) or ["source observation is not reviewed truth"],
                missing_information=[] if status != "unavailable" else ["available source response"],
                source_refs=[observation_id] if observation_id else [],
                source_family=str(observation.get("source_family") or "unknown"),
                run_refs=_string_list([observation.get("run_id")]),
                workunit_refs=_string_list([observation.get("work_unit_id")]),
                review_state=str(observation.get("review_state") or "unreviewed"),
                synthetic=str(observation.get("provider_mode") or "") == "synthetic",
                provenance={"adapter": "source_observation_delta", "input_path": _safe_label(path)},
            )
        )
    return records


def _records_from_runs_root(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    if not root.exists():
        return records, sources, [{"path": _safe_label(root), "reason": "runs_root_missing"}]
    for child in sorted(root.iterdir(), key=lambda item: item.name):
        if not child.is_dir():
            continue
        manifest_path = child / "run_manifest.json"
        if not manifest_path.is_file():
            continue
        validation = validate_run_bundle(child, strict=True)
        if validation.get("status") != "valid":
            skipped.append({"path": _safe_label(child), "reason": "invalid_run_bundle", "errors": list(validation.get("errors", []))})
            continue
        run_manifest = _load_json(manifest_path)
        lane_snapshot = _load_json(child / "lane_snapshot.json")
        result = _load_json(child / "result.json")
        run_state = _load_json(child / "run_state.json")
        workunits = _load_jsonl(child / "workunits.jsonl")
        records.extend(_records_from_run_bundle(child, run_manifest, lane_snapshot, result, run_state, workunits))
        sources.append(_source_entry("resolution_run_bundle", manifest_path))
    return records, sources, skipped


def _records_from_run_bundle(
    run_dir: Path,
    manifest: Mapping[str, Any],
    lane_snapshot: Mapping[str, Any],
    result: Mapping[str, Any],
    run_state: Mapping[str, Any],
    workunits: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    run_id = str(manifest.get("run_id") or run_state.get("run_id") or run_dir.name)
    synthetic = bool(manifest.get("synthetic") is True or run_state.get("synthetic") is True)
    records: list[dict[str, Any]] = []
    lanes = ((lane_snapshot.get("lane_page") or {}).get("lanes") if isinstance(lane_snapshot.get("lane_page"), Mapping) else []) or []
    for lane in lanes:
        if not isinstance(lane, Mapping):
            continue
        lane_kind = str(lane.get("lane_kind") or "unknown")
        for item in lane.get("items") or []:
            if not isinstance(item, Mapping):
                continue
            status = _status_from_lane(lane_kind, synthetic=synthetic)
            title = str(item.get("title") or item.get("summary") or lane_kind.replace("_", " ").title())
            summary = str(item.get("summary") or lane.get("summary") or title)
            source_refs = _string_list(item.get("source_record_ids")) + _string_list(item.get("source_refs"))
            evidence_refs = _string_list(item.get("evidence_refs"))
            records.append(
                _preview_record(
                    semantic_type="resolution_run_lane_item",
                    status=status,
                    authority="synthetic_test" if synthetic else "run_projection",
                    title=title,
                    summary=summary,
                    normalized_search_text=_join_text(title, summary, lane_kind, manifest.get("query"), item),
                    matched_query_terms=[str(manifest.get("query") or "")],
                    why_matched=["run lane title, summary, and query are indexed"],
                    why_ranked=["ResolutionRun lane output is projection authority only"],
                    uncertainty=_string_list(item.get("uncertainty")) or _string_list(item.get("limitations")) or ["run projection is not accepted truth"],
                    missing_information=_string_list(item.get("missing_information")),
                    source_refs=source_refs,
                    evidence_refs=evidence_refs,
                    run_refs=[run_id],
                    workunit_refs=_workunit_refs_for_lane(workunits, lane_kind),
                    source_family=str(item.get("source_family") or "resolution_run"),
                    review_state="unreviewed" if status != "reviewed" else "accepted",
                    synthetic=synthetic,
                    provenance={"adapter": "resolution_run_bundle", "input_path": _safe_label(run_dir), "lane_kind": lane_kind},
                )
            )
    for record in result.get("records") or []:
        if isinstance(record, Mapping):
            title = str(record.get("title") or record.get("record_id") or "Synthetic result")
            records.append(
                _preview_record(
                    semantic_type="resolution_run_result",
                    status=str(record.get("status") or "candidate") if str(record.get("status") or "") in CORE_STATUSES else "candidate",
                    authority="synthetic_test" if synthetic else "run_projection",
                    title=title,
                    summary=str(record.get("summary") or "ResolutionRun result record."),
                    normalized_search_text=_join_text(title, record, manifest.get("query")),
                    matched_query_terms=[str(manifest.get("query") or "")],
                    why_matched=["run result record and query are indexed"],
                    why_ranked=["result record is a run projection"],
                    uncertainty=["not accepted truth"],
                    missing_information=["review before promotion"],
                    run_refs=[run_id],
                    source_family=str(record.get("source_family") or "resolution_run"),
                    synthetic=synthetic,
                    provenance={"adapter": "resolution_run_bundle_result", "input_path": _safe_label(run_dir)},
                )
            )
    if not records:
        state = str(manifest.get("current_state") or run_state.get("state") or "unknown")
        records.append(
            _preview_record(
                semantic_type="resolution_run_state",
                status="policy_blocked" if state == "policy_blocked" else "unknown",
                authority="synthetic_test" if synthetic else "run_projection",
                title=f"ResolutionRun {state}",
                summary=f"Run {run_id} ended with state {state}.",
                normalized_search_text=_join_text(manifest.get("query"), state, run_id),
                matched_query_terms=[str(manifest.get("query") or "")],
                why_matched=["run state and query are indexed"],
                why_ranked=["run state is projection authority only"],
                uncertainty=["run state is not accepted truth"],
                missing_information=[],
                run_refs=[run_id],
                synthetic=synthetic,
                provenance={"adapter": "resolution_run_state", "input_path": _safe_label(run_dir)},
            )
        )
    return records


def _preview_record(
    *,
    semantic_type: str,
    status: str,
    authority: str,
    title: str,
    summary: str,
    normalized_search_text: str,
    matched_query_terms: Sequence[str],
    why_matched: Sequence[str],
    why_ranked: Sequence[str],
    uncertainty: Sequence[str],
    missing_information: Sequence[str],
    source_refs: Sequence[str] = (),
    evidence_refs: Sequence[str] = (),
    candidate_refs: Sequence[str] = (),
    reviewed_record_refs: Sequence[str] = (),
    run_refs: Sequence[str] = (),
    workunit_refs: Sequence[str] = (),
    review_refs: Sequence[str] = (),
    source_family: str = "unknown",
    provenance: Mapping[str, Any] | None = None,
    privacy_posture: str = "local_private",
    synthetic: bool = False,
    accepted_truth: bool = False,
    artifact_verified: bool = False,
    review_required: bool = True,
    review_state: str = "unreviewed",
    permitted_actions: Sequence[str] = DEFAULT_PERMITTED_ACTIONS,
    forbidden_actions: Sequence[str] = DEFAULT_FORBIDDEN_ACTIONS,
    warnings: Sequence[str] = (),
    limitations: Sequence[str] = (),
    gaps: Sequence[str] = (),
) -> dict[str, Any]:
    safe_status = status if status in CORE_STATUSES else "unknown"
    safe_authority = authority if authority in CORE_AUTHORITIES else "unknown"
    base = {
        "schema_version": PREVIEW_RECORD_SCHEMA_VERSION,
        "semantic_type": semantic_type,
        "status": safe_status,
        "authority": safe_authority,
        "title": title,
        "summary": summary,
        "normalized_search_text": _normalize_text(normalized_search_text),
        "matched_query_terms": sorted(set(_clean_strings(matched_query_terms))),
        "why_matched": sorted(set(_clean_strings(why_matched))),
        "why_ranked": sorted(set(_clean_strings(why_ranked))),
        "uncertainty": sorted(set(_clean_strings(uncertainty))),
        "missing_information": sorted(set(_clean_strings(missing_information))),
        "source_refs": sorted(set(_clean_strings(source_refs))),
        "evidence_refs": sorted(set(_clean_strings(evidence_refs))),
        "candidate_refs": sorted(set(_clean_strings(candidate_refs))),
        "reviewed_record_refs": sorted(set(_clean_strings(reviewed_record_refs))),
        "run_refs": sorted(set(_clean_strings(run_refs))),
        "workunit_refs": sorted(set(_clean_strings(workunit_refs))),
        "review_refs": sorted(set(_clean_strings(review_refs))),
        "source_family": source_family or "unknown",
        "provenance": dict(provenance or {}),
        "privacy_posture": privacy_posture,
        "synthetic": bool(synthetic),
        "accepted_truth": bool(accepted_truth),
        "artifact_verified": bool(artifact_verified),
        "review_required": bool(review_required),
        "review_state": review_state,
        "permitted_actions": list(permitted_actions),
        "forbidden_actions": list(forbidden_actions),
        "warnings": sorted(set(_clean_strings(warnings))),
        "limitations": sorted(set(_clean_strings(limitations))),
        "gaps": sorted(set(_clean_strings(gaps))),
        "record_state": "reviewed" if safe_status == "reviewed" else "preview",
        "reviewed_record_id": (_clean_strings(reviewed_record_refs) or [""])[0],
        "review_event_id": (_clean_strings(review_refs) or [""])[0],
        "non_verified_reason": "" if accepted_truth else "preview record is not accepted truth",
        "verified": bool(accepted_truth and safe_authority == "reviewed_record"),
        "source_hints": sorted(set(_clean_strings(source_refs))),
        "evidence_hints": sorted(set(_clean_strings(evidence_refs))),
        "safe_next_action": _safe_next_action(safe_status),
    }
    content_hash = _hash(base)
    base["deterministic_content_hash"] = f"sha256:{content_hash}"
    base["preview_record_id"] = f"preview:{safe_authority}:{content_hash[:24]}"
    base["id"] = base["preview_record_id"]
    return base


def _record_validation_errors(records: Sequence[Mapping[str, Any]], *, strict: bool) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for index, record in enumerate(records):
        record_id = str(record.get("preview_record_id") or "")
        label = record_id or f"record[{index}]"
        if not record_id:
            errors.append(f"{label}: preview_record_id is required")
        if record_id in seen:
            errors.append(f"duplicate preview_record_id: {record_id}")
        seen.add(record_id)
        status = str(record.get("status") or "")
        authority = str(record.get("authority") or "")
        if status not in CORE_STATUSES:
            errors.append(f"{label}: unsupported status {status}")
        if authority not in CORE_AUTHORITIES:
            errors.append(f"{label}: unsupported authority {authority}")
        if status == "reviewed" and authority != "reviewed_record":
            errors.append(f"{label}: reviewed status requires reviewed_record authority")
        if authority == "reviewed_record" and not _string_list(record.get("reviewed_record_refs")):
            errors.append(f"{label}: reviewed_record authority requires reviewed_record_refs")
        if record.get("accepted_truth") is True and authority != "reviewed_record":
            errors.append(f"{label}: accepted_truth requires reviewed_record authority")
        if record.get("artifact_verified") is True and record.get("accepted_truth") is not True:
            errors.append(f"{label}: artifact_verified requires accepted_truth")
        if authority in {"candidate_only", "evidence_summary_only", "source_observation_only"} and record.get("accepted_truth") is True:
            errors.append(f"{label}: provisional authority cannot set accepted_truth")
        if status == "absence" and not (_string_list(record.get("missing_information")) or _string_list(record.get("uncertainty"))):
            errors.append(f"{label}: absence status requires coverage or reason information")
        if record.get("synthetic") is True and authority == "reviewed_record":
            errors.append(f"{label}: synthetic record cannot have reviewed_record authority")
        if not _string_list(record.get("permitted_actions")):
            errors.append(f"{label}: permitted_actions are required")
        if not _string_list(record.get("forbidden_actions")):
            errors.append(f"{label}: forbidden_actions are required")
        if status != "reviewed" and not _string_list(record.get("uncertainty")):
            errors.append(f"{label}: non-reviewed record must explain uncertainty")
        if strict and _private_path_found(record):
            errors.append(f"{label}: private path-like value is forbidden")
    return errors


def _load_candidate_records(manifest_path: Path) -> list[dict[str, Any]]:
    manifest = _load_json(manifest_path)
    file_name = str(manifest.get("candidate_file") or "candidate_index_delta.jsonl")
    return _load_jsonl(manifest_path.parent / file_name)


def _load_evidence_summary_records(manifest_path: Path) -> list[dict[str, Any]]:
    manifest = _load_json(manifest_path)
    file_name = str(manifest.get("evidence_summary_file") or "evidence_summaries.jsonl")
    return _load_jsonl(manifest_path.parent / file_name)


def _load_source_observation_records(manifest_path: Path) -> dict[str, dict[str, Any]]:
    manifest = _load_json(manifest_path)
    file_name = str(manifest.get("observation_file") or "source_observations.jsonl")
    records = _load_jsonl(manifest_path.parent / file_name)
    return {str(item.get("observation_id") or ""): item for item in records if item.get("observation_id")}


def _load_records_for_manifest(
    manifest: Mapping[str, Any],
    *,
    index_root: Path,
    errors: list[str] | None = None,
) -> list[dict[str, Any]]:
    record_file = _record_file_for_manifest(manifest, index_root=index_root)
    try:
        return _load_jsonl(record_file)
    except (OSError, json.JSONDecodeError, PreviewIndexError) as exc:
        if errors is not None:
            errors.append(f"could not load preview records: {type(exc).__name__}")
            return []
        raise


def _record_file_for_manifest(manifest: Mapping[str, Any], *, index_root: Path) -> Path:
    generation_path = str(manifest.get("generation_path") or "")
    record_file = str(manifest.get("record_file") or "preview_records.jsonl")
    if not generation_path:
        raise PreviewIndexError("generation_path is required")
    return _safe_child(index_root, generation_path) / record_file


def _index_root_from_manifest_path(path: Path, manifest: Mapping[str, Any]) -> Path:
    if path.name == "current.json":
        return path.parent
    generation_path = str(manifest.get("generation_path") or "")
    if path.name == "manifest.json" and generation_path:
        # .../<root>/generations/<id>/manifest.json
        return path.parents[2]
    return path.parent


def _deduplicate_records(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    by_hash: dict[str, dict[str, Any]] = {}
    for record in records:
        item = dict(record)
        key = str(item.get("deterministic_content_hash") or _hash(item))
        if key in by_hash:
            existing = by_hash[key]
            existing["source_refs"] = sorted(set(_string_list(existing.get("source_refs")) + _string_list(item.get("source_refs"))))
            existing["evidence_refs"] = sorted(set(_string_list(existing.get("evidence_refs")) + _string_list(item.get("evidence_refs"))))
            existing.setdefault("merge_group_id", f"merge:{_hash({'key': key})[:16]}")
            item["duplicate_of"] = existing["preview_record_id"]
            continue
        by_hash[key] = item
    return list(by_hash.values())


def _assert_no_duplicate_ids(records: Sequence[Mapping[str, Any]]) -> None:
    ids = [str(item.get("preview_record_id") or "") for item in records]
    duplicates = sorted(item for item, count in Counter(ids).items() if count > 1)
    if duplicates:
        raise PreviewIndexError(f"duplicate PreviewRecord IDs: {', '.join(duplicates[:5])}")


def _stats(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "eureka.e2e_preview_index_stats.v0",
        "record_count": len(records),
        "status_counts": _counts(item.get("status") for item in records),
        "authority_counts": _counts(item.get("authority") for item in records),
        "source_family_counts": _counts(item.get("source_family") for item in records),
        "synthetic_count": sum(1 for item in records if item.get("synthetic") is True),
        "reviewed_count": sum(1 for item in records if item.get("status") == "reviewed"),
        "candidate_count": sum(1 for item in records if item.get("status") == "candidate"),
    }


def _source_entry(kind: str, path: Path) -> dict[str, Any]:
    return {
        "kind": kind,
        "path": _safe_label(path),
        "sha256": _file_hash(path) if path.is_file() else "",
    }


def _preview_index_id(records: Sequence[Mapping[str, Any]], sources: Sequence[Mapping[str, Any]]) -> str:
    material = {
        "records": [item.get("deterministic_content_hash") for item in records],
        "sources": sources,
        "schema": PREVIEW_INDEX_SCHEMA_VERSION,
    }
    return f"preview-index-{_hash(material)[:24]}"


def _score_record(record: Mapping[str, Any], query: str) -> tuple[int, list[str], list[str]]:
    query_text = _normalize_text(query)
    query_tokens = _query_tokens(query)
    if not query_text:
        return 0, [], []
    title = _normalize_text(record.get("title"))
    searchable = str(record.get("normalized_search_text") or "")
    score = 0
    why_matched: list[str] = []
    why_ranked: list[str] = []
    if title == query_text:
        score += 1000
        why_matched.append("exact normalized title match")
    elif query_text in title:
        score += 800
        why_matched.append("query phrase appears in title")
    elif query_text in searchable:
        score += 650
        why_matched.append("query phrase appears in indexed text")
    token_matches = [token for token in query_tokens if token in searchable]
    if token_matches:
        score += 45 * len(token_matches)
        why_matched.append("matched query terms: " + ", ".join(token_matches))
    if not why_matched:
        return 0, [], []
    authority = str(record.get("authority") or "unknown")
    status = str(record.get("status") or "unknown")
    score += {
        "reviewed_record": 120,
        "candidate_only": 60,
        "evidence_summary_only": 30,
        "source_observation_only": 20,
        "absence_finding": 10,
        "run_projection": 5,
        "synthetic_test": 0,
    }.get(authority, 0)
    why_ranked.append(f"authority={authority}")
    if status == "reviewed":
        why_ranked.append("reviewed status is explicit")
    if status == "near_miss":
        score -= 40
        why_ranked.append("near-miss penalty")
    if status in {"unavailable", "policy_blocked"}:
        score -= 80
        why_ranked.append(f"{status} lane retained but ranked lower")
    if record.get("missing_information"):
        score -= min(40, 5 * len(_string_list(record.get("missing_information"))))
        why_ranked.append("missing information penalty")
    if record.get("synthetic") is True:
        score -= 20
        why_ranked.append("synthetic test record included by explicit filter")
    return max(score, 0), why_matched, why_ranked


def _lanes(records: Sequence[Mapping[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    lanes: dict[str, list[dict[str, Any]]] = {
        "reviewed": [],
        "candidates": [],
        "near_misses": [],
        "needs": [],
        "absence_or_next_steps": [],
        "blocked_or_unavailable": [],
        "other": [],
    }
    for record in records:
        lane = STATUS_TO_LANE.get(str(record.get("status") or ""), "other")
        lanes[lane].append(dict(record))
    return lanes


def _status_from_lane(lane_kind: str, *, synthetic: bool) -> str:
    if lane_kind == "reviewed_local_results":
        return "candidate" if synthetic else "reviewed"
    if lane_kind in {"local_candidate_results", "ia_metadata_candidates"}:
        return "candidate"
    if lane_kind == "known_absence":
        return "absence"
    if lane_kind == "near_misses":
        return "near_miss"
    if lane_kind in {"deferred_deepening", "future_extraction_work"}:
        return "need"
    if lane_kind == "blocked_actions":
        return "policy_blocked"
    if lane_kind == "source_cache_hits":
        return "mention_only"
    if lane_kind == "running_workunits":
        return "unknown"
    return "unknown"


def _candidate_summary(candidate: Mapping[str, Any], evidence: Sequence[Mapping[str, Any]]) -> str:
    title = str(candidate.get("normalized_title") or candidate.get("candidate_id") or "Candidate")
    if evidence:
        return f"{title}; {len(evidence)} provisional evidence summary record(s) are linked."
    return f"{title}; candidate remains provisional and unreviewed."


def _candidate_uncertainty(candidate: Mapping[str, Any], evidence: Sequence[Mapping[str, Any]]) -> list[str]:
    uncertainty = ["candidate is provisional", "review is required before accepted use"]
    uncertainty.extend(_string_list(candidate.get("limitations")))
    for item in evidence[:3]:
        uncertainty.extend(_string_list(item.get("uncertainty")))
    return sorted(set(uncertainty))


def _workunit_refs_for_lane(workunits: Sequence[Mapping[str, Any]], lane_kind: str) -> list[str]:
    if lane_kind != "running_workunits":
        return []
    return _clean_strings(str(item.get("workunit_id") or "") for item in workunits)


def _orphan_ref_count(records: Sequence[Mapping[str, Any]]) -> int:
    return sum(1 for item in records if item.get("authority") == "candidate_only" and not _string_list(item.get("source_refs")))


def _safe_next_action(status: str) -> str:
    if status == "reviewed":
        return "inspect reviewed lineage before reuse"
    if status == "candidate":
        return "review candidate evidence before promotion"
    if status == "near_miss":
        return "compare constraints and refine the query"
    if status == "need":
        return "collect missing source evidence"
    if status == "absence":
        return "inspect coverage before treating as absence"
    if status == "policy_blocked":
        return "wait for the relevant policy or operator gate"
    if status == "unavailable":
        return "retry later or add another source"
    return "inspect preview record and provenance"


def _load_current_generation(root: Path) -> str | None:
    current = root / "current.json"
    if not current.is_file():
        return None
    try:
        payload = json.loads(current.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return str(payload.get("generation_id") or "") or None


def _count_delta(left: Any, right: Any) -> dict[str, int]:
    left_map = left if isinstance(left, Mapping) else {}
    right_map = right if isinstance(right, Mapping) else {}
    keys = sorted(set(left_map) | set(right_map))
    return {str(key): int(right_map.get(key, 0) or 0) - int(left_map.get(key, 0) or 0) for key in keys}


def _private_path_found(value: Any) -> bool:
    text = json.dumps(value, sort_keys=True, ensure_ascii=True, default=str)
    return any(pattern.search(text) for pattern in PRIVATE_PATH_PATTERNS)


def _safe_child(root: Path, child: str) -> Path:
    safe_child = str(child or "").replace("\\", "/")
    if safe_child.startswith("/") or ".." in safe_child.split("/"):
        raise PreviewIndexError("unsafe preview index path")
    resolved_root = root.resolve()
    path = (resolved_root / safe_child).resolve()
    if resolved_root != path and resolved_root not in path.parents:
        raise PreviewIndexError("preview path escapes output root")
    return path


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    _atomic_write_text(path, json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n")


def _write_jsonl(path: Path, records: Sequence[Mapping[str, Any]]) -> None:
    _atomic_write_text(path, "".join(json.dumps(record, sort_keys=True, ensure_ascii=True) + "\n" for record in records))


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent, newline="\n") as handle:
        handle.write(text)
        temp_name = handle.name
    os.replace(temp_name, path)


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PreviewIndexError(f"missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise PreviewIndexError(f"invalid JSON file {path}: {exc.msg}") from exc
    if not isinstance(payload, Mapping):
        raise PreviewIndexError(f"JSON file must contain an object: {path}")
    return dict(payload)


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as exc:
        raise PreviewIndexError(f"missing JSONL file: {path}") from exc
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise PreviewIndexError(f"{path}:{line_number}: invalid JSONL row: {exc.msg}") from exc
        if not isinstance(payload, Mapping):
            raise PreviewIndexError(f"{path}:{line_number}: JSONL row must be an object")
        records.append(dict(payload))
    return records


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str).encode("utf-8")).hexdigest()


def _counts(values: Iterable[Any]) -> dict[str, int]:
    counter = Counter(str(value or "unknown") for value in values)
    return {key: counter[key] for key in sorted(counter)}


def _safe_label(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve())).replace("\\", "/")
    except ValueError:
        return f"external:{path.name}"


def _clean_strings(values: Iterable[Any]) -> list[str]:
    return [str(item) for item in values if item not in (None, "")]


def _string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value else []
    if not isinstance(value, (list, tuple, set)):
        return []
    return _clean_strings(value)


def _join_text(*parts: Any) -> str:
    values: list[str] = []
    for part in parts:
        if part in (None, ""):
            continue
        if isinstance(part, Mapping):
            values.extend(str(value) for value in part.values() if value not in (None, ""))
        elif isinstance(part, (list, tuple, set)):
            values.extend(str(item) for item in part if item not in (None, ""))
        else:
            values.append(str(part))
    return _normalize_text(" ".join(values))


def _normalize_text(value: Any) -> str:
    return " ".join(str(value or "").casefold().split())[:8000]


def _query_tokens(query: str) -> list[str]:
    return sorted(set(token for token in re.findall(r"[a-z0-9]+", _normalize_text(query)) if token not in STOPWORDS))

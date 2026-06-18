"""Build governed local evidence-summary deltas from IA source-wave outputs."""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "eureka.evidence_ledger_summary_delta.v0"
EVIDENCE_SUMMARY_SCHEMA_VERSION = "eureka.evidence_summary_record.v0"
REPORT_SCHEMA_VERSION = "eureka.evidence_ledger_summary_report.v0"
SOURCE_OBSERVATION_SCHEMA_VERSION = "eureka.source_observation_cache_delta.v0"
CANDIDATE_SCHEMA_VERSION = "eureka.candidate_index_refresh_delta.v0"
SOURCE_FAMILY = "ia_metadata"
DEFAULT_LICENSE_POSTURE = "restricted_source_available"
DEFAULT_RECOMMENDED_NEXT_TASK = "REVIEW-IA-CANDIDATES-BATCH-00"

SOURCE_OBSERVATION_FILE_FALLBACK = "source_observations.jsonl"
CANDIDATE_FILE_FALLBACK = "candidate_index_delta.jsonl"
EVIDENCE_SUMMARY_FILE_NAME = "evidence_summaries.jsonl"
MANIFEST_FILE_NAME = "evidence_summary_delta_manifest.json"
REPORT_FILE_NAME = "EVIDENCE_LEDGER_SUMMARY_REPORT.md"

ALLOWED_EVIDENCE_TYPES = {
    "identity clue",
    "title/name clue",
    "version clue",
    "date/time clue",
    "platform clue",
    "object-type clue",
    "representation/member clue",
    "source-location clue",
    "compatibility clue",
    "provenance clue",
    "absence clue",
    "near-miss clue",
    "conflicting-metadata clue",
    "transport/unavailability clue",
    "other typed source-supported clue",
}
ALLOWED_SUPPORT_POSTURES = {
    "supports_clue",
    "metadata_mention",
    "candidate_support",
    "conflicting",
    "insufficient",
    "source_unavailable",
    "unknown",
}
ALLOWED_RIGHTS_SAFETY_POSTURES = {
    "unknown",
    "not_assessed",
    "unknown_not_assessed",
}

REQUIRED_MANIFEST_FIELDS = {
    "delta_id",
    "source_family",
    "generated_at",
    "input_source_observation_delta",
    "input_source_observation_delta_hash",
    "input_candidate_index_delta",
    "input_candidate_index_delta_hash",
    "source_observation_count",
    "candidate_count",
    "evidence_summary_count",
    "deduplicated_evidence_summary_count",
    "query_count",
    "provider_modes",
    "evidence_type_counts",
    "support_posture_counts",
    "contradiction_count",
    "absence_near_miss_count",
    "insufficient_support_count",
    "source_unavailable_count",
    "unsafe_record_count",
    "redacted_error_count",
    "orphan_candidate_ref_count",
    "orphan_source_observation_ref_count",
    "no_downloads",
    "no_file_fetch",
    "no_wayback_replay",
    "no_public_fanout",
    "reviewed_master_mutation",
    "public_index_mutation",
    "candidate_index_store_mutation",
    "evidence_summary_delta_written",
    "evidence_ledger_store_mutation",
    "review_promotion_mutation",
    "accepted_truth_created",
    "license_posture",
    "evidence_summary_file",
    "evidence_summary_file_hash",
    "previous_delta_id",
    "previous_delta_path",
    "diff_status",
    "validation_status",
    "blockers",
    "recommended_next_task",
}

REQUIRED_SUMMARY_FIELDS = {
    "evidence_summary_id",
    "evidence_type",
    "evidence_status",
    "authority",
    "proposition",
    "source_family",
    "source_observation_refs",
    "candidate_refs",
    "query_seed_refs",
    "provider_mode_refs",
    "source_locator_refs",
    "supporting_fields",
    "normalized_support_summary",
    "support_posture",
    "support_strength_hint",
    "uncertainty",
    "contradiction_flags",
    "absence_or_near_miss_flags",
    "review_required",
    "review_state",
    "rights_posture",
    "safety_posture",
    "generated_at",
    "deterministic_hash",
    "input_candidate_delta_id",
    "input_source_observation_delta_id",
    "safety_flags",
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
    "evidence_ledger_store_mutation",
    "evidence_ledger_mutation",
    "evidence_ledger_materialized",
    "review_promotion_mutation",
    "review_queue_mutated",
    "accepted_truth_created",
    "accepted_truth",
    "accepted_as_truth",
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

FORBIDDEN_CLAIM_PATTERNS = (
    re.compile(r"\bverified (?:artifact|fact|object|record|candidate)\b", re.IGNORECASE),
    re.compile(r"\b(?:is|are|was|were) verified\b", re.IGNORECASE),
    re.compile(r"\baccepted truth\b", re.IGNORECASE),
    re.compile(r"\bauthoritative truth\b", re.IGNORECASE),
    re.compile(r"\bproven (?:artifact|fact|object|record|candidate)\b", re.IGNORECASE),
    re.compile(r"\bright[s]? (?:are )?cleared\b", re.IGNORECASE),
    re.compile(r"\bright[s]?[-_ ]cleared\b", re.IGNORECASE),
    re.compile(r"\bmalware safe\b", re.IGNORECASE),
    re.compile(r"\bsafe to (?:download|install|execute|run)\b", re.IGNORECASE),
    re.compile(r"\bproduction[- ]ready\b", re.IGNORECASE),
)

PRIVATE_PATH_PATTERNS = (
    re.compile(r"\b[A-Za-z]:\\Users\\[^\\\s]+", re.IGNORECASE),
    re.compile(r"/home/[^/\s]+", re.IGNORECASE),
    re.compile(r"/Users/[^/\s]+", re.IGNORECASE),
    re.compile(r"\.aide\.local[/\\]", re.IGNORECASE),
    re.compile(r"\.cache[/\\]", re.IGNORECASE),
    re.compile(r"\.local[/\\]", re.IGNORECASE),
)


class EvidenceLedgerSummaryError(ValueError):
    """Raised when an evidence-summary delta is unsafe or invalid."""


def load_source_observation_delta_manifest(path: str | Path) -> dict[str, Any]:
    manifest = _load_json_object(Path(path), "source-observation delta manifest")
    errors = _source_observation_manifest_errors(manifest)
    if errors:
        raise EvidenceLedgerSummaryError("; ".join(errors))
    return manifest


def load_candidate_index_delta_manifest(path: str | Path) -> dict[str, Any]:
    manifest = _load_json_object(Path(path), "candidate-index delta manifest")
    errors = _candidate_index_manifest_errors(manifest)
    if errors:
        raise EvidenceLedgerSummaryError("; ".join(errors))
    return manifest


def load_source_observations(
    manifest_path: str | Path,
    manifest: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    path = Path(manifest_path)
    active_manifest = dict(manifest or load_source_observation_delta_manifest(path))
    observation_path = path.parent / str(active_manifest.get("observation_file") or SOURCE_OBSERVATION_FILE_FALLBACK)
    records = _read_jsonl(observation_path, "source observations")
    expected_hash = str(active_manifest.get("observation_file_hash") or "")
    if expected_hash and expected_hash != f"sha256:{_file_hash(observation_path)}":
        raise EvidenceLedgerSummaryError("source observation file hash does not match source-observation manifest")
    errors = _source_observation_record_errors(records)
    if errors:
        raise EvidenceLedgerSummaryError("; ".join(errors))
    return records


def load_candidates(
    manifest_path: str | Path,
    manifest: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    path = Path(manifest_path)
    active_manifest = dict(manifest or load_candidate_index_delta_manifest(path))
    candidate_path = path.parent / str(active_manifest.get("candidate_file") or CANDIDATE_FILE_FALLBACK)
    records = _read_jsonl(candidate_path, "candidate-index delta")
    expected_hash = str(active_manifest.get("candidate_file_hash") or "")
    if expected_hash and expected_hash != f"sha256:{_file_hash(candidate_path)}":
        raise EvidenceLedgerSummaryError("candidate file hash does not match candidate-index manifest")
    errors = _candidate_record_errors(records)
    if errors:
        raise EvidenceLedgerSummaryError("; ".join(errors))
    return records


def build_delta(
    *,
    source: str,
    source_observation_delta_path: str | Path,
    candidate_index_delta_path: str | Path,
    out_dir: str | Path,
) -> dict[str, Any]:
    normalized_source = _normalize_source(source)
    if normalized_source != SOURCE_FAMILY:
        raise EvidenceLedgerSummaryError(f"unsupported source: {source}")

    source_delta_path = Path(source_observation_delta_path)
    candidate_delta_path = Path(candidate_index_delta_path)
    source_manifest = load_source_observation_delta_manifest(source_delta_path)
    candidate_manifest = load_candidate_index_delta_manifest(candidate_delta_path)
    source_observations = load_source_observations(source_delta_path, source_manifest)
    candidates = load_candidates(candidate_delta_path, candidate_manifest)
    source_delta_hash = _file_hash(source_delta_path)
    candidate_delta_hash = _file_hash(candidate_delta_path)
    input_errors = _input_compatibility_errors(
        source_manifest=source_manifest,
        candidate_manifest=candidate_manifest,
        source_delta_hash=source_delta_hash,
        source_observations=source_observations,
        candidates=candidates,
    )
    if input_errors:
        raise EvidenceLedgerSummaryError("; ".join(input_errors))

    summaries = normalize_evidence_summaries(
        source_observations=source_observations,
        candidates=candidates,
        source_manifest=source_manifest,
        candidate_manifest=candidate_manifest,
        source_delta_hash=source_delta_hash,
        candidate_delta_hash=candidate_delta_hash,
    )
    summary_errors = _evidence_summary_record_errors(
        summaries,
        source_observation_ids={str(item.get("observation_id") or "") for item in source_observations},
        candidate_ids={str(item.get("candidate_id") or "") for item in candidates},
    )
    if summary_errors:
        raise EvidenceLedgerSummaryError("; ".join(summary_errors))

    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    summary_path = output / EVIDENCE_SUMMARY_FILE_NAME
    manifest_path = output / MANIFEST_FILE_NAME
    report_path = output / REPORT_FILE_NAME

    previous = _load_previous_manifest(manifest_path)
    _write_jsonl(summary_path, summaries)
    summary_hash = _file_hash(summary_path)
    manifest = build_evidence_summary_delta_manifest(
        source_manifest=source_manifest,
        candidate_manifest=candidate_manifest,
        source_delta_path=source_delta_path,
        candidate_delta_path=candidate_delta_path,
        source_delta_hash=source_delta_hash,
        candidate_delta_hash=candidate_delta_hash,
        source_observations=source_observations,
        candidates=candidates,
        summaries=summaries,
        summary_path=summary_path,
        summary_hash=summary_hash,
        previous=previous,
    )
    manifest_errors = validate_evidence_summary_delta_manifest(
        manifest,
        summaries=summaries,
        source_observations=source_observations,
        candidates=candidates,
    )
    if manifest_errors:
        raise EvidenceLedgerSummaryError("; ".join(manifest_errors))
    _write_json(manifest_path, manifest)
    report_path.write_text(render_markdown_summary(manifest, summaries=summaries), encoding="utf-8", newline="\n")
    return {
        "schema_version": "eureka.evidence_ledger_summary_delta_build_result.v0",
        "status": "PASS" if manifest["validation_status"] == "PASS" else "PASS_WITH_WARNINGS",
        "manifest": manifest,
        "manifest_path": _safe_path_label(manifest_path),
        "evidence_summary_path": _safe_path_label(summary_path),
        "report_path": _safe_path_label(report_path),
        "evidence_summary_count": len(summaries),
        "deduplicated_evidence_summary_count": len({str(item.get("evidence_summary_id", "")) for item in summaries}),
        "network_used": False,
        "provider_calls": False,
        "downloads": False,
        "file_fetch": False,
        "wayback_replay": False,
        "reviewed_master_mutation": False,
        "public_index_mutation": False,
        "candidate_index_store_mutation": False,
        "evidence_ledger_store_mutation": False,
        "review_promotion_mutation": False,
        "accepted_truth_created": False,
    }


def normalize_evidence_summaries(
    *,
    source_observations: Sequence[Mapping[str, Any]],
    candidates: Sequence[Mapping[str, Any]],
    source_manifest: Mapping[str, Any],
    candidate_manifest: Mapping[str, Any],
    source_delta_hash: str,
    candidate_delta_hash: str,
) -> list[dict[str, Any]]:
    generated_at = str(candidate_manifest.get("generated_at") or source_manifest.get("generated_at") or "")
    source_delta_id = str(source_manifest.get("delta_id") or "")
    candidate_delta_id = str(candidate_manifest.get("delta_id") or "")
    observations_by_id = {str(item.get("observation_id") or ""): dict(item) for item in source_observations}
    conflict_keys = _conflict_keys(candidates)
    summaries: list[dict[str, Any]] = []
    for candidate in sorted(candidates, key=lambda item: str(item.get("candidate_id") or "")):
        candidate_id = str(candidate.get("candidate_id") or "")
        observation_refs = _text_list(candidate.get("source_observation_refs"))
        observation = observations_by_id.get(observation_refs[0], {}) if observation_refs else {}
        query_refs = _text_list(candidate.get("query_seed_refs")) or _text_list(observation.get("query_seed"))
        provider_refs = _text_list(candidate.get("provider_mode_refs")) or _text_list(observation.get("provider_mode"))
        locator_refs = _locator_refs(candidate, observation)
        base = {
            "source_family": SOURCE_FAMILY,
            "source_observation_refs": observation_refs,
            "candidate_refs": [candidate_id],
            "query_seed_refs": query_refs,
            "provider_mode_refs": provider_refs,
            "source_locator_refs": locator_refs,
            "generated_at": generated_at,
            "input_candidate_delta_id": candidate_delta_id,
            "input_source_observation_delta_id": source_delta_id,
            "input_candidate_delta_hash": f"sha256:{candidate_delta_hash}",
            "input_source_observation_delta_hash": f"sha256:{source_delta_hash}",
        }
        title = _text(candidate.get("normalized_title"))
        if title:
            conflict = _conflicting(conflict_keys, candidate, "title/name clue", title)
            summaries.append(
                _entry(
                    base,
                    evidence_type="title/name clue",
                    proposition=f"Metadata preview mentions candidate title/name: {title}",
                    supporting_fields={
                        "candidate.normalized_title": title,
                        "source_observation.query_seed": _text(observation.get("query_seed")),
                    },
                    normalized_support_summary=f"Metadata-only candidate title/name mention for query {_display(query_refs)}.",
                    support_posture="conflicting" if conflict else "metadata_mention",
                    contradiction_flags=conflict,
                    absence_or_near_miss_flags=[],
                )
            )
        type_hints = _text_list(candidate.get("normalized_type_hints"))
        if type_hints:
            summaries.append(
                _entry(
                    base,
                    evidence_type="object-type clue",
                    proposition=f"Metadata-derived object-type hints: {', '.join(type_hints)}",
                    supporting_fields={"candidate.normalized_type_hints": type_hints},
                    normalized_support_summary="Candidate type hints are derived from existing metadata-smoke source observations.",
                    support_posture="candidate_support",
                    contradiction_flags=[],
                    absence_or_near_miss_flags=[],
                )
            )
        platform_hints = _text_list(candidate.get("platform_time_version_hints"))
        if platform_hints:
            evidence_type = "date/time clue" if any(any(ch.isdigit() for ch in hint) for hint in platform_hints) else "platform clue"
            summaries.append(
                _entry(
                    base,
                    evidence_type=evidence_type,
                    proposition=f"Metadata-derived platform/time/version hints: {', '.join(platform_hints)}",
                    supporting_fields={"candidate.platform_time_version_hints": platform_hints},
                    normalized_support_summary="Platform, time, or version hints remain unreviewed candidate support.",
                    support_posture="candidate_support",
                    contradiction_flags=[],
                    absence_or_near_miss_flags=[],
                )
            )
        representation_hints = _text_list(candidate.get("representation_member_hints"))
        if representation_hints:
            summaries.append(
                _entry(
                    base,
                    evidence_type="representation/member clue",
                    proposition=f"Metadata-derived representation/member hints: {', '.join(representation_hints)}",
                    supporting_fields={"candidate.representation_member_hints": representation_hints},
                    normalized_support_summary="Representation/member hints require review before any artifact claim.",
                    support_posture="candidate_support",
                    contradiction_flags=[],
                    absence_or_near_miss_flags=[],
                )
            )
        if locator_refs:
            summaries.append(
                _entry(
                    base,
                    evidence_type="source-location clue",
                    proposition=f"Source locator metadata is available for candidate {candidate_id}.",
                    supporting_fields={"candidate.source_locator_refs": locator_refs},
                    normalized_support_summary="Locator refs are metadata-only and do not authorize fetch, download, or replay.",
                    support_posture="metadata_mention",
                    contradiction_flags=[],
                    absence_or_near_miss_flags=[],
                )
            )
        summaries.append(
            _entry(
                base,
                evidence_type="provenance clue",
                proposition=f"Candidate {candidate_id} is linked to IA source observation refs for review.",
                supporting_fields={
                    "candidate.candidate_id": candidate_id,
                    "candidate.source_confidence_hints": dict(candidate.get("source_confidence_hints", {}) or {}),
                    "source_observation.transport_status": _text(observation.get("transport_status")),
                },
                normalized_support_summary="Provenance is source-observation and candidate-ref lineage only.",
                support_posture="candidate_support",
                contradiction_flags=[],
                absence_or_near_miss_flags=[],
            )
        )
        ambiguity_flags = _text_list(candidate.get("ambiguity_flags"))
        if ambiguity_flags:
            summaries.append(
                _entry(
                    base,
                    evidence_type="near-miss clue",
                    proposition=f"Candidate ambiguity requires review: {', '.join(ambiguity_flags)}",
                    supporting_fields={"candidate.ambiguity_flags": ambiguity_flags},
                    normalized_support_summary="Ambiguity is preserved for review and is not resolved automatically.",
                    support_posture="insufficient",
                    contradiction_flags=[],
                    absence_or_near_miss_flags=ambiguity_flags,
                )
            )
        absence_clues = _text_list(candidate.get("absence_near_miss_clues"))
        if absence_clues:
            summaries.append(
                _entry(
                    base,
                    evidence_type="absence clue",
                    proposition=f"Candidate carries bounded absence/near-miss clues: {', '.join(absence_clues)}",
                    supporting_fields={"candidate.absence_near_miss_clues": absence_clues},
                    normalized_support_summary="Absence or near-miss clues are bounded to this metadata preview.",
                    support_posture="insufficient",
                    contradiction_flags=[],
                    absence_or_near_miss_flags=absence_clues,
                )
            )
        redacted_errors = _text_list(observation.get("redacted_error_state"))
        transport_status = _text(observation.get("transport_status"))
        if redacted_errors or (transport_status and transport_status != "fixture_replayed"):
            flags = redacted_errors or [transport_status]
            summaries.append(
                _entry(
                    base,
                    evidence_type="transport/unavailability clue",
                    proposition=f"Source observation transport state requires review: {', '.join(flags)}",
                    supporting_fields={
                        "source_observation.transport_status": transport_status,
                        "source_observation.redacted_error_state": redacted_errors,
                    },
                    normalized_support_summary="Transport or unavailable-state support is not an object availability claim.",
                    support_posture="source_unavailable",
                    contradiction_flags=[],
                    absence_or_near_miss_flags=flags,
                )
            )
    return _deduplicate_summaries(summaries)


def build_evidence_summary_delta_manifest(
    *,
    source_manifest: Mapping[str, Any],
    candidate_manifest: Mapping[str, Any],
    source_delta_path: Path,
    candidate_delta_path: Path,
    source_delta_hash: str,
    candidate_delta_hash: str,
    source_observations: Sequence[Mapping[str, Any]],
    candidates: Sequence[Mapping[str, Any]],
    summaries: Sequence[Mapping[str, Any]],
    summary_path: Path,
    summary_hash: str,
    previous: Mapping[str, Any] | None,
) -> dict[str, Any]:
    evidence_type_counts = Counter(str(item.get("evidence_type") or "unknown") for item in summaries)
    support_posture_counts = Counter(str(item.get("support_posture") or "unknown") for item in summaries)
    source_ids = {str(item.get("observation_id") or "") for item in source_observations}
    candidate_ids = {str(item.get("candidate_id") or "") for item in candidates}
    orphan_source_refs = _orphan_ref_count(summaries, "source_observation_refs", source_ids)
    orphan_candidate_refs = _orphan_ref_count(summaries, "candidate_refs", candidate_ids)
    contradiction_count = sum(1 for item in summaries if _text_list(item.get("contradiction_flags")))
    absence_near_miss_count = sum(1 for item in summaries if _text_list(item.get("absence_or_near_miss_flags")))
    insufficient_count = support_posture_counts.get("insufficient", 0)
    source_unavailable_count = support_posture_counts.get("source_unavailable", 0)
    summary_ids = [str(item.get("evidence_summary_id") or "") for item in summaries]
    stable_seed = {
        "schema_version": SCHEMA_VERSION,
        "source_family": SOURCE_FAMILY,
        "source_delta": f"sha256:{source_delta_hash}",
        "candidate_delta": f"sha256:{candidate_delta_hash}",
        "summary_ids": sorted(summary_ids),
        "summary_hash": f"sha256:{summary_hash}",
    }
    delta_id = f"evidence-summary-delta:{SOURCE_FAMILY}:{_stable_digest(stable_seed, 20)}"
    previous_delta_id: str | None = None
    previous_delta_path: str | None = None
    diff_status = "first_run_no_previous_delta"
    if previous:
        previous_delta_id = str(previous.get("delta_id") or "") or None
        previous_delta_path = str(previous.get("previous_delta_path") or _safe_path_label(summary_path.parent)) or None
        diff_status = "unchanged_from_previous_delta" if previous_delta_id == delta_id else "changed_from_previous_delta"
        if previous_delta_id == delta_id and previous.get("diff_status") == "first_run_no_previous_delta":
            previous_delta_id = None
            previous_delta_path = None
            diff_status = "first_run_no_previous_delta"
    validation_status = "PASS" if previous_delta_id else "PASS_WITH_WARNINGS"
    return {
        "schema_version": SCHEMA_VERSION,
        "delta_id": delta_id,
        "source_family": SOURCE_FAMILY,
        "generated_at": str(candidate_manifest.get("generated_at") or source_manifest.get("generated_at") or ""),
        "input_source_observation_delta": _manifest_path_label(source_delta_path, base_dir=summary_path.parent),
        "input_source_observation_delta_hash": f"sha256:{source_delta_hash}",
        "input_source_observation_delta_id": source_manifest.get("delta_id"),
        "input_candidate_index_delta": _manifest_path_label(candidate_delta_path, base_dir=summary_path.parent),
        "input_candidate_index_delta_hash": f"sha256:{candidate_delta_hash}",
        "input_candidate_index_delta_id": candidate_manifest.get("delta_id"),
        "source_observation_count": len(source_observations),
        "candidate_count": len(candidates),
        "evidence_summary_count": len(summaries),
        "deduplicated_evidence_summary_count": len(set(summary_ids)),
        "query_count": int(candidate_manifest.get("query_count") or source_manifest.get("query_count") or 0),
        "provider_modes": sorted(set(_text_list(candidate_manifest.get("provider_modes")) + _text_list(source_manifest.get("provider_modes_represented")))),
        "evidence_type_counts": dict(sorted(evidence_type_counts.items())),
        "support_posture_counts": dict(sorted(support_posture_counts.items())),
        "contradiction_count": contradiction_count,
        "absence_near_miss_count": absence_near_miss_count,
        "insufficient_support_count": insufficient_count,
        "source_unavailable_count": source_unavailable_count,
        "unsafe_record_count": 0,
        "redacted_error_count": int(source_manifest.get("redacted_error_count") or 0) + int(candidate_manifest.get("redacted_error_count") or 0),
        "orphan_candidate_ref_count": orphan_candidate_refs,
        "orphan_source_observation_ref_count": orphan_source_refs,
        "no_downloads": True,
        "no_file_fetch": True,
        "no_wayback_replay": True,
        "no_public_fanout": True,
        "reviewed_master_mutation": False,
        "public_index_mutation": False,
        "candidate_index_store_mutation": False,
        "evidence_summary_delta_written": True,
        "evidence_ledger_store_mutation": False,
        "review_promotion_mutation": False,
        "accepted_truth_created": False,
        "license_posture": DEFAULT_LICENSE_POSTURE,
        "evidence_summary_file": EVIDENCE_SUMMARY_FILE_NAME,
        "evidence_summary_file_hash": f"sha256:{summary_hash}",
        "previous_delta_id": previous_delta_id,
        "previous_delta_path": previous_delta_path,
        "diff_status": diff_status,
        "validation_status": validation_status,
        "blockers": [],
        "recommended_next_task": DEFAULT_RECOMMENDED_NEXT_TASK,
        "review_state": "unreviewed",
        "evidence_status": "provisional",
        "authority": "evidence_summary_only",
        "live_probe_statuses_preserved": source_manifest.get("live_probe_statuses", []),
        "source_index_path": [
            "IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00",
            "IA-SOURCE-OBSERVATION-CACHE-DELTA-00",
            "IA-CANDIDATE-INDEX-REFRESH-00",
            "IA-EVIDENCE-LEDGER-SUMMARY-00",
            "REVIEW-IA-CANDIDATES-BATCH-00",
            "REVIEWED-INDEX-REFRESH-FROM-IA-00",
        ],
    }


def validate_evidence_summary_delta_manifest(
    manifest: Mapping[str, Any],
    *,
    summaries: Sequence[Mapping[str, Any]] | None = None,
    source_observations: Sequence[Mapping[str, Any]] | None = None,
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
    for key in ("no_downloads", "no_file_fetch", "no_wayback_replay", "no_public_fanout", "evidence_summary_delta_written"):
        if manifest.get(key) is not True:
            errors.append(f"{key} must be true")
    for key in (
        "reviewed_master_mutation",
        "public_index_mutation",
        "candidate_index_store_mutation",
        "evidence_ledger_store_mutation",
        "review_promotion_mutation",
        "accepted_truth_created",
    ):
        if manifest.get(key) is not False:
            errors.append(f"{key} must be false")
    for key in (
        "source_observation_count",
        "candidate_count",
        "evidence_summary_count",
        "deduplicated_evidence_summary_count",
        "query_count",
        "contradiction_count",
        "absence_near_miss_count",
        "insufficient_support_count",
        "source_unavailable_count",
        "unsafe_record_count",
        "redacted_error_count",
        "orphan_candidate_ref_count",
        "orphan_source_observation_ref_count",
    ):
        if not isinstance(manifest.get(key), int) or int(manifest.get(key)) < 0:
            errors.append(f"{key} must be a non-negative integer")
    if manifest.get("unsafe_record_count") != 0:
        errors.append("unsafe_record_count must be 0")
    if manifest.get("orphan_candidate_ref_count") != 0:
        errors.append("orphan_candidate_ref_count must be 0")
    if manifest.get("orphan_source_observation_ref_count") != 0:
        errors.append("orphan_source_observation_ref_count must be 0")
    if manifest.get("recommended_next_task") != DEFAULT_RECOMMENDED_NEXT_TASK:
        errors.append(f"recommended_next_task must be {DEFAULT_RECOMMENDED_NEXT_TASK}")
    if summaries is not None:
        summary_ids = [str(item.get("evidence_summary_id", "")) for item in summaries]
        source_ids = {str(item.get("observation_id") or "") for item in source_observations or []}
        candidate_ids = {str(item.get("candidate_id") or "") for item in candidates or []}
        if manifest.get("evidence_summary_count") != len(summaries):
            errors.append("evidence_summary_count does not match evidence summary rows")
        if manifest.get("deduplicated_evidence_summary_count") != len(set(summary_ids)):
            errors.append("deduplicated_evidence_summary_count does not match unique evidence summary IDs")
        if source_observations is not None and manifest.get("source_observation_count") != len(source_observations):
            errors.append("source_observation_count does not match source observation rows")
        if candidates is not None and manifest.get("candidate_count") != len(candidates):
            errors.append("candidate_count does not match candidate rows")
        errors.extend(
            _evidence_summary_record_errors(
                summaries,
                source_observation_ids=source_ids,
                candidate_ids=candidate_ids,
            )
        )
        evidence_type_counts = Counter(str(item.get("evidence_type") or "unknown") for item in summaries)
        support_posture_counts = Counter(str(item.get("support_posture") or "unknown") for item in summaries)
        if dict(sorted(evidence_type_counts.items())) != dict(manifest.get("evidence_type_counts", {})):
            errors.append("evidence_type_counts do not match evidence summaries")
        if dict(sorted(support_posture_counts.items())) != dict(manifest.get("support_posture_counts", {})):
            errors.append("support_posture_counts do not match evidence summaries")
    for path, value in _walk_items(manifest):
        key = path.rsplit(".", 1)[-1]
        if key in FORBIDDEN_TRUE_FLAGS and value is True:
            errors.append(f"{path} must be false")
    errors.extend(_scan_unsafe_content(manifest, "$"))
    return sorted(dict.fromkeys(errors))


def load_delta_manifest(path: str | Path) -> dict[str, Any]:
    return _load_json_object(Path(path), "evidence-summary delta manifest")


def validate_delta_path(path: str | Path, *, strict: bool = False) -> dict[str, Any]:
    manifest_path = Path(path)
    manifest = load_delta_manifest(manifest_path)
    summary_path = manifest_path.parent / str(manifest.get("evidence_summary_file", EVIDENCE_SUMMARY_FILE_NAME))
    summaries = _read_jsonl(summary_path, "evidence summaries")
    errors: list[str] = []
    actual_summary_hash = f"sha256:{_file_hash(summary_path)}"
    if manifest.get("evidence_summary_file_hash") != actual_summary_hash:
        errors.append("evidence_summary_file_hash does not match evidence summary file")
    source_observations: list[dict[str, Any]] | None = None
    candidates: list[dict[str, Any]] | None = None
    source_delta_path = _resolve_manifest_ref(manifest_path.parent, str(manifest.get("input_source_observation_delta") or ""))
    candidate_delta_path = _resolve_manifest_ref(manifest_path.parent, str(manifest.get("input_candidate_index_delta") or ""))
    if source_delta_path.is_file():
        source_manifest = load_source_observation_delta_manifest(source_delta_path)
        source_observations = load_source_observations(source_delta_path, source_manifest)
        actual_source_hash = f"sha256:{_file_hash(source_delta_path)}"
        if manifest.get("input_source_observation_delta_hash") != actual_source_hash:
            errors.append("input_source_observation_delta_hash does not match source-observation delta")
    elif strict:
        errors.append("input source-observation delta not found for strict validation")
    if candidate_delta_path.is_file():
        candidate_manifest = load_candidate_index_delta_manifest(candidate_delta_path)
        candidates = load_candidates(candidate_delta_path, candidate_manifest)
        actual_candidate_hash = f"sha256:{_file_hash(candidate_delta_path)}"
        if manifest.get("input_candidate_index_delta_hash") != actual_candidate_hash:
            errors.append("input_candidate_index_delta_hash does not match candidate-index delta")
    elif strict:
        errors.append("input candidate-index delta not found for strict validation")
    errors.extend(
        validate_evidence_summary_delta_manifest(
            manifest,
            summaries=summaries,
            source_observations=source_observations,
            candidates=candidates,
        )
    )
    if strict and manifest.get("validation_status") not in {"PASS", "PASS_WITH_WARNINGS"}:
        errors.append("validation_status must be PASS or PASS_WITH_WARNINGS")
    status = "PASS" if not errors else "FAIL"
    return {
        "schema_version": "eureka.evidence_ledger_summary_delta_validation.v0",
        "status": status,
        "strict": bool(strict),
        "delta": _safe_path_label(manifest_path),
        "delta_id": manifest.get("delta_id"),
        "evidence_summary_count": manifest.get("evidence_summary_count"),
        "deduplicated_evidence_summary_count": manifest.get("deduplicated_evidence_summary_count"),
        "unsafe_record_count": manifest.get("unsafe_record_count"),
        "errors": sorted(errors),
        "reviewed_master_mutation": bool(manifest.get("reviewed_master_mutation", False)),
        "public_index_mutation": bool(manifest.get("public_index_mutation", False)),
        "candidate_index_store_mutation": bool(manifest.get("candidate_index_store_mutation", False)),
        "evidence_ledger_store_mutation": bool(manifest.get("evidence_ledger_store_mutation", False)),
        "review_promotion_mutation": bool(manifest.get("review_promotion_mutation", False)),
        "accepted_truth_created": bool(manifest.get("accepted_truth_created", False)),
    }


def status_for_delta(path: str | Path) -> dict[str, Any]:
    manifest = load_delta_manifest(path)
    return {
        "schema_version": "eureka.evidence_ledger_summary_delta_status.v0",
        "status": str(manifest.get("validation_status") or "UNKNOWN"),
        "delta_id": manifest.get("delta_id"),
        "source_family": manifest.get("source_family"),
        "source_observation_count": manifest.get("source_observation_count"),
        "candidate_count": manifest.get("candidate_count"),
        "evidence_summary_count": manifest.get("evidence_summary_count"),
        "deduplicated_evidence_summary_count": manifest.get("deduplicated_evidence_summary_count"),
        "query_count": manifest.get("query_count"),
        "provider_modes": manifest.get("provider_modes", []),
        "evidence_type_counts": manifest.get("evidence_type_counts", {}),
        "support_posture_counts": manifest.get("support_posture_counts", {}),
        "contradiction_count": manifest.get("contradiction_count"),
        "absence_near_miss_count": manifest.get("absence_near_miss_count"),
        "insufficient_support_count": manifest.get("insufficient_support_count"),
        "source_unavailable_count": manifest.get("source_unavailable_count"),
        "unsafe_record_count": manifest.get("unsafe_record_count"),
        "redacted_error_count": manifest.get("redacted_error_count"),
        "orphan_candidate_ref_count": manifest.get("orphan_candidate_ref_count"),
        "orphan_source_observation_ref_count": manifest.get("orphan_source_observation_ref_count"),
        "diff_status": manifest.get("diff_status"),
        "previous_delta_id": manifest.get("previous_delta_id"),
        "reviewed_master_mutation": manifest.get("reviewed_master_mutation"),
        "public_index_mutation": manifest.get("public_index_mutation"),
        "candidate_index_store_mutation": manifest.get("candidate_index_store_mutation"),
        "evidence_ledger_store_mutation": manifest.get("evidence_ledger_store_mutation"),
        "review_promotion_mutation": manifest.get("review_promotion_mutation"),
        "accepted_truth_created": manifest.get("accepted_truth_created"),
        "recommended_next_task": manifest.get("recommended_next_task"),
    }


def render_markdown_summary(
    manifest: Mapping[str, Any],
    *,
    summaries: Sequence[Mapping[str, Any]] | None = None,
) -> str:
    evidence_counts = ", ".join(f"{key}: {value}" for key, value in dict(manifest.get("evidence_type_counts", {})).items())
    support_counts = ", ".join(f"{key}: {value}" for key, value in dict(manifest.get("support_posture_counts", {})).items())
    return (
        "# IA Evidence Ledger Summary Delta\n\n"
        f"- status: {manifest.get('validation_status')}\n"
        f"- delta id: {manifest.get('delta_id')}\n"
        f"- source family: {manifest.get('source_family')}\n"
        f"- source-observation input: {manifest.get('input_source_observation_delta')}\n"
        f"- source-observation hash: {manifest.get('input_source_observation_delta_hash')}\n"
        f"- candidate-index input: {manifest.get('input_candidate_index_delta')}\n"
        f"- candidate-index hash: {manifest.get('input_candidate_index_delta_hash')}\n"
        f"- source observations consumed: {manifest.get('source_observation_count')}\n"
        f"- candidates consumed: {manifest.get('candidate_count')}\n"
        f"- evidence summaries written: {manifest.get('evidence_summary_count')}\n"
        f"- deduplicated summaries: {manifest.get('deduplicated_evidence_summary_count')}\n"
        f"- query count: {manifest.get('query_count')}\n"
        f"- provider modes: {', '.join(str(item) for item in manifest.get('provider_modes', []) or [])}\n"
        f"- evidence type counts: {evidence_counts}\n"
        f"- support posture counts: {support_counts}\n"
        f"- contradictions: {manifest.get('contradiction_count')}\n"
        f"- absence/near-miss entries: {manifest.get('absence_near_miss_count')}\n"
        f"- insufficient-support entries: {manifest.get('insufficient_support_count')}\n"
        f"- source-unavailable entries: {manifest.get('source_unavailable_count')}\n"
        f"- orphan candidate refs: {manifest.get('orphan_candidate_ref_count')}\n"
        f"- orphan source-observation refs: {manifest.get('orphan_source_observation_ref_count')}\n"
        f"- previous delta: {manifest.get('previous_delta_id') or 'none'}\n"
        f"- diff status: {manifest.get('diff_status')}\n"
        f"- evidence file: {manifest.get('evidence_summary_file')}\n"
        f"- evidence file hash: {manifest.get('evidence_summary_file_hash')}\n"
        f"- reviewed/master mutation: {str(manifest.get('reviewed_master_mutation')).lower()}\n"
        f"- public-index mutation: {str(manifest.get('public_index_mutation')).lower()}\n"
        f"- candidate-index store mutation: {str(manifest.get('candidate_index_store_mutation')).lower()}\n"
        f"- evidence-ledger store mutation: {str(manifest.get('evidence_ledger_store_mutation')).lower()}\n"
        f"- review/promotion mutation: {str(manifest.get('review_promotion_mutation')).lower()}\n"
        f"- accepted truth created: {str(manifest.get('accepted_truth_created')).lower()}\n"
        f"- no downloads: {str(manifest.get('no_downloads')).lower()}\n"
        f"- no file fetch: {str(manifest.get('no_file_fetch')).lower()}\n"
        f"- no Wayback replay: {str(manifest.get('no_wayback_replay')).lower()}\n"
        f"- no public fanout: {str(manifest.get('no_public_fanout')).lower()}\n"
        f"- license posture: {manifest.get('license_posture')}\n"
        f"- recommended next task: {manifest.get('recommended_next_task')}\n\n"
        "## Boundary\n\n"
        "This delta records provisional, unreviewed evidence summaries derived from source observations and candidates. "
        "It is not reviewed truth, not a public snapshot, not a candidate-store write, and not review or promotion.\n"
    )


def _entry(
    base: Mapping[str, Any],
    *,
    evidence_type: str,
    proposition: str,
    supporting_fields: Mapping[str, Any],
    normalized_support_summary: str,
    support_posture: str,
    contradiction_flags: Sequence[str],
    absence_or_near_miss_flags: Sequence[str],
) -> dict[str, Any]:
    seed = {
        "evidence_type": evidence_type,
        "proposition": proposition,
        "source_refs": list(base.get("source_observation_refs", [])),
        "candidate_refs": list(base.get("candidate_refs", [])),
        "supporting_fields": supporting_fields,
    }
    digest = _stable_digest(seed, 20)
    evidence_summary_id = f"evidence-summary:{SOURCE_FAMILY}:{digest}"
    deterministic_hash = f"sha256:{_stable_digest(seed, 64)}"
    return {
        "schema_version": EVIDENCE_SUMMARY_SCHEMA_VERSION,
        "evidence_summary_id": evidence_summary_id,
        "evidence_type": evidence_type,
        "evidence_status": "provisional",
        "authority": "evidence_summary_only",
        "proposition": proposition,
        "source_family": SOURCE_FAMILY,
        "source_observation_refs": list(base.get("source_observation_refs", [])),
        "candidate_refs": list(base.get("candidate_refs", [])),
        "query_seed_refs": list(base.get("query_seed_refs", [])),
        "provider_mode_refs": list(base.get("provider_mode_refs", [])),
        "source_locator_refs": list(base.get("source_locator_refs", [])),
        "supporting_fields": dict(supporting_fields),
        "normalized_support_summary": normalized_support_summary,
        "support_posture": support_posture,
        "support_strength_hint": "low",
        "uncertainty": [
            "metadata-only support",
            "not reviewed truth",
            "requires human review before downstream truth use",
        ],
        "contradiction_flags": list(contradiction_flags),
        "absence_or_near_miss_flags": list(absence_or_near_miss_flags),
        "review_required": True,
        "review_state": "unreviewed",
        "rights_posture": "unknown_not_assessed",
        "safety_posture": "unknown_not_assessed",
        "generated_at": str(base.get("generated_at") or ""),
        "deterministic_hash": deterministic_hash,
        "input_candidate_delta_id": str(base.get("input_candidate_delta_id") or ""),
        "input_source_observation_delta_id": str(base.get("input_source_observation_delta_id") or ""),
        "input_candidate_delta_hash": str(base.get("input_candidate_delta_hash") or ""),
        "input_source_observation_delta_hash": str(base.get("input_source_observation_delta_hash") or ""),
        "safety_flags": {
            "no_downloads": True,
            "no_file_fetch": True,
            "no_wayback_replay": True,
            "no_public_fanout": True,
            "reviewed_master_mutation": False,
            "public_index_mutation": False,
            "candidate_index_store_mutation": False,
            "evidence_ledger_store_mutation": False,
            "review_promotion_mutation": False,
            "accepted_truth_created": False,
            "rights_clearance_claimed": False,
            "malware_safety_claimed": False,
            "production_readiness_claimed": False,
        },
        "limitations": [
            "evidence summary is provisional and unreviewed",
            "metadata is evidence support, not verified artifact truth",
            "no files, payload bytes, public fanout, review, or promotion occurred",
        ],
    }


def _source_observation_manifest_errors(manifest: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema_version") != SOURCE_OBSERVATION_SCHEMA_VERSION:
        errors.append(f"source-observation schema_version must be {SOURCE_OBSERVATION_SCHEMA_VERSION}")
    if manifest.get("source_family") != SOURCE_FAMILY:
        errors.append(f"source-observation source_family must be {SOURCE_FAMILY}")
    for key in ("no_downloads", "no_file_fetch", "no_wayback_replay", "no_public_fanout"):
        if manifest.get(key) is not True:
            errors.append(f"source-observation {key} must be true")
    for key in ("reviewed_master_mutation", "public_index_mutation", "candidate_index_mutation", "evidence_ledger_mutation"):
        if manifest.get(key) is not False:
            errors.append(f"source-observation {key} must be false")
    errors.extend(_scan_unsafe_content(manifest, "$.source_observation_manifest"))
    return errors


def _candidate_index_manifest_errors(manifest: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema_version") != CANDIDATE_SCHEMA_VERSION:
        errors.append(f"candidate-index schema_version must be {CANDIDATE_SCHEMA_VERSION}")
    if manifest.get("source_family") != SOURCE_FAMILY:
        errors.append(f"candidate-index source_family must be {SOURCE_FAMILY}")
    for key in ("no_downloads", "no_file_fetch", "no_wayback_replay", "no_public_fanout", "candidate_index_delta_written"):
        if manifest.get(key) is not True:
            errors.append(f"candidate-index {key} must be true")
    for key in ("reviewed_master_mutation", "public_index_mutation", "candidate_index_store_mutation", "evidence_ledger_mutation", "review_promotion_mutation"):
        if manifest.get(key) is not False:
            errors.append(f"candidate-index {key} must be false")
    errors.extend(_scan_unsafe_content(manifest, "$.candidate_index_manifest"))
    return errors


def _source_observation_record_errors(records: Sequence[Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    if not records:
        errors.append("source observations must not be empty")
    for index, record in enumerate(records):
        ref = f"source_observations[{index}]"
        if record.get("authority") != "source_observation_only":
            errors.append(f"{ref}.authority must be source_observation_only")
        if record.get("review_state") != "unreviewed":
            errors.append(f"{ref}.review_state must be unreviewed")
        errors.extend(_scan_unsafe_content(record, ref))
    return errors


def _candidate_record_errors(records: Sequence[Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    if not records:
        errors.append("candidate-index delta must not be empty")
    for index, record in enumerate(records):
        ref = f"candidates[{index}]"
        if record.get("candidate_status") != "provisional":
            errors.append(f"{ref}.candidate_status must be provisional")
        if record.get("candidate_authority") != "candidate_only":
            errors.append(f"{ref}.candidate_authority must be candidate_only")
        if record.get("review_state") != "unreviewed":
            errors.append(f"{ref}.review_state must be unreviewed")
        if not _text_list(record.get("source_observation_refs")):
            errors.append(f"{ref}.source_observation_refs must be present")
        errors.extend(_scan_unsafe_content(record, ref))
    return errors


def _input_compatibility_errors(
    *,
    source_manifest: Mapping[str, Any],
    candidate_manifest: Mapping[str, Any],
    source_delta_hash: str,
    source_observations: Sequence[Mapping[str, Any]],
    candidates: Sequence[Mapping[str, Any]],
) -> list[str]:
    errors: list[str] = []
    if candidate_manifest.get("input_source_observation_delta_id") != source_manifest.get("delta_id"):
        errors.append("candidate input_source_observation_delta_id does not match source-observation delta")
    if candidate_manifest.get("input_source_observation_delta_hash") != f"sha256:{source_delta_hash}":
        errors.append("candidate input_source_observation_delta_hash does not match source-observation delta")
    if int(candidate_manifest.get("source_observation_count") or -1) != len(source_observations):
        errors.append("candidate source_observation_count does not match source observations")
    if int(candidate_manifest.get("candidate_count") or -1) != len(candidates):
        errors.append("candidate_count does not match candidate rows")
    return errors


def _evidence_summary_record_errors(
    summaries: Sequence[Mapping[str, Any]],
    *,
    source_observation_ids: set[str],
    candidate_ids: set[str],
) -> list[str]:
    errors: list[str] = []
    if not summaries:
        errors.append("evidence summaries must not be empty")
    seen: set[str] = set()
    for index, record in enumerate(summaries):
        ref = f"evidence_summaries[{index}]"
        missing = sorted(REQUIRED_SUMMARY_FIELDS - set(record))
        if missing:
            errors.append(f"{ref} missing required fields: {', '.join(missing)}")
        summary_id = str(record.get("evidence_summary_id") or "")
        if not summary_id.startswith(f"evidence-summary:{SOURCE_FAMILY}:"):
            errors.append(f"{ref}.evidence_summary_id must be source-family scoped")
        if summary_id in seen:
            errors.append(f"duplicate evidence_summary_id: {summary_id}")
        seen.add(summary_id)
        if record.get("evidence_type") not in ALLOWED_EVIDENCE_TYPES:
            errors.append(f"{ref}.evidence_type is not allowed")
        if record.get("evidence_status") != "provisional":
            errors.append(f"{ref}.evidence_status must be provisional")
        if record.get("authority") != "evidence_summary_only":
            errors.append(f"{ref}.authority must be evidence_summary_only")
        if record.get("source_family") != SOURCE_FAMILY:
            errors.append(f"{ref}.source_family must be {SOURCE_FAMILY}")
        if record.get("support_posture") not in ALLOWED_SUPPORT_POSTURES:
            errors.append(f"{ref}.support_posture is not allowed")
        if record.get("review_required") is not True:
            errors.append(f"{ref}.review_required must be true")
        if record.get("review_state") != "unreviewed":
            errors.append(f"{ref}.review_state must be unreviewed")
        if record.get("rights_posture") not in ALLOWED_RIGHTS_SAFETY_POSTURES:
            errors.append(f"{ref}.rights_posture must be unknown or not_assessed")
        if record.get("safety_posture") not in ALLOWED_RIGHTS_SAFETY_POSTURES:
            errors.append(f"{ref}.safety_posture must be unknown or not_assessed")
        if not _text(record.get("proposition")):
            errors.append(f"{ref}.proposition must be present")
        if not isinstance(record.get("supporting_fields"), Mapping) or not record.get("supporting_fields"):
            errors.append(f"{ref}.supporting_fields must be a non-empty object")
        if not _text(record.get("normalized_support_summary")):
            errors.append(f"{ref}.normalized_support_summary must be present")
        source_refs = _text_list(record.get("source_observation_refs"))
        candidate_refs = _text_list(record.get("candidate_refs"))
        if not source_refs:
            errors.append(f"{ref}.source_observation_refs must be present")
        if not candidate_refs:
            errors.append(f"{ref}.candidate_refs must be present")
        for item in source_refs:
            if source_observation_ids and item not in source_observation_ids:
                errors.append(f"{ref}.source_observation_refs contains orphan ref: {item}")
        for item in candidate_refs:
            if candidate_ids and item not in candidate_ids:
                errors.append(f"{ref}.candidate_refs contains orphan ref: {item}")
        flags = record.get("safety_flags")
        if not isinstance(flags, Mapping):
            errors.append(f"{ref}.safety_flags must be an object")
        else:
            for key in ("no_downloads", "no_file_fetch", "no_wayback_replay", "no_public_fanout"):
                if flags.get(key) is not True:
                    errors.append(f"{ref}.safety_flags.{key} must be true")
            for key in (
                "reviewed_master_mutation",
                "public_index_mutation",
                "candidate_index_store_mutation",
                "evidence_ledger_store_mutation",
                "review_promotion_mutation",
                "accepted_truth_created",
                "rights_clearance_claimed",
                "malware_safety_claimed",
                "production_readiness_claimed",
            ):
                if flags.get(key) is not False:
                    errors.append(f"{ref}.safety_flags.{key} must be false")
        errors.extend(_scan_unsafe_content(record, ref))
    return sorted(dict.fromkeys(errors))


def _scan_unsafe_content(value: Any, path: str) -> list[str]:
    errors: list[str] = []
    for item_path, item in _walk_items(value, path):
        key = item_path.rsplit(".", 1)[-1]
        if key in FORBIDDEN_KEYS:
            errors.append(f"{item_path} is forbidden")
        if key in FORBIDDEN_TRUE_FLAGS and item is True:
            errors.append(f"{item_path} must be false")
        if isinstance(item, str):
            lowered = item.casefold()
            for pattern in PRIVATE_PATH_PATTERNS:
                if pattern.search(item):
                    errors.append(f"{item_path} contains a private/local path")
            for pattern in FORBIDDEN_CLAIM_PATTERNS:
                if pattern.search(item) and not _negative_claim_context(item_path, lowered):
                    errors.append(f"{item_path} contains an unsafe authoritative claim")
    return errors


def _walk_items(value: Any, path: str = "$") -> list[tuple[str, Any]]:
    items = [(path, value)]
    if isinstance(value, Mapping):
        for key, child in value.items():
            items.extend(_walk_items(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            items.extend(_walk_items(child, f"{path}[{index}]"))
    return items


def _negative_claim_context(path: str, lowered: str) -> bool:
    if any(part in path for part in ("limitations", "uncertainty", "rights_posture", "safety_posture")):
        return True
    return any(marker in lowered for marker in ("not ", "no ", "unknown", "not_assessed", "not claimed", "not verified"))


def _deduplicate_summaries(summaries: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for summary in summaries:
        by_id[str(summary.get("evidence_summary_id") or "")] = dict(summary)
    return [by_id[key] for key in sorted(by_id)]


def _conflict_keys(candidates: Sequence[Mapping[str, Any]]) -> set[tuple[str, str]]:
    values_by_ref: dict[tuple[str, str], set[str]] = defaultdict(set)
    for candidate in candidates:
        title = _text(candidate.get("normalized_title"))
        for ref in _text_list(candidate.get("source_observation_refs")):
            if title:
                values_by_ref[(ref, "title/name clue")].add(title)
    return {key for key, values in values_by_ref.items() if len(values) > 1}


def _conflicting(
    conflict_keys: set[tuple[str, str]],
    candidate: Mapping[str, Any],
    evidence_type: str,
    _value: str,
) -> list[str]:
    flags: list[str] = []
    for ref in _text_list(candidate.get("source_observation_refs")):
        if (ref, evidence_type) in conflict_keys:
            flags.append("conflicting_metadata_requires_review")
    return flags


def _locator_refs(candidate: Mapping[str, Any], observation: Mapping[str, Any]) -> list[dict[str, Any]]:
    refs = candidate.get("source_locator_refs")
    if isinstance(refs, list):
        return [dict(item) for item in refs if isinstance(item, Mapping)]
    locator = observation.get("source_locator")
    if isinstance(locator, Mapping):
        return [dict(locator)]
    return []


def _orphan_ref_count(summaries: Sequence[Mapping[str, Any]], key: str, allowed: set[str]) -> int:
    count = 0
    for summary in summaries:
        for ref in _text_list(summary.get(key)):
            if ref not in allowed:
                count += 1
    return count


def _load_json_object(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise EvidenceLedgerSummaryError(f"{label} not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise EvidenceLedgerSummaryError(f"{label} is not valid JSON: {exc.msg}") from exc
    if not isinstance(payload, Mapping):
        raise EvidenceLedgerSummaryError(f"{label} must be a JSON object")
    return dict(payload)


def _read_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    if not path.is_file():
        raise EvidenceLedgerSummaryError(f"{label} file not found: {path}")
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise EvidenceLedgerSummaryError(f"{path}:{line_number}: invalid JSONL row: {exc.msg}") from exc
        if not isinstance(payload, Mapping):
            raise EvidenceLedgerSummaryError(f"{path}:{line_number}: JSONL row must be an object")
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


def _file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stable_digest(value: Any, length: int = 16) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:length]


def _safe_path_label(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _manifest_path_label(path: Path, *, base_dir: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        pass
    try:
        return os.path.relpath(resolved, start=base_dir.resolve()).replace("\\", "/")
    except ValueError:
        return path.name


def _resolve_manifest_ref(base_dir: Path, label: str) -> Path:
    path = Path(label)
    if path.is_absolute() or path.is_file():
        return path
    return base_dir / path


def _normalize_source(source: str) -> str:
    return source.strip().lower().replace("-", "_")


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _text_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, tuple):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def _display(values: Sequence[str]) -> str:
    return ", ".join(values) if values else "unknown"

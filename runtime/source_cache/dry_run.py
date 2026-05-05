"""Local dry-run source cache candidate loading and classification."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from runtime.source_cache.models import SourceCacheCandidateSummary, SourceCacheDryRunError
from runtime.source_cache.policy import (
    DRY_RUN_EXAMPLES_ROOT,
    EVIDENCE_READINESS,
    LEGACY_RECORD_KIND_ALIASES,
    LEGACY_SOURCE_FAMILY_ALIASES,
    POLICY_STATUSES,
    PRIVACY_ALIASES,
    PRIVACY_STATUSES,
    PUBLIC_SAFETY_STATUSES,
    RECORD_KINDS,
    SOURCE_FAMILIES,
    ensure_approved_input_root,
    normalize_enum,
    repo_relative,
    scan_candidate_policy,
)
from runtime.source_cache.report import build_report


CANDIDATE_FILENAMES = ("SOURCE_CACHE_CANDIDATE.json", "SOURCE_CACHE_RECORD.json")
REQUIRED_FIELDS = {
    "schema_version",
    "candidate_id",
    "candidate_kind",
    "source_family",
    "record_kind",
    "privacy_status",
    "public_safety_status",
    "evidence_readiness",
    "policy_status",
    "source_ref",
    "summary",
    "limitations",
    "hard_booleans",
}
LEGACY_REQUIRED_FIELDS = {
    "schema_version",
    "source_cache_record_id",
    "source_cache_record_kind",
    "source_ref",
    "cache_kind",
    "source_policy",
    "cached_payload_summary",
    "privacy",
    "rights_and_risk",
    "no_runtime_guarantees",
    "no_mutation_guarantees",
}
HARD_TRUE = {"local_dry_run"}
HARD_FALSE = {
    "live_source_called",
    "external_calls_performed",
    "connector_runtime_executed",
    "source_sync_worker_executed",
    "authoritative_source_cache_written",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
    "public_search_runtime_mutated",
    "telemetry_exported",
    "credentials_used",
    "downloads_enabled",
    "installs_enabled",
    "execution_enabled",
}
LEGACY_RUNTIME_FALSE = {
    "source_cache_runtime_implemented",
    "cache_write_performed",
    "live_source_called",
    "external_calls_performed",
    "arbitrary_url_fetched",
    "raw_payload_stored",
    "private_data_stored",
    "executable_payload_stored",
    "telemetry_exported",
    "credentials_used",
}
LEGACY_MUTATION_FALSE = {
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
}


def load_candidate(path: Path) -> dict[str, Any]:
    """Load one source cache candidate JSON object."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} does not parse as JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def discover_candidates(root: Path) -> list[Path]:
    """Find candidate JSON files under a root deterministically."""

    if root.is_file():
        return [root] if root.name in CANDIDATE_FILENAMES else []
    if not root.exists():
        return []
    found: list[Path] = []
    for filename in CANDIDATE_FILENAMES:
        found.extend(path for path in root.rglob(filename) if path.is_file())
    return sorted(set(found), key=lambda item: item.as_posix())


def validate_candidate_shape(record: Mapping[str, Any]) -> tuple[list[str], list[str]]:
    """Validate the bounded dry-run shape without accepting truth claims."""

    errors: list[str] = []
    warnings: list[str] = []
    if _is_legacy_source_cache_record(record):
        missing = LEGACY_REQUIRED_FIELDS - set(record)
        if missing:
            errors.append(f"legacy source cache record missing required fields: {', '.join(sorted(missing))}")
        _validate_legacy_false_fields(record, errors)
    else:
        missing = REQUIRED_FIELDS - set(record)
        if missing:
            errors.append(f"source cache candidate missing required fields: {', '.join(sorted(missing))}")
        if record.get("candidate_kind") != "source_cache_candidate":
            errors.append("candidate_kind must be source_cache_candidate")
        if normalize_enum(record.get("source_family"), SOURCE_FAMILIES, LEGACY_SOURCE_FAMILY_ALIASES) == "unknown":
            errors.append("source_family is unsupported or unknown")
        if normalize_enum(record.get("record_kind"), RECORD_KINDS, LEGACY_RECORD_KIND_ALIASES) == "unknown":
            errors.append("record_kind is unsupported or unknown")
        if normalize_enum(record.get("privacy_status"), PRIVACY_STATUSES, PRIVACY_ALIASES) == "unknown":
            errors.append("privacy_status is unsupported or unknown")
        if normalize_enum(record.get("public_safety_status"), PUBLIC_SAFETY_STATUSES) == "unknown":
            errors.append("public_safety_status is unsupported or unknown")
        if normalize_enum(record.get("evidence_readiness"), EVIDENCE_READINESS) == "unknown":
            errors.append("evidence_readiness is unsupported or unknown")
        if normalize_enum(record.get("policy_status"), POLICY_STATUSES) == "unknown":
            errors.append("policy_status is unsupported or unknown")
        hard = record.get("hard_booleans", {})
        if not isinstance(hard, Mapping):
            errors.append("hard_booleans must be an object")
        else:
            for key in HARD_TRUE:
                if hard.get(key) is not True:
                    errors.append(f"hard_booleans.{key} must be true")
            for key in HARD_FALSE:
                if hard.get(key) is not False:
                    errors.append(f"hard_booleans.{key} must be false")
    errors.extend(scan_candidate_policy(record))
    return sorted(set(errors)), warnings


def classify_candidate(record: Mapping[str, Any], *, path: Path | None = None) -> SourceCacheCandidateSummary:
    """Classify a source cache candidate conservatively."""

    errors, warnings = validate_candidate_shape(record)
    if _is_legacy_source_cache_record(record):
        source_ref = _mapping(record.get("source_ref"))
        cache_kind = _mapping(record.get("cache_kind"))
        privacy = _mapping(record.get("privacy"))
        source_policy = _mapping(record.get("source_policy"))
        summary = _mapping(record.get("cached_payload_summary"))
        rights = _mapping(record.get("rights_and_risk"))
        source_family = normalize_enum(source_ref.get("source_family"), SOURCE_FAMILIES, LEGACY_SOURCE_FAMILY_ALIASES)
        record_kind = normalize_enum(cache_kind.get("kind"), RECORD_KINDS, LEGACY_RECORD_KIND_ALIASES)
        privacy_status = normalize_enum(privacy.get("privacy_classification"), PRIVACY_STATUSES, PRIVACY_ALIASES)
        public_safety = "public_safe" if summary.get("public_safe") is True and privacy.get("publishable") is True else "review_required"
        evidence_readiness = "evidence_review_required" if source_policy.get("evidence_attribution_required") is True else "insufficient"
        policy_status = normalize_enum(source_ref.get("source_status"), POLICY_STATUSES)
        if policy_status == "unknown" and source_ref.get("source_status") == "approval_required":
            policy_status = "approval_required"
        if rights.get("downloads_enabled") is not False or rights.get("execution_enabled") is not False:
            errors.append("rights/action fields must keep downloads and execution disabled")
        candidate_id = str(record.get("source_cache_record_id", "unknown"))
        source_ref_text = str(source_ref.get("source_id") or source_ref.get("source_family") or "unknown")
        summary_text = summary.get("summary_text") if isinstance(summary.get("summary_text"), str) else None
    else:
        source_family = normalize_enum(record.get("source_family"), SOURCE_FAMILIES, LEGACY_SOURCE_FAMILY_ALIASES)
        record_kind = normalize_enum(record.get("record_kind"), RECORD_KINDS, LEGACY_RECORD_KIND_ALIASES)
        privacy_status = normalize_enum(record.get("privacy_status"), PRIVACY_STATUSES, PRIVACY_ALIASES)
        public_safety = normalize_enum(record.get("public_safety_status"), PUBLIC_SAFETY_STATUSES)
        evidence_readiness = normalize_enum(record.get("evidence_readiness"), EVIDENCE_READINESS)
        policy_status = normalize_enum(record.get("policy_status"), POLICY_STATUSES)
        candidate_id = str(record.get("candidate_id", "unknown"))
        source_ref_text = _source_ref_text(record.get("source_ref"))
        summary_text = _summary_text(record.get("summary"))
    return SourceCacheCandidateSummary(
        candidate_id=candidate_id,
        path=repo_relative(path) if path else "",
        source_family=source_family,
        record_kind=record_kind,
        privacy_status=privacy_status,
        public_safety_status=public_safety,
        evidence_readiness=evidence_readiness,
        policy_status=policy_status,
        valid=not errors,
        source_ref=source_ref_text,
        summary_text=summary_text,
        warnings=tuple(warnings),
        errors=tuple(errors),
    )


def run_source_cache_dry_run(
    roots: Iterable[Path] | None = None,
    strict: bool = False,
    *,
    enforce_approved_roots: bool = False,
    allow_temp_roots: bool = False,
):
    """Run a local dry-run over approved candidate roots."""

    input_roots = tuple(Path(root) for root in (roots or (DRY_RUN_EXAMPLES_ROOT,)))
    summaries: list[SourceCacheCandidateSummary] = []
    report_errors: list[SourceCacheDryRunError] = []
    warnings: list[str] = []
    for root in input_roots:
        try:
            checked_root = ensure_approved_input_root(root, allow_temp=allow_temp_roots) if enforce_approved_roots else root.resolve()
        except Exception as exc:
            report_errors.append(SourceCacheDryRunError("input_root_rejected", str(exc), str(root)))
            continue
        candidates = discover_candidates(checked_root)
        if not candidates:
            warnings.append(f"no source-cache dry-run candidates found under {repo_relative(checked_root)}")
        for candidate_path in candidates:
            try:
                record = load_candidate(candidate_path)
                summaries.append(classify_candidate(record, path=candidate_path))
            except Exception as exc:
                report_errors.append(SourceCacheDryRunError("candidate_load_failed", str(exc), repo_relative(candidate_path)))
    if strict and not summaries:
        report_errors.append(SourceCacheDryRunError("strict_no_candidates", "strict mode requires at least one candidate"))
    report = build_report(
        input_roots=(repo_relative(root) for root in input_roots),
        candidates=summaries,
        warnings=warnings,
        errors=report_errors,
    )
    return report


def _is_legacy_source_cache_record(record: Mapping[str, Any]) -> bool:
    return record.get("source_cache_record_kind") == "source_cache_record"


def _validate_legacy_false_fields(record: Mapping[str, Any], errors: list[str]) -> None:
    runtime = _mapping(record.get("no_runtime_guarantees"))
    mutation = _mapping(record.get("no_mutation_guarantees"))
    acquisition = _mapping(record.get("acquisition_context"))
    cache_kind = _mapping(record.get("cache_kind"))
    rights = _mapping(record.get("rights_and_risk"))
    for key in LEGACY_RUNTIME_FALSE:
        if runtime.get(key) is not False:
            errors.append(f"no_runtime_guarantees.{key} must be false")
    for key in LEGACY_MUTATION_FALSE:
        if mutation.get(key) is not False:
            errors.append(f"no_mutation_guarantees.{key} must be false")
    for key in ("live_network_used", "external_call_performed", "credentials_used"):
        if acquisition.get(key) is not False:
            errors.append(f"acquisition_context.{key} must be false")
    if cache_kind.get("raw_payload_allowed") is not False:
        errors.append("cache_kind.raw_payload_allowed must be false")
    for key in ("downloads_enabled", "installs_enabled", "execution_enabled"):
        if rights.get(key) is not False:
            errors.append(f"rights_and_risk.{key} must be false")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _source_ref_text(value: Any) -> str | None:
    if isinstance(value, Mapping):
        for key in ("source_id", "source_ref_id", "source_label", "source_family"):
            if isinstance(value.get(key), str):
                return value[key]
    if isinstance(value, str):
        return value
    return None


def _summary_text(value: Any) -> str | None:
    if isinstance(value, Mapping):
        for key in ("summary_text", "title", "label"):
            if isinstance(value.get(key), str):
                return value[key]
    if isinstance(value, str):
        return value
    return None

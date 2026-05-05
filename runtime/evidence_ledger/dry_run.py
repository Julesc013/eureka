"""Local dry-run evidence-ledger candidate loading and classification."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from runtime.evidence_ledger.models import EvidenceLedgerCandidateSummary, EvidenceLedgerDryRunError
from runtime.evidence_ledger.policy import (
    CLAIM_KINDS,
    DRY_RUN_EXAMPLES_ROOT,
    EVIDENCE_KINDS,
    LEGACY_CLAIM_KIND_ALIASES,
    LEGACY_EVIDENCE_KIND_ALIASES,
    LEGACY_PROVENANCE_ALIASES,
    LEGACY_REVIEW_STATUS_ALIASES,
    LEGACY_SOURCE_FAMILY_ALIASES,
    PRIVACY_ALIASES,
    PRIVACY_STATUSES,
    PROMOTION_READINESS,
    PROVENANCE_STATUSES,
    PUBLIC_SAFETY_STATUSES,
    REVIEW_STATUSES,
    RIGHTS_RISK_STATUSES,
    SOURCE_FAMILIES,
    ensure_approved_input_root,
    normalize_enum,
    repo_relative,
    scan_candidate_policy,
)
from runtime.evidence_ledger.report import build_report


CANDIDATE_FILENAMES = ("EVIDENCE_LEDGER_CANDIDATE.json", "EVIDENCE_LEDGER_RECORD.json")
REQUIRED_FIELDS = {
    "schema_version",
    "candidate_id",
    "candidate_kind",
    "evidence_kind",
    "claim_kind",
    "source_family",
    "provenance_status",
    "review_status",
    "privacy_status",
    "public_safety_status",
    "rights_risk_status",
    "promotion_readiness",
    "source_ref",
    "provenance_ref",
    "claim",
    "observation",
    "limitations",
    "hard_booleans",
}
LEGACY_REQUIRED_FIELDS = {
    "schema_version",
    "evidence_ledger_record_id",
    "evidence_ledger_record_kind",
    "status",
    "evidence_kind",
    "subject_ref",
    "claim",
    "source_cache_refs",
    "provenance",
    "observation",
    "confidence",
    "review",
    "conflicts",
    "privacy",
    "rights_and_risk",
    "no_truth_guarantees",
    "no_runtime_guarantees",
    "no_mutation_guarantees",
}
HARD_TRUE = {"local_dry_run"}
HARD_FALSE = {
    "live_source_called",
    "external_calls_performed",
    "connector_runtime_executed",
    "source_sync_worker_executed",
    "authoritative_evidence_ledger_written",
    "evidence_ledger_mutated",
    "source_cache_mutated",
    "candidate_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
    "public_search_runtime_mutated",
    "claim_accepted_as_truth",
    "promotion_decision_created",
    "telemetry_exported",
    "credentials_used",
    "downloads_enabled",
    "installs_enabled",
    "execution_enabled",
}
LEGACY_TRUTH_FALSE = {"accepted_as_truth"}
LEGACY_RUNTIME_FALSE = {
    "evidence_ledger_runtime_implemented",
    "ledger_write_performed",
    "live_source_called",
    "external_calls_performed",
    "telemetry_exported",
    "credentials_used",
}
LEGACY_MUTATION_FALSE = {
    "source_cache_mutated",
    "candidate_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
}


def load_candidate(path: Path) -> dict[str, Any]:
    """Load one evidence-ledger candidate JSON object."""

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
    if _is_legacy_evidence_ledger_record(record):
        missing = LEGACY_REQUIRED_FIELDS - set(record)
        if missing:
            errors.append(f"legacy evidence ledger record missing required fields: {', '.join(sorted(missing))}")
        _validate_legacy_false_fields(record, errors)
    else:
        missing = REQUIRED_FIELDS - set(record)
        if missing:
            errors.append(f"evidence ledger candidate missing required fields: {', '.join(sorted(missing))}")
        if record.get("candidate_kind") != "evidence_ledger_candidate":
            errors.append("candidate_kind must be evidence_ledger_candidate")
        if normalize_enum(record.get("evidence_kind"), EVIDENCE_KINDS, LEGACY_EVIDENCE_KIND_ALIASES) == "unknown":
            errors.append("evidence_kind is unsupported or unknown")
        if normalize_enum(record.get("claim_kind"), CLAIM_KINDS, LEGACY_CLAIM_KIND_ALIASES) == "unknown":
            errors.append("claim_kind is unsupported or unknown")
        if normalize_enum(record.get("source_family"), SOURCE_FAMILIES, LEGACY_SOURCE_FAMILY_ALIASES) == "unknown":
            errors.append("source_family is unsupported or unknown")
        if normalize_enum(record.get("provenance_status"), PROVENANCE_STATUSES, LEGACY_PROVENANCE_ALIASES) == "unknown":
            errors.append("provenance_status is unsupported or unknown")
        if normalize_enum(record.get("review_status"), REVIEW_STATUSES, LEGACY_REVIEW_STATUS_ALIASES) == "unknown":
            errors.append("review_status is unsupported or unknown")
        if normalize_enum(record.get("privacy_status"), PRIVACY_STATUSES, PRIVACY_ALIASES) == "unknown":
            errors.append("privacy_status is unsupported or unknown")
        if normalize_enum(record.get("public_safety_status"), PUBLIC_SAFETY_STATUSES) == "unknown":
            errors.append("public_safety_status is unsupported or unknown")
        if normalize_enum(record.get("rights_risk_status"), RIGHTS_RISK_STATUSES) == "unknown":
            errors.append("rights_risk_status is unsupported or unknown")
        if normalize_enum(record.get("promotion_readiness"), PROMOTION_READINESS) == "unknown":
            errors.append("promotion_readiness is unsupported or unknown")
        claim = _mapping(record.get("claim"))
        if claim.get("global_absence_claimed") is not False:
            errors.append("claim.global_absence_claimed must be false")
        if claim.get("accepted_as_truth") is not False:
            errors.append("claim.accepted_as_truth must be false")
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


def classify_candidate(record: Mapping[str, Any], *, path: Path | None = None) -> EvidenceLedgerCandidateSummary:
    """Classify an evidence-ledger candidate conservatively."""

    errors, warnings = validate_candidate_shape(record)
    if _is_legacy_evidence_ledger_record(record):
        evidence_kind_section = _mapping(record.get("evidence_kind"))
        subject = _mapping(record.get("subject_ref"))
        claim = _mapping(record.get("claim"))
        provenance = _mapping(record.get("provenance"))
        review = _mapping(record.get("review"))
        conflicts = _mapping(record.get("conflicts"))
        privacy = _mapping(record.get("privacy"))
        rights = _mapping(record.get("rights_and_risk"))
        evidence_kind = normalize_enum(evidence_kind_section.get("kind"), EVIDENCE_KINDS, LEGACY_EVIDENCE_KIND_ALIASES)
        claim_kind = normalize_enum(claim.get("claim_type"), CLAIM_KINDS, LEGACY_CLAIM_KIND_ALIASES)
        source_family = normalize_enum(subject.get("source_family"), SOURCE_FAMILIES, LEGACY_SOURCE_FAMILY_ALIASES)
        provenance_status = normalize_enum(provenance.get("provenance_kind"), PROVENANCE_STATUSES, LEGACY_PROVENANCE_ALIASES)
        review_status = normalize_enum(review.get("review_status"), REVIEW_STATUSES, LEGACY_REVIEW_STATUS_ALIASES)
        if conflicts.get("conflict_status") not in (None, "none_known", "unknown"):
            review_status = "conflict_review_required"
        privacy_status = normalize_enum(privacy.get("privacy_classification"), PRIVACY_STATUSES, PRIVACY_ALIASES)
        public_safety = "public_safe" if privacy.get("publishable") is True else "review_required"
        rights_risk = _rights_risk_status(rights)
        promotion_readiness = "review_required" if review_status in {"review_required", "policy_review_required", "conflict_review_required"} else "not_ready"
        candidate_id = str(record.get("evidence_ledger_record_id", "unknown"))
        source_ref_text = str(subject.get("source_id") or subject.get("source_family") or "unknown")
        provenance_ref = _first_string(provenance.get("provenance_refs"))
        claim_summary = _claim_summary(claim.get("claim_value"))
    else:
        evidence_kind = normalize_enum(record.get("evidence_kind"), EVIDENCE_KINDS, LEGACY_EVIDENCE_KIND_ALIASES)
        claim_kind = normalize_enum(record.get("claim_kind"), CLAIM_KINDS, LEGACY_CLAIM_KIND_ALIASES)
        source_family = normalize_enum(record.get("source_family"), SOURCE_FAMILIES, LEGACY_SOURCE_FAMILY_ALIASES)
        provenance_status = normalize_enum(record.get("provenance_status"), PROVENANCE_STATUSES, LEGACY_PROVENANCE_ALIASES)
        review_status = normalize_enum(record.get("review_status"), REVIEW_STATUSES, LEGACY_REVIEW_STATUS_ALIASES)
        privacy_status = normalize_enum(record.get("privacy_status"), PRIVACY_STATUSES, PRIVACY_ALIASES)
        public_safety = normalize_enum(record.get("public_safety_status"), PUBLIC_SAFETY_STATUSES)
        rights_risk = normalize_enum(record.get("rights_risk_status"), RIGHTS_RISK_STATUSES)
        promotion_readiness = normalize_enum(record.get("promotion_readiness"), PROMOTION_READINESS)
        candidate_id = str(record.get("candidate_id", "unknown"))
        source_ref_text = _source_ref_text(record.get("source_ref"))
        provenance_ref = _source_ref_text(record.get("provenance_ref"))
        claim_summary = _claim_summary(_mapping(record.get("claim")).get("claim_value"))
    return EvidenceLedgerCandidateSummary(
        candidate_id=candidate_id,
        path=repo_relative(path) if path else "",
        evidence_kind=evidence_kind,
        claim_kind=claim_kind,
        source_family=source_family,
        provenance_status=provenance_status,
        review_status=review_status,
        privacy_status=privacy_status,
        public_safety_status=public_safety,
        rights_risk_status=rights_risk,
        promotion_readiness=promotion_readiness,
        valid=not errors,
        source_ref=source_ref_text,
        provenance_ref=provenance_ref,
        claim_summary=claim_summary,
        warnings=tuple(warnings),
        errors=tuple(errors),
    )


def run_evidence_ledger_dry_run(
    roots: Iterable[Path] | None = None,
    strict: bool = False,
    *,
    enforce_approved_roots: bool = False,
    allow_temp_roots: bool = False,
):
    """Run a local dry-run over approved evidence candidate roots."""

    input_roots = tuple(Path(root) for root in (roots or (DRY_RUN_EXAMPLES_ROOT,)))
    summaries: list[EvidenceLedgerCandidateSummary] = []
    report_errors: list[EvidenceLedgerDryRunError] = []
    warnings: list[str] = []
    for root in input_roots:
        try:
            checked_root = ensure_approved_input_root(root, allow_temp=allow_temp_roots) if enforce_approved_roots else root.resolve()
        except Exception as exc:
            report_errors.append(EvidenceLedgerDryRunError("input_root_rejected", str(exc), str(root)))
            continue
        candidates = discover_candidates(checked_root)
        if not candidates:
            warnings.append(f"no evidence-ledger dry-run candidates found under {repo_relative(checked_root)}")
        for candidate_path in candidates:
            try:
                record = load_candidate(candidate_path)
                summaries.append(classify_candidate(record, path=candidate_path))
            except Exception as exc:
                report_errors.append(EvidenceLedgerDryRunError("candidate_load_failed", str(exc), repo_relative(candidate_path)))
    if strict and not summaries:
        report_errors.append(EvidenceLedgerDryRunError("strict_no_candidates", "strict mode requires at least one candidate"))
    report = build_report(
        input_roots=(repo_relative(root) for root in input_roots),
        candidates=summaries,
        warnings=warnings,
        errors=report_errors,
    )
    return report


def _is_legacy_evidence_ledger_record(record: Mapping[str, Any]) -> bool:
    return record.get("evidence_ledger_record_kind") == "evidence_ledger_record"


def _validate_legacy_false_fields(record: Mapping[str, Any], errors: list[str]) -> None:
    truth = _mapping(record.get("no_truth_guarantees"))
    runtime = _mapping(record.get("no_runtime_guarantees"))
    mutation = _mapping(record.get("no_mutation_guarantees"))
    claim = _mapping(record.get("claim"))
    kind = _mapping(record.get("evidence_kind"))
    review = _mapping(record.get("review"))
    conflicts = _mapping(record.get("conflicts"))
    privacy = _mapping(record.get("privacy"))
    rights = _mapping(record.get("rights_and_risk"))
    for key in LEGACY_TRUTH_FALSE:
        if truth.get(key) is not False:
            errors.append(f"no_truth_guarantees.{key} must be false")
    for key in LEGACY_RUNTIME_FALSE:
        if runtime.get(key) is not False:
            errors.append(f"no_runtime_guarantees.{key} must be false")
    for key in LEGACY_MUTATION_FALSE:
        if mutation.get(key) is not False:
            errors.append(f"no_mutation_guarantees.{key} must be false")
    if claim.get("global_absence_claimed") is not False:
        errors.append("claim.global_absence_claimed must be false")
    if kind.get("accepted_evidence_now") is not False:
        errors.append("evidence_kind.accepted_evidence_now must be false")
    if review.get("promotion_policy_required") is not True:
        errors.append("review.promotion_policy_required must be true")
    if conflicts.get("destructive_merge_allowed") is not False:
        errors.append("conflicts.destructive_merge_allowed must be false")
    for key in ("contains_private_path", "contains_secret", "contains_private_url", "contains_user_identifier", "contains_ip_address"):
        if privacy.get(key) is not False:
            errors.append(f"privacy.{key} must be false")
    for key in ("rights_clearance_claimed", "malware_safety_claimed", "downloads_enabled", "installs_enabled", "execution_enabled"):
        if rights.get(key) is not False:
            errors.append(f"rights_and_risk.{key} must be false")


def _rights_risk_status(rights: Mapping[str, Any]) -> str:
    risk = normalize_enum(rights.get("risk_classification"), RIGHTS_RISK_STATUSES)
    if risk != "unknown":
        return risk
    return normalize_enum(rights.get("rights_classification"), RIGHTS_RISK_STATUSES)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _first_string(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        for item in value:
            if isinstance(item, str):
                return item
    return None


def _source_ref_text(value: Any) -> str | None:
    if isinstance(value, Mapping):
        for key in ("source_id", "source_ref_id", "source_label", "source_family", "provenance_id"):
            if isinstance(value.get(key), str):
                return value[key]
    if isinstance(value, str):
        return value
    return None


def _claim_summary(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        for key in ("summary", "label", "absence_status", "version", "package_name"):
            if isinstance(value.get(key), str):
                return value[key]
    return None

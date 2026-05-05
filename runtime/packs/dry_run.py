"""Local dry-run discovery, validation, and classification for pack examples."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from runtime.packs.models import PackCandidateSummary, PackImportDryRunErrorRecord
from runtime.packs.policy import (
    MUTATION_IMPACT_ALIASES,
    MUTATION_IMPACTS,
    PACK_IMPORT_DRY_RUN_ROOT,
    PACK_KINDS,
    PRIVACY_STATUSES,
    PROMOTION_READINESS,
    PUBLIC_SAFETY_STATUSES,
    RISK_STATUSES,
    VALIDATION_STATUSES,
    ensure_approved_input_root,
    normalize_enum,
    normalize_pack_kind,
    repo_relative,
    scan_pack_policy,
)
from runtime.packs.report import build_report
from runtime.packs.validators import run_validator_for_pack


MANIFEST_FILENAMES = (
    "SOURCE_PACK.json",
    "EVIDENCE_PACK.json",
    "INDEX_PACK.json",
    "CONTRIBUTION_PACK.json",
    "PACK_IMPORT_DRY_RUN_INPUT.json",
)


def load_pack_manifest(path: Path) -> dict[str, Any]:
    """Load a pack manifest or P104 dry-run input JSON object."""

    manifest_path = _manifest_path(path)
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{manifest_path} does not parse as JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{manifest_path} must contain a JSON object")
    payload = dict(payload)
    payload["_manifest_filename"] = manifest_path.name
    payload["_manifest_path"] = manifest_path
    return payload


def discover_pack_candidates(root: Path) -> list[Path]:
    """Find pack manifest files under a root deterministically."""

    if root.is_file():
        return [root] if root.name in MANIFEST_FILENAMES else []
    if not root.exists():
        return []
    found: list[Path] = []
    for filename in MANIFEST_FILENAMES:
        found.extend(path for path in root.rglob(filename) if path.is_file())
    return sorted(set(found), key=lambda item: item.as_posix())


def validate_pack_candidate_shape(record_or_root: Mapping[str, Any] | Path) -> tuple[list[str], list[str]]:
    """Validate dry-run shape without importing, staging, or accepting claims."""

    record = load_pack_manifest(record_or_root) if isinstance(record_or_root, Path) else record_or_root
    errors: list[str] = []
    warnings: list[str] = []
    filename = str(record.get("_manifest_filename") or "")
    pack_kind = normalize_pack_kind(record, filename=filename)
    if pack_kind not in PACK_KINDS or pack_kind == "unknown":
        errors.append("pack kind is unsupported or unknown")
    if _schema_version(record) == "unknown":
        errors.append("schema version is missing or unknown")
    if not _pack_id(record):
        errors.append("pack_id is required")
    privacy = _privacy_status(record)
    if privacy not in PRIVACY_STATUSES or privacy == "unknown":
        warnings.append("privacy status was classified unknown")
    public_safety = _public_safety_status(record)
    if public_safety not in PUBLIC_SAFETY_STATUSES or public_safety == "unknown":
        warnings.append("public safety status was classified unknown")
    risk = _risk_status(record)
    if risk not in RISK_STATUSES:
        errors.append("risk status is unsupported")
    mutation = _mutation_impact(record, pack_kind)
    if mutation not in MUTATION_IMPACTS:
        errors.append("mutation impact is unsupported")
    promotion = _promotion_readiness(record, pack_kind)
    if promotion not in PROMOTION_READINESS:
        errors.append("promotion readiness is unsupported")
    errors.extend(scan_pack_policy(record))
    return sorted(set(errors)), sorted(set(warnings))


def classify_pack_candidate(
    record_or_root: Mapping[str, Any] | Path,
    *,
    run_validators: bool = True,
) -> PackCandidateSummary:
    """Classify one pack candidate conservatively."""

    record = load_pack_manifest(record_or_root) if isinstance(record_or_root, Path) else record_or_root
    manifest_path = record.get("_manifest_path")
    root = manifest_path.parent if isinstance(manifest_path, Path) else None
    filename = str(record.get("_manifest_filename") or "")
    errors, warnings = validate_pack_candidate_shape(record)
    pack_kind = normalize_pack_kind(record, filename=filename)
    validation_status = "validator_not_run"
    validator_command = None
    validator_exit_code = None
    if run_validators and root is not None and filename != "PACK_IMPORT_DRY_RUN_INPUT.json":
        validator_result = run_validator_for_pack(root, pack_kind)
        validation_status = normalize_enum(validator_result.validation_status, VALIDATION_STATUSES)
        validator_command = validator_result.validator_command
        validator_exit_code = validator_result.exit_code
        if validator_result.warning:
            warnings.append(validator_result.warning)
        if validation_status == "invalid":
            errors.append("validator failed for pack candidate")
        elif validation_status == "validator_missing":
            warnings.append(f"validator missing for {pack_kind}")
    elif run_validators and filename == "PACK_IMPORT_DRY_RUN_INPUT.json":
        warnings.append("synthetic dry-run input classified without invoking pack validators")

    if validation_status == "unknown":
        validation_status = "validator_not_run"
    return PackCandidateSummary(
        pack_id=_pack_id(record) or "unknown",
        path=repo_relative(manifest_path if isinstance(manifest_path, Path) else Path(".")),
        pack_kind=pack_kind,
        schema_version=_schema_version(record),
        validation_status=validation_status,
        privacy_status=_privacy_status(record),
        public_safety_status=_public_safety_status(record),
        risk_status=_risk_status(record),
        mutation_impact=_mutation_impact(record, pack_kind),
        promotion_readiness=_promotion_readiness(record, pack_kind),
        valid=not errors,
        pack_version=_pack_version(record),
        title=_title(record),
        validator_command=validator_command,
        validator_exit_code=validator_exit_code,
        summary_text=_summary(record),
        warnings=tuple(sorted(set(warnings))),
        errors=tuple(sorted(set(errors))),
    )


def run_pack_import_dry_run(
    roots: Iterable[Path] | None = None,
    strict: bool = False,
    *,
    run_validators: bool = True,
    enforce_approved_roots: bool = False,
    allow_temp_roots: bool = False,
):
    """Run a local dry-run over approved pack example roots."""

    input_roots = tuple(Path(root) for root in (roots or (PACK_IMPORT_DRY_RUN_ROOT,)))
    summaries: list[PackCandidateSummary] = []
    report_errors: list[PackImportDryRunErrorRecord] = []
    warnings: list[str] = []
    for root in input_roots:
        try:
            checked_root = ensure_approved_input_root(root, allow_temp=allow_temp_roots) if enforce_approved_roots else root.resolve()
        except Exception as exc:
            report_errors.append(PackImportDryRunErrorRecord("input_root_rejected", str(exc), str(root)))
            continue
        manifest_paths = discover_pack_candidates(checked_root)
        if not manifest_paths:
            warnings.append(f"no pack dry-run manifests found under {repo_relative(checked_root)}")
        for manifest_path in manifest_paths:
            try:
                summaries.append(classify_pack_candidate(manifest_path, run_validators=run_validators))
            except Exception as exc:
                report_errors.append(PackImportDryRunErrorRecord("pack_load_failed", str(exc), repo_relative(manifest_path)))
    if strict and not summaries:
        report_errors.append(PackImportDryRunErrorRecord("strict_no_packs", "strict mode requires at least one pack candidate"))
    return build_report(
        input_roots=(repo_relative(root) for root in input_roots),
        packs=summaries,
        warnings=warnings,
        errors=report_errors,
    )


def _manifest_path(path: Path) -> Path:
    if path.is_file():
        return path
    for filename in MANIFEST_FILENAMES:
        candidate = path / filename
        if candidate.is_file():
            return candidate
    raise ValueError(f"{path} does not contain a known pack manifest")


def _pack_id(record: Mapping[str, Any]) -> str | None:
    for key in ("pack_id", "pack_set_id", "dry_run_input_id"):
        value = record.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _schema_version(record: Mapping[str, Any]) -> str:
    for key in ("pack_schema_version", "schema_version"):
        value = record.get(key)
        if isinstance(value, str) and value:
            return value
    return "unknown"


def _pack_version(record: Mapping[str, Any]) -> str | None:
    value = record.get("pack_version")
    return value if isinstance(value, str) and value else None


def _title(record: Mapping[str, Any]) -> str | None:
    value = record.get("title")
    return value if isinstance(value, str) and value else None


def _summary(record: Mapping[str, Any]) -> str | None:
    for key in ("summary", "description"):
        value = record.get(key)
        if isinstance(value, str) and value:
            return value
        if isinstance(value, Mapping):
            nested = value.get("text") or value.get("summary_text")
            if isinstance(nested, str) and nested:
                return nested
    return None


def _privacy_status(record: Mapping[str, Any]) -> str:
    explicit = normalize_enum(record.get("privacy_status"), PRIVACY_STATUSES)
    if explicit != "unknown":
        return explicit
    privacy = record.get("privacy")
    if isinstance(privacy, Mapping):
        for key in ("classification", "privacy_classification"):
            status = normalize_enum(privacy.get(key), PRIVACY_STATUSES)
            if status != "unknown":
                return status
        if privacy.get("contains_private_paths") is True or privacy.get("contains_credentials") is True:
            return "rejected_sensitive"
    return "unknown"


def _public_safety_status(record: Mapping[str, Any]) -> str:
    explicit = normalize_enum(record.get("public_safety_status"), PUBLIC_SAFETY_STATUSES)
    if explicit != "unknown":
        return explicit
    privacy = _privacy_status(record)
    if privacy == "public_safe":
        return "public_safe"
    if privacy in {"redacted", "local_private", "unknown"}:
        return "review_required"
    if privacy == "rejected_sensitive":
        return "rejected"
    return "unknown"


def _risk_status(record: Mapping[str, Any]) -> str:
    explicit = normalize_enum(record.get("risk_status"), RISK_STATUSES)
    if explicit != "unknown":
        return explicit
    policy_errors = scan_pack_policy(record)
    if any("URL" in error for error in policy_errors):
        return "URL_fetch_risk"
    if any("secret" in error or "sensitive" in error for error in policy_errors):
        return "credential_risk"
    if any("private path" in error for error in policy_errors):
        return "private_data_risk"
    if any("executable" in error or "script" in error for error in policy_errors):
        return "executable_reference"
    if any("mutation" in error or "promotion" in error for error in policy_errors):
        return "mutation_risk"
    return "metadata_only"


def _mutation_impact(record: Mapping[str, Any], pack_kind: str) -> str:
    explicit = normalize_enum(record.get("mutation_impact"), MUTATION_IMPACTS, MUTATION_IMPACT_ALIASES)
    if explicit != "unknown":
        return explicit
    if any("mutation" in error or "promotion" in error for error in scan_pack_policy(record)):
        return "blocked_mutation_claim"
    by_kind = {
        "source_pack": "source_cache_candidate_effect",
        "evidence_pack": "evidence_ledger_candidate_effect",
        "index_pack": "public_index_candidate_effect",
        "contribution_pack": "candidate_index_candidate_effect",
        "pack_set": "candidate_index_candidate_effect",
    }
    return by_kind.get(pack_kind, "unknown")


def _promotion_readiness(record: Mapping[str, Any], pack_kind: str) -> str:
    explicit = normalize_enum(record.get("promotion_readiness"), PROMOTION_READINESS)
    if explicit != "unknown":
        return explicit
    if any("promotion" in error or "accepted" in error for error in scan_pack_policy(record)):
        return "blocked"
    if pack_kind == "contribution_pack":
        return "review_required"
    return "not_ready"

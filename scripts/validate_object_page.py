#!/usr/bin/env python3
"""Validate Eureka Object Page Contract v0 examples.

The validator is stdlib-only and local-only. It opens no network connections,
performs no live source calls, and mutates no indexes, source cache, evidence
ledger, candidate index, or object-page store.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = REPO_ROOT / "examples" / "object_pages"

TOP_LEVEL_REQUIRED = {
    "schema_version",
    "object_page_id",
    "object_page_kind",
    "status",
    "created_by_tool",
    "object_identity",
    "object_status",
    "title",
    "summary",
    "versions_states_releases",
    "representations",
    "members",
    "sources",
    "evidence",
    "compatibility",
    "rights_risk_action_posture",
    "conflicts",
    "absence_near_misses_gaps",
    "result_card_projection",
    "api_projection",
    "static_projection",
    "privacy",
    "limitations",
    "no_runtime_guarantees",
    "no_mutation_guarantees",
    "notes",
}
HARD_FALSE_FIELDS = {
    "runtime_object_page_implemented",
    "persistent_object_page_store_implemented",
    "object_page_generated_from_live_source",
    "live_source_called",
    "external_calls_performed",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "candidate_promotion_performed",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
    "downloads_enabled",
    "uploads_enabled",
    "installs_enabled",
    "execution_enabled",
    "arbitrary_url_fetch_enabled",
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "telemetry_exported",
}
PAGE_STATUSES = {
    "draft_example",
    "dry_run_validated",
    "synthetic_example",
    "public_safe_example",
    "candidate_only",
    "review_required",
    "runtime_future",
    "rejected_by_policy",
}
OBJECT_KINDS = {
    "software",
    "software_version",
    "driver",
    "manual_or_documentation",
    "source_code_release",
    "package_metadata",
    "web_capture",
    "article_or_scan_segment",
    "file_inside_container",
    "compatibility_evidence",
    "source_identity",
    "collection",
    "unknown",
}
LANES = {"official", "preservation", "community", "candidate", "absence", "conflicted", "demo", "unknown"}
VERIFICATION_STATUSES = {
    "fixture_backed",
    "evidence_backed",
    "candidate_only",
    "review_required",
    "insufficient_evidence",
    "conflicted",
    "synthetic_example",
}
COMPATIBILITY_STATUSES = {
    "known_supported",
    "likely_supported",
    "unknown",
    "likely_unsupported",
    "conflicting",
    "evidence_required",
}
GAP_TYPES = {
    "source_coverage_gap",
    "capability_gap",
    "compatibility_evidence_gap",
    "member_access_gap",
    "representation_gap",
    "query_interpretation_gap",
    "live_probe_disabled",
    "external_baseline_pending",
    "deep_extraction_missing",
    "OCR_missing",
    "source_cache_missing",
    "evidence_ledger_missing",
    "unknown",
}
PRIVATE_PATH_RE = re.compile(r"([A-Za-z]:[\\/]|\\\\|file://|/(?:home|users|tmp|var|etc)/)", re.IGNORECASE)
SECRET_RE = re.compile(r"(api[_-]?key\s*=|auth[_-]?token\s*=|password\s*=|secret\s*=|token\s*=)", re.IGNORECASE)
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
ACCOUNT_RE = re.compile(r"\b(?:account|user)[_-]?id\s*[:=]", re.IGNORECASE)


def validate_page(path: Path, *, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    payload = _read_json(path, errors)
    if isinstance(payload, Mapping):
        _validate_payload(payload, errors)
        _scan_sensitive_values(payload, errors)
    return {
        "status": "valid" if not errors else "invalid",
        "page": _rel(path),
        "errors": errors,
        "warnings": warnings,
        "strict": strict,
    }


def validate_page_root(root: Path, *, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    page_path = root / "OBJECT_PAGE.json"
    page_report = validate_page(page_path, strict=strict)
    errors.extend(page_report["errors"])
    warnings.extend(page_report["warnings"])
    _validate_checksums(root, errors)
    return {
        "status": "valid" if not errors else "invalid",
        "page_root": _rel(root),
        "errors": errors,
        "warnings": warnings,
        "strict": strict,
    }


def validate_all_examples(*, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    roots = [path for path in sorted(EXAMPLES_ROOT.iterdir()) if path.is_dir()] if EXAMPLES_ROOT.is_dir() else []
    if not roots:
        errors.append("examples/object_pages: no example roots found.")
    reports = []
    for root in roots:
        report = validate_page_root(root, strict=strict)
        reports.append(report)
        errors.extend(f"{report['page_root']}: {error}" for error in report["errors"])
        warnings.extend(f"{report['page_root']}: {warning}" for warning in report["warnings"])
    return {
        "status": "valid" if not errors else "invalid",
        "example_count": len(roots),
        "examples": [_rel(root) for root in roots],
        "reports": reports,
        "errors": errors,
        "warnings": warnings,
        "strict": strict,
    }


def _validate_payload(page: Mapping[str, Any], errors: list[str]) -> None:
    missing = sorted((TOP_LEVEL_REQUIRED | HARD_FALSE_FIELDS) - set(page))
    if missing:
        errors.append(f"missing required top-level fields: {', '.join(missing)}")
    if page.get("schema_version") != "0.1.0":
        errors.append("schema_version must be 0.1.0.")
    if page.get("object_page_kind") != "object_page":
        errors.append("object_page_kind must be object_page.")
    if page.get("status") not in PAGE_STATUSES:
        errors.append("status is not an allowed Object Page v0 status.")
    for key in sorted(HARD_FALSE_FIELDS):
        if page.get(key) is not False:
            errors.append(f"{key} must be false.")

    identity = _mapping(page.get("object_identity"))
    if identity.get("object_kind") not in OBJECT_KINDS:
        errors.append("object_identity.object_kind is not allowed.")
    if identity.get("identity_not_truth") is not True:
        errors.append("object_identity.identity_not_truth must be true.")
    if identity.get("identity_status") not in {"accepted_fixture", "candidate", "review_required", "conflicted", "unknown"}:
        errors.append("object_identity.identity_status is not allowed.")

    status = _mapping(page.get("object_status"))
    if status.get("page_lane") not in LANES:
        errors.append("object_status.page_lane is not allowed.")
    if status.get("verification_status") not in VERIFICATION_STATUSES:
        errors.append("object_status.verification_status is not allowed.")

    for item in _list(page.get("evidence")):
        evidence = _mapping(item)
        if evidence.get("confidence_not_truth") is not True:
            errors.append(f"evidence {evidence.get('evidence_ref', '<unknown>')} confidence_not_truth must be true.")
    compatibility = _mapping(page.get("compatibility"))
    if compatibility.get("compatibility_status") not in COMPATIBILITY_STATUSES:
        errors.append("compatibility.compatibility_status is not allowed.")

    posture = _mapping(page.get("rights_risk_action_posture"))
    for key in (
        "downloads_enabled",
        "installs_enabled",
        "execution_enabled",
        "uploads_enabled",
        "mirroring_enabled",
        "arbitrary_url_fetch_enabled",
        "rights_clearance_claimed",
        "malware_safety_claimed",
    ):
        if posture.get(key) is not False:
            errors.append(f"rights_risk_action_posture.{key} must be false.")
    disabled = set(posture.get("disabled_actions", [])) if isinstance(posture.get("disabled_actions"), list) else set()
    for action in ("download", "install", "execute", "upload", "mirror", "arbitrary_url_fetch"):
        if action not in disabled:
            errors.append(f"rights_risk_action_posture.disabled_actions must include {action}.")

    for item in _list(page.get("representations")):
        representation = _mapping(item)
        if representation.get("payload_included") is not False:
            errors.append(f"representation {representation.get('representation_ref', '<unknown>')} payload_included must be false.")
        if representation.get("downloads_enabled") is not False:
            errors.append(f"representation {representation.get('representation_ref', '<unknown>')} downloads_enabled must be false.")

    for item in _list(page.get("conflicts")):
        conflict = _mapping(item)
        if conflict.get("destructive_merge_allowed") is not False:
            errors.append(f"conflict {conflict.get('conflict_id', '<unknown>')} destructive_merge_allowed must be false.")

    absence = _mapping(page.get("absence_near_misses_gaps"))
    if absence.get("global_absence_claimed") is not False:
        errors.append("absence_near_misses_gaps.global_absence_claimed must be false.")
    for gap in _list(absence.get("gaps")):
        if _mapping(gap).get("gap_type") not in GAP_TYPES:
            errors.append("absence_near_misses_gaps.gaps contains an unknown gap_type.")

    api = _mapping(page.get("api_projection"))
    if api.get("implemented_now") is not False:
        errors.append("api_projection.implemented_now must be false.")

    privacy = _mapping(page.get("privacy"))
    for key in (
        "contains_private_path",
        "contains_secret",
        "contains_private_url",
        "contains_user_identifier",
        "contains_ip_address",
        "contains_raw_private_query",
    ):
        if privacy.get(key) is not False:
            errors.append(f"privacy.{key} must be false for public examples.")
    if privacy.get("publishable") is not True:
        errors.append("privacy.publishable must be true for committed examples.")


def _scan_sensitive_values(value: Any, errors: list[str], path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            if key_text in {"private_local_path", "raw_source_payload", "download_url", "install_url", "execute_url"}:
                errors.append(f"{path}.{key_text}: forbidden public object-page key.")
            _scan_sensitive_values(child, errors, f"{path}.{key_text}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_sensitive_values(child, errors, f"{path}[{index}]")
    elif isinstance(value, str):
        if PRIVATE_PATH_RE.search(value):
            errors.append(f"{path}: contains a private or absolute local path.")
        if SECRET_RE.search(value):
            errors.append(f"{path}: contains credential-like material.")
        if IP_RE.search(value):
            errors.append(f"{path}: contains an IP address.")
        if ACCOUNT_RE.search(value):
            errors.append(f"{path}: contains an account or user identifier.")


def _validate_checksums(root: Path, errors: list[str]) -> None:
    checksums = root / "CHECKSUMS.SHA256"
    if not checksums.is_file():
        errors.append("CHECKSUMS.SHA256 is missing.")
        return
    expected: dict[str, str] = {}
    for line in checksums.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != 2:
            errors.append("CHECKSUMS.SHA256 contains an invalid line.")
            continue
        expected[parts[1]] = parts[0]
    actual: dict[str, str] = {}
    for path in sorted(root.iterdir()):
        if path.is_file() and path.name != "CHECKSUMS.SHA256":
            actual[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    if expected != actual:
        errors.append("CHECKSUMS.SHA256 does not match example files.")


def _read_json(path: Path, errors: list[str]) -> Any:
    if not path.is_file():
        errors.append(f"{_rel(path)}: missing.")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)}: invalid JSON at line {exc.lineno}: {exc.msg}.")
        return None


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Object Page validation",
        f"status: {report['status']}",
    ]
    if "example_count" in report:
        lines.append(f"example_count: {report['example_count']}")
    if "page" in report:
        lines.append(f"page: {report['page']}")
    if "page_root" in report:
        lines.append(f"page_root: {report['page_root']}")
    if report.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report.get("warnings"):
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--page", help="Path to OBJECT_PAGE.json.")
    parser.add_argument("--page-root", help="Path to an example root containing OBJECT_PAGE.json.")
    parser.add_argument("--all-examples", action="store_true", help="Validate all committed examples.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--strict", action="store_true", help="Enable strict mode; currently all checks are strict.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    selected = sum(bool(value) for value in (args.page, args.page_root, args.all_examples))
    if selected != 1:
        parser.error("Choose exactly one of --page, --page-root, or --all-examples.")
    if args.page:
        report = validate_page(Path(args.page), strict=args.strict)
    elif args.page_root:
        report = validate_page_root(Path(args.page_root), strict=args.strict)
    else:
        report = validate_all_examples(strict=args.strict)

    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())

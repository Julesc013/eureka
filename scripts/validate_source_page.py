#!/usr/bin/env python3
"""Validate Eureka Source Page Contract v0 examples.

The validator is stdlib-only and local-only. It opens no network connections,
performs no live source calls, and mutates no source cache, evidence ledger,
candidate index, public index, local index, master index, or source-page store.
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
EXAMPLES_ROOT = REPO_ROOT / "examples" / "source_pages"

TOP_LEVEL_REQUIRED = {
    "schema_version",
    "source_page_id",
    "source_page_kind",
    "status",
    "created_by_tool",
    "source_identity",
    "source_status",
    "title",
    "summary",
    "coverage",
    "connector_posture",
    "source_policy",
    "source_cache_projection",
    "evidence_ledger_projection",
    "public_index_projection",
    "public_search_projection",
    "query_intelligence_projection",
    "limitations_and_gaps",
    "trust_and_provenance_caution",
    "rights_access_risk_posture",
    "result_card_source_badge_projection",
    "api_projection",
    "static_projection",
    "privacy",
    "no_runtime_guarantees",
    "no_mutation_guarantees",
    "notes",
}
HARD_FALSE_FIELDS = {
    "runtime_source_page_implemented",
    "persistent_source_page_store_implemented",
    "source_page_generated_from_live_source",
    "connector_runtime_implemented",
    "connector_live_enabled",
    "live_source_called",
    "external_calls_performed",
    "source_sync_worker_executed",
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
    "source_trust_claimed",
    "telemetry_exported",
}
PAGE_STATUSES = {
    "draft_example",
    "dry_run_validated",
    "synthetic_example",
    "public_safe_example",
    "fixture_source",
    "recorded_fixture_source",
    "placeholder_source",
    "approval_required",
    "runtime_future",
    "rejected_by_policy",
}
SOURCE_FAMILIES = {
    "internet_archive",
    "wayback_cdx_memento",
    "github_releases",
    "pypi",
    "npm",
    "software_heritage",
    "wikidata_open_library",
    "sourceforge",
    "local_fixture",
    "recorded_fixture",
    "manual_baseline",
    "source_pack",
    "evidence_pack",
    "local_private_future",
    "placeholder",
    "unknown",
}
STATUS_CLASSES = {"active_fixture", "active_recorded_fixture", "placeholder", "future", "approval_required", "disabled", "local_private_future", "unknown"}
COVERAGE_DEPTHS = {"none", "placeholder", "fixture_only", "recorded_fixture", "metadata_summary_future", "source_cache_future", "evidence_ledger_future", "unknown"}
CONNECTOR_STATUSES = {"not_applicable", "no_connector", "approval_required", "approved_future", "runtime_future", "disabled", "fixture_only", "unknown"}
SOURCE_POLICY_STATUSES = {"not_applicable", "not_reviewed", "review_required", "fixture_only", "approved_future", "disabled", "unknown"}
GAP_TYPES = {
    "source_coverage_gap",
    "connector_approval_gap",
    "source_policy_review_gap",
    "live_probe_disabled",
    "source_cache_missing",
    "evidence_ledger_missing",
    "compatibility_evidence_gap",
    "member_access_gap",
    "representation_gap",
    "external_baseline_pending",
    "manual_observation_pending",
    "unknown",
}
PRIVATE_PATH_RE = re.compile(r"([A-Za-z]:[\\/]|\\\\|file://|/(?:home|users|tmp|var|etc)/)", re.IGNORECASE)
SECRET_RE = re.compile(r"(api[_-]?key\s*=|auth[_-]?token\s*=|password\s*=|secret\s*=|token\s*=)", re.IGNORECASE)
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
ACCOUNT_RE = re.compile(r"\b(?:account|user)[_-]?id\s*[:=]", re.IGNORECASE)
FORBIDDEN_KEYS = {
    "private_local_path",
    "raw_source_payload",
    "download_url",
    "install_url",
    "execute_url",
    "source_credentials",
    "connector_path",
    "source_cache_path",
    "evidence_ledger_path",
    "candidate_path",
    "promotion_path",
    "index_path",
    "store_root",
    "local_path",
    "database_path",
    "source_root",
}


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
    page_path = root / "SOURCE_PAGE.json"
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
        errors.append("examples/source_pages: no example roots found.")
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
    if page.get("source_page_kind") != "source_page":
        errors.append("source_page_kind must be source_page.")
    if page.get("status") not in PAGE_STATUSES:
        errors.append("status is not an allowed Source Page v0 status.")
    for key in sorted(HARD_FALSE_FIELDS):
        if page.get(key) is not False:
            errors.append(f"{key} must be false.")

    identity = _mapping(page.get("source_identity"))
    if identity.get("source_family") not in SOURCE_FAMILIES:
        errors.append("source_identity.source_family is not allowed.")
    if identity.get("identity_status") not in {"inventory_backed", "fixture_backed", "recorded_fixture_backed", "placeholder", "future", "approval_required", "unknown"}:
        errors.append("source_identity.identity_status is not allowed.")

    status = _mapping(page.get("source_status"))
    if status.get("status_class") not in STATUS_CLASSES:
        errors.append("source_status.status_class is not allowed.")
    for key in (
        "live_enabled",
        "connector_runtime_implemented",
        "source_cache_runtime_implemented",
        "evidence_ledger_runtime_implemented",
        "public_search_live_fanout_allowed",
    ):
        if status.get(key) is not False:
            errors.append(f"source_status.{key} must be false.")

    coverage = _mapping(page.get("coverage"))
    if coverage.get("coverage_depth") not in COVERAGE_DEPTHS:
        errors.append("coverage.coverage_depth is not allowed.")
    if coverage.get("source_coverage_claim_not_exhaustive") is not True:
        errors.append("coverage.source_coverage_claim_not_exhaustive must be true.")

    posture = _mapping(page.get("connector_posture"))
    if posture.get("connector_status") not in CONNECTOR_STATUSES:
        errors.append("connector_posture.connector_status is not allowed.")
    if posture.get("connector_status") == "approval_required" and not posture.get("connector_approval_refs"):
        errors.append("connector_posture.connector_approval_refs must be present for approval_required examples.")

    source_policy = _mapping(page.get("source_policy"))
    if source_policy.get("source_policy_status") not in SOURCE_POLICY_STATUSES:
        errors.append("source_policy.source_policy_status is not allowed.")

    cache = _mapping(page.get("source_cache_projection"))
    if cache.get("source_cache_mutation_allowed_now") is not False:
        errors.append("source_cache_projection.source_cache_mutation_allowed_now must be false.")
    ledger = _mapping(page.get("evidence_ledger_projection"))
    if ledger.get("evidence_ledger_mutation_allowed_now") is not False:
        errors.append("evidence_ledger_projection.evidence_ledger_mutation_allowed_now must be false.")
    public_index = _mapping(page.get("public_index_projection"))
    if public_index.get("public_index_mutation_allowed_now") is not False:
        errors.append("public_index_projection.public_index_mutation_allowed_now must be false.")
    public_search = _mapping(page.get("public_search_projection"))
    if public_search.get("public_search_live_fanout_allowed") is not False:
        errors.append("public_search_projection.public_search_live_fanout_allowed must be false.")
    if public_search.get("public_search_reads_live_connector_now") is not False:
        errors.append("public_search_projection.public_search_reads_live_connector_now must be false.")
    qi = _mapping(page.get("query_intelligence_projection"))
    if qi.get("query_intelligence_mutation_allowed_now") is not False:
        errors.append("query_intelligence_projection.query_intelligence_mutation_allowed_now must be false.")

    gaps = _mapping(page.get("limitations_and_gaps"))
    if not gaps.get("limitations"):
        errors.append("limitations_and_gaps.limitations must be present.")
    if not gaps.get("gaps"):
        errors.append("limitations_and_gaps.gaps must be present.")
    for gap in _list(gaps.get("gaps")):
        if _mapping(gap).get("gap_type") not in GAP_TYPES:
            errors.append("limitations_and_gaps.gaps contains an unknown gap_type.")

    trust = _mapping(page.get("trust_and_provenance_caution"))
    if trust.get("source_trust_claimed") is not False:
        errors.append("trust_and_provenance_caution.source_trust_claimed must be false.")

    risk = _mapping(page.get("rights_access_risk_posture"))
    for key in (
        "downloads_enabled",
        "mirroring_enabled",
        "installs_enabled",
        "execution_enabled",
        "uploads_enabled",
        "arbitrary_url_fetch_enabled",
        "rights_clearance_claimed",
        "malware_safety_claimed",
    ):
        if risk.get(key) is not False:
            errors.append(f"rights_access_risk_posture.{key} must be false.")
    disabled = set(risk.get("disabled_actions", [])) if isinstance(risk.get("disabled_actions"), list) else set()
    for action in ("live_probe", "download", "mirror", "install", "execute", "upload", "arbitrary_url_fetch"):
        if action not in disabled:
            errors.append(f"rights_access_risk_posture.disabled_actions must include {action}.")

    api = _mapping(page.get("api_projection"))
    if api.get("implemented_now") is not False:
        errors.append("api_projection.implemented_now must be false.")
    static = _mapping(page.get("static_projection"))
    if static.get("generated_static_artifact") not in (False, True):
        errors.append("static_projection.generated_static_artifact must be a boolean.")

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
            if key_text in FORBIDDEN_KEYS:
                errors.append(f"{path}.{key_text}: forbidden public source-page key.")
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
        "Source Page validation",
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
    parser.add_argument("--page", help="Path to SOURCE_PAGE.json.")
    parser.add_argument("--page-root", help="Path to an example root containing SOURCE_PAGE.json.")
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

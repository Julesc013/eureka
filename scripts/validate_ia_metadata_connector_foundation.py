#!/usr/bin/env python3
"""Validate IA-BUNDLE-01 metadata connector foundation artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.connectors.internet_archive import (  # noqa: E402
    detect_product_boundary_violations,
    detect_truth_boundary_violations,
    load_fixture,
    map_normalized_to_source_cache_candidate,
    normalize_ia_metadata,
    preview_evidence_candidates,
    validate_no_live_call_boundary,
)


AUDIT_DIR = Path("control/audits/ia-bundle-01-metadata-connector-foundation-v0")
REPORT_PATH = AUDIT_DIR / "ia_bundle_01_report.json"
FIXTURE_ROOT = Path("examples/connectors/internet_archive/fixtures")
NORMALIZED_ROOT = Path("examples/connectors/internet_archive/normalized")
FIXTURE_NAMES = (
    "minimal_item_metadata.json",
    "software_item_metadata.json",
    "manual_item_metadata.json",
    "multi_file_item_metadata.json",
    "policy_blocked_item_metadata.json",
)
NORMALIZED_NAMES = (
    "minimal_item_normalized.json",
    "software_item_normalized.json",
    "manual_item_normalized.json",
    "multi_file_item_normalized.json",
    "policy_blocked_item_normalized.json",
)
REQUIRED_JSON_PATHS = (
    "contracts/connectors/internet_archive_metadata_connector.v0.json",
    "contracts/connectors/source_connector_fixture.v0.json",
    "control/inventory/connectors/internet_archive_source_policy.json",
    "control/inventory/connectors/internet_archive_endpoint_policy.json",
    "control/inventory/connectors/internet_archive_rate_limit_policy.json",
    "control/inventory/connectors/internet_archive_cache_policy.json",
    "control/inventory/connectors/internet_archive_kill_switch_policy.json",
    "control/inventory/connectors/internet_archive_fixture_policy.json",
    "control/inventory/connectors/internet_archive_normalization_policy.json",
    "control/inventory/connectors/internet_archive_source_cache_mapping_policy.json",
    "control/inventory/connectors/internet_archive_evidence_mapping_policy.json",
    REPORT_PATH.as_posix(),
)
REQUIRED_DOCS = (
    "docs/reference/INTERNET_ARCHIVE_METADATA_CONNECTOR.md",
    "docs/architecture/IA_METADATA_CONNECTOR_MODEL.md",
    "docs/operations/IA_METADATA_SOURCE_POLICY.md",
    "docs/operations/IA_METADATA_FIXTURE_REPLAY.md",
    "docs/operations/IA_METADATA_NO_LIVE_CALL_POLICY.md",
)
REQUIRED_AUDIT_FILES = (
    "README.md",
    "ia_bundle_01_report.json",
    "source_policy_decision_packet.md",
    "fixture_normalization_report.md",
    "source_cache_mapping_report.md",
    "evidence_mapping_report.md",
    "live_call_block_report.md",
    "validation.md",
    "generated/sample_normalized_ia_metadata.json",
    "generated/sample_source_cache_candidate.json",
    "generated/sample_evidence_candidate_preview.json",
)
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|urllib|http|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)
NETWORK_IMPORT_SCAN_PATHS = (
    "runtime/connectors/internet_archive/__init__.py",
    "runtime/connectors/internet_archive/fixture_loader.py",
    "runtime/connectors/internet_archive/metadata_normalizer.py",
    "scripts/normalize_ia_metadata_fixture.py",
    "scripts/validate_ia_metadata_connector_foundation.py",
)


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    payloads: dict[str, Mapping[str, Any]] = {}
    for rel in REQUIRED_JSON_PATHS:
        path = root / rel
        payloads[rel] = load_json_object(path, errors)
    for rel in REQUIRED_DOCS:
        if not (root / rel).is_file():
            errors.append(f"missing doc: {rel}")
    validate_audit_files(root, errors)
    validate_policies(payloads, errors)
    validate_report(payloads.get(REPORT_PATH.as_posix(), {}), errors)
    validate_fixture_examples(root, errors)
    validate_generated_outputs(root, errors)
    validate_import_scans(root, errors)
    return {
        "status": "valid" if not errors else "invalid",
        "task": "IA-BUNDLE-01",
        "fixture_count": len(FIXTURE_NAMES),
        "errors": errors,
    }


def load_json_object(path: Path, errors: list[str]) -> Mapping[str, Any]:
    if not path.is_file():
        errors.append(f"missing JSON: {rel(path)}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - deterministic validator surface.
        errors.append(f"invalid JSON: {rel(path)}: {exc}")
        return {}
    if not isinstance(payload, Mapping):
        errors.append(f"JSON must be an object: {rel(path)}")
        return {}
    return payload


def validate_audit_files(root: Path, errors: list[str]) -> None:
    for rel_name in REQUIRED_AUDIT_FILES:
        path = root / AUDIT_DIR / rel_name
        if not path.is_file():
            errors.append(f"missing audit file: {(AUDIT_DIR / rel_name).as_posix()}")


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    source = payloads.get("control/inventory/connectors/internet_archive_source_policy.json", {})
    require_value(source, "source_id", "internet_archive", errors)
    require_value(source, "source_family", "archive_metadata", errors)
    require_value(source, "connector_scope", "metadata_only_foundation", errors)
    require_value(source, "current_status", "fixture_only", errors)
    require_false(source, ("live_access_approved", "metadata_probe_approved", "file_download_approved", "item_file_fetch_approved", "scraping_approved", "public_query_fanout_approved"), "source_policy", errors)
    if source.get("source_cache_write_approved_current") != "fixture_only":
        errors.append("source_policy.source_cache_write_approved_current must be fixture_only")
    if source.get("evidence_candidate_generation_approved_current") != "fixture_only":
        errors.append("source_policy.evidence_candidate_generation_approved_current must be fixture_only")
    if source.get("human_review_required") is not True:
        errors.append("source_policy.human_review_required must be true")
    if source.get("operator_approval_required_for_live_access") is not True:
        errors.append("source_policy.operator_approval_required_for_live_access must be true")

    endpoint = payloads.get("control/inventory/connectors/internet_archive_endpoint_policy.json", {})
    require_value(endpoint, "current_allowed_endpoint_behavior", "committed_fixture_only", errors)
    require_false(endpoint, ("current_live_access_approved", "current_network_calls_allowed"), "endpoint_policy", errors)
    forbidden = endpoint.get("forbidden_current")
    if not isinstance(forbidden, Mapping):
        errors.append("endpoint_policy.forbidden_current must be an object")
    else:
        for key in ("downloads", "file_fetches", "item_file_downloads", "unbounded_search", "account_access", "login_session_use", "scraping", "crawling", "public_query_live_fanout", "malware_safety_claims", "rights_claims", "installability_claims"):
            if forbidden.get(key) is not True:
                errors.append(f"endpoint_policy.forbidden_current.{key} must be true")

    rate = payloads.get("control/inventory/connectors/internet_archive_rate_limit_policy.json", {})
    require_value(rate, "decision_status", "pending_operator_approval", errors)
    require_value(rate, "proposed_user_agent", "pending", errors)
    require_value(rate, "contact_email", "pending", errors)
    require_value(rate, "max_requests_per_minute", "pending", errors)
    require_value(rate, "timeout_seconds", "pending", errors)
    require_value(rate, "retry_policy", "pending", errors)
    require_value(rate, "cache_ttl", "pending", errors)
    require_value(rate, "kill_switch_name", "IA_METADATA_CONNECTOR_ENABLED", errors)
    require_false(rate, ("default_enabled", "live_access_approved"), "rate_limit_policy", errors)
    require_value(rate, "failure_mode", "fail_closed", errors)

    cache = payloads.get("control/inventory/connectors/internet_archive_cache_policy.json", {})
    require_value(cache, "decision_status", "pending_operator_approval", errors)
    require_value(cache, "cache_ttl", "pending", errors)
    require_false(cache, ("live_response_cache_write_approved", "public_search_reads_live_source", "raw_payload_retention_approved"), "cache_policy", errors)

    kill = payloads.get("control/inventory/connectors/internet_archive_kill_switch_policy.json", {})
    require_value(kill, "decision_status", "pending_operator_approval", errors)
    require_value(kill, "kill_switch_name", "IA_METADATA_CONNECTOR_ENABLED", errors)
    require_false(kill, ("default_enabled", "live_access_approved", "live_probe_enabled", "source_sync_enabled", "connector_runtime_enabled"), "kill_switch_policy", errors)
    require_value(kill, "failure_mode", "fail_closed", errors)


def validate_report(report: Mapping[str, Any], errors: list[str]) -> None:
    require_value(report, "schema_version", "ia_bundle_01_report.v0", errors)
    require_value(report, "task", "IA-BUNDLE-01", errors)
    runtime_scope = require_mapping(report, "runtime_scope", errors)
    truth = require_mapping(report, "truth_boundary", errors)
    product = require_mapping(report, "product_boundary", errors)
    require_false(runtime_scope, ("live_connector_enabled", "network_calls_made", "api_calls_made", "downloads_made", "source_cache_runtime_mutated", "evidence_ledger_runtime_mutated"), "report.runtime_scope", errors)
    require_false(truth, ("ia_metadata_is_public_truth", "source_cache_preview_is_accepted_source", "evidence_preview_is_accepted_evidence", "candidate_truth_accepted", "public_index_mutated", "master_index_mutated", "rights_clearance_claimed", "malware_safety_claimed", "verified_installability_claimed"), "report.truth_boundary", errors)
    require_false(product, ("changed_public_search_behavior", "enabled_hosting", "enabled_live_probes", "enabled_source_sync", "enabled_source_connectors", "enabled_downloads", "enabled_uploads", "enabled_accounts", "enabled_telemetry", "mutated_public_index", "mutated_master_index"), "report.product_boundary", errors)


def validate_fixture_examples(root: Path, errors: list[str]) -> None:
    for fixture_name, normalized_name in zip(FIXTURE_NAMES, NORMALIZED_NAMES, strict=True):
        fixture_path = root / FIXTURE_ROOT / fixture_name
        normalized_path = root / NORMALIZED_ROOT / normalized_name
        if not fixture_path.is_file():
            errors.append(f"missing fixture: {(FIXTURE_ROOT / fixture_name).as_posix()}")
            continue
        if not normalized_path.is_file():
            errors.append(f"missing normalized example: {(NORMALIZED_ROOT / normalized_name).as_posix()}")
            continue
        fixture = load_fixture(fixture_path)
        if fixture.get("source_id") != "internet_archive":
            errors.append(f"{fixture_name}: source_id must be internet_archive")
        for key in ("live_call_used", "network_used", "external_api_used"):
            if fixture.get(key) is not False:
                errors.append(f"{fixture_name}: {key} must be false")
        errors.extend(f"{fixture_name}: {error}" for error in validate_no_live_call_boundary(fixture))
        normalized = normalize_ia_metadata(fixture)
        expected = load_json_object(normalized_path, errors)
        if expected and normalized != expected:
            errors.append(f"{normalized_name}: normalized output is stale")
        validate_boundaries(normalized, normalized_name, errors)
        source_cache = map_normalized_to_source_cache_candidate(normalized)
        evidence = preview_evidence_candidates(normalized)
        if source_cache.get("accepted_source_truth") is not False:
            errors.append(f"{fixture_name}: source-cache preview accepted_source_truth must be false")
        if evidence.get("accepted_evidence") is not False:
            errors.append(f"{fixture_name}: evidence preview accepted_evidence must be false")
        validate_boundaries(source_cache, f"{fixture_name} source-cache preview", errors)
        validate_boundaries(evidence, f"{fixture_name} evidence preview", errors)
    blocked = load_json_object(root / NORMALIZED_ROOT / "policy_blocked_item_normalized.json", errors)
    policy = blocked.get("policy")
    if isinstance(policy, Mapping) and policy.get("blocked_current") is not True:
        errors.append("policy_blocked_item_normalized.json must preserve blocked_current true")


def validate_generated_outputs(root: Path, errors: list[str]) -> None:
    generated_paths = (
        AUDIT_DIR / "generated/sample_normalized_ia_metadata.json",
        AUDIT_DIR / "generated/sample_source_cache_candidate.json",
        AUDIT_DIR / "generated/sample_evidence_candidate_preview.json",
    )
    for rel_path in generated_paths:
        payload = load_json_object(root / rel_path, errors)
        validate_boundaries(payload, rel_path.as_posix(), errors)
    source_cache = load_json_object(root / AUDIT_DIR / "generated/sample_source_cache_candidate.json", errors)
    if source_cache.get("accepted_source_truth") is not False:
        errors.append("sample_source_cache_candidate.accepted_source_truth must be false")
    evidence = load_json_object(root / AUDIT_DIR / "generated/sample_evidence_candidate_preview.json", errors)
    if evidence.get("accepted_evidence") is not False:
        errors.append("sample_evidence_candidate_preview.accepted_evidence must be false")


def validate_import_scans(root: Path, errors: list[str]) -> None:
    for rel_path in NETWORK_IMPORT_SCAN_PATHS:
        path = root / rel_path
        if not path.is_file():
            errors.append(f"missing Python file for import scan: {rel_path}")
            continue
        text = path.read_text(encoding="utf-8")
        for match in BANNED_IMPORT_RE.finditer(text):
            errors.append(f"forbidden import in {rel_path}: {match.group(1)}")


def validate_boundaries(payload: Mapping[str, Any], label: str, errors: list[str]) -> None:
    errors.extend(f"{label}: {error}" for error in detect_truth_boundary_violations(payload))
    errors.extend(f"{label}: {error}" for error in detect_product_boundary_violations(payload))


def require_mapping(payload: Mapping[str, Any], key: str, errors: list[str]) -> Mapping[str, Any]:
    value = payload.get(key)
    if not isinstance(value, Mapping):
        errors.append(f"{key} must be an object")
        return {}
    return value


def require_value(payload: Mapping[str, Any], key: str, expected: Any, errors: list[str]) -> None:
    if payload.get(key) != expected:
        errors.append(f"{key} must be {expected!r}")


def require_false(payload: Mapping[str, Any], keys: Sequence[str], label: str, errors: list[str]) -> None:
    for key in keys:
        if payload.get(key) is not False:
            errors.append(f"{label}.{key} must be false")


def rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"status: {report['status']}", file=stdout)
        for error in report["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())

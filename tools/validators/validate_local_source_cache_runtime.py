#!/usr/bin/env python3
"""Validate Track B Local Source Cache runtime artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.foundry import source_cache as runtime  # noqa: E402
from scripts import record_source_cache, summarize_source_cache  # noqa: E402


POLICY_FILES = [
    "control/inventory/source_cache/local_source_cache_record_runtime_policy.json",
    "control/inventory/source_cache/local_source_cache_record_status_policy.json",
    "control/inventory/source_cache/local_source_cache_record_type_policy.json",
    "control/inventory/source_cache/local_source_cache_input_output_policy.json",
    "control/inventory/source_cache/local_source_cache_runtime_review_policy.json",
    "control/inventory/source_cache/local_source_cache_runtime_path_policy.json",
]
DOC_FILES = [
    "docs/reference/LOCAL_SOURCE_CACHE_RUNTIME.md",
    "docs/architecture/LOCAL_SOURCE_CACHE_RUNTIME_MODEL.md",
    "docs/operations/LOCAL_SOURCE_CACHE_REVIEW.md",
]
EXAMPLE_FILES = [
    "examples/sources/cache/records/minimal_source_cache_record_v0.json",
    "examples/sources/cache/records/source_metadata_record_v0.json",
    "examples/sources/cache/records/source_locator_record_v0.json",
    "examples/sources/cache/records/source_policy_record_v0.json",
    "examples/sources/cache/records/source_coverage_record_v0.json",
    "examples/sources/cache/records/source_lead_record_v0.json",
    "examples/sources/cache/records/connector_fixture_record_v0.json",
    "examples/sources/cache/records/policy_blocked_source_cache_record_v0.json",
]
AUDIT_FILES = [
    "control/audits/track-b-15-local-source-cache-runtime-v0/README.md",
    "control/audits/track-b-15-local-source-cache-runtime-v0/track_b_15_report.json",
    "control/audits/track-b-15-local-source-cache-runtime-v0/validation.md",
    "control/audits/track-b-15-local-source-cache-runtime-v0/generated/sample_source_cache_record.json",
    "control/audits/track-b-15-local-source-cache-runtime-v0/generated/sample_source_cache_summary.md",
]
SAMPLE_REPORT = "control/audits/track-b-15-local-source-cache-runtime-v0/generated/sample_source_cache_record.json"


def validate_local_source_cache_runtime(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    for rel in sorted(POLICY_FILES + DOC_FILES + EXAMPLE_FILES + AUDIT_FILES):
        if not (repo_root / rel).exists():
            errors.append(f"missing required file: {rel}")
    if errors:
        return _report(errors)

    policies = {rel: _read_json(repo_root / rel) for rel in POLICY_FILES}
    errors.extend(_validate_policy_files(policies))

    seen_ids: dict[str, str] = {}
    for rel in sorted(EXAMPLE_FILES):
        payload = _read_json(repo_root / rel)
        record = runtime.build_source_cache_record(payload)
        errors.extend(f"{rel}: {error}" for error in runtime.validate_source_cache_record(record))
        if record["source_cache_record_id"] in seen_ids:
            errors.append(f"duplicate source_cache_record_id {record['source_cache_record_id']}: {seen_ids[record['source_cache_record_id']]} and {rel}")
        seen_ids[record["source_cache_record_id"]] = rel

    sample = _read_json(repo_root / SAMPLE_REPORT)
    errors.extend(_validate_sample_report(sample, SAMPLE_REPORT))
    errors.extend(_validate_script_checks(repo_root))
    errors.extend(_validate_output_roots(repo_root))
    errors.extend(_validate_synthetic_boundaries())
    return _report(errors)


def _validate_policy_files(policies: Mapping[str, Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    runtime_policy = policies[POLICY_FILES[0]]
    status_policy = policies[POLICY_FILES[1]]
    type_policy = policies[POLICY_FILES[2]]
    io_policy = policies[POLICY_FILES[3]]
    review_policy = policies[POLICY_FILES[4]]
    path_policy = policies[POLICY_FILES[5]]

    errors.extend(_require_values(POLICY_FILES[0], "allowed_input_types", runtime_policy, runtime.ALLOWED_INPUT_TYPES))
    errors.extend(_require_values(POLICY_FILES[0], "current_allowed_input_types", runtime_policy, runtime.CURRENT_ALLOWED_INPUT_TYPES))
    errors.extend(_require_values(POLICY_FILES[0], "forbidden_input_types", runtime_policy, runtime.FORBIDDEN_INPUT_TYPES))
    errors.extend(_require_values(POLICY_FILES[0], "allowed_statuses", runtime_policy, runtime.ALLOWED_STATUSES))
    errors.extend(_require_values(POLICY_FILES[0], "current_allowed_statuses", runtime_policy, runtime.CURRENT_ALLOWED_STATUSES))
    errors.extend(_require_values(POLICY_FILES[0], "allowed_record_types", runtime_policy, runtime.ALLOWED_RECORD_TYPES))
    errors.extend(_require_values(POLICY_FILES[0], "current_allowed_record_types", runtime_policy, runtime.CURRENT_ALLOWED_RECORD_TYPES))
    errors.extend(_require_values(POLICY_FILES[0], "allowed_source_access_modes", runtime_policy, runtime.ALLOWED_SOURCE_ACCESS_MODES))
    errors.extend(_require_values(POLICY_FILES[0], "allowed_output_types", runtime_policy, runtime.ALLOWED_OUTPUT_TYPES))
    errors.extend(_require_values(POLICY_FILES[0], "forbidden_output_types", runtime_policy, runtime.FORBIDDEN_OUTPUT_TYPES))
    errors.extend(_require_values(POLICY_FILES[1], "allowed_statuses", status_policy, runtime.ALLOWED_STATUSES))
    errors.extend(_require_values(POLICY_FILES[2], "allowed_record_types", type_policy, runtime.ALLOWED_RECORD_TYPES))
    errors.extend(_require_values(POLICY_FILES[3], "allowed_input_types", io_policy, runtime.ALLOWED_INPUT_TYPES))
    errors.extend(_require_values(POLICY_FILES[3], "forbidden_input_types", io_policy, runtime.FORBIDDEN_INPUT_TYPES))
    errors.extend(_require_values(POLICY_FILES[3], "allowed_output_types", io_policy, runtime.ALLOWED_OUTPUT_TYPES))
    errors.extend(_require_values(POLICY_FILES[3], "forbidden_output_types", io_policy, runtime.FORBIDDEN_OUTPUT_TYPES))

    if runtime_policy.get("review_required_before_downstream_use") is not True:
        errors.append(f"{POLICY_FILES[0]}: review_required_before_downstream_use must be true")
    for key in ("source_access_disabled_current", "source_sync_disabled_current", "live_probe_disabled_current"):
        if runtime_policy.get(key) is not True:
            errors.append(f"{POLICY_FILES[0]}: {key} must be true")
    errors.extend(_check_false_map(POLICY_FILES[0], runtime_policy.get("product_boundary", {}), runtime.PRODUCT_BOUNDARY_FALSE_FIELDS, "product_boundary"))
    truth = runtime_policy.get("truth_boundary", {})
    for field in sorted(runtime.TRUTH_BOUNDARY_FALSE_FIELDS):
        if truth.get(field) is not False:
            errors.append(f"{POLICY_FILES[0]}: truth_boundary.{field} must be false")
    if truth.get("human_review_required_for_downstream_use") is not True:
        errors.append(f"{POLICY_FILES[0]}: human_review_required_for_downstream_use must be true")
    for key in (
        "review_required_before_evidence_ledger_bridge",
        "review_required_before_candidate_store_use",
        "review_required_before_public_index_use",
        "review_required_before_pack_export",
    ):
        if review_policy.get(key) is not True:
            errors.append(f"{POLICY_FILES[4]}: {key} must be true")
    for key in (
        "automatic_evidence_acceptance_allowed",
        "automatic_public_index_use_allowed",
        "automatic_master_index_mutation_allowed",
        "automatic_connector_enable_allowed",
    ):
        if review_policy.get(key) is not False:
            errors.append(f"{POLICY_FILES[4]}: {key} must be false")
    for root in ("site/dist/", "runtime/", "contracts/", "control/inventory/sources/", ".aide.local/", ".local/eureka/", ".cache/eureka/"):
        if root not in path_policy.get("forbidden_output_roots", []):
            errors.append(f"{POLICY_FILES[5]}: missing forbidden output root {root}")
    return errors


def _validate_sample_report(report: Mapping[str, Any], ref: str) -> list[str]:
    errors: list[str] = []
    if report.get("schema_version") != runtime.REPORT_SCHEMA_VERSION:
        errors.append(f"{ref}: schema_version must be {runtime.REPORT_SCHEMA_VERSION}")
    if report.get("status") != "pass":
        errors.append(f"{ref}: status must be pass")
    record = report.get("record", {})
    if not isinstance(record, Mapping):
        errors.append(f"{ref}: record must be an object")
    else:
        errors.extend(f"{ref}: {error}" for error in runtime.validate_source_cache_record(record))
    return errors


def _validate_script_checks(repo_root: Path) -> list[str]:
    errors: list[str] = []
    commands = [
        [sys.executable, "scripts/record_source_cache.py", "--input", "examples/sources/cache/records/source_lead_record_v0.json", "--check", "--json"],
        [sys.executable, "scripts/summarize_source_cache.py", "--input", "examples/sources/cache/records", "--check", "--json"],
    ]
    for command in commands:
        completed = subprocess.run(command, cwd=repo_root, capture_output=True, text=True, check=False)
        if completed.returncode != 0:
            errors.append(f"script failed {' '.join(command)}: {completed.stderr.strip()}")
            continue
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            errors.append(f"script did not emit JSON {' '.join(command)}: {exc}")
            continue
        if payload.get("status") != "pass":
            errors.append(f"script report did not pass {' '.join(command)}")
    return errors


def _validate_output_roots(repo_root: Path) -> list[str]:
    errors: list[str] = []
    allowed = [
        repo_root / "control/audits/track-b-15-local-source-cache-runtime-v0/generated/example.json",
    ]
    forbidden = [
        repo_root / "site/dist/source_cache.json",
        repo_root / "runtime/source/cache.json",
        repo_root / "contracts/source/cache.json",
        repo_root / "control/inventory/sources/source_cache.json",
        repo_root / ".aide.local/eureka/source_cache.json",
        repo_root / ".local/eureka/source_cache.json",
        repo_root / ".cache/eureka/source_cache.json",
    ]
    for path in allowed:
        if not record_source_cache.output_path_allowed(path):
            errors.append(f"allowed output root rejected: {path}")
    for path in forbidden:
        if record_source_cache.output_path_allowed(path):
            errors.append(f"forbidden output root accepted: {path}")
    return errors


def _validate_synthetic_boundaries() -> list[str]:
    errors: list[str] = []
    record = runtime.build_source_cache_record({"source_label": "Synthetic"})
    record["truth_boundary"]["source_cache_record_is_public_truth"] = True
    if not runtime.detect_truth_boundary_violations(record):
        errors.append("truth-boundary true claim was not detected")
    record = runtime.build_source_cache_record({"source_label": "Synthetic"})
    record["product_boundary"]["enabled_network_access"] = True
    if not runtime.detect_product_boundary_violations(record):
        errors.append("product-boundary true claim was not detected")
    record = runtime.build_source_cache_record({"source_label": "Synthetic", "source_access_mode": "live_probe"})
    if not runtime.detect_source_access_violations(record):
        errors.append("live source access violation was not detected")
    record = runtime.build_source_cache_record({"source_label": "Synthetic", "notes": ["rights clearance confirmed"]})
    if not runtime.validate_source_cache_record(record):
        errors.append("forbidden rights claim was not detected")
    return errors


def _require_values(path: str, key: str, policy: Mapping[str, Any], expected: set[str]) -> list[str]:
    actual = set(policy.get(key, []))
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    errors: list[str] = []
    if missing:
        errors.append(f"{path}: {key} missing {missing}")
    if extra:
        errors.append(f"{path}: {key} has unexpected {extra}")
    return errors


def _check_false_map(path: str, mapping: Any, fields: set[str], name: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(mapping, Mapping):
        return [f"{path}: {name} must be an object"]
    for field in sorted(fields):
        if mapping.get(field) is not False:
            errors.append(f"{path}: {name}.{field} must be false")
    return errors


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: JSON must be an object")
    return payload


def _report(errors: list[str]) -> dict[str, Any]:
    return {
        "schema_version": "local_source_cache_runtime_validation.v0",
        "status": "pass" if not errors else "fail",
        "error_count": len(errors),
        "errors": sorted(errors),
    }


def main() -> int:
    report = validate_local_source_cache_runtime()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate Track B Candidate Store runtime artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_foundry import candidate_store as runtime  # noqa: E402
from scripts import record_candidate, summarize_candidate_store  # noqa: E402


POLICY_FILES = [
    "control/inventory/candidates/candidate_store_runtime_policy.json",
    "control/inventory/candidates/candidate_status_policy.json",
    "control/inventory/candidates/candidate_type_policy.json",
    "control/inventory/candidates/candidate_origin_policy.json",
    "control/inventory/candidates/candidate_output_policy.json",
    "control/inventory/candidates/candidate_review_policy.json",
    "control/inventory/candidates/candidate_dedup_policy.json",
]
DOC_FILES = [
    "docs/reference/CANDIDATE_STORE_RUNTIME.md",
    "docs/architecture/CANDIDATE_STORE_MODEL.md",
    "docs/operations/CANDIDATE_STORE_REVIEW.md",
]
EXAMPLE_FILES = [
    "examples/candidates/minimal_candidate_v0.json",
    "examples/candidates/search_need_candidate_v0.json",
    "examples/candidates/source_lead_candidate_v0.json",
    "examples/candidates/workunit_result_candidate_v0.json",
    "examples/candidates/evidence_needed_candidate_v0.json",
    "examples/candidates/duplicate_possible_candidate_v0.json",
    "examples/candidates/policy_blocked_candidate_v0.json",
]
AUDIT_FILES = [
    "control/audits/track-b-12-candidate-store-runtime-v0/README.md",
    "control/audits/track-b-12-candidate-store-runtime-v0/track_b_12_report.json",
    "control/audits/track-b-12-candidate-store-runtime-v0/validation.md",
    "control/audits/track-b-12-candidate-store-runtime-v0/generated/sample_candidate_store_report.json",
    "control/audits/track-b-12-candidate-store-runtime-v0/generated/sample_candidate_store_summary.md",
]
SAMPLE_REPORT = "control/audits/track-b-12-candidate-store-runtime-v0/generated/sample_candidate_store_report.json"


def validate_candidate_store_runtime(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
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
        record = runtime.build_candidate_record(payload)
        errors.extend(f"{rel}: {error}" for error in runtime.validate_candidate_record(record))
        if record["candidate_id"] in seen_ids:
            errors.append(f"duplicate candidate_id {record['candidate_id']}: {seen_ids[record['candidate_id']]} and {rel}")
        seen_ids[record["candidate_id"]] = rel

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
    origin_policy = policies[POLICY_FILES[3]]
    output_policy = policies[POLICY_FILES[4]]
    review_policy = policies[POLICY_FILES[5]]
    dedup_policy = policies[POLICY_FILES[6]]

    errors.extend(_require_values(POLICY_FILES[0], "allowed_statuses", runtime_policy, runtime.ALLOWED_STATUSES))
    errors.extend(_require_values(POLICY_FILES[0], "current_allowed_statuses", runtime_policy, runtime.CURRENT_ALLOWED_STATUSES))
    errors.extend(_require_values(POLICY_FILES[0], "allowed_candidate_types", runtime_policy, runtime.ALLOWED_CANDIDATE_TYPES))
    errors.extend(_require_values(POLICY_FILES[0], "allowed_origins", runtime_policy, runtime.ALLOWED_ORIGINS))
    errors.extend(_require_values(POLICY_FILES[0], "allowed_output_types", runtime_policy, runtime.ALLOWED_OUTPUT_TYPES))
    errors.extend(_require_values(POLICY_FILES[0], "forbidden_output_types", runtime_policy, runtime.FORBIDDEN_OUTPUT_TYPES))
    errors.extend(_require_values(POLICY_FILES[1], "allowed_statuses", status_policy, runtime.ALLOWED_STATUSES))
    errors.extend(_require_values(POLICY_FILES[2], "allowed_candidate_types", type_policy, runtime.ALLOWED_CANDIDATE_TYPES))
    errors.extend(_require_values(POLICY_FILES[3], "allowed_origins", origin_policy, runtime.ALLOWED_ORIGINS))
    errors.extend(_require_values(POLICY_FILES[4], "allowed_output_types", output_policy, runtime.ALLOWED_OUTPUT_TYPES))
    errors.extend(_require_values(POLICY_FILES[4], "forbidden_output_types", output_policy, runtime.FORBIDDEN_OUTPUT_TYPES))
    if runtime_policy.get("review_required_before_downstream_use") is not True:
        errors.append(f"{POLICY_FILES[0]}: review_required_before_downstream_use must be true")
    errors.extend(_check_false_map(POLICY_FILES[0], runtime_policy.get("product_boundary", {}), runtime.PRODUCT_BOUNDARY_FALSE_FIELDS, "product_boundary"))
    truth = runtime_policy.get("truth_boundary", {})
    for field in sorted(runtime.TRUTH_BOUNDARY_FALSE_FIELDS):
        if truth.get(field) is not False:
            errors.append(f"{POLICY_FILES[0]}: truth_boundary.{field} must be false")
    if truth.get("human_review_required_for_downstream_use") is not True:
        errors.append(f"{POLICY_FILES[0]}: human_review_required_for_downstream_use must be true")
    for key in ("review_required_before_public_use", "review_required_before_evidence_acceptance", "review_required_before_master_index"):
        if review_policy.get(key) is not True:
            errors.append(f"{POLICY_FILES[5]}: {key} must be true")
    for key in ("automatic_public_use_allowed", "automatic_master_index_mutation_allowed"):
        if review_policy.get(key) is not False:
            errors.append(f"{POLICY_FILES[5]}: {key} must be false")
    if dedup_policy.get("merge_allowed") is not False:
        errors.append(f"{POLICY_FILES[6]}: merge_allowed must be false")
    if dedup_policy.get("automatic_merge_allowed") is not False:
        errors.append(f"{POLICY_FILES[6]}: automatic_merge_allowed must be false")
    if dedup_policy.get("conflict_preservation_required") is not True:
        errors.append(f"{POLICY_FILES[6]}: conflict_preservation_required must be true")
    return errors


def _validate_sample_report(report: Mapping[str, Any], ref: str) -> list[str]:
    errors: list[str] = []
    if report.get("schema_version") != runtime.REPORT_SCHEMA_VERSION:
        errors.append(f"{ref}: schema_version must be {runtime.REPORT_SCHEMA_VERSION}")
    if report.get("status") != "pass":
        errors.append(f"{ref}: status must be pass")
    snapshot = report.get("snapshot", {})
    if snapshot.get("schema_version") != runtime.SNAPSHOT_SCHEMA_VERSION:
        errors.append(f"{ref}: snapshot schema_version must be {runtime.SNAPSHOT_SCHEMA_VERSION}")
    for record in snapshot.get("candidates", []):
        errors.extend(f"{ref}: {error}" for error in runtime.validate_candidate_record(record))
    dedup = snapshot.get("deduplication_summary", {})
    if dedup.get("automatic_merge_allowed") is not False:
        errors.append(f"{ref}: automatic merge must be false")
    if dedup.get("merged_candidate_ids"):
        errors.append(f"{ref}: merged_candidate_ids must be empty")
    return errors


def _validate_script_checks(repo_root: Path) -> list[str]:
    errors: list[str] = []
    commands = [
        [sys.executable, "scripts/record_candidate.py", "--input", "examples/search_needs/software_version_search_need_v0.json", "--check", "--json"],
        [sys.executable, "scripts/summarize_candidate_store.py", "--input", "examples/candidates", "--check", "--json"],
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
        repo_root / "control/audits/track-b-12-candidate-store-runtime-v0/generated/example.json",
    ]
    forbidden = [
        repo_root / "site/dist/candidate.json",
        repo_root / "runtime/candidate.json",
        repo_root / "contracts/candidate.json",
        repo_root / ".aide.local/eureka/candidate.json",
        repo_root / ".local/eureka/candidate.json",
        repo_root / ".cache/eureka/candidate.json",
    ]
    for path in allowed:
        if not record_candidate.output_path_allowed(path):
            errors.append(f"allowed output root rejected: {path}")
    for path in forbidden:
        if record_candidate.output_path_allowed(path):
            errors.append(f"forbidden output root accepted: {path}")
    return errors


def _validate_synthetic_boundaries() -> list[str]:
    errors: list[str] = []
    record = runtime.build_candidate_record({"candidate_label": "Synthetic"})
    record["truth_boundary"]["candidate_is_public_truth"] = True
    if not runtime.detect_candidate_truth_boundary_violations(record):
        errors.append("truth-boundary true claim was not detected")
    record = runtime.build_candidate_record({"candidate_label": "Synthetic"})
    record["product_boundary"]["enabled_telemetry"] = True
    if not runtime.detect_candidate_product_boundary_violations(record):
        errors.append("product-boundary true claim was not detected")
    record = runtime.build_candidate_record({"candidate_label": "Synthetic", "notes": ["rights clearance confirmed"]})
    if not runtime.validate_candidate_record(record):
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
        raise ValueError(f"{path} must be a JSON object")
    return payload


def _report(errors: list[str]) -> dict[str, Any]:
    return {
        "schema_version": "candidate_store_runtime_validation.v0",
        "status": "valid" if not errors else "invalid",
        "errors": sorted(dict.fromkeys(errors)),
        "validated_examples": len(EXAMPLE_FILES),
    }


def main() -> int:
    report = validate_candidate_store_runtime(REPO_ROOT)
    if report["status"] != "valid":
        print("Candidate Store runtime validation: FAIL")
        for error in report["errors"]:
            print(f"- {error}")
        return 1
    print("Candidate Store runtime validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


#!/usr/bin/env python3
"""Validate Track B Source Cache to Evidence Ledger bridge artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_foundry import evidence_ledger, source_cache, source_cache_to_evidence as bridge  # noqa: E402
from scripts import bridge_source_cache_to_evidence  # noqa: E402


POLICY_FILES = [
    "control/inventory/evidence_ledger/source_cache_to_evidence_bridge_runtime_policy.json",
    "control/inventory/evidence_ledger/source_cache_to_evidence_mapping_policy.json",
    "control/inventory/evidence_ledger/source_cache_to_evidence_output_policy.json",
    "control/inventory/evidence_ledger/source_cache_to_evidence_review_policy.json",
    "control/inventory/evidence_ledger/source_cache_to_evidence_path_policy.json",
]
DOC_FILES = [
    "docs/reference/SOURCE_CACHE_TO_EVIDENCE_BRIDGE_RUNTIME.md",
    "docs/architecture/SOURCE_CACHE_TO_EVIDENCE_BRIDGE_MODEL.md",
    "docs/operations/SOURCE_CACHE_TO_EVIDENCE_BRIDGE_REVIEW.md",
]
EXAMPLE_FILES = [
    "examples/source_cache_to_evidence/minimal_bridge_case_v0.json",
    "examples/source_cache_to_evidence/source_metadata_to_metadata_claim_v0.json",
    "examples/source_cache_to_evidence/source_locator_to_source_observation_v0.json",
    "examples/source_cache_to_evidence/source_policy_to_policy_claim_v0.json",
    "examples/source_cache_to_evidence/source_coverage_to_coverage_claim_v0.json",
    "examples/source_cache_to_evidence/policy_blocked_bridge_case_v0.json",
]
AUDIT_FILES = [
    "control/audits/track-b-17-source-cache-to-evidence-bridge-v0/README.md",
    "control/audits/track-b-17-source-cache-to-evidence-bridge-v0/track_b_17_report.json",
    "control/audits/track-b-17-source-cache-to-evidence-bridge-v0/validation.md",
    "control/audits/track-b-17-source-cache-to-evidence-bridge-v0/generated/sample_bridge_result.json",
    "control/audits/track-b-17-source-cache-to-evidence-bridge-v0/generated/sample_evidence_from_source_cache.json",
    "control/audits/track-b-17-source-cache-to-evidence-bridge-v0/generated/sample_bridge_summary.md",
]
SAMPLE_BRIDGE_RESULT = "control/audits/track-b-17-source-cache-to-evidence-bridge-v0/generated/sample_bridge_result.json"
SAMPLE_EVIDENCE = "control/audits/track-b-17-source-cache-to-evidence-bridge-v0/generated/sample_evidence_from_source_cache.json"


def validate_source_cache_to_evidence_bridge(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    for rel in sorted(POLICY_FILES + DOC_FILES + EXAMPLE_FILES + AUDIT_FILES):
        if not (repo_root / rel).exists():
            errors.append(f"missing required file: {rel}")
    if errors:
        return _report(errors)

    policies = {rel: _read_json(repo_root / rel) for rel in POLICY_FILES}
    errors.extend(_validate_policy_files(policies))

    seen_result_ids: dict[str, str] = {}
    for rel in sorted(EXAMPLE_FILES):
        record = bridge.load_source_cache_record(repo_root / rel)
        candidates = bridge.map_source_cache_record_to_evidence_candidates(record)
        result = bridge.build_bridge_result(record, candidates)
        errors.extend(f"{rel}: {error}" for error in bridge.validate_bridge_result(result))
        if result["bridge_result_id"] in seen_result_ids:
            errors.append(f"duplicate bridge_result_id {result['bridge_result_id']}: {seen_result_ids[result['bridge_result_id']]} and {rel}")
        seen_result_ids[result["bridge_result_id"]] = rel

    sample_result = _read_json(repo_root / SAMPLE_BRIDGE_RESULT)
    sample_evidence = _read_json(repo_root / SAMPLE_EVIDENCE)
    errors.extend(_validate_sample_bridge_result(sample_result, SAMPLE_BRIDGE_RESULT))
    errors.extend(f"{SAMPLE_EVIDENCE}: {error}" for error in bridge.validate_bridge_evidence_candidate(sample_evidence))
    errors.extend(_validate_script_checks(repo_root))
    errors.extend(_validate_output_roots(repo_root))
    errors.extend(_validate_synthetic_boundaries())
    return _report(errors)


def _validate_policy_files(policies: Mapping[str, Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    runtime_policy = policies[POLICY_FILES[0]]
    mapping_policy = policies[POLICY_FILES[1]]
    output_policy = policies[POLICY_FILES[2]]
    review_policy = policies[POLICY_FILES[3]]
    path_policy = policies[POLICY_FILES[4]]

    errors.extend(_require_values(POLICY_FILES[0], "allowed_source_cache_record_statuses", runtime_policy, source_cache.ALLOWED_STATUSES))
    errors.extend(_require_values(POLICY_FILES[0], "current_allowed_source_cache_record_statuses", runtime_policy, source_cache.CURRENT_ALLOWED_STATUSES))
    errors.extend(_require_values(POLICY_FILES[0], "allowed_source_cache_record_types", runtime_policy, source_cache.ALLOWED_RECORD_TYPES))
    errors.extend(_require_values(POLICY_FILES[0], "current_allowed_source_cache_record_types", runtime_policy, source_cache.CURRENT_ALLOWED_RECORD_TYPES))
    errors.extend(_require_values(POLICY_FILES[0], "allowed_output_evidence_types", runtime_policy, evidence_ledger.CURRENT_ALLOWED_RECORD_TYPES))
    errors.extend(_require_values(POLICY_FILES[0], "allowed_bridge_statuses", runtime_policy, bridge.ALLOWED_BRIDGE_STATUSES))
    errors.extend(_require_values(POLICY_FILES[0], "current_allowed_bridge_statuses", runtime_policy, bridge.CURRENT_ALLOWED_BRIDGE_STATUSES))
    errors.extend(_require_values(POLICY_FILES[0], "allowed_mapping_statuses", runtime_policy, bridge.ALLOWED_MAPPING_STATUSES))
    errors.extend(_require_values(POLICY_FILES[0], "allowed_output_types", runtime_policy, bridge.ALLOWED_OUTPUT_TYPES))
    errors.extend(_require_values(POLICY_FILES[0], "forbidden_output_types", runtime_policy, bridge.FORBIDDEN_OUTPUT_TYPES))
    errors.extend(_require_values(POLICY_FILES[0], "forbidden_conversions", runtime_policy, bridge.FORBIDDEN_CONVERSIONS))
    if runtime_policy.get("bridge_runtime_scope") != "fixture_only":
        errors.append(f"{POLICY_FILES[0]}: bridge_runtime_scope must be fixture_only")
    for key in ("live_source_access_enabled", "source_sync_enabled", "evidence_acceptance_enabled", "public_index_use_enabled", "master_index_mutation_enabled"):
        if runtime_policy.get(key) is not False:
            errors.append(f"{POLICY_FILES[0]}: {key} must be false")
    truth = runtime_policy.get("truth_boundary", {})
    for field in sorted(bridge.TRUTH_BOUNDARY_FALSE_FIELDS):
        if truth.get(field) is not False:
            errors.append(f"{POLICY_FILES[0]}: truth_boundary.{field} must be false")
    if truth.get("human_review_required_for_downstream_use") is not True:
        errors.append(f"{POLICY_FILES[0]}: human_review_required_for_downstream_use must be true")
    errors.extend(_check_false_map(POLICY_FILES[0], runtime_policy.get("product_boundary", {}), bridge.PRODUCT_BOUNDARY_FALSE_FIELDS, "product_boundary"))

    for source_type, rule in sorted(bridge.MAPPING_RULES.items()):
        allowed = mapping_policy.get("allowed_mappings", {})
        if source_type not in allowed:
            errors.append(f"{POLICY_FILES[1]}: missing mapping for {source_type}")
            continue
        if allowed[source_type].get("evidence_record_type") != rule["evidence_record_type"]:
            errors.append(f"{POLICY_FILES[1]}: mapping {source_type}.evidence_record_type mismatch")
        if allowed[source_type].get("claim_type") != rule["claim_type"]:
            errors.append(f"{POLICY_FILES[1]}: mapping {source_type}.claim_type mismatch")
    errors.extend(_require_values(POLICY_FILES[1], "forbidden_mappings", mapping_policy, bridge.FORBIDDEN_CONVERSIONS))
    if mapping_policy.get("review_required_for_all_outputs") is not True:
        errors.append(f"{POLICY_FILES[1]}: review_required_for_all_outputs must be true")

    errors.extend(_require_values(POLICY_FILES[2], "allowed_output_types", output_policy, bridge.ALLOWED_OUTPUT_TYPES))
    errors.extend(_require_values(POLICY_FILES[2], "forbidden_output_types", output_policy, bridge.FORBIDDEN_OUTPUT_TYPES))
    for key in (
        "review_required_before_candidate_store_use",
        "review_required_before_public_index_use",
        "review_required_before_pack_export",
        "review_required_before_master_index",
        "review_required_before_rights_claim",
        "review_required_before_malware_safety_claim",
        "review_required_before_installability_claim",
    ):
        if review_policy.get(key) is not True:
            errors.append(f"{POLICY_FILES[3]}: {key} must be true")
    for key in (
        "automatic_evidence_acceptance_allowed",
        "automatic_public_index_use_allowed",
        "automatic_master_index_mutation_allowed",
        "automatic_rights_clearance_allowed",
        "automatic_malware_safety_allowed",
        "automatic_installability_verification_allowed",
    ):
        if review_policy.get(key) is not False:
            errors.append(f"{POLICY_FILES[3]}: {key} must be false")
    for root in ("site/dist/", "runtime/", "contracts/", "control/inventory/sources/", ".aide.local/", ".local/eureka/", ".cache/eureka/"):
        if root not in path_policy.get("forbidden_output_roots", []):
            errors.append(f"{POLICY_FILES[4]}: missing forbidden output root {root}")
    return errors


def _validate_sample_bridge_result(result: Mapping[str, Any], ref: str) -> list[str]:
    errors: list[str] = []
    if result.get("schema_version") != bridge.SCHEMA_VERSION:
        errors.append(f"{ref}: schema_version must be {bridge.SCHEMA_VERSION}")
    errors.extend(f"{ref}: {error}" for error in bridge.validate_bridge_result(result))
    return errors


def _validate_script_checks(repo_root: Path) -> list[str]:
    errors: list[str] = []
    command = [
        sys.executable,
        "scripts/bridge_source_cache_to_evidence.py",
        "--input",
        "examples/source_cache_records/source_metadata_record_v0.json",
        "--check",
        "--json",
    ]
    completed = subprocess.run(command, cwd=repo_root, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        errors.append(f"script failed {' '.join(command)}: {completed.stderr.strip()}")
        return errors
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        errors.append(f"script did not emit JSON {' '.join(command)}: {exc}")
        return errors
    if payload.get("status") != "pass":
        errors.append(f"script report did not pass {' '.join(command)}")
    return errors


def _validate_output_roots(repo_root: Path) -> list[str]:
    errors: list[str] = []
    allowed = [
        repo_root / "control/audits/track-b-17-source-cache-to-evidence-bridge-v0/generated/example.json",
    ]
    forbidden = [
        repo_root / "site/dist/bridge.json",
        repo_root / "runtime/bridge.json",
        repo_root / "contracts/bridge.json",
        repo_root / "control/inventory/sources/bridge.json",
        repo_root / ".aide.local/eureka/bridge.json",
        repo_root / ".local/eureka/bridge.json",
        repo_root / ".cache/eureka/bridge.json",
    ]
    for path in allowed:
        if not bridge_source_cache_to_evidence.output_path_allowed(path):
            errors.append(f"allowed output root rejected: {path}")
    for path in forbidden:
        if bridge_source_cache_to_evidence.output_path_allowed(path):
            errors.append(f"forbidden output root accepted: {path}")
    return errors


def _validate_synthetic_boundaries() -> list[str]:
    errors: list[str] = []
    record = bridge.load_source_cache_record(REPO_ROOT / "examples/source_cache_records/source_metadata_record_v0.json")
    candidates = bridge.map_source_cache_record_to_evidence_candidates(record)
    result = bridge.build_bridge_result(record, candidates)
    result["truth_boundary"]["bridge_output_is_accepted_evidence"] = True
    if not bridge.detect_bridge_truth_boundary_violations(result):
        errors.append("truth-boundary true claim did not fail")
    result = bridge.build_bridge_result(record, candidates)
    result["product_boundary"]["enabled_network_access"] = True
    if not bridge.detect_bridge_product_boundary_violations(result):
        errors.append("product-boundary true claim did not fail")
    candidate = dict(candidates[0])
    candidate["truth_boundary"] = dict(candidate["truth_boundary"])
    candidate["truth_boundary"]["evidence_record_is_accepted_evidence"] = True
    if not bridge.validate_bridge_evidence_candidate(candidate):
        errors.append("accepted evidence candidate claim did not fail")
    candidate = dict(candidates[0])
    candidate["truth_boundary"] = dict(candidate["truth_boundary"])
    candidate["truth_boundary"]["evidence_record_can_mutate_master_index"] = True
    if not bridge.validate_bridge_evidence_candidate(candidate):
        errors.append("master-index mutation claim did not fail")
    return errors


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: JSON must be an object")
    return payload


def _require_values(ref: str, field: str, payload: Mapping[str, Any], expected: set[str]) -> list[str]:
    actual = set(payload.get(field, []))
    missing = sorted(expected - actual)
    return [f"{ref}: {field} missing {item}" for item in missing]


def _check_false_map(ref: str, payload: Mapping[str, Any], fields: set[str], prefix: str) -> list[str]:
    errors: list[str] = []
    for field in sorted(fields):
        if payload.get(field) is not False:
            errors.append(f"{ref}: {prefix}.{field} must be false")
    return errors


def _report(errors: list[str]) -> dict[str, Any]:
    return {
        "schema_version": "source_cache_to_evidence_bridge_validation.v0",
        "status": "pass" if not errors else "fail",
        "errors": sorted(dict.fromkeys(errors)),
    }


def main() -> int:
    report = validate_source_cache_to_evidence_bridge(REPO_ROOT)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

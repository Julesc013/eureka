#!/usr/bin/env python3
"""Validate Track B node policy evaluator artifacts."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_foundry import node_policy_evaluator
from scripts import evaluate_node_policy


POLICY_FILES = [
    "control/inventory/nodes/node_policy_evaluator_policy.json",
    "control/inventory/nodes/node_policy_evaluation_decision_registry.json",
    "control/inventory/nodes/node_policy_evaluation_reason_registry.json",
    "control/inventory/nodes/node_policy_evaluation_output_policy.json",
    "control/inventory/nodes/node_policy_evaluation_review_policy.json",
]

REQUIRED_DOCS = [
    "docs/reference/NODE_POLICY_EVALUATOR.md",
    "docs/architecture/NODE_POLICY_EVALUATOR_MODEL.md",
    "docs/operations/NODE_POLICY_EVALUATION_REVIEW.md",
]

EXAMPLE_RESULTS = [
    "examples/node_policy_evaluations/local_private_allowed_v0/evaluation_result.json",
    "examples/node_policy_evaluations/source_lead_allowed_v0/evaluation_result.json",
    "examples/node_policy_evaluations/policy_blocked_v0/evaluation_result.json",
    "examples/node_policy_evaluations/network_required_blocked_v0/evaluation_result.json",
    "examples/node_policy_evaluations/future_metadata_probe_gated_v0/evaluation_result.json",
    "examples/node_policy_evaluations/noop_repeat_allowed_v0/evaluation_result.json",
]

SAMPLE_RESULTS = [
    "control/audits/track-b-11-node-policy-evaluator-v0/generated/sample_node_policy_evaluation_result.json"
]

REQUIRED_AUDIT_FILES = [
    "control/audits/track-b-11-node-policy-evaluator-v0/README.md",
    "control/audits/track-b-11-node-policy-evaluator-v0/track_b_11_report.json",
    "control/audits/track-b-11-node-policy-evaluator-v0/validation.md",
    "control/audits/track-b-11-node-policy-evaluator-v0/generated/sample_node_policy_evaluation_result.json",
    "control/audits/track-b-11-node-policy-evaluator-v0/generated/sample_node_policy_evaluation_summary.md",
]

SAFE_EXAMPLE_ARGS = [
    "--node-manifest",
    "examples/nodes/local_private_node_v0/eureka_node_manifest.json",
    "--node-policy",
    "examples/nodes/policies/local_private_node_policy_v0.json",
    "--workunit",
    "examples/work_units/search_need_review_v0/work_unit.json",
    "--check",
    "--json",
]


def _path(rel: str) -> Path:
    return REPO_ROOT / rel


def _load_json(rel: str) -> dict:
    with _path(rel).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{rel} is not a JSON object")
    return data


def _check_required_files(errors: list[str]) -> None:
    for rel in sorted(POLICY_FILES + REQUIRED_DOCS + EXAMPLE_RESULTS + REQUIRED_AUDIT_FILES):
        if not _path(rel).exists():
            errors.append(f"missing required file: {rel}")


def _check_policy_vocabularies(errors: list[str]) -> None:
    evaluator_policy = _load_json(POLICY_FILES[0])
    decision_registry = _load_json(POLICY_FILES[1])
    reason_registry = _load_json(POLICY_FILES[2])
    output_policy = _load_json(POLICY_FILES[3])
    review_policy = _load_json(POLICY_FILES[4])

    if sorted(evaluator_policy.get("allowed_decisions", [])) != sorted(node_policy_evaluator.DECISIONS):
        errors.append("evaluator policy decisions differ from runtime decisions")
    if sorted(decision_registry.get("allowed_decisions", [])) != sorted(node_policy_evaluator.DECISIONS):
        errors.append("decision registry differs from runtime decisions")
    if sorted(evaluator_policy.get("allowed_reason_categories", [])) != sorted(node_policy_evaluator.REASON_CATEGORIES):
        errors.append("evaluator policy reasons differ from runtime reasons")
    if sorted(reason_registry.get("allowed_reason_categories", [])) != sorted(node_policy_evaluator.REASON_CATEGORIES):
        errors.append("reason registry differs from runtime reasons")
    if sorted(output_policy.get("allowed_output_types", [])) != sorted(node_policy_evaluator.ALLOWED_OUTPUT_TYPES):
        errors.append("output policy allowed types differ from runtime output types")
    if sorted(output_policy.get("forbidden_output_types", [])) != sorted(node_policy_evaluator.FORBIDDEN_OUTPUT_TYPES):
        errors.append("output policy forbidden types differ from runtime forbidden output types")
    required_false = set(node_policy_evaluator.FALSE_PRODUCT_BOUNDARY_FIELDS)
    if not required_false.issubset(set(evaluator_policy.get("required_false_product_booleans", []))):
        errors.append("evaluator policy is missing product-boundary false booleans")
    required_truth = set(node_policy_evaluator.FALSE_TRUTH_BOUNDARY_FIELDS)
    if not required_truth.issubset(set(evaluator_policy.get("required_false_truth_booleans", []))):
        errors.append("evaluator policy is missing truth-boundary false booleans")
    for field in (
        "automatic_public_use_allowed",
        "automatic_master_index_mutation_allowed",
        "automatic_network_enable_allowed",
        "automatic_model_enable_allowed",
        "automatic_local_state_enable_allowed",
    ):
        if review_policy.get(field) is not False:
            errors.append(f"review policy {field} must be false")


def _check_result_file(rel: str, errors: list[str]) -> None:
    try:
        result = _load_json(rel)
    except Exception as exc:
        errors.append(f"{rel}: {exc}")
        return
    for error in node_policy_evaluator.validate_node_policy_evaluation_result(result):
        errors.append(f"{rel}: {error}")


def _check_result_files(errors: list[str]) -> None:
    ids: dict[str, str] = {}
    for rel in sorted(EXAMPLE_RESULTS):
        _check_result_file(rel, errors)
        if _path(rel).exists():
            result_id = str(_load_json(rel).get("evaluation_result_id", ""))
            if result_id in ids:
                errors.append(f"duplicate evaluation_result_id {result_id}: {ids[result_id]} and {rel}")
            ids[result_id] = rel
    for rel in sorted(SAMPLE_RESULTS):
        _check_result_file(rel, errors)


def _check_cli(errors: list[str]) -> None:
    command = [sys.executable, "scripts/evaluate_node_policy.py", *SAFE_EXAMPLE_ARGS]
    completed = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        errors.append(f"safe evaluator command failed: {completed.stderr.strip()}")
        return
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        errors.append(f"safe evaluator command did not emit JSON: {exc}")
        return
    if result.get("decision") != "allowed_for_dry_run":
        errors.append("safe evaluator command did not allow dry-run")
    if result.get("allowed_for_execution") is not False:
        errors.append("safe evaluator command claimed execution allowance")


def _check_output_roots(errors: list[str]) -> None:
    allowed = [
        Path("control/audits/track-b-11-node-policy-evaluator-v0/generated/example.json"),
        Path("examples/node_policy_evaluations/local_private_allowed_v0/evaluation_result.json"),
    ]
    forbidden = [
        Path("site/dist/node_policy_eval.json"),
        Path("runtime/node_policy_eval.json"),
        Path("contracts/node_policy_eval.json"),
        Path(".aide.local/eureka/node_policy_eval.json"),
        Path(".local/eureka/node_policy_eval.json"),
        Path(".cache/eureka/node_policy_eval.json"),
    ]
    for rel in allowed:
        if not evaluate_node_policy.output_path_allowed(REPO_ROOT / rel):
            errors.append(f"allowed output root rejected: {rel.as_posix()}")
    for rel in forbidden:
        if evaluate_node_policy.output_path_allowed(REPO_ROOT / rel):
            errors.append(f"forbidden output root accepted: {rel.as_posix()}")


def validate() -> list[str]:
    errors: list[str] = []
    try:
        _check_required_files(errors)
        _check_policy_vocabularies(errors)
        _check_result_files(errors)
        _check_cli(errors)
        _check_output_roots(errors)
    except Exception as exc:
        errors.append(str(exc))
    return sorted(dict.fromkeys(errors))


def main() -> int:
    errors = validate()
    if errors:
        print("FAIL validate_node_policy_evaluator")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS validate_node_policy_evaluator")
    print(f"- policies: {len(POLICY_FILES)}")
    print(f"- examples: {len(EXAMPLE_RESULTS)}")
    print(f"- samples: {len(SAMPLE_RESULTS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate Track B WorkUnit dry-run runner artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Iterable, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.foundry import workunit_dry_run as runtime  # noqa: E402
from scripts.validate_eureka_workunit_result import validate_workunit_result_record  # noqa: E402


DRY_RUN_POLICY_PATH = "control/inventory/nodes/workunit_dry_run_policy.json"
ACTION_MATRIX_PATH = "control/inventory/nodes/workunit_dry_run_action_matrix.json"
OUTPUT_POLICY_PATH = "control/inventory/nodes/workunit_dry_run_output_policy.json"
REVIEW_POLICY_PATH = "control/inventory/nodes/workunit_dry_run_review_policy.json"
AUDIT_REPORT_PATH = "control/audits/track-b-10-workunit-dry-run-runner-v0/track_b_10_report.json"
SAMPLE_REPORT_PATH = "control/audits/track-b-10-workunit-dry-run-runner-v0/generated/sample_workunit_dry_run_result.json"
SAMPLE_SUMMARY_PATH = "control/audits/track-b-10-workunit-dry-run-runner-v0/generated/sample_workunit_dry_run_summary.md"
EXAMPLE_ROOT = "examples/work_units/dry_runs"
DOC_PATHS = (
    "docs/reference/WORKUNIT_DRY_RUN_RUNNER.md",
    "docs/architecture/WORKUNIT_DRY_RUN_MODEL.md",
    "docs/operations/WORKUNIT_DRY_RUN_REVIEW.md",
)
REQUIRED_EXAMPLES = {
    "search_need_review_dry_run_v0/work_unit_result.json",
    "source_lead_inspection_dry_run_v0/work_unit_result.json",
    "policy_blocked_dry_run_v0/work_unit_result.json",
    "noop_dry_run_v0/work_unit_result.json",
}
AUDIT_PRODUCT_FALSE_FIELDS = {
    "implemented_workunit_execution",
    "implemented_node_runtime",
    "created_local_private_state",
    "enabled_network_access",
    "enabled_live_probes",
    "enabled_source_sync",
    "enabled_source_connectors",
    "enabled_downloads",
    "enabled_installers",
    "enabled_execution",
    "enabled_uploads",
    "enabled_accounts",
    "enabled_telemetry",
    "enabled_pack_import_runtime",
    "enabled_review_runtime",
    "enabled_model_provider_calls",
    "mutated_master_index",
    "claimed_rights_clearance",
    "claimed_malware_safety",
    "claimed_verified_installability",
    "claimed_exhaustive_global_search",
    "claimed_production_readiness",
}
FORBIDDEN_STRING_CLAIMS = {
    "workunit executed",
    "executed workunit actions",
    "network call completed",
    "api call completed",
    "model provider call completed",
    "live probe enabled",
    "source sync enabled",
    "download enabled",
    "upload enabled",
    "account enabled",
    "telemetry enabled",
    "master-index mutation allowed",
    "rights clearance confirmed",
    "malware safe",
    "verified installability",
    "exhaustive global search proof",
    "production readiness",
}


def validate_workunit_dry_run_runner(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    required_files = [
        DRY_RUN_POLICY_PATH,
        ACTION_MATRIX_PATH,
        OUTPUT_POLICY_PATH,
        REVIEW_POLICY_PATH,
        AUDIT_REPORT_PATH,
        SAMPLE_REPORT_PATH,
        SAMPLE_SUMMARY_PATH,
        "runtime/local/foundry/workunit_dry_run.py",
        "scripts/run_workunit_dry_run.py",
        *DOC_PATHS,
    ]
    for path in required_files:
        if not (repo_root / path).is_file():
            errors.append(f"missing required file: {path}")
    if errors:
        return _report(errors)

    dry_run_policy = _read_json(repo_root / DRY_RUN_POLICY_PATH)
    action_matrix = _read_json(repo_root / ACTION_MATRIX_PATH)
    output_policy = _read_json(repo_root / OUTPUT_POLICY_PATH)
    review_policy = _read_json(repo_root / REVIEW_POLICY_PATH)
    audit_report = _read_json(repo_root / AUDIT_REPORT_PATH)
    sample_report = _read_json(repo_root / SAMPLE_REPORT_PATH)

    errors.extend(validate_dry_run_policy(dry_run_policy, DRY_RUN_POLICY_PATH))
    errors.extend(validate_action_matrix(action_matrix, ACTION_MATRIX_PATH))
    errors.extend(validate_output_policy(output_policy, OUTPUT_POLICY_PATH))
    errors.extend(validate_review_policy(review_policy, REVIEW_POLICY_PATH))
    errors.extend(validate_audit_report(audit_report, AUDIT_REPORT_PATH))
    errors.extend(validate_docs(repo_root))
    errors.extend(validate_sample_report(sample_report, SAMPLE_REPORT_PATH, repo_root))
    errors.extend(validate_script_check(repo_root))
    errors.extend(validate_forbidden_output_root_rejected(repo_root))

    found = {
        path.relative_to(repo_root / EXAMPLE_ROOT).as_posix()
        for path in sorted((repo_root / EXAMPLE_ROOT).glob("*/work_unit_result.json"))
    }
    missing_examples = sorted(REQUIRED_EXAMPLES - found)
    if missing_examples:
        errors.append(f"{EXAMPLE_ROOT}: missing examples {missing_examples}")
    for path in sorted((repo_root / EXAMPLE_ROOT).glob("*/work_unit_result.json")):
        payload = _read_json(path)
        ref = path.relative_to(repo_root).as_posix()
        errors.extend(validate_dry_run_result_payload(payload, ref, repo_root))
        errors.extend(_scan_for_forbidden_claims(payload, ref))

    blocked = runtime.build_workunit_dry_run_result(
        {
            "schema_version": "work_unit.v0",
            "workunit_id": "synthetic_network_blocked",
            "workunit_label": "Synthetic network blocked",
            "workunit_type": "search_need_review",
            "workunit_status": "planned",
            "workunit_scope": "repo_local",
            "required_node_modes": ["local_private"],
            "required_node_capabilities": [{"capability_id": "repo_local_inspection", "required": True}],
            "related_node_manifest_refs": ["examples/nodes/local_private_node_v0/eureka_node_manifest.json"],
            "required_node_policy_refs": ["examples/nodes/policies/local_private_node_policy_v0.json"],
            "network_requirements": {"network_required": True, "current_enabled": False},
            "source_access_requirements": {"source_access_required": False, "current_enabled": False},
            "model_provider_requirements": {"model_provider_required": False, "current_enabled": False},
            "credential_requirements": {"credentials_required": False, "current_enabled": False},
            "local_state_requirements": {"local_state_required": False, "current_enabled": False},
            "allowed_actions": ["inspect_repo_local_artifact"],
            "forbidden_actions": ["mutate_master_index"],
            "expected_outputs": [{"output_id": "dry_run_report", "output_type": "dry_run_report", "output_requires_review": True}],
            "review_gates": {field: True for field in runtime.REQUIRED_REVIEW_GATES},
        },
        source_workunit_ref="examples/work_units/search_need_review_v0/work_unit.json",
    )
    if blocked.get("workunit_result_status") != "blocked":
        errors.append("synthetic network-required WorkUnit was not blocked")

    return _report(errors)


def validate_dry_run_policy(policy: Mapping[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    if policy.get("schema_version") != "workunit_dry_run_policy.v0":
        errors.append(f"{path}: unexpected schema_version")
    errors.extend(_require_values(path, "allowed_workunit_statuses_for_dry_run", policy, runtime.ALLOWED_WORKUNIT_STATUSES))
    errors.extend(_require_values(path, "allowed_workunit_types_for_dry_run", policy, runtime.ALLOWED_WORKUNIT_TYPES))
    errors.extend(_require_values(path, "allowed_node_modes_for_dry_run", policy, runtime.ALLOWED_NODE_MODES))
    errors.extend(_require_values(path, "current_dry_run_node_modes", policy, runtime.CURRENT_DRY_RUN_NODE_MODES))
    if policy.get("dry_run_only") is not True:
        errors.append(f"{path}: dry_run_only must be true")
    if policy.get("executes_workunit_actions") is not False:
        errors.append(f"{path}: executes_workunit_actions must be false")
    errors.extend(_check_false_map(path, policy.get("product_boundary", {}), runtime.PRODUCT_BOUNDARY_FALSE_FIELDS, "product_boundary"))
    return errors


def validate_action_matrix(policy: Mapping[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    if policy.get("schema_version") != "workunit_dry_run_action_matrix.v0":
        errors.append(f"{path}: unexpected schema_version")
    errors.extend(_require_values(path, "action_classifications", policy, runtime.DRY_RUN_CLASSIFICATIONS))
    errors.extend(_require_values(path, "forbidden_actions", policy, runtime.FORBIDDEN_ACTIONS))
    for action in runtime.FORBIDDEN_ACTIONS:
        behavior = policy.get("action_rules", {}).get(action)
        if behavior != "forbidden_checked":
            errors.append(f"{path}: forbidden action {action} must map to forbidden_checked")
    errors.extend(_check_false_map(path, policy.get("product_boundary", {}), runtime.PRODUCT_BOUNDARY_FALSE_FIELDS, "product_boundary"))
    return errors


def validate_output_policy(policy: Mapping[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    if policy.get("schema_version") != "workunit_dry_run_output_policy.v0":
        errors.append(f"{path}: unexpected schema_version")
    errors.extend(_require_values(path, "allowed_output_types", policy, runtime.ALLOWED_OUTPUT_TYPES))
    errors.extend(_require_values(path, "forbidden_output_types", policy, runtime.FORBIDDEN_OUTPUT_TYPES))
    rules = policy.get("output_rules", {})
    for key in ("writes_no_files_by_default", "review_required_before_downstream_use"):
        if rules.get(key) is not True:
            errors.append(f"{path}: output_rules.{key} must be true")
    for key in ("automatic_public_use_allowed", "automatic_master_index_mutation_allowed", "automatic_evidence_acceptance_allowed"):
        if rules.get(key) is not False:
            errors.append(f"{path}: output_rules.{key} must be false")
    errors.extend(_check_false_map(path, policy.get("product_boundary", {}), runtime.PRODUCT_BOUNDARY_FALSE_FIELDS, "product_boundary"))
    return errors


def validate_review_policy(policy: Mapping[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    if policy.get("schema_version") != "workunit_dry_run_review_policy.v0":
        errors.append(f"{path}: unexpected schema_version")
    errors.extend(_require_values(path, "required_review_gates", policy, runtime.REQUIRED_REVIEW_GATES))
    for key in (
        "human_review_required_before_downstream_use",
        "source_policy_review_required_for_source_work",
        "master_index_review_required_before_mutation",
    ):
        if policy.get(key) is not True:
            errors.append(f"{path}: {key} must be true")
    for key in ("automatic_public_use_allowed", "automatic_master_index_mutation_allowed"):
        if policy.get(key) is not False:
            errors.append(f"{path}: {key} must be false")
    errors.extend(_check_false_map(path, policy.get("product_boundary", {}), runtime.PRODUCT_BOUNDARY_FALSE_FIELDS, "product_boundary"))
    return errors


def validate_audit_report(report: Mapping[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    if report.get("schema_version") != "track_b_10_report.v0":
        errors.append(f"{path}: unexpected schema_version")
    if report.get("task") != "TRACK-B-10":
        errors.append(f"{path}: task must be TRACK-B-10")
    scope = report.get("runtime_scope", {})
    for key in ("explicit_workunit_input_only", "dry_run_only", "writes_no_files_by_default"):
        if scope.get(key) is not True:
            errors.append(f"{path}: runtime_scope.{key} must be true")
    for key in ("executes_workunit_actions", "public_telemetry_enabled"):
        if scope.get(key) is not False:
            errors.append(f"{path}: runtime_scope.{key} must be false")
    truth = report.get("truth_boundary", {})
    for key in ("dry_run_result_is_public_truth", "dry_run_result_is_accepted_evidence", "dry_run_result_can_mutate_master_index"):
        if truth.get(key) is not False:
            errors.append(f"{path}: truth_boundary.{key} must be false")
    if truth.get("human_review_required_for_downstream_use") is not True:
        errors.append(f"{path}: truth_boundary.human_review_required_for_downstream_use must be true")
    errors.extend(_check_false_map(path, report.get("product_boundary", {}), AUDIT_PRODUCT_FALSE_FIELDS, "product_boundary"))
    return errors


def validate_sample_report(report: Mapping[str, Any], path: str, repo_root: Path) -> list[str]:
    return validate_dry_run_result_payload(report, path, repo_root)


def validate_dry_run_result_payload(payload: Mapping[str, Any], path: str, repo_root: Path) -> list[str]:
    errors = []
    errors.extend(f"{path}: {error}" for error in runtime.validate_dry_run_result(payload))
    errors.extend(validate_workunit_result_record(payload, path, repo_root=repo_root))
    if _sequence(payload.get("executed_actions")):
        errors.append(f"{path}: executed_actions must be empty")
    return sorted(set(errors))


def validate_docs(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for doc in DOC_PATHS:
        text = (repo_root / doc).read_text(encoding="utf-8").casefold()
        for phrase in ("dry-run", "workunitresult", "review", "master-index"):
            if phrase not in text:
                errors.append(f"{doc}: missing phrase {phrase}")
    return errors


def validate_script_check(repo_root: Path) -> list[str]:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_workunit_dry_run.py",
            "--workunit",
            "examples/work_units/search_need_review_v0/work_unit.json",
            "--check",
            "--json",
        ],
        cwd=repo_root,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        return [f"run_workunit_dry_run --check failed: {completed.stderr.strip()} {completed.stdout.strip()}"]
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return [f"run_workunit_dry_run --check did not emit JSON: {exc}"]
    if payload.get("workunit_result_status") != "pass":
        return ["run_workunit_dry_run --check returned non-pass dry-run result"]
    if payload.get("executed_actions"):
        return ["run_workunit_dry_run emitted executed actions"]
    return []


def validate_forbidden_output_root_rejected(repo_root: Path) -> list[str]:
    forbidden = repo_root / "runtime" / "__workunit_dry_run_forbidden_result.json"
    if forbidden.exists():
        return [f"forbidden test path unexpectedly exists before validation: {forbidden}"]
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_workunit_dry_run.py",
            "--workunit",
            "examples/work_units/search_need_review_v0/work_unit.json",
            "--output",
            str(forbidden),
        ],
        cwd=repo_root,
        text=True,
        capture_output=True,
    )
    if completed.returncode == 0:
        return ["run_workunit_dry_run allowed forbidden runtime output path"]
    if forbidden.exists():
        return ["run_workunit_dry_run created forbidden runtime output path"]
    return []


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require_values(path: str, field: str, data: Mapping[str, Any], expected: Iterable[str]) -> list[str]:
    actual = set(data.get(field, []))
    missing = sorted(set(expected) - actual)
    return [f"{path}: {field} missing {missing}"] if missing else []


def _check_false_map(path: str, data: Any, fields: Iterable[str], label: str) -> list[str]:
    if not isinstance(data, Mapping):
        return [f"{path}: {label} must be an object"]
    return [f"{path}: {label}.{field} must be false" for field in sorted(fields) if data.get(field) is not False]


def _scan_for_forbidden_claims(value: Any, path: str) -> list[str]:
    errors: list[str] = []
    for key_path, text in _walk_strings(value):
        lowered = text.casefold()
        for phrase in sorted(FORBIDDEN_STRING_CLAIMS):
            if phrase in lowered:
                errors.append(f"{path}: forbidden claim phrase {phrase!r} in {key_path}")
    return errors


def _walk_strings(value: Any, prefix: str = "$") -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield prefix, value
    elif isinstance(value, Mapping):
        for key, child in value.items():
            yield from _walk_strings(child, f"{prefix}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_strings(child, f"{prefix}[{index}]")


def _sequence(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _report(errors: Sequence[str]) -> dict[str, Any]:
    sorted_errors = sorted(set(errors))
    return {
        "status": "invalid" if sorted_errors else "valid",
        "errors": sorted_errors,
        "checked": {
            "policies": sorted([DRY_RUN_POLICY_PATH, ACTION_MATRIX_PATH, OUTPUT_POLICY_PATH, REVIEW_POLICY_PATH]),
            "examples": EXAMPLE_ROOT,
            "sample_report": SAMPLE_REPORT_PATH,
        },
    }


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(argv)

    report = validate_workunit_dry_run_runner(REPO_ROOT)
    if args.json:
        stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    elif report["status"] == "valid":
        stdout.write("WorkUnit dry-run runner validation: PASS\n")
    else:
        stdout.write("WorkUnit dry-run runner validation: FAIL\n")
        for error in report["errors"]:
            stdout.write(f"- {error}\n")
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())

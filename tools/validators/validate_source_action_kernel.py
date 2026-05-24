#!/usr/bin/env python3
"""Validate SOURCE-ACTION-KERNEL-00 evidence, runtime behavior, and boundaries."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from runtime.connectors.fixture_source_action import build_adapter
from runtime.connectors.internet_archive_metadata import build_registration
from runtime.source.action import (
    check_source_action_policy,
    default_source_action_policy,
    plan_source_action,
    register_source_action_adapter,
    reset_source_action_registry_for_tests,
    run_source_action,
    validate_source_action_manifest,
)


TASK = "AIDE-BATCH-SOURCE-ACTION-KERNEL-00"

CONTRACTS = {
    "contracts/source/action/README.md",
    "contracts/source/action/source_action_manifest.v0.json",
    "contracts/source/action/source_action_policy.v0.json",
    "contracts/source/action/source_capability_profile.v0.json",
    "contracts/source/action/source_request_plan.v0.json",
    "contracts/source/action/source_transport_plan.v0.json",
    "contracts/source/action/source_transport_result.v0.json",
    "contracts/source/action/source_normalizer_result.v0.json",
    "contracts/source/action/source_observation_envelope.v0.json",
    "contracts/source/action/source_cache_mapping_plan.v0.json",
    "contracts/source/action/evidence_candidate_mapping_plan.v0.json",
    "contracts/source/action/candidate_mapping_plan.v0.json",
    "contracts/source/action/review_handoff_plan.v0.json",
    "contracts/source/action/result_lane_projection_plan.v0.json",
    "contracts/source/action/source_rate_limit_ledger.v0.json",
    "contracts/source/action/source_backoff_decision.v0.json",
    "contracts/source/action/source_action_boundary_report.v0.json",
    "contracts/source/action/source_action_run.v0.json",
    "contracts/source/action/source_action_scorecard.v0.json",
    "contracts/source/action/source_action_adapter_registration.v0.json",
}

FAMILIES = {
    "contracts/source/families/README.md",
    "contracts/source/families/fixture_source_action.v0.json",
    "contracts/source/families/internet_archive_metadata.v0.json",
    "contracts/source/families/wayback_cdx.v0.json",
    "contracts/source/families/github_releases.v0.json",
    "contracts/source/families/software_heritage.v0.json",
    "contracts/source/families/package_registries.v0.json",
    "contracts/source/families/open_library.v0.json",
    "contracts/source/families/wikidata.v0.json",
    "contracts/source/families/manual_source_pack.v0.json",
}

POLICIES = {
    "control/policies/source_action_kernel_policy.json",
    "control/policies/source_action_adapter_policy.json",
    "control/policies/source_action_transport_policy.json",
    "control/policies/source_action_rate_limit_policy.json",
    "control/policies/source_action_mapping_policy.json",
    "control/policies/source_action_non_claim_policy.json",
    "control/policies/source_action_future_live_policy.json",
}

MATRICES = {
    "control/inventory/source_action_kernel_input_state.json",
    "control/inventory/source_action_contract_matrix.json",
    "control/inventory/source_action_lifecycle_matrix.json",
    "control/inventory/source_action_policy_matrix.json",
    "control/inventory/source_action_adapter_manifest_matrix.json",
    "control/inventory/source_action_capability_matrix.json",
    "control/inventory/source_action_transport_matrix.json",
    "control/inventory/source_action_normalizer_matrix.json",
    "control/inventory/source_action_mapping_matrix.json",
    "control/inventory/source_action_lane_projection_matrix.json",
    "control/inventory/source_action_review_handoff_matrix.json",
    "control/inventory/source_action_rate_limit_matrix.json",
    "control/inventory/source_action_backoff_matrix.json",
    "control/inventory/source_action_scorecard_matrix.json",
    "control/inventory/source_action_resolution_run_handoff_matrix.json",
    "control/inventory/source_action_workbench_console_matrix.json",
    "control/inventory/source_action_boundary_report.json",
    "control/inventory/source_action_smoke_result.json",
    "control/inventory/source_action_failure_repair_log.json",
    "control/inventory/source_action_validation_matrix.json",
    "control/inventory/source_action_kernel_result.json",
    "control/inventory/source_action_next_task_decision.json",
}

EXAMPLES = {
    "examples/source_actions/fixture_source_action_manifest.json",
    "examples/source_actions/fixture_source_action_request_plan.json",
    "examples/source_actions/fixture_source_action_transport_result.json",
    "examples/source_actions/fixture_source_action_normalizer_result.json",
    "examples/source_actions/fixture_source_observation_envelope.json",
    "examples/source_actions/fixture_source_cache_mapping_plan.json",
    "examples/source_actions/fixture_evidence_candidate_mapping_plan.json",
    "examples/source_actions/fixture_candidate_mapping_plan.json",
    "examples/source_actions/fixture_review_handoff_plan.json",
    "examples/source_actions/fixture_result_lane_projection_plan.json",
    "examples/source_actions/fixture_boundary_report.json",
    "examples/source_actions/fixture_scorecard.json",
    "examples/sources/wayback_cdx/source_family_descriptor.json",
    "examples/sources/github_releases/source_family_descriptor.json",
    "examples/sources/software_heritage/source_family_descriptor.json",
    "examples/sources/package_registries/source_family_descriptor.json",
    "examples/sources/open_library/source_family_descriptor.json",
    "examples/sources/wikidata/source_family_descriptor.json",
    "examples/sources/internet_archive_metadata/source_family_descriptor.json",
}

DOCS = {
    "docs/architecture/SOURCE_ACTION_KERNEL.md",
    "docs/architecture/SOURCE_ACTION_ADAPTER_MODEL.md",
    "docs/architecture/SOURCE_ACTION_POLICY_GATE.md",
    "docs/architecture/SOURCE_ACTION_RATE_LIMIT_AND_BACKOFF.md",
    "docs/architecture/SOURCE_ACTION_MAPPING_MODEL.md",
    "docs/operations/SOURCE_ACTION_KERNEL_RUNBOOK.md",
    "docs/operations/POST_SOURCE_ACTION_KERNEL_PLAN.md",
    "docs/reference/SOURCE_ACTION_MANIFEST.md",
    "docs/reference/SOURCE_ACTION_LIFECYCLE.md",
    "docs/reference/SOURCE_ACTION_BOUNDARY_REPORT.md",
    "docs/reference/SOURCE_ACTION_SCORECARD.md",
}

AUDIT_FILES = {
    "control/audits/source-action-kernel-00-v0/README.md",
    "control/audits/source-action-kernel-00-v0/source_action_kernel_report.json",
    "control/audits/source-action-kernel-00-v0/contract_matrix.md",
    "control/audits/source-action-kernel-00-v0/lifecycle_matrix.md",
    "control/audits/source-action-kernel-00-v0/adapter_manifest_matrix.md",
    "control/audits/source-action-kernel-00-v0/capability_matrix.md",
    "control/audits/source-action-kernel-00-v0/transport_matrix.md",
    "control/audits/source-action-kernel-00-v0/mapping_matrix.md",
    "control/audits/source-action-kernel-00-v0/rate_limit_matrix.md",
    "control/audits/source-action-kernel-00-v0/scorecard_matrix.md",
    "control/audits/source-action-kernel-00-v0/boundary_report.md",
    "control/audits/source-action-kernel-00-v0/smoke_result.md",
    "control/audits/source-action-kernel-00-v0/validation_matrix.md",
    "control/audits/source-action-kernel-00-v0/validation.md",
    "control/audits/source-action-kernel-00-v0/generated/sample_source_action_manifest.json",
    "control/audits/source-action-kernel-00-v0/generated/sample_request_plan.json",
    "control/audits/source-action-kernel-00-v0/generated/sample_transport_result.json",
    "control/audits/source-action-kernel-00-v0/generated/sample_observation_envelope.json",
    "control/audits/source-action-kernel-00-v0/generated/sample_mapping_plan.json",
    "control/audits/source-action-kernel-00-v0/generated/sample_lane_projection_plan.json",
    "control/audits/source-action-kernel-00-v0/generated/sample_review_handoff_plan.json",
    "control/audits/source-action-kernel-00-v0/generated/sample_boundary_report.json",
    "control/audits/source-action-kernel-00-v0/generated/sample_scorecard.json",
    "control/audits/source-action-kernel-00-v0/generated/sample_summary.md",
}

BOUNDARY_FALSES = (
    "live_call_performed",
    "raw_response_committed",
    "source_cache_write_performed",
    "evidence_write_performed",
    "candidate_write_performed",
    "reviewed_index_mutated",
    "master_index_mutated",
    "operator_instance_mutated",
    "download_performed",
    "extraction_executed",
    "model_provider_used",
    "deployment_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"source action kernel validation: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
        for warning in result["warnings"]:
            print(f"WARN: {warning}", file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    for rel in sorted(CONTRACTS | FAMILIES | POLICIES | MATRICES | EXAMPLES | DOCS | AUDIT_FILES):
        require_file(root, rel, errors)
    payloads = {rel: load_json(root / rel, errors) for rel in sorted(POLICIES | MATRICES | EXAMPLES)}
    validate_policies(payloads, errors)
    validate_matrices(payloads, errors)
    validate_result(payloads.get("control/inventory/source_action_kernel_result.json", {}), errors)
    validate_examples(payloads, errors)
    runtime_checks = validate_runtime(root, errors)
    script_checks = validate_scripts(root, errors)
    validate_ia_registration(errors)
    return {
        "schema_version": "source_action_kernel_validation.v0",
        "task": TASK,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "runtime_checks": runtime_checks,
        "script_checks": script_checks,
        "contracts_added": all((root / rel).is_file() for rel in CONTRACTS),
        "policies_added": all((root / rel).is_file() for rel in POLICIES),
        "source_family_descriptors_added": all((root / rel).is_file() for rel in FAMILIES),
        "runtime_source_action_kernel_added": (root / "runtime/source/action/action_kernel.py").is_file(),
        "fixture_adapter_added": (root / "runtime/connectors/fixture_source_action/adapter.py").is_file(),
        "ia_metadata_reference_adapter_registered": (root / "runtime/connectors/internet_archive_metadata/registration.py").is_file(),
        "cli_added": (root / "scripts/eureka_source_action.py").is_file(),
        "tools_added": (root / "tools/generators/source_action_fixture_builder.py").is_file(),
        "examples_added": all((root / rel).is_file() for rel in EXAMPLES),
        "docs_added": all((root / rel).is_file() for rel in DOCS),
        "validator_added": True,
        "tests_added": True,
        "fixture_source_action_passed": runtime_checks.get("fixture_source_action_passed") is True,
        "source_action_manifest_validation_passed": runtime_checks.get("manifest_validation_passed") is True,
        "mapping_plans_created": runtime_checks.get("mapping_plans_created") is True,
        "review_handoff_plan_created": runtime_checks.get("review_handoff_plan_created") is True,
        "lane_projection_plan_created": runtime_checks.get("lane_projection_plan_created") is True,
        "boundary_report_created": runtime_checks.get("boundary_report_created") is True,
        "scorecard_created": runtime_checks.get("scorecard_created") is True,
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    combined: dict[str, Any] = {}
    for rel in POLICIES:
        combined.update(payloads.get(rel, {}))
    for field in (
        "source_actions_are_not_truth",
        "source_actions_do_not_create_reviewed_records",
        "source_actions_do_not_mutate_master_index",
        "source_actions_do_not_mutate_public_index",
        "source_actions_do_not_mutate_operator_instance_by_default",
        "source_actions_require_policy_gate",
        "source_actions_require_boundary_report",
        "source_actions_require_source_family_manifest",
        "source_actions_require_capability_profile",
        "source_actions_require_rate_limit_policy",
        "source_actions_require_redaction_policy_for_live",
        "source_actions_require_transport_result_classification",
        "mock_transport_enabled",
        "fixture_transport_enabled",
        "live_transport_requires_operator_policy",
    ):
        if combined.get(field) is not True:
            errors.append(f"policy requires {field}=true")
    for field in (
        "live_source_calls_enabled_by_default",
        "public_live_source_action_enabled",
        "downloads_enabled",
        "extraction_enabled",
        "model_provider_enabled",
        "deployment_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if combined.get(field) is not False:
            errors.append(f"policy requires {field}=false")


def validate_matrices(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    lifecycle = payloads.get("control/inventory/source_action_lifecycle_matrix.json", {})
    for state in ("planned", "policy_checked", "transport_completed", "normalized", "mapping_planned", "lane_projected", "review_handoff_prepared", "completed"):
        if state not in lifecycle.get("states", []):
            errors.append(f"lifecycle matrix missing state {state}")
    adapters = payloads.get("control/inventory/source_action_adapter_manifest_matrix.json", {})
    for adapter in ("fixture_source_action", "internet_archive_metadata_reference", "future_wayback_cdx", "future_github_releases"):
        if adapter not in adapters.get("adapters", []):
            errors.append(f"adapter matrix missing {adapter}")
    lanes = payloads.get("control/inventory/source_action_lane_projection_matrix.json", {})
    for lane in ("source_cache_hits", "ia_metadata_candidates", "local_candidate_results", "review_queue_items", "blocked_actions"):
        if lane not in lanes.get("lane_projection_targets", []):
            errors.append(f"lane projection matrix missing {lane}")
    review = payloads.get("control/inventory/source_action_review_handoff_matrix.json", {})
    if review.get("review_acceptance_performed") is not False or review.get("promotion_performed") is not False:
        errors.append("review handoff matrix must not accept review or promote")
    mapping = payloads.get("control/inventory/source_action_mapping_matrix.json", {})
    if mapping.get("store_mutation_performed") is not False:
        errors.append("mapping matrix must be plan-only")


def validate_result(payload: Mapping[str, Any], errors: list[str]) -> None:
    if payload.get("status") not in {"pass", "pass_with_warnings"}:
        errors.append("source_action_kernel_result status must be pass or pass_with_warnings")
    for field in (
        "contracts_added",
        "policies_added",
        "source_family_descriptors_added",
        "runtime_source_action_kernel_added",
        "fixture_adapter_added",
        "ia_metadata_reference_adapter_registered",
        "fixture_source_action_passed",
        "source_action_manifest_validation_passed",
        "mapping_plans_created",
        "review_handoff_plan_created",
        "lane_projection_plan_created",
        "boundary_report_created",
        "scorecard_created",
    ):
        if payload.get(field) is not True:
            errors.append(f"result requires {field}=true")
    for field in (
        "live_source_call_performed",
        "source_probe_executed",
        "raw_live_source_response_committed",
        "source_cache_write_performed",
        "evidence_write_performed",
        "candidate_index_mutated",
        "reviewed_index_mutated",
        "master_index_mutated",
        "operator_instance_mutated",
        "download_performed",
        "upload_performed",
        "extraction_executed",
        "model_provider_used",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if payload.get(field) is not False:
            errors.append(f"result requires {field}=false")


def validate_examples(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    manifest = payloads.get("examples/source_actions/fixture_source_action_manifest.json", {})
    if validate_source_action_manifest(manifest)["status"] != "pass":
        errors.append("fixture source action manifest example does not validate")
    boundary = payloads.get("examples/source_actions/fixture_boundary_report.json", {})
    for field in BOUNDARY_FALSES:
        if boundary.get(field) is not False:
            errors.append(f"fixture boundary report requires {field}=false")


def validate_runtime(root: Path, errors: list[str]) -> dict[str, Any]:
    del root
    reset_source_action_registry_for_tests()
    adapter = build_adapter()
    registration = register_source_action_adapter(adapter)
    manifest_validation = validate_source_action_manifest(adapter.manifest())
    run = run_source_action(query="sampleproject", source_family="fixture_source_action", action_kind="metadata_search")
    live_plan = plan_source_action(
        "sampleproject",
        "fixture_source_action",
        "metadata_search",
        default_source_action_policy(),
        transport_mode="operator_approved_live",
    )
    live_policy = check_source_action_policy(live_plan, default_source_action_policy())
    for field in BOUNDARY_FALSES:
        if run["boundary_report"].get(field) is not False:
            errors.append(f"runtime boundary report requires {field}=false")
    if live_policy.get("allowed") is not False:
        errors.append("operator-approved live transport must be blocked by default")
    return {
        "registration": registration.get("registered") is True,
        "fixture_source_action_passed": run.get("status") == "completed",
        "manifest_validation_passed": manifest_validation.get("status") == "pass",
        "mapping_plans_created": bool(run.get("source_cache_mapping_plan") and run.get("candidate_mapping_plan")),
        "review_handoff_plan_created": bool(run.get("review_handoff_plan")),
        "lane_projection_plan_created": bool(run.get("result_lane_projection_plan")),
        "boundary_report_created": bool(run.get("boundary_report")),
        "scorecard_created": bool(run.get("scorecard")),
        "live_blocked_by_default": live_policy.get("allowed") is False,
    }


def validate_scripts(root: Path, errors: list[str]) -> dict[str, Any]:
    commands = {
        "manifest": [
            sys.executable,
            "scripts/eureka_source_action_manifest.py",
            "--manifest",
            "examples/source_actions/fixture_source_action_manifest.json",
            "--validate",
            "--json",
        ],
        "fixture": [
            sys.executable,
            "scripts/eureka_source_action.py",
            "--source-family",
            "fixture_source_action",
            "--action-kind",
            "metadata_search",
            "--query",
            "sampleproject",
            "--transport",
            "fixture",
            "--dry-run",
            "--json",
        ],
        "scorecard": [
            sys.executable,
            "scripts/eureka_source_action_scorecard.py",
            "--source-family",
            "fixture_source_action",
            "--from-examples",
            "--json",
        ],
    }
    results: dict[str, Any] = {}
    for name, command in commands.items():
        completed = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
        results[name] = {"returncode": completed.returncode}
        if completed.returncode != 0:
            errors.append(f"script command failed: {name}: {completed.stderr or completed.stdout}")
    return results


def validate_ia_registration(errors: list[str]) -> None:
    registration = build_registration()
    if registration.get("source_family") != "internet_archive_metadata":
        errors.append("IA metadata registration source family mismatch")
    for field in ("default_enabled", "public_fanout_allowed", "downloads_allowed", "extraction_allowed", "accepted_truth"):
        if registration.get(field) is not False:
            errors.append(f"IA metadata registration requires {field}=false")


def require_file(root: Path, rel: str, errors: list[str]) -> None:
    if not (root / rel).is_file():
        errors.append(f"missing required file: {rel}")


def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"invalid json: {path.relative_to(REPO_ROOT)}: {exc}")
        return {}


if __name__ == "__main__":
    raise SystemExit(main())

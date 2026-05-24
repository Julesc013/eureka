#!/usr/bin/env python3
"""Validate SOURCE-WAVE-00 metadata-only source family registration."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from runtime.source.action import (
    REQUIRED_SOURCE_WAVE_FAMILIES,
    get_source_family_manifest,
    list_registered_source_families,
    run_source_family_fixture_action,
    smoke_source_wave_families,
    validate_source_action_manifest,
)


TASK = "AIDE-BATCH-SOURCE-WAVE-00"

POLICIES = {
    "control/policies/source_wave_policy.json",
    "control/policies/source_wave_family_policy.json",
    "control/policies/source_wave_fixture_policy.json",
    "control/policies/source_wave_live_policy.json",
    "control/policies/source_wave_mapping_policy.json",
    "control/policies/source_wave_non_claim_policy.json",
}

MATRICES = {
    "control/inventory/source_wave_input_state.json",
    "control/inventory/source_wave_family_matrix.json",
    "control/inventory/source_wave_manifest_matrix.json",
    "control/inventory/source_wave_capability_matrix.json",
    "control/inventory/source_wave_fixture_matrix.json",
    "control/inventory/source_wave_transport_matrix.json",
    "control/inventory/source_wave_normalizer_matrix.json",
    "control/inventory/source_wave_mapping_matrix.json",
    "control/inventory/source_wave_lane_projection_matrix.json",
    "control/inventory/source_wave_review_handoff_matrix.json",
    "control/inventory/source_wave_scorecard_matrix.json",
    "control/inventory/source_wave_resolution_run_handoff_matrix.json",
    "control/inventory/source_wave_boundary_report.json",
    "control/inventory/source_wave_smoke_result.json",
    "control/inventory/source_wave_failure_repair_log.json",
    "control/inventory/source_wave_validation_matrix.json",
    "control/inventory/source_wave_result.json",
    "control/inventory/source_wave_next_task_decision.json",
}

DOCS = {
    "docs/architecture/SOURCE_WAVE_METADATA.md",
    "docs/architecture/SOURCE_FAMILY_ADAPTERS.md",
    "docs/architecture/SOURCE_WAVE_POLICY_GATE.md",
    "docs/architecture/SOURCE_WAVE_SCORECARDS.md",
    "docs/operations/SOURCE_WAVE_RUNBOOK.md",
    "docs/operations/POST_SOURCE_WAVE_PLAN.md",
    "docs/reference/SOURCE_FAMILY_MANIFEST.md",
    "docs/reference/SOURCE_WAVE_BOUNDARY_REPORT.md",
    "docs/reference/SOURCE_WAVE_SCORECARD.md",
}

SCRIPTS = {
    "scripts/eureka_source_wave.py",
    "scripts/eureka_source_wave_smoke.py",
    "scripts/validate_source_wave.py",
    "tools/generators/source_wave_fixture_builder.py",
    "tools/auditors/source_wave_boundary_auditor.py",
    "tools/validators/validate_source_wave.py",
}

AUDIT_FILES = {
    "control/audits/source-wave-00-v0/README.md",
    "control/audits/source-wave-00-v0/source_wave_report.json",
    "control/audits/source-wave-00-v0/family_matrix.md",
    "control/audits/source-wave-00-v0/manifest_matrix.md",
    "control/audits/source-wave-00-v0/capability_matrix.md",
    "control/audits/source-wave-00-v0/fixture_matrix.md",
    "control/audits/source-wave-00-v0/transport_matrix.md",
    "control/audits/source-wave-00-v0/mapping_matrix.md",
    "control/audits/source-wave-00-v0/scorecard_matrix.md",
    "control/audits/source-wave-00-v0/resolution_run_handoff_matrix.md",
    "control/audits/source-wave-00-v0/boundary_report.md",
    "control/audits/source-wave-00-v0/smoke_result.md",
    "control/audits/source-wave-00-v0/validation_matrix.md",
    "control/audits/source-wave-00-v0/validation.md",
    "control/audits/source-wave-00-v0/generated/sample_source_family_manifest.json",
    "control/audits/source-wave-00-v0/generated/sample_fixture_transport_result.json",
    "control/audits/source-wave-00-v0/generated/sample_mapping_plan.json",
    "control/audits/source-wave-00-v0/generated/sample_lane_projection_plan.json",
    "control/audits/source-wave-00-v0/generated/sample_review_handoff_plan.json",
    "control/audits/source-wave-00-v0/generated/sample_scorecard.json",
    "control/audits/source-wave-00-v0/generated/sample_boundary_report.json",
    "control/audits/source-wave-00-v0/generated/sample_summary.md",
}

BOUNDARY_FALSES = (
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
        print(f"source wave validation: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
        for warning in result["warnings"]:
            print(f"WARN: {warning}", file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    source_action_result = load_json(root / "control/inventory/source_action_kernel_result.json", errors)
    if source_action_result.get("status") not in {"pass", "pass_with_warnings"}:
        errors.append("SOURCE-ACTION-KERNEL-00 result is missing or not pass/pass_with_warnings")
    for rel in sorted(POLICIES | MATRICES | DOCS | SCRIPTS | AUDIT_FILES):
        require_file(root, rel, errors)
    for family in REQUIRED_SOURCE_WAVE_FAMILIES:
        require_file(root, f"contracts/source/families/{family}.v0.json", errors)
        require_file(root, f"{get_source_family_manifest(family)['fixture_refs'][0]}", errors)
        require_file(root, f"{Path(get_source_family_manifest(family)['fixture_refs'][0]).parent}/source_scorecard.json", errors)
    payloads = {rel: load_json(root / rel, errors) for rel in sorted(POLICIES | MATRICES)}
    validate_policies(payloads, errors)
    validate_result(payloads.get("control/inventory/source_wave_result.json", {}), errors)
    validate_runtime(errors)
    validate_scripts(root, errors)
    return {
        "schema_version": "source_wave_validation.v0",
        "task": TASK,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "required_family_count": len(REQUIRED_SOURCE_WAVE_FAMILIES),
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    required_true = (
        "source_wave_uses_source_action_kernel",
        "source_wave_adds_metadata_families_only",
        "source_wave_outputs_are_not_truth",
        "source_wave_does_not_accept_evidence",
        "source_wave_does_not_create_reviewed_records",
        "source_wave_does_not_mutate_master_index",
        "source_wave_does_not_mutate_public_index",
        "source_wave_does_not_mutate_operator_instance",
        "source_wave_requires_source_family_manifest",
        "source_wave_requires_fixture_or_mock_transport",
        "source_wave_requires_scorecard",
        "source_wave_requires_boundary_report",
    )
    required_false = (
        "live_source_calls_enabled_by_default",
        "public_live_source_fanout_enabled",
        "downloads_enabled",
        "extraction_enabled",
        "model_provider_enabled",
        "deployment_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    )
    for rel, payload in payloads.items():
        if not rel.startswith("control/policies/"):
            continue
        for key in required_true:
            if payload.get(key) is not True:
                errors.append(f"{rel}: {key} must be true")
        for key in required_false:
            if payload.get(key) is not False:
                errors.append(f"{rel}: {key} must be false")


def validate_result(result: Mapping[str, Any], errors: list[str]) -> None:
    required_true = (
        "policies_added",
        "source_families_added",
        "family_descriptors_added",
        "fixtures_added",
        "adapters_registered",
        "capability_matrix_added",
        "manifest_matrix_added",
        "transport_matrix_added",
        "normalizer_matrix_added",
        "mapping_matrix_added",
        "lane_projection_matrix_added",
        "review_handoff_matrix_added",
        "scorecard_matrix_added",
        "resolution_run_handoff_matrix_added",
        "scripts_added",
        "examples_added",
        "docs_added",
        "validator_added",
        "tests_added",
        "all_required_families_fixture_smoke_passed",
        "source_wave_smoke_passed",
        "mapping_plans_created",
        "review_handoff_plans_created",
        "lane_projection_plans_created",
        "scorecards_created",
        "boundary_reports_created",
    )
    for key in required_true:
        if result.get(key) is not True:
            errors.append(f"source_wave_result: {key} must be true")
    if result.get("required_family_count") != len(REQUIRED_SOURCE_WAVE_FAMILIES):
        errors.append("source_wave_result: required_family_count mismatch")
    for key in BOUNDARY_FALSES:
        if result.get(key) is not False:
            errors.append(f"source_wave_result: {key} must be false")


def validate_runtime(errors: list[str]) -> None:
    families = list_registered_source_families()
    if set(families) != set(REQUIRED_SOURCE_WAVE_FAMILIES):
        errors.append("runtime source wave family list mismatch")
    for family in REQUIRED_SOURCE_WAVE_FAMILIES:
        manifest = get_source_family_manifest(family)
        manifest_result = validate_source_action_manifest(manifest)
        if manifest_result["status"] != "pass":
            errors.append(f"{family}: source action manifest validation failed: {manifest_result['errors']}")
        action_kind = manifest["supported_capabilities"][0]
        run = run_source_family_fixture_action(family, action_kind, "sampleproject")
        if run.get("status") != "completed":
            errors.append(f"{family}: fixture run did not complete")
        if not run.get("candidate_mapping_plan"):
            errors.append(f"{family}: missing candidate mapping plan")
        if not run.get("review_handoff_plan"):
            errors.append(f"{family}: missing review handoff plan")
        if not run.get("result_lane_projection_plan"):
            errors.append(f"{family}: missing lane projection plan")
        if not run.get("scorecard"):
            errors.append(f"{family}: missing scorecard")
        boundary = run.get("boundary_report", {})
        for key in (
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
        ):
            if boundary.get(key) is not False:
                errors.append(f"{family}: boundary {key} must be false")
    smoke = smoke_source_wave_families()
    if smoke.get("status") != "pass":
        errors.append("source wave smoke did not pass")


def validate_scripts(root: Path, errors: list[str]) -> None:
    commands = (
        [sys.executable, "scripts/eureka_source_wave.py", "--list-families", "--json"],
        [
            sys.executable,
            "scripts/eureka_source_wave.py",
            "--family",
            "internet_archive_metadata_v2",
            "--action-kind",
            "metadata_search",
            "--query",
            "sampleproject",
            "--transport",
            "fixture",
            "--json",
        ],
        [sys.executable, "scripts/eureka_source_wave_smoke.py", "--all-families", "--transport", "fixture", "--json"],
    )
    for command in commands:
        completed = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
        if completed.returncode != 0:
            errors.append(f"script failed: {' '.join(command)} :: {completed.stderr or completed.stdout}")


def require_file(root: Path, rel: str, errors: list[str]) -> None:
    if not (root / rel).is_file():
        errors.append(f"missing file: {rel}")


def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"missing json: {path.relative_to(REPO_ROOT)}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid json: {path.relative_to(REPO_ROOT)}: {exc}")
        return {}


if __name__ == "__main__":
    raise SystemExit(main())

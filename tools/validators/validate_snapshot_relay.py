#!/usr/bin/env python3
"""Validate SNAPSHOT-RELAY-00 read-only snapshot and relay foundation."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from runtime.capabilities import build_capability_profile, validate_capability_profile
from runtime.relay import build_relay_from_snapshot
from runtime.relay.validation import validate_relay_manifest
from runtime.snapshots.relay_foundation import (
    build_snapshot_from_examples,
    validate_snapshot_envelope,
)


TASK = "AIDE-BATCH-SNAPSHOT-RELAY-00"

POLICIES = {
    "control/policies/snapshot_policy.json",
    "control/policies/snapshot_integrity_policy.json",
    "control/policies/snapshot_publication_policy.json",
    "control/policies/relay_policy.json",
    "control/policies/relay_read_only_policy.json",
    "control/policies/capability_profile_policy.json",
    "control/policies/snapshot_relay_non_claim_policy.json",
}

CONTRACTS = {
    "contracts/snapshot/README.md",
    "contracts/snapshot/snapshot_envelope.v0.json",
    "contracts/snapshot/snapshot_manifest.v0.json",
    "contracts/snapshot/snapshot_record.v0.json",
    "contracts/snapshot/snapshot_record_set.v0.json",
    "contracts/snapshot/snapshot_integrity_manifest.v0.json",
    "contracts/snapshot/snapshot_source_summary.v0.json",
    "contracts/snapshot/snapshot_evidence_summary.v0.json",
    "contracts/snapshot/snapshot_absence_summary.v0.json",
    "contracts/snapshot/snapshot_need_summary.v0.json",
    "contracts/snapshot/snapshot_build_plan.v0.json",
    "contracts/snapshot/snapshot_build_result.v0.json",
    "contracts/snapshot/snapshot_validation_report.v0.json",
    "contracts/snapshot/snapshot_boundary_report.v0.json",
    "contracts/relay/relay_manifest.v0.json",
    "contracts/relay/relay_projection.v0.json",
    "contracts/relay/relay_record_index.v0.json",
    "contracts/relay/relay_query_response.v0.json",
    "contracts/relay/relay_health_packet.v0.json",
    "contracts/relay/relay_boundary_report.v0.json",
    "contracts/capabilities/README.md",
    "contracts/capabilities/capability_profile.v0.json",
    "contracts/capabilities/client_capability_request.v0.json",
    "contracts/capabilities/server_capability_response.v0.json",
    "contracts/capabilities/projection_capability.v0.json",
}

MATRICES = {
    "control/inventory/snapshot_relay_input_state.json",
    "control/inventory/snapshot_contract_matrix.json",
    "control/inventory/snapshot_record_matrix.json",
    "control/inventory/snapshot_manifest_matrix.json",
    "control/inventory/snapshot_integrity_matrix.json",
    "control/inventory/snapshot_capability_matrix.json",
    "control/inventory/relay_contract_matrix.json",
    "control/inventory/relay_manifest_matrix.json",
    "control/inventory/relay_projection_matrix.json",
    "control/inventory/relay_read_only_matrix.json",
    "control/inventory/snapshot_surface_projection_matrix.json",
    "control/inventory/snapshot_relay_boundary_report.json",
    "control/inventory/snapshot_relay_smoke_result.json",
    "control/inventory/snapshot_relay_failure_repair_log.json",
    "control/inventory/snapshot_relay_validation_matrix.json",
    "control/inventory/snapshot_relay_result.json",
    "control/inventory/snapshot_relay_next_task_decision.json",
}

EXAMPLES = {
    "examples/snapshots/sample_reviewed_record.json",
    "examples/snapshots/sample_source_summary.json",
    "examples/snapshots/sample_evidence_summary.json",
    "examples/snapshots/sample_absence_summary.json",
    "examples/snapshots/sample_need_summary.json",
    "examples/snapshots/sample_snapshot_build_plan.json",
    "examples/snapshots/sample_snapshot_manifest.json",
    "examples/snapshots/sample_snapshot_integrity_manifest.json",
    "examples/snapshots/sample_snapshot_envelope.json",
    "examples/snapshots/sample_snapshot_validation_report.json",
    "examples/snapshots/sample_snapshot_boundary_report.json",
    "examples/relay/sample_relay_manifest.json",
    "examples/relay/sample_relay_record_index.json",
    "examples/relay/sample_relay_query_response.json",
    "examples/relay/sample_relay_health_packet.json",
    "examples/relay/sample_relay_boundary_report.json",
    "examples/capabilities/sample_public_api_read_only_profile.json",
    "examples/capabilities/sample_native_read_only_profile.json",
    "examples/capabilities/sample_lite_read_only_profile.json",
    "snapshots/schema/README.md",
    "snapshots/examples/sample_snapshot_envelope.json",
    "snapshots/examples/sample_snapshot_manifest.json",
    "snapshots/examples/sample_snapshot_integrity_manifest.json",
}

DOCS = {
    "docs/architecture/SNAPSHOT_RELAY.md",
    "docs/architecture/REVIEWED_RECORD_SNAPSHOT_MODEL.md",
    "docs/architecture/READ_ONLY_RELAY_MODEL.md",
    "docs/architecture/CAPABILITY_PROFILE_MODEL.md",
    "docs/operations/SNAPSHOT_RELAY_RUNBOOK.md",
    "docs/operations/POST_SNAPSHOT_RELAY_PLAN.md",
    "docs/reference/SNAPSHOT_ENVELOPE.md",
    "docs/reference/SNAPSHOT_MANIFEST.md",
    "docs/reference/SNAPSHOT_RECORD.md",
    "docs/reference/RELAY_MANIFEST.md",
    "docs/reference/CAPABILITY_PROFILE.md",
}

SCRIPTS = {
    "scripts/eureka_snapshot_build.py",
    "scripts/eureka_snapshot_validate.py",
    "scripts/eureka_relay_project.py",
    "scripts/eureka_relay_validate.py",
    "scripts/eureka_capability_profile.py",
    "scripts/validate_snapshot_relay.py",
    "tools/generators/snapshot_fixture_builder.py",
    "tools/auditors/snapshot_relay_boundary_auditor.py",
    "tools/validators/validate_snapshot_relay.py",
}

AUDIT_FILES = {
    "control/audits/snapshot-relay-00-v0/README.md",
    "control/audits/snapshot-relay-00-v0/snapshot_relay_report.json",
    "control/audits/snapshot-relay-00-v0/snapshot_contract_matrix.md",
    "control/audits/snapshot-relay-00-v0/snapshot_manifest_matrix.md",
    "control/audits/snapshot-relay-00-v0/snapshot_integrity_matrix.md",
    "control/audits/snapshot-relay-00-v0/relay_contract_matrix.md",
    "control/audits/snapshot-relay-00-v0/relay_projection_matrix.md",
    "control/audits/snapshot-relay-00-v0/capability_matrix.md",
    "control/audits/snapshot-relay-00-v0/surface_projection_matrix.md",
    "control/audits/snapshot-relay-00-v0/boundary_report.md",
    "control/audits/snapshot-relay-00-v0/smoke_result.md",
    "control/audits/snapshot-relay-00-v0/validation_matrix.md",
    "control/audits/snapshot-relay-00-v0/validation.md",
    "control/audits/snapshot-relay-00-v0/generated/sample_snapshot_envelope.json",
    "control/audits/snapshot-relay-00-v0/generated/sample_snapshot_manifest.json",
    "control/audits/snapshot-relay-00-v0/generated/sample_snapshot_integrity_manifest.json",
    "control/audits/snapshot-relay-00-v0/generated/sample_relay_manifest.json",
    "control/audits/snapshot-relay-00-v0/generated/sample_relay_query_response.json",
    "control/audits/snapshot-relay-00-v0/generated/sample_capability_profile.json",
    "control/audits/snapshot-relay-00-v0/generated/sample_boundary_report.json",
    "control/audits/snapshot-relay-00-v0/generated/sample_summary.md",
}

BOUNDARY_FALSES = (
    "private_local_state_included",
    "operator_tokens_included",
    "raw_live_source_response_committed",
    "live_source_call_performed",
    "source_probe_executed",
    "operator_instance_mutated",
    "master_index_mutated",
    "committed_data_public_index_mutated",
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
        print(f"snapshot relay validation: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
        for warning in result["warnings"]:
            print(f"WARN: {warning}", file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    source_wave_result = load_json(root / "control/inventory/source_wave_result.json", errors)
    if source_wave_result.get("status") not in {"pass", "pass_with_warnings"}:
        errors.append("SOURCE-WAVE-00 result is missing or not pass/pass_with_warnings")
    for rel in sorted(POLICIES | CONTRACTS | MATRICES | EXAMPLES | DOCS | SCRIPTS | AUDIT_FILES):
        require_file(root, rel, errors)
    json_examples = {rel for rel in EXAMPLES if rel.endswith(".json")}
    payloads = {rel: load_json(root / rel, errors) for rel in sorted(POLICIES | MATRICES | json_examples)}
    validate_policies(payloads, errors)
    validate_result(payloads.get("control/inventory/snapshot_relay_result.json", {}), errors)
    validate_examples(payloads, errors)
    validate_runtime(errors)
    validate_scripts(root, errors)
    return {
        "schema_version": "snapshot_relay_validation.v0",
        "task": TASK,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    required_true = (
        "snapshots_are_read_only_data_products",
        "snapshots_may_include_reviewed_records",
        "snapshots_must_not_include_private_local_state",
        "snapshots_must_not_include_operator_tokens",
        "snapshots_must_not_include_raw_live_source_responses",
        "snapshots_must_not_include_unreviewed_truth",
        "snapshot_integrity_manifest_required",
        "snapshot_hashes_required",
        "private_signing_keys_forbidden",
        "relay_read_only",
    )
    required_false = (
        "relay_mutation_enabled",
        "relay_live_source_calls_enabled",
        "relay_downloads_enabled",
        "relay_extraction_enabled",
        "public_launch_claim_enabled",
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
        "snapshot_contracts_added",
        "relay_contracts_added",
        "capability_contracts_added",
        "snapshot_runtime_added",
        "relay_runtime_added",
        "capability_runtime_added",
        "surface_projections_added",
        "examples_added",
        "snapshots_examples_added",
        "scripts_added",
        "docs_added",
        "validator_added",
        "tests_added",
        "snapshot_build_passed",
        "snapshot_integrity_passed",
        "snapshot_validation_passed",
        "relay_manifest_passed",
        "relay_query_passed",
        "capability_profiles_passed",
        "public_projection_read_only",
        "native_projection_read_only",
        "lite_projection_read_only",
    )
    for field in required_true:
        if result.get(field) is not True:
            errors.append(f"snapshot_relay_result: {field} must be true")
    for field in BOUNDARY_FALSES:
        if result.get(field) is not False:
            errors.append(f"snapshot_relay_result: {field} must be false")


def validate_examples(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    envelope = payloads.get("examples/snapshots/sample_snapshot_envelope.json", {})
    validation = validate_snapshot_envelope(envelope)
    if validation["status"] != "pass":
        errors.append(f"sample snapshot envelope does not validate: {validation['errors']}")
    relay = payloads.get("examples/relay/sample_relay_manifest.json", {})
    relay_validation = validate_relay_manifest(relay)
    if relay_validation["status"] != "pass":
        errors.append(f"sample relay manifest does not validate: {relay_validation['errors']}")
    for rel in (
        "examples/capabilities/sample_public_api_read_only_profile.json",
        "examples/capabilities/sample_native_read_only_profile.json",
        "examples/capabilities/sample_lite_read_only_profile.json",
    ):
        profile_validation = validate_capability_profile(payloads.get(rel, {}))
        if profile_validation["status"] != "pass":
            errors.append(f"{rel} does not validate: {profile_validation['errors']}")


def validate_runtime(errors: list[str]) -> None:
    build = build_snapshot_from_examples()
    if validate_snapshot_envelope(build["envelope"])["status"] != "pass":
        errors.append("runtime snapshot envelope validation failed")
    if not build["integrity_manifest"].get("entries"):
        errors.append("runtime integrity manifest has no entries")
    relay = build_relay_from_snapshot(build, "public_api_read_only")
    if validate_relay_manifest(relay["relay_manifest"])["status"] != "pass":
        errors.append("runtime relay manifest validation failed")
    if relay["relay_query_response"].get("read_only") is not True:
        errors.append("runtime relay query must be read-only")
    for profile_id in ("public_api_read_only", "native_desktop_read_only", "lite_client_read_only"):
        profile = build_capability_profile(profile_id)
        if validate_capability_profile(profile)["status"] != "pass":
            errors.append(f"runtime capability profile failed: {profile_id}")


def validate_scripts(root: Path, errors: list[str]) -> None:
    commands = (
        [sys.executable, "scripts/eureka_snapshot_build.py", "--from-examples", "--json"],
        [sys.executable, "scripts/eureka_snapshot_validate.py", "--snapshot", "examples/snapshots/sample_snapshot_envelope.json", "--json"],
        [
            sys.executable,
            "scripts/eureka_relay_project.py",
            "--snapshot",
            "examples/snapshots/sample_snapshot_envelope.json",
            "--query",
            "sampleproject",
            "--projection",
            "public_api_read_only",
            "--json",
        ],
        [sys.executable, "scripts/eureka_relay_validate.py", "--relay", "examples/relay/sample_relay_manifest.json", "--json"],
        [sys.executable, "scripts/eureka_capability_profile.py", "--profile", "public_api_read_only", "--json"],
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

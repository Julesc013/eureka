#!/usr/bin/env python3
"""Validate F0 fixture-only extraction/member discovery foundation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.extraction_safe_fixtures import (  # noqa: E402
    BLOCKED_ACTIONS,
    PROJECTION_PROFILES,
    REQUIRED_FIXTURE_IDS,
    build_container_descriptor_from_fixture,
    build_extraction_console_view,
    build_member_manifest,
    build_workunit_seed_suggestions,
    load_f0_fixture_manifest,
    validate_f0_fixture_manifest,
    validate_member_record,
)


TASK = "AIDE-BATCH-F0-FOUNDATION-01"
FIXTURE_MANIFEST = "examples/f0/f0_fixture_manifest.json"

REQUIRED_POLICIES = (
    "control/policies/f0_extraction_policy.json",
    "control/policies/f0_fixture_policy.json",
    "control/policies/f0_resource_limit_policy.json",
    "control/policies/f0_member_manifest_policy.json",
    "control/policies/f0_non_claim_policy.json",
    "control/policies/f0_future_fetch_policy.json",
    "control/policies/f0_future_ai_policy.json",
)

REQUIRED_CONTRACTS = (
    "contracts/extraction/README.md",
    "contracts/extraction/extraction_policy.v0.json",
    "contracts/extraction/container_descriptor.v0.json",
    "contracts/extraction/member_manifest.v0.json",
    "contracts/extraction/member_record.v0.json",
    "contracts/extraction/member_observation_candidate.v0.json",
    "contracts/extraction/extraction_workunit_seed.v0.json",
    "contracts/extraction/extraction_risk_report.v0.json",
    "contracts/extraction/extraction_boundary_report.v0.json",
    "contracts/extraction/extraction_fixture_manifest.v0.json",
    "contracts/extraction/extraction_console_view.v0.json",
)

REQUIRED_MATRICES = (
    "control/inventory/f0_contract_matrix.json",
    "control/inventory/f0_safe_fixture_inventory.json",
    "control/inventory/f0_resource_limit_matrix.json",
    "control/inventory/f0_member_manifest_matrix.json",
    "control/inventory/f0_supported_container_matrix.json",
    "control/inventory/f0_blocked_container_matrix.json",
    "control/inventory/f0_workunit_seed_matrix.json",
    "control/inventory/f0_domain_handoff_matrix.json",
    "control/inventory/f0_scout_handoff_matrix.json",
    "control/inventory/f0_syn_handoff_matrix.json",
    "control/inventory/f0_workbench_console_matrix.json",
)

REQUIRED_DOCS = (
    "docs/architecture/F0_EXTRACTION_MEMBER_DISCOVERY.md",
    "docs/architecture/F0_SAFE_FIXTURE_MODEL.md",
    "docs/architecture/F0_RESOURCE_AND_SECURITY_MODEL.md",
    "docs/operations/F0_FOUNDATION_RUNBOOK.md",
    "docs/operations/POST_F0_FOUNDATION_PLAN.md",
    "docs/reference/F0_MEMBER_MANIFEST.md",
    "docs/reference/F0_EXTRACTION_WORKUNIT_SEED.md",
    "docs/reference/F0_BLOCKED_ACTIONS.md",
)

REQUIRED_SCRIPTS = (
    "scripts/eureka_f0_manifest.py",
    "scripts/eureka_f0_fixture_builder.py",
    "scripts/eureka_f0_workunit_seed.py",
    "scripts/eureka_f0_smoke.py",
    "scripts/validate_f0_foundation.py",
)

FORBIDDEN_TEXT = (
    "production-ready",
    "public launch ready",
    "download completed",
    "filesystem extraction completed",
    "arbitrary extraction completed",
    "execution completed",
    "accepted evidence truth",
    "verified record created",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    report = validate_f0_foundation(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    else:
        print("F0 foundation validation", file=stdout)
        print(f"status: {report['status']}", file=stdout)
        print(f"error_count: {len(report['errors'])}", file=stdout)
        for error in report["errors"]:
            print(f"- {error}", file=stdout)
    return 0 if report["status"] == "valid" else 1


def validate_f0_foundation(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads: dict[str, Mapping[str, Any]] = {}

    for rel_path in (*REQUIRED_CONTRACTS, *REQUIRED_DOCS, *REQUIRED_SCRIPTS):
        if not (root / rel_path).is_file():
            errors.append(f"{rel_path}: required file is missing.")

    for rel_path in (*REQUIRED_POLICIES, *REQUIRED_MATRICES):
        payload = _load_json(root / rel_path, errors)
        if isinstance(payload, Mapping):
            payloads[rel_path] = payload

    _validate_policy(payloads.get("control/policies/f0_extraction_policy.json", {}), errors)
    _validate_non_claim_policy(payloads.get("control/policies/f0_non_claim_policy.json", {}), errors)
    _validate_resource_limits(payloads.get("control/inventory/f0_resource_limit_matrix.json", {}), errors)
    _validate_container_matrices(payloads, errors)
    _validate_handoffs(payloads, errors)

    fixture_manifest = load_f0_fixture_manifest(root / FIXTURE_MANIFEST)
    fixture_report = validate_f0_fixture_manifest(fixture_manifest)
    errors.extend(fixture_report["errors"])
    if set(fixture_report["fixture_ids"]) != set(REQUIRED_FIXTURE_IDS):
        errors.append(f"{FIXTURE_MANIFEST}: fixture ids must match required F0 fixture ids.")

    safe_fixture = next((item for item in fixture_manifest["fixtures"] if item["fixture_id"] == "safe_zip_basic"), None)
    if not isinstance(safe_fixture, Mapping):
        errors.append(f"{FIXTURE_MANIFEST}: safe_zip_basic descriptor is missing.")
        safe_manifest: Mapping[str, Any] = {}
    else:
        safe_manifest = build_member_manifest(build_container_descriptor_from_fixture(safe_fixture["container_descriptor"]))
        if safe_manifest.get("member_count", 0) < 2:
            errors.append("safe_zip_basic: expected at least two member records.")
        if _mapping(safe_manifest.get("risk_report")).get("blocked_member_count") != 0:
            errors.append("safe_zip_basic: expected no blocked members.")
        for member in safe_manifest.get("members", []):
            if isinstance(member, Mapping):
                errors.extend(validate_member_record(member)["errors"])

    for descriptor_path, expected_reason in (
        ("examples/f0/unsafe_path_traversal_descriptor.json", "path_traversal"),
        ("examples/f0/unsafe_absolute_path_descriptor.json", "absolute_path"),
        ("examples/f0/large_member_declared_size_descriptor.json", "declared_size_exceeds_limit"),
    ):
        descriptor = _load_json(root / descriptor_path, errors)
        if descriptor:
            manifest = build_member_manifest(descriptor)
            reasons = set(_mapping(manifest.get("risk_report")).get("blocked_reasons", []))
            if expected_reason not in reasons:
                errors.append(f"{descriptor_path}: expected blocked reason {expected_reason}.")

    workunit_seed = build_workunit_seed_suggestions(safe_manifest)
    if workunit_seed.get("dry_run") is not True:
        errors.append("F0 WorkUnit seed suggestions must be dry-run.")
    if workunit_seed.get("creates_runtime_workunit") is not False:
        errors.append("F0 WorkUnit seed suggestions must not create runtime WorkUnits.")

    for profile in PROJECTION_PROFILES:
        view = build_extraction_console_view(safe_manifest, profile)
        if view.get("read_only") is not True:
            errors.append(f"{profile}: F0 console view must be read-only.")
        if set(view.get("blocked_actions", [])) != set(BLOCKED_ACTIONS):
            errors.append(f"{profile}: F0 console view must include all blocked actions.")
        if _mapping(view.get("non_claims")).get("filesystem_extraction_performed") is not False:
            errors.append(f"{profile}: F0 console must not claim filesystem extraction.")

    _validate_script_smoke(root, errors)
    _validate_docs_text(root, errors)

    return {
        "schema_version": "f0_foundation_validation_report.v0",
        "task": TASK,
        "status": "valid" if not errors else "invalid",
        "fixture_count": len(fixture_report.get("fixture_ids", [])),
        "safe_manifest_member_count": int(safe_manifest.get("member_count", 0)) if isinstance(safe_manifest, Mapping) else 0,
        "required_contract_count": len(REQUIRED_CONTRACTS),
        "required_policy_count": len(REQUIRED_POLICIES),
        "required_matrix_count": len(REQUIRED_MATRICES),
        "errors": errors,
        "fake_evidence_created": False,
        "fake_verified_records_created": False,
        "live_source_call_performed": False,
        "download_performed": False,
        "filesystem_extraction_performed": False,
        "arbitrary_file_extraction_performed": False,
        "execution_performed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def _validate_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    required_true = (
        "fixture_only_foundation",
        "manifest_only_enumeration_enabled",
        "path_traversal_forbidden",
        "absolute_paths_forbidden",
        "parent_directory_paths_forbidden",
        "symlink_materialization_forbidden",
        "device_file_materialization_forbidden",
        "archive_bomb_guard_required",
        "max_member_count_required",
        "max_total_uncompressed_size_required",
        "max_depth_required",
        "nested_archive_recursion_disabled_by_default",
        "future_ai_outputs_candidate_only",
    )
    required_false = (
        "arbitrary_file_extraction_enabled",
        "live_source_file_fetch_enabled",
        "downloads_enabled",
        "uploads_enabled",
        "execution_enabled",
        "install_enabled",
        "emulation_enabled",
        "extraction_to_filesystem_enabled",
        "evidence_creation_enabled",
        "reviewed_record_creation_enabled",
        "master_index_mutation_enabled",
        "model_provider_enabled",
        "public_fanout_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    )
    for flag in required_true:
        if policy.get(flag) is not True:
            errors.append(f"control/policies/f0_extraction_policy.json: {flag} must be true.")
    for flag in required_false:
        if policy.get(flag) is not False:
            errors.append(f"control/policies/f0_extraction_policy.json: {flag} must be false.")


def _validate_non_claim_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    for flag in (
        "fake_evidence_created",
        "fake_verified_records_created",
        "live_source_call_performed",
        "source_probe_executed",
        "download_performed",
        "upload_performed",
        "filesystem_extraction_performed",
        "arbitrary_file_extraction_performed",
        "execution_performed",
        "operator_instance_mutated",
        "master_index_mutated",
        "model_provider_used",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if policy.get(flag) is not False:
            errors.append(f"control/policies/f0_non_claim_policy.json: {flag} must be false.")


def _validate_resource_limits(matrix: Mapping[str, Any], errors: list[str]) -> None:
    required = {
        "max_fixture_file_size_bytes": 1048576,
        "max_member_count": 100,
        "max_declared_total_size_bytes": 10485760,
        "max_uncompressed_total_size_bytes": 10485760,
        "max_nested_depth": 1,
        "max_filename_length": 240,
    }
    limits = _mapping(matrix.get("resource_limits"))
    for key, value in required.items():
        if limits.get(key) != value:
            errors.append(f"control/inventory/f0_resource_limit_matrix.json: {key} must be {value}.")
    if limits.get("path_safety_required") is not True:
        errors.append("control/inventory/f0_resource_limit_matrix.json: path_safety_required must be true.")


def _validate_container_matrices(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    supported = payloads.get("control/inventory/f0_supported_container_matrix.json", {})
    supported_ids = {str(item.get("container_type", "")) for item in _list(supported.get("supported_container_types")) if isinstance(item, Mapping)}
    if "zip_fixture_manifest" not in supported_ids:
        errors.append("control/inventory/f0_supported_container_matrix.json: zip_fixture_manifest must be supported.")
    blocked = payloads.get("control/inventory/f0_blocked_container_matrix.json", {})
    blocked_ids = {str(item.get("container_type", "")) for item in _list(blocked.get("blocked_container_types")) if isinstance(item, Mapping)}
    for required in ("iso", "dmg", "cab", "msi", "7z", "rar", "sit", "hqx", "bin/cue", "nested archives", "encrypted archives", "executable installers", "unknown binary containers"):
        if required not in blocked_ids:
            errors.append(f"control/inventory/f0_blocked_container_matrix.json: missing blocked type {required}.")


def _validate_handoffs(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    domain = payloads.get("control/inventory/f0_domain_handoff_matrix.json", {})
    domain_ids = {str(item.get("domain_id", "")) for item in _list(domain.get("domains")) if isinstance(item, Mapping)}
    for required in ("legacy_software", "driver_support_media", "frontier_resolution_media", "manuals_docs_scans", "package_source_release", "games_emulation", "hardware_firmware_support"):
        if required not in domain_ids:
            errors.append(f"control/inventory/f0_domain_handoff_matrix.json: missing domain {required}.")
    scout = payloads.get("control/inventory/f0_scout_handoff_matrix.json", {})
    if not _list(scout.get("handoffs")):
        errors.append("control/inventory/f0_scout_handoff_matrix.json: handoffs must not be empty.")
    syn = payloads.get("control/inventory/f0_syn_handoff_matrix.json", {})
    if not _list(syn.get("syn_cases")):
        errors.append("control/inventory/f0_syn_handoff_matrix.json: syn_cases must not be empty.")


def _validate_script_smoke(root: Path, errors: list[str]) -> None:
    commands = (
        ["scripts/eureka_f0_fixture_builder.py", "--check", "--json"],
        ["scripts/eureka_f0_manifest.py", "--fixture-manifest", FIXTURE_MANIFEST, "--json"],
        ["scripts/eureka_f0_workunit_seed.py", "--from-manifest", "examples/f0/safe_zip_expected_manifest.json", "--dry-run", "--json"],
    )
    for command in commands:
        result = subprocess.run([sys.executable, *command], cwd=root, text=True, capture_output=True, check=False)
        if result.returncode != 0:
            errors.append(f"{' '.join(command)} failed: {result.stdout} {result.stderr}")


def _validate_docs_text(root: Path, errors: list[str]) -> None:
    required_phrases = ("fixture-only", "manifest-only", "no downloads", "no filesystem extraction", "no execution", "not truth", "review")
    for rel_path in REQUIRED_DOCS:
        path = root / rel_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8").lower()
        for phrase in required_phrases:
            if phrase not in text:
                errors.append(f"{rel_path}: must state {phrase!r}.")
        for forbidden in FORBIDDEN_TEXT:
            if forbidden in text:
                errors.append(f"{rel_path}: forbidden claim text {forbidden!r}.")


def _load_json(path: Path, errors: list[str]) -> Mapping[str, Any]:
    if not path.is_file():
        errors.append(f"{path.relative_to(REPO_ROOT)}: required JSON file is missing.")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{path.relative_to(REPO_ROOT)}: invalid JSON: {exc}.")
        return {}
    if not isinstance(payload, Mapping):
        errors.append(f"{path.relative_to(REPO_ROOT)}: JSON root must be an object.")
        return {}
    return payload


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


if __name__ == "__main__":
    raise SystemExit(main())

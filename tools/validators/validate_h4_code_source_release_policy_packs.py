#!/usr/bin/env python3
"""Validate H4-BUNDLE-01 code/source/release host policy packs offline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]

EXPECTED_SOURCES = {
    "software_heritage_identity": {
        "source_record": "examples/sources/source_records/software_heritage_identity_source_v2.json",
        "policy_pack": "examples/connectors/h4_code_source_release/policies/software_heritage_identity_policy_pack_v0.json",
        "coverage": "examples/connectors/h4_code_source_release/coverage/software_heritage_identity_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h4_code_source_release/scorecards/software_heritage_identity_scorecard_preview_v0.json",
    },
    "github_repository": {
        "source_record": "examples/sources/source_records/github_repository_source_v2.json",
        "policy_pack": "examples/connectors/h4_code_source_release/policies/github_repository_policy_pack_v0.json",
        "coverage": "examples/connectors/h4_code_source_release/coverage/github_repository_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h4_code_source_release/scorecards/github_repository_scorecard_preview_v0.json",
    },
    "github_releases": {
        "source_record": "examples/sources/source_records/github_releases_source_v2.json",
        "policy_pack": "examples/connectors/h4_code_source_release/policies/github_releases_policy_pack_v0.json",
        "coverage": "examples/connectors/h4_code_source_release/coverage/github_releases_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h4_code_source_release/scorecards/github_releases_scorecard_preview_v0.json",
    },
    "gitlab_repository": {
        "source_record": "examples/sources/source_records/gitlab_repository_source_v2.json",
        "policy_pack": "examples/connectors/h4_code_source_release/policies/gitlab_repository_policy_pack_v0.json",
        "coverage": "examples/connectors/h4_code_source_release/coverage/gitlab_repository_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h4_code_source_release/scorecards/gitlab_repository_scorecard_preview_v0.json",
    },
    "gitlab_releases": {
        "source_record": "examples/sources/source_records/gitlab_releases_source_v2.json",
        "policy_pack": "examples/connectors/h4_code_source_release/policies/gitlab_releases_policy_pack_v0.json",
        "coverage": "examples/connectors/h4_code_source_release/coverage/gitlab_releases_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h4_code_source_release/scorecards/gitlab_releases_scorecard_preview_v0.json",
    },
    "sourceforge": {
        "source_record": "examples/sources/source_records/sourceforge_source_v2.json",
        "policy_pack": "examples/connectors/h4_code_source_release/policies/sourceforge_policy_pack_v0.json",
        "coverage": "examples/connectors/h4_code_source_release/coverage/sourceforge_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h4_code_source_release/scorecards/sourceforge_scorecard_preview_v0.json",
    },
    "fosshub": {
        "source_record": "examples/sources/source_records/fosshub_source_v2.json",
        "policy_pack": "examples/connectors/h4_code_source_release/policies/fosshub_policy_pack_v0.json",
        "coverage": "examples/connectors/h4_code_source_release/coverage/fosshub_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h4_code_source_release/scorecards/fosshub_scorecard_preview_v0.json",
    },
    "github_archive_program": {
        "source_record": "examples/sources/source_records/github_archive_program_source_v2.json",
        "policy_pack": "examples/connectors/h4_code_source_release/policies/github_archive_program_policy_pack_v0.json",
        "coverage": "examples/connectors/h4_code_source_release/coverage/github_archive_program_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h4_code_source_release/scorecards/github_archive_program_scorecard_preview_v0.json",
    },
    "generic_git_repository": {
        "source_record": "examples/sources/source_records/generic_git_repository_source_v2.json",
        "policy_pack": "examples/connectors/h4_code_source_release/policies/generic_git_repository_policy_pack_v0.json",
        "coverage": "examples/connectors/h4_code_source_release/coverage/generic_git_repository_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h4_code_source_release/scorecards/generic_git_repository_scorecard_preview_v0.json",
    },
    "generic_release_host": {
        "source_record": "examples/sources/source_records/generic_release_host_source_v2.json",
        "policy_pack": "examples/connectors/h4_code_source_release/policies/generic_release_host_policy_pack_v0.json",
        "coverage": "examples/connectors/h4_code_source_release/coverage/generic_release_host_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h4_code_source_release/scorecards/generic_release_host_scorecard_preview_v0.json",
    },
}

INVENTORY_FILES = (
    "control/inventory/source_packs/h4_code_source_release_source_pack_policy.json",
    "control/inventory/source_packs/h4_code_source_release_sources.json",
    "control/inventory/source_packs/h4_code_source_release_connector_families.json",
    "control/inventory/source_packs/h4_source_identity_policy.json",
    "control/inventory/source_packs/h4_release_identity_policy.json",
    "control/inventory/source_packs/h4_source_to_binary_relation_policy.json",
    "control/inventory/source_packs/h4_code_source_release_approval_gates.json",
    "control/inventory/source_packs/h4_code_source_release_output_policy.json",
    "control/inventory/source_packs/h4_code_source_release_truth_policy.json",
    "control/inventory/source_packs/h4_code_source_release_no_live_call_policy.json",
    "control/inventory/source_packs/h4_code_source_release_no_clone_download_policy.json",
)
SOURCE_PACK_EXAMPLES = (
    "examples/packs/source/h4_code_source_release_source_pack_manifest_v0.json",
    "examples/packs/source/h4_code_source_release_policy_pack_v0.json",
)
EXTRA_EXAMPLES = (
    "examples/sources/source_records/code_source_release_policy_blocked_source_v2.json",
    "examples/connectors/h4_code_source_release/policies/code_source_release_policy_blocked_pack_v0.json",
)
DOCS = (
    "docs/reference/H4_CODE_SOURCE_RELEASE_SOURCE_PACKS.md",
    "docs/reference/H4_SOURCE_IDENTITY_POLICY.md",
    "docs/reference/H4_RELEASE_IDENTITY_POLICY.md",
    "docs/reference/H4_SOURCE_TO_BINARY_RELATION_POLICY.md",
    "docs/architecture/H4_CODE_SOURCE_RELEASE_MODEL.md",
    "docs/architecture/CODE_SOURCE_RELEASE_SOURCE_FAMILY_MODEL.md",
    "docs/operations/H4_CODE_SOURCE_RELEASE_POLICY_GATES.md",
    "docs/operations/H4_CODE_SOURCE_RELEASE_NO_LIVE_CALL_POLICY.md",
    "docs/operations/H4_CODE_SOURCE_RELEASE_NO_CLONE_DOWNLOAD_POLICY.md",
    "docs/operations/H4_CODE_SOURCE_RELEASE_FIXTURE_PLAN.md",
)
AUDIT_FILES = (
    "control/audits/h4-bundle-01-code-source-release-policy-packs-v0/README.md",
    "control/audits/h4-bundle-01-code-source-release-policy-packs-v0/h4_bundle_01_report.json",
    "control/audits/h4-bundle-01-code-source-release-policy-packs-v0/h4_source_pack_summary.md",
    "control/audits/h4-bundle-01-code-source-release-policy-packs-v0/h4_source_policy_gate_summary.md",
    "control/audits/h4-bundle-01-code-source-release-policy-packs-v0/h4_connector_family_summary.md",
    "control/audits/h4-bundle-01-code-source-release-policy-packs-v0/h4_source_identity_policy_summary.md",
    "control/audits/h4-bundle-01-code-source-release-policy-packs-v0/h4_release_identity_policy_summary.md",
    "control/audits/h4-bundle-01-code-source-release-policy-packs-v0/h4_source_to_binary_relation_policy_summary.md",
    "control/audits/h4-bundle-01-code-source-release-policy-packs-v0/h4_fixture_plan.md",
    "control/audits/h4-bundle-01-code-source-release-policy-packs-v0/h4_no_live_call_report.md",
    "control/audits/h4-bundle-01-code-source-release-policy-packs-v0/h4_no_clone_download_report.md",
    "control/audits/h4-bundle-01-code-source-release-policy-packs-v0/h4_readiness_for_fixture_runtime.md",
    "control/audits/h4-bundle-01-code-source-release-policy-packs-v0/validation.md",
    "control/audits/h4-bundle-01-code-source-release-policy-packs-v0/generated/sample_h4_source_summary.json",
    "control/audits/h4-bundle-01-code-source-release-policy-packs-v0/generated/sample_h4_source_summary.md",
    "control/audits/h4-bundle-01-code-source-release-policy-packs-v0/generated/sample_h4_option_matrix.json",
)
H4_PYTHON_FILES = (
    "scripts/validate_h4_code_source_release_policy_packs.py",
    "scripts/summarize_h4_code_source_release_sources.py",
)
ALLOWED_CURRENT_OPERATIONS = {
    "inspect_fixture",
    "normalize_fixture_future",
    "record_source_policy",
    "record_source_metadata_preview",
    "record_source_identity_policy",
    "record_release_identity_policy",
    "record_source_to_binary_relation_policy",
    "create_coverage_preview",
    "create_scorecard_preview",
}
FORBIDDEN_TRUE_KEYS = {
    "live_access_enabled",
    "source_sync_enabled",
    "connector_runtime_enabled",
    "approved_live_probe_enabled",
    "repository_clone_enabled",
    "source_archive_download_enabled",
    "release_asset_download_enabled",
    "binary_download_enabled",
    "package_download_enabled",
    "git_command_invocation_enabled",
    "build_tool_invocation_enabled",
    "install_or_execute_enabled",
    "install_execute_enabled",
    "policy_pack_grants_live_access",
    "source_pack_is_truth",
    "source_pack_is_accepted_evidence",
    "source_pack_is_imported_state",
    "capability_grants_permission",
    "coverage_preview_is_exhaustive",
    "coverage_claims_exhaustive_global_coverage",
    "coverage_manifest_is_exhaustive_global_coverage",
    "scorecard_preview_is_production_ready",
    "scorecard_claims_production_readiness",
    "scorecard_auto_approves_future_connectors",
    "production_ready",
    "auto_approves_future_connectors",
    "public_index_mutation_allowed",
    "master_index_mutation_allowed",
    "public_index_mutated",
    "master_index_mutated",
    "mutated_public_index",
    "mutated_master_index",
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "verified_installability_claimed",
    "verified_authenticity_claimed",
    "verified_build_reproducibility_claimed",
    "source_metadata_is_identity_truth",
    "release_metadata_is_release_truth",
    "source_identity_candidate_is_truth",
    "release_identity_candidate_is_truth",
    "source_to_binary_relation_candidate_is_provenance_truth",
    "git_object_id_candidate_is_provenance_truth",
    "swhid_candidate_is_object_truth",
    "release_asset_hash_proves_malware_safety",
    "signature_metadata_proves_authenticity",
    "license_field_proves_rights_clearance",
    "repository_presence_proves_endorsement",
    "archived_presence_proves_completeness",
    "source_archive_asset_proves_build_reproducibility",
    "release_notes_prove_compatibility_or_installability",
    "verified_authenticity",
    "verified_build_reproducibility",
    "accepted_source_truth",
    "accepted_evidence_truth",
    "accepted_candidate_truth",
    "accepted_source_identity",
    "accepted_release_identity",
    "accepted_source_to_binary_relation",
}
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|urllib|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)
SECRET_KEY_RE = re.compile(
    r'"[^"]*(api[_-]?key|api[_-]?token|access[_-]?token|auth[_-]?token|client_secret|password|private_key|cookie)[^"]*"\s*:',
    re.IGNORECASE,
)
REPOSITORY_PAYLOAD_RE = re.compile(
    r'"[^"]*(repository_payload|cloned_repository|repo_bytes|git_pack_bytes|source_archive_bytes|release_asset_payload|binary_payload|installer_bytes|tarball_bytes|zip_bytes|git_command_output|build_tool_output|package_manager_output|executable_payload)[^"]*"\s*:',
    re.IGNORECASE,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print JSON validation result.")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("H4 code/source/release policy pack validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"errors: {len(result['errors'])}", file=stdout)
        for error in result["errors"]:
            print(f"- {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads: dict[str, dict[str, Any]] = {}
    required_paths = list(INVENTORY_FILES + SOURCE_PACK_EXAMPLES + EXTRA_EXAMPLES + DOCS + AUDIT_FILES + H4_PYTHON_FILES)
    for source in EXPECTED_SOURCES.values():
        required_paths.extend(source.values())
    for rel in required_paths:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing required artifact: {rel}")
            continue
        if path.suffix == ".json":
            payload = load_json_object(path, errors)
            if payload is not None:
                payloads[rel] = payload

    known = load_known_values(root, errors)
    add_h4_planned_connector_families(payloads.get("control/inventory/source_packs/h4_code_source_release_connector_families.json", {}), known)
    inventory = payloads.get("control/inventory/source_packs/h4_code_source_release_sources.json", {})
    validate_source_inventory(inventory, errors)
    for source_id, paths in EXPECTED_SOURCES.items():
        errors.extend(f"{source_id} source_record: {item}" for item in validate_source_record(payloads.get(paths["source_record"], {}), source_id, known))
        errors.extend(f"{source_id} policy_pack: {item}" for item in validate_policy_pack(payloads.get(paths["policy_pack"], {}), source_id))
        errors.extend(f"{source_id} coverage: {item}" for item in validate_coverage_preview(payloads.get(paths["coverage"], {}), source_id, known))
        errors.extend(f"{source_id} scorecard: {item}" for item in validate_scorecard_preview(payloads.get(paths["scorecard"], {}), source_id))
    for rel in SOURCE_PACK_EXAMPLES:
        errors.extend(f"{rel}: {item}" for item in validate_source_pack_example(payloads.get(rel, {})))
    errors.extend(validate_source_record(payloads.get("examples/sources/source_records/code_source_release_policy_blocked_source_v2.json", {}), "code_source_release_policy_blocked", known))
    errors.extend(validate_policy_pack(payloads.get("examples/connectors/h4_code_source_release/policies/code_source_release_policy_blocked_pack_v0.json", {}), "code_source_release_policy_blocked"))
    errors.extend(f"source_identity_policy: {item}" for item in validate_source_identity_policy(payloads.get("control/inventory/source_packs/h4_source_identity_policy.json", {})))
    errors.extend(f"release_identity_policy: {item}" for item in validate_release_identity_policy(payloads.get("control/inventory/source_packs/h4_release_identity_policy.json", {})))
    errors.extend(f"source_to_binary_relation_policy: {item}" for item in validate_relation_policy(payloads.get("control/inventory/source_packs/h4_source_to_binary_relation_policy.json", {})))
    validate_audit_report(payloads.get("control/audits/h4-bundle-01-code-source-release-policy-packs-v0/h4_bundle_01_report.json", {}), errors)
    validate_json_text_security(root, errors)
    validate_python_no_network(root, errors)
    validate_no_private_roots(root, errors)
    return {
        "schema_version": "h4_code_source_release_policy_pack_validation.v0",
        "status": "valid" if not errors else "invalid",
        "source_count": len(EXPECTED_SOURCES),
        "errors": errors,
        "network_calls_made": False,
        "model_provider_calls_made": False,
        "repository_clone_enabled": False,
        "downloads_enabled": False,
    }


def load_json_object(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{path.relative_to(REPO_ROOT)} invalid JSON: {exc}")
        return None
    if not isinstance(payload, dict):
        errors.append(f"{path.relative_to(REPO_ROOT)} must contain a JSON object")
        return None
    return payload


def load_known_values(root: Path, errors: list[str]) -> dict[str, set[str]]:
    source_families = load_json_object(root / "control/inventory/sources/source_family_registry.json", errors) or {}
    connector_families = load_json_object(root / "control/inventory/connectors/connector_family_registry.json", errors) or {}
    trust_lanes = load_json_object(root / "control/inventory/sources/source_trust_lane_policy.json", errors) or {}
    index_depths = load_json_object(root / "control/inventory/sources/source_index_depth_registry.json", errors) or {}
    access_modes = load_json_object(root / "control/inventory/sources/source_access_mode_policy.json", errors) or {}
    return {
        "source_families": {str(item.get("family_id")) for item in source_families.get("families", []) if isinstance(item, Mapping)},
        "connector_families": {str(item.get("family_id")) for item in connector_families.get("families", []) if isinstance(item, Mapping)},
        "trust_lanes": {str(item.get("trust_lane")) for item in trust_lanes.get("trust_lanes", []) if isinstance(item, Mapping)},
        "index_depths": {str(item.get("depth_id")) for item in index_depths.get("index_depths", []) if isinstance(item, Mapping)},
        "access_modes": {str(item.get("access_mode")) for item in access_modes.get("access_modes", []) if isinstance(item, Mapping)},
    }


def add_h4_planned_connector_families(mapping_payload: Mapping[str, Any], known: dict[str, set[str]]) -> None:
    planned = mapping_payload.get("planned_connector_family_values", [])
    if isinstance(planned, list):
        known.setdefault("connector_families", set()).update(str(item) for item in planned)
    mappings = mapping_payload.get("source_connector_family_mappings", [])
    if isinstance(mappings, list):
        for item in mappings:
            if isinstance(item, Mapping):
                for key in ("connector_family", "preferred_connector_family", "alternate_connector_family"):
                    if item.get(key):
                        known.setdefault("connector_families", set()).add(str(item.get(key)))


def validate_source_inventory(inventory: Mapping[str, Any], errors: list[str]) -> None:
    if inventory.get("schema_version") != "h4_code_source_release_sources.v0":
        errors.append("H4 source inventory schema_version mismatch")
    sources = inventory.get("sources", [])
    if not isinstance(sources, list):
        errors.append("H4 source inventory sources must be a list")
        return
    ids = [str(item.get("source_id")) for item in sources if isinstance(item, Mapping)]
    if sorted(ids) != sorted(EXPECTED_SOURCES):
        errors.append("H4 source inventory must list exactly the ten H4 sources")
    if len(ids) != len(set(ids)):
        errors.append("H4 source inventory source IDs must be unique")


def validate_source_record(record: Mapping[str, Any], expected_source_id: str, known: Mapping[str, set[str]]) -> list[str]:
    errors: list[str] = []
    if record.get("schema_version") != "source_record.v2":
        errors.append("schema_version must be source_record.v2")
    source_id = record.get("source_id")
    if source_id != expected_source_id:
        errors.append(f"source_id must be {expected_source_id}")
    if source_id not in EXPECTED_SOURCES and source_id != "code_source_release_policy_blocked":
        errors.append(f"unexpected H4 source_id: {source_id}")
    if record.get("source_family") != "code_source_release_host":
        errors.append("source_family must be code_source_release_host")
    _check_known(record.get("source_family"), known.get("source_families", set()), "source_family", errors)
    connector_values = set(record.get("connector_family_refs", []))
    if record.get("connector_family"):
        connector_values.add(str(record.get("connector_family")))
    for connector_family in connector_values:
        _check_known(connector_family, known.get("connector_families", set()), "connector_family", errors)
    _check_known(record.get("trust_lane"), known.get("trust_lanes", set()), "trust_lane", errors)
    for depth_key in ("current_index_depth", "target_index_depth_future", "index_depth_current", "index_depth_target_future"):
        _check_known(record.get(depth_key), known.get("index_depths", set()), depth_key, errors)
    if record.get("current_access_mode") not in {"no_autonomous_access", "committed_fixture_only"}:
        errors.append("current_access_mode must be no_autonomous_access or committed_fixture_only")
    for key in (
        "live_access_enabled",
        "source_sync_enabled",
        "connector_runtime_enabled",
        "approved_live_probe_enabled",
        "repository_clone_enabled",
        "source_archive_download_enabled",
        "release_asset_download_enabled",
        "git_command_invocation_enabled",
        "build_tool_invocation_enabled",
        "install_execute_enabled",
    ):
        if record.get(key) is not False:
            errors.append(f"{key} must be false")
    if not isinstance(record.get("source_identity_support"), Mapping) and record.get("current_status") != "policy_blocked":
        errors.append("source_identity_support is required")
    if not isinstance(record.get("release_identity_support"), Mapping):
        errors.append("release_identity_support is required")
    if not isinstance(record.get("source_to_binary_relation_support"), Mapping):
        errors.append("source_to_binary_relation_support is required")
    errors.extend(detect_forbidden_boundary_claims(record))
    return errors


def validate_policy_pack(pack: Mapping[str, Any], expected_source_id: str | None = None) -> list[str]:
    errors: list[str] = []
    if pack.get("schema_version") != "h4_code_source_release_policy_pack.v0":
        errors.append("schema_version must be h4_code_source_release_policy_pack.v0")
    if expected_source_id and pack.get("source_id") != expected_source_id:
        errors.append(f"source_id must be {expected_source_id}")
    if pack.get("current_status") not in {"policy_pack_only", "policy_blocked"}:
        errors.append("current_status must be policy_pack_only or policy_blocked")
    if pack.get("policy_pack_grants_live_access") is not False:
        errors.append("policy_pack_grants_live_access must be false")
    allowed = set(str(item) for item in pack.get("allowed_current_operations", []))
    extra = sorted(allowed - ALLOWED_CURRENT_OPERATIONS)
    if extra:
        errors.append(f"allowed_current_operations contains forbidden operations: {extra}")
    if pack.get("current_status") != "policy_blocked":
        for key in ("source_identity_mapping_future", "release_identity_mapping_future", "source_to_binary_relation_mapping_future"):
            if not isinstance(pack.get(key), Mapping):
                errors.append(f"{key} must be an object")
    errors.extend(detect_forbidden_boundary_claims(pack))
    return errors


def validate_coverage_preview(record: Mapping[str, Any], expected_source_id: str | None = None, known: Mapping[str, set[str]] | None = None) -> list[str]:
    errors: list[str] = []
    known = known or {}
    if record.get("schema_version") != "source_coverage_ledger.v0":
        errors.append("schema_version must be source_coverage_ledger.v0")
    if expected_source_id and record.get("source_id") != expected_source_id:
        errors.append(f"source_id must be {expected_source_id}")
    if record.get("source_family") != "code_source_release_host":
        errors.append("source_family must be code_source_release_host")
    _check_known(record.get("source_family"), known.get("source_families", set()), "source_family", errors)
    if record.get("coverage_basis") not in {"example_only", "policy_pack_only"}:
        errors.append("coverage_basis must be example_only or policy_pack_only")
    if record.get("coverage_depth_current") not in {"D0_source_known", "D1_catalog_indexed"}:
        errors.append("coverage_depth_current must be D0 or D1 for H4-BUNDLE-01")
    for key in ("records_seen", "repositories_cloned", "source_archives_downloaded", "release_assets_downloaded", "git_commands_invoked", "build_tools_invoked"):
        if record.get(key) not in (0, None):
            errors.append(f"{key} must be 0")
    if record.get("live_access_enabled") is not False:
        errors.append("live_access_enabled must be false")
    errors.extend(detect_forbidden_boundary_claims(record))
    return errors


def validate_scorecard_preview(scorecard: Mapping[str, Any], expected_source_id: str | None = None) -> list[str]:
    errors: list[str] = []
    if scorecard.get("schema_version") != "connector_scorecard.v0":
        errors.append("schema_version must be connector_scorecard.v0")
    if expected_source_id and scorecard.get("source_id") != expected_source_id:
        errors.append(f"source_id must be {expected_source_id}")
    required_statuses = {
        "fixture_replay_status": "not_started",
        "policy_evaluation_status": "planned",
        "live_probe_envelope_status": "not_approved",
        "source_cache_mapping_status": "planned",
        "evidence_mapping_status": "planned",
        "source_identity_mapping_status": "planned",
        "release_identity_mapping_status": "planned",
        "source_to_binary_relation_mapping_status": "planned",
        "quality_delta_status": "not_started",
        "repository_clone_status": "forbidden_current",
        "source_archive_download_status": "forbidden_current",
        "release_asset_download_status": "forbidden_current",
        "git_command_invocation_status": "forbidden_current",
        "build_tool_invocation_status": "forbidden_current",
    }
    for key, expected in required_statuses.items():
        if scorecard.get(key) != expected:
            errors.append(f"{key} must be {expected}")
    if scorecard.get("production_ready") is not False:
        errors.append("production_ready must be false")
    if scorecard.get("auto_approves_future_connectors") is not False:
        errors.append("auto_approves_future_connectors must be false")
    errors.extend(detect_forbidden_boundary_claims(scorecard))
    return errors


def validate_source_pack_example(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    schema = payload.get("schema_version")
    if schema not in {"source_pack_manifest.v0", "h4_code_source_release_policy_pack.v0"}:
        errors.append("unexpected source pack example schema_version")
    source_ids = set(str(item) for item in payload.get("source_ids", []))
    if source_ids and source_ids != set(EXPECTED_SOURCES):
        errors.append("aggregate policy pack must reference all ten H4 source IDs")
    if schema == "source_pack_manifest.v0":
        if payload.get("pack_status") != "draft_only":
            errors.append("source pack manifest must remain draft_only")
        refs = payload.get("source_records", [])
        if isinstance(refs, list) and len(refs) != len(EXPECTED_SOURCES):
            errors.append("source pack manifest must reference all ten source records")
    errors.extend(detect_forbidden_boundary_claims(payload))
    return errors


def validate_source_identity_policy(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    boundary = payload.get("identity_boundary", {})
    for key in (
        "source_identity_candidate_is_not_accepted_source_identity_truth",
        "git_object_id_candidate_is_not_accepted_provenance_truth_without_review",
        "swhid_candidate_is_not_accepted_object_truth_without_review",
        "repository_url_does_not_prove_official_status",
        "license_field_does_not_prove_rights_clearance",
        "repository_presence_does_not_prove_endorsement",
        "archived_presence_does_not_prove_completeness",
    ):
        if not isinstance(boundary, Mapping) or boundary.get(key) is not True:
            errors.append(f"identity_boundary.{key} must be true")
    errors.extend(detect_forbidden_boundary_claims(payload))
    return errors


def validate_release_identity_policy(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    boundary = payload.get("release_boundary", {})
    for key in (
        "release_identity_candidate_is_not_accepted_release_truth",
        "release_asset_metadata_does_not_grant_download_permission",
        "release_asset_hash_does_not_prove_malware_safety",
        "signature_metadata_does_not_prove_authenticity_without_future_verification",
        "source_archive_asset_does_not_prove_build_reproducibility",
        "release_notes_do_not_prove_compatibility_or_installability",
    ):
        if not isinstance(boundary, Mapping) or boundary.get(key) is not True:
            errors.append(f"release_boundary.{key} must be true")
    errors.extend(detect_forbidden_boundary_claims(payload))
    return errors


def validate_relation_policy(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    boundary = payload.get("relation_boundary", {})
    for key in (
        "source_to_binary_relation_candidate_is_not_accepted_provenance",
        "tag_release_match_does_not_prove_build_relation",
        "asset_presence_does_not_prove_source_relationship",
        "checksums_do_not_prove_malware_safety",
        "sbom_signature_metadata_requires_future_verification_before_trust_claims",
    ):
        if not isinstance(boundary, Mapping) or boundary.get(key) is not True:
            errors.append(f"relation_boundary.{key} must be true")
    errors.extend(detect_forbidden_boundary_claims(payload))
    return errors


def validate_audit_report(report: Mapping[str, Any], errors: list[str]) -> None:
    if not report:
        return
    if report.get("schema_version") != "h4_bundle_01_report.v0":
        errors.append("h4 bundle 01 report schema_version mismatch")
    if sorted(report.get("sources", [])) != sorted(EXPECTED_SOURCES):
        errors.append("h4 bundle 01 report must list all ten H4 sources")
    wave_scope = report.get("wave_scope", {})
    if isinstance(wave_scope, Mapping):
        for key in ("live_access_enabled", "source_sync_enabled", "connector_runtime_enabled", "repository_clone_enabled", "source_archive_download_enabled", "release_asset_download_enabled", "git_command_invocation_enabled", "build_tool_invocation_enabled", "install_execute_enabled", "network_calls_made"):
            if wave_scope.get(key) is not False:
                errors.append(f"h4 bundle 01 report wave_scope.{key} must be false")
    errors.extend(f"h4_bundle_01_report: {item}" for item in detect_forbidden_boundary_claims(report))


def detect_forbidden_boundary_claims(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            next_path = f"{path}.{key_text}"
            if key_text in FORBIDDEN_TRUE_KEYS and item is True:
                errors.append(f"{next_path} must not be true")
            errors.extend(detect_forbidden_boundary_claims(item, next_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            errors.extend(detect_forbidden_boundary_claims(item, f"{path}[{index}]"))
    return errors


def validate_json_text_security(root: Path, errors: list[str]) -> None:
    rels = list(INVENTORY_FILES + SOURCE_PACK_EXAMPLES + EXTRA_EXAMPLES)
    for source in EXPECTED_SOURCES.values():
        rels.extend(source.values())
    for rel in rels:
        path = root / rel
        if not path.is_file() or path.suffix != ".json":
            continue
        text = path.read_text(encoding="utf-8")
        if SECRET_KEY_RE.search(text):
            errors.append(f"{rel}: credential/cookie/token-like key is not allowed")
        if REPOSITORY_PAYLOAD_RE.search(text):
            errors.append(f"{rel}: repository or release payload-like key is not allowed")


def validate_python_no_network(root: Path, errors: list[str]) -> None:
    for rel in H4_PYTHON_FILES:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing H4 Python file: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        match = BANNED_IMPORT_RE.search(text)
        if match:
            errors.append(f"{rel}: forbidden network/model/browser import {match.group(1)}")
        if ("url" + "open(") in text or (".Re" + "quest(") in text:
            errors.append(f"{rel}: forbidden live-call primitive")


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
        if (root / rel).exists():
            errors.append(f"local private-state root must not exist: {rel}")


def _check_known(value: Any, known_values: set[str], label: str, errors: list[str]) -> None:
    if not value:
        errors.append(f"{label} is required")
        return
    if known_values and str(value) not in known_values:
        errors.append(f"unknown {label}: {value}")


if __name__ == "__main__":
    raise SystemExit(main())

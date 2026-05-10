#!/usr/bin/env python3
"""Validate H5-BUNDLE-01 vendor/update/driver/firmware policy packs offline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_FAMILY = "vendor_update_driver_firmware"
EXPECTED_SOURCES = {
    "microsoft_download_center": {
        "source_record": "examples/sources/source_records/microsoft_download_center_source_v2.json",
        "policy_pack": "examples/connectors/h5_vendor_update_driver/policies/microsoft_download_center_policy_pack_v0.json",
        "coverage": "examples/connectors/h5_vendor_update_driver/coverage/microsoft_download_center_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h5_vendor_update_driver/scorecards/microsoft_download_center_scorecard_preview_v0.json",
    },
    "microsoft_update_catalog": {
        "source_record": "examples/sources/source_records/microsoft_update_catalog_source_v2.json",
        "policy_pack": "examples/connectors/h5_vendor_update_driver/policies/microsoft_update_catalog_policy_pack_v0.json",
        "coverage": "examples/connectors/h5_vendor_update_driver/coverage/microsoft_update_catalog_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h5_vendor_update_driver/scorecards/microsoft_update_catalog_scorecard_preview_v0.json",
    },
    "microsoft_runtime_redistributables": {
        "source_record": "examples/sources/source_records/microsoft_runtime_redistributables_source_v2.json",
        "policy_pack": "examples/connectors/h5_vendor_update_driver/policies/microsoft_runtime_redistributables_policy_pack_v0.json",
        "coverage": "examples/connectors/h5_vendor_update_driver/coverage/microsoft_runtime_redistributables_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h5_vendor_update_driver/scorecards/microsoft_runtime_redistributables_scorecard_preview_v0.json",
    },
    "apple_software_downloads": {
        "source_record": "examples/sources/source_records/apple_software_downloads_source_v2.json",
        "policy_pack": "examples/connectors/h5_vendor_update_driver/policies/apple_software_downloads_policy_pack_v0.json",
        "coverage": "examples/connectors/h5_vendor_update_driver/coverage/apple_software_downloads_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h5_vendor_update_driver/scorecards/apple_software_downloads_scorecard_preview_v0.json",
    },
    "apple_software_update_catalog": {
        "source_record": "examples/sources/source_records/apple_software_update_catalog_source_v2.json",
        "policy_pack": "examples/connectors/h5_vendor_update_driver/policies/apple_software_update_catalog_policy_pack_v0.json",
        "coverage": "examples/connectors/h5_vendor_update_driver/coverage/apple_software_update_catalog_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h5_vendor_update_driver/scorecards/apple_software_update_catalog_scorecard_preview_v0.json",
    },
    "nvidia_driver_downloads": {
        "source_record": "examples/sources/source_records/nvidia_driver_downloads_source_v2.json",
        "policy_pack": "examples/connectors/h5_vendor_update_driver/policies/nvidia_driver_downloads_policy_pack_v0.json",
        "coverage": "examples/connectors/h5_vendor_update_driver/coverage/nvidia_driver_downloads_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h5_vendor_update_driver/scorecards/nvidia_driver_downloads_scorecard_preview_v0.json",
    },
    "amd_driver_downloads": {
        "source_record": "examples/sources/source_records/amd_driver_downloads_source_v2.json",
        "policy_pack": "examples/connectors/h5_vendor_update_driver/policies/amd_driver_downloads_policy_pack_v0.json",
        "coverage": "examples/connectors/h5_vendor_update_driver/coverage/amd_driver_downloads_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h5_vendor_update_driver/scorecards/amd_driver_downloads_scorecard_preview_v0.json",
    },
    "intel_driver_support": {
        "source_record": "examples/sources/source_records/intel_driver_support_source_v2.json",
        "policy_pack": "examples/connectors/h5_vendor_update_driver/policies/intel_driver_support_policy_pack_v0.json",
        "coverage": "examples/connectors/h5_vendor_update_driver/coverage/intel_driver_support_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h5_vendor_update_driver/scorecards/intel_driver_support_scorecard_preview_v0.json",
    },
    "dell_support_downloads": {
        "source_record": "examples/sources/source_records/dell_support_downloads_source_v2.json",
        "policy_pack": "examples/connectors/h5_vendor_update_driver/policies/dell_support_downloads_policy_pack_v0.json",
        "coverage": "examples/connectors/h5_vendor_update_driver/coverage/dell_support_downloads_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h5_vendor_update_driver/scorecards/dell_support_downloads_scorecard_preview_v0.json",
    },
    "hp_support_downloads": {
        "source_record": "examples/sources/source_records/hp_support_downloads_source_v2.json",
        "policy_pack": "examples/connectors/h5_vendor_update_driver/policies/hp_support_downloads_policy_pack_v0.json",
        "coverage": "examples/connectors/h5_vendor_update_driver/coverage/hp_support_downloads_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h5_vendor_update_driver/scorecards/hp_support_downloads_scorecard_preview_v0.json",
    },
    "lenovo_support_downloads": {
        "source_record": "examples/sources/source_records/lenovo_support_downloads_source_v2.json",
        "policy_pack": "examples/connectors/h5_vendor_update_driver/policies/lenovo_support_downloads_policy_pack_v0.json",
        "coverage": "examples/connectors/h5_vendor_update_driver/coverage/lenovo_support_downloads_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h5_vendor_update_driver/scorecards/lenovo_support_downloads_scorecard_preview_v0.json",
    },
    "asus_support_downloads": {
        "source_record": "examples/sources/source_records/asus_support_downloads_source_v2.json",
        "policy_pack": "examples/connectors/h5_vendor_update_driver/policies/asus_support_downloads_policy_pack_v0.json",
        "coverage": "examples/connectors/h5_vendor_update_driver/coverage/asus_support_downloads_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h5_vendor_update_driver/scorecards/asus_support_downloads_scorecard_preview_v0.json",
    },
    "acer_support_downloads": {
        "source_record": "examples/sources/source_records/acer_support_downloads_source_v2.json",
        "policy_pack": "examples/connectors/h5_vendor_update_driver/policies/acer_support_downloads_policy_pack_v0.json",
        "coverage": "examples/connectors/h5_vendor_update_driver/coverage/acer_support_downloads_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h5_vendor_update_driver/scorecards/acer_support_downloads_scorecard_preview_v0.json",
    },
    "generic_vendor_driver_firmware": {
        "source_record": "examples/sources/source_records/generic_vendor_driver_firmware_source_v2.json",
        "policy_pack": "examples/connectors/h5_vendor_update_driver/policies/generic_vendor_driver_firmware_policy_pack_v0.json",
        "coverage": "examples/connectors/h5_vendor_update_driver/coverage/generic_vendor_driver_firmware_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h5_vendor_update_driver/scorecards/generic_vendor_driver_firmware_scorecard_preview_v0.json",
    },
    "generic_runtime_redistributable": {
        "source_record": "examples/sources/source_records/generic_runtime_redistributable_source_v2.json",
        "policy_pack": "examples/connectors/h5_vendor_update_driver/policies/generic_runtime_redistributable_policy_pack_v0.json",
        "coverage": "examples/connectors/h5_vendor_update_driver/coverage/generic_runtime_redistributable_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h5_vendor_update_driver/scorecards/generic_runtime_redistributable_scorecard_preview_v0.json",
    },
}
INVENTORY_FILES = (
    "control/inventory/source_packs/h5_vendor_update_driver_source_pack_policy.json",
    "control/inventory/source_packs/h5_vendor_update_driver_sources.json",
    "control/inventory/source_packs/h5_vendor_update_driver_connector_families.json",
    "control/inventory/source_packs/h5_vendor_identity_policy.json",
    "control/inventory/source_packs/h5_driver_device_compatibility_policy.json",
    "control/inventory/source_packs/h5_firmware_update_policy.json",
    "control/inventory/source_packs/h5_runtime_redistributable_policy.json",
    "control/inventory/source_packs/h5_vendor_update_driver_approval_gates.json",
    "control/inventory/source_packs/h5_vendor_update_driver_output_policy.json",
    "control/inventory/source_packs/h5_vendor_update_driver_truth_policy.json",
    "control/inventory/source_packs/h5_vendor_update_driver_no_live_call_policy.json",
    "control/inventory/source_packs/h5_vendor_update_driver_no_download_execute_policy.json",
)
SOURCE_PACK_EXAMPLES = (
    "examples/source_packs/h5_vendor_update_driver_source_pack_manifest_v0.json",
    "examples/source_packs/h5_vendor_update_driver_policy_pack_v0.json",
)
EXTRA_EXAMPLES = (
    "examples/sources/source_records/vendor_update_driver_policy_blocked_source_v2.json",
    "examples/connectors/h5_vendor_update_driver/policies/vendor_update_driver_policy_blocked_pack_v0.json",
)
DOCS = (
    "docs/reference/H5_VENDOR_UPDATE_DRIVER_SOURCE_PACKS.md",
    "docs/reference/H5_VENDOR_IDENTITY_POLICY.md",
    "docs/reference/H5_DRIVER_DEVICE_COMPATIBILITY_POLICY.md",
    "docs/reference/H5_FIRMWARE_UPDATE_POLICY.md",
    "docs/reference/H5_RUNTIME_REDISTRIBUTABLE_POLICY.md",
    "docs/architecture/H5_VENDOR_UPDATE_DRIVER_MODEL.md",
    "docs/architecture/VENDOR_UPDATE_DRIVER_SOURCE_FAMILY_MODEL.md",
    "docs/operations/H5_VENDOR_UPDATE_DRIVER_POLICY_GATES.md",
    "docs/operations/H5_VENDOR_UPDATE_DRIVER_NO_LIVE_CALL_POLICY.md",
    "docs/operations/H5_VENDOR_UPDATE_DRIVER_NO_DOWNLOAD_EXECUTE_POLICY.md",
    "docs/operations/H5_VENDOR_UPDATE_DRIVER_FIXTURE_PLAN.md",
)
AUDIT_FILES = (
    "control/audits/h5-bundle-01-vendor-update-driver-policy-packs-v0/README.md",
    "control/audits/h5-bundle-01-vendor-update-driver-policy-packs-v0/h5_bundle_01_report.json",
    "control/audits/h5-bundle-01-vendor-update-driver-policy-packs-v0/h5_source_pack_summary.md",
    "control/audits/h5-bundle-01-vendor-update-driver-policy-packs-v0/h5_source_policy_gate_summary.md",
    "control/audits/h5-bundle-01-vendor-update-driver-policy-packs-v0/h5_connector_family_summary.md",
    "control/audits/h5-bundle-01-vendor-update-driver-policy-packs-v0/h5_vendor_identity_policy_summary.md",
    "control/audits/h5-bundle-01-vendor-update-driver-policy-packs-v0/h5_driver_device_compatibility_policy_summary.md",
    "control/audits/h5-bundle-01-vendor-update-driver-policy-packs-v0/h5_firmware_update_policy_summary.md",
    "control/audits/h5-bundle-01-vendor-update-driver-policy-packs-v0/h5_runtime_redistributable_policy_summary.md",
    "control/audits/h5-bundle-01-vendor-update-driver-policy-packs-v0/h5_fixture_plan.md",
    "control/audits/h5-bundle-01-vendor-update-driver-policy-packs-v0/h5_no_live_call_report.md",
    "control/audits/h5-bundle-01-vendor-update-driver-policy-packs-v0/h5_no_download_execute_report.md",
    "control/audits/h5-bundle-01-vendor-update-driver-policy-packs-v0/h5_readiness_for_fixture_runtime.md",
    "control/audits/h5-bundle-01-vendor-update-driver-policy-packs-v0/validation.md",
    "control/audits/h5-bundle-01-vendor-update-driver-policy-packs-v0/generated/sample_h5_source_summary.json",
    "control/audits/h5-bundle-01-vendor-update-driver-policy-packs-v0/generated/sample_h5_source_summary.md",
    "control/audits/h5-bundle-01-vendor-update-driver-policy-packs-v0/generated/sample_h5_option_matrix.json",
)
H5_PYTHON_FILES = (
    "scripts/validate_h5_vendor_update_driver_policy_packs.py",
    "scripts/summarize_h5_vendor_update_driver_sources.py",
)
ALLOWED_CURRENT_OPERATIONS = {
    "inspect_fixture",
    "normalize_fixture_future",
    "record_source_policy",
    "record_source_metadata_preview",
    "record_vendor_identity_policy",
    "record_driver_device_compatibility_policy",
    "record_firmware_update_policy",
    "record_runtime_redistributable_policy",
    "create_coverage_preview",
    "create_scorecard_preview",
}
FORBIDDEN_TRUE_KEYS = {
    "live_access_enabled",
    "source_sync_enabled",
    "connector_runtime_enabled",
    "approved_live_probe_enabled",
    "vendor_catalog_fetch_enabled",
    "driver_download_enabled",
    "firmware_download_enabled",
    "runtime_download_enabled",
    "installer_download_enabled",
    "update_package_download_enabled",
    "signature_fetch_enabled",
    "checksum_fetch_enabled",
    "vendor_tool_invocation_enabled",
    "package_manager_invocation_enabled",
    "firmware_flash_enabled",
    "install_or_execute_enabled",
    "install_execute_enabled",
    "policy_pack_grants_live_access",
    "source_pack_is_truth",
    "source_pack_is_accepted_evidence",
    "source_pack_is_imported_state",
    "capability_grants_permission",
    "coverage_preview_is_exhaustive",
    "coverage_manifest_is_exhaustive_global_coverage",
    "scorecard_preview_is_production_ready",
    "scorecard_claims_production_readiness",
    "scorecard_auto_approves_future_connectors",
    "production_ready",
    "auto_approves_future_connectors",
    "vendor_metadata_is_official_truth",
    "vendor_identity_candidate_is_truth",
    "driver_metadata_is_driver_identity_truth",
    "driver_identity_candidate_is_truth",
    "firmware_metadata_is_firmware_identity_truth",
    "firmware_identity_candidate_is_truth",
    "runtime_metadata_is_runtime_identity_truth",
    "runtime_identity_candidate_is_truth",
    "compatibility_metadata_is_compatibility_truth",
    "compatibility_candidate_is_truth",
    "authenticity_candidate_is_truth",
    "safety_candidate_is_truth",
    "hash_metadata_proves_malware_safety",
    "signature_metadata_proves_authenticity",
    "license_field_proves_rights_clearance",
    "vendor_presence_proves_endorsement",
    "vendor_presence_proves_official_status",
    "device_id_match_proves_safe_installability",
    "os_version_match_proves_runtime_correctness",
    "firmware_metadata_proves_device_compatibility",
    "installer_metadata_grants_execution_permission",
    "flashing_tool_metadata_grants_execution_permission",
    "public_index_mutation_allowed",
    "master_index_mutation_allowed",
    "public_index_mutated",
    "master_index_mutated",
    "mutated_public_index",
    "mutated_master_index",
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "verified_installability_claimed",
    "verified_compatibility_claimed",
    "verified_authenticity_claimed",
    "accepted_source_truth",
    "accepted_evidence_truth",
    "accepted_candidate_truth",
    "accepted_public_record",
    "accepted_vendor_truth",
    "accepted_driver_identity",
    "accepted_firmware_identity",
    "accepted_runtime_identity",
    "accepted_compatibility_truth",
    "accepted_authenticity_truth",
    "accepted_safety_truth",
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
PAYLOAD_RE = re.compile(
    r'"[^"]*(downloaded_payload|driver_payload|firmware_image|bios_image|uefi_image|installer_bytes|binary_payload|cab_bytes|msi_bytes|msu_bytes|exe_bytes|dmg_bytes|pkg_bytes|vendor_tool_output|package_manager_output|executable_payload)[^"]*"\s*:',
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
        print("H5 vendor/update/driver policy pack validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"errors: {len(result['errors'])}", file=stdout)
        for error in result["errors"]:
            print(f"- {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads: dict[str, dict[str, Any]] = {}
    required_paths = list(INVENTORY_FILES + SOURCE_PACK_EXAMPLES + EXTRA_EXAMPLES + DOCS + AUDIT_FILES + H5_PYTHON_FILES)
    for source_paths in EXPECTED_SOURCES.values():
        required_paths.extend(source_paths.values())
    for rel in required_paths:
        path = root / rel
        if not path.exists():
            errors.append(f"missing required path: {rel}")
            continue
        if path.suffix == ".json":
            try:
                payload = _load_json(path)
            except (OSError, json.JSONDecodeError, ValueError) as exc:
                errors.append(f"{rel}: invalid JSON: {exc}")
                continue
            payloads[rel] = payload
            _scan_json_payload(rel, payload, errors)
    known = _load_known_values(root, errors)
    inventory = payloads.get("control/inventory/source_packs/h5_vendor_update_driver_sources.json", {})
    sources = inventory.get("sources", [])
    if not isinstance(sources, list):
        errors.append("h5 source inventory must contain sources list")
        sources = []
    source_ids = [item.get("source_id") for item in sources if isinstance(item, Mapping)]
    if len(sources) != 15:
        errors.append(f"h5 source inventory expected 15 sources, got {len(sources)}")
    if sorted(source_ids) != sorted(EXPECTED_SOURCES):
        errors.append("h5 source inventory source IDs do not match expected set")
    if len(source_ids) != len(set(source_ids)):
        errors.append("h5 source inventory source IDs must be unique")

    for source_id, paths in EXPECTED_SOURCES.items():
        record = payloads.get(paths["source_record"], {})
        errors.extend(validate_source_record(source_id, record, known))
        pack = payloads.get(paths["policy_pack"], {})
        errors.extend(validate_policy_pack(source_id, pack))
        coverage = payloads.get(paths["coverage"], {})
        errors.extend(validate_coverage_preview(source_id, coverage))
        scorecard = payloads.get(paths["scorecard"], {})
        errors.extend(validate_scorecard_preview(source_id, scorecard))

    blocked_record = payloads.get("examples/sources/source_records/vendor_update_driver_policy_blocked_source_v2.json", {})
    if blocked_record:
        errors.extend(validate_source_record("vendor_update_driver_policy_blocked", blocked_record, known, allow_blocked=True))
    blocked_pack = payloads.get("examples/connectors/h5_vendor_update_driver/policies/vendor_update_driver_policy_blocked_pack_v0.json", {})
    if blocked_pack:
        errors.extend(validate_policy_pack("vendor_update_driver_policy_blocked", blocked_pack, allow_blocked=True))

    errors.extend(validate_policies(payloads))
    errors.extend(validate_registry_entries(root))
    errors.extend(scan_python_files(root))
    errors.extend(scan_for_private_roots(root))
    return {
        "schema_version": "h5_vendor_update_driver_policy_pack_validation.v0",
        "status": "valid" if not errors else "invalid",
        "source_count": len(EXPECTED_SOURCES),
        "errors": errors,
    }


def validate_source_record(source_id: str, record: Mapping[str, Any], known: Mapping[str, set[str]], allow_blocked: bool = False) -> list[str]:
    errors: list[str] = []
    prefix = f"source_record {source_id}"
    if record.get("schema_version") != "source_record.v2":
        errors.append(f"{prefix}: schema_version must be source_record.v2")
    if record.get("source_id") != source_id:
        errors.append(f"{prefix}: source_id mismatch")
    if record.get("source_family") != SOURCE_FAMILY:
        errors.append(f"{prefix}: source_family must be {SOURCE_FAMILY}")
    if SOURCE_FAMILY not in known.get("source_families", set()):
        errors.append(f"{prefix}: source family {SOURCE_FAMILY} is not registered")
    if record.get("connector_family") not in known.get("connector_families", set()):
        errors.append(f"{prefix}: connector_family is not registered")
    if record.get("trust_lane") not in known.get("trust_lanes", set()):
        errors.append(f"{prefix}: unknown trust_lane {record.get('trust_lane')}")
    if record.get("current_access_mode") not in known.get("access_modes", set()):
        errors.append(f"{prefix}: unknown current_access_mode {record.get('current_access_mode')}")
    if record.get("current_index_depth") not in known.get("index_depths", set()):
        errors.append(f"{prefix}: unknown current_index_depth {record.get('current_index_depth')}")
    if record.get("target_index_depth_future") not in known.get("index_depths", set()):
        errors.append(f"{prefix}: unknown target_index_depth_future {record.get('target_index_depth_future')}")
    if record.get("current_status") not in {"policy_pack_only", "policy_blocked"}:
        errors.append(f"{prefix}: current_status must be policy_pack_only or policy_blocked")
    if allow_blocked and record.get("current_status") != "policy_blocked":
        errors.append(f"{prefix}: blocked record must be policy_blocked")
    for key in (
        "vendor_identity_support",
        "driver_device_compatibility_support",
        "firmware_update_support",
        "runtime_redistributable_support",
        "signature_or_hash_metadata_support",
    ):
        if not isinstance(record.get(key), Mapping):
            errors.append(f"{prefix}: missing {key}")
    for key in (
        "fixture_required",
        "live_probe_required_future",
        "scorecard_required",
        "coverage_required",
    ):
        if record.get(key) is not True:
            errors.append(f"{prefix}: {key} must be true")
    errors.extend(_detect_forbidden_true_values(record, prefix))
    errors.extend(_detect_boundary_overclaim(record, prefix))
    return errors


def validate_policy_pack(source_id: str, pack: Mapping[str, Any], allow_blocked: bool = False) -> list[str]:
    errors: list[str] = []
    prefix = f"policy_pack {source_id}"
    if pack.get("schema_version") != "h5_vendor_update_driver_policy_pack.v0":
        errors.append(f"{prefix}: schema_version mismatch")
    if pack.get("source_id") != source_id:
        errors.append(f"{prefix}: source_id mismatch")
    if pack.get("source_family") != SOURCE_FAMILY:
        errors.append(f"{prefix}: source_family must be {SOURCE_FAMILY}")
    if pack.get("current_status") not in {"policy_pack_only", "policy_blocked"}:
        errors.append(f"{prefix}: current_status must be policy_pack_only or policy_blocked")
    if allow_blocked and pack.get("current_status") != "policy_blocked":
        errors.append(f"{prefix}: blocked pack must be policy_blocked")
    allowed_ops = pack.get("allowed_current_operations")
    if not isinstance(allowed_ops, list):
        errors.append(f"{prefix}: allowed_current_operations must be a list")
    elif not set(allowed_ops).issubset(ALLOWED_CURRENT_OPERATIONS):
        errors.append(f"{prefix}: allowed_current_operations contains unapproved operation")
    for key in (
        "endpoint_or_metadata_classes_planned",
        "endpoint_or_metadata_classes_forbidden_current",
        "fixture_requirements",
        "live_probe_requirements_future",
        "vendor_identity_mapping_future",
        "driver_device_compatibility_mapping_future",
        "firmware_update_mapping_future",
        "runtime_redistributable_mapping_future",
        "source_cache_mapping_future",
        "evidence_mapping_future",
        "review_requirements",
        "scorecard_requirements",
        "coverage_requirements",
        "no_goals",
    ):
        if key not in pack:
            errors.append(f"{prefix}: missing {key}")
    errors.extend(_detect_forbidden_true_values(pack, prefix))
    errors.extend(_detect_boundary_overclaim(pack, prefix))
    return errors


def validate_coverage_preview(source_id: str, coverage: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    prefix = f"coverage {source_id}"
    if coverage.get("schema_version") != "source_coverage_ledger.v0":
        errors.append(f"{prefix}: schema_version mismatch")
    if coverage.get("source_id") != source_id:
        errors.append(f"{prefix}: source_id mismatch")
    if coverage.get("source_family") != SOURCE_FAMILY:
        errors.append(f"{prefix}: source_family must be {SOURCE_FAMILY}")
    if coverage.get("coverage_basis") not in {"policy_pack_only", "example_only"}:
        errors.append(f"{prefix}: coverage_basis must be policy_pack_only or example_only")
    if coverage.get("coverage_depth_current") not in {"D0_source_known", "D1_catalog_indexed"}:
        errors.append(f"{prefix}: coverage_depth_current must be D0 or D1 preview")
    for key in (
        "records_seen",
        "vendor_catalogs_fetched",
        "downloads_performed",
        "vendor_tools_invoked",
        "firmware_flashes_performed",
        "installers_executed",
    ):
        if coverage.get(key) != 0:
            errors.append(f"{prefix}: {key} must be 0")
    errors.extend(_detect_forbidden_true_values(coverage, prefix))
    errors.extend(_detect_boundary_overclaim(coverage, prefix))
    return errors


def validate_scorecard_preview(source_id: str, scorecard: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    prefix = f"scorecard {source_id}"
    if scorecard.get("schema_version") != "connector_scorecard.v0":
        errors.append(f"{prefix}: schema_version mismatch")
    if scorecard.get("source_id") != source_id:
        errors.append(f"{prefix}: source_id mismatch")
    expected_statuses = {
        "fixture_replay_status": "not_started",
        "policy_evaluation_status": "planned",
        "live_probe_envelope_status": "not_approved",
        "source_cache_mapping_status": "planned",
        "evidence_mapping_status": "planned",
        "vendor_identity_mapping_status": "planned",
        "driver_device_compatibility_mapping_status": "planned",
        "firmware_update_mapping_status": "planned",
        "runtime_redistributable_mapping_status": "planned",
        "quality_delta_status": "not_started",
        "vendor_catalog_fetch_status": "forbidden_current",
        "driver_download_status": "forbidden_current",
        "firmware_download_status": "forbidden_current",
        "runtime_download_status": "forbidden_current",
        "installer_execution_status": "forbidden_current",
        "firmware_flash_status": "forbidden_current",
    }
    for key, expected in expected_statuses.items():
        if scorecard.get(key) != expected:
            errors.append(f"{prefix}: {key} must be {expected}")
    errors.extend(_detect_forbidden_true_values(scorecard, prefix))
    errors.extend(_detect_boundary_overclaim(scorecard, prefix))
    return errors


def validate_policies(payloads: Mapping[str, Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    source_policy = payloads.get("control/inventory/source_packs/h5_vendor_update_driver_source_pack_policy.json", {})
    for key in (
        "live_access_enabled",
        "source_sync_enabled",
        "connector_runtime_enabled",
        "approved_live_probe_enabled",
        "vendor_catalog_fetch_enabled",
        "driver_download_enabled",
        "firmware_download_enabled",
        "runtime_download_enabled",
        "installer_download_enabled",
        "update_package_download_enabled",
        "signature_fetch_enabled",
        "checksum_fetch_enabled",
        "vendor_tool_invocation_enabled",
        "package_manager_invocation_enabled",
        "firmware_flash_enabled",
        "install_or_execute_enabled",
        "source_pack_import_enabled",
    ):
        if source_policy.get(key) is not False:
            errors.append(f"source policy: {key} must be false")
    for key in (
        "source_pack_export_only",
        "review_required_before_live_access",
        "review_required_before_source_cache_write",
        "review_required_before_evidence_acceptance",
        "review_required_before_public_index_use",
        "review_required_before_master_index",
    ):
        if source_policy.get(key) is not True:
            errors.append(f"source policy: {key} must be true")

    identity = payloads.get("control/inventory/source_packs/h5_vendor_identity_policy.json", {})
    errors.extend(_require_true(identity.get("identity_boundary", {}), (
        "vendor_identity_candidate_is_not_accepted_vendor_truth",
        "vendor_domain_or_source_record_does_not_prove_official_status_without_review",
        "product_support_page_metadata_does_not_prove_compatibility",
        "release_date_does_not_prove_current_availability",
        "hash_signature_metadata_is_not_verified_authenticity",
        "vendor_presence_does_not_prove_safety_or_endorsement",
    ), "vendor identity policy"))
    compatibility = payloads.get("control/inventory/source_packs/h5_driver_device_compatibility_policy.json", {})
    errors.extend(_require_true(compatibility.get("compatibility_boundary", {}), (
        "driver_compatibility_candidate_is_not_verified_compatibility",
        "device_id_match_does_not_prove_safe_installability",
        "os_version_match_does_not_prove_runtime_correctness",
        "architecture_match_does_not_prove_device_compatibility",
        "signature_metadata_does_not_prove_authenticity_until_verified",
        "driver_metadata_does_not_prove_malware_safety",
    ), "driver compatibility policy"))
    firmware = payloads.get("control/inventory/source_packs/h5_firmware_update_policy.json", {})
    errors.extend(_require_true(firmware.get("firmware_update_boundary", {}), (
        "firmware_update_candidate_is_not_approved_to_install_or_flash",
        "firmware_metadata_does_not_prove_device_compatibility",
        "firmware_hash_does_not_prove_malware_safety",
        "firmware_signature_metadata_is_not_verified_authenticity",
        "flashing_tool_metadata_is_not_execution_permission",
        "wrong_firmware_can_brick_hardware_action_blocked_by_default",
    ), "firmware update policy"))
    runtime = payloads.get("control/inventory/source_packs/h5_runtime_redistributable_policy.json", {})
    errors.extend(_require_true(runtime.get("runtime_boundary", {}), (
        "runtime_redistributable_candidate_is_not_installability_truth",
        "installer_metadata_is_not_execution_permission",
        "runtime_dependency_metadata_is_not_dependency_correctness",
        "security_update_metadata_is_not_safety_proof",
        "hash_signature_metadata_is_not_verified_authenticity_unless_future_policy_verifies_it",
    ), "runtime redistributable policy"))
    approvals = payloads.get("control/inventory/source_packs/h5_vendor_update_driver_approval_gates.json", {})
    for item in approvals.get("source_gates", []):
        if isinstance(item, Mapping) and item.get("approval_state_current") != "not_approved_for_live_access":
            errors.append(f"approval gates {item.get('source_id')}: current approval must be not_approved_for_live_access")
    return errors


def validate_registry_entries(root: Path) -> list[str]:
    errors: list[str] = []
    source_registry = _load_json(root / "control/inventory/sources/source_family_registry.json")
    if SOURCE_FAMILY not in {item.get("family_id") for item in source_registry.get("families", []) if isinstance(item, Mapping)}:
        errors.append(f"source family registry missing {SOURCE_FAMILY}")
    connector_registry = _load_json(root / "control/inventory/connectors/connector_family_registry.json")
    registered = {item.get("family_id") for item in connector_registry.get("families", []) if isinstance(item, Mapping)}
    for family in ("vendor_update_catalog", "driver_catalog", "vendor_support_catalog", "runtime_redistributable_catalog"):
        if family not in registered:
            errors.append(f"connector family registry missing {family}")
    return errors


def scan_python_files(root: Path) -> list[str]:
    errors: list[str] = []
    for rel in H5_PYTHON_FILES:
        text = (root / rel).read_text(encoding="utf-8")
        if BANNED_IMPORT_RE.search(text):
            errors.append(f"{rel}: imports network/provider/browser library")
    return errors


def scan_for_private_roots(root: Path) -> list[str]:
    errors: list[str] = []
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "vendor_downloads", "firmware_staging", "package_cache"):
        if (root / rel).exists():
            errors.append(f"forbidden private/download root exists: {rel}")
    return errors


def _load_known_values(root: Path, errors: list[str]) -> dict[str, set[str]]:
    try:
        source_families = _load_json(root / "control/inventory/sources/source_family_registry.json")
        connector_families = _load_json(root / "control/inventory/connectors/connector_family_registry.json")
        trust_lanes = _load_json(root / "control/inventory/sources/source_trust_lane_policy.json")
        index_depths = _load_json(root / "control/inventory/sources/source_index_depth_registry.json")
        access_modes = _load_json(root / "control/inventory/sources/source_access_mode_policy.json")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"unable to load registry values: {exc}")
        return {"source_families": set(), "connector_families": set(), "trust_lanes": set(), "index_depths": set(), "access_modes": set()}
    return {
        "source_families": {str(item.get("family_id")) for item in source_families.get("families", []) if isinstance(item, Mapping)},
        "connector_families": {str(item.get("family_id")) for item in connector_families.get("families", []) if isinstance(item, Mapping)},
        "trust_lanes": {str(item.get("trust_lane")) for item in trust_lanes.get("trust_lanes", []) if isinstance(item, Mapping)},
        "index_depths": {str(item.get("depth_id")) for item in index_depths.get("depths", []) if isinstance(item, Mapping)},
        "access_modes": set(str(item) for item in access_modes.get("access_modes", [])),
    }


def _scan_json_payload(rel: str, payload: Mapping[str, Any], errors: list[str]) -> None:
    text = json.dumps(payload, sort_keys=True)
    if SECRET_KEY_RE.search(text):
        errors.append(f"{rel}: contains credential/token/cookie-like key")
    if PAYLOAD_RE.search(text):
        errors.append(f"{rel}: contains downloaded payload/installer/firmware/tool-output-like key")


def _detect_forbidden_true_values(payload: Any, prefix: str) -> list[str]:
    errors: list[str] = []
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            if key in FORBIDDEN_TRUE_KEYS and value is True:
                errors.append(f"{prefix}: forbidden truth/behavior flag is true: {key}")
            errors.extend(_detect_forbidden_true_values(value, f"{prefix}.{key}"))
    elif isinstance(payload, list):
        for index, item in enumerate(payload):
            errors.extend(_detect_forbidden_true_values(item, f"{prefix}[{index}]"))
    return errors


def _detect_boundary_overclaim(payload: Mapping[str, Any], prefix: str) -> list[str]:
    errors: list[str] = []
    truth = payload.get("truth_boundary")
    if isinstance(truth, Mapping):
        errors.extend(_detect_forbidden_true_values(truth, f"{prefix}.truth_boundary"))
    product = payload.get("product_boundary")
    if isinstance(product, Mapping):
        errors.extend(_detect_forbidden_true_values(product, f"{prefix}.product_boundary"))
    return errors


def _require_true(mapping: Any, keys: Sequence[str], label: str) -> list[str]:
    if not isinstance(mapping, Mapping):
        return [f"{label}: boundary must be object"]
    return [f"{label}: {key} must be true" for key in keys if mapping.get(key) is not True]


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


if __name__ == "__main__":
    raise SystemExit(main())

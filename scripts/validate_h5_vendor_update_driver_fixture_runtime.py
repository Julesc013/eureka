#!/usr/bin/env python3
"""Validate H5-BUNDLE-02 vendor/update fixture runtime offline."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.connectors.h5_vendor_update_driver.fixture_loader import load_h5_vendor_update_fixture  # noqa: E402
from runtime.connectors.h5_vendor_update_driver.normalizer_common import (  # noqa: E402
    H5_FIXTURE_KINDS,
    H5_SOURCE_IDS,
    build_h5_fixture_replay_result,
    detect_h5_product_boundary_violations,
    detect_h5_truth_boundary_violations,
)

CONTRACT_FILES = (
    "contracts/connectors/h5_vendor_update_fixture.v0.json",
    "contracts/connectors/h5_vendor_update_normalized_record.v0.json",
    "contracts/connectors/h5_vendor_identity_candidate.v0.json",
    "contracts/connectors/h5_driver_device_compatibility_candidate.v0.json",
    "contracts/connectors/h5_firmware_update_candidate.v0.json",
    "contracts/connectors/h5_runtime_redistributable_candidate.v0.json",
    "contracts/connectors/h5_vendor_payload_metadata_candidate.v0.json",
    "contracts/connectors/h5_vendor_update_fixture_replay_result.v0.json",
)
POLICY_FILES = (
    "control/inventory/connectors/h5_vendor_update_fixture_runtime_policy.json",
    "control/inventory/connectors/h5_vendor_update_normalization_policy.json",
    "control/inventory/connectors/h5_vendor_identity_mapping_policy.json",
    "control/inventory/connectors/h5_driver_device_compatibility_mapping_policy.json",
    "control/inventory/connectors/h5_firmware_update_mapping_policy.json",
    "control/inventory/connectors/h5_runtime_redistributable_mapping_policy.json",
    "control/inventory/connectors/h5_payload_metadata_mapping_policy.json",
    "control/inventory/connectors/h5_vendor_update_fixture_output_policy.json",
    "control/inventory/connectors/h5_vendor_update_fixture_path_policy.json",
    "control/inventory/connectors/h5_vendor_update_fixture_truth_policy.json",
    "control/inventory/connectors/h5_vendor_update_source_cache_mapping_policy.json",
    "control/inventory/connectors/h5_vendor_update_evidence_mapping_policy.json",
    "control/inventory/connectors/h5_vendor_update_no_download_execute_policy.json",
)
DOC_FILES = (
    "docs/reference/H5_VENDOR_UPDATE_FIXTURE_RUNTIME.md",
    "docs/reference/H5_VENDOR_UPDATE_NORMALIZED_RECORD.md",
    "docs/reference/H5_VENDOR_IDENTITY_CANDIDATE.md",
    "docs/reference/H5_DRIVER_DEVICE_COMPATIBILITY_CANDIDATE.md",
    "docs/reference/H5_FIRMWARE_UPDATE_CANDIDATE.md",
    "docs/reference/H5_RUNTIME_REDISTRIBUTABLE_CANDIDATE.md",
    "docs/reference/H5_VENDOR_PAYLOAD_METADATA_CANDIDATE.md",
    "docs/architecture/H5_VENDOR_UPDATE_NORMALIZER_MODEL.md",
    "docs/architecture/H5_VENDOR_IDENTITY_MODEL.md",
    "docs/architecture/H5_DRIVER_DEVICE_COMPATIBILITY_MODEL.md",
    "docs/architecture/H5_FIRMWARE_UPDATE_MODEL.md",
    "docs/architecture/H5_RUNTIME_REDISTRIBUTABLE_MODEL.md",
    "docs/operations/H5_VENDOR_UPDATE_FIXTURE_REPLAY.md",
    "docs/operations/H5_VENDOR_UPDATE_FIXTURE_NO_LIVE_CALL_POLICY.md",
    "docs/operations/H5_VENDOR_UPDATE_FIXTURE_NO_DOWNLOAD_EXECUTE_POLICY.md",
)
PYTHON_FILES = (
    "scripts/normalize_h5_vendor_update_fixture.py",
    "scripts/replay_h5_vendor_update_fixtures.py",
    "scripts/validate_h5_vendor_update_driver_fixture_runtime.py",
    "scripts/summarize_h5_vendor_update_fixture_outputs.py",
)
TEST_FILES = (
    "tests/connectors/test_h5_vendor_update_fixture_runtime.py",
    "tests/connectors/test_h5_vendor_identity_mapping.py",
    "tests/connectors/test_h5_driver_device_compatibility_mapping.py",
    "tests/connectors/test_h5_firmware_runtime_mapping.py",
    "tests/operations/test_h5_vendor_update_fixture_scripts.py",
)
IDENTITY_EXAMPLES = (
    "examples/connectors/h5_vendor_update_driver/identity/vendor_identity_candidate_v0.json",
    "examples/connectors/h5_vendor_update_driver/identity/driver_device_compatibility_candidate_v0.json",
    "examples/connectors/h5_vendor_update_driver/identity/firmware_update_candidate_v0.json",
    "examples/connectors/h5_vendor_update_driver/identity/runtime_redistributable_candidate_v0.json",
    "examples/connectors/h5_vendor_update_driver/identity/payload_metadata_candidate_v0.json",
    "examples/connectors/h5_vendor_update_driver/identity/hash_metadata_candidate_v0.json",
    "examples/connectors/h5_vendor_update_driver/identity/signature_metadata_candidate_v0.json",
    "examples/connectors/h5_vendor_update_driver/identity/policy_blocked_identity_candidate_v0.json",
)
AUDIT_FILES = (
    "control/audits/h5-bundle-02-vendor-update-fixture-runtime-v0/README.md",
    "control/audits/h5-bundle-02-vendor-update-fixture-runtime-v0/h5_bundle_02_report.json",
    "control/audits/h5-bundle-02-vendor-update-fixture-runtime-v0/fixture_runtime_summary.md",
    "control/audits/h5-bundle-02-vendor-update-fixture-runtime-v0/normalizer_coverage_summary.md",
    "control/audits/h5-bundle-02-vendor-update-fixture-runtime-v0/vendor_identity_mapping_summary.md",
    "control/audits/h5-bundle-02-vendor-update-fixture-runtime-v0/driver_device_compatibility_mapping_summary.md",
    "control/audits/h5-bundle-02-vendor-update-fixture-runtime-v0/firmware_update_mapping_summary.md",
    "control/audits/h5-bundle-02-vendor-update-fixture-runtime-v0/runtime_redistributable_mapping_summary.md",
    "control/audits/h5-bundle-02-vendor-update-fixture-runtime-v0/payload_metadata_mapping_preview.md",
    "control/audits/h5-bundle-02-vendor-update-fixture-runtime-v0/source_cache_mapping_preview.md",
    "control/audits/h5-bundle-02-vendor-update-fixture-runtime-v0/evidence_mapping_preview.md",
    "control/audits/h5-bundle-02-vendor-update-fixture-runtime-v0/no_live_call_report.md",
    "control/audits/h5-bundle-02-vendor-update-fixture-runtime-v0/no_download_execute_report.md",
    "control/audits/h5-bundle-02-vendor-update-fixture-runtime-v0/validation.md",
    "control/audits/h5-bundle-02-vendor-update-fixture-runtime-v0/generated/sample_h5_normalized_record.json",
    "control/audits/h5-bundle-02-vendor-update-fixture-runtime-v0/generated/sample_h5_vendor_identity_candidate.json",
    "control/audits/h5-bundle-02-vendor-update-fixture-runtime-v0/generated/sample_h5_driver_device_compatibility_candidate.json",
    "control/audits/h5-bundle-02-vendor-update-fixture-runtime-v0/generated/sample_h5_firmware_update_candidate.json",
    "control/audits/h5-bundle-02-vendor-update-fixture-runtime-v0/generated/sample_h5_runtime_redistributable_candidate.json",
    "control/audits/h5-bundle-02-vendor-update-fixture-runtime-v0/generated/sample_h5_payload_metadata_candidate.json",
    "control/audits/h5-bundle-02-vendor-update-fixture-runtime-v0/generated/sample_h5_source_cache_candidate.json",
    "control/audits/h5-bundle-02-vendor-update-fixture-runtime-v0/generated/sample_h5_evidence_candidate_preview.json",
    "control/audits/h5-bundle-02-vendor-update-fixture-runtime-v0/generated/sample_h5_fixture_replay_result.json",
    "control/audits/h5-bundle-02-vendor-update-fixture-runtime-v0/generated/sample_h5_fixture_summary.md",
)
FIXTURE_ROOT = Path("examples/connectors/h5_vendor_update_driver/fixtures")
NORMALIZED_ROOT = Path("examples/connectors/h5_vendor_update_driver/normalized")
REPLAY_ROOT = Path("examples/connectors/h5_vendor_update_driver/replay_results")

BANNED_IMPORT_RE = re.compile(r"^\s*(?:from|import)\s+(requests|urllib|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b", re.MULTILINE)
TOOL_COMMAND_RE = re.compile(r"(subprocess\.|os\.system|Popen\().*\b(vendor|installer|package|flash|firmware|driver)\b", re.IGNORECASE | re.DOTALL)
SECRET_KEY_RE = re.compile(r'"[^"]*(api[_-]?key|api[_-]?token|access[_-]?token|auth[_-]?token|client_secret|password|private_key|cookie)[^"]*"\s*:', re.IGNORECASE)
PAYLOAD_RE = re.compile(r'"[^"]*(downloaded_payload|firmware_image|bios_image|uefi_image|installer_bytes|binary_payload|cab_bytes|msi_bytes|msu_bytes|exe_bytes|dmg_bytes|pkg_bytes|package_manager_output|executable_payload)[^"]*"\s*:', re.IGNORECASE)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("H5 vendor/update fixture runtime validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"errors: {len(result['errors'])}", file=stdout)
        for error in result["errors"]:
            print(f"- {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    required_paths = list(CONTRACT_FILES + POLICY_FILES + DOC_FILES + PYTHON_FILES + TEST_FILES + IDENTITY_EXAMPLES + AUDIT_FILES)
    for source_id in H5_SOURCE_IDS:
        for kind in H5_FIXTURE_KINDS:
            filename = "policy_blocked_record.json" if kind == "policy_blocked" else f"{kind}_record.json"
            required_paths.append(str(FIXTURE_ROOT / source_id / filename))
        required_paths.append(str(NORMALIZED_ROOT / f"{source_id}_normalized.json"))
        required_paths.append(str(REPLAY_ROOT / f"{source_id}_replay_result.json"))
        required_paths.append(f"runtime/connectors/h5_vendor_update_driver/{source_id}.py")
    required_paths.extend([
        "runtime/connectors/h5_vendor_update_driver/__init__.py",
        "runtime/connectors/h5_vendor_update_driver/fixture_loader.py",
        "runtime/connectors/h5_vendor_update_driver/normalizer_common.py",
        "runtime/connectors/h5_vendor_update_driver/vendor_identity.py",
        "runtime/connectors/h5_vendor_update_driver/driver_device_compatibility.py",
        "runtime/connectors/h5_vendor_update_driver/firmware_update.py",
        "runtime/connectors/h5_vendor_update_driver/runtime_redistributable.py",
        "runtime/connectors/h5_vendor_update_driver/payload_metadata.py",
    ])
    for rel in required_paths:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing required artifact: {rel}")
            continue
        if path.suffix == ".json":
            load_json_object(path, errors)
    validate_fixtures(root, errors)
    validate_examples(root, errors)
    validate_runtime_imports(errors)
    validate_python_safety(root, errors)
    validate_scripts_offline(root, errors)
    validate_no_private_roots(root, errors)
    return {
        "schema_version": "h5_vendor_update_fixture_runtime_validation.v0",
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "source_count": len(H5_SOURCE_IDS),
        "fixture_kinds": list(H5_FIXTURE_KINDS),
        "network_calls_made": False,
        "downloads_made": False,
        "vendor_tools_invoked": False,
        "firmware_flashes_made": False,
    }


def validate_fixtures(root: Path, errors: list[str]) -> None:
    for source_id in H5_SOURCE_IDS:
        normalizer = importlib.import_module(f"runtime.connectors.h5_vendor_update_driver.{source_id}").normalize
        for kind in H5_FIXTURE_KINDS:
            filename = "policy_blocked_record.json" if kind == "policy_blocked" else f"{kind}_record.json"
            rel = FIXTURE_ROOT / source_id / filename
            path = root / rel
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            if SECRET_KEY_RE.search(text):
                errors.append(f"secret-like key in fixture: {rel}")
            if PAYLOAD_RE.search(text):
                errors.append(f"payload/tool-output-like field in fixture: {rel}")
            try:
                fixture = load_h5_vendor_update_fixture(path)
                normalized = normalizer(fixture)
                replay = build_h5_fixture_replay_result(fixture, normalized)
                errors.extend(f"{rel} normalized: {item}" for item in validate_normalized_record(normalized))
                errors.extend(f"{rel} replay: {item}" for item in validate_replay_result(replay))
            except Exception as exc:  # noqa: BLE001
                errors.append(f"failed to normalize fixture {rel}: {exc}")


def validate_examples(root: Path, errors: list[str]) -> None:
    for source_id in H5_SOURCE_IDS:
        normalized_path = root / NORMALIZED_ROOT / f"{source_id}_normalized.json"
        replay_path = root / REPLAY_ROOT / f"{source_id}_replay_result.json"
        if normalized_path.is_file():
            payload = load_json_object(normalized_path, errors)
            if payload is not None:
                errors.extend(f"{normalized_path.relative_to(root)}: {item}" for item in validate_normalized_record(payload))
        if replay_path.is_file():
            payload = load_json_object(replay_path, errors)
            if payload is not None:
                errors.extend(f"{replay_path.relative_to(root)}: {item}" for item in validate_replay_result(payload))
    for rel in IDENTITY_EXAMPLES:
        payload = load_json_object(root / rel, errors)
        if payload is not None:
            errors.extend(f"{rel}: {item}" for item in validate_candidate_boundary(payload))


def validate_normalized_record(record: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if record.get("schema_version") != "h5_vendor_update_normalized_record.v0":
        errors.append("normalized schema_version must be h5_vendor_update_normalized_record.v0")
    for key in ("source_id", "connector_family", "vendor_name", "vendor_identity_candidate", "source_cache_candidate_preview", "evidence_candidate_preview"):
        if key not in record:
            errors.append(f"normalized record missing {key}")
    errors.extend(detect_h5_truth_boundary_violations(record))
    errors.extend(detect_h5_product_boundary_violations(record))
    return errors


def validate_replay_result(result: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if result.get("schema_version") != "h5_vendor_update_fixture_replay_result.v0":
        errors.append("replay schema_version must be h5_vendor_update_fixture_replay_result.v0")
    for key in ("no_network_used", "no_live_source_used", "no_vendor_catalog_fetch_used", "no_download_used", "no_vendor_tool_invoked", "no_package_manager_invoked", "no_firmware_flash_invoked", "no_installer_or_artifact_executed"):
        if result.get(key) is not True:
            errors.append(f"{key} must be true")
    errors.extend(detect_h5_truth_boundary_violations(result))
    errors.extend(detect_h5_product_boundary_violations(result))
    return errors


def validate_candidate_boundary(candidate: Mapping[str, Any]) -> list[str]:
    return detect_h5_truth_boundary_violations(candidate) + detect_h5_product_boundary_violations(candidate)


def validate_runtime_imports(errors: list[str]) -> None:
    modules = [
        "runtime.connectors.h5_vendor_update_driver.fixture_loader",
        "runtime.connectors.h5_vendor_update_driver.normalizer_common",
        "runtime.connectors.h5_vendor_update_driver.vendor_identity",
        "runtime.connectors.h5_vendor_update_driver.driver_device_compatibility",
        "runtime.connectors.h5_vendor_update_driver.firmware_update",
        "runtime.connectors.h5_vendor_update_driver.runtime_redistributable",
        "runtime.connectors.h5_vendor_update_driver.payload_metadata",
    ] + [f"runtime.connectors.h5_vendor_update_driver.{source_id}" for source_id in H5_SOURCE_IDS]
    for module_name in modules:
        try:
            importlib.import_module(module_name)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"failed to import {module_name}: {exc}")


def validate_python_safety(root: Path, errors: list[str]) -> None:
    python_paths = [root / rel for rel in PYTHON_FILES]
    python_paths.extend((root / "runtime/connectors/h5_vendor_update_driver").glob("*.py"))
    for path in python_paths:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if BANNED_IMPORT_RE.search(text):
            errors.append(f"banned network/model/provider import in {path.relative_to(root)}")
        if path.as_posix().endswith("runtime/connectors/h5_vendor_update_driver/normalizer_common.py") and TOOL_COMMAND_RE.search(text):
            errors.append(f"forbidden vendor/package/tool command invocation in {path.relative_to(root)}")


def validate_scripts_offline(root: Path, errors: list[str]) -> None:
    commands = [
        [sys.executable, "scripts/normalize_h5_vendor_update_fixture.py", "--source-id", "nvidia_driver_downloads", "--input", "examples/connectors/h5_vendor_update_driver/fixtures/nvidia_driver_downloads/typical_record.json", "--check"],
        [sys.executable, "scripts/replay_h5_vendor_update_fixtures.py", "--check"],
        [sys.executable, "scripts/summarize_h5_vendor_update_fixture_outputs.py", "--input", "examples/connectors/h5_vendor_update_driver", "--check"],
    ]
    for command in commands:
        result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            errors.append(f"script failed offline: {' '.join(command[1:])} :: {result.stdout}{result.stderr}")
    bad = subprocess.run(
        [sys.executable, "scripts/normalize_h5_vendor_update_fixture.py", "--source-id", "nvidia_driver_downloads", "--input", "examples/connectors/h5_vendor_update_driver/fixtures/nvidia_driver_downloads/typical_record.json", "--output", "site/dist/h5.json"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if bad.returncode == 0 or "refusing forbidden output root" not in bad.stdout:
        errors.append("normalizer did not reject site/dist output")


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "vendor_downloads", "firmware_staging", "package_cache"):
        if (root / rel).exists():
            errors.append(f"local/private or artifact root exists: {rel}")


def load_json_object(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"{path.relative_to(REPO_ROOT)} invalid JSON: {exc}")
        return None
    if not isinstance(payload, dict):
        errors.append(f"{path.relative_to(REPO_ROOT)} must be a JSON object")
        return None
    return payload


if __name__ == "__main__":
    raise SystemExit(main())

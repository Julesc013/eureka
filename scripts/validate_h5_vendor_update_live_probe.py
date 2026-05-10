#!/usr/bin/env python3
"""Validate H5 vendor/update live-probe framework without live calls."""

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

from runtime.connectors.h5_vendor_update_driver.live_probe_common import (  # noqa: E402
    H5_SOURCE_IDS,
    detect_h5_vendor_update_live_probe_product_boundary_violations,
    detect_h5_vendor_update_live_probe_truth_boundary_violations,
    load_h5_vendor_update_live_probe_policy_bundle,
    validate_h5_source_approval,
)

CONTRACTS = (
    "contracts/connectors/h5_vendor_update_live_probe_request.v0.json",
    "contracts/connectors/h5_vendor_update_live_probe_result.v0.json",
    "contracts/connectors/h5_vendor_update_live_probe_output_bundle.v0.json",
    "contracts/connectors/h5_vendor_update_connector_health_summary.v0.json",
)
POLICIES = (
    "control/inventory/connectors/h5_vendor_update_live_probe_policy.json",
    "control/inventory/connectors/h5_vendor_update_live_probe_allowed_requests.json",
    "control/inventory/connectors/h5_vendor_update_live_probe_endpoint_policy.json",
    "control/inventory/connectors/h5_vendor_update_live_probe_rate_limit_policy.json",
    "control/inventory/connectors/h5_vendor_update_live_probe_cache_policy.json",
    "control/inventory/connectors/h5_vendor_update_live_probe_kill_switch_policy.json",
    "control/inventory/connectors/h5_vendor_update_live_probe_output_policy.json",
    "control/inventory/connectors/h5_vendor_update_live_probe_path_policy.json",
    "control/inventory/connectors/h5_vendor_update_live_probe_review_policy.json",
    "control/inventory/connectors/h5_vendor_update_live_probe_truth_policy.json",
    "control/inventory/connectors/h5_vendor_update_live_probe_no_download_execute_policy.json",
    "control/inventory/connectors/h5_vendor_update_live_probe_no_catalog_sync_policy.json",
)
DOCS = (
    "docs/reference/H5_VENDOR_UPDATE_LIVE_PROBE.md",
    "docs/reference/H5_VENDOR_UPDATE_LIVE_PROBE_RESULT.md",
    "docs/reference/H5_VENDOR_UPDATE_CONNECTOR_HEALTH_SUMMARY.md",
    "docs/architecture/H5_VENDOR_UPDATE_LIVE_PROBE_MODEL.md",
    "docs/operations/H5_VENDOR_UPDATE_LIVE_PROBE_APPROVAL_GATES.md",
    "docs/operations/H5_VENDOR_UPDATE_LIVE_PROBE_REVIEW.md",
    "docs/operations/H5_VENDOR_UPDATE_LIVE_PROBE_BLOCKED_MODE.md",
    "docs/operations/H5_VENDOR_UPDATE_LIVE_PROBE_NO_DOWNLOAD_EXECUTE_POLICY.md",
    "docs/operations/H5_VENDOR_UPDATE_LIVE_PROBE_NO_CATALOG_SYNC_POLICY.md",
)
AUDIT_DIR = Path("control/audits/h5-bundle-03-vendor-update-live-probes-v0")
AUDIT_FILES = (
    "README.md",
    "h5_bundle_03_report.json",
    "live_probe_policy_review.md",
    "live_probe_execution_report.md",
    "vendor_identity_candidate_preview.md",
    "driver_device_compatibility_candidate_preview.md",
    "firmware_update_candidate_preview.md",
    "runtime_redistributable_candidate_preview.md",
    "payload_metadata_candidate_preview.md",
    "source_cache_candidate_preview.md",
    "evidence_candidate_preview.md",
    "review_queue_seed_preview.md",
    "connector_health_summary.md",
    "no_download_execute_report.md",
    "no_catalog_sync_report.md",
    "h5_live_probe_blocked_or_completed_summary.md",
    "validation.md",
    "generated/sample_h5_live_probe_result.json",
    "generated/sample_h5_vendor_identity_candidate_from_probe.json",
    "generated/sample_h5_driver_device_compatibility_candidate_from_probe.json",
    "generated/sample_h5_firmware_update_candidate_from_probe.json",
    "generated/sample_h5_runtime_redistributable_candidate_from_probe.json",
    "generated/sample_h5_payload_metadata_candidate_from_probe.json",
    "generated/sample_h5_source_cache_candidate_from_probe.json",
    "generated/sample_h5_evidence_candidate_preview_from_probe.json",
    "generated/sample_h5_review_queue_seed_from_probe.json",
    "generated/sample_h5_connector_health_summary.json",
    "generated/sample_h5_live_probe_summary.md",
)
PYTHON_FILES = tuple(
    ["runtime/connectors/h5_vendor_update_driver/live_probe_common.py"]
    + [f"runtime/connectors/h5_vendor_update_driver/live_probe_{source_id}.py" for source_id in H5_SOURCE_IDS]
    + [
        "scripts/run_h5_vendor_update_live_probe.py",
        "scripts/validate_h5_vendor_update_live_probe.py",
        "scripts/summarize_h5_vendor_update_live_probe_outputs.py",
    ]
)
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)
SECRET_KEY_RE = re.compile(r'"[^"]*(api[_-]?key|api[_-]?token|access[_-]?token|auth[_-]?token|client_secret|password|private_key|cookie)[^"]*"\s*:', re.IGNORECASE)
TOOL_CALL_RE = re.compile(r"(os\.system|subprocess\.(?:call|Popen)).*\b(git|make|cmake|ninja|npm|yarn|pnpm|pip|poetry|cargo|go|mvn|gradle|installer|apt|dnf|brew|winget|choco|flash|firmware|driver)\b", re.IGNORECASE)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("H5 vendor/update live probe validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads: dict[str, dict[str, Any]] = {}
    for rel in CONTRACTS + POLICIES:
        payloads[rel] = load_json_object(root / rel, errors)
    for rel in DOCS + PYTHON_FILES:
        if not (root / rel).is_file():
            errors.append(f"missing required file: {rel}")
    for name in AUDIT_FILES:
        if not (root / AUDIT_DIR / name).is_file():
            errors.append(f"missing audit file: {(AUDIT_DIR / name).as_posix()}")
    validate_policies(payloads, errors)
    validate_examples(root, errors)
    validate_runtime_imports(errors)
    validate_python_safety(root, errors)
    validate_cli_offline(root, errors)
    validate_generated_outputs(root, errors)
    validate_no_private_roots(root, errors)
    return {
        "schema_version": "h5_vendor_update_live_probe_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "H5-BUNDLE-03",
        "offline_default": True,
        "network_calls_made": False,
        "catalog_sync_used": False,
        "downloads_used": False,
        "vendor_tools_invoked": False,
        "firmware_flashes_made": False,
        "install_execute_used": False,
        "errors": errors,
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    live = payloads.get("control/inventory/connectors/h5_vendor_update_live_probe_policy.json", {})
    for key in ("live_probe_default_enabled", "source_sync_enabled", "public_query_fanout_enabled", "vendor_catalog_sync_enabled", "downloads_enabled", "vendor_tool_invocation_enabled", "firmware_flash_enabled", "install_execute_enabled"):
        if live.get(key) is not False:
            errors.append(f"global policy {key} must be false")
    allowed = payloads.get("control/inventory/connectors/h5_vendor_update_live_probe_allowed_requests.json", {})
    sources = allowed.get("sources", [])
    if sorted(item.get("source_id") for item in sources if isinstance(item, Mapping)) != sorted(H5_SOURCE_IDS):
        errors.append("allowed requests policy must list all H5 sources")
    bundle = load_h5_vendor_update_live_probe_policy_bundle(REPO_ROOT)
    for item in sources:
        if not isinstance(item, Mapping):
            errors.append("allowed request source entry must be object")
            continue
        source_id = item.get("source_id")
        if item.get("approval_status") != "not_approved_for_live_access":
            errors.append(f"{source_id}: approval_status must remain not_approved_for_live_access")
        if item.get("allowed_request_keys") not in ([], None):
            errors.append(f"{source_id}: allowed_request_keys must stay empty without approval")
        for key in ("live_access_approved", "metadata_probe_approved"):
            if item.get(key) is not False:
                errors.append(f"{source_id}: {key} must be false")
        for key in (
            "source_sync_approved",
            "vendor_catalog_fetch_approved",
            "driver_download_approved",
            "firmware_download_approved",
            "runtime_download_approved",
            "installer_download_approved",
            "update_package_download_approved",
            "checksum_fetch_approved",
            "signature_fetch_approved",
            "vendor_tool_invocation_approved",
            "package_manager_invocation_approved",
            "firmware_flash_approved",
            "install_execute_approved",
            "scraping_approved",
            "crawling_approved",
            "public_query_fanout_approved",
        ):
            if item.get(key) is not False:
                errors.append(f"{source_id}: {key} must be false")
        request_key = str((item.get("planned_request_keys") or [""])[0])
        approval = validate_h5_source_approval(str(source_id), request_key, bundle)
        if approval["approved"]:
            errors.append(f"{source_id}: live approval unexpectedly passes")
    truth = payloads.get("control/inventory/connectors/h5_vendor_update_live_probe_truth_policy.json", {})
    for key in (
        "live_probe_result_is_public_truth",
        "vendor_identity_candidate_is_truth",
        "driver_identity_candidate_is_truth",
        "firmware_identity_candidate_is_truth",
        "runtime_identity_candidate_is_truth",
        "compatibility_candidate_is_truth",
        "signature_metadata_is_authenticity",
        "payload_hash_candidate_is_malware_safety",
        "source_cache_candidate_is_accepted_source",
        "evidence_candidate_preview_is_accepted_evidence",
        "review_seed_is_review_decision",
        "public_index_mutated",
        "master_index_mutated",
        "rights_clearance_claimed",
        "malware_safety_claimed",
        "verified_installability_claimed",
        "verified_compatibility_claimed",
        "verified_authenticity_claimed",
    ):
        if truth.get(key) is not False:
            errors.append(f"truth policy {key} must be false")
    output = payloads.get("control/inventory/connectors/h5_vendor_update_live_probe_output_policy.json", {})
    for key in (
        "downloaded_driver",
        "downloaded_firmware",
        "downloaded_installer",
        "downloaded_runtime",
        "downloaded_update_package",
        "vendor_tool_output",
        "firmware_flash",
        "package_manager_output",
        "executed_artifact",
        "accepted_vendor_truth",
        "accepted_driver_identity_truth",
        "accepted_firmware_identity_truth",
        "accepted_runtime_identity_truth",
        "accepted_compatibility_truth",
        "accepted_authenticity_truth",
        "accepted_safety_truth",
        "accepted_source_truth",
        "accepted_evidence_truth",
        "accepted_candidate_truth",
        "accepted_public_record",
        "public_index_mutation",
        "master_index_mutation",
        "rights_clearance",
        "malware_safety",
        "verified_installability",
        "verified_compatibility",
        "verified_authenticity",
        "production_readiness_claim",
    ):
        if key not in output.get("forbidden_outputs", []):
            errors.append(f"output policy must forbid {key}")


def validate_examples(root: Path, errors: list[str]) -> None:
    expected_requests = ["blocked_live_probe_request_v0.json"] + [f"approved_{source_id}_probe_request_v0.json" for source_id in H5_SOURCE_IDS]
    expected_results = ["blocked_live_probe_result_v0.json"] + [f"{source_id}_live_probe_result_example_v0.json" for source_id in H5_SOURCE_IDS]
    paths = [f"examples/connectors/h5_vendor_update_driver/live_probe/{name}" for name in expected_requests]
    paths += [f"examples/connectors/h5_vendor_update_driver/live_probe_results/{name}" for name in expected_results]
    paths += [
        "examples/connectors/h5_vendor_update_driver/live_probe_outputs/source_cache_candidate_from_h5_probe_v0.json",
        "examples/connectors/h5_vendor_update_driver/live_probe_outputs/evidence_candidate_preview_from_h5_probe_v0.json",
        "examples/connectors/h5_vendor_update_driver/live_probe_outputs/review_queue_seed_from_h5_probe_v0.json",
        "examples/connectors/h5_vendor_update_driver/live_probe_outputs/connector_health_from_h5_probe_v0.json",
        "examples/connectors/h5_vendor_update_driver/live_probe_outputs/vendor_identity_candidate_from_h5_probe_v0.json",
        "examples/connectors/h5_vendor_update_driver/live_probe_outputs/driver_device_compatibility_candidate_from_h5_probe_v0.json",
        "examples/connectors/h5_vendor_update_driver/live_probe_outputs/firmware_update_candidate_from_h5_probe_v0.json",
        "examples/connectors/h5_vendor_update_driver/live_probe_outputs/runtime_redistributable_candidate_from_h5_probe_v0.json",
        "examples/connectors/h5_vendor_update_driver/live_probe_outputs/payload_metadata_candidate_from_h5_probe_v0.json",
    ]
    for rel in paths:
        payload = load_json_object(root / rel, errors)
        validate_boundaries(payload, rel, errors)
        validate_no_secret_text(root / rel, errors)


def validate_runtime_imports(errors: list[str]) -> None:
    for source_id in H5_SOURCE_IDS:
        try:
            importlib.import_module(f"runtime.connectors.h5_vendor_update_driver.live_probe_{source_id}")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"failed to import live probe module for {source_id}: {exc}")


def validate_python_safety(root: Path, errors: list[str]) -> None:
    for rel in PYTHON_FILES:
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if BANNED_IMPORT_RE.search(text):
            errors.append(f"banned network/model/provider import in {rel}")
        if TOOL_CALL_RE.search(text):
            errors.append(f"forbidden tool/package invocation pattern in {rel}")


def validate_cli_offline(root: Path, errors: list[str]) -> None:
    commands = [
        [sys.executable, "scripts/run_h5_vendor_update_live_probe.py", "--source-id", "nvidia_driver_downloads", "--request-key", "example_driver_metadata", "--check", "--json"],
        [sys.executable, "scripts/summarize_h5_vendor_update_live_probe_outputs.py", "--input", "examples/connectors/h5_vendor_update_driver/live_probe_results", "--check", "--json"],
    ]
    for command in commands:
        completed = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
        if completed.returncode != 0:
            errors.append(f"offline command failed: {' '.join(command)}: {completed.stderr or completed.stdout}")
    with tempfile.TemporaryDirectory() as tempdir:
        temp_output = Path(tempdir) / "probe.json"
        completed = subprocess.run([sys.executable, "scripts/run_h5_vendor_update_live_probe.py", "--source-id", "nvidia_driver_downloads", "--request-key", "example_driver_metadata", "--output", str(temp_output), "--json"], cwd=root, text=True, capture_output=True, check=False)
        if completed.returncode != 0 or not temp_output.is_file():
            errors.append("CLI failed to write explicit temp output")
    forbidden = subprocess.run([sys.executable, "scripts/run_h5_vendor_update_live_probe.py", "--source-id", "nvidia_driver_downloads", "--request-key", "example_driver_metadata", "--output", "site/dist/h5_probe.json", "--json"], cwd=root, text=True, capture_output=True, check=False)
    if forbidden.returncode == 0:
        errors.append("CLI accepted forbidden site/dist output root")


def validate_generated_outputs(root: Path, errors: list[str]) -> None:
    for json_path in (root / AUDIT_DIR / "generated").glob("*.json"):
        payload = load_json_object(json_path, errors)
        validate_boundaries(payload, str(json_path.relative_to(root)), errors)


def validate_boundaries(payload: Mapping[str, Any], rel: str, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        return
    errors.extend(f"{rel}: {item}" for item in detect_h5_vendor_update_live_probe_truth_boundary_violations(payload))
    errors.extend(f"{rel}: {item}" for item in detect_h5_vendor_update_live_probe_product_boundary_violations(payload))


def validate_no_secret_text(path: Path, errors: list[str]) -> None:
    if path.is_file() and SECRET_KEY_RE.search(path.read_text(encoding="utf-8")):
        errors.append(f"secret-like key in example: {path.relative_to(REPO_ROOT)}")


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "vendor_downloads", "firmware_staging", "package_cache"):
        if (root / rel).exists():
            errors.append(f"local private or forbidden root exists: {rel}")


def load_json_object(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"missing JSON file: {path.relative_to(REPO_ROOT)}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"invalid JSON {path.relative_to(REPO_ROOT)}: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"JSON must be object: {path.relative_to(REPO_ROOT)}")
        return {}
    return payload


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate H5-BUNDLE-04 review, quality delta, and audit artifacts offline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.connectors.h5_vendor_update_driver.quality_delta import detect_h5_quality_overclaim  # noqa: E402
from runtime.connectors.h5_vendor_update_driver.review_integration import (  # noqa: E402
    detect_h5_review_product_boundary_violations,
    detect_h5_review_truth_boundary_violations,
)

AUDIT_DIR = Path("control/audits/h5-bundle-04-vendor-update-review-quality-audit-v0")
REVIEW_DIR = Path("examples/connectors/h5_vendor_update_driver/review_integration")
REQUIRED_JSON = (
    "control/schemas/audits/h5/connectors/vendor_update_review_integration_result.v0.json",
    "control/schemas/audits/h5/connectors/vendor_update_quality_delta_report.v0.json",
    "control/schemas/audits/h5/connectors/vendor_update_connector_wave_postmortem.v0.json",
    "control/schemas/audits/h5/connectors/vendor_update_integration_audit.v0.json",
    "control/schemas/tasks/h5/connectors/vendor_update_next_phase_recommendation.v0.json",
    "control/inventory/connectors/h5_vendor_update_review_integration_policy.json",
    "control/inventory/connectors/h5_vendor_update_review_output_policy.json",
    "control/inventory/connectors/h5_vendor_update_review_path_policy.json",
    "control/inventory/connectors/h5_vendor_update_review_truth_policy.json",
    "control/inventory/connectors/h5_vendor_update_quality_delta_policy.json",
    "control/inventory/connectors/h5_vendor_update_connector_wave_postmortem_policy.json",
    "control/inventory/connectors/h5_vendor_update_integration_audit_policy.json",
    "control/inventory/connectors/h5_vendor_update_next_phase_policy.json",
    (AUDIT_DIR / "h5_bundle_04_report.json").as_posix(),
)
REQUIRED_EXAMPLES = (
    "h5_vendor_identity_review_seed_v0.json",
    "h5_driver_device_compatibility_review_seed_v0.json",
    "h5_firmware_update_review_seed_v0.json",
    "h5_runtime_redistributable_review_seed_v0.json",
    "h5_payload_metadata_review_seed_v0.json",
    "h5_source_cache_review_seed_v0.json",
    "h5_evidence_candidate_review_seed_v0.json",
    "h5_candidate_promotion_preview_v0.json",
    "h5_source_coverage_update_preview_v0.json",
    "h5_connector_scorecard_update_v0.json",
    "h5_source_pack_update_preview_v0.json",
    "h5_quality_delta_report_v0.json",
    "h5_connector_wave_postmortem_v0.json",
    "h5_blocked_review_integration_v0.json",
    "h5_review_integration_result_v0.json",
    "h5_next_phase_recommendation_v0.json",
    "h5_integration_audit_v0.json",
)
REQUIRED_AUDIT_FILES = (
    "README.md",
    "h5_bundle_04_report.json",
    "h5_review_integration_report.md",
    "h5_quality_delta_report.md",
    "h5_connector_wave_postmortem.md",
    "h5_integration_audit.md",
    "h5_exit_gate_decision.md",
    "next_phase_recommendation.md",
    "h6_readiness_review.md",
    "j1_risky_action_deferral_review.md",
    "k_semantic_ai_deferral_review.md",
    "l_wider_client_deferral_review.md",
    "validation.md",
    "generated/sample_h5_review_integration_result.json",
    "generated/sample_h5_quality_delta_report.json",
    "generated/sample_h5_connector_wave_postmortem.json",
    "generated/sample_h5_integration_audit.json",
    "generated/sample_h5_next_phase_recommendation.json",
    "generated/sample_h5_summary.md",
)
REQUIRED_DOCS = (
    "docs/reference/H5_VENDOR_UPDATE_REVIEW_INTEGRATION.md",
    "docs/reference/H5_VENDOR_UPDATE_QUALITY_DELTA_REPORT.md",
    "docs/reference/H5_VENDOR_UPDATE_CONNECTOR_WAVE_POSTMORTEM.md",
    "docs/architecture/H5_VENDOR_UPDATE_REVIEW_INTEGRATION_MODEL.md",
    "docs/operations/H5_VENDOR_UPDATE_WAVE_POSTMORTEM.md",
    "docs/operations/H5_VENDOR_UPDATE_WAVE_QUALITY_DELTA.md",
    "docs/operations/H5_TO_H6_HANDOFF.md",
    "docs/operations/H5_TO_J1_K_L_DEFERRAL.md",
)
PYTHON_SCAN_PATHS = (
    "runtime/connectors/h5_vendor_update_driver/review_integration.py",
    "runtime/connectors/h5_vendor_update_driver/quality_delta.py",
    "runtime/connectors/h5_vendor_update_driver/wave_postmortem.py",
    "scripts/integrate_h5_vendor_update_review.py",
    "scripts/summarize_h5_vendor_update_quality_delta.py",
    "scripts/audit_h5_vendor_update_driver_wave.py",
    "scripts/validate_h5_vendor_update_review_quality_audit.py",
)
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|urllib|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)
TOOL_CALL_RE = re.compile(r"(os\.system|subprocess\.(?:call|Popen)).*\b(git|make|cmake|ninja|npm|pip|cargo|go|docker|podman|apt|dnf|brew|choco|winget|flash|installer)\b", re.IGNORECASE)
SECRET_KEY_RE = re.compile(
    r'"[^"]*(api[_-]?key|api[_-]?token|access[_-]?token|auth[_-]?token|client_secret|password|private_key|cookie)[^"]*"\s*:',
    re.IGNORECASE,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit validation JSON.")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("H5 vendor/update/driver review quality audit validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"error_count: {len(result['errors'])}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads = {rel: load_json_object(root / rel, errors) for rel in REQUIRED_JSON}
    validate_policies(payloads, errors)
    validate_docs(root, errors)
    validate_examples(root, errors)
    validate_audit_files(root, errors)
    validate_generated_outputs(root, errors)
    validate_python_imports(root, errors)
    validate_scripts(root, errors)
    validate_no_private_roots(root, errors)
    return {
        "schema_version": "h5_review_quality_audit_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "H5-BUNDLE-04",
        "offline_default": True,
        "network_calls_made": False,
        "errors": errors,
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    review = payloads.get("control/inventory/connectors/h5_vendor_update_review_integration_policy.json", {})
    for key in (
        "live_call_allowed_by_default",
        "source_cache_persistence_enabled",
        "evidence_acceptance_enabled",
        "candidate_acceptance_enabled",
        "vendor_identity_acceptance_enabled",
        "driver_identity_acceptance_enabled",
        "firmware_identity_acceptance_enabled",
        "runtime_identity_acceptance_enabled",
        "compatibility_acceptance_enabled",
        "authenticity_acceptance_enabled",
        "safety_acceptance_enabled",
        "public_index_mutation_allowed",
        "master_index_mutation_allowed",
        "catalog_sync_enabled",
        "downloads_enabled",
        "vendor_tool_invocation_enabled",
        "firmware_flash_enabled",
        "install_execute_enabled",
    ):
        if review.get(key) is not False:
            errors.append(f"h5 review policy {key} must be false")
    output = payloads.get("control/inventory/connectors/h5_vendor_update_review_output_policy.json", {})
    for key in (
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
        "catalog_fetch_permission",
        "download_permission",
        "installer_execution_permission",
        "firmware_flash_permission",
        "vendor_tool_permission",
        "install_execute_permission",
        "production_readiness_claim",
    ):
        if key not in output.get("forbidden_outputs", []):
            errors.append(f"h5 review output policy must forbid {key}")
    audit = payloads.get("control/inventory/connectors/h5_vendor_update_integration_audit_policy.json", {})
    if "READY_FOR_H6_BUNDLE_01" not in audit.get("next_phase_values", []):
        errors.append("H5 audit policy must allow READY_FOR_H6_BUNDLE_01")
    next_phase = payloads.get("control/inventory/connectors/h5_vendor_update_next_phase_policy.json", {})
    if next_phase.get("j1_risky_actions_deferred") is not True or next_phase.get("k_semantic_ai_deferred") is not True or next_phase.get("l_wider_clients_deferred") is not True:
        errors.append("H5 next phase policy must defer J1/K/L")


def validate_docs(root: Path, errors: list[str]) -> None:
    for rel in REQUIRED_DOCS:
        if not (root / rel).is_file():
            errors.append(f"missing doc: {rel}")


def validate_examples(root: Path, errors: list[str]) -> None:
    for name in REQUIRED_EXAMPLES:
        payload = load_json_object(root / REVIEW_DIR / name, errors)
        validate_boundaries(payload, f"example {name}", errors)
        validate_no_secret_text(root / REVIEW_DIR / name, errors)
    delta = load_json_object(root / REVIEW_DIR / "h5_quality_delta_report_v0.json", errors)
    errors.extend(detect_h5_quality_overclaim(delta))
    postmortem = load_json_object(root / REVIEW_DIR / "h5_connector_wave_postmortem_v0.json", errors)
    if postmortem.get("auto_approves_future_connectors") is not False:
        errors.append("postmortem must not auto-approve future connectors")


def validate_audit_files(root: Path, errors: list[str]) -> None:
    for rel_name in REQUIRED_AUDIT_FILES:
        if not (root / AUDIT_DIR / rel_name).is_file():
            errors.append(f"missing audit file: {(AUDIT_DIR / rel_name).as_posix()}")


def validate_generated_outputs(root: Path, errors: list[str]) -> None:
    for rel_name in REQUIRED_AUDIT_FILES:
        if rel_name.startswith("generated/") and rel_name.endswith(".json"):
            payload = load_json_object(root / AUDIT_DIR / rel_name, errors)
            validate_boundaries(payload, rel_name, errors)
    report = load_json_object(root / AUDIT_DIR / "h5_bundle_04_report.json", errors)
    if report.get("h5_exit_gate") not in {"PASS", "PASS_WITH_WARNINGS", "PARTIAL", "BLOCKED", "FAIL"}:
        errors.append("H5 report must have explicit h5_exit_gate")
    if report.get("next_phase_recommendation") != "READY_FOR_H6_BUNDLE_01":
        errors.append("H5 report should recommend READY_FOR_H6_BUNDLE_01 when fixture-equivalent outputs are sufficient")
    validate_boundaries(report, "h5_bundle_04_report", errors)


def validate_python_imports(root: Path, errors: list[str]) -> None:
    for rel in PYTHON_SCAN_PATHS:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing Python file: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for match in BANNED_IMPORT_RE.finditer(text):
            errors.append(f"banned import in {rel}: {match.group(1)}")
        if TOOL_CALL_RE.search(text):
            errors.append(f"script/runtime may invoke vendor/package/build tools: {rel}")


def validate_scripts(root: Path, errors: list[str]) -> None:
    commands = [
        ["python", "scripts/integrate_h5_vendor_update_review.py", "--input-dir", "examples/connectors/h5_vendor_update_driver/replay_results", "--check"],
        ["python", "scripts/summarize_h5_vendor_update_quality_delta.py", "--input-dir", "examples/connectors/h5_vendor_update_driver/review_integration", "--check"],
        ["python", "scripts/audit_h5_vendor_update_driver_wave.py", "--check"],
    ]
    for command in commands:
        proc = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
        if proc.returncode != 0:
            errors.append(f"script failed: {' '.join(command)} :: {proc.stdout.strip()} {proc.stderr.strip()}".strip())
    forbidden_commands = [
        ["python", "scripts/integrate_h5_vendor_update_review.py", "--input-dir", "examples/connectors/h5_vendor_update_driver/replay_results", "--output-dir", "site/dist/h5", "--json"],
        ["python", "scripts/summarize_h5_vendor_update_quality_delta.py", "--input-dir", "examples/connectors/h5_vendor_update_driver/review_integration", "--output", "data/public_index/h5.json", "--json"],
        ["python", "scripts/audit_h5_vendor_update_driver_wave.py", "--json-output", "firmware_staging/h5.json"],
    ]
    for command in forbidden_commands:
        proc = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
        if proc.returncode == 0:
            errors.append(f"forbidden output root unexpectedly allowed: {' '.join(command)}")
        if "refusing" not in (proc.stdout + proc.stderr):
            errors.append(f"forbidden output root did not report refusal: {' '.join(command)}")


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "vendor_downloads", "firmware_staging", "package_cache"):
        if (root / rel).exists():
            errors.append(f"local private or artifact root must not exist: {rel}")


def validate_boundaries(payload: Mapping[str, Any], label: str, errors: list[str]) -> None:
    errors.extend(f"{label}: {item}" for item in detect_h5_review_truth_boundary_violations(payload))
    errors.extend(f"{label}: {item}" for item in detect_h5_review_product_boundary_violations(payload))


def validate_no_secret_text(path: Path, errors: list[str]) -> None:
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    if SECRET_KEY_RE.search(text):
        errors.append(f"secret-like key in {path.as_posix()}")


def load_json_object(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"missing JSON file: {path.as_posix()}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {path.as_posix()}: {exc}")
        return {}
    if not isinstance(payload, Mapping):
        errors.append(f"JSON file must contain object: {path.as_posix()}")
        return {}
    return dict(payload)


if __name__ == "__main__":
    raise SystemExit(main())

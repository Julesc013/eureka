#!/usr/bin/env python3
"""Validate H11-BUNDLE-04 review, quality delta, and audit artifacts offline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from archive.prototypes.legacy_runtime.connectors.h11_storefront.quality_delta import detect_h11_quality_overclaim  # noqa: E402
from archive.prototypes.legacy_runtime.connectors.h11_storefront.review_integration import (  # noqa: E402
    detect_h11_review_product_boundary_violations,
    detect_h11_review_truth_boundary_violations,
)

AUDIT_DIR = Path("control/audits/h11-bundle-04-storefront-review-quality-audit-v0")
REVIEW_DIR = Path("examples/connectors/h11_storefront/review_integration")
REQUIRED_JSON = (
    "contracts/schema/control/audits/h11/connectors/storefront_review_integration_result.v0.json",
    "contracts/schema/control/audits/h11/connectors/storefront_quality_delta_report.v0.json",
    "contracts/schema/control/audits/h11/connectors/storefront_connector_wave_postmortem.v0.json",
    "contracts/schema/control/audits/h11/connectors/storefront_integration_audit.v0.json",
    "contracts/schema/control/tasks/h11/connectors/storefront_next_phase_recommendation.v0.json",
    "control/inventory/connectors/h11_storefront_review_integration_policy.json",
    "control/inventory/connectors/h11_storefront_review_output_policy.json",
    "control/inventory/connectors/h11_storefront_review_path_policy.json",
    "control/inventory/connectors/h11_storefront_review_truth_policy.json",
    "control/inventory/connectors/h11_storefront_quality_delta_policy.json",
    "control/inventory/connectors/h11_storefront_connector_wave_postmortem_policy.json",
    "control/inventory/connectors/h11_storefront_integration_audit_policy.json",
    "control/inventory/connectors/h11_storefront_next_phase_policy.json",
    (AUDIT_DIR / "h11_bundle_04_report.json").as_posix(),
)
REQUIRED_EXAMPLES = (
    "h11_storefront_listing_identity_review_seed_v0.json",
    "h11_app_product_identity_review_seed_v0.json",
    "h11_version_release_channel_review_seed_v0.json",
    "h11_price_availability_region_review_seed_v0.json",
    "h11_acquisition_path_review_seed_v0.json",
    "h11_review_rating_metadata_review_seed_v0.json",
    "h11_account_entitlement_boundary_review_seed_v0.json",
    "h11_storefront_rights_safety_review_seed_v0.json",
    "h11_source_cache_review_seed_v0.json",
    "h11_evidence_candidate_review_seed_v0.json",
    "h11_candidate_promotion_preview_v0.json",
    "h11_source_coverage_update_preview_v0.json",
    "h11_connector_scorecard_update_v0.json",
    "h11_source_pack_update_preview_v0.json",
    "h11_quality_delta_report_v0.json",
    "h11_connector_wave_postmortem_v0.json",
    "h11_blocked_review_integration_v0.json",
    "h11_review_integration_result_v0.json",
    "h11_next_phase_recommendation_v0.json",
    "h11_integration_audit_v0.json",
)
REQUIRED_AUDIT_FILES = (
    "README.md",
    "h11_bundle_04_report.json",
    "h11_review_integration_report.md",
    "h11_quality_delta_report.md",
    "h11_connector_wave_postmortem.md",
    "h11_integration_audit.md",
    "h11_exit_gate_decision.md",
    "next_phase_recommendation.md",
    "h12_readiness_review.md",
    "j1_risky_action_deferral_review.md",
    "k_semantic_ai_deferral_review.md",
    "l_wider_client_deferral_review.md",
    "validation.md",
    "generated/sample_h11_review_integration_result.json",
    "generated/sample_h11_quality_delta_report.json",
    "generated/sample_h11_connector_wave_postmortem.json",
    "generated/sample_h11_integration_audit.json",
    "generated/sample_h11_next_phase_recommendation.json",
    "generated/sample_h11_summary.md",
)
REQUIRED_DOCS = (
    "docs/reference/H11_STOREFRONT_REVIEW_INTEGRATION.md",
    "docs/reference/H11_STOREFRONT_QUALITY_DELTA_REPORT.md",
    "docs/reference/H11_STOREFRONT_CONNECTOR_WAVE_POSTMORTEM.md",
    "docs/architecture/H11_STOREFRONT_REVIEW_INTEGRATION_MODEL.md",
    "docs/operations/H11_STOREFRONT_WAVE_POSTMORTEM.md",
    "docs/operations/H11_STOREFRONT_WAVE_QUALITY_DELTA.md",
    "docs/operations/H11_TO_H12_HANDOFF.md",
    "docs/operations/H11_TO_J1_K_L_DEFERRAL.md",
)
PYTHON_SCAN_PATHS = (
    "archive/prototypes/legacy_runtime/connectors/h11_storefront/review_integration.py",
    "archive/prototypes/legacy_runtime/connectors/h11_storefront/quality_delta.py",
    "archive/prototypes/legacy_runtime/connectors/h11_storefront/wave_postmortem.py",
    "scripts/integrate_h11_storefront_review.py",
    "scripts/summarize_h11_storefront_quality_delta.py",
    "scripts/audit_h11_storefront_wave.py",
    "scripts/validate_h11_storefront_review_quality_audit.py",
)
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|urllib|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)
FORBIDDEN_TEXT_RE = re.compile(r"(private_key|api[_-]?token|access[_-]?token|cookie|receipt_payload|license_key_payload|entitlement_payload|payment_payload|installer_payload|download_payload|checkout_output|purchase_output)", re.IGNORECASE)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit validation JSON.")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("H11 storefront review quality audit validation", file=stdout)
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
        "schema_version": "h11_review_quality_audit_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "H11-BUNDLE-04",
        "offline_default": True,
        "network_calls_made": False,
        "query_fetch_download_account_purchase_entitlement_install_launch_used": False,
        "restricted_source_access_used": False,
        "errors": errors,
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    review = payloads.get("control/inventory/connectors/h11_storefront_review_integration_policy.json", {})
    for key in (
        "live_call_allowed_by_default", "source_cache_persistence_enabled",
        "evidence_acceptance_enabled", "candidate_acceptance_enabled",
        "listing_identity_truth_acceptance_enabled", "app_product_truth_acceptance_enabled",
        "version_release_truth_acceptance_enabled", "price_availability_truth_acceptance_enabled",
        "acquisition_permission_acceptance_enabled", "review_rating_truth_acceptance_enabled",
        "account_entitlement_truth_acceptance_enabled", "rights_safety_truth_acceptance_enabled",
        "public_index_mutation_allowed", "master_index_mutation_allowed",
        "api_catalog_query_enabled", "product_page_fetch_enabled",
        "download_account_purchase_entitlement_install_launch_enabled",
        "review_rating_write_enabled", "scraping_crawling_enabled",
        "restricted_source_access_enabled",
    ):
        if review.get(key) is not False:
            errors.append(f"h11 review policy {key} must be false")
    output = payloads.get("control/inventory/connectors/h11_storefront_review_output_policy.json", {})
    for key in (
        "accepted_listing_identity_truth", "accepted_app_product_truth",
        "accepted_version_release_truth", "accepted_price_availability_truth",
        "accepted_acquisition_permission", "accepted_review_rating_truth",
        "accepted_account_entitlement_truth", "accepted_rights_safety_truth",
        "accepted_source_truth", "accepted_evidence_truth", "accepted_candidate_truth",
        "accepted_public_record", "public_index_mutation", "master_index_mutation",
        "api_catalog_sync_permission", "product_page_fetch_permission",
        "download_permission", "account_access_permission", "purchase_permission",
        "checkout_permission", "entitlement_verification_permission",
        "install_launch_permission", "review_rating_write_permission",
        "scraping_crawling_permission", "restricted_source_access_permission",
        "source_sync_enablement", "production_readiness_claim",
    ):
        if key not in output.get("forbidden_outputs", []):
            errors.append(f"h11 review output policy must forbid {key}")
    audit = payloads.get("control/inventory/connectors/h11_storefront_integration_audit_policy.json", {})
    if "READY_FOR_H12_BUNDLE_01" not in audit.get("next_phase_values", []):
        errors.append("H11 audit policy must allow READY_FOR_H12_BUNDLE_01")
    next_phase = payloads.get("control/inventory/connectors/h11_storefront_next_phase_policy.json", {})
    if next_phase.get("j1_risky_actions_deferred") is not True or next_phase.get("k_semantic_ai_deferred") is not True or next_phase.get("l_wider_clients_deferred") is not True:
        errors.append("H11 next phase policy must defer J1/K/L")


def validate_docs(root: Path, errors: list[str]) -> None:
    for rel in REQUIRED_DOCS:
        if not (root / rel).is_file():
            errors.append(f"missing doc: {rel}")


def validate_examples(root: Path, errors: list[str]) -> None:
    for name in REQUIRED_EXAMPLES:
        path = root / REVIEW_DIR / name
        payload = load_json_object(path, errors)
        validate_boundaries(payload, f"example {name}", errors)
        validate_no_forbidden_text(path, errors)
    delta = load_json_object(root / REVIEW_DIR / "h11_quality_delta_report_v0.json", errors)
    errors.extend(detect_h11_quality_overclaim(delta))
    postmortem = load_json_object(root / REVIEW_DIR / "h11_connector_wave_postmortem_v0.json", errors)
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
    report = load_json_object(root / AUDIT_DIR / "h11_bundle_04_report.json", errors)
    if report.get("h11_exit_gate") not in {"PASS", "PASS_WITH_WARNINGS", "PARTIAL", "BLOCKED", "FAIL"}:
        errors.append("H11 report must have explicit h11_exit_gate")
    if report.get("next_phase_recommendation") not in {"READY_FOR_H12_BUNDLE_01", "READY_WITH_WARNINGS"}:
        errors.append("H11 report should recommend H12 when fixture-equivalent outputs are sufficient")
    validate_boundaries(report, "h11_bundle_04_report", errors)


def validate_python_imports(root: Path, errors: list[str]) -> None:
    for rel in PYTHON_SCAN_PATHS:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing Python file: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        if BANNED_IMPORT_RE.search(text):
            errors.append(f"{rel}: imports network/provider/browser library")


def validate_scripts(root: Path, errors: list[str]) -> None:
    commands = [
        [sys.executable, "scripts/integrate_h11_storefront_review.py", "--input-dir", "examples/connectors/h11_storefront/replay_results", "--check"],
        [sys.executable, "scripts/summarize_h11_storefront_quality_delta.py", "--input-dir", "examples/connectors/h11_storefront/review_integration", "--check"],
        [sys.executable, "scripts/audit_h11_storefront_wave.py", "--check"],
    ]
    for command in commands:
        proc = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
        if proc.returncode != 0:
            errors.append(f"script failed: {' '.join(command)} :: {proc.stdout}{proc.stderr}")
    forbidden_checks = [
        [sys.executable, "scripts/integrate_h11_storefront_review.py", "--input-dir", "examples/connectors/h11_storefront/replay_results", "--output-dir", "site/dist/h11"],
        [sys.executable, "scripts/summarize_h11_storefront_quality_delta.py", "--input-dir", "examples/connectors/h11_storefront/review_integration", "--output", "site/dist/data/public_index/h11.json"],
        [sys.executable, "scripts/audit_h11_storefront_wave.py", "--json-output", "accounts/h11.json"],
    ]
    for command in forbidden_checks:
        proc = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
        if proc.returncode == 0 or "refusing" not in (proc.stdout + proc.stderr):
            errors.append(f"forbidden output root was not rejected: {' '.join(command)}")


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "accounts", "receipts", "entitlements", "storefront_libraries", "app_downloads", "game_downloads", "package_downloads", "checkout_sessions", "install_actions"):
        if (root / rel).exists():
            errors.append(f"local private or storefront action root must not exist: {rel}")


def validate_boundaries(payload: Mapping[str, Any], label: str, errors: list[str]) -> None:
    errors.extend(f"{label}: {error}" for error in detect_h11_review_truth_boundary_violations(payload))
    errors.extend(f"{label}: {error}" for error in detect_h11_review_product_boundary_violations(payload))


def validate_no_forbidden_text(path: Path, errors: list[str]) -> None:
    if path.is_file() and FORBIDDEN_TEXT_RE.search(path.read_text(encoding="utf-8")):
        errors.append(f"forbidden credential/private/payload marker in {path}")


def load_json_object(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"missing JSON file: {path}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {path}: {exc}")
        return {}
    if not isinstance(payload, Mapping):
        errors.append(f"{path} must contain a JSON object")
        return {}
    return dict(payload)


if __name__ == "__main__":
    raise SystemExit(main())

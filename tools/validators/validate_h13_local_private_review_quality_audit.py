#!/usr/bin/env python3
"""Validate H13-BUNDLE-04 review, quality delta, and audit artifacts offline."""

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

from archive.prototypes.legacy_runtime.connectors.h13_local_private.quality_delta import detect_h13_quality_overclaim  # noqa: E402
from archive.prototypes.legacy_runtime.connectors.h13_local_private.review_integration import (  # noqa: E402
    detect_h13_review_private_data_violations,
    detect_h13_review_product_boundary_violations,
    detect_h13_review_truth_boundary_violations,
)

AUDIT_DIR = Path("control/audits/h13-bundle-04-local-private-review-quality-audit-v0")
REVIEW_DIR = Path("examples/connectors/h13_local_private/review_integration")
REQUIRED_JSON = (
    "contracts/schema/control/audits/h13/connectors/local_private_review_integration_result.v0.json",
    "contracts/schema/control/audits/h13/connectors/local_private_quality_delta_report.v0.json",
    "contracts/schema/control/audits/h13/connectors/local_private_connector_wave_postmortem.v0.json",
    "contracts/schema/control/audits/h13/connectors/local_private_integration_audit.v0.json",
    "contracts/schema/control/tasks/h13/connectors/local_private_next_phase_recommendation.v0.json",
    "control/inventory/connectors/h13_local_private_review_integration_policy.json",
    "control/inventory/connectors/h13_local_private_review_output_policy.json",
    "control/inventory/connectors/h13_local_private_review_path_policy.json",
    "control/inventory/connectors/h13_local_private_review_truth_policy.json",
    "control/inventory/connectors/h13_local_private_quality_delta_policy.json",
    "control/inventory/connectors/h13_local_private_connector_wave_postmortem_policy.json",
    "control/inventory/connectors/h13_local_private_integration_audit_policy.json",
    "control/inventory/connectors/h13_local_private_next_phase_policy.json",
    (AUDIT_DIR / "h13_bundle_04_report.json").as_posix(),
)
REQUIRED_EXAMPLES = (
    "h13_local_source_identity_review_seed_v0.json",
    "h13_private_source_boundary_review_seed_v0.json",
    "h13_user_supplied_url_boundary_review_seed_v0.json",
    "h13_authenticated_source_boundary_review_seed_v0.json",
    "h13_restricted_source_manifest_review_seed_v0.json",
    "h13_local_cas_import_boundary_review_seed_v0.json",
    "h13_pack_export_import_boundary_review_seed_v0.json",
    "h13_privacy_redaction_review_seed_v0.json",
    "h13_local_private_rights_safety_review_seed_v0.json",
    "h13_source_cache_review_seed_v0.json",
    "h13_evidence_candidate_review_seed_v0.json",
    "h13_candidate_promotion_preview_v0.json",
    "h13_source_coverage_update_preview_v0.json",
    "h13_connector_scorecard_update_v0.json",
    "h13_source_pack_update_preview_v0.json",
    "h13_quality_delta_report_v0.json",
    "h13_connector_wave_postmortem_v0.json",
    "h13_blocked_review_integration_v0.json",
    "h13_review_integration_result_v0.json",
    "h13_next_phase_recommendation_v0.json",
    "h13_integration_audit_v0.json",
)
REQUIRED_AUDIT_FILES = (
    "README.md",
    "h13_bundle_04_report.json",
    "h13_review_integration_report.md",
    "h13_quality_delta_report.md",
    "h13_connector_wave_postmortem.md",
    "h13_integration_audit.md",
    "h13_exit_gate_decision.md",
    "next_phase_recommendation.md",
    "h14_readiness_review.md",
    "f_deep_extraction_deferral_review.md",
    "i_pack_federation_deferral_review.md",
    "j_risky_action_deferral_review.md",
    "k_semantic_ai_deferral_review.md",
    "l_wider_client_deferral_review.md",
    "validation.md",
    "generated/sample_h13_review_integration_result.json",
    "generated/sample_h13_quality_delta_report.json",
    "generated/sample_h13_connector_wave_postmortem.json",
    "generated/sample_h13_integration_audit.json",
    "generated/sample_h13_next_phase_recommendation.json",
    "generated/sample_h13_summary.md",
)
REQUIRED_DOCS = (
    "docs/reference/H13_LOCAL_PRIVATE_REVIEW_INTEGRATION.md",
    "docs/reference/H13_LOCAL_PRIVATE_QUALITY_DELTA_REPORT.md",
    "docs/reference/H13_LOCAL_PRIVATE_CONNECTOR_WAVE_POSTMORTEM.md",
    "docs/architecture/H13_LOCAL_PRIVATE_REVIEW_INTEGRATION_MODEL.md",
    "docs/operations/H13_LOCAL_PRIVATE_WAVE_POSTMORTEM.md",
    "docs/operations/H13_LOCAL_PRIVATE_WAVE_QUALITY_DELTA.md",
    "docs/operations/H13_TO_H14_HANDOFF.md",
    "docs/operations/H13_TO_F_I_J_K_L_DEFERRAL.md",
)
PYTHON_SCAN_PATHS = (
    "archive/prototypes/legacy_runtime/connectors/h13_local_private/review_integration.py",
    "archive/prototypes/legacy_runtime/connectors/h13_local_private/quality_delta.py",
    "archive/prototypes/legacy_runtime/connectors/h13_local_private/wave_postmortem.py",
    "scripts/integrate_h13_local_private_review.py",
    "scripts/summarize_h13_local_private_quality_delta.py",
    "scripts/audit_h13_local_private_wave.py",
    "scripts/validate_h13_local_private_review_quality_audit.py",
)
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|urllib|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)
FORBIDDEN_TEXT_RE = re.compile(r"(api[_-]?token|access[_-]?token|private_file_payload_included\"\\s*:\\s*true|local_file_content_included\"\\s*:\\s*true|cas_blob_included\"\\s*:\\s*true|exported_pack_included\"\\s*:\\s*true|imported_pack_included\"\\s*:\\s*true|source_cache_write_included\"\\s*:\\s*true|evidence_write_included\"\\s*:\\s*true|public_index_write_included\"\\s*:\\s*true)", re.IGNORECASE)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit validation JSON.")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("H13 local/private review quality audit validation", file=stdout)
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
        "schema_version": "h13_review_quality_audit_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "H13-BUNDLE-04",
        "offline_default": True,
        "network_calls_made": False,
        "local_private_restricted_access_used": False,
        "errors": errors,
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    review = payloads.get("control/inventory/connectors/h13_local_private_review_integration_policy.json", {})
    for key in (
        "new_boundary_dry_runs_enabled", "local_access_enabled",
        "private_source_access_enabled", "user_supplied_url_fetch_enabled",
        "authenticated_source_access_enabled", "restricted_source_access_enabled",
        "network_access_enabled", "external_api_enabled", "model_provider_enabled",
        "filesystem_scan_enabled", "directory_listing_enabled", "archive_listing_enabled",
        "account_access_enabled", "credential_handling_enabled",
        "local_cas_import_enabled", "pack_export_enabled", "pack_import_enabled",
        "source_cache_write_enabled", "evidence_write_enabled",
        "review_queue_write_enabled", "public_index_write_enabled",
        "master_index_write_enabled", "extraction_enabled", "execution_enabled",
        "acquisition_action_enabled", "upload_enabled", "publication_enabled",
        "truth_acceptance_enabled",
    ):
        if review.get(key) is not False:
            errors.append(f"h13 review policy {key} must be false")
    output = payloads.get("control/inventory/connectors/h13_local_private_review_output_policy.json", {})
    for key in ['accepted_local_source_identity_truth', 'accepted_private_source_truth', 'accepted_user_supplied_url_truth', 'accepted_authenticated_source_truth', 'accepted_restricted_source_truth', 'accepted_cas_import_truth', 'accepted_pack_export_import_truth', 'accepted_privacy_redaction_truth', 'accepted_rights_safety_truth', 'accepted_source_truth', 'accepted_evidence_truth', 'accepted_candidate_truth', 'accepted_public_record', 'public_index_mutation', 'master_index_mutation', 'local_access_permission', 'private_source_access_permission', 'user_supplied_url_fetch_permission', 'authenticated_access_permission', 'restricted_source_access_permission', 'cas_import_permission', 'pack_export_import_permission', 'source_cache_write_permission', 'evidence_write_permission', 'publication_permission', 'source_sync_enablement', 'production_readiness_claim', 'rights_clearance', 'ownership_truth', 'user_authority_truth', 'legal_access_truth', 'account_entitlement_truth', 'privacy_safety', 'malware_safety', 'source_safety_truth', 'verified_authenticity']:
        if key not in output.get("forbidden_outputs", []):
            errors.append(f"h13 review output policy must forbid {key}")
    audit = payloads.get("control/inventory/connectors/h13_local_private_integration_audit_policy.json", {})
    if "READY_FOR_H14_BUNDLE_01" not in audit.get("next_phase_values", []):
        errors.append("H13 audit policy must allow READY_FOR_H14_BUNDLE_01")
    next_phase = payloads.get("control/inventory/connectors/h13_local_private_next_phase_policy.json", {})
    for key in ("f_deep_extraction_deferred", "i_federation_private_pack_export_deferred", "j_risky_actions_deferred", "k_semantic_ai_deferred", "l_wider_clients_deferred"):
        if next_phase.get(key) is not True:
            errors.append(f"H13 next phase policy must defer {key}")


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
    delta = load_json_object(root / REVIEW_DIR / "h13_quality_delta_report_v0.json", errors)
    errors.extend(detect_h13_quality_overclaim(delta))
    postmortem = load_json_object(root / REVIEW_DIR / "h13_connector_wave_postmortem_v0.json", errors)
    if postmortem.get("auto_approves_future_connectors") is not False:
        errors.append("postmortem must not auto-approve future connectors")
    if postmortem.get("auto_approves_access_import_export_publication") is not False:
        errors.append("postmortem must not auto-approve access/import/export/publication")


def validate_audit_files(root: Path, errors: list[str]) -> None:
    for rel_name in REQUIRED_AUDIT_FILES:
        if not (root / AUDIT_DIR / rel_name).is_file():
            errors.append(f"missing audit file: {(AUDIT_DIR / rel_name).as_posix()}")


def validate_generated_outputs(root: Path, errors: list[str]) -> None:
    for rel_name in REQUIRED_AUDIT_FILES:
        if rel_name.startswith("generated/") and rel_name.endswith(".json"):
            payload = load_json_object(root / AUDIT_DIR / rel_name, errors)
            validate_boundaries(payload, rel_name, errors)
    report = load_json_object(root / AUDIT_DIR / "h13_bundle_04_report.json", errors)
    if report.get("h13_exit_gate") not in {"PASS", "PASS_WITH_WARNINGS", "PARTIAL", "BLOCKED", "FAIL"}:
        errors.append("H13 report must have explicit h13_exit_gate")
    if report.get("next_phase_recommendation") not in {"READY_FOR_H14_BUNDLE_01", "READY_WITH_WARNINGS"}:
        errors.append("H13 report should recommend H14 when fixture-equivalent outputs are sufficient")
    validate_boundaries(report, "h13_bundle_04_report", errors)


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
        [sys.executable, "scripts/integrate_h13_local_private_review.py", "--input-dir", "examples/connectors/h13_local_private/replay_results", "--check"],
        [sys.executable, "scripts/summarize_h13_local_private_quality_delta.py", "--input-dir", "examples/connectors/h13_local_private/review_integration", "--check"],
        [sys.executable, "scripts/audit_h13_local_private_wave.py", "--check"],
    ]
    for command in commands:
        proc = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
        if proc.returncode != 0:
            errors.append(f"script failed: {' '.join(command)} :: {proc.stdout}{proc.stderr}")
    forbidden_checks = [
        [sys.executable, "scripts/integrate_h13_local_private_review.py", "--input-dir", "examples/connectors/h13_local_private/replay_results", "--output-dir", "site/dist/h13"],
        [sys.executable, "scripts/summarize_h13_local_private_quality_delta.py", "--input-dir", "examples/connectors/h13_local_private/review_integration", "--output", "site/dist/data/public_index/h13.json"],
        [sys.executable, "scripts/audit_h13_local_private_wave.py", "--json-output", ".local/eureka/h13.json"],
    ]
    for command in forbidden_checks:
        proc = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
        if proc.returncode == 0 or "refusing" not in (proc.stdout + proc.stderr):
            errors.append(f"forbidden output root was not rejected: {' '.join(command)}")


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "local_sources", "private_sources", "cas", "cas_roots", "credential_roots", "account_roots", "user_url_fetch", "import_export_staging", "archive_extractions", "source_cache", "evidence_ledger"):
        if (root / rel).exists():
            errors.append(f"local private or action root must not exist: {rel}")


def validate_boundaries(payload: Mapping[str, Any], label: str, errors: list[str]) -> None:
    errors.extend(f"{label}: {error}" for error in detect_h13_review_truth_boundary_violations(payload))
    errors.extend(f"{label}: {error}" for error in detect_h13_review_product_boundary_violations(payload))
    errors.extend(f"{label}: {error}" for error in detect_h13_review_private_data_violations(payload))


def validate_no_forbidden_text(path: Path, errors: list[str]) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if FORBIDDEN_TEXT_RE.search(text):
        errors.append(f"{path.relative_to(REPO_ROOT).as_posix()}: contains forbidden private/payload marker")


def load_json_object(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"missing JSON file: {path.relative_to(REPO_ROOT).as_posix() if path.is_absolute() else path.as_posix()}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {path}: {exc}")
        return {}
    if not isinstance(payload, Mapping):
        errors.append(f"JSON file must contain object: {path}")
        return {}
    return dict(payload)


if __name__ == "__main__":
    raise SystemExit(main())

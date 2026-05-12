#!/usr/bin/env python3
"""Validate H8-BUNDLE-04 review, quality delta, and audit artifacts offline."""

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

from runtime.connectors.h8_manuals_docs_standards.quality_delta import detect_h8_quality_overclaim  # noqa: E402
from runtime.connectors.h8_manuals_docs_standards.review_integration import (  # noqa: E402
    detect_h8_review_product_boundary_violations,
    detect_h8_review_truth_boundary_violations,
)

AUDIT_DIR = Path("control/audits/h8-bundle-04-manuals-docs-review-quality-audit-v0")
REVIEW_DIR = Path("examples/connectors/h8_manuals_docs_standards/review_integration")
REQUIRED_JSON = (
    "control/schemas/audits/h8/connectors/manuals_docs_review_integration_result.v0.json",
    "control/schemas/audits/h8/connectors/manuals_docs_quality_delta_report.v0.json",
    "control/schemas/audits/h8/connectors/manuals_docs_connector_wave_postmortem.v0.json",
    "control/schemas/audits/h8/connectors/manuals_docs_integration_audit.v0.json",
    "control/schemas/tasks/h8/connectors/manuals_docs_next_phase_recommendation.v0.json",
    "control/inventory/connectors/h8_manuals_docs_review_integration_policy.json",
    "control/inventory/connectors/h8_manuals_docs_review_output_policy.json",
    "control/inventory/connectors/h8_manuals_docs_review_path_policy.json",
    "control/inventory/connectors/h8_manuals_docs_review_truth_policy.json",
    "control/inventory/connectors/h8_manuals_docs_quality_delta_policy.json",
    "control/inventory/connectors/h8_manuals_docs_connector_wave_postmortem_policy.json",
    "control/inventory/connectors/h8_manuals_docs_integration_audit_policy.json",
    "control/inventory/connectors/h8_manuals_docs_next_phase_policy.json",
    (AUDIT_DIR / "h8_bundle_04_report.json").as_posix(),
)
REQUIRED_EXAMPLES = (
    "h8_technical_document_identity_review_seed_v0.json",
    "h8_manual_artifact_relation_review_seed_v0.json",
    "h8_datasheet_device_identity_review_seed_v0.json",
    "h8_standards_specification_identity_review_seed_v0.json",
    "h8_install_requirement_claim_review_seed_v0.json",
    "h8_repair_service_safety_review_seed_v0.json",
    "h8_access_rights_review_seed_v0.json",
    "h8_source_cache_review_seed_v0.json",
    "h8_evidence_candidate_review_seed_v0.json",
    "h8_candidate_promotion_preview_v0.json",
    "h8_source_coverage_update_preview_v0.json",
    "h8_connector_scorecard_update_v0.json",
    "h8_source_pack_update_preview_v0.json",
    "h8_quality_delta_report_v0.json",
    "h8_connector_wave_postmortem_v0.json",
    "h8_blocked_review_integration_v0.json",
    "h8_review_integration_result_v0.json",
    "h8_next_phase_recommendation_v0.json",
    "h8_integration_audit_v0.json",
)
REQUIRED_AUDIT_FILES = (
    "README.md",
    "h8_bundle_04_report.json",
    "h8_review_integration_report.md",
    "h8_quality_delta_report.md",
    "h8_connector_wave_postmortem.md",
    "h8_integration_audit.md",
    "h8_exit_gate_decision.md",
    "next_phase_recommendation.md",
    "h9_readiness_review.md",
    "j1_risky_action_deferral_review.md",
    "k_semantic_ai_deferral_review.md",
    "l_wider_client_deferral_review.md",
    "validation.md",
    "generated/sample_h8_review_integration_result.json",
    "generated/sample_h8_quality_delta_report.json",
    "generated/sample_h8_connector_wave_postmortem.json",
    "generated/sample_h8_integration_audit.json",
    "generated/sample_h8_next_phase_recommendation.json",
    "generated/sample_h8_summary.md",
)
REQUIRED_DOCS = (
    "docs/reference/H8_MANUALS_DOCS_REVIEW_INTEGRATION.md",
    "docs/reference/H8_MANUALS_DOCS_QUALITY_DELTA_REPORT.md",
    "docs/reference/H8_MANUALS_DOCS_CONNECTOR_WAVE_POSTMORTEM.md",
    "docs/architecture/H8_MANUALS_DOCS_REVIEW_INTEGRATION_MODEL.md",
    "docs/operations/H8_MANUALS_DOCS_WAVE_POSTMORTEM.md",
    "docs/operations/H8_MANUALS_DOCS_WAVE_QUALITY_DELTA.md",
    "docs/operations/H8_TO_H9_HANDOFF.md",
    "docs/operations/H8_TO_J1_K_L_DEFERRAL.md",
)
PYTHON_SCAN_PATHS = (
    "runtime/connectors/h8_manuals_docs_standards/review_integration.py",
    "runtime/connectors/h8_manuals_docs_standards/quality_delta.py",
    "runtime/connectors/h8_manuals_docs_standards/wave_postmortem.py",
    "scripts/integrate_h8_manuals_docs_review.py",
    "scripts/summarize_h8_manuals_docs_quality_delta.py",
    "scripts/audit_h8_manuals_docs_standards_wave.py",
    "scripts/validate_h8_manuals_docs_review_quality_audit.py",
)
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|urllib|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)
FORBIDDEN_TEXT_RE = re.compile(r"(payload_body|private_key|api[_-]?token|access[_-]?token|cookie)", re.IGNORECASE)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit validation JSON.")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("H8 manuals/docs/standards review quality audit validation", file=stdout)
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
        "schema_version": "h8_review_quality_audit_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "H8-BUNDLE-04",
        "offline_default": True,
        "network_calls_made": False,
        "query_fetch_download_extract_used": False,
        "restricted_source_access_used": False,
        "errors": errors,
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    review = payloads.get("control/inventory/connectors/h8_manuals_docs_review_integration_policy.json", {})
    for key in (
        "live_call_allowed_by_default",
        "source_cache_persistence_enabled",
        "evidence_acceptance_enabled",
        "candidate_acceptance_enabled",
        "document_truth_acceptance_enabled",
        "manual_artifact_relation_truth_acceptance_enabled",
        "datasheet_device_truth_acceptance_enabled",
        "standards_truth_acceptance_enabled",
        "install_requirement_truth_acceptance_enabled",
        "repair_service_safety_truth_acceptance_enabled",
        "access_rights_truth_acceptance_enabled",
        "public_index_mutation_allowed",
        "master_index_mutation_allowed",
        "api_catalog_query_enabled",
        "document_fetch_enabled",
        "downloads_enabled",
        "full_text_ocr_enabled",
        "scraping_crawling_enabled",
        "restricted_source_access_enabled",
        "repair_or_install_action_permission_enabled",
    ):
        if review.get(key) is not False:
            errors.append(f"h8 review policy {key} must be false")
    output = payloads.get("control/inventory/connectors/h8_manuals_docs_review_output_policy.json", {})
    for key in (
        "accepted_document_truth",
        "accepted_manual_artifact_relation_truth",
        "accepted_datasheet_device_truth",
        "accepted_standards_truth",
        "accepted_install_requirement_truth",
        "accepted_repair_service_safety_truth",
        "accepted_access_rights_truth",
        "accepted_source_truth",
        "accepted_evidence_truth",
        "accepted_candidate_truth",
        "accepted_public_record",
        "public_index_mutation",
        "master_index_mutation",
        "api_catalog_sync_permission",
        "document_fetch_permission",
        "download_permission",
        "full_text_ocr_permission",
        "scraping_crawling_permission",
        "restricted_source_access_permission",
        "repair_or_install_action_permission",
        "production_readiness_claim",
    ):
        if key not in output.get("forbidden_outputs", []):
            errors.append(f"h8 review output policy must forbid {key}")
    audit = payloads.get("control/inventory/connectors/h8_manuals_docs_integration_audit_policy.json", {})
    if "READY_FOR_H9_BUNDLE_01" not in audit.get("next_phase_values", []):
        errors.append("H8 audit policy must allow READY_FOR_H9_BUNDLE_01")
    next_phase = payloads.get("control/inventory/connectors/h8_manuals_docs_next_phase_policy.json", {})
    if next_phase.get("j1_risky_actions_deferred") is not True or next_phase.get("k_semantic_ai_deferred") is not True or next_phase.get("l_wider_clients_deferred") is not True:
        errors.append("H8 next phase policy must defer J1/K/L")


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
    delta = load_json_object(root / REVIEW_DIR / "h8_quality_delta_report_v0.json", errors)
    errors.extend(detect_h8_quality_overclaim(delta))
    postmortem = load_json_object(root / REVIEW_DIR / "h8_connector_wave_postmortem_v0.json", errors)
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
    report = load_json_object(root / AUDIT_DIR / "h8_bundle_04_report.json", errors)
    if report.get("h8_exit_gate") not in {"PASS", "PASS_WITH_WARNINGS", "PARTIAL", "BLOCKED", "FAIL"}:
        errors.append("H8 report must have explicit h8_exit_gate")
    if report.get("next_phase_recommendation") not in {"READY_FOR_H9_BUNDLE_01", "READY_WITH_WARNINGS"}:
        errors.append("H8 report should recommend H9 when fixture-equivalent outputs are sufficient")
    validate_boundaries(report, "h8_bundle_04_report", errors)


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
        ["python", "scripts/integrate_h8_manuals_docs_review.py", "--input-dir", "examples/connectors/h8_manuals_docs_standards/replay_results", "--check"],
        ["python", "scripts/summarize_h8_manuals_docs_quality_delta.py", "--input-dir", "examples/connectors/h8_manuals_docs_standards/review_integration", "--check"],
        ["python", "scripts/audit_h8_manuals_docs_standards_wave.py", "--check"],
    ]
    for command in commands:
        proc = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
        if proc.returncode != 0:
            errors.append(f"script failed: {' '.join(command)} :: {proc.stdout} {proc.stderr}".strip())
    forbidden = subprocess.run(
        ["python", "scripts/integrate_h8_manuals_docs_review.py", "--input-dir", "examples/connectors/h8_manuals_docs_standards/replay_results", "--output-dir", "site/dist/h8"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if forbidden.returncode == 0 or "refusing" not in (forbidden.stdout + forbidden.stderr):
        errors.append("integrate script must refuse site/dist output")


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "downloads", "document_downloads", "pdf_downloads", "manual_downloads", "datasheet_downloads", "standards_downloads", "schematic_downloads", "service_manual_downloads", "ocr", "full_text", "media_downloads", "restricted_sources", "repair_actions"):
        if (root / rel).exists():
            errors.append(f"forbidden local/private root exists: {rel}")


def validate_boundaries(payload: Mapping[str, Any], label: str, errors: list[str]) -> None:
    errors.extend(f"{label}: {item}" for item in detect_h8_review_truth_boundary_violations(payload))
    errors.extend(f"{label}: {item}" for item in detect_h8_review_product_boundary_violations(payload))


def validate_no_forbidden_text(path: Path, errors: list[str]) -> None:
    if path.exists() and FORBIDDEN_TEXT_RE.search(path.read_text(encoding="utf-8")):
        errors.append(f"forbidden payload/secret marker in {path.relative_to(REPO_ROOT)}")


def load_json_object(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"missing JSON: {path.relative_to(REPO_ROOT) if path.is_absolute() else path}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {path}: {exc}")
        return {}
    if not isinstance(payload, Mapping):
        errors.append(f"JSON must be object: {path}")
        return {}
    return dict(payload)


if __name__ == "__main__":
    raise SystemExit(main())

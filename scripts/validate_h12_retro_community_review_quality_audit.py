#!/usr/bin/env python3
"""Validate H12-BUNDLE-04 review, quality delta, and audit artifacts offline."""

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

from runtime.connectors.h12_retro_community.quality_delta import detect_h12_quality_overclaim  # noqa: E402
from runtime.connectors.h12_retro_community.review_integration import (  # noqa: E402
    detect_h12_review_product_boundary_violations,
    detect_h12_review_truth_boundary_violations,
)

AUDIT_DIR = Path("control/audits/h12-bundle-04-retro-community-review-quality-audit-v0")
REVIEW_DIR = Path("examples/connectors/h12_retro_community/review_integration")
REQUIRED_JSON = (
    "contracts/connectors/h12_retro_community_review_integration_result.v0.json",
    "contracts/connectors/h12_retro_community_quality_delta_report.v0.json",
    "contracts/connectors/h12_retro_community_connector_wave_postmortem.v0.json",
    "contracts/connectors/h12_retro_community_integration_audit.v0.json",
    "contracts/connectors/h12_retro_community_next_phase_recommendation.v0.json",
    "control/inventory/connectors/h12_retro_community_review_integration_policy.json",
    "control/inventory/connectors/h12_retro_community_review_output_policy.json",
    "control/inventory/connectors/h12_retro_community_review_path_policy.json",
    "control/inventory/connectors/h12_retro_community_review_truth_policy.json",
    "control/inventory/connectors/h12_retro_community_quality_delta_policy.json",
    "control/inventory/connectors/h12_retro_community_connector_wave_postmortem_policy.json",
    "control/inventory/connectors/h12_retro_community_integration_audit_policy.json",
    "control/inventory/connectors/h12_retro_community_next_phase_policy.json",
    (AUDIT_DIR / "h12_bundle_04_report.json").as_posix(),
)
REQUIRED_EXAMPLES = (
    "h12_retro_software_identity_review_seed_v0.json",
    "h12_platform_version_edition_review_seed_v0.json",
    "h12_archive_item_member_review_seed_v0.json",
    "h12_compatibility_install_note_review_seed_v0.json",
    "h12_community_review_comment_review_seed_v0.json",
    "h12_hash_checksum_review_seed_v0.json",
    "h12_ia_wayback_corroboration_review_seed_v0.json",
    "h12_gated_source_boundary_review_seed_v0.json",
    "h12_retro_rights_safety_review_seed_v0.json",
    "h12_source_cache_review_seed_v0.json",
    "h12_evidence_candidate_review_seed_v0.json",
    "h12_candidate_promotion_preview_v0.json",
    "h12_source_coverage_update_preview_v0.json",
    "h12_connector_scorecard_update_v0.json",
    "h12_source_pack_update_preview_v0.json",
    "h12_quality_delta_report_v0.json",
    "h12_connector_wave_postmortem_v0.json",
    "h12_blocked_review_integration_v0.json",
    "h12_review_integration_result_v0.json",
    "h12_next_phase_recommendation_v0.json",
    "h12_integration_audit_v0.json",
)
REQUIRED_AUDIT_FILES = (
    "README.md",
    "h12_bundle_04_report.json",
    "h12_review_integration_report.md",
    "h12_quality_delta_report.md",
    "h12_connector_wave_postmortem.md",
    "h12_integration_audit.md",
    "h12_exit_gate_decision.md",
    "next_phase_recommendation.md",
    "h13_readiness_review.md",
    "j1_risky_action_deferral_review.md",
    "k_semantic_ai_deferral_review.md",
    "l_wider_client_deferral_review.md",
    "validation.md",
    "generated/sample_h12_review_integration_result.json",
    "generated/sample_h12_quality_delta_report.json",
    "generated/sample_h12_connector_wave_postmortem.json",
    "generated/sample_h12_integration_audit.json",
    "generated/sample_h12_next_phase_recommendation.json",
    "generated/sample_h12_summary.md",
)
REQUIRED_DOCS = (
    "docs/reference/H12_RETRO_COMMUNITY_REVIEW_INTEGRATION.md",
    "docs/reference/H12_RETRO_COMMUNITY_QUALITY_DELTA_REPORT.md",
    "docs/reference/H12_RETRO_COMMUNITY_CONNECTOR_WAVE_POSTMORTEM.md",
    "docs/architecture/H12_RETRO_COMMUNITY_REVIEW_INTEGRATION_MODEL.md",
    "docs/operations/H12_RETRO_COMMUNITY_WAVE_POSTMORTEM.md",
    "docs/operations/H12_RETRO_COMMUNITY_WAVE_QUALITY_DELTA.md",
    "docs/operations/H12_TO_H13_HANDOFF.md",
    "docs/operations/H12_TO_J1_K_L_DEFERRAL.md",
)
PYTHON_SCAN_PATHS = (
    "runtime/connectors/h12_retro_community/review_integration.py",
    "runtime/connectors/h12_retro_community/quality_delta.py",
    "runtime/connectors/h12_retro_community/wave_postmortem.py",
    "scripts/integrate_h12_retro_community_review.py",
    "scripts/summarize_h12_retro_community_quality_delta.py",
    "scripts/audit_h12_retro_community_wave.py",
    "scripts/validate_h12_retro_community_review_quality_audit.py",
)
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|urllib|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)
FORBIDDEN_TEXT_RE = re.compile(r"(private_key|api[_-]?token|access[_-]?token|cookie|software_binary_payload|rom_payload|iso_payload|bios_firmware_payload|driver_payload|installer_payload|patch_payload|crack_key_serial_payload|download_payload|extraction_output|execution_output|acquisition_output|hash_submission_payload)", re.IGNORECASE)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit validation JSON.")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("H12 retro/community review quality audit validation", file=stdout)
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
        "schema_version": "h12_review_quality_audit_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "H12-BUNDLE-04",
        "offline_default": True,
        "network_calls_made": False,
        "query_fetch_download_extract_execute_acquire_upload_used": False,
        "restricted_source_access_used": False,
        "errors": errors,
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    review = payloads.get("control/inventory/connectors/h12_retro_community_review_integration_policy.json", {})
    for key in (
        "live_call_allowed_by_default", "source_cache_persistence_enabled",
        "evidence_acceptance_enabled", "candidate_acceptance_enabled",
        "retro_software_identity_truth_acceptance_enabled",
        "platform_version_truth_acceptance_enabled",
        "archive_item_member_truth_acceptance_enabled",
        "compatibility_install_truth_acceptance_enabled",
        "community_review_truth_acceptance_enabled",
        "hash_checksum_truth_acceptance_enabled",
        "ia_wayback_corroboration_truth_acceptance_enabled",
        "gated_source_access_truth_acceptance_enabled",
        "rights_safety_truth_acceptance_enabled",
        "public_index_mutation_allowed", "master_index_mutation_allowed",
        "api_catalog_query_enabled", "forum_or_gated_fetch_enabled",
        "download_extract_execute_acquire_upload_enabled",
        "hash_submission_enabled", "scraping_crawling_enabled",
        "restricted_source_access_enabled",
    ):
        if review.get(key) is not False:
            errors.append(f"h12 review policy {key} must be false")
    output = payloads.get("control/inventory/connectors/h12_retro_community_review_output_policy.json", {})
    for key in ['accepted_retro_software_identity_truth', 'accepted_platform_version_truth', 'accepted_archive_item_member_truth', 'accepted_compatibility_install_truth', 'accepted_community_review_truth', 'accepted_hash_checksum_truth', 'accepted_ia_wayback_corroboration_truth', 'accepted_gated_source_access_truth', 'accepted_rights_safety_truth', 'accepted_source_truth', 'accepted_evidence_truth', 'accepted_candidate_truth', 'accepted_public_record', 'public_index_mutation', 'master_index_mutation', 'api_catalog_sync_permission', 'forum_or_gated_fetch_permission', 'download_permission', 'extraction_permission', 'execution_permission', 'acquisition_action_permission', 'upload_permission', 'hash_submission_permission', 'scraping_crawling_permission', 'restricted_source_access_permission', 'source_sync_enablement', 'production_readiness_claim', 'rights_clearance', 'legal_acquisition_truth', 'file_authenticity_truth', 'checksum_correctness_truth', 'compatibility_correctness', 'installability_truth', 'playability_truth', 'malware_safety', 'content_safety_truth', 'privacy_safety', 'community_reputation_truth', 'verified_authenticity']:
        if key not in output.get("forbidden_outputs", []):
            errors.append(f"h12 review output policy must forbid {key}")
    audit = payloads.get("control/inventory/connectors/h12_retro_community_integration_audit_policy.json", {})
    if "READY_FOR_H13_BUNDLE_01" not in audit.get("next_phase_values", []):
        errors.append("H12 audit policy must allow READY_FOR_H13_BUNDLE_01")
    next_phase = payloads.get("control/inventory/connectors/h12_retro_community_next_phase_policy.json", {})
    if next_phase.get("j1_risky_actions_deferred") is not True or next_phase.get("k_semantic_ai_deferred") is not True or next_phase.get("l_wider_clients_deferred") is not True:
        errors.append("H12 next phase policy must defer J1/K/L")


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
    delta = load_json_object(root / REVIEW_DIR / "h12_quality_delta_report_v0.json", errors)
    errors.extend(detect_h12_quality_overclaim(delta))
    postmortem = load_json_object(root / REVIEW_DIR / "h12_connector_wave_postmortem_v0.json", errors)
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
    report = load_json_object(root / AUDIT_DIR / "h12_bundle_04_report.json", errors)
    if report.get("h12_exit_gate") not in {"PASS", "PASS_WITH_WARNINGS", "PARTIAL", "BLOCKED", "FAIL"}:
        errors.append("H12 report must have explicit h12_exit_gate")
    if report.get("next_phase_recommendation") not in {"READY_FOR_H13_BUNDLE_01", "READY_WITH_WARNINGS"}:
        errors.append("H12 report should recommend H13 when fixture-equivalent outputs are sufficient")
    validate_boundaries(report, "h12_bundle_04_report", errors)


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
        [sys.executable, "scripts/integrate_h12_retro_community_review.py", "--input-dir", "examples/connectors/h12_retro_community/replay_results", "--check"],
        [sys.executable, "scripts/summarize_h12_retro_community_quality_delta.py", "--input-dir", "examples/connectors/h12_retro_community/review_integration", "--check"],
        [sys.executable, "scripts/audit_h12_retro_community_wave.py", "--check"],
    ]
    for command in commands:
        proc = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
        if proc.returncode != 0:
            errors.append(f"script failed: {' '.join(command)} :: {proc.stdout}{proc.stderr}")
    forbidden_checks = [
        [sys.executable, "scripts/integrate_h12_retro_community_review.py", "--input-dir", "examples/connectors/h12_retro_community/replay_results", "--output-dir", "site/dist/h12"],
        [sys.executable, "scripts/summarize_h12_retro_community_quality_delta.py", "--input-dir", "examples/connectors/h12_retro_community/review_integration", "--output", "data/public_index/h12.json"],
        [sys.executable, "scripts/audit_h12_retro_community_wave.py", "--json-output", "roms/h12.json"],
    ]
    for command in forbidden_checks:
        proc = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
        if proc.returncode == 0 or "refusing" not in (proc.stdout + proc.stderr):
            errors.append(f"forbidden output root was not rejected: {' '.join(command)}")


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "roms", "isos", "disc_images", "bios", "firmware", "vintage_software_downloads", "software_downloads", "installer_downloads", "patch_downloads", "crack_keys", "gated_accounts", "forum_sessions", "archive_extractions", "execution_actions"):
        if (root / rel).exists():
            errors.append(f"local private or retro/community action root must not exist: {rel}")


def validate_boundaries(payload: Mapping[str, Any], label: str, errors: list[str]) -> None:
    errors.extend(f"{label}: {error}" for error in detect_h12_review_truth_boundary_violations(payload))
    errors.extend(f"{label}: {error}" for error in detect_h12_review_product_boundary_violations(payload))


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

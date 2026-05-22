#!/usr/bin/env python3
"""Validate H7-BUNDLE-04 review, quality delta, and audit artifacts offline."""

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

from archive.prototypes.legacy_runtime.connectors.h7_library_research.quality_delta import detect_h7_quality_overclaim  # noqa: E402
from archive.prototypes.legacy_runtime.connectors.h7_library_research.review_integration import (  # noqa: E402
    detect_h7_review_product_boundary_violations,
    detect_h7_review_truth_boundary_violations,
)

AUDIT_DIR = Path("control/audits/h7-bundle-04-library-research-review-quality-audit-v0")
REVIEW_DIR = Path("examples/connectors/h7_library_research/review_integration")
REQUIRED_JSON = (
    "contracts/control_schemas/audits/h7/connectors/library_research_review_integration_result.v0.json",
    "contracts/control_schemas/audits/h7/connectors/library_research_quality_delta_report.v0.json",
    "contracts/control_schemas/audits/h7/connectors/library_research_connector_wave_postmortem.v0.json",
    "contracts/control_schemas/audits/h7/connectors/library_research_integration_audit.v0.json",
    "contracts/control_schemas/tasks/h7/connectors/library_research_next_phase_recommendation.v0.json",
    "control/inventory/connectors/h7_library_research_review_integration_policy.json",
    "control/inventory/connectors/h7_library_research_review_output_policy.json",
    "control/inventory/connectors/h7_library_research_review_path_policy.json",
    "control/inventory/connectors/h7_library_research_review_truth_policy.json",
    "control/inventory/connectors/h7_library_research_quality_delta_policy.json",
    "control/inventory/connectors/h7_library_research_connector_wave_postmortem_policy.json",
    "control/inventory/connectors/h7_library_research_integration_audit_policy.json",
    "control/inventory/connectors/h7_library_research_next_phase_policy.json",
    (AUDIT_DIR / "h7_bundle_04_report.json").as_posix(),
)
REQUIRED_EXAMPLES = (
    "h7_bibliographic_identity_review_seed_v0.json",
    "h7_research_work_identity_review_seed_v0.json",
    "h7_dataset_identity_review_seed_v0.json",
    "h7_cultural_object_identity_review_seed_v0.json",
    "h7_patent_identity_review_seed_v0.json",
    "h7_citation_relation_review_seed_v0.json",
    "h7_access_rights_availability_review_seed_v0.json",
    "h7_source_cache_review_seed_v0.json",
    "h7_evidence_candidate_review_seed_v0.json",
    "h7_candidate_promotion_preview_v0.json",
    "h7_source_coverage_update_preview_v0.json",
    "h7_connector_scorecard_update_v0.json",
    "h7_source_pack_update_preview_v0.json",
    "h7_quality_delta_report_v0.json",
    "h7_connector_wave_postmortem_v0.json",
    "h7_blocked_review_integration_v0.json",
    "h7_review_integration_result_v0.json",
    "h7_next_phase_recommendation_v0.json",
    "h7_integration_audit_v0.json",
)
REQUIRED_AUDIT_FILES = (
    "README.md",
    "h7_bundle_04_report.json",
    "h7_review_integration_report.md",
    "h7_quality_delta_report.md",
    "h7_connector_wave_postmortem.md",
    "h7_integration_audit.md",
    "h7_exit_gate_decision.md",
    "next_phase_recommendation.md",
    "h8_readiness_review.md",
    "j1_risky_action_deferral_review.md",
    "k_semantic_ai_deferral_review.md",
    "l_wider_client_deferral_review.md",
    "validation.md",
    "generated/sample_h7_review_integration_result.json",
    "generated/sample_h7_quality_delta_report.json",
    "generated/sample_h7_connector_wave_postmortem.json",
    "generated/sample_h7_integration_audit.json",
    "generated/sample_h7_next_phase_recommendation.json",
    "generated/sample_h7_summary.md",
)
REQUIRED_DOCS = (
    "docs/reference/H7_LIBRARY_RESEARCH_REVIEW_INTEGRATION.md",
    "docs/reference/H7_LIBRARY_RESEARCH_QUALITY_DELTA_REPORT.md",
    "docs/reference/H7_LIBRARY_RESEARCH_CONNECTOR_WAVE_POSTMORTEM.md",
    "docs/architecture/H7_LIBRARY_RESEARCH_REVIEW_INTEGRATION_MODEL.md",
    "docs/operations/H7_LIBRARY_RESEARCH_WAVE_POSTMORTEM.md",
    "docs/operations/H7_LIBRARY_RESEARCH_WAVE_QUALITY_DELTA.md",
    "docs/operations/H7_TO_H8_HANDOFF.md",
    "docs/operations/H7_TO_J1_K_L_DEFERRAL.md",
)
PYTHON_SCAN_PATHS = (
    "archive/prototypes/legacy_runtime/connectors/h7_library_research/review_integration.py",
    "archive/prototypes/legacy_runtime/connectors/h7_library_research/quality_delta.py",
    "archive/prototypes/legacy_runtime/connectors/h7_library_research/wave_postmortem.py",
    "scripts/integrate_h7_library_research_review.py",
    "scripts/summarize_h7_library_research_quality_delta.py",
    "scripts/audit_h7_library_research_wave.py",
    "scripts/validate_h7_library_research_review_quality_audit.py",
)
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|urllib|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)
FORBIDDEN_TEXT_RE = re.compile(r"(full_text_payload|pdf_payload|book_scan_payload|article_payload|dataset_payload|patent_document_payload|iiif_payload|media_payload|scraping_output|crawling_output|private_key|api[_-]?token|access[_-]?token|cookie)", re.IGNORECASE)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit validation JSON.")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("H7 library/cultural/research review quality audit validation", file=stdout)
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
        "schema_version": "h7_review_quality_audit_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "H7-BUNDLE-04",
        "offline_default": True,
        "network_calls_made": False,
        "errors": errors,
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    review = payloads.get("control/inventory/connectors/h7_library_research_review_integration_policy.json", {})
    for key in (
        "live_call_allowed_by_default",
        "source_cache_persistence_enabled",
        "evidence_acceptance_enabled",
        "candidate_acceptance_enabled",
        "bibliographic_truth_acceptance_enabled",
        "research_work_truth_acceptance_enabled",
        "dataset_truth_acceptance_enabled",
        "cultural_object_truth_acceptance_enabled",
        "patent_truth_acceptance_enabled",
        "citation_truth_acceptance_enabled",
        "access_rights_truth_acceptance_enabled",
        "public_index_mutation_allowed",
        "master_index_mutation_allowed",
        "oai_pmh_harvest_enabled",
        "api_sync_enabled",
        "full_text_fetch_enabled",
        "downloads_enabled",
        "scraping_crawling_enabled",
        "restricted_source_access_enabled",
    ):
        if review.get(key) is not False:
            errors.append(f"h7 review policy {key} must be false")
    output = payloads.get("control/inventory/connectors/h7_library_research_review_output_policy.json", {})
    for key in (
        "accepted_bibliographic_truth",
        "accepted_research_work_truth",
        "accepted_dataset_truth",
        "accepted_cultural_object_truth",
        "accepted_patent_truth",
        "accepted_citation_truth",
        "accepted_access_rights_truth",
        "accepted_source_truth",
        "accepted_evidence_truth",
        "accepted_candidate_truth",
        "accepted_public_record",
        "public_index_mutation",
        "master_index_mutation",
        "oai_pmh_harvest_permission",
        "api_sync_permission",
        "full_text_fetch_permission",
        "download_permission",
        "scraping_crawling_permission",
        "restricted_source_access_permission",
        "production_readiness_claim",
    ):
        if key not in output.get("forbidden_outputs", []):
            errors.append(f"h7 review output policy must forbid {key}")
    audit = payloads.get("control/inventory/connectors/h7_library_research_integration_audit_policy.json", {})
    if "READY_FOR_H8_BUNDLE_01" not in audit.get("next_phase_values", []):
        errors.append("H7 audit policy must allow READY_FOR_H8_BUNDLE_01")
    next_phase = payloads.get("control/inventory/connectors/h7_library_research_next_phase_policy.json", {})
    if next_phase.get("j1_risky_actions_deferred") is not True or next_phase.get("k_semantic_ai_deferred") is not True or next_phase.get("l_wider_clients_deferred") is not True:
        errors.append("H7 next phase policy must defer J1/K/L")


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
    delta = load_json_object(root / REVIEW_DIR / "h7_quality_delta_report_v0.json", errors)
    errors.extend(detect_h7_quality_overclaim(delta))
    postmortem = load_json_object(root / REVIEW_DIR / "h7_connector_wave_postmortem_v0.json", errors)
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
    report = load_json_object(root / AUDIT_DIR / "h7_bundle_04_report.json", errors)
    if report.get("h7_exit_gate") not in {"PASS", "PASS_WITH_WARNINGS", "PARTIAL", "BLOCKED", "FAIL"}:
        errors.append("H7 report must have explicit h7_exit_gate")
    if report.get("next_phase_recommendation") not in {"READY_FOR_H8_BUNDLE_01", "READY_WITH_WARNINGS"}:
        errors.append("H7 report should recommend H8 when fixture-equivalent outputs are sufficient")
    validate_boundaries(report, "h7_bundle_04_report", errors)


def validate_python_imports(root: Path, errors: list[str]) -> None:
    for rel in PYTHON_SCAN_PATHS:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing Python file: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for match in BANNED_IMPORT_RE.finditer(text):
            errors.append(f"banned import in {rel}: {match.group(1)}")


def validate_scripts(root: Path, errors: list[str]) -> None:
    commands = [
        ["python", "scripts/integrate_h7_library_research_review.py", "--input-dir", "examples/connectors/h7_library_research/replay_results", "--check"],
        ["python", "scripts/summarize_h7_library_research_quality_delta.py", "--input-dir", "examples/connectors/h7_library_research/review_integration", "--check"],
        ["python", "scripts/audit_h7_library_research_wave.py", "--check"],
    ]
    for command in commands:
        proc = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
        if proc.returncode != 0:
            errors.append(f"script failed: {' '.join(command)} :: {proc.stdout} {proc.stderr}".strip())
    forbidden = subprocess.run(
        ["python", "scripts/integrate_h7_library_research_review.py", "--input-dir", "examples/connectors/h7_library_research/replay_results", "--output-dir", "site/dist/h7"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if forbidden.returncode == 0 or "refusing" not in (forbidden.stdout + forbidden.stderr):
        errors.append("integrate script must refuse site/dist output")


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "harvest", "downloads", "pdf_downloads", "book_downloads", "article_downloads", "dataset_downloads", "patent_downloads", "ocr", "media_downloads", "restricted_sources"):
        if (root / rel).exists():
            errors.append(f"forbidden local/private root exists: {rel}")


def validate_boundaries(payload: Mapping[str, Any], label: str, errors: list[str]) -> None:
    errors.extend(f"{label}: {error}" for error in detect_h7_review_truth_boundary_violations(payload))
    errors.extend(f"{label}: {error}" for error in detect_h7_review_product_boundary_violations(payload))


def validate_no_forbidden_text(path: Path, errors: list[str]) -> None:
    if path.is_file() and FORBIDDEN_TEXT_RE.search(path.read_text(encoding="utf-8")):
        errors.append(f"forbidden payload/private marker in {path.relative_to(REPO_ROOT).as_posix()}")


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
        errors.append(f"JSON file must contain an object: {path}")
        return {}
    return dict(payload)


if __name__ == "__main__":
    raise SystemExit(main())

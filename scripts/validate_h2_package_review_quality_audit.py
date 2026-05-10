#!/usr/bin/env python3
"""Validate H2-BUNDLE-04 review, quality delta, and audit artifacts offline."""

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

from runtime.connectors.h2_package_registries.quality_delta import detect_h2_quality_overclaim  # noqa: E402
from runtime.connectors.h2_package_registries.review_integration import (  # noqa: E402
    detect_h2_review_product_boundary_violations,
    detect_h2_review_truth_boundary_violations,
)


AUDIT_DIR = Path("control/audits/h2-bundle-04-package-review-quality-audit-v0")
REVIEW_DIR = Path("examples/connectors/h2_package_registries/review_integration")
REQUIRED_JSON = (
    "contracts/connectors/h2_package_review_integration_result.v0.json",
    "contracts/connectors/h2_package_quality_delta_report.v0.json",
    "contracts/connectors/h2_package_connector_wave_postmortem.v0.json",
    "contracts/connectors/h2_package_integration_audit.v0.json",
    "contracts/connectors/h2_package_next_phase_recommendation.v0.json",
    "control/inventory/connectors/h2_package_review_integration_policy.json",
    "control/inventory/connectors/h2_package_review_output_policy.json",
    "control/inventory/connectors/h2_package_review_path_policy.json",
    "control/inventory/connectors/h2_package_review_truth_policy.json",
    "control/inventory/connectors/h2_package_quality_delta_policy.json",
    "control/inventory/connectors/h2_package_connector_wave_postmortem_policy.json",
    "control/inventory/connectors/h2_package_integration_audit_policy.json",
    "control/inventory/connectors/h2_package_next_phase_policy.json",
    (AUDIT_DIR / "h2_bundle_04_report.json").as_posix(),
)
REQUIRED_EXAMPLES = (
    "h2_package_identity_review_seed_v0.json",
    "h2_dependency_candidate_review_seed_v0.json",
    "h2_package_file_candidate_review_seed_v0.json",
    "h2_source_cache_review_seed_v0.json",
    "h2_evidence_candidate_review_seed_v0.json",
    "h2_candidate_promotion_preview_v0.json",
    "h2_source_coverage_update_preview_v0.json",
    "h2_connector_scorecard_update_v0.json",
    "h2_source_pack_update_preview_v0.json",
    "h2_quality_delta_report_v0.json",
    "h2_connector_wave_postmortem_v0.json",
    "h2_blocked_review_integration_v0.json",
    "h2_review_integration_result_v0.json",
    "h2_next_phase_recommendation_v0.json",
)
REQUIRED_AUDIT_FILES = (
    "README.md",
    "h2_bundle_04_report.json",
    "h2_review_integration_report.md",
    "h2_quality_delta_report.md",
    "h2_connector_wave_postmortem.md",
    "h2_integration_audit.md",
    "h2_exit_gate_decision.md",
    "next_phase_recommendation.md",
    "h3_readiness_review.md",
    "j1_risky_action_deferral_review.md",
    "k_semantic_ai_deferral_review.md",
    "l_wider_client_deferral_review.md",
    "validation.md",
    "generated/sample_h2_review_integration_result.json",
    "generated/sample_h2_quality_delta_report.json",
    "generated/sample_h2_connector_wave_postmortem.json",
    "generated/sample_h2_integration_audit.json",
    "generated/sample_h2_next_phase_recommendation.json",
    "generated/sample_h2_summary.md",
)
REQUIRED_DOCS = (
    "docs/reference/H2_PACKAGE_REVIEW_INTEGRATION.md",
    "docs/reference/H2_PACKAGE_QUALITY_DELTA_REPORT.md",
    "docs/reference/H2_PACKAGE_CONNECTOR_WAVE_POSTMORTEM.md",
    "docs/architecture/H2_PACKAGE_REVIEW_INTEGRATION_MODEL.md",
    "docs/operations/H2_PACKAGE_WAVE_POSTMORTEM.md",
    "docs/operations/H2_PACKAGE_WAVE_QUALITY_DELTA.md",
    "docs/operations/H2_TO_H3_HANDOFF.md",
    "docs/operations/H2_TO_J1_K_L_DEFERRAL.md",
)
PYTHON_SCAN_PATHS = (
    "runtime/connectors/h2_package_registries/review_integration.py",
    "runtime/connectors/h2_package_registries/quality_delta.py",
    "runtime/connectors/h2_package_registries/wave_postmortem.py",
    "scripts/integrate_h2_package_review.py",
    "scripts/summarize_h2_package_quality_delta.py",
    "scripts/audit_h2_package_registry_wave.py",
    "scripts/validate_h2_package_review_quality_audit.py",
)
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|urllib|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)
PACKAGE_MANAGER_CALL_RE = re.compile(r"(os\.system|subprocess\.(?:run|call|Popen)).*(pip|npm|cargo|gem|cpan|conda|docker|podman|Rscript)", re.IGNORECASE)
SECRET_KEY_RE = re.compile(
    r'"[^"]*(api[_-]?key|api[_-]?token|access[_-]?token|auth[_-]?token|client_secret|password|private_key|cookie)[^"]*"\s*:',
    re.IGNORECASE,
)


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
        "schema_version": "h2_review_quality_audit_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "H2-BUNDLE-04",
        "offline_default": True,
        "network_calls_made": False,
        "errors": errors,
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    review = payloads.get("control/inventory/connectors/h2_package_review_integration_policy.json", {})
    for key in (
        "live_call_allowed_by_default",
        "source_cache_persistence_enabled",
        "evidence_acceptance_enabled",
        "candidate_acceptance_enabled",
        "package_identity_acceptance_enabled",
        "public_index_mutation_allowed",
        "master_index_mutation_allowed",
    ):
        if review.get(key) is not False:
            errors.append(f"h2 review policy {key} must be false")
    output = payloads.get("control/inventory/connectors/h2_package_review_output_policy.json", {})
    for key in (
        "accepted_package_identity_truth",
        "accepted_dependency_correctness",
        "accepted_source_truth",
        "accepted_evidence_truth",
        "accepted_candidate_truth",
        "public_index_mutation",
        "master_index_mutation",
        "package_download_permission",
        "install_execute_permission",
        "production_readiness_claim",
    ):
        if key not in output.get("forbidden_outputs", []):
            errors.append(f"h2 review output policy must forbid {key}")
    audit = payloads.get("control/inventory/connectors/h2_package_integration_audit_policy.json", {})
    if "READY_FOR_H3_BUNDLE_01" not in audit.get("next_phase_values", []):
        errors.append("H2 audit policy must allow READY_FOR_H3_BUNDLE_01")


def validate_docs(root: Path, errors: list[str]) -> None:
    for rel in REQUIRED_DOCS:
        if not (root / rel).is_file():
            errors.append(f"missing doc: {rel}")


def validate_examples(root: Path, errors: list[str]) -> None:
    for name in REQUIRED_EXAMPLES:
        payload = load_json_object(root / REVIEW_DIR / name, errors)
        validate_boundaries(payload, f"example {name}", errors)
        validate_no_secret_text(root / REVIEW_DIR / name, errors)
    delta = load_json_object(root / REVIEW_DIR / "h2_quality_delta_report_v0.json", errors)
    errors.extend(detect_h2_quality_overclaim(delta))
    postmortem = load_json_object(root / REVIEW_DIR / "h2_connector_wave_postmortem_v0.json", errors)
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
    report = load_json_object(root / AUDIT_DIR / "h2_bundle_04_report.json", errors)
    if report.get("h2_exit_gate") not in {"PASS", "PASS_WITH_WARNINGS", "PARTIAL", "BLOCKED", "FAIL"}:
        errors.append("H2 report must have explicit h2_exit_gate")
    if report.get("next_phase_recommendation") != "READY_FOR_H3_BUNDLE_01":
        errors.append("H2 report should recommend READY_FOR_H3_BUNDLE_01 when fixture-equivalent outputs are sufficient")
    validate_boundaries(report, "h2_bundle_04_report", errors)


def validate_python_imports(root: Path, errors: list[str]) -> None:
    for rel in PYTHON_SCAN_PATHS:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing Python file: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for match in BANNED_IMPORT_RE.finditer(text):
            errors.append(f"forbidden import in {rel}: {match.group(1)}")
        if PACKAGE_MANAGER_CALL_RE.search(text):
            errors.append(f"forbidden package-manager invocation primitive in {rel}")


def validate_scripts(root: Path, errors: list[str]) -> None:
    commands = (
        [sys.executable, "scripts/integrate_h2_package_review.py", "--input-dir", "examples/connectors/h2_package_registries/replay_results", "--check", "--json"],
        [sys.executable, "scripts/summarize_h2_package_quality_delta.py", "--input-dir", "examples/connectors/h2_package_registries/review_integration", "--check", "--json"],
        [sys.executable, "scripts/audit_h2_package_registry_wave.py", "--check"],
    )
    for command in commands:
        result = subprocess.run(command, cwd=root, check=False, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            errors.append(f"script failed: {' '.join(command)} :: {result.stdout} {result.stderr}")
    bad = subprocess.run(
        [sys.executable, "scripts/integrate_h2_package_review.py", "--input-dir", "examples/connectors/h2_package_registries/replay_results", "--output-dir", "site/dist/h2-review"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if bad.returncode == 0 or "refusing forbidden output root" not in bad.stdout:
        errors.append("integrate script must reject site/dist output")
    bad_public = subprocess.run(
        [sys.executable, "scripts/summarize_h2_package_quality_delta.py", "--input-dir", "examples/connectors/h2_package_registries/review_integration", "--output", "data/public_index/h2-quality.json"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if bad_public.returncode == 0 or "refusing forbidden output root" not in bad_public.stdout:
        errors.append("quality script must reject data/public_index output")


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
        if (root / rel).exists():
            errors.append(f"local private root must not exist: {rel}")


def validate_boundaries(payload: Mapping[str, Any], label: str, errors: list[str]) -> None:
    errors.extend(f"{label}: {error}" for error in detect_h2_review_truth_boundary_violations(payload))
    errors.extend(f"{label}: {error}" for error in detect_h2_review_product_boundary_violations(payload))
    errors.extend(f"{label}: {error}" for error in detect_h2_quality_overclaim(payload))
    text = json.dumps(payload, sort_keys=True)
    for term in ("jar_bytes", "nupkg_bytes", "crate_bytes", "gem_bytes", "conda_package_bytes", "oci_layer_bytes", "package_manager_output"):
        if term in text:
            errors.append(f"{label}: forbidden payload/package-manager term present: {term}")


def load_json_object(path: Path, errors: list[str]) -> Mapping[str, Any]:
    if not path.is_file():
        errors.append(f"missing JSON: {rel(path)}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - deterministic validator output.
        errors.append(f"invalid JSON: {rel(path)}: {exc}")
        return {}
    if not isinstance(payload, Mapping):
        errors.append(f"JSON must be an object: {rel(path)}")
        return {}
    return payload


def validate_no_secret_text(path: Path, errors: list[str]) -> None:
    if path.is_file() and SECRET_KEY_RE.search(path.read_text(encoding="utf-8")):
        errors.append(f"{path.relative_to(REPO_ROOT)} contains credential/cookie/token-like key")


def rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("H2 package review quality audit validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())

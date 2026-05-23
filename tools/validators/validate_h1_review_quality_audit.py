#!/usr/bin/env python3
"""Validate H1-BUNDLE-04 review, quality delta, and audit artifacts offline."""

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

from archive.prototypes.legacy_runtime.connectors.h1_metadata_wave.quality_delta import detect_h1_quality_overclaim  # noqa: E402
from archive.prototypes.legacy_runtime.connectors.h1_metadata_wave.review_integration import (  # noqa: E402
    detect_h1_review_product_boundary_violations,
    detect_h1_review_truth_boundary_violations,
)


AUDIT_DIR = Path("control/audits/h1-bundle-04-review-quality-audit-v0")
REVIEW_DIR = Path("examples/connectors/h1_metadata_wave/review_integration")
REQUIRED_JSON = (
    "contracts/schema/control/audits/h1/connectors/review_integration_result.v0.json",
    "contracts/schema/control/audits/h1/connectors/quality_delta_report.v0.json",
    "contracts/schema/control/audits/h1/connectors/connector_wave_postmortem.v0.json",
    "contracts/schema/control/audits/h1/connectors/integration_audit.v0.json",
    "control/inventory/connectors/h1_review_integration_policy.json",
    "control/inventory/connectors/h1_review_output_policy.json",
    "control/inventory/connectors/h1_review_path_policy.json",
    "control/inventory/connectors/h1_review_truth_policy.json",
    "control/inventory/connectors/h1_quality_delta_policy.json",
    "control/inventory/connectors/h1_connector_wave_postmortem_policy.json",
    "control/inventory/connectors/h1_integration_audit_policy.json",
    (AUDIT_DIR / "h1_bundle_04_report.json").as_posix(),
)
REQUIRED_EXAMPLES = (
    "h1_source_cache_review_seed_v0.json",
    "h1_evidence_candidate_review_seed_v0.json",
    "h1_candidate_promotion_preview_v0.json",
    "h1_source_coverage_update_preview_v0.json",
    "h1_connector_scorecard_update_v0.json",
    "h1_source_pack_update_preview_v0.json",
    "h1_quality_delta_report_v0.json",
    "h1_connector_wave_postmortem_v0.json",
    "h1_blocked_review_integration_v0.json",
    "h1_review_integration_result_v0.json",
)
REQUIRED_AUDIT_FILES = (
    "README.md",
    "h1_bundle_04_report.json",
    "h1_review_integration_report.md",
    "h1_quality_delta_report.md",
    "h1_connector_wave_postmortem.md",
    "h1_integration_audit.md",
    "h1_exit_gate_decision.md",
    "next_phase_recommendation.md",
    "f_bundle_01_readiness.md",
    "h2_defer_or_continue_recommendation.md",
    "validation.md",
    "generated/sample_h1_review_integration_result.json",
    "generated/sample_h1_quality_delta_report.json",
    "generated/sample_h1_connector_wave_postmortem.json",
    "generated/sample_h1_integration_audit.json",
    "generated/sample_h1_summary.md",
)
REQUIRED_DOCS = (
    "docs/reference/H1_METADATA_REVIEW_INTEGRATION.md",
    "docs/reference/H1_METADATA_QUALITY_DELTA_REPORT.md",
    "docs/reference/H1_CONNECTOR_WAVE_POSTMORTEM.md",
    "docs/architecture/H1_REVIEW_INTEGRATION_MODEL.md",
    "docs/operations/H1_METADATA_WAVE_POSTMORTEM.md",
    "docs/operations/H1_METADATA_WAVE_QUALITY_DELTA.md",
    "docs/operations/H1_TO_EXTRACTION_HANDOFF.md",
)
PYTHON_SCAN_PATHS = (
    "archive/prototypes/legacy_runtime/connectors/h1_metadata_wave/review_integration.py",
    "archive/prototypes/legacy_runtime/connectors/h1_metadata_wave/quality_delta.py",
    "archive/prototypes/legacy_runtime/connectors/h1_metadata_wave/wave_postmortem.py",
    "scripts/integrate_h1_metadata_review.py",
    "scripts/summarize_h1_quality_delta.py",
    "scripts/audit_h1_metadata_wave.py",
    "scripts/validate_h1_review_quality_audit.py",
)
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|urllib|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    root = root.resolve()
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
        "schema_version": "h1_review_quality_audit_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "H1-BUNDLE-04",
        "offline_default": True,
        "errors": errors,
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    review = payloads.get("control/inventory/connectors/h1_review_integration_policy.json", {})
    require_value(review, "live_call_allowed_by_default", False, errors)
    require_value(review, "source_cache_persistence_enabled", False, errors)
    require_value(review, "evidence_acceptance_enabled", False, errors)
    require_value(review, "public_index_mutation_allowed", False, errors)
    require_value(review, "master_index_mutation_allowed", False, errors)
    output = payloads.get("control/inventory/connectors/h1_review_output_policy.json", {})
    for key in ("accepted_source_truth", "accepted_evidence_truth", "accepted_candidate_truth", "public_index_mutation", "master_index_mutation", "production_readiness_claim"):
        if key not in output.get("forbidden_output_types", []):
            errors.append(f"h1 review output policy must forbid {key}")
    audit = payloads.get("control/inventory/connectors/h1_integration_audit_policy.json", {})
    if "READY_FOR_F_BUNDLE_01" not in audit.get("next_phase_values", []):
        errors.append("H1 audit policy must allow READY_FOR_F_BUNDLE_01")


def validate_docs(root: Path, errors: list[str]) -> None:
    for rel in REQUIRED_DOCS:
        if not (root / rel).is_file():
            errors.append(f"missing doc: {rel}")


def validate_examples(root: Path, errors: list[str]) -> None:
    for name in REQUIRED_EXAMPLES:
        payload = load_json_object(root / REVIEW_DIR / name, errors)
        validate_boundaries(payload, f"example {name}", errors)
    delta = load_json_object(root / REVIEW_DIR / "h1_quality_delta_report_v0.json", errors)
    errors.extend(detect_h1_quality_overclaim(delta))
    postmortem = load_json_object(root / REVIEW_DIR / "h1_connector_wave_postmortem_v0.json", errors)
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
    report = load_json_object(root / AUDIT_DIR / "h1_bundle_04_report.json", errors)
    if report.get("h1_exit_gate") not in {"PASS", "PASS_WITH_WARNINGS", "PARTIAL", "BLOCKED", "FAIL"}:
        errors.append("H1 report must have explicit h1_exit_gate")
    if report.get("next_phase_recommendation") != "READY_FOR_F_BUNDLE_01":
        errors.append("H1 report should recommend READY_FOR_F_BUNDLE_01 when fixture-equivalent outputs are sufficient")
    validate_boundaries(report, "h1_bundle_04_report", errors)


def validate_python_imports(root: Path, errors: list[str]) -> None:
    for rel in PYTHON_SCAN_PATHS:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing Python file: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for match in BANNED_IMPORT_RE.finditer(text):
            errors.append(f"forbidden import in {rel}: {match.group(1)}")


def validate_scripts(root: Path, errors: list[str]) -> None:
    commands = (
        [
            sys.executable,
            "scripts/integrate_h1_metadata_review.py",
            "--input-dir",
            "examples/connectors/h1_metadata_wave/replay_results",
            "--check",
            "--json",
        ],
        [
            sys.executable,
            "scripts/summarize_h1_quality_delta.py",
            "--input-dir",
            "examples/connectors/h1_metadata_wave/review_integration",
            "--check",
            "--json",
        ],
        [
            sys.executable,
            "scripts/audit_h1_metadata_wave.py",
            "--check",
        ],
    )
    for command in commands:
        result = subprocess.run(command, cwd=root, check=False, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            errors.append(f"script failed: {' '.join(command)} :: {result.stdout} {result.stderr}")
    forbidden = subprocess.run(
        [
            sys.executable,
            "scripts/integrate_h1_metadata_review.py",
            "--input-dir",
            "examples/connectors/h1_metadata_wave/replay_results",
            "--output-dir",
            "site/dist/h1-review",
        ],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if forbidden.returncode == 0 or "refusing forbidden output root" not in forbidden.stdout:
        errors.append("integrate script must reject site/dist output")
    forbidden_public = subprocess.run(
        [
            sys.executable,
            "scripts/summarize_h1_quality_delta.py",
            "--input-dir",
            "examples/connectors/h1_metadata_wave/review_integration",
            "--output",
            "site/dist/data/public_index/h1-quality.json",
        ],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if forbidden_public.returncode == 0 or "refusing forbidden output root" not in forbidden_public.stdout:
        errors.append("quality script must reject site/dist/data/public_index output")


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
        if (root / rel).exists():
            errors.append(f"local private root must not exist: {rel}")


def validate_boundaries(payload: Mapping[str, Any], label: str, errors: list[str]) -> None:
    errors.extend(f"{label}: {error}" for error in detect_h1_review_truth_boundary_violations(payload))
    errors.extend(f"{label}: {error}" for error in detect_h1_review_product_boundary_violations(payload))
    errors.extend(f"{label}: {error}" for error in detect_h1_quality_overclaim(payload))


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


def require_value(payload: Mapping[str, Any], key: str, expected: Any, errors: list[str]) -> None:
    if payload.get(key) != expected:
        errors.append(f"{key} must be {expected!r}")


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
        print("H1 review quality audit validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())

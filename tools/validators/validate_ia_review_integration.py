#!/usr/bin/env python3
"""Validate IA-BUNDLE-03 review integration and quality delta artifacts."""

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

from runtime.connectors.internet_archive.quality_delta import detect_quality_overclaim  # noqa: E402
from runtime.connectors.internet_archive.review_integration import (  # noqa: E402
    detect_ia_review_product_boundary_violations,
    detect_ia_review_truth_boundary_violations,
)


AUDIT_DIR = Path("control/audits/ia-bundle-03-review-integration-quality-delta-v0")
EXAMPLE_DIR = Path("examples/connectors/internet_archive/review_integration")
IA02_GENERATED = Path("control/audits/ia-bundle-02-bounded-metadata-live-probe-v0/generated")
REQUIRED_JSON = (
    "control/inventory/connectors/internet_archive_review_integration_policy.json",
    "control/inventory/connectors/internet_archive_quality_delta_policy.json",
    "control/inventory/connectors/internet_archive_postmortem_policy.json",
    "control/inventory/connectors/internet_archive_review_output_policy.json",
    "control/inventory/connectors/internet_archive_review_path_policy.json",
    "control/inventory/connectors/internet_archive_review_truth_policy.json",
    (AUDIT_DIR / "ia_bundle_03_report.json").as_posix(),
)
REQUIRED_EXAMPLES = (
    "ia_source_cache_review_entry_v0.json",
    "ia_evidence_candidate_review_entry_v0.json",
    "ia_candidate_promotion_dry_run_v0.json",
    "ia_pack_draft_preview_v0.json",
    "ia_quality_delta_example_v0.json",
    "ia_connector_postmortem_example_v0.json",
    "ia_blocked_review_integration_v0.json",
)
REQUIRED_AUDIT_FILES = (
    "README.md",
    "ia_bundle_03_report.json",
    "ia_review_integration_report.md",
    "ia_quality_delta_report.md",
    "ia_connector_postmortem.md",
    "h0_readiness_recommendation.md",
    "validation.md",
    "generated/sample_ia_source_cache_review_entry.json",
    "generated/sample_ia_evidence_candidate_review_entry.json",
    "generated/sample_ia_candidate_promotion_dry_run.json",
    "generated/sample_ia_pack_draft_preview.json",
    "generated/sample_ia_quality_delta.json",
    "generated/sample_ia_connector_postmortem.json",
    "generated/sample_ia_review_integration_summary.md",
)
REQUIRED_DOCS = (
    "docs/reference/IA_METADATA_REVIEW_INTEGRATION.md",
    "docs/architecture/IA_METADATA_REVIEW_INTEGRATION_MODEL.md",
    "docs/operations/IA_METADATA_CONNECTOR_POSTMORTEM.md",
    "docs/operations/IA_METADATA_QUALITY_DELTA.md",
)
PYTHON_SCAN_PATHS = (
    "runtime/connectors/internet_archive/review_integration.py",
    "runtime/connectors/internet_archive/quality_delta.py",
    "scripts/integrate_ia_metadata_review.py",
    "scripts/summarize_ia_connector_quality_delta.py",
    "scripts/validate_ia_review_integration.py",
)
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|urllib|http|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
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
        "schema_version": "ia_review_integration_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "IA-BUNDLE-03",
        "offline_default": True,
        "errors": errors,
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    review = payloads.get("control/inventory/connectors/internet_archive_review_integration_policy.json", {})
    require_value(review, "source_id", "internet_archive", errors)
    require_value(review, "connector_id", "internet_archive_metadata_connector", errors)
    require_value(review, "public_index_mutation_allowed", False, errors)
    require_value(review, "master_index_mutation_allowed", False, errors)
    require_value(review, "live_call_allowed_by_default", False, errors)
    for key in (
        "review_required_before_source_cache_persistence",
        "review_required_before_evidence_acceptance",
        "review_required_before_candidate_acceptance",
        "review_required_before_public_index_use",
        "review_required_before_master_index",
    ):
        require_value(review, key, True, errors)

    output = payloads.get("control/inventory/connectors/internet_archive_review_output_policy.json", {})
    for key in (
        "accepted_source_truth",
        "accepted_evidence_truth",
        "accepted_candidate_truth",
        "accepted_public_record",
        "public_index_mutation",
        "master_index_mutation",
        "rights_clearance",
        "malware_safety",
        "verified_installability",
        "production_readiness_claim",
        "downloaded_file",
        "item_file_payload",
    ):
        if key not in output.get("forbidden_output_types", []):
            errors.append(f"review output policy must forbid {key}")

    truth = payloads.get("control/inventory/connectors/internet_archive_review_truth_policy.json", {})
    for key in (
        "ia_review_output_is_truth",
        "ia_source_cache_review_entry_accepts_source",
        "ia_evidence_review_entry_accepts_evidence",
        "ia_candidate_promotion_dry_run_accepts_candidate",
        "ia_pack_draft_is_accepted_pack",
        "ia_quality_delta_is_production_claim",
        "ia_postmortem_enables_future_connectors_automatically",
        "ia_review_can_mutate_public_index",
        "ia_review_can_mutate_master_index",
        "ia_review_can_claim_rights_clearance",
        "ia_review_can_claim_malware_safety",
        "ia_review_can_claim_verified_installability",
    ):
        require_value(truth, key, False, errors)

    quality = payloads.get("control/inventory/connectors/internet_archive_quality_delta_policy.json", {})
    for key in ("beats_google", "beats_internet_archive", "production_search_quality"):
        if key not in quality.get("forbidden_metrics", []):
            errors.append(f"quality delta policy must forbid {key}")


def validate_docs(root: Path, errors: list[str]) -> None:
    for rel in REQUIRED_DOCS:
        if not (root / rel).is_file():
            errors.append(f"missing doc: {rel}")


def validate_examples(root: Path, errors: list[str]) -> None:
    for name in REQUIRED_EXAMPLES:
        payload = load_json_object(root / EXAMPLE_DIR / name, errors)
        validate_boundaries(payload, f"example {name}", errors)


def validate_audit_files(root: Path, errors: list[str]) -> None:
    for rel_name in REQUIRED_AUDIT_FILES:
        if not (root / AUDIT_DIR / rel_name).is_file():
            errors.append(f"missing audit file: {(AUDIT_DIR / rel_name).as_posix()}")


def validate_generated_outputs(root: Path, errors: list[str]) -> None:
    for rel_name in REQUIRED_AUDIT_FILES:
        if not rel_name.startswith("generated/") or not rel_name.endswith(".json"):
            continue
        payload = load_json_object(root / AUDIT_DIR / rel_name, errors)
        validate_boundaries(payload, rel_name, errors)
    report = load_json_object(root / AUDIT_DIR / "ia_bundle_03_report.json", errors)
    if report.get("inputs", {}).get("used_live_probe_output") is not False:
        errors.append("IA-BUNDLE-03 report must not claim live probe output was used for current blocked run")
    if report.get("truth_boundary", {}).get("public_index_mutated") is not False:
        errors.append("IA-BUNDLE-03 report must preserve public_index_mutated false")
    if report.get("truth_boundary", {}).get("master_index_mutated") is not False:
        errors.append("IA-BUNDLE-03 report must preserve master_index_mutated false")


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
    integration = subprocess.run(
        [
            sys.executable,
            "scripts/integrate_ia_metadata_review.py",
            "--source-cache-candidate",
            (IA02_GENERATED / "sample_source_cache_candidate_from_live_probe.json").as_posix(),
            "--evidence-preview",
            (IA02_GENERATED / "sample_evidence_candidate_preview_from_live_probe.json").as_posix(),
            "--check",
            "--json",
        ],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if integration.returncode != 0:
        errors.append(f"integration CLI check failed: {integration.stdout} {integration.stderr}")
    else:
        payload = json.loads(integration.stdout)
        if payload.get("integration_status") != "blocked_dry_run":
            errors.append("integration CLI must report blocked_dry_run for current IA-BUNDLE-02 outputs")

    quality = subprocess.run(
        [
            sys.executable,
            "scripts/summarize_ia_connector_quality_delta.py",
            "--input-dir",
            (AUDIT_DIR / "generated").as_posix(),
            "--check",
            "--json",
        ],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if quality.returncode != 0:
        errors.append(f"quality CLI check failed: {quality.stdout} {quality.stderr}")

    forbidden = subprocess.run(
        [
            sys.executable,
            "scripts/integrate_ia_metadata_review.py",
            "--source-cache-candidate",
            (IA02_GENERATED / "sample_source_cache_candidate_from_live_probe.json").as_posix(),
            "--evidence-preview",
            (IA02_GENERATED / "sample_evidence_candidate_preview_from_live_probe.json").as_posix(),
            "--output-dir",
            "site/dist/ia-review",
        ],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if forbidden.returncode == 0 or "refusing forbidden output root" not in forbidden.stdout:
        errors.append("integration CLI must refuse site/dist output root")


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
        if (root / rel).exists():
            errors.append(f"local private root must not be created: {rel}")


def validate_boundaries(payload: Mapping[str, Any], label: str, errors: list[str]) -> None:
    errors.extend(f"{label}: {error}" for error in detect_ia_review_truth_boundary_violations(payload))
    errors.extend(f"{label}: {error}" for error in detect_ia_review_product_boundary_violations(payload))
    errors.extend(f"{label}: {error}" for error in detect_quality_overclaim(payload))
    text = json.dumps(payload, sort_keys=True)
    forbidden_terms = (
        '"claims_external_superiority": true',
        '"claims_production_readiness": true',
        '"public_index_mutated": true',
        '"master_index_mutated": true',
        '"rights_clearance_claimed": true',
        '"malware_safety_claimed": true',
        '"verified_installability_claimed": true',
    )
    for term in forbidden_terms:
        if term in text:
            errors.append(f"{label}: forbidden true claim present: {term}")


def load_json_object(path: Path, errors: list[str]) -> Mapping[str, Any]:
    if not path.is_file():
        errors.append(f"missing JSON: {rel(path)}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - deterministic validator surface.
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
    report = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"status: {report['status']}", file=stdout)
        for error in report["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())

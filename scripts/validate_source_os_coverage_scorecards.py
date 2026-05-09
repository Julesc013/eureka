#!/usr/bin/env python3
"""Validate H0-BUNDLE-03 coverage, scorecard, and source-pack artifacts offline."""

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

from runtime.connectors.core.coverage_ledger import (  # noqa: E402
    build_source_coverage_manifest,
    detect_coverage_truth_boundary_violations,
    validate_source_coverage_record,
)
from runtime.connectors.core.connector_scorecard import (  # noqa: E402
    detect_scorecard_truth_boundary_violations,
    validate_connector_scorecard,
)
from runtime.connectors.core.source_pack import (  # noqa: E402
    detect_source_pack_truth_boundary_violations,
    validate_source_pack_manifest,
)


CONTRACTS = (
    "contracts/sources/source_coverage_ledger.v0.json",
    "contracts/sources/source_coverage_manifest.v0.json",
    "contracts/connectors/connector_scorecard.v0.json",
    "contracts/connectors/connector_quality_delta.v0.json",
    "contracts/packs/source_pack_manifest.v0.json",
    "contracts/packs/source_pack_export.v0.json",
)
INVENTORIES = (
    "control/inventory/sources/source_coverage_ledger_policy.json",
    "control/inventory/sources/source_coverage_manifest_policy.json",
    "control/inventory/sources/source_coverage_depth_policy.json",
    "control/inventory/sources/source_coverage_output_policy.json",
    "control/inventory/sources/source_coverage_truth_policy.json",
    "control/inventory/connectors/connector_scorecard_policy.json",
    "control/inventory/connectors/connector_scorecard_metric_policy.json",
    "control/inventory/connectors/connector_scorecard_output_policy.json",
    "control/inventory/connectors/connector_scorecard_truth_policy.json",
    "control/inventory/packs/source_pack_manifest_policy.json",
    "control/inventory/packs/source_pack_export_policy.json",
    "control/inventory/packs/source_pack_input_policy.json",
    "control/inventory/packs/source_pack_output_policy.json",
    "control/inventory/packs/source_pack_truth_policy.json",
)
COVERAGE_EXAMPLES = (
    "examples/source_coverage/minimal_source_coverage_record_v0.json",
    "examples/source_coverage/internet_archive_coverage_record_v0.json",
    "examples/source_coverage/h1_metadata_wave_coverage_preview_v0.json",
    "examples/source_coverage/policy_blocked_coverage_record_v0.json",
    "examples/source_coverage/minimal_source_coverage_manifest_v0.json",
)
SCORECARD_EXAMPLES = (
    "examples/connectors/core/scorecards/minimal_connector_scorecard_v0.json",
    "examples/connectors/core/scorecards/internet_archive_scorecard_v0.json",
    "examples/connectors/core/scorecards/api_json_family_scorecard_v0.json",
    "examples/connectors/core/scorecards/package_registry_family_scorecard_v0.json",
    "examples/connectors/core/scorecards/warc_cdx_family_scorecard_v0.json",
    "examples/connectors/core/scorecards/policy_blocked_connector_scorecard_v0.json",
)
PACK_EXAMPLES = (
    "examples/source_packs/minimal_source_pack_manifest_v0.json",
    "examples/source_packs/internet_archive_source_pack_manifest_v0.json",
    "examples/source_packs/h1_metadata_wave_source_pack_preview_v0.json",
    "examples/source_packs/policy_blocked_source_pack_manifest_v0.json",
)
DOCS = (
    "docs/reference/SOURCE_COVERAGE_LEDGER.md",
    "docs/reference/SOURCE_COVERAGE_MANIFEST.md",
    "docs/reference/CONNECTOR_SCORECARD_CONTRACT.md",
    "docs/reference/SOURCE_PACK_MANIFEST_CONTRACT.md",
    "docs/architecture/SOURCE_COVERAGE_MODEL.md",
    "docs/architecture/CONNECTOR_SCORECARD_MODEL.md",
    "docs/architecture/SOURCE_PACK_MODEL.md",
    "docs/operations/SOURCE_COVERAGE_REVIEW.md",
    "docs/operations/CONNECTOR_SCORECARD_REVIEW.md",
    "docs/operations/SOURCE_PACK_EXPORT_REVIEW.md",
    "docs/operations/H0_SOURCE_OS_INTEGRATION_AUDIT.md",
)
AUDIT_FILES = (
    "control/audits/h0-bundle-03-coverage-scorecards-source-packs-v0/README.md",
    "control/audits/h0-bundle-03-coverage-scorecards-source-packs-v0/h0_bundle_03_report.json",
    "control/audits/h0-bundle-03-coverage-scorecards-source-packs-v0/coverage_ledger_summary.md",
    "control/audits/h0-bundle-03-coverage-scorecards-source-packs-v0/connector_scorecard_summary.md",
    "control/audits/h0-bundle-03-coverage-scorecards-source-packs-v0/source_pack_summary.md",
    "control/audits/h0-bundle-03-coverage-scorecards-source-packs-v0/h0_integration_audit.md",
    "control/audits/h0-bundle-03-coverage-scorecards-source-packs-v0/h0_exit_gate_decision.md",
    "control/audits/h0-bundle-03-coverage-scorecards-source-packs-v0/h1_readiness_recommendation.md",
    "control/audits/h0-bundle-03-coverage-scorecards-source-packs-v0/no_live_call_report.md",
    "control/audits/h0-bundle-03-coverage-scorecards-source-packs-v0/validation.md",
    "control/audits/h0-bundle-03-coverage-scorecards-source-packs-v0/generated/sample_source_coverage_record.json",
    "control/audits/h0-bundle-03-coverage-scorecards-source-packs-v0/generated/sample_source_coverage_manifest.json",
    "control/audits/h0-bundle-03-coverage-scorecards-source-packs-v0/generated/sample_connector_scorecard.json",
    "control/audits/h0-bundle-03-coverage-scorecards-source-packs-v0/generated/sample_source_pack_manifest.json",
    "control/audits/h0-bundle-03-coverage-scorecards-source-packs-v0/generated/sample_h0_integration_report.json",
    "control/audits/h0-bundle-03-coverage-scorecards-source-packs-v0/generated/sample_h0_summary.md",
)
PYTHON_SCAN_PATHS = (
    "runtime/connectors/core/coverage_ledger.py",
    "runtime/connectors/core/connector_scorecard.py",
    "runtime/connectors/core/source_pack.py",
    "scripts/record_source_coverage.py",
    "scripts/build_source_pack.py",
    "scripts/score_connector.py",
    "scripts/validate_source_os_coverage_scorecards.py",
    "scripts/audit_h0_integration.py",
)
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads = {rel: load_json_object(root / rel, errors) for rel in CONTRACTS + INVENTORIES + COVERAGE_EXAMPLES + SCORECARD_EXAMPLES + PACK_EXAMPLES + ("control/audits/h0-bundle-03-coverage-scorecards-source-packs-v0/h0_bundle_03_report.json",)}
    validate_required_files(root, errors)
    validate_examples(payloads, errors)
    validate_policies(payloads, errors)
    validate_generated_outputs(payloads, errors)
    validate_python_no_network(root, errors)
    validate_scripts(root, errors)
    validate_h0_audit(root, errors)
    validate_no_private_roots(root, errors)
    return {
        "schema_version": "source_os_coverage_scorecards_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "H0-BUNDLE-03",
        "offline_default": True,
        "errors": errors,
    }


def validate_required_files(root: Path, errors: list[str]) -> None:
    for rel in CONTRACTS + INVENTORIES + COVERAGE_EXAMPLES + SCORECARD_EXAMPLES + PACK_EXAMPLES + DOCS + AUDIT_FILES:
        if not (root / rel).is_file():
            errors.append(f"missing required file: {rel}")


def validate_examples(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    coverage_records = []
    for rel in COVERAGE_EXAMPLES:
        payload = payloads.get(rel, {})
        if payload.get("schema_version") == "source_coverage_ledger.v0":
            try:
                validate_source_coverage_record(payload, {})
                coverage_records.append(payload)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{rel} invalid coverage record: {exc}")
        else:
            errors.extend(f"{rel}: {item}" for item in detect_coverage_truth_boundary_violations(payload, {}))
    if coverage_records:
        try:
            build_source_coverage_manifest(coverage_records, {})
        except Exception as exc:  # noqa: BLE001
            errors.append(f"coverage manifest builder failed: {exc}")
    for rel in SCORECARD_EXAMPLES:
        try:
            validate_connector_scorecard(payloads.get(rel, {}), {})
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{rel} invalid scorecard: {exc}")
    for rel in PACK_EXAMPLES:
        try:
            validate_source_pack_manifest(payloads.get(rel, {}), {})
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{rel} invalid source pack: {exc}")


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    coverage_truth = payloads.get("control/inventory/sources/source_coverage_truth_policy.json", {})
    for key in ("coverage_record_is_public_truth", "coverage_manifest_is_exhaustive_global_coverage", "coverage_record_can_mutate_public_index", "coverage_record_can_mutate_master_index", "coverage_record_can_claim_rights_clearance", "coverage_record_can_claim_malware_safety", "coverage_record_can_claim_verified_installability"):
        if coverage_truth.get(key) is not False:
            errors.append(f"source_coverage_truth_policy.{key} must be false")
    scorecard_metrics = payloads.get("control/inventory/connectors/connector_scorecard_metric_policy.json", {})
    for forbidden in ("production_ready", "external_superiority", "exhaustive_coverage", "rights_clearance", "malware_safety", "verified_installability", "automatic_future_connector_approval"):
        if forbidden not in scorecard_metrics.get("forbidden_metrics", []):
            errors.append(f"connector scorecard metric policy must forbid {forbidden}")
    pack_truth = payloads.get("control/inventory/packs/source_pack_truth_policy.json", {})
    for key in ("source_pack_is_accepted_truth", "source_pack_is_imported_state", "source_pack_is_submitted", "source_pack_can_mutate_public_index", "source_pack_can_mutate_master_index"):
        if pack_truth.get(key) is not False:
            errors.append(f"source_pack_truth_policy.{key} must be false")


def validate_generated_outputs(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    report = payloads.get("control/audits/h0-bundle-03-coverage-scorecards-source-packs-v0/h0_bundle_03_report.json", {})
    if report:
        if report.get("schema_version") != "h0_bundle_03_report.v0":
            errors.append("h0 bundle 03 report schema_version mismatch")
        if report.get("h0_exit_gate") not in {"PASS", "PASS_WITH_WARNINGS"}:
            errors.append("h0 bundle 03 report must record H0 pass or pass-with-warnings")
        if report.get("h1_readiness") not in {"READY_FOR_H1_POLICY_PACKS", "READY_WITH_WARNINGS"}:
            errors.append("h0 bundle 03 report must record H1 readiness")
        for detector in (detect_coverage_truth_boundary_violations, detect_scorecard_truth_boundary_violations, detect_source_pack_truth_boundary_violations):
            errors.extend(f"h0_bundle_03_report: {item}" for item in detector(report, {}))


def validate_python_no_network(root: Path, errors: list[str]) -> None:
    for rel in PYTHON_SCAN_PATHS:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing Python file: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for match in BANNED_IMPORT_RE.finditer(text):
            errors.append(f"forbidden import in {rel}: {match.group(1)}")
        if ("url" + "open(") in text or (".Re" + "quest(") in text:
            errors.append(f"forbidden live-call primitive in H0-BUNDLE-03 file: {rel}")


def validate_scripts(root: Path, errors: list[str]) -> None:
    commands = (
        [sys.executable, "scripts/record_source_coverage.py", "--input", "examples/source_coverage/internet_archive_coverage_record_v0.json", "--check"],
        [sys.executable, "scripts/score_connector.py", "--input", "examples/connectors/core/scorecards/internet_archive_scorecard_v0.json", "--check"],
        [sys.executable, "scripts/build_source_pack.py", "--input", "examples/source_packs/internet_archive_source_pack_manifest_v0.json", "--check"],
        [sys.executable, "scripts/audit_h0_integration.py", "--check"],
    )
    for command in commands:
        result = subprocess.run(command, cwd=root, check=False, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            errors.append(f"script failed: {' '.join(command)} :: {result.stdout} {result.stderr}")
    forbidden_commands = (
        [sys.executable, "scripts/record_source_coverage.py", "--input", "examples/source_coverage/internet_archive_coverage_record_v0.json", "--output", "site/dist/coverage.json"],
        [sys.executable, "scripts/score_connector.py", "--input", "examples/connectors/core/scorecards/internet_archive_scorecard_v0.json", "--output", "data/public_index/scorecard.json"],
        [sys.executable, "scripts/build_source_pack.py", "--input", "examples/source_packs/internet_archive_source_pack_manifest_v0.json", "--output", "contracts/source_pack.json"],
    )
    for command in forbidden_commands:
        result = subprocess.run(command, cwd=root, check=False, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            errors.append(f"script accepted forbidden output root: {' '.join(command)}")


def validate_h0_audit(root: Path, errors: list[str]) -> None:
    result = subprocess.run([sys.executable, "scripts/audit_h0_integration.py", "--check", "--json"], cwd=root, check=False, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        errors.append(f"H0 integration audit failed: {result.stdout} {result.stderr}")
        return
    payload = json.loads(result.stdout)
    if payload.get("h0_exit_gate") not in {"PASS", "PASS_WITH_WARNINGS"}:
        errors.append("H0 integration audit did not pass exit gate")
    if payload.get("h1_readiness") not in {"READY_FOR_H1_POLICY_PACKS", "READY_WITH_WARNINGS"}:
        errors.append("H0 integration audit did not produce H1 readiness")


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
        if (root / rel).exists():
            errors.append(f"local private root must not be created: {rel}")


def load_json_object(path: Path, errors: list[str]) -> Mapping[str, Any]:
    if not path.is_file():
        errors.append(f"missing JSON: {rel(path)}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"invalid JSON: {rel(path)}: {exc}")
        return {}
    if not isinstance(payload, Mapping):
        errors.append(f"JSON must be an object: {rel(path)}")
        return {}
    return payload


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

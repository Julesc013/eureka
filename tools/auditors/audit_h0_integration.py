#!/usr/bin/env python3
"""Audit H0 Source OS integration coherence offline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_OUTPUT_ROOTS = ("site/dist", "site/dist/data/public_index", "runtime", "contracts", "data/master_index", "master_index", ".aide.local", ".local/eureka", ".cache/eureka")
REQUIRED_PATHS = (
    "control/audits/h0-bundle-01-source-os-foundation-v0/h0_bundle_01_report.json",
    "control/audits/h0-bundle-02-connector-interface-replay-v0/h0_bundle_02_report.json",
    "contracts/source/records/source_registry.v2.json",
    "contracts/connectors/source_connector_interface.v0.json",
    "contracts/source/records/source_coverage_ledger.v0.json",
    "contracts/connectors/connector_scorecard.v0.json",
    "contracts/pack/source_pack_manifest.v0.json",
    "examples/sources/coverage/internet_archive_coverage_record_v0.json",
    "examples/connectors/core/scorecards/internet_archive_scorecard_v0.json",
    "examples/packs/source/internet_archive_source_pack_manifest_v0.json",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--json-output", help="Optional JSON audit output path.")
    parser.add_argument("--summary-output", help="Optional Markdown summary output path.")
    args = parser.parse_args(argv)
    try:
        report = audit_h0_integration(REPO_ROOT)
        if not args.check:
            if args.json_output:
                _write_json(args.json_output, report)
            if args.summary_output:
                _write_text(args.summary_output, render_summary_markdown(report))
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
        else:
            print("H0 integration audit", file=stdout)
            print(f"status: {report['status']}", file=stdout)
            print(f"h0_exit_gate: {report['h0_exit_gate']}", file=stdout)
            print(f"h1_readiness: {report['h1_readiness']}", file=stdout)
            for warning in report["warnings"]:
                print(f"WARN: {warning}", file=stdout)
            for error in report["errors"]:
                print(f"ERROR: {error}", file=stdout)
        return 0 if report["status"] in {"pass", "pass_with_warnings"} else 1
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "fail", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H0 integration audit", file=stdout)
            print("status: fail", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def audit_h0_integration(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    for rel in REQUIRED_PATHS:
        if not (root / rel).is_file():
            errors.append(f"missing required H0 artifact: {rel}")
    h0_01 = _load_optional_json(root / "control/audits/h0-bundle-01-source-os-foundation-v0/h0_bundle_01_report.json", warnings)
    h0_02 = _load_optional_json(root / "control/audits/h0-bundle-02-connector-interface-replay-v0/h0_bundle_02_report.json", warnings)
    for label, report in (("H0-BUNDLE-01", h0_01), ("H0-BUNDLE-02", h0_02)):
        if report and report.get("status") not in {"pass", "pass_with_warnings"}:
            errors.append(f"{label} status is not pass/pass_with_warnings: {report.get('status')}")
    for rel in (
        "examples/sources/coverage/internet_archive_coverage_record_v0.json",
        "examples/connectors/core/scorecards/internet_archive_scorecard_v0.json",
        "examples/packs/source/internet_archive_source_pack_manifest_v0.json",
    ):
        payload = _load_optional_json(root / rel, warnings)
        if _has_forbidden_true(payload):
            errors.append(f"truth/product boundary violation in {rel}")
    status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "schema_version": "h0_integration_audit.v0",
        "status": status,
        "h0_exit_gate": "FAIL" if errors else ("PASS_WITH_WARNINGS" if warnings else "PASS"),
        "h1_readiness": "NOT_READY" if errors else ("READY_WITH_WARNINGS" if warnings else "READY_FOR_H1_POLICY_PACKS"),
        "checks": {
            "source_registry_exists": (root / "contracts/source/records/source_registry.v2.json").is_file(),
            "connector_interface_exists": (root / "contracts/connectors/source_connector_interface.v0.json").is_file(),
            "coverage_ledger_exists": (root / "contracts/source/records/source_coverage_ledger.v0.json").is_file(),
            "connector_scorecard_exists": (root / "contracts/connectors/connector_scorecard.v0.json").is_file(),
            "source_pack_exists": (root / "contracts/pack/source_pack_manifest.v0.json").is_file(),
            "live_access_enabled": False,
            "source_sync_enabled": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
        },
        "warnings": warnings,
        "errors": errors,
        "next_task": "H1-BUNDLE-01 - First metadata wave source policy packs",
    }


def render_summary_markdown(report: Mapping[str, Any]) -> str:
    return "\n".join([
        "# H0 Integration Summary",
        "",
        f"- status: `{report.get('status')}`",
        f"- h0_exit_gate: `{report.get('h0_exit_gate')}`",
        f"- h1_readiness: `{report.get('h1_readiness')}`",
        f"- warnings: `{len(report.get('warnings', []))}`",
        f"- errors: `{len(report.get('errors', []))}`",
        "",
    ])


def _load_optional_json(path: Path, warnings: list[str]) -> dict[str, Any]:
    if not path.is_file():
        warnings.append(f"missing optional audit input: {rel(path)}")
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _has_forbidden_true(value: Any) -> bool:
    forbidden = {
        "accepted_public_truth",
        "accepted_source_truth",
        "accepted_evidence_truth",
        "public_index_mutated",
        "master_index_mutated",
        "mutated_public_index",
        "mutated_master_index",
        "rights_clearance_claimed",
        "malware_safety_claimed",
        "verified_installability_claimed",
        "source_pack_is_accepted_truth",
        "source_pack_is_imported_state",
        "source_pack_is_submitted",
        "scorecard_claims_production_readiness",
        "scorecard_auto_approves_future_connectors",
        "coverage_claims_exhaustive_global_coverage",
    }
    if isinstance(value, Mapping):
        return any((key in forbidden and child is True) or _has_forbidden_true(child) for key, child in value.items())
    if isinstance(value, list):
        return any(_has_forbidden_true(child) for child in value)
    return False


def _write_json(path_text: str, payload: Mapping[str, Any]) -> None:
    path = _safe_output_path(Path(path_text))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path_text: str, text: str) -> None:
    path = _safe_output_path(Path(path_text))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _safe_output_path(path: Path) -> Path:
    resolved = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    repo_resolved = REPO_ROOT.resolve()
    try:
        rel_path = resolved.relative_to(repo_resolved).as_posix()
        rel_lower = rel_path.casefold()
        for forbidden in FORBIDDEN_OUTPUT_ROOTS:
            forbidden_lower = forbidden.casefold().rstrip("/")
            if rel_lower == forbidden_lower or rel_lower.startswith(forbidden_lower + "/"):
                raise ValueError(f"refusing forbidden output root: {forbidden}")
        if rel_lower.startswith("control/audits/") and "/generated/" in rel_lower:
            return resolved
        raise ValueError(f"refusing output outside approved audit generated roots: {rel_path}")
    except ValueError as exc:
        if str(exc).startswith("refusing"):
            raise
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
            return resolved
        except ValueError as temp_exc:
            raise ValueError(f"refusing output outside repository approved roots or temp directory: {resolved}") from temp_exc


def rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())

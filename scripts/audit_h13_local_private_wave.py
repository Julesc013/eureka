#!/usr/bin/env python3
"""Audit H13 local/private/restricted wave artifacts offline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist", "data/public_index", "runtime", "contracts", "control/inventory/sources",
    "control/inventory/publication", "data/master_index", "master_index", "local_sources",
    "cas", "private_sources", "credentials", "accounts", "user_url_fetch",
    "import_export_staging", "archive_extractions", "source_cache", "evidence_ledger",
    ".aide.local", ".local/eureka", ".cache/eureka",
)

from control.prototypes.legacy_runtime.connectors.h13_local_private.normalizer_common import H13_SOURCE_IDS  # noqa: E402
from control.prototypes.legacy_runtime.connectors.h13_local_private.quality_delta import build_h13_quality_delta  # noqa: E402
from control.prototypes.legacy_runtime.connectors.h13_local_private.review_integration import (  # noqa: E402
    build_h13_review_integration_result,
    detect_h13_review_product_boundary_violations,
    detect_h13_review_truth_boundary_violations,
    load_h13_local_private_outputs,
)
from control.prototypes.legacy_runtime.connectors.h13_local_private.wave_postmortem import (  # noqa: E402
    build_h13_connector_wave_postmortem,
    build_h13_integration_audit,
    build_h13_next_phase_recommendation,
)

AUDIT_DIR = Path("control/audits/h13-bundle-04-local-private-review-quality-audit-v0")


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate only and write no files.")
    parser.add_argument("--json-output", help="Optional audit JSON output path.")
    parser.add_argument("--summary-output", help="Optional audit Markdown output path.")
    args = parser.parse_args(argv)
    try:
        audit = build_wave_audit(REPO_ROOT)
        if args.json_output and not args.check:
            write_json(args.json_output, audit)
        if args.summary_output and not args.check:
            write_text(args.summary_output, render_summary(audit))
        status = "pass" if audit["h13_exit_gate"] in {"PASS", "PASS_WITH_WARNINGS"} else "partial"
        print("H13 local/private wave audit", file=stdout)
        print(f"status: {status}", file=stdout)
        print(f"h13_exit_gate: {audit['h13_exit_gate']}", file=stdout)
        print(f"next_phase_recommendation: {audit['next_phase_recommendation']}", file=stdout)
        print(f"source_count: {len(audit['audited_sources'])}", file=stdout)
        print(f"wrote_files: {str(bool((args.json_output or args.summary_output) and not args.check)).lower()}", file=stdout)
        return 0 if status == "pass" else 1
    except Exception as exc:  # noqa: BLE001
        print("H13 local/private wave audit", file=stdout)
        print("status: invalid", file=stdout)
        print(f"ERROR: {exc}", file=stdout)
        return 1


def build_wave_audit(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    required_paths = [
        "control/audits/h13-bundle-01-local-private-policy-packs-v0/h13_bundle_01_report.json",
        "control/audits/h13-bundle-02-local-private-fixture-runtime-v0/h13_bundle_02_report.json",
        "control/audits/h13-bundle-03-local-private-boundary-dry-runs-v0/h13_bundle_03_report.json",
        "control/audits/h13-bundle-04-local-private-review-quality-audit-v0/h13_bundle_04_report.json",
        "examples/connectors/h13_local_private/replay_results",
        "examples/connectors/h13_local_private/boundary_dry_run_results",
        "examples/connectors/h13_local_private/review_integration",
    ]
    for rel in required_paths:
        if not (root / rel).exists():
            errors.append(f"missing artifact: {rel}")
    replay_paths = sorted((root / "examples/connectors/h13_local_private/replay_results").glob("*.json"))
    boundary_paths = sorted((root / "examples/connectors/h13_local_private/boundary_dry_run_results").glob("*.json"))
    outputs = load_h13_local_private_outputs([*replay_paths, *boundary_paths])
    review = build_h13_review_integration_result({"outputs": outputs, "input_refs": [rel_path(path) for path in [*replay_paths, *boundary_paths]]})
    h13_boundary_report_path = root / "control/audits/h13-bundle-03-local-private-boundary-dry-runs-v0/h13_bundle_03_report.json"
    if h13_boundary_report_path.exists():
        h13_boundary_report = load_json(h13_boundary_report_path)
        report_blocked = h13_boundary_report.get("boundary_dry_run_results", {}).get("blocked_sources", [])
        if isinstance(report_blocked, list):
            review["blocked_sources"] = sorted(set(review.get("blocked_sources", [])) | {str(source) for source in report_blocked})
            review["warnings"] = ["H13 boundary dry-runs remain blocked pending operator/user approval."] if review["blocked_sources"] else []
    delta = build_h13_quality_delta({"review_integration_result": review})
    postmortem = build_h13_connector_wave_postmortem(review, delta)
    recommendation = build_h13_next_phase_recommendation(postmortem)
    audit = build_h13_integration_audit(review, delta, postmortem, recommendation)
    if set(audit.get("audited_sources", [])) != set(H13_SOURCE_IDS):
        errors.append("audited sources must match all twelve H13 source IDs")
    errors.extend(detect_h13_review_truth_boundary_violations(audit))
    errors.extend(detect_h13_review_product_boundary_violations(audit))
    if errors:
        audit["h13_exit_gate"] = "PARTIAL"
        audit["next_phase_recommendation"] = "NEEDS_REMEDIATION"
        audit["blockers"] = sorted(dict.fromkeys(audit.get("blockers", []) + errors))
    return audit


def render_summary(audit: Mapping[str, Any]) -> str:
    return "\n".join([
        "# H13 Integration Audit Summary",
        "",
        f"- h13_exit_gate: `{audit.get('h13_exit_gate')}`",
        f"- next_phase_recommendation: `{audit.get('next_phase_recommendation')}`",
        f"- audited_sources: `{len(audit.get('audited_sources', []))}`",
        "- local_source_identity_truth_accepted: `false`",
        "- private_source_access_permission: `false`",
        "- user_supplied_url_fetch_permission: `false`",
        "- authenticated_access_permission: `false`",
        "- restricted_source_access_permission: `false`",
        "- cas_import_permission: `false`",
        "- pack_export_import_permission: `false`",
        "- privacy_public_safety_truth: `false`",
        "- rights_safety_truth_accepted: `false`",
        "- source_cache_writes: `false`",
        "- evidence_writes: `false`",
        "- public_index_writes: `false`",
        "- private_publication: `false`",
        "",
    ])


def write_json(path_text: str, payload: Mapping[str, Any]) -> None:
    path = _safe_output_path(Path(path_text))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path_text: str, text: str) -> None:
    path = _safe_output_path(Path(path_text))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError(f"{path} must contain a JSON object")
    return dict(payload)


def _safe_output_path(path: Path) -> Path:
    resolved = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    repo_resolved = REPO_ROOT.resolve()
    try:
        rel = resolved.relative_to(repo_resolved).as_posix()
        rel_lower = rel.casefold()
        for forbidden in FORBIDDEN_OUTPUT_ROOTS:
            forbidden_lower = forbidden.casefold().rstrip("/")
            if rel_lower == forbidden_lower or rel_lower.startswith(forbidden_lower + "/"):
                raise ValueError(f"refusing forbidden output root: {forbidden}")
        if rel_lower.startswith("control/audits/") and (rel_lower.endswith(".json") or rel_lower.endswith(".md")):
            return resolved
        raise ValueError(f"refusing output outside approved H13 audit roots: {rel}")
    except ValueError as exc:
        if str(exc).startswith("refusing"):
            raise
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
            return resolved
        except ValueError as temp_exc:
            raise ValueError(f"refusing output outside repository approved roots or temp directory: {resolved}") from temp_exc


def rel_path(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())

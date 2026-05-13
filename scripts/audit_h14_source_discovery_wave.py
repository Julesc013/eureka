#!/usr/bin/env python3
"""Audit H14 Source OS wave artifacts offline."""

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
    "control/inventory/connectors", "source_registry_mutation", "connector_registry_mutation",
    "pack_import_staging", "pack_export_staging", "source_cache", "evidence_ledger",
    "review_queue", "public_index", "master_index", ".aide.local", ".local/eureka",
    ".cache/eureka", "local_sources", "private_sources",
)

from control.prototypes.legacy_runtime.connectors.h14_source_discovery.normalizer_common import H14_SOURCE_IDS  # noqa: E402
from control.prototypes.legacy_runtime.connectors.h14_source_discovery.quality_delta import build_h14_quality_delta  # noqa: E402
from control.prototypes.legacy_runtime.connectors.h14_source_discovery.review_integration import (  # noqa: E402
    build_h14_review_integration_result,
    detect_h14_review_product_boundary_violations,
    detect_h14_review_registry_or_pack_mutation_violations,
    detect_h14_review_truth_boundary_violations,
    load_h14_source_discovery_outputs,
)
from control.prototypes.legacy_runtime.connectors.h14_source_discovery.wave_postmortem import (  # noqa: E402
    build_h14_connector_wave_postmortem,
    build_h14_integration_audit,
    build_h14_next_phase_recommendation,
)


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
        status = "pass" if audit["h14_exit_gate"] in {"PASS", "PASS_WITH_WARNINGS"} else "partial"
        print("H14 Source OS wave audit", file=stdout)
        print(f"status: {status}", file=stdout)
        print(f"h14_exit_gate: {audit['h14_exit_gate']}", file=stdout)
        print(f"next_phase_recommendation: {audit['next_phase_recommendation']}", file=stdout)
        print(f"source_count: {len(audit['audited_sources'])}", file=stdout)
        print(f"wrote_files: {str(bool((args.json_output or args.summary_output) and not args.check)).lower()}", file=stdout)
        return 0 if status == "pass" else 1
    except Exception as exc:  # noqa: BLE001
        print("H14 Source OS wave audit", file=stdout)
        print("status: invalid", file=stdout)
        print(f"ERROR: {exc}", file=stdout)
        return 1


def build_wave_audit(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    required_paths = [
        "control/audits/h14-bundle-01-source-discovery-policy-packs-v0/h14_bundle_01_report.json",
        "control/audits/h14-bundle-02-source-discovery-fixture-runtime-v0/h14_bundle_02_report.json",
        "control/audits/h14-bundle-03-source-discovery-rollup-dry-runs-v0/h14_bundle_03_report.json",
        "control/audits/h14-bundle-04-source-discovery-review-quality-audit-v0/h14_bundle_04_report.json",
        "examples/connectors/h14_source_discovery/replay_results",
        "examples/connectors/h14_source_discovery/rollup_dry_run_results",
        "examples/connectors/h14_source_discovery/review_integration",
    ]
    for rel in required_paths:
        if not (root / rel).exists():
            errors.append(f"missing artifact: {rel}")
    replay_paths = sorted((root / "examples/connectors/h14_source_discovery/replay_results").glob("*.json"))
    rollup_paths = sorted((root / "examples/connectors/h14_source_discovery/rollup_dry_run_results").glob("*.json"))
    outputs = load_h14_source_discovery_outputs([*replay_paths, *rollup_paths])
    review = build_h14_review_integration_result({"outputs": outputs, "input_refs": [rel_path(path) for path in [*replay_paths, *rollup_paths]]})
    h14_rollup_report_path = root / "control/audits/h14-bundle-03-source-discovery-rollup-dry-runs-v0/h14_bundle_03_report.json"
    if h14_rollup_report_path.exists():
        h14_rollup_report = load_json(h14_rollup_report_path)
        report_blocked = h14_rollup_report.get("rollup_dry_run_results", {}).get("blocked_concepts", [])
        if isinstance(report_blocked, list):
            review["blocked_sources"] = sorted(set(review.get("blocked_sources", [])) | {str(source) for source in report_blocked})
            review["warnings"] = ["H14 rollup dry-runs include policy-blocked concepts; fixture-equivalent evidence carries review integration."] if review["blocked_sources"] else []
    delta = build_h14_quality_delta({"review_integration_result": review})
    postmortem = build_h14_connector_wave_postmortem(review, delta)
    recommendation = build_h14_next_phase_recommendation(postmortem)
    audit = build_h14_integration_audit(review, delta, postmortem, recommendation)
    if set(audit.get("audited_sources", [])) != set(H14_SOURCE_IDS):
        errors.append("audited sources must match all eleven H14 source IDs")
    errors.extend(detect_h14_review_truth_boundary_violations(audit))
    errors.extend(detect_h14_review_product_boundary_violations(audit))
    errors.extend(detect_h14_review_registry_or_pack_mutation_violations(audit))
    if errors:
        audit["h14_exit_gate"] = "PARTIAL"
        audit["next_phase_recommendation"] = "NEEDS_REMEDIATION"
        audit["blockers"] = sorted(dict.fromkeys(audit.get("blockers", []) + errors))
    return audit


def render_summary(audit: Mapping[str, Any]) -> str:
    return "\n".join([
        "# H14 Integration Audit Summary",
        "",
        f"- h14_exit_gate: `{audit.get('h14_exit_gate')}`",
        f"- next_phase_recommendation: `{audit.get('next_phase_recommendation')}`",
        f"- audited_sources: `{len(audit.get('audited_sources', []))}`",
        "- source_need_truth_accepted: `false`",
        "- source_candidate_truth_accepted: `false`",
        "- source_discovery_truth_accepted: `false`",
        "- source_approval: `false`",
        "- connector_approval: `false`",
        "- pack_export_import: `false`",
        "- registry_mutation: `false`",
        "- public_index_writes: `false`",
        "- production_readiness: `false`",
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
        raise ValueError(f"refusing output outside approved H14 audit roots: {rel}")
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

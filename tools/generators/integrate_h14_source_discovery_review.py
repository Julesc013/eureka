#!/usr/bin/env python3
"""Integrate explicit H14 Source OS outputs into offline review previews."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist", "site/dist/data/public_index", "runtime", "contracts",
    "control/inventory/sources", "control/inventory/connectors",
    "source_registry_mutation", "connector_registry_mutation",
    "pack_import_staging", "pack_export_staging", "pack_imports", "pack_exports",
    "source_cache", "evidence_ledger", "review_queue", "master_index", "public_index",
    ".aide.local", ".local/eureka", ".cache/eureka", "local_sources", "private_sources",
    "source_discovery_runtime", "external_source_fetch",
)

from archive.prototypes.legacy_runtime.connectors.h14_source_discovery.quality_delta import build_h14_quality_delta  # noqa: E402
from archive.prototypes.legacy_runtime.connectors.h14_source_discovery.review_integration import (  # noqa: E402
    build_h14_review_integration_result,
    detect_h14_review_product_boundary_violations,
    detect_h14_review_truth_boundary_violations,
    load_h14_source_discovery_outputs,
    summarize_h14_review_integration,
)
from archive.prototypes.legacy_runtime.connectors.h14_source_discovery.wave_postmortem import (  # noqa: E402
    build_h14_connector_wave_postmortem,
    build_h14_integration_audit,
    build_h14_next_phase_recommendation,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", default=[], help="Explicit H14 output JSON file. May be repeated.")
    parser.add_argument("--input-dir", action="append", default=[], help="Directory containing H14 output JSON files. May be repeated.")
    parser.add_argument("--output-dir", help="Optional output directory for review previews.")
    parser.add_argument("--check", action="store_true", help="Validate only and write no files.")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    args = parser.parse_args(argv)
    try:
        artifacts = run_integration(args.input, args.input_dir)
        if args.output_dir and not args.check:
            write_outputs(args.output_dir, artifacts)
        summary = summarize_h14_review_integration(artifacts["review_integration_result"])
        summary["wrote_files"] = bool(args.output_dir and not args.check)
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H14 Source OS review integration", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"source_need_review_seed_count: {summary['source_need_review_seed_count']}", file=stdout)
            print(f"source_candidate_review_seed_count: {summary['source_candidate_review_seed_count']}", file=stdout)
            print(f"blocked_sources: {len(summary['blocked_sources'])}", file=stdout)
            print(f"wrote_files: {str(summary['wrote_files']).lower()}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H14 Source OS review integration", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def run_integration(inputs: Sequence[str], input_dirs: Sequence[str]) -> dict[str, Any]:
    paths = _collect_input_paths(inputs, input_dirs)
    outputs = load_h14_source_discovery_outputs(paths)
    result = build_h14_review_integration_result({"outputs": outputs, "input_refs": [rel(path) for path in paths]})
    _merge_h14_bundle_03_blocked_sources(result)
    errors = detect_h14_review_truth_boundary_violations(result) + detect_h14_review_product_boundary_violations(result)
    if errors:
        raise ValueError("; ".join(errors))
    delta = build_h14_quality_delta({"review_integration_result": result})
    postmortem = build_h14_connector_wave_postmortem(result, delta)
    recommendation = build_h14_next_phase_recommendation(postmortem)
    audit = build_h14_integration_audit(result, delta, postmortem, recommendation)
    return {
        "review_integration_result": result,
        "source_need_review_seed": _first(result.get("source_need_review_seeds")),
        "source_candidate_review_seed": _first(result.get("source_candidate_review_seeds")),
        "source_discovery_candidate_review_seed": _first(result.get("source_discovery_candidate_review_seeds")),
        "source_pack_manifest_review_seed": _first(result.get("source_pack_manifest_review_seeds")),
        "connector_pack_manifest_review_seed": _first(result.get("connector_pack_manifest_review_seeds")),
        "coverage_manifest_review_seed": _first(result.get("coverage_manifest_review_seeds")),
        "connector_scorecard_review_seed": _first(result.get("connector_scorecard_review_seeds")),
        "reliability_freshness_review_seed": _first(result.get("reliability_freshness_review_seeds")),
        "dispute_revocation_review_seed": _first(result.get("dispute_revocation_review_seeds")),
        "lineage_provenance_review_seed": _first(result.get("lineage_provenance_review_seeds")),
        "pack_import_export_boundary_review_seed": _first(result.get("pack_import_export_boundary_review_seeds")),
        "source_cache_review_seed": _first(result.get("source_cache_review_seeds")),
        "evidence_candidate_review_seed": _first(result.get("evidence_candidate_review_seeds")),
        "candidate_promotion_preview": _first(result.get("candidate_promotion_previews")),
        "source_coverage_update_preview": _first(result.get("coverage_update_previews")),
        "connector_scorecard_update": _first(result.get("scorecard_updates")),
        "source_pack_update_preview": _first(result.get("source_pack_update_previews")),
        "quality_delta_report": delta,
        "connector_wave_postmortem": postmortem,
        "next_phase_recommendation": recommendation,
        "integration_audit": audit,
        "blocked_review_integration": build_blocked_review_integration(result),
        "summary_markdown": render_summary_markdown(summarize_h14_review_integration(result)),
    }


def build_blocked_review_integration(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "h14_blocked_review_integration.v0",
        "wave_id": "H14",
        "review_integration_status": "fixture_review_integrated_with_rollup_dry_run_blocks",
        "blocked_sources": list(result.get("blocked_sources", [])),
        "source_discovery_runtime_permission": False,
        "source_registry_mutation": False,
        "connector_registry_mutation": False,
        "pack_export_import_permission": False,
        "source_cache_writes": False,
        "evidence_writes": False,
        "public_index_writes": False,
        "truth_boundary": result.get("truth_boundary", {}),
        "product_boundary": result.get("product_boundary", {}),
        "limitations": ["Blocked rollup dry-runs are recorded as policy evidence only."],
        "notes": ["Blocked review integration is not a review decision."],
    }


def _merge_h14_bundle_03_blocked_sources(result: dict[str, Any]) -> None:
    report_path = REPO_ROOT / "control/audits/h14-bundle-03-source-discovery-rollup-dry-runs-v0/h14_bundle_03_report.json"
    if not report_path.is_file():
        return
    report = json.loads(report_path.read_text(encoding="utf-8"))
    blocked = report.get("rollup_dry_run_results", {}).get("blocked_concepts", [])
    if not isinstance(blocked, list):
        return
    merged = sorted(set(result.get("blocked_sources", [])) | {str(source) for source in blocked if source})
    result["blocked_sources"] = merged
    if merged:
        result["warnings"] = ["H14 rollup dry-runs include policy-blocked concepts; fixture-equivalent evidence carries review integration."]


def write_outputs(output_dir_text: str, artifacts: Mapping[str, Any]) -> None:
    output_dir = _safe_output_dir(Path(output_dir_text))
    output_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "h14_source_need_review_seed_v0.json": "source_need_review_seed",
        "h14_source_candidate_review_seed_v0.json": "source_candidate_review_seed",
        "h14_source_discovery_candidate_review_seed_v0.json": "source_discovery_candidate_review_seed",
        "h14_source_pack_manifest_review_seed_v0.json": "source_pack_manifest_review_seed",
        "h14_connector_pack_manifest_review_seed_v0.json": "connector_pack_manifest_review_seed",
        "h14_coverage_manifest_review_seed_v0.json": "coverage_manifest_review_seed",
        "h14_connector_scorecard_review_seed_v0.json": "connector_scorecard_review_seed",
        "h14_reliability_freshness_review_seed_v0.json": "reliability_freshness_review_seed",
        "h14_dispute_revocation_review_seed_v0.json": "dispute_revocation_review_seed",
        "h14_lineage_provenance_review_seed_v0.json": "lineage_provenance_review_seed",
        "h14_pack_import_export_boundary_review_seed_v0.json": "pack_import_export_boundary_review_seed",
        "h14_source_cache_review_seed_v0.json": "source_cache_review_seed",
        "h14_evidence_candidate_review_seed_v0.json": "evidence_candidate_review_seed",
        "h14_candidate_promotion_preview_v0.json": "candidate_promotion_preview",
        "h14_source_coverage_update_preview_v0.json": "source_coverage_update_preview",
        "h14_connector_scorecard_update_v0.json": "connector_scorecard_update",
        "h14_source_pack_update_preview_v0.json": "source_pack_update_preview",
        "h14_quality_delta_report_v0.json": "quality_delta_report",
        "h14_connector_wave_postmortem_v0.json": "connector_wave_postmortem",
        "h14_blocked_review_integration_v0.json": "blocked_review_integration",
        "h14_review_integration_result_v0.json": "review_integration_result",
        "h14_next_phase_recommendation_v0.json": "next_phase_recommendation",
        "h14_integration_audit_v0.json": "integration_audit",
    }
    for name, key in files.items():
        (output_dir / name).write_text(json.dumps(artifacts[key], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "h14_summary.md").write_text(str(artifacts["summary_markdown"]), encoding="utf-8")
    if output_dir.name == "generated":
        sample_map = {
            "sample_h14_review_integration_result.json": artifacts["review_integration_result"],
            "sample_h14_quality_delta_report.json": artifacts["quality_delta_report"],
            "sample_h14_connector_wave_postmortem.json": artifacts["connector_wave_postmortem"],
            "sample_h14_integration_audit.json": artifacts["integration_audit"],
            "sample_h14_next_phase_recommendation.json": artifacts["next_phase_recommendation"],
        }
        for name, payload in sample_map.items():
            (output_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (output_dir / "sample_h14_summary.md").write_text(str(artifacts["summary_markdown"]), encoding="utf-8")


def render_summary_markdown(summary: Mapping[str, Any]) -> str:
    return "\n".join([
        "# H14 Review Integration Summary",
        "",
        f"- status: `{summary.get('status')}`",
        f"- source_count: `{summary.get('source_count', 0)}`",
        f"- source_need_review_seed_count: `{summary.get('source_need_review_seed_count', 0)}`",
        f"- source_candidate_review_seed_count: `{summary.get('source_candidate_review_seed_count', 0)}`",
        f"- blocked_sources: `{', '.join(summary.get('blocked_sources', []))}`",
        "- source_discovery_runtime: `false`",
        "- pack_export_import: `false`",
        "- registry_mutation: `false`",
        "- source_cache_writes: `false`",
        "- evidence_writes: `false`",
        "- public_index_writes: `false`",
        "- truth_acceptance: `false`",
        "",
    ])


def _collect_input_paths(inputs: Sequence[str], input_dirs: Sequence[str]) -> list[Path]:
    paths: list[Path] = []
    for item in inputs:
        paths.append(_resolve_input(Path(item)))
    for item in input_dirs:
        directory = _resolve_input(Path(item))
        if not directory.is_dir():
            raise ValueError(f"input-dir is not a directory: {directory}")
        paths.extend(sorted(path for path in directory.glob("*.json") if path.is_file()))
    if not paths:
        raise ValueError("at least one --input or --input-dir is required")
    return paths


def _resolve_input(path: Path) -> Path:
    resolved = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    if not resolved.exists():
        raise ValueError(f"input path does not exist: {resolved}")
    return resolved


def _safe_output_dir(path: Path) -> Path:
    resolved = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    repo_resolved = REPO_ROOT.resolve()
    try:
        rel_path = resolved.relative_to(repo_resolved).as_posix()
        rel_lower = rel_path.casefold().rstrip("/")
        for forbidden in FORBIDDEN_OUTPUT_ROOTS:
            forbidden_lower = forbidden.casefold().rstrip("/")
            if rel_lower == forbidden_lower or rel_lower.startswith(forbidden_lower + "/"):
                raise ValueError(f"refusing forbidden output root: {forbidden}")
        if rel_lower == "examples/connectors/h14_source_discovery/review_integration" or rel_lower.startswith("examples/connectors/h14_source_discovery/review_integration/"):
            return resolved
        if rel_lower.startswith("control/audits/") and (rel_lower.endswith("/generated") or "/generated/" in rel_lower):
            return resolved
        raise ValueError(f"refusing output outside approved H14 review roots: {rel_path}")
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


def _first(items: list[Any] | None) -> Any:
    return items[0] if items else None


if __name__ == "__main__":
    raise SystemExit(main())

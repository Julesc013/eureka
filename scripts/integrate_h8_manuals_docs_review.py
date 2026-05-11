#!/usr/bin/env python3
"""Integrate explicit H8 manuals/docs/standards outputs into offline review previews."""

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
    "site/dist",
    "data/public_index",
    "runtime",
    "contracts",
    "control/inventory/publication",
    "control/inventory/sources",
    "data/master_index",
    "master_index",
    "downloads",
    "document_downloads",
    "pdf_downloads",
    "manual_downloads",
    "datasheet_downloads",
    "standards_downloads",
    "schematic_downloads",
    "service_manual_downloads",
    "ocr",
    "full_text",
    "media_downloads",
    "restricted_sources",
    "repair_actions",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
)

from runtime.connectors.h8_manuals_docs_standards.quality_delta import build_h8_quality_delta  # noqa: E402
from runtime.connectors.h8_manuals_docs_standards.review_integration import (  # noqa: E402
    build_h8_review_integration_result,
    detect_h8_review_product_boundary_violations,
    detect_h8_review_truth_boundary_violations,
    load_h8_manuals_docs_outputs,
    summarize_h8_review_integration,
)
from runtime.connectors.h8_manuals_docs_standards.wave_postmortem import (  # noqa: E402
    build_h8_connector_wave_postmortem,
    build_h8_integration_audit,
    build_h8_next_phase_recommendation,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", default=[], help="Explicit H8 output JSON file. May be repeated.")
    parser.add_argument("--input-dir", action="append", default=[], help="Directory containing H8 output JSON files. May be repeated.")
    parser.add_argument("--output-dir", help="Optional output directory for review previews.")
    parser.add_argument("--check", action="store_true", help="Validate only and write no files.")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    args = parser.parse_args(argv)
    try:
        artifacts = run_integration(args.input, args.input_dir)
        if args.output_dir and not args.check:
            write_outputs(args.output_dir, artifacts)
        summary = summarize_h8_review_integration(artifacts["review_integration_result"])
        summary["wrote_files"] = bool(args.output_dir and not args.check)
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H8 manuals/docs/standards review integration", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"technical_document_identity_review_seed_count: {summary['technical_document_identity_review_seed_count']}", file=stdout)
            print(f"manual_artifact_relation_review_seed_count: {summary['manual_artifact_relation_review_seed_count']}", file=stdout)
            print(f"datasheet_device_identity_review_seed_count: {summary['datasheet_device_identity_review_seed_count']}", file=stdout)
            print(f"standards_specification_identity_review_seed_count: {summary['standards_specification_identity_review_seed_count']}", file=stdout)
            print(f"install_requirement_claim_review_seed_count: {summary['install_requirement_claim_review_seed_count']}", file=stdout)
            print(f"repair_service_safety_review_seed_count: {summary['repair_service_safety_review_seed_count']}", file=stdout)
            print(f"access_rights_review_seed_count: {summary['access_rights_review_seed_count']}", file=stdout)
            print(f"wrote_files: {str(summary['wrote_files']).lower()}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H8 manuals/docs/standards review integration", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def run_integration(inputs: Sequence[str], input_dirs: Sequence[str]) -> dict[str, Any]:
    paths = _collect_input_paths(inputs, input_dirs)
    outputs = load_h8_manuals_docs_outputs(paths)
    result = build_h8_review_integration_result({"outputs": outputs, "input_refs": [rel(path) for path in paths]})
    _merge_h8_bundle_03_blocked_sources(result)
    errors = detect_h8_review_truth_boundary_violations(result) + detect_h8_review_product_boundary_violations(result)
    if errors:
        raise ValueError("; ".join(errors))
    delta = build_h8_quality_delta({"review_integration_result": result})
    postmortem = build_h8_connector_wave_postmortem(result, delta)
    recommendation = build_h8_next_phase_recommendation(postmortem)
    audit = build_h8_integration_audit(result, delta, postmortem, recommendation)
    return {
        "review_integration_result": result,
        "technical_document_identity_review_seed": _first(result.get("technical_document_identity_review_seeds")),
        "manual_artifact_relation_review_seed": _first(result.get("manual_artifact_relation_review_seeds")),
        "datasheet_device_identity_review_seed": _first(result.get("datasheet_device_identity_review_seeds")),
        "standards_specification_identity_review_seed": _first(result.get("standards_specification_identity_review_seeds")),
        "install_requirement_claim_review_seed": _first(result.get("install_requirement_claim_review_seeds")),
        "repair_service_safety_review_seed": _first(result.get("repair_service_safety_review_seeds")),
        "access_rights_review_seed": _first(result.get("access_rights_review_seeds")),
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
        "summary_markdown": render_summary_markdown(summarize_h8_review_integration(result)),
    }


def build_blocked_review_integration(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "h8_blocked_review_integration.v0",
        "wave_id": "H8",
        "review_integration_status": "fixture_review_integrated_with_live_probe_blocks",
        "blocked_sources": list(result.get("blocked_sources", [])),
        "source_cache_runtime_mutated": False,
        "evidence_ledger_runtime_mutated": False,
        "review_queue_runtime_mutated": False,
        "document_truth_accepted": False,
        "manual_artifact_relation_truth_accepted": False,
        "datasheet_device_truth_accepted": False,
        "standards_truth_accepted": False,
        "install_requirement_truth_accepted": False,
        "repair_service_safety_truth_accepted": False,
        "access_rights_truth_accepted": False,
        "query_fetch_download_extract": False,
        "restricted_source_access": False,
        "repair_or_install_action_permission": False,
        "truth_boundary": result.get("truth_boundary", {}),
        "product_boundary": result.get("product_boundary", {}),
        "limitations": ["Blocked live probes are recorded as policy evidence only."],
        "notes": ["Blocked review integration is not a review decision."],
    }


def _merge_h8_bundle_03_blocked_sources(result: dict[str, Any]) -> None:
    report_path = REPO_ROOT / "control/audits/h8-bundle-03-manuals-docs-live-probes-v0/h8_bundle_03_report.json"
    if not report_path.is_file():
        return
    report = json.loads(report_path.read_text(encoding="utf-8"))
    blocked = report.get("live_probe_results", {}).get("blocked_sources", [])
    if not isinstance(blocked, list):
        return
    merged = sorted(set(result.get("blocked_sources", [])) | {str(source) for source in blocked if source})
    result["blocked_sources"] = merged
    if merged:
        result["warnings"] = ["H8 live probes remain blocked pending operator approval."]


def write_outputs(output_dir_text: str, artifacts: Mapping[str, Any]) -> None:
    output_dir = _safe_output_dir(Path(output_dir_text))
    output_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "h8_technical_document_identity_review_seed_v0.json": artifacts["technical_document_identity_review_seed"],
        "h8_manual_artifact_relation_review_seed_v0.json": artifacts["manual_artifact_relation_review_seed"],
        "h8_datasheet_device_identity_review_seed_v0.json": artifacts["datasheet_device_identity_review_seed"],
        "h8_standards_specification_identity_review_seed_v0.json": artifacts["standards_specification_identity_review_seed"],
        "h8_install_requirement_claim_review_seed_v0.json": artifacts["install_requirement_claim_review_seed"],
        "h8_repair_service_safety_review_seed_v0.json": artifacts["repair_service_safety_review_seed"],
        "h8_access_rights_review_seed_v0.json": artifacts["access_rights_review_seed"],
        "h8_source_cache_review_seed_v0.json": artifacts["source_cache_review_seed"],
        "h8_evidence_candidate_review_seed_v0.json": artifacts["evidence_candidate_review_seed"],
        "h8_candidate_promotion_preview_v0.json": artifacts["candidate_promotion_preview"],
        "h8_source_coverage_update_preview_v0.json": artifacts["source_coverage_update_preview"],
        "h8_connector_scorecard_update_v0.json": artifacts["connector_scorecard_update"],
        "h8_source_pack_update_preview_v0.json": artifacts["source_pack_update_preview"],
        "h8_review_integration_result_v0.json": artifacts["review_integration_result"],
        "h8_quality_delta_report_v0.json": artifacts["quality_delta_report"],
        "h8_connector_wave_postmortem_v0.json": artifacts["connector_wave_postmortem"],
        "h8_next_phase_recommendation_v0.json": artifacts["next_phase_recommendation"],
        "h8_integration_audit_v0.json": artifacts["integration_audit"],
        "h8_blocked_review_integration_v0.json": artifacts["blocked_review_integration"],
    }
    for name, payload in files.items():
        (output_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "h8_summary.md").write_text(str(artifacts["summary_markdown"]), encoding="utf-8")
    if output_dir.name == "generated":
        sample_map = {
            "sample_h8_review_integration_result.json": artifacts["review_integration_result"],
            "sample_h8_quality_delta_report.json": artifacts["quality_delta_report"],
            "sample_h8_connector_wave_postmortem.json": artifacts["connector_wave_postmortem"],
            "sample_h8_integration_audit.json": artifacts["integration_audit"],
            "sample_h8_next_phase_recommendation.json": artifacts["next_phase_recommendation"],
        }
        for name, payload in sample_map.items():
            (output_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (output_dir / "sample_h8_summary.md").write_text(str(artifacts["summary_markdown"]), encoding="utf-8")


def render_summary_markdown(summary: Mapping[str, Any]) -> str:
    return "\n".join([
        "# H8 Review Integration Summary",
        "",
        f"- status: `{summary.get('status')}`",
        f"- source_count: `{summary.get('source_count', 0)}`",
        f"- technical_document_identity_review_seed_count: `{summary.get('technical_document_identity_review_seed_count', 0)}`",
        f"- manual_artifact_relation_review_seed_count: `{summary.get('manual_artifact_relation_review_seed_count', 0)}`",
        f"- datasheet_device_identity_review_seed_count: `{summary.get('datasheet_device_identity_review_seed_count', 0)}`",
        f"- standards_specification_identity_review_seed_count: `{summary.get('standards_specification_identity_review_seed_count', 0)}`",
        f"- install_requirement_claim_review_seed_count: `{summary.get('install_requirement_claim_review_seed_count', 0)}`",
        f"- repair_service_safety_review_seed_count: `{summary.get('repair_service_safety_review_seed_count', 0)}`",
        f"- access_rights_review_seed_count: `{summary.get('access_rights_review_seed_count', 0)}`",
        f"- blocked_sources: `{', '.join(summary.get('blocked_sources', []))}`",
        "- document_truth_accepted: `false`",
        "- manual_artifact_relation_truth_accepted: `false`",
        "- datasheet_device_truth_accepted: `false`",
        "- standards_truth_accepted: `false`",
        "- install_requirement_truth_accepted: `false`",
        "- repair_service_safety_truth_accepted: `false`",
        "- access_rights_truth_accepted: `false`",
        "- query_fetch_download_extract: `false`",
        "- restricted_source_access: `false`",
        "- repair_or_install_action_permission: `false`",
        "- public_index_mutated: `false`",
        "- master_index_mutated: `false`",
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
        rel_lower = rel_path.casefold()
        for forbidden in FORBIDDEN_OUTPUT_ROOTS:
            forbidden_lower = forbidden.casefold().rstrip("/")
            if rel_lower == forbidden_lower or rel_lower.startswith(forbidden_lower + "/"):
                raise ValueError(f"refusing forbidden output root: {forbidden}")
        if rel_lower == "examples/connectors/h8_manuals_docs_standards/review_integration" or rel_lower.startswith("examples/connectors/h8_manuals_docs_standards/review_integration/"):
            return resolved
        if rel_lower.startswith("control/audits/") and (rel_lower.endswith("/generated") or "/generated/" in rel_lower):
            return resolved
        raise ValueError(f"refusing output outside approved H8 review roots: {rel_path}")
    except ValueError as exc:
        if str(exc).startswith("refusing"):
            raise
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
            return resolved
        except ValueError as temp_exc:
            raise ValueError(f"refusing output outside repository approved roots or temp directory: {resolved}") from temp_exc


def _first(values: object) -> dict[str, Any]:
    if isinstance(values, list) and values:
        first = values[0]
        if isinstance(first, Mapping):
            return dict(first)
    return {}


def rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())

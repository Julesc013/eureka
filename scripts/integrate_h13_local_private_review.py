#!/usr/bin/env python3
"""Integrate explicit H13 local/private outputs into offline review previews."""

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
    "site/dist", "data/public_index", "runtime", "contracts",
    "control/inventory/publication", "control/inventory/sources",
    "data/master_index", "master_index", "local_sources", "local-source-roots",
    "cas", "cas_roots", "private_sources", "private-source-roots",
    "credentials", "credential_roots", "accounts", "account_roots",
    "user_url_fetch", "user-url-fetch-roots", "import_export_staging",
    "archive_extractions", "source_cache", "evidence_ledger",
    ".aide.local", ".local/eureka", ".cache/eureka",
)

from control.prototypes.legacy_runtime.connectors.h13_local_private.quality_delta import build_h13_quality_delta  # noqa: E402
from control.prototypes.legacy_runtime.connectors.h13_local_private.review_integration import (  # noqa: E402
    build_h13_review_integration_result,
    detect_h13_review_product_boundary_violations,
    detect_h13_review_truth_boundary_violations,
    load_h13_local_private_outputs,
    summarize_h13_review_integration,
)
from control.prototypes.legacy_runtime.connectors.h13_local_private.wave_postmortem import (  # noqa: E402
    build_h13_connector_wave_postmortem,
    build_h13_integration_audit,
    build_h13_next_phase_recommendation,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", default=[], help="Explicit H13 output JSON file. May be repeated.")
    parser.add_argument("--input-dir", action="append", default=[], help="Directory containing H13 output JSON files. May be repeated.")
    parser.add_argument("--output-dir", help="Optional output directory for review previews.")
    parser.add_argument("--check", action="store_true", help="Validate only and write no files.")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    args = parser.parse_args(argv)
    try:
        artifacts = run_integration(args.input, args.input_dir)
        if args.output_dir and not args.check:
            write_outputs(args.output_dir, artifacts)
        summary = summarize_h13_review_integration(artifacts["review_integration_result"])
        summary["wrote_files"] = bool(args.output_dir and not args.check)
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H13 local/private review integration", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"local_source_identity_review_seed_count: {summary['local_source_identity_review_seed_count']}", file=stdout)
            print(f"private_source_boundary_review_seed_count: {summary['private_source_boundary_review_seed_count']}", file=stdout)
            print(f"blocked_sources: {len(summary['blocked_sources'])}", file=stdout)
            print(f"wrote_files: {str(summary['wrote_files']).lower()}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H13 local/private review integration", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def run_integration(inputs: Sequence[str], input_dirs: Sequence[str]) -> dict[str, Any]:
    paths = _collect_input_paths(inputs, input_dirs)
    outputs = load_h13_local_private_outputs(paths)
    result = build_h13_review_integration_result({"outputs": outputs, "input_refs": [rel(path) for path in paths]})
    _merge_h13_bundle_03_blocked_sources(result)
    errors = detect_h13_review_truth_boundary_violations(result) + detect_h13_review_product_boundary_violations(result)
    if errors:
        raise ValueError("; ".join(errors))
    delta = build_h13_quality_delta({"review_integration_result": result})
    postmortem = build_h13_connector_wave_postmortem(result, delta)
    recommendation = build_h13_next_phase_recommendation(postmortem)
    audit = build_h13_integration_audit(result, delta, postmortem, recommendation)
    return {
        "review_integration_result": result,
        "local_source_identity_review_seed": _first(result.get("local_source_identity_review_seeds")),
        "private_source_boundary_review_seed": _first(result.get("private_source_boundary_review_seeds")),
        "user_supplied_url_boundary_review_seed": _first(result.get("user_supplied_url_boundary_review_seeds")),
        "authenticated_source_boundary_review_seed": _first(result.get("authenticated_source_boundary_review_seeds")),
        "restricted_source_manifest_review_seed": _first(result.get("restricted_source_manifest_review_seeds")),
        "local_cas_import_boundary_review_seed": _first(result.get("local_cas_import_boundary_review_seeds")),
        "pack_export_import_boundary_review_seed": _first(result.get("pack_export_import_boundary_review_seeds")),
        "privacy_redaction_review_seed": _first(result.get("privacy_redaction_review_seeds")),
        "local_private_rights_safety_review_seed": _first(result.get("local_private_rights_safety_review_seeds")),
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
        "summary_markdown": render_summary_markdown(summarize_h13_review_integration(result)),
    }


def build_blocked_review_integration(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "h13_blocked_review_integration.v0",
        "wave_id": "H13",
        "review_integration_status": "fixture_review_integrated_with_boundary_dry_run_blocks",
        "blocked_sources": list(result.get("blocked_sources", [])),
        "source_cache_runtime_mutated": False,
        "evidence_ledger_runtime_mutated": False,
        "review_queue_runtime_mutated": False,
        "local_source_identity_truth_accepted": False,
        "private_source_access_permission": False,
        "user_supplied_url_fetch_permission": False,
        "authenticated_access_permission": False,
        "restricted_source_access_permission": False,
        "cas_import_permission": False,
        "pack_export_import_permission": False,
        "privacy_public_safety_truth": False,
        "rights_safety_truth_accepted": False,
        "source_cache_writes": False,
        "evidence_writes": False,
        "public_index_writes": False,
        "private_publication": False,
        "truth_boundary": result.get("truth_boundary", {}),
        "product_boundary": result.get("product_boundary", {}),
        "limitations": ["Blocked boundary dry-runs are recorded as policy evidence only."],
        "notes": ["Blocked review integration is not a review decision."],
    }


def _merge_h13_bundle_03_blocked_sources(result: dict[str, Any]) -> None:
    report_path = REPO_ROOT / "control/audits/h13-bundle-03-local-private-boundary-dry-runs-v0/h13_bundle_03_report.json"
    if not report_path.is_file():
        return
    report = json.loads(report_path.read_text(encoding="utf-8"))
    blocked = report.get("boundary_dry_run_results", {}).get("blocked_sources", [])
    if not isinstance(blocked, list):
        return
    merged = sorted(set(result.get("blocked_sources", [])) | {str(source) for source in blocked if source})
    result["blocked_sources"] = merged
    if merged:
        result["warnings"] = ["H13 boundary dry-runs remain blocked pending operator/user approval."]


def write_outputs(output_dir_text: str, artifacts: Mapping[str, Any]) -> None:
    output_dir = _safe_output_dir(Path(output_dir_text))
    output_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "h13_local_source_identity_review_seed_v0.json": "local_source_identity_review_seed",
        "h13_private_source_boundary_review_seed_v0.json": "private_source_boundary_review_seed",
        "h13_user_supplied_url_boundary_review_seed_v0.json": "user_supplied_url_boundary_review_seed",
        "h13_authenticated_source_boundary_review_seed_v0.json": "authenticated_source_boundary_review_seed",
        "h13_restricted_source_manifest_review_seed_v0.json": "restricted_source_manifest_review_seed",
        "h13_local_cas_import_boundary_review_seed_v0.json": "local_cas_import_boundary_review_seed",
        "h13_pack_export_import_boundary_review_seed_v0.json": "pack_export_import_boundary_review_seed",
        "h13_privacy_redaction_review_seed_v0.json": "privacy_redaction_review_seed",
        "h13_local_private_rights_safety_review_seed_v0.json": "local_private_rights_safety_review_seed",
        "h13_source_cache_review_seed_v0.json": "source_cache_review_seed",
        "h13_evidence_candidate_review_seed_v0.json": "evidence_candidate_review_seed",
        "h13_candidate_promotion_preview_v0.json": "candidate_promotion_preview",
        "h13_source_coverage_update_preview_v0.json": "source_coverage_update_preview",
        "h13_connector_scorecard_update_v0.json": "connector_scorecard_update",
        "h13_source_pack_update_preview_v0.json": "source_pack_update_preview",
        "h13_quality_delta_report_v0.json": "quality_delta_report",
        "h13_connector_wave_postmortem_v0.json": "connector_wave_postmortem",
        "h13_blocked_review_integration_v0.json": "blocked_review_integration",
        "h13_review_integration_result_v0.json": "review_integration_result",
        "h13_next_phase_recommendation_v0.json": "next_phase_recommendation",
        "h13_integration_audit_v0.json": "integration_audit",
    }
    for name, key in files.items():
        (output_dir / name).write_text(json.dumps(artifacts[key], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "h13_summary.md").write_text(str(artifacts["summary_markdown"]), encoding="utf-8")
    if output_dir.name == "generated":
        sample_map = {
            "sample_h13_review_integration_result.json": artifacts["review_integration_result"],
            "sample_h13_quality_delta_report.json": artifacts["quality_delta_report"],
            "sample_h13_connector_wave_postmortem.json": artifacts["connector_wave_postmortem"],
            "sample_h13_integration_audit.json": artifacts["integration_audit"],
            "sample_h13_next_phase_recommendation.json": artifacts["next_phase_recommendation"],
        }
        for name, payload in sample_map.items():
            (output_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (output_dir / "sample_h13_summary.md").write_text(str(artifacts["summary_markdown"]), encoding="utf-8")


def render_summary_markdown(summary: Mapping[str, Any]) -> str:
    return "\n".join([
        "# H13 Review Integration Summary",
        "",
        f"- status: `{summary.get('status')}`",
        f"- source_count: `{summary.get('source_count', 0)}`",
        f"- local_source_identity_review_seed_count: `{summary.get('local_source_identity_review_seed_count', 0)}`",
        f"- private_source_boundary_review_seed_count: `{summary.get('private_source_boundary_review_seed_count', 0)}`",
        f"- blocked_sources: `{', '.join(summary.get('blocked_sources', []))}`",
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
        if rel_lower == "examples/connectors/h13_local_private/review_integration" or rel_lower.startswith("examples/connectors/h13_local_private/review_integration/"):
            return resolved
        if rel_lower.startswith("control/audits/") and (rel_lower.endswith("/generated") or "/generated/" in rel_lower):
            return resolved
        raise ValueError(f"refusing output outside approved H13 review roots: {rel_path}")
    except ValueError as exc:
        if str(exc).startswith("refusing"):
            raise
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
            return resolved
        except ValueError as temp_exc:
            raise ValueError(f"refusing output outside repository approved roots or temp directory: {resolved}") from temp_exc


def _first(values):
    return list(values or [{}])[0]


def rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())

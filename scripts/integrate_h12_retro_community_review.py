#!/usr/bin/env python3
"""Integrate explicit H12 retro/community outputs into offline review previews."""

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
    "data/master_index", "master_index", "roms", "rom_roots",
    "iso", "isos", "iso_roots", "disc_images", "disc-image",
    "bios", "firmware", "vintage_software_downloads",
    "software_downloads", "installer_downloads", "patch_downloads",
    "crack_keys", "crack_key_serials", "serials", "gated_accounts",
    "forum_sessions", "archive_extractions", "extractions",
    "execution_actions", "action_output", "restricted_sources",
    ".aide.local", ".local/eureka", ".cache/eureka",
)

from runtime.connectors.h12_retro_community.quality_delta import build_h12_quality_delta  # noqa: E402
from runtime.connectors.h12_retro_community.review_integration import (  # noqa: E402
    build_h12_review_integration_result,
    detect_h12_review_product_boundary_violations,
    detect_h12_review_truth_boundary_violations,
    load_h12_retro_community_outputs,
    summarize_h12_review_integration,
)
from runtime.connectors.h12_retro_community.wave_postmortem import (  # noqa: E402
    build_h12_connector_wave_postmortem,
    build_h12_integration_audit,
    build_h12_next_phase_recommendation,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", default=[], help="Explicit H12 output JSON file. May be repeated.")
    parser.add_argument("--input-dir", action="append", default=[], help="Directory containing H12 output JSON files. May be repeated.")
    parser.add_argument("--output-dir", help="Optional output directory for review previews.")
    parser.add_argument("--check", action="store_true", help="Validate only and write no files.")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    args = parser.parse_args(argv)
    try:
        artifacts = run_integration(args.input, args.input_dir)
        if args.output_dir and not args.check:
            write_outputs(args.output_dir, artifacts)
        summary = summarize_h12_review_integration(artifacts["review_integration_result"])
        summary["wrote_files"] = bool(args.output_dir and not args.check)
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H12 retro/community review integration", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"retro_software_identity_review_seed_count: {summary['retro_software_identity_review_seed_count']}", file=stdout)
            print(f"platform_version_edition_review_seed_count: {summary['platform_version_edition_review_seed_count']}", file=stdout)
            print(f"archive_item_member_review_seed_count: {summary['archive_item_member_review_seed_count']}", file=stdout)
            print(f"wrote_files: {str(summary['wrote_files']).lower()}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H12 retro/community review integration", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def run_integration(inputs: Sequence[str], input_dirs: Sequence[str]) -> dict[str, Any]:
    paths = _collect_input_paths(inputs, input_dirs)
    outputs = load_h12_retro_community_outputs(paths)
    result = build_h12_review_integration_result({"outputs": outputs, "input_refs": [rel(path) for path in paths]})
    _merge_h12_bundle_03_blocked_sources(result)
    errors = detect_h12_review_truth_boundary_violations(result) + detect_h12_review_product_boundary_violations(result)
    if errors:
        raise ValueError("; ".join(errors))
    delta = build_h12_quality_delta({"review_integration_result": result})
    postmortem = build_h12_connector_wave_postmortem(result, delta)
    recommendation = build_h12_next_phase_recommendation(postmortem)
    audit = build_h12_integration_audit(result, delta, postmortem, recommendation)
    return {
        "review_integration_result": result,
        "retro_software_identity_review_seed": _first(result.get("retro_software_identity_review_seeds")),
        "platform_version_edition_review_seed": _first(result.get("platform_version_edition_review_seeds")),
        "archive_item_member_review_seed": _first(result.get("archive_item_member_review_seeds")),
        "compatibility_install_note_review_seed": _first(result.get("compatibility_install_note_review_seeds")),
        "community_review_comment_review_seed": _first(result.get("community_review_comment_review_seeds")),
        "hash_checksum_review_seed": _first(result.get("hash_checksum_review_seeds")),
        "ia_wayback_corroboration_review_seed": _first(result.get("ia_wayback_corroboration_review_seeds")),
        "gated_source_boundary_review_seed": _first(result.get("gated_source_boundary_review_seeds")),
        "retro_rights_safety_review_seed": _first(result.get("retro_rights_safety_review_seeds")),
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
        "summary_markdown": render_summary_markdown(summarize_h12_review_integration(result)),
    }


def build_blocked_review_integration(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "h12_blocked_review_integration.v0",
        "wave_id": "H12",
        "review_integration_status": "fixture_review_integrated_with_live_probe_blocks",
        "blocked_sources": list(result.get("blocked_sources", [])),
        "source_cache_runtime_mutated": False,
        "evidence_ledger_runtime_mutated": False,
        "review_queue_runtime_mutated": False,
        "retro_software_identity_truth_accepted": False,
        "platform_version_truth_accepted": False,
        "archive_item_member_truth_accepted": False,
        "compatibility_install_truth_accepted": False,
        "community_review_truth_accepted": False,
        "hash_checksum_truth_accepted": False,
        "ia_wayback_corroboration_truth_accepted": False,
        "gated_source_access_truth_accepted": False,
        "rights_safety_truth_accepted": False,
        "query_fetch_download_extract_execute_acquire_upload": False,
        "restricted_source_access": False,
        "acquisition_permission": False,
        "truth_boundary": result.get("truth_boundary", {}),
        "product_boundary": result.get("product_boundary", {}),
        "limitations": ["Blocked live probes are recorded as policy evidence only."],
        "notes": ["Blocked review integration is not a review decision."],
    }


def _merge_h12_bundle_03_blocked_sources(result: dict[str, Any]) -> None:
    report_path = REPO_ROOT / "control/audits/h12-bundle-03-retro-community-live-probes-v0/h12_bundle_03_report.json"
    if not report_path.is_file():
        return
    report = json.loads(report_path.read_text(encoding="utf-8"))
    blocked = report.get("live_probe_results", {}).get("blocked_sources", [])
    if not isinstance(blocked, list):
        return
    merged = sorted(set(result.get("blocked_sources", [])) | {str(source) for source in blocked if source})
    result["blocked_sources"] = merged
    if merged:
        result["warnings"] = ["H12 live probes remain blocked pending operator approval."]


def write_outputs(output_dir_text: str, artifacts: Mapping[str, Any]) -> None:
    output_dir = _safe_output_dir(Path(output_dir_text))
    output_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "h12_archive_item_member_review_seed_v0.json": "archive_item_member_review_seed",
        "h12_blocked_review_integration_v0.json": "blocked_review_integration",
        "h12_candidate_promotion_preview_v0.json": "candidate_promotion_preview",
        "h12_community_review_comment_review_seed_v0.json": "community_review_comment_review_seed",
        "h12_compatibility_install_note_review_seed_v0.json": "compatibility_install_note_review_seed",
        "h12_connector_scorecard_update_v0.json": "connector_scorecard_update",
        "h12_connector_wave_postmortem_v0.json": "connector_wave_postmortem",
        "h12_evidence_candidate_review_seed_v0.json": "evidence_candidate_review_seed",
        "h12_gated_source_boundary_review_seed_v0.json": "gated_source_boundary_review_seed",
        "h12_hash_checksum_review_seed_v0.json": "hash_checksum_review_seed",
        "h12_ia_wayback_corroboration_review_seed_v0.json": "ia_wayback_corroboration_review_seed",
        "h12_integration_audit_v0.json": "integration_audit",
        "h12_next_phase_recommendation_v0.json": "next_phase_recommendation",
        "h12_platform_version_edition_review_seed_v0.json": "platform_version_edition_review_seed",
        "h12_quality_delta_report_v0.json": "quality_delta_report",
        "h12_retro_rights_safety_review_seed_v0.json": "retro_rights_safety_review_seed",
        "h12_retro_software_identity_review_seed_v0.json": "retro_software_identity_review_seed",
        "h12_review_integration_result_v0.json": "review_integration_result",
        "h12_source_cache_review_seed_v0.json": "source_cache_review_seed",
        "h12_source_coverage_update_preview_v0.json": "source_coverage_update_preview",
        "h12_source_pack_update_preview_v0.json": "source_pack_update_preview"
}
    for name, key in files.items():
        payload = artifacts[key]
        (output_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "h12_summary.md").write_text(str(artifacts["summary_markdown"]), encoding="utf-8")
    if output_dir.name == "generated":
        sample_map = {
            "sample_h12_review_integration_result.json": artifacts["review_integration_result"],
            "sample_h12_quality_delta_report.json": artifacts["quality_delta_report"],
            "sample_h12_connector_wave_postmortem.json": artifacts["connector_wave_postmortem"],
            "sample_h12_integration_audit.json": artifacts["integration_audit"],
            "sample_h12_next_phase_recommendation.json": artifacts["next_phase_recommendation"],
        }
        for name, payload in sample_map.items():
            (output_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (output_dir / "sample_h12_summary.md").write_text(str(artifacts["summary_markdown"]), encoding="utf-8")


def render_summary_markdown(summary: Mapping[str, Any]) -> str:
    return "\n".join([
        "# H12 Review Integration Summary",
        "",
        f"- status: `{summary.get('status')}`",
        f"- source_count: `{summary.get('source_count', 0)}`",
        f"- retro_software_identity_review_seed_count: `{summary.get('retro_software_identity_review_seed_count', 0)}`",
        f"- platform_version_edition_review_seed_count: `{summary.get('platform_version_edition_review_seed_count', 0)}`",
        f"- archive_item_member_review_seed_count: `{summary.get('archive_item_member_review_seed_count', 0)}`",
        f"- blocked_sources: `{', '.join(summary.get('blocked_sources', []))}`",
        "- retro_software_identity_truth_accepted: `false`",
        "- platform_version_truth_accepted: `false`",
        "- archive_item_member_truth_accepted: `false`",
        "- compatibility_install_truth_accepted: `false`",
        "- community_review_truth_accepted: `false`",
        "- hash_checksum_truth_accepted: `false`",
        "- ia_wayback_corroboration_truth_accepted: `false`",
        "- gated_source_access_truth_accepted: `false`",
        "- rights_safety_truth_accepted: `false`",
        "- query_fetch_download_extract_execute_acquire_upload: `false`",
        "- restricted_source_access: `false`",
        "- acquisition_permission: `false`",
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
        rel_lower = rel_path.casefold().rstrip("/")
        for forbidden in FORBIDDEN_OUTPUT_ROOTS:
            forbidden_lower = forbidden.casefold().rstrip("/")
            if rel_lower == forbidden_lower or rel_lower.startswith(forbidden_lower + "/"):
                raise ValueError(f"refusing forbidden output root: {forbidden}")
        if rel_lower == "examples/connectors/h12_retro_community/review_integration" or rel_lower.startswith("examples/connectors/h12_retro_community/review_integration/"):
            return resolved
        if rel_lower.startswith("control/audits/") and (rel_lower.endswith("/generated") or "/generated/" in rel_lower):
            return resolved
        raise ValueError(f"refusing output outside approved H12 review roots: {rel_path}")
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

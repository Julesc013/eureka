#!/usr/bin/env python3
"""Run offline H14 Source OS rollup dry-runs with fail-closed gates."""

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

from runtime.connectors.h14_source_discovery.rollup_dry_run_common import (  # noqa: E402
    H14_SOURCE_IDS,
    ROLLUP_REQUEST_KEYS,
    build_h14_rollup_blocked_result,
    build_h14_rollup_dry_run_output_bundle,
    build_h14_rollup_dry_run_result,
    build_h14_source_discovery_rollup_dry_run_request,
    load_h14_rollup_inputs,
    load_h14_rollup_policy_bundle,
    summarize_h14_rollup_dry_run_result,
    validate_h14_rollup_dry_run_request,
)

ALLOWED_PREFIXES = (
    "examples/connectors/h14_source_discovery/rollup_dry_run_results",
    "examples/connectors/h14_source_discovery/rollup_dry_run_outputs",
    "control/audits/h14-bundle-03-source-discovery-rollup-dry-runs-v0/generated",
)
REQUEST_INPUT_PREFIXES = (
    "examples/connectors/h14_source_discovery/rollup_dry_run",
    "control/audits/h14-bundle-03-source-discovery-rollup-dry-runs-v0/generated",
)
FORBIDDEN_PREFIXES = (
    "site/dist", "data/public_index", "runtime", "contracts", "control/inventory/sources",
    "control/inventory/connectors", "source_registry_mutation", "connector_registry_mutation",
    "pack_import_staging", "pack_export_staging", "pack_imports", "pack_exports", "source_cache",
    "evidence_ledger", "review_queue", "master_index", "public_index", ".aide.local", ".local/eureka",
    ".cache/eureka", "local_sources", "private_sources", "source_discovery_runtime", "external_source_fetch",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-id", choices=sorted(H14_SOURCE_IDS))
    parser.add_argument("--request-key")
    parser.add_argument("--input")
    parser.add_argument("--artifact-root")
    parser.add_argument("--output")
    parser.add_argument("--source-need-output")
    parser.add_argument("--source-candidate-output")
    parser.add_argument("--discovery-output")
    parser.add_argument("--source-pack-output")
    parser.add_argument("--connector-pack-output")
    parser.add_argument("--coverage-output")
    parser.add_argument("--scorecard-output")
    parser.add_argument("--reliability-output")
    parser.add_argument("--dispute-output")
    parser.add_argument("--lineage-output")
    parser.add_argument("--pack-boundary-output")
    parser.add_argument("--source-cache-output")
    parser.add_argument("--evidence-preview-output")
    parser.add_argument("--review-seed-output")
    parser.add_argument("--health-output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        bundle = load_h14_rollup_policy_bundle(REPO_ROOT)
        request = _load_request(args, bundle)
        result = run_rollup(request, bundle, args.artifact_root)
        if not args.check:
            outputs = {
                args.output: result,
                args.source_need_output: _first(result["source_need_candidates"]),
                args.source_candidate_output: _first(result["source_candidate_candidates"]),
                args.discovery_output: _first(result["source_discovery_candidates"]),
                args.source_pack_output: _first(result["source_pack_manifest_candidates"]),
                args.connector_pack_output: _first(result["connector_pack_manifest_candidates"]),
                args.coverage_output: _first(result["coverage_manifest_candidates"]),
                args.scorecard_output: _first(result["connector_scorecard_candidates"]),
                args.reliability_output: _first(result["source_reliability_freshness_candidates"]),
                args.dispute_output: _first(result["source_dispute_revocation_candidates"]),
                args.lineage_output: _first(result["source_lineage_provenance_candidates"]),
                args.pack_boundary_output: _first(result["pack_import_export_boundary_candidates"]),
                args.source_cache_output: result["source_cache_candidate_preview"],
                args.evidence_preview_output: result["evidence_candidate_preview"],
                args.review_seed_output: result["review_queue_seed_preview"],
                args.health_output: result["source_os_rollup_health_summary"],
            }
            for path, payload in outputs.items():
                if path:
                    _write_json(path, payload)
            if args.summary_output:
                _write_text(args.summary_output, render_summary(result))
        summary = {
            "status": "valid",
            "mode": "check" if args.check else "dry_run",
            "wrote_files": (not args.check) and any([
                args.output, args.source_need_output, args.source_candidate_output, args.discovery_output,
                args.source_pack_output, args.connector_pack_output, args.coverage_output, args.scorecard_output,
                args.reliability_output, args.dispute_output, args.lineage_output, args.pack_boundary_output,
                args.source_cache_output, args.evidence_preview_output, args.review_seed_output, args.health_output,
                args.summary_output,
            ]),
            "rollup_dry_run": summarize_h14_rollup_dry_run_result(result),
        }
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            dry = summary["rollup_dry_run"]
            print("H14 Source OS rollup dry-run", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"mode: {summary['mode']}", file=stdout)
            print(f"source_id: {dry['source_id']}", file=stdout)
            print(f"result: {dry['result_status']}", file=stdout)
            print(f"operation_count: {dry['operation_count']}", file=stdout)
            print(f"network_used: {str(dry['network_used']).lower()}", file=stdout)
            print(f"model_provider_used: {str(dry['model_provider_used']).lower()}", file=stdout)
            print(f"registry_mutation_performed: {str(dry['registry_mutation_performed']).lower()}", file=stdout)
            print(f"pack_export_import_performed: {str(dry['pack_export_import_performed']).lower()}", file=stdout)
            if dry["blocked_reasons"]:
                print("blocked_reasons:", file=stdout)
                for reason in dry["blocked_reasons"]:
                    print(f"- {reason}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H14 Source OS rollup dry-run", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def run_rollup(request: Mapping[str, Any], bundle: Mapping[str, Any], artifact_root: str | None = None) -> dict[str, Any]:
    validation = validate_h14_rollup_dry_run_request(request, bundle)
    if not validation["approved"]:
        return build_h14_rollup_blocked_result(request, validation["blocked_reasons"], bundle)
    refs = list(request.get("h0_h13_artifact_refs") or [])
    if artifact_root:
        refs.append(str(_safe_artifact_root(artifact_root).relative_to(REPO_ROOT).as_posix()))
    inputs = load_h14_rollup_inputs(refs, bundle)
    return build_h14_rollup_dry_run_result(str(request["source_id"]), inputs, bundle)


def render_summary(result: Mapping[str, Any]) -> str:
    summary = summarize_h14_rollup_dry_run_result(result)
    lines = [
        "# H14 Source OS Rollup Dry-Run Summary",
        "",
        f"- source_id: `{summary['source_id']}`",
        f"- result: `{summary['result_status']}`",
        f"- operation_count: `{summary['operation_count']}`",
        f"- network_used: `{str(summary['network_used']).lower()}`",
        f"- model_provider_used: `{str(summary['model_provider_used']).lower()}`",
        f"- registry_mutation_performed: `{str(summary['registry_mutation_performed']).lower()}`",
        f"- pack_export_import_performed: `{str(summary['pack_export_import_performed']).lower()}`",
        "- rollup_dry_run_only: `true`",
        "- committed_artifacts_only: `true`",
        "- public_index_writes: `false`",
    ]
    if summary["blocked_reasons"]:
        lines.extend(["", "## Blocked Reasons"])
        lines.extend(f"- {reason}" for reason in summary["blocked_reasons"])
    return "\n".join(lines) + "\n"


def _load_request(args: argparse.Namespace, bundle: Mapping[str, Any]) -> dict[str, Any]:
    if args.input:
        payload = json.loads(_safe_input_path(args.input).read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("request input must be a JSON object")
        return payload
    if not args.source_id:
        raise ValueError("--source-id is required when --input is not provided")
    request_key = args.request_key or ROLLUP_REQUEST_KEYS[args.source_id]
    return build_h14_source_discovery_rollup_dry_run_request(args.source_id, request_key, bundle)


def _safe_input_path(raw: str | Path) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = REPO_ROOT / path
    resolved = path.resolve()
    repo = REPO_ROOT.resolve()
    try:
        rel = resolved.relative_to(repo).as_posix().lower()
    except ValueError:
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
        except ValueError as exc:
            raise ValueError("request input path must be under H14 rollup request examples/audit roots or an explicit temp directory") from exc
        return resolved
    if any(rel == prefix or rel.startswith(prefix + "/") for prefix in REQUEST_INPUT_PREFIXES):
        return resolved
    raise ValueError("repo request input path must be under H14 rollup request examples or audit generated roots")


def _safe_artifact_root(raw: str | Path) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = REPO_ROOT / path
    resolved = path.resolve()
    rel = resolved.relative_to(REPO_ROOT.resolve()).as_posix().lower()
    allowed = ("control/audits", "control/inventory/source_packs", "control/inventory/connectors", "examples/connectors/h14_source_discovery", "examples/source_packs", "examples/sources")
    if any(rel == prefix or rel.startswith(prefix + "/") for prefix in allowed):
        return resolved
    raise ValueError("artifact root must be an allowlisted committed H0-H14 artifact root")


def safe_output_path(output: str | Path) -> Path:
    path = Path(output)
    if not path.is_absolute():
        path = REPO_ROOT / path
    resolved = path.resolve()
    repo = REPO_ROOT.resolve()
    try:
        rel = resolved.relative_to(repo).as_posix()
    except ValueError:
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
        except ValueError as exc:
            raise ValueError("output path must be under H14 rollup examples/audit roots or an explicit temp directory") from exc
        return resolved
    rel_lower = rel.lower()
    for forbidden in FORBIDDEN_PREFIXES:
        if rel_lower == forbidden or rel_lower.startswith(forbidden.rstrip("/") + "/"):
            raise ValueError(f"refusing forbidden output root: {forbidden}")
    if any(rel_lower == prefix or rel_lower.startswith(prefix.rstrip("/") + "/") for prefix in ALLOWED_PREFIXES):
        return resolved
    raise ValueError("repo output path must be under H14 rollup examples or audit generated roots")


def _write_json(path: str | Path, payload: Any) -> None:
    out = safe_output_path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: str | Path, text: str) -> None:
    out = safe_output_path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")


def _first(items: list[Any]) -> Any:
    return items[0] if items else None


if __name__ == "__main__":
    raise SystemExit(main())

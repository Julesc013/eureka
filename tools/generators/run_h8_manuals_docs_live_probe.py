#!/usr/bin/env python3
"""Run or preflight H8 manuals/docs/standards metadata live probes with fail-closed policy gates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
from collections.abc import Mapping, Sequence
from typing import Any, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from archive.prototypes.legacy_runtime.connectors.h8_manuals_docs_standards.live_probe_common import (  # noqa: E402
    SOURCE_CONFIGS,
    build_h8_manuals_docs_live_probe_blocked_result,
    build_h8_manuals_docs_live_probe_output_bundle,
    build_h8_manuals_docs_live_probe_request,
    load_h8_manuals_docs_live_probe_policy_bundle,
    summarize_h8_manuals_docs_live_probe_result,
    validate_h8_manuals_docs_live_probe_request,
)

FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist",
    "site/dist/data/public_index",
    "runtime",
    "contracts",
    "control/inventory/publication",
    "control/inventory/sources",
    "data/master_index",
    "master_index",
    "document_downloads",
    "standards_downloads",
    "manual_downloads",
    "datasheet_downloads",
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


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-id", choices=sorted(SOURCE_CONFIGS))
    parser.add_argument("--request-key")
    parser.add_argument("--input")
    parser.add_argument("--output")
    parser.add_argument("--document-output")
    parser.add_argument("--relation-output")
    parser.add_argument("--datasheet-output")
    parser.add_argument("--standard-output")
    parser.add_argument("--install-output")
    parser.add_argument("--repair-output")
    parser.add_argument("--access-output")
    parser.add_argument("--source-cache-output")
    parser.add_argument("--evidence-preview-output")
    parser.add_argument("--review-seed-output")
    parser.add_argument("--health-output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        bundle = load_h8_manuals_docs_live_probe_policy_bundle(REPO_ROOT)
        request = _load_request(args, bundle)
        artifacts = run_probe(request, bundle, live=args.live and not args.check)
        result = artifacts["live_probe_result"]
        if not args.check:
            outputs = {
                args.output: result,
                args.document_output: result["technical_document_identity_candidate"],
                args.relation_output: result["manual_artifact_relation_candidate"],
                args.datasheet_output: result["datasheet_device_identity_candidate"],
                args.standard_output: result["standards_specification_identity_candidate"],
                args.install_output: result["install_requirement_claim_candidate"],
                args.repair_output: result["repair_service_safety_candidate"],
                args.access_output: result["access_rights_candidate"],
                args.source_cache_output: result["source_cache_candidate_preview"],
                args.evidence_preview_output: result["evidence_candidate_preview"],
                args.review_seed_output: result["review_queue_seed_preview"],
                args.health_output: result["connector_health_summary"],
            }
            for path, payload in outputs.items():
                if path:
                    _write_json(path, payload)
            if args.summary_output:
                _write_text(args.summary_output, render_summary(result))
        summary = {
            "status": "valid",
            "mode": "live" if args.live and not args.check else "check",
            "wrote_files": (not args.check) and any([
                args.output,
                args.document_output,
                args.relation_output,
                args.datasheet_output,
                args.standard_output,
                args.install_output,
                args.repair_output,
                args.access_output,
                args.source_cache_output,
                args.evidence_preview_output,
                args.review_seed_output,
                args.health_output,
                args.summary_output,
            ]),
            "live_probe": summarize_h8_manuals_docs_live_probe_result(result),
        }
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            live = summary["live_probe"]
            print("H8 manuals/docs/standards metadata live probe", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"mode: {summary['mode']}", file=stdout)
            print(f"source_id: {live['source_id']}", file=stdout)
            print(f"result: {live['result_status']}", file=stdout)
            print(f"request_count: {live['request_count']}", file=stdout)
            print(f"network_used: {str(live['network_used']).lower()}", file=stdout)
            if live["blocked_reasons"]:
                print("blocked_reasons:", file=stdout)
                for reason in live["blocked_reasons"]:
                    print(f"- {reason}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H8 manuals/docs/standards metadata live probe", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def run_probe(request: Mapping[str, Any], policy_bundle: Mapping[str, Any], live: bool) -> dict[str, Any]:
    validation = validate_h8_manuals_docs_live_probe_request(request, policy_bundle)
    if not validation["approved"]:
        result = build_h8_manuals_docs_live_probe_blocked_result(request, validation["blocked_reasons"], policy_bundle)
        return {"live_probe_result": result, "output_bundle": build_h8_manuals_docs_live_probe_output_bundle(result)}
    if not live:
        result = build_h8_manuals_docs_live_probe_blocked_result(request, ["dry preflight only; --live not provided"], policy_bundle)
        result["result_status"] = "dry_run_preflight_pass"
        result["blocked_reason"] = None
        result["blocked_reasons"] = []
        result["connector_health_summary"]["live_probe_status"] = "dry_run_preflight_pass"
        result["connector_health_summary"]["response_status_summary"] = "preflight_pass"
        result["connector_health_summary"]["policy_blockers"] = []
        result["limitations"] = ["Committed policy approves this request, but no network call was requested."]
        return {"live_probe_result": result, "output_bundle": build_h8_manuals_docs_live_probe_output_bundle(result)}
    result = build_h8_manuals_docs_live_probe_blocked_result(
        request,
        ["live network execution remains fail-closed in H8-BUNDLE-03; source-specific executor requires future reviewed approval"],
        policy_bundle,
    )
    result["result_status"] = "live_probe_failed"
    result["connector_health_summary"]["live_probe_status"] = "live_probe_failed"
    return {"live_probe_result": result, "output_bundle": build_h8_manuals_docs_live_probe_output_bundle(result)}


def render_summary(result: Mapping[str, Any]) -> str:
    summary = summarize_h8_manuals_docs_live_probe_result(result)
    lines = [
        "# H8 Manuals Docs Live Probe Summary",
        "",
        f"- source_id: `{summary['source_id']}`",
        f"- result: `{summary['result_status']}`",
        f"- request_count: `{summary['request_count']}`",
        f"- network_used: `{str(summary['network_used']).lower()}`",
        "- api_catalog_query: `false unless approved bounded metadata-only`",
        "- downloads: `false`",
        "- full_text_ocr: `false`",
        "- scraping_crawling: `false`",
        "- restricted_source_access: `false`",
        "- public_index_mutated: `false`",
        "- master_index_mutated: `false`",
    ]
    if summary["blocked_reasons"]:
        lines.extend(["", "## Blocked Reasons"])
        lines.extend(f"- {reason}" for reason in summary["blocked_reasons"])
    return "\n".join(lines) + "\n"


def _load_request(args: argparse.Namespace, bundle: Mapping[str, Any]) -> dict[str, Any]:
    if args.input:
        payload = json.loads(_repo_path(args.input).read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("request input must be a JSON object")
        return payload
    if not args.source_id or not args.request_key:
        raise ValueError("--source-id and --request-key are required when --input is not provided")
    return build_h8_manuals_docs_live_probe_request(args.source_id, args.request_key, bundle, live_requested=args.live and not args.check)


def _repo_path(path_text: str | Path) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else REPO_ROOT / path


def _write_json(path_text: str, payload: object) -> None:
    path = _safe_output_path(Path(path_text))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path_text: str, text: str) -> None:
    path = _safe_output_path(Path(path_text))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _safe_output_path(path: Path) -> Path:
    resolved = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    try:
        rel = resolved.relative_to(REPO_ROOT.resolve()).as_posix()
        rel_lower = rel.casefold()
        for forbidden in FORBIDDEN_OUTPUT_ROOTS:
            forbidden_lower = forbidden.casefold().rstrip("/")
            if rel_lower == forbidden_lower or rel_lower.startswith(forbidden_lower + "/"):
                raise ValueError(f"refusing forbidden output root: {forbidden}")
        if rel_lower.startswith("control/audits/") and "/generated/" in rel_lower:
            return resolved
        if rel_lower.startswith("examples/connectors/h8_manuals_docs_standards/live_probe_results/"):
            return resolved
        if rel_lower.startswith("examples/connectors/h8_manuals_docs_standards/live_probe_outputs/"):
            return resolved
        raise ValueError(f"refusing output outside approved H8 live-probe roots: {rel}")
    except ValueError as exc:
        if str(exc).startswith("refusing"):
            raise
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
            return resolved
        except ValueError as temp_exc:
            raise ValueError(f"refusing output outside approved roots or temp directory: {resolved}") from temp_exc


if __name__ == "__main__":
    raise SystemExit(main())

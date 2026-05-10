#!/usr/bin/env python3
"""Run or preflight H6 web archive/news/event metadata live probes with fail-closed policy gates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
from collections.abc import Mapping, Sequence
from typing import Any, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.connectors.h6_web_archive_news_event.live_probe_common import (  # noqa: E402
    H6WebArchiveLiveProbeBlocked,
    SOURCE_CONFIGS,
    build_h6_web_archive_live_probe_blocked_result,
    build_h6_web_archive_live_probe_output_bundle,
    build_h6_web_archive_live_probe_request,
    build_h6_web_archive_live_probe_result,
    fetch_h6_web_archive_metadata_once,
    load_h6_web_archive_live_probe_policy_bundle,
    summarize_h6_web_archive_live_probe_result,
    validate_h6_web_archive_live_probe_request,
)

FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist",
    "data/public_index",
    "runtime",
    "contracts",
    "control/inventory/publication",
    "control/inventory/sources",
    "data/master_index",
    "master_index",
    "crawl",
    "crawls",
    "warc_cache",
    "wacz_cache",
    "media_downloads",
    "transcript_dump",
    "document_dump",
    "sensitive_sources",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-id", choices=sorted(SOURCE_CONFIGS))
    parser.add_argument("--request-key")
    parser.add_argument("--input", help="Optional explicit H6 web archive live-probe request envelope.")
    parser.add_argument("--output")
    parser.add_argument("--capture-output")
    parser.add_argument("--time-state-output")
    parser.add_argument("--event-output")
    parser.add_argument("--dead-link-output")
    parser.add_argument("--public-document-output")
    parser.add_argument("--media-transcript-output")
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
        bundle = load_h6_web_archive_live_probe_policy_bundle(REPO_ROOT)
        request = _load_request(args, bundle)
        artifacts = run_probe(request, bundle, live=args.live and not args.check)
        result = artifacts["live_probe_result"]
        if not args.check:
            if args.output:
                _write_json(args.output, result)
            if args.capture_output:
                _write_json(args.capture_output, result["web_capture_identity_candidate"])
            if args.time_state_output:
                _write_json(args.time_state_output, result["archived_url_time_state_candidate"])
            if args.event_output:
                _write_json(args.event_output, result["news_event_mention_candidate"])
            if args.dead_link_output:
                _write_json(args.dead_link_output, result["dead_link_trace_candidate"])
            if args.public_document_output:
                _write_json(args.public_document_output, result["public_document_trace_candidate"])
            if args.media_transcript_output:
                _write_json(args.media_transcript_output, result["media_transcript_metadata_candidate"])
            if args.source_cache_output:
                _write_json(args.source_cache_output, result["source_cache_candidate_preview"])
            if args.evidence_preview_output:
                _write_json(args.evidence_preview_output, result["evidence_candidate_preview"])
            if args.review_seed_output:
                _write_json(args.review_seed_output, result["review_queue_seed_preview"])
            if args.health_output:
                _write_json(args.health_output, result["connector_health_summary"])
            if args.summary_output:
                _write_text(args.summary_output, render_summary(result))
        summary = {
            "status": "valid",
            "mode": "live" if args.live and not args.check else "check",
            "wrote_files": (not args.check) and any([
                args.output,
                args.capture_output,
                args.time_state_output,
                args.event_output,
                args.dead_link_output,
                args.public_document_output,
                args.media_transcript_output,
                args.source_cache_output,
                args.evidence_preview_output,
                args.review_seed_output,
                args.health_output,
                args.summary_output,
            ]),
            "live_probe": summarize_h6_web_archive_live_probe_result(result),
        }
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            live = summary["live_probe"]
            print("H6 web archive/news/event metadata live probe", file=stdout)
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
            print("H6 web archive/news/event metadata live probe", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def run_probe(request: Mapping[str, Any], policy_bundle: Mapping[str, Any], live: bool) -> dict[str, Any]:
    validation = validate_h6_web_archive_live_probe_request(request, policy_bundle)
    if not validation["approved"]:
        result = build_h6_web_archive_live_probe_blocked_result(request, validation["blocked_reasons"], policy_bundle)
        return {"live_probe_result": result, "output_bundle": build_h6_web_archive_live_probe_output_bundle(result)}
    if not live:
        result = build_h6_web_archive_live_probe_blocked_result(request, ["dry preflight only; --live not provided"], policy_bundle)
        result["result_status"] = "dry_run_preflight_pass"
        result["blocked_reason"] = None
        result["blocked_reasons"] = []
        result["connector_health_summary"]["live_probe_status"] = "dry_run_preflight_pass"
        result["connector_health_summary"]["response_status_summary"] = "preflight_pass"
        result["connector_health_summary"]["policy_blockers"] = []
        result["limitations"] = ["Committed policy approves this request, but no network call was requested."]
        return {"live_probe_result": result, "output_bundle": build_h6_web_archive_live_probe_output_bundle(result)}
    try:
        payload, metadata = fetch_h6_web_archive_metadata_once(request, policy_bundle)
    except H6WebArchiveLiveProbeBlocked as exc:
        result = exc.result
        return {"live_probe_result": result, "output_bundle": build_h6_web_archive_live_probe_output_bundle(result)}
    metadata["live_probe_request_ref"] = request.get("live_probe_request_id")
    result = build_h6_web_archive_live_probe_result(str(request["source_id"]), payload, metadata, policy_bundle)
    return {"live_probe_result": result, "output_bundle": build_h6_web_archive_live_probe_output_bundle(result)}


def render_summary(result: Mapping[str, Any]) -> str:
    summary = summarize_h6_web_archive_live_probe_result(result)
    lines = [
        "# H6 Web Archive Live Probe Summary",
        "",
        f"- source_id: `{summary['source_id']}`",
        f"- result: `{summary['result_status']}`",
        f"- request_count: `{summary['request_count']}`",
        f"- network_used: `{str(summary['network_used']).lower()}`",
        "- warc_wacz_fetch: `false`",
        "- archived_page_fetch: `false`",
        "- scraping_crawling: `false`",
        "- restricted_source_access: `false`",
        f"- web_capture_candidate_present: `{str(summary['web_capture_candidate_present']).lower()}`",
        f"- time_state_candidate_present: `{str(summary['time_state_candidate_present']).lower()}`",
        f"- news_event_candidate_present: `{str(summary['news_event_candidate_present']).lower()}`",
        f"- dead_link_candidate_present: `{str(summary['dead_link_candidate_present']).lower()}`",
        f"- public_document_candidate_present: `{str(summary['public_document_candidate_present']).lower()}`",
        f"- media_candidate_present: `{str(summary['media_candidate_present']).lower()}`",
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
    return build_h6_web_archive_live_probe_request(args.source_id, args.request_key, bundle, live_requested=args.live and not args.check)


def _repo_path(path_text: str | Path) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else REPO_ROOT / path


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
    try:
        rel = resolved.relative_to(REPO_ROOT.resolve()).as_posix()
        rel_lower = rel.casefold()
        for forbidden in FORBIDDEN_OUTPUT_ROOTS:
            forbidden_lower = forbidden.casefold().rstrip("/")
            if rel_lower == forbidden_lower or rel_lower.startswith(forbidden_lower + "/"):
                raise ValueError(f"refusing forbidden output root: {forbidden}")
        if rel_lower.startswith("control/audits/") and "/generated/" in rel_lower:
            return resolved
        if rel_lower.startswith("examples/connectors/h6_web_archive_news_event/live_probe_results/"):
            return resolved
        if rel_lower.startswith("examples/connectors/h6_web_archive_news_event/live_probe_outputs/"):
            return resolved
        raise ValueError(f"refusing output outside approved H6 live-probe roots: {rel}")
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

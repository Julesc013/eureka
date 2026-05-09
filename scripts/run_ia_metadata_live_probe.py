#!/usr/bin/env python3
"""Run or preflight the IA metadata live probe with fail-closed policy gates."""

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

from runtime.connectors.internet_archive.live_metadata_probe import (  # noqa: E402
    LiveProbeBlocked,
    build_blocked_live_probe_result,
    build_live_probe_result,
    build_not_created_preview,
    build_review_queue_seed_preview,
    fetch_ia_metadata_once,
    load_policy_bundle,
    map_live_probe_to_source_cache_candidate,
    normalize_live_probe_result,
    preview_live_probe_evidence_candidates,
    summarize_live_probe_result,
    validate_identifier_allowed,
    validate_live_probe_policy,
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
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--identifier", required=True, help="Exact approved IA identifier.")
    parser.add_argument("--output", help="Optional live probe result output path.")
    parser.add_argument("--source-cache-output", help="Optional source-cache candidate preview output path.")
    parser.add_argument("--evidence-preview-output", help="Optional evidence candidate preview output path.")
    parser.add_argument("--review-seed-output", help="Optional review queue seed preview output path.")
    parser.add_argument("--summary-output", help="Optional Markdown summary output path.")
    parser.add_argument("--check", action="store_true", help="Dry preflight only; no network call.")
    parser.add_argument("--live", action="store_true", help="Attempt the one metadata call if policy approves it.")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    args = parser.parse_args(argv)

    try:
        bundle = load_policy_bundle(REPO_ROOT)
        artifacts = run_probe(args.identifier, bundle, live=args.live and not args.check)
        if args.output:
            _write_json(args.output, artifacts["live_probe_result"])
        if args.source_cache_output:
            _write_json(args.source_cache_output, artifacts["source_cache_candidate"])
        if args.evidence_preview_output:
            _write_json(args.evidence_preview_output, artifacts["evidence_preview"])
        if args.review_seed_output:
            _write_json(args.review_seed_output, artifacts["review_seed"])
        if args.summary_output:
            _write_text(args.summary_output, render_summary(artifacts["live_probe_result"]))
        summary = {
            "status": "valid",
            "mode": "live" if args.live and not args.check else "check",
            "wrote_files": any([args.output, args.source_cache_output, args.evidence_preview_output, args.review_seed_output, args.summary_output]),
            "live_probe": summarize_live_probe_result(artifacts["live_probe_result"]),
        }
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            live = summary["live_probe"]
            print("IA metadata live probe", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"mode: {summary['mode']}", file=stdout)
            print(f"identifier: {live['identifier']}", file=stdout)
            print(f"result: {live['result_status']}", file=stdout)
            print(f"attempted: {str(live['attempted']).lower()}", file=stdout)
            print(f"request_count: {live['request_count']}", file=stdout)
            if live["blocked_reasons"]:
                print("blocked_reasons:", file=stdout)
                for reason in live["blocked_reasons"]:
                    print(f"- {reason}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001 - CLI validation surface.
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("IA metadata live probe", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def run_probe(identifier: str, policy_bundle: Mapping[str, Any], live: bool) -> dict[str, Any]:
    policy_result = validate_live_probe_policy(policy_bundle)
    identifier_result = validate_identifier_allowed(identifier, policy_bundle.get("allowed_identifier_policy", {}))
    blocked_reasons = policy_result["blocked_reasons"] + identifier_result["blocked_reasons"]
    if blocked_reasons:
        result = build_blocked_live_probe_result(identifier, policy_bundle, blocked_reasons)
        return _blocked_artifacts(result)
    if not live:
        result = dict(build_blocked_live_probe_result(identifier, policy_bundle, ["dry preflight only; --live not provided"]))
        result["result_status"] = "ready"
        result["blocked_by_policy"] = False
        result["blocked_reasons"] = []
        result["notes"] = ["Committed policy approves this identifier, but no network call was requested."]
        return _blocked_artifacts(result)

    try:
        payload, response_metadata = fetch_ia_metadata_once(identifier, policy_bundle)
    except LiveProbeBlocked as exc:
        return _blocked_artifacts(exc.result)
    result = build_live_probe_result(identifier, payload, response_metadata, policy_bundle)
    normalized = normalize_live_probe_result(result, policy_bundle.get("normalization_policy", {}))
    source_cache = map_live_probe_to_source_cache_candidate(normalized, policy_bundle.get("source_cache_mapping_policy", {}))
    evidence = preview_live_probe_evidence_candidates(normalized, policy_bundle.get("evidence_mapping_policy", {}))
    review_seed = build_review_queue_seed_preview(result, source_cache, evidence, policy_bundle.get("review_policy", {}))
    return {
        "live_probe_result": result,
        "normalized": normalized,
        "source_cache_candidate": source_cache,
        "evidence_preview": evidence,
        "review_seed": review_seed,
    }


def render_summary(result: Mapping[str, Any]) -> str:
    summary = summarize_live_probe_result(result)
    lines = [
        "# IA Metadata Live Probe Summary",
        "",
        f"- identifier: `{summary['identifier']}`",
        f"- result: `{summary['result_status']}`",
        f"- attempted: `{str(summary['attempted']).lower()}`",
        f"- request_count: `{summary['request_count']}`",
        f"- network_used: `{str(summary['network_used']).lower()}`",
        "- public_index_mutated: `false`",
        "- master_index_mutated: `false`",
    ]
    if summary["blocked_reasons"]:
        lines.append("")
        lines.append("## Blocked Reasons")
        lines.extend(f"- {reason}" for reason in summary["blocked_reasons"])
    return "\n".join(lines) + "\n"


def _blocked_artifacts(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "live_probe_result": dict(result),
        "normalized": None,
        "source_cache_candidate": build_not_created_preview("source_cache_candidate", result),
        "evidence_preview": build_not_created_preview("evidence_candidate_preview", result),
        "review_seed": build_not_created_preview("review_queue_seed_preview", result),
    }


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
        rel = resolved.relative_to(repo_resolved).as_posix()
        rel_lower = rel.casefold()
        for forbidden in FORBIDDEN_OUTPUT_ROOTS:
            forbidden_lower = forbidden.casefold().rstrip("/")
            if rel_lower == forbidden_lower or rel_lower.startswith(forbidden_lower + "/"):
                raise ValueError(f"refusing forbidden output root: {forbidden}")
        if rel_lower.startswith("examples/connectors/internet_archive/live_probe/"):
            return resolved
        if rel_lower.startswith("control/audits/") and "/generated/" in rel_lower:
            return resolved
        raise ValueError(f"refusing output outside approved IA live-probe roots: {rel}")
    except ValueError as exc:
        if str(exc).startswith("refusing"):
            raise
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
            return resolved
        except ValueError as temp_exc:
            raise ValueError(f"refusing output outside repository approved roots or temp directory: {resolved}") from temp_exc


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run offline H13 local/private boundary dry-runs with fail-closed gates."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from archive.prototypes.legacy_runtime.connectors.h13_local_private.boundary_dry_run_common import (  # noqa: E402
    BOUNDARY_REQUEST_KEYS,
    H13_SOURCE_IDS,
    build_h13_boundary_dry_run_blocked_result,
    build_h13_boundary_dry_run_output_bundle,
    build_h13_boundary_dry_run_result,
    build_h13_local_private_boundary_dry_run_request,
    load_h13_local_private_boundary_policy_bundle,
    summarize_h13_boundary_dry_run_result,
    validate_h13_boundary_dry_run_request,
)
from archive.prototypes.legacy_runtime.connectors.h13_local_private.fixture_loader import load_h13_local_private_fixture  # noqa: E402

ALLOWED_PREFIXES = (
    "examples/connectors/h13_local_private/boundary_dry_run_results",
    "examples/connectors/h13_local_private/boundary_dry_run_outputs",
    "control/audits/h13-bundle-03-local-private-boundary-dry-runs-v0/generated",
)
REQUEST_INPUT_PREFIXES = (
    "examples/connectors/h13_local_private/boundary_dry_run",
    "control/audits/h13-bundle-03-local-private-boundary-dry-runs-v0/generated",
)
FORBIDDEN_PREFIXES = (
    "site/dist", "site/dist/data/public_index", "runtime", "contracts", "control/inventory/publication", "control/inventory/sources",
    "local_sources", "cas", "cas_roots", "private_sources", "credential_directories", "credentials", "user_url_fetches", "accounts",
    "import_export_staging", "pack_exports", "pack_imports", "archive_extractions", "execution_actions", "acquisition_actions",
    "source_cache", "evidence_ledger", "review_queue", "master_index", "public_index", ".aide.local", ".local/eureka", ".cache/eureka",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-id", choices=sorted(H13_SOURCE_IDS))
    parser.add_argument("--request-key")
    parser.add_argument("--input")
    parser.add_argument("--fixture-input")
    parser.add_argument("--output")
    parser.add_argument("--local-source-output")
    parser.add_argument("--private-boundary-output")
    parser.add_argument("--url-boundary-output")
    parser.add_argument("--authenticated-boundary-output")
    parser.add_argument("--restricted-manifest-output")
    parser.add_argument("--cas-boundary-output")
    parser.add_argument("--pack-boundary-output")
    parser.add_argument("--privacy-output")
    parser.add_argument("--rights-safety-output")
    parser.add_argument("--source-cache-output")
    parser.add_argument("--evidence-preview-output")
    parser.add_argument("--review-seed-output")
    parser.add_argument("--health-output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        bundle = load_h13_local_private_boundary_policy_bundle(REPO_ROOT)
        request = _load_request(args, bundle)
        result = run_boundary(request, bundle, args.fixture_input)
        if not args.check:
            outputs = {
                args.output: result,
                args.local_source_output: result["local_source_identity_candidate"],
                args.private_boundary_output: result["private_source_boundary_candidate"],
                args.url_boundary_output: result["user_supplied_url_boundary_candidate"],
                args.authenticated_boundary_output: result["authenticated_source_boundary_candidate"],
                args.restricted_manifest_output: result["restricted_source_manifest_candidate"],
                args.cas_boundary_output: result["local_cas_import_boundary_candidate"],
                args.pack_boundary_output: result["pack_export_import_boundary_candidate"],
                args.privacy_output: result["privacy_redaction_candidate"],
                args.rights_safety_output: result["local_private_rights_safety_candidate"],
                args.source_cache_output: result["source_cache_candidate_preview"],
                args.evidence_preview_output: result["evidence_candidate_preview"],
                args.review_seed_output: result["review_queue_seed_preview"],
                args.health_output: result["boundary_health_summary"],
            }
            for path, payload in outputs.items():
                if path:
                    _write_json(path, payload)
            if args.summary_output:
                _write_text(args.summary_output, render_summary(result))
        summary = {
            "status": "valid",
            "mode": "check" if args.check else "dry_run",
            "wrote_files": (not args.check) and any([args.output, args.local_source_output, args.private_boundary_output, args.url_boundary_output, args.authenticated_boundary_output, args.restricted_manifest_output, args.cas_boundary_output, args.pack_boundary_output, args.privacy_output, args.rights_safety_output, args.source_cache_output, args.evidence_preview_output, args.review_seed_output, args.health_output, args.summary_output]),
            "boundary_dry_run": summarize_h13_boundary_dry_run_result(result),
        }
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            dry = summary["boundary_dry_run"]
            print("H13 local/private boundary dry-run", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"mode: {summary['mode']}", file=stdout)
            print(f"source_id: {dry['source_id']}", file=stdout)
            print(f"result: {dry['result_status']}", file=stdout)
            print(f"operation_count: {dry['operation_count']}", file=stdout)
            print(f"local_access_used: {str(dry['local_access_used']).lower()}", file=stdout)
            print(f"network_used: {str(dry['network_used']).lower()}", file=stdout)
            if dry["blocked_reasons"]:
                print("blocked_reasons:", file=stdout)
                for reason in dry["blocked_reasons"]:
                    print(f"- {reason}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H13 local/private boundary dry-run", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def run_boundary(request: Mapping[str, Any], bundle: Mapping[str, Any], fixture_input: str | None = None) -> dict[str, Any]:
    validation = validate_h13_boundary_dry_run_request(request, bundle)
    if not validation["approved"]:
        return build_h13_boundary_dry_run_blocked_result(request, validation["blocked_reasons"], bundle)
    if fixture_input:
        fixture = load_h13_local_private_fixture(fixture_input)
        return build_h13_boundary_dry_run_result(str(request["source_id"]), fixture, {"result_status": "boundary_dry_run_completed", "operation_count": 1, "boundary_dry_run_request_ref": request.get("boundary_dry_run_request_id"), "request_key": request.get("approved_request_key")}, bundle)
    return build_h13_boundary_dry_run_result(str(request["source_id"]), {"metadata_summary": "Approved boundary preflight without source access."}, {"result_status": "dry_run_preflight_pass", "operation_count": 1, "boundary_dry_run_request_ref": request.get("boundary_dry_run_request_id"), "request_key": request.get("approved_request_key")}, bundle)


def render_summary(result: Mapping[str, Any]) -> str:
    summary = summarize_h13_boundary_dry_run_result(result)
    lines = [
        "# H13 Local/Private Boundary Dry-Run Summary",
        "",
        f"- source_id: `{summary['source_id']}`",
        f"- result: `{summary['result_status']}`",
        f"- operation_count: `{summary['operation_count']}`",
        f"- local_access_used: `{str(summary['local_access_used']).lower()}`",
        f"- network_used: `{str(summary['network_used']).lower()}`",
        "- boundary_dry_run_only: `true`",
        "- local_access: `false`",
        "- private_source_access: `false`",
        "- user_supplied_url_fetch: `false`",
        "- authenticated_access: `false`",
        "- restricted_source_access: `false`",
        "- cas_import: `false`",
        "- pack_export_import: `false`",
        "- source_cache_writes: `false`",
        "- public_index_writes: `false`",
        "- private_publication: `false`",
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
    request_key = args.request_key or BOUNDARY_REQUEST_KEYS[args.source_id]
    module = importlib.import_module(f"archive.prototypes.legacy_runtime.connectors.h13_local_private.boundary_dry_run_{args.source_id}")
    return module.build_boundary_request(build_h13_local_private_boundary_dry_run_request(args.source_id, request_key, bundle), bundle)


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
            raise ValueError("request input path must be under H13 boundary request examples/audit roots or an explicit temp directory") from exc
        return resolved
    if any(rel == prefix or rel.startswith(prefix + "/") for prefix in REQUEST_INPUT_PREFIXES):
        return resolved
    raise ValueError("repo request input path must be under H13 boundary request examples or audit generated roots")


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
            raise ValueError("output path must be under H13 boundary examples/audit roots or an explicit temp directory") from exc
        return resolved
    rel_lower = rel.lower()
    for forbidden in FORBIDDEN_PREFIXES:
        if rel_lower == forbidden or rel_lower.startswith(forbidden.rstrip("/") + "/"):
            raise ValueError(f"refusing forbidden output root: {forbidden}")
    if any(rel_lower == prefix or rel_lower.startswith(prefix.rstrip("/") + "/") for prefix in ALLOWED_PREFIXES):
        return resolved
    raise ValueError("repo output path must be under H13 boundary examples or audit generated roots")


def _write_json(raw: str, payload: Mapping[str, Any]) -> None:
    path = safe_output_path(raw)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(raw: str, payload: str) -> None:
    path = safe_output_path(raw)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())

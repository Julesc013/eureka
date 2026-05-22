#!/usr/bin/env python3
"""Summarize H13 local/private boundary dry-run outputs offline."""

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

from archive.prototypes.legacy_runtime.connectors.h13_local_private.boundary_dry_run_common import H13_SOURCE_IDS  # noqa: E402

ALLOWED_INPUT_PREFIXES = (
    "examples/connectors/h13_local_private/boundary_dry_run_results",
    "examples/connectors/h13_local_private/boundary_dry_run_outputs",
    "control/audits/h13-bundle-03-local-private-boundary-dry-runs-v0/generated",
)
FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist", "site/dist/data/public_index", "runtime", "contracts", "local_sources", "cas", "cas_roots", "private_sources",
    "credentials", "credential_directories", "user_url_fetches", "accounts", "import_export_staging", "pack_exports",
    "pack_imports", "source_cache", "evidence_ledger", "review_queue", "archive_extractions", "execution_actions",
    "acquisition_actions", "master_index", "public_index", ".aide.local", ".local/eureka", ".cache/eureka",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", default=[])
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        summary = build_summary(args.input or ["examples/connectors/h13_local_private/boundary_dry_run_results"])
        if not args.check:
            if args.output:
                _write_json(args.output, summary)
                summary["wrote_files"] = True
            if args.summary_output:
                _write_text(args.summary_output, render_summary_markdown(summary))
                summary["wrote_files"] = True
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H13 local/private boundary dry-run output summary", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"attempted_sources: {len(summary['attempted_sources'])}", file=stdout)
            print(f"completed_sources: {len(summary['completed_sources'])}", file=stdout)
            print(f"blocked_sources: {len(summary['blocked_sources'])}", file=stdout)
            print(f"operation_count_total: {summary['operation_count_total']}", file=stdout)
            print(f"local_access_used: {str(summary['local_access_used']).lower()}", file=stdout)
            print(f"network_used: {str(summary['network_used']).lower()}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H13 local/private boundary dry-run output summary", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def build_summary(inputs: Sequence[str]) -> dict[str, Any]:
    files: list[Path] = []
    for raw in inputs:
        path = safe_input_path(raw)
        if path.is_dir():
            files.extend(path.rglob("*.json"))
        elif path.exists():
            files.append(path)
    records: list[Mapping[str, Any]] = []
    for path in files:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(value, Mapping):
            records.extend(_walk_mappings(value))

    def count_schema(schema: str) -> int:
        return sum(1 for item in records if str(item.get("schema_version", "")).startswith(schema))

    results = [item for item in records if item.get("schema_version") == "h13_local_private_boundary_dry_run_result.v0"]
    attempted = sorted({str(item.get("source_id")) for item in results if item.get("source_id") in H13_SOURCE_IDS})
    blocked = sorted({str(item.get("source_id")) for item in results if str(item.get("result_status", "")).startswith("blocked_")})
    completed = sorted({str(item.get("source_id")) for item in results if item.get("result_status") in ("dry_run_preflight_pass", "boundary_dry_run_completed")})
    return {
        "schema_version": "h13_local_private_boundary_output_summary.v0",
        "status": "pass",
        "attempted_sources": attempted,
        "completed_sources": completed,
        "blocked_sources": blocked,
        "operation_count_total": sum(int(item.get("operation_count") or 0) for item in results),
        "local_access_used": any(bool(item.get("local_access_used")) for item in results),
        "network_used": any(bool(item.get("network_used")) for item in results),
        "local_source_identity_candidate_count": count_schema("h13_local_source_identity_candidate"),
        "private_source_boundary_candidate_count": count_schema("h13_private_source_boundary_candidate"),
        "user_supplied_url_boundary_candidate_count": count_schema("h13_user_supplied_url_boundary_candidate"),
        "authenticated_source_boundary_candidate_count": count_schema("h13_authenticated_source_boundary_candidate"),
        "restricted_source_manifest_candidate_count": count_schema("h13_restricted_source_manifest_candidate"),
        "local_cas_import_boundary_candidate_count": count_schema("h13_local_cas_import_boundary_candidate"),
        "pack_export_import_boundary_candidate_count": count_schema("h13_pack_export_import_boundary_candidate"),
        "privacy_redaction_candidate_count": count_schema("h13_privacy_redaction_candidate"),
        "local_private_rights_safety_candidate_count": count_schema("h13_local_private_rights_safety_candidate"),
        "source_cache_candidate_preview_count": count_schema("h13_local_private_source_cache_candidate_preview"),
        "evidence_candidate_preview_count": count_schema("h13_local_private_evidence_candidate_preview"),
        "review_queue_seed_preview_count": count_schema("h13_local_private_boundary_review_seed"),
        "boundary_health_summary_count": count_schema("h13_local_private_boundary_health_summary"),
        "blocked_reasons": sorted({reason for item in results for reason in item.get("blocked_reasons", [])}),
        "wrote_files": False,
    }


def render_summary_markdown(summary: Mapping[str, Any]) -> str:
    return "\n".join([
        "# H13 Local/Private Boundary Dry-Run Output Summary",
        "",
        f"- status: `{summary['status']}`",
        f"- attempted_sources: `{len(summary['attempted_sources'])}`",
        f"- completed_sources: `{len(summary['completed_sources'])}`",
        f"- blocked_sources: `{len(summary['blocked_sources'])}`",
        f"- operation_count_total: `{summary['operation_count_total']}`",
        "- local/private/restricted access: `false`",
        "- source-cache/evidence/index writes: `false`",
        "",
        "Outputs are boundary dry-run candidates and previews, not accepted local/private/restricted source truth.",
    ]) + "\n"


def _walk_mappings(value: Any) -> list[Mapping[str, Any]]:
    records: list[Mapping[str, Any]] = []
    if isinstance(value, Mapping):
        records.append(value)
        for item in value.values():
            records.extend(_walk_mappings(item))
    elif isinstance(value, list):
        for item in value:
            records.extend(_walk_mappings(item))
    return records


def safe_input_path(raw: str | Path) -> Path:
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
            raise ValueError("input path must be H13 boundary examples/audit generated root or explicit temp directory") from exc
        return resolved
    if any(rel == prefix or rel.startswith(prefix + "/") for prefix in ALLOWED_INPUT_PREFIXES):
        return resolved
    raise ValueError("repo input path must be under H13 boundary examples or audit generated roots")


def safe_output_path(raw: str | Path) -> Path:
    path = Path(raw)
    resolved = path if path.is_absolute() else REPO_ROOT / path
    resolved = resolved.resolve()
    repo = REPO_ROOT.resolve()
    try:
        rel = resolved.relative_to(repo).as_posix()
    except ValueError:
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
        except ValueError as exc:
            raise ValueError("output path must be under H13 audit generated root or explicit temp directory") from exc
        return resolved
    rel_lower = rel.lower()
    allowed_prefix = "control/audits/h13-bundle-03-local-private-boundary-dry-runs-v0/generated/"
    if rel_lower.startswith(allowed_prefix):
        return resolved
    for prefix in FORBIDDEN_OUTPUT_ROOTS:
        if rel_lower == prefix or rel_lower.startswith(prefix + "/"):
            raise ValueError(f"refusing forbidden output root: {prefix}")
    raise ValueError("repo output path must be under the H13 boundary audit generated root")


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

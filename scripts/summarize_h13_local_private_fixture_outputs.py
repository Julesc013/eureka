#!/usr/bin/env python3
"""Summarize H13 local/private fixture outputs offline."""

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

from control.prototypes.legacy_runtime.connectors.h13_local_private.normalizer_common import H13_SOURCE_IDS  # noqa: E402

FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist", "data/public_index", "runtime", "contracts", "local_sources", "cas", "cas_roots", "private_sources",
    "credentials", "credential_directories", "user_url_fetches", "accounts", "import_export_staging", "pack_exports",
    "pack_imports", "source_cache", "evidence_ledger", "review_queue", "archive_extractions", "execution_actions",
    "acquisition_actions", "master_index", ".aide.local", ".local/eureka", ".cache/eureka",
)
ALLOWED_INPUT_PREFIXES = (
    "examples/connectors/h13_local_private",
    "control/audits/h13-bundle-02-local-private-fixture-runtime-v0/generated",
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
        summary = build_summary(args.input or ["examples/connectors/h13_local_private"])
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
            print("H13 local/private fixture output summary", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"normalized_record_count: {summary['normalized_record_count']}", file=stdout)
            print(f"local_source_identity_candidate_count: {summary['local_source_identity_candidate_count']}", file=stdout)
            print(f"rights_safety_candidate_count: {summary['local_private_rights_safety_candidate_count']}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H13 local/private fixture output summary", file=stdout)
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

    source_ids = {str(item.get("source_id")) for item in records if item.get("source_id") in H13_SOURCE_IDS}
    return {
        "schema_version": "h13_local_private_fixture_output_summary.v0",
        "status": "pass",
        "source_count": len(source_ids),
        "normalized_record_count": count_schema("h13_local_private_normalized_record"),
        "local_source_identity_candidate_count": count_schema("h13_local_source_identity_candidate"),
        "private_source_boundary_candidate_count": count_schema("h13_private_source_boundary_candidate"),
        "user_supplied_url_boundary_candidate_count": count_schema("h13_user_supplied_url_boundary_candidate"),
        "authenticated_source_boundary_candidate_count": count_schema("h13_authenticated_source_boundary_candidate"),
        "restricted_source_manifest_candidate_count": count_schema("h13_restricted_source_manifest_candidate"),
        "local_cas_import_boundary_candidate_count": count_schema("h13_local_cas_import_boundary_candidate"),
        "pack_export_import_boundary_candidate_count": count_schema("h13_pack_export_import_boundary_candidate"),
        "privacy_redaction_candidate_count": count_schema("h13_privacy_redaction_candidate"),
        "local_private_rights_safety_candidate_count": count_schema("h13_local_private_rights_safety_candidate"),
        "fixture_replay_result_count": count_schema("h13_local_private_fixture_replay_result"),
        "blockers": ["local/private/restricted access not approved", "CAS import, pack export/import, publication, source-cache writes, evidence writes, and truth acceptance forbidden"],
        "warnings": [],
        "wrote_files": False,
    }


def render_summary_markdown(summary: Mapping[str, Any]) -> str:
    return "\n".join([
        "# H13 Local/Private Fixture Output Summary",
        "",
        f"- status: `{summary['status']}`",
        f"- source_count: `{summary['source_count']}`",
        f"- normalized_record_count: `{summary['normalized_record_count']}`",
        f"- local_source_identity_candidate_count: `{summary['local_source_identity_candidate_count']}`",
        f"- restricted_source_manifest_candidate_count: `{summary['restricted_source_manifest_candidate_count']}`",
        "",
        "Outputs are fixture-only candidates and previews, not accepted local/private/restricted source truth.",
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
            raise ValueError("input path must be H13 examples/audit generated root or explicit temp directory") from exc
        return resolved
    if any(rel == prefix or rel.startswith(prefix + "/") for prefix in ALLOWED_INPUT_PREFIXES):
        return resolved
    raise ValueError("repo input path must be under H13 fixture examples or audit generated roots")


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
    allowed_prefix = "control/audits/h13-bundle-02-local-private-fixture-runtime-v0/generated/"
    if rel_lower.startswith(allowed_prefix):
        return resolved
    for prefix in FORBIDDEN_OUTPUT_ROOTS:
        if rel_lower == prefix or rel_lower.startswith(prefix + "/"):
            raise ValueError(f"refusing forbidden output root: {prefix}")
    raise ValueError("repo output path must be under the H13 fixture audit generated root")


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

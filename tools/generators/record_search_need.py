#!/usr/bin/env python3
"""Record a local-only SearchNeed report from explicit JSON input.

The command writes no files by default. It performs no network calls, no model
calls, no WorkUnit execution, no public telemetry, no public search mutation,
and no master-index mutation.
"""

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

from runtime.local.foundry.search_need import (  # noqa: E402
    REPORT_SCHEMA_VERSION,
    build_search_need_from_query_observation,
    build_search_need_from_search_miss,
    format_summary_markdown,
    summarize_search_need,
    validate_search_need,
)


FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist/",
    "runtime/",
    "contracts/",
    "control/inventory/publication/",
    "control/inventory/master_index/",
    ".aide.local/",
    ".local/eureka/",
    ".cache/eureka/",
)


def build_report(input_path: Path, *, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    payload = _read_json(input_path)
    if payload.get("schema_version") == "query_observation_runtime.v0":
        record = build_search_need_from_query_observation(payload)
    else:
        record = build_search_need_from_search_miss(payload)
    errors = validate_search_need(record)
    summary = summarize_search_need(record)
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "status": "pass" if not errors else "fail",
        "input_ref": _display_path(input_path, repo_root),
        "record": record,
        "summary": summary,
        "validation_errors": errors,
        "warnings": [],
        "runtime_scope": {
            "explicit_input_only": True,
            "local_only": True,
            "writes_no_files_by_default": True,
            "public_telemetry_enabled": False,
            "raw_public_query_logging_enabled": False,
        },
        "truth_boundary": {
            "search_need_is_public_truth": False,
            "search_need_is_accepted_evidence": False,
            "search_need_can_mutate_master_index": False,
            "search_need_is_exhaustive_global_absence": False,
            "human_review_required_for_downstream_use": True,
        },
        "product_boundary": {
            "implemented_public_telemetry": False,
            "changed_public_search_behavior": False,
            "created_local_private_state": False,
            "enabled_network_access": False,
            "enabled_live_probes": False,
            "enabled_source_sync": False,
            "enabled_source_connectors": False,
            "enabled_downloads": False,
            "enabled_installers": False,
            "enabled_execution": False,
            "enabled_uploads": False,
            "enabled_accounts": False,
            "enabled_telemetry": False,
            "enabled_pack_import_runtime": False,
            "enabled_review_runtime": False,
            "enabled_model_provider_calls": False,
            "mutated_master_index": False,
            "claimed_rights_clearance": False,
            "claimed_malware_safety": False,
            "claimed_verified_installability": False,
            "claimed_exhaustive_global_search": False,
            "claimed_production_readiness": False,
        },
    }


def output_path_allowed(path: Path, *, repo_root: Path = REPO_ROOT) -> bool:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
            return True
        except ValueError:
            return False

    normalized = relative.rstrip("/") + "/"
    if any(normalized.startswith(root) or relative == root.rstrip("/") for root in FORBIDDEN_OUTPUT_ROOTS):
        return False
    return relative.startswith("control/audits/") and "/generated/" in f"/{relative}"


def write_report(report: Mapping[str, Any], output_path: Path) -> None:
    if not output_path_allowed(output_path):
        raise ValueError(f"refusing forbidden output path: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_summary(report: Mapping[str, Any], output_path: Path) -> None:
    if not output_path_allowed(output_path):
        raise ValueError(f"refusing forbidden output path: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(format_summary_markdown(report["summary"]), encoding="utf-8")


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None, stderr: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Explicit search miss, query observation, or SearchNeed JSON input.")
    parser.add_argument("--output", type=Path, help="Optional explicit JSON report output path.")
    parser.add_argument("--summary-output", type=Path, help="Optional explicit markdown summary output path.")
    parser.add_argument("--check", action="store_true", help="Validate and report status without requiring output.")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    out = stdout or sys.stdout
    err = stderr or sys.stderr
    try:
        report = build_report(args.input)
        if args.output:
            write_report(report, args.output)
        if args.summary_output:
            write_summary(report, args.summary_output)
    except Exception as exc:  # deterministic CLI surface
        err.write(f"record_search_need: ERROR: {exc}\n")
        return 2

    if args.json:
        out.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        summary = report["summary"]
        out.write("SearchNeed report\n")
        out.write(f"status: {report['status']}\n")
        out.write(f"search_need_id: {summary.get('search_need_id')}\n")
        out.write(f"need_intent: {summary.get('need_intent')}\n")
        out.write(f"review_required: {str(summary.get('review_required')).lower()}\n")
        if report["validation_errors"]:
            out.write("errors:\n")
            for error in report["validation_errors"]:
                out.write(f"- {error}\n")

    return 0 if report["status"] == "pass" else 1


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("input JSON must be an object")
    return payload


def _display_path(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())

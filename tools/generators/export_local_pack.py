#!/usr/bin/env python3
"""Export a local pack draft as a review-gated draft artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_foundry import pack_export


FORBIDDEN_OUTPUT_PREFIXES = (
    "site/dist",
    "runtime",
    "contracts",
    "site/dist/data/public_index",
    "control/inventory/publication",
    "control/inventory/sources",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
    ".git",
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Explicit pack draft JSON input path.")
    parser.add_argument("--output", help="Optional exported pack JSON output path.")
    parser.add_argument("--report-output", help="Optional pack export result JSON output path.")
    parser.add_argument("--summary-output", help="Optional markdown summary output path.")
    parser.add_argument("--check", action="store_true", help="Validate and print only.")
    parser.add_argument("--json", action="store_true", help="Print result JSON.")
    args = parser.parse_args(argv)

    try:
        input_pack_draft = pack_export.load_json(args.input)
        export_record = pack_export.build_pack_export(input_pack_draft)
        request = _build_request(args, input_pack_draft, export_record)
        result = pack_export.build_pack_export_result(request, export_record)
        errors = result["validation"]["request_errors"] + result["validation"]["export_errors"]
        if errors:
            _print_errors(errors)
            return 1

        if not args.check:
            for path in (args.output, args.report_output, args.summary_output):
                if path:
                    _validate_output_path(path)
            if args.output:
                _write_json(Path(args.output), export_record)
            if args.report_output:
                _write_json(Path(args.report_output), result)
            if args.summary_output:
                _write_text(Path(args.summary_output), pack_export.format_pack_export_summary_markdown(pack_export.summarize_pack_export(export_record)))

        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(pack_export.format_pack_export_summary_markdown(pack_export.summarize_pack_export(export_record)), end="")
        return 0
    except Exception as exc:  # pragma: no cover - exercised by subprocess tests
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def _build_request(args: argparse.Namespace, input_pack_draft: dict[str, Any], export_record: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": pack_export.REQUEST_SCHEMA_VERSION,
        "pack_export_request_id": f"pack_export_request.{export_record.get('export_pack_type', 'unknown')}.cli.v0",
        "requested_pack_type": export_record.get("export_pack_type", ""),
        "request_status": "local_export_only",
        "input_pack_draft_ref": str(Path(args.input).as_posix()),
        "input_pack_draft_summary": {
            "pack_draft_id": input_pack_draft.get("pack_draft_id", ""),
            "pack_type": input_pack_draft.get("pack_type", ""),
            "pack_status": input_pack_draft.get("pack_status", ""),
        },
        "requested_output_path": _safe_output_ref(args.output),
        "export_format": "json_pack_export",
        "fixity_policy": {
            "algorithm": "sha256",
            "fixity_required_for_export": True,
            "deterministic_serialization_required": True,
            "real_signing_enabled": False,
        },
        "signature_policy": _signature_policy(),
        "review_gates": {field: True for field in pack_export.REVIEW_GATE_TRUE_FIELDS},
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "no_goals": [
            "no pack import",
            "no pack submission",
            "no hosted upload",
            "no accepted pack",
            "no real signing",
            "no public index mutation",
            "no master index mutation",
        ],
        "notes": ["CLI request built from explicit local pack draft JSON."],
    }


def _signature_policy() -> dict[str, Any]:
    return {
        "signature_status": "unsigned_placeholder_only",
        "real_signing_enabled": False,
        "signature_placeholder_allowed": True,
        "private_keys_allowed": False,
        "claims_cryptographic_signature": False,
    }


def _truth_boundary() -> dict[str, bool]:
    truth = {field: False for field in pack_export.TRUTH_BOUNDARY_FALSE_FIELDS}
    truth.update({field: True for field in pack_export.TRUTH_BOUNDARY_TRUE_FIELDS})
    return truth


def _product_boundary() -> dict[str, bool]:
    product = {field: False for field in pack_export.PRODUCT_BOUNDARY_FALSE_FIELDS}
    product.update({field: True for field in pack_export.PRODUCT_BOUNDARY_TRUE_FIELDS})
    return product


def _safe_output_ref(output_path: str | None) -> str:
    if not output_path:
        return ""
    path = Path(output_path)
    resolved = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    rel = _repo_relative(resolved)
    if rel is not None:
        return rel.as_posix()
    temp_root = Path(tempfile.gettempdir()).resolve()
    try:
        resolved.relative_to(temp_root)
        return "explicit_temp_test_output"
    except ValueError:
        return "explicit_output_path"


def _validate_output_path(path_text: str) -> None:
    path = Path(path_text)
    resolved = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    rel = _repo_relative(resolved)
    rel_posix = rel.as_posix() if rel is not None else ""
    for prefix in FORBIDDEN_OUTPUT_PREFIXES:
        if rel_posix == prefix or rel_posix.startswith(prefix + "/"):
            raise ValueError(f"output path is forbidden by pack export path policy: {path_text}")
    if rel is not None:
        parts = rel.parts
        if len(parts) >= 4 and parts[0] == "control" and parts[1] == "audits" and "generated" in parts:
            return
        if len(parts) >= 2 and parts[0] == "examples" and parts[1] == "pack_exports":
            return
    temp_root = Path(tempfile.gettempdir()).resolve()
    try:
        resolved.relative_to(temp_root)
        return
    except ValueError:
        pass
    raise ValueError(f"output path is not in an allowed pack export output root: {path_text}")


def _repo_relative(path: Path) -> Path | None:
    try:
        return path.relative_to(REPO_ROOT)
    except ValueError:
        return None


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    if not path.is_absolute():
        path = REPO_ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, payload: str) -> None:
    if not path.is_absolute():
        path = REPO_ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def _print_errors(errors: list[str]) -> None:
    for error in sorted(errors):
        print(f"ERROR: {error}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build a preview-only import projection from a quarantined pack result."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.extraction.guards import ensure_allowed_input_path, ensure_allowed_output_path  # noqa: E402
from runtime.local.foundry import pack_import_preview, pack_quarantine  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Quarantine result JSON or exported pack JSON.")
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        policy = pack_quarantine.load_quarantine_policy(REPO_ROOT)
        input_path = ensure_allowed_input_path(args.input, policy, REPO_ROOT)
        payload = pack_quarantine.load_json(input_path)
        if payload.get("schema_version") == pack_quarantine.RESULT_SCHEMA_VERSION:
            quarantine_result = payload
            pack_like = {
                "pack_export_id": quarantine_result.get("input_pack_ref", ""),
                "export_pack_type": quarantine_result.get("input_pack_type", ""),
                "provenance_summary": quarantine_result.get("provenance_summary", {}),
            }
        else:
            partial = pack_quarantine.build_full_quarantine_bundle(payload, policy)
            quarantine_result = partial["quarantine_result"]
            pack_like = payload
        preview = pack_import_preview.build_pack_import_preview(pack_like, quarantine_result, policy)
        errors = pack_import_preview.validate_pack_import_preview(preview, policy)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        if not args.check:
            if args.output:
                _write_json(ensure_allowed_output_path(args.output, policy, REPO_ROOT), preview)
            if args.summary_output:
                _write_text(ensure_allowed_output_path(args.summary_output, policy, REPO_ROOT), _summary(preview))
        response = {"schema_version": "pack_import_preview_cli_result.v0", "status": "pass", "wrote_files": bool(not args.check and (args.output or args.summary_output)), "import_preview": preview}
        if args.json:
            print(json.dumps(response, indent=2, sort_keys=True))
        else:
            print(_summary(preview), end="")
        return 0
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def _summary(preview: dict) -> str:
    summary = pack_import_preview.summarize_pack_import_preview(preview)
    return (
        "# Pack Import Preview\n\n"
        f"- Status: {summary.get('import_preview_status')}\n"
        f"- Proposed records: {summary.get('proposed_record_count')}\n"
        f"- Blockers: {summary.get('blocker_count')}\n"
        "- Imports records: false\n"
        "- Public index mutated: false\n"
        "- Master index mutated: false\n"
    )


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())

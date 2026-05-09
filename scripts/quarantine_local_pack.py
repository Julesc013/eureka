#!/usr/bin/env python3
"""Quarantine an explicit local pack export without importing or accepting it."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.extraction.guards import ensure_allowed_input_path, ensure_allowed_output_path  # noqa: E402
from runtime.local_foundry import pack_quarantine  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Explicit exported pack draft JSON.")
    parser.add_argument("--output", help="Optional quarantine result JSON output.")
    parser.add_argument("--fixity-output", help="Optional fixity report JSON output.")
    parser.add_argument("--signature-output", help="Optional signature verification report JSON output.")
    parser.add_argument("--import-preview-output", help="Optional import preview JSON output.")
    parser.add_argument("--review-seed-output", help="Optional contribution review seed JSON output.")
    parser.add_argument("--summary-output", help="Optional markdown summary output.")
    parser.add_argument("--check", action="store_true", help="Validate only; do not write outputs.")
    parser.add_argument("--json", action="store_true", help="Print JSON payload.")
    args = parser.parse_args(argv)

    try:
        policy = pack_quarantine.load_quarantine_policy(REPO_ROOT)
        input_path = ensure_allowed_input_path(args.input, policy, REPO_ROOT)
        pack = pack_quarantine.load_pack_for_quarantine(input_path)
        bundle = pack_quarantine.build_full_quarantine_bundle(pack, policy)
        errors = _validate_bundle(bundle, policy)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        if not args.check:
            outputs = {
                args.output: bundle["quarantine_result"],
                args.fixity_output: bundle["fixity_report"],
                args.signature_output: bundle["signature_verification_report"],
                args.import_preview_output: bundle["import_preview"],
                args.review_seed_output: bundle["contribution_review_seed"],
            }
            for path_text, payload in outputs.items():
                if path_text:
                    _write_json(ensure_allowed_output_path(path_text, policy, REPO_ROOT), payload)
            if args.summary_output:
                _write_text(
                    ensure_allowed_output_path(args.summary_output, policy, REPO_ROOT),
                    _summary_markdown(bundle["quarantine_result"]),
                )
        response = {
            "schema_version": "pack_quarantine_cli_result.v0",
            "status": "pass",
            "wrote_files": bool(
                not args.check
                and (
                    args.output
                    or args.fixity_output
                    or args.signature_output
                    or args.import_preview_output
                    or args.review_seed_output
                    or args.summary_output
                )
            ),
            **bundle,
        }
        if args.json:
            print(json.dumps(response, indent=2, sort_keys=True))
        else:
            print(_summary_markdown(bundle["quarantine_result"]), end="")
        return 0
    except Exception as exc:  # pragma: no cover - subprocess tests exercise
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def _validate_bundle(bundle: dict[str, Any], policy: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    errors.extend(pack_quarantine.validate_pack_quarantine_result(bundle["quarantine_result"], policy))
    errors.extend(pack_quarantine.validate_pack_fixity_report(bundle["fixity_report"], policy))
    errors.extend(pack_quarantine.validate_signature_envelope(bundle["signature_envelope"], policy))
    errors.extend(pack_quarantine.validate_signature_verification_report(bundle["signature_verification_report"], policy))
    errors.extend(pack_quarantine.validate_pack_import_preview(bundle["import_preview"], policy))
    errors.extend(pack_quarantine.validate_contribution_review_seed(bundle["contribution_review_seed"], policy))
    errors.extend(pack_quarantine.validate_pack_trust_preview(bundle["trust_preview"], policy))
    errors.extend(pack_quarantine.validate_pack_trust_preview(bundle["revocation_preview"], policy))
    return sorted(dict.fromkeys(errors))


def _summary_markdown(result: dict[str, Any]) -> str:
    summary = pack_quarantine.summarize_pack_quarantine_result(result)
    lines = [
        "# Pack Quarantine Summary",
        "",
        f"- Quarantine result: {summary.get('quarantine_result_id', '')}",
        f"- Input pack type: {summary.get('input_pack_type', '')}",
        f"- Status: {summary.get('quarantine_status', '')}",
        f"- Blockers: {summary.get('blocker_count', 0)}",
        f"- Review required: {str(summary.get('requires_review', True)).lower()}",
        f"- Pack imported: {str(summary.get('pack_imported', False)).lower()}",
        f"- Pack submitted: {str(summary.get('pack_submitted', False)).lower()}",
        f"- Pack accepted: {str(summary.get('pack_accepted', False)).lower()}",
        f"- Real signing: {str(summary.get('real_signing', False)).lower()}",
        f"- Public index mutated: {str(summary.get('public_index_mutated', False)).lower()}",
        f"- Master index mutated: {str(summary.get('master_index_mutated', False)).lower()}",
    ]
    return "\n".join(lines) + "\n"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())

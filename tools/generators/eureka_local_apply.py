#!/usr/bin/env python3
"""Run the explicit local apply gate for a reviewed-index refresh."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.apply import APPLY_CONFIRMATION, run_local_apply


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", required=True, help="Explicit local instance path. Must be outside the repo.")
    parser.add_argument("--from-review-promote-fixture", action="store_true", help="Use the deterministic review/promote fixture preview.")
    parser.add_argument("--from-preview", help="Optional local apply or review/promote preview JSON file.")
    parser.add_argument("--dry-run", action="store_true", help="Preview only. This is the default.")
    parser.add_argument("--apply", action="store_true", help="Perform the approved local apply.")
    parser.add_argument("--operator-token", default="", help="Operator token. The raw value is never emitted.")
    parser.add_argument("--confirm", default="", help=f"Required confirmation string for apply: {APPLY_CONFIRMATION}.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--audit-output")
    parser.add_argument("--boundary-output")
    args = parser.parse_args(argv)

    try:
        source_preview = load_source_preview(args.from_preview)
        result = run_local_apply(
            target_instance=args.instance,
            source_preview=source_preview,
            apply=bool(args.apply),
            operator_token=args.operator_token,
            confirmation=args.confirm,
        )
    except Exception as exc:
        result = {
            "schema_version": "local_apply_cli_result.v0",
            "status": "fail",
            "error": "local_apply_failed",
            "message": str(exc),
            "operator_instance_mutated": False,
            "committed_instance_state": False,
            "master_index_mutated": False,
            "committed_data_public_index_mutated": False,
            "download_performed": False,
            "upload_performed": False,
            "extraction_executed": False,
            "model_provider_used": False,
            "deployment_performed": False,
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
        }
        emit(result, args, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2

    emit(result, args, stdout)
    if result.get("status") in {"pass", "pass_with_warnings", "dry_run"}:
        return 0
    return 2 if result.get("status") == "blocked" else 1


def load_source_preview(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if "reviewed_index_refresh_preview" in payload:
        return dict(payload["reviewed_index_refresh_preview"])
    if "preview" in payload and isinstance(payload["preview"], Mapping):
        preview = payload["preview"]
        return dict(preview.get("source_preview", preview))
    return dict(payload)


def emit(result: Mapping[str, Any], args: argparse.Namespace, stdout: TextIO) -> None:
    if args.output:
        write_json(Path(args.output), result)
    if args.audit_output:
        write_json(Path(args.audit_output), dict(result.get("audit_log") or {}))
    if args.boundary_output:
        write_json(Path(args.boundary_output), dict(result.get("boundary_report") or {}))
    if args.json:
        print(json.dumps(dict(result), indent=2, sort_keys=True), file=stdout)
    else:
        print(f"status: {result.get('status', 'unknown')}", file=stdout)


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Evaluate a connector operation request without executing it."""

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

from runtime.connectors.core.policy_evaluator import evaluate_connector_policy  # noqa: E402


FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist",
    "data/public_index",
    "runtime",
    "contracts",
    "data/master_index",
    "master_index",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, help="Connector operation or live-probe request JSON.")
    parser.add_argument("--source-policy", action="append", default=[], help="Optional source/connector policy JSON. Repeatable.")
    parser.add_argument("--output", help="Optional JSON output path.")
    parser.add_argument("--check", action="store_true", help="Evaluate without writing files.")
    parser.add_argument("--json", action="store_true", help="Print JSON evaluation.")
    args = parser.parse_args(argv)
    try:
        request = _load_json(args.request)
        policies = {
            "connector_policy_evaluation_policy": _load_optional("control/inventory/connectors/connector_policy_evaluation_policy.json")
        }
        for path in args.source_policy:
            policies[str(path)] = _load_json(path)
        result = evaluate_connector_policy(request, policies)
        if args.output and not args.check:
            _write_json(args.output, result)
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
        else:
            print("Connector policy evaluation", file=stdout)
            print(f"status: {result['decision']}", file=stdout)
            print(f"connector_id: {result['connector_id']}", file=stdout)
            print(f"source_id: {result['source_id']}", file=stdout)
            print("network_used: false", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("Connector policy evaluation", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def _load_optional(path_text: str) -> dict[str, Any]:
    path = REPO_ROOT / path_text
    if not path.is_file():
        return {}
    return _load_json(path)


def _load_json(path_text: str | Path) -> dict[str, Any]:
    path = REPO_ROOT / path_text if not Path(path_text).is_absolute() else Path(path_text)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON must be an object: {path}")
    return payload


def _write_json(path_text: str, payload: Mapping[str, Any]) -> None:
    path = _safe_output_path(Path(path_text))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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
        if rel_lower.startswith("examples/connectors/core/live_probe/"):
            return resolved
        if rel_lower.startswith("control/audits/") and "/generated/" in rel_lower:
            return resolved
        raise ValueError(f"refusing output outside approved connector policy roots: {rel}")
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

#!/usr/bin/env python3
"""Build an export manifest without importing, submitting, or publishing."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.actions import action_policy  # noqa: E402
from runtime.actions.export_manifest import build_export_manifest, validate_export_manifest  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        policy = action_policy.load_action_policy(REPO_ROOT)
        manifest = build_export_manifest(_load_subject(args.subject), policy)
        errors = validate_export_manifest(manifest, policy)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        wrote_files = False
        if args.output and not args.check:
            _write_json(action_policy.ensure_allowed_output_path(args.output, policy, REPO_ROOT), manifest)
            wrote_files = True
        response = {"schema_version": "export_manifest_cli_result.v0", "status": "pass", "wrote_files": wrote_files, "export_manifest": manifest}
        if args.json:
            print(json.dumps(response, indent=2, sort_keys=True))
        else:
            print(f"Export manifest: {manifest['export_manifest_id']}\nImports or submits: false\nPublic index mutated: false\n")
        return 0
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def _load_subject(path_text: str) -> dict[str, Any]:
    path = Path(path_text)
    resolved = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    rel = resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    if not (rel.startswith("examples/actions/") or rel.startswith("control/audits/")):
        raise ValueError(f"refusing subject outside approved action roots: {rel}")
    payload = json.loads(resolved.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("subject JSON must be an object")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())

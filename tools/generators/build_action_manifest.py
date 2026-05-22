#!/usr/bin/env python3
"""Build a non-executing J0 action manifest from an explicit local subject."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.actions import action_manifest, action_policy, blocked_action  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--action", required=True, help="Action family to describe.")
    parser.add_argument("--subject", required=True, help="Explicit subject/example JSON.")
    parser.add_argument("--output", help="Optional action manifest output JSON.")
    parser.add_argument("--blocked-output", help="Optional blocked action report output JSON.")
    parser.add_argument("--check", action="store_true", help="Validate only; do not write outputs.")
    parser.add_argument("--json", action="store_true", help="Print JSON.")
    args = parser.parse_args(argv)

    try:
        policy = action_policy.load_action_policy(REPO_ROOT)
        subject = _load_subject(args.subject)
        manifest = action_manifest.build_action_manifest(subject, args.action, policy)
        blocked = None
        if manifest["action_status"] == "blocked_by_policy":
            blocked = blocked_action.build_blocked_action_report(args.action, subject, policy)
        errors = action_manifest.validate_action_manifest(manifest, policy)
        if blocked:
            errors.extend(blocked_action.validate_blocked_action_report(blocked, policy))
        if errors:
            for error in sorted(dict.fromkeys(errors)):
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        wrote_files = False
        if not args.check:
            if args.output:
                _write_json(action_policy.ensure_allowed_output_path(args.output, policy, REPO_ROOT), manifest)
                wrote_files = True
            if args.blocked_output and blocked:
                _write_json(action_policy.ensure_allowed_output_path(args.blocked_output, policy, REPO_ROOT), blocked)
                wrote_files = True
        response: dict[str, Any] = {
            "schema_version": "action_manifest_cli_result.v0",
            "status": "pass",
            "wrote_files": wrote_files,
            "action_manifest": manifest,
        }
        if blocked:
            response["blocked_action_report"] = blocked
        if args.json:
            print(json.dumps(response, indent=2, sort_keys=True))
        else:
            print(_manifest_markdown(manifest), end="")
        return 0
    except Exception as exc:  # pragma: no cover - subprocess tests cover this path
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def _manifest_markdown(manifest: dict[str, Any]) -> str:
    summary = action_manifest.summarize_action_manifest(manifest)
    lines = [
        "# Action Manifest",
        "",
        f"- Action: {summary['action_family']}",
        f"- Status: {summary['action_status']}",
        f"- Subject: {summary['subject_ref']}",
        f"- Blocked: {str(summary['blocked']).lower()}",
        f"- Download enabled: {str(summary['download_enabled']).lower()}",
        f"- Execute enabled: {str(summary['execute_enabled']).lower()}",
        f"- Public index mutated: {str(summary['public_index_mutated']).lower()}",
        f"- Master index mutated: {str(summary['master_index_mutated']).lower()}",
    ]
    return "\n".join(lines) + "\n"


def _load_subject(path_text: str) -> dict[str, Any]:
    path = _ensure_allowed_input_path(path_text)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"subject JSON must be an object: {path_text}")
    return payload


def _ensure_allowed_input_path(path_text: str) -> Path:
    path = Path(path_text)
    resolved = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    if not resolved.exists():
        raise ValueError(f"subject path does not exist: {resolved}")
    try:
        resolved.relative_to(Path(__import__("tempfile").gettempdir()).resolve())
        return resolved
    except ValueError:
        pass
    allowed = (
        "examples/actions",
        "examples/pack_exports",
        "examples/pack_quarantine",
        "examples/search_quality",
        "control/audits",
    )
    rel = resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    if rel.startswith(allowed):
        return resolved
    raise ValueError(f"refusing subject outside approved example/audit roots: {rel}")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())

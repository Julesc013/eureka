"""Verify fixture-only snapshot artifacts offline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.snapshots.envelope import build_envelope_for_manifest
from runtime.snapshots.fixity import build_snapshot_fixity_report
from runtime.snapshots.manifest import ensure_allowed_input_path, ensure_allowed_output_path, load_json, load_snapshot_policy
from runtime.snapshots.signature import build_unsigned_signature_envelope
from runtime.snapshots.verify import build_snapshot_verification_report


def _load_optional(path: str | None) -> dict[str, Any]:
    return load_json(ensure_allowed_input_path(path)) if path else {}


def _write_json(path: str | None, payload: Mapping[str, Any], policy: Mapping[str, Any]) -> None:
    if not path:
        return
    output = ensure_allowed_output_path(path, policy)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(args: argparse.Namespace, policy: Mapping[str, Any]) -> dict[str, Any]:
    manifest = _load_optional(args.manifest)
    envelope = _load_optional(args.envelope)
    if not envelope and manifest:
        envelope = build_envelope_for_manifest(manifest, policy)
    fixity = _load_optional(args.fixity)
    if not fixity and envelope and manifest:
        fixity = build_snapshot_fixity_report(envelope, manifest, manifest.get("records", []), policy)
    signature = _load_optional(args.signature)
    if not signature and envelope:
        signature = build_unsigned_signature_envelope(envelope, policy)
    return build_snapshot_verification_report(
        {
            "envelope": envelope,
            "manifest": manifest,
            "fixity_report": fixity,
            "signature_envelope": signature,
            "render_results": [],
        },
        policy,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify a fixture-only snapshot bundle.")
    parser.add_argument("--envelope")
    parser.add_argument("--manifest")
    parser.add_argument("--fixity")
    parser.add_argument("--signature")
    parser.add_argument("--output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    if not any((args.envelope, args.manifest, args.fixity, args.signature)):
        parser.error("at least one snapshot artifact path is required")

    policy = load_snapshot_policy()
    report = build_report(args, policy)
    if not args.check:
        _write_json(args.output, report, policy)
    if args.as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"snapshot verification: {report['verification_status']}")
    return 0 if not report.get("blockers") else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - script boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)

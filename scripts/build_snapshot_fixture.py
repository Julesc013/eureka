"""Build fixture-only snapshot envelopes and manifests.

This script reads an explicit local snapshot fixture and creates offline
snapshot artifacts. It does not fetch sources, host routes, write site/dist,
or mutate indexes.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.snapshots.envelope import build_snapshot_envelope
from runtime.snapshots.fixity import build_snapshot_fixity_report
from runtime.snapshots.manifest import (
    build_snapshot_manifest,
    ensure_allowed_input_path,
    ensure_allowed_output_path,
    load_json,
    load_snapshot_policy,
)
from runtime.snapshots.signature import build_unsigned_signature_envelope
from runtime.snapshots.summaries import format_snapshot_summary, summarize_snapshot_bundle


def _records_from_input(payload: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    records = payload.get("records", [])
    if not isinstance(records, list):
        raise ValueError("snapshot input must contain a records list")
    return [record for record in records if isinstance(record, Mapping)]


def _write_json(path: str | None, payload: Mapping[str, Any], policy: Mapping[str, Any]) -> None:
    if not path:
        return
    output = ensure_allowed_output_path(path, policy)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: str | None, text: str, policy: Mapping[str, Any]) -> None:
    if not path:
        return
    output = ensure_allowed_output_path(path, policy)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")


def build_outputs(input_path: str, policy: Mapping[str, Any]) -> dict[str, Any]:
    payload = load_json(ensure_allowed_input_path(input_path))
    records = _records_from_input(payload)
    manifest = build_snapshot_manifest(records, policy)
    envelope = build_snapshot_envelope(records, policy)
    fixity = build_snapshot_fixity_report(envelope, manifest, manifest["records"], policy)
    signature = build_unsigned_signature_envelope(envelope, policy)
    summary = summarize_snapshot_bundle({"envelope": envelope, "manifest": manifest}, policy)
    return {
        "manifest": manifest,
        "envelope": envelope,
        "fixity": fixity,
        "signature": signature,
        "summary": summary,
        "summary_text": format_snapshot_summary(summary),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a fixture-only snapshot bundle.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--manifest-output")
    parser.add_argument("--envelope-output")
    parser.add_argument("--fixity-output")
    parser.add_argument("--signature-output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    policy = load_snapshot_policy()
    outputs = build_outputs(args.input, policy)
    if not args.check:
        _write_json(args.manifest_output, outputs["manifest"], policy)
        _write_json(args.envelope_output, outputs["envelope"], policy)
        _write_json(args.fixity_output, outputs["fixity"], policy)
        _write_json(args.signature_output, outputs["signature"], policy)
        _write_text(args.summary_output, outputs["summary_text"], policy)

    if args.as_json:
        print(json.dumps({key: value for key, value in outputs.items() if key != "summary_text"}, indent=2, sort_keys=True))
    else:
        print(outputs["summary_text"], end="")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - script boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)

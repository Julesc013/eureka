"""Render fixture-only snapshots as text, lite HTML, file-tree, or JSON manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.snapshots.manifest import build_snapshot_manifest, ensure_allowed_input_path, ensure_allowed_output_path, load_json, load_snapshot_policy
from runtime.snapshots.render_file_tree import render_snapshot_file_tree_index
from runtime.snapshots.render_lite_html import render_snapshot_lite_html
from runtime.snapshots.render_text import render_snapshot_text


def _manifest_from_input(path: str, policy: Mapping[str, Any]) -> dict[str, Any]:
    payload = load_json(ensure_allowed_input_path(path))
    if payload.get("schema_version") == "snapshot_manifest.v0":
        return payload
    records = payload.get("records", [])
    if not isinstance(records, list):
        raise ValueError("snapshot render input must be a manifest or contain a records list")
    return build_snapshot_manifest([record for record in records if isinstance(record, Mapping)], policy)


def _render(manifest: Mapping[str, Any], profile: str, policy: Mapping[str, Any]) -> tuple[Mapping[str, Any], str]:
    bundle = {"manifest": manifest}
    if profile == "text":
        result = render_snapshot_text(bundle, policy)
        return result, str(result["content"])
    if profile == "lite_html":
        result = render_snapshot_lite_html(bundle, policy)
        return result, str(result["content"])
    if profile == "file_tree":
        result = render_snapshot_file_tree_index(bundle, policy)
        return result, str(result["content"])
    if profile == "json_manifest":
        return manifest, json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    raise ValueError(f"unsupported render profile: {profile}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render a fixture-only snapshot.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--profile", required=True, choices=("text", "lite_html", "file_tree", "json_manifest"))
    parser.add_argument("--output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    policy = load_snapshot_policy()
    manifest = _manifest_from_input(args.input, policy)
    result, content = _render(manifest, args.profile, policy)
    if not args.check and args.output:
        output = ensure_allowed_output_path(args.output, policy)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")
    if args.as_json:
        payload = dict(result)
        payload.pop("content", None)
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(content, end="")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - script boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)

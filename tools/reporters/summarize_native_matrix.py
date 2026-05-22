#!/usr/bin/env python3
"""Summarize the native matrix without writing files unless explicitly asked."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
TOOLS_ROOT = SCRIPT_DIR.parents[0]
REPO_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(TOOLS_ROOT / "validators"))

from validate_native_matrix import load_toml_sections, validate_native_matrix  # noqa: E402

FORBIDDEN_OUTPUT_ROOTS = [
    "site/dist",
    "site/dist/data/public_index",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
    "control/inventory/publication",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", help="Optional JSON summary output path.")
    parser.add_argument("--summary-output", help="Optional Markdown summary output path.")
    parser.add_argument("--check", action="store_true", help="Validate and print summary without required writes.")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout.")
    args = parser.parse_args()

    summary = build_summary(REPO_ROOT)
    if summary["validation"]["status"] not in {"pass", "pass_with_warnings"}:
        print(json.dumps(summary, indent=2, sort_keys=True) if args.json else format_markdown(summary))
        return 1

    if args.output:
        output = _validate_output_path(args.output)
        output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.summary_output:
        output = _validate_output_path(args.summary_output)
        output.write_text(format_markdown(summary) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(format_markdown(summary))
    return 0


def build_summary(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    validation = validate_native_matrix(repo_root)
    native_sections = load_toml_sections(repo_root / "native" / "matrix" / "native.toml")
    artifact_sections = load_toml_sections(repo_root / "native" / "matrix" / "artifacts.toml")
    host_sections = load_toml_sections(repo_root / "native" / "matrix" / "hosts.toml")
    lanes = []
    for lane_id, lane in sorted(native_sections.items()):
        lanes.append(
            {
                "lane_id": lane_id,
                "path": lane.get("path"),
                "api": lane.get("api"),
                "toolchain": lane.get("toolchain"),
                "systems": lane.get("systems", []),
                "current_status": lane.get("current_status"),
                "support_tier": lane.get("support_tier"),
            }
        )
    return {
        "schema_version": "native_matrix_summary.v0",
        "status": validation["status"],
        "validation": validation,
        "lanes": lanes,
        "artifacts": sorted(artifact_sections),
        "hosts": sorted(host_sections),
        "scope": {
            "skeleton": "enabled",
            "matrix": "enabled",
            "c89_library": "enabled",
            "winforms_readonly_proof": "enabled",
            "downloads": False,
            "install": False,
            "execute": False,
            "telemetry": False,
        },
    }


def format_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Native Matrix Summary",
        "",
        f"Status: {summary['status']}",
        "",
        "## Lanes",
    ]
    for lane in summary["lanes"]:
        lines.append(f"- {lane['lane_id']}: {lane.get('api')} / {lane.get('toolchain')} ({lane.get('current_status')})")
    lines.extend(
        [
            "",
            "## Boundaries",
            "- Native clients consume snapshot, relay, action, and view contracts only.",
            "- Downloads, installs, execution, source sync, accounts, and telemetry remain disabled.",
            "- No release binaries or build outputs are produced by this summary.",
        ]
    )
    return "\n".join(lines)


def _validate_output_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = REPO_ROOT / path
    resolved = path.resolve()
    repo = REPO_ROOT.resolve()
    try:
        relative = resolved.relative_to(repo).as_posix()
    except ValueError:
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
        except ValueError as exc:
            raise SystemExit(f"Refusing output outside repository or temp directory: {raw_path}") from exc
    else:
        lower = relative.casefold()
        for forbidden in FORBIDDEN_OUTPUT_ROOTS:
            if lower == forbidden.casefold() or lower.startswith(forbidden.casefold().rstrip("/") + "/"):
                raise SystemExit(f"Refusing forbidden output path: {relative}")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


if __name__ == "__main__":
    raise SystemExit(main())

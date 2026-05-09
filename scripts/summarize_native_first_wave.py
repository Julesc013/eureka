#!/usr/bin/env python3
"""Summarize C-BUNDLE-02 first-wave native skeletons."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_OUTPUT_ROOTS = [
    "site/dist",
    "data/public_index",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
    "control/inventory/publication",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    summary = build_summary(REPO_ROOT)
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
    lanes = [
        {
            "lane_id": "win.win32",
            "api": "Win32 ANSI",
            "toolchain": "Visual C++ 6.0",
            "path": "native/win/win32",
            "build_evidence_status": "manual_build_required",
            "readonly": True,
        },
        {
            "lane_id": "mac.appkit",
            "api": "AppKit",
            "toolchain": "Xcode 9.x",
            "path": "native/mac/appkit",
            "build_evidence_status": "manual_build_required",
            "readonly": True,
        },
        {
            "lane_id": "mac.carbon",
            "api": "Carbon",
            "toolchain": "CodeWarrior Pro 8/9",
            "path": "native/mac/carbon",
            "build_evidence_status": "manual_build_required",
            "readonly": True,
        },
    ]
    return {
        "schema_version": "native_first_wave_summary.v0",
        "status": "pass",
        "lanes": lanes,
        "scope": {
            "win32_skeleton": "enabled",
            "appkit_skeleton": "enabled",
            "carbon_skeleton": "enabled",
            "swiftui_project": False,
            "win16_project": False,
            "winui_project": False,
            "downloads": False,
            "install": False,
            "execute": False,
            "telemetry": False,
            "build_outputs_committed": False,
        },
        "audit_ref": "control/audits/c-bundle-02-native-first-wave-skeletons-v0/",
    }


def format_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Native First-Wave Summary",
        "",
        f"Status: {summary['status']}",
        "",
        "## Lanes",
    ]
    for lane in summary["lanes"]:
        lines.append(f"- {lane['lane_id']}: {lane['api']} / {lane['toolchain']} ({lane['build_evidence_status']})")
    lines.extend(
        [
            "",
            "## Boundaries",
            "- Win32, AppKit, and Carbon skeletons are read-only fixture consumers.",
            "- Downloads, installs, execution, source sync, accounts, telemetry, and index mutation remain disabled.",
            "- Build evidence is manual/future; no build outputs or release binaries are committed.",
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

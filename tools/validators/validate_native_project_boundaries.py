#!/usr/bin/env python3
"""Scan C-BUNDLE-02 native skeletons for risky APIs and forbidden dependencies."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SCAN_ROOTS = [
    "native/win/win32/src",
    "native/win/win32/project",
    "native/win/win32/res",
    "native/mac/appkit/src",
    "native/mac/appkit/project",
    "native/mac/carbon/src",
    "native/mac/carbon/project",
]
TEXT_SUFFIXES = {".c", ".h", ".m", ".mm", ".rc", ".dsp", ".dsw", ".md", ".txt"}
FORBIDDEN_TOKENS = [
    "http://",
    "https://",
    "socket",
    "URLSession",
    "NSURLConnection",
    "WinINet",
    "URLDownloadToFile",
    "CreateProcess",
    "system(",
    "runtime/engine",
    "runtime/local_foundry",
    "runtime/search_quality",
    "runtime/connectors",
    "python_runtime",
    "source_connector",
    "public_index_mutation_allowed = true",
    "master_index_mutation_allowed = true",
    "login",
    "password",
]
CONTEXTUAL_TOKENS = [
    "ShellExecute"
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = validate_native_project_boundaries(REPO_ROOT)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(format_report(report))
    return 0 if report["status"] == "pass" else 1


def validate_native_project_boundaries(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    scanned_files: list[str] = []
    for root in SCAN_ROOTS:
        path = repo_root / root
        if not path.exists():
            errors.append(f"{root}: scan root is missing.")
            continue
        for file_path in path.rglob("*"):
            if file_path.is_dir() or file_path.suffix not in TEXT_SUFFIXES:
                continue
            relative = file_path.relative_to(repo_root).as_posix()
            scanned_files.append(relative)
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            _scan_text(relative, text, errors)
    return {
        "schema_version": "native_project_boundary_validation.v0",
        "status": "fail" if errors else "pass",
        "scanned_file_count": len(scanned_files),
        "scanned_files": scanned_files,
        "errors": errors,
    }


def _scan_text(relative: str, text: str, errors: list[str]) -> None:
    lower = text.casefold()
    for token in FORBIDDEN_TOKENS:
        if token.casefold() in lower:
            errors.append(f"{relative}: forbidden native boundary token {token!r}.")
    for token in CONTEXTUAL_TOKENS:
        index = lower.find(token.casefold())
        if index >= 0:
            context = lower[max(0, index - 80) : index + 120]
            if "blocked" not in context and "not used" not in context and "forbidden" not in context:
                errors.append(f"{relative}: risky token {token!r} lacks blocked-action context.")


def format_report(report: dict[str, Any]) -> str:
    lines = [
        "Native project boundary validation",
        f"status: {report['status']}",
        f"scanned_files: {report['scanned_file_count']}",
    ]
    for error in report["errors"]:
        lines.append(f"ERROR: {error}")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())

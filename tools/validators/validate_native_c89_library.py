#!/usr/bin/env python3
"""Validate the C89 native contract helper library."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
C89_ROOT = REPO_ROOT / "native" / "lib" / "c89"
REQUIRED_FILES = [
    "include/eu_status.h",
    "include/eu_snapshot.h",
    "include/eu_relay.h",
    "include/eu_action.h",
    "include/eu_string.h",
    "src/eu_status.c",
    "src/eu_snapshot.c",
    "src/eu_relay.c",
    "src/eu_action.c",
    "src/eu_string.c",
    "test/test_eu_c89_contracts.c",
]
C99_TOKENS = ["//", "stdint.h", "stdbool.h", "for (int ", "for(size_t ", "inline "]
FORBIDDEN_RUNTIME_TOKENS = [
    "socket",
    "connect(",
    "curl",
    "WinExec",
    "ShellExecute",
    "CreateProcess",
    "system(",
    "popen",
    "fopen",
    "CreateFile",
    "WinHttp",
    "InternetOpen",
]
REQUIRED_SYMBOLS = [
    "eu_status_is_ok",
    "eu_status_name",
    "eu_strnlen_c89",
    "eu_contains_token",
    "eu_copy_string",
    "eu_snapshot_has_manifest_marker",
    "eu_relay_status_is_readonly",
    "eu_action_manifest_is_blocked",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = validate_native_c89_library(REPO_ROOT)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(format_report(report))
    return 0 if report["status"] in {"pass", "pass_with_warnings"} else 1


def validate_native_c89_library(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    text_by_file: dict[str, str] = {}

    for relative in REQUIRED_FILES:
        path = repo_root / "native" / "lib" / "c89" / relative
        if not path.is_file():
            errors.append(f"native/lib/c89/{relative}: required C89 file is missing.")
            continue
        text_by_file[relative] = path.read_text(encoding="utf-8")

    _validate_static_tokens(text_by_file, errors)
    _validate_required_symbols(text_by_file, errors)
    compile_result = _try_compile(repo_root, warnings, errors)

    return {
        "schema_version": "native_c89_validation.v0",
        "status": "fail" if errors else ("pass_with_warnings" if warnings else "pass"),
        "file_count": len(text_by_file),
        "compile": compile_result,
        "errors": errors,
        "warnings": warnings,
    }


def _validate_static_tokens(text_by_file: dict[str, str], errors: list[str]) -> None:
    for relative, text in sorted(text_by_file.items()):
        for token in C99_TOKENS:
            if token in text:
                errors.append(f"native/lib/c89/{relative}: C99-only or old-compiler-hostile token {token!r}.")
        for token in FORBIDDEN_RUNTIME_TOKENS:
            if token in text:
                errors.append(f"native/lib/c89/{relative}: forbidden runtime token {token!r}.")


def _validate_required_symbols(text_by_file: dict[str, str], errors: list[str]) -> None:
    combined = "\n".join(text_by_file.values())
    for symbol in REQUIRED_SYMBOLS:
        if symbol not in combined:
            errors.append(f"native/lib/c89: missing required symbol {symbol}.")


def _try_compile(repo_root: Path, warnings: list[str], errors: list[str]) -> dict[str, Any]:
    compiler = shutil.which("gcc") or shutil.which("clang") or shutil.which("cc")
    if compiler is None:
        warnings.append("No C compiler found; static C89 validation completed without compile.")
        return {"attempted": False, "passed": False, "reason": "compiler_unavailable"}
    with tempfile.TemporaryDirectory(prefix="eureka_c89_") as temp_dir:
        output = Path(temp_dir) / "test_eu_c89_contracts"
        command = [
            compiler,
            "-std=c89",
            "-pedantic",
            "-Wall",
            "-Werror",
            "-I",
            str(repo_root / "native" / "lib" / "c89" / "include"),
            str(repo_root / "native" / "lib" / "c89" / "src" / "eu_status.c"),
            str(repo_root / "native" / "lib" / "c89" / "src" / "eu_string.c"),
            str(repo_root / "native" / "lib" / "c89" / "src" / "eu_snapshot.c"),
            str(repo_root / "native" / "lib" / "c89" / "src" / "eu_relay.c"),
            str(repo_root / "native" / "lib" / "c89" / "src" / "eu_action.c"),
            str(repo_root / "native" / "lib" / "c89" / "test" / "test_eu_c89_contracts.c"),
            "-o",
            str(output),
        ]
        result = subprocess.run(command, cwd=repo_root, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            errors.append("native/lib/c89: optional local C89 compile failed.")
            return {
                "attempted": True,
                "passed": False,
                "compiler": compiler,
                "stderr": result.stderr[-1000:],
            }
        return {"attempted": True, "passed": True, "compiler": compiler}


def format_report(report: dict[str, Any]) -> str:
    lines = [
        "Native C89 library validation",
        f"status: {report['status']}",
        f"files: {report['file_count']}",
        f"compile_attempted: {report['compile'].get('attempted')}",
        f"compile_passed: {report['compile'].get('passed')}",
    ]
    for error in report["errors"]:
        lines.append(f"ERROR: {error}")
    for warning in report["warnings"]:
        lines.append(f"WARN: {warning}")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())

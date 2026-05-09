#!/usr/bin/env python3
"""Validate the C-BUNDLE-01 native directory and WinForms skeleton."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = REPO_ROOT / "control" / "inventory" / "native" / "native_directory_policy.json"
PROJECT_ALLOWLIST = {
    "native/win/winforms/project/Eureka.sln",
    "native/win/winforms/src/Eureka/Eureka.csproj",
    "native/win/win32/project/Eureka.dsw",
    "native/win/win32/project/Eureka.dsp",
    "native/mac/appkit/project/Eureka.xcodeproj",
}
PROJECT_SUFFIXES = {".sln", ".dsw", ".dsp", ".vcxproj", ".csproj", ".xcodeproj", ".xcworkspace", ".pbxproj"}
BINARY_SUFFIXES = {".exe", ".dll", ".pdb", ".obj", ".o", ".a", ".lib", ".dylib", ".so", ".app", ".msi"}
FORBIDDEN_API_TOKENS = {
    "System.Net",
    "HttpClient",
    "WebClient",
    "WebRequest",
    "DownloadFile",
    "UploadFile",
    "Process.Start",
    "File.Write",
    "Registry.",
    "TelemetryClient",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = validate_native_skeleton(REPO_ROOT)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(format_report(report))
    return 0 if report["status"] == "pass" else 1


def validate_native_skeleton(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    policy = _load_json(POLICY_PATH, errors)
    required_dirs = policy.get("required_directories", [])
    required_readmes = policy.get("required_readmes", [])

    for relative in required_dirs:
        if not (repo_root / relative).is_dir():
            errors.append(f"{relative}: required native directory is missing.")
    for relative in required_readmes:
        if not (repo_root / relative).is_file():
            errors.append(f"{relative}: required README is missing.")

    for relative in sorted(PROJECT_ALLOWLIST):
        path = repo_root / relative
        if relative.endswith(".xcodeproj"):
            if not path.is_dir():
                errors.append(f"{relative}: governed AppKit project placeholder directory is missing.")
        elif not path.is_file():
            errors.append(f"{relative}: governed native project file is missing.")

    _validate_project_files(repo_root, errors)
    _validate_no_build_outputs(repo_root, errors)
    _validate_no_forbidden_apis(repo_root, errors)
    _validate_no_private_roots(repo_root, errors)

    return {
        "schema_version": "native_skeleton_validation.v0",
        "status": "fail" if errors else "pass",
        "required_directory_count": len(required_dirs),
        "required_readme_count": len(required_readmes),
        "allowed_project_files": sorted(PROJECT_ALLOWLIST),
        "errors": errors,
    }


def _validate_project_files(repo_root: Path, errors: list[str]) -> None:
    for path in repo_root.rglob("*"):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        if path.suffix.casefold() in PROJECT_SUFFIXES:
            relative = path.relative_to(repo_root).as_posix()
            if relative not in PROJECT_ALLOWLIST:
                errors.append(f"{relative}: native project file is outside the governed native project allowlist.")


def _validate_no_build_outputs(repo_root: Path, errors: list[str]) -> None:
    native_root = repo_root / "native"
    for path in native_root.rglob("*"):
        relative = path.relative_to(repo_root).as_posix()
        if path.is_dir() and path.name.casefold() in {"bin", "obj"}:
            errors.append(f"{relative}: build output directory must not be committed.")
        if path.is_file() and path.suffix.casefold() in BINARY_SUFFIXES:
            if path.name == "README.md":
                continue
            errors.append(f"{relative}: native binary/build output must not be committed.")


def _validate_no_forbidden_apis(repo_root: Path, errors: list[str]) -> None:
    source_root = repo_root / "native" / "win" / "winforms" / "src"
    if not source_root.exists():
        return
    for path in source_root.rglob("*.cs"):
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN_API_TOKENS:
            if token in text:
                errors.append(f"{path.relative_to(repo_root).as_posix()}: forbidden WinForms API token {token!r}.")


def _validate_no_private_roots(repo_root: Path, errors: list[str]) -> None:
    for relative in [".aide.local", ".local/eureka", ".cache/eureka"]:
        if (repo_root / relative).exists():
            errors.append(f"{relative}: local private-state root must not be created.")


def _load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{path.relative_to(REPO_ROOT).as_posix()}: missing JSON file.")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"{path.relative_to(REPO_ROOT).as_posix()}: invalid JSON: {exc}.")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"{path.relative_to(REPO_ROOT).as_posix()}: must be a JSON object.")
        return {}
    return payload


def format_report(report: dict[str, Any]) -> str:
    lines = [
        "Native skeleton validation",
        f"status: {report['status']}",
        f"required_directories: {report['required_directory_count']}",
        f"required_readmes: {report['required_readme_count']}",
    ]
    for error in report["errors"]:
        lines.append(f"ERROR: {error}")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())

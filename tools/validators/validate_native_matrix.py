#!/usr/bin/env python3
"""Validate the C-BUNDLE-01 native matrix without building native artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - exercised only on older Python.
    tomllib = None

REPO_ROOT = Path(__file__).resolve().parents[2]
MATRIX_ROOT = REPO_ROOT / "native" / "matrix"

REQUIRED_FIRST_WAVE = {"mac.carbon", "mac.appkit", "win.win32", "win.winforms"}
REQUIRED_FUTURE = {"mac.swiftui", "win.win16", "win.winui"}
REQUIRED_LIBS = {"lib.c89", "lib.objc", "lib.dotnet"}
ALLOWED_CONSUMES = {
    "snapshot",
    "relay",
    "action_manifest",
    "view_contracts",
    "citation_bundle",
    "export_manifest",
    "acquisition_manifest",
}
FORBIDDEN_NATIVE_DEPENDENCIES = {
    "python_runtime",
    "runtime_python_internals",
    "runtime/engine",
    "runtime/local_foundry",
    "runtime/search_quality",
    "runtime/relay",
    "source_connector",
    "live_source",
}
FORBIDDEN_DIRECTORY_NAMES = {
    "legacy",
    "modern",
    "classic",
    "old",
    "new",
    "universal",
    "desktop",
    "lite",
    "historical",
    "retro-client",
    "experimental_as_primary_name",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    args = parser.parse_args()
    report = validate_native_matrix(REPO_ROOT)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(format_report(report))
    return 0 if report["status"] in {"pass", "pass_with_warnings"} else 1


def validate_native_matrix(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    native_sections = load_toml_sections(repo_root / "native" / "matrix" / "native.toml", errors)
    artifact_sections = load_toml_sections(repo_root / "native" / "matrix" / "artifacts.toml", errors)
    host_sections = load_toml_sections(repo_root / "native" / "matrix" / "hosts.toml", errors)
    required_lanes = REQUIRED_FIRST_WAVE | REQUIRED_FUTURE | REQUIRED_LIBS

    missing = sorted(required_lanes - set(native_sections))
    if missing:
        errors.append(f"native/matrix/native.toml: missing lanes {missing}.")

    for lane_id in sorted(required_lanes & set(native_sections)):
        lane = native_sections[lane_id]
        _validate_lane(repo_root, lane_id, lane, errors)

    for artifact_id, artifact in sorted(artifact_sections.items()):
        if bool(artifact.get("produced_current")):
            errors.append(f"native/matrix/artifacts.toml:{artifact_id}: produced_current must be false.")
        if bool(artifact.get("production_release_current")):
            errors.append(f"native/matrix/artifacts.toml:{artifact_id}: production_release_current must be false.")

    required_hosts = {
        "host.vs2022",
        "host.vs6_future",
        "host.xcode9_future",
        "host.codewarrior9_future",
        "host.appkit_future",
        "host.carbon_future",
    }
    missing_hosts = sorted(required_hosts - set(host_sections))
    if missing_hosts:
        errors.append(f"native/matrix/hosts.toml: missing hosts {missing_hosts}.")

    _validate_forbidden_directory_names(repo_root, errors)

    return {
        "schema_version": "native_matrix_validation.v0",
        "status": "fail" if errors else ("pass_with_warnings" if warnings else "pass"),
        "lane_count": len(native_sections),
        "artifact_count": len(artifact_sections),
        "host_count": len(host_sections),
        "first_wave_lanes": sorted(REQUIRED_FIRST_WAVE),
        "future_lanes": sorted(REQUIRED_FUTURE),
        "native_library_lanes": sorted(REQUIRED_LIBS),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_lane(repo_root: Path, lane_id: str, lane: dict[str, Any], errors: list[str]) -> None:
    path_value = str(lane.get("path", ""))
    path = repo_root / path_value
    if not path_value:
        errors.append(f"native/matrix/native.toml:{lane_id}: missing path.")
    elif not path.exists():
        errors.append(f"native/matrix/native.toml:{lane_id}: path does not exist: {path_value}.")

    consumes = _as_string_list(lane.get("consumes"))
    unknown_consumes = sorted(set(consumes) - ALLOWED_CONSUMES)
    if unknown_consumes:
        errors.append(f"native/matrix/native.toml:{lane_id}: unsupported consumes {unknown_consumes}.")

    lane_text = json.dumps(lane, sort_keys=True).casefold()
    for forbidden in FORBIDDEN_NATIVE_DEPENDENCIES:
        if forbidden.casefold() in lane_text and forbidden not in _as_string_list(lane.get("must_not_consume")):
            errors.append(f"native/matrix/native.toml:{lane_id}: must not depend on {forbidden}.")

    if lane_id in REQUIRED_FIRST_WAVE and not str(lane.get("current_status", "")):
        errors.append(f"native/matrix/native.toml:{lane_id}: missing current_status.")


def _validate_forbidden_directory_names(repo_root: Path, errors: list[str]) -> None:
    native_root = repo_root / "native"
    if not native_root.exists():
        errors.append("native/: missing native directory.")
        return
    for path in native_root.rglob("*"):
        if path.is_dir() and path.name.casefold() in FORBIDDEN_DIRECTORY_NAMES:
            errors.append(f"{path.relative_to(repo_root).as_posix()}: forbidden native directory name.")


def load_toml_sections(path: Path, errors: list[str] | None = None) -> dict[str, dict[str, Any]]:
    if errors is None:
        errors = []
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        errors.append(f"{path.relative_to(REPO_ROOT).as_posix()}: missing TOML file.")
        return {}
    if tomllib is not None:
        try:
            data = tomllib.loads(raw.decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - validator reports parser details.
            errors.append(f"{path.relative_to(REPO_ROOT).as_posix()}: invalid TOML: {exc}.")
            return {}
        return flatten_toml_sections(data)
    return parse_tiny_toml(raw.decode("utf-8"), path, errors)


def flatten_toml_sections(data: dict[str, Any], prefix: str = "") -> dict[str, dict[str, Any]]:
    sections: dict[str, dict[str, Any]] = {}
    scalar_seen = False
    for value in data.values():
        if not isinstance(value, dict):
            scalar_seen = True
            break
    if prefix and scalar_seen:
        sections[prefix] = dict(data)
        return sections
    for key, value in data.items():
        child_prefix = key if not prefix else f"{prefix}.{key}"
        if isinstance(value, dict):
            sections.update(flatten_toml_sections(value, child_prefix))
    return sections


def parse_tiny_toml(text: str, path: Path, errors: list[str]) -> dict[str, dict[str, Any]]:
    sections: dict[str, dict[str, Any]] = {}
    current: dict[str, Any] | None = None
    for line_number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("[") and stripped.endswith("]"):
            name = stripped[1:-1].strip()
            current = {}
            sections[name] = current
            continue
        if current is None or "=" not in stripped:
            errors.append(f"{path.relative_to(REPO_ROOT).as_posix()}:{line_number}: unsupported TOML line.")
            continue
        key, raw_value = stripped.split("=", 1)
        current[key.strip()] = _parse_tiny_value(raw_value.strip())
    return sections


def _parse_tiny_value(raw: str) -> Any:
    if raw in {"true", "false"}:
        return raw == "true"
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [part.strip().strip('"') for part in inner.split(",")]
    return raw.strip('"')


def _as_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def format_report(report: dict[str, Any]) -> str:
    lines = [
        "Native matrix validation",
        f"status: {report['status']}",
        f"lanes: {report['lane_count']}",
        f"artifacts: {report['artifact_count']}",
        f"hosts: {report['host_count']}",
    ]
    for error in report["errors"]:
        lines.append(f"ERROR: {error}")
    for warning in report["warnings"]:
        lines.append(f"WARN: {warning}")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())

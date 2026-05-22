#!/usr/bin/env python3
"""Validate C-BUNDLE-02 Win32, AppKit, and Carbon native skeletons."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "native/win/win32/README.md",
    "native/win/win32/project/Eureka.dsw",
    "native/win/win32/project/Eureka.dsp",
    "native/win/win32/src/app/main.c",
    "native/win/win32/src/app/eu_win32_app.h",
    "native/win/win32/src/app/eu_win32_app.c",
    "native/win/win32/src/ui/eu_win32_main_window.h",
    "native/win/win32/src/ui/eu_win32_main_window.c",
    "native/win/win32/src/ui/eu_win32_dialogs.h",
    "native/win/win32/src/ui/eu_win32_dialogs.c",
    "native/win/win32/src/contract/eu_win32_snapshot_adapter.h",
    "native/win/win32/src/contract/eu_win32_snapshot_adapter.c",
    "native/win/win32/src/contract/eu_win32_relay_adapter.h",
    "native/win/win32/src/contract/eu_win32_relay_adapter.c",
    "native/win/win32/res/Eureka.rc",
    "native/win/win32/res/resource.h",
    "native/win/win32/build/README.md",
    "native/win/win32/test/README.md",
    "native/win/win32/dist/README.md",
    "native/mac/appkit/README.md",
    "native/mac/appkit/project/Eureka.xcodeproj/README.md",
    "native/mac/appkit/src/App/EurekaAppDelegate.h",
    "native/mac/appkit/src/App/EurekaAppDelegate.m",
    "native/mac/appkit/src/App/main.m",
    "native/mac/appkit/src/UI/EurekaMainWindowController.h",
    "native/mac/appkit/src/UI/EurekaMainWindowController.m",
    "native/mac/appkit/src/UI/EurekaReadOnlySearchView.h",
    "native/mac/appkit/src/UI/EurekaReadOnlySearchView.m",
    "native/mac/appkit/src/Contract/EurekaSnapshotAdapter.h",
    "native/mac/appkit/src/Contract/EurekaSnapshotAdapter.m",
    "native/mac/appkit/src/Contract/EurekaRelayAdapter.h",
    "native/mac/appkit/src/Contract/EurekaRelayAdapter.m",
    "native/mac/appkit/res/README.md",
    "native/mac/appkit/build/README.md",
    "native/mac/appkit/test/README.md",
    "native/mac/appkit/dist/README.md",
    "native/mac/carbon/README.md",
    "native/mac/carbon/project/Eureka.mcp.README.md",
    "native/mac/carbon/src/app/main.c",
    "native/mac/carbon/src/app/eu_carbon_app.h",
    "native/mac/carbon/src/app/eu_carbon_app.c",
    "native/mac/carbon/src/ui/eu_carbon_window.h",
    "native/mac/carbon/src/ui/eu_carbon_window.c",
    "native/mac/carbon/src/contract/eu_carbon_snapshot_adapter.h",
    "native/mac/carbon/src/contract/eu_carbon_snapshot_adapter.c",
    "native/mac/carbon/src/contract/eu_carbon_relay_adapter.h",
    "native/mac/carbon/src/contract/eu_carbon_relay_adapter.c",
    "native/mac/carbon/rsrc/README.md",
    "native/mac/carbon/build/README.md",
    "native/mac/carbon/test/README.md",
    "native/mac/carbon/dist/README.md",
]
REQUIRED_POLICIES = [
    "control/inventory/native/native_win32_policy.json",
    "control/inventory/native/native_appkit_policy.json",
    "control/inventory/native/native_carbon_policy.json",
    "control/inventory/native/native_project_skeleton_policy.json",
    "control/inventory/native/native_manual_build_policy.json",
    "control/inventory/native/native_smoke_checklist_policy.json",
    "control/inventory/native/native_first_wave_boundary_policy.json",
]
FUTURE_PROJECT_ROOTS = [
    "native/mac/swiftui",
    "native/win/win16",
    "native/win/winui",
]
PROJECT_SUFFIXES = {".sln", ".dsw", ".dsp", ".vcxproj", ".csproj", ".xcodeproj", ".xcworkspace", ".pbxproj", ".mcp"}
BINARY_SUFFIXES = {".exe", ".dll", ".pdb", ".obj", ".o", ".a", ".lib", ".dylib", ".so", ".app", ".msi", ".pkg"}
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
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = validate_native_first_wave_skeletons(REPO_ROOT)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(format_report(report))
    return 0 if report["status"] == "pass" else 1


def validate_native_first_wave_skeletons(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    _validate_required_files(repo_root, errors)
    _validate_required_policies(repo_root, errors)
    _validate_no_future_lane_projects(repo_root, errors)
    _validate_no_build_outputs(repo_root, errors)
    _validate_no_forbidden_directories(repo_root, errors)
    _validate_policy_boundaries(repo_root, errors)
    _validate_no_private_roots(repo_root, errors)
    return {
        "schema_version": "native_first_wave_skeleton_validation.v0",
        "status": "fail" if errors else "pass",
        "required_file_count": len(REQUIRED_FILES),
        "required_policy_count": len(REQUIRED_POLICIES),
        "lanes": ["win.win32", "mac.appkit", "mac.carbon"],
        "errors": errors,
    }


def _validate_required_files(repo_root: Path, errors: list[str]) -> None:
    for relative in REQUIRED_FILES:
        if not (repo_root / relative).is_file():
            errors.append(f"{relative}: required first-wave skeleton file is missing.")


def _validate_required_policies(repo_root: Path, errors: list[str]) -> None:
    for relative in REQUIRED_POLICIES:
        if not (repo_root / relative).is_file():
            errors.append(f"{relative}: required first-wave native policy is missing.")


def _validate_no_future_lane_projects(repo_root: Path, errors: list[str]) -> None:
    for root in FUTURE_PROJECT_ROOTS:
        path = repo_root / root
        if not path.exists():
            continue
        for child in path.rglob("*"):
            if child.suffix.casefold() in PROJECT_SUFFIXES:
                errors.append(f"{child.relative_to(repo_root).as_posix()}: future-lane project file is not allowed in C-BUNDLE-02.")


def _validate_no_build_outputs(repo_root: Path, errors: list[str]) -> None:
    native_root = repo_root / "native"
    for path in native_root.rglob("*"):
        relative = path.relative_to(repo_root).as_posix()
        if path.is_dir() and path.name.casefold() in {"bin", "obj", "deriveddata"}:
            errors.append(f"{relative}: native build output directory must not be committed.")
        if path.is_file() and path.suffix.casefold() in BINARY_SUFFIXES:
            errors.append(f"{relative}: native binary or package must not be committed.")


def _validate_no_forbidden_directories(repo_root: Path, errors: list[str]) -> None:
    native_root = repo_root / "native"
    for path in native_root.rglob("*"):
        if path.is_dir() and path.name.casefold() in FORBIDDEN_DIRECTORY_NAMES:
            errors.append(f"{path.relative_to(repo_root).as_posix()}: forbidden native directory name.")


def _validate_policy_boundaries(repo_root: Path, errors: list[str]) -> None:
    policy_path = repo_root / "control" / "inventory" / "native" / "native_first_wave_boundary_policy.json"
    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append("control/inventory/native/native_first_wave_boundary_policy.json: missing policy.")
        return
    for key in (
        "live_source_access_allowed",
        "download_allowed",
        "install_allowed",
        "execute_allowed",
        "emulate_allowed",
        "account_auth_allowed",
        "telemetry_allowed",
        "public_index_mutation_allowed",
        "master_index_mutation_allowed",
        "python_runtime_internal_dependency_allowed",
        "connector_runtime_dependency_allowed",
        "accepted_truth_creation_allowed",
        "release_binaries_allowed",
        "build_outputs_committed_allowed",
    ):
        if policy.get(key) is not False:
            errors.append(f"native_first_wave_boundary_policy.json: {key} must be false.")
    for key in ("win32_readonly", "appkit_readonly", "carbon_readonly"):
        if policy.get(key) is not True:
            errors.append(f"native_first_wave_boundary_policy.json: {key} must be true.")


def _validate_no_private_roots(repo_root: Path, errors: list[str]) -> None:
    for relative in [".aide.local", ".local/eureka", ".cache/eureka"]:
        if (repo_root / relative).exists():
            errors.append(f"{relative}: local private-state root must not be created.")


def format_report(report: dict[str, Any]) -> str:
    lines = [
        "Native first-wave skeleton validation",
        f"status: {report['status']}",
        f"required_files: {report['required_file_count']}",
        f"required_policies: {report['required_policy_count']}",
    ]
    for error in report["errors"]:
        lines.append(f"ERROR: {error}")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())

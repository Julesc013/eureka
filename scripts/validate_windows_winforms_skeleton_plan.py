from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
PLAN_DIR = REPO_ROOT / "control" / "audits" / "windows-7-winforms-native-skeleton-planning-v0"
PLAN_JSON = PLAN_DIR / "winforms_skeleton_plan.json"
READINESS_REPORT = (
    REPO_ROOT
    / "control"
    / "audits"
    / "native-client-project-readiness-v0"
    / "native_readiness_report.json"
)

REQUIRED_FILES = {
    "README.md",
    "SCOPE.md",
    "PROJECT_LAYOUT_DECISION.md",
    "NAMESPACE_DECISION.md",
    "BUILD_HOST_REQUIREMENTS.md",
    "ALLOWED_INITIAL_FEATURES.md",
    "PROHIBITED_INITIAL_FEATURES.md",
    "DATA_INPUTS.md",
    "UI_BOUNDARY.md",
    "TEST_PLAN.md",
    "APPROVAL_GATE.md",
    "RISKS.md",
    "NEXT_IMPLEMENTATION_PROMPT_REQUIREMENTS.md",
    "winforms_skeleton_plan.json",
}

PROJECT_SUFFIXES = {
    ".sln",
    ".csproj",
    ".cs",
    ".resx",
    ".vcxproj",
    ".xcodeproj",
    ".xcworkspace",
    ".pbxproj",
}

REQUIRED_PROHIBITIONS = {
    "downloads",
    "installers",
    "local cache runtime",
    "telemetry",
    "accounts",
    "live backend dependency",
    "Rust FFI",
    "relay runtime",
}

REQUIRED_BUILD_REQUIREMENTS = {
    "Windows host",
    "Visual Studio 2022",
    ".NET Framework 4.8 targeting pack or developer pack",
    "x64 build target",
    "Windows 7 SP1+ x64 runtime compatibility verification",
}

FORBIDDEN_ABSOLUTE_PATH_PATTERNS = (
    re.compile(r"[A-Za-z]:\\"),
    re.compile(r"/Users/"),
    re.compile(r"/home/"),
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Windows 7 WinForms Native Skeleton Planning v0."
    )
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_windows_winforms_skeleton_plan(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_windows_winforms_skeleton_plan(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    plan_dir = repo_root / "control" / "audits" / "windows-7-winforms-native-skeleton-planning-v0"
    plan_json = plan_dir / "winforms_skeleton_plan.json"
    readiness_json = (
        repo_root
        / "control"
        / "audits"
        / "native-client-project-readiness-v0"
        / "native_readiness_report.json"
    )
    plan = _load_json(plan_json, repo_root, errors)
    readiness = _load_json(readiness_json, repo_root, errors)
    project_files = _find_native_project_files(repo_root)

    _validate_files(plan_dir, errors)
    _validate_plan(plan, readiness, errors)
    _validate_markdown(plan_dir, errors)
    _validate_no_project_files(project_files, errors)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "windows_winforms_skeleton_plan_validator_v0",
        "plan_dir": "control/audits/windows-7-winforms-native-skeleton-planning-v0",
        "plan_id": _mapping(plan).get("plan_id"),
        "lane_id": _mapping(_mapping(plan).get("lane")).get("lane_id"),
        "proposed_project_path": _mapping(plan).get("proposed_project_path"),
        "proposed_namespace": _mapping(plan).get("proposed_namespace"),
        "human_approval_required": _mapping(plan).get(
            "human_approval_required_before_implementation"
        ),
        "native_project_file_count": len(project_files),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_files(plan_dir: Path, errors: list[str]) -> None:
    if not plan_dir.is_dir():
        errors.append("control/audits/windows-7-winforms-native-skeleton-planning-v0: missing plan directory.")
        return
    present = {path.name for path in plan_dir.iterdir() if path.is_file()}
    missing = sorted(REQUIRED_FILES - present)
    if missing:
        errors.append(f"Windows WinForms skeleton planning pack: missing files {missing}.")


def _validate_plan(plan: Any, readiness: Any, errors: list[str]) -> None:
    if not isinstance(plan, Mapping):
        errors.append("winforms_skeleton_plan.json: must be a JSON object.")
        return

    expected_scalars = {
        "plan_id": "windows_7_winforms_native_skeleton_planning_v0",
        "created_by_slice": "windows_7_winforms_native_skeleton_planning_v0",
        "status": "planning_only",
        "implementation_started": False,
        "human_approval_required_before_implementation": True,
        "proposed_project_path": "clients/windows/winforms-net48/",
        "proposed_namespace": "Eureka.Clients.Windows.WinForms",
        "project_path_created": False,
        "visual_studio_solution_created": False,
        "csproj_created": False,
        "csharp_source_created": False,
    }
    for key, expected in expected_scalars.items():
        if plan.get(key) != expected:
            errors.append(f"winforms_skeleton_plan.json: {key} must be {expected!r}.")

    dependency = _mapping(plan.get("readiness_dependency"))
    if dependency.get("decision") != "ready_for_minimal_project_skeleton_after_human_approval":
        errors.append("winforms_skeleton_plan.json: readiness dependency decision must match P17.")
    if dependency.get("first_candidate_lane") != "windows_7_x64_winforms_net48":
        errors.append("winforms_skeleton_plan.json: readiness dependency must reference windows_7_x64_winforms_net48.")
    if _mapping(readiness).get("decision") != dependency.get("decision"):
        errors.append("winforms_skeleton_plan.json: readiness dependency does not match native readiness report.")

    lane = _mapping(plan.get("lane"))
    expected_lane = {
        "lane_id": "windows_7_x64_winforms_net48",
        "target_os": "Windows 7 SP1+ x64",
        "ui_stack": "WinForms",
        "framework": ".NET Framework 4.8",
        "toolchain": "Visual Studio 2022",
        "architecture": "x64",
    }
    for key, expected in expected_lane.items():
        if lane.get(key) != expected:
            errors.append(f"winforms_skeleton_plan.json: lane.{key} must be {expected!r}.")

    scope = _mapping(plan.get("initial_scope"))
    for flag in ("read_only", "demo_only", "no_network_by_default"):
        if scope.get(flag) is not True:
            errors.append(f"winforms_skeleton_plan.json: initial_scope.{flag} must be true.")
    for flag in (
        "live_backend_required",
        "live_probes_enabled",
        "downloads_enabled",
        "installers_enabled",
        "cache_runtime_enabled",
        "telemetry_enabled",
        "accounts_enabled",
        "private_file_scanning_enabled",
        "rust_ffi_enabled",
        "relay_runtime_enabled",
    ):
        if scope.get(flag) is not False:
            errors.append(f"winforms_skeleton_plan.json: initial_scope.{flag} must be false.")

    prohibited = {str(item) for item in _list(plan.get("prohibited_initial_features"))}
    missing = sorted(REQUIRED_PROHIBITIONS - prohibited)
    if missing:
        errors.append(f"winforms_skeleton_plan.json: prohibited_initial_features missing {missing}.")

    build = {str(item) for item in _list(plan.get("build_host_requirements"))}
    missing_build = sorted(REQUIRED_BUILD_REQUIREMENTS - build)
    if missing_build:
        errors.append(f"winforms_skeleton_plan.json: build_host_requirements missing {missing_build}.")

    gates = _lower_join(plan.get("validation_gates_before_implementation"))
    for phrase in (
        "explicit human approval",
        "confirm proposed project path",
        "confirm proposed namespace",
        "confirm visual studio 2022 availability",
        "confirm .net framework 4.8 developer pack availability",
        "confirm read-only demo-only scope",
    ):
        if phrase not in gates:
            errors.append(f"winforms_skeleton_plan.json: validation gates missing {phrase!r}.")

    serialized = json.dumps(plan, sort_keys=True)
    for pattern in FORBIDDEN_ABSOLUTE_PATH_PATTERNS:
        if pattern.search(serialized):
            errors.append("winforms_skeleton_plan.json: must not include volatile absolute local paths.")


def _validate_markdown(plan_dir: Path, errors: list[str]) -> None:
    expected = {
        "PROJECT_LAYOUT_DECISION.md": [
            "clients/windows/winforms-net48/",
            "No directory is created by this milestone",
        ],
        "NAMESPACE_DECISION.md": [
            "Eureka.Clients.Windows.WinForms",
            "No C# namespace or source file is created",
        ],
        "BUILD_HOST_REQUIREMENTS.md": [
            "Visual Studio 2022",
            ".NET Framework 4.8",
            "Windows 7 SP1+ x64",
            "no network/live backend",
        ],
        "APPROVAL_GATE.md": [
            "Human approval is required before any implementation",
            "Unsigned or implicit approval is not sufficient",
        ],
        "PROHIBITED_INITIAL_FEATURES.md": [
            "downloads",
            "installers",
            "local cache runtime",
            "telemetry",
            "live backend dependency",
            "Rust FFI",
            "relay runtime",
        ],
    }
    for filename, phrases in expected.items():
        path = plan_dir / filename
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{path.name}: missing phrase {phrase!r}.")


def _validate_no_project_files(project_files: list[str], errors: list[str]) -> None:
    for path in project_files:
        errors.append(f"{path}: native project/source file is not allowed in planning-only milestone.")


def _find_native_project_files(repo_root: Path) -> list[str]:
    offenders: list[str] = []
    ignored_parts = {".git", "__pycache__"}
    for path in repo_root.rglob("*"):
        if any(part in ignored_parts for part in path.parts):
            continue
        suffix = path.suffix.casefold()
        if suffix in PROJECT_SUFFIXES:
            offenders.append(_display_path(path, repo_root))
    return sorted(offenders)


def _load_json(path: Path, repo_root: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_display_path(path, repo_root)}: missing JSON file.")
    except json.JSONDecodeError as exc:
        errors.append(f"{_display_path(path, repo_root)}: invalid JSON at line {exc.lineno}: {exc.msg}.")
    return None


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Windows 7 WinForms skeleton plan validation",
        f"status: {report['status']}",
        f"plan_id: {report.get('plan_id')}",
        f"lane_id: {report.get('lane_id')}",
        f"proposed_project_path: {report.get('proposed_project_path')}",
        f"proposed_namespace: {report.get('proposed_namespace')}",
        f"human_approval_required: {report.get('human_approval_required')}",
        f"native_project_files: {report.get('native_project_file_count')}",
    ]
    for key in ("errors", "warnings"):
        values = _list(report.get(key))
        if values:
            lines.append(f"{key}:")
            lines.extend(f"- {value}" for value in values)
    return "\n".join(lines) + "\n"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _lower_join(value: Any) -> str:
    return " ".join(str(item).casefold() for item in _list(value))


def _display_path(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())


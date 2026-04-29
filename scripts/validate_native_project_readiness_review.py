from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_DIR = REPO_ROOT / "control" / "audits" / "native-client-project-readiness-v0"
REPORT_PATH = REVIEW_DIR / "native_readiness_report.json"
LANES_PATH = REPO_ROOT / "control" / "inventory" / "publication" / "native_client_lanes.json"

REQUIRED_REVIEW_FILES = {
    "README.md",
    "CURRENT_STATE.md",
    "CONTRACT_COVERAGE.md",
    "LANE_READINESS.md",
    "RISK_REGISTER.md",
    "READINESS_DECISION.md",
    "PRE_NATIVE_CHECKLIST.md",
    "NEXT_STEPS.md",
    "native_readiness_report.json",
}

ALLOWED_DECISIONS = {
    "not_ready",
    "ready_for_design_only",
    "ready_for_minimal_project_skeleton_after_human_approval",
    "ready_for_prototype",
}

PROJECT_SUFFIXES = {
    ".sln",
    ".vcxproj",
    ".csproj",
    ".xcodeproj",
    ".xcworkspace",
    ".pbxproj",
}

REQUIRED_REPORT_FIELDS = {
    "report_id",
    "created_by_slice",
    "decision",
    "first_candidate_lane",
    "human_approval_required",
    "contract_coverage",
    "lane_readiness",
    "blockers",
    "required_before_project_creation",
    "prohibited_initial_scope",
    "recommended_next_milestone",
    "notes",
}

REQUIRED_PROHIBITED_SCOPE = {
    "downloads",
    "installers",
    "local cache runtime",
    "private file ingestion",
    "telemetry",
    "accounts",
    "cloud sync",
    "relay runtime",
    "live backend dependency",
    "live probes",
    "Rust FFI",
    "production readiness claims",
}

FORBIDDEN_NATIVE_IMPLEMENTED_PATTERNS = (
    re.compile(r"\bnative GUI (is )?implemented\b", re.IGNORECASE),
    re.compile(r"\bnative app(s)? (is|are) implemented\b", re.IGNORECASE),
    re.compile(r"\bVisual Studio project (is )?(created|implemented|available)\b", re.IGNORECASE),
    re.compile(r"\bXcode project (is )?(created|implemented|available)\b", re.IGNORECASE),
    re.compile(r"\bproduction[- ]ready native\b", re.IGNORECASE),
)

FORBIDDEN_ABSOLUTE_PATH_PATTERNS = (
    re.compile(r"[A-Za-z]:\\"),
    re.compile(r"/Users/"),
    re.compile(r"/home/"),
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Native Client Project Readiness Review v0."
    )
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_native_project_readiness_review(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_native_project_readiness_review(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    review_dir = repo_root / "control" / "audits" / "native-client-project-readiness-v0"
    report_path = review_dir / "native_readiness_report.json"
    lanes_path = repo_root / "control" / "inventory" / "publication" / "native_client_lanes.json"

    report = _load_json(report_path, repo_root, errors)
    lanes = _load_json(lanes_path, repo_root, errors)
    project_files = _find_project_files(repo_root)

    _validate_pack_files(review_dir, errors)
    _validate_report(report, lanes, errors)
    _validate_markdown(review_dir, errors)
    _validate_no_project_files(project_files, errors)
    _validate_no_runtime_claims(review_dir, errors)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "native_project_readiness_review_validator_v0",
        "review_dir": "control/audits/native-client-project-readiness-v0",
        "decision": _mapping(report).get("decision"),
        "first_candidate_lane": _mapping(report).get("first_candidate_lane"),
        "human_approval_required": _mapping(report).get("human_approval_required"),
        "project_file_count": len(project_files),
        "required_file_count": len(REQUIRED_REVIEW_FILES),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_pack_files(review_dir: Path, errors: list[str]) -> None:
    if not review_dir.is_dir():
        errors.append("control/audits/native-client-project-readiness-v0: review directory is missing.")
        return
    present = {path.name for path in review_dir.iterdir() if path.is_file()}
    missing = sorted(REQUIRED_REVIEW_FILES - present)
    if missing:
        errors.append(f"native readiness review pack: missing files {missing}.")


def _validate_report(report: Any, lanes: Any, errors: list[str]) -> None:
    if not isinstance(report, Mapping):
        errors.append("native_readiness_report.json: must be a JSON object.")
        return

    missing = sorted(REQUIRED_REPORT_FIELDS - set(report))
    if missing:
        errors.append(f"native_readiness_report.json: missing fields {missing}.")

    if report.get("report_id") != "native_client_project_readiness_review_v0":
        errors.append("native_readiness_report.json: report_id must be native_client_project_readiness_review_v0.")
    if report.get("created_by_slice") != "native_client_project_readiness_review_v0":
        errors.append("native_readiness_report.json: created_by_slice must match this review.")

    decision = report.get("decision")
    if decision not in ALLOWED_DECISIONS:
        errors.append(f"native_readiness_report.json: decision must be one of {sorted(ALLOWED_DECISIONS)}.")

    if decision == "ready_for_minimal_project_skeleton_after_human_approval":
        if report.get("human_approval_required") is not True:
            errors.append("native_readiness_report.json: human approval must be required for skeleton readiness.")
        if "human approval" not in _lower_join(report.get("required_before_project_creation")):
            errors.append("native_readiness_report.json: required_before_project_creation must include human approval.")

    if report.get("native_gui_implemented") is not False:
        errors.append("native_readiness_report.json: native_gui_implemented must be false.")
    if report.get("native_project_files_added") is not False:
        errors.append("native_readiness_report.json: native_project_files_added must be false.")
    if report.get("production_ready") is not False:
        errors.append("native_readiness_report.json: production_ready must be false.")

    lane_ids = _lane_ids(lanes)
    first_lane = report.get("first_candidate_lane")
    if first_lane not in lane_ids:
        errors.append(f"native_readiness_report.json: first_candidate_lane {first_lane!r} is not in native_client_lanes.json.")

    for key in ("contract_coverage", "lane_readiness", "blockers", "required_before_project_creation", "prohibited_initial_scope"):
        if not isinstance(report.get(key), list) or not report.get(key):
            errors.append(f"native_readiness_report.json: {key} must be a non-empty list.")

    prohibited = {str(item) for item in _list(report.get("prohibited_initial_scope"))}
    missing_prohibited = sorted(REQUIRED_PROHIBITED_SCOPE - prohibited)
    if missing_prohibited:
        errors.append(f"native_readiness_report.json: prohibited_initial_scope missing {missing_prohibited}.")

    serialized = json.dumps(report, sort_keys=True)
    for pattern in FORBIDDEN_ABSOLUTE_PATH_PATTERNS:
        if pattern.search(serialized):
            errors.append("native_readiness_report.json: must not include volatile absolute local paths.")


def _validate_markdown(review_dir: Path, errors: list[str]) -> None:
    expected_phrases = {
        "CURRENT_STATE.md": [
            "No GUI native app is implemented",
            "No Visual Studio project is present",
            "No Xcode project is present",
            "No FFI boundary is implemented",
        ],
        "READINESS_DECISION.md": [
            "ready_for_minimal_project_skeleton_after_human_approval",
            "explicit human approval",
            "no Rust FFI",
            "no production readiness claim",
        ],
        "PRE_NATIVE_CHECKLIST.md": [
            "Status: unsigned and future",
            "Human explicitly approves native project scaffolding",
            "No telemetry, analytics, accounts, cloud sync, or diagnostic upload is approved",
            "Operator signoff is recorded",
        ],
        "NEXT_STEPS.md": [
            "Windows 7 WinForms Native Skeleton Planning v0",
            "planning only",
            "must not create Visual Studio project files",
            "Manual Observation Batch 0 Execution",
        ],
    }
    for filename, phrases in expected_phrases.items():
        path = review_dir / filename
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{path.relative_to(review_dir.parent.parent.parent).as_posix()}: missing phrase {phrase!r}.")


def _validate_no_project_files(project_files: list[str], errors: list[str]) -> None:
    for path in project_files:
        errors.append(f"{path}: native project file/directory is not allowed before explicit future approval.")


def _validate_no_runtime_claims(review_dir: Path, errors: list[str]) -> None:
    combined = []
    for path in review_dir.glob("*.md"):
        combined.append(path.read_text(encoding="utf-8"))
    text = "\n".join(combined)
    for pattern in FORBIDDEN_NATIVE_IMPLEMENTED_PATTERNS:
        for match in pattern.finditer(text):
            context = text[max(0, match.start() - 90) : match.end() + 90].casefold()
            if any(token in context for token in ("no ", "not ", "does not", "future", "deferred", "must not")):
                continue
            errors.append(f"native readiness docs include forbidden positive claim {match.group(0)!r}.")
    if re.search(r"\bproduction[- ]ready\b", text, re.IGNORECASE):
        for match in re.finditer(r"\bproduction[- ]ready\b", text, re.IGNORECASE):
            context = text[max(0, match.start() - 90) : match.end() + 90].casefold()
            if any(token in context for token in ("no ", "not ", "does not", "without", "must not")):
                continue
            errors.append("native readiness docs must not claim production-ready status.")


def _find_project_files(repo_root: Path) -> list[str]:
    offenders: list[str] = []
    ignored_parts = {".git", "__pycache__"}
    for path in repo_root.rglob("*"):
        if any(part in ignored_parts for part in path.parts):
            continue
        if path.suffix.casefold() in PROJECT_SUFFIXES:
            offenders.append(_display_path(path, repo_root))
    return sorted(offenders)


def _lane_ids(payload: Any) -> set[str]:
    lanes = _mapping(payload).get("lanes")
    if not isinstance(lanes, list):
        return set()
    return {str(item.get("lane_id")) for item in lanes if isinstance(item, Mapping) and item.get("lane_id")}


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
        "Native Client Project Readiness Review validation",
        f"status: {report['status']}",
        f"decision: {report.get('decision')}",
        f"first_candidate_lane: {report.get('first_candidate_lane')}",
        f"human_approval_required: {report.get('human_approval_required')}",
        f"native_project_files: {report.get('project_file_count')}",
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


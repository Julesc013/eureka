from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
PLAN_DIR = REPO_ROOT / "control" / "audits" / "relay-prototype-planning-v0"
PLAN_JSON = PLAN_DIR / "relay_prototype_plan.json"

REQUIRED_FILES = {
    "README.md",
    "CURRENT_STATE.md",
    "PROTOTYPE_SCOPE.md",
    "PROTOCOL_DECISION.md",
    "INPUT_DATA_CONTRACT.md",
    "OUTPUT_SURFACE_CONTRACT.md",
    "SECURITY_PRIVACY_REVIEW.md",
    "OPERATOR_GATES.md",
    "TEST_PLAN.md",
    "RISKS.md",
    "IMPLEMENTATION_BOUNDARIES.md",
    "NEXT_IMPLEMENTATION_PROMPT_REQUIREMENTS.md",
    "relay_prototype_plan.json",
}

REQUIRED_ALLOWED_INPUTS = {
    "site/dist/data/*.json",
    "site/dist/text/*",
    "site/dist/files/*",
    "snapshots/examples/static_snapshot_v0/*",
    "generated public data summaries",
    "static snapshot manifests and checksums",
}

REQUIRED_PROHIBITED_INPUTS = {
    "arbitrary user directories",
    "private cache roots",
    "credentials",
    "live API responses",
    "live probe outputs",
    "external URLs",
}

REQUIRED_ALLOWED_OUTPUTS = {
    "read-only HTTP pages",
    "plain text pages",
    "JSON static summaries",
    "file-tree index views",
    "checksum files",
    "snapshot manifest views",
}

REQUIRED_PROHIBITED_OUTPUTS = {
    "write endpoints",
    "upload endpoints",
    "admin endpoints",
    "live probe endpoints",
    "arbitrary file serving",
    "executable launch",
}

RELAY_RUNTIME_FILENAMES = {
    "relay_server.py",
    "run_relay.py",
    "local_http_relay.py",
    "relay_runtime.py",
    "relay_proxy.py",
    "ftp_relay.py",
    "smb_relay.py",
    "webdav_relay.py",
    "gopher_relay.py",
    "snapshot_mount.py",
}

RELAY_RUNTIME_NAME_PATTERNS = (
    re.compile(r"(^|[_-])relay[_-]server\.py$", re.IGNORECASE),
    re.compile(r"(^|[_-])local[_-]http[_-]relay\.py$", re.IGNORECASE),
    re.compile(r"(^|[_-])relay[_-]runtime\.py$", re.IGNORECASE),
    re.compile(r"(^|[_-])relay[_-]proxy\.py$", re.IGNORECASE),
)

IMPLEMENTED_RELAY_CLAIMS = (
    re.compile(r"\brelay runtime (is )?(implemented|available|enabled|running)\b", re.IGNORECASE),
    re.compile(r"\brelay server (is )?(implemented|available|enabled|running)\b", re.IGNORECASE),
    re.compile(r"\bold-client relay support (is )?(implemented|available|enabled)\b", re.IGNORECASE),
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Relay Prototype Planning v0.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_relay_prototype_plan(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_relay_prototype_plan(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    plan_dir = repo_root / "control" / "audits" / "relay-prototype-planning-v0"
    plan = _load_json(plan_dir / "relay_prototype_plan.json", repo_root, errors)
    relay_runtime_files = _find_relay_runtime_files(repo_root)

    _validate_files(plan_dir, errors)
    _validate_plan(plan, errors)
    _validate_markdown(plan_dir, errors)
    _validate_no_relay_runtime_files(relay_runtime_files, errors)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "relay_prototype_plan_validator_v0",
        "plan_dir": "control/audits/relay-prototype-planning-v0",
        "report_id": _mapping(plan).get("report_id"),
        "decision": _mapping(plan).get("decision"),
        "recommended_first_prototype": _mapping(plan).get("recommended_first_prototype"),
        "first_protocol_candidate": _mapping(
            _mapping(plan).get("first_protocol_candidate")
        ).get("id"),
        "implementation_approved": _mapping(plan).get("implementation_approved"),
        "human_approval_required": _mapping(plan).get("human_approval_required"),
        "no_relay_runtime_implemented": _mapping(plan).get("no_relay_runtime_implemented"),
        "no_network_sockets_opened": _mapping(plan).get("no_network_sockets_opened"),
        "relay_runtime_file_count": len(relay_runtime_files),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_files(plan_dir: Path, errors: list[str]) -> None:
    if not plan_dir.is_dir():
        errors.append("control/audits/relay-prototype-planning-v0: missing plan directory.")
        return
    present = {path.name for path in plan_dir.iterdir() if path.is_file()}
    missing = sorted(REQUIRED_FILES - present)
    if missing:
        errors.append(f"relay prototype planning pack: missing files {missing}.")


def _validate_plan(plan: Any, errors: list[str]) -> None:
    if not isinstance(plan, Mapping):
        errors.append("relay_prototype_plan.json: must be a JSON object.")
        return

    expected_scalars = {
        "report_id": "relay_prototype_planning_v0",
        "created_by_slice": "relay_prototype_planning_v0",
        "decision": "first_future_relay_prototype_should_be_local_static_http",
        "recommended_first_prototype": "local_static_http_relay_prototype",
        "status": "planning_only",
        "implementation_approved": False,
        "human_approval_required": True,
        "no_relay_runtime_implemented": True,
        "no_network_sockets_opened": True,
        "no_protocol_servers_implemented": True,
    }
    for key, expected in expected_scalars.items():
        if plan.get(key) != expected:
            errors.append(f"relay_prototype_plan.json: {key} must be {expected!r}.")

    protocol = _mapping(plan.get("first_protocol_candidate"))
    if protocol.get("id") != "local_static_http":
        errors.append("relay_prototype_plan.json: first_protocol_candidate.id must be local_static_http.")
    if protocol.get("default_bind_scope") != "localhost_only":
        errors.append(
            "relay_prototype_plan.json: first protocol default bind scope must be localhost_only."
        )
    if protocol.get("mode") != "read_only":
        errors.append("relay_prototype_plan.json: first protocol mode must be read_only.")

    allowed_inputs = {str(item) for item in _list(plan.get("allowed_initial_inputs"))}
    missing_allowed_inputs = sorted(REQUIRED_ALLOWED_INPUTS - allowed_inputs)
    if missing_allowed_inputs:
        errors.append(
            f"relay_prototype_plan.json: allowed_initial_inputs missing {missing_allowed_inputs}."
        )

    prohibited_inputs = {str(item) for item in _list(plan.get("prohibited_initial_inputs"))}
    missing_prohibited_inputs = sorted(REQUIRED_PROHIBITED_INPUTS - prohibited_inputs)
    if missing_prohibited_inputs:
        errors.append(
            f"relay_prototype_plan.json: prohibited_initial_inputs missing {missing_prohibited_inputs}."
        )

    allowed_outputs = {str(item) for item in _list(plan.get("allowed_initial_outputs"))}
    missing_allowed_outputs = sorted(REQUIRED_ALLOWED_OUTPUTS - allowed_outputs)
    if missing_allowed_outputs:
        errors.append(
            f"relay_prototype_plan.json: allowed_initial_outputs missing {missing_allowed_outputs}."
        )

    prohibited_outputs = {str(item) for item in _list(plan.get("prohibited_initial_outputs"))}
    missing_prohibited_outputs = sorted(REQUIRED_PROHIBITED_OUTPUTS - prohibited_outputs)
    if missing_prohibited_outputs:
        errors.append(
            f"relay_prototype_plan.json: prohibited_initial_outputs missing {missing_prohibited_outputs}."
        )

    security = _mapping(plan.get("security_defaults"))
    expected_security = {
        "bind_scope": "localhost_only",
        "lan_bind_allowed": False,
        "public_internet_exposure_allowed": False,
        "read_only": True,
        "public_data_only": True,
        "private_data_allowed": False,
        "writes_allowed": False,
        "uploads_allowed": False,
        "admin_routes_allowed": False,
        "live_backend_proxy_allowed": False,
        "live_probes_allowed": False,
        "telemetry_allowed": False,
        "downloads_allowed": False,
        "installer_actions_allowed": False,
        "executable_launch_allowed": False,
    }
    for key, expected in expected_security.items():
        if security.get(key) != expected:
            errors.append(f"relay_prototype_plan.json: security_defaults.{key} must be {expected!r}.")

    gates = _lower_join(plan.get("required_before_implementation"))
    for phrase in (
        "explicit human approval",
        "bind scope approval",
        "input roots approval",
        "privacy review",
        "action policy review",
        "snapshot consumer review",
        "no private data confirmation",
        "no live probe confirmation",
        "no live backend proxy confirmation",
    ):
        if phrase not in gates:
            errors.append(f"relay_prototype_plan.json: required_before_implementation missing {phrase!r}.")


def _validate_markdown(plan_dir: Path, errors: list[str]) -> None:
    expected = {
        "README.md": [
            "planning only",
            "local_static_http_relay_prototype",
            "Future implementation requires explicit human approval",
        ],
        "CURRENT_STATE.md": [
            "no relay runtime exists",
            "no sockets or listeners exist",
            "relay implementation requires explicit human approval later",
        ],
        "PROTOTYPE_SCOPE.md": [
            "localhost bind only by default",
            "read-only",
            "no live backend proxying",
            "no private file roots",
        ],
        "INPUT_DATA_CONTRACT.md": [
            "site/dist/data/*.json",
            "arbitrary user directories",
            "external URLs",
        ],
        "OUTPUT_SURFACE_CONTRACT.md": [
            "read-only HTTP pages",
            "write endpoints",
            "arbitrary file serving",
            "executable launch",
        ],
        "SECURITY_PRIVACY_REVIEW.md": [
            "localhost-only default",
            "no public internet exposure",
            "no private data",
            "no live backend proxy",
        ],
        "OPERATOR_GATES.md": [
            "explicit human approval",
            "no private data confirmation",
            "no live probe confirmation",
        ],
        "IMPLEMENTATION_BOUNDARIES.md": [
            "This planning milestone does not implement",
            "relay server",
            "socket listener",
        ],
    }
    for filename, phrases in expected.items():
        path = plan_dir / filename
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        lowered = text.casefold()
        for phrase in phrases:
            if phrase.casefold() not in lowered:
                errors.append(f"{filename}: missing phrase {phrase!r}.")

    for path in plan_dir.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        for pattern in IMPLEMENTED_RELAY_CLAIMS:
            for match in pattern.finditer(text):
                context = text[max(0, match.start() - 120) : match.end() + 120].casefold()
                if any(token in context for token in ("no ", "not ", "does not", "future", "planning")):
                    continue
                errors.append(f"{path.name}: prohibited implemented relay claim {match.group(0)!r}.")


def _validate_no_relay_runtime_files(paths: list[str], errors: list[str]) -> None:
    for path in paths:
        errors.append(f"{path}: relay runtime/server/protocol implementation file is not allowed.")


def _find_relay_runtime_files(repo_root: Path) -> list[str]:
    offenders: list[str] = []
    ignored_parts = {".git", "__pycache__"}
    for path in repo_root.rglob("*.py"):
        if any(part in ignored_parts for part in path.parts):
            continue
        name = path.name.casefold()
        if name in RELAY_RUNTIME_FILENAMES or any(pattern.search(name) for pattern in RELAY_RUNTIME_NAME_PATTERNS):
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
        "Relay prototype plan validation",
        f"status: {report['status']}",
        f"report_id: {report.get('report_id')}",
        f"decision: {report.get('decision')}",
        f"recommended_first_prototype: {report.get('recommended_first_prototype')}",
        f"first_protocol_candidate: {report.get('first_protocol_candidate')}",
        f"implementation_approved: {report.get('implementation_approved')}",
        f"human_approval_required: {report.get('human_approval_required')}",
        f"no_relay_runtime_implemented: {report.get('no_relay_runtime_implemented')}",
        f"no_network_sockets_opened: {report.get('no_network_sockets_opened')}",
        f"relay_runtime_files: {report.get('relay_runtime_file_count')}",
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

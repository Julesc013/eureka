from __future__ import annotations

import argparse
import json
from pathlib import Path
import shlex
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = (
    REPO_ROOT / "control" / "inventory" / "generated_artifacts" / "generated_artifacts.json"
)
POLICY_PATH = REPO_ROOT / "control" / "inventory" / "generated_artifacts" / "drift_policy.json"

CREATED_BY = "generated_artifact_drift_guard_v0"
FORBIDDEN_COMMAND_TERMS = (
    "curl",
    "wget",
    "invoke-webrequest",
    "invoke-restmethod",
    "internet_archive_live",
    "google_web_search",
    "live-source",
    "scrape",
    "crawl",
)
SUCCESS_STATUSES = {"passed", "skipped"}


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check committed generated artifacts for drift."
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument(
        "--artifact",
        action="append",
        default=[],
        help="Only check the named artifact_id. May be supplied more than once.",
    )
    parser.add_argument("--list", action="store_true", help="List known artifact groups.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat optional skips and command-resolution warnings as failures.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    output = stdout or sys.stdout
    report = check_generated_artifact_drift(
        selected_artifacts=args.artifact,
        strict=args.strict,
        list_only=args.list,
    )

    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    elif args.list:
        for artifact_id in report["artifact_ids"]:
            output.write(f"{artifact_id}\n")
    else:
        output.write(_format_plain(report))

    if args.list:
        return 0 if report["status"] == "valid" else 1
    return 0 if report["status"] == "valid" else 1


def check_generated_artifact_drift(
    *,
    selected_artifacts: Sequence[str] = (),
    strict: bool = False,
    list_only: bool = False,
) -> dict[str, Any]:
    errors: list[str] = []
    inventory = _load_json(INVENTORY_PATH, errors)
    policy = _load_json(POLICY_PATH, errors)
    groups = _artifact_groups(inventory, errors)
    selected = set(selected_artifacts)

    artifact_ids = [str(group.get("artifact_id")) for group in groups if group.get("artifact_id")]
    unknown = sorted(selected - set(artifact_ids))
    if unknown:
        errors.append(f"unknown artifact ids requested: {unknown}")

    if not _policy_is_no_network(policy):
        errors.append(f"{_rel(POLICY_PATH)}: no_network_policy is missing or empty.")

    if list_only:
        return {
            "status": "valid" if not errors else "invalid",
            "created_by": CREATED_BY,
            "inventory": _rel(INVENTORY_PATH),
            "policy": _rel(POLICY_PATH),
            "artifact_ids": artifact_ids,
            "selected_artifacts": sorted(selected),
            "strict": strict,
            "errors": errors,
        }

    results: list[dict[str, Any]] = []
    for group in groups:
        artifact_id = str(group.get("artifact_id", ""))
        if selected and artifact_id not in selected:
            continue
        results.append(_check_group(group, strict=strict))

    for result in results:
        errors.extend(str(error) for error in result.get("errors", []))

    status_counts: dict[str, int] = {}
    for result in results:
        status = str(result.get("status"))
        status_counts[status] = status_counts.get(status, 0) + 1

    failed = any(result.get("status") == "failed" for result in results)
    unavailable_required = any(
        result.get("status") == "unavailable" and result.get("required", True)
        for result in results
    )
    strict_problem = strict and any(result.get("status") not in SUCCESS_STATUSES for result in results)

    status = "invalid" if errors or failed or unavailable_required or strict_problem else "valid"
    return {
        "status": status,
        "created_by": CREATED_BY,
        "inventory": _rel(INVENTORY_PATH),
        "policy": _rel(POLICY_PATH),
        "artifact_ids": artifact_ids,
        "selected_artifacts": sorted(selected),
        "strict": strict,
        "artifact_results": results,
        "status_counts": status_counts,
        "errors": errors,
    }


def _check_group(group: Mapping[str, Any], *, strict: bool) -> dict[str, Any]:
    artifact_id = str(group.get("artifact_id", "<missing-artifact-id>"))
    errors: list[str] = []
    warnings: list[str] = []
    path_results = _check_artifact_paths(group, errors)
    command_results: list[dict[str, Any]] = []

    check_command = group.get("check_command")
    if not isinstance(check_command, str) or not check_command.strip():
        errors.append(f"{artifact_id}: check_command is missing.")
    else:
        command_results.append(_run_declared_command(artifact_id, "check_command", check_command))

    for command in group.get("validator_commands", []):
        if isinstance(command, str) and command.strip():
            command_results.append(_run_declared_command(artifact_id, "validator_command", command))
        else:
            errors.append(f"{artifact_id}: validator_commands entries must be non-empty strings.")

    generator_command = group.get("generator_command")
    if isinstance(generator_command, str) and generator_command.startswith("python "):
        resolution = _resolve_command(generator_command)
        if not resolution["available"]:
            message = f"{artifact_id}: generator command is unavailable: {generator_command}"
            if strict:
                errors.append(message)
            else:
                warnings.append(message)

    for command_result in command_results:
        if command_result["status"] == "failed":
            errors.append(
                f"{artifact_id}: {command_result['kind']} failed with exit code "
                f"{command_result.get('returncode')}: {command_result['command']}"
            )
        elif command_result["status"] == "unavailable":
            errors.append(
                f"{artifact_id}: {command_result['kind']} is unavailable: {command_result['command']}"
            )
        elif command_result["status"] == "forbidden":
            errors.append(
                f"{artifact_id}: {command_result['kind']} contains a forbidden network/live term: "
                f"{command_result['command']}"
            )

    required = group.get("status") not in {"optional", "future", "deferred"}
    status = "passed"
    if errors:
        status = "failed"
    elif any(result["status"] == "unavailable" for result in command_results):
        status = "unavailable"
    elif not required:
        status = "skipped"

    return {
        "artifact_id": artifact_id,
        "status": status,
        "required": required,
        "deterministic": bool(group.get("deterministic")),
        "artifact_paths": path_results,
        "check_command": check_command,
        "validator_commands": [
            command for command in group.get("validator_commands", []) if isinstance(command, str)
        ],
        "command_results": command_results,
        "errors": errors,
        "warnings": warnings,
    }


def _check_artifact_paths(group: Mapping[str, Any], errors: list[str]) -> list[dict[str, Any]]:
    artifact_id = str(group.get("artifact_id", "<missing-artifact-id>"))
    paths = group.get("artifact_paths")
    if not isinstance(paths, list) or not paths:
        errors.append(f"{artifact_id}: artifact_paths must be a non-empty list.")
        return []

    results: list[dict[str, Any]] = []
    for raw in paths:
        if not isinstance(raw, str) or not raw.strip():
            errors.append(f"{artifact_id}: artifact_paths entries must be non-empty strings.")
            continue
        matches = _resolve_path_pattern(raw)
        exists = bool(matches)
        if not exists:
            errors.append(f"{artifact_id}: artifact path is missing: {raw}")
        results.append(
            {
                "path": raw,
                "exists": exists,
                "match_count": len(matches),
                "sample_matches": [_rel(path) for path in matches[:5]],
            }
        )
    return results


def _run_declared_command(artifact_id: str, kind: str, command: str) -> dict[str, Any]:
    lowered = command.lower()
    forbidden_terms = [term for term in FORBIDDEN_COMMAND_TERMS if term in lowered]
    if forbidden_terms:
        return {
            "artifact_id": artifact_id,
            "kind": kind,
            "command": command,
            "status": "forbidden",
            "forbidden_terms": forbidden_terms,
            "stdout_summary": "",
            "stderr_summary": "",
        }

    resolution = _resolve_command(command)
    if not resolution["available"]:
        return {
            "artifact_id": artifact_id,
            "kind": kind,
            "command": command,
            "status": "unavailable",
            "reason": resolution["reason"],
            "stdout_summary": "",
            "stderr_summary": "",
        }

    completed = subprocess.run(
        _command_tokens(command),
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "artifact_id": artifact_id,
        "kind": kind,
        "command": command,
        "status": "passed" if completed.returncode == 0 else "failed",
        "returncode": completed.returncode,
        "stdout_summary": _summarize_output(completed.stdout),
        "stderr_summary": _summarize_output(completed.stderr),
    }


def _resolve_command(command: str) -> dict[str, Any]:
    try:
        tokens = shlex.split(command)
    except ValueError as exc:
        return {"available": False, "reason": f"cannot parse command: {exc}"}
    if not tokens:
        return {"available": False, "reason": "empty command"}

    executable = tokens[0].lower()
    if executable not in {"python", "py"} and tokens[0] != sys.executable:
        return {"available": False, "reason": "only Python/std-lib commands are allowed"}
    if len(tokens) < 2:
        return {"available": False, "reason": "missing Python target"}

    target = tokens[1]
    if target.endswith(".py"):
        path = REPO_ROOT / target
        return {
            "available": path.exists(),
            "reason": "ok" if path.exists() else f"missing script {_rel(path)}",
        }
    if target == "-m" and len(tokens) >= 3:
        module = tokens[2]
        if module == "unittest":
            return _resolve_unittest_command(tokens[3:])
        return {"available": True, "reason": "module command"}
    return {"available": True, "reason": "python command"}


def _resolve_unittest_command(args: Sequence[str]) -> dict[str, Any]:
    if not args:
        return {"available": True, "reason": "unittest default discovery"}
    if args[0] == "discover":
        directory = None
        for index, arg in enumerate(args):
            if arg == "-s" and index + 1 < len(args):
                directory = args[index + 1]
                break
        if directory is None:
            return {"available": True, "reason": "unittest discover without explicit directory"}
        path = REPO_ROOT / directory
        return {
            "available": path.exists(),
            "reason": "ok" if path.exists() else f"missing unittest discovery root {_rel(path)}",
        }

    missing: list[str] = []
    for module in args:
        if module.startswith("-"):
            continue
        path = REPO_ROOT / (module.replace(".", "/") + ".py")
        package = REPO_ROOT / module.replace(".", "/") / "__init__.py"
        if not path.exists() and not package.exists():
            missing.append(module)
    if missing:
        return {"available": False, "reason": f"missing unittest modules {missing}"}
    return {"available": True, "reason": "ok"}


def _command_tokens(command: str) -> list[str]:
    tokens = shlex.split(command)
    if tokens and tokens[0].lower() in {"python", "py"}:
        tokens[0] = sys.executable
    return tokens


def _resolve_path_pattern(pattern: str) -> list[Path]:
    normalized = pattern.replace("\\", "/")
    if any(char in normalized for char in "*?["):
        return sorted(REPO_ROOT.glob(normalized))
    path = REPO_ROOT / normalized
    return [path] if path.exists() else []


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path)}: missing JSON file.")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)}: invalid JSON: {exc}.")
    return None


def _artifact_groups(inventory: Any, errors: list[str]) -> list[Mapping[str, Any]]:
    if not isinstance(inventory, Mapping):
        errors.append(f"{_rel(INVENTORY_PATH)}: inventory must be a JSON object.")
        return []
    groups = inventory.get("artifact_groups")
    if not isinstance(groups, list):
        errors.append(f"{_rel(INVENTORY_PATH)}: artifact_groups must be a list.")
        return []
    valid_groups: list[Mapping[str, Any]] = []
    for index, group in enumerate(groups):
        if isinstance(group, Mapping):
            valid_groups.append(group)
        else:
            errors.append(f"{_rel(INVENTORY_PATH)}: artifact_groups[{index}] must be an object.")
    return valid_groups


def _policy_is_no_network(policy: Any) -> bool:
    return isinstance(policy, Mapping) and bool(str(policy.get("no_network_policy", "")).strip())


def _summarize_output(text: str, *, max_lines: int = 8, max_chars: int = 1200) -> str:
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    summary = "\n".join(lines[:max_lines])
    if len(summary) > max_chars:
        return summary[: max_chars - 3] + "..."
    return summary


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Generated Artifact Drift Guard v0",
        f"status: {report['status']}",
        f"inventory: {report['inventory']}",
        f"policy: {report['policy']}",
        f"strict: {report['strict']}",
    ]
    if "status_counts" in report:
        lines.append(f"status_counts: {report['status_counts']}")
        for result in report.get("artifact_results", []):
            lines.append(f"- {result['artifact_id']}: {result['status']}")
            for command_result in result.get("command_results", []):
                lines.append(
                    f"  - {command_result['kind']}: {command_result['status']} "
                    f"({command_result['command']})"
                )
    if report.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    else:
        lines.append("errors: []")
    return "\n".join(lines) + "\n"


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())

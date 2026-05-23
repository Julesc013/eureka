from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY = REPO_ROOT / "control" / "policies" / "path_taxonomy_policy.json"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Eureka second-level path taxonomy policy.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--policy", default=str(POLICY), help="Path taxonomy policy JSON.")
    parser.add_argument("--strict-debt", action="store_true", help="Fail when known taxonomy debt remains.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_path_taxonomy(Path(args.repo_root), Path(args.policy), strict_debt=args.strict_debt)
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_path_taxonomy(
    repo_root: Path = REPO_ROOT,
    policy_path: Path = POLICY,
    *,
    strict_debt: bool = False,
) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    policy = _load_policy(policy_path, errors)
    tracked_files = _git_ls_files(root)
    tracked_set = set(tracked_files)
    root_reports: dict[str, Any] = {}
    debt_paths: list[str] = []

    for root_name, rule_value in _mapping(policy.get("root_rules")).items():
        rule = _mapping(rule_value)
        dirs = _first_level_dirs(tracked_files, root_name)
        allowed = set(_string_list(rule.get("allowed_first_level")))
        known_debt = set(_string_list(rule.get("known_debt_first_level")))
        compatibility = set(_string_list(rule.get("compatibility_first_level")))
        compatibility_only_files = set(_string_list(rule.get("compatibility_only_files")))
        known_debt_prefixes = tuple(_string_list(rule.get("known_debt_prefixes")))
        required = set(_string_list(rule.get("required_first_level")))
        classify_unlisted_as_debt = rule.get("classify_unlisted_as_debt") is True

        missing_required = sorted(required - set(dirs))
        for missing in missing_required:
            errors.append(f"{root_name}/{missing}: required taxonomy directory is missing.")

        unexpected: list[str] = []
        debt: list[str] = []
        compatibility_present: list[str] = []
        for name in dirs:
            if name in allowed:
                continue
            if name in compatibility:
                compatibility_present.append(name)
                offenders = _compatibility_offenders(tracked_files, root_name, name, compatibility_only_files)
                for offender in offenders:
                    errors.append(
                        f"{root_name}/{name}: compatibility path contains non-wrapper file {offender}."
                    )
                continue
            if name in known_debt or any(name.startswith(prefix) for prefix in known_debt_prefixes):
                debt.append(name)
                debt_paths.append(f"{root_name}/{name}")
                continue
            if classify_unlisted_as_debt:
                debt.append(name)
                debt_paths.append(f"{root_name}/{name}")
            else:
                unexpected.append(name)

        for name in unexpected:
            errors.append(f"{root_name}/{name}: first-level directory is not allowed or classified as known debt.")

        root_reports[root_name] = {
            "actual_first_level": dirs,
            "allowed_first_level": sorted(allowed),
            "compatibility_first_level": sorted(set(compatibility_present)),
            "known_debt_first_level": sorted(set(debt)),
            "unexpected_first_level": unexpected,
            "missing_required_first_level": missing_required,
            "target_families": _string_list(rule.get("target_families")),
        }

    forbidden_present: list[str] = []
    for path in _string_list(policy.get("forbidden_active_paths")):
        if path in tracked_set or any(item.startswith(f"{path}/") for item in tracked_files):
            forbidden_present.append(path)
            errors.append(f"{path}: forbidden active path is still tracked.")

    if strict_debt and debt_paths:
        errors.extend(f"{path}: strict debt mode forbids remaining taxonomy debt." for path in debt_paths)

    return {
        "schema_version": "path_taxonomy_validation.v0",
        "status": "valid" if not errors else "invalid",
        "policy": _rel(policy_path, root),
        "strict_debt": strict_debt,
        "roots": root_reports,
        "debt_count": len(debt_paths),
        "debt_paths": sorted(debt_paths),
        "forbidden_active_paths_present": forbidden_present,
        "errors": errors,
        "product_behavior_changed": False,
    }


def _load_policy(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{path.as_posix()}: policy file is missing.")
    except json.JSONDecodeError as exc:
        errors.append(f"{path.as_posix()}: invalid JSON: {exc}.")
    return {}


def _git_ls_files(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _first_level_dirs(tracked_files: Sequence[str], root_name: str) -> list[str]:
    prefix = f"{root_name}/"
    dirs = {
        path[len(prefix) :].split("/", 1)[0]
        for path in tracked_files
        if path.startswith(prefix) and "/" in path[len(prefix) :]
    }
    return sorted(dirs)


def _compatibility_offenders(
    tracked_files: Sequence[str],
    root_name: str,
    first_level: str,
    allowed_files: set[str],
) -> list[str]:
    if not allowed_files:
        return []
    prefix = f"{root_name}/{first_level}/"
    offenders: list[str] = []
    for path in tracked_files:
        if not path.startswith(prefix):
            continue
        relative = path[len(prefix) :]
        if relative not in allowed_files:
            offenders.append(path)
    return offenders


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _format_plain(report: dict[str, Any]) -> str:
    lines = [
        f"Path taxonomy: {report['status']}",
        f"debt_count: {report['debt_count']}",
    ]
    for path in report["debt_paths"]:
        lines.append(f"- debt: {path}")
    for error in report["errors"]:
        lines.append(f"- error: {error}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())

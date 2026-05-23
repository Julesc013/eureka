#!/usr/bin/env python3
"""Validate INSTANCE-LAYOUT-01 policy, docs, scripts, and dry-run helpers."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.appliance.errors import LocalInstancePathError
from runtime.local.appliance.paths import resolve_default_instance_root, resolve_instance_root


POLICY = REPO_ROOT / "control/policies/instance_layout_policy.json"
RUNBOOKS = (
    REPO_ROOT / "docs/operations/LOCAL_INSTANCE_LAYOUT.md",
    REPO_ROOT / "docs/operations/INSTANCE_PATH_POLICY.md",
    REPO_ROOT / "docs/operations/LOCAL_INSTANCE_BOOTSTRAP.md",
    REPO_ROOT / "docs/operations/LOCAL_INSTANCE_MIGRATION_POLICY.md",
    REPO_ROOT / "docs/operations/LOCAL_HTTP_SERVICE_RUNBOOK.md",
    REPO_ROOT / "docs/operations/LOCAL_HTML_WORKBENCH_RUNBOOK.md",
    REPO_ROOT / "docs/operations/SEARCH_HUNT_RUNTIME_RUNBOOK.md",
    REPO_ROOT / "docs/operations/SEARCH_HUNT_COMMAND_RUNBOOK.md",
    REPO_ROOT / "docs/operations/LOCAL_APPLIANCE_TRACK.md",
)
SCRIPT_HELP_SURFACES = (
    REPO_ROOT / "scripts/eureka_init_instance.py",
    REPO_ROOT / "scripts/eureka_new_instance.py",
    REPO_ROOT / "scripts/eureka_resolve_paths.py",
    REPO_ROOT / "scripts/eureka_list_instances.py",
    REPO_ROOT / "scripts/eureka_migrate_instance_layout.py",
)
DISALLOWED_DEFAULT_PHRASES = (
    "default root is `./eureka-instance`",
    "default instance is `./eureka-instance`",
    "default documented local development instance is `./eureka-instance`",
    "--instance ./eureka-instance",
    "--instance .\\eureka-instance",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    result = validate()
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    return 0 if result["status"] in {"pass", "pass_with_warnings"} else 1


def validate() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    policy = load_json(POLICY, errors)
    if policy.get("schema_version") != "instance_layout_policy.v0":
        errors.append("policy schema_version mismatch")
    expected = {
        "preferred_default_instance_relative_to_repo": "../instances/default",
        "legacy_sibling_instance_allowed": True,
        "legacy_sibling_instance_name": "eureka-instance",
        "repo_nested_instance_allowed": False,
        "explicit_instance_path_required_for_mutating_commands": True,
        "hidden_state_roots_forbidden": True,
        "auto_move_operator_instance_forbidden": True,
        "delete_operator_instance_forbidden": True,
        "commit_instance_state_forbidden": True,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
    for key, value in expected.items():
        if policy.get(key) != value:
            errors.append(f"policy {key} mismatch")

    default_root = resolve_default_instance_root(REPO_ROOT)
    if default_root != (REPO_ROOT.parent / "instances" / "default").resolve():
        errors.append("resolver preferred default is not ../instances/default")
    try:
        resolve_instance_root(REPO_ROOT / "eureka-instance", REPO_ROOT)
        errors.append("resolver accepted repo-nested eureka-instance")
    except LocalInstancePathError:
        pass
    try:
        resolve_instance_root(REPO_ROOT.parent / "eureka-instance", REPO_ROOT)
    except LocalInstancePathError:
        errors.append("resolver rejected explicit legacy sibling eureka-instance")

    for runbook in RUNBOOKS:
        text = read_text(runbook, errors)
        for phrase in DISALLOWED_DEFAULT_PHRASES:
            if phrase in text:
                errors.append(f"runbook recommends repo-nested eureka-instance: {rel(runbook)}")
                break
    for script in SCRIPT_HELP_SURFACES:
        text = script_help_text(script, errors)
        if "../instances/default" not in text and script.name in {"eureka_init_instance.py", "eureka_new_instance.py"}:
            errors.append(f"{script.name} help text does not mention ../instances/default")

    migration = run(
        "python",
        "scripts/eureka_migrate_instance_layout.py",
        "--from",
        "../eureka-instance",
        "--to",
        "../instances/default",
        "--dry-run",
        "--json",
    )
    if migration.returncode != 0:
        errors.append("migration helper dry-run failed")
    else:
        payload = parse_json(migration.stdout, errors, "migration dry-run")
        if payload.get("mutation_performed") is not False or payload.get("source_deleted") is not False:
            errors.append("migration dry-run reported mutation or source deletion")

    tracked_instances = git("ls-files", "--", "eureka-instance", "instances")
    if tracked_instances:
        errors.append("instance roots are committed: " + tracked_instances.replace("\n", ", "))
    gitignore = read_text(REPO_ROOT / ".gitignore", errors)
    for pattern in ("/eureka-instance/", "/instances/", "/.local-instance/", "/.local/", "__pycache__/", "*.py[cod]", "*.pyo", "*.sqlite", "*.sqlite3", "*.db-wal", "*.db-shm", "*.db-journal"):
        if pattern not in gitignore:
            errors.append(f".gitignore missing defensive pattern: {pattern}")

    status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "schema_version": "instance_layout_policy_validation.v0",
        "task": "INSTANCE-LAYOUT-01",
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read JSON {rel(path)}: {exc}")
        return {}
    return payload if isinstance(payload, dict) else {}


def read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"missing file: {rel(path)}")
        return ""


def script_help_text(script: Path, errors: list[str]) -> str:
    text = read_text(script, errors)
    implementation = REPO_ROOT / "tools/generators" / script.name
    if implementation.is_file():
        text += "\n" + read_text(implementation, errors)
    return text


def parse_json(text: str, errors: list[str], label: str) -> dict[str, Any]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        errors.append(f"{label} did not emit JSON: {exc}")
        return {}
    return payload if isinstance(payload, dict) else {}


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(args), cwd=REPO_ROOT, text=True, capture_output=True, check=False)


def git(*args: str) -> str:
    completed = run("git", *args)
    return completed.stdout.strip() if completed.returncode == 0 else ""


def rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())

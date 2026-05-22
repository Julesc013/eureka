#!/usr/bin/env python3
"""Create a clean temp checkout and bootstrap an explicit local instance."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "LOCAL-13"
FORBIDDEN_STATE_NAMES = {"eureka-instance", ".aide.local", ".cache", ".local", "secrets"}
FORBIDDEN_STATE_FILES = {".env"}
DEFAULT_INSTANCE_NAME = "eureka-instance"


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=str(REPO_ROOT))
    parser.add_argument("--workdir")
    parser.add_argument("--instance-name", default=DEFAULT_INSTANCE_NAME)
    parser.add_argument("--skip-clone", action="store_true")
    parser.add_argument("--include-smoke", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)

    try:
        result = run_bootstrap(
            repo=Path(args.repo),
            workdir=Path(args.workdir) if args.workdir else None,
            instance_name=args.instance_name,
            skip_clone=args.skip_clone,
            include_smoke=args.include_smoke,
            cleanup=True,
        )
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        result = fail_result("clean_machine_bootstrap_failed", str(exc))
        print(f"ERROR: {exc}", file=stderr)
    emit_result(result, args.json, args.output, stdout)
    return 0 if result.get("status") in {"pass", "pass_with_warnings"} else 1


def run_bootstrap(
    *,
    repo: Path,
    workdir: Path | None,
    instance_name: str,
    skip_clone: bool,
    include_smoke: bool,
    cleanup: bool,
) -> dict[str, Any]:
    source_repo = repo.resolve()
    if not source_repo.is_dir():
        raise ValueError(f"repo does not exist: {source_repo}")
    if not instance_name or Path(instance_name).name != instance_name:
        raise ValueError("--instance-name must be a single directory name")

    temp_parent = Path(tempfile.mkdtemp(prefix="eureka-clean-machine-", dir=str(workdir.resolve()) if workdir else None))
    checkout = source_repo if skip_clone else temp_parent / "checkout"
    instance = checkout / instance_name
    commands: list[dict[str, Any]] = []
    skipped_state = detect_forbidden_state(source_repo)
    cleaned = False
    try:
        if not skip_clone:
            copy_clean_repo(source_repo, checkout)
        hidden_state_copied = forbidden_state_exists(checkout)
        init = run_script(checkout, "scripts/eureka_init_instance.py", "--instance", str(instance), "--json")
        commands.append(command_record("init_instance", init))
        validate = run_script(checkout, "scripts/eureka_validate_instance.py", "--instance", str(instance), "--json")
        commands.append(command_record("validate_instance", validate))
        runtime = run_script(checkout, "scripts/eureka_local_runtime_status.py", "--instance", str(instance), "--read-only", "--json")
        commands.append(command_record("runtime_status", runtime))

        smoke_result: dict[str, Any] | None = None
        if include_smoke:
            smoke = run_script(checkout, "scripts/eureka_clean_machine_smoke.py", "--repo", str(checkout), "--instance", str(instance), "--json", timeout=300)
            commands.append(command_record("clean_machine_smoke", smoke))
            smoke_result = parse_json(smoke.stdout)

        init_payload = parse_json(init.stdout)
        validate_payload = parse_json(validate.stdout)
        runtime_payload = parse_json(runtime.stdout)
        instance_initialized = init.returncode == 0 and init_payload.get("status") in {"pass", "pass_with_warnings"}
        instance_validated = validate.returncode == 0 and validate_payload.get("status") in {"pass", "pass_with_warnings"}
        runtime_status_passed = runtime.returncode == 0 and runtime_payload.get("status") in {"pass", "pass_with_warnings"}
        committed_state = committed_instance_state(checkout, instance)
        status = "pass" if instance_initialized and instance_validated and runtime_status_passed and not hidden_state_copied and not committed_state else "fail"
        warnings: list[str] = []
        if skipped_state:
            warnings.append("forbidden local state was present in source repo and skipped during clean copy")
        if skip_clone:
            warnings.append("skip-clone mode uses the current repo and is a dry validation posture")
        if include_smoke and smoke_result and smoke_result.get("status") != "pass":
            status = "pass_with_warnings" if smoke_result.get("status") == "pass_with_warnings" and status == "pass" else "fail"
        return {
            "schema_version": "local_clean_machine_bootstrap_result.v0",
            "task": TASK_ID,
            "status": "pass_with_warnings" if warnings and status == "pass" else status,
            "created_at": utc_now(),
            "source_repo": str(source_repo),
            "temp_parent": str(temp_parent),
            "temp_checkout": str(checkout),
            "instance": str(instance),
            "temp_checkout_created": not skip_clone,
            "skip_clone": bool(skip_clone),
            "instance_initialized": instance_initialized,
            "instance_validated": instance_validated,
            "runtime_status_passed": runtime_status_passed,
            "hidden_state_copied": bool(hidden_state_copied),
            "forbidden_state_skipped": skipped_state,
            "committed_instance_state_found": bool(committed_state),
            "committed_instance_state_paths": committed_state,
            "smoke_included": bool(include_smoke),
            "smoke_result": smoke_result,
            "commands": commands,
            "deployment_performed": False,
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
            "warnings": warnings,
            "limitations": [
                "temp checkout proof is local reproducibility evidence",
                "actual second-machine proof is not implied",
            ],
        }
    finally:
        if cleanup and not skip_clone:
            shutil.rmtree(temp_parent, ignore_errors=True)
            cleaned = True
        if cleanup and cleaned:
            pass


def copy_clean_repo(source: Path, destination: Path) -> None:
    if is_relative_to(destination.resolve(), source.resolve()):
        raise ValueError("workdir must not place the temp checkout inside the source repo")
    shutil.copytree(source, destination, ignore=ignore_forbidden_state)


def ignore_forbidden_state(directory: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        if name == ".git" or name in FORBIDDEN_STATE_NAMES or name in FORBIDDEN_STATE_FILES:
            ignored.add(name)
    return ignored


def detect_forbidden_state(repo: Path) -> list[str]:
    found: list[str] = []
    for name in sorted(FORBIDDEN_STATE_NAMES | FORBIDDEN_STATE_FILES | {".git"}):
        if (repo / name).exists() and name != ".git":
            found.append(name)
    return found


def forbidden_state_exists(checkout: Path) -> bool:
    for name in FORBIDDEN_STATE_NAMES | FORBIDDEN_STATE_FILES:
        if (checkout / name).exists():
            return True
    return False


def run_script(repo: Path, *args: str, timeout: int = 180) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=repo, text=True, capture_output=True, check=False, timeout=timeout)


def command_record(name: str, completed: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    payload = parse_json(completed.stdout)
    return {
        "name": name,
        "returncode": completed.returncode,
        "status": payload.get("status", "unknown") if isinstance(payload, dict) else "unknown",
        "schema_version": payload.get("schema_version") if isinstance(payload, dict) else None,
    }


def parse_json(text: str) -> dict[str, Any]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def committed_instance_state(repo: Path, instance: Path) -> list[str]:
    try:
        rel = instance.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return []
    completed = subprocess.run(["git", "ls-files", "--", rel], cwd=repo, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        return []
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def fail_result(code: str, message: str) -> dict[str, Any]:
    return {
        "schema_version": "local_clean_machine_bootstrap_result.v0",
        "task": TASK_ID,
        "status": "fail",
        "error": code,
        "message": message,
        "temp_checkout_created": False,
        "instance_initialized": False,
        "instance_validated": False,
        "runtime_status_passed": False,
        "hidden_state_copied": False,
        "committed_instance_state_found": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def emit_result(result: dict[str, Any], as_json: bool, output: str | None, stdout: TextIO) -> None:
    if output:
        write_json(Path(output), result)
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
        return
    print(f"status: {result['status']}", file=stdout)
    print(f"temp_checkout_created: {result.get('temp_checkout_created')}", file=stdout)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run localhost smoke checks for an explicit clean-machine instance."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


TASK_ID = "LOCAL-13"


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--instance", required=True)
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)

    try:
        result = run_smoke(repo=Path(args.repo), instance=Path(args.instance), port=args.port)
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        result = fail_result("clean_machine_smoke_failed", str(exc))
        print(f"ERROR: {exc}", file=stderr)
    emit_result(result, args.json, args.output, stdout)
    return 0 if result.get("status") in {"pass", "pass_with_warnings"} else 1


def run_smoke(*, repo: Path, instance: Path, port: int) -> dict[str, Any]:
    repo_root = repo.resolve()
    if not repo_root.is_dir():
        raise ValueError(f"repo does not exist: {repo_root}")
    instance_path = instance if instance.is_absolute() else repo_root / instance
    commands: list[dict[str, Any]] = []

    init = run_script(repo_root, "scripts/eureka_init_instance.py", "--instance", str(instance_path), "--json")
    commands.append(command_record("init_instance", init))
    validate_before = run_script(repo_root, "scripts/eureka_validate_instance.py", "--instance", str(instance_path), "--json")
    commands.append(command_record("validate_instance_before_smoke", validate_before))
    runtime_status = run_script(repo_root, "scripts/eureka_local_runtime_status.py", "--instance", str(instance_path), "--read-only", "--json")
    commands.append(command_record("runtime_status", runtime_status))

    process, startup = start_server(repo_root, instance_path, port)
    actual_port = int(startup.get("port", port))
    base_url = f"http://127.0.0.1:{actual_port}"
    service_smoke: dict[str, Any] = {}
    workbench_smoke: dict[str, Any] = {}
    auto_test: dict[str, Any] = {}
    auto_search: dict[str, Any] = {}
    try:
        service = run_script(repo_root, "scripts/eureka_local_service_smoke.py", "--base-url", base_url, "--json", timeout=120)
        commands.append(command_record("service_smoke", service))
        service_smoke = parse_json(service.stdout)
        workbench = run_script(repo_root, "scripts/eureka_local_workbench_smoke.py", "--base-url", base_url, "--json", timeout=120)
        commands.append(command_record("workbench_smoke", workbench))
        workbench_smoke = parse_json(workbench.stdout)
        auto = run_script(repo_root, "scripts/eureka_local_auto_test.py", "--base-url", base_url, "--json", timeout=180)
        commands.append(command_record("auto_test", auto))
        auto_test = parse_json(auto.stdout)
        search = run_script(repo_root, "scripts/eureka_local_auto_search.py", "--base-url", base_url, "--json", timeout=120)
        commands.append(command_record("auto_search", search))
        auto_search = parse_json(search.stdout)
    finally:
        stop_server(process)

    validate_after = run_script(repo_root, "scripts/eureka_validate_instance.py", "--instance", str(instance_path), "--json")
    commands.append(command_record("validate_instance_after_shutdown", validate_after))
    shutdown = run_script(repo_root, "scripts/eureka_lan_shutdown_check.py", "--instance", str(instance_path), "--port", str(actual_port), "--json")
    commands.append(command_record("shutdown_check", shutdown))
    shutdown_payload = parse_json(shutdown.stdout)

    site_dist_mutated = bool(git_status_paths(repo_root, "site/dist"))
    master_index_mutated = bool(git_status_paths(repo_root, "data/public_index"))
    committed_state = committed_instance_state(repo_root, instance_path)
    ok = all(
        (
            init.returncode == 0,
            validate_before.returncode == 0,
            runtime_status.returncode == 0,
            service_smoke.get("status") == "pass",
            workbench_smoke.get("status") == "pass",
            auto_test.get("status") == "pass",
            auto_search.get("status") == "pass",
            validate_after.returncode == 0,
            shutdown_payload.get("status") == "pass",
            not site_dist_mutated,
            not master_index_mutated,
            not committed_state,
        )
    )
    return {
        "schema_version": "local_clean_machine_smoke_result.v0",
        "task": TASK_ID,
        "status": "pass" if ok else "fail",
        "repo": str(repo_root),
        "instance": str(instance_path),
        "base_url": base_url,
        "localhost_server_started": startup.get("status") == "pass",
        "service_smoke_passed": service_smoke.get("status") == "pass",
        "workbench_smoke_passed": workbench_smoke.get("status") == "pass",
        "auto_test_passed": auto_test.get("status") == "pass",
        "auto_search_passed": auto_search.get("status") == "pass",
        "server_shutdown_clean": shutdown_payload.get("status") == "pass",
        "instance_valid_after_shutdown": validate_after.returncode == 0 and parse_json(validate_after.stdout).get("status") in {"pass", "pass_with_warnings"},
        "runtime_status_passed": runtime_status.returncode == 0 and parse_json(runtime_status.stdout).get("status") in {"pass", "pass_with_warnings"},
        "committed_instance_state_found": bool(committed_state),
        "committed_instance_state_paths": committed_state,
        "site_dist_mutated": site_dist_mutated,
        "master_index_mutated": master_index_mutated,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "service_smoke": service_smoke,
        "workbench_smoke": workbench_smoke,
        "auto_test": summarize_report(auto_test),
        "auto_search": summarize_report(auto_search),
        "shutdown": shutdown_payload,
        "commands": commands,
        "warnings": [],
        "limitations": ["localhost smoke is not public hosting or second-machine proof"],
    }


def start_server(repo: Path, instance: Path, port: int) -> tuple[subprocess.Popen[str], dict[str, Any]]:
    process = subprocess.Popen(
        [
            sys.executable,
            "scripts/eureka_local_server.py",
            "--instance",
            str(instance),
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--json-startup",
        ],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    line = process.stdout.readline() if process.stdout else ""
    startup = parse_json(line)
    if startup.get("status") != "pass":
        stderr = process.stderr.read() if process.stderr else ""
        stop_server(process)
        raise ValueError(f"server did not start: {line or stderr}")
    return process, startup


def stop_server(process: subprocess.Popen[str]) -> None:
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
    if process.stdout:
        process.stdout.close()
    if process.stderr:
        process.stderr.close()


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


def summarize_report(payload: dict[str, Any]) -> dict[str, Any]:
    keys = ("schema_version", "status", "case_count", "passed_case_count", "query_count", "passed_query_count")
    return {key: payload[key] for key in keys if key in payload}


def git_status_paths(repo: Path, path: str) -> list[str]:
    completed = subprocess.run(["git", "status", "--short", "--", path], cwd=repo, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        return []
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


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
        "schema_version": "local_clean_machine_smoke_result.v0",
        "task": TASK_ID,
        "status": "fail",
        "error": code,
        "message": message,
        "localhost_server_started": False,
        "service_smoke_passed": False,
        "workbench_smoke_passed": False,
        "auto_test_passed": False,
        "auto_search_passed": False,
        "server_shutdown_clean": False,
        "instance_valid_after_shutdown": False,
        "site_dist_mutated": False,
        "master_index_mutated": False,
        "deployment_performed": False,
    }


def emit_result(result: dict[str, Any], as_json: bool, output: str | None, stdout: TextIO) -> None:
    if output:
        write_json(Path(output), result)
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
        return
    print(f"status: {result['status']}", file=stdout)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())

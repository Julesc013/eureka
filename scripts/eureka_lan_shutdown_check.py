#!/usr/bin/env python3
"""Check LOCAL LAN smoke shutdown and cleanup posture."""

from __future__ import annotations

import argparse
import json
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO
from urllib.error import URLError
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)

    try:
        result = run_shutdown_check(Path(args.instance), args.port)
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        result = {
            "schema_version": "local_lan_shutdown_result.v0",
            "status": "fail",
            "error": "shutdown_check_failed",
            "message": str(exc),
            "instance_valid": False,
            "server_stopped": False,
            "deployment_performed": False,
        }
        print(f"ERROR: {exc}", file=stderr)
    emit_result(result, args.json, args.output, stdout)
    return 0 if result.get("status") == "pass" else 1


def run_shutdown_check(instance: Path, port: int) -> dict[str, Any]:
    instance_result = run_cmd("scripts/eureka_validate_instance.py", "--instance", str(instance), "--json")
    instance_valid = False
    try:
        instance_payload = json.loads(instance_result.stdout)
        instance_valid = instance_payload.get("status") in {"pass", "pass_with_warnings"}
    except json.JSONDecodeError:
        instance_payload = {"status": "fail", "error": "invalid validation output"}
    server_stopped = not is_eureka_serving(port)
    port_reusable = can_bind_port(port)
    local_state_clean = no_committed_instance_state(instance)
    status = "pass" if instance_valid and server_stopped and port_reusable and local_state_clean else "fail"
    return {
        "schema_version": "local_lan_shutdown_result.v0",
        "task": "LOCAL-12",
        "status": status,
        "instance": str(instance),
        "port": port,
        "graceful_shutdown_required": True,
        "server_process_cleanup_required": True,
        "server_stopped": server_stopped,
        "port_reuse_or_cleanup_checked": True,
        "port_reusable": port_reusable,
        "instance_left_valid_after_shutdown": instance_valid,
        "instance_valid": instance_valid,
        "working_tree_clean_after_shutdown": local_state_clean,
        "committed_local_state_found": not local_state_clean,
        "logs_may_be_written_only_under_instance": True,
        "committed_local_state_forbidden": True,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "validation": instance_payload,
        "warnings": [] if status == "pass" else ["shutdown cleanup check found a blocker"],
        "limitations": ["port cleanup is checked from the local smoke host"],
    }


def is_eureka_serving(port: int) -> bool:
    if port <= 0:
        return False
    request = Request(f"http://127.0.0.1:{port}/api/v1/status", method="GET", headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=1) as response:
            body = response.read().decode("utf-8")
    except Exception:
        return False
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return False
    return str(payload.get("schema_version", "")).startswith("local_http_")


def can_bind_port(port: int) -> bool:
    if port <= 0:
        return True
    sock = socket.socket()
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.0.1", int(port)))
        return True
    except OSError:
        return False
    finally:
        sock.close()


def no_committed_instance_state(instance: Path) -> bool:
    try:
        rel = instance.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return True
    tracked = subprocess.run(["git", "ls-files", "--", rel], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    if tracked.stdout.strip():
        return False
    visible = subprocess.run(["git", "status", "--short", "--", rel], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return not visible.stdout.strip()


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=REPO_ROOT, text=True, capture_output=True, check=False, timeout=120)


def emit_result(result: dict[str, Any], as_json: bool, output: str | None, stdout: TextIO) -> None:
    if output:
        write_json(Path(output), result)
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
        return
    print(f"status: {result['status']}", file=stdout)
    print(f"server_stopped: {result.get('server_stopped')}", file=stdout)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())

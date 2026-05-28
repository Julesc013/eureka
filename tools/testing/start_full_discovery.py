#!/usr/bin/env python3
"""Start full unittest discovery in the background and return immediately."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.testing.run_full_unittest_discovery import (  # noqa: E402
    DEFAULT_HEARTBEAT_SECONDS,
    DEFAULT_TIMEOUT_SECONDS,
    discovery_artifact_paths,
    file_size,
    normalize_output_dir,
    output_dir_for_run_id,
    write_json_atomic,
)


_REAPER_THREADS: list[threading.Thread] = []


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True, help="Run directory name under ../eureka-test-runs/")
    parser.add_argument("--out", help="Explicit output directory; defaults to ../eureka-test-runs/<run-id>")
    parser.add_argument("--allow-repo-local-output", action="store_true")
    parser.add_argument("--start-dir", default="tests")
    parser.add_argument("--top-level-dir", default=".")
    parser.add_argument("--pattern", default="test*.py")
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--heartbeat-seconds", type=int, default=DEFAULT_HEARTBEAT_SECONDS)
    parser.add_argument("--quiet", action="store_true", help="Suppress harness progress output in harness stderr.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable start metadata.")
    args = parser.parse_args(argv)
    if args.heartbeat_seconds < 1:
        parser.error("--heartbeat-seconds must be at least 1")

    try:
        out_dir = normalize_output_dir(
            Path(args.out) if args.out else output_dir_for_run_id(args.run_id),
            args.allow_repo_local_output,
        )
    except ValueError as exc:
        parser.error(str(exc))

    try:
        metadata = start_discovery(args=args, out_dir=out_dir)
    except RuntimeError as exc:
        print(f"start_full_discovery: {exc}", file=stderr)
        return 2

    if args.json:
        print(json.dumps(metadata, indent=2, sort_keys=True), file=stdout)
    else:
        print("Started:", file=stdout)
        print(f"  run_id: {metadata['run_id']}", file=stdout)
        print(f"  pid: {metadata['pid']}", file=stdout)
        print(f"  out: {metadata['out_dir']}", file=stdout)
        print(f"  status: {metadata['status_path']}", file=stdout)
        print(f"  harness_stdout: {metadata['harness_stdout_path']}", file=stdout)
        print(f"  harness_stderr: {metadata['harness_stderr_path']}", file=stdout)
        print("", file=stdout)
        print("Check:", file=stdout)
        print(f"  python scripts/check_full_discovery.py --run-id {metadata['run_id']}", file=stdout)
        print("", file=stdout)
        print("Watch to completion:", file=stdout)
        print(
            f"  python scripts/check_full_discovery.py --run-id {metadata['run_id']} --watch --interval-seconds 300 --handoff",
            file=stdout,
        )
    return 0


def start_discovery(*, args: argparse.Namespace, out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    artifacts = discovery_artifact_paths(out_dir)
    harness_stdout_path = out_dir / "harness_stdout.txt"
    harness_stderr_path = out_dir / "harness_stderr.txt"
    existing = read_json(artifacts["status_path"])
    if existing and existing.get("status") in {"starting", "running"} and pid_is_running(existing.get("pid")):
        raise RuntimeError(f"run already appears active at {artifacts['status_path']}")

    command = [
        sys.executable,
        str(REPO_ROOT / "scripts/run_full_unittest_discovery.py"),
        "--run-id",
        args.run_id,
        "--out",
        str(out_dir),
        "--start-dir",
        args.start_dir,
        "--top-level-dir",
        args.top_level_dir,
        "--pattern",
        args.pattern,
        "--timeout-seconds",
        str(args.timeout_seconds),
        "--heartbeat-seconds",
        str(args.heartbeat_seconds),
    ]
    if args.allow_repo_local_output:
        command.append("--allow-repo-local-output")
    if args.quiet:
        command.append("--quiet")

    started_at = now_utc()
    write_json_atomic(
        artifacts["status_path"],
        {
            "schema_version": "full_discovery_status.v0",
            "run_id": args.run_id,
            "status": "starting",
            "pid": None,
            "command": " ".join(command),
            "started_at": started_at,
            "updated_at": started_at,
            "elapsed_seconds": 0,
            "stdout_path": str(artifacts["stdout_path"]),
            "stderr_path": str(artifacts["stderr_path"]),
            "stdout_bytes": file_size(artifacts["stdout_path"]),
            "stderr_bytes": file_size(artifacts["stderr_path"]),
            "exit_code": None,
            "summary_path": str(artifacts["summary_path"]),
            "failure_families_path": str(artifacts["failure_families_path"]),
            "failed_tests_path": str(artifacts["failed_tests_path"]),
            "harness_stdout_path": str(harness_stdout_path),
            "harness_stderr_path": str(harness_stderr_path),
        },
    )

    creationflags = 0
    start_new_session = False
    if os.name == "nt":
        creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    else:
        start_new_session = True

    with harness_stdout_path.open("w", encoding="utf-8") as out, harness_stderr_path.open("w", encoding="utf-8") as err:
        process = subprocess.Popen(
            command,
            cwd=REPO_ROOT,
            stdout=out,
            stderr=err,
            text=True,
            creationflags=creationflags,
            start_new_session=start_new_session,
        )
        status = read_json(artifacts["status_path"]) or {}
        if status.get("status") not in {"pass", "fail", "error", "cancelled", "timeout"}:
            status.update({"status": "running", "pid": process.pid, "updated_at": now_utc()})
            write_json_atomic(artifacts["status_path"], status)
    track_detached_process(process)

    metadata = {
        "schema_version": "full_discovery_start.v0",
        "run_id": args.run_id,
        "pid": process.pid,
        "out_dir": str(out_dir),
        "status_path": str(artifacts["status_path"]),
        "summary_path": str(artifacts["summary_path"]),
        "failure_families_path": str(artifacts["failure_families_path"]),
        "failed_tests_path": str(artifacts["failed_tests_path"]),
        "harness_stdout_path": str(harness_stdout_path),
        "harness_stderr_path": str(harness_stderr_path),
        "command": command,
    }
    return metadata


def track_detached_process(process: subprocess.Popen[str]) -> None:
    def reap() -> None:
        process.wait()

    thread = threading.Thread(target=reap, name=f"full-discovery-reaper-{process.pid}", daemon=True)
    thread.start()
    _REAPER_THREADS.append(thread)


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None


def pid_is_running(pid: object) -> bool:
    try:
        value = int(pid)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return False
    if value <= 0:
        return False
    if os.name == "nt":
        completed = subprocess.run(
            ["tasklist", "/FI", f"PID eq {value}", "/FO", "CSV", "/NH"],
            text=True,
            capture_output=True,
            check=False,
        )
        return str(value) in completed.stdout
    try:
        os.kill(value, 0)
    except OSError:
        return False
    return True


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Check status for a background or foreground full unittest discovery run."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WATCH_INTERVAL_SECONDS = 300.0
TERMINAL_STATUSES = {"pass", "fail", "error", "cancelled", "timeout"}
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.testing.run_full_unittest_discovery import (  # noqa: E402
    discovery_artifact_paths,
    format_duration,
    normalize_output_dir,
    output_dir_for_run_id,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", help="Run directory name under ../eureka-test-runs/")
    parser.add_argument("--out", help="Explicit output directory.")
    parser.add_argument("--allow-repo-local-output", action="store_true")
    parser.add_argument("--json", action="store_true", help="Print machine-readable status.")
    parser.add_argument("--watch", action="store_true", help="Wait until the run reaches a terminal status.")
    parser.add_argument(
        "--interval-seconds",
        type=float,
        default=DEFAULT_WATCH_INTERVAL_SECONDS,
        help="Seconds between watch updates; defaults to 300.",
    )
    parser.add_argument("--handoff", action="store_true", help="Print compact paste-ready handoff artifacts when complete.")
    args = parser.parse_args(argv)
    if not args.run_id and not args.out:
        parser.error("one of --run-id or --out is required")
    if args.interval_seconds <= 0:
        parser.error("--interval-seconds must be greater than 0")

    try:
        out_dir = normalize_output_dir(
            Path(args.out) if args.out else output_dir_for_run_id(str(args.run_id)),
            args.allow_repo_local_output,
        )
    except ValueError as exc:
        parser.error(str(exc))

    if args.watch:
        try:
            payload = watch_status(
                out_dir=out_dir,
                interval_seconds=args.interval_seconds,
                stdout=stdout,
                stderr=stderr,
            )
        except FileNotFoundError as exc:
            print(f"check_full_discovery: {exc}", file=stderr)
            return 2
        if args.handoff:
            print_handoff(payload, stdout=stdout)
        return status_exit_code(payload)

    try:
        payload = load_status(out_dir)
    except FileNotFoundError as exc:
        print(f"check_full_discovery: {exc}", file=stderr)
        return 2

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)
    else:
        print_status(payload, stdout=stdout)
        if args.handoff and is_terminal(payload):
            print_handoff(payload, stdout=stdout)
    return status_exit_code(payload) if args.handoff and is_terminal(payload) else 0


def load_status(out_dir: Path) -> dict[str, Any]:
    artifacts = discovery_artifact_paths(out_dir)
    status_path = artifacts["status_path"]
    try:
        status = json.loads(status_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        summary_path = artifacts["summary_path"]
        if not summary_path.exists():
            raise FileNotFoundError(f"no status.json or full_unittest_summary.json found under {out_dir}")
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        status = status_from_summary(summary=summary, artifacts=artifacts, out_dir=out_dir)
    summary = read_json(Path(status.get("summary_path") or artifacts["summary_path"]))
    if summary:
        counts = summary.get("counts") or {}
        status.update(
            {
                "status": summary.get("status") or status.get("status"),
                "tests_run": counts.get("tests_run"),
                "failures": counts.get("failures"),
                "errors": counts.get("errors"),
                "summary_exit_code": summary.get("exit_code"),
            }
        )
    return status


def watch_status(
    *,
    out_dir: Path,
    interval_seconds: float = DEFAULT_WATCH_INTERVAL_SECONDS,
    stdout: TextIO,
    stderr: TextIO,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    last_line = ""
    while True:
        payload = load_status(out_dir)
        line = watch_line(payload)
        if line != last_line:
            print(line, file=stdout, flush=True)
            last_line = line
        if is_terminal(payload):
            print_status(payload, stdout=stdout)
            return payload
        sleep(interval_seconds)


def watch_line(payload: dict[str, Any]) -> str:
    return (
        "[full-discovery] "
        f"status={payload.get('status')} "
        f"elapsed={format_duration(float(payload.get('elapsed_seconds') or 0))} "
        f"pid={payload.get('pid')} "
        f"stdout_bytes={payload.get('stdout_bytes')} "
        f"stderr_bytes={payload.get('stderr_bytes')} "
        f"updated_at={payload.get('updated_at')}"
    )


def is_terminal(payload: dict[str, Any]) -> bool:
    return str(payload.get("status") or "").lower() in TERMINAL_STATUSES


def status_exit_code(payload: dict[str, Any]) -> int:
    return 0 if str(payload.get("status") or "").lower() == "pass" else 1


def status_from_summary(*, summary: dict[str, Any], artifacts: dict[str, Path], out_dir: Path) -> dict[str, Any]:
    counts = summary.get("counts") or {}
    return {
        "schema_version": "full_discovery_status.v0",
        "run_id": out_dir.name,
        "status": summary.get("status"),
        "pid": None,
        "command": summary.get("command"),
        "started_at": summary.get("started_at"),
        "updated_at": summary.get("finished_at"),
        "elapsed_seconds": summary.get("duration_seconds"),
        "stdout_path": str(artifacts["stdout_path"]),
        "stderr_path": str(artifacts["stderr_path"]),
        "stdout_bytes": byte_count(artifacts["stdout_path"]),
        "stderr_bytes": byte_count(artifacts["stderr_path"]),
        "exit_code": summary.get("exit_code"),
        "summary_path": str(artifacts["summary_path"]),
        "failure_families_path": str(artifacts["failure_families_path"]),
        "failed_tests_path": str(artifacts["failed_tests_path"]),
        "tests_run": counts.get("tests_run"),
        "failures": counts.get("failures"),
        "errors": counts.get("errors"),
    }


def print_status(payload: dict[str, Any], *, stdout: TextIO) -> None:
    print(f"status: {payload.get('status')}", file=stdout)
    print(f"run_id: {payload.get('run_id')}", file=stdout)
    print(f"elapsed: {format_duration(float(payload.get('elapsed_seconds') or 0))}", file=stdout)
    print(f"pid: {payload.get('pid')}", file=stdout)
    print(f"stdout_bytes: {payload.get('stdout_bytes')}", file=stdout)
    print(f"stderr_bytes: {payload.get('stderr_bytes')}", file=stdout)
    print(f"last_update: {payload.get('updated_at')}", file=stdout)
    if payload.get("tests_run") is not None:
        print(f"tests_run: {payload.get('tests_run')}", file=stdout)
        print(f"failures: {payload.get('failures')}", file=stdout)
        print(f"errors: {payload.get('errors')}", file=stdout)
    if payload.get("exit_code") is not None:
        print(f"exit_code: {payload.get('exit_code')}", file=stdout)
    print(f"summary: {payload.get('summary_path')}", file=stdout)
    print(f"failure_families: {payload.get('failure_families_path')}", file=stdout)
    print(f"failed_tests: {payload.get('failed_tests_path')}", file=stdout)


def print_handoff(payload: dict[str, Any], *, stdout: TextIO) -> None:
    print("", file=stdout)
    print("=== full_unittest_summary.json ===", file=stdout)
    print(read_text(Path(str(payload.get("summary_path") or ""))), file=stdout)
    print("=== failure_families.json ===", file=stdout)
    print(read_text(Path(str(payload.get("failure_families_path") or ""))), file=stdout)
    print("=== failed_tests.txt ===", file=stdout)
    print(read_text(Path(str(payload.get("failed_tests_path") or ""))), file=stdout)
    print("=== git status --short --branch ===", file=stdout)
    print(git_status_short(), file=stdout)


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").rstrip()
    except OSError:
        return f"<missing: {path}>"


def git_status_short() -> str:
    completed = subprocess.run(
        ["git", "status", "--short", "--branch"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return completed.stderr.strip() or f"git status failed with exit code {completed.returncode}"
    return completed.stdout.rstrip()


def byte_count(path: Path) -> int:
    try:
        return path.stat().st_size
    except FileNotFoundError:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())

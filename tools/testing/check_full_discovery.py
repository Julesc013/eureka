#!/usr/bin/env python3
"""Check status for a background or foreground full unittest discovery run."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
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
    args = parser.parse_args(argv)
    if not args.run_id and not args.out:
        parser.error("one of --run-id or --out is required")

    try:
        out_dir = normalize_output_dir(
            Path(args.out) if args.out else output_dir_for_run_id(str(args.run_id)),
            args.allow_repo_local_output,
        )
    except ValueError as exc:
        parser.error(str(exc))

    try:
        payload = load_status(out_dir)
    except FileNotFoundError as exc:
        print(f"check_full_discovery: {exc}", file=stderr)
        return 2

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)
    else:
        print_status(payload, stdout=stdout)
    return 0


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


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None


def byte_count(path: Path) -> int:
    try:
        return path.stat().st_size
    except FileNotFoundError:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run unittest discovery into external artifacts and a compact JSON summary."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TIMEOUT_SECONDS = 7200

sys.path.insert(0, str(REPO_ROOT))
from tools.reporters.summarize_unittest_log import summarize_paths, write_json  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", help="Output directory; defaults to .aide.local/test-runs/<timestamp>")
    parser.add_argument("--start-dir", default="tests", help="unittest discover -s value")
    parser.add_argument("--top-level-dir", default=".", help="unittest discover -t value")
    parser.add_argument("--pattern", default="test*.py", help="unittest discover -p value")
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--paths-touched-file")
    parser.add_argument("--no-fail-exit", action="store_true")
    args = parser.parse_args(argv)

    out_dir = Path(args.out) if args.out else default_output_dir()
    result = run_discovery(
        out_dir=out_dir,
        start_dir=args.start_dir,
        top_level_dir=args.top_level_dir,
        pattern=args.pattern,
        timeout_seconds=args.timeout_seconds,
        paths_touched_file=Path(args.paths_touched_file) if args.paths_touched_file else None,
    )
    print(
        json.dumps(
            {
                "output_dir": str(out_dir),
                "summary": str(result["summary_path"]),
                "exit_code": result["exit_code"],
            },
            indent=2,
        ),
        file=stdout,
    )
    if args.no_fail_exit:
        return 0
    return int(result["exit_code"])


def run_discovery(
    *,
    out_dir: Path,
    start_dir: str = "tests",
    top_level_dir: str = ".",
    pattern: str = "test*.py",
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    paths_touched_file: Path | None = None,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = out_dir / "full_unittest_stdout.txt"
    stderr_path = out_dir / "full_unittest_stderr.txt"
    exit_code_path = out_dir / "full_unittest_exit_code.txt"
    environment_path = out_dir / "environment.json"
    summary_path = out_dir / "full_unittest_summary.json"
    families_path = out_dir / "failure_families.json"
    failed_tests_path = out_dir / "failed_tests.txt"
    paths_touched_path = paths_touched_file or out_dir / "paths_touched.txt"
    if not paths_touched_path.exists():
        write_paths_touched(paths_touched_path)

    command = [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        start_dir,
        "-t",
        top_level_dir,
        "-p",
        pattern,
    ]
    display_command = command_display(start_dir=start_dir, top_level_dir=top_level_dir, pattern=pattern)
    started_at = now_utc()
    start_time = dt.datetime.now(dt.timezone.utc)
    timed_out = False
    with stdout_path.open("w", encoding="utf-8") as out, stderr_path.open("w", encoding="utf-8") as err:
        process = subprocess.Popen(command, cwd=REPO_ROOT, stdout=out, stderr=err, text=True)
        try:
            exit_code = process.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            process.kill()
            process.wait()
            err.write(f"\nTIMEOUT: unittest discovery exceeded {timeout_seconds} seconds\n")
            exit_code = 124

    finished_at = now_utc()
    duration_seconds = (dt.datetime.now(dt.timezone.utc) - start_time).total_seconds()
    exit_code_path.write_text(f"{exit_code}\n", encoding="utf-8")
    environment = environment_payload(
        command=display_command,
        start_dir=start_dir,
        top_level_dir=top_level_dir,
        pattern=pattern,
        timeout_seconds=timeout_seconds,
        timed_out=timed_out,
    )
    write_json(environment_path, environment)
    git = environment["git"]
    summary = summarize_paths(
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        exit_code_path=exit_code_path,
        command=display_command,
        started_at=started_at,
        finished_at=finished_at,
        duration_seconds=duration_seconds,
        environment_path=environment_path,
        git_branch=git.get("branch"),
        git_head=git.get("head"),
        git_working_tree_clean=git.get("working_tree_clean"),
        generated_by="scripts/run_full_unittest_discovery.py",
    )
    if timed_out:
        summary["status"] = "timeout"
    summary["paths_touched_path"] = str(paths_touched_path)
    summary["paths_touched"] = read_lines(paths_touched_path)
    write_json(summary_path, summary)
    write_json(families_path, {"schema_version": "failure_family_list.v0", "failure_families": summary["failure_families"]})
    failed_tests_path.write_text("\n".join(summary["failed_tests"]) + ("\n" if summary["failed_tests"] else ""), encoding="utf-8")
    return {
        "exit_code": exit_code,
        "summary_path": summary_path,
        "stdout_path": stdout_path,
        "stderr_path": stderr_path,
        "environment_path": environment_path,
        "paths_touched_path": paths_touched_path,
    }


def default_output_dir() -> Path:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return REPO_ROOT / ".aide.local" / "test-runs" / stamp


def command_display(*, start_dir: str, top_level_dir: str, pattern: str) -> str:
    base = f"python -m unittest discover -s {start_dir} -t {top_level_dir}"
    if pattern != "test*.py":
        base = f"{base} -p {pattern}"
    return base


def environment_payload(
    *,
    command: str,
    start_dir: str,
    top_level_dir: str,
    pattern: str,
    timeout_seconds: int,
    timed_out: bool,
) -> dict[str, Any]:
    return {
        "schema_version": "full_unittest_environment.v0",
        "command": command,
        "cwd": str(REPO_ROOT),
        "python_executable": sys.executable,
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "start_dir": start_dir,
        "top_level_dir": top_level_dir,
        "pattern": pattern,
        "timeout_seconds": timeout_seconds,
        "timed_out": timed_out,
        "git": git_metadata(),
        "environment_variables_recorded": False,
        "secrets_recorded": False,
        "raw_live_source_responses_recorded": False,
    }


def git_metadata() -> dict[str, Any]:
    def git(*args: str) -> str | None:
        completed = subprocess.run(["git", *args], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
        if completed.returncode != 0:
            return None
        return completed.stdout.strip()

    status = git("status", "--short")
    return {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "working_tree_clean": status == "",
        "origin_main": git("rev-parse", "origin/main"),
        "origin_dev": git("rev-parse", "origin/dev"),
    }


def write_paths_touched(path: Path) -> None:
    paths: set[str] = set()
    for args in (
        ("diff", "--name-only"),
        ("diff", "--name-only", "--cached"),
        ("ls-files", "--others", "--exclude-standard"),
    ):
        completed = subprocess.run(["git", *args], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
        if completed.returncode == 0:
            paths.update(line.strip().replace("\\", "/") for line in completed.stdout.splitlines() if line.strip())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(sorted(paths)) + ("\n" if paths else ""), encoding="utf-8")


def read_lines(path: Path) -> list[str]:
    try:
        return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except FileNotFoundError:
        return []


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())

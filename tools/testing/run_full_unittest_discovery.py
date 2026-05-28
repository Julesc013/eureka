#!/usr/bin/env python3
"""Run unittest discovery into external artifacts and a compact JSON summary."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TIMEOUT_SECONDS = 7200
DEFAULT_HEARTBEAT_SECONDS = 30
DEFAULT_OUTPUT_ROOT_NAME = "eureka-test-runs"
STATUS_SCHEMA_VERSION = "full_discovery_status.v0"
FORBIDDEN_REPO_LOCAL_OUTPUT_ROOTS = {
    ".aide.local",
    ".cache",
    ".local",
    "eureka-instance",
    "secrets",
}

sys.path.insert(0, str(REPO_ROOT))
from tools.reporters.summarize_unittest_log import summarize_paths, write_json  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", help="Logical run id for status.json; defaults to output directory name.")
    parser.add_argument("--out", help="Output directory; defaults to ../eureka-test-runs/<timestamp>")
    parser.add_argument(
        "--allow-repo-local-output",
        action="store_true",
        help="Allow output below a forbidden repo-local private root for exceptional debugging.",
    )
    parser.add_argument("--start-dir", default="tests", help="unittest discover -s value")
    parser.add_argument("--top-level-dir", default=".", help="unittest discover -t value")
    parser.add_argument("--pattern", default="test*.py", help="unittest discover -p value")
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument(
        "--heartbeat-seconds",
        type=int,
        default=DEFAULT_HEARTBEAT_SECONDS,
        help="Emit a compact operator progress heartbeat this often while discovery runs.",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress operator progress output.")
    parser.add_argument("--no-progress", action="store_true", dest="quiet", help="Alias for --quiet.")
    parser.add_argument("--paths-touched-file")
    parser.add_argument("--no-fail-exit", action="store_true")
    args = parser.parse_args(argv)
    if args.heartbeat_seconds < 1:
        parser.error("--heartbeat-seconds must be at least 1")

    try:
        out_dir = normalize_output_dir(Path(args.out) if args.out else default_output_dir(), args.allow_repo_local_output)
    except ValueError as exc:
        parser.error(str(exc))
    result = run_discovery(
        out_dir=out_dir,
        start_dir=args.start_dir,
        top_level_dir=args.top_level_dir,
        pattern=args.pattern,
        timeout_seconds=args.timeout_seconds,
        heartbeat_seconds=args.heartbeat_seconds,
        run_id=args.run_id,
        paths_touched_file=Path(args.paths_touched_file) if args.paths_touched_file else None,
        progress_stream=None if args.quiet else sys.stderr,
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
    heartbeat_seconds: int = DEFAULT_HEARTBEAT_SECONDS,
    run_id: str | None = None,
    paths_touched_file: Path | None = None,
    allow_repo_local_output: bool = False,
    progress_stream: TextIO | None = None,
) -> dict[str, Any]:
    out_dir = normalize_output_dir(out_dir, allow_repo_local_output)
    out_dir.mkdir(parents=True, exist_ok=True)
    artifacts = discovery_artifact_paths(out_dir)
    stdout_path = artifacts["stdout_path"]
    stderr_path = artifacts["stderr_path"]
    exit_code_path = artifacts["exit_code_path"]
    environment_path = artifacts["environment_path"]
    summary_path = artifacts["summary_path"]
    families_path = artifacts["failure_families_path"]
    failed_tests_path = artifacts["failed_tests_path"]
    status_path = artifacts["status_path"]
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
    monotonic_start = time.monotonic()
    timed_out = False
    interrupted = False
    run_id = run_id or out_dir.name
    write_run_status(
        status_path=status_path,
        run_id=run_id,
        status="starting",
        pid=None,
        command=display_command,
        started_at=started_at,
        start_time=start_time,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        summary_path=summary_path,
        failure_families_path=families_path,
        failed_tests_path=failed_tests_path,
        exit_code=None,
    )
    emit_progress(progress_stream, f"run_id={run_id}")
    emit_progress(progress_stream, f"command={display_command}")
    emit_progress(progress_stream, f"output={out_dir}")
    emit_progress(progress_stream, f"stdout={stdout_path}")
    emit_progress(progress_stream, f"stderr={stderr_path}")
    with stdout_path.open("w", encoding="utf-8") as out, stderr_path.open("w", encoding="utf-8") as err:
        process = subprocess.Popen(command, cwd=REPO_ROOT, stdout=out, stderr=err, text=True)
        emit_progress(progress_stream, f"status=running pid={process.pid}")
        write_status = make_status_writer(
            status_path=status_path,
            run_id=run_id,
            command=display_command,
            started_at=started_at,
            start_time=start_time,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            summary_path=summary_path,
            failure_families_path=families_path,
            failed_tests_path=failed_tests_path,
        )
        write_status(status="running", pid=process.pid, exit_code=None)
        exit_code = wait_for_process_with_progress(
            process=process,
            timeout_seconds=timeout_seconds,
            heartbeat_seconds=heartbeat_seconds,
            started_monotonic=monotonic_start,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            progress_stream=progress_stream,
            status_writer=write_status,
        )
        if exit_code == 124:
            timed_out = True
            err.write(f"\nTIMEOUT: unittest discovery exceeded {timeout_seconds} seconds\n")
        elif exit_code == 130:
            interrupted = True
            err.write("\nINTERRUPTED: unittest discovery was stopped by operator\n")

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
        interrupted=interrupted,
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
    if interrupted:
        summary["status"] = "cancelled"
    summary["paths_touched_path"] = str(paths_touched_path)
    summary["paths_touched"] = read_lines(paths_touched_path)
    summary["status_path"] = str(status_path)
    write_json(summary_path, summary)
    write_json(families_path, {"schema_version": "failure_family_list.v0", "failure_families": summary["failure_families"]})
    failed_tests_path.write_text("\n".join(summary["failed_tests"]) + ("\n" if summary["failed_tests"] else ""), encoding="utf-8")
    write_run_status(
        status_path=status_path,
        run_id=run_id,
        status=str(summary.get("status") or "error"),
        pid=None,
        command=display_command,
        started_at=started_at,
        start_time=start_time,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        summary_path=summary_path,
        failure_families_path=families_path,
        failed_tests_path=failed_tests_path,
        exit_code=exit_code,
    )
    emit_progress(
        progress_stream,
        (
            "completed "
            f"status={summary.get('status')} tests={summary.get('counts', {}).get('tests_run')} "
            f"failures={summary.get('counts', {}).get('failures')} errors={summary.get('counts', {}).get('errors')} "
            f"duration={format_duration(duration_seconds)} exit_code={exit_code}"
        ),
    )
    emit_progress(progress_stream, f"summary={summary_path}")
    emit_progress(progress_stream, f"failure_families={families_path}")
    emit_progress(progress_stream, f"failed_tests={failed_tests_path}")
    emit_progress(progress_stream, f"status_file={status_path}")
    return {
        "exit_code": exit_code,
        "summary_path": summary_path,
        "stdout_path": stdout_path,
        "stderr_path": stderr_path,
        "environment_path": environment_path,
        "paths_touched_path": paths_touched_path,
        "status_path": status_path,
    }


def discovery_artifact_paths(out_dir: Path) -> dict[str, Path]:
    return {
        "stdout_path": out_dir / "full_unittest_stdout.txt",
        "stderr_path": out_dir / "full_unittest_stderr.txt",
        "exit_code_path": out_dir / "full_unittest_exit_code.txt",
        "environment_path": out_dir / "environment.json",
        "summary_path": out_dir / "full_unittest_summary.json",
        "failure_families_path": out_dir / "failure_families.json",
        "failed_tests_path": out_dir / "failed_tests.txt",
        "status_path": out_dir / "status.json",
    }


def make_status_writer(
    *,
    status_path: Path,
    run_id: str,
    command: str,
    started_at: str,
    start_time: dt.datetime,
    stdout_path: Path,
    stderr_path: Path,
    summary_path: Path,
    failure_families_path: Path,
    failed_tests_path: Path,
) -> Callable[[str, int | None, int | None], None]:
    def write(status: str, pid: int | None, exit_code: int | None) -> None:
        write_run_status(
            status_path=status_path,
            run_id=run_id,
            status=status,
            pid=pid,
            command=command,
            started_at=started_at,
            start_time=start_time,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            summary_path=summary_path,
            failure_families_path=failure_families_path,
            failed_tests_path=failed_tests_path,
            exit_code=exit_code,
        )

    return write


def write_run_status(
    *,
    status_path: Path,
    run_id: str,
    status: str,
    pid: int | None,
    command: str,
    started_at: str,
    start_time: dt.datetime,
    stdout_path: Path,
    stderr_path: Path,
    summary_path: Path,
    failure_families_path: Path,
    failed_tests_path: Path,
    exit_code: int | None,
) -> dict[str, Any]:
    now = dt.datetime.now(dt.timezone.utc)
    payload: dict[str, Any] = {
        "schema_version": STATUS_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "pid": pid,
        "command": command,
        "started_at": started_at,
        "updated_at": now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "elapsed_seconds": round((now - start_time).total_seconds(), 3),
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "stdout_bytes": file_size(stdout_path),
        "stderr_bytes": file_size(stderr_path),
        "exit_code": exit_code,
        "summary_path": str(summary_path),
        "failure_families_path": str(failure_families_path),
        "failed_tests_path": str(failed_tests_path),
    }
    write_json_atomic(status_path, payload)
    return payload


def write_json_atomic(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def wait_for_process_with_progress(
    *,
    process: subprocess.Popen[str],
    timeout_seconds: int,
    heartbeat_seconds: int,
    started_monotonic: float,
    stdout_path: Path,
    stderr_path: Path,
    progress_stream: TextIO | None,
    status_writer: Callable[[str, int | None, int | None], None] | None = None,
) -> int:
    deadline = started_monotonic + timeout_seconds
    next_heartbeat = started_monotonic + heartbeat_seconds
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            emit_progress(progress_stream, f"timeout reached after {format_duration(timeout_seconds)}; stopping child process")
            process.kill()
            process.wait()
            if status_writer:
                status_writer("timeout", process.pid, 124)
            return 124
        try:
            exit_code = process.wait(timeout=min(1.0, remaining))
        except subprocess.TimeoutExpired:
            now = time.monotonic()
            if now >= next_heartbeat:
                elapsed = now - started_monotonic
                emit_progress(
                    progress_stream,
                    (
                        f"running elapsed={format_duration(elapsed)} "
                        f"pid={process.pid} stdout={format_size(stdout_path)} stderr={format_size(stderr_path)}"
                    ),
                )
                if status_writer:
                    status_writer("running", process.pid, None)
                while next_heartbeat <= now:
                    next_heartbeat += heartbeat_seconds
            continue
        except KeyboardInterrupt:
            emit_progress(progress_stream, "interrupted by operator; stopping child test process")
            stop_process(process)
            if status_writer:
                status_writer("cancelled", process.pid, 130)
            return 130
        return int(exit_code)


def stop_process(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def emit_progress(stream: TextIO | None, message: str) -> None:
    if stream is None:
        return
    print(f"[full-discovery] {message}", file=stream, flush=True)


def format_duration(seconds: float) -> str:
    total = max(0, int(seconds))
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:d}:{secs:02d}"


def format_size(path: Path) -> str:
    size = file_size(path)
    units = ("B", "KiB", "MiB", "GiB")
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024


def file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except FileNotFoundError:
        return 0


def default_output_dir() -> Path:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return output_dir_for_run_id(stamp)


def output_dir_for_run_id(run_id: str) -> Path:
    normalized = run_id.strip().replace("\\", "/").strip("/")
    if not normalized or "/" in normalized or normalized in {".", ".."}:
        raise ValueError("run-id must be a single directory name")
    return REPO_ROOT.parent / DEFAULT_OUTPUT_ROOT_NAME / normalized


def normalize_output_dir(out_dir: Path, allow_repo_local_output: bool = False) -> Path:
    expanded = out_dir.expanduser()
    if not expanded.is_absolute():
        expanded = REPO_ROOT / expanded
    resolved = expanded.resolve()
    if allow_repo_local_output:
        return resolved
    rel = relative_to_repo(resolved)
    if rel is None:
        return resolved
    parts = rel.parts
    if not parts:
        raise ValueError(
            "refusing full-discovery output at repo root; use a sibling path such as "
            "../eureka-test-runs/<run-id> or pass --allow-repo-local-output for exceptional debugging"
        )
    first = parts[0]
    if first in FORBIDDEN_REPO_LOCAL_OUTPUT_ROOTS:
        raise ValueError(
            f"refusing full-discovery output inside repo-private root: {rel.as_posix()}; "
            "use ../eureka-test-runs/<run-id> or pass --allow-repo-local-output for exceptional debugging"
        )
    return resolved


def relative_to_repo(path: Path) -> Path | None:
    repo = REPO_ROOT.resolve()
    try:
        return path.relative_to(repo)
    except ValueError:
        try:
            common = os.path.commonpath([str(path), str(repo)])
        except ValueError:
            return None
        if common != str(repo):
            return None
        return Path(os.path.relpath(path, repo))


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
    interrupted: bool,
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
        "interrupted": interrupted,
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

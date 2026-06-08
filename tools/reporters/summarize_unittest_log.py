#!/usr/bin/env python3
"""Summarize unittest stdout/stderr logs into compact JSON for AI handoff."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_COMMAND = "python -m unittest discover -s tests -t ."
SECRET_PATTERNS = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)(api[_-]?key|token|secret)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{16,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stdout", required=True, dest="stdout_path")
    parser.add_argument("--stderr", required=True, dest="stderr_path")
    parser.add_argument("--exit-code-file", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--command", default=DEFAULT_COMMAND)
    parser.add_argument("--started-at")
    parser.add_argument("--finished-at")
    parser.add_argument("--duration-seconds", type=float)
    parser.add_argument("--environment")
    parser.add_argument("--git-branch")
    parser.add_argument("--git-head")
    parser.add_argument("--git-working-tree-clean")
    parser.add_argument("--generated-by", default="tools/reporters/summarize_unittest_log.py")
    args = parser.parse_args(argv)

    summary = summarize_paths(
        stdout_path=Path(args.stdout_path),
        stderr_path=Path(args.stderr_path),
        exit_code_path=Path(args.exit_code_file),
        command=args.command,
        started_at=args.started_at,
        finished_at=args.finished_at,
        duration_seconds=args.duration_seconds,
        environment_path=Path(args.environment) if args.environment else None,
        git_branch=args.git_branch,
        git_head=args.git_head,
        git_working_tree_clean=parse_optional_bool(args.git_working_tree_clean),
        generated_by=args.generated_by,
    )
    write_json(Path(args.out), summary)
    print(str(Path(args.out)), file=stdout)
    return 0


def summarize_paths(
    *,
    stdout_path: Path,
    stderr_path: Path,
    exit_code_path: Path,
    command: str = DEFAULT_COMMAND,
    started_at: str | None = None,
    finished_at: str | None = None,
    duration_seconds: float | None = None,
    environment_path: Path | None = None,
    git_branch: str | None = None,
    git_head: str | None = None,
    git_working_tree_clean: bool | None = None,
    generated_by: str = "tools/reporters/summarize_unittest_log.py",
) -> dict[str, Any]:
    stdout_text = read_text(stdout_path)
    stderr_text = read_text(stderr_path)
    exit_code = read_exit_code(exit_code_path)
    combined = "\n".join(part for part in (stdout_text, stderr_text) if part)
    redacted = redact_secrets(combined)
    counts = parse_counts(redacted)
    failures = extract_failure_blocks(redacted)
    failed_tests = sorted({failure["test"] for failure in failures if failure.get("test")})
    failed_modules = sorted({module for test in failed_tests for module in [module_from_test_name(test)] if module})
    families = group_failure_families(failures, first_seen_at=started_at or now_utc())
    return {
        "schema_version": "full_unittest_summary.v0",
        "command": command,
        "exit_code": exit_code,
        "status": infer_status(exit_code, counts, redacted),
        "started_at": started_at,
        "finished_at": finished_at or now_utc(),
        "duration_seconds": duration_seconds,
        "git": {
            "branch": git_branch,
            "head": git_head,
            "working_tree_clean": git_working_tree_clean,
        },
        "counts": counts,
        "failed_tests": failed_tests,
        "failed_modules": failed_modules,
        "failure_families": families,
        "stdout_path": display_path(stdout_path),
        "stderr_path": display_path(stderr_path),
        "exit_code_path": display_path(exit_code_path),
        "environment_path": display_path(environment_path) if environment_path else None,
        "path_classification": {
            "stdout_path": classify_path(stdout_path),
            "stderr_path": classify_path(stderr_path),
            "exit_code_path": classify_path(exit_code_path),
            "environment_path": classify_path(environment_path) if environment_path else None,
        },
        "tail_excerpt": tail_excerpt(redacted),
        "generated_by": generated_by,
    }


def build_summary(
    *,
    stdout_path: Path,
    stderr_path: Path,
    exit_code: int | None = None,
    exit_code_file: Path | None = None,
    duration_seconds: float | None = None,
    duration_file: Path | None = None,
    paths_touched_file: Path | None = None,
    extra_paths_touched: Sequence[str] | None = None,
    command: str = DEFAULT_COMMAND,
    output_path: Path | None = None,
    root: Path = REPO_ROOT,
) -> dict[str, Any]:
    del duration_file, paths_touched_file, extra_paths_touched, output_path, root
    if exit_code_file is None:
        exit_code_file = stdout_path.parent / "full_unittest_exit_code.txt"
        exit_code_file.write_text(f"{1 if exit_code is None else exit_code}\n", encoding="utf-8")
    return summarize_paths(
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        exit_code_path=exit_code_file,
        command=command,
        duration_seconds=duration_seconds,
    )


def parse_counts(text: str) -> dict[str, int]:
    counts = {"tests_run": 0, "failures": 0, "errors": 0, "skipped": 0}
    ran_matches = re.findall(r"Ran\s+(\d+)\s+tests?\s+in\s+[0-9.]+s", text)
    if ran_matches:
        counts["tests_run"] = int(ran_matches[-1])
    final_matches = re.findall(r"(FAILED|OK|ERROR)(?:\s*\(([^)]*)\))?", text)
    if final_matches:
        _status, details = final_matches[-1]
        for key, value in re.findall(r"(failures|errors|skipped)=(\d+)", details or ""):
            counts[key] = int(value)
    return counts


def extract_failure_blocks(text: str) -> list[dict[str, str]]:
    lines = text.splitlines()
    blocks: list[dict[str, str]] = []
    index = 0
    header_re = re.compile(r"^(FAIL|ERROR):\s+(.+)$")
    while index < len(lines):
        match = header_re.match(lines[index])
        if not match or not _has_unittest_separator(lines, index):
            index += 1
            continue
        kind = match.group(1).lower()
        test = match.group(2).strip()
        start = index
        index += 1
        while index < len(lines):
            if lines[index].startswith("=" * 20) and index > start:
                break
            if re.match(r"^(FAILED|OK|Ran\s+\d+\s+tests?)", lines[index]):
                break
            index += 1
        block_text = "\n".join(lines[start:index]).strip()
        exception_type, message = exception_from_block(block_text)
        blocks.append(
            {
                "kind": kind,
                "test": test,
                "exception_type": exception_type,
                "message": message,
                "traceback_excerpt": trim_lines(block_text, 24),
            }
        )
    return blocks


def _has_unittest_separator(lines: Sequence[str], index: int) -> bool:
    if index <= 0:
        return False
    previous = lines[index - 1].strip()
    return previous.startswith("=" * 20)


def exception_from_block(block_text: str) -> tuple[str, str]:
    candidates = [line.strip() for line in block_text.splitlines() if line.strip()]
    for line in reversed(candidates):
        if line.startswith(("File ", "Traceback ", "During handling ")):
            continue
        match = re.match(r"^([A-Za-z_][\w.]*?(?:Error|Exception|Warning|Failure)|AssertionError)(?::\s*(.*))?$", line)
        if match:
            return match.group(1), normalize_message(match.group(2) or "")
    if candidates:
        return "AssertionError", normalize_message(candidates[-1])
    return "unknown", ""


def group_failure_families(failures: Iterable[Mapping[str, str]], *, first_seen_at: str) -> list[dict[str, Any]]:
    families: dict[str, dict[str, Any]] = {}
    for failure in failures:
        exception_type = failure.get("exception_type") or "unknown"
        normalized = normalize_message(failure.get("message") or "")
        digest = hashlib.sha256(f"{exception_type}\n{normalized}".encode("utf-8")).hexdigest()[:16]
        family = families.setdefault(
            digest,
            {
                "family_id": f"unittest-{digest}",
                "family_hash": digest,
                "exception_type": exception_type,
                "normalized_message": normalized,
                "representative_test": failure.get("test"),
                "representative_traceback_excerpt": failure.get("traceback_excerpt", ""),
                "failed_tests": [],
                "suspected_owner": "unknown",
                "suspected_root_cause": "unknown",
                "first_seen_at": first_seen_at,
            },
        )
        test = failure.get("test")
        if test and test not in family["failed_tests"]:
            family["failed_tests"].append(test)
    return sorted(families.values(), key=lambda item: item["family_id"])


def infer_status(exit_code: int, counts: Mapping[str, int], text: str) -> str:
    if "TIMEOUT" in text or exit_code == 124:
        return "timeout"
    if exit_code == 0:
        return "pass"
    if counts.get("failures", 0) or counts.get("errors", 0):
        return "fail"
    return "error" if exit_code != 0 else "unknown"


def module_from_test_name(test_name: str) -> str:
    paren_match = re.search(r"\(([^)]+)\)", test_name)
    target = (paren_match.group(1) if paren_match else test_name).strip()
    parts = target.split(".")
    if len(parts) >= 3:
        return ".".join(parts[:-2])
    if len(parts) >= 2:
        return ".".join(parts[:-1])
    return target


def normalize_message(message: str) -> str:
    value = message.strip()
    value = re.sub(r"[A-Za-z]:\\[^\s:]+", "<path>", value)
    value = re.sub(r"/[^\s:]+", "<path>", value)
    value = re.sub(r"line \d+", "line <n>", value)
    value = re.sub(r"0x[0-9a-fA-F]+", "0x<hex>", value)
    value = re.sub(r"\b\d{4,}\b", "<n>", value)
    value = re.sub(r"\s+", " ", value)
    return value[:500]


def tail_excerpt(text: str, max_lines: int = 40) -> str:
    return trim_lines(text, max_lines, tail=True)


def trim_lines(text: str, max_lines: int, *, tail: bool = False) -> str:
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return "\n".join(lines)
    selected = lines[-max_lines:] if tail else lines[:max_lines]
    return "\n".join((["[truncated]"] + selected) if tail else (selected + ["[truncated]"]))


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""


def read_exit_code(path: Path) -> int:
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except (FileNotFoundError, ValueError):
        return 1


def redact_secrets(text: str) -> str:
    redacted = text
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def display_path(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def classify_path(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        path.resolve().relative_to(Path.cwd().resolve())
        return "relative"
    except ValueError:
        return "absolute_local"


def git_metadata(root: Path = REPO_ROOT) -> dict[str, Any]:
    def git(*args: str) -> str | None:
        completed = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)
        return completed.stdout.strip() if completed.returncode == 0 else None

    status = git("status", "--short")
    return {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "working_tree_clean": status == "",
    }


def parse_optional_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes"}:
        return True
    if lowered in {"0", "false", "no"}:
        return False
    return None


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())

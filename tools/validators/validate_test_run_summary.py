#!/usr/bin/env python3
"""Validate compact full unittest discovery summary artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "command",
    "exit_code",
    "status",
    "started_at",
    "finished_at",
    "duration_seconds",
    "git",
    "counts",
    "failed_tests",
    "failed_modules",
    "failure_families",
    "stdout_path",
    "stderr_path",
    "exit_code_path",
    "environment_path",
    "tail_excerpt",
    "generated_by",
}
VALID_STATUSES = {"pass", "fail", "error", "timeout", "unknown"}
SECRET_PATTERNS = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)(api[_-]?key|token|secret)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{16,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)raw live source response|raw_live_source_response"),
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", nargs="?", help="Path to full_unittest_summary.json")
    parser.add_argument("--summary", dest="summary_flag")
    parser.add_argument("--max-bytes", type=int, default=200_000)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    summary_path = Path(args.summary_flag or args.summary or "")
    if not str(summary_path):
        parser.error("summary path is required")
    result = validate_summary_path(summary_path, max_bytes=args.max_bytes)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"test run summary validation: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate_summary_path(path: Path, *, max_bytes: int = 200_000) -> dict[str, Any]:
    errors: list[str] = []
    try:
        size = path.stat().st_size
    except FileNotFoundError:
        return validation_result(errors=[f"missing summary: {path}"], size_bytes=0)
    if size > max_bytes:
        errors.append(f"summary exceeds compact handoff limit: {size} > {max_bytes}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return validation_result(errors=[f"invalid json: {exc}"], size_bytes=size)
    if not isinstance(payload, dict):
        return validation_result(errors=["summary must be a JSON object"], size_bytes=size)
    errors.extend(validate_summary(payload))
    return validation_result(errors=errors, size_bytes=size)


def validate_summary(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_TOP_LEVEL - set(payload))
    if missing:
        errors.append(f"missing required fields: {missing}")
    if payload.get("schema_version") != "full_unittest_summary.v0":
        errors.append("schema_version must be full_unittest_summary.v0")
    if payload.get("status") not in VALID_STATUSES:
        errors.append("status must be pass/fail/error/timeout/unknown")
    if not isinstance(payload.get("exit_code"), int):
        errors.append("exit_code must be integer")
    if not isinstance(payload.get("duration_seconds"), (int, float)) and payload.get("duration_seconds") is not None:
        errors.append("duration_seconds must be number or null")
    counts = payload.get("counts")
    if not isinstance(counts, Mapping):
        errors.append("counts must be object")
        counts = {}
    for key in ("tests_run", "failures", "errors", "skipped"):
        if not isinstance(counts.get(key), int):
            errors.append(f"counts.{key} must be integer")
    families = payload.get("failure_families")
    if not isinstance(families, list):
        errors.append("failure_families must be list")
        families = []
    if int(counts.get("failures", 0) or 0) + int(counts.get("errors", 0) or 0) > 0 and not families:
        errors.append("failure_families required when failures/errors are present")
    for family in families:
        errors.extend(validate_family(family))
    for field in ("stdout_path", "stderr_path", "exit_code_path", "environment_path"):
        errors.extend(validate_path_field(payload, field))
    serialized = json.dumps(payload, sort_keys=True)
    for pattern in SECRET_PATTERNS:
        if pattern.search(serialized):
            errors.append("summary contains secret-like or raw-source-response text")
            break
    return errors


def validate_family(family: Any) -> list[str]:
    if not isinstance(family, Mapping):
        return ["failure family must be object"]
    errors: list[str] = []
    for key in (
        "family_id",
        "family_hash",
        "exception_type",
        "normalized_message",
        "representative_test",
        "representative_traceback_excerpt",
        "failed_tests",
        "suspected_owner",
        "suspected_root_cause",
        "first_seen_at",
    ):
        if key not in family:
            errors.append(f"failure family missing {key}")
    if not isinstance(family.get("failed_tests", []), list):
        errors.append("failure family failed_tests must be list")
    return errors


def validate_path_field(payload: Mapping[str, Any], field: str) -> list[str]:
    value = payload.get(field)
    if value in {None, ""} and field == "environment_path":
        return []
    if not isinstance(value, str):
        return [f"{field} must be string"]
    path = Path(value)
    if not path.is_absolute():
        return []
    classification = payload.get("path_classification", {})
    if isinstance(classification, Mapping) and classification.get(field) == "absolute_local":
        return []
    return [f"{field} absolute path requires path_classification.{field}=absolute_local"]


def validation_result(*, errors: list[str], size_bytes: int) -> dict[str, Any]:
    return {
        "schema_version": "test_run_summary_validation.v0",
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "size_bytes": size_bytes,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


if __name__ == "__main__":
    raise SystemExit(main())

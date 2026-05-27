from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from tools.validators.validate_test_run_summary import validate_summary_path


class ValidateTestRunSummaryTests(unittest.TestCase):
    def test_valid_compact_summary_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "summary.json"
            path.write_text(json.dumps(valid_summary()) + "\n", encoding="utf-8")

            result = validate_summary_path(path)

        self.assertEqual(result["status"], "pass")

    def test_failures_require_failure_families(self) -> None:
        payload = valid_summary()
        payload["counts"]["failures"] = 1
        payload["failure_families"] = []
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "summary.json"
            path.write_text(json.dumps(payload) + "\n", encoding="utf-8")

            result = validate_summary_path(path)

        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("failure_families required" in error for error in result["errors"]))

    def test_secret_like_content_fails(self) -> None:
        payload = valid_summary()
        payload["tail_excerpt"] = "api_key=abcdefghijklmnop"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "summary.json"
            path.write_text(json.dumps(payload) + "\n", encoding="utf-8")

            result = validate_summary_path(path)

        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("secret-like" in error for error in result["errors"]))


def valid_summary() -> dict:
    return {
        "schema_version": "full_unittest_summary.v0",
        "command": "python -m unittest discover -s tests -t .",
        "exit_code": 0,
        "status": "pass",
        "started_at": "2026-05-26T00:00:00Z",
        "finished_at": "2026-05-26T00:00:01Z",
        "duration_seconds": 1.0,
        "git": {"branch": "dev", "head": "abc123", "working_tree_clean": True},
        "counts": {"tests_run": 1, "failures": 0, "errors": 0, "skipped": 0},
        "failed_tests": [],
        "failed_modules": [],
        "failure_families": [],
        "stdout_path": "../eureka-test-runs/run/stdout.txt",
        "stderr_path": "../eureka-test-runs/run/stderr.txt",
        "exit_code_path": "../eureka-test-runs/run/exit.txt",
        "environment_path": "../eureka-test-runs/run/environment.json",
        "tail_excerpt": "OK",
        "generated_by": "test",
    }


if __name__ == "__main__":
    unittest.main()

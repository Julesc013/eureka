from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from tools.reporters.summarize_unittest_log import summarize_paths, write_json


PASS_LOG = """...
----------------------------------------------------------------------
Ran 2 tests in 0.001s

OK
"""

FAIL_LOG = """======================================================================
FAIL: test_alpha (sample_tests.SampleCase.test_alpha)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/sample_tests.py", line 10, in test_alpha
    self.assertEqual(1, 2)
AssertionError: 1 != 2

======================================================================
FAIL: test_beta (sample_tests.SampleCase.test_beta)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/sample_tests.py", line 14, in test_beta
    self.assertEqual(1, 2)
AssertionError: 1 != 2

----------------------------------------------------------------------
Ran 2 tests in 0.002s

FAILED (failures=2)
"""

ERROR_LOG = """======================================================================
ERROR: test_boom (sample_tests.SampleCase.test_boom)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/sample_tests.py", line 18, in test_boom
    raise ValueError("boom 12345")
ValueError: boom 12345

----------------------------------------------------------------------
Ran 1 test in 0.001s

FAILED (errors=1)
"""


class SummarizeUnittestLogTests(unittest.TestCase):
    def test_pass_log_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            summary = summarize_fixture(Path(tmp), stdout="", stderr=PASS_LOG, exit_code=0)

        self.assertEqual(summary["status"], "pass")
        self.assertEqual(summary["counts"]["tests_run"], 2)
        self.assertEqual(summary["failed_tests"], [])

    def test_fail_log_summary_groups_failure_family(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            summary = summarize_fixture(Path(tmp), stdout="", stderr=FAIL_LOG, exit_code=1)

        self.assertEqual(summary["status"], "fail")
        self.assertEqual(summary["counts"]["failures"], 2)
        self.assertEqual(len(summary["failed_tests"]), 2)
        self.assertEqual(len(summary["failure_families"]), 1)
        self.assertIn("AssertionError", summary["failure_families"][0]["exception_type"])

    def test_error_log_summary_normalizes_messages(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            summary = summarize_fixture(Path(tmp), stdout="", stderr=ERROR_LOG, exit_code=1)

        self.assertEqual(summary["counts"]["errors"], 1)
        self.assertEqual(summary["failure_families"][0]["exception_type"], "ValueError")
        self.assertIn("<n>", summary["failure_families"][0]["normalized_message"])

    def test_summary_writer_outputs_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "summary.json"
            payload = {"schema_version": "example.v0"}
            write_json(out, payload)

            self.assertEqual(json.loads(out.read_text(encoding="utf-8")), payload)


def summarize_fixture(root: Path, *, stdout: str, stderr: str, exit_code: int) -> dict:
    stdout_path = root / "stdout.txt"
    stderr_path = root / "stderr.txt"
    exit_code_path = root / "exit.txt"
    stdout_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text(stderr, encoding="utf-8")
    exit_code_path.write_text(f"{exit_code}\n", encoding="utf-8")
    return summarize_paths(
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        exit_code_path=exit_code_path,
        duration_seconds=0.01,
        git_branch="dev",
        git_head="abc123",
        git_working_tree_clean=True,
    )


if __name__ == "__main__":
    unittest.main()

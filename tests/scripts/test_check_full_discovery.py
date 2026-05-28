from __future__ import annotations

import io
import json
from pathlib import Path
import tempfile
import unittest

from scripts.check_full_discovery import main, status_exit_code, watch_status


class CheckFullDiscoveryTests(unittest.TestCase):
    def write_json(self, path: Path, payload: dict[str, object]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def test_check_full_discovery_reports_running_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "run"
            self.write_json(
                out_dir / "status.json",
                {
                    "schema_version": "full_discovery_status.v0",
                    "run_id": "run",
                    "status": "running",
                    "pid": 1234,
                    "command": "python -m unittest discover -s tests -t .",
                    "started_at": "2026-05-28T00:00:00Z",
                    "updated_at": "2026-05-28T00:00:30Z",
                    "elapsed_seconds": 30,
                    "stdout_path": str(out_dir / "full_unittest_stdout.txt"),
                    "stderr_path": str(out_dir / "full_unittest_stderr.txt"),
                    "stdout_bytes": 128,
                    "stderr_bytes": 0,
                    "exit_code": None,
                    "summary_path": str(out_dir / "full_unittest_summary.json"),
                    "failure_families_path": str(out_dir / "failure_families.json"),
                    "failed_tests_path": str(out_dir / "failed_tests.txt"),
                },
            )
            stdout = io.StringIO()

            exit_code = main(["--out", str(out_dir)], stdout=stdout)

            self.assertEqual(0, exit_code)
            text = stdout.getvalue()
            self.assertIn("status: running", text)
            self.assertIn("elapsed: 0:30", text)
            self.assertIn("stdout_bytes: 128", text)

    def test_check_full_discovery_merges_complete_summary_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "run"
            self.write_json(
                out_dir / "status.json",
                {
                    "schema_version": "full_discovery_status.v0",
                    "run_id": "run",
                    "status": "running",
                    "pid": 1234,
                    "command": "python -m unittest discover -s tests -t .",
                    "started_at": "2026-05-28T00:00:00Z",
                    "updated_at": "2026-05-28T00:01:00Z",
                    "elapsed_seconds": 60,
                    "stdout_path": str(out_dir / "full_unittest_stdout.txt"),
                    "stderr_path": str(out_dir / "full_unittest_stderr.txt"),
                    "stdout_bytes": 256,
                    "stderr_bytes": 16,
                    "exit_code": 0,
                    "summary_path": str(out_dir / "full_unittest_summary.json"),
                    "failure_families_path": str(out_dir / "failure_families.json"),
                    "failed_tests_path": str(out_dir / "failed_tests.txt"),
                },
            )
            self.write_json(
                out_dir / "full_unittest_summary.json",
                {
                    "schema_version": "full_unittest_summary.v0",
                    "status": "pass",
                    "exit_code": 0,
                    "counts": {"tests_run": 3, "failures": 0, "errors": 0, "skipped": 0},
                },
            )
            stdout = io.StringIO()

            exit_code = main(["--out", str(out_dir), "--json"], stdout=stdout)

            self.assertEqual(0, exit_code)
            payload = json.loads(stdout.getvalue())
            self.assertEqual("pass", payload["status"])
            self.assertEqual(3, payload["tests_run"])
            self.assertEqual(0, payload["failures"])
            self.assertEqual(0, payload["errors"])

    def test_check_full_discovery_can_read_summary_without_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "run"
            self.write_json(
                out_dir / "full_unittest_summary.json",
                {
                    "schema_version": "full_unittest_summary.v0",
                    "command": "python -m unittest discover -s tests -t .",
                    "status": "fail",
                    "exit_code": 1,
                    "started_at": "2026-05-28T00:00:00Z",
                    "finished_at": "2026-05-28T00:01:00Z",
                    "duration_seconds": 60,
                    "counts": {"tests_run": 3, "failures": 1, "errors": 0, "skipped": 0},
                },
            )
            stdout = io.StringIO()

            exit_code = main(["--out", str(out_dir)], stdout=stdout)

            self.assertEqual(0, exit_code)
            text = stdout.getvalue()
            self.assertIn("status: fail", text)
            self.assertIn("tests_run: 3", text)
            self.assertIn("failures: 1", text)

    def test_watch_exits_immediately_for_terminal_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "run"
            self.write_json(
                out_dir / "status.json",
                {
                    "schema_version": "full_discovery_status.v0",
                    "run_id": "run",
                    "status": "pass",
                    "pid": None,
                    "command": "python -m unittest discover -s tests -t .",
                    "started_at": "2026-05-28T00:00:00Z",
                    "updated_at": "2026-05-28T00:01:00Z",
                    "elapsed_seconds": 60,
                    "stdout_path": str(out_dir / "full_unittest_stdout.txt"),
                    "stderr_path": str(out_dir / "full_unittest_stderr.txt"),
                    "stdout_bytes": 256,
                    "stderr_bytes": 16,
                    "exit_code": 0,
                    "summary_path": str(out_dir / "full_unittest_summary.json"),
                    "failure_families_path": str(out_dir / "failure_families.json"),
                    "failed_tests_path": str(out_dir / "failed_tests.txt"),
                },
            )
            stdout = io.StringIO()
            sleeps: list[float] = []

            payload = watch_status(out_dir=out_dir, interval_seconds=1, stdout=stdout, stderr=io.StringIO(), sleep=sleeps.append)

            self.assertEqual("pass", payload["status"])
            self.assertEqual([], sleeps)
            self.assertIn("[full-discovery] status=pass", stdout.getvalue())
            self.assertIn("status: pass", stdout.getvalue())

    def test_handoff_prints_compact_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "run"
            self.write_json(
                out_dir / "status.json",
                {
                    "schema_version": "full_discovery_status.v0",
                    "run_id": "run",
                    "status": "pass",
                    "pid": None,
                    "command": "python -m unittest discover -s tests -t .",
                    "started_at": "2026-05-28T00:00:00Z",
                    "updated_at": "2026-05-28T00:01:00Z",
                    "elapsed_seconds": 60,
                    "stdout_path": str(out_dir / "full_unittest_stdout.txt"),
                    "stderr_path": str(out_dir / "full_unittest_stderr.txt"),
                    "stdout_bytes": 256,
                    "stderr_bytes": 16,
                    "exit_code": 0,
                    "summary_path": str(out_dir / "full_unittest_summary.json"),
                    "failure_families_path": str(out_dir / "failure_families.json"),
                    "failed_tests_path": str(out_dir / "failed_tests.txt"),
                },
            )
            self.write_json(
                out_dir / "full_unittest_summary.json",
                {
                    "schema_version": "full_unittest_summary.v0",
                    "status": "pass",
                    "exit_code": 0,
                    "counts": {"tests_run": 3, "failures": 0, "errors": 0, "skipped": 0},
                },
            )
            self.write_json(out_dir / "failure_families.json", {"schema_version": "failure_family_list.v0", "failure_families": []})
            (out_dir / "failed_tests.txt").write_text("", encoding="utf-8")
            stdout = io.StringIO()

            exit_code = main(["--out", str(out_dir), "--handoff"], stdout=stdout)

            self.assertEqual(0, exit_code)
            text = stdout.getvalue()
            self.assertIn("=== full_unittest_summary.json ===", text)
            self.assertIn('"tests_run": 3', text)
            self.assertIn("=== failure_families.json ===", text)
            self.assertIn("=== failed_tests.txt ===", text)
            self.assertIn("=== git status --short --branch ===", text)

    def test_status_exit_code_distinguishes_pass_from_failure(self) -> None:
        self.assertEqual(0, status_exit_code({"status": "pass"}))
        self.assertEqual(1, status_exit_code({"status": "fail"}))
        self.assertEqual(1, status_exit_code({"status": "timeout"}))


if __name__ == "__main__":
    unittest.main()

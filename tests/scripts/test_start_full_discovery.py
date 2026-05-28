from __future__ import annotations

import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import scripts.start_full_discovery as start_tool


main = start_tool.main


class FakeProcess:
    pid = 4321

    def wait(self) -> int:
        return 0


class StartFullDiscoveryTests(unittest.TestCase):
    def write_test_module(self, root: Path, source: str) -> Path:
        tests_dir = root / "tests"
        tests_dir.mkdir()
        (tests_dir / "__init__.py").write_text("", encoding="utf-8")
        (tests_dir / "test_tiny.py").write_text(source, encoding="utf-8")
        return tests_dir

    def read_status(self, out_dir: Path) -> dict[str, object]:
        status_path = out_dir / "status.json"
        self.assertTrue(status_path.is_file())
        return json.loads(status_path.read_text(encoding="utf-8"))

    def write_stale_status(self, out_dir: Path) -> None:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "status.json").write_text(
            json.dumps(
                {
                    "schema_version": "full_discovery_status.v0",
                    "run_id": "stale_run",
                    "status": "running",
                    "pid": -1,
                    "command": "python -m unittest discover -s tests -t .",
                    "started_at": "2026-05-28T00:00:00Z",
                    "updated_at": "2026-05-28T00:00:30Z",
                    "elapsed_seconds": 30,
                    "stdout_path": str(out_dir / "full_unittest_stdout.txt"),
                    "stderr_path": str(out_dir / "full_unittest_stderr.txt"),
                    "stdout_bytes": 0,
                    "stderr_bytes": 0,
                    "exit_code": None,
                    "summary_path": str(out_dir / "full_unittest_summary.json"),
                    "failure_families_path": str(out_dir / "failure_families.json"),
                    "failed_tests_path": str(out_dir / "failed_tests.txt"),
                }
            )
            + "\n",
            encoding="utf-8",
        )

    def test_start_full_discovery_returns_immediately_and_writes_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tests_dir = self.write_test_module(
                root,
                "import unittest\n\n"
                "class Tiny(unittest.TestCase):\n"
                "    def test_ok(self):\n"
                "        self.assertTrue(True)\n",
            )
            out_dir = root / "run"
            stdout = io.StringIO()
            stderr = io.StringIO()

            with patch.object(start_tool.subprocess, "Popen", return_value=FakeProcess()) as popen, patch.object(
                start_tool,
                "track_detached_process",
                lambda process: None,
            ):
                exit_code = main(
                    [
                        "--run-id",
                        "tiny_run",
                        "--out",
                        str(out_dir),
                        "--start-dir",
                        str(tests_dir),
                        "--top-level-dir",
                        str(root),
                        "--heartbeat-seconds",
                        "1",
                    ],
                    stdout=stdout,
                    stderr=stderr,
                )

            self.assertEqual(0, exit_code, stderr.getvalue())
            self.assertIn("Started:", stdout.getvalue())
            self.assertIn("python scripts/check_full_discovery.py --run-id tiny_run", stdout.getvalue())
            self.assertIn("--watch --interval-seconds 300 --handoff", stdout.getvalue())
            popen.assert_called_once()
            status = self.read_status(out_dir)
            self.assertEqual("tiny_run", status["run_id"])
            self.assertEqual("running", status["status"])
            self.assertEqual(4321, status["pid"])
            self.assertIsNone(status["exit_code"])
            self.assertTrue((out_dir / "harness_stdout.txt").is_file())
            self.assertTrue((out_dir / "harness_stderr.txt").is_file())

    def test_start_full_discovery_json_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tests_dir = self.write_test_module(
                root,
                "import unittest\n\n"
                "class Tiny(unittest.TestCase):\n"
                "    def test_ok(self):\n"
                "        self.assertTrue(True)\n",
            )
            out_dir = root / "json_run"
            stdout = io.StringIO()

            with patch.object(start_tool.subprocess, "Popen", return_value=FakeProcess()), patch.object(
                start_tool,
                "track_detached_process",
                lambda process: None,
            ):
                exit_code = main(
                    [
                        "--run-id",
                        "json_run",
                        "--out",
                        str(out_dir),
                        "--start-dir",
                        str(tests_dir),
                        "--top-level-dir",
                        str(root),
                        "--json",
                    ],
                    stdout=stdout,
                )

            self.assertEqual(0, exit_code)
            payload = json.loads(stdout.getvalue())
            self.assertEqual("full_discovery_start.v0", payload["schema_version"])
            self.assertEqual("json_run", payload["run_id"])
            self.assertEqual(4321, payload["pid"])
            status = self.read_status(out_dir)
            self.assertEqual("running", status["status"])
            self.assertEqual(4321, status["pid"])

    def test_start_full_discovery_ignores_stale_running_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tests_dir = self.write_test_module(
                root,
                "import unittest\n\n"
                "class Tiny(unittest.TestCase):\n"
                "    def test_ok(self):\n"
                "        self.assertTrue(True)\n",
            )
            out_dir = root / "stale"
            self.write_stale_status(out_dir)
            stdout = io.StringIO()
            stderr = io.StringIO()

            with patch.object(start_tool.subprocess, "Popen", return_value=FakeProcess()), patch.object(
                start_tool,
                "track_detached_process",
                lambda process: None,
            ):
                exit_code = main(
                    [
                        "--run-id",
                        "stale_run",
                        "--out",
                        str(out_dir),
                        "--start-dir",
                        str(tests_dir),
                        "--top-level-dir",
                        str(root),
                    ],
                    stdout=stdout,
                    stderr=stderr,
                )

            self.assertEqual(0, exit_code, stderr.getvalue())
            status = self.read_status(out_dir)
            self.assertEqual("running", status["status"])
            self.assertEqual(4321, status["pid"])


if __name__ == "__main__":
    unittest.main()

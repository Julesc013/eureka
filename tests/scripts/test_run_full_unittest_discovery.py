from __future__ import annotations

from contextlib import redirect_stderr
import io
import json
from pathlib import Path
import tempfile
import unittest

from scripts.run_full_unittest_discovery import REPO_ROOT, default_output_dir, main, normalize_output_dir, run_discovery


class RunFullUnittestDiscoveryTests(unittest.TestCase):
    def write_test_module(self, root: Path, name: str, source: str) -> Path:
        tests_dir = root / "tests"
        tests_dir.mkdir(exist_ok=True)
        (tests_dir / "__init__.py").write_text("", encoding="utf-8")
        (tests_dir / name).write_text(source, encoding="utf-8")
        return tests_dir

    def test_default_output_dir_is_outside_repo(self) -> None:
        out_dir = default_output_dir().resolve()

        self.assertEqual("eureka-test-runs", out_dir.parent.name)
        self.assertNotEqual(REPO_ROOT, out_dir)
        self.assertNotIn(".aide.local", out_dir.parts)

    def test_repo_local_private_root_requires_explicit_override(self) -> None:
        forbidden = REPO_ROOT / ".aide.local" / "test-runs" / "bad"

        with self.assertRaises(ValueError):
            normalize_output_dir(forbidden)
        self.assertFalse((REPO_ROOT / ".aide.local").exists())

    def test_repo_local_private_root_override_is_explicit(self) -> None:
        forbidden = REPO_ROOT / ".aide.local" / "test-runs" / "debug"

        self.assertEqual(forbidden.resolve(), normalize_output_dir(forbidden, allow_repo_local_output=True))
        self.assertFalse((REPO_ROOT / ".aide.local").exists())

    def test_harness_runs_tiny_fake_test_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tests_dir = self.write_test_module(
                root,
                "test_tiny.py",
                "import unittest\n\n"
                "class Tiny(unittest.TestCase):\n"
                "    def test_ok(self):\n"
                "        self.assertTrue(True)\n",
            )
            out_dir = root / "run"

            result = run_discovery(
                out_dir=out_dir,
                start_dir=str(tests_dir),
                top_level_dir=str(root),
                timeout_seconds=30,
            )

            summary = json.loads((out_dir / "full_unittest_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(result["exit_code"], 0)
            self.assertEqual(summary["status"], "pass")
            self.assertEqual(summary["counts"]["tests_run"], 1)
            self.assertTrue((out_dir / "environment.json").is_file())
            self.assertTrue((out_dir / "failure_families.json").is_file())
            self.assertTrue((out_dir / "failed_tests.txt").is_file())

    def test_harness_emits_operator_progress_when_requested(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tests_dir = self.write_test_module(
                root,
                "test_tiny.py",
                "import unittest\n\n"
                "class Tiny(unittest.TestCase):\n"
                "    def test_ok(self):\n"
                "        self.assertTrue(True)\n",
            )
            progress = io.StringIO()
            out_dir = root / "run"

            result = run_discovery(
                out_dir=out_dir,
                start_dir=str(tests_dir),
                top_level_dir=str(root),
                timeout_seconds=30,
                progress_stream=progress,
            )

            text = progress.getvalue()
            self.assertEqual(result["exit_code"], 0)
            self.assertIn("[full-discovery] started:", text)
            self.assertIn("[full-discovery] output_dir:", text)
            self.assertIn("[full-discovery] finished:", text)
            self.assertIn("full_unittest_summary.json", text)

    def test_harness_emits_heartbeat_for_slow_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tests_dir = self.write_test_module(
                root,
                "test_slow.py",
                "import time\n"
                "import unittest\n\n"
                "class Slow(unittest.TestCase):\n"
                "    def test_slow_ok(self):\n"
                "        time.sleep(1.2)\n"
                "        self.assertTrue(True)\n",
            )
            progress = io.StringIO()
            out_dir = root / "run"

            result = run_discovery(
                out_dir=out_dir,
                start_dir=str(tests_dir),
                top_level_dir=str(root),
                timeout_seconds=30,
                heartbeat_seconds=1,
                progress_stream=progress,
            )

            self.assertEqual(result["exit_code"], 0)
            self.assertIn("still running after", progress.getvalue())

    def test_harness_timeout_writes_compact_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tests_dir = self.write_test_module(
                root,
                "test_timeout.py",
                "import time\n"
                "import unittest\n\n"
                "class Slow(unittest.TestCase):\n"
                "    def test_timeout(self):\n"
                "        time.sleep(5)\n",
            )
            progress = io.StringIO()
            out_dir = root / "run"

            result = run_discovery(
                out_dir=out_dir,
                start_dir=str(tests_dir),
                top_level_dir=str(root),
                timeout_seconds=1,
                heartbeat_seconds=1,
                progress_stream=progress,
            )

            summary = json.loads((out_dir / "full_unittest_summary.json").read_text(encoding="utf-8"))
            stderr_text = (out_dir / "full_unittest_stderr.txt").read_text(encoding="utf-8")
            self.assertEqual(result["exit_code"], 124)
            self.assertEqual(summary["status"], "timeout")
            self.assertIn("TIMEOUT: unittest discovery exceeded 1 seconds", stderr_text)
            self.assertIn("timeout reached after", progress.getvalue())

    def test_cli_can_suppress_progress(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tests_dir = self.write_test_module(
                root,
                "test_tiny.py",
                "import unittest\n\n"
                "class Tiny(unittest.TestCase):\n"
                "    def test_ok(self):\n"
                "        self.assertTrue(True)\n",
            )
            stdout = io.StringIO()
            stderr = io.StringIO()

            with redirect_stderr(stderr):
                exit_code = main(
                    [
                        "--out",
                        str(root / "run"),
                        "--start-dir",
                        str(tests_dir),
                        "--top-level-dir",
                        str(root),
                        "--timeout-seconds",
                        "30",
                        "--no-progress",
                    ],
                    stdout=stdout,
                )

            self.assertEqual(exit_code, 0)
            self.assertEqual("", stderr.getvalue())
            self.assertIn("full_unittest_summary.json", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts.run_full_unittest_discovery import REPO_ROOT, default_output_dir, normalize_output_dir, run_discovery


class RunFullUnittestDiscoveryTests(unittest.TestCase):
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
            tests_dir = root / "tests"
            tests_dir.mkdir()
            (tests_dir / "__init__.py").write_text("", encoding="utf-8")
            (tests_dir / "test_tiny.py").write_text(
                "import unittest\n\n"
                "class Tiny(unittest.TestCase):\n"
                "    def test_ok(self):\n"
                "        self.assertTrue(True)\n",
                encoding="utf-8",
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


if __name__ == "__main__":
    unittest.main()

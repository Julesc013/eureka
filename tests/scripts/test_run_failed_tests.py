from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts.run_failed_tests import plan_or_run_failed_tests, rerun_commands


class RunFailedTestsTests(unittest.TestCase):
    def test_prints_failed_test_commands(self) -> None:
        payload = {
            "failed_tests": ["test_alpha (sample_tests.SampleCase.test_alpha)"],
            "failed_modules": ["sample_tests"],
        }

        commands = rerun_commands(payload)

        self.assertEqual(len(commands), 1)
        self.assertIn("-m unittest sample_tests.SampleCase.test_alpha", commands[0])

    def test_modules_only_plan_writes_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            summary = root / "full_unittest_summary.json"
            summary.write_text(
                json.dumps(
                    {
                        "failed_tests": ["test_alpha (sample_tests.SampleCase.test_alpha)"],
                        "failed_modules": ["sample_tests"],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            out = root / "failed_rerun_summary.json"

            result = plan_or_run_failed_tests(summary_path=summary, modules_only=True, out_path=out)

            written = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(result["status"], "planned")
        self.assertEqual(written["mode"], "modules_only")
        self.assertFalse(written["full_discovery_run"])


if __name__ == "__main__":
    unittest.main()

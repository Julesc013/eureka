from __future__ import annotations

import json
from io import StringIO
import unittest

from surfaces.native.cli.main import main


def run_cli(*args: str) -> tuple[int, str]:
    output = StringIO()
    exit_code = main(list(args), stdout=output)
    return exit_code, output.getvalue()


class ArchiveResolutionEvalsCliTestCase(unittest.TestCase):
    def test_eval_command_returns_suite_summary(self) -> None:
        exit_code, output = run_cli("evals-archive-resolution", "--task", "windows_7_apps")

        self.assertEqual(exit_code, 0)
        self.assertIn("Archive resolution evals", output)
        self.assertIn("windows_7_apps", output)
        self.assertIn("satisfied", output)
        self.assertIn("status_counts: satisfied=1", output)

    def test_eval_command_json_mode_works(self) -> None:
        exit_code, output = run_cli(
            "evals-archive-resolution",
            "--task",
            "windows_7_apps",
            "--json",
        )
        payload = json.loads(output)

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["status"], "evaluated")
        self.assertEqual(payload["eval_suite"]["total_task_count"], 1)
        self.assertEqual(payload["eval_suite"]["tasks"][0]["task_id"], "windows_7_apps")


if __name__ == "__main__":
    unittest.main()

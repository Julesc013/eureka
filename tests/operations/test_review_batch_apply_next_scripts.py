from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class ReviewBatchApplyNextScriptsTests(unittest.TestCase):
    def test_cli_smoke_commands_pass(self) -> None:
        commands = [
            ["scripts/eureka_review_batch_apply_validate.py", "--from-examples", "--json"],
            ["scripts/eureka_review_batch_apply_next.py", "--from-examples", "--use-temp-instance", "--json"],
            ["scripts/eureka_review_batch_apply_report.py", "--from-examples", "--json"],
        ]
        for command in commands:
            completed = subprocess.run(
                [sys.executable, *command],
                cwd=REPO_ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)


if __name__ == "__main__":
    unittest.main()

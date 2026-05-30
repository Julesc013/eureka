from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class ReviewBatchScriptTests(unittest.TestCase):
    def test_review_batch_scripts_help(self) -> None:
        for script in (
            "scripts/eureka_review_batch.py",
            "scripts/eureka_review_batch_preview.py",
            "scripts/eureka_review_batch_decision.py",
            "scripts/eureka_review_batch_handoff.py",
        ):
            completed = subprocess.run(
                [sys.executable, str(REPO_ROOT / script), "--help"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, completed.returncode, msg=completed.stderr)


if __name__ == "__main__":
    unittest.main()

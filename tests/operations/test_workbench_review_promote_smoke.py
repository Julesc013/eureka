from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]


class WorkbenchReviewPromoteSmokeTests(unittest.TestCase):
    def test_cli_temp_apply_smoke(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/eureka_workbench_review_promote.py",
                "--from-fixtures",
                "--decision",
                "accept_local_reviewed",
                "--operator-token",
                "local-dev-token",
                "--use-temp-instance",
                "--apply-to-temp",
                "--projection",
                "operator_workbench",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["temp_reviewed_index_refresh_passed"], payload)
        self.assertTrue(payload["temp_search_after_refresh_passed"], payload)
        self.assertFalse(payload["master_index_mutated"])


if __name__ == "__main__":
    unittest.main()

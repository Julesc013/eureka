from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]


class WorkbenchReviewPromoteScriptsTests(unittest.TestCase):
    def test_cli_operator_dry_run_and_read_only_projections(self) -> None:
        cases = (
            ("operator_workbench", "promotion_preview_created"),
            ("public_web", "public_projection_blocked"),
            ("native_desktop_read_only", "native_read_only_projection_blocked"),
        )
        for projection, expected_key in cases:
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/eureka_workbench_review_promote.py",
                    "--from-fixtures",
                    "--decision",
                    "accept_local_reviewed",
                    "--dry-run",
                    "--projection",
                    projection,
                    "--json",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertTrue(payload[expected_key], payload)
            self.assertFalse(payload["operator_instance_mutated"])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]


class IALiveMetadataLaneScriptsTests(unittest.TestCase):
    def test_cli_dry_run_and_mock_live(self) -> None:
        for flag, expected_key in (("--dry-run", "dry_run_passed"), ("--mock-live", "mock_live_passed")):
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/eureka_ia_live_metadata_lane.py",
                    "--query",
                    "sampleproject",
                    "--projection",
                    "operator_workbench",
                    flag,
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
            self.assertFalse(payload["raw_response_committed"])


if __name__ == "__main__":
    unittest.main()

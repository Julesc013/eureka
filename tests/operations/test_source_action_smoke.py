from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class SourceActionSmokeTests(unittest.TestCase):
    def test_scorecard_cli_json(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/eureka_source_action_scorecard.py",
                "--source-family",
                "fixture_source_action",
                "--from-examples",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("source_action_scorecard.v0", payload["schema_version"])
        self.assertFalse(payload["live_call_performed"])


if __name__ == "__main__":
    unittest.main()

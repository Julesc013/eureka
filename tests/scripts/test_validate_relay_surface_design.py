from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate_relay_surface_design.py"


class ValidateRelaySurfaceDesignScriptTest(unittest.TestCase):
    def test_plain_validator_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("Relay surface design validation", completed.stdout)
        self.assertIn("status: valid", completed.stdout)

    def test_json_validator_passes_and_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertTrue(payload["no_relay_implemented"])
        self.assertIn("local_static_http", payload["protocol_candidates"])
        self.assertIn("snapshot_mount", payload["protocol_candidates"])


if __name__ == "__main__":
    unittest.main()

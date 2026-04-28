from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate_compatibility_surfaces.py"


class ValidateCompatibilitySurfacesScriptTest(unittest.TestCase):
    def test_plain_validator_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("Compatibility surface validation", completed.stdout)
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
        self.assertIn("lite", payload["implemented_static_surfaces"])
        self.assertIn("live_backend", payload["future_disabled_surfaces"])


if __name__ == "__main__":
    unittest.main()

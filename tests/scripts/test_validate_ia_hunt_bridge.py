import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class ValidateIAHuntBridgeScriptTests(unittest.TestCase):
    def test_validator_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_ia_hunt_bridge.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=90,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("status: valid", completed.stdout)


if __name__ == "__main__":
    unittest.main()

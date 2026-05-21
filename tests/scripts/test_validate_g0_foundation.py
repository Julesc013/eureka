import json
import subprocess
import sys
import unittest

from scripts.validate_g0_foundation import validate_g0_foundation


class ValidateG0FoundationTests(unittest.TestCase):
    def test_validator_function_passes(self) -> None:
        report = validate_g0_foundation()
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])

    def test_validator_cli_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_g0_foundation.py", "--json"],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(json.loads(completed.stdout)["status"], "valid")


if __name__ == "__main__":
    unittest.main()

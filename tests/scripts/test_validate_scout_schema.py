from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest

from scripts.validate_scout_schema import validate_scout_schema


REPO_ROOT = Path(__file__).resolve().parents[2]


class ValidateScoutSchemaTests(unittest.TestCase):
    def test_validator_function_passes(self) -> None:
        report = validate_scout_schema(REPO_ROOT)
        self.assertEqual(report["status"], "valid", report["errors"])
        self.assertGreaterEqual(report["seed_count"], 5)

    def test_validator_cli_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/validate_scout_schema.py"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", result.stdout)


if __name__ == "__main__":
    unittest.main()

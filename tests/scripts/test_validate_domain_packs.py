from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from scripts.validate_domain_packs import validate_domain_packs


REPO_ROOT = Path(__file__).resolve().parents[2]


class ValidateDomainPacksTests(unittest.TestCase):
    def test_validator_function_passes(self) -> None:
        report = validate_domain_packs(REPO_ROOT)
        self.assertEqual(report["status"], "valid", report["errors"])
        self.assertEqual(report["domain_count"], 8)

    def test_validator_cli_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/validate_domain_packs.py"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", result.stdout)


if __name__ == "__main__":
    unittest.main()

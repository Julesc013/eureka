from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class ScoutSchemaScriptTests(unittest.TestCase):
    def test_schema_cli_validates_manifest(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/eureka_scout_schema.py",
                "--manifest",
                "examples/scout/scout_seed_manifest.json",
                "--validate",
                "--json",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn('"validation_passed": true', result.stdout)

    def test_schema_cli_lists_seed_ids(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/eureka_scout_schema.py",
                "--manifest",
                "examples/scout/scout_seed_manifest.json",
                "--list",
                "--json",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("scout_seed_legacy_software_portable_utils", result.stdout)


if __name__ == "__main__":
    unittest.main()

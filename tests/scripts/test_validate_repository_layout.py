from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate_repository_layout.py"


class RepositoryLayoutValidatorScriptTest(unittest.TestCase):
    def test_validator_plain_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("static_artifact_root: site/dist", completed.stdout)
        self.assertIn("generated_artifact_id: static_site_dist", completed.stdout)

    def test_validator_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["static_artifact_root"], "site/dist")
        self.assertEqual(payload["external_root"], "external")
        self.assertEqual(payload["generated_artifact_id"], "static_site_dist")
        self.assertEqual(payload["active_legacy_reference_hits"], [])

    def test_validator_strict_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--strict", "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(json.loads(completed.stdout)["status"], "valid")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "generate_public_alpha_rehearsal_evidence.py"


class PublicAlphaRehearsalEvidenceScriptTest(unittest.TestCase):
    def test_plain_summary_runs(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Public Alpha Rehearsal Evidence", completed.stdout)
        self.assertIn("static_site: valid", completed.stdout)
        self.assertIn("public_alpha_smoke: passed", completed.stdout)
        self.assertIn("signoff_status: unsigned", completed.stdout)

    def test_json_summary_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "ready")
        self.assertTrue(payload["manifest"]["no_deployment_performed"])
        self.assertEqual(payload["manifest"]["signoff_status"], "unsigned")
        self.assertEqual(payload["summary"]["route_inventory"]["total_routes"], 89)

    def test_check_mode_passes_plain_and_json(self) -> None:
        plain = subprocess.run(
            [sys.executable, str(SCRIPT), "--check"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", plain.stdout)

        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--check", "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["errors"], [])


if __name__ == "__main__":
    unittest.main()

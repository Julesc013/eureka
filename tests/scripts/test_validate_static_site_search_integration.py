from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate_static_site_search_integration.py"


class ValidateStaticSiteSearchIntegrationScriptTest(unittest.TestCase):
    def test_validator_plain_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", completed.stdout)

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
        self.assertEqual(payload["errors"], [])
        self.assertEqual(payload["backend_status"], "backend_unconfigured")
        self.assertFalse(payload["hosted_backend_verified"])
        self.assertFalse(payload["search_form_enabled"])
        self.assertGreater(payload["document_count"], 0)


if __name__ == "__main__":
    unittest.main()

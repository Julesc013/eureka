from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "scripts" / "validate_pack_import_planning.py"


class ValidatePackImportPlanningScriptTestCase(unittest.TestCase):
    def test_validator_passes_plain_and_json(self) -> None:
        plain = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", plain.stdout)
        self.assertIn("default_future_mode: validate_only", plain.stdout)

        completed = subprocess.run(
            [sys.executable, str(VALIDATOR), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertFalse(payload["import_runtime_implemented"])
        self.assertEqual(payload["default_future_mode"], "validate_only")
        self.assertEqual(payload["next_future_mode"], "stage_local_quarantine")
        self.assertIn("source_pack", payload["supported_pack_types"])
        self.assertIn("contribution_pack", payload["supported_pack_types"])


if __name__ == "__main__":
    unittest.main()

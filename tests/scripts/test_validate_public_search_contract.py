from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate_public_search_contract.py"


class PublicSearchContractValidatorScriptTest(unittest.TestCase):
    def test_validator_plain_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("first_allowed_mode: local_index_only", completed.stdout)
        self.assertIn("runtime_routes_implemented: False", completed.stdout)

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
        self.assertEqual(payload["contract_id"], "public_search_api_contract_v0")
        self.assertEqual(payload["first_allowed_mode"], "local_index_only")
        self.assertFalse(payload["runtime_routes_implemented"])
        self.assertIn("GET /api/v1/search", payload["registered_routes"])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate_public_search_production_contract.py"


class ValidatePublicSearchProductionContractScriptTest(unittest.TestCase):
    def test_plain_validator_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("active_mode: local_index_only", completed.stdout)

    def test_json_validator_passes_and_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["report_id"], "public_search_production_contract_v0")
        self.assertEqual(payload["active_mode"], "local_index_only")
        self.assertFalse(payload["hosted_search_implemented"])
        self.assertFalse(payload["live_probes_enabled"])
        self.assertIn("source_status.v0.json", payload["required_schemas"])


if __name__ == "__main__":
    unittest.main()

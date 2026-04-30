from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate_public_search_result_card_contract.py"


class PublicSearchResultCardContractValidatorScriptTest(unittest.TestCase):
    def test_validator_plain_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("contract_id: public_search_result_card_contract_v0", completed.stdout)
        self.assertIn("examples: 5", completed.stdout)

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
        self.assertEqual(payload["contract_id"], "public_search_result_card_contract_v0")
        self.assertEqual(payload["schema"], "contracts/api/search_result_card.v0.json")
        self.assertIn("download", payload["unsafe_actions"])
        self.assertIn("still_searching", payload["required_lanes"])


if __name__ == "__main__":
    unittest.main()

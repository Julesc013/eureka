from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate_snapshot_consumer_contract.py"


class SnapshotConsumerContractValidatorTestCase(unittest.TestCase):
    def test_validator_json_output_parses(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["created_by"], "snapshot_consumer_contract_validator_v0")
        self.assertEqual(payload["profile_count"], 6)
        self.assertFalse(payload["production_consumer_implemented"])
        self.assertFalse(payload["native_consumer_implemented"])
        self.assertFalse(payload["relay_consumer_implemented"])
        self.assertIn("minimal_file_tree_consumer", payload["profile_ids"])


if __name__ == "__main__":
    unittest.main()

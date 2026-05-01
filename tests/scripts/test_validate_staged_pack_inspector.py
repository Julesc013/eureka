from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "scripts" / "validate_staged_pack_inspector.py"


class ValidateStagedPackInspectorScriptTestCase(unittest.TestCase):
    def test_validator_plain_and_json_pass(self) -> None:
        plain = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Staged Pack Inspector validation", plain.stdout)
        self.assertIn("status: valid", plain.stdout)

        completed = subprocess.run(
            [sys.executable, str(VALIDATOR), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertEqual(payload["validator_id"], "staged_pack_inspector_validator_v0")
        self.assertEqual(payload["inspection_summary"], {"total": 1, "passed": 1, "failed": 0, "unavailable": 0})
        for field in [
            "model_calls_performed",
            "network_performed",
            "mutation_performed",
            "staging_performed",
            "import_performed",
            "indexing_performed",
            "upload_performed",
            "runtime_mutation_performed",
            "master_index_mutation_performed",
            "public_search_mutated",
            "local_index_mutated",
        ]:
            self.assertFalse(payload[field], field)


if __name__ == "__main__":
    unittest.main()

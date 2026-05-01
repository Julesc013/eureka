from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "scripts" / "validate_staging_report_path_contract.py"


class ValidateStagingReportPathContractScriptTestCase(unittest.TestCase):
    def test_validator_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("default_output_mode: stdout", completed.stdout)
        self.assertIn("staging_runtime_implemented: False", completed.stdout)
        self.assertIn("local_state_roots_present: 0", completed.stdout)

    def test_validator_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["default_output_mode"], "stdout")
        self.assertTrue(payload["explicit_output_required_for_file_write"])
        self.assertTrue(payload["local_private_by_default"])
        self.assertFalse(payload["report_path_runtime_implemented"])
        self.assertFalse(payload["staging_runtime_implemented"])
        self.assertEqual(payload["local_state_roots_present"], [])
        self.assertFalse(payload["network_performed"])
        self.assertFalse(payload["mutation_performed"])
        self.assertFalse(payload["staging_performed"])
        self.assertFalse(payload["import_performed"])
        self.assertFalse(payload["indexing_performed"])
        self.assertFalse(payload["upload_performed"])
        self.assertFalse(payload["master_index_mutation_performed"])


if __name__ == "__main__":
    unittest.main()

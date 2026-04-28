from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate_rust_local_index_parity_plan.py"


class RustLocalIndexParityPlanValidatorTestCase(unittest.TestCase):
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
        self.assertEqual(payload["status"], "passed")
        self.assertEqual(payload["check_id"], "rust_local_index_parity_planning_v0")
        self.assertEqual(payload["record_kind_count"], 7)
        self.assertGreaterEqual(payload["case_count"], 14)
        self.assertEqual(payload["current_oracle_query_cases"], 3)
        self.assertGreaterEqual(payload["planned_future_query_cases"], 10)
        self.assertTrue(payload["python_remains_oracle"])
        self.assertFalse(payload["rust_local_index_implemented"])
        self.assertFalse(payload["runtime_wiring_allowed"])


if __name__ == "__main__":
    unittest.main()

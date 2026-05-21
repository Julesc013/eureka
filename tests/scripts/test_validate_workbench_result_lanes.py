from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate_workbench_result_lanes.py"


class WorkbenchResultLanesValidatorScriptTest(unittest.TestCase):
    def test_validator_plain_passes(self) -> None:
        completed = subprocess.run([sys.executable, str(SCRIPT)], cwd=REPO_ROOT, check=True, capture_output=True, text=True)
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("error_count: 0", completed.stdout)

    def test_validator_json_records_boundaries(self) -> None:
        completed = subprocess.run([sys.executable, str(SCRIPT), "--json"], cwd=REPO_ROOT, check=True, capture_output=True, text=True)
        payload = json.loads(completed.stdout)
        self.assertEqual("valid", payload["status"])
        self.assertFalse(payload["source_probe_executed"])
        self.assertFalse(payload["live_ia_call_performed"])
        self.assertFalse(payload["production_readiness_claimed"])


if __name__ == "__main__":
    unittest.main()

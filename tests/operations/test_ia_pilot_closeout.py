import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class IAPilotCloseoutTests(unittest.TestCase):
    def test_closeout_result_records_complete_vertical_slice(self):
        result = json.loads((ROOT / "control/inventory/ia_pilot_closeout_result.json").read_text(encoding="utf-8"))
        self.assertEqual("pass", result["status"])
        self.assertTrue(result["full_ia_metadata_vertical_slice_complete"])
        self.assertFalse(result["full_archive_org_integration_claimed"])
        self.assertTrue(result["syn_can_start"])

    def test_validator_passes(self):
        completed = subprocess.run(
            [sys.executable, "scripts/validate_ia_pilot_closeout.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)

    def test_summary_script_reports_no_full_integration_claim(self):
        completed = subprocess.run(
            [sys.executable, "scripts/summarize_ia_pilot.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["full_ia_metadata_vertical_slice_complete"])
        self.assertFalse(payload["full_archive_org_integration_claimed"])


if __name__ == "__main__":
    unittest.main()

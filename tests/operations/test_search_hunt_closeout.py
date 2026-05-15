import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.audit_search_hunt_closeout import audit_closeout


class SearchHuntCloseoutTests(unittest.TestCase):
    def test_closeout_audit_reports_complete_track(self):
        result = audit_closeout(Path.cwd())
        closeout = result["closeout_result"]
        self.assertEqual(closeout["status"], "pass")
        self.assertTrue(closeout["hunt_track_complete"])
        self.assertEqual(closeout["hard_blockers_remaining"], 0)
        self.assertEqual(closeout["warnings_remaining"], 0)
        self.assertFalse(closeout["provider_calls_performed"])
        self.assertFalse(closeout["source_probes_executed"])
        self.assertFalse(closeout["extraction_executed"])

    def test_closeout_fails_when_required_hunt_result_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = audit_closeout(Path(tmp))
        self.assertNotEqual(result["closeout_result"]["hard_blockers_remaining"], 0)
        self.assertFalse(result["closeout_result"]["hunt_track_complete"])

    def test_validator_script_passes_with_disposed_warnings(self):
        completed = subprocess.run(
            [sys.executable, "scripts/validate_search_hunt_closeout.py", "--json"],
            text=True,
            capture_output=True,
            check=False,
            timeout=240,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
        payload = json.loads(completed.stdout)
        self.assertIn(payload["status"], {"pass", "pass_with_warnings"})
        self.assertEqual(payload["hard_blockers_remaining"], 0)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class TestFailureLedgerTests(unittest.TestCase):
    def test_failure_entries_are_first_class_and_failed_first(self) -> None:
        payload = json.loads((REPO_ROOT / "control/inventory/test_failure_ledger.json").read_text(encoding="utf-8"))
        self.assertEqual("test_failure_ledger.v0", payload["schema_version"])
        failures = payload["failures"]
        self.assertGreaterEqual(len(failures), 2)
        for failure in failures:
            self.assertIn(failure["status"], {"new", "reproduced", "fixed_pending_full", "fixed_confirmed", "flaky_quarantined", "external_environment", "accepted_nonblocking"})
            self.assertTrue(failure["rerun_command"].startswith("python -m unittest "))
            self.assertIn("test_module", failure)
            self.assertIn("blocking_level", failure)


if __name__ == "__main__":
    unittest.main()

